# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import enum as amaranth_enum, data

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