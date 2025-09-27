#![no_std]
#![no_main]

use critical_section::Mutex;
use log::{info, warn};
use riscv_rt::entry;
use irq::handler;
use core::cell::RefCell;
use heapless::String;
use micromath::{F32Ext};
use strum_macros::{EnumIter, IntoStaticStr};
use embedded_hal::delay::DelayNs;
use embedded_hal::i2c::Operation;

use core::str::FromStr;
use core::fmt::Write;

use tiliqua_lib::*;
use tiliqua_lib::eeprominfo::{EepromConfig, EepromManager};
use pac::constants::*;
use tiliqua_fw::*;
use tiliqua_hal::pmod::EurorackPmod;
use tiliqua_hal::persist::Persist;
use tiliqua_hal::si5351::*;
use tiliqua_hal::cy8cmbr3xxx::*;
use tiliqua_hal::dma_framebuffer::DMAFramebuffer;
use tiliqua_manifest::*;
use opts::OptionString;

use tiliqua_hal::embedded_graphics::{
    mono_font::{ascii::FONT_9X15, ascii::FONT_9X15_BOLD, MonoTextStyle},
    prelude::*,
    primitives::{PrimitiveStyleBuilder, Line},
    text::{Alignment, Text},
};
use tiliqua_lib::color::HI8;

use tiliqua_fw::options::*;
use hal::pca9635::Pca9635Driver;
use hal::dma_framebuffer::{Rotate, DVIModeline};

pub const TIMER0_ISR_PERIOD_MS: u32 = 10;
// Technically this lower bound is out of the ECP5 PLL spec,
// see the notes in `tiliqua_pll.py:create_dynamic_dvi_pll`.
// But we keep it this low for compatibility with low res modes.
pub const PIXEL_CLK_MIN_KHZ: u32 = 24_000u32;
pub const PIXEL_CLK_MAX_KHZ: u32 = CLOCK_DVI_HZ / 1000u32;

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum BitstreamError {
    InvalidManifest,
    HwVersionMismatch,
    SpiflashCrcError,
    PllBadConfigError,
    PllI2cError,
    BootloaderStaticModeline,
}

struct App {
    ui: ui::UI<Encoder0, EurorackPmod0, I2c0, Opts>,
    pll: Option<Si5351Device<I2c0>>,
    eeprom_manager: EepromManager<I2c1>,
    reboot_n: Option<usize>,
    error_n: [Option<String<32>>; N_MANIFESTS],
    time_since_reboot_requested: u32,
    manifests: [Option<BitstreamManifest>; N_MANIFESTS],
    animation_elapsed_ms: u32,
    modeline: DVIModeline,
    autoboot_slot: Option<usize>,
    autoboot_countdown_ms: u32,
}

