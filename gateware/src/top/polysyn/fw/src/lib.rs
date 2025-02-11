#![no_std]
#![no_main]

pub use tiliqua_pac as pac;
pub use tiliqua_hal as hal;

use tiliqua_lib::generated_constants::N_VOICES;

hal::impl_tiliqua_soc_pac!();

tiliqua_hal::impl_polysynth! {
    Polysynth0: pac::SYNTH_PERIPH,
    N_VOICES
}

pub mod handlers;
pub mod opts;
