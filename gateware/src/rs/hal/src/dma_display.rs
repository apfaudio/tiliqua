pub trait DMAFramebuffer {
    fn set_palette_rgb(&mut self, intensity: u8, hue: u8, r: u8, g: u8, b: u8);
}

#[macro_export]
macro_rules! impl_dma_framebuffer {
    ($(
        $DMA_FRAMEBUFFERX:ident: $PACFRAMEBUFFERX:ty,
    )+) => {
        $(
            struct $DMA_FRAMEBUFFERX {
                registers: $PACFRAMEBUFFERX,
                framebuffer_base: *mut u32,
                h_active: u32,
                v_active: u32,
                rotate_90: bool,
            }

            impl hal::dma_display::DMAFramebuffer for $DMA_FRAMEBUFFERX {
                fn set_palette_rgb(&mut self, intensity: u8, hue: u8, r: u8, g: u8, b: u8)  {
                    /* wait until last coefficient written */ 
                    while self.registers.palette_busy().read().bits() == 1 { }
                    self.registers.palette().write(|w| unsafe {
                        w.position().bits(((intensity&0xF) << 4) | (hue&0xF));
                        w.red()     .bits(r);
                        w.green()   .bits(g);
                        w.blue()    .bits(b)
                    } );
                }
            }

            impl OriginDimensions for $DMA_FRAMEBUFFERX {
                fn size(&self) -> Size {
                    Size::new(self.h_active, self.v_active)
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
                        if let Ok((x, y)) = coord.try_into() {
                            if x >= 0 && x < self.h_active && y >= 0 && y < self.v_active {
                                let xf: u32 = if self.rotate_90 {self.v_active - y} else {x};
                                let yf: u32 = if self.rotate_90 {x}             else {y};
                                // Calculate the index in the framebuffer.
                                let index: u32 = (xf + yf * self.h_active) / 4;
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
