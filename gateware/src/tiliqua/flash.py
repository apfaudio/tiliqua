#!/usr/bin/env python3

"""
Flash tool for Tiliqua bitstream archives.
See docs/gettingstarted.rst for usage.
See docs/bootloader.rst for implementation details and flash memory layout.
"""

import argparse
import json
import os
import subprocess
import sys
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

# Flash memory map constants
BOOTLOADER_BITSTREAM_ADDR = 0x000000
FIRMWARE_BASE_SLOT0 = 0x1B0000
FLASH_PAGE_SIZE = 1024  # 1KB

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
                f"  start: 0x{self.addr:x}\n"
                f"  end:   0x{self.addr + self.aligned_size - 1:x}")


def flash_file(file_path: str, offset: int, file_type: str = "auto", skip_reset: bool = False, dry_run: bool = True) -> List[str]:
    """
    Generate or execute the openFPGALoader command to flash a file to the specified offset.
    
    Args:
        file_path: Path to the file to flash
        offset: Flash memory offset
        file_type: File type for openFPGALoader
        skip_reset: Whether to skip resetting the device after flashing
        dry_run: If True, return command instead of executing it
        
    Returns:
        Command list if dry_run is True, otherwise None after executing the command
    """
    cmd = [
        "sudo", "openFPGALoader", "-c", "dirtyJtag",
        "-f", "-o", f"{hex(offset)}",
    ]
    if file_type != "auto":
        cmd.extend(["--file-type", file_type])
    if skip_reset:
        cmd.append("--skip-reset")
    cmd.append(file_path)
    
    if dry_run:
        return cmd
    
    print(f"Flashing to {hex(offset)}:")
    print(f"\t$ {' '.join(cmd)}")
    subprocess.check_call(cmd)
    return None


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


def flash_archive(archive_path: str, slot: Optional[int] = None, noconfirm: bool = False) -> None:
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
                handle_slotted_firmware(tmpdir_path, manifest, slot, commands_to_run, regions)

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
    commands.append(flash_file(str(bitstream_path), BOOTLOADER_BITSTREAM_ADDR, dry_run=True))
    
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
            dry_run=True
        ))
        
        regions.append(Region(
            region_addr,
            region_info["size"],
            f"firmware '{region_info['filename']}'"
        ))


def handle_slotted_firmware(tmpdir: Path, manifest: Dict, slot: int, commands: List, regions: List) -> None:
    """
    Handle slotted firmware bitstream flashing preparation.
    
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
    commands.append(flash_file(str(bitstream_path), bitstream_addr, dry_run=True))
    commands.append(flash_file(str(manifest_path), manifest_addr, "raw", dry_run=True))
    
    for region_info in manifest.get("regions", []):
        if "filename" not in region_info or "spiflash_src" not in region_info:
            continue
            
        region_path = tmpdir / region_info["filename"]
        commands.append(flash_file(
            str(region_path),
            region_info["spiflash_src"],
            "raw", 
            dry_run=True
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
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=False) as tmp_file:
        temp_file_name = tmp_file.name
        
    try:
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
    finally:
        os.unlink(temp_file_name)


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
    print("\nManifests:")
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
                for key, value in json_data.items():
                    print(f"    {key}: {value}")
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

    if args.command == 'archive':
        if not os.path.exists(args.archive_path):
            print(f"Error: Archive not found: {args.archive_path}")
            sys.exit(1)
        if args.slot is not None and not 0 <= args.slot < N_MANIFESTS:
            print(f"Error: Slot must be between 0 and {N_MANIFESTS-1}")
            sys.exit(1)
        flash_archive(args.archive_path, args.slot, args.noconfirm)
    elif args.command == 'status':
        flash_status()


if __name__ == "__main__":
    main()
