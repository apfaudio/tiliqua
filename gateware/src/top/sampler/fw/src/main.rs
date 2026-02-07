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

use tiliqua_hal::embedded_graphics::prelude::*;
use tiliqua_hal::embedded_graphics::mono_font::{ascii::FONT_9X15, MonoTextStyle};
use tiliqua_hal::embedded_graphics::text::{Alignment, Text};
use tiliqua_lib::color::HI8;

use options::*;
use channel::{Channel, ChannelView};
use hal::pca9635::Pca9635Driver;
use tiliqua_hal::delay_line::DelayLine;
use tiliqua_hal::persist::Persist;
use tiliqua_hal::pmod::EurorackPmod;

pub const TIMER0_ISR_PERIOD_MS: u32 = 5;
pub const WAVEFORM_SAMPLES: usize = 240;

pub type Channels = (
    Channel<DelayLine0, GrainPlayer0>,
    Channel<DelayLine1, GrainPlayer1>,
    Channel<DelayLine2, GrainPlayer2>,
);

struct App {
    ui: ui::UI<Encoder0, EurorackPmod0, I2c0, Opts>,
    channels: Channels,
}

impl App {
    pub fn new(
        opts: Opts,
        channels: Channels,
    ) -> Self {
        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
        Self {
            ui: ui::UI::new(opts, TIMER0_ISR_PERIOD_MS,
                            encoder, pca9635, pmod),
            channels,
        }
    }
}

