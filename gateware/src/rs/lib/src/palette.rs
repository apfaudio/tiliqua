use tiliqua_hal::dma_framebuffer::DMAFramebuffer;
use serde_derive::{Serialize, Deserialize};

use strum_macros::{EnumIter, IntoStaticStr};

use micromath::F32Ext;

// TODO: take this dynamically from DMAFramebuffer configuration.
pub const PX_HUE_MAX: i32 = 16;
pub const PX_INTENSITY_MAX: i32 = 16;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr, Serialize, Deserialize)]
#[strum(serialize_all = "kebab-case")]
pub enum ColorPalette {
    Exp,
    #[default]
    Linear,
    Dim,
    Gray,
    InvGray,
    Inferno,
    Hueswap,
}

fn hue2rgb(p: f32, q: f32, mut t: f32) -> f32 {
    if t < 0.0 {
        t += 1.0;
    }
    if t > 1.0 {
        t -= 1.0;
    }
    if t < 1.0 / 6.0 {
        return p + (q - p) * 6.0 * t;
    }
    if t < 0.5 {
        return q;
    }
    if t < 2.0 / 3.0 {
        return p + (q - p) * (2.0 / 3.0 - t) * 6.0;
    }
    p
}

pub struct RGB {
    pub r: u8,
    pub g: u8,
    pub b: u8,
}

/// Converts an HSL color value to RGB. Conversion formula
/// adapted from http://en.wikipedia.org/wiki/HSL_color_space.
/// Assumes h, s, and l are contained in the set [0, 1] and
/// returns RGB in the set [0, 255].
pub fn hsl2rgb(h: f32, s: f32, l: f32) -> RGB {
    if s == 0.0 {
        // achromatic
        let gray = (l * 255.0) as u8;
        return RGB { r: gray, g: gray, b: gray };
    }

    let q = if l < 0.5 {
        l * (1.0 + s)
    } else {
        l + s - l * s
    };
    let p = 2.0 * l - q;

    RGB {
        r: (hue2rgb(p, q, h + 1.0 / 3.0) * 255.0) as u8,
        g: (hue2rgb(p, q, h) * 255.0) as u8,
        b: (hue2rgb(p, q, h - 1.0 / 3.0) * 255.0) as u8,
    }
}


impl ColorPalette {
    pub fn default() -> Self {
        ColorPalette::Linear
    }

    fn compute_color(&self, i: i32, h: i32) -> RGB {
        let n_i: i32 = PX_INTENSITY_MAX;
        let n_h: i32 = PX_HUE_MAX;
        match self {
            ColorPalette::Exp => {
                let fac = 1.35f32;
                let hue = (h as f32)/(n_h as f32);
                let saturation = 0.9f32;
                let intensity = fac.powi(i+1) / fac.powi(n_i);
                hsl2rgb(hue, saturation, intensity)
            },
            ColorPalette::Linear => {
                hsl2rgb((h as f32)/(n_h as f32), 0.9f32,
                        (i as f32)/(n_h as f32))
            },
            ColorPalette::Dim => {
                let rgb = hsl2rgb((h as f32)/(n_h as f32), 0.9f32,
                                  (i as f32)/(n_h as f32));
                RGB { r: rgb.r / 2, g: rgb.g / 2, b: rgb.b / 2 }
            },
            ColorPalette::Gray => {
                let gray: u8 = (i * 16) as u8;
                RGB { r: gray, g: gray, b: gray }
            },
            ColorPalette::InvGray => {
                let gray: u8 = 255u8 - (i * 16) as u8;
                RGB { r: gray, g: gray, b: gray }
            },
            ColorPalette::Inferno => {
                // Inferno colormap from matplotlib, sampled at 16 points
                // Maps intensity to color, ignoring hue (sequential colormap)
                const INFERNO: [(u8, u8, u8); 16] = [
                    (0, 0, 4),
                    (10, 7, 34),
                    (32, 12, 74),
                    (60, 9, 101),
                    (87, 16, 110),
                    (114, 25, 110),
                    (140, 41, 99),
                    (165, 62, 79),
                    (187, 86, 57),
                    (206, 114, 36),
                    (222, 143, 17),
                    (234, 176, 5),
                    (242, 210, 37),
                    (248, 238, 85),
                    (252, 252, 139),
                    (252, 255, 164),
                ];
                let (r, g, b) = INFERNO[i as usize];
                RGB { r, g, b }
            },
            ColorPalette::Hueswap => {
                // Like Linear but with intensity and hue axes swapped
                // Lowest intensity level (i=0) is black
                if i == 0 {
                    RGB { r: 0, g: 0, b: 0 }
                } else {
                    hsl2rgb((i as f32)/(n_i as f32), 0.9f32,
                            (h as f32)/(n_h as f32))
                }
            }
        }
    }

    pub fn write_to_hardware(&self, video: &mut impl DMAFramebuffer) {
        for i in 0..PX_INTENSITY_MAX {
            for h in 0..PX_HUE_MAX {
                let rgb = self.compute_color(i, h);
                video.set_palette_rgb(i as u8, h as u8, rgb.r, rgb.g, rgb.b);
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use image::{ImageBuffer, RgbImage, Rgb};
    use strum::IntoEnumIterator;

    const BLOCK_SIZE: u32 = 8;

    /// Test to draw every pallette to an image file for previewing.
    #[test]
    fn test_plot_all_palettes() {
        let width = PX_HUE_MAX as u32 * BLOCK_SIZE;
        let height = PX_INTENSITY_MAX as u32 * BLOCK_SIZE;
        for palette in ColorPalette::iter() {
            let mut img: RgbImage = ImageBuffer::new(width, height);
            for h in 0..PX_HUE_MAX {
                for i in 0..PX_INTENSITY_MAX {
                    let rgb = palette.compute_color(i, h);
                    let pixel = Rgb([rgb.r, rgb.g, rgb.b]);
                    let x_start = h as u32 * BLOCK_SIZE;
                    let y_start = (PX_INTENSITY_MAX as u32 - 1 - i as u32) * BLOCK_SIZE;
                    for dy in 0..BLOCK_SIZE {
                        for dx in 0..BLOCK_SIZE {
                            img.put_pixel(x_start + dx, y_start + dy, pixel);
                        }
                    }
                }
            }

            let palette_name: &'static str = palette.into();
            let filename = format!("palette_{}.png", palette_name);
            img.save(&filename).unwrap();
        }
    }
}
