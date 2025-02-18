#![no_std]
#![no_main]

use riscv_rt::entry;
use irq::handler;
use log::{info, error};

use critical_section::Mutex;
use core::cell::RefCell;
use core::convert::TryInto;
use core::fmt::Write;

use embedded_hal::i2c::Operation;
use embedded_hal::i2c::I2c;
use embedded_hal::delay::DelayNs;
use embedded_graphics::{
    pixelcolor::{Gray8, GrayColor},
    prelude::*,
};

use heapless::String;

use tiliqua_pac as pac;
use tiliqua_fw::*;
use tiliqua_lib::*;
use tiliqua_lib::generated_constants::*;
use tiliqua_lib::draw;
use tiliqua_lib::calibration::*;
use tiliqua_fw::options::*;
use tiliqua_hal::video::Video;
use tiliqua_hal::pmod::EurorackPmod;
use tiliqua_hal::pca9635::Pca9635Driver;

const TUSB322I_ADDR:  u8 = 0x47;

pub type ReportString = String<512>;

tiliqua_hal::impl_dma_display!(DMADisplay, H_ACTIVE, V_ACTIVE, VIDEO_ROTATE_90);

pub const TIMER0_ISR_PERIOD_MS: u32 = 10;

fn timer0_handler(app: &Mutex<RefCell<App>>) {

    critical_section::with(|cs| {

        let mut app = app.borrow_ref_mut(cs);

        //
        // Update UI and options
        //

        app.ui.update();

        let opts_ro = app.ui.opts.clone();

        if opts_ro.autocal.autozero.value == EnAutoZero::Run {
            let stimulus_raw = 4000 * opts_ro.autocal.volts.value as i16;
            let sample_i = app.ui.pmod.sample_i();
            let mut deltas = [0i16; 4];
            for ch in 0..4 {
                let delta = (sample_i[ch] - stimulus_raw)/4;
                if delta.abs() < 1024 {
                    if delta > 0 {
                        deltas[ch] = -1;
                    } else if delta < 0 {
                        deltas[ch] = 1;
                    }
                }
            }
            match opts_ro.autocal.set.value {
                AutoZero::AdcZero => {
                    app.ui.opts.caladc.zero0.value  += deltas[0];
                    app.ui.opts.caladc.zero1.value  += deltas[1];
                    app.ui.opts.caladc.zero2.value  += deltas[2];
                    app.ui.opts.caladc.zero3.value  += deltas[3];
                }
                AutoZero::AdcScale => {
                    app.ui.opts.caladc.scale0.value += deltas[0];
                    app.ui.opts.caladc.scale1.value += deltas[1];
                    app.ui.opts.caladc.scale2.value += deltas[2];
                    app.ui.opts.caladc.scale3.value += deltas[3];
                }
                AutoZero::DacZero => {
                    app.ui.opts.caldac.zero0.value  += deltas[0];
                    app.ui.opts.caldac.zero1.value  += deltas[1];
                    app.ui.opts.caldac.zero2.value  += deltas[2];
                    app.ui.opts.caldac.zero3.value  += deltas[3];
                }
                AutoZero::DacScale => {
                    app.ui.opts.caldac.scale0.value += deltas[0];
                    app.ui.opts.caldac.scale1.value += deltas[1];
                    app.ui.opts.caldac.scale2.value += deltas[2];
                    app.ui.opts.caldac.scale3.value += deltas[3];
                }
            }
        }

    });
}

fn psram_memtest(s: &mut ReportString, timer: &mut Timer0) {

    // WARN: assume framebuffer is at the start of PSRAM - don't try memtesting that section.

    let psram_ptr = PSRAM_BASE as *mut u32;
    let psram_sz_test = 1024;

    timer.enable();
    timer.set_timeout_ticks(0xFFFFFFFF);

    let start = timer.counter();

    unsafe {
        for i in (PSRAM_SZ_WORDS - psram_sz_test)..PSRAM_SZ_WORDS {
            psram_ptr.offset(i as isize).write_volatile(i as u32);
        }
    }

    pac::cpu::vexriscv::flush_dcache();

    let endwrite = timer.counter();

    let mut psram_fl = false;
    unsafe {
        for i in (PSRAM_SZ_WORDS - psram_sz_test)..PSRAM_SZ_WORDS {
            let value = psram_ptr.offset(i as isize).read_volatile();
            if (i as u32) != value {
                psram_fl = true;
                error!("FAIL: PSRAM selftest @ {:#x} is {:#x}", i, value);
            }
        }
    }

    let endread = timer.counter();

    let write_ticks = start-endwrite;
    let read_ticks = endwrite-endread;

    let sysclk = pac::clock::sysclk();
    if psram_fl {
        write!(s, "FAIL: PSRAM memtest\r\n").ok();

    } else {
        write!(s, "PASS: PSRAM memtest\r\n").ok();
    }

    write!(s, "  write {} KByte/sec\r\n", ((sysclk as u64) * (psram_sz_test/1024) as u64) / write_ticks as u64).ok();
    write!(s, "  read {} KByte/sec\r\n", ((sysclk as u64) * (psram_sz_test/1024) as u64) / (read_ticks as u64)).ok();
}

