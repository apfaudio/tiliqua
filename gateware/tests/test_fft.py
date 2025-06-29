import unittest

from math import cos, sin, pi

from amaranth              import *
from amaranth.sim          import *
from amaranth.utils        import exact_log2

from amaranth_future       import fixed

from tiliqua.eurorack_pmod import ASQ
from tiliqua               import dsp

from vendor.fixedpointfft  import FixedPointFFT

class FFTTests(unittest.TestCase):

    def test_fft(self):

        m = Module()

        fft = FixedPointFFT(pts=256)
        ifft = FixedPointFFT(pts=256, ifft=True)

        m.d.comb += [
            ifft.in_i.eq(fft.out_real),
            ifft.in_q.eq(fft.out_imag),
            ifft.strobe_in.eq(fft.strobe_out),
        ]

        m.submodules.fft = fft
        m.submodules.ifft = ifft

        async def testbench(ctx):
            dut = fft
            PTS = 256
            LPTS = exact_log2(PTS)

            I =[0.5*cos(2*16*pi*i/PTS) for i in range(PTS)]
            Q =[0.5*sin(2*16*pi*i/PTS) for i in range(PTS)]

            # FFT
            await ctx.tick()
            ctx.set(dut.start, 1)
            await ctx.tick()
            ctx.set(dut.start, 0)
            await ctx.tick()
            await ctx.tick()
            await ctx.tick()

            for i in range(PTS):
                ctx.set(dut.in_i, fixed.Const(I[i], shape=dut.shape))
                ctx.set(dut.in_q, fixed.Const(Q[i], shape=dut.shape))
                await ctx.tick()
                ctx.set(dut.strobe_in, 1)
                await ctx.tick()
                ctx.set(dut.strobe_in, 0)
                await ctx.tick()
                await ctx.tick()
                await ctx.tick()

            for _ in range(PTS*LPTS*10):
                await ctx.tick()

            ctx.set(ifft.start, 1)
            await ctx.tick()
            ctx.set(ifft.start, 0)
            await ctx.tick()

            # Looks that it will take ~13 cycles for read-butterfly-write
            for _ in range(PTS*LPTS*20):
                await ctx.tick()

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_fft.vcd", "w")):
            sim.run()

