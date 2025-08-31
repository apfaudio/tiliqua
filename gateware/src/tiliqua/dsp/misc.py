# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import stream, wiring
from amaranth.lib.wiring import In, Out

from . import ASQ


def named_submodules(m_submodules, elaboratables, override_name=None):
    """
    Normally, using constructs like:

    .. code-block:: python

        m.submodules += delaylines

    You get generated code with names like U$14 ... as Amaranth's
    namer doesn't give such modules a readable name.

    Instead, you can do:

    .. code-block:: python

        named_submodules(m.submodules, delaylines)

    And this helper will give each instance a name.

    TODO: is there an idiomatic way of doing this?
    """
    if override_name is None:
        [setattr(m_submodules, f"{type(e).__name__.lower()}{i}", e) for i, e in enumerate(elaboratables)]
    else:
        [setattr(m_submodules, f"{override_name}{i}", e) for i, e in enumerate(elaboratables)]


class CountingFollower(wiring.Component):
    """
    Simple unsigned counting follower.

    Output follows the input, getting closer to it by 1 count per :py:`valid` strobe.

    This is quite a cheap way to avoid pops on envelopes.
    """

    def __init__(self, bits=8):
        super().__init__({
            "i": In(stream.Signature(unsigned(bits))),
            "o": Out(stream.Signature(unsigned(bits))),
        })

    def elaborate(self, platform):
        m = Module()
        m.d.comb += self.i.ready.eq(self.o.ready)
        m.d.comb += self.o.valid.eq(self.i.valid)
        with m.If(self.i.valid & self.o.ready):
            with m.If(self.o.payload < self.i.payload):
                m.d.sync += self.o.payload.eq(self.o.payload + 1)
            with m.Elif(self.o.payload > self.i.payload):
                m.d.sync += self.o.payload.eq(self.o.payload - 1)
        return m


class Duplicate(wiring.Component):
    """
    Simple 'upsampler' that duplicates each input sample N times.

    No filtering is performed - each input sample is simply repeated N times
    in the output stream.

    Members
    -------
    i : :py:`In(stream.Signature(ASQ))`
        Input stream for samples to be upsampled.
    o : :py:`Out(stream.Signature(ASQ))`
        Output stream producing each input sample N times.
    """

    i: In(stream.Signature(ASQ))
    o: Out(stream.Signature(ASQ))

    def __init__(self, n: int):
        self.n = n
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        if self.n == 1:
            wiring.connect(m, wiring.flipped(self.i), self.o)
        else:
            output_count = Signal(range(self.n + 1), init=0)
            current_sample = Signal(ASQ)
            m.d.comb += self.i.ready.eq(output_count == 0)
            m.d.comb += self.o.valid.eq(output_count > 0)
            m.d.comb += self.o.payload.eq(current_sample)
            with m.If(self.i.valid & self.i.ready):
                m.d.sync += [
                    current_sample.eq(self.i.payload),
                    output_count.eq(self.n),
                ]
            with m.If(self.o.valid & self.o.ready):
                m.d.sync += output_count.eq(output_count - 1)

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
