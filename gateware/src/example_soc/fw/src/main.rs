#![no_std]
#![no_main]

use core::panic::PanicInfo;

use tiliqua_pac as pac;
use lunasoc_hal as hal;

use hal::hal::delay::DelayUs;

use tiliqua_fw::Serial0;
use tiliqua_fw::Timer0;

use log::{info, error};

use riscv_rt::entry;

#[riscv_rt::pre_init]
unsafe fn pre_main() {
    pac::cpu::vexriscv::flush_icache();
    pac::cpu::vexriscv::flush_dcache();
}

#[cfg(not(test))]
#[panic_handler]
fn panic(panic_info: &PanicInfo) -> ! {
    if let Some(location) = panic_info.location() {
        error!("panic(): file '{}' at line {}",
            location.file(),
            location.line(),
        );
    } else {
        error!("panic(): no location information");
    }
    loop {}
}

#[export_name = "ExceptionHandler"]
fn exception_handler(trap_frame: &riscv_rt::TrapFrame) -> ! {
    error!("exception_handler(): TrapFrame.ra={:x}", trap_frame.ra);
    loop {}
}

#[export_name = "DefaultHandler"]
fn default_isr_handler() -> ! {
    error!("default_isr_handler()");
    loop {}
}

#[entry]
fn main() -> ! {
    let peripherals = pac::Peripherals::take().unwrap();
    let leds = &peripherals.LEDS;

    // initialize logging
    let serial = Serial0::new(peripherals.UART);
    tiliqua_fw::log::init(serial);

    let mut timer = Timer0::new(peripherals.TIMER, pac::clock::sysclk());
    let mut counter = 0;
    let mut direction = true;
    let mut led_state = 0b110000;

    info!("Peripherals initialized.");

    info!("PSRAM memtest...");

    // PSRAM memtest

    unsafe {
        const HRAM_BASE: usize = 0x20000000;
        let hram_ptr = HRAM_BASE as *mut u32;

        timer.enable();
        timer.set_timeout_ticks(0xFFFFFFFF);

        let start = timer.counter();

        for i in 0..(1024*1024*4) {
            hram_ptr.offset(i).write_volatile(i as u32);
        }

        let endwrite = timer.counter();

        for i in 0..(1024*1024*4) {
            if (i as u32) != hram_ptr.offset(i).read_volatile() {
                info!("hyperram FL @ {:#x}", i);
            }
        }

        let endread = timer.counter();

        let write_ticks = start-endwrite;
        let read_ticks = endwrite-endread;

        let sysclk = pac::clock::sysclk();

        info!("write speed {} KByte/sec", ((sysclk as u64) * (16*1024) as u64) / write_ticks as u64);

        info!("read speed {} KByte/sec", ((sysclk as u64) * (16*1024 as u64)) / (read_ticks as u64));

    }

    loop {
        timer.delay_ms(100).unwrap();

        if direction {
            led_state >>= 1;
            if led_state == 0b000011 {
                direction = false;
                info!("left: {}", counter);
            }
        } else {
            led_state <<= 1;
            if led_state == 0b110000 {
                direction = true;
                info!("right: {}", counter);
            }
        }

        leds.output().write(|w| unsafe { w.output().bits(led_state) });
        counter += 1;
    }
}
