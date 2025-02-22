use heapless::{String, Vec};
use serde::{Deserialize};
use log::info;
use opts::OptionString;

#[derive(Deserialize, Clone)]
pub struct MemoryRegion {
    pub filename: String<32>,
    pub spiflash_src: u32,
    pub psram_dst: Option<u32>,
    pub size: u32,
    pub crc: u32,
}

#[derive(Deserialize, Clone)]
pub struct ExternalPLLConfig {
    pub clk0_hz: u32,
    pub clk1_hz: u32,
    pub spread_spectrum: Option<f32>,
}

#[derive(Deserialize, Clone)]
pub struct BitstreamManifest {
    pub name: OptionString,
    pub version: u32,
    pub sha: String<8>,
    pub brief: String<128>,
    pub video: String<64>,
    pub external_pll_config: Option<ExternalPLLConfig>,
    pub regions: Vec<MemoryRegion, 3>,
}

impl BitstreamManifest {

    pub fn print(&self) {
        info!("BitstreamManifest {{");
        info!("\tname:    '{}'",  self.name);
        info!("\tversion: {}", self.version);
        info!("\tsha:     '{}'",   self.sha);
        info!("\tbrief:   '{}'", self.brief);
        info!("\tvideo:   '{}'", self.video);
        if let Some(clocks) = &self.external_pll_config {
            info!("\texternal_pll_config = {{");
            info!("\t\tclk0_hz: {}", clocks.clk0_hz);
            info!("\t\tclk1_hz: {}", clocks.clk1_hz);
            info!("\t\tspread_spectrum: {:?}", clocks.spread_spectrum);
            info!("\t}}");
        }
        for (i, region) in self.regions.iter().enumerate() {
            info!("\tmemory_region[{}] = {{", i);
            info!("\t\tfilename:     '{}'", region.filename);
            info!("\t\tspiflash_src: {:#x}", region.spiflash_src);
            if let Some(psram_dst) = region.psram_dst {
                info!("\t\tpsram_dst:    {:#x} (copyto)", psram_dst);
            }
            info!("\t\tsize:         {:#x}", region.size);
            info!("\t\tcrc:          {:#x}", region.crc);
            info!("\t}}");
        }
        info!("}}");
    }

    pub fn from_slice(manifest_slice: &[u8]) -> Option<BitstreamManifest> {
        let manifest_de = serde_json_core::from_slice::<BitstreamManifest>(manifest_slice);
        match manifest_de {
            Ok((contents, _rest)) => {
                info!("BitstreamManifest: parse OK");
                contents.print();
                Some(contents)
            }
            Err(err) => {
                info!("BitstreamManifest: parse failed with {:?}", err);
                info!("BitstreamManifest: bad or nonexisting manifest");
                None
            }
        }
    }

    pub fn from_addr(addr: usize, size: usize) -> Option<BitstreamManifest> {
        let manifest_slice = unsafe {
            core::slice::from_raw_parts(
                addr as *mut u8,
                size,
            )
        };

        // Erasing flash should always set bytes to 0xff. Count back from the
        // end of the manifest region to find where there is data. Otherwise,
        // Serde will fail out with a TrailingCharacters error.
        let mut last_byte = size;
        for i in (0..size).rev() {
            if manifest_slice[i] != 0xff {
                last_byte = i+1;
                break;
            }
        }

        if last_byte == size {
            info!("Manifest region is all ones, ignoring.");
            return None
        }

        let manifest_slice = &manifest_slice[0..last_byte];
        info!("Manifest length: {}", last_byte);

        Self::from_slice(manifest_slice)
    }
}
