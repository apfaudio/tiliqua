use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use serde_derive::{Serialize, Deserialize};

use tiliqua_lib::palette::ColorPalette;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Help,
    Poly,
    Beam,
    Vector,
    Misc,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum TouchControl {
    Off,
    #[default]
    On,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum UsbHost {
    #[default]
    Off,
    On,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum UsbMidiSerialDebug {
    #[default]
    Off,
    On,
}

int_params!(PageNumParams<u16>    { step: 1, min: 0, max: 0 });
int_params!(DriveParams<u16>      { step: 2048, min: 0, max: 32768 });
int_params!(ResoParams<u16>       { step: 2048, min: 8192, max: 32768 });
int_params!(DiffuseParams<u16>    { step: 2048, min: 0, max: 32768 });
int_params!(PersistParams<u16>    { step: 32, min: 32, max: 4096 });
int_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(XScaleParams<u8>      { step: 1, min: 0, max: 15 });
int_params!(YScaleParams<u8>      { step: 1, min: 0, max: 15 });

button_params!(OneShotButtonParams { mode: ButtonMode::OneShot });

#[derive(OptionPage, Clone)]
pub struct HelpOpts {
    #[option]
    pub page: IntOption<PageNumParams>,
}

#[derive(OptionPage, Clone)]
pub struct PolyOpts {
    #[option]
    pub touch_control: EnumOption<TouchControl>,
    #[option(16384)]
    pub drive: IntOption<DriveParams>,
    #[option(16384)]
    pub reso: IntOption<ResoParams>,
    #[option(12288)]
    pub diffuse: IntOption<DiffuseParams>,
}

#[derive(OptionPage, Clone)]
pub struct VectorOpts {
    #[option(6)]
    pub xscale: IntOption<XScaleParams>,
    #[option(6)]
    pub yscale: IntOption<YScaleParams>,
}

#[derive(OptionPage, Clone)]
pub struct BeamOpts {
    #[option(64)]
    pub persist: IntOption<PersistParams>,
    #[option(2)]
    pub decay: IntOption<DecayParams>,
    #[option(8)]
    pub intensity: IntOption<IntensityParams>,
    #[option(10)]
    pub hue: IntOption<HueParams>,
    #[option]
    pub palette: EnumOption<ColorPalette>,
}

#[derive(OptionPage, Clone)]
pub struct MiscOpts {
    #[option]
    pub usb_host: EnumOption<UsbHost>,
    #[option]
    pub serial_debug: EnumOption<UsbMidiSerialDebug>,
    #[option(false)]
    pub save_opts: ButtonOption<OneShotButtonParams>,
    #[option(false)]
    pub wipe_opts: ButtonOption<OneShotButtonParams>,
}

#[derive(Options, Clone)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Help)]
    pub help: HelpOpts,
    #[page(Page::Poly)]
    pub poly: PolyOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
    #[page(Page::Vector)]
    pub vector: VectorOpts,
    #[page(Page::Misc)]
    pub misc: MiscOpts,
}
