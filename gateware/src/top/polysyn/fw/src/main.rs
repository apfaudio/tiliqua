#![no_std]
#![no_main]

use critical_section::Mutex;
use log::{info, warn};
use riscv_rt::entry;
use irq::handler;
use core::cell::RefCell;

use micromath::F32Ext;
use midi_types::*;
use midi_convert::render_slice::MidiRenderSlice;

use tiliqua_pac as pac;
use tiliqua_hal as hal;
use tiliqua_lib::*;
use tiliqua_lib::draw;
use tiliqua_lib::dsp::OnePoleSmoother;
use tiliqua_lib::midi::MidiTouchController;
use pac::constants::*;
use tiliqua_hal::persist::Persist;
use tiliqua_fw::*;
use tiliqua_fw::options::*;
use tiliqua_hal::pmod::EurorackPmod;

use tiliqua_hal::embedded_graphics::prelude::*;

use opts::persistence::*;
use hal::pca9635::Pca9635Driver;

pub const TIMER0_ISR_PERIOD_MS: u32 = 5;

fn timer0_handler(app: &Mutex<RefCell<App>>) {

    critical_section::with(|cs| {

        let mut app = app.borrow_ref_mut(cs);

        //
        // Update UI and options
        //

        app.ui.update();
        let opts = app.ui.opts.clone();

        //
        // Check for TRS/USB MIDI traffic
        // (this is forwarded by the hardware to the synth
        //  for minimum possible latency, here we peek
        //  the FIFO contents for debugging purposes)
        //

        let midi_word = app.synth.midi_read();
        if midi_word != 0 {
            // Blink MIDI activity LED on TRS port
            app.ui.midi_activity();
            // Optionally dump raw MIDI messages out serial port.
            if opts.misc.serial_debug.value == UsbMidiSerialDebug::On {
                info!("midi: 0x{:x} 0x{:x} 0x{:x}",
                      midi_word&0xff,
                      (midi_word>>8)&0xff,
                      (midi_word>>16)&0xff);
            }
        }

        //
        // Update synthesizer
        //

        let drive_smooth = app.drive_smoother.proc_u16(opts.poly.drive.value);
        app.synth.set_drive(drive_smooth);

        let reso_smooth = app.reso_smoother.proc_u16(opts.poly.reso.value);
        app.synth.set_reso(reso_smooth);

        let diffuse_smooth = app.diffusion_smoother.proc_u16(opts.poly.diffuse.value);
        let coeff_dry: i32 = (32768 - diffuse_smooth) as i32;
        let coeff_wet: i32 = diffuse_smooth as i32;

        app.synth.set_matrix_coefficient(0, 0, coeff_dry);
        app.synth.set_matrix_coefficient(1, 1, coeff_dry);
        app.synth.set_matrix_coefficient(2, 2, coeff_dry);
        app.synth.set_matrix_coefficient(3, 3, coeff_dry);

        app.synth.set_matrix_coefficient(0, 4, coeff_wet);
        app.synth.set_matrix_coefficient(1, 5, coeff_wet);
        app.synth.set_matrix_coefficient(2, 6, coeff_wet);
        app.synth.set_matrix_coefficient(3, 7, coeff_wet);


        // Touch controller logic (sends MIDI to internal polysynth)
        if opts.poly.touch_control.value == TouchControl::On {
            app.ui.touch_led_mask(0b00111111);
            let touch = app.ui.pmod.touch();
            let jack = app.ui.pmod.jack();
            let msgs = app.touch_controller.update(&touch, jack);
            for msg in msgs {
                if msg != MidiMessage::Stop {
                    // TODO move MidiMessage rendering into HAL, perhaps
                    // even inside synth.midi_write.
                    let mut bytes = [0u8; 3];
                    msg.render_slice(&mut bytes);
                    let v: u32 = (bytes[2] as u32) << 16 |
                                 (bytes[1] as u32) << 8 |
                                 (bytes[0] as u32) << 0;
                    app.synth.midi_write(v);
                }
            }
        }

        app.synth.usb_midi_host(opts.misc.host.value == UsbHost::Enable,
                                opts.misc.cfg_id.value,
                                opts.misc.endpt_id.value);
    });
}

