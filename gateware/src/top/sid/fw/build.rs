use opts::persistence::{OptionsPersistence, FlashOptionsPersistence};
use tiliqua_hal::dummy::DummyFlash;

// Include the options definitions needed for validation
// This will bring in all the necessary types
include!("src/options.rs");

fn main() {
    println!("cargo:rerun-if-changed=src/options.rs");
    let opts = Opts::default();
    let dummy_flash = DummyFlash::new(1024);
    let flash_range = 0..1024; // Dummy range
    let persistence = FlashOptionsPersistence::new(dummy_flash, flash_range);
    println!("cargo:warning=Generated option keys:");
    for opt in opts.all() {
        println!("cargo:warning=  {} = 0x{:08x}", opt.name(), opt.key());
    }
    match persistence.validate_options(&opts) {
        Ok(()) => {
            println!("cargo:warning=Options validation passed: all keys are unique");
        }
        Err(e) => {
            panic!("Options validation failed: {:?}", e);
        }
    }
}
