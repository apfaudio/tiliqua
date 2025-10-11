# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import subprocess
import tempfile
import unittest
from pathlib import Path

from tiliqua.build.archive import ArchiveBuilder, ArchiveLoader
from tiliqua.build.flash import (FlashCommandGenerator,
                                 compute_concrete_regions_to_flash)
from tiliqua.build.types import FirmwareLocation
from tiliqua.platform import TiliquaRevision


class TestFlashCommandGenerator(unittest.TestCase):

    def _print_regions_and_commands(self, flashable_regions, commands):
        """Helper to print regions and commands."""
        print(f"\n=== regions ===")
        for region in sorted(flashable_regions):
            print(f"{region}")

        print(f"\n=== commands ===")
        for cmd in commands:
            print(f"{' '.join(cmd)}")

    def setUp(self):
        """Set up test fixtures with temporary build directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.build_path = Path(self.temp_dir) / "build"
        self.build_path.mkdir()

        # Create test bitstream file
        self.bitstream_path = self.build_path / "top.bit"
        with open(self.bitstream_path, 'wb') as f:
            f.write(b'TEST_BITSTREAM' * 100)

        # Create test firmware file
        self.firmware_path = self.build_path / "firmware.bin"
        with open(self.firmware_path, 'wb') as f:
            f.write(b'TEST_FIRMWARE' * 50)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)

    def test_bootloader_archive_commands(self):

        archiver = ArchiveBuilder.for_project(
            build_path=str(self.build_path),
            name="BOOTLOADER",
            sha="abc123",
            hw_rev=TiliquaRevision.R5
        ).with_bitstream()                                                           \
         .with_firmware(str(self.firmware_path), FirmwareLocation.SPIFlash, 0xb0000) \

        archiver.create()

        with ArchiveLoader(archiver.archive_path) as loader:
            manifest = loader.get_manifest()
            (_concrete_manifest, flashable_regions) = compute_concrete_regions_to_flash(
                    manifest, slot=None)  # Bootloader
            generator = FlashCommandGenerator(flashable_regions)
            commands = generator.generate_commands()

            self._print_regions_and_commands(flashable_regions, commands)

            # Should have 3 commands: bitstream, firmware, manifest
            self.assertEqual(len(commands), 3)

            # Check bitstream command (first, at address 0x0)
            self.assertIn("0x0", commands[0])
            self.assertIn("--skip-reset", commands[0])
            self.assertIn("top.bit", " ".join(commands[0]))

            # Check firmware command (XIP firmware)
            self.assertIn("0xb0000", commands[1])
            self.assertIn("--skip-reset", commands[1])
            self.assertIn("firmware.bin", " ".join(commands[1]))

            # Last command should not have --skip-reset
            self.assertNotIn("--skip-reset", commands[2])

    def test_user_bitstream_without_firmware(self):

        archiver = ArchiveBuilder.for_project(
            build_path=str(self.build_path),
            name="USER_NO_FW",
            sha="def456",
            hw_rev=TiliquaRevision.R5
        ).with_bitstream()

        archiver.create()

        with ArchiveLoader(archiver.archive_path) as loader:
            manifest = loader.get_manifest()
            (_concrete_manifest, flashable_regions) = compute_concrete_regions_to_flash(
                    manifest, slot=1)  # User slot 1
            generator = FlashCommandGenerator(flashable_regions)
            commands = generator.generate_commands()

            self._print_regions_and_commands(flashable_regions, commands)

            # Should have 2 commands: bitstream, manifest
            self.assertEqual(len(commands), 2)

            # Check bitstream command (slot 1 starts at 0x200000)
            self.assertIn("0x200000", commands[0])
            self.assertIn("--skip-reset", commands[0])
            self.assertIn("top.bit", " ".join(commands[0]))

            # Last command should not have --skip-reset
            self.assertNotIn("--skip-reset", commands[1])

    def test_user_bitstream_with_firmware(self):

        archiver = ArchiveBuilder.for_project(
            build_path=str(self.build_path),
            name="USER_WITH_FW",
            sha="ghi789",
            hw_rev=TiliquaRevision.R5
        ).with_bitstream()                                                         \
         .with_firmware(str(self.firmware_path), FirmwareLocation.PSRAM, 0x200000) \
         .with_option_storage()

        archiver.create()

        with ArchiveLoader(archiver.archive_path) as loader:
            manifest = loader.get_manifest()
            (_concrete_manifest, flashable_regions) = compute_concrete_regions_to_flash(
                    manifest, slot=2)  # User slot 2
            generator = FlashCommandGenerator(flashable_regions)
            commands = generator.generate_commands()

            self._print_regions_and_commands(flashable_regions, commands)

            # Should have 3 commands: bitstream, firmware, manifest
            self.assertEqual(len(commands), 3)
            self.assertEqual(len(flashable_regions), 4)

            # Check bitstream command (slot 2 starts at 0x300000)
            self.assertIn("0x300000", commands[0])
            self.assertIn("--skip-reset", commands[0])
            self.assertIn("top.bit", " ".join(commands[0]))

            # Check firmware command (should be at firmware base for slot 2)
            self.assertIn("0x390000", commands[1])
            self.assertIn("--skip-reset", commands[1])
            self.assertIn("firmware.bin", " ".join(commands[1]))

            # Last command should not have --skip-reset
            self.assertNotIn("--skip-reset", commands[2])

    def test_manifest_rust_compatibility(self):
        """Test that a Python-generated manifest can be read by Rust lib.rs."""

        archiver = ArchiveBuilder.for_project(
            build_path=str(self.build_path),
            name="RUST_TEST",
            sha="abc123",
            hw_rev=TiliquaRevision.R5,
            brief="Test manifest for Rust compatibility"
        ).with_bitstream()                                                         \
         .with_firmware(str(self.firmware_path), FirmwareLocation.PSRAM, 0x200000) \
         .with_option_storage()

        # Create the archive and then load it to get the finalized manifest
        archiver.create()
        with ArchiveLoader(archiver.archive_path) as loader:
            manifest_json_path = loader.get_tmpdir() / "manifest.json"
            with open(manifest_json_path, 'r') as f:
                manifest_json = f.read()

        # Create a simple Rust test program to validate parsing
        rust_test = f'''
use tiliqua_manifest::BitstreamManifest;
fn main() {{
    let json_data = r#"{manifest_json}"#;
    let json_bytes = json_data.as_bytes();
    match BitstreamManifest::from_slice(json_bytes) {{
        Some(manifest) => {{
            println!("SUCCESS: Manifest parsed successfully");
            std::process::exit(0);
        }}
        None => {{
            println!("ERROR: Failed to parse manifest");
            std::process::exit(1);
        }}
    }}
}}
'''

        # Create a minimal Cargo project for the test
        test_dir = Path(self.temp_dir) / "rust_test"
        test_dir.mkdir()

        # Create Cargo.toml
        cargo_toml = f'''
[package]
name = "manifest_test"
version = "0.1.0"
edition = "2021"

[dependencies]
tiliqua-manifest = {{ path = "{Path(__file__).parent.parent / "src" / "rs" / "manifest"}" }}
'''
        with open(test_dir / "Cargo.toml", 'w') as f:
            f.write(cargo_toml)

        # Create src directory and main.rs
        src_dir = test_dir / "src"
        src_dir.mkdir()
        with open(src_dir / "main.rs", 'w') as f:
            f.write(rust_test)

        result = subprocess.run([
            'cargo', 'run'
        ], capture_output=True, text=True, cwd=test_dir)
        print(f"\nRust test output: {result.stdout}")
        if result.stderr:
            print(f"Rust test stderr: {result.stderr}")
        self.assertEqual(result.returncode, 0, "Rust parsing failed")
        self.assertIn("SUCCESS: Manifest parsed successfully", result.stdout)

if __name__ == '__main__':
    unittest.main()
