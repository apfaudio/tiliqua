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

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List, Optional

MANIFEST_MAGIC           = 0xFEEDBEEF
N_MANIFESTS              = 8
SLOT_BITSTREAM_BASE      = 0x100000 # First user slot starts here
SLOT_SIZE                = 0x100000 # Spacing between user slots
MANIFEST_SIZE            = 1024     # Each manifest starts at:
                                    # SLOT_BITSTREAM_BASE + (N+1)*SLOT_SIZE-MANIFEST_SIZE

@dataclass_json
@dataclass
class MemoryRegion:
    filename: str
    spiflash_src: int
    psram_dst: Optional[int]
    size: int
    crc: int

@dataclass_json
@dataclass
class ExternalPLLConfig:
    clk0_hz: int
    clk1_hz: Optional[int]
    clk1_inherit: bool
    spread_spectrum: Optional[float]

@dataclass_json
@dataclass
class BitstreamManifest:
    hw_rev: int
    name: str
    sha: str
    brief: str
    video: str
    external_pll_config: Optional[ExternalPLLConfig]
    regions: List[MemoryRegion]
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
