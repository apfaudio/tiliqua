use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use tiliqua_lib::palette::ColorPalette;
pub use tiliqua_lib::scope::{Timebase, VScale};
use tiliqua_hal::dma_framebuffer::Rotate;
use tiliqua_pac::constants::AUDIO_FS;
use serde_derive::{Serialize, Deserialize};

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Help,
    Vector,
    Delay,
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
pub enum GridOverlay {
    Off,
    Grid,
    #[default]
    Cross,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum CcHighlight {
    Off,
    #[default]
    On,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum XZoom {
    #[strum(serialize = "0.5x")]
    Half,
    #[default]
    #[strum(serialize = "1x")]
    Normal,
    #[strum(serialize = "2x")]
    Double,
}

int_params!(DelayParams<u16>      { step: 8, min: 0, max: 512, format: IntFormat::Scaled { divisor: AUDIO_FS / 1000, precision: 1, suffix: "ms" } });
int_params!(PCScaleParams<u8>     { step: 1, min: 0, max: 15 });
int_params!(PersistParams<u16>    { step: 32, min: 32, max: 4096 });
int_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(SkipParams<u8>        { step: 16, min: 0, max: 240 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(TriggerLvlParams<i16> { step: 500, min: -16000, max: 16000, format: IntFormat::Scaled { divisor: 4000, precision: 2, suffix: "V" } });
int_params!(PosParams<i16>       { step: 1, min: -40, max: 40, format: IntFormat::Scaled { divisor: 4, precision: 2, suffix: "d" } });
int_params!(ScrollParams<u8>      { step: 1, min: 0, max: 125 });
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
    #[option(0)]
    pub skip: IntOption<SkipParams>,
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
    pub usb_mode: EnumOption<USBMode>,
    #[option]
    pub rotation: EnumOption<Rotate>,
    #[option]
    pub help: EnumOption<HelpPage>,
    #[option]
    pub cc_highlight: EnumOption<CcHighlight>,
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
    pub xzoom: EnumOption<XZoom>,
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
    #[page(Page::Delay)]
    pub delay: DelayOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
}
