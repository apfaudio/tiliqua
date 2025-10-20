// See top-level comment in 'top.py' for usage information.

#![no_std]
#![no_main]

use log::{info, warn};
use riscv_rt::entry;
use core::cell::RefCell;
use critical_section::Mutex;
use irq::handler;
use embedded_alloc::LlffHeap as Heap;
use mi_plaits_dsp::dsp::voice::{Modulations, Patch, Voice};
use tiliqua_hal::embedded_graphics::prelude::*;

use tiliqua_pac as pac;
use tiliqua_hal as hal;
use tiliqua_fw::*;
use tiliqua_lib::*;
use pac::constants::*;
use tiliqua_hal::persist::Persist;
use options::*;
use opts::persistence::*;
use hal::pca9635::*;

pub const TIMER0_ISR_PERIOD_MS: u32 = 5;
const BLOCK_SIZE: usize = 128;
// PSRAM heap for big audio buffers.
const HEAP_START: usize = PSRAM_BASE + (PSRAM_SZ_BYTES / 2);
const HEAP_SIZE: usize = 128*1024;

static HEAP: Heap = Heap::empty();

struct App<'a> {
    voice: Voice<'a>,
    patch: Patch,
    modulations: Modulations,
    ui: ui::UI<Encoder0, EurorackPmod0, I2c0, Opts>,
}

impl<'a> App<'a> {
    pub fn new(opts: Opts) -> Self {
        let mut voice = Voice::new(&HEAP, BLOCK_SIZE);
        let mut patch = Patch::default();

        patch.engine = 0;
        patch.harmonics = 0.5;
        patch.timbre = 0.5;
        patch.morph = 0.5;
        patch.timbre_modulation_amount = 0.5;
        patch.morph_modulation_amount  = 0.5;
        voice.init();

        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);

        Self {
            voice,
            patch,
            modulations: Modulations::default(),
            ui: ui::UI::new(opts, TIMER0_ISR_PERIOD_MS,
                            encoder, pca9635, pmod),
        }
    }
}

// TODO: move this to hardware as it is quite expensive.
#[inline(always)]
pub fn f32_to_i32(f: u32) -> i32 {
    let a = f & !0 >> 1; // Remove sign bit.
    if a < 127 << 23 { // >= 0, < 1
        0
    } else if a < 158 << 23 { // >= 1, < max
        let m = 1 << 31 | a << 8; // Mantissa and the implicit 1-bit.
        let s = 158 - (a >> 23); // Shift based on the exponent and bias.
        let u = (m >> s) as i32; // Unsigned result.
        if (f as i32) < 0 { -u } else { u }
    } else  { // >= max (incl. inf)
        if (f as i32) < 0 { i32::MIN } else { i32::MAX }
    }
}

