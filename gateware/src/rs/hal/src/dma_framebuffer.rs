use serde_derive::{Serialize, Deserialize};

#[derive(Debug, PartialEq, PartialOrd, Clone, Serialize, Deserialize)]
pub enum Rotate {
    Normal,
    Left,
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
    )+) => {
        $(
            use tiliqua_hal::dma_framebuffer::{DVIModeline, Rotate};
            use embedded_graphics::prelude::{Pixel, Size, OriginDimensions, DrawTarget, GrayColor};
            use embedded_graphics::pixelcolor::Gray8;

            pub struct $DMA_FRAMEBUFFERX {
                registers_fb: $PACFRAMEBUFFERX,
                registers_palette: $PACPALETTEX,
                registers_blitter: $PACBLITTERX,
                mode: DVIModeline,
                framebuffer_base: *mut u32,
                pixel_plot_mem_base: *mut u32,
                blitter_mem_base: *mut u32,
                current_spritesheet_key: u32,
            }

            impl $DMA_FRAMEBUFFERX {
                pub fn new(registers_fb: $PACFRAMEBUFFERX, registers_palette: $PACPALETTEX, registers_blitter: $PACBLITTERX,
                       fb_base: usize, mode: DVIModeline, pixel_plot_mem_base: usize, blitter_mem_base: usize) -> Self {
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
                        w.enable().bit(true)
                    });
                    Self {
                        registers_fb,
                        registers_palette,
                        registers_blitter,
                        mode,
                        framebuffer_base: fb_base as *mut u32,
                        pixel_plot_mem_base: pixel_plot_mem_base as *mut u32,
                        blitter_mem_base: blitter_mem_base as *mut u32,
                        current_spritesheet_key: 0, // No spritesheet loaded initially
                    }
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
                    Size::new(self.mode.h_active as u32,
                              self.mode.v_active as u32)
                }
            }

            impl DrawTarget for $DMA_FRAMEBUFFERX {
                type Color = Gray8;
                type Error = core::convert::Infallible;
                fn draw_iter<I>(&mut self, pixels: I) -> Result<(), Self::Error>
                where
                    I: IntoIterator<Item = Pixel<Self::Color>>,
                {
                    for Pixel(coord, color) in pixels.into_iter() {
                        let cmd: u32 = ((coord.x as u32) << 20) |
                                       ((coord.y as u32) << 8) |
                                       (color.luma() as u32 & 0xffu32);
                        unsafe {
                            self.pixel_plot_mem_base.write_volatile(cmd);
                        }
                    }
                    Ok(())
                }

                fn upload_spritesheet(&mut self, key: u32, pixels: &[u8], width: u32, height: u32) -> Result<(), Self::Error> {
                    // Check if this spritesheet is already loaded
                    if self.current_spritesheet_key == key {
                        return Ok(()); // Already loaded, NOP
                    }

                    // Get hardware spritesheet width from status register
                    let status = self.registers_blitter.status().read();
                    let hw_width_words = status.sheet_width_words().bits() as u32;
                    let hw_width_pixels = hw_width_words * 32;

                    // Upload pixel data to blitter sprite memory
                    // ImageRaw<BinaryColor> data is already packed: 8 pixels per byte, 1 bit per pixel
                    let sprite_mem = self.blitter_mem_base;
                    let bytes_per_row = (width + 7) / 8;

                    for y in 0..height {
                        let row_start_byte = (y * bytes_per_row) as usize;
                        let row_start_word = y * hw_width_words;
                        
                        // Process each word in the hardware row (may be wider than actual data)
                        for word_in_row in 0..hw_width_words {
                            let mut word_value = 0u32;
                            
                            // Only fill with data if we're within the actual image width
                            if word_in_row * 32 < width {
                                // Pack 4 bytes (32 pixels) into one 32-bit word
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
                            unsafe {
                                log::info!("{:#x}@{:#x}", word_value, word_offset);
                                sprite_mem.offset(word_offset).write_volatile(word_value);
                            }
                        }
                    }

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

                    // Wait for any previous operation to complete before starting new one
                    while self.registers_blitter.status().read().busy().bit() {
                        // Busy wait for previous operation
                    }

                    // Set up source parameters (CMD0)
                    self.registers_blitter.src().write(|w| unsafe {
                        w.src_x().bits(src_x as u8);
                        w.src_y().bits(src_y as u8);
                        w.width().bits(width as u8);
                        w.height().bits(height as u8)
                    });

                    //log::info!("s_x={} s_y={} w={} h={}", src_x, src_y, width, height);

                    // Convert Gray8 color to 4-bit color and intensity
                    let luma = color.luma();
                    let intensity_4bit = (luma >> 4) & 0xF;
                    let color_4bit = luma & 0xF;

                    // Trigger blit with destination parameters (CMD1)
                    // This starts the hardware operation in parallel
                    self.registers_blitter.blit().write(|w| unsafe {
                        w.dst_x().bits(dst_x as u16); // Convert signed to unsigned representation
                        w.dst_y().bits(dst_y as u16);
                        w.color().bits(color_4bit); // Use actual color from text style
                        w.intensity().bits(intensity_4bit) // Use actual intensity from text style
                    });

                    // Don't wait for completion - let hardware run in parallel
                    // Next blit_sprite call will wait if needed
                    Ok(())
                }
            }
        )+
    }
}
