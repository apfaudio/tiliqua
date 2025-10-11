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

This should have zero code dependencies from this repository besides some
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

from .types import *
from .archive import ArchiveLoader
from .flash_layout import *

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

    def __init__(self, flashable_regions: List[FlashableRegion]):
        self.flashable_regions = sorted(flashable_regions)

    def generate_commands(self, erase_option_storage: bool = False) -> List[List[str]]:
        """Generate flash commands for all regions."""
        commands = []
        for region in self.flashable_regions:
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

    def execute_commands(self, commands: List[List[str]]):
        """Execute all flash commands."""
        print("\nExecuting flash commands...")
        for cmd in commands:
            subprocess.check_call(cmd)
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

        manifest = loader.get_manifest()

        # Validate hardware compatibility and other CLI arguments

        if manifest.hw_rev != hw_rev_major:
            print(f"Aborting: attached Tiliqua (hw=r{hw_rev_major}) does not match archive (hw=r{manifest.hw_rev}).")
            sys.exit(1)

        is_bootloader = loader.is_bootloader_archive()
        if is_bootloader and slot is not None:
            print("Error: bootloader bitstream must be flashed to bootloader slot")
            print(f"Remove --slot argument to flash to bootloader slot.")
            sys.exit(1)
        elif not is_bootloader and slot is None:
            print("Error: Must specify slot for user bitstreams")
            sys.exit(1)

        (concrete_manifest, regions_to_flash) = compute_concrete_regions_to_flash(
            manifest, slot)

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

        if not noconfirm and not confirm_operation():
            print("Aborting.")
            sys.exit(0)

        command_generator.execute_commands(commands)

def read_flash_segment(offset: int, size: int, reset: bool = False) -> bytes:
    """
    Read a segment of flash memory to a temporary file and return its contents.

    Args:
        offset: Flash memory offset
        size: Number of bytes to read
        reset: Whether to reset the device after reading

    Returns:
        Binary data read from flash
    """
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=True) as tmp_file:
        temp_file_name = tmp_file.name

    cmd = [
        "openFPGALoader", "-c", "dirtyJtag",
        "--dump-flash", "-o", f"{hex(offset)}",
        "--file-size", str(size),
    ]

    if not reset:
        cmd.append("--skip-reset")

    cmd.append(temp_file_name)
    print(" ".join(cmd))
    subprocess.check_call(cmd)

    with open(temp_file_name, 'rb') as f:
        data = f.read()

    return data


def is_empty_flash(data: bytes) -> bool:
    """Check if a flash segment is empty (all 0xFF)."""
    return all(b == 0xFF for b in data)


def parse_json_from_flash(data: bytes) -> Optional[Dict]:
    """
    Try to parse JSON data from a flash segment.

    Args:
        data: Binary data to parse

    Returns:
        Parsed JSON object or None if parsing failed
    """
    try:
        # Find the end of the JSON data (null terminator or 0xFF)
        for delimiter in [b'\x00', b'\xff']:
            end_idx = data.find(delimiter)
            if end_idx != -1:
                break
        else:
            end_idx = len(data)

        json_bytes = data[:end_idx]
        return json.loads(json_bytes)
    except json.JSONDecodeError:
        return None


def flash_status() -> None:
    """Display the status of flashed bitstreams in each manifest slot."""
    print("Reading manifests from flash...")
    manifest_data = []

    # Read all manifests
    for slot in range(N_MANIFESTS):
        slot_layout = SlotLayout(slot)
        offset = slot_layout.manifest_addr
        is_last = (slot == N_MANIFESTS - 1)

        print(f"\nReading Slot {slot} manifest at {hex(offset)}:")
        try:
            data = read_flash_segment(offset, MANIFEST_SIZE, reset=is_last)
            manifest_data.append((slot, offset, data))
        except subprocess.CalledProcessError as e:
            print(f"  Error reading flash: {e}")

    # Print manifest statuses
    print("\nMANIFESTS:")
    print("-" * 40)

    for slot, offset, data in manifest_data:
        print(f"\nSlot {slot} manifest at {hex(offset)}:")

        try:
            if is_empty_flash(data):
                print("  status: empty (all 0xFF)")
                continue

            json_data = parse_json_from_flash(data)
            if json_data:
                print("  status: valid manifest")
                print("  contents:")
                print(json.dumps(json_data, indent=2))
            else:
                print("  status: data is there, but does not look like a manifest")
                print(f"  first 32 bytes: {data[:32].hex()}")
        except Exception as e:
            print(f"  Error processing data: {e}")

    print("\nNote: empty segments are shown as 'empty (all 0xFF)'")


def confirm_operation() -> bool:
    """Prompt for user confirmation."""
    response = input("\nProceed with flashing? [y/N] ")
    return response.lower() == 'y'


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
