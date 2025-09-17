# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Implementation of PSRAM-backed framebuffer with a DVI PHY."""

from amaranth import *
from amaranth.build import *
from amaranth.lib import wiring
from amaranth.lib.cdc import FFSynchronizer
from amaranth.lib.fifo import AsyncFIFOBuffered
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2
from amaranth_soc import csr, wishbone

from ..build import sim
from . import dvi
from .types import Rotation


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

    def __init__(self, *, palette, fb_base_default=0, addr_width=22,
                 fifo_depth=512, bytes_per_pixel=1, burst_threshold_words=128,
                 fixed_modeline=None):

        self.fifo_depth = fifo_depth
        self.bytes_per_pixel = bytes_per_pixel
        self.burst_threshold_words = burst_threshold_words
        self.fixed_modeline = fixed_modeline

        self.palette = palette

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

        m.submodules.fifo = fifo = AsyncFIFOBuffered(
                width=32, depth=self.fifo_depth, r_domain='dvi', w_domain='sync')

        m.submodules.dvi_tgen = dvi_tgen = dvi.DVITimingGen()

        # TODO: FFSync needed? (sync -> dvi crossing, but should always be in reset when changed).
        wiring.connect(m, wiring.flipped(self.timings), dvi_tgen.timings)

        # Create a VSync signal in the 'sync' domain. Decoupled from display VSync inversion!
        phy_vsync_sync = Signal()
        m.submodules.vsync_ff = FFSynchronizer(
                i=dvi_tgen.ctrl.vsync, o=phy_vsync_sync, o_domain="sync")

        # DMA master bus
        bus = self.bus

        # Current offset into the framebuffer
        dma_addr = Signal(32)
        burst_cnt = Signal(16, init=0)

        # DMA bus master -> FIFO state machine
        # Burst until FIFO is full, then wait until half empty.

        fb_size_words = (self.timings.active_pixels * self.bytes_per_pixel) // 4


        # Read to FIFO in sync domain
        with m.FSM() as fsm:
            with m.State('WAIT-VSYNC'):
                with m.If(phy_vsync_sync):
                    m.d.sync += dma_addr.eq(0)
                    m.next = 'WAIT'
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

                with m.If(bus.ack):
                    m.d.sync += [
                        burst_cnt.eq(burst_cnt + 1),
                        dma_addr.eq(dma_addr+1),
                    ]

                with m.If((fifo.w_level == (self.fifo_depth-1)) |
                          (burst_cnt == self.burst_threshold_words)):
                    m.d.comb += bus.cti.eq(
                            wishbone.CycleType.END_OF_BURST)
                    m.next = 'WAIT'

                with m.If(dma_addr == (fb_size_words-1)):
                    m.d.comb += bus.cti.eq(
                            wishbone.CycleType.END_OF_BURST)
                    m.next = 'WAIT-VSYNC'

            with m.State('WAIT'):
                with m.If(fifo.w_level < self.fifo_depth-self.burst_threshold_words):
                    m.d.sync += burst_cnt.eq(0)
                    m.next = 'BURST'

        # Tracking in DVI domain

        # 'dvi' domain: read FIFO -> DVI PHY (1 fifo word is N pixels)
        bytecounter = Signal(exact_log2(4//self.bytes_per_pixel))
        last_word   = Signal(32)
        with m.If(dvi_tgen.ctrl.vsync):
            m.d.dvi += bytecounter.eq(0)
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


class Peripheral(wiring.Component):

    """
    CSR peripheral for tweaking framebuffer timing/palette parameters from an SoC.
    Timing values follow the same format as DVIModeline in modeline.py.
    """

    class HTimingReg(csr.Register, access="w"):
        h_active:     csr.Field(csr.action.W, unsigned(16))
        h_sync_start: csr.Field(csr.action.W, unsigned(16))

    class HTimingReg2(csr.Register, access="w"):
        h_sync_end:   csr.Field(csr.action.W, unsigned(16))
        h_total:      csr.Field(csr.action.W, unsigned(16))

    class VTimingReg(csr.Register, access="w"):
        v_active:     csr.Field(csr.action.W, unsigned(16))
        v_sync_start: csr.Field(csr.action.W, unsigned(16))

    class VTimingReg2(csr.Register, access="w"):
        v_sync_end:   csr.Field(csr.action.W, unsigned(16))
        v_total:      csr.Field(csr.action.W, unsigned(16))

    class HVTimingReg(csr.Register, access="w"):
        h_sync_invert: csr.Field(csr.action.W, unsigned(1))
        v_sync_invert: csr.Field(csr.action.W, unsigned(1))
        active_pixels: csr.Field(csr.action.W, unsigned(30))

    class FlagsReg(csr.Register, access="w"):
        enable:        csr.Field(csr.action.W, unsigned(1))
        rotation:      csr.Field(csr.action.W, Rotation)

    class FBBaseReg(csr.Register, access="w"):
        fb_base: csr.Field(csr.action.W, unsigned(32))

    class HpdReg(csr.Register, access="r"):
        # DVI hot plug detect
        hpd: csr.Field(csr.action.R, unsigned(1))

    def __init__(self, fb):
        self.fb = fb

        regs = csr.Builder(addr_width=6, data_width=8)

        self._h_timing     = regs.add("h_timing",     self.HTimingReg(),     offset=0x00)
        self._h_timing2    = regs.add("h_timing2",    self.HTimingReg2(),    offset=0x04)
        self._v_timing     = regs.add("v_timing",     self.VTimingReg(),     offset=0x08)
        self._v_timing2    = regs.add("v_timing2",    self.VTimingReg2(),    offset=0x0C)
        self._hv_timing    = regs.add("hv_timing",    self.HVTimingReg(),    offset=0x10)
        self._flags        = regs.add("flags",        self.FlagsReg(),       offset=0x14)
        self._fb_base      = regs.add("fb_base",      self.FBBaseReg(),      offset=0x18)
        self._hpd          = regs.add("hpd",          self.HpdReg(),         offset=0x1C)

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "rotation": Out(Rotation),
        })

        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge

        wiring.connect(m, wiring.flipped(self.bus), self._bridge.bus)

        if not self.fb.fixed_modeline:
            with m.If(self._h_timing.element.w_stb):
                m.d.sync += self.fb.timings.h_active.eq(self._h_timing.f.h_active.w_data)
                m.d.sync += self.fb.timings.h_sync_start.eq(self._h_timing.f.h_sync_start.w_data)
            with m.If(self._h_timing2.element.w_stb):
                m.d.sync += self.fb.timings.h_sync_end.eq(self._h_timing2.f.h_sync_end.w_data)
                m.d.sync += self.fb.timings.h_total.eq(self._h_timing2.f.h_total.w_data)
            with m.If(self._v_timing.element.w_stb):
                m.d.sync += self.fb.timings.v_active.eq(self._v_timing.f.v_active.w_data)
                m.d.sync += self.fb.timings.v_sync_start.eq(self._v_timing.f.v_sync_start.w_data)
            with m.If(self._v_timing2.element.w_stb):
                m.d.sync += self.fb.timings.v_sync_end.eq(self._v_timing2.f.v_sync_end.w_data)
                m.d.sync += self.fb.timings.v_total.eq(self._v_timing2.f.v_total.w_data)
            with m.If(self._hv_timing.element.w_stb):
                m.d.sync += self.fb.timings.h_sync_invert.eq(self._hv_timing.f.h_sync_invert.w_data)
                m.d.sync += self.fb.timings.v_sync_invert.eq(self._hv_timing.f.v_sync_invert.w_data)
                m.d.sync += self.fb.timings.active_pixels.eq(self._hv_timing.f.active_pixels.w_data)
        with m.If(self._flags.f.enable.w_stb):
            m.d.sync += self.fb.enable.eq(self._flags.f.enable.w_data)
        with m.If(self._flags.f.rotation.w_stb):
            m.d.sync += self.rotation.eq(self._flags.f.rotation.w_data)
        with m.If(self._fb_base.f.fb_base.w_stb):
            m.d.sync += self.fb.fb_base.eq(self._fb_base.f.fb_base.w_data)

        if sim.is_hw(platform):
            m.d.comb += self._hpd.f.hpd.r_data.eq(platform.request("dvi_hpd").i)
        else:
            # Fake connected screen in simulation
            m.d.comb += self._hpd.f.hpd.r_data.eq(1)

        return m

