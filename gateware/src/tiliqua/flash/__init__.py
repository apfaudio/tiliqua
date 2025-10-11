# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Flash tool for Tiliqua bitstream archives.
See docs/gettingstarted.rst for usage.
See docs/bootloader.rst for implementation details and flash memory layout.

This tool unpacks a 'bitstream archive' containing a bitstream image,
firmware images and manifest describing the contents, and issues
`openFPGALoader` commands required for the Tiliqua bootloader to
correctly enter these bitstreams.

We must distinguish between XiP (bootloader) and non-XiP (psram, user)
bitstreams, as for user bitstreams the bootloader is responsible for
copying the firmware from SPIFlash to a desired region of PSRAM before
the user bitstream is started.

This should have minimal code dependencies from this repository besides some
constants, as it will be re-used for the WebUSB flasher.
"""

import argparse
import json
import os
import subprocess
import sys
import re
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional

from ..build.types import N_MANIFESTS, RegionType
from .archive_loader import ArchiveLoader
from .spiflash_layout import compute_concrete_regions_to_flash
from .spiflash_status import flash_status

class OpenFPGALoaderCommandSequence:

    """
    Generates the ``openFPGALoader`` commands needed in order
    to flash each region to the hardware.
    """

    def __init__(self, binary="openFPGALoader"):
        self._command_base = [binary, "-c", "dirtyJtag"]
        self._commands = []

    @staticmethod
    def from_flashable_regions(regions, erase_option_storage=False):
        sequence = OpenFPGALoaderCommandSequence()
        for region in regions:
            if region.memory_region.region_type == RegionType.OptionStorage:
                if erase_option_storage:
                    sequence = sequence.with_erase_cmd(region.addr, region.memory_region.size)
                continue
            sequence = sequence.with_flash_cmd(str(region.memory_region.filename), region.addr, "raw")
        return sequence

    @staticmethod
    def _create_erased_file(size: int) -> str:
        """
        Create a temporary file filled with 0xff bytes (erased flash state).
        This is used to erase sectors because openFPGALoader does not have such a command.
        """
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".erase.bin")
        try:
            with os.fdopen(fd, 'wb') as f:
                f.write(b'\xff' * size)
        except:
            os.close(fd)
            raise
        return path


    def with_flash_cmd(self, path: str, offset: int, file_type: str = "auto"):
        # Command to flash a file to a specific flash offset.
        # Add commands using a builder pattern:  o.with_flash_cmd(...).execute()
        cmd = self._command_base + [
            "-f", "-o", f"{hex(offset)}",
        ]
        if file_type != "auto":
            cmd.extend(["--file-type", file_type])
        cmd.append(path)
        self._commands.append(cmd)
        return self

    def with_erase_cmd(self, offset: int, size: int):
        # Command to flash 0xff*size bytes to offset (same as erasing)
        temp_file = self._create_erased_file(size)
        return self.with_flash_cmd(temp_file, offset, "raw")

    @property
    def commands(self):
        commands = self._commands.copy()
        # Add skip-reset flag to all but the last command
        if len(commands) > 1:
            for cmd in commands[:-1]:
                if "--skip-reset" not in cmd:
                    cmd.insert(-1, "--skip-reset")
        return commands

    def execute(self, cwd=None):
        """
        Execute flashing commands on the hardware.

        ``cwd`` should normally be the path to which the bitstream
        archive was extracted, so ``openFPGALoader`` can find the files
        that it needs to flash.
        """
        print("\nExecuting commands...")
        for cmd in self.commands:
            subprocess.check_call(cmd, cwd=cwd)

def scan_for_tiliqua():
    """
    Scan for a debugger with "apfbug" in the product name using openFPGALoader.
    Return the attached Tiliqua hardware version.
    """
    print("Scan for Tiliqua...")
    try:
        result = subprocess.run(
            ["openFPGALoader", "--scan-usb"],
            capture_output=True,
            text=True,
            check=True
        )
        output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running openFPGALoader: {e}")
        sys.exit(1)
    print(output)
    lines = output.strip().split('\n')
    for line in lines:
        if "apfbug" in line.lower() or "apf.audio" in line.lower():
            # Extract serial (16-char hex string) and product (contains "Tiliqua R#")
            serial_match = re.search(r'\b([A-F0-9]{16})\b', line)
            product_match = re.search(r'(Tiliqua\s+R\d+[^$]*)', line, re.IGNORECASE)
            if serial_match and product_match:
                serial = serial_match.group(1)
                product = product_match.group(1).strip()
                hw_version_match = re.search(r'R(\d+)', product)
                if hw_version_match:
                    hw_version = int(hw_version_match.group(1))
                    print(f"Found attached Tiliqua! (hw_rev={hw_version}, serial={serial})")
                    return hw_version
                else:
                    print("Found tiliqua-like device, product code is malformed (update RP2040?).")

    print("Could not find Tiliqua debugger.")
    print("Check it is turned on, plugged in ('dbg' port), permissions correct, and RP2040 firmware is up to date.")
    sys.exit(1)

def flash_archive(
    archive_path: str,
    hw_rev_major: int,
    slot: Optional[int] = None,
    noconfirm: bool = False,
    erase_option_storage: bool = False):

    with ArchiveLoader(archive_path) as loader:

        manifest = loader.manifest

        # Validate hardware compatibility

        if manifest.hw_rev != hw_rev_major:
            print(f"Aborting: attached Tiliqua (hw=r{hw_rev_major}) does not match archive (hw=r{manifest.hw_rev}).")
            sys.exit(1)

        # Error out if we flash to the wrong kind of slot

        is_bootloader = loader.is_bootloader_archive()
        if is_bootloader and slot is not None:
            print("Error: bootloader bitstream must be flashed to bootloader slot")
            print(f"Remove --slot argument to flash to bootloader slot.")
            sys.exit(1)
        elif not is_bootloader and slot is None:
            print("Error: Must specify slot for user bitstreams")
            sys.exit(1)

        # Assign real SPI flash addresses to memory regions that must exist
        # in the SPI flash (but could not have their addresses calculated until now,
        # as we didn't know which slot the bitstream would land in).

        (concrete_manifest, regions_to_flash) = compute_concrete_regions_to_flash(
            manifest, slot)

        # Write the concrete manifest back to our extracted archive path.
        # So that it is the one actually flashed to the device.

        with open(loader.tmpdir / "manifest.json", "w") as f:
            manifest_dict = concrete_manifest.to_dict()
            print(f"\nFinal manifest contents:\n{json.dumps(manifest_dict, indent=2)}")
            json.dump(manifest_dict, f)

        print("\nRegions to flash:")
        for region in sorted(regions_to_flash):
            print(f"  {region}")

        # Generate and execute flashing commands (with optional confirmation)

        sequence = OpenFPGALoaderCommandSequence.from_flashable_regions(
            regions_to_flash, erase_option_storage)

        print("\nThe following commands will be executed:")
        for cmd in sequence.commands:
            print(f"\t$ {' '.join(cmd)}")

        def confirm_operation():
            response = input("\nProceed with flashing? [y/N] ")
            return response.lower() == 'y'

        if not noconfirm and not confirm_operation():
            print("Aborting.")
            sys.exit(0)

        sequence.execute(cwd=loader.tmpdir)

def main():
    parser = argparse.ArgumentParser(description="Flash Tiliqua bitstream archives")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Flash a bitstream archive')
    archive_parser.add_argument("archive_path", help="Path to bitstream archive (.tar.gz)")
    archive_parser.add_argument("--slot", type=int, help="Slot number (0-7) for bootloader-managed bitstreams")
    archive_parser.add_argument("--noconfirm", action="store_true", help="Do not ask for confirmation before flashing")
    archive_parser.add_argument("--erase-option-storage", action="store_true", help="Erase option storage regions in the manifest")

    # Status command
    subparsers.add_parser('status', help='Display current bitstream status')

    args = parser.parse_args()

    hw_rev_major = scan_for_tiliqua()

    match args.command:
        case 'archive':
            if not os.path.exists(args.archive_path):
                print(f"Error: Archive not found: {args.archive_path}")
                sys.exit(1)
            if args.slot is not None and not 0 <= args.slot < N_MANIFESTS:
                print(f"Error: Slot must be between 0 and {N_MANIFESTS-1}")
                sys.exit(1)
            flash_archive(args.archive_path, hw_rev_major, args.slot, args.noconfirm, args.erase_option_storage)
        case 'status':
            flash_status()


if __name__ == "__main__":
    main()
