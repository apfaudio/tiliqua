use log::info;
use crate::delay_line::DelayLine;
use tiliqua_hal::nor_flash::{NorFlash, ReadNorFlash};

// XXX: hardcoded delayline offset in spiflash that is far
// away from any other bitstreams. at the moment, we don't have
// any other bitstreams using persistent storage, but this should
// become a bit less dumb in the future.
//
// Likely, the 'proper' solution will be to store sampler delaylines
// on mass storage (thumbdrive) instead of on SPI flash, which is slow.
//
const BASE: u32 = 0x900000;
const MAGIC: u32 = 0x534D504C;   // "SMPL" <= sampler delayline identifier
const DATA_OFFSET: u32 = 0x1000; // audio data starts DATA_OFFSET after BASE
const CHUNK: usize = 0x4000;     // erase/write to spiflash in 16 KiB chunks

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
        mut progress: impl FnMut(usize, usize),
    ) -> bool {
        let mut magic_buf = [0u8; 4];
        self.flash.read(BASE, &mut magic_buf).unwrap();
        let magic = u32::from_le_bytes(magic_buf);
        if magic != MAGIC {
            info!("No saved delay line found in flash (magic=0x{:08x}).", magic);
            return false;
        }

        let flash_offset = BASE + DATA_OFFSET;
        let size_bytes = delayln.size_samples() * 2;
        let data = unsafe { core::slice::from_raw_parts_mut(delayln.data_ptr() as *mut u8, size_bytes) };
        info!("Loading delay line from flash 0x{:x} ({} bytes)...", flash_offset, size_bytes);
        let mut loaded = 0usize;
        while loaded < size_bytes {
            let chunk = (size_bytes - loaded).min(CHUNK);
            self.flash.read(flash_offset + loaded as u32, &mut data[loaded..loaded + chunk]).unwrap();
            loaded += chunk;
            progress(loaded / 1024, size_bytes / 1024);
        }
        info!("Delay line loaded.");
        true
    }

    /// Erase flash region, write magic + unrotated delayline data (undo circular buffer).
    /// ASSUMPTION: on startup the delayline write position is reset to 0
    pub fn save(
        &mut self,
        data: &[u8],
        wr_bytes: usize,
        mut progress: impl FnMut(&str, usize, usize),
    ) {
        let size_bytes = data.len();
        info!("Saving delay line ({} bytes, wrptr={})...", size_bytes, wr_bytes);

        // Erase entire region first
        // it's annoying to do this inline with each write as we're simultaneously
        // unrotating the circular buffer. easier to just erase the whole region first.
        let flash_offset = BASE + DATA_OFFSET;
        let erase_end = flash_offset + size_bytes as u32;
        let erase_total = (erase_end - BASE) as usize;
        let mut erased = 0usize;
        while erased < erase_total {
            let chunk = (erase_total - erased).min(CHUNK);
            let addr = BASE + erased as u32;
            self.flash.erase(addr, addr + chunk as u32).unwrap();
            erased += chunk;
            progress("Erasing", erased / 1024, erase_total / 1024);
        }

        // Write the magic and then unrotated data (on load, wrpointer=0, data must
        // be correctly ordered)
        self.flash.write(BASE, &MAGIC.to_le_bytes()).unwrap();
        let parts: [&[u8]; 2] = [&data[wr_bytes..], &data[..wr_bytes]];
        let mut flash_written = 0usize;
        for part in parts {
            let mut part_written = 0usize;
            while part_written < part.len() {
                let chunk = (part.len() - part_written).min(CHUNK);
                let addr = flash_offset + flash_written as u32;
                self.flash.write(addr, &part[part_written..part_written + chunk]).unwrap();
                part_written += chunk;
                flash_written += chunk;
                progress("Saving", flash_written / 1024, size_bytes / 1024);
            }
        }
        info!("Delay line saved.");
    }

    pub fn wipe_magic(&mut self) {
        self.flash.erase(BASE, BASE + DATA_OFFSET).unwrap();
    }
}
