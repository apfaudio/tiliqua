use embedded_hal::i2c::I2c;
use embedded_hal::i2c::Operation;

// I2C address of the CY8CMBR3108 device (0x37)
const CY8CMBR3108_ADDR: u8 = 0x37;

// CRC calculation constants (from cy8cmbr3108 reference code)
const CY8CMBR3XXX_CONFIG_DATA_LENGTH: usize = 126;
const CY8CMBR3XXX_CRC_BIT_WIDTH: u16 = 2 * 8;
const CY8CMBR3XXX_CRC_BIT4_MASK: u16 = 0x0F;
const CY8CMBR3XXX_CRC_BIT4_SHIFT: u16 = 4;
const CY8CMBR3XXX_CCITT16_DEFAULT_SEED: u16 = 0xffff;
const CY8CMBR3XXX_CCITT16_POLYNOM: u16 = 0x1021;

// Command register and commands
const COMMAND_REG: u8 = 0x86;
const CMD_SAVE_CHECK_CRC: u8 = 0x02;
const CMD_WRITE_RESET: u8 = 0xFF;

/// Register addresses for CY8CMBR3108 configuration
#[derive(Debug, Clone, Copy)]
#[allow(non_camel_case_types)]
pub enum Register {
    SENSOR_EN = 0x00,
    FSS_EN = 0x02,
    TOGGLE_EN = 0x04,
    LED_ON_EN = 0x06,
    SENSITIVITY0 = 0x08,
    SENSITIVITY1 = 0x09,
    SENSITIVITY2 = 0x0a,
    SENSITIVITY3 = 0x0b,
    BASE_THRESHOLD0 = 0x0c,
    BASE_THRESHOLD1 = 0x0d,
    FINGER_THRESHOLD2 = 0x0e,
    FINGER_THRESHOLD3 = 0x0f,
    FINGER_THRESHOLD4 = 0x10,
    FINGER_THRESHOLD5 = 0x11,
    FINGER_THRESHOLD6 = 0x12,
    FINGER_THRESHOLD7 = 0x13,
    FINGER_THRESHOLD8 = 0x14,
    FINGER_THRESHOLD9 = 0x15,
    FINGER_THRESHOLD10 = 0x16,
    FINGER_THRESHOLD11 = 0x17,
    FINGER_THRESHOLD12 = 0x18,
    FINGER_THRESHOLD13 = 0x19,
    FINGER_THRESHOLD14 = 0x1a,
    FINGER_THRESHOLD15 = 0x1b,
    SENSOR_DEBOUNCE = 0x1c,
    BUTTON_HYS = 0x1d,
    BUTTON_LBR = 0x1f,
    BUTTON_NNT = 0x20,
    BUTTON_NT = 0x21,
    PROX_EN = 0x26,
    PROX_CFG = 0x27,
    PROX_CFG2 = 0x28,
    PROX_TOUCH_TH0 = 0x2a,
    PROX_TOUCH_TH1 = 0x2c,
    PROX_RESOLUTION0 = 0x2e,
    PROX_RESOLUTION1 = 0x2f,
    PROX_HYS = 0x30,
    PROX_LBR = 0x32,
    PROX_NNT = 0x33,
    PROX_NT = 0x34,
    PROX_POSITIVE_TH0 = 0x35,
    PROX_POSITIVE_TH1 = 0x36,
    PROX_NEGATIVE_TH0 = 0x39,
    PROX_NEGATIVE_TH1 = 0x3a,
    LED_ON_TIME = 0x3d,
    BUZZER_CFG = 0x3e,
    BUZZER_ON_TIME = 0x3f,
    GPO_CFG = 0x40,
    PWM_DUTYCYCLE_CFG0 = 0x41,
    PWM_DUTYCYCLE_CFG1 = 0x42,
    PWM_DUTYCYCLE_CFG2 = 0x43,
    PWM_DUTYCYCLE_CFG3 = 0x44,
    PWM_DUTYCYCLE_CFG4 = 0x45,
    PWM_DUTYCYCLE_CFG5 = 0x46,
    PWM_DUTYCYCLE_CFG6 = 0x47,
    PWM_DUTYCYCLE_CFG7 = 0x48,
    SPO_CFG = 0x4c,
    DEVICE_CFG0 = 0x4d,
    DEVICE_CFG1 = 0x4e,
    DEVICE_CFG2 = 0x4f,
    DEVICE_CFG3 = 0x50,
    I2C_ADDR = 0x51,
    REFRESH_CTRL = 0x52,
    STATE_TIMEOUT = 0x55,
    SLIDER_CFG = 0x5d,
    SLIDER1_CFG = 0x61,
    SLIDER1_RESOLUTION = 0x62,
    SLIDER1_THRESHOLD = 0x63,
    SLIDER2_CFG = 0x67,
    SLIDER2_RESOLUTION = 0x68,
    SLIDER2_THRESHOLD = 0x69,
    SLIDER_LBR = 0x71,
    SLIDER_NNT = 0x72,
    SLIDER_NT = 0x73,
    SCRATCHPAD0 = 0x7a,
    SCRATCHPAD1 = 0x7b,
    CONFIG_CRC = 0x7e,
}

