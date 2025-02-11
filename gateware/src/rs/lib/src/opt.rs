use heapless::String;
use heapless::Vec;

use core::fmt::Write;
use core::str::FromStr;

pub const MAX_OPTS_PER_TAB: usize = 16;
pub const MAX_OPT_NAME:     usize = 32;

pub type OptionString = String<MAX_OPT_NAME>;
pub type OptionVec<'a> = Vec<&'a dyn OptionTrait, MAX_OPTS_PER_TAB>;
pub type OptionVecMut<'a> = Vec<&'a mut dyn OptionTrait, MAX_OPTS_PER_TAB>;

pub trait OptionTrait {
    fn name(&self) -> &OptionString;
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
pub struct NumOption<T> {
    pub name: OptionString,
    pub value: T,
    pub step: T,
    pub min: T,
    pub max: T,
}

#[derive(Clone)]
pub struct EnumOption<T> {
    pub name: OptionString,
    pub value: T,
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

impl<T: Copy +
        core::ops::Add<Output = T> +
        core::ops::Sub<Output = T> +
        core::cmp::PartialOrd +
        core::fmt::Display> NumOption<T> {
    pub fn new(name: &str, value: T, min: T, max: T, step: T) -> Self {
        NumOption {
            name: String::from_str(name).unwrap(),
            value,
            step,
            min,
            max,
        }
    }
}

impl<T: Copy +
        strum::IntoEnumIterator +
        PartialEq +
        Into<&'static str>>
    EnumOption<T> {
    pub fn new(name: &str, value: T) -> Self {
        EnumOption {
            name: String::from_str(name).unwrap(),
            value
        }
    }
}

impl<T: Copy +
        core::ops::Add<Output = T> +
        core::ops::Sub<Output = T> +
        core::cmp::PartialOrd +
        core::fmt::Display>
    OptionTrait for NumOption<T> where f32: From<T> {

    fn name(&self) -> &OptionString {
        &self.name
    }

    fn value(&self) -> OptionString {
        let mut s: OptionString = String::new();
        write!(&mut s, "{}", self.value).ok();
        s
    }

    fn tick_up(&mut self) {
        if self.value >= self.max {
            self.value = self.max;
            return
        }
        if self.value + self.step >= self.max {
            self.value = self.max;
        } else {
            self.value = self.value + self.step;
        }
    }

    fn tick_down(&mut self) {
        if self.value <= self.min {
            self.value = self.min;
            return
        }
        if self.value - self.step <= self.min {
            self.value = self.min;
        } else {
            self.value = self.value - self.step;
        }
    }

    fn percent(&self) -> f32 {
        let n: f32 = f32::from(self.value - self.min);
        let d: f32 = f32::from(self.max - self.min);
        n / d
    }

    fn n_unique_values(&self) -> usize {
        // TODO
        0
    }
}

impl<T: Copy + strum::IntoEnumIterator + PartialEq + Into<&'static str>>
    OptionTrait for EnumOption<T> {

    fn name(&self) -> &OptionString {
        &self.name
    }

    fn value(&self) -> OptionString {
        String::from_str(self.value.into()).unwrap_or(OptionString::new())
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
