use crate::pac;

pub trait DelayLine {
    fn size_samples(&self) -> usize;
    fn data_ptr(&self) -> *const i16;
    fn wrpointer(&self) -> usize;
}

pub struct DelayLine0 {
    registers: pac::DELAYLN_PERIPH0,
    base: usize,
    size_samples: usize,
}

impl DelayLine0 {
    pub fn new(registers: pac::DELAYLN_PERIPH0) -> Self {
        let base = registers.base().read().base().bits() as usize;
        let size_samples = registers.size().read().size_samples().bits() as usize;
        Self { registers, base, size_samples }
    }
}

impl DelayLine for DelayLine0 {

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
