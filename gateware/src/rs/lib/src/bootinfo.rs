use tiliqua_hal::dma_framebuffer::DVIModeline;
use tiliqua_manifest::BitstreamManifest;
use serde_derive::{Serialize, Deserialize};

const BOOTINFO_MAX_SIZE: usize = 1024;

/// Information shared from Tiliqua bootloader to SoC bitstreams.
/// This is placed in PSRAM at a known address.
#[derive(Clone, Serialize, Deserialize)]
pub struct BootInfo {
    pub manifest: BitstreamManifest,
    pub modeline: DVIModeline,
}

impl BootInfo {
    /// Serialize BootInfo to memory at the given address in PSRAM.
    /// This is intended to be only used by the bootloader bitstream.
    pub unsafe fn to_addr(&self, addr: usize) -> Option<usize> {
        let buffer = core::slice::from_raw_parts_mut(addr as *mut u8, BOOTINFO_MAX_SIZE);
        postcard::to_slice(self, buffer).ok().map(|slice| slice.len())
    }

    /// Deserialize BootInfo from memory at the given address in PSRAM.
    /// This is intended to only be used by application bitstreams.
    pub unsafe fn from_addr(addr: usize) -> Option<BootInfo> {
        let buffer = core::slice::from_raw_parts(addr as *const u8, BOOTINFO_MAX_SIZE);
        postcard::from_bytes(buffer).ok()
    }
}