fn timer0_handler(app: &Mutex<RefCell<App>>) {

    let peripherals = unsafe { pac::Peripherals::steal() };
    let audio_fifo = peripherals.AUDIO_FIFO;
    let pmod = peripherals.PMOD0_PERIPH;

    critical_section::with(|cs| {

        let mut app = app.borrow_ref_mut(cs);

        //
        // Update UI and options
        //

        app.ui.update();

        //
        // Page/option overrides
        //

        app.ui.opts.misc.plot_type.value = match app.ui.opts.tracker.page.value {
            Page::Vector => PlotType::Vector,
            Page::Scope => PlotType::Scope,
            _ => app.ui.opts.misc.plot_type.value
        };

        //
        // Patch settings from UI
        //

        let opts = app.ui.opts.clone();
        let mut patch = app.patch.clone();

        patch.engine    = opts.osc.engine.value as usize;
        patch.note      = opts.osc.note.value as f32;
        patch.harmonics = (opts.osc.harmonics.value as f32) / 256.0f32;
        patch.timbre    = (opts.osc.timbre.value as f32) / 256.0f32;
        patch.morph     = (opts.osc.morph.value as f32) / 256.0f32;

        //
        // Modulation sources from jacks
        //

        let mut modulations = app.modulations.clone();
        let jack = pmod.jack().read().bits();

        let note_patched = (jack & 0x1) != 0;
        modulations.trigger_patched   = (jack & 0x2) != 0;
        modulations.timbre_patched    = (jack & 0x4) != 0;
        modulations.morph_patched     = (jack & 0x8) != 0;

        if note_patched {
            // 1V/oct
            let v_oct = ((pmod.sample_i0().read().bits() as i16) as f32) / 4000.0f32;
            modulations.note = v_oct * 12.0f32;
        }

        modulations.trigger = ((pmod.sample_i1().read().bits() as i16) as f32) / 16384.0f32;
        modulations.timbre = ((pmod.sample_i2().read().bits() as i16) as f32) / 16384.0f32;
        modulations.morph = ((pmod.sample_i3().read().bits() as i16) as f32) / 16384.0f32;

        //
        // Render audio
        //

        let mut out = [0.0f32; BLOCK_SIZE];
        let mut aux = [0.0f32; BLOCK_SIZE];

        let mut n_attempts = 0;
        while (audio_fifo.fifo_len().read().bits() as usize) < AUDIO_FIFO_ELASTIC_SZ - BLOCK_SIZE {
            n_attempts += 1;
            if n_attempts > 10 {
                // TODO set underrun flag
                break
            }
            app.voice
               .render(&patch, &modulations, &mut out, &mut aux);
            for i in 0..BLOCK_SIZE {
                unsafe {
                    let fifo_base = AUDIO_FIFO_MEM_BASE as *mut u32;
                    *fifo_base = f32_to_i32((out[i]*16000.0f32).to_bits()) as u32;
                    *fifo_base.add(1) = f32_to_i32((aux[i]*16000.0f32).to_bits()) as u32;
                }
            }
        }

    });
}

