# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
SoC peripheral for controlling a DelayLine.
"""


from amaranth import *
from amaranth.lib import stream, wiring, enum
from amaranth.lib.wiring import In, Out

from amaranth_future import fixed
from amaranth_soc import csr

from ..dsp import ASQ, delay_line

class Peripheral(wiring.Component):

    class AttrReg(csr.Register, access="r"):
        bytes_per_sample: csr.Field(csr.action.R, unsigned(4))

    class BaseReg(csr.Register, access="r"):
        base: csr.Field(csr.action.R, unsigned(32))

    class SizeReg(csr.Register, access="r"):
        size_samples: csr.Field(csr.action.R, unsigned(32))

    class WrPointerReg(csr.Register, access="r"):
        wrpointer: csr.Field(csr.action.R, unsigned(32))

    def __init__(self, delayln, psram_base):
        self._delayln = delayln
        self._psram_base = psram_base

        assert delayln.psram_backed

        regs = csr.Builder(addr_width=5, data_width=8)
        self._attr = regs.add("attr", self.AttrReg(), offset=0x00)
        self._base = regs.add("base", self.BaseReg(), offset=0x04)
        self._size = regs.add("size", self.SizeReg(), offset=0x08)
        self._wrpointer = regs.add("wrpointer", self.WrPointerReg(), offset=0x0C)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge

        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        m.d.comb += [
            self._attr.f.bytes_per_sample.r_data.eq(self._delayln.INTERNAL_BUS_DATA_WIDTH),
            self._base.f.base.r_data.eq(self._psram_base + self._delayln._adapter.base),
            self._size.f.size_samples.r_data.eq(self._delayln.max_delay),
            self._wrpointer.f.wrpointer.r_data.eq(self._delayln._wrpointer),
        ]

        return m
