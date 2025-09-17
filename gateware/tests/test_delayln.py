# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import math
import sys
import unittest

from amaranth import *
from amaranth.lib import wiring
from amaranth.sim import *
from amaranth_soc import wishbone
from parameterized import parameterized

from amaranth_future import fixed
from tiliqua import dsp
from tiliqua.dsp import ASQ
from tiliqua.test import wishbone, psram, stream

class DelayLineTests(unittest.TestCase):

    @parameterized.expand([
        ["b4_c64_lr_short_taps", 64,  4, 256, 1,   3],
        ["b4_c16_lr_long_taps",  16,  4, 256, 150, 220],
        ["b4_c64_lr_long_taps",  64,  4, 256, 150, 220],
        ["b4_c256_lr_long_taps", 256, 4, 256, 150, 220],
        ["b4_c64_lr_endpoints1", 64,  4, 256, 0,   255],
        ["b4_c64_lr_endpoints2", 64,  4, 256, 255, 0],
        ["b8_c64_lr_long_taps",  64,  8, 256, 150, 220],
    ])
    def test_psram_delayln(self, name, cachesize_words, cache_burst_len,
                           max_delay, tap1_delay, tap2_delay):

        cache_kwargs = {
            "burst_len":       cache_burst_len,
            "cachesize_words": cachesize_words,
        }

        m = Module()
        m.submodules.dut = dut = dsp.DelayLine(
            max_delay=max_delay,
            psram_backed=True,
            base=0x0,
            addr_width_o=22,
            write_triggers_read=True,
            cache_kwargs=cache_kwargs,
        )
        m.submodules.psram_c = wishbone.BusChecker(dut.bus)
        m.submodules.psram = _psram = psram.FakePSRAM(storage_words=dut.max_delay)
        wiring.connect(m, dut.bus, _psram.bus)

        tap1 = dut.add_tap(fixed_delay=tap1_delay)
        tap2 = dut.add_tap(fixed_delay=tap2_delay)

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield fixed.Const(0.8*math.sin(n*0.2), shape=ASQ)

        async def stimulus_i(ctx):
            """Send `stimulus_values` to the DUT."""
            s = stimulus_values()
            while True:
                await ctx.tick().until(dut.i.ready) # TODO: remove. bug?
                await stream.put(ctx, dut.i, next(s))

        def validate_tap(tap):
            """Verify tap outputs exactly match a delayed stimulus."""
            async def _validate_tap(ctx):
                s = stimulus_values()
                n_samples_o = 0
                while True:
                    expected_payload = next(s) if n_samples_o >= tap.fixed_delay else fixed.Const(0, shape=ASQ)
                    tap_out = await stream.get(ctx, tap.o)
                    assert ctx.get(tap_out == expected_payload)
                    n_samples_o += 1
            return _validate_tap

        async def testbench(ctx):
            """Top-level testbench."""

            n_samples_in    = 0
            n_samples_tap1  = 0
            n_samples_tap2  = 0

            n_write_bursts  = 0
            n_read_bursts   = 0

            for _ in range(max_delay*40):
                n_samples_in    += ctx.get(dut.i.valid & dut.i.ready)
                n_samples_tap1  += ctx.get(tap1.o.valid & tap1.o.ready)
                n_samples_tap2  += ctx.get(tap2.o.valid & tap2.o.ready)
                n_write_bursts  += ctx.get(
                    dut.bus.we & (dut.bus.cti == wishbone.CycleType.END_OF_BURST))
                n_read_bursts   += ctx.get(
                    ~dut.bus.we & (dut.bus.cti == wishbone.CycleType.END_OF_BURST))
                await ctx.tick()

            print()
            print("n_samples_in",   n_samples_in)
            print("n_samples_tap1", n_samples_tap1)
            print("n_samples_tap2", n_samples_tap2)
            print("n_write_bursts", n_write_bursts)
            print("n_read_bursts",  n_read_bursts)

            samples_per_burst = (n_samples_in + n_samples_tap1 + n_samples_tap2) / (n_write_bursts + n_read_bursts)

            print("samples_per_burst", samples_per_burst)

            assert n_samples_in > 100
            assert abs(n_samples_in - n_samples_tap1) < 2
            assert abs(n_samples_in - n_samples_tap2) < 2

            if cachesize_words > 64:
                # arbitrarily chosen based on current cache performance
                assert samples_per_burst > 2 * cache_burst_len

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_i)
        sim.add_testbench(validate_tap(tap1), background=True)
        sim.add_testbench(validate_tap(tap2), background=True)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_psram_delayln_{name}.vcd", "w")):
            sim.run()

    def test_sram_delayln(self):

        dut = dsp.DelayLine(
            max_delay=256,
            write_triggers_read=False,
        )

        tap1 = dut.add_tap()
        tap2 = dut.add_tap()

        async def stimulus_wr(ctx):
            for n in range(0, sys.maxsize):
                await stream.put(ctx, dut.i, fixed.Const(0.8*math.sin(n*0.2), shape=ASQ))
                await ctx.tick().repeat(30)

        async def stimulus_rd1(ctx):
            while True:
                await stream.put(ctx, tap1.i, 4)
                _ = await stream.get(ctx, tap1.o)

        async def stimulus_rd2(ctx):
            while True:
                await stream.put(ctx, tap2.i, 10)
                _ = await stream.get(ctx, tap2.o)

        async def testbench(ctx):
            n_rd1 = 0
            n_rd2 = 0
            for n in range(200):
                await ctx.tick()
                if ctx.get(tap1.o.valid) and ctx.get(tap1.o.ready):
                    n_rd1 += 1
                if ctx.get(tap2.o.valid) and ctx.get(tap2.o.ready):
                    n_rd2 += 1
            # both taps produced some output samples
            assert n_rd1 > 5
            assert n_rd2 > 5

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        sim.add_process(stimulus_wr)
        sim.add_process(stimulus_rd1)
        sim.add_process(stimulus_rd2)
        with sim.write_vcd(vcd_file=open("test_sram_delayln.vcd", "w")):
            sim.run()
