# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest
import tempfile
from pathlib import Path

from tiliqua.flash import FlashCommandGenerator, promote_to_flashable_regions
from tiliqua.archive import ArchiveBuilder, ArchiveLoader
from tiliqua.types import FirmwareLocation
from tiliqua.tiliqua_platform import TiliquaRevision


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
        """Test flash commands for bootloader archive (XIP firmware)."""
        archiver = ArchiveBuilder.for_project(
            build_path=str(self.build_path),
            name="BOOTLOADER",
            sha="abc123",
            hw_rev=TiliquaRevision.R5
        ).with_bitstream().with_firmware(str(self.firmware_path), FirmwareLocation.SPIFlash, 0xb0000)
        
        archiver.create()
        
        with ArchiveLoader(archiver.archive_path) as loader:
            flashable_regions = promote_to_flashable_regions(loader, slot=None)  # Bootloader
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
        """Test flash commands for user bitstream without firmware."""
        archiver = ArchiveBuilder.for_project(
            build_path=str(self.build_path),
            name="USER_NO_FW",
            sha="def456",
            hw_rev=TiliquaRevision.R5
        ).with_bitstream()
        
        archiver.create()
        
        with ArchiveLoader(archiver.archive_path) as loader:
            flashable_regions = promote_to_flashable_regions(loader, slot=1)  # User slot 1
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
        """Test flash commands for user bitstream with PSRAM firmware."""
        archiver = ArchiveBuilder.for_project(
            build_path=str(self.build_path),
            name="USER_WITH_FW",
            sha="ghi789",
            hw_rev=TiliquaRevision.R5
        ).with_bitstream().with_firmware(str(self.firmware_path), FirmwareLocation.PSRAM, 0x200000).with_option_storage()
        
        archiver.create()
        
        with ArchiveLoader(archiver.archive_path) as loader:
            flashable_regions = promote_to_flashable_regions(loader, slot=2)  # User slot 2
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
            self.assertIn("0x3b0000", commands[1])
            self.assertIn("--skip-reset", commands[1])
            self.assertIn("firmware.bin", " ".join(commands[1]))
            
            # Last command should not have --skip-reset
            self.assertNotIn("--skip-reset", commands[2])

if __name__ == '__main__':
    unittest.main()
