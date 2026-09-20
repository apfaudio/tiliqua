# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Utilities for dumping manifests from the SPI flash on a device to
determine what is flashed where (i.e. ``pdm flash status``).
"""

import json
import re
import subprocess
from typing import Dict, List, Tuple, Optional

from .spiflash_layout import SlotLayout, N_MANIFESTS, MANIFEST_SIZE
from .openfpgaloader import dump_flash_region, reset_fpga

def is_empty_flash(data: bytes) -> bool:
    return all(b == 0xFF for b in data)

def parse_json_from_flash(data: bytes) -> Optional[Dict]:
    """Try to parse JSON data from a flash segment."""
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

def read_bootloader_manifest() -> Optional[Dict]:
    """Read and parse the bootloader manifest, or None if empty/unreadable."""
    try:
        data = dump_flash_region(SlotLayout(None).manifest_addr, MANIFEST_SIZE)
    except subprocess.CalledProcessError:
        return None
    if is_empty_flash(data):
        return None
    return parse_json_from_flash(data)

def parse_version_tag(tag: str) -> Optional[Tuple[int, int, int]]:
    """Parse a 'vX.Y.Z' tag into a tuple, or None for untagged (dev) builds."""
    m = re.match(r"^v(\d+)\.(\d+)\.(\d+)", tag or "")
    if m is None:
        return None
    return tuple(int(x) for x in m.groups())

def flash_status():
    """Dump the JSON manifest flashed to the bootloader and every user slot."""

    slots = [None] + list(range(N_MANIFESTS))
    manifest_data = []
    try:
        for slot in slots:
            name = "Bootloader" if slot is None else f"Slot {slot}"
            offset = SlotLayout(slot).manifest_addr
            print(f"\nReading {name} manifest at {hex(offset)}:")
            try:
                data = dump_flash_region(offset, MANIFEST_SIZE)
                manifest_data.append((name, offset, data))
            except subprocess.CalledProcessError as e:
                print(f"  Error reading flash: {e}")
    finally:
        reset_fpga()

    print("\nMANIFESTS:")
    print("-" * 40)
    for name, offset, data in manifest_data:
        print(f"\n{name} manifest at {hex(offset)}:")
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
                print("  status: unable to parse")
                print(f"  first 32 bytes: {data[:32].hex()}")
        except Exception as e:
            print(f"  Error processing data: {e}")