impl App {
    pub fn new(opts: Opts, manifests: [Option<BitstreamManifest>; N_MANIFESTS],
               pll: Option<Si5351Device<I2c0>>, modeline: DVIModeline, autoboot_slot: Option<usize>, 
               eeprom_manager: EepromManager<I2c1>) -> Self {
        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
        Self {
            ui: ui::UI::new(opts, TIMER0_ISR_PERIOD_MS,
                            encoder, pca9635, pmod),
            pll,
            eeprom_manager,
            reboot_n: None,
            error_n: [const { None }; N_MANIFESTS],
            time_since_reboot_requested: 0u32,
            manifests,
            animation_elapsed_ms: 0u32,
            modeline,
            autoboot_slot,
            autoboot_countdown_ms: if autoboot_slot.is_some() { 5000 } else { 0 },
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
    D: DrawTarget<Color = HI8> + OriginDimensions,
{
    let style = MonoTextStyle::new(&FONT_9X15_BOLD, HI8::WHITE);
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

fn print_autoboot_countdown<D>(d: &mut D, countdown_ms: u32, slot: usize, target: &OptionString)
where
    D: DrawTarget<Color = HI8> + OriginDimensions,
{
    let style = MonoTextStyle::new(&FONT_9X15_BOLD, HI8::WHITE);
    let h_active = d.size().width as i32;
    let v_active = d.size().height as i32;

    let countdown_sec = (countdown_ms + 999) / 1000; // Round up
    let mut countdown_text: String<64> = String::new();
    write!(countdown_text, "Autoboot {} (slot {}) in {}sec", target, slot, countdown_sec).ok();
    Text::with_alignment(
        &countdown_text,
        Point::new(h_active/2, v_active/2 - 125),
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
    D: DrawTarget<Color = HI8> + OriginDimensions,
{
    let h_active = d.size().width as i32;
    let v_active = d.size().height as i32;
    let norm = MonoTextStyle::new(&FONT_9X15, HI8::new(hue, 11));
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
        Point::new((h_active/2) as i32, (v_active/2+130) as i32 + ot),
        norm,
        Alignment::Center,
    )
    .draw(d).ok();
    Text::with_alignment(
        "Select a bitstream. To return here, hold encoder down for 3sec.",
        Point::new((h_active/2) as i32, (v_active/2-70) as i32 + ot),
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

fn validate_and_copy_spiflash_region(region: &MemoryRegion) -> Result<(), BitstreamError> {
    // Skip regions without spiflash_src (e.g. during simulation)
    let spiflash_src = match region.spiflash_src {
        Some(addr) => addr,
        None => {
            info!("Skip region '{}' (no spiflash_src)", region.filename);
            return Ok(());
        }
    };

    let spiflash_ptr = SPIFLASH_BASE as *mut u32;
    let spiflash_offset_words = spiflash_src as isize / 4isize;
    let size_words = region.size as isize / 4isize + 1;

    match region.region_type {
        RegionType::Bitstream | RegionType::XipFirmware | RegionType::RamLoad => {
            info!("Validate region '{}' at {:#x} (size: {} KiB) ...", 
                  region.filename, SPIFLASH_BASE + spiflash_src as usize, region.size / 1024);
        },
        _ => {
            info!("Skip region '{}' at {:#x} (size: {} KiB) ...", 
                  region.filename, SPIFLASH_BASE + spiflash_src as usize, region.size / 1024);
            return Ok(());
        }
    }

    // Always validate CRC from SPI flash source first
    if let Some(crc_target) = region.crc {
        let crc_bzip2 = crc::Crc::<u32>::new(&crc::CRC_32_BZIP2);
        let mut digest = crc_bzip2.digest();
        for i in 0..size_words {
            unsafe {
                let d = spiflash_ptr.offset(spiflash_offset_words + i).read_volatile();
                if i != (size_words - 1) {
                    digest.update(&d.to_le_bytes());
                } else {
                    digest.update(&d.to_le_bytes()[0..(region.size as usize)%4usize]);
                }
            }
        }
        let crc_result = digest.finalize();
        info!("got SPI flash crc: {:#x}, manifest wants: {:#x}", crc_result, crc_target);
        if crc_result != crc_target {
            return Err(BitstreamError::SpiflashCrcError);
        }
    } else {
        warn!("Expected region.crc target for region '{}'", region.filename);
        return Err(BitstreamError::InvalidManifest);
    }

    // Now copy to PSRAM if needed
    if region.region_type == RegionType::RamLoad {
        if let Some(psram_dst) = region.psram_dst {
            let psram_ptr = PSRAM_BASE as *mut u32;
            let psram_offset_words = psram_dst as isize / 4isize;
            info!("Copying to {:#x}..{:#x} (psram) ...",
                  PSRAM_BASE + psram_dst as usize,
                  PSRAM_BASE + (psram_dst + region.size) as usize);
            for i in 0..size_words {
                unsafe {
                    let d = spiflash_ptr.offset(spiflash_offset_words + i).read_volatile();
                    psram_ptr.offset(psram_offset_words + i).write_volatile(d);
                }
            }
            info!("Copy completed ({} KiB)", (size_words*4) / 1024);
        } else {
            warn!("RamLoad region'{}' without psram_dst! marking invalid...", region.filename);
            return Err(BitstreamError::InvalidManifest);
        }
    }

    Ok(())
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

        // Handle autoboot countdown
        if let Some(slot) = app.autoboot_slot {
            if app.ui.encoder_recently_touched(TIMER0_ISR_PERIOD_MS*2) {
                // Encoder was touched during countdown, cancel autoboot, clear flag for next boot.
                app.autoboot_slot = None;
                app.autoboot_countdown_ms = 0;
                let config = EepromConfig { last_boot_slot: None };
                app.eeprom_manager.write_config(&config).ok();
            } else if app.autoboot_countdown_ms > 0 {
                // Autoboot is configured, continue countdown
                app.autoboot_countdown_ms = app.autoboot_countdown_ms.saturating_sub(TIMER0_ISR_PERIOD_MS);
            } else {
                // Countdown finished, trigger autoboot into selected bitstream
                app.reboot_n = Some(slot);
            }
        }

        if app.ui.opts.tracker.modify {
            if let Some(n) = app.ui.opts.tracker.selected {
                app.reboot_n = Some(n)
            }
        }

        if let Some(n) = app.reboot_n {
            app.time_since_reboot_requested += TIMER0_ISR_PERIOD_MS;
            // Give codec time to mute and display time to draw 'REBOOTING'
            if app.time_since_reboot_requested > 250 {
                // Is there a firmware image to copy to PSRAM before we switch bitstreams?
                let error = if let Some(manifest) = &app.manifests[n].clone() {
                    || -> Result<(), BitstreamError> {
                        if manifest.magic != MANIFEST_MAGIC {
                            Err(BitstreamError::InvalidManifest)?;
                        }
                        if manifest.hw_rev != HW_REV_MAJOR {
                            Err(BitstreamError::HwVersionMismatch)?;
                        }
                        // BootInfo structure placed at the end of PSRAM
                        let mut bootinfo = bootinfo::BootInfo {
                            manifest: manifest.clone(),
                            modeline: app.modeline.clone(),
                        };
                        for region in &manifest.regions {
                            validate_and_copy_spiflash_region(region)?;
                        }
                        // Save this bitstream as the last loaded
                        let config = EepromConfig { last_boot_slot: Some(n as u8) };
                        app.eeprom_manager.write_config(&config).ok();
                        if let Some(mut pll_config) = manifest.external_pll_config.clone() {
                            if pll_config.clk1_inherit {
                                info!("video/pll: inherit pixel clock from bootloader modeline.");
                                pll_config.clk1_hz = Some((bootinfo.modeline.pixel_clk_mhz*1e6f32) as u32);
                                bootinfo.manifest.external_pll_config = Some(pll_config.clone());
                                if FIXED_MODELINE.is_some() {
                                    // Can't boot a dynamic modeline bitstream if the bootloader
                                    // itself only supports static modelines, as we haven't read
                                    // the EDID and so can't forward it. Fix is to only flash other
                                    // bitstreams with static modelines, or reflash the bootloader
                                    // with support for dynamic modelines.
                                    Err(BitstreamError::BootloaderStaticModeline)?;
                                }
                            }
                            // Disable audio components
                            app.ui.pmod.set_aclk_unstable();
                            if let Some(ref mut pll) = app.pll {
                                // Disable DVI PHY before playing with external PLL.
                                unsafe { pac::FRAMEBUFFER_PERIPH::steal() }.flags().write(|w|
                                    w.enable().bit(false)
                                );
                                riscv::asm::delay(10_000_000);
                                configure_external_pll(&pll_config, pll).or(
                                    Err(BitstreamError::PllI2cError))?;
                            } else {
                                // External PLL config is in manifest but this bootloader
                                // didn't set up the PLL (likely hardware / gateware mismatch).
                                Err(BitstreamError::PllBadConfigError)?;
                            }
                        }
                        // Place BootInfo at the end of PSRAM
                        unsafe { bootinfo.to_addr(BOOTINFO_BASE).expect("Failed to serialize BootInfo") };
                        riscv::asm::fence();
                        riscv::asm::fence_i();
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

use embedded_hal::i2c::I2c;

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
    const EDID_READ_ATTEMPTS: usize = 3;
    let mut read_attempts = 0;
    loop {
        info!("video/edid: read_edid from i2c0 address 0x{:x}", EDID_ADDR);
        let mut edid: [u8; 128] = [0; 128];
        for i in 0..16 {
            // WARN: be careful these transactions are not interrupted, because
            // bad EDID transactions could brick monitors.
            i2cdev.transaction(EDID_ADDR, &mut [Operation::Write(&[(i*8) as u8]),
                                                Operation::Read(&mut edid[i*8..i*8+8])]).ok();
        }
        let edid = edid::Edid::parse(&edid);
        info!("video/edid: (attempt {}) read_edid got {:?}", read_attempts, edid);
        match edid {
            Ok(edid_parsed) => return Ok(edid_parsed),
            Err(error) => {
                read_attempts += 1;
                if read_attempts == (EDID_READ_ATTEMPTS+1) {
                    return Err(error)
                }
            }
        }
        riscv::asm::delay(10_000_000);
    }
}

fn modeline_from_edid(edid: edid::Edid) -> Option<DVIModeline> {

    // Read the EDID contents and see if we can use it to dynamically create a
    // sensible modeline. If we can't fine a reasonable descriptor, we return
    // None and assumably the caller falls back to some default modeline.

    info!("video/edid: valid edid. scanning detailed timing descriptors...");
    for descriptor in edid.descriptors.iter() {
        if let edid::Descriptor::DetailedTiming(desc) = descriptor {
            info!("video/edid: checking detailed timing descriptor, contents: {:?}", descriptor);
            if desc.pixel_clock_khz < PIXEL_CLK_MIN_KHZ || desc.pixel_clock_khz > PIXEL_CLK_MAX_KHZ {
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
    if FIXED_MODELINE.is_none() {
        match read_edid(i2cdev) {
            Ok(edid) => match modeline_from_edid(edid) {
                Some(edid_modeline) => edid_modeline,
                _ => DVIModeline::default()
            }
            _ => DVIModeline::default()
        }
    } else {
        DVIModeline::default().maybe_override_fixed(FIXED_MODELINE, CLOCK_DVI_HZ)
    }
}

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    let sysclk = pac::clock::sysclk();
    let serial = Serial0::new(peripherals.UART0);
    let mut timer = Timer0::new(peripherals.TIMER0, sysclk);
    let mut persist = Persist0::new(peripherals.PERSIST_PERIPH);
    let mut pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);

    crate::handlers::logger_init(serial);

    info!("Hello from Tiliqua bootloader!");

    let mut startup_report: String<256> = Default::default();

    // Check if we already started any bitstreams by checking if we already wrote
    // something to the PSRAM for client bitstreams. Warm/Cold boots have different
    // autoboot behavior, this is used to distinguish between them.

    let cold_boot = unsafe { bootinfo::BootInfo::from_addr(BOOTINFO_BASE) }.is_none();
    info!("cold_boot: {}", cold_boot);

    // Read autoboot flag and maybe configure us to start an autoboot countdown by
    // setting 'autoboot_to'.

    let mut autoboot_to: Option<usize> = None;
    let mut eeprom_manager = EepromManager::new(unsafe{I2c1::summon()});
    if !cold_boot {
        // Warm boot: Clear the autoboot flag.
        let config = EepromConfig { last_boot_slot: None };
        eeprom_manager.write_config(&config).ok();
    } else {
        // Cold boot: Check the autoboot flag and boot
        match eeprom_manager.read_config() {
            Ok(config) => {
                log::info!("EepromConfig.read_config() wants: {:?}", config);
                if let Some(slot) = config.last_boot_slot {
                    autoboot_to = Some(slot as usize);
                }
            },
            Err(e) => {
                log::warn!("EepromConfig.read_config() failed: {:?}", e);
            }
        }
    }

    // Verify/reprogram touch sensing NVM

    {
        if HW_REV_MAJOR >= 5 {
            // Rev5+, resetting CODEC is always allowed without popping.
            // So let's just do it to bring the CODEC into a consistent state.
            if cold_boot {
                timer.delay_ms(200); // Wait for POR on eurorack-pmod
            }
            pmod.hard_reset();
        }
        let mut cy8 = Cy8cmbr3108Driver::new(unsafe{I2c1::summon()}, &TOUCH_SENSOR_ORDER);
        if let Err(e) = maybe_reprogram_cy8cmbr3xxx(&mut cy8) {
            let s: &'static str = e.into();
            write!(startup_report, "{}\r\n", s).ok();
        }
    }

    // Fetch initial modeline (may be used for external PLL setup)

    timer.delay_ms(10);
    let mut i2cdev_edid = I2c0::new(unsafe { pac::I2C0::steal() } );
    let mut modeline = modeline_or_fallback(&mut i2cdev_edid);

    // Setup audio clocks on external PLL

    let maybe_external_pll = if USE_EXTERNAL_PLL {
        let i2cdev_mobo_pll = I2c0::new(unsafe { pac::I2C0::steal() } );
        let mut si5351drv = Si5351Device::new_adafruit_module(i2cdev_mobo_pll);
        configure_external_pll(&ExternalPLLConfig{
            clk0_hz: CLOCK_AUDIO_HZ,
            clk1_hz: Some((modeline.pixel_clk_mhz*1e6) as u32),
            clk1_inherit: false,
            spread_spectrum: Some(0.01),
        }, &mut si5351drv).unwrap();
        Some(si5351drv)
    } else {
        None
    };

    // Setup CODEC and load audio calibration.

    let mut i2cdev1 = I2c1::new(peripherals.I2C1);
    if let Err(e) = maybe_restart_codec(&mut i2cdev1, &mut pmod) {
        let s: &'static str = e.into();
        write!(startup_report, "{}\r\n", s).ok();
    }
    calibration::CalibrationConstants::load_or_default(&mut i2cdev1, &mut pmod);

    // Load serialized JSON manifests from spiflash

    let mut manifests: [Option<BitstreamManifest>; 8] = [const { None }; 8];
    for n in 0usize..N_MANIFESTS {
        let size: usize = MANIFEST_SIZE;
        let addr: usize = SPIFLASH_BASE + MANIFEST_OFFSET + (n+1)*SLOT_SIZE;
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
    if let Some(n) = autoboot_to {
        opts.tracker.selected = Some(n);
    }

    let app = Mutex::new(RefCell::new(
            App::new(opts, manifests.clone(), maybe_external_pll, modeline.clone(), autoboot_to, eeprom_manager)));

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

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        let mut logo_coord_ix = 0u32;
        let mut rng = fastrand::Rng::with_seed(0);

        persist.set_persist(256);

        let stroke = PrimitiveStyleBuilder::new()
            .stroke_color(HI8::new(0, 11))
            .stroke_width(1)
            .build();

        palette::ColorPalette::default().write_to_hardware(&mut display);

        log::info!("{}", startup_report);

        s.register(handlers::Interrupt::TIMER0, timer0);
        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);


        let mut last_hpd = display.get_hpd();

        loop {

            let h_active = display.size().width;
            let v_active = display.size().height;

            // Always mute the CODEC to stop pops on flashing while in the bootloader.
            pmod.mute(true);

            let (opts, reboot_n, error_n, final_modeline, autoboot_countdown_ms) = critical_section::with(|cs| {

                let mut app = app.borrow_ref_mut(cs);

                //
                // Dynamic modeline switching.
                // Rising edge hotplug checks EDID, reprograms PLL and reinitializes display.
                //

                if display.get_hpd() && !last_hpd {
                    // Rising edge of DVI HPD
                    info!("video/hpd: display reconnected!");
                    let new_modeline = modeline_or_fallback(&mut i2cdev_edid);
                    info!("video/hpd: modeline was {:?}", modeline);
                    info!("video/hpd: modeline infer {:?}", new_modeline);
                    let mut reprogrammed_pll = false;
                    if new_modeline != modeline {
                        info!("video/hpd: display inferred different modeline to previous. switching timings...");
                        if let Some(ref mut external_pll) = app.pll {
                            // Hold DVI PHY in reset before touching the video PLL
                            unsafe { pac::FRAMEBUFFER_PERIPH::steal() }.flags().write(|w|
                                w.enable().bit(false)
                            );
                            // Configure new pixel clock. Technically we don't need to touch
                            // the audio clock. This might be important to separate if we decide
                            // to support dynamic hotplug timings in user bitstreams where
                            // we want the audio streams to not be interrupted.
                            configure_external_pll(&ExternalPLLConfig{
                                clk0_hz: CLOCK_AUDIO_HZ,
                                clk1_hz: Some((new_modeline.pixel_clk_mhz*1e6) as u32),
                                clk1_inherit: false,
                                spread_spectrum: Some(0.01),
                            }, external_pll).unwrap();
                            reprogrammed_pll = true;
                        }
                    } else {
                        info!("video/hpd: display inferred same modeline as previous. do nothing");
                    }

                    if reprogrammed_pll {
                        // Finally, reinitialize the display.
                        let peripherals = unsafe { pac::Peripherals::steal() };
                        display = DMAFramebuffer0::new(
                            peripherals.FRAMEBUFFER_PERIPH,
                            peripherals.PALETTE_PERIPH,
                            peripherals.BLIT,
                            peripherals.PIXEL_PLOT,
                            peripherals.LINE,
                            PSRAM_FB_BASE,
                            new_modeline.clone(),
                            BLIT_MEM_BASE,
                        );
                        app.modeline = new_modeline;
                    }
                }

                last_hpd = display.get_hpd();

                //
                // Copy out mutable application state
                //

                (app.ui.opts.clone(),
                 app.reboot_n.clone(),
                 app.error_n.clone(),
                 app.modeline.clone(),
                 app.autoboot_countdown_ms)
            });

            modeline = final_modeline;

            draw::draw_options(&mut display, &opts, 100, v_active/2-50, 0).ok();
            draw::draw_name(&mut display, h_active/2, v_active-50, 0, UI_NAME, UI_SHA, &modeline).ok();

            if let Some(n) = opts.tracker.selected {
                draw_summary(&mut display, &manifests[n], &error_n[n], &startup_report, -20, -18, 0);
                if manifests[n].is_some() {
                    Line::new(Point::new(255, (v_active/2 - 55 + (n as u32)*18) as i32),
                              Point::new((h_active/2-90) as i32, (v_active/2+8) as i32))
                              .into_styled(stroke)
                              .draw(&mut display).ok();
                }
            }

            const LINES_PER_LOOP: usize = 2;
            for _ in 0..LINES_PER_LOOP {
                let _ = draw::draw_boot_logo(&mut display,
                                             (h_active/2) as i32,
                                             150 as i32,
                                             logo_coord_ix);
                logo_coord_ix += 1;
            }

            if let Some(_) = reboot_n {
                print_rebooting(&mut display, &mut rng);
            }

            if let Some(n) = autoboot_to {
                if autoboot_countdown_ms > 0 {
                    print_autoboot_countdown(&mut display, autoboot_countdown_ms, n, &names[n]);
                }
            }
        }
    })
}