fn spiflash_memtest(s: &mut ReportString, timer: &mut Timer0) {

    let spiflash_ptr = SPIFLASH_BASE as *mut u32;
    let spiflash_sz_test = 1024;

    timer.enable();
    timer.set_timeout_ticks(0xFFFFFFFF);

    let start = timer.counter();

    let mut first_words: [u32; 8] = [0u32; 8];

    unsafe {
        for i in 0..spiflash_sz_test {
            let value = spiflash_ptr.offset(i as isize).read_volatile();
            if i < first_words.len() {
                first_words[i] = value
            }
        }
    }

    let read_ticks = start-timer.counter();

    let sysclk = pac::clock::sysclk();

    // TODO: verify there is actually a bitstream header in first N words?
    let mut spiflash_fl = true;
    for i in 0..first_words.len() {
        info!("spiflash_memtest: read @ {:#x} at {:#x}", first_words[i], i);
        if first_words[i] != 0xff && first_words[i] != 0x00 {
            spiflash_fl = false;
        }
    }

    if spiflash_fl {
        write!(s, "FAIL: SPIFLASH memtest\r\n").ok();
    } else {
        write!(s, "PASS: SPIFLASH memtest\r\n").ok();
    }
    write!(s, "  read {} KByte/sec\r\n", ((sysclk as u64) * (spiflash_sz_test/1024) as u64) / (read_ticks as u64)).ok();
}

fn tusb322i_id_test(s: &mut ReportString, i2cdev: &mut I2c0) {
    // Read TUSB322I device ID
    let mut tusb322i_id: [u8; 8] = [0; 8];
    let _ = i2cdev.transaction(TUSB322I_ADDR, &mut [Operation::Write(&[0x00u8]),
                                                    Operation::Read(&mut tusb322i_id)]);
    if tusb322i_id != [0x32, 0x32, 0x33, 0x42, 0x53, 0x55, 0x54, 0x0] {
        write!(s, "FAIL: tusb322i_id ").ok();
    } else {
        write!(s, "PASS: tusb322i_id ").ok();
    }
    for byte in tusb322i_id {
        write!(s, "{:x} ", byte).ok();
    }
    write!(s, "\r\n").ok();
}

fn eeprom_id_test(s: &mut ReportString, i2cdev: &mut I2c1) -> bool {
    let mut ok = false;
    let mut eeprom_id: [u8; 6] = [0; 6];
    let err = i2cdev.transaction(EEPROM_ADDR, &mut [Operation::Write(&[0xFAu8]),
                                                    Operation::Read(&mut eeprom_id)]);
    if !err.is_ok() {
        write!(s, "FAIL: eeprom_id (nak?) ").ok();
    } else if eeprom_id[0] == 0x29 {
        ok = true;
        write!(s, "PASS: eeprom_id ").ok();
    } else {
        write!(s, "FAIL: eeprom_id ").ok();
    }
    for byte in eeprom_id {
        write!(s, "{:x} ", byte).ok();
    }
    write!(s, "\r\n").ok();
    ok
}

fn print_touch_err(s: &mut ReportString, pmod: &EurorackPmod0)
{
    if pmod.touch_err() != 0 {
        write!(s, "FAIL: cy8cmbr_nak\r\n").ok();
    } else {
        write!(s, "PASS: cy8cmbr_nak\r\n").ok();
    }
}

fn print_usb_state(s: &mut ReportString, i2cdev: &mut I2c0)
{
    // Read TUSB322I connection status register
    // We don't use this yet. But it's useful for checking for usb circuitry assembly problems.
    // (in particular the cable orientation detection registers)
    let mut tusb322_conn_status: [u8; 1] = [0; 1];
    let _ = i2cdev.transaction(TUSB322I_ADDR, &mut [Operation::Write(&[0x09u8]),
                                                    Operation::Read(&mut tusb322_conn_status)]);

    write!(s, "tusb322i_state 0x{:x} (DUA={} DDC={} VF={} IS={} CD={} AS={})\r\n",
          tusb322_conn_status[0],
          tusb322_conn_status[0]        & 0x1,
          (tusb322_conn_status[0] >> 1) & 0x3,
          (tusb322_conn_status[0] >> 3) & 0x1,
          (tusb322_conn_status[0] >> 4) & 0x1,
          (tusb322_conn_status[0] >> 5) & 0x1,
          (tusb322_conn_status[0] >> 6) & 0x3,
          ).ok();
}

