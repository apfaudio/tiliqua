use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use tiliqua_lib::palette::ColorPalette;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    Vector,
    Beam,
    Usb,
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

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum Timebase {
    #[strum(serialize = "1s")]
    Timebase1s,
    #[strum(serialize = "500ms")]
    Timebase500ms,
    #[strum(serialize = "250ms")]
    Timebase250ms,
    #[default]
    #[strum(serialize = "100ms")]
    Timebase100ms,
    #[strum(serialize = "50ms")]
    Timebase50ms,
    #[strum(serialize = "25ms")]
    Timebase25ms,
    #[strum(serialize = "10ms")]
    Timebase10ms,
    #[strum(serialize = "5ms")]
    Timebase5ms,
    #[strum(serialize = "2.5ms")]
    Timebase2p5ms,
    #[strum(serialize = "1ms")]
    Timebase1ms,
}

int_params!(ScaleParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(PersistParams<u16>    { step: 16, min: 16, max: 4096 });
int_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(TriggerLvlParams<i16> { step: 512, min: -16384, max: 16384 });
int_params!(YPosParams<i16>       { step: 25, min: -500, max: 500 });

#[derive(OptionPage, Clone)]
pub struct VectorOpts {
    #[option(6)]
    pub xscale: IntOption<ScaleParams>,
    #[option(6)]
    pub yscale: IntOption<ScaleParams>,
    #[option(10)]
    pub pscale: IntOption<ScaleParams>,
    #[option(10)]
    pub cscale: IntOption<ScaleParams>,
}

#[derive(OptionPage, Clone)]
pub struct BeamOpts {
    #[option(64)]
    pub persist: IntOption<PersistParams>,
    #[option(2)]
    pub decay: IntOption<DecayParams>,
    #[option(4)]
    pub intensity: IntOption<IntensityParams>,
    #[option(10)]
    pub hue: IntOption<HueParams>,
    #[option]
    pub palette: EnumOption<ColorPalette>,
}

#[derive(OptionPage, Clone)]
pub struct UsbOpts {
    #[option]
    pub mode: EnumOption<USBMode>,
    #[option]
    pub show: EnumOption<Show>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts {
    #[option]
    pub timebase: EnumOption<Timebase>,
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
    pub yscale: IntOption<ScaleParams>,
    #[option(6)]
    pub xscale: IntOption<ScaleParams>,
}

#[derive(Options, Clone, Default)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Vector)]
    pub vector: VectorOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
    #[page(Page::Usb)]
    pub usb: UsbOpts,
    #[page(Page::Scope)]
    pub scope: ScopeOpts,
}
