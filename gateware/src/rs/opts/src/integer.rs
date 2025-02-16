use heapless::String;
use core::fmt::Write;

use crate::traits::*;

#[derive(Clone)]
pub struct NumOption<T: NumOptionParams> {
    name: &'static str,
    pub value: T::Value,
}

pub trait NumOptionParams {
    type Value: Copy + Default;
    const STEP: Self::Value;
    const MIN: Self::Value;
    const MAX: Self::Value;
}

impl<T: NumOptionParams> NumOption<T> {
    pub fn new(name: &'static str, value: T::Value) -> Self {
        Self {
            name,
            value,
        }
    }
}

impl<T: NumOptionParams> OptionTrait for NumOption<T>
where
    T::Value: Copy
        + Default
        + core::ops::Add<Output = T::Value>
        + core::ops::Sub<Output = T::Value>
        + core::cmp::Ord
        + core::fmt::Display,
    f32: From<T::Value>,
{
    fn name(&self) -> &'static str {
        self.name
    }

    fn value(&self) -> OptionString {
        let mut s: OptionString = String::new();
        write!(&mut s, "{}", self.value).ok();
        s
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
        f32::from(value) / f32::from(range)
    }

    fn n_unique_values(&self) -> usize {
        // TODO
        0
    }
}

#[macro_export]
macro_rules! num_params {
    ($name:ident<$t:ty> { step: $step:expr, min: $min:expr, max: $max:expr }) => {
        #[derive(Clone)]
        pub struct $name;

        impl NumOptionParams for $name {
            type Value = $t;
            const STEP: Self::Value = $step;
            const MIN: Self::Value = $min;
            const MAX: Self::Value = $max;
        }
    };
}
