# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Implementation of PSRAM-backed framebuffer with a DVI PHY."""

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

from tiliqua               import sim, dvi, palette
from tiliqua.dvi_modeline  import DVIModeline


class DMAFramebuffer(wiring.Component):

    """
    Interpret a PSRAM region as a framebuffer, effectively DMAing it to the display.
    - 'sync' domain: Pixels are DMA'd from PSRAM as a wishbone master in bursts,
       whenever 'burst_threshold_words' space is available in the FIFO.
    - 'dvi' domain: FIFO is drained to the display as required by DVI timings.
    Framebuffer storage: currently fixed at 1byte/pix: 4-bit intensity, 4-bit color.
    """

    class FramebufferSimulationInterface(wiring.Signature):
        """
        Enough information for simulation to plot the output of this core to bitmaps.
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

    def __init__(self, *, fb_base_default=0, addr_width=22,
                 fifo_depth=512, bytes_per_pixel=1, burst_threshold_words=128,
                 fixed_modeline: DVIModeline = None):

        self.fixed_modeline = fixed_modeline
        self.fifo_depth = fifo_depth
        self.bytes_per_pixel = bytes_per_pixel
        self.burst_threshold_words = burst_threshold_words

        # Color palette tweaking interface is presented by this
        self.palette = palette.ColorPalette()

        super().__init__({
            # Start of framebuffer
            "fb_base": In(32, init=fb_base_default),
            # We are a DMA master
            "bus":  Out(wishbone.Signature(addr_width=addr_width, data_width=32, granularity=8,
                                           features={"cti", "bte"})),
            # Kick this to start the core
            "enable": In(1),
            # Must be updated on timing changes
            "timings": In(dvi.DVITimingGen.TimingProperties()),
            # Enough information to plot the output of this core to images
            "simif": Out(self.FramebufferSimulationInterface())
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        if self.fixed_modeline is not None:
            for member in self.timings.signature.members:
                m.d.comb += getattr(self.timings, member).eq(getattr(self.fixed_modeline, member))

        m.submodules.palette = self.palette
        m.submodules.fifo = fifo = AsyncFIFOBuffered(
                width=32, depth=self.fifo_depth, r_domain='dvi', w_domain='sync')
        m.submodules.dvi_tgen = dvi_tgen = dvi.DVITimingGen()
        # TODO: FFSync needed? (sync -> dvi crossing, but should always be in reset when changed).
        wiring.connect(m, wiring.flipped(self.timings), dvi_tgen.timings)

        # Create a VSync signal in the 'sync' domain. Decoupled from display VSync inversion!
        phy_vsync_sync = Signal()
        m.submodules.vsync_ff = FFSynchronizer(
                i=dvi_tgen.ctrl.vsync, o=phy_vsync_sync, o_domain="sync")
        phy_vsync_sync_prev = Signal()
        vsync_rise = Signal()
        m.d.sync += phy_vsync_sync_prev.eq(phy_vsync_sync)
        m.d.comb += vsync_rise.eq(phy_vsync_sync & ~phy_vsync_sync_prev)

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
                with m.If(vsync_rise):
                    m.next = 'VSYNC'
                with m.Elif(fifo.w_level < self.fifo_depth-self.burst_threshold_words):
                    m.next = 'BURST'
            with m.State('VSYNC'):
                # drain DVI side. We only want to drain once.
                m.d.comb += drain_fifo.eq(1)
                with m.If(fifo.w_level == 0):
                    m.d.sync += dma_addr.eq(0)
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

        # Index by intensity (4-bit) and color (4-bit)
        m.d.comb += [
            self.palette.pixel_in.eq(Cat(last_word[0:4], last_word[4:8])),
        ]

        if sim.is_hw(platform):
            # Instantiate the DVI PHY itself
            m.submodules.dvi_gen = dvi_gen = dvi.DVIPHY()
            m.d.dvi += [
                dvi_gen.de.eq(dvi_tgen.ctrl_phy.de),
                # RGB -> TMDS
                dvi_gen.data_in_ch0.eq(self.palette.pixel_out.b),
                dvi_gen.data_in_ch1.eq(self.palette.pixel_out.g),
                dvi_gen.data_in_ch2.eq(self.palette.pixel_out.r),
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
                self.simif.r.eq(self.palette.pixel_out.r),
                self.simif.g.eq(self.palette.pixel_out.g),
                self.simif.b.eq(self.palette.pixel_out.b),
            ]

        return m
