use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use tiliqua_lib::palette::ColorPalette;
pub use tiliqua_lib::scope::{Timebase, VScale};
use tiliqua_hal::dma_framebuffer::Rotate;
use serde_derive::{Serialize, Deserialize};

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Help,
    Vector,
    Beam,
    Misc,
    Scope1,
    Scope2,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum TriggerMode {
    #[default]
    Always,
    Rising,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum USBMode {
    #[default]
    Bypass,
    Enable,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum PlotSrc {
    Inputs,
    #[default]
    Outputs,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum PlotType {
    Vector,
    #[default]
    Scope,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum HelpPage {
    Off,
    #[default]
    On,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum PlotIO {
    #[default]
    Builtin,
    #[cfg(expander_ex0)]
    Ex0,
    #[cfg(expander_ex1)]
    Ex1,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum GridOverlay {
    Off,
    Grid,
    #[default]
    Cross,
}

int_params!(PCScaleParams<u8>     { step: 1, min: 0, max: 15 });
int_params!(PersistParams<u16>    { step: 32, min: 32, max: 4096 });
int_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(TriggerLvlParams<i16> { step: 500, min: -16000, max: 16000, format: IntFormat::Scaled { divisor: 4000, precision: 2, suffix: "V" } });
int_params!(PosParams<i16>       { step: 1, min: -40, max: 40, format: IntFormat::Scaled { divisor: 4, precision: 2, suffix: "d" } });
int_params!(ScrollParams<u8>      { step: 1, min: 0, max: 60 });
int_params!(NChannelsParams<u8>   { step: 1, min: 1, max: 4 });

button_params!(OneShotButtonParams { mode: ButtonMode::OneShot });

#[derive(OptionPage, Clone)]
pub struct HelpOpts {
    #[option(0)]
    pub scroll: IntOption<ScrollParams>,
}

#[derive(OptionPage, Clone)]
pub struct VectorOpts {
    #[option(0)]
    pub x_offset: IntOption<PosParams>,
    #[option(VScale::Scale2V)]
    pub x_scale: EnumOption<VScale>,
    #[option(0)]
    pub y_offset: IntOption<PosParams>,
    #[option(VScale::Scale2V)]
    pub y_scale: EnumOption<VScale>,
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
pub struct BeamOpts {
    #[option(32)]
    pub persist: IntOption<PersistParams>,
    #[option(1)]
    pub decay: IntOption<DecayParams>,
    #[option(10)]
    pub ui_hue: IntOption<HueParams>,
    #[option]
    pub palette: EnumOption<ColorPalette>,
    #[option]
    pub grid: EnumOption<GridOverlay>,
    #[option(4)]
    pub grid_i: IntOption<IntensityParams>,
}

#[derive(OptionPage, Clone)]
pub struct MiscOpts {
    #[option]
    pub plot_type: EnumOption<PlotType>,
    #[option]
    pub plot_src: EnumOption<PlotSrc>,
    #[option]
    pub plot_io: EnumOption<PlotIO>,
    #[option]
    pub usb_mode: EnumOption<USBMode>,
    #[option]
    pub rotation: EnumOption<Rotate>,
    #[option]
    pub help: EnumOption<HelpPage>,
    #[option(false)]
    pub save_opts: ButtonOption<OneShotButtonParams>,
    #[option(false)]
    pub wipe_opts: ButtonOption<OneShotButtonParams>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts1 {
    #[option(-14)]
    pub ypos0: IntOption<PosParams>,
    #[option(-5)]
    pub ypos1: IntOption<PosParams>,
    #[option(5)]
    pub ypos2: IntOption<PosParams>,
    #[option(14)]
    pub ypos3: IntOption<PosParams>,
    #[option(4)]
    pub n_channels: IntOption<NChannelsParams>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts2 {
    #[option(VScale::Scale4V)]
    pub yscale: EnumOption<VScale>,
    #[option]
    pub timebase: EnumOption<Timebase>,
    #[option]
    pub trig_mode: EnumOption<TriggerMode>,
    #[option]
    pub trig_lvl: IntOption<TriggerLvlParams>,
    #[option(8)]
    pub intensity: IntOption<IntensityParams>,
    #[option(10)]
    pub hue: IntOption<HueParams>,
}

#[derive(Options, Clone)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Help)]
    pub help: HelpOpts,
    #[page(Page::Misc)]
    pub misc: MiscOpts,
    #[page(Page::Scope1)]
    pub scope1: ScopeOpts1,
    #[page(Page::Scope2)]
    pub scope2: ScopeOpts2,

    #[page(Page::Vector)]
    pub vector: VectorOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
}
