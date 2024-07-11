use embedded_graphics::{
    pixelcolor::{Gray8, GrayColor},
    primitives::{PrimitiveStyleBuilder, Line},
    mono_font::{ascii::FONT_9X15, ascii::FONT_9X15_BOLD, MonoTextStyle},
    text::{Alignment, Text},
    prelude::*,
};

use crate::opt;

pub fn draw_options<D, O>(d: &mut D, opts: &O,
                       pos_x: u32, pos_y: u32, hue: u8) -> Result<(), D::Error>
where
    D: DrawTarget<Color = Gray8>,
    O: opt::OptionPage
{
    let font_small_white = MonoTextStyle::new(&FONT_9X15_BOLD, Gray8::WHITE);
    let font_small_grey = MonoTextStyle::new(&FONT_9X15, Gray8::new(0xB0 + hue));

    let opts_view = opts.view().options();

    let vx = pos_x as i32;
    let vy = pos_y as usize;
    let vspace: usize = 18;
    let hspace: i32 = 150;

    let screen_hl = match (opts.view().selected(), opts.modify()) {
        (None, _) => true,
        _ => false,
    };

    Text::with_alignment(
        &opts.screen().value(),
        Point::new(vx-12, vy as i32),
        if screen_hl { font_small_white } else { font_small_grey },
        Alignment::Right
    ).draw(d)?;

    if screen_hl && opts.modify() {
        Text::with_alignment(
            "^",
            Point::new(vx-12, (vy + vspace) as i32),
            font_small_white,
            Alignment::Right,
        ).draw(d)?;
    }

    let vx = vx-2;

    for (n, opt) in opts_view.iter().enumerate() {
        let mut font = font_small_grey;
        if let Some(n_selected) = opts.view().selected() {
            if n_selected == n {
                font = font_small_white;
                if opts.modify() {
                    Text::with_alignment(
                        "<",
                        Point::new(vx+hspace+2, (vy+vspace*n) as i32),
                        font,
                        Alignment::Left,
                    ).draw(d)?;
                }
            }
        }
        Text::with_alignment(
            opt.name(),
            Point::new(vx+5, (vy+vspace*n) as i32),
            font,
            Alignment::Left,
        ).draw(d)?;
        Text::with_alignment(
            &opt.value(),
            Point::new(vx+hspace, (vy+vspace*n) as i32),
            font,
            Alignment::Right,
        ).draw(d)?;
    }

    let stroke = PrimitiveStyleBuilder::new()
        .stroke_color(Gray8::new(0xB0 + hue))
        .stroke_width(1)
        .build();
    Line::new(Point::new(vx-3, vy as i32 - 10),
              Point::new(vx-3, (vy - 13 + vspace*opts_view.len()) as i32))
              .into_styled(stroke)
              .draw(d)?;

    Ok(())
}

#[cfg(test)]
mod test_data {

    // Fake set of options for quick render testing

    use heapless::String;
    use core::str::FromStr;
    use strum_macros::{EnumIter, IntoStaticStr};

    use crate::opt::*;
    use crate::impl_option_view;
    use crate::impl_option_page;

    #[derive(Clone, Copy, PartialEq, EnumIter, IntoStaticStr)]
    #[strum(serialize_all = "SCREAMING-KEBAB-CASE")]
    pub enum Screen {
        Xbeam,
    }

    #[derive(Clone)]
    pub struct XbeamOptions {
        pub selected: Option<usize>,
        pub persist: NumOption<u16>,
        pub hue: NumOption<u8>,
        pub intensity: NumOption<u8>,
    }

    impl_option_view!(XbeamOptions,
                      persist, hue, intensity);

    #[derive(Clone)]
    pub struct Options {
        pub modify: bool,
        pub screen: EnumOption<Screen>,

        pub xbeam: XbeamOptions,
    }


    impl_option_page!(Options,
                      (Screen::Xbeam, xbeam));

    impl Options {
        pub fn new() -> Options {
            Options {
                modify: true,
                screen: EnumOption {
                    name: String::from_str("screen").unwrap(),
                    value: Screen::Xbeam,
                },
                xbeam: XbeamOptions {
                    selected: None,
                    persist: NumOption{
                        name: String::from_str("persist").unwrap(),
                        value: 1024,
                        step: 256,
                        min: 512,
                        max: 32768,
                    },
                    hue: NumOption{
                        name: String::from_str("hue").unwrap(),
                        value: 0,
                        step: 1,
                        min: 0,
                        max: 15,
                    },
                    intensity: NumOption{
                        name: String::from_str("intensity").unwrap(),
                        value: 6,
                        step: 1,
                        min: 0,
                        max: 15,
                    },
                },
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    use image::{ImageBuffer, RgbImage, Rgb};

    const H_ACTIVE: u32 = 800;
    const V_ACTIVE: u32 = 600;

    struct FakeDisplay {
        img: RgbImage,
    }

    impl DrawTarget for FakeDisplay {
        type Color = Gray8;
        type Error = core::convert::Infallible;

        fn draw_iter<I>(&mut self, pixels: I) -> Result<(), Self::Error>
        where
            I: IntoIterator<Item = Pixel<Self::Color>>,
        {
            for Pixel(coord, color) in pixels.into_iter() {
                if let Ok((x @ 0..=H_ACTIVE, y @ 0..=V_ACTIVE)) = coord.try_into() {
                    *self.img.get_pixel_mut(x, y) = Rgb([
                        color.luma(),
                        color.luma(),
                        color.luma()
                    ]);
                }
            }

            Ok(())
        }
    }

    impl OriginDimensions for FakeDisplay {
        fn size(&self) -> Size {
            Size::new(H_ACTIVE, V_ACTIVE)
        }
    }

    #[test]
    fn draw_screen() {
        use crate::opt::OptionPageEncoderInterface;

        let mut disp = FakeDisplay {
            img: ImageBuffer::new(H_ACTIVE, V_ACTIVE)
        };

        let mut opts = test_data::Options::new();
        opts.tick_up();
        opts.toggle_modify();
        opts.tick_up();
        opts.toggle_modify();

        disp.img = ImageBuffer::new(H_ACTIVE, V_ACTIVE);
        draw_options(&mut disp, &opts, H_ACTIVE-200, V_ACTIVE-100, 0).ok();
        disp.img.save("draw_opt_test.png").unwrap();
    }

}
