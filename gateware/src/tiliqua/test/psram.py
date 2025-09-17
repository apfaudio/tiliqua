from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out
from amaranth.lib.memory import Memory

from amaranth_soc import wishbone

class FakePSRAM(wiring.Component):

    """
    Fake PSRAM core for testbenches. Simulates classic and burst transactions to
    a memory that has a high access latency, like our real PSRAM core.
    """

    def __init__(self, *, addr_width=22, data_width=32,
                 storage_words=512, latency_cycles=4):
        self.latency_cycles = latency_cycles
        self.storage_words = storage_words
        super().__init__({
            "bus": In(wishbone.Signature(
                addr_width=addr_width,
                data_width=data_width,
                granularity=8,
                features={"cti", "bte"}
            ))
        })

    def elaborate(self, platform):
        m = Module()

        bus = self.bus

        memory = Memory(shape=unsigned(self.bus.signature.data_width), depth=self.storage_words, init=[])
        m.submodules.memory = memory
        mem_wr_port = memory.write_port(granularity=8)
        mem_rd_port = memory.read_port()

        latency_counter = Signal(range(self.latency_cycles + 1))
        in_burst = Signal()
        burst_counter = Signal(8)

        prev_stb = Signal()
        m.d.sync += prev_stb.eq(bus.stb)

        m.d.comb += [
            mem_rd_port.addr.eq(bus.adr),
            mem_wr_port.addr.eq(bus.adr),
            mem_wr_port.data.eq(bus.dat_w),
            bus.dat_r.eq(mem_rd_port.data),
        ]

        m.d.sync += [
            # We simulate an address space larger than the amount of storage
            # we actually have. The test should be aware of this, check anyway.
            Assert(bus.adr < self.storage_words),
            # Real PSRAM core does not support accesses at byte granularity.
            Assert(bus.sel == 0b1111),
        ]

        m.d.sync += mem_wr_port.en.eq(0)

        with m.FSM():
            with m.State("IDLE"):
                m.d.sync += [
                    bus.ack.eq(0),
                    latency_counter.eq(0),
                    in_burst.eq(0),
                    burst_counter.eq(0),
                ]
                with m.If(bus.cyc & bus.stb):
                    is_burst = (bus.cti != wishbone.CycleType.CLASSIC)
                    m.d.sync += in_burst.eq(is_burst)
                    m.next = "LATENCY"

            with m.State("LATENCY"):
                m.d.sync += latency_counter.eq(latency_counter + 1)
                with m.If(latency_counter == (self.latency_cycles - 1)):
                    m.next = "RESPOND"

            with m.State("RESPOND"):
                m.d.sync += bus.ack.eq(1)

                with m.If(bus.we):
                    m.d.sync += mem_wr_port.en.eq(bus.sel)

                with m.If(bus.ack):
                    m.d.comb += mem_rd_port.addr.eq(bus.adr+1)

                with m.If(in_burst):
                    m.d.sync += burst_counter.eq(burst_counter + 1)
                    end_of_burst = (bus.cti == wishbone.CycleType.END_OF_BURST)
                    with m.If(end_of_burst):
                        m.d.sync += bus.ack.eq(0)
                        m.next = "IDLE"
                with m.Else():
                    m.next = "IDLE"

        return m
