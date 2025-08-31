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
