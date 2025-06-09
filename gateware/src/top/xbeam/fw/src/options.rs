use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use tiliqua_lib::palette::ColorPalette;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    Vector,
    Delay,
    Beam,
    Usb,
    #[default]
    Scope1,
    Scope2,
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
    Inputs,
    #[default]
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

int_params!(DelayParams<u16>      { step: 8, min: 0, max: 512 });
int_params!(ScaleParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(PCScaleParams<u8>     { step: 1, min: 0, max: 15 });
int_params!(PersistParams<u16>    { step: 32, min: 32, max: 4096 });
int_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(TriggerLvlParams<i16> { step: 512, min: -16384, max: 16384 });
int_params!(PosParams<i16>       { step: 25, min: -500, max: 500 });

#[derive(OptionPage, Clone)]
pub struct VectorOpts {
    #[option(0)]
    pub x_offset: IntOption<PosParams>,
    #[option(9)]
    pub x_scale: IntOption<ScaleParams>,
    #[option(0)]
    pub y_offset: IntOption<PosParams>,
    #[option(9)]
    pub y_scale: IntOption<ScaleParams>,
    #[option(4)]
    pub i_offset: IntOption<IntensityParams>,
    #[option(0)]
    pub i_scale: IntOption<PCScaleParams>,
    #[option(10)]
    pub c_offset: IntOption<HueParams>,
    #[option(0)]
    pub c_scale: IntOption<PCScaleParams>,
}

#[derive(OptionPage, Clone)]
pub struct DelayOpts {
    #[option(0)]
    pub delay_x: IntOption<DelayParams>,
    #[option(0)]
    pub delay_y: IntOption<DelayParams>,
    #[option(0)]
    pub delay_i: IntOption<DelayParams>,
    #[option(0)]
    pub delay_c: IntOption<DelayParams>,
}

#[derive(OptionPage, Clone)]
pub struct BeamOpts {
    #[option(32)]
    pub persist: IntOption<PersistParams>,
    #[option(1)]
    pub decay: IntOption<DecayParams>,
    #[option(10)]
    pub ui_hue: IntOption<HueParams>,
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
pub struct ScopeOpts1 {
    #[option]
    pub timebase: EnumOption<Timebase>,
    #[option]
    pub trig_mode: EnumOption<TriggerMode>,
    #[option]
    pub trig_lvl: IntOption<TriggerLvlParams>,
    #[option(6)]
    pub yscale: IntOption<ScaleParams>,
    #[option(9)]
    pub xscale: IntOption<ScaleParams>,
    #[option(8)]
    pub intensity: IntOption<IntensityParams>,
    #[option(10)]
    pub hue: IntOption<HueParams>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts2 {
    #[option(-250)]
    pub ypos0: IntOption<PosParams>,
    #[option(-75)]
    pub ypos1: IntOption<PosParams>,
    #[option(75)]
    pub ypos2: IntOption<PosParams>,
    #[option(250)]
    pub ypos3: IntOption<PosParams>,
}

#[derive(Options, Clone, Default)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Vector)]
    pub vector: VectorOpts,
    #[page(Page::Delay)]
    pub delay: DelayOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
    #[page(Page::Usb)]
    pub usb: UsbOpts,
    #[page(Page::Scope1)]
    pub scope1: ScopeOpts1,
    #[page(Page::Scope2)]
    pub scope2: ScopeOpts2,
}
