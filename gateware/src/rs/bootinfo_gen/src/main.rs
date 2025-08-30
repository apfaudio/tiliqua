use clap::Parser;
use std::fs;
use std::path::PathBuf;
use tiliqua_lib::bootinfo::BootInfo;
use tiliqua_manifest::BitstreamManifest;
use tiliqua_hal::dma_framebuffer::DVIModeline;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Input manifest JSON file
    #[arg(short, long)]
    manifest: PathBuf,
    
    /// Horizontal active pixels
    #[arg(long)]
    h_active: u16,
    
    /// Vertical active pixels  
    #[arg(long)]
    v_active: u16,
    
    /// Fixed pixel clock in Hz
    #[arg(long)]
    fixed_pclk_hz: u32,
    
    /// Output bootinfo binary file
    #[arg(short, long)]
    output: PathBuf,
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();
    
    // Read and parse manifest JSON using serde_json (std mode)
    let manifest_str = fs::read_to_string(&args.manifest)?;
    println!("Manifest file content: {}", manifest_str);
    
    let manifest: BitstreamManifest = serde_json::from_str(&manifest_str)?;
    println!("Manifest parsed successfully");
    
    // Create modeline using maybe_override_fixed approach
    let modeline = DVIModeline::default().maybe_override_fixed(
        Some((args.h_active, args.v_active)), 
        args.fixed_pclk_hz
    );
    
    // Create BootInfo structure
    let bootinfo = BootInfo {
        manifest,
        modeline,
    };
    
    // Serialize to binary using postcard (same as bootloader)
    let mut buffer = [0u8; 1024]; // BOOTINFO_MAX_SIZE
    let crc_checker = crc::Crc::<u32>::new(&crc::CRC_32_BZIP2);
    let digest = crc_checker.digest();
    let serialized = postcard::to_slice_crc32(&bootinfo, &mut buffer, digest)?;
    let serialized_len = serialized.len();
    
    // Write to output file
    fs::write(&args.output, serialized)?;
    
    println!("Generated bootinfo: {} bytes -> {:?}", serialized_len, args.output);
    
    Ok(())
}