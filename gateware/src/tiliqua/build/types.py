# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import enum

# Re-export all `tiliqua-manifest` types and constants.
from rs.manifest.src.lib import *


class FirmwareLocation(str, enum.Enum):
    BRAM      = "bram"
    SPIFlash  = "spiflash"
    PSRAM     = "psram"


class BitstreamHelp:
    """Metadata for bitstream help display in bootloader."""
    def __init__(self, brief, io_left, io_right):
        self.brief = brief
        self.io_left = io_left
        self.io_right = io_right