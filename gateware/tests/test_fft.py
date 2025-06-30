import sys
import unittest

from math import cos, sin, pi

from amaranth              import *
from amaranth.sim          import *
from amaranth.utils        import exact_log2
from amaranth.lib          import wiring

from amaranth_future       import fixed

from tiliqua.eurorack_pmod import ASQ
from tiliqua               import dsp

from vendor.fixedpointfft  import FixedPointFFT

from parameterized         import parameterized
import numpy as np
import scipy.fft

class FFTTests(unittest.TestCase):

    @parameterized.expand([
        ["dual_cosine", 256, fixed.SQ(1, 15), lambda n: 0.7*cos(2*pi*n/17) + 0.2*cos(2*pi*n/10)],
    ])
    def test_fft_ifft(self, name, pts, shape, stimulus_function):

        """
        Run FFT followed by IFFT and verify the result matches our original signal.
        """

        m = Module()

        # FFT directly followed by IFFT
        fft = FixedPointFFT(pts=pts, shape=shape)
        ifft = FixedPointFFT(pts=pts, shape=shape)
        m.d.comb += [
            fft.ifft.eq(0),
            ifft.ifft.eq(1),
        ]
        wiring.connect(m, fft.o, ifft.i)
        m.d.comb += ifft.o.ready.eq(1)
        m.submodules.fft = fft
        m.submodules.ifft = ifft

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield fixed.Const(stimulus_function(n), shape=fft.shape)

        async def stimulus_i(ctx):
            s = stimulus_values()
            while True:
                await ctx.tick().until(fft.i.ready)
                ctx.set(fft.i.valid, 1)
                ctx.set(fft.i.payload.sample.real, next(s))
                ctx.set(fft.i.payload.sample.imag, fixed.Const(0.0, shape=fft.shape))
                await ctx.tick()
                ctx.set(fft.i.valid, 0)
                await ctx.tick()

        async def testbench(ctx):
            samples_i = []
            samples_fr = []
            samples_fi = []
            samples_o = []
            while True:
                if ctx.get(fft.i.valid & fft.i.ready):
                    # forward FFT inputs
                    samples_i.append(ctx.get(fft.i.payload.sample.real).as_float())
                if ctx.get(fft.o.valid & fft.o.ready):
                    # forward FFT outputs (frequency domain)
                    samples_fr.append(ctx.get(fft.o.payload.sample.real).as_float())
                    samples_fi.append(ctx.get(fft.o.payload.sample.imag).as_float())
                if ctx.get(ifft.o.valid & ifft.o.ready):
                    # inverse FFT outputs (should match original signal)
                    samples_o.append(ctx.get(ifft.o.payload.sample.real).as_float())
                    if len(samples_o) == pts:
                        break
                await ctx.tick()

            s_i = np.array(samples_i[:pts], dtype=float)
            s_f = (np.array(samples_fr[:pts], dtype=float) +
                   1j * np.array(samples_fi[:pts], dtype=float))
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
        with sim.write_vcd(vcd_file=open("test_fft_ifft_{name}.vcd", "w")):
            sim.run()

