use crate::delay_line::DelayLine;
use crate::grain_player::GrainPlayer;
use crate::options::{ChannelOpts, PlaybackMode};
use micromath::F32Ext;

pub struct Channel<G: GrainPlayer> {
    pub grain: G,
    l_gate: bool,
    l_mode: PlaybackMode,
    l_start: u32,
    l_len: u32,
}

impl<G: GrainPlayer> Channel<G> {
    pub fn new(grain: G) -> Self {
        Self { grain, l_gate: false, l_mode: PlaybackMode::default(), l_start: 0, l_len: 0 }
    }

    /// Update grain player from channel options and input state
    pub fn update(&mut self, opts: &ChannelOpts, max_samples: u32, touch_idx: usize, touch: &[u8; 8], jack: u8, cv: i32) {
        let size = max_samples;
        let ui_start = (opts.start.value as i32).max(5) as u32;
        let start = size.saturating_sub(ui_start);
        let max_length = start.saturating_sub(2);
        let length = ((opts.len.value as i32).max(0) as u32).min(max_length);

        // In gate-stuck modes: jack CV controls speed (1V/oct, 3V = 1.0x),
        // or touch scales from 1x to 2x the UI speed value.
        let jack_plugged = (jack & (1 << touch_idx)) != 0;
        let speed = if opts.mode.value.gate_stuck() && jack_plugged {
            let volts = cv as f32 / 4000.0;
            (256.0 * (2.0f32).powf(volts - 3.0)).clamp(32.0, 1024.0) as u16
        } else if opts.mode.value.gate_stuck() {
            let t = u32::from(touch[touch_idx]);
            (u32::from(opts.speed.value) * (256 + t) / 256) as u16
        } else {
            opts.speed.value
        };
        self.grain.set_params(speed, start, length);

        // Pulse gate low for one tick on mode/start/len change to force a rising edge restart
        let mode_changed = opts.mode.value != self.l_mode;
        let params_changed = opts.start.value != self.l_start || opts.len.value != self.l_len;
        self.l_mode = opts.mode.value;
        self.l_start = opts.start.value;
        self.l_len = opts.len.value;

        // Gate logic with hysteresis (always touch/CV, unless mode has gate stuck on)
        let (gate, hw_gate_enable) = if mode_changed || params_changed {
            (false, false)
        } else if opts.mode.value.gate_stuck() {
            (true, false)
        } else if jack_plugged {
            (false, true)
        } else {
            let touch_gate = if self.l_gate {
                touch[touch_idx] >= 150
            } else {
                touch[touch_idx] > 200
            };
            (touch_gate, false)
        };
        self.l_gate = gate;

        self.grain.set_control(opts.mode.value.into(), gate, hw_gate_enable, opts.reverse.value);
    }

    pub fn view<D: DelayLine>(&self, delayln: &D) -> ChannelView {
        ChannelView {
            grain_position: self.grain.position(),
            delayln_max_samples: delayln.size_samples(),
            delayln_base: delayln.data_ptr(),
            delayln_wrpointer: delayln.wrpointer(),
        }
    }
}

#[derive(Clone)]
pub struct ChannelView {
    pub grain_position: usize,
    pub delayln_max_samples: usize,
    pub delayln_base: *const i16,
    pub delayln_wrpointer: usize,
}

impl ChannelView {
    pub fn from_delayln<D: DelayLine>(delayln: &D) -> Self {
        Self {
            grain_position: 0,
            delayln_max_samples: delayln.size_samples(),
            delayln_base: delayln.data_ptr(),
            delayln_wrpointer: delayln.wrpointer(),
        }
    }

    pub fn grain_start_delay(&self, opts: &ChannelOpts) -> usize {
        let ui_start = (opts.start.value as i32).max(0) as usize;
        self.delayln_max_samples.saturating_sub(ui_start)
    }

    pub fn grain_len(opts: &ChannelOpts) -> usize {
        (opts.len.value as i32).max(0) as usize
    }

