/// TODO: just a placeholder for printing string options for now.
/// modification is not implemented.

use crate::traits::*;
use core::str::FromStr;

#[derive(Clone, Default)]
pub struct StringOption {
    pub name: &'static str,
    pub value: OptionString,
    key: u32,
}

impl StringOption {
    pub fn new(name: &'static str, value: &str, key: u32) -> Self {
        Self {
            name,
            value: OptionString::from_str(value).unwrap(),
            key
        }
    }
}

impl OptionTrait for StringOption {
    fn name(&self) -> &'static str {
        self.name
    }

    fn value(&self) -> OptionString {
        self.value.clone()
    }

    fn key(&self) -> u32 {
        self.key
    }

    fn tick_up(&mut self) {
        // do nothing (for now)
    }

    fn tick_down(&mut self) {
        // do nothing (for now)
    }

    fn percent(&self) -> f32 {
        0.5f32
    }

    fn n_unique_values(&self) -> usize {
        1usize
    }

    fn encode(&self, buf: &mut [u8]) -> usize {
        0
    }

    fn decode(&mut self, buf: &[u8]) -> bool {
        false
    }
}
