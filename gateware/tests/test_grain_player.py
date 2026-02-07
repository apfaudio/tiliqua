# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import math
import unittest

from amaranth import *
from amaranth.lib import wiring
from amaranth.sim import *

from amaranth_future import fixed
from amaranth_soc import csr
from amaranth_soc.csr import wishbone as csr_wishbone

from tiliqua import dsp
from tiliqua.dsp import ASQ
from tiliqua.periph import grain_player
from tiliqua.periph.grain_player import GrainPlayer
from tiliqua.test import stream, csr as csr_util


class GrainPlayerTests(unittest.TestCase):

    def test_grain_player_peripheral(self):

        m = Module()

        # SRAM-backed delay line so we don't need a memory sim
        delayln = dsp.DelayLine(max_delay=256, write_triggers_read=False)
        m.submodules.delayln = delayln

        dut = grain_player.Peripheral(delayln)
        m.submodules.dut = dut

        # CSR access
        decoder = csr.Decoder(addr_width=28, data_width=8)
        decoder.add(dut.csr_bus, addr=0, name="dut")
        bridge = csr_wishbone.WishboneCSRBridge(decoder.bus, data_width=32)
        m.submodules += [decoder, bridge]

        test_samples = [
            fixed.Const(0.5, shape=ASQ),
            fixed.Const(-0.25, shape=ASQ),
            fixed.Const(0.75, shape=ASQ),
            fixed.Const(-0.5, shape=ASQ),
        ]

        async def write_samples(ctx):
            for sample in test_samples:
                await stream.put(ctx, delayln.i, sample)
                await ctx.tick().repeat(10)
            while True:
                await ctx.tick()

        async def testbench(ctx):

            async def csr_write(register, fields):
                await csr_util.wb_csr_w_dict(
                    ctx, dut.csr_bus, bridge.wb_bus, register, fields)

            # Wait for test samples to arrive in delay line
            await ctx.tick().repeat(20)

            await csr_write("start", {"start": 4})
            await csr_write("length", {"length": 4})
            await csr_write("speed", {"speed": 0x100})

            # GATE mode
            await csr_write("control", {"gate": 1, "mode": GrainPlayer.Mode.GATE.value})
            output_samples = []
            for _ in range(8):
                sample = await stream.get(ctx, dut.o)
                output_samples.append(sample)
            print(f"gate mode: {[s.as_float() for s in output_samples]}")

            # Close gate
            await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.GATE.value})
            output_samples = []
            for _ in range(8):
                sample = await stream.get(ctx, dut.o)
                output_samples.append(sample)
            print(f"closed: {[s.as_float() for s in output_samples]}")

            # LOOP mode
            await csr_write("control", {"gate": 1, "mode": GrainPlayer.Mode.LOOP.value})
            output_samples = []
            for i in range(16):
                if i == 10:
                    # Close gate mid-loop
                    await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.GATE.value})
                sample = await stream.get(ctx, dut.o)
                output_samples.append(sample)
            print(f"loop/halt: {[s.as_float() for s in output_samples]}")

            # GATE mode, half speed
            await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.GATE.value})
            await csr_write("speed", {"speed": 0x80})
            await csr_write("control", {"gate": 1, "mode": GrainPlayer.Mode.GATE.value})
            output_samples = []
            for _ in range(16):
                sample = await stream.get(ctx, dut.o)
                output_samples.append(sample)
            print(f"halfspeed: {[s.as_float() for s in output_samples]}")

            # GATE mode, reversed
            await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.GATE.value, "reverse": 1})
            await csr_write("speed", {"speed": 0x100})
            await csr_write("control", {"gate": 1, "mode": GrainPlayer.Mode.GATE.value, "reverse": 1})
            output_samples = []
            for _ in range(8):
                sample = await stream.get(ctx, dut.o)
                output_samples.append(sample)
            print(f"reverse: {[s.as_float() for s in output_samples]}")

            # ONESHOT mode: play full length even if gate goes low
            await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.ONESHOT.value, "reverse": 0})
            await csr_write("control", {"gate": 1, "mode": GrainPlayer.Mode.ONESHOT.value})
            output_samples = []
            for i in range(8):
                if i == 2:
                    # Close gate early - should continue playing
                    await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.ONESHOT.value})
                sample = await stream.get(ctx, dut.o)
                output_samples.append(sample)
            print(f"oneshot: {[s.as_float() for s in output_samples]}")

            # BOUNCE mode: alternate direction at boundaries
            await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.BOUNCE.value})
            await csr_write("control", {"gate": 1, "mode": GrainPlayer.Mode.BOUNCE.value})
            output_samples = []
            for i in range(16):
                if i == 12:
                    # Close gate mid-bounce
                    await csr_write("control", {"gate": 0, "mode": GrainPlayer.Mode.GATE.value})
                sample = await stream.get(ctx, dut.o)
                output_samples.append(sample)
            print(f"bounce: {[s.as_float() for s in output_samples]}")

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(write_samples)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_grain_player_peripheral.vcd", "w")):
            sim.run()
