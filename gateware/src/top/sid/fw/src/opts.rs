use tiliqua_lib::opt::*;
use tiliqua_lib::impl_option_page;
use tiliqua_lib::impl_option_view;
use tiliqua_lib::num_option_config;
use strum_macros::{EnumIter, IntoStaticStr};

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Screen {
    Modulate,
    Voice1,
    Voice2,
    Voice3,
    Filter,
    Scope,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum TriggerMode {
    Always,
    Rising,
}

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum Wave {
    Triangle,
    Saw,
    Pulse,
    Noise,
}

// Define configs for different numeric ranges
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

#[derive(Clone)]
pub struct VoiceOptions {
    pub selected: Option<usize>,
    pub freq: NumOption<FrequencyConfig>,
    pub freq_os: NumOption<FreqOffsetConfig>,
    pub pw: NumOption<PulseWidthConfig>,
    pub wave: EnumOption<Wave>,
    pub gate: NumOption<BinaryConfig>,
    pub sync: NumOption<BinaryConfig>,
    pub ring: NumOption<BinaryConfig>,
    pub attack: NumOption<EnvelopeConfig>,
    pub decay: NumOption<EnvelopeConfig>,
    pub sustain: NumOption<EnvelopeConfig>,
    pub release: NumOption<EnvelopeConfig>,
}

impl VoiceOptions {
    fn new() -> Self {
        Self {
            selected: None,
            freq: NumOption::new("f-base", 1000),
            freq_os: NumOption::new("f-offs", 1000),
            pw: NumOption::new("pw", 2048),
            wave: EnumOption::new("wave", Wave::Triangle),
            gate: NumOption::new("gate", 1),
            sync: NumOption::new("sync", 0),
            ring: NumOption::new("ring", 0),
            attack: NumOption::new("attack", 0),
            decay: NumOption::new("decay", 0),
            sustain: NumOption::new("sustain", 15),
            release: NumOption::new("release", 0),
        }
    }
}

impl_option_view!(VoiceOptions,
                  freq, freq_os, pw, wave, gate, sync, ring,
                  attack, decay, sustain, release);

#[derive(Clone)]
pub struct FilterOptions {
    pub selected: Option<usize>,
    pub cutoff: NumOption<CutoffConfig>,
    pub reso: NumOption<EnvelopeConfig>,
    pub filt1: NumOption<BinaryConfig>,
    pub filt2: NumOption<BinaryConfig>,
    pub filt3: NumOption<BinaryConfig>,
    pub lp: NumOption<BinaryConfig>,
    pub bp: NumOption<BinaryConfig>,
    pub hp: NumOption<BinaryConfig>,
    pub v3off: NumOption<BinaryConfig>,
    pub volume: NumOption<VolumeConfig>,
}

impl FilterOptions {
    fn new() -> Self {
        Self {
            selected: None,
            cutoff: NumOption::new("cutoff", 1500),
            reso: NumOption::new("reso", 0),
            filt1: NumOption::new("filt1", 0),
            filt2: NumOption::new("filt2", 0),
            filt3: NumOption::new("filt3", 0),
            lp: NumOption::new("lp", 0),
            bp: NumOption::new("bp", 0),
            hp: NumOption::new("hp", 0),
            v3off: NumOption::new("3off", 0),
            volume: NumOption::new("volume", 15),
        }
    }
}

impl_option_view!(FilterOptions,
                  cutoff, reso, filt1, filt2, filt3,
                  lp, bp, hp, v3off, volume);

#[derive(Clone)]
pub struct ScopeOptions {
    pub selected: Option<usize>,
    pub timebase: NumOption<TimebaseConfig>,
    pub trigger_mode: EnumOption<TriggerMode>,
    pub trigger_lvl: NumOption<TriggerLevelConfig>,
    pub ypos0: NumOption<PositionConfig>,
    pub ypos1: NumOption<PositionConfig>,
    pub ypos2: NumOption<PositionConfig>,
    pub ypos3: NumOption<PositionConfig>,
    pub yscale: NumOption<ScaleConfig>,
    pub xscale: NumOption<ScaleConfig>,
    pub xpos: NumOption<PositionConfig>,
}

impl ScopeOptions {
    fn new() -> Self {
        Self {
            selected: None,
            timebase: NumOption::new("timebase", 32),
            trigger_mode: EnumOption::new("trig-mode", TriggerMode::Always),
            trigger_lvl: NumOption::new("trig-lvl", 0),
            ypos0: NumOption::new("ypos0", 150),
            ypos1: NumOption::new("ypos1", -150),
            ypos2: NumOption::new("ypos2", -50),
            ypos3: NumOption::new("ypos3", 50),
            yscale: NumOption::new("yscale", 8),
            xscale: NumOption::new("xscale", 7),
            xpos: NumOption::new("xpos", 175),
        }
    }
}

impl_option_view!(ScopeOptions,
                  timebase, trigger_mode, trigger_lvl,
                  ypos0, ypos1, ypos2, ypos3,
                  yscale, xscale, xpos);

#[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum ModulationTarget {
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

#[derive(Clone)]
pub struct ModulateOptions {
    pub selected: Option<usize>,
    pub in0: EnumOption<ModulationTarget>,
    pub in1: EnumOption<ModulationTarget>,
    pub in2: EnumOption<ModulationTarget>,
    pub in3: EnumOption<ModulationTarget>,
}

impl ModulateOptions {
    fn new() -> Self {
        Self {
            selected: None,
            in0: EnumOption::new("in0", ModulationTarget::Nothing),
            in1: EnumOption::new("in1", ModulationTarget::Nothing),
            in2: EnumOption::new("in2", ModulationTarget::Nothing),
            in3: EnumOption::new("in3", ModulationTarget::Nothing),
        }
    }
}

impl_option_view!(ModulateOptions, in0, in1, in2, in3);

#[derive(Clone)]
pub struct Options {
    pub modify: bool,
    pub screen: EnumOption<Screen>,
    pub modulate: ModulateOptions,
    pub voice1: VoiceOptions,
    pub voice2: VoiceOptions,
    pub voice3: VoiceOptions,
    pub filter: FilterOptions,
    pub scope: ScopeOptions,
}

impl_option_page!(Options,
                  (Screen::Modulate, modulate),
                  (Screen::Voice1, voice1),
                  (Screen::Voice2, voice2),
                  (Screen::Voice3, voice3),
                  (Screen::Filter, filter),
                  (Screen::Scope, scope));

impl Options {
    pub fn new() -> Options {
        Options {
            modify: false,
            screen: EnumOption::new("screen", Screen::Voice1),
            modulate: ModulateOptions::new(),
            voice1: VoiceOptions::new(),
            voice2: VoiceOptions::new(),
            voice3: VoiceOptions::new(),
            filter: FilterOptions::new(),
            scope: ScopeOptions::new(),
        }
    }
}
