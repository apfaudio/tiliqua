# Copyright (c) 2024 Seb Holzapfel, apfelaudio UG <info@apfelaudio.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import unittest

import math

from amaranth              import *
from amaranth.sim          import *
from amaranth.lib          import wiring, data
from amaranth.lib.memory   import Memory
from amaranth.lib.fifo     import SyncFIFO
from tiliqua               import eurorack_pmod
from tiliqua.eurorack_pmod import ASQ

from amaranth_future       import fixed

class I2STests(unittest.TestCase):

    def test_i2s(self):
        m = Module()
        i2stdm = eurorack_pmod.I2STDM(audio_192=False) # 48kHz logic
        dut = eurorack_pmod.I2SCalibrator()
        m.d.comb += i2stdm.i2s.sdout1.eq(i2stdm.i2s.sdin1) # I2S hardware loopback
        m.d.comb += [
            # I2S <-> calibrator
            dut.channel.eq(i2stdm.channel),
            dut.strobe.eq(i2stdm.strobe),
            dut.i_uncal.eq(i2stdm.o),
            i2stdm.i.eq(dut.o_uncal),
        ]
        m.submodules += [i2stdm, dut]
        m = DomainRenamer({"audio": "sync"})(m)

        async def process(ctx):
            for n in range(0, 100):
                await ctx.tick().until(dut.i_cal.ready)
                x = fixed.Const(math.sin(n*0.10), shape=ASQ)
                ctx.set(dut.i_cal.payload, [x, 0, 0, 0])
                ctx.set(dut.i_cal.valid, 1)
                ctx.set(dut.o_cal.ready, 1)
                await ctx.tick()
                ctx.set(dut.i_cal.valid, 0)
                ctx.set(dut.o_cal.ready, 0)

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(process)

        with sim.write_vcd(vcd_file=open("test_i2s.vcd", "w")):
            sim.run()
