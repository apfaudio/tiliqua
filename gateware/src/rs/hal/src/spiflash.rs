#[derive(Debug)]
pub enum Error {
    TxTimeout,
    RxTimeout,
    InvalidReadSize,
}

pub trait SpiFlash {
    type Error;
    fn read_transaction(&mut self, prefix: &[u8], data: &mut [u8]) -> Result<(), Self::Error>;
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

                fn read_transaction(&mut self, prefix: &[u8], data: &mut [u8]) -> Result<(), Self::Error> {

                    self.registers
                        .phy()
                        .write(|w| unsafe { w.length().bits(8).width().bits(1).mask().bits(1) });

                    if !spi_ready(&|| self.registers.status().read().tx_ready().bit()) {
                        return Err(Self::Error::TxTimeout);
                    }

                    self.registers.cs().write(|w| w.select().bit(true));

                    for byte in prefix {
                        self.registers
                            .data()
                            .write(|w| unsafe { w.tx().bits(*byte as u32) });
                    }

                    self.registers
                        .phy()
                        .write(|w| unsafe { w.length().bits(8).width().bits(1).mask().bits(0) });

                    for _ in 0..data.len() {
                        self.registers
                            .data()
                            .write(|w| unsafe { w.tx().bits(0x0) });
                    }

                    if !spi_ready(&|| self.registers.status().read().rx_ready().bit()) {
                        return Err(Self::Error::RxTimeout);
                    }

                    let mut n = 0;
                    while self.registers.status().read().rx_ready().bit() {
                        if n > prefix.len() {
                            data[n] = self.registers.data().read().rx().bits() as u8;
                            if n > prefix.len() + data.len() {
                                return Err(Self::Error::InvalidReadSize);
                            }
                        }
                        n = n + 1;
                    }

                    self.registers.cs().write(|w| w.select().bit(false));

                    Ok(())
                }

                fn uuid(&mut self) -> Result<[u8; 8], Self::Error> {
                    let command: [u8; 5] = [SPIFLASH_CMD_UUID, 0, 0, 0, 0];
                    let mut response: [u8; 8] = [0, 0, 0, 0, 0, 0, 0, 0];
                    self.read_transaction(&command, &mut response)?;
                    Ok(response)
                }
            }
        )+
    }
}
