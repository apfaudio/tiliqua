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

        fft = FixedPointFFT(bitwidth=18, pts=256)

        async def testbench(ctx):
            dut = fft
            PTS = 256
            LPTS = exact_log2(PTS)

            I =[int(cos(2*16*pi*i/PTS) * (2**16-1)) for i in range(PTS)]
            Q =[int(sin(2*16*pi*i/PTS) * (2**16-1)) for i in range(PTS)]

            # Loading window function
            # Rectangular
            WR =[(2**17-1) for i in range(PTS)]
            # Flat top 1-1.93*cos(2*pi*i/PTS)+1.29*cos(4*pi*i/PTS)-0.388*cos(6*pi*i/PTS)+0.032*cos(8*pi*i/PTS)
            #WR =[int((1-1.93*cos(2*pi*i/PTS)+1.29*cos(4*pi*i/PTS)-0.388*cos(6*pi*i/PTS)+0.032*cos(8*pi*i/PTS))*(2**17-1)) for i in range(PTS)]
            # Blackman Nuttall
            #WR =[int((0.3635819-0.4891775*cos(k*2*pi/PTS)+0.1365995*cos(k*4*pi/PTS)-0.0106411*cos(k*6*pi/PTS))*(2**17-1)) for k in range(PTS)]
            WI =[0 for i in range(PTS)]

            await ctx.tick()
            ctx.set(dut.wf_start, 1)
            await ctx.tick()
            ctx.set(dut.wf_start, 0)
            await ctx.tick()
            await ctx.tick()
            await ctx.tick()

            for i in range(PTS):
                ctx.set(dut.wf_real, WR[i])
                ctx.set(dut.wf_imag, WI[i])
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
                ctx.set(dut.in_i, I[i])
                ctx.set(dut.in_q, Q[i])
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

