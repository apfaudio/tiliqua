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
from dataclasses import dataclass

# Flash memory map constants shared with the bootloader
from rs.manifest.src.lib import (
    FLASH_PAGE_SZ,
    RegionType,
    BitstreamManifest,
    MemoryRegion,
    MANIFEST_SIZE,
    N_MANIFESTS,
    SLOT_BITSTREAM_BASE,
    SLOT_SIZE,
)
from tiliqua.archive import ArchiveLoader


class SlotLayout:
    """Flash addressing of overall SPI flash, for bootloader and user slots."""

    def __init__(self, slot_number: Optional[int] = None, 
                 bootloader_bitstream_addr: int = 0x000000,
                 firmware_base_slot0: int = 0x1B0000,
                 options_base_addr: int = 0xFD000):
        self.slot_number = slot_number  # None = bootloader, int = user slot
        self.bootloader_bitstream_addr = bootloader_bitstream_addr
        self.firmware_base_slot0 = firmware_base_slot0
        self.options_base_addr = options_base_addr

    @classmethod
    def for_bootloader(cls) -> 'SlotLayout':
        return cls(slot_number=None)

    @classmethod
    def for_user_slot(cls, slot: int) -> 'SlotLayout':
        return cls(slot_number=slot)

    @property
    def is_bootloader(self) -> bool:
        return self.slot_number is None

    @property
    def bitstream_addr(self) -> int:
        if self.is_bootloader:
            return self.bootloader_bitstream_addr
        else:
            return SLOT_BITSTREAM_BASE + (self.slot_number * SLOT_SIZE)

    @property
    def manifest_addr(self) -> int:
        if self.is_bootloader:
            return SLOT_BITSTREAM_BASE - MANIFEST_SIZE
        else:
            return self.bitstream_addr + SLOT_SIZE - MANIFEST_SIZE

    @property
    def firmware_base(self) -> int:
        if self.is_bootloader:
            raise ValueError("Bootloader doesn't have firmware base (uses XiP)")
        return self.firmware_base_slot0 + (self.slot_number * SLOT_SIZE)

    @property
    def options_base(self) -> int:
        if self.is_bootloader:
            return self.options_base_addr
        else:
            return self.options_base_addr + ((1+self.slot_number) * SLOT_SIZE)

    @staticmethod
    def slot_start_addr(slot: int) -> int:
        return SLOT_BITSTREAM_BASE + (slot * SLOT_SIZE)

    @staticmethod
    def slot_end_addr(slot: int) -> int:
        return SlotLayout.slot_start_addr(slot) + SLOT_SIZE

    @staticmethod
    def slot_from_addr(addr: int) -> int:
        return (addr - SLOT_BITSTREAM_BASE) // SLOT_SIZE


class FlashableRegion:
    """Flash memory region descriptor containing a MemoryRegion with finalized addresses."""
    def __init__(self, memory_region, file_path: Optional[Path] = None):
        self.memory_region = memory_region
        self.file_path = file_path

    @property
    def addr(self) -> int:
        """Flash address where this region will be written."""
        return self.memory_region.spiflash_src

    @property
    def size(self) -> int:
        """Size of the region in bytes."""
        return self.memory_region.size

    @property
    def name(self) -> str:
        """Human-readable name for the region."""
        return f"'{self.memory_region.filename}'"

    @property
    def aligned_size(self) -> int:
        """Return size aligned up to page boundary."""
        return (self.size + FLASH_PAGE_SZ - 1) & ~(FLASH_PAGE_SZ - 1)

    @property
    def end_addr(self) -> int:
        """Return end address (exclusive)."""
        return self.addr + self.aligned_size

    def __lt__(self, other):
        """Enable sorting regions by address."""
        return self.addr < other.addr

    def __str__(self) -> str:
        result = (f"{self.name} ({self.memory_region.region_type}):\n"
                  f"    start: 0x{self.addr:x}\n"
                  f"    end:   0x{self.addr + self.aligned_size - 1:x}")
        return result


class FlashCommandGenerator:
    """Generates and executes flash commands."""
    
    def __init__(self, flashable_regions: List[FlashableRegion]):
        self.flashable_regions = sorted(flashable_regions)
    
    def generate_commands(self) -> List[List[str]]:
        """Generate flash commands for all regions."""
        commands = []
        
        for region in self.flashable_regions:
            # Skip OptionStorage regions - they don't have actual files to flash
            if region.memory_region.region_type == RegionType.OptionStorage:
                continue
                
            # Use the pre-calculated file path
            commands.append(flash_file(str(region.file_path), region.addr, "raw"))
        
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

def promote_to_flashable_regions(loader: ArchiveLoader, slot: Optional[int]) -> List[FlashableRegion]:
    """
    Finalize addresses and promote MemoryRegions to FlashableRegions.
    
    Args:
        loader: ArchiveLoader containing extracted archive and manifest
        slot: Slot number (None for bootloader, int for user slots)
    
    Returns:
        List of FlashableRegion objects ready for flashing
    """
    # Finalize addresses using unified function
    finalize_addresses(loader, slot)
    
    # Promote regions with finalized addresses
    flashable_regions = []
    manifest = loader.get_manifest()
    tmpdir = loader.get_tmpdir()
    
    for region in manifest.regions:
        if region.spiflash_src is not None:
            file_path = tmpdir / region.filename
            flashable_regions.append(FlashableRegion(region, file_path))
    
    return flashable_regions




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

