use heapless::String;
use strum::IntoEnumIterator;
use core::str::FromStr;
use serde::{Serialize, Deserialize};

use crate::traits::*;

#[derive(Clone, Default)]
pub struct EnumOption<T: Copy + IntoEnumIterator + Default> {
    pub name: &'static str,
    pub value: T,
}

impl<T: Copy + IntoEnumIterator + Default> EnumOption<T> {
    pub fn new(name: &'static str, value: T) -> Self {
        Self {
            name,
            value,
        }
    }
}

impl<T> OptionTrait for EnumOption<T>
where
    T: Copy
        + IntoEnumIterator
        + PartialEq
        + Into<&'static str>
        + Default
        + Serialize
        + for<'de> Deserialize<'de>
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

    fn typeid(&self) -> &'static str {
        core::any::type_name::<T>()
    }

    fn encode(&self, buf: &mut [u8]) -> usize {
        use postcard::to_slice;
        let used = to_slice(&self.value, buf).unwrap();
        used.len()
    }

    fn decode(&mut self, buf: &[u8]) -> bool {
        use postcard::from_bytes;
        if let Ok(v) = from_bytes::<T>(buf) {
            self.value = v;
            true
        } else {
            false
        }
    }
}
