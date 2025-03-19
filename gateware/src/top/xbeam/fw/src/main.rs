#![no_std]
#![no_main]

use critical_section::Mutex;
use core::convert::TryInto;
use log::info;
use riscv_rt::entry;
use irq::handler;
use core::cell::RefCell;

use tiliqua_fw::*;
use tiliqua_lib::*;
use pac::constants::*;
use tiliqua_lib::calibration::*;
use tiliqua_hal::video::Video;

use embedded_graphics::{
    pixelcolor::{Gray8, GrayColor},
    prelude::*,
};

use options::*;
use hal::pca9635::Pca9635Driver;

tiliqua_hal::impl_dma_display!(DMADisplay, H_ACTIVE, V_ACTIVE, VIDEO_ROTATE_90);

pub const TIMER0_ISR_PERIOD_MS: u32 = 5;

struct App {
    ui: ui::UI<Encoder0, EurorackPmod0, I2c0, Opts>,
}

impl App {
    pub fn new(opts: Opts) -> Self {
        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
        Self {
            ui: ui::UI::new(opts, TIMER0_ISR_PERIOD_MS,
                            encoder, pca9635, pmod),
        }
    }
}

fn timer0_handler(app: &Mutex<RefCell<App>>) {
    critical_section::with(|cs| {
        let mut app = app.borrow_ref_mut(cs);
        app.ui.update();
    });
}

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    let sysclk = pac::clock::sysclk();
    let serial = Serial0::new(peripherals.UART0);
    let mut timer = Timer0::new(peripherals.TIMER0, sysclk);
    let mut video = Video0::new(peripherals.VIDEO_PERIPH);
    let mut display = DMADisplay {
        framebuffer_base: PSRAM_FB_BASE as *mut u32,
    };

    tiliqua_fw::handlers::logger_init(serial);

    info!("Hello from Tiliqua XBEAM!");

    let mut i2cdev1 = I2c1::new(peripherals.I2C1);
    let mut pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
    CalibrationConstants::load_or_default(&mut i2cdev1, &mut pmod);

    let opts = Opts::default();
    let mut last_palette = opts.beam.palette.value;
    let app = Mutex::new(RefCell::new(App::new(opts)));

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        let vscope  = peripherals.VECTOR_PERIPH;
        let scope  = peripherals.SCOPE_PERIPH;
        let mut first = true;

        loop {

            let (opts, draw_options) = critical_section::with(|cs| {
                let ui = &app.borrow_ref(cs).ui;
                (ui.opts.clone(), ui.draw()) 
            });

            if opts.beam.palette.value != last_palette || first {
                opts.beam.palette.value.write_to_hardware(&mut video);
                last_palette = opts.beam.palette.value;
            }

            if draw_options {
                draw::draw_options(&mut display, &opts, H_ACTIVE-200, V_ACTIVE/2, opts.beam.hue.value).ok();
                draw::draw_name(&mut display, H_ACTIVE/2, V_ACTIVE-50, opts.beam.hue.value, UI_NAME, UI_SHA).ok();
            }

            video.set_persist(opts.beam.persist.value);
            video.set_decay(opts.beam.decay.value);

            vscope.hue().write(|w| unsafe { w.hue().bits(opts.beam.hue.value) } );
            vscope.intensity().write(|w| unsafe { w.intensity().bits(opts.beam.intensity.value) } );
            vscope.xscale().write(|w| unsafe { w.xscale().bits(opts.vector.xscale.value) } );
            vscope.yscale().write(|w| unsafe { w.yscale().bits(opts.vector.yscale.value) } );

            scope.hue().write(|w| unsafe { w.hue().bits(opts.beam.hue.value) } );
            scope.intensity().write(|w| unsafe { w.intensity().bits(opts.beam.intensity.value) } );

            scope.trigger_lvl().write(|w| unsafe { w.trigger_level().bits(opts.scope.trig_lvl.value as u16) } );
            scope.xscale().write(|w| unsafe { w.xscale().bits(opts.scope.xscale.value) } );
            scope.yscale().write(|w| unsafe { w.yscale().bits(opts.scope.yscale.value) } );
            scope.timebase().write(|w| unsafe { w.timebase().bits(opts.scope.timebase.value) } );

            scope.ypos0().write(|w| unsafe { w.ypos().bits(opts.scope.ypos0.value as u16) } );
            scope.ypos1().write(|w| unsafe { w.ypos().bits(opts.scope.ypos1.value as u16) } );
            scope.ypos2().write(|w| unsafe { w.ypos().bits(opts.scope.ypos2.value as u16) } );
            scope.ypos3().write(|w| unsafe { w.ypos().bits(opts.scope.ypos3.value as u16) } );

            scope.trigger_always().write(
                |w| w.trigger_always().bit(opts.scope.trig_mode.value == TriggerMode::Always) );

            if opts.tracker.page.value == Page::Vector {
                scope.en().write(|w| w.enable().bit(false) );
                vscope.en().write(|w| w.enable().bit(true) );
            }

            if opts.tracker.page.value == Page::Scope {
                scope.en().write(|w| w.enable().bit(true) );
                vscope.en().write(|w| w.enable().bit(false) );
            }

            first = false;
        }
    })
}
