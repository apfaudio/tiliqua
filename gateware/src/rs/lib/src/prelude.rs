//! Common imports for firmware applications
//!
//! Use `use tiliqua_lib::prelude::*;` to import all common functionality
//! needed by firmware applications.

// Re-export all tiliqua crates
pub use tiliqua_hal::*;
pub use crate::*;
pub use opts::*;

// Common external crate re-exports for firmware convenience
pub use log::{debug, error, info, warn};
pub use embedded_hal::*;
pub use heapless::{String, Vec};
pub use micromath::F32Ext;
pub use strum::*;
pub use strum_macros::*;
pub use serde::{Deserialize, Serialize};
pub use fastrand;
pub use critical_section;
pub use irq;

// Common types that firmware apps frequently use
pub type HeaplessString<const N: usize> = heapless::String<N>;
pub type HeaplessVec<T, const N: usize> = heapless::Vec<T, N>;