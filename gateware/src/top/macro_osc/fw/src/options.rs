use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use serde_derive::{Serialize, Deserialize};
use tiliqua_lib::palette::ColorPalette;
pub use tiliqua_lib::scope::{Timebase, VScale};

#[derive(Default, Clone, Copy, PartialEq, Eq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Help,
    Scope,
    Osc,
    Misc,
    Beam,
    Vector,
}

#[derive(Default, Clone, Copy, PartialEq, Eq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum TriggerMode {
    Always,
    #[default]
    Rising,
}

#[derive(Default, Clone, Copy, PartialEq, Eq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum PlotType {
    Vector,
    #[default]
    Scope,
}

#[derive(Default, Clone, Copy, PartialEq, Eq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum Engine {
    #[default]
    VrtAnlg1,
    PhaseDst,
    SixOp1,
    SixOp2,
    SixOp3,
    String1,
    Chiptne,
    VrtAnlg2,
    WaveShp,
    FmEngine,
    Additive,
    Wavetbl,
    Chord,
    Speech,
    Swarm,
    Noise,
    String2,
    Modal,
    BassDrm,
    Snare,
    Hihat,
}

int_params!(NoteParams<u8>        { step: 1, min: 0, max: 128 });
int_params!(HarmonicsParams<u8>   { step: 8, min: 0, max: 240 });
int_params!(TimbreParams<u8>      { step: 8, min: 0, max: 240 });
int_params!(MorphParams<u8>       { step: 8, min: 0, max: 240 });
int_params!(PersistParams<u8>     { step: 1, min: 1, max: 80 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(TriggerLvlParams<i16> { step: 500, min: -16000, max: 16000, format: IntFormat::Scaled { divisor: 4000, precision: 2, suffix: "V" } });
int_params!(YPosParams<i16>       { step: 25, min: -500, max: 500 });
int_params!(ScrollParams<u8>      { step: 1, min: 0, max: 60 });

button_params!(OneShotButtonParams { mode: ButtonMode::OneShot });

#[derive(OptionPage, Clone)]
pub struct HelpOpts {
    #[option(0)]
    pub scroll: IntOption<ScrollParams>,
}

#[derive(OptionPage, Clone)]
pub struct MiscOpts {
    #[option]
    pub plot_type: EnumOption<PlotType>,
    #[option(false)]
    pub save_opts: ButtonOption<OneShotButtonParams>,
    #[option(false)]
    pub wipe_opts: ButtonOption<OneShotButtonParams>,
}

#[derive(OptionPage, Clone)]
pub struct OscOpts {
    #[option]
    pub engine: EnumOption<Engine>,
    #[option(77)] // empirically match frequency knob full left
    pub note: IntOption<NoteParams>,
    #[option(96)]
    pub harmonics: IntOption<HarmonicsParams>,
    #[option(80)]
    pub timbre: IntOption<TimbreParams>,
    #[option(128)]
    pub morph: IntOption<MorphParams>,
}

#[derive(OptionPage, Clone)]
pub struct VectorOpts {
    #[option]
    pub xscale: EnumOption<VScale>,
    #[option]
    pub yscale: EnumOption<VScale>,
}

#[derive(OptionPage, Clone)]
pub struct BeamOpts {
    #[option(15)]
    pub persist: IntOption<PersistParams>,
    #[option(8)]
    pub intensity: IntOption<IntensityParams>,
    #[option(10)]
    pub hue: IntOption<HueParams>,
    #[option]
    pub palette: EnumOption<ColorPalette>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts {
    #[option(VScale::Scale2V)]
    pub yscale: EnumOption<VScale>,
    #[option(Timebase::Timebase5ms)]
    pub timebase: EnumOption<Timebase>,
    #[option]
    pub trig_mode: EnumOption<TriggerMode>,
    #[option(512)]
    pub trig_lvl: IntOption<TriggerLvlParams>,
    #[option(-200)]
    pub ypos_out: IntOption<YPosParams>,
    #[option(200)]
    pub ypos_aux: IntOption<YPosParams>,
}

#[derive(Options, Clone)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Help)]
    pub help: HelpOpts,
    #[page(Page::Misc)]
    pub misc: MiscOpts,
    #[page(Page::Scope)]
    pub scope: ScopeOpts,
    #[page(Page::Osc)]
    pub osc: OscOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
    #[page(Page::Vector)]
    pub vector: VectorOpts,
}
