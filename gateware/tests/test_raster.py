# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import struct
import unittest

from amaranth import *
from amaranth.sim import *

from tiliqua.test import wishbone, stream, csr as csr_util
from tiliqua.raster import persist, stroke, plot, blit
from tiliqua.video import framebuffer, modeline, palette

from amaranth_soc import csr
from amaranth_soc.csr import wishbone as csr_wishbone

class RasterTests(unittest.TestCase):

    MODELINE = modeline.DVIModeline.all_timings()["1280x720p60"]

    def test_persist(self):

        m = Module()
        fb = framebuffer.DMAFramebuffer(
            fixed_modeline=self.MODELINE, palette=palette.ColorPalette())
        dut = persist.Persistance(fb=fb)
        check = wishbone.BusChecker(dut.bus, prefix='[bus] ')
        m.submodules += [dut, fb, fb.palette, check]

        # No actual FB backing store, just simulating WB transactions

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            ctx.set(fb.enable, 1)
            # Simulate N burst accesses
            for _ in range(4):
                ix = 0
                while not ctx.get(dut.bus.stb):
                    await ctx.tick()
                # Simulate acks delayed from stb
                await ctx.tick().repeat(8)
                ctx.set(dut.bus.ack, 1)
                while ctx.get(dut.bus.stb):
                    # for all burst accesses, simulate full intensity.
                    ctx.set(dut.bus.dat_r, 0xffffff00 | (ix&0xf))
                    if ctx.get(dut.bus.we):
                        # for all burst reads, verify intensity of every
                        # pixel is reduced as expected
                        self.assertEqual(ctx.get(dut.bus.dat_w),
                                         0xefefef00 | (ix&0xf))
                    await ctx.tick()
                    ix = ix + 1
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

        N = 8

        async def stimulus(ctx):
            # Send a few sample points to the stroke
            for n in range(N):
                await stream.put(ctx, dut.i, [0, 0, 0, 0])
                await ctx.tick().repeat(4)

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            ctx.set(fb.enable, 1)
            for _ in range(N):
                # Test passes if we got something
                _ = await stream.get(ctx, dut.plot_req)
                await ctx.tick()

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        sim.add_process(stimulus)
        with sim.write_vcd(vcd_file=open("test_stroke.vcd", "w")):
            sim.run()

    def test_plot_backend(self):

        m = Module()
        fb = framebuffer.DMAFramebuffer(
            fixed_modeline=self.MODELINE, palette=palette.ColorPalette())
        dut = plot._FramebufferBackend(fb=fb)
        check = wishbone.BusChecker(dut.bus, prefix='[bus] ')
        m.submodules += [dut, fb, fb.palette, check]

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            ctx.set(fb.enable, 1)

            # Absolute positioning with replacement
            await stream.put(ctx, dut.req, {
                'x': 1,
                'y': 0,
                'pixel': {
                    'color': 0xa,
                    'intensity': 0xb,
                },
                'blend': plot.BlendMode.REPLACE,
                'offset': plot.OffsetMode.ABSOLUTE,
            })
            result = await wishbone.classic_ack(ctx, dut.bus)
            self.assertEqual(result.adr, 0x0)
            self.assertEqual(result.dat_w, 0xbabababa)
            self.assertEqual(result.sel, 0b0010)

            # Center positioning with replacement
            await stream.put(ctx, dut.req, {
                'x': 1,
                'y': 0,
                'pixel': {
                    'color': 0xa,
                    'intensity': 0xb,
                },
                'blend': plot.BlendMode.REPLACE,
                'offset': plot.OffsetMode.CENTER,
            })
            result = await wishbone.classic_ack(ctx, dut.bus)
            self.assertEqual(
                result.adr,
                int(self.MODELINE.h_active/4*(self.MODELINE.v_active/2 + 1/2)))
            self.assertEqual(result.dat_w, 0xbabababa)
            self.assertEqual(result.sel, 0b0010)

            # Absolute positioning, additive blending
            await stream.put(ctx, dut.req, {
                'x': 1,
                'y': 0,
                'pixel': {
                    'color': 0xa,
                    'intensity': 0xb,
                },
                'blend': plot.BlendMode.ADDITIVE,
                'offset': plot.OffsetMode.ABSOLUTE,
            })
            # Read cycle (get current pixel value)
            ctx.set(dut.bus.dat_r, 0x00009100)
            result = await wishbone.classic_ack(ctx, dut.bus)
            self.assertEqual(result.adr, 0x0)
            self.assertEqual(result.sel, 0b0010)
            # Write cycle (put newly calculated pixel value)
            result = await wishbone.classic_ack(ctx, dut.bus)
            self.assertEqual(result.adr, 0x0)
            self.assertEqual(result.sel, 0b0010)
            self.assertEqual(result.dat_w, 0xfafafafa)

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_plot_backend.vcd", "w")):
            sim.run()

    def test_blit_peripheral(self):

        m = Module()
        dut = blit.Peripheral()
        decoder = csr.Decoder(addr_width=28, data_width=8)
        decoder.add(dut.csr_bus, addr=0, name="dut")
        bridge = csr_wishbone.WishboneCSRBridge(decoder.bus, data_width=32)
        m.submodules += [dut, decoder, bridge]

        async def test_stimulus(ctx):

            async def csr_write(ctx, value, register, field=None):
                await csr_util.wb_csr_w(
                        ctx, dut.csr_bus, bridge.wb_bus, value, register, field)

            async def csr_read(ctx, register, field=None):
                return await csr_util.wb_csr_r(
                        ctx, dut.csr_bus, bridge.wb_bus, register, field)

            ctx.set(dut.enable, 1)

            # Write a font sheet to hardware memory
            with open('tests/data/font_9x15.raw', 'rb') as f:
                sheet_bytes = f.read()
            sheet_sx = 144  # sheet .raw data width
            sheet_sy = 90   # sheet .raw data height
            bytes_per_row = (sheet_sx + 7) // 8
            for y in range(sheet_sy):
                row_start_byte = y * bytes_per_row
                row_start_word = y * dut.column_words
                for word_in_row in range(dut.column_words):
                    word_value = 0
                    # Only fill with data if we're within the actual image width
                    if word_in_row * 32 < sheet_sx:
                        # Pack 4 bytes (32 pixels) into one 32-bit word
                        for byte_in_word in range(4):
                            byte_idx = row_start_byte + (word_in_row * 4 + byte_in_word)
                            if byte_idx < len(sheet_bytes):
                                word_value |= sheet_bytes[byte_idx] << (byte_in_word * 8)
                        word_offset = row_start_word + word_in_row
                        await wishbone.classic_wr(ctx, dut.sprite_mem_bus, adr=word_offset, dat_w=word_value)

            # Issue a blit
            # width=0x28, height=0x24, x=0, y=0
            await csr_write(ctx, 0x24280000, "src")
            # pixel=0xab, x=5, y=3
            await csr_write(ctx, (0xab<<24) | (0x3<<12) | 0x5, "blit")

            while True:
                await ctx.tick()

        async def test_response(ctx):
            # Collect all the blitted points into an ASCII grid, and print it
            ctx.set(dut.plot_req.ready, 1)
            points = set()
            for _ in range(10000):
                if ctx.get(dut.plot_req.valid):
                    p_x = ctx.get(dut.plot_req.payload.x)
                    p_y = ctx.get(dut.plot_req.payload.y)
                    points.add((p_x, p_y))
                await ctx.tick()
            for y in range(60):
                row = ''
                for x in range(60):
                    if (x, y) in points:
                        row = row+'#'
                    else:
                        row = row+'.'
                print(row)

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(test_stimulus, background=True)
        sim.add_testbench(test_response)
        with sim.write_vcd(vcd_file=open("test_blit_peripheral.vcd", "w")):
            sim.run()
