from amaranth import *
from amaranth.lib import wiring, data, stream, memory
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import atan, pi

from tiliqua.fft import CQ
from tiliqua import dsp

class RectToPolarCordic(wiring.Component):

    # CORDIC gain constant
    K = 1.646760258121

    def __init__(self, shape: fixed.Shape, iterations: int = None,
                 magnitude_correction=True):
        self.shape = shape
        self.iterations = iterations or shape.i_bits + shape.f_bits
        self.internal_shape = fixed.SQ(self.shape.i_bits + 2, self.shape.f_bits)
        self.magnitude_correction = magnitude_correction
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

        # Output assignments
        m.d.comb += self.o.payload.phase.eq(z + quadrant_adjust),
        if self.magnitude_correction:
            # Scale magnitude by 1/K to compensate for CORDIC gain
            m.d.comb += self.o.payload.magnitude.eq(
                x * fixed.Const(1.0/self.K, self.internal_shape))
        else:
            m.d.comb += self.o.payload.magnitude.eq(x)

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
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.next = "IDLE"

        return m

class SpectralEnvelope(wiring.Component):

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int):
        self.shape = shape
        self.sz    = sz
        super().__init__({
            "i": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
            "o": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": self.shape
            }))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.cordic = cordic = RectToPolarCordic(
                self.shape, magnitude_correction=False)

        cordic_mag = Signal(cordic.internal_shape)

        idx = Signal(range(self.sz+1))

        m.submodules.mem = mem = memory.Memory(shape=cordic.internal_shape, depth=self.sz, init=[])
        mem_rd = mem.read_port()
        mem_wr = mem.write_port()

        beta = 0.7
        a = fixed.Const(beta, shape=cordic.internal_shape)
        b = fixed.Const(1-beta, shape=cordic.internal_shape)

        m.d.comb += [
            mem_rd.addr.eq(idx),
            mem_rd.en.eq(1),
            mem_wr.addr.eq(idx),
            mem_wr.data.eq(mem_rd.data*a + cordic_mag*b)
        ]

        m.d.sync += mem_wr.en.eq(0)

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                    m.d.sync += cordic.i.payload.real.eq(self.i.payload.sample.real)
                    m.d.sync += cordic.i.payload.imag.eq(self.i.payload.sample.imag)
                    with m.If(self.i.payload.first):
                        m.d.sync += idx.eq(0)
                    with m.Else():
                        m.d.sync += idx.eq(idx+1)
                    m.next = "CORDIC"

            with m.State("CORDIC"):
                m.d.comb += [
                    cordic.i.valid.eq(1),
                    cordic.o.ready.eq(1),
                ]
                with m.If(cordic.o.valid):
                    m.d.sync += cordic_mag.eq(cordic.o.payload.magnitude)
                    m.next = "UPDATE"

            with m.State("UPDATE"):
                m.d.sync += [
                    mem_wr.en.eq(1),
                    self.o.payload.first.eq(idx == 0),
                    self.o.payload.sample.eq(mem_wr.data),
                ]
                m.next = "OUTPUT"

            with m.State("OUTPUT"):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.next = "IDLE"

        return m

class SimpleVocoder(wiring.Component):

    """
    Consume 2 sets of frequency-domain information representing a
    'carrier' and 'modulator'. The (real) magnitude of the 'modulator'
    spectra is multiplied by the (complex) 'carrier' spectra, creating
    a classic vocoder effect where the timbre of the 'carrier' dominates,
    but is filtered spectrally by the 'modulator'

    This core runs a Rectangular-to-Polar conversion on each 'modulator'
    datapoint, discards the phase and uses the magnitude to compute:

        out.real = carrier.real * modulator.magnitude
        out.imag = carrier.imag * modulator.magnitude

    A single multiplier is shared for this, to reduce resource usage.
    Additionally, the CORDIC is run without magnitude correction, which
    saves another multiplier at the cost of everything being multiplied
    by a constant factor (which makes no difference here).
    """

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int):

        self.shape = shape
        self.sz    = sz

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

        m.submodules.envelope = envelope = SpectralEnvelope(shape=self.shape, sz=self.sz)

        l_carrier   = Signal.like(self.i_carrier.payload.sample)
        l_modulator = Signal.like(self.i_modulator.payload.sample)
        l_first     = Signal()

        m.submodules.merge2 = merge2 = dsp.Merge(
                n_channels=2, shape=self.i_carrier.payload.shape())
        wiring.connect(m, wiring.flipped(self.i_carrier), merge2.i[0])
        wiring.connect(m, wiring.flipped(self.i_modulator), merge2.i[1])

        # Shared multiplier for carrier * mag(modulator) terms
        modulator_a = Signal(self.shape)
        modulator_b = Signal(self.shape)
        modulator_z = Signal(self.shape)
        m.d.comb += modulator_z.eq((modulator_a * modulator_b)<<3)

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += merge2.o.ready.eq(1)
                with m.If(merge2.o.valid):
                    m.d.sync += [
                        l_carrier.eq(merge2.o.payload[0].sample),
                        l_modulator.eq(merge2.o.payload[1].sample),
                        # TODO frame alignment (not needed for STFT cores
                        # with shared reset.)
                        l_first.eq(merge2.o.payload[0].first),
                    ]
                    m.next = "ENVELOPE"

            with m.State("ENVELOPE"):
                m.d.comb += [
                    envelope.i.valid.eq(1),
                    envelope.i.payload.sample.real.eq(l_modulator.real),
                    envelope.i.payload.sample.imag.eq(l_modulator.imag),
                    envelope.i.payload.first.eq(l_first),
                    envelope.o.ready.eq(1),
                ]
                with m.If(envelope.o.valid):
                    m.d.sync += modulator_b.eq(envelope.o.payload.sample)
                    m.next = "REAL"

            with m.State("REAL"):
                m.d.comb += modulator_a.eq(l_carrier.real)
                m.d.sync += self.o.payload.sample.real.eq(modulator_z)
                m.next = "IMAG"

            with m.State("IMAG"):
                m.d.comb += modulator_a.eq(l_carrier.imag)
                m.d.sync += self.o.payload.sample.imag.eq(modulator_z)
                m.next = "OUTPUT"

            with m.State("OUTPUT"):
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload.first.eq(l_first),
                ]
                with m.If(self.o.ready):
                    m.next = "IDLE"

        return m
