from amaranth import *
from amaranth.lib import wiring, data, stream, memory
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import atan, pi

from tiliqua.fft import CQ

class RectToPolarCordic(wiring.Component):

    # CORDIC gain constant
    K = 1.646760258121

    def __init__(self, shape: fixed.Shape, iterations: int = None):
        self.shape = shape
        self.iterations = iterations or shape.i_bits + shape.f_bits
        self.internal_shape = fixed.SQ(self.shape.i_bits + 2, self.shape.f_bits)
        super().__init__({
            "i": In(stream.Signature(CQ(shape))),
            "o": Out(stream.Signature(data.StructLayout({
                "magnitude": self.internal_shape,
                "phase": self.internal_shape,
            })))
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # Create ROM for arctangent values
        # atan(2^-i) for i in range(iterations)
        atan_values = []
        for i in range(self.iterations):
            angle = atan(1.0 / (1<<i)) / pi
            atan_values.append(angle)
        m.submodules.atan_rom = atan_rom = memory.Memory(
            shape=self.internal_shape, 
            depth=self.iterations, 
            init=atan_values
        )
        atan_rd = atan_rom.read_port(domain='comb')

        # State registers
        x = Signal(self.internal_shape)
        y = Signal(self.internal_shape)
        z = Signal(self.internal_shape)

        # Iteration counter
        iteration = Signal(range(self.iterations + 1))

        # Shifted versions for current iteration
        x_shift = Signal(self.internal_shape)
        y_shift = Signal(self.internal_shape)

        # Direction of rotation (sign of y)
        d = Signal()

        # ROM addressing
        m.d.comb += atan_rd.addr.eq(iteration)

        # Compute shifted values
        m.d.comb += [
            x_shift.eq(x >> iteration),
            y_shift.eq(y >> iteration),
            # Direction based on sign of y (we want to drive y to zero)
            d.eq((x<0) ^ (y<0)),  # y < 0 means rotate clockwise (d=1)
        ]

        # Input handling - convert to internal representation
        in_latch = Signal.like(self.i.payload)

        # Handle input quadrant adjustment
        quadrant = Signal(2)
        x_abs = Signal(self.internal_shape)
        y_abs = Signal(self.internal_shape)

        quadrant_adjust = Signal(self.internal_shape)

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                    m.d.sync += in_latch.eq(self.i.payload)
                    m.next = "QUADRANT"

            with m.State("QUADRANT"):
                m.d.sync += [
                    z.eq(0),
                    iteration.eq(0),
                    quadrant_adjust.eq(0)
                ]
                with m.If((in_latch.real >= 0)):  # Q1, Q4
                    m.d.sync += [
                        x.eq(in_latch.real),
                        y.eq(in_latch.imag),
                    ]
                with m.Else():
                    m.d.sync += [
                        x.eq(-in_latch.real),
                        y.eq(-in_latch.imag),
                    ]
                    with m.If(in_latch.imag >= 0):
                        m.d.sync += quadrant_adjust.eq(fixed.Const(1.0))  # Q2
                    with m.Else():
                        m.d.sync += quadrant_adjust.eq(fixed.Const(-1.0)) # Q3
                m.next = "ITERATE"

            with m.State("ITERATE"):
                with m.If(iteration < self.iterations):
                    with m.If(d):  # y >= 0, rotate clockwise
                        m.d.sync += [
                            x.eq(x - y_shift),
                            y.eq(y + x_shift),
                            z.eq(z - atan_rd.data),
                        ]
                    with m.Else():  # y < 0, rotate counter-clockwise
                        m.d.sync += [
                            x.eq(x + y_shift),
                            y.eq(y - x_shift),
                            z.eq(z + atan_rd.data),
                        ]
                    m.d.sync += iteration.eq(iteration + 1)
                    m.next = "ITERATE"
                with m.Else():
                    m.next = "OUTPUT"

            with m.State("OUTPUT"):
                # Scale magnitude by 1/K to compensate for CORDIC gain
                mag_scaled = Signal(self.internal_shape)
                m.d.comb += mag_scaled.eq(
                    x * fixed.Const(1.0/self.K, self.internal_shape))
                # Apply quadrant adjustment to phase
                phase_adjusted = Signal(self.internal_shape)
                m.d.comb += phase_adjusted.eq(z + quadrant_adjust)
                # Output the results
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload.magnitude.eq(mag_scaled),
                    self.o.payload.phase.eq(phase_adjusted),
                ]
                with m.If(self.o.ready):
                    m.next = "IDLE"

        return m

class SimpleVocoder(wiring.Component):

    def __init__(self,
                 shape: fixed.Shape,
                 sz:    int):

        self.sz        = sz
        self.shape     = shape

        super().__init__({
            # All frequency domain spectra in blocks.
            "i_carrier": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
            "i_modulator": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
            "o": Out(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        """
        mag = Signal(self.shape)
        m.d.comb += [
            # TODO frame synchronization
            self.i_carrier.ready.eq(self.o.ready),
            self.i_modulator.ready.eq(self.o.ready),
            self.o.valid.eq(self.i_carrier.valid),
            self.o.payload.first.eq(self.i_carrier.payload.first),
            # TODO real magnitude calculation
            mag.eq(
                (self.i_carrier.payload.sample.real*self.i_carrier.payload.sample.real +
                 self.i_carrier.payload.sample.imag*self.i_carrier.payload.sample.imag)>>1
            ),
            # TODO normalize modulator vector
            self.o.payload.sample.real.eq(mag * self.i_modulator.payload.sample.real),
            self.o.payload.sample.imag.eq(mag * self.i_modulator.payload.sample.imag),
        ]
        """
        m.submodules.cordic = cordic = RectToPolarCordic(self.shape)
        l_carrier   = Signal.like(self.i_carrier.payload.sample)
        l_modulator = Signal.like(self.i_modulator.payload.sample)
        l_first     = Signal()
        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += [
                    self.i_carrier.ready.eq(1),
                    self.i_modulator.ready.eq(1),
                ]
                with m.If(self.i_carrier.valid & self.i_modulator.valid):
                    m.d.sync += [
                        l_carrier.eq(self.i_carrier.payload.sample),
                        l_modulator.eq(self.i_modulator.payload.sample),
                        l_first.eq(self.i_carrier.payload.first),
                    ]
                    m.next = "CORDIC"

            with m.State("CORDIC"):
                m.d.comb += [
                    cordic.i.valid.eq(1),
                    cordic.i.payload.eq(l_modulator),
                    cordic.o.ready.eq(1),
                ]
                with m.If(cordic.o.valid):
                    m.d.sync += [
                        self.o.payload.sample.real.eq(
                            l_carrier.real * cordic.o.payload.magnitude),
                        self.o.payload.sample.imag.eq(
                            l_carrier.imag * cordic.o.payload.magnitude),
                    ]
                    m.next = "OUTPUT"

            with m.State("OUTPUT"):
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload.first.eq(l_first),
                ]
                with m.If(self.o.ready):
                    m.next = "IDLE"
        return m
