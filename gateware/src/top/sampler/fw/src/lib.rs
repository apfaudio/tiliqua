#![no_std]
#![no_main]

pub use tiliqua_pac as pac;
pub use tiliqua_hal as hal;

hal::impl_tiliqua_soc_pac!();

hal::impl_delay_line! {
    DelayLine0: pac::DELAYLN_PERIPH0,
    DelayLine1: pac::DELAYLN_PERIPH1,
    DelayLine2: pac::DELAYLN_PERIPH2,
}

hal::impl_grain_player! {
    GrainPlayer0: pac::GRAIN_PERIPH0,
    GrainPlayer1: pac::GRAIN_PERIPH1,
    GrainPlayer2: pac::GRAIN_PERIPH2,
}

pub mod channel;
pub mod handlers;
pub mod options;
