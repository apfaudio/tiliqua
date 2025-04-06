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
import tarfile
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

# Flash memory map constants shared with the bootloader
from rs.manifest.src.lib import (
    N_MANIFESTS,
    SLOT_BITSTREAM_BASE,
    SLOT_SIZE,
    MANIFEST_SIZE,
)

# Where the XiP bootloader bitstream should be flashed.
BOOTLOADER_BITSTREAM_ADDR = 0x000000
# Used to determine where non-XiP firmware is stored
# (it is copied from SPIFLASH -> PSRAM before the CPU is
# reset in the new bitstream and starts executing)
FIRMWARE_BASE_SLOT0 = 0x1B0000
# Used to detect region collisions
FLASH_PAGE_SIZE = 1024  # 1KB


def scan_for_tiliqua():
    """
    Scan for a debugger with "apfbug" in the product name using openFPGALoader.
    """
    print("Scan for Tiliqua...")
    try:
        result = subprocess.run(
            ["sudo", "openFPGALoader", "--scan-usb"],
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
    data_lines = [line for line in lines if line and not line.startswith("Bus")]
    for line in data_lines:
        if "apfbug" in line.lower() or "apf.audio" in line.lower():
            parts = re.split(r'\s{2,}', line.strip())
            if len(parts) >= 5:
                serial = parts[3].strip()
                product = parts[4].strip()
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

class Region:
    """Flash memory region descriptor."""
    def __init__(self, addr: int, size: int, name: str):
        self.addr = addr
        self.size = size
        self.name = name

    @property
    def aligned_size(self) -> int:
        """Return size aligned up to page boundary."""
        return (self.size + FLASH_PAGE_SIZE - 1) & ~(FLASH_PAGE_SIZE - 1)

    @property
    def end_addr(self) -> int:
        """Return end address (exclusive)."""
        return self.addr + self.aligned_size

    def __lt__(self, other):
        """Enable sorting regions by address."""
        return self.addr < other.addr

    def __str__(self) -> str:
        return (f"{self.name}:\n"
                f"    start: 0x{self.addr:x}\n"
                f"    end:   0x{self.addr + self.aligned_size - 1:x}")


def flash_file(file_path: str, offset: int, file_type: str = "auto") -> List[str]:
    """
    Generate an openFPGALoader command to flash a file to the specified offset.
    """
    cmd = [
        "sudo", "openFPGALoader", "-c", "dirtyJtag",
        "-f", "-o", f"{hex(offset)}",
    ]
    if file_type != "auto":
        cmd.extend(["--file-type", file_type])
    cmd.append(file_path)
    return cmd


def check_region_overlaps(regions: List[Region], slot: Optional[int] = None) -> Tuple[bool, str]:
    """
    Check for overlapping regions in flash commands and slot boundaries.

    Args:
        regions: List of Region objects to check
        slot: Slot number for checking slot boundary constraints

    Returns:
        Tuple of (has_overlap, error_message)
    """
    # For non-XIP firmware, check if any region exceeds its slot
    if slot is not None:
        for region in regions:
            slot_start = (region.addr // SLOT_SIZE) * SLOT_SIZE
            slot_end = slot_start + SLOT_SIZE
            if region.end_addr > slot_end:
                return (True, f"Region '{region.name}' exceeds slot boundary: "
                             f"ends at 0x{region.end_addr:x}, slot ends at 0x{slot_end:x}")

    # Sort by start address and check for overlaps
    sorted_regions = sorted(regions)
    for i in range(len(sorted_regions) - 1):
        curr_end = sorted_regions[i].end_addr
        next_start = sorted_regions[i + 1].addr
        if curr_end > next_start:
            return (True, f"Overlap detected between '{sorted_regions[i].name}' (ends at 0x{curr_end:x}) "
                          f"and '{sorted_regions[i+1].name}' (starts at 0x{next_start:x})")

    return (False, "")


def flash_archive(archive_path: str, hw_rev_major: int, slot: Optional[int] = None, noconfirm: bool = False) -> None:
    """
    Flash a bitstream archive to the specified slot.

    Args:
        archive_path: Path to the bitstream archive
        slot: Slot number for bootloader-managed bitstreams
        noconfirm: Skip confirmation prompt if True
    """
    regions = []

    # Extract archive to temporary location
    with tarfile.open(archive_path, "r:gz") as tar:
        # Read manifest first
        manifest_info = tar.getmember("manifest.json")
        manifest_f = tar.extractfile(manifest_info)
        if not manifest_f:
            print("Error: Could not extract manifest.json from archive")
            sys.exit(1)
        manifest = json.load(manifest_f)

        hw_rev_manifest = manifest["hw_rev"]
        if hw_rev_manifest != hw_rev_major:
            print(f"Aborting: attached Tiliqua (hw=r{hw_rev_major}) does not match archive (hw=r{hw_rev_manifest}).")
            sys.exit(1)


        # Check if this is an XIP firmware
        has_xip_firmware = False
        xip_offset = None
        for region in manifest.get("regions", []):
            if region.get("spiflash_src") is not None:
                has_xip_firmware = True
                xip_offset = region["spiflash_src"]
                break

        if has_xip_firmware and slot is not None:
            print("Error: XIP firmware bitstreams must be flashed to bootloader slot")
            print(f"Remove --slot argument to flash at 0x0 with firmware at 0x{xip_offset:x}")
            sys.exit(1)
        elif not has_xip_firmware and slot is None:
            print("Error: Must specify slot for non-XIP firmware bitstreams")
            sys.exit(1)

        # Create temp directory for extracted files
        with tempfile.TemporaryDirectory() as tmpdir:
            tar.extractall(tmpdir)
            tmpdir_path = Path(tmpdir)

            # Prepare flashing commands and regions
            commands_to_run = []
            if has_xip_firmware:
                handle_xip_firmware(tmpdir_path, manifest, commands_to_run, regions)
            else:
                handle_psram_firmware(tmpdir_path, manifest, slot, commands_to_run, regions)

            # Print all regions
            print("\nRegions to be flashed:")
            for region in sorted(regions):
                print(f"  {region}")

            # Check for overlaps before proceeding
            has_overlap, error_msg = check_region_overlaps(regions, slot)
            if has_overlap:
                print(f"Error: {error_msg}")
                sys.exit(1)

            # Add skip-reset flag to all but the last command
            if len(commands_to_run) > 1:
                for cmd in commands_to_run[:-1]:
                    if "--skip-reset" not in cmd:
                        cmd.insert(-1, "--skip-reset")

            # Show all commands and get confirmation
            print("\nThe following commands will be executed:")
            for cmd in commands_to_run:
                print(f"\t$ {' '.join(cmd)}")

            if not noconfirm and not confirm_operation():
                print("Aborting.")
                sys.exit(0)

            # Execute all commands
            print("\nExecuting flash commands...")
            for i, cmd in enumerate(commands_to_run):
                subprocess.check_call(cmd)

            print("\nFlashing completed successfully")


def handle_xip_firmware(tmpdir: Path, manifest: Dict, commands: List, regions: List) -> None:
    """
    Handle XIP firmware bitstream flashing preparation.

    Args:
        tmpdir: Temporary directory with extracted files
        manifest: Parsed manifest.json
        commands: List to append commands to
        regions: List to append regions to
    """
    print("\nPreparing to flash XIP firmware bitstream to bootloader slot...")

    # Prepare bootloader bitstream
    bitstream_path = tmpdir / "top.bit"
    bitstream_size = os.path.getsize(bitstream_path)

    # Collect commands for bootloader location
    commands.append(flash_file(str(bitstream_path), BOOTLOADER_BITSTREAM_ADDR))

    # Add bootloader bitstream region
    regions.append(Region(BOOTLOADER_BITSTREAM_ADDR, bitstream_size, 'bootloader bitstream'))

    # Collect commands for XIP firmware regions
    for region_info in manifest.get("regions", []):
        if "filename" not in region_info:
            continue

        region_path = tmpdir / region_info["filename"]
        region_addr = region_info["spiflash_src"]

        commands.append(flash_file(
            str(region_path),
            region_addr,
            "raw",
        ))

        regions.append(Region(
            region_addr,
            region_info["size"],
            f"firmware '{region_info['filename']}'"
        ))


def handle_psram_firmware(tmpdir: Path, manifest: Dict, slot: int, commands: List, regions: List) -> None:
    """
    Handle psram (user) firmware bitstream flashing preparation.

    Args:
        tmpdir: Temporary directory with extracted files
        manifest: Parsed manifest.json
        slot: Slot number
        commands: List to append commands to
        regions: List to append regions to
    """
    print(f"\nPreparing to flash bitstream to slot {slot}...")

    # Calculate addresses for this slot
    slot_base = SLOT_BITSTREAM_BASE + (slot * SLOT_SIZE)
    bitstream_addr = slot_base
    manifest_addr = (slot_base + SLOT_SIZE) - MANIFEST_SIZE
    firmware_base = FIRMWARE_BASE_SLOT0 + (slot * SLOT_SIZE)

    # Add bitstream region
    bitstream_path = tmpdir / "top.bit"
    bitstream_size = os.path.getsize(bitstream_path)
    regions.append(Region(bitstream_addr, bitstream_size, 'bitstream'))

    # Add manifest region
    regions.append(Region(manifest_addr, MANIFEST_SIZE, 'manifest'))

    # Update manifest and add firmware regions
    for region_info in manifest.get("regions", []):
        if "filename" not in region_info:
            continue

        if region_info.get("psram_dst") is not None:
            if region_info.get("spiflash_src") is not None:
                assert region_info["spiflash_src"] is None, "Both psram_dst and spiflash_src set"

            region_info["spiflash_src"] = firmware_base
            print(f"manifest: region {region_info['filename']}: spiflash_src set to 0x{firmware_base:x}")

            regions.append(Region(
                firmware_base,
                region_info["size"],
                region_info['filename']
            ))

            # Align firmware base to next 4KB boundary (0x1000)
            firmware_base += region_info["size"]
            firmware_base = (firmware_base + 0xFFF) & ~0xFFF

    # Write updated manifest
    manifest_path = tmpdir / "manifest.json"
    print(f"\nFinal manifest contents:\n{json.dumps(manifest, indent=2)}")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f)

    # Collect all commands
    commands.append(flash_file(str(bitstream_path), bitstream_addr))
    commands.append(flash_file(str(manifest_path), manifest_addr, "raw"))

    for region_info in manifest.get("regions", []):
        if "filename" not in region_info or "spiflash_src" not in region_info:
            continue

        region_path = tmpdir / region_info["filename"]
        commands.append(flash_file(
            str(region_path),
            region_info["spiflash_src"],
            "raw",
        ))


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
        "sudo", "openFPGALoader", "-c", "dirtyJtag",
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
        offset = SLOT_BITSTREAM_BASE + (slot + 1) * SLOT_SIZE - MANIFEST_SIZE
        is_last = (slot == N_MANIFESTS - 1)

        print(f"\nReading Slot {slot} manifest at {hex(offset)}:")
        try:
            data = read_flash_segment(offset, 512, reset=is_last)
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

    # Status command
    subparsers.add_parser('status', help='Display current bitstream status')

    args = parser.parse_args()

    hw_rev_major = scan_for_tiliqua()

    if args.command == 'archive':
        if not os.path.exists(args.archive_path):
            print(f"Error: Archive not found: {args.archive_path}")
            sys.exit(1)
        if args.slot is not None and not 0 <= args.slot < N_MANIFESTS:
            print(f"Error: Slot must be between 0 and {N_MANIFESTS-1}")
            sys.exit(1)
        flash_archive(args.archive_path, hw_rev_major, args.slot, args.noconfirm)
    elif args.command == 'status':
        flash_status()


if __name__ == "__main__":
    main()
