#[derive(Clone, Copy)]
pub enum PlaybackMode {
    Gate = 0,
    Oneshot = 1,
    Loop = 2,
    Bounce = 3,
}

pub trait GrainPlayer {
    fn set_params(&mut self, speed: u16, start: u32, length: u32);
    fn set_control(&mut self, mode: PlaybackMode, gate: bool, hw_gate_enable: bool, reverse: bool);
    fn position(&self) -> usize;
}

#[macro_export]
macro_rules! impl_grain_player {
    ($(
        $GRAINX:ident: $PACGRAINX:ty,
    )+) => {
        $(
            pub struct $GRAINX {
                registers: $PACGRAINX,
            }

            impl $GRAINX {
                pub fn new(registers: $PACGRAINX) -> Self {
                    Self { registers }
                }
            }

            impl hal::grain_player::GrainPlayer for $GRAINX {
                fn set_params(&mut self, speed: u16, start: u32, length: u32) {
                    self.registers.speed().write(|w| unsafe { w.speed().bits(speed) });
                    self.registers.start().write(|w| unsafe { w.start().bits(start) });
                    self.registers.length().write(|w| unsafe { w.length().bits(length) });
                }

                fn set_control(&mut self, mode: hal::grain_player::PlaybackMode, gate: bool, hw_gate_enable: bool, reverse: bool) {
                    self.registers.control().write(|w| unsafe {
                        w.mode().bits(mode as u8);
                        w.gate().bit(gate);
                        w.hw_gate_enable().bit(hw_gate_enable);
                        w.reverse().bit(reverse)
                    });
                }

                fn position(&self) -> usize {
                    self.registers.status().read().bits() as usize
                }
            }
        )+
    };
}
