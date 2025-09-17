# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import unittest

from amaranth import *
from amaranth.lib import wiring
from amaranth.sim import *

from tiliqua.test import wishbone, psram
from tiliqua.cache import WishboneL2Cache

class CacheTests(unittest.TestCase):
    def setUp(self):
        self.cache = WishboneL2Cache(
            cachesize_words=64,
            addr_width=22,
            data_width=32,
            granularity=8,
            burst_len=4
        )
        self.psram = psram.FakePSRAM()

    def test_cache_basic_operations(self):

        m = Module()

        m.submodules.cache = self.cache
        m.submodules.psram = self.psram

        wiring.connect(m, self.cache.slave, self.psram.bus)

        m.submodules.m_check = wishbone.BusChecker(self.cache.master, prefix='[usr] ')
        m.submodules.s_check = wishbone.BusChecker(self.cache.slave, prefix='[ram] ')

        async def testbench(ctx):
            master = self.cache.master

            # Test 1: Simple read miss (should trigger refill)
            await wishbone.classic_rd(ctx, master, adr=0x100)

            # Test 2: Read hit to same cache line (should be fast)
            await wishbone.classic_rd(ctx, master, adr=0x101)

            # Test 3: Write operation
            await wishbone.classic_wr(ctx, master, adr=0x101, dat_w=0xdeadbeef)

            # Test 4: Read back the written data
            data = await wishbone.classic_rd(ctx, master, adr=0x101)
            self.assertEqual(data, 0xdeadbeef)

            # Test 5: Miss to different cache line (should trigger evict + refill)
            await wishbone.classic_rd(ctx, master, adr=0x180)

            # Test 6: Read back the data flushed earlier
            data = await wishbone.classic_rd(ctx, master, adr=0x101)
            self.assertEqual(data, 0xdeadbeef)

        sim = Simulator(m)
        sim.add_clock(1e-6)  # 1MHz clock
        sim.add_testbench(testbench)

        with sim.write_vcd(vcd_file=open("test_cache_basic.vcd", "w")):
            sim.run()

if __name__ == "__main__":
    unittest.main()
