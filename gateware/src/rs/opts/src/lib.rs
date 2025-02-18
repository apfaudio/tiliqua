#![cfg_attr(not(test), no_std)]

use strum::IntoEnumIterator;

pub use opts_derive::{OptionPage, Options};

mod traits;
mod integer;
mod enumeration;
mod float;
mod string;

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

#[cfg(test)]
mod tests {
    use log::info;
    use super::*;
    use strum::{EnumIter, IntoStaticStr};

    #[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
    #[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
    pub enum Page {
        #[default]
        Scope,
    }

    #[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
    #[strum(serialize_all = "kebab-case")]
    pub enum TestEnum {
        EnumValue1,
        #[default]
        EnumValue2,
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
        #[option]
        pub enumo: EnumOption<TestEnum>,
        #[option("hello")]
        pub stro: StringOption,
    }

    #[derive(Options, Clone, Default)]
    pub struct Opts {
        pub tracker: ScreenTracker<Page>,
        #[page(Page::Scope)]
        pub scope: ScopeOpts,
    }

    #[test]
    fn test_opts() {
        env_logger::init();
        let opts = Opts::default();
        info!("page: {}", opts.page().value());
        for opt in opts.view().options() {
            info!("\t{}: {}", opt.name(), opt.value());
        }
    }

}
