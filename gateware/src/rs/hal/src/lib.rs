#![cfg_attr(not(test), no_std)]
#![allow(clippy::inline_always)]
#![allow(clippy::must_use_candidate)]

#[cfg(test)]
#[macro_use]
extern crate std;

// modules
pub mod dma_framebuffer;
pub mod encoder;
pub mod i2c;
pub mod pca9635;
pub mod pmod;
pub mod polysynth;
pub mod serial;
pub mod si5351;
pub mod timer;
pub mod video;
pub mod cy8cmbr3xxx;

pub use embedded_hal as hal;
pub use embedded_hal_nb as hal_nb;

#[macro_use]
extern crate bitflags;

pub use nb;

// Peripherals common to all ordinary tiliqua_soc instances.
#[macro_export]
macro_rules! impl_tiliqua_soc_pac {
    () => {
        tiliqua_hal::impl_serial! {
            Serial0: tiliqua_pac::UART0,
        }

        tiliqua_hal::impl_timer! {
            Timer0: tiliqua_pac::TIMER0,
        }

        tiliqua_hal::impl_i2c! {
            I2c0: tiliqua_pac::I2C0,
        }

        tiliqua_hal::impl_i2c! {
            I2c1: tiliqua_pac::I2C1,
        }

        tiliqua_hal::impl_encoder! {
            Encoder0: tiliqua_pac::ENCODER0,
        }

        tiliqua_hal::impl_eurorack_pmod! {
            EurorackPmod0: tiliqua_pac::PMOD0_PERIPH,
        }

        tiliqua_hal::impl_video! {
            Video0: tiliqua_pac::VIDEO_PERIPH,
        }
    };
}

#[cfg(test)]
mod tests {
    use super::*;
    use embedded_hal::i2c::{I2c, ErrorType, Operation};

    // Mock I2C implementation for testing
    pub struct MockI2c;

    impl ErrorType for MockI2c {
        type Error = std::convert::Infallible;
    }

    impl I2c for MockI2c {
        fn write(&mut self, addr: u8, bytes: &[u8]) -> Result<(), Self::Error> {
            log::info!("I2c::write(addr=0x{:02X}): {:02X?}", addr, bytes);
            Ok(())
        }

        fn write_read(
            &mut self,
            address: u8,
            bytes: &[u8],
            buffer: &mut [u8],
        ) -> Result<(), Self::Error> {
            log::info!("I2c::write_read(addr=0x{:02X}):", address);
            log::info!("  Write: {:02X?}", bytes);
            log::info!("  Read buffer size: {}", buffer.len());
            Ok(())
        }

        fn transaction(
            &mut self,
            address: u8,
            operations: &mut [Operation<'_>],
        ) -> Result<(), Self::Error> {
            log::info!("I2c::transaction(addr=0x{:02X}):", address);
            for (i, op) in operations.iter().enumerate() {
                match op {
                    Operation::Read(buffer) => {
                        log::info!("  Op {}: Read {} bytes", i, buffer.len());
                    }
                    Operation::Write(bytes) => {
                        log::info!("  Op {}: Write {:02X?}", i, bytes);
                    }
                }
            }
            Ok(())
        }
    }

    use std::sync::Once;

    static INIT: Once = Once::new();

    pub fn setup_logger() {
      INIT.call_once(env_logger::init);
    }
}
