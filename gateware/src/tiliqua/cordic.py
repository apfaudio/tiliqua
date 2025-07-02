from amaranth import *
from amaranth.lib import wiring, data, stream, memory
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import atan, pi

from tiliqua.fft import CQ

class MagPhaseCordic(wiring.Component):

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
        atan_rd = atan_rom.read_port()

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
        x_in = Signal(self.internal_shape)
        y_in = Signal(self.internal_shape)

        # Handle input quadrant adjustment
        quadrant = Signal(2)
        x_abs = Signal(self.internal_shape)
        y_abs = Signal(self.internal_shape)

        quadrant_adjust = Signal(self.internal_shape)

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                    # Vectoring mode: rotate the input vector to the positive x-axis
                    # We need to handle the quadrants correctly
                    x_in = self.i.payload.real
                    y_in = self.i.payload.imag
                    # Quadrant detection and rotation to Q1/Q4
                    with m.If((x_in >= 0) & (y_in >= 0)):  # Q1
                        m.d.sync += [
                            x.eq(x_in),
                            y.eq(y_in),
                            quadrant_adjust.eq(0),
                        ]
                    with m.Elif((x_in < 0) & (y_in >= 0)):  # Q2
                        m.d.sync += [
                            x.eq(-x_in),
                            y.eq(-y_in),
                            quadrant_adjust.eq(fixed.Const(1.0, self.internal_shape).as_value()),  # π
                        ]
                    with m.Elif((x_in < 0) & (y_in < 0)):  # Q3
                        m.d.sync += [
                            x.eq(-x_in),
                            y.eq(-y_in),
                            quadrant_adjust.eq(fixed.Const(-1.0, self.internal_shape).as_value()),  # -π
                        ]
                    with m.Else():  # Q4: x >= 0, y < 0
                        m.d.sync += [
                            x.eq(x_in),
                            y.eq(y_in),
                            quadrant_adjust.eq(0),
                        ]
                    m.d.sync += [
                        z.eq(0),
                        iteration.eq(0),
                    ]
                    m.next = "ITERATE"

            with m.State("WAIT"):
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
                    m.next = "WAIT"
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
