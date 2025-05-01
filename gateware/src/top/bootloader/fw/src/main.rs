#![no_std]
#![no_main]

use critical_section::Mutex;
use core::convert::TryInto;
use log::{info, warn};
use riscv_rt::entry;
use irq::handler;
use core::cell::RefCell;
use heapless::String;
use micromath::{F32Ext};
use strum_macros::{EnumIter, IntoStaticStr};
use embedded_hal::delay::DelayNs;

use core::str::FromStr;
use core::fmt::Write;

use tiliqua_lib::*;
use pac::constants::*;
use tiliqua_fw::*;
use tiliqua_hal::pmod::EurorackPmod;
use tiliqua_hal::persist::Persist;
use tiliqua_hal::si5351::*;
use tiliqua_hal::cy8cmbr3xxx::*;
use tiliqua_manifest::*;
use opts::OptionString;

use embedded_graphics::{
    mono_font::{ascii::FONT_9X15, ascii::FONT_9X15_BOLD, MonoTextStyle},
    pixelcolor::{Gray8, GrayColor},
    prelude::*,
    primitives::{PrimitiveStyleBuilder, Line},
    text::{Alignment, Text},
    geometry::OriginDimensions,
};

use tiliqua_fw::options::*;
use hal::pca9635::Pca9635Driver;

tiliqua_hal::impl_dma_framebuffer! {
    DMAFramebuffer0: tiliqua_pac::FRAMEBUFFER_PERIPH,
    Palette0: tiliqua_pac::PALETTE_PERIPH,
}

pub const TIMER0_ISR_PERIOD_MS: u32 = 10;

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum BitstreamError {
    InvalidManifest,
    HwVersionMismatch,
    SpiflashCrcError,
    PllBadConfigError,
    PllI2cError,
}

struct App {
    ui: ui::UI<Encoder0, EurorackPmod0, I2c0, Opts>,
    pll: Option<Si5351Device<I2c0>>,
    reboot_n: Option<usize>,
    error_n: [Option<String<32>>; N_MANIFESTS],
    time_since_reboot_requested: u32,
    manifests: [Option<BitstreamManifest>; N_MANIFESTS],
    animation_elapsed_ms: u32,
}

impl App {
    pub fn new(opts: Opts, manifests: [Option<BitstreamManifest>; N_MANIFESTS],
               pll: Option<Si5351Device<I2c0>>) -> Self {
        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
        Self {
            ui: ui::UI::new(opts, TIMER0_ISR_PERIOD_MS,
                            encoder, pca9635, pmod),
            pll,
            reboot_n: None,
            error_n: [const { None }; N_MANIFESTS],
            time_since_reboot_requested: 0u32,
            manifests,
            animation_elapsed_ms: 0u32,
        }
    }

    // Return 'true' while startup LED animation is in progress.
    pub fn startup_animation(&mut self) -> bool {
        use tiliqua_hal::pca9635::Pca9635;
        let animation_end_ms = 500u32;
        if self.animation_elapsed_ms < animation_end_ms {
            let tau = 6.2832f32;
            let lerp1: f32 = self.animation_elapsed_ms as f32 / animation_end_ms as f32;
            for n in 0..8 {
                let lerp2: f32 = n as f32 / 7.0f32;
                self.ui.pmod.led_set_manual(n,
                    (100.0f32*f32::sin(tau*(lerp1+lerp2).clamp(0.0f32, tau))*
                        f32::sin(tau*lerp1*0.5f32)) as i8);
            }
            for n in 0..16 {
                let lerp2: f32 = n as f32 / 15.0f32;
                self.ui.pca9635.leds[n] =
                    (100.0f32*f32::sin(tau*(lerp1+lerp2).clamp(0.0f32, tau*0.5f32))*
                        f32::sin(tau*lerp1*0.5f32)) as u8;
            }
            self.ui.pca9635.push().ok();
            self.animation_elapsed_ms += TIMER0_ISR_PERIOD_MS;
            return true;
        }
        return false;
    }
}

fn print_rebooting<D>(d: &mut D, rng: &mut fastrand::Rng)
where
    D: DrawTarget<Color = Gray8> + OriginDimensions,
{
    let style = MonoTextStyle::new(&FONT_9X15_BOLD, Gray8::WHITE);
    let h_active = d.size().width as i32;
    let v_active = d.size().height as i32;
    Text::with_alignment(
        "REBOOTING",
        Point::new(rng.i32(0..h_active), rng.i32(0..v_active)),
        style,
        Alignment::Center,
    )
    .draw(d).ok();
}

