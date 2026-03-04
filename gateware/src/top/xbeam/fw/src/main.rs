#![no_std]
#![no_main]

use critical_section::Mutex;
use log::{info, warn};
use riscv_rt::entry;
use irq::handler;
use core::cell::RefCell;

use tiliqua_fw::*;
use tiliqua_lib::*;
use pac::constants::*;
use tiliqua_lib::calibration::*;

use tiliqua_hal::embedded_graphics::prelude::*;

use options::*;
use opts::persistence::*;
use hal::pca9635::Pca9635Driver;
use tiliqua_hal::tusb322::{TUSB322Driver, TUSB322Mode, AttachedState};
use tiliqua_hal::persist::Persist;

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
        if app.ui.opts.misc.help.value == HelpPage::Off
            && app.ui.opts.tracker.page.value == Page::Help {
            app.ui.opts.tracker.page.value = Page::Vector;
        }
        app.ui.opts.misc.plot_type.value = match app.ui.opts.tracker.page.value {
            Page::Vector => PlotType::Vector,
            Page::Scope1 => PlotType::Scope,
            Page::Scope2 => PlotType::Scope,
            _ => app.ui.opts.misc.plot_type.value
        };
    });
}

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let sysclk = pac::clock::sysclk();
    let serial = Serial0::new(peripherals.UART0);
    let mut timer = Timer0::new(peripherals.TIMER0, sysclk);
    let mut persist = Persist0::new(peripherals.PERSIST_PERIPH);
    let spiflash = SPIFlash0::new(
        peripherals.SPIFLASH_CTRL,
        SPIFLASH_BASE,
        SPIFLASH_SZ_BYTES
    );

    tiliqua_fw::handlers::logger_init(serial);

    info!("Hello from Tiliqua XBEAM!");

    let bootinfo = unsafe { bootinfo::BootInfo::from_addr(BOOTINFO_BASE) }.unwrap();
    let modeline = bootinfo.modeline.maybe_override_fixed(
        FIXED_MODELINE, CLOCK_DVI_HZ);
    let mut display = DMAFramebuffer0::new(
        peripherals.FRAMEBUFFER_PERIPH,
        peripherals.PALETTE_PERIPH,
        peripherals.BLIT,
        peripherals.PIXEL_PLOT,
        peripherals.LINE,
        PSRAM_FB_BASE,
        modeline.clone(),
        BLIT_MEM_BASE,
    );

    let mut i2cdev1 = I2c1::new(peripherals.I2C1);
    let mut pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
    CalibrationConstants::load_or_default(&mut i2cdev1, &mut pmod);

    #[cfg(expander_ex0)]
    {
        info!("Loading calibration for expander EX0...");
        let mut i2c_ex0 = I2cEx0::new(peripherals.I2C2);
        let mut ex0_pmod = EurorackPmodEx0::new(peripherals.EX0_PMOD_PERIPH);
        CalibrationConstants::load_or_default(&mut i2c_ex0, &mut ex0_pmod);
    }

    #[cfg(expander_ex1)]
    {
        info!("Loading calibration for expander EX1...");
        let mut i2c_ex1 = I2cEx1::new(peripherals.I2C3);
        let mut ex1_pmod = EurorackPmodEx1::new(peripherals.EX1_PMOD_PERIPH);
        CalibrationConstants::load_or_default(&mut i2c_ex1, &mut ex1_pmod);
    }

    //
    // Start up TUSB322 in UFP/Device mode
    //

    let i2cdev_tusb = I2c0::new(unsafe { pac::I2C0::steal() } );
    let mut tusb322 = TUSB322Driver::new(i2cdev_tusb);
    tusb322.soft_reset().ok();
    tusb322.set_mode(TUSB322Mode::Ufp).ok();

    //
    // Create options and maybe load from persistent storage
    //

    let mut opts = Opts::default();
    opts.misc.rotation.value = modeline.rotate.clone();
    let mut flash_persist_opt = if let Some(storage_window) = bootinfo.manifest.get_option_storage_window() {
        let mut flash_persist = FlashOptionsPersistence::new(spiflash, storage_window);
        flash_persist.load_options(&mut opts).unwrap();
        Some(flash_persist)
    } else {
        warn!("No option storage region: disable persistent storage");
        None
    };

    //
    // Create App instance
    //

    let mut last_palette = opts.beam.palette.value;
    let app = Mutex::new(RefCell::new(App::new(opts)));

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        let mut vscope = Vector0::new(peripherals.VECTOR_PERIPH);
        let mut scope = Scope0::new(peripherals.SCOPE_PERIPH, 6);
        let xbeam_mux = peripherals.XBEAM_PERIPH;
        let overlay_periph = peripherals.OVERLAY_PERIPH;
        let mut first = true;

        let mut usb_cc_attached = false;

        // Grid overlay configuration (ppd is constant after init)
        let (ppd_x, ppd_y) = vscope.pixels_per_div();
        overlay_periph.grid_spacing().write(|w| unsafe {
            w.spacing_x().bits(ppd_x as u8);
            w.spacing_y().bits(ppd_y as u8)
        });
        overlay_periph.grid_start().write(|w| unsafe {
            w.start_x().bits(((display.size().width / 2) % ppd_x) as u8);
            w.start_y().bits((((display.size().height / 2) + 1) % ppd_y) as u8)
        });
        overlay_periph.grid_offset().write(|w| unsafe {
            w.offset_x().bits((display.size().width / 2) as u16);
            w.offset_y().bits((display.size().height / 2) as u16)
        });

        loop {

            let h_active = display.size().width;
            let v_active = display.size().height;

            let (opts, draw_options, save_opts, wipe_opts) = critical_section::with(|cs| {
                let mut app = app.borrow_ref_mut(cs);
                let save_opts = app.ui.opts.misc.save_opts.poll();
                let wipe_opts = app.ui.opts.misc.wipe_opts.poll();
                (app.ui.opts.clone(), app.ui.draw(), save_opts, wipe_opts)
            });

            let on_help_page = opts.tracker.page.value == Page::Help;

            if opts.beam.palette.value != last_palette || first {
                opts.beam.palette.value.write_to_hardware(&mut display);
                last_palette = opts.beam.palette.value;
            }

            if draw_options || on_help_page {
                let (x, y) = if on_help_page {
                    (h_active/2-30, v_active-100)
                } else {
                    (h_active-200, v_active/2)
                };
                draw::draw_options(&mut display, &opts, x, y, opts.beam.ui_hue.value).ok();
                draw::draw_name(&mut display, h_active/2, v_active-50, opts.beam.ui_hue.value,
                                &bootinfo.manifest.name, &bootinfo.manifest.tag, &modeline).ok();
            }

            if on_help_page {
                draw::draw_help_page(&mut display,
                    MODULE_DOCSTRING,
                    bootinfo.manifest.help.as_ref(),
                    h_active,
                    v_active,
                    opts.help.scroll.value,
                    opts.beam.ui_hue.value).ok();
                persist.set_persist(256);
                persist.set_decay(1);
            } else {
                persist.set_persist(opts.beam.persist.value);
                persist.set_decay(opts.beam.decay.value);
            }


            if save_opts {
                if let Some(ref mut flash_persist) = flash_persist_opt {
                    flash_persist.save_options(&opts).unwrap();
                }
            }

            if wipe_opts {
                critical_section::with(|cs| {
                    let mut app = app.borrow_ref_mut(cs);
                    app.ui.opts = Opts::default();
                    app.ui.opts.misc.rotation.value = modeline.rotate.clone();
                    if let Some(ref mut flash_persist) = flash_persist_opt {
                        flash_persist.erase_all().unwrap();
                    }
                });
            }

            let (ppd_x, ppd_y) = vscope.pixels_per_div();
            vscope.set_xoffset_px(opts.vector.x_offset.value * (ppd_x / 4) as i16);
            vscope.set_yoffset_px(opts.vector.y_offset.value * (ppd_y / 4) as i16);
            vscope.set_xscale(opts.vector.x_scale.value);
            vscope.set_yscale(opts.vector.y_scale.value);
            vscope.set_pscale(opts.vector.i_scale.value);
            vscope.set_intensity(opts.vector.i_offset.value);
            vscope.set_cscale(opts.vector.c_scale.value);
            vscope.set_hue(opts.vector.c_offset.value);

            scope.set_hue(opts.scope2.hue.value);
            scope.set_intensity(opts.scope2.intensity.value);
            scope.set_trigger_level(opts.scope2.trig_lvl.value);
            scope.set_yscale(opts.scope2.yscale.value);
            scope.set_timebase(opts.scope2.timebase.value);
            let (_, sppd) = scope.pixels_per_div();
            let n_ch = opts.scope1.n_channels.value;
            let ypos = [opts.scope1.ypos0.value, opts.scope1.ypos1.value,
                         opts.scope1.ypos2.value, opts.scope1.ypos3.value];
            for ch in 0..4u8 {
                let pos = if ch < n_ch {
                    ypos[ch as usize] * (sppd / 4) as i16
                } else {
                    750 // hide inactive channels off-screen
                };
                scope.set_ypos_px(ch.into(), pos);
            }

            // Only connect USB PHY if the TUSB322 Type-C controller says we are attached.
            // This fixes enumeration issues on some machines when using typec <-> typec cables.
            critical_section::with(|_| {
                if let Ok(status) = tusb322.read_connection_status_control() {
                    // Only update on valid reads to reduce risk of unintended toggling mid-stream
                    let new_state = status.attached_state == AttachedState::AttachedSnk;
                    if new_state != usb_cc_attached {
                        info!("USB CC hotplug: {:?}", status);
                        usb_cc_attached = new_state;
                    }
                }
            });

            let plot_io_val: u8 = match opts.misc.plot_io.value {
                PlotIO::Builtin => 0,
                #[cfg(expander_ex0)]
                PlotIO::Ex0 => 1,
                #[cfg(expander_ex1)]
                PlotIO::Ex1 => 2,
            };

            xbeam_mux.flags().write(
                |w| { w.usb_en().bit(opts.misc.usb_mode.value == USBMode::Enable);
                      w.show_outputs().bit(opts.misc.plot_src.value == PlotSrc::Outputs);
                      w.usb_connect().bit(usb_cc_attached);
                      unsafe { w.plot_io().bits(plot_io_val) }
                } );

            // Grid overlay style/pixel (changes with options)
            let grid_style: u8 = if on_help_page { 0 } else {
                match opts.beam.grid.value {
                    GridOverlay::Off => 0,
                    GridOverlay::Grid => 1,
                    GridOverlay::Cross => 2,
                }
            };
            overlay_periph.flags().write(|w| unsafe {
                w.grid_style().bits(grid_style);
                w.grid_pixel().bits(((opts.beam.grid_i.value as u8) << 4) | opts.beam.ui_hue.value)
            });

            display.rotate(&opts.misc.rotation.value);


            if opts.tracker.page.value == Page::Help {
                scope.set_enabled(false, false);
                vscope.set_enabled(false);
            } else {
                if opts.misc.plot_type.value == PlotType::Vector {
                    scope.set_enabled(false, false);
                    vscope.set_enabled(true);
                } else {
                    scope.set_enabled(true, opts.scope2.trig_mode.value == TriggerMode::Always);
                    vscope.set_enabled(false);
                }
            }

            first = false;
        }
    })
}
