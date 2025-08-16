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

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional

MANIFEST_MAGIC           = 0xFEEDBEEF
N_MANIFESTS              = 8
SLOT_BITSTREAM_BASE      = 0x100000 # First user slot starts here
SLOT_SIZE                = 0x100000 # Spacing between user slots
FLASH_PAGE_SZ            = 4096
MANIFEST_SIZE            = FLASH_PAGE_SZ  # Each manifest starts at:
                                          # SLOT_BITSTREAM_BASE + (N+1)*SLOT_SIZE-MANIFEST_SIZE
OPTION_STORAGE           = "options.storage"
OPTION_STORAGE_SZ        = 2*FLASH_PAGE_SZ
BITSTREAM_REGION         = "top.bit"

class RegionType(StrEnum):
    """Memory region type enum matching the Rust schema"""
    Bitstream = "Bitstream"        # Bitstream region that gets loaded directly by the bootloader
    XipFirmware = "XipFirmware"    # XiP firmware that executes directly from SPI flash
    RamLoad = "RamLoad"            # Region that gets copied from SPI flash to RAM before use (firmware.bin to PSRAM)
    Reserved = "Reserved"          # Reserved region for system use (options.storage, etc.)
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


def _parse_rust_constants():
    """Parse constants from lib.rs using simple regex."""
    lib_rs_path = os.path.join(os.path.dirname(__file__), 'lib.rs')
    constants = {}
    
    if os.path.exists(lib_rs_path):
        with open(lib_rs_path, 'r') as f:
            content = f.read()
            
        # Match: pub const NAME = 0x123456;
        for match in re.finditer(r'pub const (\w+).* = (0x[0-9a-fA-F]+);', content):
            name, value = match.groups()
            constants[name] = int(value, 16)
            
        # Match: pub const NAME = 123;  
        for match in re.finditer(r'pub const (\w+).* = (\d+);', content):
            name, value = match.groups()
            constants[name] = int(value)
    
    return constants


class SlotLayout:
    """Manages memory layout for both bootloader and user slots."""
    
    def __init__(self, slot_number: Optional[int] = None):
        self.slot_number = slot_number  # None = bootloader, int = user slot
        
        # Parse constants from lib.rs
        rust_constants = _parse_rust_constants()
        
        # Constants from lib.rs
        self.slot_bitstream_base = rust_constants['SLOT_BITSTREAM_BASE']
        self.slot_size = rust_constants['SLOT_SIZE'] 
        self.manifest_size = rust_constants['MANIFEST_SIZE']
        
        # SlotLayout-specific constants (not in lib.rs)
        self.bootloader_bitstream_addr = 0x000000
        self.firmware_base_slot0 = 0x1B0000
        self.options_base_addr = 0xFD000
    
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
    
    @classmethod
    def for_bootloader(cls) -> 'SlotLayout':
        """Create layout for bootloader slot."""
        return cls(slot_number=None)
    
    @classmethod
    def for_user_slot(cls, slot: int) -> 'SlotLayout':
        """Create layout for user slot."""
        return cls(slot_number=slot)
