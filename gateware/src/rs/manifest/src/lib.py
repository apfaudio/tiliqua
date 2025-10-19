# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
WARNING: Make sure this schema matches `lib.rs`!

Python representation of 'Bitstream Manifests', describing each bitstream
flashed to the Tiliqua, alongside any memory regions and settings required
for it to start up correctly (these are set up by the bootloader).

This representation is used for manifest generation and flashing.
"""

import json
import os
import re
from enum import StrEnum
from functools import lru_cache

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional

@lru_cache(maxsize=1)
def _parse_rust_constants():
    """Extract shared constants from lib.rs to avoid duplication here."""
    lib_rs_path = os.path.join(os.path.dirname(__file__), 'lib.rs')
    constants = {}
    if os.path.exists(lib_rs_path):
        with open(lib_rs_path, 'r') as f:
            content = f.read()
        # e.g. pub const NAME = 0x123456;
        for match in re.finditer(r'pub const (\w+).* = (0x[0-9a-fA-F]+);', content):
            name, value = match.groups()
            constants[name] = int(value, 16)
        # e.g. pub const NAME = 123;
        for match in re.finditer(r'pub const (\w+).* = (\d+);', content):
            name, value = match.groups()
            constants[name] = int(value)
    return constants

RUST_CONSTANTS           = _parse_rust_constants()
MANIFEST_MAGIC           = RUST_CONSTANTS['MANIFEST_MAGIC']
MANIFEST_OFFSET          = RUST_CONSTANTS['MANIFEST_OFFSET']
MANIFEST_SIZE            = RUST_CONSTANTS['MANIFEST_SIZE']
N_MANIFESTS              = RUST_CONSTANTS['N_MANIFESTS']
SLOT_BITSTREAM_BASE      = RUST_CONSTANTS['SLOT_BITSTREAM_BASE']
SLOT_SIZE                = RUST_CONSTANTS['SLOT_SIZE']
FLASH_PAGE_SZ            = RUST_CONSTANTS['FLASH_PAGE_SZ']
FLASH_SECTOR_SZ          = RUST_CONSTANTS['FLASH_SECTOR_SZ']

class RegionType(StrEnum):
    """Memory region type enum matching the Rust schema"""
    Bitstream = "Bitstream"        # Bitstream region that gets loaded directly by the bootloader
    XipFirmware = "XipFirmware"    # XiP firmware that executes directly from SPI flash
    RamLoad = "RamLoad"            # Region that gets copied from SPI flash to RAM before use (firmware.bin to PSRAM)
    OptionStorage = "OptionStorage"  # Option storage region for persistent application settings
    Manifest = "Manifest"          # Manifest region containing metadata about the bitstream

@dataclass_json
@dataclass
class MemoryRegion:
    filename: str
    size: int
    region_type: RegionType = RegionType.Bitstream
    spiflash_src: Optional[int] = None
    psram_dst: Optional[int] = None
    crc: Optional[int] = None

@dataclass_json
@dataclass
class BitstreamHelp:
    brief: str
    io_left: List[str]  # 8 strings for left jacks
    io_right: List[str] # 6 strings for right connectors
    video: str = "<none>"

@dataclass_json
@dataclass
class ExternalPLLConfig:
    clk0_hz: int
    clk1_inherit: bool
    clk1_hz: Optional[int] = None
    spread_spectrum: Optional[float] = None

@dataclass_json
@dataclass
class BitstreamManifest:
    hw_rev: int
    name: str
    tag: str
    regions: List[MemoryRegion]
    help: Optional[BitstreamHelp] = None
    external_pll_config: Optional[ExternalPLLConfig] = None
    magic: int = MANIFEST_MAGIC

    def write_to_path(self, manifest_path):
        # Clean up empty keys for improved backwards compatibility of manifests.
        def cleandict(d):
            """Remove all k, v pairs where v == None."""
            if isinstance(d, dict):
                return {k: cleandict(v) for k, v in d.items() if v is not None}
            elif isinstance(d, list):
                return [cleandict(v) for v in d]
            else:
                return d
        with open(manifest_path, "w") as f:
            # Drop all keys with None values (optional fields)
            f.write(json.dumps(cleandict(self.to_dict())))

