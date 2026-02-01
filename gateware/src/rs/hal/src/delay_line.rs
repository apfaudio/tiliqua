pub trait DelayLine {
    fn size_samples(&self) -> usize;
    fn data_ptr(&self) -> *const i16;
    fn wrpointer(&self) -> usize;
}

#[macro_export]
macro_rules! impl_delay_line {
    ($(
        $DELAYX:ident: $PACDELAYX:ty,
    )+) => {
        $(
            pub struct $DELAYX {
                registers: $PACDELAYX,
                base: usize,
                size_samples: usize,
            }

            impl $DELAYX {
                pub fn new(registers: $PACDELAYX) -> Self {
                    let base = registers.base().read().base().bits() as usize;
                    let size_samples = registers.size().read().size_samples().bits() as usize;
                    Self { registers, base, size_samples }
                }
            }

            impl hal::delay_line::DelayLine for $DELAYX {

                fn size_samples(&self) -> usize {
                    self.size_samples
                }

                fn data_ptr(&self) -> *const i16 {
                    self.base as *const i16
                }

                fn wrpointer(&self) -> usize {
                    self.registers.wrpointer().read().bits() as usize
                }
            }
        )+
    };
}
