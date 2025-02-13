use tiliqua_lib::opt::*;
use tiliqua_lib::impl_option_page;
use tiliqua_lib::impl_option_view;
use tiliqua_lib::num_option_config;

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

num_option_config!(RefVoltageConfig: i8 => 1, -8, 8);

#[derive(Clone)]
pub struct AutocalOptions {
    pub selected: Option<usize>,
    pub volts: NumOption<RefVoltageConfig>,
    pub autozero: EnumOption<AutoZero>,
    pub run: EnumOption<EnAutoZero>,
    pub write: EnumOption<EnWrite>,
}

impl_option_view!(AutocalOptions, volts, autozero, run, write);

num_option_config!(CalTweakerConfig: i16 => 1, -256, 256);

#[derive(Clone)]
pub struct CalOptions {
    pub selected: Option<usize>,
    pub zero0: NumOption<CalTweakerConfig>,
    pub zero1: NumOption<CalTweakerConfig>,
    pub zero2: NumOption<CalTweakerConfig>,
    pub zero3: NumOption<CalTweakerConfig>,
    pub scale0: NumOption<CalTweakerConfig>,
    pub scale1: NumOption<CalTweakerConfig>,
    pub scale2: NumOption<CalTweakerConfig>,
    pub scale3: NumOption<CalTweakerConfig>,
}


impl CalOptions {
    pub fn default() -> Self {
        Self {
            selected: None,
            zero0: NumOption::new("zero0", 0),
            zero1: NumOption::new("zero1", 0),
            zero2: NumOption::new("zero2", 0),
            zero3: NumOption::new("zero3", 0),
            scale0: NumOption::new("scale0", 0),
            scale1: NumOption::new("scale1", 0),
            scale2: NumOption::new("scale2", 0),
            scale3: NumOption::new("scale3", 0),
        }
    }
}

impl_option_view!(CalOptions,
                   zero0,  zero1,  zero2,  zero3,
                  scale0, scale1, scale2, scale3);

#[derive(Clone)]
pub struct ReportOptions {
    pub selected: Option<usize>,
    pub page: EnumOption<ReportPage>,
}

impl_option_view!(ReportOptions, page);

#[derive(Clone)]
pub struct Options {
    pub modify: bool,
    pub screen: EnumOption<Screen>,

    pub report: ReportOptions,
    pub reference: AutocalOptions,
    pub caldac: CalOptions,
    pub caladc: CalOptions,
}

impl_option_page!(Options,
                  (Screen::Report, report),
                  (Screen::Autocal, reference),
                  (Screen::TweakAdc, caladc),
                  (Screen::TweakDac, caldac)
                  );

impl Options {
    pub fn new() -> Options {
        Options {
            modify: true,
            screen: EnumOption::<Screen>::new("", Screen::Autocal),
            report: ReportOptions {
                selected: None,
                page: EnumOption::new("page", ReportPage::Startup),
            },
            reference: AutocalOptions {
                selected: None,
                volts: NumOption::new("volts", 0),
                autozero: EnumOption::new("set", AutoZero::AdcZero),
                run: EnumOption::new("autozero", EnAutoZero::Stop),
                write: EnumOption::new("write", EnWrite::Turn),
            },
            caldac: CalOptions::default(),
            caladc: CalOptions::default(),
        }
    }
}
