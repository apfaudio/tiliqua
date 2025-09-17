from types import SimpleNamespace

from amaranth import *
from amaranth.lib import wiring, enum
from amaranth.lib.wiring import In
from amaranth_soc.wishbone import *

async def classic_rd(ctx, bus, adr, sel=0xf):
    """Issue a single non-pipelined, non-burst, wishbone B4 classic read."""
    ctx.set(bus.cyc, 1)
    ctx.set(bus.stb, 1)
    ctx.set(bus.we, 0)
    ctx.set(bus.adr, adr)
    ctx.set(bus.sel, sel)
    while not ctx.get(bus.ack):
        await ctx.tick()
    dat_r = ctx.get(bus.dat_r)
    await ctx.tick()
    ctx.set(bus.cyc, 0)
    ctx.set(bus.stb, 0)
    await ctx.tick()
    return dat_r

async def classic_wr(ctx, bus, adr, dat_w, sel=0xf):
    """Issue a single non-pipelined, non-burst, wishbone B4 classic write."""
    ctx.set(bus.cyc, 1)
    ctx.set(bus.stb, 1)
    ctx.set(bus.we, 1)
    ctx.set(bus.adr, adr)
    ctx.set(bus.sel, sel)
    ctx.set(bus.dat_w, dat_w)
    while not ctx.get(bus.ack):
        await ctx.tick()
    await ctx.tick()
    ctx.set(bus.cyc, 0)
    ctx.set(bus.stb, 0)
    await ctx.tick()

async def classic_ack(ctx, bus):
    """Wait for a single non-pipelined classic transaction initiation, ack it."""
    await ctx.tick().until(bus.cyc & bus.stb)
    result = {}
    for member in bus.signature.members:
        result[member] = ctx.get(getattr(bus, member))
    await ctx.tick()
    ctx.set(bus.ack, 1)
    await ctx.tick()
    ctx.set(bus.ack, 0)
    return SimpleNamespace(**result)

