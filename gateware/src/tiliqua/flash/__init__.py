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
import colorama
import json
import os
import sys
from colorama import Fore, Style
from typing import Optional

from ..build.types import N_MANIFESTS
from .archive_loader import ArchiveLoader
from .spiflash_layout import compute_concrete_regions_to_flash
from .spiflash_status import flash_status
from .openfpgaloader import *

def flash_archive(args, detected_hw_rev: int):

    slot = args.slot

    with ArchiveLoader(args.archive_path) as loader:

        manifest = loader.manifest

        # Validate hardware compatibility

        if manifest.hw_rev != detected_hw_rev:
            print(f"Aborting: attached Tiliqua (hw=r{detected_hw_rev}) does not match archive (hw=r{manifest.hw_rev}).")
            sys.exit(1)

        # Error out if we flash to the wrong kind of slot

        is_bootloader = loader.is_bootloader_archive()
        if is_bootloader and slot is not None:
            print("Error: bootloader bitstream must be flashed to bootloader region")
            print(f"Remove `--slot` argument to flash to bootloader region.")
            sys.exit(1)
        elif not is_bootloader and slot is None:
            print("Error: Please specify target `--slot` for user bitstreams")
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
            if args.dump_manifest:
                print(f"\nManifest (for slot={slot}), with concrete flash layout:")
                print(f"{Style.DIM}{json.dumps(manifest_dict, indent=2)}{Style.RESET_ALL}")
            json.dump(manifest_dict, f)

        print(f"\nFlash layout (for slot = {slot}):")
        for region in sorted(regions_to_flash):
            print(f"  {region}")

        # Generate and execute flashing commands (with optional confirmation)

        sequence = OpenFPGALoaderCommandSequence.from_flashable_regions(
            regions_to_flash, args.erase_option_storage)

        print("\nThe following commands will be executed:")
        print(f"{Fore.BLUE}{Style.BRIGHT}")
        for cmd in sequence.commands:
            print(f"\t$ {' '.join(cmd)}")
        print(Style.RESET_ALL)

        def confirm_operation():
            response = input("Proceed with flashing? [y/N] ")
            return response.lower() == 'y'

        if not args.noconfirm and not confirm_operation():
            print("Aborting.")
            sys.exit(0)

        sequence.execute(cwd=loader.tmpdir)

def main():

    colorama.init()

    parser = argparse.ArgumentParser(description="Flash Tiliqua bitstream archives")
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Archive command
    archive_parser = subparsers.add_parser('archive', help='Flash a bitstream archive')
    archive_parser.add_argument("archive_path", help="Path to bitstream archive (.tar.gz)")
    archive_parser.add_argument("--slot", type=int, help="Slot number (0-7) for bootloader-managed bitstreams")
    archive_parser.add_argument("--noconfirm", action="store_true", help="Do not ask for confirmation before flashing")
    archive_parser.add_argument("--erase-option-storage", action="store_true", help="Erase option storage regions in the manifest")
    archive_parser.add_argument("--dump-manifest", action="store_true", help="Dump the final JSON manifest before flashing it.")

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
            flash_archive(args, detected_hw_rev=hw_rev_major)
        case 'status':
            flash_status()


if __name__ == "__main__":
    main()
