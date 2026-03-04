#![no_std]
#![no_main]

pub use tiliqua_pac as pac;
pub use tiliqua_hal as hal;

hal::impl_tiliqua_soc_pac!();

#[cfg(expander_ex0)]
hal::impl_i2c! {
    I2cEx0: pac::I2C2,
}

#[cfg(expander_ex0)]
hal::impl_eurorack_pmod! {
    EurorackPmodEx0: pac::EX0_PMOD_PERIPH,
}

#[cfg(expander_ex1)]
hal::impl_i2c! {
    I2cEx1: pac::I2C3,
}

#[cfg(expander_ex1)]
hal::impl_eurorack_pmod! {
    EurorackPmodEx1: pac::EX1_PMOD_PERIPH,
}

hal::impl_scope! {
    Scope0: pac::SCOPE_PERIPH,
}

hal::impl_vector! {
    Vector0: pac::VECTOR_PERIPH,
}

pub mod handlers;
pub mod options;
