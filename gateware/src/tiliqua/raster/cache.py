# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Cache components optimized for raster graphics operations.

These are wrappers for the existing WishboneL2Cache, with the
main differences being:

    A) periodic cache flushing (relevant for framebuffer writes)
    B) internal bus arbitration between multiple initiators

"""

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
from amaranth_soc import wishbone

from ..cache import WishboneL2Cache


class CacheFlusher(wiring.Component):

    """
    Periodically flush stale cache lines.
    """

    def __init__(self, *, base, addr_width, burst_len, flush_backoff_bits=10):
        self.base = base
        self.burst_len = burst_len
        self.flush_backoff_bits = flush_backoff_bits
        super().__init__({
            # Kick this to start the core
            "enable": In(1),
            # We are a DMA master (no burst support)
            "bus":  Out(wishbone.Signature(addr_width=addr_width, data_width=32, granularity=8)),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        bus = self.bus

        flush_wait = Signal(self.flush_backoff_bits, init=1)
        flush_adr  = Signal(16)

        m.d.comb += [
            bus.we.eq(0),
            bus.sel.eq(0xf),
            bus.adr.eq(self.base + flush_adr),
        ]

        with m.FSM() as fsm:

            with m.State('OFF'):
                with m.If(self.enable):
                    m.next = 'WAIT'

            with m.State('WAIT'):
                m.d.sync += flush_wait.eq(flush_wait+1)
                with m.If(flush_wait == 0):
                    m.next = 'READ'

            with m.State('READ'):
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                ]
                with m.If(bus.stb & bus.ack):
                    m.next = 'WAIT'
                    m.d.sync += flush_adr.eq(flush_adr + self.burst_len)

        return m


class Cache(wiring.Component):
    """
    Cache optimized for plot operations with integrated arbiter and flusher.
    """

    def __init__(self, fb, n_ports=1, cachesize_words=64):
        self.fb = fb
        self.n_ports = n_ports

        # L2 cache
        self.cache = WishboneL2Cache(
            addr_width=fb.bus.addr_width,
            cachesize_words=cachesize_words)

        # Arbiter for cache access
        self.arbiter = wishbone.Arbiter(
            addr_width=self.cache.master.addr_width,
            data_width=self.cache.master.data_width,
            granularity=self.cache.master.granularity,
        )

        # Cache flusher
        self.flusher = CacheFlusher(
            base=fb.fb_base,
            addr_width=self.cache.master.addr_width,
            burst_len=self.cache.burst_len)
        self.arbiter.add(self.flusher.bus)

        super().__init__({
            # Output to backing store
            "bus": Out(wishbone.Signature(addr_width=self.cache.slave.addr_width,
                                        data_width=self.cache.slave.data_width,
                                        granularity=self.cache.slave.granularity,
                                        features={"cti", "bte"})),
        })

    def add_port(self, bus):
        """Add a wishbone bus to the cache arbiter."""
        self.arbiter.add(bus)

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.cache = self.cache
        m.submodules.flusher = self.flusher
        m.submodules.arbiter = self.arbiter

        wiring.connect(m, self.arbiter.bus, self.cache.master)
        wiring.connect(m, self.cache.slave, wiring.flipped(self.bus))

        # Enable flusher when cache is active
        with m.If(self.cache.slave.ack):
            m.d.sync += self.flusher.enable.eq(1)

        return m
