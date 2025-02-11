pub trait EurorackPmod {
    fn jack(&self) -> u8;
    fn touch_err(&self) -> u8;
    fn touch(&self) -> [u8; 8];
    fn sample_i(&self) -> [i16; 4];
    fn led_set_manual(&mut self, index: usize, value: i8);
    fn led_set_auto(&mut self, index: usize);
    fn led_all_auto(&mut self);
    fn led_all_manual(&mut self);
    fn write_calibration_constant(&mut self, ch: u8, a: i32, b: i32);
}

#[macro_export]
macro_rules! impl_eurorack_pmod {
    ($(
        $PMODX:ident: $PACPMODX:ty,
    )+) => {
        $(
            #[derive(Debug)]
            pub struct $PMODX {
                pub registers: $PACPMODX,
                led_mode: u8,
            }

            impl $PMODX {
                pub fn new(registers: $PACPMODX) -> Self {
                    Self { registers, led_mode: 0xff }
                }
            }

            impl hal::pmod::EurorackPmod for $PMODX {

                fn jack(&self) -> u8 {
                    self.registers.jack().read().bits() as u8
                }

                fn touch_err(&self) -> u8 {
                    self.registers.touch_err().read().bits() as u8
                }

                fn touch(&self) -> [u8; 8] {
                    [
                        self.registers.touch0().read().bits() as u8,
                        self.registers.touch1().read().bits() as u8,
                        self.registers.touch2().read().bits() as u8,
                        self.registers.touch3().read().bits() as u8,
                        self.registers.touch4().read().bits() as u8,
                        self.registers.touch5().read().bits() as u8,
                        self.registers.touch6().read().bits() as u8,
                        self.registers.touch7().read().bits() as u8,
                    ]
                }

                fn sample_i(&self) -> [i16; 4] {
                    [
                        self.registers.sample_i0().read().bits() as i16,
                        self.registers.sample_i1().read().bits() as i16,
                        self.registers.sample_i2().read().bits() as i16,
                        self.registers.sample_i3().read().bits() as i16,
                    ]
                }

                fn led_set_manual(&mut self, index: usize, value: i8)  {

                    match index {
                        0 => self.registers.led0().write(|w| unsafe { w.led().bits(value as u8) } ),
                        1 => self.registers.led1().write(|w| unsafe { w.led().bits(value as u8) } ),
                        2 => self.registers.led2().write(|w| unsafe { w.led().bits(value as u8) } ),
                        3 => self.registers.led3().write(|w| unsafe { w.led().bits(value as u8) } ),
                        4 => self.registers.led4().write(|w| unsafe { w.led().bits(value as u8) } ),
                        5 => self.registers.led5().write(|w| unsafe { w.led().bits(value as u8) } ),
                        6 => self.registers.led6().write(|w| unsafe { w.led().bits(value as u8) } ),
                        7 => self.registers.led7().write(|w| unsafe { w.led().bits(value as u8) } ),
                        _ => panic!("bad index")
                    };

                    self.led_mode &= !(1 << index);
                    self.registers.led_mode().write(|w| unsafe { w.led().bits(self.led_mode) } );
                }

                fn led_set_auto(&mut self, index: usize)  {

                    if index > 7 {
                        panic!("bad index");
                    }

                    self.led_mode |= 1 << index;
                    self.registers.led_mode().write(|w| unsafe { w.led().bits(self.led_mode) } );
                }

                fn led_all_auto(&mut self)  {
                    self.led_mode = 0xff;
                    self.registers.led_mode().write(|w| unsafe { w.led().bits(self.led_mode) } );
                }

                fn led_all_manual(&mut self)  {
                    self.led_mode = 0xff;
                    self.registers.led_mode().write(|w| unsafe { w.led().bits(self.led_mode) } );
                }

                fn write_calibration_constant(&mut self, ch: u8, a: i32, b: i32) {
                    self.registers.cal_a().write(|w| unsafe { w.value().bits(a as u32) });
                    self.registers.cal_b().write(|w| unsafe { w.value().bits(b as u32) });
                    self.registers.cal_reg().write(|w| unsafe {
                        w.write().bit(true);
                        w.channel().bits(ch)
                    });
                    while !self.registers.cal_reg().read().done().bit() {}
                }
            }
        )+
    };
}
