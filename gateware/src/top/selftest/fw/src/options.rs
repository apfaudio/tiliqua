use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Report,
    Autocal,
    TweakAdc,
    TweakDac,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum AutoZero {
    #[default]
    AdcZero,
    AdcScale,
    DacZero,
    DacScale,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum ReportPage {
    Startup,
    #[default]
    Status,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum EnAutoZero {
    #[default]
    Stop,
    Run,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum EnWrite {
    WriteD,
    #[default]
    Turn,
    WriteU,
}

int_params!(RefVoltageParams<i8>     { step: 1, min: -12, max: 12 });
int_params!(CalTweakerParams<i16>    { step: 1, min: -256, max: 256 });

#[derive(OptionPage, Clone)]
pub struct ReportOpts {
    #[option]
    pub page: EnumOption<ReportPage>,
}

#[derive(OptionPage, Clone)]
pub struct AutocalOpts {
    #[option]
    pub volts: IntOption<RefVoltageParams>,
    #[option]
    pub set: EnumOption<AutoZero>,
    #[option]
    pub autozero: EnumOption<EnAutoZero>,
    #[option]
    pub write: EnumOption<EnWrite>,
}

#[derive(OptionPage, Clone)]
pub struct CalOpts {
    #[option]
    pub zero0: IntOption<CalTweakerParams>,
    #[option]
    pub zero1: IntOption<CalTweakerParams>,
    #[option]
    pub zero2: IntOption<CalTweakerParams>,
    #[option]
    pub zero3: IntOption<CalTweakerParams>,
    #[option]
    pub scale0: IntOption<CalTweakerParams>,
    #[option]
    pub scale1: IntOption<CalTweakerParams>,
    #[option]
    pub scale2: IntOption<CalTweakerParams>,
    #[option]
    pub scale3: IntOption<CalTweakerParams>,
}

#[derive(Options, Clone, Default)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Report)]
    pub report: ReportOpts,
    #[page(Page::Autocal)]
    pub autocal: AutocalOpts,
    #[page(Page::TweakAdc)]
    pub caladc: CalOpts,
    #[page(Page::TweakDac)]
    pub caldac: CalOpts,
}
