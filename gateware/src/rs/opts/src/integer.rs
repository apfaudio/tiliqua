use heapless::String;
use core::fmt::Write;
use serde::{Serialize, Deserialize};
use num_traits::AsPrimitive;

use crate::traits::*;

#[derive(Clone, Copy, Default)]
pub enum IntFormat {
    #[default]
    Raw,
    Scaled { divisor: u32, precision: usize },
}

#[derive(Clone)]
pub struct IntOption<T: IntOptionParams> {
    name: &'static str,
    pub value: T::Value,
    init: T::Value,
    option_key: OptionKey,
}

pub trait IntOptionParams {
    type Value: Copy + Default;
    const STEP: Self::Value;
    const MIN: Self::Value;
    const MAX: Self::Value;
    const FORMAT: IntFormat = IntFormat::Raw;
}

impl<T: IntOptionParams> IntOption<T> {
    pub fn new(name: &'static str, value: T::Value, key: u32) -> Self {
        Self {
            name,
            value,
            init: value,
            option_key: OptionKey::new(key),
        }
    }
}

impl<T: IntOptionParams> OptionTrait for IntOption<T>
where
    T::Value: Copy
        + Default
        + core::ops::Add<Output = T::Value>
        + core::ops::Sub<Output = T::Value>
        + core::cmp::Ord
        + core::fmt::Display
        + Serialize
        + for<'de> Deserialize<'de>
        + AsPrimitive<f32>,
{
    fn name(&self) -> &'static str {
        self.name
    }

    fn value(&self) -> OptionString {
        let mut s: OptionString = String::new();
        match T::FORMAT {
            IntFormat::Raw => {
                write!(&mut s, "{}", self.value).ok();
            }
            IntFormat::Scaled { divisor, precision } => {
                let scaled = self.value.as_() / divisor as f32;
                write!(&mut s, "{:.*}", precision, scaled).ok();
            }
        }
        s
    }

    fn key(&self) -> &OptionKey {
        &self.option_key
    }

    fn key_mut(&mut self) -> &mut OptionKey {
        &mut self.option_key
    }

    fn tick_up(&mut self) {
        let new_value = self.value + T::STEP;
        // Tolerate unsigned overflow.
        if new_value <= T::MAX && new_value > self.value {
            self.value = new_value;
        }
    }

    fn tick_down(&mut self) {
        let new_value = self.value - T::STEP;
        if new_value >= T::MIN && new_value < self.value {
            self.value = new_value;
        }
    }

    fn percent(&self) -> f32 {
        let range = T::MAX - T::MIN;
        let value = self.value - T::MIN;
        value.as_() / range.as_()
    }

    fn n_unique_values(&self) -> usize {
        // TODO
        0
    }

    fn encode(&self, buf: &mut [u8]) -> Option<usize> {
        if self.value != self.init {
            use postcard::to_slice;
            if let Ok(used) = to_slice(&self.value, buf) {
                Some(used.len())
            } else {
                None
            }
        } else {
            None
        }
    }

    fn decode(&mut self, buf: &[u8]) -> bool {
        use postcard::from_bytes;
        if let Ok(v) = from_bytes::<T::Value>(buf) {
            self.value = v;
            self.init = v;
            true
        } else {
            false
        }
    }
}

#[macro_export]
macro_rules! int_params {
    ($name:ident<$t:ty> { step: $step:expr, min: $min:expr, max: $max:expr }) => {
        #[derive(Clone)]
        pub struct $name;

        impl IntOptionParams for $name {
            type Value = $t;
            const STEP: Self::Value = $step;
            const MIN: Self::Value = $min;
            const MAX: Self::Value = $max;
        }
    };
    ($name:ident<$t:ty> { step: $step:expr, min: $min:expr, max: $max:expr, format: $format:expr }) => {
        #[derive(Clone)]
        pub struct $name;

        impl IntOptionParams for $name {
            type Value = $t;
            const STEP: Self::Value = $step;
            const MIN: Self::Value = $min;
            const MAX: Self::Value = $max;
            const FORMAT: IntFormat = $format;
        }
    };
}
