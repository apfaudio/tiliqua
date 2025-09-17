# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Utilities for splitting, merging, remapping streams."""

from amaranth import *
from amaranth.lib import data, stream, wiring, fifo
from amaranth.lib.wiring import In, Out

from . import ASQ


class Split(wiring.Component):

    """
    Consumes payloads from a single stream and splits it into multiple independent streams.
    This component may be instantiated in 2 modes depending on the value of :py:`replicate`:

    - **Channel splitter** (:py:`replicate == False`):
        The incoming stream has an :py:`data.ArrayLayout` signature. Each payload in the
        :py:`data.ArrayLayout` becomes an independent outgoing stream. :py:`n_channels`
        must match the number of payloads in the :py:`data.ArrayLayout`.

    - **Channel replicater** (:py:`replicate == True`):
        The incoming stream has a single payload. Each payload in the incoming stream
        is replicated and at the output appears as :py:`n_channels` independent streams,
        which produce the same values, however may be synchronized/consumed independently.

    This class is inspired by previous work in the lambdalib and LiteX projects.
    """

    def __init__(self, n_channels, replicate=False, source=None, shape=ASQ):
        """
        n_channels : int
            The number of independent output streams. See usage above.
        replicate : bool, optional
            See usage above.
        source : stream, optional
            Optional incoming stream to pass through to :py:`wiring.connect` on
            elaboration. This argument means you do not have to hook up :py:`self.i`
            and can make some pipelines a little easier to read.
        """
        self.n_channels   = n_channels
        self.replicate    = replicate
        self.source       = source
        self.shape        = shape

        if self.replicate:
            super().__init__({
                "i": In(stream.Signature(shape)),
                "o": Out(stream.Signature(shape)).array(n_channels),
            })
        else:
            super().__init__({
                "i": In(stream.Signature(data.ArrayLayout(shape, n_channels))),
                "o": Out(stream.Signature(shape)).array(n_channels),
            })

    def elaborate(self, platform):
        m = Module()

        done = Signal(self.n_channels)

        m.d.comb += self.i.ready.eq(Cat([self.o[n].ready | done[n] for n in range(self.n_channels)]).all())
        m.d.comb += [self.o[n].valid.eq(self.i.valid & ~done[n]) for n in range(self.n_channels)]

        if self.replicate:
            m.d.comb += [self.o[n].payload.eq(self.i.payload) for n in range(self.n_channels)]
        else:
            m.d.comb += [self.o[n].payload.eq(self.i.payload[n]) for n in range(self.n_channels)]

        flow = [self.o[n].valid & self.o[n].ready
                for n in range(self.n_channels)]
        end  = Cat([flow[n] | done[n]
                    for n in range(self.n_channels)]).all()
        with m.If(end):
            m.d.sync += done.eq(0)
        with m.Else():
            for n in range(self.n_channels):
                with m.If(flow[n]):
                    m.d.sync += done[n].eq(1)

        if self.source is not None:
            wiring.connect(m, self.source, self.i)

        return m

    def wire_ready(self, m, channels):
        """Set out channels as permanently READY so they don't block progress."""
        for n in channels:
            wiring.connect(m, self.o[n],
                           stream.Signature(self.shape, always_ready=True).flip().create())


class Merge(wiring.Component):

    """
    Consumes payloads from multiple independent streams and merges them into a single stream.

    This class is inspired by previous work in the lambdalib and LiteX projects.
    """

    def __init__(self, n_channels, sink=None, shape=ASQ):
        """
        n_channels : int
            The number of independent incoming streams.
        sink : stream, optional
            Optional outgoing stream to pass through to :py:`wiring.connect` on
            elaboration. This argument means you do not have to hook up :py:`self.o`
            and can make some pipelines a little easier to read.
        """
        self.n_channels = n_channels
        self.sink       = sink
        self.shape      = shape
        super().__init__({
            "i": In(stream.Signature(shape)).array(n_channels),
            "o": Out(stream.Signature(data.ArrayLayout(shape, n_channels))),
        })

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [self.i[n].ready.eq(self.o.ready & self.o.valid) for n in range(self.n_channels)]
        m.d.comb += [self.o.payload[n].eq(self.i[n].payload) for n in range(self.n_channels)]
        m.d.comb += self.o.valid.eq(Cat([self.i[n].valid for n in range(self.n_channels)]).all())

        if self.sink is not None:
            wiring.connect(m, self.o, self.sink)

        return m

    def wire_valid(self, m, channels):
        """Set in channels as permanently VALID so they don't block progress."""
        for n in channels:
            wiring.connect(m, stream.Signature(self.shape, always_valid=True).create(),
                           self.i[n])

