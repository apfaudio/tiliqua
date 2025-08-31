import sys
import unittest
from math import cos, pi, sin

import numpy as np
from amaranth import *
from amaranth.lib import wiring
from amaranth.sim import *
from parameterized import parameterized

from amaranth_future import fixed
from tiliqua.dsp import fft

FFT_SZ = 16

class FFTTests(unittest.TestCase):

    @parameterized.expand([
        ["r_impulse", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1 if n == 0 else 0],
        ["i_impulse", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1j if n == 0 else 0],
        ["all_zero", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 0],
        ["r_all_one", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1],
        ["i_all_one", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1j],
        ["r_alternate", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1.0 if n % 2 == 0 else -1.0],
        ["i_alternate", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1j if n % 2 == 0 else -1j],
        ["e_even", FFT_SZ, fixed.SQ(2, 30),
         lambda n: cos(8*2*np.pi*n/FFT_SZ) + 1j * sin(8*2*np.pi*n/FFT_SZ)],
        ["e_fraction", FFT_SZ, fixed.SQ(2, 30),
         lambda n: cos((43./7)*2*np.pi*n/FFT_SZ) + 1j * sin((43./7)*2*np.pi*n/FFT_SZ)],
        ["r_cos_fraction", FFT_SZ, fixed.SQ(2, 30),
         lambda n: cos((43./7)*2*np.pi*n/FFT_SZ)],
        ["r_cos_fraction_small", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 0.1*cos((43./7)*2*np.pi*n/FFT_SZ)],
        ["i_cos_fraction", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1j*cos((43./7)*2*np.pi*n/FFT_SZ)],
        ["r_sin_fraction", FFT_SZ, fixed.SQ(2, 30),
         lambda n: sin((43./7)*2*np.pi*n/FFT_SZ)],
        ["i_sin_fraction", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1j*sin((43./7)*2*np.pi*n/FFT_SZ)],
        ["r_pulse", FFT_SZ, fixed.SQ(2, 30),
         lambda n: 1 if n < 4 else 0],
    ])
    def test_fft(self, name, sz, shape, stimulus_function):

        """
        For a set of stimuli, verify:
        1) The frequency response of our forward fft is numerically close to
           the frequency response of ``numpy.fft`` for the same time domain input.
        2) The time-domain signal after having passed through an ``ifft(fft(x))``
           round trip is numerically close to the original time domain signal.
        """

        m = Module()
        dut = fft.FFT(sz=sz, shape=shape)
        ifft = fft.FFT(sz=sz, shape=shape)
        wiring.connect(m, dut.o, ifft.i)
        m.d.comb += ifft.ifft.eq(1)
        m.d.comb += ifft.o.ready.eq(1)
        m.submodules.dut = dut
        m.submodules.ifft = ifft

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield (fixed.Const((stimulus_function(n)+0*1j).real, shape=shape),
                       fixed.Const((stimulus_function(n)+0*1j).imag, shape=shape))

        async def stimulus_i(ctx):
            s = stimulus_values()
            while True:
                ctx.set(dut.i.payload.first, 1)
                for _ in range(sz):
                    await ctx.tick().until(dut.i.ready)
                    real, imag = next(s)
                    ctx.set(dut.i.valid, 1)
                    ctx.set(dut.i.payload.sample.real, real)
                    ctx.set(dut.i.payload.sample.imag, imag)
                    await ctx.tick()
                    ctx.set(dut.i.valid, 0)
                    ctx.set(dut.i.payload.first, 0)
                    await ctx.tick()

        async def testbench(ctx):
            s_i = []
            s_f = []
            s_o = []
            def complex_from_payload(payload):
                return (ctx.get(payload.sample.real).as_float() +
                        1j * ctx.get(payload.sample.imag).as_float())
            while True:
                # Three tap-off points used for validation - before the
                # fft, after the fft, and after the ifft(fft(x)) round trip.
                if ctx.get(dut.i.valid & dut.i.ready):
                    # forward FFT inputs
                    s_i.append(complex_from_payload(dut.i.payload))
                if ctx.get(dut.o.valid & dut.o.ready):
                    # forward FFT outputs (frequency domain)
                    s_f.append(complex_from_payload(dut.o.payload))
                if ctx.get(ifft.o.valid & ifft.o.ready):
                    # inverse FFT outputs (should match original signal)
                    s_o.append(complex_from_payload(ifft.o.payload))
                    if len(s_o) == sz:
                        break
                await ctx.tick()

            # Convert results into numpy arrays of complex type. The simulation
            # may have fed more than 1 block into the fft by the time we have
            # enough output samples, so only take the first `sz` elements.
            s_i = np.array(s_i[:sz])
            s_f = np.array(s_f[:sz])
            s_o = np.array(s_o[:sz])

            # Validation criteria
            # Note: these tolerances depend on how wide the fixed point type is
            s_i_fft = np.fft.fft(s_i, norm="forward")
            s_freq_delta = np.abs(s_f - s_i_fft)
            assert np.all(s_freq_delta < 1.5e-9)
            s_time_delta = np.abs(s_o - s_i)
            assert np.all(s_time_delta < 1e-8)

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_fft_{name}.vcd", "w")):
            sim.run()

    @parameterized.expand([
        # 'Small' version of the STFT, with TDM-multiplexed FFT and Window blocks
        ["dual_cosine_small", 128, fft.STFTProcessor, fixed.SQ(2, 30),
         lambda n: 0.7*cos(2*pi*n/100) + 0.2*cos(2*pi*n/5)],
        # 'Large' version of the STFT, independent FFT/IFFT and Windowing blocks
        ["dual_cosine_pipelined", 128, fft.STFTProcessorPipelined, fixed.SQ(2, 30),
         lambda n: 0.7*cos(2*pi*n/100) + 0.2*cos(2*pi*n/5)],
    ])
    def test_stft(self, name, sz, cls, shape, stimulus_function):

        """
        Pass a time-domain test waveform through an STFT for resynthesis, connecting
        the frequency domain output directly to the input.

        The result should be a perfectly reconstructed time-domain signal, despite
        it having made the round trip through all our components (2x windowing,
        overlapping, overlap-add blocks, fft and ifft).
        """

        m = Module()
        m.submodules.dut = dut = cls(sz=sz, shape=shape)
        # Passthrough (resynthesize) in frequency domain.
        wiring.connect(m, dut.o_freq, dut.i_freq)
        m.d.comb += dut.o.ready.eq(1)

        def stimulus_values():
            for n in range(0, sys.maxsize):
                yield fixed.Const(stimulus_function(n), shape=shape)

        async def stimulus_i(ctx):
            s = stimulus_values()
            while True:
                await ctx.tick().until(dut.i.ready)
                ctx.set(dut.i.valid, 1)
                ctx.set(dut.i.payload, next(s))
                await ctx.tick()
                ctx.set(dut.i.valid, 0)
                await ctx.tick()

        async def testbench(ctx):
            N = sz
            samples_i = []
            samples_o = []
            while True:
                if ctx.get(dut.i.valid & dut.i.ready):
                    samples_i.append(ctx.get(dut.i.payload).as_float())
                if ctx.get(dut.o.valid & dut.o.ready):
                    samples_o.append(ctx.get(dut.o.payload).as_float())
                    if len(samples_o) == 2*N:
                        break
                await ctx.tick()
            # After 1 block of 'ramp-up' (zero-padded samples coming
            # from overlap-add reconstruction), verify the output perfectly
            # matches the input time-domain signal.
            s_i = np.array(samples_i[N:2*N], dtype=float)
            s_o = np.array(samples_o[N:2*N], dtype=float)
            s_io_delta = np.abs(s_o - s_i)
            print("Maximum difference between in/out samples:", max(s_io_delta))
            assert np.all(s_io_delta < 1e-7)
            """
            # Uncomment to see the input and output waveforms plotted. it's fun to
            # slice from 0 rather than N in samples_i/o, to see the ramp-up.
            import matplotlib.pyplot as plt
            plt.plot(s_i)
            plt.plot(s_o)
            plt.plot(s_o-s_i)
            plt.show()
            """

        sim = Simulator(m)
        sim.add_clock(1.667e-8)
        sim.add_process(stimulus_i)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_stft_{name}.vcd", "w")):
            sim.run()
