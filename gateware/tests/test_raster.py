# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import math
import sys
import unittest

from amaranth              import *
from amaranth.sim          import *
from amaranth.lib          import wiring
from tiliqua               import test_util
from tiliqua.periph   import eurorack_pmod
from tiliqua.video         import framebuffer, modeline, palette
from tiliqua.raster        import stroke, persist

from amaranth_soc          import csr
from amaranth_soc.csr      import wishbone

from amaranth_future       import fixed

class RasterTests(unittest.TestCase):

    MODELINE = modeline.DVIModeline.all_timings()["1280x720p60"]

    def test_persist(self):

        m = Module()
        fb = framebuffer.DMAFramebuffer(
            fixed_modeline=self.MODELINE, palette=palette.ColorPalette())
        dut = persist.Persistance(fb=fb)
        m.submodules += [dut, fb, fb.palette]

        # No actual FB backing store, just simulating WB transactions

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            ctx.set(fb.enable, 1)
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
        fb = framebuffer.DMAFramebuffer(
            fixed_modeline=self.MODELINE, palette=palette.ColorPalette())
        dut = stroke.Stroke(fb=fb)
        m.submodules += [dut, fb, fb.palette]

        async def stimulus(ctx):
            # Send a few sample points to the stroke
            for n in range(8):
                ctx.set(dut.i.valid, 1)
                ctx.set(dut.i.payload, [0, 0, 0, 0])
                await ctx.tick()
                ctx.set(dut.i.valid, 0)
                await ctx.tick().repeat(4)

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            ctx.set(fb.enable, 1)
            ctx.set(dut.plot_req.ready, 1)
            
            # Wait for a few plot requests to be generated
            plot_requests_seen = 0
            for _ in range(1000):
                if ctx.get(dut.plot_req.valid & dut.plot_req.ready):
                    plot_requests_seen += 1
                    if plot_requests_seen >= 8:
                        break
                await ctx.tick()
            
            # Test passes if we saw some plot requests
            assert plot_requests_seen > 0

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        sim.add_process(stimulus)
        with sim.write_vcd(vcd_file=open("test_stroke.vcd", "w")):
            sim.run()
