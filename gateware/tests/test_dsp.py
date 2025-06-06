# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import sys
import unittest

import math
import itertools


from amaranth              import *
from amaranth.sim          import *
from amaranth_future       import fixed
from amaranth.lib          import wiring, data

from scipy                 import signal
from parameterized         import parameterized

from tiliqua.eurorack_pmod import ASQ
from tiliqua               import dsp, mac, delay_line, delay

class DSPTests(unittest.TestCase):


    @parameterized.expand([
        ["dual_sine_small",          100, 16, 1, 17, 0.005, lambda n: 0.4*(math.sin(n*0.2) + math.sin(n))],
        ["dual_sine_large",          100, 64, 1, 65, 0.005, lambda n: 0.4*(math.sin(n*0.2) + math.sin(n))],
        ["dual_sine_odd",            100, 59, 1, 60, 0.005, lambda n: 0.4*(math.sin(n*0.2) + math.sin(n))],
        ["impulse_small_9",          100,  9, 1, 10, 0.005, lambda n: 0.95 if n == 0 else 0.0],
        ["impulse_small_10",         100, 10, 1, 11, 0.005, lambda n: 0.95 if n == 0 else 0.0],
        ["impulse_small_16",         100, 16, 1, 17, 0.005, lambda n: 0.95 if n == 0 else 0.0],
        ["sine_interpolator_s1_n16", 100, 16, 1, 17, 0.005, lambda n: 0.9*math.sin(n*0.2) if n % 4 == 0 else 0.0],
        ["sine_interpolator_s2_n16", 100, 16, 2, 9,  0.005, lambda n: 0.9*math.sin(n*0.2) if n % 4 == 0 else 0.0],
        ["sine_interpolator_s4_n16", 100, 16, 4, 5,  0.005, lambda n: 0.9*math.sin(n*0.2) if n % 4 == 0 else 0.0],
        ["sine_interpolator_s2_n10", 100, 10, 2, 6,  0.005, lambda n: 0.9*math.sin(n*0.2) if n % 2 == 0 else 0.0],
        ["sine_interpolator_s3_n9",  100,  9, 3, 4,  0.005, lambda n: 0.9*math.sin(n*0.2) if n % 3 == 0 else 0.0],
    ])
    def test_fir(self, name, n_samples, n_order, stride_i, expected_latency, tolerance, stimulus_function):

        m = Module()
        dut = dsp.FIR(fs=48000, filter_cutoff_hz=2000,
                      filter_order=n_order, stride_i=stride_i)
        m.submodules.dut = dut

        # fake signals so we can see the expected output in VCD output.
        expected_output = Signal(ASQ)
        s_expected_output = Signal(ASQ)
        m.d.comb += s_expected_output.eq(expected_output)

        def stimulus_values():
            """Create fixed-point samples to stimulate the DUT."""
            for n in range(0, sys.maxsize):
                yield fixed.Const(stimulus_function(n), shape=ASQ)

        def expected_samples():
            """Same samples filtered by scipy.signal (should ~match those from our RTL)."""
            x = itertools.islice(stimulus_values(), n_samples)
            return signal.lfilter(dut.taps_float, [1.0], [v.as_float() for v in x])

        async def stimulus_i(ctx):
            """Send `stimulus_values` to the DUT."""
            s = stimulus_values()
            while True:
                await ctx.tick().until(dut.i.ready)
                ctx.set(dut.i.valid, 1)
                ctx.set(dut.i.payload, next(s))
                await ctx.tick()
                ctx.set(dut.i.valid, 0)
                await ctx.tick()

        async def testbench(ctx):
            """Observe and measure FIR filter outputs."""
            y_expected = expected_samples()
            n_samples_in = 0
            n_samples_out = 0
            n_latency = 0
            ctx.set(dut.o.ready, 1)
            for n in range(0, sys.maxsize):
                i_sample = ctx.get(dut.i.valid & dut.i.ready)
                o_sample = ctx.get(dut.o.valid & dut.o.ready)
                if i_sample:
                    n_samples_in += 1
                    n_latency     = 0
                if o_sample:
                    ctx.set(expected_output, fixed.Const(y_expected[n_samples_out], shape=ASQ))
                    # Verify latency and value of the payload is as we expect.
                    assert n_latency == expected_latency
                    if tolerance is not None:
                        assert abs(ctx.get(dut.o.payload).as_float() - y_expected[n_samples_out]) < tolerance
                    n_samples_out += 1
                    if n_samples_out == len(y_expected):
                        break
                await ctx.tick()
                n_latency += 1
            assert n_samples_in == n_samples
            assert n_samples_out == n_samples

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_fir_{name}.vcd", "w")):
            sim.run()

    @parameterized.expand([
        ["dual_sine_n4_m1",     100, 4,  1, 4,   1,   0.005, lambda n: 0.4*(math.sin(n*0.2) + math.sin(n))],
        # TODO (below this comment): all visually look correct, fix reference alignment and reduce tolerance.
        ["dual_sine_n1_m4",     100, 14, 0, 1,   4,   0.1,   lambda n: 0.4*(math.sin(n*0.2) + math.sin(n))],
        ["dual_sine_n2_m3",     100, 5,  0, 2,   3,   0.25,  lambda n: 0.4*(math.sin(n*0.2) + math.sin(n))],
        ["dual_sine_n441_m480", 50,  5,  0, 441, 480, 0.25,  lambda n: 0.4*(math.sin(n*0.2) + math.sin(n))],
    ])
    def test_resample(self, name, n_samples, n_pad, n_align, n_up, m_down, tolerance, stimulus_function):

        m = Module()
        dut = dsp.Resample(fs_in=48000, n_up=n_up, m_down=m_down, order_mult=8)
        m.submodules.dut = dut

        # fake signals so we can see the expected output in VCD output.
        expected_output = Signal(ASQ)
        s_expected_output = Signal(ASQ)
        m.d.comb += s_expected_output.eq(expected_output)

        def stimulus_values():
            """Create fixed-point samples to stimulate the DUT."""
            for n in range(0, sys.maxsize):
                yield fixed.Const(stimulus_function(n), shape=ASQ)

        def expected_samples():
            """Same samples filtered by scipy (should ~match those from our RTL)."""
            x = [v.as_float() for v in itertools.islice(stimulus_values(), n_samples)]
            # zero padding needed to align to the RTL outputs.
            x = [0]*n_pad + x
            resampled = signal.resample_poly(x, dut.n_up, dut.m_down, window=dut.filt.taps_float)
            aligned =  resampled[n_align:-10]
            return aligned

        async def stimulus_i(ctx):
            """Send `stimulus_values` to the DUT."""
            s = stimulus_values()
            while True:
                await ctx.tick().until(dut.i.ready)
                ctx.set(dut.i.valid, 1)
                ctx.set(dut.i.payload, next(s))
                await ctx.tick()
                ctx.set(dut.i.valid, 0)
                await ctx.tick()

        async def testbench(ctx):
            """Observe and measure resampler outputs."""
            y_expected = expected_samples()
            n_samples_in = 0
            n_samples_out = 0
            ctx.set(dut.o.ready, 1)
            for n in range(0, sys.maxsize):
                i_sample = ctx.get(dut.i.valid & dut.i.ready)
                o_sample = ctx.get(dut.o.valid & dut.o.ready)
                if i_sample:
                    n_samples_in += 1
                if o_sample:
                    # Verify value of the payload is as we expect.
                    assert abs(ctx.get(dut.o.payload).as_float() - y_expected[n_samples_out]) < tolerance
                    ctx.set(expected_output, fixed.Const(y_expected[n_samples_out], shape=ASQ))
                    n_samples_out += 1
                    if n_samples_out == len(y_expected):
                        break
                await ctx.tick()
            assert n_samples_out == len(y_expected)
            assert abs(n_samples_out - (n_samples * n_up / m_down)) < 10

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_resample_{name}.vcd", "w")):
            sim.run()

    @parameterized.expand([
        ["mux_mac", mac.MuxMAC],
        ["ring_mac", mac.RingMAC],
    ])
    def test_pitch(self, name, mac_type):

        m = Module()

        match mac_type:
            case mac.RingMAC:
                m.submodules.server = server = mac.RingMACServer()
                macp = server.new_client()
            case _:
                macp = None

        delayln = delay_line.DelayLine(max_delay=256, write_triggers_read=False)
        pitch_shift = dsp.PitchShift(tap=delayln.add_tap(), xfade=32, macp=macp)
        m.submodules += [delayln, pitch_shift]

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield fixed.Const(0.8*math.sin(n*0.2), shape=ASQ)

        async def stimulus_i(ctx):
            """Send `stimulus_values` to the DUT."""

            ctx.set(pitch_shift.i.payload.pitch,
                fixed.Const(0.5, shape=pitch_shift.dtype))
            ctx.set(pitch_shift.i.payload.grain_sz,
                delayln.max_delay//2)

            s = stimulus_values()
            while True:
                ctx.set(delayln.i.valid, 1)
                # First clock a sample into the delay line
                await ctx.tick().until(delayln.i.ready)
                ctx.set(delayln.i.payload, next(s))
                await ctx.tick()
                ctx.set(delayln.i.valid, 0)
                # Now clock a sample into the pitch shifter
                await ctx.tick().until(pitch_shift.i.ready)
                ctx.set(pitch_shift.i.valid, 1)
                await ctx.tick()
                ctx.set(pitch_shift.i.valid, 0)
                await ctx.tick()

        async def testbench(ctx):
            n_samples_in = 0
            n_samples_out = 0
            ctx.set(pitch_shift.o.ready, 1)
            for n in range(0, 7000):
                n_samples_in  += ctx.get(delayln.i.valid & delayln.i.ready)
                n_samples_out += ctx.get(pitch_shift.o.valid & pitch_shift.o.ready)
                await ctx.tick()
            print("n_samples_in",  n_samples_in)
            print("n_samples_out", n_samples_out)
            assert n_samples_in > 50
            assert (n_samples_out - n_samples_in) < 2

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_pitch_{name}.vcd", "w")):
            sim.run()


    @parameterized.expand([
        ["mux_mac", mac.MuxMAC],
        ["ring_mac", mac.RingMAC],
    ])
    def test_svf(self, name, mac_type):

        match mac_type:
            case mac.RingMAC:
                m = Module()
                m.submodules.server = server = mac.RingMACServer()
                m.submodules.svf = dut = dsp.SVF(macp=server.new_client())
            case _:
                m = Module()
                m.submodules.svf = dut = dsp.SVF()

        async def stimulus(ctx):
            for n in range(0, 200):
                x = fixed.Const(0.4*(math.sin(n*0.2) + math.sin(n)), shape=ASQ)
                y = fixed.Const(0.8*(math.sin(n*0.1)), shape=ASQ)
                ctx.set(dut.i.valid, 1)
                ctx.set(dut.i.payload.x, x)
                ctx.set(dut.i.payload.cutoff, y)
                ctx.set(dut.i.payload.resonance, fixed.Const(0.1, shape=ASQ))
                await ctx.tick().until(dut.i.ready)
                ctx.set(dut.i.valid, 0)

        async def testbench(ctx):
            ctx.set(dut.o.ready, 1)
            while True:
                await ctx.tick().until(dut.o.valid)
                out0 = ctx.get(dut.o.payload.hp)
                out1 = ctx.get(dut.o.payload.lp)
                out2 = ctx.get(dut.o.payload.bp)

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(stimulus)
        sim.add_testbench(testbench, background=True)
        with sim.write_vcd(vcd_file=open(f"test_svf_{name}.vcd", "w")):
            sim.run()

    def test_matrix(self):

        matrix = dsp.MatrixMix(
            i_channels=4, o_channels=4,
            coefficients=[[    1, 0,   0,  0],
                          [-0.25, 1,  -2,  0],
                          [    0, 0, 0.5,  0],
                          [    0, 0,   0,  1]])

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
            self.assertAlmostEqual(ctx.get(matrix.o.payload[0]).as_float(),  0.3, places=4)
            self.assertAlmostEqual(ctx.get(matrix.o.payload[1]).as_float(), -0.4, places=4)
            self.assertAlmostEqual(ctx.get(matrix.o.payload[2]).as_float(), -0.9, places=4)
            self.assertAlmostEqual(ctx.get(matrix.o.payload[3]).as_float(), -0.8, places=4)

        sim = Simulator(matrix)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_matrix.vcd", "w")):
            sim.run()

    @parameterized.expand([
        ["mux_mac", mac.MuxMAC],
        ["ring_mac", mac.RingMAC],
    ])
    def test_waveshaper(self, name, mac_type):

        def scaled_tanh(x):
            return math.tanh(3.0*x)

        match mac_type:
            case mac.RingMAC:
                m = Module()
                m.submodules.server = server = mac.RingMACServer()
                m.submodules.waveshaper = dut = dsp.WaveShaper(
                    lut_function=scaled_tanh, lut_size=16, macp=server.new_client())
            case _:
                m = Module()
                m.submodules.waveshaper = dut = dsp.WaveShaper(lut_function=scaled_tanh, lut_size=16)

        async def testbench(ctx):
            await ctx.tick()
            for n in range(0, 100):
                x = fixed.Const(math.sin(n*0.10), shape=ASQ)
                ctx.set(dut.i.payload, x)
                ctx.set(dut.i.valid, 1)
                ctx.set(dut.o.ready, 1)
                await ctx.tick()
                ctx.set(dut.i.valid, 0)
                while ctx.get(dut.o.valid) != 1:
                    await ctx.tick()
                await ctx.tick()

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_waveshaper_{name}.vcd", "w")):
            sim.run()

    def test_gainvca(self):

        def scaled_tanh(x):
            return math.tanh(3.0*x)

        m = Module()
        vca = dsp.VCA()
        waveshaper = dsp.WaveShaper(lut_function=scaled_tanh)

        m.submodules += [vca, waveshaper]

        m.d.sync += [
            waveshaper.i.payload.eq(vca.o.payload),
        ]

        async def testbench(ctx):
            await ctx.tick()
            for n in range(0, 100):
                x = fixed.Const(0.8*math.sin(n*0.3), shape=ASQ)
                gain = fixed.Const(3.0*math.sin(n*0.1), shape=vca.i.payload[0].shape())
                ctx.set(vca.i.payload[0], x)
                ctx.set(vca.i.payload[1], gain)
                ctx.set(vca.i.valid, 1)
                ctx.set(vca.o.ready, 1)
                await ctx.tick()
                ctx.set(vca.i.valid, 0)
                while ctx.get(vca.o.valid) != 1:
                    await ctx.tick()
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

    def test_boxcar(self):

        boxcar = delay.Boxcar(n=32, hpf=True)

        async def testbench(ctx):
            for n in range(0, 1024):
                x = fixed.Const(0.1+0.4*(math.sin(n*0.2) + math.sin(n)), shape=ASQ)
                ctx.set(boxcar.i.payload, x)
                ctx.set(boxcar.i.valid, 1)
                await ctx.tick()
                while ctx.get(boxcar.i.ready) != 1:
                    await ctx.tick()
                ctx.set(boxcar.i.valid, 0)
                await ctx.tick()
                ctx.set(boxcar.o.ready, 1)
                while ctx.get(boxcar.o.ready) != 1:
                    await ctx.tick()

        sim = Simulator(boxcar)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_boxcar.vcd", "w")):
            sim.run()

    def test_dcblock(self):

        dut = dsp.DCBlock()

        async def testbench(ctx):
            for n in range(0, 1024*20):
                x = fixed.Const(0.2+0.001*(math.sin(n*0.2) + math.sin(n)), shape=ASQ)
                ctx.set(dut.i.payload, x)
                ctx.set(dut.i.valid, 1)
                await ctx.tick()
                ctx.set(dut.i.valid, 0)
                await ctx.tick()
                ctx.set(dut.o.ready, 1)
                while ctx.get(dut.o.ready) != 1:
                    await ctx.tick()
                while ctx.get(dut.i.ready) != 1:
                    await ctx.tick()

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_dcblock.vcd", "w")):
            sim.run()
