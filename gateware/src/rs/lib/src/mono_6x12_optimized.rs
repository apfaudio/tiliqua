use tiliqua_hal::embedded_graphics::{
    mono_font::{MonoFont, mapping::StrGlyphMapping, DecorationDimensions},
    image::ImageRaw,
    geometry::Size,
};

pub const MONO_6X12_OPTIMIZED: MonoFont = MonoFont {
    image: ImageRaw::new_const(
        include_bytes!("raw/mono_6x12_optimized.data"),
        Size::new(96u32, 264u32),
    ),
    glyph_mapping: &StrGlyphMapping::new(
        "\0 ~\0─◿",
        31usize,
    ),
    character_size: Size::new(6u32, 12u32),
    character_spacing: 0u32,
    baseline: 9u32,
    underline: DecorationDimensions::new(11u32, 1u32),
    strikethrough: DecorationDimensions::new(6u32, 1u32),
};
