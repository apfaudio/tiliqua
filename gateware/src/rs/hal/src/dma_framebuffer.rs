#[derive(Debug, PartialEq, Clone)]
pub enum Rotate {
    Normal,
    Left,
}

#[derive(Debug, Clone)]
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
    )+) => {
        $(
            use tiliqua_hal::dma_framebuffer::{DVIModeline, Rotate};
            use embedded_graphics::prelude::{Pixel, Size, OriginDimensions, DrawTarget, GrayColor};
            use embedded_graphics::pixelcolor::Gray8;

            pub struct $DMA_FRAMEBUFFERX {
                registers_fb: $PACFRAMEBUFFERX,
                registers_palette: $PACPALETTEX,
                mode: DVIModeline,
                framebuffer_base: *mut u32,
            }

            impl $DMA_FRAMEBUFFERX {
                pub fn new(registers_fb: $PACFRAMEBUFFERX, registers_palette: $PACPALETTEX, fb_base: usize,
                       mode: DVIModeline) -> Self {
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
                        mode,
                        framebuffer_base: fb_base as *mut u32,
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
                    let h_active = self.size().width;
                    let v_active = self.size().height;
                    for Pixel(coord, color) in pixels.into_iter() {
                        if let Ok((x, y)) = coord.try_into() {
                            if x >= 0 && x < h_active && y >= 0 && y < v_active {
                                let xf: u32 = if (self.mode.rotate == Rotate::Left) {v_active - y} else {x};
                                let yf: u32 = if (self.mode.rotate == Rotate::Left) {x}            else {y};
                                // Calculate the index in the framebuffer.
                                let index: u32 = (xf + yf * h_active) / 4;
                                unsafe {
                                    // TODO: support anything other than Gray8
                                    let mut px = self.framebuffer_base.offset(
                                        index as isize).read_volatile();
                                    px &= !(0xFFu32 << (8*(xf%4)));
                                    self.framebuffer_base.offset(index as isize).write_volatile(
                                        px | ((color.luma() as u32) << (8*(xf%4))));
                                }
                            }
                        }
                    }
                    Ok(())
                }
            }
        )+
    }
}