fn print_pmod_state(s: &mut ReportString, pmod: &impl EurorackPmod)
{
    let si = pmod.sample_i();
    write!(s, "audio_samples [ch0={:06} ch1={:06}\r\n",
           si[0] as i16,
           si[1] as i16).ok();
    write!(s, "               ch2={:06} ch3={:06}]\r\n",
           si[2] as i16,
           si[3] as i16).ok();
    write!(s, "audio_if      [jack={:x} touch_err={:x}]\r\n",
           pmod.jack(),
           pmod.touch_err()).ok();
    let touch = pmod.touch();
    write!(s, "audio_touch   [t0={:x} t1={:x} t2={:x} t3={:x}\r\n",
           touch[0], touch[1], touch[2], touch[3]).ok();
    write!(s, "               t4={:x} t5={:x} t6={:x} t7={:x}]\r\n",
           touch[4], touch[5], touch[6], touch[7]).ok();
}

fn print_die_temperature(s: &mut ReportString, dtr: &pac::DTR0)
{
    // From Table 4.3 in FPGA-TN-02210-1-4
    // "Power Consumption and Management for ECP5 and ECP5-5G Devices"
    let code_to_celsius: [i16; 64] = [
        -58, -56, -54, -52, -45, -44, -43, -42,
        -41, -40, -39, -38, -37, -36, -30, -20,
        -10,  -4,   0,   4,  10,  21,  22,  23,
         24,  25,  26,  27,  28,  29,  40,  50,
         60,  70,  76,  80,  81,  82,  83,  84,
         85,  86,  87,  88,  89,  95,  96,  97,
         98,  99, 100, 101, 102, 103, 104, 105,
        106, 107, 108, 116, 120, 124, 128, 132
    ];
    let code = dtr.temperature().read().bits();
    write!(s, "die_temp [code={} celsius={}]\r\n",
           code,
           code_to_celsius[code as usize]).ok();
}

struct App {
    ui: ui::UI<Encoder0, EurorackPmod0, I2c0, Opts>,
}

impl App {
    pub fn new(opts: Opts) -> Self {
        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        Self {
            ui: ui::UI::new(opts, TIMER0_ISR_PERIOD_MS,
                            encoder, pca9635, pmod),
        }
    }
}

