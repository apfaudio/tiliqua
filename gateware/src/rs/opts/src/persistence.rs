use sequential_storage::map::{fetch_item, store_item};
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
}

pub trait OptionsPersistence {
    type Error;

    fn load_options<O: Options>(&mut self, opts: &mut O) -> Result<(), Self::Error>;
    fn save_options<O: Options>(&mut self, opts: &O) -> Result<(), Self::Error>;
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
    F: embedded_storage::nor_flash::NorFlash,
{
    type Error = PersistenceError;

    fn load_options<O: Options>(&mut self, opts: &mut O) -> Result<(), Self::Error> {
        // Load individual options
        for opt in opts.all_mut() {
            if let Ok(item) = block_on(fetch_item::<u32, &[u8], _>(
                &mut self.flash,
                self.flash_range.clone(),
                &mut NoCache::new(),
                &mut self.data_buffer,
                &opt.key(),
            )) {
                if let Some(data) = item {
                    opt.decode(data);
                    log::info!("load option: {}={} (from key={} data={:?})", 
                              opt.name(), opt.value(), opt.key(), data);
                }
            }
        }

        // Load page selection
        if let Ok(item) = block_on(fetch_item::<u32, &[u8], _>(
            &mut self.flash,
            self.flash_range.clone(),
            &mut NoCache::new(),
            &mut self.data_buffer,
            &DEFAULT_PAGE_KEY,
        )) {
            if let Some(data) = item {
                opts.page_mut().decode(data);
            }
        }

        Ok(())
    }

    fn save_options<O: Options>(&mut self, opts: &O) -> Result<(), Self::Error> {
        // Save individual options
        for opt in opts.all() {
            let mut buf: [u8; DATA_BUFFER_SZ] = [0u8; DATA_BUFFER_SZ];
            if let Some(encoded_len) = opt.encode(&mut buf) {
                log::info!("{} {} --- {} {:?}", opt.name(), opt.value(), opt.key(), &buf[..encoded_len]);
                
                block_on(store_item::<u32, &[u8], _>(
                    &mut self.flash,
                    self.flash_range.clone(),
                    &mut NoCache::new(),
                    &mut self.data_buffer,
                    &opt.key(),
                    &&buf[..encoded_len],
                )).map_err(|_| PersistenceError::StorageError)?;
            }
        }

        // Save page selection
        let mut buf: [u8; DATA_BUFFER_SZ] = [0u8; DATA_BUFFER_SZ];
        if let Some(encoded_len) = opts.page().encode(&mut buf) {
            block_on(store_item::<u32, &[u8], _>(
                &mut self.flash,
                self.flash_range.clone(),
                &mut NoCache::new(),
                &mut self.data_buffer,
                &DEFAULT_PAGE_KEY,
                &&buf[..encoded_len],
            )).map_err(|_| PersistenceError::StorageError)?;
        }

        Ok(())
    }
}

