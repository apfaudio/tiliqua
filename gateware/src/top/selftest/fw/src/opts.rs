use tiliqua_lib::opt::*;
use tiliqua_lib::impl_option_view;
use tiliqua_lib::impl_option_page;

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

#[derive(Clone)]
pub struct AutocalOptions {
    pub selected: Option<usize>,
    pub volts: NumOption<i8>,
    pub autozero: EnumOption<AutoZero>,
    pub run: EnumOption<EnAutoZero>,
    pub write: EnumOption<EnWrite>,
}

impl_option_view!(AutocalOptions, volts, autozero, run, write);

#[derive(Clone)]
pub struct ReportOptions {
    pub selected: Option<usize>,
    pub page: EnumOption<ReportPage>,
}

impl_option_view!(ReportOptions, page);

#[derive(Clone)]
pub struct CalOptions {
    pub selected: Option<usize>,
    pub zero0: NumOption<i16>,
    pub zero1: NumOption<i16>,
    pub zero2: NumOption<i16>,
    pub zero3: NumOption<i16>,
    pub scale0: NumOption<i16>,
    pub scale1: NumOption<i16>,
    pub scale2: NumOption<i16>,
    pub scale3: NumOption<i16>,
}

impl CalOptions {
    pub fn default() -> Self {
        Self {
            selected: None,
            zero0: NumOption {
                name: String::from_str("zero0").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
            zero1: NumOption {
                name: String::from_str("zero1").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
            zero2: NumOption {
                name: String::from_str("zero2").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
            zero3: NumOption {
                name: String::from_str("zero3").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
            scale0: NumOption {
                name: String::from_str("scale0").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
            scale1: NumOption {
                name: String::from_str("scale1").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
            scale2: NumOption {
                name: String::from_str("scale2").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
            scale3: NumOption {
                name: String::from_str("scale3").unwrap(),
                value: 0,
                step: 1,
                min: -256,
                max: 256,
            },
        }
    }
}

impl_option_view!(CalOptions,
                   zero0,  zero1,  zero2,  zero3,
                  scale0, scale1, scale2, scale3);

#[derive(Clone)]
pub struct Options {
    pub modify: bool,
    pub draw: bool,
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
            draw: true,
            screen: EnumOption {
                name: String::from_str("screen").unwrap(),
                value: Screen::Report,
            },
            report: ReportOptions {
                selected: None,
                page: EnumOption {
                    name: String::from_str("page").unwrap(),
                    value: ReportPage::Startup,
                },
            },
            reference: AutocalOptions {
                selected: None,
                volts: NumOption{
                    name: String::from_str("volts").unwrap(),
                    value: 0,
                    step: 1,
                    min: -8,
                    max: 8,
                },
                autozero: EnumOption{
                    name: String::from_str("set").unwrap(),
                    value: AutoZero::AdcZero,
                },
                run: EnumOption{
                    name: String::from_str("autozero").unwrap(),
                    value: EnAutoZero::Stop,
                },
                write: EnumOption{
                    name: String::from_str("write").unwrap(),
                    value: EnWrite::Turn,
                },
            },
            caldac: CalOptions::default(),
            caladc: CalOptions::default(),
        }
    }
}
