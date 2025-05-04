use tiliqua_hal::dma_framebuffer::DVIModeline;
use tiliqua_manifest::BitstreamManifest;

/// Information shared from Tiliqua bootloader to SoC bitstreams.
/// This is placed in PSRAM at a known address.
#[derive(Clone)]
pub struct BootInfo {
    pub manifest: BitstreamManifest,
    pub modeline: DVIModeline,
}

impl BootInfo {
    pub unsafe fn to_addr(&self, addr: usize) {
        let raw_ptr = addr as *mut BootInfo;
        *(raw_ptr.as_mut().unwrap()) = self.clone();
    }

    pub unsafe fn from_addr(addr: usize) -> BootInfo {
        (*(addr as *const BootInfo)).clone()
    }
}
