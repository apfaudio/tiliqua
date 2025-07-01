import sys
import unittest

from math import cos, sin, pi

from amaranth              import *
from amaranth.sim          import *
from amaranth.utils        import exact_log2
from amaranth.lib          import wiring

from amaranth_future       import fixed

from tiliqua.eurorack_pmod import ASQ
from tiliqua               import dsp, fft

from parameterized         import parameterized
import numpy as np
import scipy.fft

class FFTTests(unittest.TestCase):

    '''
    @parameterized.expand([
        ["dual_cosine", 256, fixed.SQ(1, 15), lambda n: 0.7*cos(2*pi*n/17) + 0.2*cos(2*pi*n/10)],
    ])
    def test_fft_ifft(self, name, sz, shape, stimulus_function):

        """
        Run FFT followed by IFFT and verify the result matches our original signal.
        """

        m = Module()

        # FFT directly followed by IFFT
        ffft = fft.FFT(sz=sz, shape=shape)
        ifft = fft.FFT(sz=sz, shape=shape)
        m.d.comb += [
            ffft.ifft.eq(0),
            ifft.ifft.eq(1),
        ]
        wiring.connect(m, ffft.o, ifft.i)
        m.d.comb += ifft.o.ready.eq(1)
        m.submodules.ffft = ffft
        m.submodules.ifft = ifft

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield fixed.Const(stimulus_function(n), shape=shape)

        async def stimulus_i(ctx):
            s = stimulus_values()
            while True:
                ctx.set(ffft.i.payload.first, 1)
                for _ in range(sz):
                    await ctx.tick().until(ffft.i.ready)
                    ctx.set(ffft.i.valid, 1)
                    ctx.set(ffft.i.payload.sample.real, next(s))
                    ctx.set(ffft.i.payload.sample.imag, fixed.Const(0.0, shape=shape))
                    await ctx.tick()
                    ctx.set(ffft.i.valid, 0)
                    ctx.set(ffft.i.payload.first, 0)
                    await ctx.tick()

        async def testbench(ctx):
            samples_i = []
            samples_fr = []
            samples_fi = []
            samples_o = []
            while True:
                if ctx.get(ffft.i.valid & ffft.i.ready):
                    # forward FFT inputs
                    samples_i.append(ctx.get(ffft.i.payload.sample.real).as_float())
                if ctx.get(ffft.o.valid & ffft.o.ready):
                    # forward FFT outputs (frequency domain)
                    samples_fr.append(ctx.get(ffft.o.payload.sample.real).as_float())
                    samples_fi.append(ctx.get(ffft.o.payload.sample.imag).as_float())
                if ctx.get(ifft.o.valid & ifft.o.ready):
                    # inverse FFT outputs (should match original signal)
                    samples_o.append(ctx.get(ifft.o.payload.sample.real).as_float())
                    if len(samples_o) == sz:
                        break
                await ctx.tick()

            s_i = np.array(samples_i[:sz], dtype=float)
            s_f = (np.array(samples_fr[:sz], dtype=float) +
                   1j * np.array(samples_fi[:sz], dtype=float))
            s_o = np.array(samples_o, dtype=float)
            s_i_fft = scipy.fft.fft(s_i, norm="forward")
            s_freq_delta = np.abs(s_f - s_i_fft)
            s_time_delta = np.abs(s_o - s_i)
            print(max(s_freq_delta), max(s_time_delta))
            # These tolerances depend on how wide the fixed point type is.
            assert np.all(s_freq_delta < 4e-5)
            assert np.all(s_time_delta < 5e-3)

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_fft_ifft_{name}.vcd", "w")):
            sim.run()

    @parameterized.expand([
        ["dual_cosine", 256, fixed.SQ(1, 15), lambda n: 0.7*cos(2*pi*n/17) + 0.2*cos(2*pi*n/10)],
    ])
    def test_fft_window(self, name, sz, shape, stimulus_function):

        m = Module()

        window = fft.Window(sz=sz, shape=shape)
        ffft = fft.FFT(sz=sz, shape=shape)
        wiring.connect(m, window.o, ffft.i)
        m.d.comb += ffft.o.ready.eq(1)
        m.submodules.ffft = ffft
        m.submodules.window = window

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield fixed.Const(stimulus_function(n), shape=shape)

        async def stimulus_i(ctx):
            s = stimulus_values()
            ctx.set(window.i.payload.first, 1)
            while True:
                await ctx.tick().until(window.i.ready)
                ctx.set(window.i.valid, 1)
                ctx.set(window.i.payload.sample, next(s))
                await ctx.tick()
                ctx.set(window.i.valid, 0)
                ctx.set(window.i.payload.first, 0)
                await ctx.tick()

        async def testbench(ctx):
            samples_i = []
            samples_fr = []
            samples_fi = []
            while True:
                if ctx.get(ffft.i.valid & ffft.i.ready):
                    # forward FFT inputs
                    samples_i.append(ctx.get(ffft.i.payload.sample.real).as_float())
                if ctx.get(ffft.o.valid & ffft.o.ready):
                    # forward FFT outputs (frequency domain)
                    samples_fr.append(ctx.get(ffft.o.payload.sample.real).as_float())
                    samples_fi.append(ctx.get(ffft.o.payload.sample.imag).as_float())
                    if len(samples_fr) == sz:
                        break
                await ctx.tick()

            s_i = np.array(samples_i[:sz], dtype=float)
            s_f = (np.array(samples_fr[:sz], dtype=float) +
                   1j * np.array(samples_fi[:sz], dtype=float))
            s_i_fft = scipy.fft.fft(s_i, norm="forward")
            s_freq_delta = np.abs(s_f - s_i_fft)
            print(max(s_freq_delta))

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_fft_window_{name}.vcd", "w")):
            sim.run()
    '''

    @parameterized.expand([
        ["dual_cosine", 256, fixed.SQ(1, 15), lambda n: 0.7*cos(2*pi*n/200) + 0.2*cos(2*pi*n/10)],
    ])
    def test_stft_window(self, name, sz, shape, stimulus_function):

        m = Module()

        window = fft.STFTWindow(sz=sz, shape=shape, n_overlap=sz//2)
        overlap = fft.OverlapAdd(sz=sz, shape=shape, n_overlap=sz//2)

        m.submodules.window = window
        m.submodules.window2 = window2 = fft.Window(sz=sz, shape=shape)
        m.submodules.overlap = overlap

        #wiring.connect(m, window.o, overlap.i)
        m.d.comb += overlap.o.ready.eq(1)

        ffft = fft.FFT(sz=sz, shape=shape)
        ifft = fft.FFT(sz=sz, shape=shape)
        m.d.comb += [
            ffft.ifft.eq(0),
            ifft.ifft.eq(1),
        ]
        m.submodules.ffft = ffft
        m.submodules.ifft = ifft
        wiring.connect(m, window.o, ffft.i)
        wiring.connect(m, ffft.o, ifft.i)
        wiring.connect(m, ifft.o, window2.i)
        wiring.connect(m, window2.o, overlap.i)

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield fixed.Const(stimulus_function(n), shape=shape)

        async def stimulus_i(ctx):
            s = stimulus_values()
            while True:
                await ctx.tick().until(window.i.ready)
                ctx.set(window.i.valid, 1)
                ctx.set(window.i.payload.real, next(s))
                await ctx.tick()
                ctx.set(window.i.valid, 0)
                await ctx.tick()

        async def testbench(ctx):
            N = sz
            samples_i = []
            samples_o = []
            while True:
                if ctx.get(window.i.valid & window.i.ready):
                    samples_i.append(ctx.get(window.i.payload.real).as_float())
                if ctx.get(overlap.o.valid & overlap.o.ready):
                    samples_o.append(ctx.get(overlap.o.payload).as_float())
                    if len(samples_o) == N:
                        break
                await ctx.tick()
            s_i = np.array(samples_i[:N], dtype=float)
            s_o = np.array(samples_o[:N], dtype=float)
            s_io_delta = np.abs(s_o - s_i)
            print(max(s_io_delta))
            #assert np.all(s_io_delta < 2e-4)
            import matplotlib.pyplot as plt
            plt.plot(s_i)
            plt.plot(s_o)
            plt.plot(s_o-s_i)
            plt.show()

        sim = Simulator(m)
        sim.add_clock(1.667e-8)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_stft_window_{name}.vcd", "w")):
            sim.run()
