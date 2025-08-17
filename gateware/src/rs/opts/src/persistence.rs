use sequential_storage::map::{fetch_item, store_item, remove_all_items};
use sequential_storage::cache::NoCache;
use embassy_futures::block_on;
use embassy_embedded_hal::adapter::BlockingAsync;

use crate::traits::Options;

const DATA_BUFFER_SZ: usize = 32;
const DEFAULT_PAGE_KEY: u32 = 0xdeadbeef;

#[derive(Debug)]
pub enum PersistenceError {
    StorageError,
    SerializationError,
    FlashRangeError,
    KeyCollision(u32),
}

pub trait OptionsPersistence {
    type Error;

    fn save_key(&mut self, key: u32, value: &[u8]) -> Result<(), Self::Error>;
    fn save_key_retries(&mut self, key: u32, value: &[u8], retries: usize) -> Result<(), Self::Error>;
    fn load_key(&mut self, key: u32, buffer: &mut [u8]) -> Result<Option<usize>, Self::Error>;

    fn erase_all(&mut self) -> Result<(), Self::Error>;
    fn load_options<O: Options>(&mut self, opts: &mut O) -> Result<(), Self::Error>;
    fn save_options<O: Options>(&mut self, opts: &O) -> Result<(), Self::Error>;
    fn validate_options<O: Options>(&self, opts: &O) -> Result<(), Self::Error>;
}

pub struct FlashOptionsPersistence<F> {
    flash: BlockingAsync<F>,
    flash_range: core::ops::Range<u32>,
    data_buffer: [u8; DATA_BUFFER_SZ],
}

impl<F> FlashOptionsPersistence<F> {
    pub fn new(flash: F, flash_range: core::ops::Range<u32>) -> Self {
        Self {
            flash: BlockingAsync::new(flash),
            flash_range,
            data_buffer: [0u8; DATA_BUFFER_SZ],
        }
    }
}

impl<F> OptionsPersistence for FlashOptionsPersistence<F>
where
    F: embedded_storage::nor_flash::NorFlash + embedded_storage::nor_flash::MultiwriteNorFlash,
{
    type Error = PersistenceError;

    fn save_key(&mut self, key: u32, value: &[u8]) -> Result<(), Self::Error> {
        block_on(store_item::<u32, &[u8], _>(
            &mut self.flash,
            self.flash_range.clone(),
            &mut NoCache::new(),
            &mut self.data_buffer,
            &key,
            &value,
        )).map_err(|_| PersistenceError::StorageError)
    }

    fn save_key_retries(&mut self, key: u32, value: &[u8], retries: usize) -> Result<(), Self::Error> {
        let mut result = Ok(());
        for _ in 0..retries {
            result = self.save_key(key, value);
            if result.is_ok() {
                return result;
            } else {
                log::warn!("save_key_retries: failed once with {:?}", result);
            }
        }
        return result;
    }

    fn load_key(&mut self, key: u32, buffer: &mut [u8]) -> Result<Option<usize>, Self::Error> {
        let item = block_on(fetch_item::<u32, &[u8], _>(
            &mut self.flash,
            self.flash_range.clone(),
            &mut NoCache::new(),
            &mut self.data_buffer,
            &key,
        )).map_err(|_| PersistenceError::StorageError)?;
        if let Some(data) = item {
            let len = data.len().min(buffer.len());
            buffer[..len].copy_from_slice(&data[..len]);
            Ok(Some(len))
        } else {
            Ok(None)
        }
    }

    fn erase_all(&mut self) -> Result<(), Self::Error> {
        block_on(remove_all_items::<u32, _>(
            &mut self.flash,
            self.flash_range.clone(),
            &mut NoCache::new(),
            &mut self.data_buffer,
        )).map_err(|_| PersistenceError::StorageError)
    }

    fn save_options<O: Options>(&mut self, opts: &O) -> Result<(), Self::Error> {
        for opt in opts.all() {
            let mut buf: [u8; DATA_BUFFER_SZ] = [0u8; DATA_BUFFER_SZ];
            if let Some(encoded_len) = opt.encode(&mut buf) {
                log::info!("opts/save: {}={} ({:x}={:?})", 
                          opt.name(), opt.value(), opt.key(), &buf[..encoded_len]);
                self.save_key_retries(opt.key(), &buf[..encoded_len], 2)?;
            }
        }
        let mut buf: [u8; DATA_BUFFER_SZ] = [0u8; DATA_BUFFER_SZ];
        if let Some(encoded_len) = opts.page().encode(&mut buf) {
            self.save_key(DEFAULT_PAGE_KEY, &buf[..encoded_len])?;
        }
        Ok(())
    }

    fn load_options<O: Options>(&mut self, opts: &mut O) -> Result<(), Self::Error> {
        for opt in opts.all_mut() {
            let mut buf: [u8; DATA_BUFFER_SZ] = [0u8; DATA_BUFFER_SZ];
            if let Some(len) = self.load_key(opt.key(), &mut buf)? {
                opt.decode(&buf[..len]);
                log::info!("opts/load: {}={} ({:x}={:?})", 
                          opt.name(), opt.value(), opt.key(), &buf[..len]);
            }
        }
        let mut buf: [u8; DATA_BUFFER_SZ] = [0u8; DATA_BUFFER_SZ];
        if let Some(len) = self.load_key(DEFAULT_PAGE_KEY, &mut buf)? {
            opts.page_mut().decode(&buf[..len]);
        }
        Ok(())
    }

    fn validate_options<O: Options>(&self, opts: &O) -> Result<(), Self::Error> {
        use heapless::Vec;
        
        // Collect all keys into a small buffer - should be enough for most option sets
        let mut keys: Vec<u32, 64> = Vec::new();
        
        // Collect all option keys
        for opt in opts.all() {
            let key = opt.key();
            // Check if we've seen this key before
            for &existing_key in &keys {
                if existing_key == key {
                    log::error!("Key collision detected: duplicate key 0x{:x}", key);
                    return Err(PersistenceError::KeyCollision(key));
                }
            }
            // Add to our seen keys (ignore if buffer is full - we'll catch major issues)
            keys.push(key).ok();
        }
        
        // Also check the page key doesn't collide
        let page_key = DEFAULT_PAGE_KEY;
        for &existing_key in &keys {
            if existing_key == page_key {
                log::error!("Page key collision detected: page key 0x{:x} conflicts with option key", page_key);
                return Err(PersistenceError::KeyCollision(page_key));
            }
        }
        
        log::info!("Options validation passed: {} unique keys", keys.len());
        Ok(())
    }
}