struct App {
    ui: ui::UI<Encoder0, EurorackPmod0, I2c0, Opts>,
    synth: Polysynth0,
    drive_smoother: OnePoleSmoother,
    reso_smoother: OnePoleSmoother,
    diffusion_smoother: OnePoleSmoother,
    touch_controller: MidiTouchController,
}

impl App {
    pub fn new(opts: Opts) -> Self {
        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        let synth = Polysynth0::new(peripherals.SYNTH_PERIPH);
        let drive_smoother = OnePoleSmoother::new(0.05f32);
        let reso_smoother = OnePoleSmoother::new(0.05f32);
        let diffusion_smoother = OnePoleSmoother::new(0.05f32);
        let touch_controller = MidiTouchController::new();
        Self {
            ui: ui::UI::new(opts, TIMER0_ISR_PERIOD_MS,
                            encoder, pca9635, pmod),
            synth,
            drive_smoother,
            reso_smoother,
            diffusion_smoother,
            touch_controller,
        }
    }
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
    crate::handlers::logger_init(serial);

    info!("Hello from Tiliqua POLYSYN!");

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
    calibration::CalibrationConstants::load_or_default(&mut i2cdev1, &mut pmod);

    use tiliqua_hal::cy8cmbr3xxx::Cy8cmbr3108Driver;
    let i2cdev_cy8 = I2c1::new(unsafe { pac::I2C1::steal() } );
    let mut cy8 = Cy8cmbr3108Driver::new(i2cdev_cy8, &TOUCH_SENSOR_ORDER);

    //
    // Create options and maybe load from persistent storage
    //

    let mut opts = Opts::default();
    let mut flash_persist_opt = if let Some(storage_window) = bootinfo.manifest.get_option_storage_window() {
        let mut flash_persist = FlashOptionsPersistence::new(spiflash, storage_window);
        flash_persist.load_options(&mut opts).unwrap();
        Some(flash_persist)
    } else {
        warn!("No option storage region: disable persistent storage");
        None
    };

    //
    // Configure TUSB322 (CC controller) in DFP/Host mode
    // This is needed if Tiliqua is connected to a device with a true USB-C to USB-C cable.
    //
    // TODO: make this dynamic or disable when host mode is disabled?
    // TODO: move this into HAL layer!
    //

    use embedded_hal::i2c::{I2c, Operation};
    const TUSB322I_ADDR:  u8 = 0x47;
    let mut i2cdev = I2c0::new(peripherals.I2C0);
    // DISABLE_TERM
    let _ = i2cdev.transaction(TUSB322I_ADDR, &mut [Operation::Write(&[0x0Au8, 0x01u8])]);
    // MODE_SELECT=DFP | DISABLE_TERM
    let _ = i2cdev.transaction(TUSB322I_ADDR, &mut [Operation::Write(&[0x0Au8, 0x21u8])]);
    // MODE_SELECT=DFP | ~DISABLE_TERM
    let _ = i2cdev.transaction(TUSB322I_ADDR, &mut [Operation::Write(&[0x0Au8, 0x20u8])]);

    //
    // Create App instance
    //

    let mut last_palette = opts.beam.palette.value.clone();
    let app = Mutex::new(RefCell::new(App::new(opts)));

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        let vscope  = peripherals.VECTOR_PERIPH;
        let mut first = true;

        let h_active = display.size().width;
        let v_active = display.size().height;

        let mut last_jack = pmod.jack();

