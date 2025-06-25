use log::info;
use embedded_hal::i2c::I2c;
use embedded_hal::i2c::Operation;
use tiliqua_hal::pmod::EurorackPmod;

pub const EEPROM_ADDR: u8 = 0x52;

use heapless::String;
use core::fmt::Write;

#[derive(Debug, PartialEq)]
pub struct CalibrationConstants {
    pub adc_scale: [i32; 4],
    pub adc_zero:  [i32; 4],
    pub dac_scale: [i32; 4],
    pub dac_zero:  [i32; 4],
    checksum:  i32,
}

// These are the calibration constants with a transformation
// applied to make them easier to tweak both in the UI and by
// auto calibration. Both inputs and outputs have the form
// Ax+B, however on the ADC side, this means that scale tweaking
// performed after zero tweaking invalidates previous zero
// tweaking. A linear transformation is performed on all calibration
// constants to achieve the following:
//
//  - Default settings are centered at zero (i.e. zero for all numbers
//    in this struct represents a 'default calibration')
//  - ADC Ax+B is transformed so that we are tweaking 'gamma' and 'delta',
//    where gamma is 1/A and delta is B/A, such that changing gamma (new
//    scale mapping) does not invalidate a previous ADC zeroing operation.
//
// These numbers are what is shown in the tweakable ADC/DAC calibration screen
// as they are much easier to tweak by hand compared to the raw cal constants.
#[derive(Debug)]
pub struct TweakableConstants {
    pub adc_scale: [i16; 4],
    pub adc_zero:  [i16; 4],
    pub dac_scale: [i16; 4],
    pub dac_zero:  [i16; 4],
}

pub fn fx18tof32(x: i32) -> f32 {
    (x as f32) / 32768.0f32
}

pub fn f32tofx18(x: f32) -> i32 {
    (x * 32768.0f32) as i32
}

impl CalibrationConstants {
    pub fn default() -> Self {
        let adc_dscale = -40894i32;
        let adc_dzero  = 0i32;
        let dac_dscale = 29491i32;
        let dac_dzero  = 0i32;
        let mut result = Self {
            adc_scale: [adc_dscale; 4],
            adc_zero:  [adc_dzero;  4],
            dac_scale: [dac_dscale; 4],
            dac_zero:  [dac_dzero;  4],
            checksum:  0i32,
        };
        result.checksum = result.compute_checksum();
        result
    }

    fn compute_checksum(&self) -> i32 {
        let mut sum = 0i32;
        for n in 0..4 {
            sum += self.adc_scale[n] + self.adc_zero[n] +
                   self.dac_scale[n] + self.dac_zero[n];
        }
        // Seed checksum, so all zeros doesn't look OK.
        sum + 0xdeadi32
    }

    pub fn write_to_pmod<Pmod>(&self, pmod: &mut Pmod)
    where
        Pmod: EurorackPmod
    {
        for ch in 0..4usize {
            pmod.write_calibration_constant(
                ch as u8,
                self.adc_scale[ch],
                self.adc_zero[ch],
            );
            pmod.write_calibration_constant(
                (ch+4) as u8,
                self.dac_scale[ch],
                self.dac_zero[ch],
            );
        }
    }

    pub fn from_eeprom<EepromI2c>(i2cdev: &mut EepromI2c) -> Option<Self>
    where
        EepromI2c: I2c
    {
        let mut constants = [0i32; 8*2+1];
        for n in 0..constants.len() {
            let mut rx_bytes = [0u8; 4];
            i2cdev.transaction(EEPROM_ADDR, &mut [Operation::Write(&[(n*4) as u8]),
                                                  Operation::Read(&mut rx_bytes)]).ok();
            constants[n] = i32::from_le_bytes(rx_bytes);
        }

        let mut result = Self {
            adc_scale: [0i32; 4],
            adc_zero:  [0i32; 4],
            dac_scale: [0i32; 4],
            dac_zero:  [0i32; 4],
            checksum:  0i32,
        };

        for ch in 0..4usize {
            result.adc_scale[ch] = constants[2*ch+0];
            result.adc_zero[ch]  = constants[2*ch+1];
            result.dac_scale[ch] = constants[2*ch+8+0];
            result.dac_zero[ch]  = constants[2*ch+8+1];
        }

        result.checksum = constants[constants.len()-1];
        if result.compute_checksum() == result.checksum {
            Some(result)
        } else {
            None
        }
    }

    pub fn load_or_default<EepromI2c, Pmod>(i2cdev: &mut EepromI2c, pmod: &mut Pmod)
    where
        EepromI2c: I2c,
        Pmod: EurorackPmod
    {
        if let Some(cal_constants) = Self::from_eeprom(i2cdev) {
            info!("calibration: looks good!");
            cal_constants.write_to_pmod(pmod);
        } else {
            info!("calibration: invalid! falling back to default");
            CalibrationConstants::default().write_to_pmod(pmod);
        }
    }

