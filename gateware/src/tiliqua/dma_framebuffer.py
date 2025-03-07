# Utilities for synthesizing video timings and a DMA-driven framebuffer.
#
# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import colorsys
import os

from amaranth              import *
from amaranth.build        import *
from amaranth.lib          import wiring, data, stream
from amaranth.lib.wiring   import In, Out
from amaranth.lib.fifo     import AsyncFIFOBuffered
from amaranth.lib.cdc      import FFSynchronizer
from amaranth.utils        import exact_log2
from amaranth.lib.memory   import Memory

from amaranth_soc          import wishbone

from tiliqua               import sim, dvi
from tiliqua.dvi_modeline  import DVIModeline


class DMAFramebuffer(wiring.Component):

    """
    Interpret a PSRAM region as a framebuffer, effectively DMAing it to the display.
    - 'sync' domain: Pixels are DMA'd from PSRAM as a wishbone master in bursts of 'fifo_depth // 2'.
    - 'dvi' domain: FIFO is drained to the display as required by DVI timings.
    Framebuffer storage: currently fixed at 1byte/pix: 4-bit intensity, 4-bit color.
    """

    class FramebufferSimulationInterface(wiring.Signature):
        """
        Signals used by simulation harnesses to write images for debugging by
        inspecting the inner workings of this core.
        """
        def __init__(self):
            super().__init__({
                "de": Out(1),
                "vsync": Out(1),
                "hsync": Out(1),
                "r": Out(8),
                "g": Out(8),
                "b": Out(8),
            })

    def __init__(self, *, fb_base, bus_master,
                 fifo_depth=2048, bytes_per_pixel=1, fixed_modeline: DVIModeline = None):

        self.fixed_modeline = fixed_modeline
        self.fifo_depth = fifo_depth
        self.fb_base = fb_base
        self.bytes_per_pixel = bytes_per_pixel

        # Color palette tweaking interface
        super().__init__({
            # We are a DMA master
            "bus":  Out(wishbone.Signature(addr_width=bus_master.addr_width, data_width=32, granularity=8,
                                           features={"cti", "bte"})),
            # Kick this to start the core
            "enable": In(1),
            # Must be updated on timing changes
            "timings": In(dvi.DVITimingGen.TimingProperties()),
            # Palette updates
            "palette_rgb": In(stream.Signature(data.StructLayout({
                "position": unsigned(8),
                "red":      unsigned(8),
                "green":    unsigned(8),
                "blue":     unsigned(8),
                }))),
            # Enough information to plot the output of this core to images
            "simif": Out(self.FramebufferSimulationInterface())
        })

    @staticmethod
    def compute_color_palette():

        # Calculate 16*16 (256) color palette to map each 8-bit pixel storage
        # into R8/G8/B8 pixel value for sending to the DVI PHY. Each pixel
        # is stored as a 4-bit intensity and 4-bit color.
        #
        # TODO: make this runtime customizable?

        n_i = 16
        n_c = 16
        rs, gs, bs = [], [], []
        for i in range(n_i):
            for c in range(n_c):
                r, g, b = colorsys.hls_to_rgb(
                        float(c)/n_c, float(1.35**(i+1))/(1.35**n_i), 0.75)
                rs.append(int(r*255))
                gs.append(int(g*255))
                bs.append(int(b*255))

        return rs, gs, bs

    def elaborate(self, platform) -> Module:
        m = Module()

        if self.fixed_modeline is not None:
            for member in self.timings.signature.members:
                m.d.comb += getattr(self.timings, member).eq(getattr(self.fixed_modeline, member))

        m.submodules.fifo = fifo = AsyncFIFOBuffered(
                width=32, depth=self.fifo_depth, r_domain='dvi', w_domain='sync')
        m.submodules.dvi_tgen = dvi_tgen = dvi.DVITimingGen()
        # TODO: FFSync needed? (sync -> dvi crossing, but should always be in reset when changed).
        wiring.connect(m, wiring.flipped(self.timings), dvi_tgen.timings)

        # Create a VSync signal in the 'sync' domain.
        # NOTE: this is the same regardless of sync inversion.
        phy_vsync_sync = Signal()
        m.submodules.vsync_ff = FFSynchronizer(
                i=dvi_tgen.ctrl.vsync, o=phy_vsync_sync, o_domain="sync")

        # DMA master bus
        bus = self.bus

        # Current offset into the framebuffer
        dma_addr = Signal(32)

        # DMA bus master -> FIFO state machine
        # Burst until FIFO is full, then wait until half empty.

        # Signal from 'dvi' to 'sync' domain to drain FIFO if we are in vsync.
        drain_fifo = Signal(1, reset=0)
        drain_fifo_dvi = Signal(1, reset=0)
        m.submodules.drain_fifo_ff = FFSynchronizer(
                i=drain_fifo, o=drain_fifo_dvi, o_domain="dvi")
        drained = Signal()

        fb_size_words = (self.timings.active_pixels * self.bytes_per_pixel) // 4

        # Read to FIFO in sync domain
        with m.FSM() as fsm:
            with m.State('OFF'):
                with m.If(self.enable):
                    m.next = 'BURST'
            with m.State('BURST'):
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(0),
                    bus.sel.eq(2**(bus.data_width//8)-1),
                    bus.adr.eq(self.fb_base + dma_addr),
                    fifo.w_en.eq(bus.ack),
                    fifo.w_data.eq(bus.dat_r),
                    bus.cti.eq(
                        wishbone.CycleType.INCR_BURST),
                ]
                with m.If(fifo.w_level >= (self.fifo_depth-1)):
                    m.d.comb += bus.cti.eq(
                            wishbone.CycleType.END_OF_BURST)
                with m.If(bus.stb & bus.ack & fifo.w_rdy):
                    with m.If(dma_addr < (fb_size_words-1)):
                        m.d.sync += dma_addr.eq(dma_addr + 1)
                    with m.Else():
                        m.d.sync += dma_addr.eq(0)
                with m.Elif(~fifo.w_rdy):
                    m.next = 'WAIT'
            with m.State('WAIT'):
                with m.If(~phy_vsync_sync):
                    m.d.sync += drained.eq(0)
                with m.If(phy_vsync_sync & ~drained):
                    m.next = 'VSYNC'
                with m.Elif(fifo.w_level < self.fifo_depth//2):
                    m.next = 'BURST'
            with m.State('VSYNC'):
                # drain DVI side. We only want to drain once.
                m.d.comb += drain_fifo.eq(1)
                with m.If(fifo.w_level == 0):
                    m.d.sync += dma_addr.eq(0)
                    m.d.sync += drained.eq(1)
                    m.next = 'BURST'

        # Tracking in DVI domain

        # 'dvi' domain: read FIFO -> DVI PHY (1 fifo word is N pixels)
        bytecounter = Signal(exact_log2(4//self.bytes_per_pixel))
        last_word   = Signal(32)
        with m.If(drain_fifo_dvi):
            m.d.dvi += bytecounter.eq(0)
            m.d.comb += fifo.r_en.eq(1),
        with m.Elif(dvi_tgen.ctrl.de & fifo.r_rdy):
            m.d.comb += fifo.r_en.eq(bytecounter == 0),
            m.d.dvi += bytecounter.eq(bytecounter+1)
            with m.If(bytecounter == 0):
                m.d.dvi += last_word.eq(fifo.r_data)
            with m.Else():
                m.d.dvi += last_word.eq(last_word >> 8)

        rs, gs, bs = self.compute_color_palette()
        m.submodules.palette_r = palette_r = Memory(shape=unsigned(8), depth=256, init=rs)
        m.submodules.palette_g = palette_g = Memory(shape=unsigned(8), depth=256, init=gs)
        m.submodules.palette_b = palette_b = Memory(shape=unsigned(8), depth=256, init=bs)

        rd_port_r = palette_r.read_port(domain="comb")
        rd_port_g = palette_g.read_port(domain="comb")
        rd_port_b = palette_b.read_port(domain="comb")

        # Index by intensity (4-bit) and color (4-bit)
        m.d.comb += rd_port_r.addr.eq(Cat(last_word[0:4], last_word[4:8]))
        m.d.comb += rd_port_g.addr.eq(Cat(last_word[0:4], last_word[4:8]))
        m.d.comb += rd_port_b.addr.eq(Cat(last_word[0:4], last_word[4:8]))

        if sim.is_hw(platform):
            # Instantiate the DVI PHY itself
            m.submodules.dvi_gen = dvi_gen = dvi.DVIPHY()
            m.d.sync += [
                dvi_gen.de.eq(dvi_tgen.ctrl_phy.de),
                # RGB -> TMDS
                dvi_gen.data_in_ch0.eq(rd_port_r.data),
                dvi_gen.data_in_ch1.eq(rd_port_g.data),
                dvi_gen.data_in_ch2.eq(rd_port_b.data),
                # VSYNC/HSYNC -> TMDS
                dvi_gen.ctrl_in_ch0.eq(Cat(dvi_tgen.ctrl_phy.hsync, dvi_tgen.ctrl_phy.vsync)),
                dvi_gen.ctrl_in_ch1.eq(0),
                dvi_gen.ctrl_in_ch2.eq(0),
            ]
        else:
            # hook up simif
            m.d.comb += [
                self.simif.de.eq(dvi_tgen.ctrl_phy.de),
                self.simif.vsync.eq(dvi_tgen.ctrl_phy.vsync),
                self.simif.hsync.eq(dvi_tgen.ctrl_phy.hsync),
                self.simif.r.eq(rd_port_r.data),
                self.simif.g.eq(rd_port_g.data),
                self.simif.b.eq(rd_port_b.data),
            ]

        # palette write interface (p=position, rgb=value)
        wports = [palette_r.write_port(),
                  palette_g.write_port(),
                  palette_b.write_port()]
        # split rgb payload into one write for each rgb memory
        m.d.comb += [
            wports[0].data.eq(self.palette_rgb.payload.red),
            wports[1].data.eq(self.palette_rgb.payload.green),
            wports[2].data.eq(self.palette_rgb.payload.blue),
        ]
        m.d.comb += self.palette_rgb.ready.eq(1)
        # hook up position and stream valid -> write enable.
        for wport in wports:
            with m.If(self.palette_rgb.ready):
                m.d.comb += [
                    wport.addr.eq(self.palette_rgb.payload.position),
                    wport.en.eq(self.palette_rgb.valid),
                ]

        return m
