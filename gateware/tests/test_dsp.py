# Copyright (c) 2024 Seb Holzapfel, apfelaudio UG <info@apfelaudio.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import sys
import unittest

import math

from amaranth              import *
from amaranth.sim          import *
from amaranth_future       import fixed
from amaranth.lib          import wiring, data
from tiliqua.eurorack_pmod import ASQ

from tiliqua import dsp, delay_line

class DSPTests(unittest.TestCase):

    def test_pitch(self):

        m = Module()
        delayln = delay_line.DelayLine(max_delay=256, write_triggers_read=False)
        pitch_shift = dsp.PitchShift(tap=delayln.add_tap(), xfade=32)
        m.submodules += [delayln, pitch_shift]

        async def testbench(ctx):
            await ctx.tick()
            await ctx.tick()
            for n in range(0, 1000):
                x = fixed.Const(0.8*math.sin(n*0.1), shape=ASQ)
                ctx.set(delayln.i.valid, 1)
                ctx.set(delayln.i.payload, x)
                await ctx.tick()
                ctx.set(delayln.i.valid, 0)
                await ctx.tick()
                await ctx.tick()
                ctx.set(pitch_shift.i.payload.pitch, 
                    fixed.Const(-0.8, shape=pitch_shift.dtype))
                ctx.set(pitch_shift.i.payload.grain_sz, 
                    delayln.max_delay//2)
                ctx.set(pitch_shift.o.ready, 1)
                ctx.set(pitch_shift.i.valid, 1)
                await ctx.tick()
                ctx.set(pitch_shift.i.valid, 0)
                await ctx.tick()
                while ctx.get(pitch_shift.i.ready) != 1:
                    await ctx.tick()

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_pitch.vcd", "w")):
            sim.run()


    def test_svf(self):

        svf = dsp.SVF()

        async def testbench(ctx):
            for n in range(0, 100):
                x = fixed.Const(0.4*(math.sin(n*0.2) + math.sin(n)), shape=ASQ)
                ctx.set(svf.i.payload.x, x)
                ctx.set(svf.i.payload.cutoff, fixed.Const(0.3, shape=ASQ))
                ctx.set(svf.i.payload.resonance, fixed.Const(0.1, shape=ASQ))
                ctx.set(svf.i.valid, 1)
                await ctx.tick()
                ctx.set(svf.i.valid, 0)
                await ctx.tick().repeat(8)
                out0 = ctx.get(svf.o.payload.hp)
                out1 = ctx.get(svf.o.payload.lp)
                out2 = ctx.get(svf.o.payload.bp)
                print(out0, out1, out2)
                await ctx.tick()
                ctx.set(svf.o.ready, 1)
                await ctx.tick()
                ctx.set(svf.o.ready, 0)
                await ctx.tick()

        sim = Simulator(svf)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_svf.vcd", "w")):
            sim.run()

    def test_matrix(self):

        matrix = dsp.MatrixMix(
            i_channels=4, o_channels=4,
            coefficients=[[1, 0, 0, 0],
                          [0, 1, 0, 0],
                          [0, 0, 1, 0],
                          [0, 0, 0, 1]])

        async def testbench(ctx):
            ctx.set(matrix.i.payload[0], fixed.Const(0.2, shape=ASQ))
            ctx.set(matrix.i.payload[1], fixed.Const(-0.4,  shape=ASQ))
            ctx.set(matrix.i.payload[2], fixed.Const(0.6,  shape=ASQ))
            ctx.set(matrix.i.payload[3], fixed.Const(-0.8,  shape=ASQ))
            ctx.set(matrix.i.valid, 1)
            await ctx.tick()
            ctx.set(matrix.i.valid, 0)
            await ctx.tick()
            ctx.set(matrix.o.ready, 1)
            while ctx.get(matrix.o.valid) != 1:
                await ctx.tick()
            self.assertAlmostEqual(ctx.get(matrix.o.payload[0]).as_float(),  0.2, places=4)
            self.assertAlmostEqual(ctx.get(matrix.o.payload[1]).as_float(), -0.4, places=4)
            self.assertAlmostEqual(ctx.get(matrix.o.payload[2]).as_float(),  0.6, places=4)
            self.assertAlmostEqual(ctx.get(matrix.o.payload[3]).as_float(), -0.8, places=4)

        sim = Simulator(matrix)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_matrix.vcd", "w")):
            sim.run()

    def test_fixed_min_max(self):
        self.assertIn("7'sd63", fixed.SQ(2, 4).max().__repr__())
        self.assertIn("7'sd-64", fixed.SQ(2, 4).min().__repr__())
        self.assertIn("16'sd32767", ASQ.max().__repr__())
        self.assertIn("16'sd-32768", ASQ.min().__repr__())

    def test_waveshaper(self):

        def scaled_tanh(x):
            return math.tanh(3.0*x)

        waveshaper = dsp.WaveShaper(lut_function=scaled_tanh, lut_size=16)

        async def testbench(ctx):
            await ctx.tick()
            for n in range(0, 100):
                x = fixed.Const(math.sin(n*0.10), shape=ASQ)
                ctx.set(waveshaper.i.payload, x)
                ctx.set(waveshaper.i.valid, 1)
                ctx.set(waveshaper.o.ready, 1)
                await ctx.tick()
                ctx.set(waveshaper.i.valid, 0)
                while ctx.get(waveshaper.o.valid) != 1:
                    await ctx.tick()
                await ctx.tick()

        sim = Simulator(waveshaper)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_waveshaper.vcd", "w")):
            sim.run()

    def test_gainvca(self):

        def scaled_tanh(x):
            return math.tanh(3.0*x)

        m = Module()
        vca = dsp.GainVCA()
        waveshaper = dsp.WaveShaper(lut_function=scaled_tanh)

        m.submodules += [vca, waveshaper]

        m.d.sync += [
            waveshaper.i.payload.eq(vca.o.payload),
        ]

        async def testbench(ctx):
            await ctx.tick()
            for n in range(0, 100):
                x = fixed.Const(0.8*math.sin(n*0.3), shape=ASQ)
                gain = fixed.Const(3.0*math.sin(n*0.1), shape=fixed.SQ(2, ASQ.f_width))
                ctx.set(vca.i.payload.x, x)
                ctx.set(vca.i.payload.gain, gain)
                ctx.set(vca.i.valid, 1)
                await ctx.tick()

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_gainvca.vcd", "w")):
            sim.run()

    def test_nco(self):

        m = Module()

        def sine_osc(x):
            return math.sin(math.pi*x)

        nco = dsp.SawNCO()
        waveshaper = dsp.WaveShaper(lut_function=sine_osc, lut_size=128,
                                    continuous=True)

        m.submodules += [nco, waveshaper]

        wiring.connect(m, nco.o, waveshaper.i)

        async def testbench(ctx):
            ctx.set(waveshaper.o.ready, 1)
            await ctx.tick()
            for n in range(0, 400):
                phase = fixed.Const(0.1*math.sin(n*0.10), shape=ASQ)
                ctx.set(nco.i.payload.freq_inc, 0.66)
                ctx.set(nco.i.payload.phase, phase)
                ctx.set(nco.i.valid, 1)
                await ctx.tick()
                ctx.set(nco.i.valid, 0)
                await ctx.tick()
                while ctx.get(waveshaper.o.valid) != 1:
                    await ctx.tick()
                await ctx.tick()

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_nco.vcd", "w")):
            sim.run()

    def test_fir(self):

        fir = dsp.FIR(fs=48000, filter_cutoff_hz=2000,
                      filter_order=10)

        async def testbench(ctx):
            for n in range(0, 100):
                x = fixed.Const(0.4*(math.sin(n*0.2) + math.sin(n)), shape=ASQ)
                ctx.set(fir.i.payload, x)
                ctx.set(fir.i.valid, 1)
                await ctx.tick()
                ctx.set(fir.i.valid, 0)
                await ctx.tick()
                while ctx.get(fir.o.valid) != 1:
                    await ctx.tick()
                out0 = ctx.get(fir.o.payload)
                ctx.set(fir.o.ready, 1)
                await ctx.tick()
                ctx.set(fir.o.ready, 0)
                await ctx.tick()

        sim = Simulator(fir)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_fir.vcd", "w")):
            sim.run()

    def test_resample(self):

        N_UP   = 3
        M_DOWN = 2

        resample = dsp.Resample(fs_in=48000, n_up=N_UP, m_down=M_DOWN)

        async def testbench(ctx):
            for n in range(0, 100):
                x = fixed.Const(0.4*(math.sin(n*0.2) + math.sin(n)), shape=ASQ)
                ctx.set(resample.i.payload, x)
                ctx.set(resample.i.valid, 1)
                await ctx.tick()
                ctx.set(resample.i.valid, 0)
                await ctx.tick()
                ctx.set(resample.o.ready, 1)
                while ctx.get(resample.i.ready) != 1:
                    await ctx.tick()
                await ctx.tick()

        sim = Simulator(resample)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_resample.vcd", "w")):
            sim.run()

    def test_boxcar(self):

        boxcar = dsp.Boxcar(n=4, hpf=True)

        async def testbench(ctx):
            for n in range(0, 1024):
                x = fixed.Const(0.1+0.4*(math.sin(n*0.2) + math.sin(n)), shape=ASQ)
                ctx.set(boxcar.i.payload, x)
                ctx.set(boxcar.i.valid, 1)
                await ctx.tick()
                ctx.set(boxcar.i.valid, 0)
                await ctx.tick()
                ctx.set(boxcar.o.ready, 1)
                while ctx.get(boxcar.i.ready) != 1:
                    await ctx.tick()
                await ctx.tick()

        sim = Simulator(boxcar)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_boxcar.vcd", "w")):
            sim.run()
