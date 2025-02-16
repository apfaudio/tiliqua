use tiliqua_lib::opt::*;
use tiliqua_lib::num_option_config;
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


num_option_config!(FrequencyConfig: u16 => 125, 0, 65500);
num_option_config!(FreqOffsetConfig: u16 => 10, 500, 2000);
num_option_config!(PulseWidthConfig: u16 => 128, 0, 4096);
num_option_config!(EnvelopeConfig: u8 => 1, 0, 15);
num_option_config!(BinaryConfig: u8 => 1, 0, 1);
num_option_config!(CutoffConfig: u16 => 100, 0, 2000);
num_option_config!(VolumeConfig: u8 => 1, 0, 15);
num_option_config!(TimebaseConfig: u16 => 128, 32, 3872);
num_option_config!(TriggerLevelConfig: i16 => 512, -16384, 16384);
num_option_config!(PositionConfig: i16 => 25, -500, 500);
num_option_config!(ScaleConfig: u8 => 1, 0, 15);

#[derive(OptionSet, Clone)]
pub struct VoiceOptions {
    #[option(1000)]
    pub freq: NumOption<FrequencyConfig>,
    #[option(1000)]
    pub freq_os: NumOption<FreqOffsetConfig>,
    #[option(2048)]
    pub pw: NumOption<PulseWidthConfig>,
    #[option(Wave::Triangle)]
    pub wave: EnumOption<Wave>,
    #[option(1)]
    pub gate: NumOption<BinaryConfig>,
    #[option(0)]
    pub sync: NumOption<BinaryConfig>,
    #[option(0)]
    pub ring: NumOption<BinaryConfig>,
    #[option(0)]
    pub attack: NumOption<EnvelopeConfig>,
    #[option(0)]
    pub decay: NumOption<EnvelopeConfig>,
    #[option(15)]
    pub sustain: NumOption<EnvelopeConfig>,
    #[option(0)]
    pub release: NumOption<EnvelopeConfig>,
}

#[derive(OptionSet, Clone)]
pub struct FilterOptions {
    #[option(1500)]
    pub cutoff: NumOption<CutoffConfig>,
    #[option(0)]
    pub reso: NumOption<EnvelopeConfig>,
    #[option(0)]
    pub filt1: NumOption<BinaryConfig>,
    #[option(0)]
    pub filt2: NumOption<BinaryConfig>,
    #[option(0)]
    pub filt3: NumOption<BinaryConfig>,
    #[option(0)]
    pub lp: NumOption<BinaryConfig>,
    #[option(0)]
    pub bp: NumOption<BinaryConfig>,
    #[option(0)]
    pub hp: NumOption<BinaryConfig>,
    #[option(0)]
    pub v3off: NumOption<BinaryConfig>,
    #[option(15)]
    pub volume: NumOption<VolumeConfig>,
}

#[derive(OptionSet, Clone)]
pub struct ScopeOptions {
    #[option(32)]
    pub timebase: NumOption<TimebaseConfig>,
    #[option(TriggerMode::Always)]
    pub trigger_mode: EnumOption<TriggerMode>,
    #[option(0)]
    pub trigger_lvl: NumOption<TriggerLevelConfig>,
    #[option(150)]
    pub ypos0: NumOption<PositionConfig>,
    #[option(-150)]
    pub ypos1: NumOption<PositionConfig>,
    #[option(-50)]
    pub ypos2: NumOption<PositionConfig>,
    #[option(50)]
    pub ypos3: NumOption<PositionConfig>,
    #[option(8)]
    pub yscale: NumOption<ScaleConfig>,
    #[option(7)]
    pub xscale: NumOption<ScaleConfig>,
    #[option(175)]
    pub xpos: NumOption<PositionConfig>,
}

#[derive(OptionSet, Clone)]
pub struct ModulateOptions {
    #[option(ModulationTarget::Nothing)]
    pub in0: EnumOption<ModulationTarget>,
    #[option(ModulationTarget::Nothing)]
    pub in1: EnumOption<ModulationTarget>,
    #[option(ModulationTarget::Nothing)]
    pub in2: EnumOption<ModulationTarget>,
    #[option(ModulationTarget::Nothing)]
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
