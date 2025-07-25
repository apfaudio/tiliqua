import sys
import math
import unittest

from amaranth              import *
from amaranth.sim          import *
from amaranth.utils        import exact_log2
from amaranth.lib          import wiring

from amaranth_future       import fixed

from tiliqua.eurorack_pmod import ASQ
from tiliqua               import cordic

class CordicTests(unittest.TestCase):

    SHAPE = ASQ

    def test_cordic_vector(self):

        dut = cordic.RectToPolarCordic(self.SHAPE)

        async def send_complex(ctx, real, imag):
            ctx.set(dut.i.payload.real, fixed.Const(real, shape=self.SHAPE, clamp=True))
            ctx.set(dut.i.payload.imag, fixed.Const(imag, shape=self.SHAPE, clamp=True))
            ctx.set(dut.i.valid, 1)
            while not ctx.get(dut.i.ready):
                await ctx.tick()
            await ctx.tick()
            ctx.set(dut.i.valid, 0)

        async def receive_result(ctx):
            while not ctx.get(dut.o.valid):
                await ctx.tick()
            mag = ctx.get(dut.o.payload.magnitude).as_float()
            phase = ctx.get(dut.o.payload.phase).as_float()
            ctx.set(dut.o.ready, 1)
            await ctx.tick()
            ctx.set(dut.o.ready, 0)
            return mag, phase

        async def test_case(ctx, real, imag, name=""):
            # Calculate expected values
            expected_mag = math.sqrt(real**2 + imag**2)
            expected_phase = math.atan2(imag, real)/math.pi
            # Send stimulus, wait for result
            await send_complex(ctx, real, imag)
            mag, phase = await receive_result(ctx)
            # Calculate and print errors
            mag_error = abs(mag - expected_mag)
            phase_error = abs(phase - expected_phase)
            print(f"\n{name}")
            print(f"  Input: ({real:.4f}, {imag:.4f})")
            print(f"  Expected: mag={expected_mag:.4f}, phase={expected_phase:.4f} * pi")
            print(f"  Got:      mag={mag:.4f}, phase={phase:.4f} * pi")
            print(f"  Error:    mag={mag_error:.6f}, phase={phase_error:.6f} * pi")
            # Check for reasonable accuracy (considering fixed-point limitations)
            self.assertLess(mag_error, 0.01, f"Magnitude error too large for {name}")
            self.assertLess(phase_error, 0.01, f"Phase error too large for {name}")
            return mag, phase

        async def testbench(ctx):
            # Reset
            ctx.set(dut.o.ready, 0)
            ctx.set(dut.i.valid, 0)
            await ctx.tick().repeat(2)
            # Cover all quadrants and some edge cases
            test_cases = [
                # Quadrant 1
                (1.0, 0.0, "Positive real axis"),
                (0.0, 1.0, "Positive imaginary axis"),
                (0.707, 0.707, "45 degrees"),
                (0.5, 0.866, "60 degrees"),
                # Quadrant 2
                (-1.0, 0.0, "Negative real axis"),
                (-0.707, 0.707, "135 degrees"),
                # Quadrant 3
                (-0.707, -0.707, "225 degrees"),
                (-0.5, -0.866, "240 degrees"),
                # Quadrant 4
                (0.0, -1.0, "Negative imaginary axis"),
                (0.707, -0.707, "315 degrees"),
                # Small values
                (0.1, 0.1, "Small values"),
                # Near maximum values (considering fixed point range)
                (1.0, 1.0, "Large values"),
                (-1.0, 1.0, "Large values"),
            ]
            for real, imag, name in test_cases:
                await test_case(ctx, real, imag, name)
                # Wait a few cycles between tests
                await ctx.tick().repeat(5)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_cordic.vcd", "w")):
            sim.run()
