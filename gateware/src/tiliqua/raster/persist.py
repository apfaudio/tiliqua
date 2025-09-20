# Utilities and effects for rasterizing information to a framebuffer.
#
# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.build import *
from amaranth.lib import data, wiring
from amaranth.lib.fifo import SyncFIFOBuffered
from amaranth.lib.wiring import In, Out
from amaranth_soc import csr, wishbone

from ..video.framebuffer import DMAFramebuffer
from ..video.types import Pixel


class Persistance(wiring.Component):

    """
    Read pixels from a framebuffer in PSRAM and apply gradual intensity reduction to simulate oscilloscope glow.
    Pixels are DMA'd from PSRAM as a wishbone master in bursts of 'fifo_depth' in the 'sync' clock domain.
    The block of pixels has its intensity reduced and is then DMA'd back to the bus.

    'holdoff' is used to keep this core from saturating the bus between bursts.
    """

    def __init__(self, *, bus_signature,
                 fifo_depth=16, holdoff_default=256):
        self.fifo_depth = fifo_depth
        super().__init__({
            # Tweakables
            "holdoff": In(16, init=holdoff_default),
            "decay": In(4, init=1),
            # DMA bus / fb
            "bus":  Out(bus_signature),
            "fbp": In(DMAFramebuffer.Properties()),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # FIFO to cache pixels from PSRAM.
        m.submodules.fifo = self.fifo = SyncFIFOBuffered(
            width=self.bus.signature.data_width, depth=self.fifo_depth)

        bus = self.bus

        pixel_bits = Pixel.as_shape().size
        pixel_bytes = pixel_bits // 8

        # Length of framebuffer in bus words
        fb_len_words = ((self.fbp.timings.active_pixels * pixel_bytes) //
                        (self.bus.data_width // pixel_bits))

        # Track framebuffer position by tracking fifo reads/writes
        dma_offs_in = Signal(self.bus.addr_width, init=0)
        with m.If(self.fifo.w_en & self.fifo.w_rdy):
            with m.If(dma_offs_in < (fb_len_words-1)):
                m.d.sync += dma_offs_in.eq(dma_offs_in + 1)
            with m.Else():
                m.d.sync += dma_offs_in.eq(0)

        dma_offs_out = Signal.like(dma_offs_in)
        with m.If(self.fifo.r_en & self.fifo.r_rdy):
            with m.If(dma_offs_out < (fb_len_words-1)):
                m.d.sync += dma_offs_out.eq(dma_offs_out + 1)
            with m.Else():
                m.d.sync += dma_offs_out.eq(0)

        # Latched version of decay speed control input
        decay_latch = Signal.like(self.decay)
        # Track delay between read/write bursts
        holdoff_count = Signal(32)
        # Incoming pixel array (read from FIFO)
        pixels_r = Signal(data.ArrayLayout(Pixel, 4))

        m.d.comb += self.fifo.w_data.eq(bus.dat_r)

        # Used for fastpath when all pixels are zero
        any_nonzero_reads = Signal()
        pixels_peek = Signal(data.ArrayLayout(Pixel, 4))
        m.d.comb += pixels_peek.eq(self.fifo.w_data)
        with m.If(self.fifo.w_en):
            with m.If((pixels_peek[0].intensity != 0) |
                      (pixels_peek[1].intensity != 0) |
                      (pixels_peek[2].intensity != 0) |
                      (pixels_peek[3].intensity != 0)):
                m.d.sync += any_nonzero_reads.eq(1)

        with m.FSM() as fsm:

            with m.State('INIT'):
                # Don't hold bus in INIT state, as we may have a ResetInserter
                # holding us in reset across framebuffer size changes.
                m.d.comb += [
                    bus.stb.eq(0),
                    bus.cyc.eq(0),
                ]
                m.next = 'BURST-IN'

            with m.State('BURST-IN'):
                m.d.sync += decay_latch.eq(self.decay)
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(0),
                    bus.sel.eq(2**(bus.data_width//8)-1),
                    bus.adr.eq(self.fbp.base + dma_offs_in),
                    self.fifo.w_en.eq(bus.ack),
                    bus.cti.eq(
                        wishbone.CycleType.INCR_BURST),
                ]
                with m.If(self.fifo.w_level == (self.fifo_depth-1)):
                    m.d.comb += bus.cti.eq(
                            wishbone.CycleType.END_OF_BURST)
                    m.next = 'PREFETCH'

            with m.State('PREFETCH'):
                # Do not permit bus arbitration between burst in and out.
                m.d.comb += bus.cyc.eq(1)
                m.d.comb += self.fifo.w_en.eq(bus.ack)
                m.d.sync += holdoff_count.eq(0)
                with m.If(~bus.ack):
                    with m.If(any_nonzero_reads):
                        # Prefetch first FIFO entry before burst
                        m.d.comb += self.fifo.r_en.eq(1)
                        m.d.sync += pixels_r.eq(self.fifo.r_data)
                        m.next = 'BURST-OUT'
                    with m.Else():
                        # Fastpath: all pixels have zero intensity -
                        # no write is needed, skip it. This saves a lot
                        # of bandwidth as the screen is mostly black.
                        m.next = 'DRAIN'

            with m.State('BURST-OUT'):
                # The actual persistance calculation. 4 pixels at a time.
                pixels_w = Signal(data.ArrayLayout(Pixel, 4))
                for n in range(4):
                    # color
                    m.d.comb += pixels_w[n].color.eq(pixels_r[n].color)
                    # intensity
                    with m.If(pixels_r[n].intensity >= decay_latch):
                        m.d.comb += pixels_w[n].intensity.eq(pixels_r[n].intensity - decay_latch)
                    with m.Else():
                        m.d.comb += pixels_w[n].intensity.eq(0)

                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(1),
                    bus.sel.eq(2**(bus.data_width//8)-1),
                    bus.adr.eq(self.fbp.base + dma_offs_out - 1),
                    bus.dat_w.eq(pixels_w),
                    bus.cti.eq(
                        wishbone.CycleType.INCR_BURST)
                ]
                with m.If(bus.ack):
                    m.d.comb += self.fifo.r_en.eq(1)
                    m.d.sync += pixels_r.eq(self.fifo.r_data)
                with m.If(~self.fifo.r_rdy):
                    m.d.comb += bus.cti.eq(
                            wishbone.CycleType.END_OF_BURST)
                    m.next = 'HOLDOFF'

            with m.State('DRAIN'):
                m.d.comb += self.fifo.r_en.eq(1)
                with m.If(~self.fifo.r_rdy):
                    m.next = 'HOLDOFF'

            with m.State('HOLDOFF'):
                m.d.sync += any_nonzero_reads.eq(0)
                m.d.sync += holdoff_count.eq(holdoff_count + 1)
                with m.If(holdoff_count > self.holdoff):
                    m.next = 'BURST-IN'

        return ResetInserter({'sync': ~self.fbp.enable})(m)

class Peripheral(wiring.Component):

    class PersistReg(csr.Register, access="w"):
        persist: csr.Field(csr.action.W, unsigned(16))

    class DecayReg(csr.Register, access="w"):
        decay: csr.Field(csr.action.W, unsigned(8))

    def __init__(self, bus_dma):
        self.en = Signal()
        self.persist = Persistance(bus_signature=bus_dma.bus.signature.flip())
        bus_dma.add_master(self.persist.bus)

        regs = csr.Builder(addr_width=5, data_width=8)

        self._persist      = regs.add("persist",      self.PersistReg(),     offset=0x0)
        self._decay        = regs.add("decay",        self.DecayReg(),       offset=0x4)

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "fbp": In(DMAFramebuffer.Properties()),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        m.submodules.persist = self.persist

        wiring.connect(m, wiring.flipped(self.bus), self._bridge.bus)
        wiring.connect(m, wiring.flipped(self.fbp), self.persist.fbp)

        with m.If(self._persist.f.persist.w_stb):
            m.d.sync += self.persist.holdoff.eq(self._persist.f.persist.w_data)

        with m.If(self._decay.f.decay.w_stb):
            m.d.sync += self.persist.decay.eq(self._decay.f.decay.w_data)

        return m
