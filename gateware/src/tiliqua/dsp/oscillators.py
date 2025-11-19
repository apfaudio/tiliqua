# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from . import ASQ, mac


class SawNCO(wiring.Component):
    """
    Sawtooth Numerically Controlled Oscillator.

    Often this can be simply routed into a LUT waveshaper for any other waveform type.

    Members
    -------
    i : :py:`In(stream.Signature(data.StructLayout)`
        Input stream, with fields :py:`freq_inc` (linear frequency) and
        :py:`phase` (phase offset). One output sample is produced for each
        input sample.
    o : :py:`Out(stream.Signature(ASQ))`
        Output stream, values sweep from :py:`ASQ.min()` to :py:`ASQ.max()`.
    """
    i: In(stream.Signature(data.StructLayout({
            "freq_inc": ASQ,
            "phase": ASQ,
        })))
    o: Out(stream.Signature(ASQ))

    def __init__(self, extra_bits=16, shift=6):
        self.extra_bits = extra_bits
        self.shift = shift
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        s = Signal(fixed.SQ(self.extra_bits, ASQ.f_bits))

        out_no_phase_mod = Signal(ASQ)

        m.d.comb += [
            self.o.valid.eq(self.i.valid),
            self.i.ready.eq(self.o.ready),
            out_no_phase_mod.eq(s >> self.shift),
            self.o.payload.eq(
                out_no_phase_mod + self.i.payload.phase),
        ]

        with m.If(self.i.valid & self.o.ready):
            m.d.sync += s.eq(s + self.i.payload.freq_inc),

        return m

class WhiteNoise(wiring.Component):

    """
    Simple white noise generator.

    See: https://www.musicdsp.org/en/latest/Synthesis/216-fast-whitenoise-generator.html

    Members
    -------
    o : :py:`Out(stream.Signature(ASQ))`
        Output stream of white noise.
    """

    o: Out(stream.Signature(ASQ))

    def elaborate(self, platform):
        m = Module()

        x0 = Signal(unsigned(32), init=0x67452301)
        x1 = Signal(unsigned(32), init=0xefcdab89)

        m.d.comb += [
            self.o.payload.as_value().eq(x1>>(ASQ.f_bits+ASQ.i_bits)),
        ]

        with m.FSM() as fsm:
            with m.State('X'):
                m.d.sync += x1.eq(x1+x0)
                m.next = 'OUT'
            with m.State('OUT'):
                m.d.comb += self.o.valid.eq(1),
                with m.If(self.o.ready):
                    m.d.sync += x0.eq(x0^x1)
                    m.next = 'X'

        return m

class DWO(wiring.Component):

    """
    Digital Waveguide Oscillator.

    Emits a fixed frequency and amplitude sine wave, without needing
    a sine LUT. Instead, only uses 2 registers, 1 multiply, 3 adds.

    This is not easy to modulate, but it is an interesting way to
    achieve a high-fidelity sine wave with minimal resources.

    For details, see Fig. 3 from:
        https://ccrma.stanford.edu/~jos/wgo/Second_Order_Waveguide_Filter.html

    Members
    -------
    o : :py:`Out(stream.Signature(ASQ))`
        Output stream of sinusoid samples.
    """

    o: Out(stream.Signature(ASQ))

    def __init__(self, sq=None, macp=None, c=0.99):
        super().__init__()
        self.c = c
        self.sq = sq or self.o.payload.shape()
        self.macp = macp or mac.MAC.default()

    def elaborate(self, platform):
        m = Module()

        sq = self.sq

        m.submodules.macp = mp = self.macp

        # Frequency tuning coefficient: `C = cos(2*pi*f/fs)`.
        C = fixed.Const(self.c, shape=sq)

        # Initial conditions (determines output amplitude)
        x1 = Signal(sq, init=fixed.Const(0.0, shape=sq))
        x2 = Signal(sq, init=fixed.Const(0.5, shape=sq))

        # x2 -> Output
        m.d.comb += self.o.payload.eq(x2),

        with m.FSM() as fsm:
            with m.State('MAC'):
                with mp.Multiply(m, a=(x1+x2), b=C):
                    m.d.sync += [
                        x1.eq(mp.result.z - x2),
                        x2.eq(mp.result.z + x1),
                    ]
                    m.next = 'WAIT-READY'

            with m.State('WAIT-READY'):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.next = 'MAC'

        return m

class Lorenz(wiring.Component):

    """
    Lorenz Attractor.

    Generates a chaotic 3D trajectory based on the Lorenz system of
    differential equations.

    Equations:
        dx/dt = σ * (y - x)
        dy/dt = x * (ρ - z) - y
        dz/dt = x * y - β * z

    Members
    -------
    i : :py:`In(stream.Signature(data.ArrayLayout(ASQ, 3)))`
        Input stream of parameters to tweak sigma / rho / beta.
    o : :py:`Out(stream.Signature(data.ArrayLayout(ASQ, 3)))`
        Output stream of 3D trajectory samples [x, y, z].
        Scaled to fit approximately in the range [-1, +1].
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 3)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 3)))

    def __init__(self, dt=1/256, output_scale=1/64, sigma=10.0, rho=28.0, beta=8.0/3.0, ):
        super().__init__()
        self.dt_log2 = exact_log2(int(1/dt))
        self.scale_log2 = exact_log2(int(1/output_scale))
        self.sigma = sigma
        self.rho = rho
        self.beta = beta

    def elaborate(self, platform):
        m = Module()

        # Type used for internal computations.
        sq = fixed.SQ(9, 9)

        # System parameter defaults
        SIGMA = fixed.Const(self.sigma, shape=sq)
        RHO   = fixed.Const(self.rho, shape=sq)
        BETA  = fixed.Const(self.beta, shape=sq)

        # System parameters after tweaking
        sigma = Signal(shape=sq, init=SIGMA)
        rho   = Signal(shape=sq, init=RHO)
        beta  = Signal(shape=sq, init=BETA)

        m.d.comb += self.i.ready.eq(1)
        with m.If(self.i.valid):
            m.d.sync += [
                sigma.eq(SIGMA + (self.i.payload[0]<<3)),
                rho.eq(RHO + (self.i.payload[1]<<4)),
                beta.eq(BETA + (self.i.payload[2]<<1)),
            ]

        # State variables and initial conditions
        x = Signal(sq, init=fixed.Const(2.0, shape=sq))
        y = Signal(sq, init=fixed.Const(1.0, shape=sq))
        z = Signal(sq, init=fixed.Const(1.0, shape=sq))

        m.submodules.noise = noise = WhiteNoise()

        # Compute derivatives
        dx = sigma * (y - x)
        dy = x * (rho - z) - y
        dz = x * y - beta * z

        with m.If(self.o.ready):
            # Update state based on derivatives only when output is consumed.
            m.d.comb += noise.o.ready.eq(1)
            m.d.sync += [
                x.eq(x + (dx >> self.dt_log2) + (noise.o.payload >> 10)),
                y.eq(y + (dy >> self.dt_log2)- (noise.o.payload >> 9) ),
                z.eq(z + (dz >> self.dt_log2)),
            ]

        # Scale all outputs to fit in [-1, +1]
        m.d.comb += [
            self.o.payload[0].eq(x >> self.scale_log2),
            self.o.payload[1].eq(y >> self.scale_log2),
            # Center at 0 rather than ~+0.45
            self.o.payload[2].eq((z >> self.scale_log2) - fixed.Const(0.45, shape=ASQ)),
            self.o.valid.eq(1),
        ]

        return m