    pub fn write_to_eeprom<EepromI2c>(&self, i2cdev: &mut EepromI2c)
    where
        EepromI2c: I2c
    {
        // Print the calibration constants in amaranth-friendly format.
        let mut s: String<256> = String::new();
        write!(s, "[\n\r").ok();
        for ch in 0..4 {
            write!(s, "  [{:.4}, {:.4}],\n\r",
                   fx18tof32(self.adc_scale[ch as usize]),
                   fx18tof32(self.adc_zero[ch as usize])).ok();
        }
        for ch in 0..4 {
            write!(s, "  [{:.4}, {:.4}],\n\r",
                   fx18tof32(self.dac_scale[ch as usize]),
                   fx18tof32(self.dac_zero[ch as usize])).ok();
        }
        write!(s, "]\n\r").ok();
        info!("[write to eeprom] cal_constants = {}", s);
        // Commit to eeprom
        let mut constants = [0i32; 8*2+1];
        for ch in 0..4usize {
            constants[2*ch+0]   = self.adc_scale[ch];
            constants[2*ch+1]   = self.adc_zero[ch];
            constants[2*ch+8+0] = self.dac_scale[ch];
            constants[2*ch+8+1] = self.dac_zero[ch];
        }
        constants[constants.len()-1] = self.compute_checksum();
        for n in 0..constants.len() {
            let mut tx_bytes = [0u8; 5];
            tx_bytes[0] = (4*n) as u8; // 4 bytes storage per constant
            tx_bytes[1..5].clone_from_slice(&constants[n].to_le_bytes());
            loop {
                // TODO: add timeouts!
                match i2cdev.transaction(EEPROM_ADDR, &mut [Operation::Write(&tx_bytes)]) {
                    Ok(_) => break,
                    _ => {}
                }
            }
        }
        info!("[write to eeprom] complete");
    }

    // See comment on 'TweakableConstants' for the purpose of this.
    fn adc_default_gamma_delta() -> (f32, f32) {
        let defaults = Self::default();
        let adc_gamma_default  = 1.0f32/fx18tof32(defaults.adc_scale[0]);
        let adc_delta_default  = -fx18tof32(defaults.adc_zero[0])*adc_gamma_default;
        (adc_gamma_default, adc_delta_default)
    }

    pub fn from_tweakable(c: TweakableConstants) -> Self {
        let defaults   = Self::default();
        let mut result = Self::default();
        // DAC
        for ch in 0..4usize {
            result.dac_scale[ch] = defaults.dac_scale[0] + 4*c.dac_scale[ch] as i32;
            result.dac_zero[ch]  = defaults.dac_zero[0]  + 2*c.dac_zero[ch] as i32; // FIXME 2x/4x
        }
        // ADC
        let (adc_gd, adc_dd) = CalibrationConstants::adc_default_gamma_delta();
        for ch in 0..4usize {
            let adc_gamma      = adc_gd + 0.00010*(c.adc_scale[ch] as f32);
            let adc_delta      = adc_dd + 0.00005*(c.adc_zero[ch] as f32);
            result.adc_scale[ch] = f32tofx18(1.0f32/adc_gamma);
            result.adc_zero[ch]  = f32tofx18(-adc_delta/adc_gamma);
        }
        result
    }

    pub fn to_tweakable(&self) -> TweakableConstants {
        let mut adc_scale = [0i16; 4];
        let mut adc_zero  = [0i16; 4];
        let mut dac_scale = [0i16; 4];
        let mut dac_zero  = [0i16; 4];
        let defaults = Self::default();
        let (adc_gd, adc_dd) = CalibrationConstants::adc_default_gamma_delta();
        for ch in 0..4usize {
            let adc_gamma = 1.0f32/fx18tof32(self.adc_scale[ch]);
            adc_scale[ch] = ((adc_gamma - adc_gd) / 0.00010) as i16;
            let adc_delta = -fx18tof32(self.adc_zero[ch])*adc_gamma;
            adc_zero[ch]  = ((adc_delta - adc_dd) / 0.00005) as i16;
            dac_scale[ch] = ((self.dac_scale[ch] - defaults.dac_scale[0]) / 4) as i16;
            dac_zero[ch]  = ((self.dac_zero[ch]  -  defaults.dac_zero[0]) / 2) as i16;
        }
        TweakableConstants {
            adc_scale,
            adc_zero,
            dac_scale,
            dac_zero,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    pub fn tweakable_conversion() {
        // Verify TweakableConstants transformation reverses correctly.
        let mut defaults = CalibrationConstants::default();
        defaults.adc_scale[0] += 500;
        defaults.adc_zero[0]  += 250;
        defaults.dac_scale[0] -= 100;
        defaults.dac_zero[0]  += 50;
        let converted = CalibrationConstants::from_tweakable(defaults.to_tweakable());
        let tol = |x: i32, y: i32, t: i32| (x-y).abs() <= t;
        for ch in 0..4 {
            assert!(tol(defaults.adc_scale[ch], converted.adc_scale[ch], 1));
            assert!(tol(defaults.adc_zero[ch], converted.adc_zero[ch], 1));
            assert!(tol(defaults.dac_scale[ch], converted.dac_scale[ch], 1));
            assert!(tol(defaults.dac_zero[ch], converted.dac_zero[ch], 1));
        }
    }
}
