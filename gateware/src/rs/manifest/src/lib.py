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

from dataclasses import dataclass, field
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

    REGION_FILE_LEN = RUST_CONSTANTS['REGION_FILE_LEN']

    def __post_init__(self):
        if len(self.filename) > self.REGION_FILE_LEN:
            raise ValueError(f"Field 'filename' (len={len(self.filename)}) is too long (max={self.REGION_FILE_LEN}).")

@dataclass_json
@dataclass
class BitstreamHelp:
    """
    Brief info describing a bitstream, used by the bootloader to display
    a brief summary of the bitstream before we switch to it.

    As bitstreams may or may not use the display, it's useful for the
    bootloader to show such information (especially the jack mapping)
    in case the bitstream itself does not display anything.
    """
    HELP_BRIEF_MAX_SIZE = RUST_CONSTANTS['HELP_BRIEF_MAX_SIZE']
    HELP_IO_MAX_SIZE = RUST_CONSTANTS['HELP_IO_MAX_SIZE']
    HELP_IO_LEFT_N = RUST_CONSTANTS['HELP_IO_LEFT_N']
    HELP_IO_RIGHT_N = RUST_CONSTANTS['HELP_IO_RIGHT_N']
    # One-line (~10 word) summary displayed by bootloader.
    brief: str = "<none>"
    # *** Strings for drawing small Tiliqua with IO mapping ***
    # 8 strings, one for each of the audio/cv jacks
    # in0, in1, in2, in3, out0, out1, out2, out3
    # max length 16, determined by BitstreamManifest rust type.
    io_left: List[str] = field(default_factory=lambda: ['']*BitstreamHelp.HELP_IO_LEFT_N)
    # 6 strings, one for each of the  right connectors (except dbg)
    # encoder, usb2, gpdi, ex0, ex1, midi_trs
    # max length 16, determined by BitstreamManifest rust type.
    io_right: List[str] = field(default_factory=lambda: ['']*BitstreamHelp.HELP_IO_RIGHT_N)
    # String displayed by bootloader describing the video mode.
    # This is automatically populated by ``cli.py`` based on
    # what hardware revision and/or ``--modeline`` is selected!
    video: str = "<none>"

    def __post_init__(self):
        if len(self.brief) > self.HELP_BRIEF_MAX_SIZE:
            raise ValueError(f"Field 'brief' (len={len(self.brief)}) is too long (max={self.HELP_BRIEF_MAX_SIZE}).")
        if len(self.io_left) != self.HELP_IO_LEFT_N:
            raise ValueError(f"Field 'io_left': list must have {self.HELP_IO_LEFT_N} entries.")
        if len(self.io_right) != self.HELP_IO_RIGHT_N:
            raise ValueError(f"Field 'io_right': list must have {self.HELP_IO_RIGHT_N} entries.")
        for i, label in enumerate(self.io_left):
            if len(label) > self.HELP_IO_MAX_SIZE:
                raise ValueError(f"io_left[{i}] = '{label}' is {len(label)} chars (max {self.HELP_IO_MAX_SIZE})")
        for i, label in enumerate(self.io_right):
            if len(label) > self.HELP_IO_MAX_SIZE:
                raise ValueError(f"io_right[{i}] = '{label}' is {len(label)} chars (max {self.HELP_IO_MAX_SIZE})")

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

    BITSTREAM_NAME_LEN = RUST_CONSTANTS['BITSTREAM_NAME_LEN']
    BITSTREAM_TAG_LEN = RUST_CONSTANTS['BITSTREAM_TAG_LEN']
    REGION_MAX_N = RUST_CONSTANTS['REGION_MAX_N']

    def __post_init__(self):
        if len(self.name) > self.BITSTREAM_NAME_LEN:
            raise ValueError(f"Field 'name' (len={len(self.name)}) is too long (max={self.BITSTREAM_NAME_LEN}).")
        if len(self.tag) > self.BITSTREAM_TAG_LEN:
            raise ValueError(f"Field 'tag' (len={len(self.tag)}) is too long (max={self.BITSTREAM_TAG_LEN}).")
        if len(self.regions) > self.REGION_MAX_N:
            raise ValueError(f"Field 'regions' (len={len(self.regions)}) is too long (max={self.REGION_MAX_N}).")

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

