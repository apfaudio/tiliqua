#![no_std]
#![no_main]

pub use tiliqua_pac as pac;
pub use tiliqua_hal as hal;

hal::impl_tiliqua_soc_pac!();

tiliqua_lib::impl_handlers!(Serial0, Timer0);

pub mod channel;
pub mod delay_line;
pub mod flash;
pub mod grain_player;
pub mod options;

pub use delay_line::DelayLine0;
pub use grain_player::{GrainPlayer0, GrainPlayer1, GrainPlayer2};
