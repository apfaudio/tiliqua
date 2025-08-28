# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import enum

from amaranth import *
from amaranth.lib import enum as amaranth_enum, data

# Re-export `tiliqua-manifest` types.
from rs.manifest.src.lib import BitstreamManifest as BitstreamManifest
from rs.manifest.src.lib import MemoryRegion as MemoryRegion
from rs.manifest.src.lib import ExternalPLLConfig as ExternalPLLConfig

class FirmwareLocation(str, enum.Enum):
    BRAM      = "bram"
    SPIFlash  = "spiflash"
    PSRAM     = "psram"


class AudioClock(str, enum.Enum):
    FINE_48KHZ  = "fine_48khz"
    FINE_192KHZ = "fine_192khz"
    COARSE_48KHZ  = "coarse_48khz"
    COARSE_192KHZ = "coarse_192khz"

    def mclk(self):
        return {
            self.FINE_48KHZ: 12_288_000,
            self.FINE_192KHZ: 49_152_000,
            self.COARSE_48KHZ: 12_500_000, # These don't need an extra PLL.
            self.COARSE_192KHZ: 50_000_000,
        }[self]

    def fs(self):
        return self.mclk() // 256

    def to_192khz(self):
        return {
            self.FINE_48KHZ: self.FINE_192KHZ,
            self.COARSE_48KHZ: self.COARSE_192KHZ,
        }[self]

    def is_192khz(self):
        return self in [
            self.FINE_192KHZ,
            self.COARSE_192KHZ,
        ]

class Rotation(amaranth_enum.Enum, shape=unsigned(2)):
    """
    Display rotation enumeration supporting all 90-degree orientations.
    
    Values:
    - NORMAL: 0° rotation (no change)
    - LEFT: 90° counter-clockwise rotation  
    - INVERTED: 180° rotation (upside down)
    - RIGHT: 90° clockwise rotation
    """
    NORMAL = 0
    LEFT = 1
    INVERTED = 2
    RIGHT = 3


class Pixel(data.Struct):
    """
    Standard pixel format used throughout the raster system.
    
    Fields:
    - color: 4-bit color index (0-15)
    - intensity: 4-bit intensity/brightness (0-15)
    """
    color:     unsigned(4)
    intensity: unsigned(4)
