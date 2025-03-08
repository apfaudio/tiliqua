# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import math
import sys
import unittest

from amaranth              import *
from amaranth.sim          import *
from amaranth.lib          import wiring
from tiliqua               import raster, test_util, eurorack_pmod, dma_framebuffer, dvi_modeline

from amaranth_soc          import csr
from amaranth_soc.csr      import wishbone

from amaranth_future       import fixed

class RasterTests(unittest.TestCase):

    MODELINE = dvi_modeline.DVIModeline.all_timings()["1280x720p60"]

    def test_persist(self):

        m = Module()
        fb = dma_framebuffer.DMAFramebuffer(
            fixed_modeline=self.MODELINE)
        dut = raster.Persistance(fb=fb)
        m.submodules += [dut, fb]

        # No actual FB backing store, just simulating WB transactions

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            # Simulate N burst accesses
            for _ in range(4):
                while not ctx.get(dut.bus.stb):
                    await ctx.tick()
                # Simulate acks delayed from stb
                await ctx.tick().repeat(8)
                ctx.set(dut.bus.ack, 1)
                while ctx.get(dut.bus.stb):
                    # for all burst accesses, simulate full intensity.
                    ctx.set(dut.bus.dat_r, 0xffffffff)
                    if ctx.get(dut.bus.we):
                        # for all burst reads, verify intensity of every
                        # pixel is reduced as expected
                        self.assertEqual(ctx.get(dut.bus.dat_w),
                                         0xefefefef)
                    await ctx.tick()
                ctx.set(dut.bus.ack, 0)

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_persist.vcd", "w")):
            sim.run()

    def test_stroke(self):

        m = Module()
        fb = dma_framebuffer.DMAFramebuffer(
            fixed_modeline=self.MODELINE)
        dut = raster.Stroke(fb=fb)
        m.submodules += [dut, fb]

        async def stimulus(ctx):
            for n in range(0, sys.maxsize):
                ctx.set(dut.i.valid, 1)
                ctx.set(dut.i.payload, [0, 0, 0, 0])
                await ctx.tick()
                ctx.set(dut.i.valid, 0)
                await ctx.tick().repeat(128)

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            # Simulate some acks delayed from stb
            for _ in range(16):
                while not ctx.get(dut.bus.stb):
                    await ctx.tick()
                await ctx.tick().repeat(8)
                ctx.set(dut.bus.ack, 1)
                await ctx.tick()
                ctx.set(dut.bus.ack, 0)
                await ctx.tick()

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        sim.add_process(stimulus)
        with sim.write_vcd(vcd_file=open("test_stroke.vcd", "w")):
            sim.run()
