# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import enum

# Re-export `tiliqua-manifest` types.
from rs.manifest.src.lib import BitstreamManifest as BitstreamManifest
from rs.manifest.src.lib import MemoryRegion as MemoryRegion
from rs.manifest.src.lib import ExternalPLLConfig as ExternalPLLConfig

class TiliquaRevision(str, enum.Enum):
    R2    = "r2"
    R2SC3 = "r2sc3"
    R3    = "r3"
    R4    = "r4"

    def default():
        return TiliquaRevision.R2

    def all():
        return [
            TiliquaRevision.R2,
            TiliquaRevision.R2SC3,
            TiliquaRevision.R3,
            TiliquaRevision.R4,
        ]

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
