#!/usr/bin/env python3

"""
Flash tool for Tiliqua bitstream archives - Command line interface.
See docs/gettingstarted.rst for usage.
See docs/bootloader.rst for implementation details and flash memory layout.
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

# Import core flashing logic
from .flash_core import (
    FlashCore, FlashOperation, Region,
    N_MANIFESTS, SLOT_BITSTREAM_BASE, SLOT_SIZE, MANIFEST_SIZE,
    parse_manifest_from_flash, is_empty_flash
)


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


def execute_flash_operation(operation: FlashOperation, temp_dir: Path) -> None:
    """Execute a flash operation using openFPGALoader."""
    # Write data to temporary file
    temp_file = temp_dir / operation.filename
    with open(temp_file, 'wb') as f:
        f.write(operation.data)
    
    # Build command
    cmd = ["sudo", "openFPGALoader"] + operation.to_args() + [str(temp_file)]
    
    # Execute
    subprocess.check_call(cmd)


def extract_archive_files(archive_path: str) -> Tuple[Dict, Dict[str, bytes]]:
    """Extract files from archive and return manifest and file contents."""
    files = {}
    manifest = None
    
    with tarfile.open(archive_path, "r:gz") as tar:
        for member in tar.getmembers():
            if member.isfile():
                f = tar.extractfile(member)
                if f:
                    data = f.read()
                    files[member.name] = data
                    
                    if member.name == "manifest.json":
                        manifest = json.loads(data)
    
    if not manifest:
        raise ValueError("No manifest.json found in archive")
    
    return manifest, files


def flash_archive(archive_path: str, hw_rev_major: int, slot: Optional[int] = None, noconfirm: bool = False) -> None:
    """
    Flash a bitstream archive to the specified slot.

    Args:
        archive_path: Path to the bitstream archive
        hw_rev_major: Hardware revision of attached device
        slot: Slot number for bootloader-managed bitstreams
        noconfirm: Skip confirmation prompt if True
    """
    # Extract archive
    manifest, files = extract_archive_files(archive_path)
    
    # Initialize core
    core = FlashCore()
    
    # Validate hardware
    valid, error = core.validate_hardware(hw_rev_major, manifest["hw_rev"])
    if not valid:
        print(error)
        sys.exit(1)
    
    # Check if XIP firmware
    has_xip, xip_offset = core.check_xip_firmware(manifest)
    if has_xip:
        print("\nPreparing to flash XIP firmware bitstream to bootloader slot...")
    else:
        print(f"\nPreparing to flash bitstream to slot {slot}...")
    
    try:
        # Process archive
        operations, regions, updated_manifest = core.process_archive(manifest, files, slot)
        
        # Update manifest if needed
        if updated_manifest != manifest:
            print(f"\nFinal manifest contents:\n{json.dumps(updated_manifest, indent=2)}")
            
            # Log updated regions
            for region_info in updated_manifest.get("regions", []):
                if "filename" in region_info and region_info.get("spiflash_src") is not None:
                    print(f"manifest: region {region_info['filename']}: spiflash_src set to 0x{region_info['spiflash_src']:x}")
        
        # Print regions
        print("\nRegions to be flashed:")
        for region in sorted(regions):
            print(f"  {region}")
        
        # Show commands
        print("\nThe following commands will be executed:")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            for op in operations:
                temp_file = temp_path / op.filename
                cmd = ["sudo", "openFPGALoader"] + op.to_args() + [str(temp_file)]
                print(f"\t$ {' '.join(cmd)}")
            
            # Confirm
            if not noconfirm and not confirm_operation():
                print("Aborting.")
                sys.exit(0)
            
            # Execute
            print("\nExecuting flash commands...")
            for op in operations:
                execute_flash_operation(op, temp_path)
        
        print("\nFlashing completed successfully")
        
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"Flash command failed: {e}")
        sys.exit(1)


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

            json_data = parse_manifest_from_flash(data)
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
