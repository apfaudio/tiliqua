use tiliqua_lib::opt::*;
use tiliqua_lib::num_params;
use strum_macros::{EnumIter, IntoStaticStr};
use opts_macro::{OptionMenu, OptionSet};

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Default)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Screen {
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
    #[default]
    Always,
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


num_params!(FrequencyParams<u16>    { step: 125, min: 0,      max: 65500 });
num_params!(FreqOffsetParams<u16>   { step: 10,  min: 500,    max: 2000 });
num_params!(PulseWidthParams<u16>   { step: 128, min: 0,      max: 4096 });
num_params!(EnvelopeParams<u8>      { step: 1,   min: 0,      max: 15 });
num_params!(BinaryParams<u8>        { step: 1,   min: 0,      max: 1 });
num_params!(CutoffParams<u16>       { step: 100, min: 0,      max: 2000 });
num_params!(VolumeParams<u8>        { step: 1,   min: 0,      max: 15 });
num_params!(TimebaseParams<u16>     { step: 128, min: 32,     max: 3872 });
num_params!(TriggerLevelParams<i16> { step: 512, min: -16384, max: 16384 });
num_params!(PositionParams<i16>     { step: 25,  min: -500,   max: 500 });
num_params!(ScaleParams<u8>         { step: 1,   min: 0,      max: 15 });

#[derive(OptionSet, Clone)]
pub struct VoiceOptions {
    #[option(1000)]
    pub freq: NumOption<FrequencyParams>,
    #[option(1000)]
    pub freq_os: NumOption<FreqOffsetParams>,
    #[option(2048)]
    pub pw: NumOption<PulseWidthParams>,
    #[option]
    pub wave: EnumOption<Wave>,
    #[option(1)]
    pub gate: NumOption<BinaryParams>,
    #[option]
    pub sync: NumOption<BinaryParams>,
    #[option]
    pub ring: NumOption<BinaryParams>,
    #[option]
    pub attack: NumOption<EnvelopeParams>,
    #[option]
    pub decay: NumOption<EnvelopeParams>,
    #[option(15)]
    pub sustain: NumOption<EnvelopeParams>,
    #[option]
    pub release: NumOption<EnvelopeParams>,
}

#[derive(OptionSet, Clone)]
pub struct FilterOptions {
    #[option(1500)]
    pub cutoff: NumOption<CutoffParams>,
    #[option]
    pub reso: NumOption<EnvelopeParams>,
    #[option]
    pub filt1: NumOption<BinaryParams>,
    #[option]
    pub filt2: NumOption<BinaryParams>,
    #[option]
    pub filt3: NumOption<BinaryParams>,
    #[option]
    pub lp: NumOption<BinaryParams>,
    #[option]
    pub bp: NumOption<BinaryParams>,
    #[option]
    pub hp: NumOption<BinaryParams>,
    #[option]
    pub v3off: NumOption<BinaryParams>,
    #[option(15)]
    pub volume: NumOption<VolumeParams>,
}

#[derive(OptionSet, Clone)]
pub struct ScopeOptions {
    #[option(32)]
    pub timebase: NumOption<TimebaseParams>,
    #[option]
    pub trigger_mode: EnumOption<TriggerMode>,
    #[option]
    pub trigger_lvl: NumOption<TriggerLevelParams>,
    #[option(150)]
    pub ypos0: NumOption<PositionParams>,
    #[option(-150)]
    pub ypos1: NumOption<PositionParams>,
    #[option(-50)]
    pub ypos2: NumOption<PositionParams>,
    #[option(50)]
    pub ypos3: NumOption<PositionParams>,
    #[option(8)]
    pub yscale: NumOption<ScaleParams>,
    #[option(7)]
    pub xscale: NumOption<ScaleParams>,
    #[option(175)]
    pub xpos: NumOption<PositionParams>,
}

#[derive(OptionSet, Clone)]
pub struct ModulateOptions {
    #[option]
    pub in0: EnumOption<ModulationTarget>,
    #[option]
    pub in1: EnumOption<ModulationTarget>,
    #[option]
    pub in2: EnumOption<ModulationTarget>,
    #[option]
    pub in3: EnumOption<ModulationTarget>,
}


#[derive(OptionMenu, Clone, Default)]
pub struct Options {
    pub tracker: ScreenTracker<Screen>,
    #[option_menu(Screen::Modulate)]
    pub modulate: ModulateOptions,
    #[option_menu(Screen::Voice1)]
    pub voice1: VoiceOptions,
    #[option_menu(Screen::Voice2)]
    pub voice2: VoiceOptions,
    #[option_menu(Screen::Voice3)]
    pub voice3: VoiceOptions,
    #[option_menu(Screen::Filter)]
    pub filter: FilterOptions,
    #[option_menu(Screen::Scope)]
    pub scope: ScopeOptions,
}
