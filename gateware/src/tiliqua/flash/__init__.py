#!/usr/bin/env python3

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

from ..build.types import RegionType
from .archive_loader import ArchiveLoader
from .spiflash_layout import compute_concrete_regions_to_flash
from .spiflash_status import flash_status

def scan_for_tiliqua():
    """
    Scan for a debugger with "apfbug" in the product name using openFPGALoader.
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

class FlashCommandGenerator:
    """Generates and executes flash commands."""

    def __init__(self, regions_to_flash):
        self.regions_to_flash = sorted(regions_to_flash)

    def generate_commands(self, erase_option_storage: bool = False) -> List[List[str]]:
        """Generate flash commands for all regions."""
        commands = []
        for region in self.regions_to_flash:
            if region.memory_region.region_type == RegionType.OptionStorage:
                # Handle OptionStorage regions based on erase_option_storage flag
                if erase_option_storage:
                    temp_file = create_erased_file(region.memory_region.size)
                    commands.append(flash_file(temp_file, region.addr, "raw"))
                continue
            # Use the pre-calculated file path
            commands.append(flash_file(str(region.memory_region.filename), region.addr, "raw"))
        # Add skip-reset flag to all but the last command
        if len(commands) > 1:
            for cmd in commands[:-1]:
                if "--skip-reset" not in cmd:
                    cmd.insert(-1, "--skip-reset")
        return commands

    def execute_commands(self, commands: List[List[str]], cwd=None):
        """Execute all flash commands."""
        print("\nExecuting flash commands...")
        for cmd in commands:
            subprocess.check_call(cmd, cwd=cwd)
        print("\nFlashing completed successfully")


def flash_file(file_path: str, offset: int, file_type: str = "auto") -> List[str]:
    """
    Generate an openFPGALoader command to flash a file to the specified offset.
    """
    cmd = [
        "openFPGALoader", "-c", "dirtyJtag",
        "-f", "-o", f"{hex(offset)}",
    ]
    if file_type != "auto":
        cmd.extend(["--file-type", file_type])
    cmd.append(file_path)
    return cmd


def create_erased_file(size: int) -> str:
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


def flash_archive(archive_path: str, hw_rev_major: int, slot: Optional[int] = None, noconfirm: bool = False, erase_option_storage: bool = False) -> None:
    """
    Flash a bitstream archive to the specified slot.

    Args:
        archive_path: Path to the bitstream archive
        hw_rev_major: Hardware revision of attached Tiliqua
        slot: Slot number for bootloader-managed bitstreams
        noconfirm: Skip confirmation prompt if True
        erase_option_storage: Erase option storage regions if True
    """
    # Load and extract archive
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

        # Generate and execute flash commands
        command_generator = FlashCommandGenerator(regions_to_flash)
        commands = command_generator.generate_commands(erase_option_storage)

        # Show all commands and get confirmation
        print("\nThe following commands will be executed:")
        for cmd in commands:
            print(f"\t$ {' '.join(cmd)}")

        def confirm_operation():
            response = input("\nProceed with flashing? [y/N] ")
            return response.lower() == 'y'

        if not noconfirm and not confirm_operation():
            print("Aborting.")
            sys.exit(0)

        command_generator.execute_commands(commands, cwd=loader.get_tmpdir())

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
