# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import data
from amaranth.lib import enum as amaranth_enum


class Rotation(amaranth_enum.Enum, shape=unsigned(2)):
    """
    Display rotation, all 90-degree orientations.
    """
    NORMAL = 0
    LEFT = 1
    INVERTED = 2
    RIGHT = 3


class Pixel(data.Struct):
    """
    Framebuffer pixel format used throughout video/raster system.
    Separate color and intensity such that phosphor simulation is cheap.
    """

    color:     unsigned(4)
    intensity: unsigned(4)

    def intensity_max():
        return 0xF