fn draw_summary<D>(d: &mut D,
                   bitstream_manifest: &Option<BitstreamManifest>,
                   error: &Option<String<32>>,
                   startup_report: &String<256>,
                   or: i32, ot: i32, hue: u8)
where
    D: DrawTarget<Color = Gray8> + OriginDimensions,
{
    let h_active = d.size().width as i32;
    let v_active = d.size().height as i32;
    let norm = MonoTextStyle::new(&FONT_9X15, Gray8::new(0xB0 + hue));
    if let Some(bitstream) = bitstream_manifest {
        Text::with_alignment(
            "brief:".into(),
            Point::new((h_active/2 - 10) as i32 + or, (v_active/2+20) as i32 + ot),
            norm,
            Alignment::Right,
        )
        .draw(d).ok();
        Text::with_alignment(
            &bitstream.brief,
            Point::new((h_active/2) as i32 + or, (v_active/2+20) as i32 + ot),
            norm,
            Alignment::Left,
        )
        .draw(d).ok();
        Text::with_alignment(
            "video:".into(),
            Point::new((h_active/2 - 10) as i32 + or, (v_active/2+40) as i32 + ot),
            norm,
            Alignment::Right,
        )
        .draw(d).ok();
        Text::with_alignment(
            &bitstream.video,
            Point::new((h_active/2) as i32 + or, (v_active/2+40) as i32 + ot),
            norm,
            Alignment::Left,
        )
        .draw(d).ok();
        Text::with_alignment(
            "sha:".into(),
            Point::new((h_active/2 - 10) as i32 + or, (v_active/2+60) as i32 + ot),
            norm,
            Alignment::Right,
        )
        .draw(d).ok();
        Text::with_alignment(
            &bitstream.sha,
            Point::new((h_active/2) as i32 + or, (v_active/2+60) as i32 + ot),
            norm,
            Alignment::Left,
        )
        .draw(d).ok();
    }
    if let Some(error_string) = &error {
        Text::with_alignment(
            "error:".into(),
            Point::new((h_active/2 - 10) as i32 + or, (v_active/2+80) as i32 + ot),
            norm,
            Alignment::Right,
        )
        .draw(d).ok();
        Text::with_alignment(
            &error_string,
            Point::new((h_active/2) as i32 + or, (v_active/2+80) as i32 + ot),
            norm,
            Alignment::Left,
        )
        .draw(d).ok();
    }
    Text::with_alignment(
        &startup_report,
        Point::new((h_active/2) as i32 + or, (v_active/2-70) as i32 + ot),
        norm,
        Alignment::Center,
    )
    .draw(d).ok();
}

fn configure_external_pll(pll_config: &ExternalPLLConfig, pll: &mut Si5351Device<I2c0>)
    -> Result<(), tiliqua_hal::si5351::Error> {
    pll.init_adafruit_module()?;
    match pll_config.clk1_hz {
        Some(clk1_hz) => {
            info!("si5351/pll: configure for clk0={}Hz, clk1={}Hz", pll_config.clk0_hz, clk1_hz);
            pll.set_frequencies(
                PLL::A,
                &[
                    ClockOutput::Clk0,
                    ClockOutput::Clk1,
                ],
                &[
                    pll_config.clk0_hz,
                    clk1_hz,
                ],
                pll_config.spread_spectrum)
        }
        _ => {
            info!("si5351/pll: configure for clk0={}Hz, clk1=disabled", pll_config.clk0_hz);
            pll.set_frequencies(
                PLL::A,
                &[
                    ClockOutput::Clk0,
                ],
                &[
                    pll_config.clk0_hz,
                ],
                pll_config.spread_spectrum)
        }
    }
}

