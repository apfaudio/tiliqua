use serde_derive::{Serialize, Deserialize};
use strum_macros::{EnumIter, IntoStaticStr};

#[derive(Default, Debug, PartialEq, PartialOrd, Clone, Copy, Serialize, Deserialize, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum Rotate {
    #[default]
    Normal = 0,
    Left = 1,
    Inverted = 2,
    Right = 3,
}

#[derive(Debug, Clone, PartialEq, PartialOrd, Serialize, Deserialize)]
pub struct DVIModeline {
   pub h_active:      u16,
   pub h_sync_start:  u16,
   pub h_sync_end:    u16,
   pub h_total:       u16,
   pub h_sync_invert: bool,
   pub v_active:      u16,
   pub v_sync_start:  u16,
   pub v_sync_end:    u16,
   pub v_total:       u16,
   pub v_sync_invert: bool,
   pub pixel_clk_mhz: f32,
   pub rotate:        Rotate,
}

impl DVIModeline {
    pub fn refresh_rate(&self) -> f32 {
        1e6f32 * self.pixel_clk_mhz / (self.h_total as u32 * self.v_total as u32) as f32
    }

    pub fn fixed(&self) -> bool {
        self.v_total == 0
    }

    pub fn maybe_override_fixed(self, fixed: Option<(u16, u16)>, fixed_pclk_hz: u32) -> Self {
        if let Some((h_active, v_active)) = fixed {
            let rotate = match (h_active, v_active) {
                (720, 720) => Rotate::Left, // ... XXX hack for round screen :)
                _ => Rotate::Normal
            };
            DVIModeline {
                h_active      : h_active,
                h_sync_start  : 0,
                h_sync_end    : 0,
                h_total       : 0,
                h_sync_invert : false,
                v_active      : v_active,
                v_sync_start  : 0,
                v_sync_end    : 0,
                v_total       : 0,
                v_sync_invert : false,
                pixel_clk_mhz : (fixed_pclk_hz as f32) / 1e6f32,
                rotate        : rotate
            }
        } else {
            self
        }
    }
}

impl Default for DVIModeline {
    fn default() -> Self {
        Self {
            h_active      : 1280,
            h_sync_start  : 1390,
            h_sync_end    : 1430,
            h_total       : 1650,
            h_sync_invert : false,
            v_active      : 720,
            v_sync_start  : 725,
            v_sync_end    : 730,
            v_total       : 750,
            v_sync_invert : false,
            pixel_clk_mhz : 74.25,
            rotate        : Rotate::Normal,
        }
    }
}

pub trait DMAFramebuffer {
    fn update_fb_base(&mut self, fb_base: u32);
    fn set_palette_rgb(&mut self, intensity: u8, hue: u8, r: u8, g: u8, b: u8);
    fn get_hpd(&mut self) -> bool;
}

