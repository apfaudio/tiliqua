#![cfg_attr(not(test), no_std)]

use strum::IntoEnumIterator;

pub use opts_derive::{OptionPage, Options};

mod traits;
mod integer;
mod enumeration;
mod float;
mod string;
pub mod persistence;

pub use crate::traits::*;
pub use crate::integer::*;
pub use crate::enumeration::*;
pub use crate::float::*;
pub use crate::string::*;

#[derive(Clone, Default)]
pub struct ScreenTracker<ScreenT: Copy + IntoEnumIterator + Default> {
    pub selected: Option<usize>,
    pub modify: bool,
    pub page: EnumOption<ScreenT>,
}
