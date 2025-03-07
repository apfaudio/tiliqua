# Utilities for color palette hardware.
#
# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import colorsys

from amaranth              import *
from amaranth.lib          import wiring, data, stream
from amaranth.lib.wiring   import In, Out
from amaranth.lib.memory   import Memory


def compute_color_palette():
    """
    Calculate 16*16 (256) color palette to map each 8-bit pixel storage
    into R8/G8/B8 pixel value for sending to the DVI PHY. Each pixel
    is stored as a 4-bit intensity and 4-bit color.

    For SoC bitstreams, the palette is usually calculated in firmware
    and written using the palette update interface to the hardware, so
    this just serves as a sane default.
    """
    n_i = 16  # intensity levels
    n_c = 16  # color levels
    rs, gs, bs = [], [], []
    for i in range(n_i):
        for c in range(n_c):
            r, g, b = colorsys.hls_to_rgb(
                    float(c)/n_c, float(1.35**(i+1))/(1.35**n_i), 0.75)
            rs.append(int(r*255))
            gs.append(int(g*255))
            bs.append(int(b*255))

    return rs, gs, bs


class ColorPalette(wiring.Component):
    """
    Manages a 256-color palette with 8-bit RGB values.
    Format is: 1-byte in, 3-bytes (RGB) out.
    Each 8-bit pixel input is interpreted as 4 bits of intensity and 4 bits of color.
    """

    def __init__(self):
        """Initialize the color palette component."""
        super().__init__({
            # Pixel input and RGB output
            "pixel_in": In(8),  # 4 bits intensity, 4 bits color
            "pixel_out": Out(data.StructLayout({
                "r": unsigned(8),
                "g": unsigned(8),
                "b": unsigned(8),
            })),
            # Palette update interface
            "update": In(stream.Signature(data.StructLayout({
                "position": unsigned(8),
                "red":      unsigned(8),
                "green":    unsigned(8),
                "blue":     unsigned(8),
            }))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # Create memories for the palette
        rs, gs, bs = compute_color_palette()
        m.submodules.palette_r = palette_r = Memory(shape=unsigned(8), depth=256, init=rs)
        m.submodules.palette_g = palette_g = Memory(shape=unsigned(8), depth=256, init=gs)
        m.submodules.palette_b = palette_b = Memory(shape=unsigned(8), depth=256, init=bs)

        # Read ports
        rd_port_r = palette_r.read_port(domain="comb")
        rd_port_g = palette_g.read_port(domain="comb")
        rd_port_b = palette_b.read_port(domain="comb")

        # Connect read ports to address and output signals
        m.d.comb += [
            rd_port_r.addr.eq(self.pixel_in),
            rd_port_g.addr.eq(self.pixel_in),
            rd_port_b.addr.eq(self.pixel_in),

            # Connect output signals
            self.pixel_out.r.eq(rd_port_r.data),
            self.pixel_out.g.eq(rd_port_g.data),
            self.pixel_out.b.eq(rd_port_b.data),
        ]

        # Write ports for palette updates
        wport_r = palette_r.write_port()
        wport_g = palette_g.write_port()
        wport_b = palette_b.write_port()

        # Connect write ports to stream interface
        wports = [wport_r, wport_g, wport_b]
        m.d.comb += [
            wports[0].data.eq(self.update.payload.red),
            wports[1].data.eq(self.update.payload.green),
            wports[2].data.eq(self.update.payload.blue),
        ]
        m.d.comb += self.update.ready.eq(1)

        # Connect address and enable for all ports
        for wport in wports:
            with m.If(self.update.ready):
                m.d.comb += [
                    wport.addr.eq(self.update.payload.position),
                    wport.en.eq(self.update.valid),
                ]

        return m