fn timer0_handler(app: &Mutex<RefCell<App>>) {
    critical_section::with(|cs| {

        let peripherals = unsafe { pac::Peripherals::steal() };
        let pmod = peripherals.PMOD0_PERIPH;
        let sampler = peripherals.SAMPLER_PERIPH;

        let mut app = app.borrow_ref_mut(cs);

        if let Some(ix) = app.ui.opts.tracker.page.value.channel_index() {
            let max_samples = app.channels.0.delayln.size_samples(); // WARN: assumes all delayln length match
            // Snapshot options before encoder update, so we can scale step by zoom factor.
            let opts_prev = app.ui.opts.channel_opts(ix).clone();
            app.ui.update();
            // Recalculate steps by zoom factor
            let opts = app.ui.opts.channel_opts_mut(ix);
            let zoomstep = |prev: u32, cur: u32, zoom: u8| -> u32 {
                let scale = 1i32 << (4 - zoom as i32);
                let delta = cur as i32 - prev as i32;
                (prev as i32 + delta * scale).max(0).min(max_samples as i32) as u32
            };
            opts.start.value = zoomstep(opts_prev.start.value, opts.start.value.clone(), opts.zoom.value.clone());
            opts.len.value = zoomstep(opts_prev.len.value, opts.len.value.clone(), opts.zoom.value.clone());
            // Update sampler CSRs
            sampler.flags().write(|w| unsafe {
                w.record().bit(opts.record.value);
                w.record_channel().bits(ix as u8)
            });
        } else {
            app.ui.update();
        }

        app.ui.touch_led_mask(0b00001110);
        let touch = app.ui.pmod.touch();
        let jack = pmod.jack().read().bits();
        let opts = app.ui.opts.clone();
        app.channels.0.update(&opts.channel0, 1, &touch, jack);
        app.channels.1.update(&opts.channel1, 2, &touch, jack);
        app.channels.2.update(&opts.channel2, 3, &touch, jack);
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

    info!("Hello from Tiliqua SAMPLER!");

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

    let channels = (
        Channel::new(
            DelayLine0::new(peripherals.DELAYLN_PERIPH0),
            GrainPlayer0::new(peripherals.GRAIN_PERIPH0),
        ),
        Channel::new(
            DelayLine1::new(peripherals.DELAYLN_PERIPH1),
            GrainPlayer1::new(peripherals.GRAIN_PERIPH1),
        ),
        Channel::new(
            DelayLine2::new(peripherals.DELAYLN_PERIPH2),
            GrainPlayer2::new(peripherals.GRAIN_PERIPH2),
        ),
    );


    let opts = Opts::default();
    let app = Mutex::new(RefCell::new(App::new(opts, channels)));

    palette::ColorPalette::default().write_to_hardware(&mut display);

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        let hue = 10;

        loop {

            let h_active = display.size().width;
            let v_active = display.size().height;

            let (opts, _, channel_view) = critical_section::with(|cs| {
                let app = app.borrow_ref_mut(cs);
                let channel_view = match app.ui.opts.tracker.page.value {
                    Page::Channel0 => Some((app.channels.0.view(), app.ui.opts.channel0.clone())),
                    Page::Channel1 => Some((app.channels.1.view(), app.ui.opts.channel1.clone())),
                    Page::Channel2 => Some((app.channels.2.view(), app.ui.opts.channel2.clone())),
                    _ => None,
                };
                (app.ui.opts.clone(), app.ui.draw(), channel_view)
            });

            let on_help_page = opts.tracker.page.value == Page::Help;

            let (x, y) = if on_help_page {
                (h_active/2-30, v_active-100)
            } else {
                (h_active/2, 80)
            };
            draw::draw_options(&mut display, &opts, x, y, hue).ok();
            draw::draw_name(&mut display, h_active/2, v_active-50, hue,
                            &bootinfo.manifest.name, &bootinfo.manifest.tag, &modeline).ok();

            if on_help_page {
                draw::draw_help_page(&mut display,
                    MODULE_DOCSTRING,
                    bootinfo.manifest.help.as_ref(),
                    h_active,
                    v_active,
                    opts.help.scroll.value,
                    hue).ok();
                persist.set_persist(128);
                persist.set_decay(1);
            } else {
                persist.set_persist(128);
                persist.set_decay(1);
            }


            // Draw (maybe) zoomed waveform peaks, start/end points, playback position
            if let Some((view, channel_opts)) = channel_view {

                // HACK: when hovering on 'length' menu item, center on it instead of 'start'.
                let center_on_end = opts.tracker.selected == Some(7);

                // Read waveform peaks (well, samples)
                let mut waveform: [i16; WAVEFORM_SAMPLES] = [0; WAVEFORM_SAMPLES];
                view.read_samples(&channel_opts, &mut waveform, center_on_end);

                // Compute some layout constants
                let waveform_width = 720u32;
                let waveform_height = 300u32;
                let sample_width = waveform_width / WAVEFORM_SAMPLES as u32;
                let actual_span = (WAVEFORM_SAMPLES as u32 - 1) * sample_width;
                let waveform_x = h_active / 2 - actual_span / 2;
                let waveform_y = v_active / 2 - waveform_height / 2;

                // Draw waveform peaks
                draw::draw_waveform(&mut display, waveform_x, waveform_y, waveform_width, waveform_height, hue, &waveform).ok();

                // Draw grain start/end markers
                let (start_x, end_x) = view.grain_markers_x(&channel_opts, WAVEFORM_SAMPLES, center_on_end, waveform_x, actual_span);
                let marker_height = waveform_height / 2;
                let marker_y = waveform_y + waveform_height / 4;
                draw::draw_vline(&mut display, start_x, marker_y, marker_height, hue, 15).ok();
                draw::draw_vline(&mut display, end_x, marker_y, marker_height, hue, 15).ok();

                // Draw playback position
                let playback_pos = view.playback_position();
                let pos_x = view.delay_to_x(&channel_opts, playback_pos, WAVEFORM_SAMPLES, center_on_end, waveform_x, actual_span);
                let pos_height = waveform_height / 4;
                let pos_y = waveform_y + waveform_height * 3 / 8;
                draw::draw_vline(&mut display, pos_x, pos_y, pos_height, hue, 15).ok();

                // Draw view mode string
                let label = ChannelView::view_label(&channel_opts, center_on_end);
                let font = MonoTextStyle::new(&FONT_9X15, HI8::new(hue, 12));
                let label_y = waveform_y + waveform_height - 30;
                Text::with_alignment(
                    label,
                    Point::new((h_active / 2) as i32, label_y as i32),
                    font,
                    Alignment::Center
                ).draw(&mut display).ok();
            }

        }
    })
}
