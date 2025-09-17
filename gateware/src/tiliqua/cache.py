# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Cache components, for accelerating memory accesses to a backing store.
"""

from amaranth import *
from amaranth.lib import data, wiring
from amaranth.lib.memory import Memory
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2
from amaranth_soc import wishbone


class WishboneL2Cache(wiring.Component):

    """
    Wishbone cache, designed to go between a wishbone master and backing store.

    This cache is direct-mapped and write-back.
    - 'direct-mapped': https://en.wikipedia.org/wiki/Cache_placement_policies
    - 'write-back': https://en.wikipedia.org/wiki/Cache_(computing)#Writing_policies

    The 'master' bus is for the wishbone master that uses the cache. It may only
    issue classic transactions (i.e no burst transactions).
    The 'slave' bus is for the backing store. The cache acts as a master on
    this bus in order to fill / evict cache lines. The cache will issue burst
    transactions of length `burst_len` whenever a cache line is to be evicted
    (written to the backing store) or refilled (read from the backing store).

    `cachesize_words` (in `data_width` words) is the size of the data store
    and must be a power of 2.

    This cache is a partial rewrite of the equivalent LiteX component:
    https://github.com/enjoy-digital/litex/blob/master/litex/soc/interconnect/wishbone.py

    Key differences to LiteX implementation:
    - Tags now include a 'valid' bit, so every cache line must be refilled
      after reset before it can be used (imporant for any component that is
      reading from external memory, particularly if contains data at boot).
    - Translation of bus data widths is removed and replaced with wishbone burst
      transactions of length matching the cache line. Cache lines themselves have
      have size (in bits) of `data_width*burst_len`.
    """

    def __init__(self, cachesize_words=64, addr_width=22, data_width=32,
                 granularity=8, burst_len=4):

        # Technically we should issue classic transactions to the backing
        # store if burst_len == 1, but this cache will always issue bursts.
        assert burst_len > 1

        self.cachesize_words = cachesize_words
        self.data_width      = data_width
        self.burst_len       = burst_len
        self.granularity     = granularity

        super().__init__({
            "master": In(wishbone.Signature(addr_width=addr_width,
                                            data_width=data_width,
                                            granularity=granularity)),
            "slave": Out(wishbone.Signature(addr_width=addr_width,
                                            data_width=data_width,
                                            granularity=granularity,
                                            features={"cti", "bte"})),
        })

    def elaborate(self, platform):
        m = Module()

        master = self.master
        slave  = self.slave

        dw_from = dw_to = self.data_width

        # Slice master.addr into 3 fields:
        # (MSB) adr_tag .. adr_line .. adr_offset (LSB)
        addressbits = len(slave.adr)
        offsetbits  = exact_log2(self.burst_len)
        linebits    = exact_log2(self.cachesize_words // self.burst_len)
        tagbits     = addressbits - linebits - offsetbits
        adr_offset  = master.adr.bit_select(0, offsetbits)
        adr_line    = master.adr.bit_select(offsetbits, linebits)
        adr_tag     = master.adr.bit_select(offsetbits+linebits, tagbits)

        # Similar usage as adr_offset, iterates from 0..burst_len when
        # refilling/evicting cache lines.
        burst_offset = Signal.like(adr_offset)
        burst_offset_lookahead = Signal.like(burst_offset)

        # Cache line (data) memory. Each line has (virtual) size `data_width*burst_len`.
        # 'burst_offset'/'adr_offset' index are just extra concatenated address lines.
        # This ensures DPRAM inference still works (it doesn't for shape > 32bits).
        m.submodules.data_mem = data_mem = Memory(
            shape=unsigned(self.data_width), depth=2**linebits*self.burst_len, init=[])
        wr_port = data_mem.write_port(granularity=self.granularity)
        rd_port = data_mem.read_port()


        write_from_slave = Signal()

        word_select = Const(1).replicate(dw_to//self.granularity)

        m.d.comb += [
            rd_port.addr.eq(Cat(adr_offset, adr_line)),
            slave.sel.eq(word_select),
            master.dat_r.eq(rd_port.data),
            slave.dat_w.eq(rd_port.data),
        ]

        with m.If(write_from_slave):
            m.d.comb += [
                wr_port.addr.eq(Cat(burst_offset, adr_line)),
                wr_port.data.eq(slave.dat_r),
                wr_port.en.eq(word_select),
            ]
        with m.Else():
            m.d.comb += wr_port.addr.eq(Cat(adr_offset, adr_line)),
            m.d.comb += wr_port.data.eq(master.dat_w),
            with m.If(master.cyc & master.stb & master.we & master.ack):
                m.d.comb += wr_port.en.eq(master.sel)

        # Tag storage memory. Maps addr_line (cache line address) to the higher order
        # bits of master.adr (adr_tag). If the adr_tag in the tag storage matches
        # the requested adr_tag, we know the cache line has the data we want.
        tag_layout = data.StructLayout({
            "tag": unsigned(tagbits),
            "dirty": unsigned(1),
            "valid": unsigned(1),
        })
        m.submodules.tag_mem = tag_mem= Memory(shape=tag_layout, depth=2**linebits, init=[])
        tag_wr_port = tag_mem.write_port()
        tag_rd_port = tag_mem.read_port(domain='comb')
        tag_do = Signal(shape=tag_layout)
        tag_di = Signal(shape=tag_layout)
        m.d.comb += [
            tag_do.eq(tag_rd_port.data),
            tag_wr_port.data.eq(tag_di),
        ]

        m.d.comb += [
            tag_wr_port.addr.eq(adr_line),
            tag_rd_port.addr.eq(adr_line),
            tag_di.tag.eq(adr_tag)
        ]

        m.d.comb += slave.adr.eq(Cat(burst_offset, adr_line, tag_do.tag))

        m.d.sync += master.ack.eq(0)

        with m.FSM() as fsm:

            with m.State("IDLE"):
                with m.If(master.cyc & master.stb):
                    m.next = "TEST_HIT"

            with m.State("WAIT"):
                m.next = "IDLE"

            with m.State("TEST_HIT"):
                with m.If((tag_do.tag == adr_tag) & tag_do.valid):
                    m.d.sync += master.ack.eq(1)
                    with m.If(master.we):
                        m.d.comb += [
                            tag_di.valid.eq(1),
                            tag_di.dirty.eq(1),
                            tag_wr_port.en.eq(1)
                        ]
                    m.next = "WAIT"
                with m.Else():
                    with m.If(tag_do.dirty):
                        m.d.comb += rd_port.addr.eq(Cat(burst_offset_lookahead, adr_line)),
                        m.next = "EVICT"
                    with m.Else():
                        # Write the tag to set the slave address for the cache refill.
                        m.d.comb += [
                            tag_di.valid.eq(1),
                            tag_wr_port.en.eq(1),
                        ]
                        m.next = "REFILL"

            with m.State("EVICT"):

                m.d.comb += [
                    slave.stb.eq(1),
                    slave.cyc.eq(1),
                    slave.we.eq(1),
                    slave.cti.eq(wishbone.CycleType.INCR_BURST),
                    rd_port.addr.eq(Cat(burst_offset_lookahead, adr_line)),
                ]

                with m.If(slave.ack):
                    m.d.comb += burst_offset_lookahead.eq(burst_offset+1)
                    m.d.sync += burst_offset.eq(burst_offset + 1)
                    with m.If(burst_offset == (self.burst_len - 1)):
                        m.d.comb += slave.cti.eq(wishbone.CycleType.END_OF_BURST)
                        m.next = "WAIT-REFILL"

            with m.State("WAIT-REFILL"):
                # Write the tag to set the slave address for the cache refill.
                m.d.comb += [
                    tag_di.valid.eq(1),
                    tag_wr_port.en.eq(1),
                ]
                # Deassert stb between EVICT/REFILL
                m.next = "REFILL"

            with m.State("REFILL"):
                m.d.comb += [
                    slave.stb.eq(1),
                    slave.cyc.eq(1),
                    slave.we.eq(0),
                    slave.cti.eq(wishbone.CycleType.INCR_BURST),
                ]
                with m.If(slave.ack):
                    m.d.comb += [
                        write_from_slave.eq(1),
                    ]
                    m.d.sync += burst_offset.eq(burst_offset + 1)
                    with m.If(burst_offset == (self.burst_len - 1)):
                        m.d.comb += slave.cti.eq(wishbone.CycleType.END_OF_BURST)
                        m.next = "TEST_HIT"

        return m


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


class PlotterCache(wiring.Component):

    """
    Cache optimized for use in stroke-raster conversion.

    Main difference is an extra arbiter to support multiple plotting cores, as well
    as a periodic cache flusher to avoid cache lines staying dirty (without hitting
    the persistance emulation) for too long.
    """

    def __init__(self, *, fb):

        # Instantiate a small cache and connect it to the backing store as a DMA master
        self.cache = WishboneL2Cache(
                addr_width=fb.bus.addr_width,
                cachesize_words=64)

        # Create an arbiter for different plotting cores to share
        self.arbiter = wishbone.Arbiter(
            addr_width=self.cache.master.addr_width,
            data_width=self.cache.master.data_width,
            granularity=self.cache.master.granularity,
        )

        # Periodically flush stale cache lines, so we still get a dead beam 'dot'
        # even if the beam is not being deflected despite the write-back cache.
        self.flusher = CacheFlusher(
            base=fb.fb_base,
            addr_width=self.cache.master.addr_width,
            burst_len=self.cache.burst_len)
        self.arbiter.add(self.flusher.bus)

        super().__init__({
            # Transactions to backing store
            "bus": Out(wishbone.Signature(addr_width=self.cache.slave.addr_width,
                                          data_width=self.cache.slave.data_width,
                                          granularity=self.cache.slave.granularity,
                                          features={"cti", "bte"})),
        })

    def add(self, bus):
        self.arbiter.add(bus)

    def elaborate(self, platform) -> Module:
        m = Module()

        wiring.connect(m, self.arbiter.bus, self.cache.master)
        wiring.connect(m, self.cache.slave, wiring.flipped(self.bus))

        m.submodules += self.cache
        m.submodules += self.flusher
        m.submodules += self.arbiter

        with m.If(self.cache.slave.ack):
            m.d.sync += self.flusher.enable.eq(1)

        return m
