#[macro_export]
macro_rules! impl_polysynth {
    ($(
        $POLYSYNTHX:ident: $PACPOLYSYNTHX:ty,
        $N_VOICES: expr
    )+) => {
        $(
            #[derive(Debug)]
            pub struct $POLYSYNTHX {
                registers: $PACPOLYSYNTHX,
            }

            impl $POLYSYNTHX {
                pub fn new(registers: $PACPOLYSYNTHX) -> Self {
                    Self { registers }
                }
            }

            impl $POLYSYNTHX {

                pub fn voice_notes(&self) -> [u8; $N_VOICES] {
                    [
                        self.registers.voices0().read().note().bits(),
                        self.registers.voices1().read().note().bits(),
                        self.registers.voices2().read().note().bits(),
                        self.registers.voices3().read().note().bits(),
                        self.registers.voices4().read().note().bits(),
                        self.registers.voices5().read().note().bits(),
                        self.registers.voices6().read().note().bits(),
                        self.registers.voices7().read().note().bits(),
                        // TODO: proper register block. Add them yourself :)
                    ]
                }

                pub fn voice_cutoffs(&self) -> [u8; $N_VOICES] {
                    [
                        self.registers.voices0().read().cutoff().bits(),
                        self.registers.voices1().read().cutoff().bits(),
                        self.registers.voices2().read().cutoff().bits(),
                        self.registers.voices3().read().cutoff().bits(),
                        self.registers.voices4().read().cutoff().bits(),
                        self.registers.voices5().read().cutoff().bits(),
                        self.registers.voices6().read().cutoff().bits(),
                        self.registers.voices7().read().cutoff().bits(),
                        // TODO: proper register block. Add them yourself :)
                    ]
                }

                pub fn set_matrix_coefficient(&mut self, o_x: u32, i_y: u32, value: i32)  {
                    // TODO: statically verify x_o, y_i both < 16. Should be true for any normal use case
                    // as matrices larger than this won't be able to process things at audio rate.
                    while self.registers.matrix_busy().read().bits() == 1 { /* wait until last coeff written */ }
                    self.registers.matrix().write(|w| unsafe {
                        w.o_x().bits(o_x as u8);
                        w.i_y().bits(i_y as u8);
                        w.value().bits(value as u32 & 0x00FFFFFF)
                    } );
                }

                pub fn set_drive(&mut self, value: u16)  {
                    self.registers.drive().write(|w| unsafe { w.value().bits(value) } );
                }

                pub fn set_reso(&mut self, value: u16)  {
                    self.registers.reso().write(|w| unsafe { w.value().bits(value) } );
                }

                pub fn midi_write(&mut self, value: u32)  {
                    self.registers.midi_write().write(|w| unsafe { w.msg().bits(value) } );
                }

                pub fn midi_read(&mut self) -> u32  {
                    self.registers.midi_read().read().bits()
                }

                pub fn usb_midi_host(&mut self, enable: bool, cfg_id: u8, endpt_id: u8)  {
                    self.registers.usb_midi_host().write(|w| unsafe { w.host().bit(enable) } );
                    self.registers.usb_midi_cfg().write(|w| unsafe { w.value().bits(cfg_id) } );
                    self.registers.usb_midi_endp().write(|w| unsafe { w.value().bits(endpt_id) } );
                }
            }
        )+
    };
}
