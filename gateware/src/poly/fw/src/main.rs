#![no_std]
#![no_main]

use tiliqua_pac as pac;
use tiliqua_hal as hal;

use hal::hal::delay::DelayNs;

use tiliqua_fw::Serial0;
use tiliqua_fw::Timer0;
use tiliqua_fw::I2c0;
use tiliqua_fw::Encoder0;
use tiliqua_fw::EurorackPmod0;
use tiliqua_fw::Polysynth0;

use log::info;

use riscv_rt::entry;

use tiliqua_hal::pca9635::*;

use core::convert::TryInto;

use embedded_graphics::{
    pixelcolor::{Gray8, GrayColor},
    prelude::*,
};

use tiliqua_fw::opts;
use tiliqua_fw::opts::ControlInterface;

use tiliqua_lib::draw;

use tiliqua_lib::opt::*;

use tiliqua_lib::generated_constants::*;

use fixed::{FixedI32, types::extra::U16};

use micromath::F32Ext;

/// Fixed point DSP below should use 32-bit integers with a 16.16 split.
/// This could be made generic below, but isn't to reduce noise...
pub type Fix = FixedI32<U16>;

struct OnePoleSmoother {
    y_k1: Fix,
}

impl OnePoleSmoother {
    fn new() -> Self {
        OnePoleSmoother {
            y_k1: Fix::from_num(0),
        }
    }

    fn proc(&mut self, x_k: Fix) -> Fix {
        self.y_k1 = self.y_k1 * Fix::from_num(0.95f32) + x_k * Fix::from_num(0.05f32);
        self.y_k1
    }
}

tiliqua_hal::impl_dma_display!(DMADisplay, H_ACTIVE, V_ACTIVE, VIDEO_ROTATE_90);

