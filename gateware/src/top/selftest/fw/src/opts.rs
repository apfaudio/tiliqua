use tiliqua_lib::opt::*;
use opts_macro::*;

use heapless::String;

use core::str::FromStr;

use strum_macros::{EnumIter, IntoStaticStr};

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Screen {
    Report,
    Autocal,
    TweakAdc,
    TweakDac,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum AutoZero {
    AdcZero,
    AdcScale,
    DacZero,
    DacScale,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum ReportPage {
    Startup,
    Status,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum EnAutoZero {
    Stop,
    Run,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum EnWrite {
    WriteD,
    Turn,
    WriteU,
}

#[derive(OptionView, Clone)]
pub struct AutocalOptions {
    pub selected: Option<usize>,
    #[option(0, 1, -8, 8)]
    pub volts: NumOption<i8>,
    #[option(AutoZero::AdcZero)]
    pub autozero: EnumOption<AutoZero>,
    #[option(EnAutoZero::Stop)]
    pub run: EnumOption<EnAutoZero>,
    #[option(EnWrite::Turn)]
    pub write: EnumOption<EnWrite>,
}

#[derive(OptionView, Clone)]
pub struct ReportOptions {
    pub selected: Option<usize>,
    #[option(ReportPage::Startup)]
    pub page: EnumOption<ReportPage>,
}

#[derive(OptionView, Clone)]
pub struct CalOptions {
    pub selected: Option<usize>,
    #[option(0, 1, -256, 256)]
    pub zero0: NumOption<i16>,
    #[option(0, 1, -256, 256)]
    pub zero1: NumOption<i16>,
    #[option(0, 1, -256, 256)]
    pub zero2: NumOption<i16>,
    #[option(0, 1, -256, 256)]
    pub zero3: NumOption<i16>,
    #[option(0, 1, -256, 256)]
    pub scale0: NumOption<i16>,
    #[option(0, 1, -256, 256)]
    pub scale1: NumOption<i16>,
    #[option(0, 1, -256, 256)]
    pub scale2: NumOption<i16>,
    #[option(0, 1, -256, 256)]
    pub scale3: NumOption<i16>,
}

#[derive(OptionPage, Clone)]
pub struct Options {
    pub modify: bool,
    pub screen: EnumOption<Screen>,

    #[screen(Screen::Report)]
    pub report: ReportOptions,
    #[screen(Screen::Autocal)]
    pub reference: AutocalOptions,
    #[screen(Screen::TweakAdc)]
    pub caladc: CalOptions,
    #[screen(Screen::TweakDac)]
    pub caldac: CalOptions,
}

impl Options {
    pub fn new() -> Options {
        Options {
            modify: true,
            screen: EnumOption::new("", Screen::Report),
            report: ReportOptions::default(),
            reference: AutocalOptions::default(),
            caldac: CalOptions::default(),
            caladc: CalOptions::default(),
        }
    }
}
