use fixed::{FixedI32, types::extra::U16};
use trig_const::{sin, exp};

use crate::Polysynth0;
use crate::options::{ProcMode, Waveform};

// Q16.16 fixed-point used for wavetable calculation / processing
pub type Fix32 = FixedI32<U16>;

pub const CYCLE_LEN: usize = 512;
const TANH_LUT_LEN: usize = 256;

// trig_const doesn't have a tanh for some reason
const fn const_tanh(x: f64) -> f64 {
    let e2x = exp(2.0 * x);
    (e2x - 1.0) / (e2x + 1.0)
}

static SINE_LUT: [Fix32; CYCLE_LEN] = {
    let mut lut = [Fix32::ZERO; CYCLE_LEN];
    let mut i = 0;
    while i < CYCLE_LEN {
        let t = i as f64 / CYCLE_LEN as f64 * 2.0 * core::f64::consts::PI;
        lut[i] = Fix32::from_bits((sin(t) * u16::MAX as f64) as i32);
        i += 1;
    }
    lut
};

static TANH_LUT: [Fix32; TANH_LUT_LEN] = {
    let mut lut = [Fix32::ZERO; TANH_LUT_LEN];
    let mut i = 0;
    while i < TANH_LUT_LEN {
        let x = i as f64 * 5.0 / TANH_LUT_LEN as f64;
        lut[i] = Fix32::from_bits((const_tanh(x) * u16::MAX as f64) as i32);
        i += 1;
    }
    lut
};


pub fn wt_sample(waveform: Waveform, i: usize, cl: usize) -> Fix32 {
    // phase from 0->1
    let phase = Fix32::from_num(i) / cl as i32;
    match waveform {
        Waveform::Saw => {
            phase * 2 - Fix32::ONE
        }
        Waveform::Tri => {
            if i < cl / 2 {
                phase * 4 - Fix32::ONE
            } else {
                Fix32::from_num(3) - phase * 4
            }
        }
        Waveform::Sine => SINE_LUT[i],
        Waveform::Square => {
            if i < cl / 2 { Fix32::ONE - Fix32::DELTA } else { -Fix32::ONE + Fix32::DELTA }
        }
        Waveform::Organ => {
            (SINE_LUT[i] * 10 + SINE_LUT[(i * 2) % cl] * 7
             + SINE_LUT[(i * 3) % cl] * 5 + SINE_LUT[(i * 4) % cl] * 3) / 25
        }
        Waveform::Pulse => {
            if i < cl / 4 { Fix32::ONE - Fix32::DELTA } else { -Fix32::ONE + Fix32::DELTA }
        }
        Waveform::Comb => {
            let mut s = Fix32::ZERO;
            let mut h = 1usize;
            while h <= 13 {
                s += SINE_LUT[(i * h) % cl];
                h += 1;
            }
            s / 13
        }
        Waveform::Formant => {
            SINE_LUT[(i * 4) % cl] * (Fix32::ONE - phase)
        }
        Waveform::OvSine => {
            Fix32::saturating_from_num(SINE_LUT[i] * 2)
        }
        Waveform::Strng => {
            let mut s = Fix32::ZERO;
            let mut amp = Fix32::ONE - Fix32::DELTA;
            let mut h = 1usize;
            while h <= 16 {
                s += amp * SINE_LUT[(i * h) % cl];
                amp = amp * 3 / 4;
                h += 1;
            }
            Fix32::saturating_from_num(s / 3)
        }
    }
}

pub fn wt_apply_proc(sample: Fix32, mode: ProcMode, proc_amt: Fix32) -> Fix32 {
    match mode {
        ProcMode::Off => sample,
        ProcMode::Sat => {
            let scaled = sample * proc_amt;
            let abs_scaled = scaled.abs();
            let idx = (abs_scaled * TANH_LUT_LEN as i32 / 5)
                .to_num::<usize>().min(TANH_LUT_LEN - 1);
            let val = TANH_LUT[idx];
            if scaled < 0 { -val } else { val }
        }
        ProcMode::Fold => {
            let scaled = sample * proc_amt;
            let phase = (scaled * 128).to_num::<i32>() as usize & (CYCLE_LEN - 1);
            SINE_LUT[phase]
        }
        ProcMode::Rect => {
            let scaled = sample * proc_amt / 2;
            scaled.abs().min(Fix32::ONE - Fix32::DELTA)
        }
        ProcMode::Crush => {
            let shift: u32 = (proc_amt * 3).to_num::<u32>() + 3;
            Fix32::from_bits((sample.to_bits() >> shift) << shift)
        }
    }
}


fn to_asq(v: Fix32) -> i16 {
    (v.to_bits() >> 1).clamp(i32::from(i16::MIN), i32::from(i16::MAX)) as i16
}

fn gain_from_amt(proc_amt: u16) -> Fix32 {
    Fix32::from_num(proc_amt) / 10
}

pub fn wt_preview(buf: &mut [i16], waveform: Waveform,
                  proc_mode: ProcMode, proc_amt: u16) {
    let gain = gain_from_amt(proc_amt);
    let cl = CYCLE_LEN;
    let len = buf.len();
    for i in 0..len {
        let idx = i * cl / len;
        let sample = wt_sample(waveform, idx, cl);
        buf[i] = to_asq(wt_apply_proc(sample, proc_mode, gain));
    }
}

pub fn wt_lfo(phase: &mut Fix32, phase_inc: Fix32, depth: Fix32, waveform: Waveform) -> i16 {
    let idx = phase.to_num::<usize>() % CYCLE_LEN;
    let sample = wt_sample(waveform, idx, CYCLE_LEN) * depth;
    *phase += phase_inc;
    let cycle_len = Fix32::from_num(CYCLE_LEN);
    if *phase >= cycle_len {
        *phase -= cycle_len;
    }
    to_asq(sample)
}

pub fn wt_write(synth: &mut Polysynth0, waveform: Waveform,
                proc_mode: ProcMode, proc_amt: u16) {
    let gain = gain_from_amt(proc_amt);
    for i in 0..CYCLE_LEN {
        let sample = wt_sample(waveform, i, CYCLE_LEN);
        let shaped = wt_apply_proc(sample, proc_mode, gain);
        synth.write_wavetable_sample(i as u16, to_asq(shaped));
    }
}