const PCA9635_BAR_GREEN: [usize; 6] = [0, 2, 14, 12, 6, 4];
const PCA9635_BAR_RED:   [usize; 6] = [1, 3, 15, 13, 7, 5];
const _PCA9635_MIDI:     [usize; 2] = [8, 9];

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    // initialize logging
    let serial = Serial0::new(peripherals.UART);
    tiliqua_fw::handlers::logger_init(serial);

    let sysclk = pac::clock::sysclk();
    let mut timer = Timer0::new(peripherals.TIMER, sysclk);

    info!("Hello from Tiliqua XBEAM!");

    let i2cdev = I2c0::new(peripherals.I2C0);

    let mut pca9635 = Pca9635Driver::new(i2cdev);

    let mut encoder = Encoder0::new(peripherals.ENCODER0);

    let mut display = DMADisplay {
        framebuffer_base: PSRAM_FB_BASE as *mut u32,
    };

    // Must flush the dcache for framebuffer writes to go through
    // TODO: put the framebuffer in the DMA section of Vex address space?
    let pause_flush = |timer: &mut Timer0, uptime_ms: &mut u32, period_ms: u32| {
        timer.delay_ms(period_ms);
        *uptime_ms += period_ms;
        pac::cpu::vexriscv::flush_dcache();
    };

    let mut uptime_ms = 0u32;
    let period_ms = 5u32;

    let mut opts = opts::Options::new();

    let vs = peripherals.VS_PERIPH;

    let mut synth = Polysynth0::new(peripherals.SYNTH_PERIPH);

    let mut pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);

    let mut toggle_encoder_leds = false;

    let mut time_since_encoder_touched: u32 = 0;

    let mut drive_smoother = OnePoleSmoother::new();

    let mut reso_smoother = OnePoleSmoother::new();

    let mut diffusion_smoother = OnePoleSmoother::new();

    loop {

        if time_since_encoder_touched < 1000 || opts.modify() {

            draw::draw_options(&mut display, &opts, H_ACTIVE-200, V_ACTIVE/2, opts.xbeam.hue.value).ok();

        }

        pause_flush(&mut timer, &mut uptime_ms, period_ms);

        encoder.update();

        time_since_encoder_touched += period_ms;

        match encoder.poke_ticks() {
            1 => {
                opts.tick_up();
                time_since_encoder_touched = 0;
            }
            -1 => {
                opts.tick_down();
                time_since_encoder_touched = 0;
            }
            _ => {},
        }

        if encoder.poke_btn() {
            opts.toggle_modify();
            time_since_encoder_touched = 0;
        }

        vs.persist().write(|w| unsafe { w.persist().bits(opts.xbeam.persist.value) } );
        vs.hue().write(|w| unsafe { w.hue().bits(opts.xbeam.hue.value) } );
        vs.intensity().write(|w| unsafe { w.intensity().bits(opts.xbeam.intensity.value) } );
        vs.decay().write(|w| unsafe { w.decay().bits(opts.xbeam.decay.value) } );
        vs.scale().write(|w| unsafe { w.scale().bits(opts.xbeam.scale.value) } );

        let drive_smooth = drive_smoother.proc(Fix::from_bits(opts.poly.drive.value as i32)).to_bits() as u16;
        synth.set_drive(drive_smooth);

        let reso_smooth = reso_smoother.proc(Fix::from_bits(opts.poly.reso.value as i32)).to_bits() as u16;
        synth.set_reso(reso_smooth);

        let diffuse_smooth = diffusion_smoother.proc(Fix::from_bits(opts.poly.diffuse.value as i32)).to_bits() as u16;
        let coeff_dry: i32 = (32768 - diffuse_smooth) as i32;
        let coeff_wet: i32 = diffuse_smooth as i32;

        synth.set_matrix_coefficient(0, 0, coeff_dry);
        synth.set_matrix_coefficient(1, 1, coeff_dry);
        synth.set_matrix_coefficient(2, 2, coeff_dry);
        synth.set_matrix_coefficient(3, 3, coeff_dry);

        synth.set_matrix_coefficient(0, 4, coeff_wet);
        synth.set_matrix_coefficient(1, 5, coeff_wet);
        synth.set_matrix_coefficient(2, 6, coeff_wet);
        synth.set_matrix_coefficient(3, 7, coeff_wet);

        synth.set_touch_control(opts.poly.interface.value == ControlInterface::Touch);

        let notes = synth.voice_notes();
        let cutoffs = synth.voice_cutoffs();

        let n_voices = 8;
        for ix in 0usize..8usize {
            /*
            draw::draw_voice(&mut display, 100, 100 + (ix as u32) * (V_ACTIVE-200) / n_voices,
                             notes[ix], cutoffs[ix], opts.xbeam.hue.value).ok();
            */
            let j = 7-ix;
            draw::draw_voice(&mut display,
                             ((H_ACTIVE as f32)/2.0f32 + 330.0f32*f32::cos(2.3f32 + 2.0f32 * j as f32 / 8.0f32)) as i32,
                             ((V_ACTIVE as f32)/2.0f32 + 330.0f32*f32::sin(2.3f32 + 2.0f32 * j as f32 / 8.0f32)) as u32 - 15,
                             notes[ix], cutoffs[ix], opts.xbeam.hue.value).ok();
        }

        for n in 0..16 {
            pca9635.leds[n] = 0u8;
        }

        if uptime_ms % 50 == 0 {
            toggle_encoder_leds = !toggle_encoder_leds;
        }

        if let Some(n) = opts.view().selected() {
            let o = opts.view().options()[n];
            let c = o.percent();
            for n in 0..6 {
                if ((n as f32)*0.5f32/6.0f32 + 0.5) < c {
                    pca9635.leds[PCA9635_BAR_RED[n]] = 0xff as u8;
                } else {
                    pca9635.leds[PCA9635_BAR_RED[n]] = 0 as u8;
                }
                if ((n as f32)*-0.5f32/6.0f32 + 0.5) > c {
                    pca9635.leds[PCA9635_BAR_GREEN[n]] = 0xff as u8;
                } else {
                    pca9635.leds[PCA9635_BAR_GREEN[n]] = 0 as u8;
                }
            }

            if opts.modify() && !toggle_encoder_leds {
                for n in 0..6 {
                    pca9635.leds[PCA9635_BAR_GREEN[n]] = 0 as u8;
                    pca9635.leds[PCA9635_BAR_RED[n]] = 0 as u8;
                }
            }
        }

        if opts.modify() {
            if toggle_encoder_leds {
                if let Some(n) = opts.view().selected() {
                    pmod.led_set_manual(n, i8::MAX);
                }
            } else {
                pmod.led_all_auto();
            }
        } else {
            if time_since_encoder_touched < 1000 {
                for n in 0..8 {
                    pmod.led_set_manual(n, 0i8);
                }
                if let Some(n) = opts.view().selected() {
                    pmod.led_set_manual(n, (((1000-time_since_encoder_touched) * 120) / 1000) as i8);
                }
            } else {
                pmod.led_all_auto();

                // output touches on 4/5  aren't automatically routed to LEDs by eurorack-pmod gateware.
                if opts.poly.interface.value == ControlInterface::Touch {
                    let touch = pmod.touch();
                    pmod.led_set_manual(4,(touch[4]>>2) as i8);
                    pmod.led_set_manual(5,(touch[5]>>2) as i8);
                }
            }
        }



        pca9635.push().ok();
    }
}
