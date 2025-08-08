use crate::nor_flash::*;

#[derive(Debug)]
pub enum Error {
    TxTimeout,
    RxTimeout,
    InvalidReadSize,
}

impl NorFlashError for Error {
    fn kind(&self) -> NorFlashErrorKind {
        NorFlashErrorKind::Other
    }
}

pub trait SpiFlash {
    type Error;
    fn write_transaction(&mut self, cmd: &[u8]) -> Result<(), Error>;
    fn read_transaction(&mut self, prefix: &[u8], data: &mut [u8]) -> Result<(), Error>;
    fn uuid(&mut self) -> Result<[u8; 8], Error>;
    fn jedec(&mut self) -> Result<[u8; 3], Error>;
    fn busy(&mut self) -> Result<bool, Error>;
    fn sector_erase(&mut self, addr: u32) -> Result<(), Error>;
    fn page_program(&mut self, addr: u32, data: &[u8]) -> Result<(), Error>;
    fn write_enable(&mut self) -> Result<(), Error>;
    fn write_disable(&mut self) -> Result<(), Error>;
}

#[macro_export]
macro_rules! impl_spiflash {
    ($(
        $SPIFLASHX:ident: $PACSPIX:ty,
    )+) => {
        $(
            pub const SPIFLASH_FIFO_LEN: usize = 16;
            pub const SPIFLASH_CMD_UUID: u8 = 0x4b;
            pub const SPIFLASH_CMD_JEDEC: u8 = 0x9f;
            pub const SPIFLASH_CMD_STATUS1: u8 = 0x05;
            pub const SPIFLASH_CMD_WRITE_ENABLE: u8 = 0x06;
            pub const SPIFLASH_CMD_WRITE_DISABLE: u8 = 0x04;
            pub const SPIFLASH_CMD_SECTOR_ERASE: u8 = 0x20;
            pub const SPIFLASH_CMD_PAGE_PROGRAM: u8 = 0x02;

            #[derive(Debug)]
            pub struct $SPIFLASHX {
                registers: $PACSPIX,
                base: usize,
                size: usize,
            }

            impl $SPIFLASHX {
                pub fn new(registers: $PACSPIX, base: usize, size: usize) -> Self {
                    Self { registers, base, size }
                }

                pub fn free(self) -> $PACSPIX {
                    self.registers
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

                fn write_transaction(&mut self, cmd: &[u8]) -> Result<(), Self::Error> {

                    self.registers
                        .phy()
                        .write(|w| unsafe { w.length().bits(8).width().bits(1).mask().bits(1) });

                    if !spi_ready(&|| self.registers.status().read().tx_ready().bit()) {
                        return Err(Self::Error::TxTimeout);
                    }

                    self.registers.cs().write(|w| w.select().bit(true));

                    for byte in cmd {
                        self.registers
                            .data()
                            .write(|w| unsafe { w.tx().bits(*byte as u32) });
                    }

                    for n in 0..cmd.len() {
                        while !self.registers.status().read().rx_ready().bit() { }
                        let _ = self.registers.data().read().rx().bits() as u8;
                    }

                    self.registers.cs().write(|w| w.select().bit(false));

                    Ok(())
                }

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

                    for n in 0..(prefix.len() + data.len()) {
                        while !self.registers.status().read().rx_ready().bit() { }
                        let byte = self.registers.data().read().rx().bits() as u8;
                        if n >= prefix.len() {
                            data[n-prefix.len()] = byte;
                        }
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

                fn jedec(&mut self) -> Result<[u8; 3], Self::Error> {
                    let command: [u8; 1] = [SPIFLASH_CMD_JEDEC];
                    let mut response: [u8; 3] = [0, 0, 0];
                    self.read_transaction(&command, &mut response)?;
                    Ok(response)
                }

                fn busy(&mut self) -> Result<bool, Self::Error> {
                    let command: [u8; 1] = [SPIFLASH_CMD_STATUS1];
                    let mut response: [u8; 1] = [0u8; 1];
                    self.read_transaction(&command, &mut response)?;
                    Ok(response[0] & 0b0000_0001 != 0)
                }

                fn write_enable(&mut self) -> Result<(), Self::Error> {
                    let command: [u8; 1] = [SPIFLASH_CMD_WRITE_ENABLE];
                    self.write_transaction(&command)
                }

                fn write_disable(&mut self) -> Result<(), Self::Error> {
                    let command: [u8; 1] = [SPIFLASH_CMD_WRITE_DISABLE];
                    self.write_transaction(&command)
                }

                fn sector_erase(&mut self, addr: u32) -> Result<(), Self::Error> {
                    let command: [u8; 4] = [
                        SPIFLASH_CMD_SECTOR_ERASE,
                        ((addr >> 16) & 0xff) as u8,
                        ((addr >> 8) & 0xff) as u8,
                        (addr & 0xff) as u8,
                    ];
                    self.write_transaction(&command)
                }

                fn page_program(&mut self, addr: u32, data: &[u8]) -> Result<(), Self::Error> {

                    let command: [u8; 4] = [
                        SPIFLASH_CMD_PAGE_PROGRAM,
                        ((addr >> 16) & 0xff) as u8,
                        ((addr >> 8) & 0xff) as u8,
                        (addr & 0xff) as u8,
                    ];

                    self.registers
                        .phy()
                        .write(|w| unsafe { w.length().bits(8).width().bits(1).mask().bits(1) });

                    if !spi_ready(&|| self.registers.status().read().tx_ready().bit()) {
                        return Err(Self::Error::TxTimeout);
                    }

                    self.registers.cs().write(|w| w.select().bit(true));

                    for byte in command {
                        self.registers
                            .data()
                            .write(|w| unsafe { w.tx().bits(byte as u32) });
                    }

                    let mut bytes_in_fifo: usize = command.len();
                    for byte in data {
                        if self.registers.status().read().tx_ready().bit() {
                            self.registers
                                .data()
                                .write(|w| unsafe { w.tx().bits(*byte as u32) });
                            bytes_in_fifo = bytes_in_fifo + 1;
                        }
                        if bytes_in_fifo >= SPIFLASH_FIFO_LEN {
                            for n in 0..bytes_in_fifo {
                                while !self.registers.status().read().rx_ready().bit() { }
                                let _ = self.registers.data().read().rx().bits() as u8;
                            }
                            bytes_in_fifo = 0;
                        }
                    }

                    for n in 0..bytes_in_fifo {
                        while !self.registers.status().read().rx_ready().bit() { }
                        let _ = self.registers.data().read().rx().bits() as u8;
                    }

                    self.registers.cs().write(|w| w.select().bit(false));

                    Ok(())
                }
            }

            impl $crate::nor_flash::ErrorType for $SPIFLASHX {
                type Error = $crate::spiflash::Error;
            }

            impl $crate::nor_flash::ReadNorFlash for $SPIFLASHX {
                const READ_SIZE: usize = 1;
                fn read(&mut self, offset: u32, bytes: &mut [u8]) ->
                    Result<(), Self::Error> {
                    for n in 0..bytes.len() {
                        let addr = self.base + (offset as usize) + n;
                        bytes[n] = unsafe { core::ptr::read_volatile(addr as *mut u8) };
                    }
                    Ok(())
                }
                fn capacity(&self) -> usize {
                    self.size
                }
            }

            impl $crate::nor_flash::NorFlash for $SPIFLASHX {
                const WRITE_SIZE: usize = 1;
                const ERASE_SIZE: usize = 4096;

                fn erase(&mut self, from: u32, to: u32) -> Result<(), Self::Error> {
                    use $crate::spiflash::SpiFlash;
                    // TODO $crate::nor_flash::check_erase(self, from, to)?;
                    let mut addr = from;
                    self.write_enable()?;
                    while addr < to {
                        self.sector_erase(addr)?;
                        while self.busy()? { } // TODO timeout
                        addr += Self::ERASE_SIZE as u32;
                    }
                    self.write_disable()?;
                    Ok(())
                }
                fn write(&mut self, offset: u32, bytes: &[u8]) -> Result<(), Self::Error> {
                    use $crate::spiflash::SpiFlash;
                    const PAGE_SIZE: usize = 256;
                    let mut written = 0;
                    let mut current_offset = offset;
                    self.write_enable()?;
                    while written < bytes.len() {
                        let page_offset = (current_offset as usize) % PAGE_SIZE;
                        let bytes_to_write = core::cmp::min(
                                PAGE_SIZE - page_offset,
                                bytes.len() - written
                        );
                        self.page_program(current_offset, &bytes[written..written + bytes_to_write])?;
                        while self.busy()? { } // TODO timeout
                        written += bytes_to_write;
                        current_offset += bytes_to_write as u32;
                    }
                    self.write_disable()?;
                    Ok(())
                }
            }
        )+
    }
}