class Arbiter(wiring.Component):
    """
    Round-robin arbiter for multiple streams.
    """
    def __init__(self, n_channels: int, shape):
        self.n_channels = n_channels
        super().__init__({
            "i": In(stream.Signature(shape)).array(n_channels),
            "o": Out(stream.Signature(shape)),
        })
    def elaborate(self, platform) -> Module:
        m = Module()
        grant = Signal(range(self.n_channels))
        # Connect granted stream directly
        with m.Switch(grant):
            for n in range(self.n_channels):
                with m.Case(n):
                    wiring.connect(m, wiring.flipped(self.i[n]), wiring.flipped(self.o))
        # Permit switching on the end of a transaction, or if there is no pending
        # valid (we are not allowed to deassert valid, but we may deassert ready)
        transaction_complete = self.o.valid & self.o.ready
        with m.If(transaction_complete | ~self.o.valid):
            with m.If(grant == (self.n_channels - 1)):
                m.d.sync += grant.eq(0)
            with m.Else():
                m.d.sync += grant.eq(grant + 1)
        return m

class SyncFIFOBuffered(wiring.Component):
    '''Stream-friendly wrapper around [amaranth.lib.fifo.SyncFIFOBuffered][].

    Unlike the other cores around here, this one is lifted from:

    URL: https://github.com/zyp/katsuo-stream
    License: MIT
    Author: Vegard Storheil Eriksen <zyp@jvnv.net>

    Args:
        shape: Shape of the stream.
        depth: Depth of the FIFO.

    Attributes:
        input (stream): Input stream.
        output (stream): Output stream.
    '''

    def __init__(self, *, shape, depth: int):
        super().__init__({
            'i': wiring.In(stream.Signature(shape)),
            'o': wiring.Out(stream.Signature(shape)),
        })
        self.shape = shape
        self.depth = depth
        self.fifo = fifo.SyncFIFOBuffered(width = Shape.cast(self.shape).width, depth = self.depth)

    def elaborate(self, platform):
        m = Module()
        m.submodules.fifo = self.fifo

        m.d.comb += [
            # Input
            self.i.ready.eq(self.fifo.w_rdy),
            self.fifo.w_en.eq(self.i.valid),
            self.fifo.w_data.eq(self.i.payload),

            # Output
            self.o.valid.eq(self.fifo.r_rdy),
            self.o.payload.eq(self.fifo.r_data),
            self.fifo.r_en.eq(self.o.ready),
        ]

        return m

def connect_remap(m, stream_o, stream_i, mapping):
    """
    Connect 2 streams, bypassing normal wiring.connect() checks
    that the signatures match. This allows easily remapping fields when
    you are trying to connect streams with different signatures.

    For example, say I have a stream with an ArrayLayout payload and want to
    map it to a different stream with a StructLayout payload, and the underlying
    bit-representation of both layouts do not match, I can remap using:

    .. code-block:: python

        dsp.connect_remap(m, vca_merge2a.o, vca0.i, lambda o, i : [
            i.payload.x   .eq(o.payload[0]),
            i.payload.gain.eq(o.payload[1] << 2)
        ])

    This is a bit of a hack. TODO perhaps implement this as a StreamConverter
    such that we can still use wiring.connect?.
    """

    m.d.comb += mapping(stream_o, stream_i) + [
        stream_i.valid.eq(stream_o.valid),
        stream_o.ready.eq(stream_i.ready)
    ]


def channel_remap(m, stream_o, stream_i, mapping_o_to_i):
    """
    Connect 2 streams of type :py:`data.ArrayLayout`, with different channel
    counts or channel indices. For example, to connect a source with 4 channels
    to a sink with 2 channels, mapping 0 to 0, 1 to 1, leaving 2 and 3 unconnected:

    .. code-block:: python

        s1 = stream.Signature(data.ArrayLayout(ASQ, 4)).create()
        s2 = stream.Signature(data.ArrayLayout(ASQ, 2)).create()
        dsp.channel_remap(m, s1, s2, {0: 0, 1: 1})

    This also works the other way around, to connect e.g. a source with 2 channels to
    a sink with 4 channels. The stream will make progress however the value of the
    payloads in any unmapped output channels is undefined.
    """
    def remap(o, i):
        connections = []
        for k in mapping_o_to_i:
            connections.append(i.payload[mapping_o_to_i[k]].eq(o.payload[k]))
        return connections
    return connect_remap(m, stream_o, stream_i, remap)


class KickFeedback(Elaboratable):
    """
    Inject a single dummy (garbage) sample after reset between
    two streams. This is necessary to break infinite blocking
    after reset if streams are set up in a feedback loop.
    """
    def __init__(self, o, i):
        self.o = o
        self.i = i
    def elaborate(self, platform):
        m = Module()
        wiring.connect(m, self.o, self.i)
        with m.FSM() as fsm:
            with m.State('KICK'):
                m.d.comb += self.i.valid.eq(1)
                with m.If(self.i.ready):
                    m.next = 'FORWARD'
            with m.State('FORWARD'):
                pass
        return m


def connect_feedback_kick(m, o, i):
    m.submodules += KickFeedback(o, i)


def connect_peek(m, stream_peek, stream_dst, always_ready=False):
    """
    Nonblocking 'peek', used to tap off an EXISTING stream connection, without
    influencing it, for inspection / plotting purposes.
    """
    m.d.comb += [
        stream_dst.valid.eq(stream_peek.valid & stream_peek.ready),
        stream_dst.payload.eq(stream_peek.payload),
        stream_peek.ready.eq(1) if always_ready else []
    ]
