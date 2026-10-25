#[doc(hidden)]
pub use irq;
#[doc(hidden)]
pub use amaranth_soc_isr;
#[doc(hidden)]
pub use log;
#[doc(hidden)]
pub use tiliqua_hal::riscv_peripheral;
#[doc(hidden)]
pub use tiliqua_hal::clint;

#[macro_export]
macro_rules! impl_tick {
    ($clint:ty) => {
        pub mod tick {
            use super::*;
            use ::core::sync::atomic::{AtomicU32, Ordering};
            use $crate::rt::riscv_peripheral::aclint::{Clint as _, CLINT};

            $crate::rt::irq::scoped_interrupts! {
                #[allow(non_camel_case_types)]
                pub enum Interrupt {
                    TICK,
                }
                use #[$crate::rt::amaranth_soc_isr::return_as_is];
            }

            static PERIOD: AtomicU32 = AtomicU32::new(0);

            #[riscv_rt::core_interrupt(riscv::interrupt::Interrupt::MachineTimer)]
            fn machine_timer() {
                let mtimer = CLINT::<$clint>::new().mtimer();
                let cmp = mtimer.mtimecmp_mhartid().read();
                if $crate::rt::clint::mtime::<$clint>() < cmp {
                    return;
                }
                unsafe { TICK(); }
                let period = u64::from(PERIOD.load(Ordering::Relaxed));
                let now = $crate::rt::clint::mtime::<$clint>();
                let mut next = cmp + period;
                while next <= now {
                    next += period;
                }
                $crate::rt::clint::set_mtimecmp::<$clint>(next);
            }

            pub fn enable(period_ms: u32) {
                let mtimer = CLINT::<$clint>::new().mtimer();
                let period = (<$clint>::MTIME_FREQ / 1000) as u32 * period_ms;
                PERIOD.store(period, Ordering::Relaxed);
                $crate::rt::clint::set_mtimecmp::<$clint>($crate::rt::clint::mtime::<$clint>() + u64::from(period));
                unsafe {
                    mtimer.enable();
                    riscv::interrupt::enable();
                }
            }
        }
    };
}

#[macro_export]
macro_rules! impl_handlers {
    ($serial:ty) => {
        pub mod handlers {
            use super::*;

            static LOGGER: $crate::logger::WriteLogger<$serial> = $crate::logger::WriteLogger {
                writer: ::core::cell::RefCell::new(None),
                level: $crate::rt::log::Level::Trace,
            };

            pub fn logger_init(writer: $serial) {
                LOGGER.writer.replace(Some(writer));
                unsafe {
                    match $crate::rt::log::set_logger_racy(&LOGGER).map(|()| {
                        $crate::rt::log::set_max_level_racy($crate::rt::log::LevelFilter::Trace)
                    }) {
                        Ok(()) => (),
                        Err(_e) => {
                            panic!("Failed to set logger");
                        }
                    }
                }
            }

            #[cfg(not(test))]
            #[panic_handler]
            fn panic(panic_info: &::core::panic::PanicInfo) -> ! {
                if let Some(location) = panic_info.location() {
                    $crate::rt::log::error!("panic(): file '{}' at line {}",
                        location.file(),
                        location.line(),
                    );
                } else {
                    $crate::rt::log::error!("panic(): no location information");
                }
                $crate::rt::log::error!("{:?}", panic_info.message());
                loop {}
            }

            #[export_name = "ExceptionHandler"]
            fn exception_handler(trap_frame: &riscv_rt::TrapFrame) -> ! {
                $crate::rt::log::error!("exception_handler(): TrapFrame.ra={:x}", trap_frame.ra);
                loop {}
            }

            #[export_name = "DefaultHandler"]
            fn default_isr_handler() {
                $crate::rt::log::error!("default_isr_handler(): unhandled interrupt");
                loop {}
            }
        }
    };
}
