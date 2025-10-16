# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.wiring import In, Out

from amaranth_future import fixed

from . import ASQ


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
    https://www.musicdsp.org/en/latest/Synthesis/216-fast-whitenoise-generator.html
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
    """

    o: Out(stream.Signature(ASQ))

    def __init__(self, sq=None):
        super().__init__()
        self.sq = sq or self.o.payload.shape()

    def elaborate(self, platform):
        m = Module()

        sq = self.sq

        # Frequency tuning coefficient (-1 to +1)
        C = fixed.Const(0.99, shape=sq)

        # Initial conditions (determines sine amplitude)
        sg1 = Signal(sq, init=fixed.Const(0.5, shape=sq))
        o1 = Signal(sq, init=fixed.Const(0.0, shape=sq))

        o = Signal(sq)
        sg = Signal(sq)
        with m.If(self.o.ready):
            m.d.sync += [
                o1.eq(o),
                sg1.eq(sg),
            ]

        oc = Signal(sq)
        m.d.comb += [
            oc.eq((o1+sg1)*C),
            sg.eq(oc+o1),
            o.eq(oc-sg1),
            self.o.payload.eq(sg1),
            self.o.valid.eq(1),
        ]

        return m
