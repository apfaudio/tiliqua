#![cfg_attr(not(test), no_std)]

use strum::IntoEnumIterator;

pub use opts_derive::{OptionPage, Options};

mod traits;
mod integer;
mod enumeration;
mod float;

pub use crate::traits::*;
pub use crate::integer::*;
pub use crate::enumeration::*;
pub use crate::float::*;

#[derive(Clone, Default)]
pub struct Optif<
    ScreenT: Copy + IntoEnumIterator + Default,
    OptionT: Options
    > {
    pub selected: Option<usize>,
    pub modify: bool,
    pub page: EnumOption<ScreenT>,
    pub opts: OptionT,
}

pub trait OptionsEncoderInterface {
    fn toggle_modify(&mut self);
    fn tick_up(&mut self);
    fn tick_down(&mut self);
    fn consume_ticks(&mut self, ticks: i8);
    fn current_page(&self) -> OptionString;
    fn current_opts(&self) -> OptionVec;
    fn selected(&self) -> Option<usize>;
    fn modify(&self) -> bool;
}

impl<S, T> OptionsEncoderInterface for Optif<S, T>
where
    S: Copy + IntoEnumIterator + Default + Into<&'static str> + PartialEq,
    T: Options<PageT = S>,
{
    fn toggle_modify(&mut self) {
        self.modify = !self.modify
    }

    fn tick_up(&mut self) {
        if let Some(n_selected) = self.selected {
            if self.modify {
                self.opts.page_mut(&self.page.value).options_mut()[n_selected].tick_up();
            } else if n_selected < self.opts.page(&self.page.value).options().len()-1 {
                self.selected = Some(n_selected + 1);
            }
        } else if self.modify {
            self.page.tick_up();
        } else if !self.opts.page(&self.page.value).options().is_empty() {
            self.selected = Some(0);
        }
    }

    fn tick_down(&mut self) {
        if let Some(n_selected) = self.selected {
            if self.modify {
                self.opts.page_mut(&self.page.value).options_mut()[n_selected].tick_down();
            } else if n_selected != 0 {
                self.selected = Some(n_selected - 1);
            } else {
                if self.page.n_unique_values() > 1 {
                    self.selected = None;
                }
            }
        } else if self.modify {
            self.page.tick_down();
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

    fn current_opts(&self) -> OptionVec {
        self.opts.page(&self.page.value).options()
    }

    fn selected(&self) -> Option<usize> {
        self.selected
    }

    fn modify(&self) -> bool {
        self.modify
    }

    fn current_page(&self) -> OptionString {
        self.page.value()
    }
}

#[cfg(test)]
mod tests {
    use log::info;
    use super::*;
    use strum::{EnumIter, IntoStaticStr};
    use core::str::FromStr;

    #[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
    #[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
    pub enum Page {
        #[default]
        Scope,
        Position,
    }

    int_params!(PositionParams<i16>     { step: 25,  min: -500,   max: 500 });
    int_params!(ScaleParams<u8>         { step: 1,   min: 0,      max: 15 });

    #[derive(OptionPage, Clone)]
    pub struct ScopeOpts {
        #[option]
        pub ypos0: IntOption<PositionParams>,
        #[option(-150)]
        pub ypos1: IntOption<PositionParams>,
        #[option(7)]
        pub xscale: IntOption<ScaleParams>,
    }

    #[derive(OptionPage, Clone)]
    pub struct PositionOpts {
        #[option]
        pub size: IntOption<ScaleParams>,
    }

    #[derive(Options, Clone, Default)]
    pub struct Opts {
        #[page(Page::Scope)]
        pub scope: ScopeOpts,
        #[page(Page::Position)]
        pub position: PositionOpts,
    }

    #[test]
    fn test_opts() {
        env_logger::init();
        let optif = Optif::<Page, Opts>::default();
        for page in Page::iter() {
            info!("{}", String::from_str(page.into()).unwrap());
            for opt in optif.opts.page(&page).options() {
                info!("\t{}: {}", opt.name(), opt.value());
            }
        }
    }

}