fn push_to_opts(constants: &CalibrationConstants, options: &mut Opts) {
    let c = constants.to_tweakable();
    options.caladc.scale0.value = c.adc_scale[0];
    options.caladc.scale1.value = c.adc_scale[1];
    options.caladc.scale2.value = c.adc_scale[2];
    options.caladc.scale3.value = c.adc_scale[3];
    options.caladc.zero0.value  = c.adc_zero[0];
    options.caladc.zero1.value  = c.adc_zero[1];
    options.caladc.zero2.value  = c.adc_zero[2];
    options.caladc.zero3.value  = c.adc_zero[3];
    options.caldac.scale0.value = c.dac_scale[0];
    options.caldac.scale1.value = c.dac_scale[1];
    options.caldac.scale2.value = c.dac_scale[2];
    options.caldac.scale3.value = c.dac_scale[3];
    options.caldac.zero0.value  = c.dac_zero[0];
    options.caldac.zero1.value  = c.dac_zero[1];
    options.caldac.zero2.value  = c.dac_zero[2];
    options.caldac.zero3.value  = c.dac_zero[3];
}

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();

    // initialize logging
    let serial = Serial0::new(peripherals.UART0);
    tiliqua_fw::handlers::logger_init(serial);

    let sysclk = pac::clock::sysclk();
    let mut timer = Timer0::new(peripherals.TIMER0, sysclk);
    let mut video = Video0::new(peripherals.VIDEO_PERIPH);

    info!("Hello from Tiliqua selftest!");

    let mut i2cdev = I2c0::new(peripherals.I2C0);
    let mut i2cdev1 = I2c1::new(peripherals.I2C1);
    let mut pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
    let dtr = peripherals.DTR0;

    let mut startup_report = ReportString::new();
    psram_memtest(&mut startup_report, &mut timer);
    spiflash_memtest(&mut startup_report, &mut timer);
    tusb322i_id_test(&mut startup_report, &mut i2cdev);
    print_touch_err(&mut startup_report, &pmod);
    eeprom_id_test(&mut startup_report, &mut i2cdev1);

    timer.disable();
    timer.delay_ns(0);

    let mut display = DMADisplay {
        framebuffer_base: PSRAM_FB_BASE as *mut u32,
    };

    palette::ColorPalette::default().write_to_hardware(&mut video);
    video.set_persist(512);

    let mut opts = Opts::default();

    if let Some(cal_constants) = CalibrationConstants::from_eeprom(&mut i2cdev1) {
        push_to_opts(&cal_constants, &mut opts);
        write!(startup_report, "PASS: load calibration from EEPROM").ok();
    } else {
        push_to_opts(&CalibrationConstants::default(), &mut opts);
        write!(startup_report, "FAIL: load calibration from EEPROM").ok();
    }
    info!("STARTUP REPORT: {}", startup_report);

    let app = Mutex::new(RefCell::new(App::new(opts)));
    let hue = 10;

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        loop {
            let (opts, commit_to_eeprom) = critical_section::with(|cs| {
                let mut app = app.borrow_ref_mut(cs);
                // Single-shot commit: when 'write' is selected and the encoder
                // is turned, write once and change the enum back.
                let mut commit_to_eeprom = false;
                if app.ui.opts.autocal.write.value != EnWrite::Turn {
                    commit_to_eeprom = true;
                    app.ui.opts.autocal.write.value = EnWrite::Turn;
                }
                (app.ui.opts.clone(), commit_to_eeprom)
            });

            let stimulus_raw = 4000 * opts.autocal.volts.value as i16;

            draw::draw_options(&mut display, &opts, H_ACTIVE/2-30, 70,
                               hue).ok();
            draw::draw_name(&mut display, H_ACTIVE/2, 30, hue, UI_NAME, UI_SHA).ok();

            if opts.tracker.page.value == Page::Report {
                let mut status_report = ReportString::new();
                let (page_name, report_str) = match opts.report.page.value {
                    ReportPage::Startup => ("[startup report]", &startup_report),
                    ReportPage::Status  => {
                        print_pmod_state(&mut status_report, &pmod);
                        print_usb_state(&mut status_report, &mut i2cdev);
                        print_die_temperature(&mut status_report, &dtr);
                        info!("STATUS REPORT: {}", status_report);
                        ("[status report]", &status_report)
                    }
                };
                draw::draw_tiliqua(&mut display, H_ACTIVE/2-80, V_ACTIVE/2-200, hue,
                    [
                    //  "touch  jack "
                        "-      adc0 ",
                        "-      adc1 ",
                        "-      adc2 ",
                        "-      adc3 ",
                        "-      dac0 ",
                        "-      dac1 ",
                        "-      dac2 ",
                        "-      dac3 ",
                    ],
                    [
                        "menu",
                        "-",
                        "video",
                        "-",
                        "-",
                        "-",
                    ],
                    &page_name,
                    report_str
                ).ok();
            }

            if opts.tracker.page.value == Page::Autocal {
                pmod.registers.sample_o0().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
                pmod.registers.sample_o1().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
                pmod.registers.sample_o2().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
                pmod.registers.sample_o3().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
            }

            //
            // Push calibration constants to audio interface
            //
            let constants = CalibrationConstants::from_tweakable(
                TweakableConstants {
                    adc_scale: [
                        opts.caladc.scale0.value,
                        opts.caladc.scale1.value,
                        opts.caladc.scale2.value,
                        opts.caladc.scale3.value,
                    ],
                    adc_zero: [
                        opts.caladc.zero0.value,
                        opts.caladc.zero1.value,
                        opts.caladc.zero2.value,
                        opts.caladc.zero3.value,
                    ],
                    dac_scale: [
                        opts.caldac.scale0.value,
                        opts.caldac.scale1.value,
                        opts.caldac.scale2.value,
                        opts.caldac.scale3.value,
                    ],
                    dac_zero: [
                        opts.caldac.zero0.value,
                        opts.caldac.zero1.value,
                        opts.caldac.zero2.value,
                        opts.caldac.zero3.value,
                    ],
                }
            );
            constants.write_to_pmod(&mut pmod);

            if opts.tracker.page.value != Page::Report {
                draw::draw_cal(&mut display, H_ACTIVE/2-128, V_ACTIVE/2-128, hue,
                               &[stimulus_raw, stimulus_raw, stimulus_raw, stimulus_raw],
                               &pmod.sample_i()).ok();
                draw::draw_cal_constants(
                    &mut display, H_ACTIVE/2-128, V_ACTIVE/2+64, hue,
                    &constants.adc_scale, &constants.adc_zero, &constants.dac_scale, &constants.dac_zero).ok();

                if commit_to_eeprom {
                    constants.write_to_eeprom(&mut i2cdev1);
                    draw::draw_name(&mut display, H_ACTIVE/2, V_ACTIVE/2+64, hue, &"SAVED", &"").ok();
                }
            }

        }
    })
}
