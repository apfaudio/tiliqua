use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use tiliqua_lib::palette::ColorPalette;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    Vector,
    Beam,
    #[default]
    Scope,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum TriggerMode {
    #[default]
    Always,
    Rising,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum USBMode {
    #[default]
    Bypass,
    Enable,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum Show {
    #[default]
    Inputs,
    Outputs,
}

int_params!(XScaleParams<u8>      { step: 1, min: 0, max: 15 });
int_params!(YScaleParams<u8>      { step: 1, min: 0, max: 15 });
int_params!(PersistParams<u16>    { step: 64, min: 64, max: 4096 });
int_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(TimebaseParams<u16>   { step: 128, min: 32, max: 3872 });
int_params!(TriggerLvlParams<i16> { step: 512, min: -16384, max: 16384 });
int_params!(YPosParams<i16>       { step: 25, min: -500, max: 500 });

#[derive(OptionPage, Clone)]
pub struct VectorOpts {
    #[option(6)]
    pub xscale: IntOption<XScaleParams>,
    #[option(6)]
    pub yscale: IntOption<YScaleParams>,
}

#[derive(OptionPage, Clone)]
pub struct BeamOpts {
    #[option(128)]
    pub persist: IntOption<PersistParams>,
    #[option(1)]
    pub decay: IntOption<DecayParams>,
    #[option(8)]
    pub intensity: IntOption<IntensityParams>,
    #[option(10)]
    pub hue: IntOption<HueParams>,
    #[option]
    pub palette: EnumOption<ColorPalette>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts {
    #[option(32)]
    pub timebase: IntOption<TimebaseParams>,
    #[option]
    pub trig_mode: EnumOption<TriggerMode>,
    #[option]
    pub trig_lvl: IntOption<TriggerLvlParams>,
    #[option(-250)]
    pub ypos0: IntOption<YPosParams>,
    #[option(-75)]
    pub ypos1: IntOption<YPosParams>,
    #[option(75)]
    pub ypos2: IntOption<YPosParams>,
    #[option(250)]
    pub ypos3: IntOption<YPosParams>,
    #[option(8)]
    pub yscale: IntOption<YScaleParams>,
    #[option(6)]
    pub xscale: IntOption<XScaleParams>,
}

#[derive(Options, Clone, Default)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Vector)]
    pub vector: VectorOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
    #[page(Page::Scope)]
    pub scope: ScopeOpts,
}
