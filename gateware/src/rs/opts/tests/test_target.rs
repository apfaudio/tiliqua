#![cfg_attr(not(test), no_std)]

use opts::*;
use strum::{EnumIter, IntoStaticStr};
use serde_derive::{Serialize, Deserialize};

#[cfg(test)]
mod tests {
    use super::*;
    use log::info;

    #[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default, Serialize, Deserialize)]
    #[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
    pub enum Page {
        #[default]
        Scope,
    }

    #[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default, Serialize, Deserialize)]
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
            let mut buf: [u8; 8] = [0u8; 8];
            let n = opt.encode(&mut buf);
            info!("\t{} - {:?} - {:?}", opt.key(), n, buf);
        }
    }

}
