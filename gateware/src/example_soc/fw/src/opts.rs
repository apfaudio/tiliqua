use tiliqua_lib::opt::*;
use tiliqua_lib::impl_option_view;
use tiliqua_lib::impl_option_page;

use heapless::String;

use core::str::FromStr;

use strum_macros::{EnumIter, IntoStaticStr};

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
    pub decay: NumOption<u8>,
    pub scale: NumOption<u8>,
}

impl_option_view!(XbeamOptions,
                  persist, hue, intensity, decay, scale);

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
            modify: false,
            screen: EnumOption {
                name: String::from_str("screen").unwrap(),
                value: Screen::Xbeam,
            },
            xbeam: XbeamOptions {
                selected: Some(0),
                persist: NumOption{
                    name: String::from_str("persist").unwrap(),
                    value: 1024,
                    step: 256,
                    min: 512,
                    max: 32768,
                },
                hue: NumOption{
                    name: String::from_str("hue").unwrap(),
                    value: 10,
                    step: 1,
                    min: 0,
                    max: 15,
                },
                intensity: NumOption{
                    name: String::from_str("intensity").unwrap(),
                    value: 8,
                    step: 1,
                    min: 0,
                    max: 15,
                },
                decay: NumOption{
                    name: String::from_str("decay").unwrap(),
                    value: 1,
                    step: 1,
                    min: 0,
                    max: 15,
                },
                scale: NumOption{
                    name: String::from_str("scale").unwrap(),
                    value: 6,
                    step: 1,
                    min: 0,
                    max: 15,
                },
            },
        }
    }
}
