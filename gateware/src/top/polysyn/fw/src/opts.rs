use tiliqua_lib::opt::*;
use tiliqua_lib::num_params;
use strum_macros::{EnumIter, IntoStaticStr};
use opts_macro::{Options, OptionPage};

use tiliqua_lib::palette::ColorPalette;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Help,
    Poly,
    Beam,
    Vector,
    Usb,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum TouchControl {
    Off,
    #[default]
    On,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum UsbHost {
    #[default]
    Off,
    Enable,
}

num_params!(PageNumParams<u16>    { step: 1, min: 0, max: 0 });
num_params!(DriveParams<u16>      { step: 2048, min: 0, max: 32768 });
num_params!(ResoParams<u16>       { step: 2048, min: 8192, max: 32768 });
num_params!(DiffuseParams<u16>    { step: 2048, min: 0, max: 32768 });
num_params!(PersistParams<u16>    { step: 256, min: 256, max: 32768 });
num_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
num_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
num_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
num_params!(XScaleParams<u8>      { step: 1, min: 0, max: 15 });
num_params!(YScaleParams<u8>      { step: 1, min: 0, max: 15 });
num_params!(CfgIdParams<u8>       { step: 1, min: 1, max: 15 });
num_params!(EndptIdParams<u8>     { step: 1, min: 1, max: 15 });

#[derive(OptionPage, Clone)]
pub struct HelpOpts {
    #[option]
    pub page: NumOption<PageNumParams>,
}

#[derive(OptionPage, Clone)]
pub struct PolyOpts {
    #[option]
    pub touch_control: EnumOption<TouchControl>,
    #[option(16384)]
    pub drive: NumOption<DriveParams>,
    #[option(16384)]
    pub reso: NumOption<ResoParams>,
    #[option(12288)]
    pub diffuse: NumOption<DiffuseParams>,
}

#[derive(OptionPage, Clone)]
pub struct VectorOpts {
    #[option(7)]
    pub xscale: NumOption<XScaleParams>,
    #[option(7)]
    pub yscale: NumOption<YScaleParams>,
}

#[derive(OptionPage, Clone)]
pub struct BeamOpts {
    #[option(512)]
    pub persist: NumOption<PersistParams>,
    #[option(1)]
    pub decay: NumOption<DecayParams>,
    #[option(8)]
    pub intensity: NumOption<IntensityParams>,
    #[option(10)]
    pub hue: NumOption<HueParams>,
    #[option]
    pub palette: EnumOption<ColorPalette>,
}

#[derive(OptionPage, Clone)]
pub struct UsbOpts {
    #[option]
    pub host: EnumOption<UsbHost>,
    #[option(1)]
    pub cfg_id: NumOption<CfgIdParams>,
    #[option(2)]
    pub endpt_id: NumOption<EndptIdParams>,
}

#[derive(Options, Clone, Default)]
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
    #[page(Page::Usb)]
    pub usb: UsbOpts,
}
