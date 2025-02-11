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
    #[option]
    pub volts: NumOption<i8>,
    #[option]
    pub autozero: EnumOption<AutoZero>,
    #[option]
    pub run: EnumOption<EnAutoZero>,
    #[option]
    pub write: EnumOption<EnWrite>,
}

#[derive(OptionView, Clone)]
pub struct ReportOptions {
    pub selected: Option<usize>,
    #[option]
    pub page: EnumOption<ReportPage>,
}

#[derive(OptionView, Clone)]
pub struct CalOptions {
    pub selected: Option<usize>,
    #[option]
    pub zero0: NumOption<i16>,
    #[option]
    pub zero1: NumOption<i16>,
    #[option]
    pub zero2: NumOption<i16>,
    #[option]
    pub zero3: NumOption<i16>,
    #[option]
    pub scale0: NumOption<i16>,
    #[option]
    pub scale1: NumOption<i16>,
    #[option]
    pub scale2: NumOption<i16>,
    #[option]
    pub scale3: NumOption<i16>,
}

impl CalOptions {
    pub fn default() -> Self {
        Self {
            selected: None,
            zero0:  NumOption::new("zero0",  0, 1, -256, 256),
            zero1:  NumOption::new("zero1",  0, 1, -256, 256),
            zero2:  NumOption::new("zero2",  0, 1, -256, 256),
            zero3:  NumOption::new("zero3",  0, 1, -256, 256),
            scale0: NumOption::new("scale0", 0, 1, -256, 256),
            scale1: NumOption::new("scale1", 0, 1, -256, 256),
            scale2: NumOption::new("scale2", 0, 1, -256, 256),
            scale3: NumOption::new("scale3", 0, 1, -256, 256),
        }
    }
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
            screen: EnumOption {
                name: String::from_str("screen").unwrap(),
                value: Screen::Report,
            },
            report: ReportOptions {
                selected: None,
                page: EnumOption::new("page", ReportPage::Startup),
            },
            reference: AutocalOptions {
                selected: None,
                volts:    NumOption::new("volts", 0, 1, -8, 8),
                autozero: EnumOption::new("set", AutoZero::AdcZero),
                run:      EnumOption::new("run", EnAutoZero::Stop),
                write:    EnumOption::new("write", EnWrite::Turn),
            },
            caldac: CalOptions::default(),
            caladc: CalOptions::default(),
        }
    }
}
