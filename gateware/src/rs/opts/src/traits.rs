use heapless::String;
use heapless::Vec;

use strum::IntoEnumIterator;

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

pub trait OptionPage {
    fn options(&self) -> OptionVec;
    fn options_mut(&mut self) -> OptionVecMut;
}

pub trait Options {
    type PageT: Copy + IntoEnumIterator + Default;
    fn page(&self, page: &Self::PageT) -> &dyn OptionPage;
    fn page_mut(&mut self, page: &Self::PageT) -> &mut dyn OptionPage;
}
