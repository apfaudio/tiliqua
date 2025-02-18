use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Boot,
}

#[derive(OptionPage, Clone)]
pub struct BootOpts {
    #[option]
    pub slot0: StringOption,
    #[option]
    pub slot1: StringOption,
    #[option]
    pub slot2: StringOption,
    #[option]
    pub slot3: StringOption,
    #[option]
    pub slot4: StringOption,
    #[option]
    pub slot5: StringOption,
    #[option]
    pub slot6: StringOption,
    #[option]
    pub slot7: StringOption,
}

#[derive(Options, Clone, Default)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Boot)]
    pub boot: BootOpts,
}