def check_region_overlaps(flashable_regions: List[FlashableRegion], slot: Optional[int] = None) -> Tuple[bool, str]:
    """
    Check for overlapping regions in flash commands and slot boundaries.

    Args:
        flashable_regions: List of FlashableRegion objects to check
        slot: Slot number for checking slot boundary constraints

    Returns:
        Tuple of (has_overlap, error_message)
    """
    # For non-XIP firmware, check if any region exceeds its slot
    if slot is not None:
        for region in flashable_regions:
            region_slot = SlotLayout.slot_from_addr(region.addr)
            slot_end = SlotLayout.slot_end_addr(region_slot)
            if region.end_addr > slot_end:
                return (True, f"Region {region.name} exceeds slot boundary: "
                             f"ends at 0x{region.end_addr:x}, slot ends at 0x{slot_end:x}")

    # Sort by start address and check for overlaps
    sorted_regions = sorted(flashable_regions)
    for i in range(len(sorted_regions) - 1):
        curr_end = sorted_regions[i].end_addr
        next_start = sorted_regions[i + 1].addr
        if curr_end > next_start:
            return (True, f"Overlap detected between {sorted_regions[i].name} (ends at 0x{curr_end:x}) "
                          f"and {sorted_regions[i+1].name} (starts at 0x{next_start:x})")

    return (False, "")


def flash_archive(archive_path: str, hw_rev_major: int, slot: Optional[int] = None, noconfirm: bool = False) -> None:
    """
    Flash a bitstream archive to the specified slot.

    Args:
        archive_path: Path to the bitstream archive
        hw_rev_major: Hardware revision of attached Tiliqua
        slot: Slot number for bootloader-managed bitstreams
        noconfirm: Skip confirmation prompt if True
    """
    # Load and extract archive
    with ArchiveLoader(archive_path) as loader:
        # Validate hardware compatibility
        manifest = loader.get_manifest()
        if manifest.hw_rev != hw_rev_major:
            print(f"Aborting: attached Tiliqua (hw=r{hw_rev_major}) does not match archive (hw=r{manifest.hw_rev}).")
            sys.exit(1)
        
        # Validate slot configuration
        is_bootloader = loader.is_bootloader_archive()
        if is_bootloader and slot is not None:
            print("Error: bootloader bitstream must be flashed to bootloader slot")
            print(f"Remove --slot argument to flash to bootloader slot.")
            sys.exit(1)
        elif not is_bootloader and slot is None:
            print("Error: Must specify slot for user bitstreams")
            sys.exit(1)
        
        # Finalize addresses and promote to FlashableRegions
        flashable_regions = promote_to_flashable_regions(loader, slot)

        # Print all regions
        print("\nAll spiflash regions:")
        for region in sorted(flashable_regions):
            print(f"  {region}")

        # Check for overlaps before proceeding
        has_overlap, error_msg = check_region_overlaps(flashable_regions, slot)
        if has_overlap:
            print(f"Error: {error_msg}")
            sys.exit(1)

        # Generate and execute flash commands
        command_generator = FlashCommandGenerator(flashable_regions)
        commands = command_generator.generate_commands()

        # Show all commands and get confirmation
        print("\nThe following commands will be executed:")
        for cmd in commands:
            print(f"\t$ {' '.join(cmd)}")

        if not noconfirm and not confirm_operation():
            print("Aborting.")
            sys.exit(0)

        command_generator.execute_commands(commands)


def finalize_addresses(loader: ArchiveLoader, slot: Optional[int]) -> None:
    """
    Finalize addresses for bootloader or user slot and write manifest.
    
    Args:
        loader: ArchiveLoader containing extracted archive and manifest
        slot: Slot number (None for bootloader, int for user slots)
    """
    manifest = loader.get_manifest()
    tmpdir = loader.get_tmpdir()
    layout = SlotLayout.for_bootloader() if slot is None else SlotLayout.for_user_slot(slot)
    
    if layout.is_bootloader:
        print("\nPreparing to flash bitstream to bootloader slot...")
    else:
        print(f"\nPreparing to flash bitstream to user slot {slot}...")
    
    ramload_base = None
    if not layout.is_bootloader:
        ramload_base = layout.firmware_base
    
    # Update all regions with proper addresses
    for region in manifest.regions:
        match region.region_type:
            case RegionType.Bitstream:
                region.spiflash_src = layout.bitstream_addr
            case RegionType.Manifest:
                region.spiflash_src = layout.manifest_addr
            case RegionType.XipFirmware:
                # XipFirmware regions already have spiflash_src set from archive creation
                assert region.spiflash_src is not None, "XipFirmware region missing spiflash_src"
            case RegionType.OptionStorage:
                region.spiflash_src = layout.options_base
            case RegionType.RamLoad:
                assert region.spiflash_src is None, "RamLoad region already has spiflash_src set"
                region.spiflash_src = ramload_base
                print(f"manifest: region {region.filename}: spiflash_src set to 0x{ramload_base:x}")
                # Align firmware base to next flash page boundary
                ramload_base += region.size
                ramload_base = (ramload_base + FLASH_PAGE_SZ - 1) & ~(FLASH_PAGE_SZ - 1)

    # Write updated manifest for user slots
    manifest_path = tmpdir / "manifest.json"
    manifest_dict = manifest.to_dict()
    print(f"\nFinal manifest contents:\n{json.dumps(manifest_dict, indent=2)}")
    with open(manifest_path, "w") as f:
        json.dump(manifest_dict, f)


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
        slot_layout = SlotLayout.for_user_slot(slot)
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
            flash_archive(args.archive_path, hw_rev_major, args.slot, args.noconfirm)
        case 'status':
            flash_status()


if __name__ == "__main__":
    main()
