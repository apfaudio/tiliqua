use embedded_hal::i2c::I2c;
use serde_derive::{Serialize, Deserialize};
use tiliqua_hal::eeprom::{EepromDriver, EepromError};

const EEPROM_CALIBRATION_ADDR: u8 = 0x00;
const EEPROM_CALIBRATION_SIZE: usize = 0x40;
const EEPROM_CONFIG_ADDR: u8 = 0x40;
const EEPROM_CONFIG_SIZE: usize = 0x40;

#[derive(Debug, PartialEq, Clone, Serialize, Deserialize)]
pub struct EepromCalibration {
    pub adc_scale: [i32; 4],
    pub adc_zero:  [i32; 4],
    pub dac_scale: [i32; 4],
    pub dac_zero:  [i32; 4],
    pub fractional_bits: u8,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EepromConfig {
    pub last_boot_slot: Option<u8>,
}

pub struct EepromManager<I2C> {
    eeprom: EepromDriver<I2C>,
}

impl<I2C> EepromManager<I2C>
where
    I2C: I2c,
{
    pub fn new(i2c: I2C) -> Self {
        Self {
            eeprom: EepromDriver::new(i2c),
        }
    }

    pub fn read_calibration(&mut self) -> Result<EepromCalibration, EepromError<I2C::Error>> {
        let mut buffer = [0u8; EEPROM_CALIBRATION_SIZE];
        self.eeprom.read_bytes(EEPROM_CALIBRATION_ADDR, &mut buffer)?;
        match postcard::from_bytes(&buffer) {
            Ok(cal_data) => Ok(cal_data),
            Err(_) => Err(EepromError::InvalidData),
        }
    }

    pub fn write_calibration(&mut self, cal_data: &EepromCalibration) -> Result<(), EepromError<I2C::Error>> {
        let mut buffer = [0u8; EEPROM_CALIBRATION_SIZE];
        let serialized = postcard::to_slice(cal_data, &mut buffer)
            .map_err(|_| EepromError::InvalidSize)?;
        self.eeprom.write_bytes(EEPROM_CALIBRATION_ADDR, serialized)
    }

    pub fn read_config(&mut self) -> Result<EepromConfig, EepromError<I2C::Error>> {
        let mut buffer = [0u8; EEPROM_CONFIG_SIZE];
        self.eeprom.read_bytes(EEPROM_CONFIG_ADDR, &mut buffer)?;
        match postcard::from_bytes(&buffer) {
            Ok(config) => Ok(config),
            Err(_) => Err(EepromError::InvalidData),
        }
    }

    pub fn write_config(&mut self, config: &EepromConfig) -> Result<(), EepromError<I2C::Error>> {
        let mut buffer = [0u8; EEPROM_CONFIG_SIZE];
        let serialized = postcard::to_slice(config, &mut buffer)
            .map_err(|_| EepromError::InvalidSize)?;
        self.eeprom.write_bytes(EEPROM_CONFIG_ADDR, serialized)
    }
}
