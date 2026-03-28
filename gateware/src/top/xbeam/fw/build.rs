fn main() {
    println!("cargo::rustc-check-cfg=cfg(expander_ex0)");
    println!("cargo::rustc-check-cfg=cfg(expander_ex1)");
    if std::env::var("TILIQUA_EXPANDER_EX0").ok().as_deref() == Some("1") {
        println!("cargo:rustc-cfg=expander_ex0");
    }
    if std::env::var("TILIQUA_EXPANDER_EX1").ok().as_deref() == Some("1") {
        println!("cargo:rustc-cfg=expander_ex1");
    }
    println!("cargo:rerun-if-env-changed=TILIQUA_EXPANDER_EX0");
    println!("cargo:rerun-if-env-changed=TILIQUA_EXPANDER_EX1");
}
