pub trait Encoder {
    fn poke_ticks(&mut self) -> i8;
    fn poke_btn(&mut self) -> bool;
    fn poke_btn_held(&mut self) -> bool;
    fn update(&mut self);
}

#[macro_export]
macro_rules! impl_encoder {
    ($(
        $ENCODERX:ident: $PACENCODERX:ty,
    )+) => {
        $(
            #[derive(Debug)]
            pub struct $ENCODERX {
                registers: $PACENCODERX,

                rot: i16,
                lrot: i16,
                lbtn: bool,
                btn_held: u16,

                pending_ticks: i8,
                pending_release: bool,
                pending_press:   bool,

            }

            impl $ENCODERX {
                pub fn new(registers: $PACENCODERX) -> Self {
                    let btn = registers.button().read().bits() != 0;
                    Self { registers,
                           rot: 0,
                           lrot: 0,
                           lbtn: btn,
                           btn_held: 0,
                           pending_ticks: 0,
                           pending_release: false,
                           pending_press: false,
                    }
                }

            }

            impl hal::encoder::Encoder for $ENCODERX {
                /// Check for pending ticks and clear them.
                fn poke_ticks(&mut self) -> i8 {
                    let ticks = self.pending_ticks;
                    self.pending_ticks = 0;
                    ticks
                }

                /// Check for pending clicks and erase it.
                fn poke_btn(&mut self) -> bool {
                    let btn = self.pending_press && self.pending_release;
                    if btn {
                        self.pending_press = false;
                        self.pending_release = false;
                    }
                    btn
                }

                fn poke_btn_held(&mut self) -> bool {
                    if self.btn_held > 150 {
                        self.btn_held = 0;
                        true
                    } else {
                        false
                    }
                }

                fn update(&mut self) {

                    self.rot += (self.registers.step().read().bits() as i8) as i16;
                    let btn = self.registers.button().read().bits() != 0;
                    let mut delta_ticks = self.rot - self.lrot;

                    if btn {
                        self.btn_held += 1;
                    } else {
                        self.btn_held = 0;
                    }

                    // This logic is dumb. Move it into RTL.

                    while delta_ticks > 1 {
                        self.pending_ticks += 1;
                        delta_ticks -= 2;
                    }

                    while delta_ticks < -1 {
                        self.pending_ticks -= 1;
                        delta_ticks += 2;
                    }

                    // button just released
                    if self.lbtn != btn {
                        if btn {
                            self.pending_press = true;
                        } else {
                            self.pending_release = true;
                        }
                    }

                    self.lrot = self.rot - delta_ticks;
                    self.lbtn = btn;
                }
            }

            impl From<$PACENCODERX> for $ENCODERX {
                fn from(registers: $PACENCODERX) -> $ENCODERX {
                    $ENCODERX::new(registers)
                }
            }
        )+
    }
}
