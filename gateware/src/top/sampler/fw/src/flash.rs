use log::{info, error};
use crate::delay_line::DelayLine;
use crate::pac::constants::DELAYLN_SIZE_SAMPLES;
use crate::SPIFlash0;
use tiliqua_hal::nor_flash::{NorFlash, ReadNorFlash};

// XXX: hardcoded delayline offset in spiflash that is far
// away from any other bitstreams. at the moment, we don't have
// any other bitstreams using persistent storage, but this should
// become a bit less dumb in the future.
//
// Likely, the 'proper' solution will be to store sampler delaylines
// on mass storage (thumbdrive) instead of on SPI flash, which is slow.
//
pub const BASE: u32 = 0x900000;
const MAGIC: u32 = 0x534D504C;   // "SMPL" <= sampler delayline identifier
const DATA_OFFSET: u32 = 0x1000; // audio data starts DATA_OFFSET after BASE
const CHUNK: usize = 0x4000;     // erase/write to spiflash in 16 KiB chunks

const ERASE_SIZE: u32 = SPIFlash0::ERASE_SIZE as u32;
pub const PARTITION_SIZE: u32 = DATA_OFFSET + (DELAYLN_SIZE_SAMPLES * 2) as u32;
const _: () = assert!(BASE.is_multiple_of(ERASE_SIZE) && PARTITION_SIZE.is_multiple_of(ERASE_SIZE),
                      "delay line flash partition must be erase-aligned");

pub struct DelaylineFlash<F> {
    flash: F,
}

impl<F: NorFlash + ReadNorFlash> DelaylineFlash<F> {
    pub fn new(flash: F) -> Self {
        Self { flash }
    }

    /// Check for magic word, if present, load delayline contents from flash.
    /// Returns true if data was loaded.
    pub fn load(
        &mut self,
        delayln: &impl DelayLine,
        progress: impl FnMut(usize, usize),
    ) -> bool {
        self.try_load(delayln, progress).unwrap_or_else(|e| {
            error!("Failed to load delay line: {e:?}");
            false
        })
    }

    fn try_load(
        &mut self,
        delayln: &impl DelayLine,
        mut progress: impl FnMut(usize, usize),
    ) -> Result<bool, F::Error> {
        let mut magic_buf = [0u8; 4];
        self.flash.read(0, &mut magic_buf)?;
        let magic = u32::from_le_bytes(magic_buf);
        if magic != MAGIC {
            info!("No saved delay line found in flash (magic=0x{magic:08x}).");
            return Ok(false);
        }

        let flash_offset = DATA_OFFSET;
        let size_bytes = delayln.size_samples() * 2;
        let data = unsafe { core::slice::from_raw_parts_mut(delayln.data_ptr() as *mut u8, size_bytes) };
        info!("Loading delay line from flash 0x{:x} ({size_bytes} bytes)...", BASE + flash_offset);
        let mut loaded = 0usize;
        while loaded < size_bytes {
            let chunk = (size_bytes - loaded).min(CHUNK);
            self.flash.read(flash_offset + loaded as u32, &mut data[loaded..loaded + chunk])?;
            loaded += chunk;
            progress(loaded / 1024, size_bytes / 1024);
        }
        info!("Delay line loaded.");
        Ok(true)
    }

    /// Erase flash region, write magic + unrotated delayline data (undo circular buffer).
    /// ASSUMPTION: on startup the delayline write position is reset to 0
    pub fn save(
        &mut self,
        data: &[u8],
        wr_bytes: usize,
        progress: impl FnMut(&str, usize, usize),
    ) {
        if let Err(e) = self.try_save(data, wr_bytes, progress) {
            error!("Failed to save delay line: {e:?}");
        }
    }

    fn try_save(
        &mut self,
        data: &[u8],
        wr_bytes: usize,
        mut progress: impl FnMut(&str, usize, usize),
    ) -> Result<(), F::Error> {
        let size_bytes = data.len();
        info!("Saving delay line ({size_bytes} bytes, wrptr={wr_bytes})...");

        // Erase entire region first
        // it's annoying to do this inline with each write as we're simultaneously
        // unrotating the circular buffer. easier to just erase the whole region first.
        let flash_offset = DATA_OFFSET;
        let erase_end = flash_offset + size_bytes as u32;
        let erase_total = erase_end as usize;
        let mut erased = 0usize;
        while erased < erase_total {
            let chunk = (erase_total - erased).min(CHUNK);
            let addr = erased as u32;
            self.flash.erase(addr, addr + chunk as u32)?;
            erased += chunk;
            progress("Erasing", erased / 1024, erase_total / 1024);
        }

        // Write unrotated data and then the magic (on load, wrpointer=0, data must
        // be correctly ordered)
        let parts: [&[u8]; 2] = [&data[wr_bytes..], &data[..wr_bytes]];
        let mut flash_written = 0usize;
        for part in parts {
            let mut part_written = 0usize;
            while part_written < part.len() {
                let chunk = (part.len() - part_written).min(CHUNK);
                let addr = flash_offset + flash_written as u32;
                self.flash.write(addr, &part[part_written..part_written + chunk])?;
                part_written += chunk;
                flash_written += chunk;
                progress("Saving", flash_written / 1024, size_bytes / 1024);
            }
        }
        self.flash.write(0, &MAGIC.to_le_bytes())?;
        info!("Delay line saved.");
        Ok(())
    }

    pub fn wipe_magic(&mut self) {
        if let Err(e) = self.flash.erase(0, DATA_OFFSET) {
            error!("Failed to wipe delay line magic: {e:?}");
        }
    }
}