/// Default configuration for the CY8CMBR3108
/// Hand-picked after a lot of fiddling, for Tiliqua.
pub struct DefaultConfig;

impl DefaultConfig {
    pub const RAW_CONFIG: [u8; 130] = [
        // Configuration header bytes
        0x6e,       //
        0x00,       //
        // Configuration data
        0xff,       // SENSOR_EN
        0x00,       //
        0x00,       // FSS_EN
        0x00,       //
        0x00,       // TOGGLE_EN
        0x00,
        0x00,       // LED_ON_EN
        0x00,
        0xff,       // SENSITIVITY0
        0xff,       // SENSITIVITY1
        0x00,       // SENSITIVITY2
        0x00,       // SENSITIVITY3
        0x80,       // BASE_THRESHOLD0
        0x80,       // BASE_THRESHOLD1
        0x80,       // FINGER_THRESHOLD2
        0x80,       // FINGER_THRESHOLD3
        0x80,       // FINGER_THRESHOLD4
        0x80,       // FINGER_THRESHOLD5
        0x80,       // FINGER_THRESHOLD6
        0x80,       // FINGER_THRESHOLD7
        0x00,       // FINGER_THRESHOLD8
        0x00,       // FINGER_THRESHOLD9
        0x00,       // FINGER_THRESHOLD10
        0x00,       // FINGER_THRESHOLD11
        0x00,       // FINGER_THRESHOLD12
        0x00,       // FINGER_THRESHOLD13
        0x00,       // FINGER_THRESHOLD14
        0x00,       // FINGER_THRESHOLD15
        0x04,       // SENSOR_DEBOUNCE
        0x9f,       // BUTTON_HYS
        0x00,
        0xb2,       // BUTTON_LBR
        0x94,       // BUTTON_NNT
        0x94,       // BUTTON_NT
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,       // PROX_EN
        0x80,       // PROX_CFG
        0x05,       // PROX_CFG2
        0x00,
        0x00,       // PROX_TOUCH_TH0
        0x02,
        0x00,       // PROX_TOUCH_TH1
        0x02,
        0x00,       // PROX_RESOLUTION0
        0x00,       // PROX_RESOLUTION1
        0x00,       // PROX_HYS
        0x00,
        0x00,       // PROX_LBR
        0x00,       // PROX_NNT
        0x00,       // PROX_NT
        0x1e,       // PROX_POSITIVE_TH0
        0x1e,       // PROX_POSITIVE_TH1
        0x00,
        0x00,
        0x1e,       // PROX_NEGATIVE_TH0
        0x1e,       // PROX_NEGATIVE_TH1
        0x00,
        0x00,
        0x00,       // LED_ON_TIME
        0x01,       // BUZZER_CFG
        0x01,       // BUZZER_ON_TIME
        0x00,       // GPO_CFG
        0xff,       // PWM_DUTYCYCLE_CFG0
        0xff,       // PWM_DUTYCYCLE_CFG1
        0xff,       // PWM_DUTYCYCLE_CFG2
        0xff,       // PWM_DUTYCYCLE_CFG3
        0x00,       // PWM_DUTYCYCLE_CFG4
        0x00,       // PWM_DUTYCYCLE_CFG5
        0x00,       // PWM_DUTYCYCLE_CFG6
        0x00,       // PWM_DUTYCYCLE_CFG7
        0x00,
        0x00,
        0x00,
        0x10,       // SPO_CFG
        0x03,       // DEVICE_CFG0
        0x00,       // DEVICE_CFG1
        0x20,       // DEVICE_CFG2
        0x00,       // DEVICE_CFG3
        0x37,       // I2C_ADDR
        0x01,       // REFRESH_CTRL
        0x0f,
        0x00,       // STATE_TIMEOUT
        0x0a,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,       // SLIDER_CFG
        0x00,
        0x00,
        0x00,
        0x00,       // SLIDER1_CFG
        0x00,       // SLIDER1_RESOLUTION
        0x00,       // SLIDER1_THRESHOLD
        0x00,
        0x00,
        0x00,
        0x00,       // SLIDER2_CFG
        0x00,       // SLIDER2_RESOLUTION
        0x00,       // SLIDER2_THRESHOLD
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,       // SLIDER_LBR
        0x00,       // SLIDER_NNT
        0x00,       // SLIDER_NT
        0x00,
        0x00,
        0x00,       // SCRATCHPAD0
        0x00,       // SCRATCHPAD1
        0x86,
        0xc1,       // CONFIG_CRC
    ];
}

