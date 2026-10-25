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
                pub fn delay() -> $crate::riscv_peripheral::aclint::mtimer::MTIMER<Self> {
                    $crate::riscv_peripheral::aclint::CLINT::<Self>::new().mtimer()
                }
            }
        )+
    };
}
