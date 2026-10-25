use core::marker::PhantomData;

use embedded_hal::delay::DelayNs;
use riscv_peripheral::aclint::{Clint, CLINT};

#[macro_export]
macro_rules! impl_clint {
    ($(
        $CLINTX:ident: $BASE:expr, $FREQ:expr,
    )+) => {
        $(
            #[derive(Clone, Copy, Debug)]
            pub struct $CLINTX;

            unsafe impl $crate::riscv_peripheral::aclint::Clint for $CLINTX {
                const BASE: usize = $BASE;
                const MTIME_FREQ: usize = $FREQ;
            }

            impl $CLINTX {
                pub fn mtime() -> u64 {
                    $crate::clint::mtime::<Self>()
                }

                pub fn delay() -> $crate::clint::Delay<Self> {
                    $crate::clint::Delay::new()
                }
            }
        )+
    };
}

#[expect(clippy::undocumented_unsafe_blocks)]
pub fn mtime<C: Clint>() -> u64 {
    let lo = CLINT::<C>::new().mtimer().mtime().get_register().get_ptr().cast::<u32>();
    let hi = lo.wrapping_add(1);
    loop {
        let (h1, l, h2) = unsafe { (hi.read_volatile(), lo.read_volatile(), hi.read_volatile()) };
        if h1 == h2 {
            return (u64::from(h1) << 32) | u64::from(l);
        }
    }
}

#[expect(clippy::undocumented_unsafe_blocks)]
pub fn set_mtimecmp<C: Clint>(val: u64) {
    let lo = CLINT::<C>::new().mtimer().mtimecmp_mhartid().get_register().get_ptr().cast::<u32>();
    let hi = lo.wrapping_add(1);
    unsafe {
        lo.write_volatile(u32::MAX);
        hi.write_volatile((val >> 32) as u32);
        lo.write_volatile(val as u32);
    }
}

pub struct Delay<C: Clint>(PhantomData<C>);

impl<C: Clint> Delay<C> {
    pub const fn new() -> Self {
        Self(PhantomData)
    }
}

impl<C: Clint> Default for Delay<C> {
    fn default() -> Self {
        Self::new()
    }
}

impl<C: Clint> DelayNs for Delay<C> {
    fn delay_ns(&mut self, ns: u32) {
        let t0 = mtime::<C>();
        let ticks = (u64::from(ns) * C::MTIME_FREQ as u64).div_ceil(1_000_000_000) + 1;
        while mtime::<C>().wrapping_sub(t0) < ticks {}
    }
}
