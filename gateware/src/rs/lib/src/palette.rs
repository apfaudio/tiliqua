use tiliqua_hal::dma_framebuffer::DMAFramebuffer;

use strum_macros::{EnumIter, IntoStaticStr};

use micromath::F32Ext;

// TODO: take this dynamically from DMAFramebuffer configuration.
pub const PX_HUE_MAX: i32 = 16;
pub const PX_INTENSITY_MAX: i32 = 16;

#[derive(Default, Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
#[strum(serialize_all = "kebab-case")]
pub enum ColorPalette {
    Exp,
    #[default]
    Linear,
    Gray,
    InvGray,
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
            ColorPalette::Gray => {
                let gray: u8 = (i * 16) as u8;
                RGB { r: gray, g: gray, b: gray }
            },
            ColorPalette::InvGray => {
                let gray: u8 = 255u8 - (i * 16) as u8;
                RGB { r: gray, g: gray, b: gray }
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