fn copy_spiflash_region_to_psram(region: &MemoryRegion) -> Result<(), BitstreamError> {
    if let Some(psram_dst) = region.psram_dst {
        let psram_ptr = PSRAM_BASE as *mut u32;
        let spiflash_ptr = SPIFLASH_BASE as *mut u32;
        let spiflash_offset_words = region.spiflash_src as isize / 4isize;
        let psram_offset_words = psram_dst as isize / 4isize;
        let size_words = region.size as isize / 4isize + 1;
        info!("Copying {:#x}..{:#x} (spi flash) to {:#x}..{:#x} (psram) ...",
              SPIFLASH_BASE + region.spiflash_src as usize,
              SPIFLASH_BASE + (region.spiflash_src + region.size) as usize,
              PSRAM_BASE + psram_dst as usize,
              PSRAM_BASE + (psram_dst + region.size) as usize);
        for i in 0..size_words {
            unsafe {
                let d = spiflash_ptr.offset(spiflash_offset_words + i).read_volatile();
                psram_ptr.offset(psram_offset_words + i).write_volatile(d);
            }
        }
        info!("Verify {} KiB copied correctly ...", (size_words*4) / 1024);
        let crc_bzip2 = crc::Crc::<u32>::new(&crc::CRC_32_BZIP2);
        let mut digest = crc_bzip2.digest();
        for i in 0..size_words {
            unsafe {
                let d1 = psram_ptr.offset(psram_offset_words + i).read_volatile();
                if i != (size_words - 1) {
                    digest.update(&d1.to_le_bytes());
                } else {
                    digest.update(&d1.to_le_bytes()[0..(region.size as usize)%4usize]);
                }
            }
        }
        let crc_result = digest.finalize();
        info!("got PSRAM crc: {:#x}, manifest wants: {:#x}", crc_result, region.crc);
        if crc_result == region.crc {
            Ok(())
        } else {
            Err(BitstreamError::SpiflashCrcError)
        }
    } else {
        info!("skipping XiP memory region ...");
        Ok(())
    }
}