    pub fn stride(&self, opts: &ChannelOpts, n_samples: usize) -> usize {
        let max_stride = self.delayln_max_samples / n_samples;
        max_stride >> (opts.zoom.value as usize)
    }

    pub fn waveform_start_delay(&self, opts: &ChannelOpts, n_samples: usize, center_on_end: bool) -> usize {
        let stride = self.stride(opts, n_samples);
        let is_zoomed = opts.zoom.value > 0;

        if is_zoomed {
            let center_offset = (n_samples / 2) * stride;
            let grain_start = self.grain_start_delay(opts);
            let center_delay = if center_on_end {
                grain_start.saturating_sub(Self::grain_len(opts))
            } else {
                grain_start
            };
            center_delay + center_offset
        } else {
            n_samples * stride
        }
    }

    pub fn delay_to_x(&self, opts: &ChannelOpts, delay: usize, n_samples: usize, center_on_end: bool, waveform_x: u32, actual_span: u32) -> u32 {
        let stride = self.stride(opts, n_samples);
        let is_zoomed = opts.zoom.value > 0;
        let displayed_span = n_samples * stride;
        if is_zoomed {
            let center_x = waveform_x + actual_span / 2;
            let grain_start = self.grain_start_delay(opts);
            let center_delay = if center_on_end {
                grain_start.saturating_sub(Self::grain_len(opts))
            } else {
                grain_start
            };
            if delay >= center_delay {
                let offset = delay - center_delay;
                center_x.saturating_sub((offset as u32 * actual_span) / displayed_span as u32)
            } else {
                let offset = center_delay - delay;
                center_x + (offset as u32 * actual_span) / displayed_span as u32
            }
        } else {
            let size = self.delayln_max_samples;
            waveform_x + actual_span - (delay as u32 * actual_span) / size as u32
        }
    }

    pub fn grain_markers_x(&self, opts: &ChannelOpts, n_samples: usize, center_on_end: bool, waveform_x: u32, actual_span: u32) -> (u32, u32) {
        let grain_start = self.grain_start_delay(opts);
        let grain_end = grain_start.saturating_sub(Self::grain_len(opts));
        let start_x = self.delay_to_x(opts, grain_start, n_samples, center_on_end, waveform_x, actual_span);
        let end_x = self.delay_to_x(opts, grain_end, n_samples, center_on_end, waveform_x, actual_span);
        (start_x, end_x)
    }

    pub fn view_label(opts: &ChannelOpts, center_on_end: bool) -> &'static str {
        if opts.zoom.value == 0 {
            "[entire buffer]"
        } else if center_on_end {
            "[zoom end]"
        } else {
            "[zoom start]"
        }
    }

    pub fn delayln_read_samples(&self, buf: &mut [i16], start_delay: usize, stride: usize) {
        let wrpointer = self.delayln_wrpointer;
        let size = self.delayln_max_samples;
        // Convert start_delay to position and align to stride boundary
        let raw_start_pos = (wrpointer + size - start_delay) % size;
        let aligned_start_pos = (raw_start_pos / stride) * stride;
        for (i, sample) in buf.iter_mut().enumerate() {
            let offset = (aligned_start_pos + i * stride) % size;
            *sample = unsafe { self.delayln_base.add(offset).read_volatile() };
        }
    }

    pub fn read_samples(&self, opts: &ChannelOpts, buf: &mut [i16], center_on_end: bool) {
        let n_samples = buf.len();
        let start_delay = self.waveform_start_delay(opts, n_samples, center_on_end);
        let stride = self.stride(opts, n_samples);
        self.delayln_read_samples(buf, start_delay, stride);
        // Zero out samples whose delay falls outside the buffer
        for i in 0..n_samples {
            let delay = start_delay as isize - (i as isize * stride as isize);
            if delay < 0 || delay as usize > self.delayln_max_samples {
                buf[i] = 0;
            }
        }
    }

    pub fn playback_position(&self) -> usize {
        self.grain_position
    }
}