pub trait Cy8cmbr3108<I2C: I2c> {
    /// Read a single register from the device
    fn read_register(&mut self, register: u8) -> Result<u8, I2C::Error>;
    
    /// Write a single register to the device
    fn write_register(&mut self, register: u8, value: u8) -> Result<(), I2C::Error>;
    
    /// Write the current configuration to the device
    fn write_config(&mut self) -> Result<(), I2C::Error>;
    
    /// Save and apply the configuration with CRC check
    fn save_check_crc(&mut self) -> Result<(), I2C::Error>;
    
    /// Reset the device to apply configuration
    fn reset(&mut self) -> Result<(), I2C::Error>;
    
    /// Read a sensor difference count value (touch strength)
    fn read_sensor_diff(&mut self, sensor_index: u8) -> Result<u8, I2C::Error>;
}

pub struct Cy8cmbr3108Driver<I2C> {
    i2c: I2C,
    pub config: [u8; CY8CMBR3XXX_CONFIG_DATA_LENGTH],
}

impl<I2C: I2c> Cy8cmbr3108Driver<I2C> {
    /// Create a new CY8CMBR3108 driver with default configuration
    pub fn new(i2c: I2C) -> Self {
        let mut config = [0u8; CY8CMBR3XXX_CONFIG_DATA_LENGTH];
        // Copy the configuration data (skipping header and trailing CRC bytes)
        config.copy_from_slice(&DefaultConfig::RAW_CONFIG[2..128]);
        
        Self { i2c, config }
    }
    
    /// Verify that the CRC in the default configuration is valid
    /// This can be called during initialization to ensure configuration integrity
    pub fn verify_default_config_crc() -> bool {
        // Extract the configuration bytes (exclude header and CRC bytes)
        let config_data = &DefaultConfig::RAW_CONFIG[2..128];
        
        // Extract the stored CRC bytes
        let stored_crc = ((DefaultConfig::RAW_CONFIG[129] as u16) << 8) | 
                           DefaultConfig::RAW_CONFIG[128] as u16;
        
        // Calculate CRC for the configuration data
        let mut seed = CY8CMBR3XXX_CCITT16_DEFAULT_SEED;
        
        for byte_value in config_data.iter() {
            // Process high 4 bits
            let table_index = (byte_value >> CY8CMBR3XXX_CRC_BIT4_SHIFT) as u16 & CY8CMBR3XXX_CRC_BIT4_MASK
                ^ (seed >> (CY8CMBR3XXX_CRC_BIT_WIDTH - CY8CMBR3XXX_CRC_BIT4_SHIFT));
            seed = (CY8CMBR3XXX_CCITT16_POLYNOM * table_index) 
                ^ (seed << CY8CMBR3XXX_CRC_BIT4_SHIFT);
            seed &= 0xffff;
            
            // Process low 4 bits
            let table_index = byte_value as u16 & CY8CMBR3XXX_CRC_BIT4_MASK
                ^ (seed >> (CY8CMBR3XXX_CRC_BIT_WIDTH - CY8CMBR3XXX_CRC_BIT4_SHIFT));
            seed = (CY8CMBR3XXX_CCITT16_POLYNOM * table_index) 
                ^ (seed << CY8CMBR3XXX_CRC_BIT4_SHIFT);
            seed &= 0xffff;
        }
        
        // Compare calculated CRC with stored CRC
        seed == stored_crc
    }
    
    /// Calculate CRC for configuration data
    pub fn calculate_crc(&self) -> u16 {
        let mut seed = CY8CMBR3XXX_CCITT16_DEFAULT_SEED;
        
        // Calculate CRC for all configuration bytes except the CRC itself
        for byte_value in self.config.iter() {
            // Process high 4 bits
            let table_index = (byte_value >> CY8CMBR3XXX_CRC_BIT4_SHIFT) as u16 & CY8CMBR3XXX_CRC_BIT4_MASK
                ^ (seed >> (CY8CMBR3XXX_CRC_BIT_WIDTH - CY8CMBR3XXX_CRC_BIT4_SHIFT));
            seed = (CY8CMBR3XXX_CCITT16_POLYNOM * table_index) 
                ^ (seed << CY8CMBR3XXX_CRC_BIT4_SHIFT);
            seed &= 0xffff;
            
            // Process low 4 bits
            let table_index = byte_value as u16 & CY8CMBR3XXX_CRC_BIT4_MASK
                ^ (seed >> (CY8CMBR3XXX_CRC_BIT_WIDTH - CY8CMBR3XXX_CRC_BIT4_SHIFT));
            seed = (CY8CMBR3XXX_CCITT16_POLYNOM * table_index) 
                ^ (seed << CY8CMBR3XXX_CRC_BIT4_SHIFT);
            seed &= 0xffff;
        }
        
        seed
    }
    
