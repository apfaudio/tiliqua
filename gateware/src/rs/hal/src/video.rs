pub trait Video {
    fn set_persist(&mut self, value: u16);
    fn set_decay(&mut self, value: u8);
}

#[macro_export]
macro_rules! impl_video {
    ($(
        $VIDEOX:ident: $PACVIDEOX:ty,
    )+) => {
        $(
            #[derive(Debug)]
            pub struct $VIDEOX {
                registers: $PACVIDEOX,
            }

            impl $VIDEOX {
                pub fn new(registers: $PACVIDEOX) -> Self {
                    Self { registers }
                }
            }

            impl hal::video::Video for $VIDEOX {
                fn set_persist(&mut self, value: u16)  {
                    self.registers.persist().write(|w| unsafe { w.persist().bits(value) } );
                }

                fn set_decay(&mut self, value: u8)  {
                    self.registers.decay().write(|w| unsafe { w.decay().bits(value) } );
                }

            }
        )+
    };
}
