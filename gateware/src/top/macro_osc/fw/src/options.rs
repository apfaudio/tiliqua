use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use tiliqua_lib::palette::ColorPalette;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    Scope,
    #[default]
    Osc,
    Beam,
    Vector,
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
int_params!(XScaleParams<u8>      { step: 1, min: 0, max: 15 });
int_params!(YScaleParams<u8>      { step: 1, min: 0, max: 15 });
int_params!(PersistParams<u16>    { step: 128, min: 128, max: 8192 });
int_params!(DecayParams<u8>       { step: 1, min: 0, max: 15 });
int_params!(IntensityParams<u8>   { step: 1, min: 0, max: 15 });
int_params!(HueParams<u8>         { step: 1, min: 0, max: 15 });
int_params!(TimebaseParams<u16>   { step: 128, min: 32, max: 3872 });
int_params!(TriggerLvlParams<i16> { step: 512, min: -16384, max: 16384 });
int_params!(YPosParams<i16>       { step: 25, min: -500, max: 500 });

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
    #[option(6)]
    pub xscale: IntOption<XScaleParams>,
    #[option(6)]
    pub yscale: IntOption<YScaleParams>,
}

#[derive(OptionPage, Clone)]
pub struct BeamOpts {
    #[option(256)]
    pub persist: IntOption<PersistParams>,
    #[option(1)]
    pub decay: IntOption<DecayParams>,
    #[option(15)]
    pub intensity: IntOption<IntensityParams>,
    #[option(10)]
    pub hue: IntOption<HueParams>,
    #[option]
    pub palette: EnumOption<ColorPalette>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts {
    #[option(2048)]
    pub timebase: IntOption<TimebaseParams>,
    #[option]
    pub trig_mode: EnumOption<TriggerMode>,
    #[option(512)]
    pub trig_lvl: IntOption<TriggerLvlParams>,
    #[option(-200)]
    pub ypos0: IntOption<YPosParams>,
    #[option(200)]
    pub ypos1: IntOption<YPosParams>,
    #[option(500)]
    pub ypos2: IntOption<YPosParams>,
    #[option(500)]
    pub ypos3: IntOption<YPosParams>,
    #[option(7)]
    pub yscale: IntOption<YScaleParams>,
    #[option(6)]
    pub xscale: IntOption<XScaleParams>,
}

#[derive(Options, Clone, Default)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Scope)]
    pub scope: ScopeOpts,
    #[page(Page::Osc)]
    pub osc: OscOpts,
    #[page(Page::Beam)]
    pub beam: BeamOpts,
    #[page(Page::Vector)]
    pub vector: VectorOpts,
}
