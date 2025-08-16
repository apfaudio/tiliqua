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
MANIFEST_SIZE            = RUST_CONSTANTS['MANIFEST_SIZE']
FLASH_PAGE_SZ            = 0x1000

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
    sha: str
    brief: str
    video: str
    regions: List[MemoryRegion]
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

class SlotLayout:
    """Flash addressing of overall SPI flash, for bootloader and user slots."""

    def __init__(self, slot_number: Optional[int] = None):
        self.slot_number = slot_number  # None = bootloader, int = user slot

        # Core manifest constants from lib.rs
        self.n_manifests = RUST_CONSTANTS['N_MANIFESTS']
        self.slot_bitstream_base = RUST_CONSTANTS['SLOT_BITSTREAM_BASE']
        self.slot_size = RUST_CONSTANTS['SLOT_SIZE']
        self.manifest_size = MANIFEST_SIZE

        # SlotLayout-specific constants (used by flashing tool, not in lib.rs)
        self.bootloader_bitstream_addr = 0x000000
        self.firmware_base_slot0 = 0x1B0000
        self.options_base_addr = 0xFD000

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
            return self.slot_bitstream_base + (self.slot_number * self.slot_size)

    @property
    def manifest_addr(self) -> int:
        if self.is_bootloader:
            return self.slot_bitstream_base - self.manifest_size
        else:
            return self.bitstream_addr + self.slot_size - self.manifest_size

    @property
    def firmware_base(self) -> int:
        if self.is_bootloader:
            raise ValueError("Bootloader doesn't have firmware base (uses XiP)")
        return self.firmware_base_slot0 + (self.slot_number * self.slot_size)

    @property
    def options_base(self) -> int:
        if self.is_bootloader:
            return self.options_base_addr
        else:
            return self.options_base_addr + ((1+self.slot_number) * self.slot_size)

    def slot_start_addr(self, slot: int) -> int:
        return self.slot_bitstream_base + (slot * self.slot_size)

    def slot_end_addr(self, slot: int) -> int:
        return self.slot_start_addr(slot) + self.slot_size

    def slot_from_addr(self, addr: int) -> int:
        return (addr - self.slot_bitstream_base) // self.slot_size
