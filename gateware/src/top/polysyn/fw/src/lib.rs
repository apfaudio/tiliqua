#![no_std]
#![no_main]

pub use tiliqua_pac as pac;
pub use tiliqua_hal as hal;

hal::impl_tiliqua_soc_pac!();

hal::impl_vector! {
    Vector0: pac::VECTOR_PERIPH,
}

tiliqua_lib::impl_handlers!(Serial0, Timer0);

pub mod options;
pub mod polysynth;
pub mod wavetable;

pub use polysynth::Polysynth0;
