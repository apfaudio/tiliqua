# quick and dirty script to run clippy lints on firmware crates
# outside the main rs/lib/hal workspace. maybe this will become
# unnecessary if/once I decide to move all toplevels into their
# own repo

import argparse
import os
import subprocess
import sys
import tomllib
from pathlib import Path

GATEWARE = Path(__file__).resolve().parent.parent
WORKSPACE = GATEWARE / "src" / "rs"
TOP = GATEWARE / "src" / "top"

FIRMWARE_LINTS = {
    "infinite_loop": "allow",
    "undocumented_unsafe_blocks": "allow",
}

def lint_flags():
    lints = tomllib.loads((WORKSPACE / "Cargo.toml").read_text())["workspace"]["lints"]["clippy"]
    lints = {name: spec if isinstance(spec, dict) else {"level": spec} for name, spec in lints.items()}
    ordered = sorted(lints.items(), key=lambda kv: kv[1].get("priority", 0))
    entries = [(name, spec["level"]) for name, spec in ordered] + list(FIRMWARE_LINTS.items())
    return [f"--{level}=clippy::{name}" for name, level in entries]


def run(cmd, cwd, shown=None):
    print(f"$ (cd {cwd.relative_to(GATEWARE)} && {' '.join(shown or cmd)})", flush=True)
    return subprocess.run(cmd, cwd=cwd).returncode == 0


def main():
    parser = argparse.ArgumentParser(description="Run clippy on the rs workspace and all SoC firmware.")
    parser.add_argument("--deny-warnings", action="store_true",
                        help="Fail on any warning.")
    parser.add_argument("--generate-pacs", action="store_true",
                        help="Generate missing firmware PACs instead of skipping their firmware.")
    parser.add_argument("--firmware-only", action="store_true",
                        help="Skip the rs workspace and only lint firmware.")
    args = parser.parse_args()

    os.environ["CLIPPY_CONF_DIR"] = str(WORKSPACE)
    deny = ["-D", "warnings"] if args.deny_warnings else []
    ok = True

    if not args.firmware_only:
        ok &= run(["cargo", "clippy", "--workspace", "--all-targets", "--all-features", "--"] + deny, WORKSPACE)
        ok &= run(["cargo", "clippy", "--target", "riscv32im-unknown-none-elf", "--"] + deny, WORKSPACE / "hal")

    flags = lint_flags()
    skipped = []
    for manifest in sorted(TOP.glob("*/fw/Cargo.toml")):
        fw = manifest.parent
        name = fw.parent.name
        if not (fw.parent / "pac" / "src" / "generated.rs").exists():
            if not args.generate_pacs:
                skipped.append(name)
                continue
            if not run([sys.executable, str(TOP / name / "top.py"), "build", "--pac-only"], GATEWARE):
                ok = False
                continue
        cmd = ["cargo", "clippy", "--release", "--"]
        ok &= run(cmd + flags + deny, fw, cmd + ["<workspace lints>"] + deny)

    if skipped:
        print(f"skipped (PAC not generated, use --generate-pacs): {', '.join(skipped)}")

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
