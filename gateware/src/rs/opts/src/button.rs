use heapless::String;
use core::fmt::Write;
use serde::{Serialize, Deserialize};

use crate::traits::*;

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum ButtonMode {
    Toggle,
    OneShot,
}

#[derive(Clone)]
pub struct ButtonOption<T: ButtonOptionParams> {
    name: &'static str,
    pub value: bool,
    init: bool,
    key: u32,
    _phantom: core::marker::PhantomData<T>,
}

pub trait ButtonOptionParams {
    const MODE: ButtonMode;
}

impl<T: ButtonOptionParams> ButtonOption<T> {
    pub fn new(name: &'static str, init: bool, key: u32) -> Self {
        Self {
            name,
            value: init,
            init,
            key,
            _phantom: core::marker::PhantomData,
        }
    }

    /// For OneShot mode: returns and clears the latched value
    /// For Toggle mode: returns current value without clearing
    pub fn poll(&mut self) -> bool {
        let result = self.value;
        if T::MODE == ButtonMode::OneShot {
            self.value = false;
        }
        result
    }

    /// Simulates a button press - toggles for Toggle mode, latches for OneShot mode
    pub fn press(&mut self) {
        match T::MODE {
            ButtonMode::Toggle => {
                self.value = !self.value;
            }
            ButtonMode::OneShot => {
                self.value = true;
            }
        }
    }
}

impl<T: ButtonOptionParams> OptionTrait for ButtonOption<T> {
    fn name(&self) -> &'static str {
        self.name
    }

    fn value(&self) -> OptionString {
        let mut s: OptionString = String::new();
        match T::MODE {
            ButtonMode::Toggle => {
                write!(&mut s, "{}", if self.value { "<Y>" } else { "<N>" }).ok();
            }
            ButtonMode::OneShot => {
                write!(&mut s, "{}", if self.value { "<>" } else { "" }).ok();
            }
        }
        s
    }

    fn key(&self) -> u32 {
        self.key
    }

    fn tick_up(&mut self) {
        // Button options don't respond to encoder rotation
    }

    fn tick_down(&mut self) {
        // Button options don't respond to encoder rotation
    }

    fn percent(&self) -> f32 {
        if self.value { 1.0 } else { 0.0 }
    }

    fn n_unique_values(&self) -> usize {
        match T::MODE {
            ButtonMode::Toggle => 2,
            ButtonMode::OneShot => 1, // Always shows as "action" - not really multiple states
        }
    }

    fn button_press(&mut self) -> bool {
        self.press();
        true // Always handled
    }

    fn encode(&self, buf: &mut [u8]) -> Option<usize> {
        // For Toggle mode, only encode if different from default
        // For OneShot mode, don't persist state (always starts at 0)
        match T::MODE {
            ButtonMode::Toggle if self.value != self.init => {
                use postcard::to_slice;
                if let Ok(used) = to_slice(&self.value, buf) {
                    Some(used.len())
                } else {
                    None
                }
            }
            _ => None,
        }
    }

    fn decode(&mut self, buf: &[u8]) -> bool {
        use postcard::from_bytes;
        if let Ok(v) = from_bytes::<bool>(buf) {
            // Only restore Toggle mode values
            if T::MODE == ButtonMode::Toggle {
                self.value = v;
                self.init = v;
            }
            true
        } else {
            false
        }
    }
}

#[macro_export]
macro_rules! button_params {
    ($name:ident { mode: $mode:expr }) => {
        #[derive(Clone)]
        pub struct $name;

        impl ButtonOptionParams for $name {
            const MODE: ButtonMode = $mode;
        }
    };
}
