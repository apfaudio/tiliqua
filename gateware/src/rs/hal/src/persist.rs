pub trait Persist {
    fn set_persist(&mut self, value: u16);
    fn set_decay(&mut self, value: u8);
}

#[macro_export]
macro_rules! impl_persist {
    ($(
        $PERSISTX:ident: $PACPERSISTX:ty,
    )+) => {
        $(
            #[derive(Debug)]
            pub struct $PERSISTX {
                registers: $PACPERSISTX,
            }

            impl $PERSISTX {
                pub fn new(registers: $PACPERSISTX) -> Self {
                    Self { registers }
                }
            }

            impl hal::persist::Persist for $PERSISTX {
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
