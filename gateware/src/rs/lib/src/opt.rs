use heapless::String;
use heapless::Vec;

use strum::IntoEnumIterator;

use core::fmt::Write;
use core::str::FromStr;

pub const MAX_OPTS_PER_TAB: usize = 16;
pub const MAX_OPT_NAME:     usize = 32;

pub type OptionString = String<MAX_OPT_NAME>;
pub type OptionVec<'a> = Vec<&'a dyn OptionTrait, MAX_OPTS_PER_TAB>;
pub type OptionVecMut<'a> = Vec<&'a mut dyn OptionTrait, MAX_OPTS_PER_TAB>;

pub trait OptionTrait {
    fn name(&self) -> &'static str;
    fn value(&self) -> OptionString;
    fn tick_up(&mut self);
    fn tick_down(&mut self);
    fn percent(&self) -> f32;
    fn n_unique_values(&self) -> usize;
}

pub trait OptionView {
    fn selected(&self) -> Option<usize>;
    fn set_selected(&mut self, s: Option<usize>);
    fn options(&self) -> OptionVec;
    fn options_mut(&mut self) -> OptionVecMut;
}

pub trait OptionPage {
    fn modify(&self) -> bool;
    fn screen(&self) -> &dyn OptionTrait;
    fn view(&self) -> &dyn OptionView;

    fn modify_mut(&mut self, modify: bool);
    fn view_mut(&mut self) -> &mut dyn OptionView;
    fn screen_mut(&mut self) -> &mut dyn OptionTrait;
}

pub trait OptionPageEncoderInterface {
    fn toggle_modify(&mut self);
    fn tick_up(&mut self);
    fn tick_down(&mut self);
    fn consume_ticks(&mut self, ticks: i8);
}

#[derive(Clone)]
pub struct NumOption<T: NumOptionConfig> {
    name: &'static str,
    pub value: T::Value,
}

pub trait NumOptionConfig {
    type Value: Copy + Default;
    const STEP: Self::Value;
    const MIN: Self::Value;
    const MAX: Self::Value;
}

impl<T: NumOptionConfig> NumOption<T> {
    pub fn new(name: &'static str, value: T::Value) -> Self {
        Self {
            name,
            value,
        }
    }
}

#[derive(Clone)]
pub struct EnumOption<T: Copy + IntoEnumIterator> {
    pub name: &'static str,
    pub value: T,
}

impl<T: Copy + IntoEnumIterator> EnumOption<T> {
    pub fn new(name: &'static str, value: T) -> Self {
        Self {
            name,
            value,
        }
    }
}

#[macro_export]
macro_rules! impl_option_view {
    ($struct_name:ident, $($field:ident),*) => {
        impl OptionView for $struct_name {
            fn selected(&self) -> Option<usize> {
                self.selected
            }

            fn set_selected(&mut self, s: Option<usize>) {
                self.selected = s;
            }

            fn options(&self) -> OptionVec {
                OptionVec::from_slice(&[$(&self.$field),*]).unwrap()
            }

            fn options_mut(&mut self) -> OptionVecMut {
                let mut r = OptionVecMut::new();
                $(r.push(&mut self.$field).ok();)*
                r
            }
        }
    };
}

#[macro_export]
macro_rules! impl_option_page {
    ($struct_name:ident, $(($screen:path, $field:ident)),*) => {
        impl OptionPage for $struct_name {
            fn modify(&self) -> bool {
                self.modify
            }

            fn modify_mut(&mut self, modify: bool) {
                self.modify = modify
            }

            fn screen(&self) -> &dyn OptionTrait {
                &self.screen
            }

            fn screen_mut(&mut self) -> &mut dyn OptionTrait {
                &mut self.screen
            }

            #[allow(dead_code)]
            fn view(&self) -> &dyn OptionView {
                match self.screen.value {
                    $($screen => &self.$field,)*
                }
            }

            #[allow(dead_code)]
            fn view_mut(&mut self) -> &mut dyn OptionView {
                match self.screen.value {
                    $($screen => &mut self.$field,)*
                }
            }
        }
    };
}

impl<T> OptionPageEncoderInterface for T
where
    T: OptionPage,
{
    fn toggle_modify(&mut self) {
        self.modify_mut(!self.modify());
    }

    fn tick_up(&mut self) {
        if let Some(n_selected) = self.view().selected() {
            if self.modify() {
                self.view_mut().options_mut()[n_selected].tick_up();
            } else if n_selected < self.view().options().len()-1 {
                self.view_mut().set_selected(Some(n_selected + 1));
            }
        } else if self.modify() {
            self.screen_mut().tick_up();
        } else if !self.view().options().is_empty() {
            self.view_mut().set_selected(Some(0));
        }
    }

    fn tick_down(&mut self) {
        if let Some(n_selected) = self.view().selected() {
            if self.modify() {
                self.view_mut().options_mut()[n_selected].tick_down();
            } else if n_selected != 0 {
                self.view_mut().set_selected(Some(n_selected - 1));
            } else {
                if self.screen().n_unique_values() > 1 {
                    self.view_mut().set_selected(None);
                }
            }
        } else if self.modify() {
            self.screen_mut().tick_down();
        }
    }

    fn consume_ticks(&mut self, ticks: i8) {
        if ticks >= 1 {
            for _ in 0..ticks {
                self.tick_up();
            }
        }
        if ticks <= -1 {
            for _ in ticks..0 {
                self.tick_down();
            }
        }
    }
}

