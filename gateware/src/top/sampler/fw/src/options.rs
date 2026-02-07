use opts::*;
use strum_macros::{EnumIter, IntoStaticStr};
use serde_derive::{Serialize, Deserialize};

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
pub enum Page {
    #[default]
    Help,
    Channel0,
    Channel1,
    Channel2,
}

impl Page {
    pub fn channel_index(&self) -> Option<usize> {
        match self {
            Page::Channel0 => Some(0),
            Page::Channel1 => Some(1),
            Page::Channel2 => Some(2),
            _ => None,
        }
    }
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum GateMode {
    #[default]
    TouchCV,
    On,
}

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum PlaybackMode {
    #[default]
    Gate,
    Oneshot,
    Loop,
    Bounce,
}

impl From<PlaybackMode> for tiliqua_hal::grain_player::PlaybackMode {
    fn from(mode: PlaybackMode) -> Self {
        match mode {
            PlaybackMode::Gate => Self::Gate,
            PlaybackMode::Oneshot => Self::Oneshot,
            PlaybackMode::Loop => Self::Loop,
            PlaybackMode::Bounce => Self::Bounce,
        }
    }
}

int_params!(ScrollParams<u8> { step: 1, min: 0, max: 60 });
int_params!(SpeedParams<u16> { step: 1, min: 32, max: 1024, format: IntFormat::Scaled { divisor: 256, precision: 2 } });
int_params!(LenParams<u32>     { step: 256, min: 0, max: 0x40000, format: IntFormat::Scaled { divisor: 48000, precision: 2 } });
int_params!(ZoomParams<u8>     { step: 1, min: 0, max: 4 });

button_params!(ToggleButtonParams { mode: ButtonMode::Toggle });

#[derive(OptionPage, Clone)]
pub struct HelpOpts {
    #[option(0)]
    pub scroll: IntOption<ScrollParams>,
}

#[derive(OptionPage, Clone)]
pub struct ChannelOpts {
    #[option(false)]
    pub record: ButtonOption<ToggleButtonParams>,
    #[option]
    pub gate: EnumOption<GateMode>,
    #[option]
    pub mode: EnumOption<PlaybackMode>,
    #[option(false)]
    pub reverse: ButtonOption<ToggleButtonParams>,
    #[option(0x100)]
    pub speed: IntOption<SpeedParams>,
    #[option(0)]
    pub zoom: IntOption<ZoomParams>,
    #[option(0xE800)]
    pub start: IntOption<LenParams>,
    #[option(0x23000)]
    pub len: IntOption<LenParams>,
}

#[derive(Options, Clone)]
pub struct Opts {
    pub tracker: ScreenTracker<Page>,
    #[page(Page::Help)]
    pub help: HelpOpts,
    #[page(Page::Channel0)]
    pub channel0: ChannelOpts,
    #[page(Page::Channel1)]
    pub channel1: ChannelOpts,
    #[page(Page::Channel2)]
    pub channel2: ChannelOpts,
}

impl Opts {
    pub fn channel_opts(&self, index: usize) -> &ChannelOpts {
        match index {
            0 => &self.channel0,
            1 => &self.channel1,
            2 => &self.channel2,
            _ => panic!("invalid channel index"),
        }
    }

    pub fn channel_opts_mut(&mut self, index: usize) -> &mut ChannelOpts {
        match index {
            0 => &mut self.channel0,
            1 => &mut self.channel1,
            2 => &mut self.channel2,
            _ => panic!("invalid channel index"),
        }
    }
}