    /// Update the CRC in the configuration data
    pub fn update_crc(&mut self) {
        let crc = self.calculate_crc();
        // CONFIG_CRC is at offset 0x7E (126)
        self.config[0x7E - 2] = (crc & 0xFF) as u8;        // Low byte
        self.config[0x7F - 2] = ((crc >> 8) & 0xFF) as u8; // High byte
    }
    
    /// Wait for the command register to be empty (return to 0)
    pub fn wait_for_command_ready(&mut self) -> Result<(), I2C::Error> {
        let mut attempts = 0;
        let max_attempts = 10; // Limit retry attempts
        
        while attempts < max_attempts {
            let cmd_value = self.read_register(COMMAND_REG)?;
            if cmd_value == 0 {
                return Ok(());
            }
            attempts += 1;
        }
        
        // If we reach here, command register never cleared
        Ok(()) // Return success anyway, let caller decide
    }
    
    /// Configure a specific register and update CRC
    pub fn configure_register(&mut self, register: Register, value: u8) {
        let reg_addr = register as u8;
        self.config[reg_addr as usize] = value;
        self.update_crc();
    }
    
    /// Disable the touch sensing IC for better noise performance
    pub fn disable(&mut self) -> Result<(), I2C::Error> {
        // Write to command register (0x86)
        self.write_register(COMMAND_REG, 0x07)?; // Disable + enter low-power mode
        Ok(())
    }
    
    /// Initialize the device with current configuration
    pub fn initialize(&mut self) -> Result<(), I2C::Error> {
        // Write configuration
        self.write_config()?;
        
        // Save and check CRC
        self.save_check_crc()?;
        
        // Wait for command register to be ready
        self.wait_for_command_ready()?;
        
        // Reset the device to apply configuration
        self.reset()
    }
}

impl<I2C: I2c> Cy8cmbr3108<I2C> for Cy8cmbr3108Driver<I2C> {
    fn read_register(&mut self, register: u8) -> Result<u8, I2C::Error> {
        let mut buffer = [0u8];
        
        // Set the register pointer
        self.i2c.transaction(
            CY8CMBR3108_ADDR, 
            &mut [Operation::Write(&[register]), Operation::Read(&mut buffer)]
        )?;
        
        Ok(buffer[0])
    }
    
    fn write_register(&mut self, register: u8, value: u8) -> Result<(), I2C::Error> {
        // Write to register
        self.i2c.transaction(
            CY8CMBR3108_ADDR, 
            &mut [Operation::Write(&[register, value])]
        )
    }
    
    fn write_config(&mut self) -> Result<(), I2C::Error> {
        // Ensure CRC is up to date
        self.update_crc();
        
        // Write configuration one byte at a time
        for reg_addr in 0..CY8CMBR3XXX_CONFIG_DATA_LENGTH {
            // Prepare buffer with register address and data byte
            let buffer = [reg_addr as u8, self.config[reg_addr]];
            
            // Write this single byte
            self.i2c.transaction(
                CY8CMBR3108_ADDR,
                &mut [Operation::Write(&buffer)]
            )?;
        }
        
        Ok(())
    }
    
    fn save_check_crc(&mut self) -> Result<(), I2C::Error> {
        // Send SAVE_CHECK_CRC command
        self.write_register(COMMAND_REG, CMD_SAVE_CHECK_CRC)
    }
    
    fn reset(&mut self) -> Result<(), I2C::Error> {
        // Wait until command register is 0 (ready)
        self.wait_for_command_ready()?;
        
        // Send WRITE_RESET command
        self.write_register(COMMAND_REG, CMD_WRITE_RESET)
    }
    
    fn read_sensor_diff(&mut self, sensor_index: u8) -> Result<u8, I2C::Error> {
        if sensor_index > 7 {
            // Return 0 for invalid sensor index (alternatively could be an error)
            return Ok(0);
        }
        
        // Determine register address for the sensor difference count
        // 0xBA = Sensor 0, each sensor takes 2 bytes, we want MSB
        let reg_addr = 0xBA + (sensor_index * 2);
        
        self.read_register(reg_addr)
    }
}
