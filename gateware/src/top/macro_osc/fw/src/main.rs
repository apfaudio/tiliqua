// See top-level comment in 'top.py' for usage information.

#![no_std]
#![no_main]

use log::info;
use riscv_rt::entry;
use core::cell::RefCell;
use critical_section::Mutex;
use core::convert::TryInto;
use irq::handler;
use embedded_alloc::LlffHeap as Heap;
use mi_plaits_dsp::dsp::voice::{Modulations, Patch, Voice};
use embedded_graphics::{
    pixelcolor::{Gray8, GrayColor},
    prelude::*,
};

use tiliqua_pac as pac;
use tiliqua_hal as hal;
use tiliqua_fw::*;
use tiliqua_lib::*;
use tiliqua_lib::generated_constants::*;
use opts::Options;
use hal::pca9635::*;


tiliqua_hal::impl_dma_display!(DMADisplay, H_ACTIVE, V_ACTIVE, VIDEO_ROTATE_90);

impl_ui!(UI,
         Options,
         Encoder0,
         Pca9635Driver<I2c0>,
         EurorackPmod0);

pub const TIMER0_ISR_PERIOD_MS: u32 = 5;
const BLOCK_SIZE: usize = 64;
// PSRAM heap for big audio buffers.
const HEAP_START: usize = PSRAM_BASE + (PSRAM_SZ_BYTES / 2);
const HEAP_SIZE: usize = 128*1024;

static HEAP: Heap = Heap::empty();

struct App<'a> {
    voice: Voice<'a>,
    patch: Patch,
    modulations: Modulations,
    ui: UI,
}

impl<'a> App<'a> {
    pub fn new(opts: Options) -> Self {
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
            ui: UI::new(opts, TIMER0_ISR_PERIOD_MS, encoder,
                        pca9635, pmod),
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
            let v_oct = ((pmod.sample_i0().read().bits() as i16) as f32) / 4096.0f32;
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

pub fn write_palette(video: &mut Video0, p: palette::ColorPalette) {
    for i in 0..PX_INTENSITY_MAX {
        for h in 0..PX_HUE_MAX {
            let rgb = palette::compute_color(i, h, p);
            video.set_palette_rgb(i as u8, h as u8, rgb.r, rgb.g, rgb.b);
        }
    }
}

#[entry]
fn main() -> ! {

    // FIXME: doesn't seem to be needed any more?

    pac::cpu::vexriscv::flush_icache();
    pac::cpu::vexriscv::flush_dcache();

    let peripherals = pac::Peripherals::take().unwrap();

    // initialize logging
    let serial = Serial0::new(peripherals.UART0);
    tiliqua_fw::handlers::logger_init(serial);

    let sysclk = pac::clock::sysclk();
    let mut timer = Timer0::new(peripherals.TIMER0, sysclk);

    info!("Hello from Tiliqua MACRO-OSCILLATOR!");

    let mut display = DMADisplay {
        framebuffer_base: PSRAM_FB_BASE as *mut u32,
    };

    let vscope  = peripherals.VECTOR_PERIPH;
    let scope  = peripherals.SCOPE_PERIPH;

    let mut video = Video0::new(peripherals.VIDEO_PERIPH);

    //
    // Create application object.
    // DSP allocates some buffers from the heap (PSRAM)
    //

    unsafe { HEAP.init(HEAP_START, HEAP_SIZE) }

    let opts = opts::Options::new();
    let mut last_palette = opts.beam.palette.value;
    let app = App::new(opts);
    let app = Mutex::new(RefCell::new(app));

    info!("heap usage {} KiB", HEAP.used()/1024);

    /*
     * NOTE: uncomment this for some basic benchmarking
    critical_section::with(|cs| {
        let mut app = app.borrow_ref_mut(cs);

        let mut out = [0.0f32; BLOCK_SIZE];
        let mut aux = [0.0f32; BLOCK_SIZE];

        let mut patch = app.patch.clone();
        let modulations = app.modulations.clone();

        for engine in 0..24 {

            timer.enable();
            timer.set_timeout_ticks(0xFFFFFFFF);

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
    });
    */

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        //
        // Configure initial scope settings.
        //

        scope.en().write(|w| w.enable().bit(true) );
        vscope.en().write(|w| w.enable().bit(false) );
        let mut first = true;


        //
        // Everything in this loop is best-effort (mostly UI drawing ops)
        // Real-time work is done in the timer interrupt.
        //

        loop {

            //
            // Tiny critical section, prohibit timer ISR when we want
            // to copy out the current state of application options.
            //

            let opts = critical_section::with(|cs| {
                app.borrow_ref(cs).ui.opts.clone()
            });

            if opts.beam.palette.value != last_palette || first {
                write_palette(&mut video, opts.beam.palette.value);
                last_palette = opts.beam.palette.value;
            }

            if opts.draw {
                draw::draw_options(&mut display, &opts, H_ACTIVE-175, V_ACTIVE/2-50, opts.beam.hue.value).ok();
            }

            video.set_persist(opts.beam.persist.value);
            video.set_decay(opts.beam.decay.value);

            unsafe {
                vscope.hue().write(|w| w.hue().bits(opts.beam.hue.value+4));
                vscope.intensity().write(|w| w.intensity().bits(opts.beam.intensity.value));
                vscope.xscale().write(|w| w.xscale().bits(opts.vector.xscale.value));
                vscope.yscale().write(|w| w.yscale().bits(opts.vector.yscale.value));

                scope.hue().write(|w| w.hue().bits(opts.beam.hue.value+6));
                scope.intensity().write(|w| w.intensity().bits(opts.beam.intensity.value));

                scope.trigger_lvl().write(|w| w.trigger_level().bits(opts.scope.trigger_lvl.value as u16));
                scope.xscale().write(|w| w.xscale().bits(opts.scope.xscale.value));
                scope.yscale().write(|w| w.yscale().bits(opts.scope.yscale.value));
                scope.timebase().write(|w| w.timebase().bits(opts.scope.timebase.value));

                scope.ypos0().write(|w| w.ypos().bits(opts.scope.ypos0.value as u16));
                scope.ypos1().write(|w| w.ypos().bits(opts.scope.ypos1.value as u16));
                scope.ypos2().write(|w| w.ypos().bits(opts.scope.ypos2.value as u16));
                scope.ypos3().write(|w| w.ypos().bits(opts.scope.ypos3.value as u16));
            }

            scope.trigger_always().write(
                |w| w.trigger_always().bit(opts.scope.trigger_mode.value == opts::TriggerMode::Always) );

            if opts.screen.value == opts::Screen::Vector {
                scope.en().write(|w| w.enable().bit(false) );
                vscope.en().write(|w| w.enable().bit(true) );
            }

            if opts.screen.value == opts::Screen::Scope {
                scope.en().write(|w| w.enable().bit(true) );
                vscope.en().write(|w| w.enable().bit(false) );
            }

            first = false;
        }
    })
}
