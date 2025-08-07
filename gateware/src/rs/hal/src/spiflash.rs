use core::fmt;

#[derive(Debug)]
pub enum Error {
    TxTimeout,
    RxTimeout,
    InvalidRead,
}

pub trait SpiFlash {
    type Error;
    fn uuid(&mut self) -> Result<[u8; 8], Error>;
}

#[macro_export]
macro_rules! impl_spiflash {
    ($(
        $SPIFLASHX:ident: $PACSPIX:ty,
    )+) => {
        $(
            pub const SPIFLASH_CMD_UUID: u8 = 0x4b;

            #[derive(Debug)]
            pub struct $SPIFLASHX {
                registers: $PACSPIX,
            }

            impl $SPIFLASHX {
                pub fn new(registers: $PACSPIX) -> Self {
                    Self { registers }
                }

                pub fn free(self) -> $PACSPIX {
                    self.registers
                }

                pub unsafe fn summon() -> Self {
                    Self {
                        registers: <$PACSPIX>::steal(),
                    }
                }
            }

            impl From<$PACSPIX> for $SPIFLASHX {
                fn from(registers: $PACSPIX) -> $SPIFLASHX {
                    $SPIFLASHX::new(registers)
                }
            }

            fn spi_ready(f: &dyn Fn() -> bool) -> bool {
                let mut timeout = 0;
                while !f() {
                    timeout += 1;
                    if timeout > 1000 {
                        return false;
                    }
                }
                return true;
            }

            impl hal::spiflash::SpiFlash for $SPIFLASHX {

                type Error = $crate::spiflash::Error;

                fn uuid(&mut self) -> Result<[u8; 8], Self::Error> {
                    self.registers
                        .phy()
                        .write(|w| unsafe { w.length().bits(8).width().bits(1).mask().bits(1) });

                    if !spi_ready(&|| self.registers.status().read().tx_ready().bit()) {
                        return Err(Self::Error::TxTimeout);
                    }

                    self.registers.cs().write(|w| w.select().bit(true));

                    let command: [u8; 5] = [SPIFLASH_CMD_UUID, 0, 0, 0, 0];
                    for byte in command {
                        self.registers
                            .data()
                            .write(|w| unsafe { w.tx().bits(u32::from(byte)) });
                    }

                    self.registers
                        .phy()
                        .write(|w| unsafe { w.length().bits(8).width().bits(1).mask().bits(0) });

                    let response: [u8; 8] = [0, 0, 0, 0, 0, 0, 0, 0];
                    for byte in response {
                        self.registers
                            .data()
                            .write(|w| unsafe { w.tx().bits(u32::from(byte)) });
                    }

                    if !spi_ready(&|| self.registers.status().read().rx_ready().bit()) {
                        return Err(Self::Error::RxTimeout);
                    }

                    let mut response = [0_u8; 32];
                    let mut n = 0;
                    while self.registers.status().read().rx_ready().bit() {
                        response[n] = self.registers.data().read().rx().bits() as u8;
                        n = n + 1;
                        if n >= response.len() {
                            return Err(Self::Error::InvalidRead);
                        }
                    }

                    self.registers.cs().write(|w| w.select().bit(false));

                    if n != 13 {
                        return Err(Self::Error::InvalidRead);
                    }

                    let mut result: [u8; 8] = [0u8; 8];
                    result.copy_from_slice(&response[5..13]);
                    Ok(result)
                }
            }
        )+
    }
}
