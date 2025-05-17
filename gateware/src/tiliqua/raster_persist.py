# Utilities and effects for rasterizing information to a framebuffer.
#
# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import colorsys
import os

from amaranth                import *
from amaranth.build          import *
from amaranth.lib            import wiring, data, stream
from amaranth.lib.wiring     import In, Out
from amaranth.lib.fifo       import SyncFIFOBuffered
from amaranth.lib.cdc        import FFSynchronizer

from amaranth_future         import fixed

from tiliqua                 import dsp
from tiliqua.dma_framebuffer import DMAFramebuffer
from tiliqua.eurorack_pmod   import ASQ

from amaranth_soc            import wishbone, csr

class Persistance(wiring.Component):

    """
    Read pixels from a framebuffer in PSRAM and apply gradual intensity reduction to simulate oscilloscope glow.
    Pixels are DMA'd from PSRAM as a wishbone master in bursts of 'fifo_depth // 2' in the 'sync' clock domain.
    The block of pixels has its intensity reduced and is then DMA'd back to the bus.

    'holdoff' is used to keep this core from saturating the bus between bursts.
    """

    def __init__(self, *, fb: DMAFramebuffer,
                 fifo_depth=32, holdoff_default=256):

        self.fb = fb
        self.fifo_depth = fifo_depth

        # FIFO to cache pixels from PSRAM.
        self.fifo = SyncFIFOBuffered(width=32, depth=fifo_depth)

        # Current addresses in the framebuffer (read and write sides)
        self.dma_addr_in = Signal(32, init=0)
        self.dma_addr_out = Signal(32)

        super().__init__({
            # Tweakables
            "holdoff": In(16, init=holdoff_default),
            "decay": In(4, init=1),
            # We are a DMA master
            "bus":  Out(fb.bus.signature),
            # Kick this to start the core
            "enable": In(1),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # Length of framebuffer in 32-bit words
        fb_len_words = (self.fb.timings.active_pixels * self.fb.bytes_per_pixel) // 4

        holdoff_count = Signal(32)
        pnext = Signal(32)
        wr_source = Signal(32)

        m.submodules.fifo = self.fifo
        bus = self.bus
        dma_addr_in = self.dma_addr_in
        dma_addr_out = self.dma_addr_out

        decay_latch = Signal(4)

        # Persistance state machine in 'sync' domain.
        with m.FSM() as fsm:
            with m.State('OFF'):
                with m.If(self.enable):
                    m.next = 'BURST-IN'

            with m.State('BURST-IN'):
                m.d.sync += holdoff_count.eq(0)
                m.d.sync += decay_latch.eq(self.decay)
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(0),
                    bus.sel.eq(2**(bus.data_width//8)-1),
                    bus.adr.eq(self.fb.fb_base + dma_addr_in),
                    self.fifo.w_en.eq(bus.ack),
                    self.fifo.w_data.eq(bus.dat_r),
                    bus.cti.eq(
                        wishbone.CycleType.INCR_BURST),
                ]
                with m.If(self.fifo.w_level >= (self.fifo_depth-1)):
                    m.d.comb += bus.cti.eq(
                            wishbone.CycleType.END_OF_BURST)
                with m.If(bus.stb & bus.ack & self.fifo.w_rdy): # WARN: drops last word
                    with m.If(dma_addr_in < (fb_len_words-1)):
                        m.d.sync += dma_addr_in.eq(dma_addr_in + 1)
                    with m.Else():
                        m.d.sync += dma_addr_in.eq(0)
                with m.Elif(~self.fifo.w_rdy):
                    m.next = 'WAIT1'

            with m.State('WAIT1'):
                m.d.sync += holdoff_count.eq(holdoff_count + 1)
                with m.If(holdoff_count > self.holdoff):
                    m.d.sync += pnext.eq(self.fifo.r_data)
                    m.d.comb += self.fifo.r_en.eq(1)
                    m.next = 'BURST-OUT'

            with m.State('BURST-OUT'):
                m.d.sync += holdoff_count.eq(0)

                # Incoming pixel array (read from FIFO)
                pixa = Signal(data.ArrayLayout(unsigned(8), 4))
                # Outgoing pixel array (write to bus)
                pixb = Signal(data.ArrayLayout(unsigned(8), 4))

                m.d.sync += [
                    pixa.eq(wr_source),
                ]

                # The actual persistance calculation. 4 pixels at a time.
                for n in range(4):
                    # color
                    m.d.comb += pixb[n][0:4].eq(pixa[n][0:4])
                    # intensity
                    with m.If(pixa[n][4:8] >= decay_latch):
                        m.d.comb += pixb[n][4:8].eq(pixa[n][4:8] - decay_latch)
                    with m.Else():
                        m.d.comb += pixb[n][4:8].eq(0)


                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(1),
                    bus.sel.eq(2**(bus.data_width//8)-1),
                    bus.adr.eq(self.fb.fb_base + dma_addr_out),
                    wr_source.eq(pnext),
                    bus.dat_w.eq(pixb),
                    bus.cti.eq(
                        wishbone.CycleType.INCR_BURST)
                ]
                with m.If(bus.stb & bus.ack):
                    m.d.comb += self.fifo.r_en.eq(1)
                    m.d.comb += wr_source.eq(self.fifo.r_data),
                    with m.If(dma_addr_out < (fb_len_words-1)):
                        m.d.sync += dma_addr_out.eq(dma_addr_out + 1)
                        m.d.comb += bus.adr.eq(self.fb.fb_base + dma_addr_out + 1),
                    with m.Else():
                        m.d.sync += dma_addr_out.eq(0)
                        m.d.comb += bus.adr.eq(self.fb.fb_base + 0),
                with m.If(~self.fifo.r_rdy):
                    m.d.comb += bus.cti.eq(
                            wishbone.CycleType.END_OF_BURST)
                    m.next = 'WAIT2'

            with m.State('WAIT2'):
                m.d.sync += holdoff_count.eq(holdoff_count + 1)
                with m.If(holdoff_count > self.holdoff):
                    m.next = 'BURST-IN'

        return ResetInserter({'sync': ~self.fb.enable})(m)

class Peripheral(wiring.Component):

    class PersistReg(csr.Register, access="w"):
        persist: csr.Field(csr.action.W, unsigned(16))

    class DecayReg(csr.Register, access="w"):
        decay: csr.Field(csr.action.W, unsigned(8))

    def __init__(self, fb, bus_dma):
        self.en = Signal()
        self.fb = fb
        self.persist = Persistance(fb=self.fb)
        bus_dma.add_master(self.persist.bus)

        regs = csr.Builder(addr_width=5, data_width=8)

        self._persist      = regs.add("persist",      self.PersistReg(),     offset=0x0)
        self._decay        = regs.add("decay",        self.DecayReg(),       offset=0x4)

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        m.submodules.persist = self.persist
        wiring.connect(m, wiring.flipped(self.bus), self._bridge.bus)

        m.d.comb += self.persist.enable.eq(self.fb.enable)

        with m.If(self._persist.f.persist.w_stb):
            m.d.sync += self.persist.holdoff.eq(self._persist.f.persist.w_data)

        with m.If(self._decay.f.decay.w_stb):
            m.d.sync += self.persist.decay.eq(self._decay.f.decay.w_data)

        return m