impl<T: NumOptionConfig> OptionTrait for NumOption<T>
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
        self.value = (self.value + T::STEP).clamp(T::MIN, T::MAX);
    }

    fn tick_down(&mut self) {
        self.value = (self.value - T::STEP).clamp(T::MIN, T::MAX);
    }

    fn percent(&self) -> f32 {
        let range = T::MAX - T::MIN;
        let value = self.value - T::MIN;
        f32::from(value) / f32::from(range)
    }

    fn n_unique_values(&self) -> usize {
        // Implementation here
        0
    }
}

#[macro_export]
macro_rules! num_option_config {
    ($name:ident<$t:ty> { step: $step:expr, min: $min:expr, max: $max:expr }) => {
        #[derive(Clone)]
        pub struct $name;

        impl NumOptionConfig for $name {
            type Value = $t;
            const STEP: Self::Value = $step;
            const MIN: Self::Value = $min;
            const MAX: Self::Value = $max;
        }
    };
    ($name:ident: $t:ty => $step:expr, $min:expr, $max:expr) => {
        num_option_config!($name<$t> {
            step: $step,
            min: $min,
            max: $max
        });
    };
}


impl<T> OptionTrait for EnumOption<T>
where
    T: Copy
        + IntoEnumIterator
        + PartialEq
        + Into<&'static str>
    {

    fn name(&self) -> &'static str {
        self.name
    }

    fn value(&self) -> OptionString {
        String::from_str(self.value.into()).unwrap()
    }

    fn tick_up(&mut self) {
        let mut it = T::iter();
        for v in it.by_ref() {
            if v == self.value {
                break;
            }
        }
        if let Some(v) = it.next() {
            self.value = v;
        }
    }

    fn tick_down(&mut self) {
        let it = T::iter();
        let mut last_value: Option<T> = None;
        for v in it {
            if v == self.value {
                if let Some(lv) = last_value {
                    self.value = lv;
                    return;
                }
            }
            last_value = Some(v);
        }
    }

    fn percent(&self) -> f32 {
        let it = T::iter();
        let mut n = 0u32;
        for v in it {
            if v == self.value {
                break;
            }
            n += 1;
        }
        (n as f32) / (T::iter().count() as f32)
    }

    fn n_unique_values(&self) -> usize {
        T::iter().count()
    }
}

#[derive(Clone, Copy)]
pub enum FloatFormat {
    Precision(u8),  // Display as float with N decimal places
    Percent(u8),    // Display as percentage with N decimal places
}

#[derive(Clone)]
pub struct FloatOption<T: FloatOptionConfig> {
    name: &'static str,
    pub value: T::Value,
}

pub trait FloatOptionConfig {
    type Value: Copy + Default;
    const STEP: Self::Value;
    const MIN: Self::Value;
    const MAX: Self::Value;
    const FORMAT: FloatFormat;
}

impl<T: FloatOptionConfig> FloatOption<T> {
    pub fn new(name: &'static str, value: T::Value) -> Self {
        Self {
            name,
            value,
        }
    }
}

impl<T: FloatOptionConfig> OptionTrait for FloatOption<T>
where
    T::Value: Copy
        + Default
        + core::ops::Add<Output = T::Value>
        + core::ops::Sub<Output = T::Value>
        + core::ops::Div<Output = T::Value>
        + core::ops::Mul<Output = T::Value>
        + core::cmp::PartialOrd
        + core::fmt::Display,
    f32: From<T::Value>,
    T::Value: From<f32>,
{
    fn name(&self) -> &'static str {
        self.name
    }

    fn value(&self) -> OptionString {
        let mut s: OptionString = String::new();
        match T::FORMAT {
            FloatFormat::Precision(precision) => {
                write!(&mut s, "{:.*}", precision as usize, self.value).ok();
            }
            FloatFormat::Percent(precision) => {
                let percent_value = f32::from(self.value) * 100.0;
                write!(&mut s, "{:.*}%", precision as usize, percent_value).ok();
            }
        }
        s
    }

    fn tick_up(&mut self) {
        let new_value = self.value + T::STEP;
        if new_value <= T::MAX {
            self.value = new_value;
        }
    }

    fn tick_down(&mut self) {
        let new_value = self.value - T::STEP;
        if new_value >= T::MIN {
            self.value = new_value;
        }
    }

    fn percent(&self) -> f32 {
        let range = T::MAX - T::MIN;
        let value = self.value - T::MIN;
        f32::from(value) / f32::from(range)
    }

    fn n_unique_values(&self) -> usize {
        let range = T::MAX - T::MIN;
        let steps = range / T::STEP;
        f32::from(steps) as usize + 1
    }
}

// Macro for creating float option configs
#[macro_export]
macro_rules! float_option_config {
    ($name:ident<$t:ty> { step: $step:expr, min: $min:expr, max: $max:expr, format: $format:expr }) => {
        #[derive(Clone)]
        pub struct $name;

        impl FloatOptionConfig for $name {
            type Value = $t;
            const STEP: Self::Value = $step;
            const MIN: Self::Value = $min;
            const MAX: Self::Value = $max;
            const FORMAT: FloatFormat = $format;
        }
    };
    ($name:ident: $t:ty => $step:expr, $min:expr, $max:expr, $format:expr) => {
        float_option_config!($name<$t> {
            step: $step,
            min: $min,
            max: $max,
            format: $format
        });
    };
}
