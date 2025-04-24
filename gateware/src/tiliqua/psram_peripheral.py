# This file inherits a bit of `interfaces/psram` from LUNA, but is mostly new.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

from amaranth             import *
from amaranth.lib         import wiring
from amaranth.lib.wiring  import In, flipped
from amaranth.utils       import exact_log2

from amaranth_soc         import wishbone, csr
from amaranth_soc.memory  import MemoryMap

from vendor.psram_ospi    import OSPIPSRAM
from vendor.psram_hyper   import HyperPSRAM
from vendor.dqs_phy       import DQSPHY

from tiliqua              import sim

class Peripheral(wiring.Component):

    """
    Wishbone PSRAM peripheral with multiple masters and burst support.
    Includes some CSRs for measuring PSRAM bandwidth consumption.

    You can add this to an SoC as an ordinary peripheral, however it also
    has an internal arbiter (for multiple DMA masters) using add_master().

    Default region name is "ram" as that is accepted by luna-soc SVD generation
    as a memory region, in the future "psram" might also be acceptable.
    """

    # CSRs for measuring PSRAM bandwidth usage.
    #
    # Intended usage:
    # - Set 'collect' flag to 1: statistics are zeroed and collection starts.
    # - Wait a while until 'cycles_elapsed' has enough data for you.
    # - Set 'collect' flag to 0: all statistics are frozen.
    # - Read each of the register contents.
    # - When 'collect' is set to 1 again, statistics are re-zeroed before
    #   collection starts.

    class PsramStatsCtrl(csr.Register, access="w"):
        collect:        csr.Field(csr.action.W, unsigned(1))

    class PsramStatsReg0(csr.Register, access="r"):
        # Number of cycles we have collected statistics for.
        cycles_elapsed: csr.Field(csr.action.R, unsigned(32))

    class PsramStatsReg1(csr.Register, access="r"):
        # Number of 'cycles_elapsed' where the PSRAM was idle.
        # In general, the PSRAM busy time will be higher than
        # the ack_w + ack_r times measured below due to the
        # memory access latency. Thus, the difference between
        # ~idle cycles and ack_r+ack_w is the latency overhead,
        # usually dominated by small memory transactions.
        cycles_idle:    csr.Field(csr.action.R, unsigned(32))

    class PsramStatsReg2(csr.Register, access="r"):
        # Number of 'cycles_elapsed' where we read 1 word of
        # data (4 bytes) from the PSRAM controller.
        cycles_ack_r:   csr.Field(csr.action.R, unsigned(32))

    class PsramStatsReg3(csr.Register, access="r"):
        # Number of 'cycles_elapsed' where we write 1 word of
        # data (4 bytes) to the PSRAM controller.
        cycles_ack_w:   csr.Field(csr.action.R, unsigned(32))

    def __init__(self, *, size, data_width=32, granularity=8, name="psram"):
        if not isinstance(size, int) or size <= 0 or size & size-1:
            raise ValueError("Size must be an integer power of two, not {!r}"
                             .format(size))
        if size < data_width // granularity:
            raise ValueError("Size {} cannot be lesser than the data width/granularity ratio "
                             "of {} ({} / {})"
                              .format(size, data_width // granularity, data_width, granularity))

        self.size        = size
        self.granularity = granularity
        self.name        = name
        self.mem_depth   = (size * granularity) // data_width

        # memory map
        memory_map = MemoryMap(addr_width=exact_log2(size), data_width=granularity)
        memory_map.add_resource(name=("memory", self.name,), size=size, resource=self)

        # csrs
        regs = csr.Builder(addr_width=5, data_width=8)
        self._ctrl   = regs.add("ctrl",   self.PsramStatsCtrl(), offset=0x0)
        self._stats0 = regs.add("stats0", self.PsramStatsReg0(), offset=0x4)
        self._stats1 = regs.add("stats1", self.PsramStatsReg1(), offset=0x8)
        self._stats2 = regs.add("stats2", self.PsramStatsReg2(), offset=0xC)
        self._stats3 = regs.add("stats3", self.PsramStatsReg3(), offset=0x10)
        self._bridge = csr.Bridge(regs.as_memory_map())

        # bus
        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "bus": In(wishbone.Signature(addr_width=exact_log2(self.mem_depth),
                                         data_width=data_width,
                                         granularity=granularity,
                                         features={"cti", "bte"})),
            # internal psram simulation interface
            # should be optimized out in non-sim builds.
            "simif": In(sim.FakePSRAMSimulationInterface())
        })
        self.csr_bus.memory_map = self._bridge.bus.memory_map
        self.bus.memory_map = memory_map

        # hram arbiter
        self._hram_arbiter = wishbone.Arbiter(addr_width=exact_log2(self.mem_depth),
                                              data_width=data_width,
                                              granularity=granularity,
                                              features={"cti", "bte"})
        self._hram_arbiter.add(flipped(self.bus))
        self.shared_bus = self._hram_arbiter.bus

    def add_master(self, bus):
        self._hram_arbiter.add(bus)

    def elaborate(self, platform):
        m = Module()

        # csr bus
        m.submodules.bridge = self._bridge
        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        # arbiter
        m.submodules.arbiter = self._hram_arbiter

        if "APS256XXN" in platform.psram_id:
            self.psram = psram = OSPIPSRAM()
        elif "7KL1282GA" in platform.psram_id:
            self.psram = psram = HyperPSRAM()
        else:
            assert False, f"Unsupported PSRAM: {platform.psram_id}"

        if sim.is_hw(platform):
            # Real PHY and PSRAM controller
            self.psram_phy = DQSPHY()
            wiring.connect(m, psram.phy, self.psram_phy.phy)
            m.submodules += [self.psram_phy, self.psram]
        else:
            # PSRAM controller only, with fake PHY signals and simulation interface.
            m.submodules.psram = psram
            wiring.connect(m, self.simif, flipped(psram.simif))
            # Simulate DATAVALID delay after READ of ~ 8 cycles.
            phy_read_cnt = Signal(8)
            with m.If(psram.phy.read != 0):
                m.d.sync += phy_read_cnt.eq(phy_read_cnt + 1)
            with m.Else():
                m.d.sync += phy_read_cnt.eq(0)
            # Assert minimum PHY signals needed for psram to progress.
            m.d.comb += [
                psram.phy.ready.eq(1),
                psram.phy.burstdet.eq(1),
                psram.phy.datavalid.eq(phy_read_cnt > 8),
            ]

        counter      = Signal(range(128))
        timeout      = Signal(range(128))
        read_counter = Signal(range(32))
        readclksel   = Signal(3, reset=0)

        m.d.comb += [
            psram.single_page            .eq(0),
            psram.phy.readclksel         .eq(readclksel)
        ]

        m.d.sync += [
            psram.register_space         .eq(0),
            psram.start_transfer         .eq(0),
            psram.perform_write          .eq(0),
        ]

        with m.FSM() as fsm:

            # Initialize memory registers (read/write timings) before
            # we kick off memory training.
            for state, state_next, reg_mr, reg_data in platform.psram_registers:
                with m.State(state):
                    with m.If(psram.idle & ~psram.start_transfer):
                        m.d.sync += [
                            psram.start_transfer.eq(1),
                            psram.register_space.eq(1),
                            psram.perform_write .eq(1),
                            psram.address       .eq(reg_mr),
                            psram.register_data .eq(reg_data),
                        ]
                        m.next = state_next

            # Memory read leveling (training to find good readclksel)
            with m.State("TRAIN_INIT"):
                with m.If(psram.idle):
                    m.d.sync += [
                        timeout.eq(0),
                        read_counter.eq(3),
                        psram.start_transfer.eq(1),
                    ]
                    m.next = "TRAIN"
            with m.State("TRAIN"):
                m.d.sync += psram.start_transfer.eq(0),
                m.d.sync += timeout.eq(timeout + 1)
                m.d.comb += psram.final_word.eq(read_counter == 1)
                with m.If(psram.read_ready):
                    m.d.sync += read_counter.eq(read_counter - 1)
                with m.If(timeout == 127):
                    m.next = "WAIT1"
                    m.d.sync += counter.eq(counter + 1)
                    with m.If(counter == 127):
                        m.next = "IDLE"
                    with m.If(~psram.phy.burstdet):
                        m.d.sync += readclksel.eq(readclksel + 1)
                        m.d.sync += counter.eq(0)
            with m.State("WAIT1"):
                m.next = "TRAIN_INIT"

            # Training complete, now we can accept transactions.
            with m.State('IDLE'):
                with m.If(self.shared_bus.cyc & self.shared_bus.stb & psram.idle):
                    m.d.sync += [
                        psram.start_transfer          .eq(1),
                        psram.write_data              .eq(self.shared_bus.dat_w),
                        psram.write_mask              .eq(~self.shared_bus.sel),
                        psram.address                 .eq(self.shared_bus.adr << 2),
                        psram.perform_write           .eq(self.shared_bus.we),
                    ]
                    m.next = 'GO'
            with m.State('GO'):
                with m.If(self.shared_bus.cti != wishbone.CycleType.INCR_BURST):
                    m.d.comb += psram.final_word      .eq(1)
                with m.If(psram.read_ready | psram.write_ready):
                    m.d.comb += [
                        self.shared_bus.dat_r         .eq(psram.read_data),
                        self.shared_bus.ack           .eq(1),
                    ]
                    m.d.sync += [
                        psram.write_data              .eq(self.shared_bus.dat_w),
                        psram.write_mask              .eq(~self.shared_bus.sel),
                    ]
                    with m.If(self.shared_bus.cti != wishbone.CycleType.INCR_BURST):
                        m.d.comb += psram.final_word  .eq(1)
                        m.next = 'IDLE'
                # FIXME: odd case --
                # We have a page crossing during final word assertion, so psram doesn't
                # pick it up, so we have to keep final_word asserted until psram is idle.
                with m.If(~self.shared_bus.cyc & ~self.shared_bus.stb):
                    m.d.comb += psram.final_word.eq(1)
                    m.next = 'ABORT'
            with m.State('ABORT'):
                m.d.comb += psram.final_word.eq(1)
                with m.If(psram.idle):
                    m.next = 'IDLE'

        # Logic for tracking PSRAM bandwidth consumption.

        stats_collect = Signal()

        with m.If(stats_collect):
            m.d.sync += self._stats0.f.cycles_elapsed.r_data.eq(self._stats0.f.cycles_elapsed.r_data+1)
            with m.If(psram.idle):
                m.d.sync += self._stats1.f.cycles_idle.r_data.eq(self._stats1.f.cycles_idle.r_data+1)
            with m.If(psram.read_ready):
                m.d.sync += self._stats2.f.cycles_ack_r.r_data.eq(self._stats2.f.cycles_ack_r.r_data+1)
            with m.If(psram.write_ready):
                m.d.sync += self._stats3.f.cycles_ack_w.r_data.eq(self._stats3.f.cycles_ack_w.r_data+1)

        with m.If(self._ctrl.f.collect.w_stb):
            m.d.sync += stats_collect.eq(self._ctrl.f.collect.w_data)
            # Reset stats whenever collect is strobed with 1
            with m.If(self._ctrl.f.collect.w_data):
                m.d.sync += [
                    self._stats0.f.cycles_elapsed.r_data.eq(0),
                    self._stats1.f.cycles_idle.r_data.eq(0),
                    self._stats2.f.cycles_ack_r.r_data.eq(0),
                    self._stats3.f.cycles_ack_w.r_data.eq(0),
                ]


        return m
