# Copyright (c) 2026 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_soc import wishbone
from amaranth_soc.memory import MemoryMap


class Peripheral(wiring.Component):

    """
    Bare-bones CLINT, *just* enough for tick irqs and soft irqs.

    In short, these bits:
    - `mtime`/`mtimecmp`: from RISCV privileged spec v1.12, section 3.2.1
    - `msip`: also from privleged spec, section 3.1.9

    The semantics of these aren't easily representable as amaranth-soc CSRs,
    so instead, just service raw wishbone transactions.
    """

    REGION_BYTES = 0x10000

    def __init__(self, *, sync_clk_hz, timebase_hz=1_000_000, name="clint"):
        if sync_clk_hz % timebase_hz != 0:
            raise ValueError(
                f"CLINT: sync clock {sync_clk_hz} Hz must be an integer multiple "
                f"of the timebase {timebase_hz} Hz")
        self.name        = name
        self.timebase_hz = timebase_hz
        self._tick_div   = sync_clk_hz // timebase_hz

        data_width  = 32
        granularity = 8
        depth_words = self.REGION_BYTES // (data_width // granularity)
        super().__init__({
            "bus":       In(wishbone.Signature(addr_width=exact_log2(depth_words),
                                               data_width=data_width,
                                               granularity=granularity,
                                               features={"cti", "bte"})),
            "mtime":     Out(unsigned(64)),
            "timer_irq": Out(unsigned(1)),
            "soft_irq":  Out(unsigned(1)),
        })
        memory_map = MemoryMap(addr_width=exact_log2(self.REGION_BYTES), data_width=granularity)
        memory_map.add_resource(name=("clint", self.name,), size=self.REGION_BYTES, resource=self)
        self.bus.memory_map = memory_map

    def elaborate(self, platform):
        m = Module()

        mtime    = Signal(64)
        mtimecmp = Signal(64, init=2**64 - 1)
        msip     = Signal()

        if self._tick_div == 1:
            m.d.sync += mtime.eq(mtime + 1)
        else:
            tick = Signal(range(self._tick_div))
            with m.If(tick == self._tick_div - 1):
                m.d.sync += tick.eq(0)
                m.d.sync += mtime.eq(mtime + 1)
            with m.Else():
                m.d.sync += tick.eq(tick + 1)

        m.d.comb += [
            self.mtime.eq(mtime),
            self.soft_irq.eq(msip),
        ]
        m.d.sync += self.timer_irq.eq(mtime >= mtimecmp)

        # these addresses are legacy convention from sifive that
        # made it into a lot of chips .. its what Linux expects
        # under 'sifive,clint0', and the 'riscv-peripheral' crate
        # assumes the same

        W_MSIP        = 0x0000 >> 2
        W_MTIMECMP_LO = 0x4000 >> 2
        W_MTIMECMP_HI = 0x4004 >> 2
        W_MTIME_LO    = 0xBFF8 >> 2
        W_MTIME_HI    = 0xBFFC >> 2

        bus = self.bus
        m.d.sync += bus.ack.eq(bus.cyc & bus.stb & ~bus.ack)

        with m.Switch(bus.adr):
            with m.Case(W_MSIP):
                m.d.comb += bus.dat_r.eq(msip)
            with m.Case(W_MTIMECMP_LO):
                m.d.comb += bus.dat_r.eq(mtimecmp[:32])
            with m.Case(W_MTIMECMP_HI):
                m.d.comb += bus.dat_r.eq(mtimecmp[32:])
            with m.Case(W_MTIME_LO):
                m.d.comb += bus.dat_r.eq(mtime[:32])
            with m.Case(W_MTIME_HI):
                m.d.comb += bus.dat_r.eq(mtime[32:])

        def write_lanes(reg):
            for lane in range(len(bus.sel)):
                with m.If(bus.sel[lane]):
                    m.d.sync += reg.word_select(lane, 8).eq(bus.dat_w.word_select(lane, 8))

        with m.If(bus.cyc & bus.stb & bus.we & bus.ack):
            with m.Switch(bus.adr):
                with m.Case(W_MSIP):
                    with m.If(bus.sel[0]):
                        m.d.sync += msip.eq(bus.dat_w[0])
                with m.Case(W_MTIMECMP_LO):
                    write_lanes(mtimecmp[:32])
                with m.Case(W_MTIMECMP_HI):
                    write_lanes(mtimecmp[32:])
                with m.Case(W_MTIME_LO):
                    write_lanes(mtime[:32])
                with m.Case(W_MTIME_HI):
                    write_lanes(mtime[32:])

        return m