#[macro_export]
macro_rules! impl_dma_framebuffer {
    ($(
        $DMA_FRAMEBUFFERX:ident: $PACFRAMEBUFFERX:ty,
        $PALETTEX:ident: $PACPALETTEX:ty,
        $BLITTERX:ident: $PACBLITTERX:ty,
        $PIXEL_PLOTX:ident: $PACPIXEL_PLOTX:ty,
        $LINEX:ident: $PACLINEX:ty,
    )+) => {
        $(
            use tiliqua_hal::dma_framebuffer::{DVIModeline, Rotate};
            use tiliqua_hal::embedded_graphics::prelude::{Pixel, Size, OriginDimensions, DrawTarget};
            use tiliqua_lib::color::TiliquaColor;

            pub struct $DMA_FRAMEBUFFERX {
                registers_fb: $PACFRAMEBUFFERX,
                registers_palette: $PACPALETTEX,
                registers_blitter: $PACBLITTERX,
                registers_pixel_plot: $PACPIXEL_PLOTX,
                registers_line: $PACLINEX,
                mode: DVIModeline,
                framebuffer_base: *mut u32,
                blitter_mem_base: *mut u32,
                current_spritesheet_key: u32,
            }

            impl $DMA_FRAMEBUFFERX {
                pub fn new(registers_fb: $PACFRAMEBUFFERX, registers_palette: $PACPALETTEX, registers_blitter: $PACBLITTERX,
                       registers_pixel_plot: $PACPIXEL_PLOTX, registers_line: $PACLINEX, fb_base: usize, mode: DVIModeline, blitter_mem_base: usize) -> Self {
                    registers_fb.flags().write(|w| unsafe {
                        w.enable().bit(false)
                    });
                    registers_fb.fb_base().write(|w| unsafe {
                        w.fb_base().bits(fb_base as u32)
                    });
                    registers_fb.h_timing().write(|w| unsafe {
                        w.h_active().bits(mode.h_active);
                        w.h_sync_start().bits(mode.h_sync_start)
                    } );
                    registers_fb.h_timing2().write(|w| unsafe {
                        w.h_sync_end().bits(mode.h_sync_end);
                        w.h_total().bits(mode.h_total)
                    } );
                    registers_fb.v_timing().write(|w| unsafe {
                        w.v_active().bits(mode.v_active);
                        w.v_sync_start().bits(mode.v_sync_start)
                    } );
                    registers_fb.v_timing2().write(|w| unsafe {
                        w.v_sync_end().bits(mode.v_sync_end);
                        w.v_total().bits(mode.v_total)
                    } );
                    registers_fb.hv_timing().write(|w| unsafe {
                        w.h_sync_invert().bit(mode.h_sync_invert);
                        w.v_sync_invert().bit(mode.v_sync_invert);
                        w.active_pixels().bits(
                            mode.h_active as u32 * mode.v_active as u32)
                    } );
                    registers_fb.flags().write(|w| unsafe {
                        w.enable().bit(true);
                        w.rotation().bits(mode.rotate.clone() as u8)
                    });
                    Self {
                        registers_fb,
                        registers_palette,
                        registers_blitter,
                        registers_pixel_plot,
                        registers_line,
                        mode,
                        framebuffer_base: fb_base as *mut u32,
                        blitter_mem_base: blitter_mem_base as *mut u32,
                        current_spritesheet_key: 0, // No spritesheet loaded initially
                    }
                }

                pub fn rotate(&mut self, rotation: &Rotate) {
                    self.registers_fb.flags().write(|w| unsafe {
                        w.enable().bit(true);
                        w.rotation().bits(rotation.clone() as u8)
                    });
                    self.mode.rotate = rotation.clone();
                }

                /// Draw a line from start to end point using hardware line plotter
                pub fn draw_line(&mut self, start_x: i32, start_y: i32, end_x: i32, end_y: i32, color: Self::Color) -> Result<(), core::convert::Infallible> {
                    let pixel_data = color.to_raw();

                    // Wait if FIFO is full
                    while self.registers_line.status().read().full().bit() {
                        // Busy wait for FIFO space
                    }

                    // Send start point (first point in strip)
                    self.registers_line.point().write(|w| unsafe {
                        w.x().bits(start_x as u16);
                        w.y().bits(start_y as u16);
                        w.pixel().bits(pixel_data);
                        w.cmd().bit(false) // CONTINUE (0)
                    });

                    // Wait if FIFO is full again
                    while self.registers_line.status().read().full().bit() {
                        // Busy wait for FIFO space
                    }

                    // Send end point (end of strip)
                    self.registers_line.point().write(|w| unsafe {
                        w.x().bits(end_x as u16);
                        w.y().bits(end_y as u16);
                        w.pixel().bits(pixel_data);
                        w.cmd().bit(true) // END (1)
                    });

                    Ok(())
                }

            }


            impl hal::dma_framebuffer::DMAFramebuffer for $DMA_FRAMEBUFFERX {
                fn update_fb_base(&mut self, fb_base: u32) {
                    self.registers_fb.fb_base().write(|w| unsafe {
                        w.fb_base().bits(fb_base)
                    });
                    self.framebuffer_base = fb_base as *mut u32
                }

                fn set_palette_rgb(&mut self, intensity: u8, hue: u8, r: u8, g: u8, b: u8)  {
                    /* wait until last coefficient written */ 
                    while self.registers_palette.palette_busy().read().bits() == 1 { }
                    self.registers_palette.palette().write(|w| unsafe {
                        w.position().bits(((intensity&0xF) << 4) | (hue&0xF));
                        w.red()     .bits(r);
                        w.green()   .bits(g);
                        w.blue()    .bits(b)
                    } );
                }

                fn get_hpd(&mut self) -> bool  {
                    self.registers_fb.hpd().read().hpd().bit()
                }
            }

            impl OriginDimensions for $DMA_FRAMEBUFFERX {
                fn size(&self) -> Size {
                    match self.mode.rotate {
                        Rotate::Normal | Rotate::Inverted => {
                            Size::new(self.mode.h_active as u32,
                                      self.mode.v_active as u32)
                        }
                        Rotate::Left | Rotate::Right => {
                            Size::new(self.mode.v_active as u32,
                                      self.mode.h_active as u32)
                        }
                    }
                }
            }

            impl DrawTarget for $DMA_FRAMEBUFFERX {
                type Color = TiliquaColor;
                type Error = core::convert::Infallible;
                fn draw_iter<I>(&mut self, pixels: I) -> Result<(), Self::Error>
                where
                    I: IntoIterator<Item = Pixel<Self::Color>>,
                {
                    for Pixel(coord, color) in pixels.into_iter() {
                        // Use raw color value directly as pixel data
                        let pixel_data = color.to_raw();

                        // Write to CSR registers (writing to plot register triggers the operation)
                        self.registers_pixel_plot.plot().write(|w| unsafe {
                            w.x().bits(coord.x as u16);             // x coordinate
                            w.y().bits(coord.y as u16);             // y coordinate
                            w.pixel().bits(pixel_data)              // pixel data (8 bits)
                        });
                    }
                    Ok(())
                }

                fn upload_spritesheet(&mut self, key: u32, pixels: &[u8], width: u32, height: u32) -> Result<(), Self::Error> {
                    // Check if this spritesheet is already loaded
                    if self.current_spritesheet_key == key {
                        return Ok(()); // Already loaded, NOP
                    }

                    // Wait for command FIFO to be empty before changing spritesheet
                    // This ensures all pending blit operations using the current spritesheet complete
                    while !self.registers_blitter.status().read().empty().bit() {
                        // Busy wait for all pending operations to complete
                    }

                    // Get hardware spritesheet width from status register
                    let status = self.registers_blitter.status().read();
                    let hw_width_words = status.sheet_width_words().bits() as u32;
                    let hw_width_pixels = hw_width_words * 32;

                    // Upload pixel data to blitter sprite memory
                    // ImageRaw<BinaryColor> data is already packed: 8 pixels per byte, 1 bit per pixel
                    let sprite_mem = self.blitter_mem_base;
                    let bytes_per_row = (width + 7) / 8;

                    /*
                    // Debug: Print first 32x32 section of original data
                    log::info!("First 32x32 section of original embedded-graphics data:");
                    for debug_y in 0..32.min(height) {
                        let mut line = [0u8; 33]; // 32 chars + null terminator
                        let row_start = (debug_y * bytes_per_row) as usize;
                        for pixel_x in 0..32.min(width) {
                            let byte_idx = row_start + (pixel_x / 8) as usize;
                            let bit_idx = 7 - (pixel_x % 8); // MSB first within byte
                            if byte_idx < pixels.len() {
                                let byte_val = pixels[byte_idx];
                                let bit = (byte_val >> bit_idx) & 1;
                                line[pixel_x as usize] = if bit == 1 { b'#' } else { b'.' };
                            } else {
                                line[pixel_x as usize] = b'.';
                            }
                        }
                        line[32] = 0; // null terminator
                        if let Ok(line_str) = core::str::from_utf8(&line[..32]) {
                            log::info!("{}", line_str);
                        }
                    }
                    */

                    // Debug: Store first 32 words for readback
                    let mut debug_words = [0u32; 32];

                    for y in 0..height {
                        let row_start_byte = (y * bytes_per_row) as usize;
                        let row_start_word = y * hw_width_words;
                        
                        // Process each word in the hardware row (may be wider than actual data)
                        for word_in_row in 0..hw_width_words {
                            let mut word_value = 0u32;
                            
                            // Only fill with data if we're within the actual image width
                            if word_in_row * 32 < width {
                                // Pack 4 bytes (32 pixels) directly into one 32-bit word
                                // Hardware will handle the MSB-first bit ordering
                                for byte_in_word in 0..4 {
                                    let byte_idx = row_start_byte + (word_in_row * 4 + byte_in_word) as usize;
                                    if byte_idx < pixels.len() {
                                        let pixel_byte = pixels[byte_idx];
                                        word_value |= (pixel_byte as u32) << (byte_in_word * 8);
                                    }
                                }
                            }
                            // If word_in_row * 32 >= width, word_value stays 0 (padding)
                            
                            let word_offset = (row_start_word + word_in_row) as isize;
                            // Bounds check against hardware memory size (2048 words)
                            if word_offset >= 2048 {
                                panic!("Sprite memory out of bounds: offset {} >= 2048", word_offset);
                            }
                            // Store first word of first 32 rows for debug
                            if y < 32 && word_in_row == 0 {
                                debug_words[y as usize] = word_value;
                            }
                            
                            unsafe {
                                //log::info!("{:#x}@{:#x}", word_value, word_offset);
                                sprite_mem.offset(word_offset).write_volatile(word_value);
                            }
                        }
                    }

                    /*
                    // Debug: Print first 32x32 section as ASCII art using stored data
                    // Use the same bit ordering correction as hardware
                    log::info!("First 32x32 section of uploaded spritesheet (hardware view):");
                    for debug_y in 0..32 {
                        let mut line = [0u8; 33]; // 32 chars + null terminator
                        let word_data = debug_words[debug_y];
                        // Extract each bit using hardware's corrected indexing
                        for pixel_idx in 0..32 {
                            // Apply same correction as hardware:
                            let byte_in_word = pixel_idx / 8;  // Which byte (0-3)
                            let bit_in_byte = pixel_idx % 8;   // Which bit in that byte (0-7)
                            let corrected_bit_index = (byte_in_word * 8) + (7 - bit_in_byte);  // MSB-first within byte
                            let bit = (word_data >> corrected_bit_index) & 1;
                            line[pixel_idx] = if bit == 1 { b'#' } else { b'.' };
                        }
                        line[32] = 0; // null terminator
                        if let Ok(line_str) = core::str::from_utf8(&line[..32]) {
                            log::info!("{}", line_str);
                        }
                    }
                    */

                    // Update the local key to indicate this spritesheet is loaded
                    self.current_spritesheet_key = key;

                    Ok(())
                }

                fn blit_sprite(&mut self, key: u32, src_x: u32, src_y: u32, width: u32, height: u32, dst_x: i32, dst_y: i32, color: Self::Color) -> Result<(), Self::Error> {
                    // Verify the correct spritesheet is loaded
                    if self.current_spritesheet_key != key {
                        // Spritesheet not loaded, this is an error condition
                        // In a real system we might want to return an error, but for now just return Ok to not break things
                        return Ok(());
                    }

                    // Wait only if command FIFO is full (busy flag)
                    // This allows asynchronous operation while preventing overflow
                    while self.registers_blitter.status().read().busy().bit() {
                        // Busy wait for FIFO space to become available
                    }

                    // Set up source parameters (CMD0)
                    self.registers_blitter.src().write(|w| unsafe {
                        w.src_x().bits(src_x as u8);
                        w.src_y().bits(src_y as u8);
                        w.width().bits(width as u8);
                        w.height().bits(height as u8)
                    });

                    //log::info!("s_x={} s_y={} w={} h={}", src_x, src_y, width, height);

                    // Use raw color value directly as pixel data  
                    let pixel_data = color.to_raw();

                    // Trigger blit with destination parameters (CMD1)
                    // This enqueues the command in the FIFO for asynchronous execution
                    self.registers_blitter.blit().write(|w| unsafe {
                        w.dst_x().bits(dst_x as u16); // Convert signed to unsigned representation
                        w.dst_y().bits(dst_y as u16);
                        w.pixel().bits(pixel_data) // pixel data (8 bits)
                    });

                    // Command is now queued - hardware will execute asynchronously
                    // Next blit_sprite call will wait only if FIFO becomes full
                    Ok(())
                }
            }
        )+
    }
}
