use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    Modulate,
    #[default]
    Voice1,
    Voice2,
    Voice3,
    Filter,
    Scope,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
#[strum(serialize_all = "kebab-case")]
pub enum TriggerMode {
    Always,
    #[default]
    Rising,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
#[strum(serialize_all = "kebab-case")]
pub enum Wave {
    #[default]
    Triangle,
    Saw,
    Pulse,
    Noise,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
#[strum(serialize_all = "kebab-case")]
pub enum ModulationTarget {
    #[default]
    Nothing,
    Freq1,
    Freq2,
    Freq3,
    Freq12,
    Gate1,
    Gate2,
    Gate3,
    Gate12,
}

pub enum VoiceModulationType {
    Frequency,
    Gate
}

impl ModulationTarget {
    pub fn modulates_voice(&self, n: usize) -> Option<VoiceModulationType> {
        use ModulationTarget::*;
        use VoiceModulationType::*;
        match (n, *self) {
            (0, Freq1)  => Some(Frequency),
            (1, Freq2)  => Some(Frequency),
            (2, Freq3)  => Some(Frequency),
            (0, Freq12) => Some(Frequency),
            (1, Freq12) => Some(Frequency),
            (0, Gate1)  => Some(Gate),
            (1, Gate2)  => Some(Gate),
            (2, Gate3)  => Some(Gate),
            (0, Gate12) => Some(Gate),
            (1, Gate12) => Some(Gate),
            _ =>          None
        }
    }
}


int_params!(FrequencyParams<u16>    { step: 125, min: 0,      max: 65500 });
int_params!(FreqOffsetParams<u16>   { step: 10,  min: 500,    max: 2000 });
int_params!(PulseWidthParams<u16>   { step: 128, min: 0,      max: 4096 });
int_params!(EnvelopeParams<u8>      { step: 1,   min: 0,      max: 15 });
int_params!(BinaryParams<u8>        { step: 1,   min: 0,      max: 1 });
int_params!(CutoffParams<u16>       { step: 100, min: 0,      max: 2000 });
int_params!(VolumeParams<u8>        { step: 1,   min: 0,      max: 15 });
int_params!(TimebaseParams<u16>     { step: 128, min: 32,     max: 3872 });
int_params!(TriggerLevelParams<i16> { step: 512, min: -16384, max: 16384 });
int_params!(PositionParams<i16>     { step: 25,  min: -500,   max: 500 });
int_params!(ScaleParams<u8>         { step: 1,   min: 0,      max: 15 });

#[derive(OptionPage, Clone)]
pub struct VoiceOpts {
    #[option(1000)]
    pub freq: IntOption<FrequencyParams>,
    #[option(1000)]
    pub freq_os: IntOption<FreqOffsetParams>,
    #[option(2048)]
    pub pw: IntOption<PulseWidthParams>,
    #[option]
    pub wave: EnumOption<Wave>,
    #[option(1)]
    pub gate: IntOption<BinaryParams>,
    #[option]
    pub sync: IntOption<BinaryParams>,
    #[option]
    pub ring: IntOption<BinaryParams>,
    #[option]
    pub attack: IntOption<EnvelopeParams>,
    #[option]
    pub decay: IntOption<EnvelopeParams>,
    #[option(15)]
    pub sustain: IntOption<EnvelopeParams>,
    #[option]
    pub release: IntOption<EnvelopeParams>,
}

#[derive(OptionPage, Clone)]
pub struct FilterOpts {
    #[option(1500)]
    pub cutoff: IntOption<CutoffParams>,
    #[option]
    pub reso: IntOption<EnvelopeParams>,
    #[option]
    pub filt1: IntOption<BinaryParams>,
    #[option]
    pub filt2: IntOption<BinaryParams>,
    #[option]
    pub filt3: IntOption<BinaryParams>,
    #[option]
    pub lp: IntOption<BinaryParams>,
    #[option]
    pub bp: IntOption<BinaryParams>,
    #[option]
    pub hp: IntOption<BinaryParams>,
    #[option]
    pub v3off: IntOption<BinaryParams>,
    #[option(15)]
    pub volume: IntOption<VolumeParams>,
}

#[derive(OptionPage, Clone)]
pub struct ScopeOpts {
    #[option(1056)]
    pub timebase: IntOption<TimebaseParams>,
    #[option]
    pub trig_mode: EnumOption<TriggerMode>,
    #[option]
    pub trig_lvl: IntOption<TriggerLevelParams>,
    #[option(150)]
    pub ypos0: IntOption<PositionParams>,
    #[option(-150)]
    pub ypos1: IntOption<PositionParams>,
    #[option(-50)]
    pub ypos2: IntOption<PositionParams>,
    #[option(50)]
    pub ypos3: IntOption<PositionParams>,
    #[option(8)]
    pub yscale: IntOption<ScaleParams>,
    #[option(7)]
    pub xscale: IntOption<ScaleParams>,
    #[option(175)]
    pub xpos: IntOption<PositionParams>,
}

#[derive(OptionPage, Clone)]
pub struct ModulateOpts {
    #[option]
    pub in0: EnumOption<ModulationTarget>,
    #[option]
    pub in1: EnumOption<ModulationTarget>,
    #[option]
    pub in2: EnumOption<ModulationTarget>,
    #[option]
    pub in3: EnumOption<ModulationTarget>,
}

#[derive(Options, Clone, Default)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Modulate)]
    pub modulate: ModulateOpts,
    #[page(Page::Voice1)]
    pub voice1: VoiceOpts,
    #[page(Page::Voice2)]
    pub voice2: VoiceOpts,
    #[page(Page::Voice3)]
    pub voice3: VoiceOpts,
    #[page(Page::Filter)]
    pub filter: FilterOpts,
    #[page(Page::Scope)]
    pub scope: ScopeOpts,
}