class BusChecker(Elaboratable):

    """
    Simple snooping component for checking that Wishbone transactions
    on a provided bus are well-behaved. It can also print every transaction
    on the bus, which can be useful for quick debugging.

    As it uses Assert statements, these can be checked both in pysim and by verilator.
    At the moment, B4 Pipelined mode is not supported. Only B3 classic and burst.

    TODO: clean this up a bit! It works, but I suspect the logic can be simplified.
    """

    class _CType(enum.Enum, shape=unsigned(3)):
        # Workaround for https://github.com/amaranth-lang/amaranth/issues/1534
        # This should only be used for printing as Format works with it.
        CLASSIC      = 0b000
        CONST_BURST  = 0b001
        INCR_BURST   = 0b010
        END_OF_BURST = 0b111

    def __init__(self, bus, prefix=None):
        sig = bus.signature
        self.has_cti_bte = Feature.CTI in sig.features and Feature.BTE in sig.features
        assert not Feature.STALL in sig.features, "Pipelined Wishbone B4 not supported yet."
        self.bus = bus
        self.prefix = prefix if prefix else ''
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        bus = self.bus

        # CTI fallback only used for printing
        cti_signal = Signal(self._CType)
        prev_cti_signal = Signal.like(cti_signal)
        m.d.comb += cti_signal.eq(getattr(bus, 'cti', Const(CycleType.CLASSIC)))
        m.d.sync += prev_cti_signal.eq(cti_signal)

        # Previous cycle values for stability checking
        prev_cyc = Signal()
        prev_stb = Signal()
        prev_we = Signal()
        prev_adr = Signal.like(bus.adr)
        prev_dat_w = Signal.like(bus.dat_w)
        prev_sel = Signal.like(bus.sel)

        # Burst mode tracking signals (if CTI/BTE present)
        if self.has_cti_bte:
            in_burst = Signal()
            prev_cti = Signal.like(bus.cti)
            burst_count = Signal(8)  # Track transfers in current burst
            m.d.sync += prev_cti.eq(bus.cti)

            prev_bte = Signal(2)
            expected_burst_length = Signal(8)
            m.d.sync += prev_bte.eq(bus.bte)

        m.d.sync += [
            prev_cyc.eq(bus.cyc),
            prev_stb.eq(bus.stb),
            prev_we.eq(bus.we),
            prev_adr.eq(bus.adr),
            prev_dat_w.eq(bus.dat_w),
            prev_sel.eq(bus.sel),
        ]

        #
        # BASIC ASSERTIONS
        #

        # Rule: STB can only be high when CYC is high
        m.d.sync += Assert(~bus.stb | bus.cyc)

        # Rule: Only one termination signal can be asserted at a time
        err_signal = getattr(bus, 'err', Const(0))
        rty_signal = getattr(bus, 'rty', Const(0))
        termination_count = bus.ack + err_signal + rty_signal
        m.d.sync += Assert(termination_count <= 1)

        # Rule: No spurious termination signals when no request is outstanding
        with m.If(~bus.cyc):
            m.d.sync += Assert(termination_count == 0)

        #
        # STABILITY ASSERTIONS
        #

        # During an active transfer, critical signals must remain stable
        active_transfer = prev_cyc & prev_stb & bus.cyc & bus.stb

        with m.If(active_transfer & (termination_count == 0)):
            # TODO: double-check this is fine on all classic transactions??
            # so far only tested with burst and basic (single cycle) classic
            m.d.sync += [
                Assert(bus.we == prev_we),
                Assert(bus.adr == prev_adr),
                Assert(bus.sel == prev_sel),
            ]
            # Write data must be stable during write operations
            with m.If(bus.we):
                m.d.sync += Assert(bus.dat_w == prev_dat_w)

        #
        # OUTSTANDING REQUEST / ACK TRACKING
        #

        # Track outstanding requests
        new_request = bus.cyc & bus.stb & ~(prev_cyc & prev_stb)
        completed_request = (bus.ack | err_signal | rty_signal)
        prev_completed_request = Signal()
        m.d.sync += prev_completed_request.eq(completed_request)

        # Check: For write operations, at least one select bit must be set
        with m.If(bus.cyc & bus.stb & bus.we):
            m.d.sync += Assert(bus.sel != 0)

        # Track bus request to ack stall_cnt (for printing only)
        stall_cnt = Signal(unsigned(32))
        with m.If(bus.cyc & bus.stb & ~completed_request):
            m.d.sync += stall_cnt.eq(stall_cnt + 1)
        with m.Else():
            m.d.sync += stall_cnt.eq(0)

        #
        # CLASSIC / BURST MODE ASSERTIONS (CTI+BTE used)
        #

        if self.has_cti_bte:
            # CTI/BTE: Burst state tracking
            burst_start = bus.cyc & bus.stb & (bus.cti != CycleType.CLASSIC) & ~in_burst
            burst_continue = bus.cyc & bus.stb & in_burst & (bus.cti != CycleType.END_OF_BURST)
            burst_end = (bus.cti == CycleType.END_OF_BURST) | ~bus.cyc
            with m.If(burst_start):
                m.d.sync += [
                    in_burst.eq(1),
                    burst_count.eq(0)
                ]
            with m.Elif(burst_continue & completed_request):
                m.d.sync += burst_count.eq(burst_count + 1)
            with m.Elif(burst_end):
                m.d.sync += [
                    in_burst.eq(0),
                    burst_count.eq(0)
                ]
            # CTI/BTE: Validation rules
            # Check: CTI/BTE must be stable between all transactions
            with m.If(active_transfer & ~completed_request):
                m.d.sync += Assert(bus.cti == prev_cti)
                m.d.sync += Assert(bus.bte == prev_bte)
            # Check: CTI is a valid value (cti has 7 bits but only 4 values legal)
            valid_cti = ((bus.cti == CycleType.CLASSIC) |
                         (bus.cti == CycleType.CONST_BURST) |
                         (bus.cti == CycleType.INCR_BURST) |
                         (bus.cti == CycleType.END_OF_BURST))
            with m.If(bus.cyc & bus.stb):
                m.d.sync += Assert(valid_cti)
            # Check: address increments after ACK for INCR_BURST
            with m.If(bus.cyc & bus.stb & (bus.cti == CycleType.INCR_BURST) & prev_cyc & prev_stb & prev_completed_request):
                m.d.sync += Assert(bus.adr == (prev_adr + 1))

        # Print: on every transaction completion
        # TODO: make this optional?
        with m.If(completed_request):
            with m.If(~bus.we):
                m.d.sync += Print(Format(self.prefix+"adr=0x{adr:08x} dat_r=0x{data:08x} Δt={stall_cnt:02} {cti}",
                                         data=bus.dat_r, adr=bus.adr, cti=cti_signal, stall_cnt=stall_cnt))
            with m.Else():
                m.d.sync += Print(Format(self.prefix+"adr=0x{adr:08x} dat_w=0x{data:08x} Δt={stall_cnt:02} {cti}",
                                         data=bus.dat_w, adr=bus.adr, cti=cti_signal, stall_cnt=stall_cnt))

        return m
