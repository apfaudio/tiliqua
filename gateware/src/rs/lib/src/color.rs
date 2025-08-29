use tiliqua_hal::embedded_graphics::pixelcolor::{PixelColor, raw::{RawU8, RawData}};

/// Tiliqua hardware color type representing hue and intensity.
///
/// This color type matches the hardware pixel format used by Tiliqua:
/// - Upper 4 bits (7:4): Intensity/brightness (0-15)
/// - Lower 4 bits (3:0): Hue index (0-15)
///
/// The intensity controls brightness where:
/// - Intensity 0: Always black (regardless of hue)
/// - Intensity 15: Always white (regardless of hue)
/// - Intensity 10: Standard palette colors are visible
///
/// Standard hues at intensity 10:
/// - Hue 0: Red
/// - Hue 1: Orange  
/// - Hue 2: Yellow
/// - Hue 4: Green
/// - Hue 10: Blue
#[derive(Copy, Clone, Eq, PartialEq, Ord, PartialOrd, Hash, Debug, Default)]
pub struct TiliquaColor(RawU8);

impl TiliquaColor {
    /// Creates a new Tiliqua color from separate hue and intensity values.
    ///
    /// # Arguments
    /// * `hue` - Hue index (0-15), values > 15 are masked
    /// * `intensity` - Brightness level (0-15), values > 15 are masked
    ///   - 0 = always black
    ///   - 15 = always white  
    ///   - 10 = standard palette color visibility
    ///
    /// # Examples
    /// ```
    /// # use tiliqua_lib::color::TiliquaColor;
    /// let red = TiliquaColor::new(0, 10);        // Red at standard intensity
    /// let bright_blue = TiliquaColor::new(10, 15);  // Blue hue at white intensity
    /// let dim_green = TiliquaColor::new(4, 6);      // Green hue at dim intensity
    /// ```
    pub const fn new(hue: u8, intensity: u8) -> Self {
        let hue = hue & 0x0F;
        let intensity = intensity & 0x0F;
        Self(RawU8::new((intensity << 4) | hue))
    }
    
    /// Creates a new Tiliqua color from a raw 8-bit value.
    ///
    /// This is useful when working with data that's already in the hardware format.
    pub const fn from_raw(raw: u8) -> Self {
        Self(RawU8::new(raw))
    }
    
    /// Returns the hue component (0-15).
    pub fn hue(self) -> u8 {
        self.0.into_inner() & 0x0F
    }
    
    /// Returns the intensity/brightness component (0-15).  
    pub fn intensity(self) -> u8 {
        (self.0.into_inner() >> 4) & 0x0F
    }
    
    /// Returns the raw 8-bit representation matching hardware format.
    pub fn to_raw(self) -> u8 {
        self.0.into_inner()
    }
    
    /// Creates a standard palette color at standard intensity (10).
    ///
    /// This gives you the "true" colors as they appear in the standard palette.
    pub const fn palette_color(hue: u8) -> Self {
        Self::new(hue, 10)
    }
    
    /// Creates a color with the specified hue and adds a hue offset.
    ///
    /// This is useful for creating color variations based on a base hue.
    /// The hue parameter is added to the base hue index (with wraparound).
    pub fn with_hue_offset(self, hue_offset: u8) -> Self {
        Self::new(self.hue().wrapping_add(hue_offset), self.intensity())
    }
    
    /// Adjusts the intensity while keeping the same hue.
    pub fn with_intensity(self, intensity: u8) -> Self {
        Self::new(self.hue(), intensity)
    }
    
    // Common color constants
    
    /// Black color (intensity 0).
    pub const BLACK: Self = Self::new(0, 0);
    
    /// White color (intensity 15).
    pub const WHITE: Self = Self::new(0, 15);
    
    /// Standard palette colors (intensity 10)
    
    /// Red at standard palette intensity.
    pub const RED: Self = Self::new(0, 10);
    
    /// Orange at standard palette intensity.
    pub const ORANGE: Self = Self::new(1, 10);
    
    /// Yellow at standard palette intensity.
    pub const YELLOW: Self = Self::new(2, 10);
    
    /// Green at standard palette intensity.
    pub const GREEN: Self = Self::new(4, 10);
    
    /// Blue at standard palette intensity.
    pub const BLUE: Self = Self::new(10, 10);
}

/// Implement PixelColor trait to make TiliquaColor usable with embedded-graphics.
impl PixelColor for TiliquaColor {
    type Raw = RawU8;
}

/// Convert from RawU8 to TiliquaColor (required for image support).
impl From<RawU8> for TiliquaColor {
    fn from(raw: RawU8) -> Self {
        Self(raw)
    }
}

/// Convert from TiliquaColor to RawU8 (required for framebuffer support).
impl From<TiliquaColor> for RawU8 {
    fn from(color: TiliquaColor) -> Self {
        color.0
    }
}

/// Conversion from raw u8 for convenience.
impl From<u8> for TiliquaColor {
    fn from(raw: u8) -> Self {
        Self::from_raw(raw)
    }
}

/// Conversion to raw u8 for convenience.
impl From<TiliquaColor> for u8 {
    fn from(color: TiliquaColor) -> Self {
        color.to_raw()
    }
}