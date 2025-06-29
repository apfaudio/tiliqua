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

        fft = FixedPointFFT(pts=256)

        async def testbench(ctx):
            dut = fft
            PTS = 256
            LPTS = exact_log2(PTS)

            I =[0.5*cos(2*16*pi*i/PTS) for i in range(PTS)]
            Q =[0.5*sin(2*16*pi*i/PTS) for i in range(PTS)]

            # Loading window function
            # Rectangular
            WR =[0.999 for i in range(PTS)]
            # Flat top 1-1.93*cos(2*pi*i/PTS)+1.29*cos(4*pi*i/PTS)-0.388*cos(6*pi*i/PTS)+0.032*cos(8*pi*i/PTS)
            #WR =[1-1.93*cos(2*pi*i/PTS)+1.29*cos(4*pi*i/PTS)-0.388*cos(6*pi*i/PTS)+0.032*cos(8*pi*i/PTS) for i in range(PTS)]
            # Blackman Nuttall
            #WR =[0.3635819-0.4891775*cos(k*2*pi/PTS)+0.1365995*cos(k*4*pi/PTS)-0.0106411*cos(k*6*pi/PTS) for k in range(PTS)]
            WI =[0.0 for i in range(PTS)]

            await ctx.tick()
            ctx.set(dut.wf_start, 1)
            await ctx.tick()
            ctx.set(dut.wf_start, 0)
            await ctx.tick()
            await ctx.tick()
            await ctx.tick()

            for i in range(PTS):
                ctx.set(dut.wf_real, fixed.Const(WR[i], shape=dut.wshape))
                ctx.set(dut.wf_imag, fixed.Const(WI[i], shape=dut.wshape))
                await ctx.tick()
                ctx.set(dut.wf_strobe, 1)
                await ctx.tick()
                ctx.set(dut.wf_strobe, 0)
                await ctx.tick()
                await ctx.tick()
                await ctx.tick()

            # Waiting done
            for _ in range(16):
                await ctx.tick()

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

            # Looks that it will take ~13 cycles for read-butterfly-write
            for _ in range(PTS*LPTS*13):
                await ctx.tick()

        sim = Simulator(fft)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_fft.vcd", "w")):
            sim.run()