#[entry]
fn main() -> ! {

    let peripherals = pac::Peripherals::take().unwrap();

    // initialize logging
    let serial = Serial0::new(peripherals.UART0);
    tiliqua_fw::handlers::logger_init(serial);

    let sysclk = pac::clock::sysclk();
    let mut timer = Timer0::new(peripherals.TIMER0, sysclk);
    let mut persist = Persist0::new(peripherals.PERSIST_PERIPH);
    let spiflash = SPIFlash0::new(
        peripherals.SPIFLASH_CTRL,
        SPIFLASH_BASE,
        SPIFLASH_SZ_BYTES
    );

    info!("Hello from Tiliqua MACRO-OSCILLATOR!");

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

    let vscope  = peripherals.VECTOR_PERIPH;
    let scope  = peripherals.SCOPE_PERIPH;

    //
    // Create application object.
    // DSP allocates some buffers from the heap (PSRAM)
    //

    unsafe { HEAP.init(HEAP_START, HEAP_SIZE) }

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
    // Create App instance
    //

    let mut last_palette = opts.beam.palette.value;
    let app = App::new(opts);
    let app = Mutex::new(RefCell::new(app));

    info!("heap usage {} KiB", HEAP.used()/1024);

    /*
    critical_section::with(|cs| {
        let mut app = app.borrow_ref_mut(cs);

        let mut out = [0.0f32; BLOCK_SIZE];
        let mut aux = [0.0f32; BLOCK_SIZE];

        let mut patch = app.patch.clone();
        let modulations = app.modulations.clone();

        timer.set_timeout_ticks(0xFFFFFFFF);
        timer.enable();

        for engine in 0..24 {

            let start = timer.counter();

            patch.engine = engine;

            for _ in 0..8 {
                app.voice
                    .render(&patch, &modulations, &mut out, &mut aux);
                }

            let read_ticks = start-timer.counter();

            let sysclk = pac::clock::sysclk();
            info!("engine {} speed {} samples/sec", engine, ((sysclk as u64) * ((BLOCK_SIZE * 8) as u64) / (read_ticks as u64)));
        }

        timer.disable();
        use embedded_hal::delay::DelayNs;
        timer.delay_ns(0);
    });
    */


    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);


        let mut first = true;


        //
        // Everything in this loop is best-effort (mostly UI drawing ops)
        // Real-time work is done in the timer interrupt.
        //

        let h_active = display.size().width;
        let v_active = display.size().height;

        loop {

            //
            // Tiny critical section, prohibit timer ISR when we want
            // to copy out the current state of application options.
            //

            let (opts, draw_options, save_opts, wipe_opts) = critical_section::with(|cs| {
                let mut app = app.borrow_ref_mut(cs);
                let save_opts = app.ui.opts.misc.save_opts.poll();
                let wipe_opts = app.ui.opts.misc.wipe_opts.poll();
                (app.ui.opts.clone(), app.ui.draw(), save_opts, wipe_opts)
            });

            if opts.beam.palette.value != last_palette || first {
                opts.beam.palette.value.write_to_hardware(&mut display);
                last_palette = opts.beam.palette.value;
            }

            if draw_options {
                draw::draw_options(&mut display, &opts, h_active-175, v_active/2-50, opts.beam.hue.value).ok();
                draw::draw_name(&mut display, h_active/2, v_active-50, opts.beam.hue.value,
                                &bootinfo.manifest.name, &bootinfo.manifest.tag, &modeline).ok();
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
                    if let Some(ref mut flash_persist) = flash_persist_opt {
                        flash_persist.erase_all().unwrap();
                    }
                });
            }

            persist.set_persist(opts.beam.persist.value);
            persist.set_decay(opts.beam.decay.value);

            let timebase_value = match opts.scope.timebase.value {
                Timebase::Timebase1s    => 12,
                Timebase::Timebase500ms => 24,
                Timebase::Timebase250ms => 52,
                Timebase::Timebase100ms => 128,
                Timebase::Timebase50ms  => 256,
                Timebase::Timebase25ms  => 512,
                Timebase::Timebase10ms  => 1280,
                Timebase::Timebase5ms   => 2560,
            };

            unsafe {
                vscope.hue().write(|w| w.hue().bits(opts.beam.hue.value));
                vscope.intensity().write(|w| w.intensity().bits(opts.beam.intensity.value));
                vscope.xscale().write(|w| w.scale().bits(opts.vector.xscale.value));
                vscope.yscale().write(|w| w.scale().bits(opts.vector.yscale.value));

                scope.hue().write(|w| w.hue().bits(opts.beam.hue.value+6));
                scope.intensity().write(|w| w.intensity().bits(opts.beam.intensity.value));

                scope.trigger_lvl().write(|w| w.trigger_level().bits(opts.scope.trig_lvl.value as u16));
                scope.xscale().write(|w| w.xscale().bits(opts.scope.xscale.value));
                scope.yscale().write(|w| w.yscale().bits(opts.scope.yscale.value));
                scope.timebase().write(|w| w.timebase().bits(timebase_value) );

                scope.ypos0().write(|w| w.ypos().bits(opts.scope.ypos0.value as u16));
                scope.ypos1().write(|w| w.ypos().bits(opts.scope.ypos1.value as u16));
                scope.ypos2().write(|w| w.ypos().bits(opts.scope.ypos2.value as u16));
                scope.ypos3().write(|w| w.ypos().bits(opts.scope.ypos3.value as u16));
            }


            if opts.misc.plot_type.value == PlotType::Vector {
                scope.flags().write(
                    |w| w.enable().bit(false) );
                vscope.flags().write(
                    |w| w.enable().bit(true) );
            } else {
                scope.flags().write(
                    |w| { w.enable().bit(true);
                          w.trigger_always().bit(opts.scope.trig_mode.value == TriggerMode::Always)
                    } );
                vscope.flags().write(
                    |w| w.enable().bit(false) );
            }

            first = false;
        }
    })
}
