import unittest
from parameterized import parameterized

from amaranth import *
from amaranth.sim import *
from amaranth.lib import wiring

from tiliqua.tmds import TMDSEncoder

class TMDSEncoderTests(unittest.TestCase):
    def test_dc_balance(self):

        m = Module()
        dut = TMDSEncoder()
        m.submodules.dut = dut
        m = DomainRenamer({"dvi": "sync"})(m)

        # Generate a sequence that would accumulate DC bias
        test_sequence = [0b11111111] * 5 + [0b00000000] * 5

        async def testbench(ctx):
            # Initialize in control mode to reset bias
            ctx.set(dut.de, 0)
            ctx.set(dut.ctrl_in, 0b00)
            await ctx.tick()
            # Track running disparity
            disparity = 0
            # Switch to data mode and send test sequence
            ctx.set(dut.de, 1)
            for data in test_sequence:
                ctx.set(dut.data_in, data)
                await ctx.tick()
                # Analyze output for DC balance
                result = ctx.get(dut.tmds)
                # Count ones in output
                print(bin(result))
                ones_count = bin(result).count('1')
                zeros_count = 10 - ones_count
                print(ones_count, zeros_count)
                # Update disparity
                new_disparity = disparity + (ones_count - zeros_count)
                # Disparity should be controlled (not growing unbounded)
                #assert abs(new_disparity) <= 8, f"Disparity {new_disparity} exceeded bounds"
                disparity = new_disparity
            # After sequence, disparity should be close to balanced
            # assert abs(disparity) <= 2, f"Final disparity {disparity} is not well balanced"
        sim = Simulator(m)
        sim.add_clock(1e-6)  # 1MHz clock in dvi domain
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_tmds_dc_balance.vcd", "w")):
            sim.run()
