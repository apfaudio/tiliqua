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
use tiliqua_hal as hal;
use tiliqua_fw::*;
use tiliqua_lib::*;
use tiliqua_lib::generated_constants::*;
use tiliqua_lib::draw;
use tiliqua_fw::opts::*;

const TUSB322I_ADDR:  u8 = 0x47;
const EEPROM_ADDR:    u8 = 0x52;

use opts::Options;
use hal::pca9635::Pca9635Driver;

impl_ui!(UI,
         Options,
         Encoder0,
         Pca9635Driver<I2c0>,
         EurorackPmod0);

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

        if opts_ro.reference.run.value == EnAutoZero::Run {
            let stimulus_raw = 4000 * opts_ro.reference.volts.value as i16;
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
            match opts_ro.reference.autozero.value {
                AutoZero::AdcZero => {
                    app.ui.opts.caladc.zero0.value += deltas[0];
                    app.ui.opts.caladc.zero1.value += deltas[1];
                    app.ui.opts.caladc.zero2.value += deltas[2];
                    app.ui.opts.caladc.zero3.value += deltas[3];
                }
                AutoZero::DacZero => {
                    app.ui.opts.caldac.zero0.value += deltas[0];
                    app.ui.opts.caldac.zero1.value += deltas[1];
                    app.ui.opts.caldac.zero2.value += deltas[2];
                    app.ui.opts.caldac.zero3.value += deltas[3];
                }
                AutoZero::AdcScale => {
                    app.ui.opts.caladc.scale0.value += deltas[0];
                    app.ui.opts.caladc.scale1.value += deltas[1];
                    app.ui.opts.caladc.scale2.value += deltas[2];
                    app.ui.opts.caladc.scale3.value += deltas[3];
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

    write!(s, "PSRAM memtest\r\n").ok();

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
    write!(s, "  write {} KByte/sec\r\n", ((sysclk as u64) * (psram_sz_test/1024) as u64) / write_ticks as u64).ok();
    write!(s, "  read {} KByte/sec\r\n", ((sysclk as u64) * (psram_sz_test/1024) as u64) / (read_ticks as u64)).ok();

    if psram_fl {
        write!(s, "  FAIL\r\n").ok();
    } else {
        write!(s, "  PASS\r\n").ok();
    }
}

fn spiflash_memtest(s: &mut ReportString, timer: &mut Timer0) {

    write!(s, "SPIFLASH memtest\r\n").ok();

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
    write!(s, "  read {} KByte/sec\r\n", ((sysclk as u64) * (spiflash_sz_test/1024) as u64) / (read_ticks as u64)).ok();

    // TODO: verify there is actually a bitstream header in first N words?
    let mut spiflash_fl = true;
    for i in 0..first_words.len() {
        info!("read @ {:#x} at {:#x}", first_words[i], i);
        if first_words[i] != 0xff && first_words[i] != 0x00 {
            spiflash_fl = false;
        }
    }

    if spiflash_fl {
        write!(s, "  FAIL\r\n").ok();
    } else {
        write!(s, "  PASS\r\n").ok();
    }
}

fn tusb322i_id_test(s: &mut ReportString, i2cdev: &mut I2c0) {
    // Read TUSB322I device ID
    let mut tusb322i_id: [u8; 8] = [0; 8];
    let _ = i2cdev.transaction(TUSB322I_ADDR, &mut [Operation::Write(&[0x00u8]),
                                                    Operation::Read(&mut tusb322i_id)]);
    if tusb322i_id != [0x32, 0x32, 0x33, 0x42, 0x53, 0x55, 0x54, 0x0] {
        let mut ix = 0;
        for byte in tusb322i_id {
            info!("tusb322i_id{}: 0x{:x}", ix, byte);
            ix += 1;
        }
        write!(s, "FAIL: TUSB322I ID\r\n").ok();
    } else {
        write!(s, "PASS: TUSB322I ID\r\n").ok();
    }
}

fn eeprom_id_test(s: &mut ReportString, i2cdev: &mut I2c1) {
    /*
    let err = i2cdev.transaction(EEPROM_ADDR, &mut [Operation::Write(&[0x00u8, 0x42])]);
    info!("err {:?}", err);
    info!("err {:?}", err);
    info!("err {:?}", err);
    info!("err {:?}", err);
    info!("err {:?}", err);
    info!("err {:?}", err);
    info!("err {:?}", err);
    info!("err {:?}", err);
    info!("err {:?}", err);
    */
    let mut eeprom_id: [u8; 4] = [0; 4];
    let err = i2cdev.transaction(EEPROM_ADDR, &mut [Operation::Write(&[0x00u8]),
                                             Operation::Read(&mut eeprom_id)]);
    info!("err {:?}", err);
    let mut ix = 0;
    for byte in eeprom_id {
        info!("eeprom_id{}: 0x{:x}", ix, byte);
        ix += 1;
    }
    write!(s, "PASS: EEPROM ID\r\n").ok();
}

#[derive(Debug)]
struct CalibrationConstants {
    adc_scale: [i32; 4],
    adc_zero:  [i32; 4],
    dac_scale: [i32; 4],
    dac_zero:  [i32; 4],
    checksum:  i32,
}

fn fx18tof32(x: i32) -> f32 {
    (x as f32) / 32768.0f32
}

fn f32tofx18(x: f32) -> i32 {
    (x * 32768.0f32) as i32
}

impl CalibrationConstants {
    fn default() -> Self {
        let adc_dscale = -37139i32;
        let adc_dzero  =    256i32;
        let dac_dscale =  32725i32;
        let dac_dzero  =    983i32;
        let mut result = Self {
            adc_scale: [adc_dscale; 4],
            adc_zero:  [adc_dzero;  4],
            dac_scale: [dac_dscale; 4],
            dac_zero:  [dac_dzero;  4],
            checksum:  0i32,
        };
        result.checksum = result.compute_checksum();
        result
    }

    fn compute_checksum(&self) -> i32 {
        let mut sum = 0i32;
        for n in 0..4 {
            sum += self.adc_scale[n] + self.adc_zero[n] +
                   self.dac_scale[n] + self.dac_zero[n]
        }
        sum
    }

    fn from_eeprom(i2cdev: &mut I2c1) -> Option<Self> {
        let mut constants = [0i32; 8*2+1];
        for n in 0..constants.len() {
            let mut rx_bytes = [0u8; 4];
            let err = i2cdev.transaction(EEPROM_ADDR, &mut [Operation::Write(&[(n*4) as u8]),
                                                            Operation::Read(&mut rx_bytes)]);
            constants[n] = i32::from_le_bytes(rx_bytes);
            info!("from_eeprom n={} err={:?} constant={}", n, err, constants[n]);
        }

        let mut result = Self {
            adc_scale: [0i32; 4],
            adc_zero:  [0i32; 4],
            dac_scale: [0i32; 4],
            dac_zero:  [0i32; 4],
            checksum:  0i32,
        };

        for ch in 0..4usize {
            result.adc_scale[ch] = constants[2*ch+0];
            result.adc_zero[ch]  = constants[2*ch+1];
            result.dac_scale[ch] = constants[2*ch+8+0];
            result.dac_zero[ch]  = constants[2*ch+8+1];
        }

        result.checksum = constants[constants.len()-1];
        if result.compute_checksum() == result.checksum {
            Some(result)
        } else {
            None
        }
    }

    fn write_to_eeprom(&self, i2cdev: &mut I2c1) {
        let mut constants = [0i32; 8*2+1];
        for ch in 0..4usize {
            constants[2*ch+0]   = self.adc_scale[ch];
            constants[2*ch+1]   = self.adc_zero[ch];
            constants[2*ch+8+0] = self.dac_scale[ch];
            constants[2*ch+8+1] = self.dac_zero[ch];
        }
        constants[constants.len()-1] = self.compute_checksum();
        for n in 0..constants.len() {
            let mut tx_bytes = [0u8; 5];
            tx_bytes[0] = (4*n) as u8; // 4 bytes storage per constant
            tx_bytes[1..5].clone_from_slice(&constants[n].to_le_bytes());
            loop {
                match i2cdev.transaction(EEPROM_ADDR, &mut [Operation::Write(&tx_bytes)]) {
                    Ok(_) => break,
                    _ => {}
                }
            }
        }
    }

    fn write_to_pmod(&self, pmod: &mut EurorackPmod0) {
        for ch in 0..4usize {
            pmod.write_calibration_constant(
                ch as u8,
                self.adc_scale[ch],
                self.adc_zero[ch],
            );
            pmod.write_calibration_constant(
                (ch+4) as u8,
                self.dac_scale[ch],
                self.dac_zero[ch],
            );
        }
    }

    fn adc_default_gamma_delta() -> (f32, f32) {
        let defaults = Self::default();
        let adc_gamma_default  = 1.0f32/fx18tof32(defaults.adc_scale[0]);
        let adc_delta_default  = -fx18tof32(defaults.adc_zero[0])*adc_gamma_default;
        (adc_gamma_default, adc_delta_default)
    }

    fn from_opts(opts: &Options) -> Self {
        let defaults   = Self::default();
        let mut result = Self::default();
        // DAC
        {
            let zero = [
                opts.caldac.zero0.value,
                opts.caldac.zero1.value,
                opts.caldac.zero2.value,
                opts.caldac.zero3.value,
            ];
            let scale = [
                opts.caldac.scale0.value,
                opts.caldac.scale1.value,
                opts.caldac.scale2.value,
                opts.caldac.scale3.value,
            ];
            for ch in 0..4usize {
                result.dac_scale[ch] = defaults.dac_scale[0] + 4*scale[ch] as i32;
                result.dac_zero[ch]  = defaults.dac_zero[0]  + 2*zero[ch] as i32; // FIXME 2x/4x
            }
        }
        // ADC
        {
            let zero = [
                opts.caladc.zero0.value,
                opts.caladc.zero1.value,
                opts.caladc.zero2.value,
                opts.caladc.zero3.value,
            ];
            let scale = [
                opts.caladc.scale0.value,
                opts.caladc.scale1.value,
                opts.caladc.scale2.value,
                opts.caladc.scale3.value,
            ];
            let (adc_gd, adc_dd) = CalibrationConstants::adc_default_gamma_delta();
            for ch in 0..4usize {
                let adc_gamma      = adc_gd + 0.00010*(scale[ch] as f32);
                let adc_delta      = adc_dd + 0.00005*(zero[ch] as f32);
                result.adc_scale[ch] = f32tofx18(1.0f32/adc_gamma);
                result.adc_zero[ch]  = f32tofx18(-adc_delta/adc_gamma);
            }
        }
        result
    }

    fn push_to_opts(&self, opts: &mut Options) {
        let mut dac_scale = [0i16; 4];
        let mut dac_zero  = [0i16; 4];
        let mut adc_scale = [0i16; 4];
        let mut adc_zero  = [0i16; 4];
        let defaults = Self::default();
        let (adc_gd, adc_dd) = CalibrationConstants::adc_default_gamma_delta();
        for ch in 0..4usize {
            let adc_gamma = 1.0f32/fx18tof32(self.adc_scale[ch]);
            adc_scale[ch] = ((adc_gamma - adc_gd) / 0.00010) as i16;
            let adc_delta = -fx18tof32(self.adc_zero[ch])*adc_gamma;
            adc_zero[ch]  = ((adc_delta - adc_dd) / 0.00005) as i16;
            dac_scale[ch] = ((self.dac_scale[ch] - defaults.dac_scale[0]) / 4) as i16;
            dac_zero[ch]  = ((self.dac_zero[ch]  -  defaults.dac_zero[0]) / 2) as i16;
        }
        opts.caldac.scale0.value = dac_scale[0];
        opts.caldac.scale1.value = dac_scale[1];
        opts.caldac.scale2.value = dac_scale[2];
        opts.caldac.scale3.value = dac_scale[3];
        opts.caldac.zero0.value  = dac_zero[0];
        opts.caldac.zero1.value  = dac_zero[1];
        opts.caldac.zero2.value  = dac_zero[2];
        opts.caldac.zero3.value  = dac_zero[3];
        opts.caladc.scale0.value = adc_scale[0];
        opts.caladc.scale1.value = adc_scale[1];
        opts.caladc.scale2.value = adc_scale[2];
        opts.caladc.scale3.value = adc_scale[3];
        opts.caladc.zero0.value  = adc_zero[0];
        opts.caladc.zero1.value  = adc_zero[1];
        opts.caladc.zero2.value  = adc_zero[2];
        opts.caladc.zero3.value  = adc_zero[3];
    }
}


fn print_touch_err(s: &mut ReportString, pmod: &EurorackPmod0)
{
    if pmod.touch_err() != 0 {
        write!(s, "FAIL: TOUCH IC NAK\r\n").ok();
    } else {
        write!(s, "PASS: TOUCH IC\r\n").ok();
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

    write!(s, "PASS: TUSB322I state 0x{:x} (DUA={} DDC={} VF={} IS={} CD={} AS={})\r\n",
          tusb322_conn_status[0],
          tusb322_conn_status[0]        & 0x1,
          (tusb322_conn_status[0] >> 1) & 0x3,
          (tusb322_conn_status[0] >> 3) & 0x1,
          (tusb322_conn_status[0] >> 4) & 0x1,
          (tusb322_conn_status[0] >> 5) & 0x1,
          (tusb322_conn_status[0] >> 6) & 0x3,
          ).ok();
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
    write!(s, "PASS: die_temp [code={} celsius={}]\r\n",
           code,
           code_to_celsius[code as usize]).ok();
}

struct App {
    ui: UI,
}

impl App {
    pub fn new(opts: Options) -> Self {
        let peripherals = unsafe { pac::Peripherals::steal() };
        let encoder = Encoder0::new(peripherals.ENCODER0);
        let pmod = EurorackPmod0::new(peripherals.PMOD0_PERIPH);
        let i2cdev = I2c0::new(peripherals.I2C0);
        let pca9635 = Pca9635Driver::new(i2cdev);
        Self {
            ui: UI::new(opts, TIMER0_ISR_PERIOD_MS,
                        encoder, pca9635, pmod),
        }
    }
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

    let mut report = ReportString::new();
    eeprom_id_test(&mut report, &mut i2cdev1);
    psram_memtest(&mut report, &mut timer);
    spiflash_memtest(&mut report, &mut timer);
    tusb322i_id_test(&mut report, &mut i2cdev);
    print_touch_err(&mut report, &pmod);
    print_usb_state(&mut report, &mut i2cdev);
    print_die_temperature(&mut report, &dtr);
    info!("STARTUP REPORT: {}", report);

    timer.disable();
    timer.delay_ns(0);

    let mut display = DMADisplay {
        framebuffer_base: PSRAM_FB_BASE as *mut u32,
    };

    write_palette(&mut video, palette::ColorPalette::Linear);
    video.set_persist(256);

    let mut opts = opts::Options::new();

    if let Some(cal_constants) = CalibrationConstants::from_eeprom(&mut i2cdev1) {
        cal_constants.push_to_opts(&mut opts);
    } else {
        CalibrationConstants::default().push_to_opts(&mut opts);
    }

    /*
    er.write_to_eeprom(&mut i2cdev1);
    info!("DELAY");
    info!("DELAY");
    info!("DELAY");
    info!("DELAY");
    info!("DELAY");
    info!("READDDD {:?}", CalibrationConstants::from_eeprom(&mut i2cdev1));
    */


    let app = Mutex::new(RefCell::new(App::new(opts)));
    let hue = 10;

    handler!(timer0 = || timer0_handler(&app));

    irq::scope(|s| {

        s.register(handlers::Interrupt::TIMER0, timer0);

        timer.enable_tick_isr(TIMER0_ISR_PERIOD_MS,
                              pac::Interrupt::TIMER0);

        loop {
            let opts = critical_section::with(|cs| {
                let app = app.borrow_ref(cs);
                app.ui.opts.clone()
            });

            let stimulus_raw = 4000 * opts.reference.volts.value as i16;

            draw::draw_options(&mut display, &opts, H_ACTIVE/2-30, 70,
                               hue).ok();
            draw::draw_name(&mut display, H_ACTIVE/2, 30, hue, UI_NAME, UI_SHA).ok();

            if opts.screen.value == opts::Screen::StartupReport {
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
                    "[startup report]",
                    &report
                ).ok();
            }

            if opts.screen.value == opts::Screen::Autocal {
                pmod.registers.sample_o0().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
                pmod.registers.sample_o1().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
                pmod.registers.sample_o2().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
                pmod.registers.sample_o3().write(|w| unsafe { w.sample().bits(stimulus_raw as u16) } );
            }

            //
            // Push calibration constants to audio interface
            //
            let constants = CalibrationConstants::from_opts(&opts);
            constants.write_to_pmod(&mut pmod);

            if opts.screen.value != opts::Screen::StartupReport {
                draw::draw_cal(&mut display, H_ACTIVE/2-128, V_ACTIVE/2-128, hue,
                               &[stimulus_raw, stimulus_raw, stimulus_raw, stimulus_raw],
                               &pmod.sample_i()).ok();
                draw::draw_cal_constants(
                    &mut display, H_ACTIVE/2-128, V_ACTIVE/2+64, hue,
                    &constants.adc_scale, &constants.adc_zero, &constants.dac_scale, &constants.dac_zero).ok();

                if opts.reference.print.value == EnSerialPrint::SerialOn {
                    let mut s: String<256> = String::new();
                    write!(s, "cal_constants = [\n\r").ok();
                    for ch in 0..4 {
                        write!(s, "  [{:.4}, {:.4}],\n\r",
                              constants.adc_scale[ch as usize] as f32 / 32768f32,
                              constants.adc_zero[ch as usize] as f32 / 32768f32).ok();
                    }
                    for ch in 0..4 {
                        write!(s, "  [{:.4}, {:.4}],\n\r",
                              constants.dac_scale[ch as usize] as f32 / 32768f32,
                              constants.dac_zero[ch as usize] as f32 / 32768f32).ok();
                    }
                    write!(s, "]\n\r").ok();
                    log::info!("{}", s);
                    constants.write_to_eeprom(&mut i2cdev1);
                }
            }

        }
    })
}
