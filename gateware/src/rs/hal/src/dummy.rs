//! Dummy implementations for build-time validation and testing
//!
//! This module provides minimal implementations of embedded HAL traits
//! that can be used for compile-time validation and testing without
//! requiring actual hardware.

use crate::nor_flash::{ErrorType, NorFlash, NorFlashError, NorFlashErrorKind, ReadNorFlash, MultiwriteNorFlash};

/// Dummy error type for flash operations
#[derive(Debug, Clone, Copy)]
pub struct DummyError;

impl NorFlashError for DummyError {
    fn kind(&self) -> NorFlashErrorKind {
        NorFlashErrorKind::Other
    }
}

/// Dummy flash implementation for build-time validation
/// 
/// This provides a minimal implementation of the NorFlash traits
/// without any actual storage, useful for testing and validation.
pub struct DummyFlash {
    capacity: usize,
}

impl DummyFlash {
    /// Create a new dummy flash with the specified capacity
    pub fn new(capacity: usize) -> Self {
        Self { capacity }
    }
}

impl Default for DummyFlash {
    fn default() -> Self {
        Self::new(1024)
    }
}

impl ErrorType for DummyFlash {
    type Error = DummyError;
}

impl ReadNorFlash for DummyFlash {
    const READ_SIZE: usize = 1;
    
    fn read(&mut self, _offset: u32, _bytes: &mut [u8]) -> Result<(), Self::Error> {
        Ok(())
    }
    
    fn capacity(&self) -> usize {
        self.capacity
    }
}

impl NorFlash for DummyFlash {
    const WRITE_SIZE: usize = 1;
    const ERASE_SIZE: usize = 1;
    
    fn erase(&mut self, _from: u32, _to: u32) -> Result<(), Self::Error> {
        Ok(())
    }
    
    fn write(&mut self, _offset: u32, _bytes: &[u8]) -> Result<(), Self::Error> {
        Ok(())
    }
}

impl MultiwriteNorFlash for DummyFlash {}