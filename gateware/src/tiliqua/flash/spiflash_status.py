# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Utilities for dumping manifests from the SPI flash on a device to
determine what is flashed where (i.e. ``pdm flash status``).
"""

import json
import tempfile
import subprocess
from typing import Dict, List, Tuple, Optional

from .spiflash_layout import SlotLayout, N_MANIFESTS, MANIFEST_SIZE

def read_flash_segment(offset: int, size: int, reset: bool = False) -> bytes:
    # Create a unique filename, for use by openFPGALoader
    with tempfile.NamedTemporaryFile(suffix='.bin', delete=True) as tmp_file:
        temp_file_name = tmp_file.name
    # Dump the spiflash region to this temporary filename
    # FIXME: dumping to stdout and capturing it does not work somehow.
    cmd = [
        "openFPGALoader", "-c", "dirtyJtag",
        "--dump-flash", "-o", f"{hex(offset)}",
        "--file-size", str(size),
    ]
    if not reset:
        # Spamming the FPGA with resets is not nice for audio pops.
        cmd.append("--skip-reset")
    cmd.append(temp_file_name)
    print(" ".join(cmd)) # command we are running
    subprocess.check_call(cmd)
    # Finally, read out the contents and return them.
    with open(temp_file_name, 'rb') as f:
        return f.read()

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

def flash_status():
    """Dump the JSON manifest flashed to every user slot."""

    manifest_data = []
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
                print("  status: unable to parse")
                print(f"  first 32 bytes: {data[:32].hex()}")
        except Exception as e:
            print(f"  Error processing data: {e}")
