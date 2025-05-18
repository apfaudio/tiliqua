#![no_std]
#![no_main]

use critical_section::Mutex;
use log::info;
use riscv_rt::entry;
use irq::handler;
use core::cell::RefCell;

use tiliqua_fw::*;
use tiliqua_lib::*;
use pac::constants::*;
use tiliqua_lib::calibration::*;

use embedded_graphics::prelude::*;

use options::*;
use hal::pca9635::Pca9635Driver;
use tiliqua_hal::persist::Persist;
use tiliqua_hal::dma_framebuffer::Rotate;

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
    let mut persist = Persist0::new(peripherals.PERSIST_PERIPH);

    tiliqua_fw::handlers::logger_init(serial);

    info!("Hello from Tiliqua XBEAM!");

    let bootinfo = unsafe { bootinfo::BootInfo::from_addr(BOOTINFO_BASE) };
    let modeline = bootinfo.modeline.maybe_override_fixed(
        FIXED_MODELINE, CLOCK_DVI_HZ);
    let mut display = DMAFramebuffer0::new(
        peripherals.FRAMEBUFFER_PERIPH,
        peripherals.PALETTE_PERIPH,
        PSRAM_FB_BASE,
        modeline.clone(),
    );

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

        let vscope    = peripherals.VECTOR_PERIPH;
        let scope     = peripherals.SCOPE_PERIPH;
        let xbeam_mux = peripherals.XBEAM_PERIPH;
        let mut first = true;

        let h_active = display.size().width;
        let v_active = display.size().height;

        loop {

            let (opts, draw_options) = critical_section::with(|cs| {
                let ui = &app.borrow_ref(cs).ui;
                (ui.opts.clone(), ui.draw()) 
            });

            if opts.beam.palette.value != last_palette || first {
                opts.beam.palette.value.write_to_hardware(&mut display);
                last_palette = opts.beam.palette.value;
            }

            if draw_options {
                draw::draw_options(&mut display, &opts, h_active-200, v_active/2, opts.beam.hue.value).ok();
                draw::draw_name(&mut display, h_active/2, v_active-50, opts.beam.hue.value, UI_NAME, UI_SHA,
                                &modeline).ok();
            }

            persist.set_persist(opts.beam.persist.value);
            persist.set_decay(opts.beam.decay.value);

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

            xbeam_mux.flags().write(
                |w| { w.usb_bypass().bit(opts.usb.mode.value == USBMode::Bypass);
                      w.show_outputs().bit(opts.usb.show.value == Show::Outputs)
                } );

            if opts.tracker.page.value == Page::Vector {
                scope.flags().write(
                    |w| w.enable().bit(false) );
                vscope.flags().write(
                    |w| { w.enable().bit(true);
                          w.rotate_left().bit(modeline.rotate == Rotate::Left)
                    } );
            }

            if opts.tracker.page.value == Page::Scope || first {
                scope.flags().write(
                    |w| { w.enable().bit(true);
                          w.rotate_left().bit(modeline.rotate == Rotate::Left);
                          w.trigger_always().bit(opts.scope.trig_mode.value == TriggerMode::Always)
                    } );
                vscope.flags().write(
                    |w| w.enable().bit(false) );
            }

            first = false;
        }
    })
}
