# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Vectorscope and 4-channel oscilloscope with menu system.

In vectorscope mode, rasterize X/Y (audio channel 0, 1) and
color (audio channel 3) to a simulated CRT.

In oscilloscope mode, all 4 input channels are plotted simultaneosly
in classic oscilloscope fashion.
"""

import logging
import os
import sys

from amaranth                                    import *
from amaranth.lib                                import wiring, data, stream
from amaranth.lib.wiring                         import In, Out, flipped, connect

from amaranth_soc                                import csr

from amaranth_future                             import fixed

from tiliqua                                     import eurorack_pmod, dsp, scope
from tiliqua.tiliqua_soc                         import TiliquaSoc
from tiliqua.cli                                 import top_level_cli

class XbeamSoc(TiliquaSoc):

    brief = "Graphical vectorscope and oscilloscope."

    def __init__(self, **kwargs):

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False, **kwargs)

        # WARN: TiliquaSoc ends at 0x00000900
        self.vector_periph_base = 0x00001000
        self.scope_periph_base  = 0x00001100

        self.vector_periph = scope.VectorTracePeripheral(
            fb=self.fb,
            bus_dma=self.psram_periph)
        self.csr_decoder.add(self.vector_periph.bus, addr=self.vector_periph_base, name="vector_periph")

        self.scope_periph = scope.ScopeTracePeripheral(
            fb=self.fb,
            bus_dma=self.psram_periph)
        self.csr_decoder.add(self.scope_periph.bus, addr=self.scope_periph_base, name="scope_periph")

        # now we can freeze the memory map
        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        m.submodules += self.vector_periph

        m.submodules += self.scope_periph

        m.submodules += super().elaborate(platform)

        pmod0 = self.pmod0_periph.pmod

        self.scope_periph.source = pmod0.o_cal

        wiring.connect(m, pmod0.o_cal, pmod0.i_cal)

        with m.If(self.scope_periph.soc_en):
            m.d.comb += [
                self.scope_periph.i.valid.eq(pmod0.o_cal.valid & pmod0.o_cal.ready),
                self.scope_periph.i.payload.eq(pmod0.o_cal.payload),
            ]
        with m.Else():
            m.d.comb += [
                self.vector_periph.i.valid.eq(pmod0.o_cal.valid & pmod0.o_cal.ready),
                self.vector_periph.i.payload.eq(pmod0.o_cal.payload),
            ]

        # Memory controller hangs if we start making requests to it straight away.
        with m.If(self.permit_bus_traffic):
            m.d.sync += self.vector_periph.en.eq(1)
            m.d.sync += self.scope_periph.en.eq(1)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(XbeamSoc, path=this_path)
