# Copyright (c) 2024 Seb Holzapfel, apfelaudio UG <info@apfelaudio.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import math
import unittest

from amaranth import *
from amaranth.sim import *

from amaranth_future import fixed
from tiliqua.dsp import ASQ
from tiliqua.periph import eurorack_pmod
from tiliqua.test import stream


class I2STests(unittest.TestCase):

    def test_i2s(self):
        m = Module()
        i2stdm = eurorack_pmod.I2STDM(audio_192=False) # 48kHz logic
        dut = eurorack_pmod.I2SCalibrator()

        # I2S hardware loopback with 2-cycle FFBuffer pipeline delay
        sdin1_reg0 = Signal()
        sdin1_reg1 = Signal()
        m.d.audio += [
            sdin1_reg0.eq(i2stdm.i2s.sdin1),
            sdin1_reg1.eq(sdin1_reg0),
        ]
        m.d.comb += i2stdm.i2s.sdout1.eq(sdin1_reg1)

        # I2S <-> calibrator
        m.d.comb += [
            dut.channel.eq(i2stdm.channel),
            dut.strobe.eq(i2stdm.strobe),
            dut.i_uncal.eq(i2stdm.o),
            i2stdm.i.eq(dut.o_uncal),
        ]
        m.submodules += [i2stdm, dut]
        m = DomainRenamer({"audio": "sync"})(m)

        async def process(ctx):
            ctx.set(dut.o_cal.ready, 1)
            for n in range(0, 100):
                x = fixed.Const(math.sin(n*0.10), shape=ASQ)
                await stream.put(ctx, dut.i_cal, [x, 0, 0, 0])

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(process)

        with sim.write_vcd(vcd_file=open("test_i2s.vcd", "w")):
            sim.run()
