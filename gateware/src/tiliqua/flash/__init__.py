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

This directory should have minimal code dependencies from this repository
besides some constants, as it will be re-used for the WebUSB flasher.
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

from ..build.types import N_MANIFESTS
from .archive_loader import ArchiveLoader
from .spiflash_layout import compute_concrete_regions_to_flash
from .spiflash_status import flash_status
from .openfpgaloader import *

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

    hw_rev_major = scan_for_tiliqua_hardware_version()
    if not isinstance(hw_rev_major, int):
        print("Could not find Tiliqua debugger.")
        print("Check it is turned on, plugged in ('dbg' port), permissions correct, and RP2040 firmware is up to date.")
        sys.exit(1)

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
