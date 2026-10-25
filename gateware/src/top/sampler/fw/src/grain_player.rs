use crate::pac;

#[derive(Clone, Copy)]
pub enum PlaybackMode {
    Gate = 0,
    Oneshot = 1,
    Loop = 2,
    Bounce = 3,
    Scrub = 4,
}

pub trait GrainPlayer {
    fn set_params(&mut self, speed: u16, start: u32, length: u32);
    fn set_control(&mut self, mode: PlaybackMode, gate: bool, hw_gate_enable: bool, reverse: bool);
    fn position(&self) -> usize;
}

macro_rules! impl_grain_player {
    ($($PACGRAINX:ty),+) => {
        $(
            impl GrainPlayer for $PACGRAINX {
                fn set_params(&mut self, speed: u16, start: u32, length: u32) {
                    self.speed().write(|w| unsafe { w.speed().bits(speed) });
                    self.start().write(|w| unsafe { w.start().bits(start) });
                    self.length().write(|w| unsafe { w.length().bits(length) });
                }

                fn set_control(&mut self, mode: PlaybackMode, gate: bool, hw_gate_enable: bool, reverse: bool) {
                    self.control().write(|w| unsafe {
                        w.mode().bits(mode as u8);
                        w.gate().bit(gate);
                        w.hw_gate_enable().bit(hw_gate_enable);
                        w.reverse().bit(reverse)
                    });
                }

                fn position(&self) -> usize {
                    self.status().read().bits() as usize
                }
            }
        )+
    };
}

impl_grain_player!(pac::GRAIN_PERIPH0, pac::GRAIN_PERIPH1, pac::GRAIN_PERIPH2);

pub type GrainPlayer0 = pac::GRAIN_PERIPH0;
pub type GrainPlayer1 = pac::GRAIN_PERIPH1;
pub type GrainPlayer2 = pac::GRAIN_PERIPH2;