        loop {


            let (opts, notes, cutoffs, draw_options, save_opts, wipe_opts) = critical_section::with(|cs| {
                let mut app = app.borrow_ref_mut(cs);
                if pmod.jack() != last_jack {
                    // Re-calibrate touch sensing on jack swaps.
                    let _ = cy8.reset();
                }
                last_jack = pmod.jack();
                let save_opts = app.ui.opts.misc.save_opts.poll();
                let wipe_opts = app.ui.opts.misc.wipe_opts.poll();
                (app.ui.opts.clone(),
                 app.synth.voice_notes().clone(),
                 app.synth.voice_cutoffs().clone(),
                 app.ui.draw(),
                 save_opts,
                 wipe_opts)
            });

            if save_opts {
                if let Some(ref mut flash_persist) = flash_persist_opt {
                    flash_persist.save_options(&opts).unwrap();
                }
            }

            if wipe_opts {
                critical_section::with(|cs| {
                    let mut app = app.borrow_ref_mut(cs);
                    app.ui.opts = Opts::default();
                    if let Some(ref mut flash_persist) = flash_persist_opt {
                        flash_persist.erase_all().unwrap();
                    }
                });
            }

            let help_screen: bool = opts.tracker.page.value == Page::Help;

            if opts.beam.palette.value != last_palette || first {
                opts.beam.palette.value.write_to_hardware(&mut display);
                last_palette = opts.beam.palette.value;
            }

            if draw_options || help_screen {
                draw::draw_options(&mut display, &opts, h_active/2-30, 70,
                                   opts.beam.hue.value).ok();
                draw::draw_name(&mut display, h_active/2, 30, opts.beam.hue.value, UI_NAME, UI_SHA,
                                &modeline).ok();
            }

            if help_screen {
                draw::draw_tiliqua(&mut display, h_active/2-80, v_active/2-200, opts.beam.hue.value,
                    [
                        "C2     phase",
                        "G2     -    ",
                        "C3     -    ",
                        "Eb3    -    ",
                        "G3     -    ",
                        "C4     -    ",
                        "-      out L",
                        "-      out R",
                    ],
                    [
                        "menu",
                        "-",
                        "video",
                        "-",
                        "-",
                        "midi notes (+mod, +pitch)",
                    ],
                    "[8-voice polyphonic synthesizer]",
                    "The synthesizer can be controlled by touching\n\
                    jacks 0-5 or using a MIDI keyboard through TRS\n\
                    midi. Control source is selected in the menu.\n\
                    \n\
                    In touch mode, the touch magnitude controls the\n\
                    filter envelopes of each voice. In MIDI mode\n\
                    the velocity of each note as well as the value\n\
                    of the modulation wheel affects the filter\n\
                    envelopes.\n\
                    \n\
                    Output audio is sent to output channels 2 and\n\
                    3 (last 2 jacks). Input jack 0 also controls\n\
                    phase modulation of all oscillators, so you\n\
                    can patch input jack 0 to an LFO for retro-sounding\n\
                    slow vibrato, or to an oscillator for some wierd\n\
                    FM effects.\n\
                    \n\
                    * Use encoder and encoder button to navigate menu.\n\
                    * Switch away from the HELP screen to start visuals.\n\
                    * Hold encoder for 3sec to enter bootloader.\n\
                    ",
                    ).ok();
                // Enough persistance to reduce flicker on loads of text.
                persist.set_persist(512);
                persist.set_decay(1);
                vscope.flags().write(
                    |w| { w.enable().bit(false) } );
            } else {
                persist.set_persist(opts.beam.persist.value);
                persist.set_decay(opts.beam.decay.value);
                vscope.flags().write(
                    |w| w.enable().bit(true) );
            }

            vscope.hue().write(|w| unsafe { w.hue().bits(opts.beam.hue.value) } );
            vscope.intensity().write(|w| unsafe { w.intensity().bits(opts.beam.intensity.value) } );
            vscope.xscale().write(|w| unsafe { w.scale().bits(opts.vector.xscale.value) } );
            vscope.yscale().write(|w| unsafe { w.scale().bits(opts.vector.yscale.value) } );

            if !help_screen {
                for ix in 0usize..N_VOICES {
                    let j = (N_VOICES-1)-ix;
                    draw::draw_voice(&mut display,
                                     ((h_active as f32)/2.0f32 + 330.0f32*f32::cos(2.3f32 + 2.0f32 * j as f32 / (N_VOICES as f32))) as i32,
                                     ((v_active as f32)/2.0f32 + 330.0f32*f32::sin(2.3f32 + 2.0f32 * j as f32 / (N_VOICES as f32))) as u32 - 15,
                                     notes[ix], cutoffs[ix], opts.beam.hue.value).ok();
                }
            }

            first = false;
        }
    })
}