fn timer0_handler(app: &Mutex<RefCell<App>>) {

    critical_section::with(|cs| {

        let mut app = app.borrow_ref_mut(cs);

        //
        // Update UI and options
        //

        if !app.startup_animation() {
            app.ui.update();
        }

        if app.ui.opts.tracker.modify {
            if let Some(n) = app.ui.opts.tracker.selected {
                app.reboot_n = Some(n)
            }
        }

        if let Some(n) = app.reboot_n {
            app.time_since_reboot_requested += TIMER0_ISR_PERIOD_MS;
            // Give codec time to mute and display time to draw 'REBOOTING'
            if app.time_since_reboot_requested > 500 {
                // Is there a firmware image to copy to PSRAM before we switch bitstreams?
                let error = if let Some(manifest) = &app.manifests[n].clone() {
                    || -> Result<(), BitstreamError> {
                        if manifest.magic != MANIFEST_MAGIC {
                            Err(BitstreamError::InvalidManifest)?;
                        }
                        if manifest.hw_rev != HW_REV_MAJOR {
                            Err(BitstreamError::HwVersionMismatch)?;
                        }
                        for region in &manifest.regions {
                            copy_spiflash_region_to_psram(region)?;
                        }
                        if let Some(pll_config) = manifest.external_pll_config.clone() {
                            if let Some(ref mut pll) = app.pll {
                                configure_external_pll(&pll_config, pll).or(
                                    Err(BitstreamError::PllI2cError))?;
                            } else {
                                // External PLL config is in manifest but this bootloader
                                // didn't set up the PLL (likely hardware / gateware mismatch).
                                Err(BitstreamError::PllBadConfigError)?;
                            }
                        }
                        Ok(())
                    }()
                } else {
                    Err(BitstreamError::InvalidManifest)
                };
                if let Err(bitstream_error) = error {
                    // Cancel reboot, draw an error.
                    app.ui.opts.tracker.modify = false;
                    app.reboot_n = None;
                    app.time_since_reboot_requested = 0;
                    app.error_n[n] = Some(String::from_str(bitstream_error.into()).unwrap());
                    info!("Failed to load bitstream: {:?}", app.error_n[n]);
                } else {
                    // Ask RP2040 to perform reboot.
                    info!("BITSTREAM{}\n\r", n);
                    loop {}
                }
            }
        }
    });
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum StartupWarning {
    #[strum(to_string = "ak4619/codec: issued hard reset (to avoid: remove display when unpowered)")]
    CodecHardReset,
    #[strum(to_string = "cy8cmbr/touch: NVM reprogrammed (bootloader update?)")]
    TouchNvmReprogrammed,
    #[strum(to_string = "cy8cmbr/touch: NVM reprogram FAIL (try rebooting?)")]
    TouchNvmReprogramFailed,
    #[strum(to_string = "cy8cmbr/touch: disabled/nak! (try: remove in2 jack and reboot?)")]
    TouchNak,
}

use embedded_hal::i2c::{I2c, Operation};

// Mitigation for https://github.com/apfaudio/tiliqua/issues/81
pub fn maybe_restart_codec<CodecI2c, Pmod>(i2cdev: &mut CodecI2c, pmod: &mut Pmod) -> Result<(), StartupWarning>
where
    CodecI2c: I2c,
    Pmod: EurorackPmod
{
    const CODEC_ADDR: u8 = 0x10;
    let mut rx_bytes = [0u8; 4];
    let ret = i2cdev.transaction(
        CODEC_ADDR, &mut [Operation::Write(&[0u8]),
                          Operation::Read(&mut rx_bytes)]);
    if ret.is_err() || rx_bytes[0] != 0x37 {
        warn!("ak4619/codec: needs hard reset. transaction returned: {:?}.", ret);
        for n in 0usize..4usize {
            warn!("ak4619: @{}:0x{:x}", n, rx_bytes[n]);
        }
        warn!("ak4619/codec: issuing hard PDN reset ...");
        pmod.hard_reset();
        Err(StartupWarning::CodecHardReset)
    } else {
        info!("ak4619/codec: register config looks healthy.");
        Ok(())
    }
}

pub fn maybe_reprogram_cy8cmbr3xxx<TouchI2c>(dev: &mut Cy8cmbr3108Driver<TouchI2c>) -> Result<(), StartupWarning>
where
    TouchI2c: I2c,
{
    let prefix = "cy8cmbr3xxx/touch: ";
    info!("{}n_working_sensors={:?}", prefix, dev.read_n_working_sensors());
    let stored = dev.get_stored_crc();
    match stored {
        Ok(stored) => {
            let desired = dev.calculate_crc();
            info!("{}CRC stored={:#x} (desired={:#x})", prefix, stored, desired);
            if stored == desired {
                info!("{}CRC OK", prefix);
                return Ok(());
            } else {
                warn!("{}CRC NOT OK, reprogramming ...", prefix);
                match dev.reprogram_nvm_and_reset() {
                    Ok(_) => {
                        warn!("{}reprogramming DONE ...", prefix);
                        Err(StartupWarning::TouchNvmReprogrammed)
                    },
                    _ => {
                        warn!("{}reprogramming FAILED ...", prefix);
                        Err(StartupWarning::TouchNvmReprogramFailed)
                    }
                }
            }
        },
        _ => {
            warn!("{}NAK error (jack2 connected?) ignoring ...", prefix);
            Err(StartupWarning::TouchNak)
        }
    }
}

fn read_edid(i2cdev: &mut I2c0) -> Result<edid::Edid, edid::EdidError> {
    const EDID_ADDR: u8 = 0x50;
    info!("video/edid: read_edid from i2c0 address 0x{:x}", EDID_ADDR);
    let mut edid: [u8; 128] = [0; 128];
    for i in 0..16 {
        // Be extremely careful these transactions are not interrupted, because
        // bad EDID transactions could brick monitors.
        riscv::interrupt::disable();
        i2cdev.transaction(EDID_ADDR, &mut [Operation::Write(&[(i*8) as u8]),
                                            Operation::Read(&mut edid[i*8..i*8+8])]).ok();
        unsafe { riscv::interrupt::enable(); }
    }
    let edid = edid::Edid::parse(&edid);
    info!("video/edid: read_edid got {:?}", edid);
    edid
}

fn modeline_from_edid(edid: edid::Edid) -> Option<DVIModeline> {

    // Read the EDID contents and see if we can use it to dynamically create a
    // sensible modeline. If we can't fine a reasonable descriptor, we return
    // None and assumably the caller falls back to some default modeline.

    info!("video/edid: valid edid. scanning detailed timing descriptors...");
    for descriptor in edid.descriptors.iter() {
        if let edid::Descriptor::DetailedTiming(desc) = descriptor {
            info!("video/edid: checking detailed timing descriptor, contents: {:?}", descriptor);
            if desc.pixel_clock_khz < 24_000u32 || desc.pixel_clock_khz > 100_000u32 {
                warn!("video/edid: skip descriptor (out-of-range pixel clock)");
                continue;
            }
            if desc.features.interlaced {
                warn!("video/edid: skip descriptor (interlaced timings)");
                continue;
            }
            if let edid::SyncType::DigitalSeparate { vsync_positive, hsync_positive } = desc.features.sync_type {
                let mut rotate = Rotate::Normal;
                if edid.header.product_code == 0x3132 || edid.header.product_code == 0xAA61 {
                    info!("video/edid: detected tiliqua screen! rotate framebuffer 90 degrees.");
                    rotate = Rotate::Left;
                }
                let modeline = DVIModeline {
                    h_active      : desc.horizontal_active,
                    h_sync_start  : desc.horizontal_active +
                                    desc.horizontal_sync_offset,
                    h_sync_end    : desc.horizontal_active +
                                    desc.horizontal_sync_offset +
                                    desc.horizontal_sync_pulse_width,
                    h_total       : desc.horizontal_active +
                                    desc.horizontal_blanking,
                    h_sync_invert : !hsync_positive,
                    v_active      : desc.vertical_active,
                    v_sync_start  : desc.vertical_active +
                                    desc.vertical_sync_offset,
                    v_sync_end    : desc.vertical_active +
                                    desc.vertical_sync_offset +
                                    desc.vertical_sync_pulse_width,
                    v_total       : desc.vertical_active +
                                    desc.vertical_blanking,
                    v_sync_invert : !vsync_positive,
                    pixel_clk_mhz : (desc.pixel_clock_khz as f32) / 1e3f32,
                    rotate
                };
                info!("video/edid: found useable modeline, returning: {:?}", modeline);
                return Some(modeline)
            } else {
                warn!("video/edid: skip descriptor (unknown sync format)");
                continue;
            }
        }
    }
    None
}

fn modeline_or_fallback(i2cdev: &mut I2c0) -> DVIModeline {
    match read_edid(i2cdev) {
        Ok(edid) => match modeline_from_edid(edid) {
            Some(edid_modeline) => edid_modeline,
            _ => DVIModeline::default()
        }
        _ => DVIModeline::default()
    }
}

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    let sysclk = pac::clock::sysclk();
    let serial = Serial0::new(peripherals.UART0);
    let mut timer = Timer0::new(peripherals.TIMER0, sysclk);
    let mut persist = Persist0::new(peripherals.PERSIST_PERIPH);

    crate::handlers::logger_init(serial);

    info!("Hello from Tiliqua bootloader!");

    let mut startup_report: String<256> = Default::default();

    // Verify/reprogram touch sensing NVM

    {
        // TODO more sensible bus sharing
        let i2cdev1 = I2c1::new(unsafe { pac::I2C1::steal() } );
        let mut cy8 = Cy8cmbr3108Driver::new(i2cdev1);
        if let Err(e) = maybe_reprogram_cy8cmbr3xxx(&mut cy8) {
            let s: &'static str = e.into();
            write!(startup_report, "{}\r\n", s).ok();
        }
    }

    // Fetch initial modeline (may be used for external PLL setup)

    timer.delay_ms(10);
    let mut i2cdev_edid = I2c0::new(unsafe { pac::I2C0::steal() } );
    let modeline = modeline_or_fallback(&mut i2cdev_edid);

    // Setup audio clocks on external PLL

    let mut maybe_external_pll = if HW_REV_MAJOR >= 4 {
        let i2cdev_mobo_pll = I2c0::new(unsafe { pac::I2C0::steal() } );
        let mut si5351drv = Si5351Device::new_adafruit_module(i2cdev_mobo_pll);
        configure_external_pll(&ExternalPLLConfig{
            clk0_hz: CLOCK_AUDIO_HZ,
            clk1_hz: Some((modeline.pixel_clk_mhz*1e6) as u32),
            spread_spectrum: Some(0.01),
        }, &mut si5351drv).unwrap();
        Some(si5351drv)
    } else {
        None
    };

    // Setup CODEC and load audio calibration.

    let mut i2cdev1 = I2c1::new(peripherals.I2C1);
    let mut pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
    if let Err(e) = maybe_restart_codec(&mut i2cdev1, &mut pmod) {
        let s: &'static str = e.into();
        write!(startup_report, "{}\r\n", s).ok();
    }
    calibration::CalibrationConstants::load_or_default(&mut i2cdev1, &mut pmod);

    let mut manifests: [Option<BitstreamManifest>; 8] = [const { None }; 8];
    for n in 0usize..N_MANIFESTS {
        let size: usize = MANIFEST_SIZE;
        let manifest_first = SPIFLASH_BASE + SLOT_BITSTREAM_BASE;
        let addr: usize = manifest_first + (n+1)*SLOT_SIZE - size;
        info!("(entry {}) look for manifest from {:#x} to {:#x}", n, addr, addr+size);
        manifests[n] = BitstreamManifest::from_addr(addr, size);
    }

    let mut opts = Opts::default();
    // Populate option string values with bitstream names from manifest.
    let mut names: [OptionString; 8] = [const { OptionString::new() }; 8];
    for n in 0..manifests.len() {
        if let Some(manifest) = &manifests[n] {
            names[n] = manifest.name.clone();
        }
    }
    opts.boot.slot0.value = names[0].clone();
    opts.boot.slot1.value = names[1].clone();
    opts.boot.slot2.value = names[2].clone();
    opts.boot.slot3.value = names[3].clone();
    opts.boot.slot4.value = names[4].clone();
    opts.boot.slot5.value = names[5].clone();
    opts.boot.slot6.value = names[6].clone();
    opts.boot.slot7.value = names[7].clone();
    opts.tracker.selected = Some(0); // Don't start with page highlighted.
    let app = Mutex::new(RefCell::new(App::new(opts, manifests.clone(), None)));

    let mut display = DMAFramebuffer0::new(
        peripherals.FRAMEBUFFER_PERIPH,
        peripherals.PALETTE_PERIPH,
        PSRAM_FB_BASE,
        modeline
    );

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        let mut logo_coord_ix = 0u32;
        let mut rng = fastrand::Rng::with_seed(0);

        persist.set_persist(256);

        let stroke = PrimitiveStyleBuilder::new()
            .stroke_color(Gray8::new(0xB0))
            .stroke_width(1)
            .build();

        palette::ColorPalette::default().write_to_hardware(&mut display);

        log::info!("{}", startup_report);

        use tiliqua_hal::dma_framebuffer::DMAFramebuffer;

        let mut last_hpd = display.get_hpd();

        s.register(handlers::Interrupt::TIMER0, timer0);
        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        loop {

            if display.get_hpd() && !last_hpd {
                let modeline = modeline_or_fallback(&mut i2cdev_edid);
                configure_external_pll(&ExternalPLLConfig{
                    clk0_hz: CLOCK_AUDIO_HZ,
                    clk1_hz: Some((modeline.pixel_clk_mhz*1e6) as u32),
                    spread_spectrum: Some(0.01),
                }, &mut maybe_external_pll.as_mut().unwrap()).unwrap();
                let peripherals = unsafe { pac::Peripherals::steal() };
                display = DMAFramebuffer0::new(
                    peripherals.FRAMEBUFFER_PERIPH,
                    peripherals.PALETTE_PERIPH,
                    PSRAM_FB_BASE,
                    modeline,
                );
            }
            last_hpd = display.get_hpd();

            let h_active = display.size().width;
            let v_active = display.size().height;

            // Always mute the CODEC to stop pops on flashing while in the bootloader.
            pmod.mute(true);

            let (opts, reboot_n, error_n) = critical_section::with(|cs| {
                (app.borrow_ref(cs).ui.opts.clone(),
                 app.borrow_ref(cs).reboot_n.clone(),
                 app.borrow_ref(cs).error_n.clone())
            });

            draw::draw_options(&mut display, &opts, 100, v_active/2-50, 0).ok();
            draw::draw_name(&mut display, h_active/2, v_active-50, 0, UI_NAME, UI_SHA).ok();

            if let Some(n) = opts.tracker.selected {
                draw_summary(&mut display, &manifests[n], &error_n[n], &startup_report, -20, -18, 0);
                if manifests[n].is_some() {
                    Line::new(Point::new(255, (v_active/2 - 55 + (n as u32)*18) as i32),
                              Point::new((h_active/2-90) as i32, (v_active/2+8) as i32))
                              .into_styled(stroke)
                              .draw(&mut display).ok();
                }
            }

            for _ in 0..5 {
                let _ = draw::draw_boot_logo(&mut display,
                                             (h_active/2) as i32,
                                             150 as i32,
                                             logo_coord_ix);
                logo_coord_ix += 1;
            }

            if let Some(_) = reboot_n {
                print_rebooting(&mut display, &mut rng);
            }
        }
    })
}
