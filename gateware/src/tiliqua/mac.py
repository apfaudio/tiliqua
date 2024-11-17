# Copyright (c) 2024 S. Holzapfel, apfelaudio UG <info@apfelaudio.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""
Some utilities for resource-efficient MAC (multiply, accumulate)
operations. This file provides mechanisms for sharing DSP tiles
amongst multiple components using 2 different strategies:

    1) :py:`MuxMAC`: One DSP tile is Mux'd in time. Latency relatively
       low, however sharing >3x MACs quickly blows up resource usage.

    2) :py:`RingMAC`: Message ring sharing. Multiple components (and
       MACs) are connected in a message ring (essentially a large
       circular shift register). On each ring, there is a single
       DSP tile processing MAC requests. DSP tile throughput of
       near 100% is still achievable, however latency is higher.

For audio rate signals, where sample rates are low and the desired
amount of separate functional blocks is high, sharing DSP tiles is
essential. Without sharing DSP tiles, multipliers are often the first
FPGA resource (by far) to be exhausted.

MAC Message Ring
----------------

Each node on the message ring nominally shifts its input message
to its output. Each node is connected in a circular shift register,
with N 'clients' (may ask MAC questions) and 1 'server' (may have
a single DSP tile and respond to MAC questions). A client may
only send a message if there is an INVALID message being shifted
into it. This keeps latency bounded and removes the need for
extra storage. A server may 'convert' a MAC question into a MAC
answer by shifting in the question and shifting out the answer.
Each message is tagged by the generator of the MAC question, so
clients can identify and consume their own MAC answers.

Assuming all N participants ask for a MAC computation on the same
clock, the result will arrive at all participants N+1 clocks later,
with the 'server' DSP tile busy for N out of N+1 of those clocks.
"""

from amaranth              import *
from amaranth.lib          import wiring, data, stream, enum
from amaranth.lib.wiring   import In, Out

from tiliqua.eurorack_pmod import ASQ
from amaranth_future       import fixed

# Native 18-bit multiplier type.
SQNative = fixed.SQ(2, ASQ.f_width)

class MAC(wiring.Component):

    """
    Base class for MAC strategies.
    Subclasses provide the concrete strategy.

    Subclasses use this through :py:`mac.Multiply(m, ...)`
    """

    a: In(SQNative)
    b: In(SQNative)
    z: Out(SQNative)

    # Assert strobe when a, b are valid. Keep a, b
    # valid and strobe asserted until `valid` is strobed,
    # at which point z can be considered valid.
    strobe: Out(1)
    valid: Out(1)

    def Multiply(self, m, a, b):
        """
        Contents of an FSM state, computing `z = a*b`.
        Ensure a, b will NOT change until the operation completes.

        Returns a context object which may be used to perform more
        actions in the same clock the MAC is complete.
        """
        m.d.comb += [
            self.a.eq(a),
            self.b.eq(b),
            self.strobe.eq(1),
        ]
        return m.If(self.valid)

    def default():
        """Default MAC provider for DSP components if None is specified."""
        return MuxMAC()

class MuxMAC(MAC):

    """
    A Multiplexing MAC provider.

    Instantiates a single multiplier, shared between users of this
    MuxMAC effectively using a Mux.
    """

    def elaborate(self, platform):
        m = Module()
        m.d.comb += [
            self.z.eq(self.a * self.b),
            self.valid.eq(1),
        ]
        return m

class RingMessage(data.Struct):

    """
    Layout of a single message on a message ring.
    This message may be populated by a client or
    a server.
    """

    TAG_BITS = 4

    class Kind(enum.Enum, shape=unsigned(1)):
        INVALID     = 0
        MUL         = 1

    class Source(enum.Enum, shape=unsigned(1)):
        CLIENT     = 0
        SERVER     = 1

    class MulClientPayload(data.Struct):
        """A MAC computation request."""
        a: SQNative
        b: SQNative

    class MulServerPayload(data.Struct):
        """A MAC computation result."""
        z: SQNative

    source  : Source
    kind    : Kind
    tag     : unsigned(TAG_BITS) # TODO parameterize in __init__
    payload : data.UnionLayout({
        "mul_client": MulClientPayload,
        "mul_server": MulServerPayload,
    })

class RingSignature(wiring.Signature):

    """
    Connection of a Client or Server to a message ring.
    Messages shift in on :py:`i` and out on :py:`o`.
    """

    def __init__(self):
        super().__init__({
            "i":  In(RingMessage),
            "o":  Out(RingMessage),
        })

class RingMAC(MAC):

    """
    A message-ring-backed MAC provider.

    Normally these should only be created from an existing server
    using :py:`RingMACServer.new_client()`. This automatically
    hooks up the :py:`ring` and :py:`tag` attributes, but does
    NOT add it as a submodule for elaboration (you must do this).

    The common pattern here is that each functional block tends
    to use a single :py:`RingMAC`, even if it has multiple MAC
    steps. That is, the :py:`RingMAC` itself is Mux'd, however
    all requests land on the same shared bus.

    This provides near-optimal scheduling for message rings composed
    of components that have the same state machines.

    Contains no multiplier, :py:`ring` must be hooked up to a
    message ring on which a :py:`RingMACServer` can be found.
    :py:`tag` MUST uniquely identify the underlying :py:`RingClient`
    instantiated inside this :py:`RingMAC`.
    """

    ring: Out(RingSignature())
    tag:  In(RingMessage.TAG_BITS)

    def elaborate(self, platform):
        m = Module()

        m.submodules.ring_client = ring_client = RingClient()
        wiring.connect(m, wiring.flipped(self.ring), ring_client.ring)

        m.d.comb += [
            ring_client.tag.eq(self.tag),
            ring_client.i.a.eq(self.a),
            ring_client.i.b.eq(self.b),
            ring_client.strobe.eq(self.strobe),
            self.z.eq(ring_client.o.z),
            self.valid.eq(ring_client.valid),
        ]

        return m

class RingClient(wiring.Component):

    """
    Message ring client participant.

    :py:`ring` should connect to the ring bus.

    To issue a request, :py:`i` and :py:`tag` should be set,
    and :py:`strobe` asserted, until :py:`valid` is asserted. On
    the same clock that :py:`valid` is asserted, :py:`o` contains
    the answer from the server to our request.

    Under the hood, :py:`RingClient` will take care of not
    sending our request until the bus is free, and not asserting
    :py:`valid` until an appropriate response has arrived.
    """

    ring:   Out(RingSignature())

    i:      In(RingMessage.MulClientPayload)
    o:      Out(RingMessage.MulServerPayload)

    tag:    In(RingMessage.TAG_BITS)
    strobe: In(1)
    valid:  Out(1)

    def elaborate(self, platform):
        m = Module()

        ring = self.ring

        m.d.sync += [
            ring.o.eq(ring.i)
        ]

        wait = Signal()

        # TODO: latch message after strobe until bus free?
        # => not really needed assuming current contract in MAC() baseclass.

        with m.If((ring.i.kind == RingMessage.Kind.INVALID) & self.strobe & ~wait):
            m.d.sync += [
                wait.eq(1),
                ring.o.source.eq(RingMessage.Source.CLIENT),
                ring.o.kind.eq(RingMessage.Kind.MUL),
                ring.o.tag.eq(self.tag),
                ring.o.payload.mul_client.eq(self.i),
            ]

        with m.If((ring.i.kind == RingMessage.Kind.MUL) &
                  (ring.i.source == RingMessage.Source.SERVER) &
                  (ring.i.tag == self.tag) &
                  wait):

            m.d.comb += [
                self.valid.eq(1),
                self.o.eq(ring.i.payload.mul_server),
            ]

            m.d.sync += [
                ring.o.kind.eq(RingMessage.Kind.INVALID),
                wait.eq(0),
            ]

        return m

class RingMACServer(wiring.Component):

    """
    MAC message ring server and connections between clients.

    Prior to elaboration, :py:`new_client()` may be used to
    add additional client nodes to this ring.

    During elaboration, all clients (and this server) are
    connected in a ring, and a single shared DSP tile
    is instantiated to serve requests.
    """

    def __init__(self):
        self.clients = []
        super().__init__({
            "ring": Out(RingSignature())
        })

    def new_client(self):
        self.clients.append(RingMAC())
        assert len(self.clients) <= 2**RingMessage.TAG_BITS
        return self.clients[-1]

    def elaborate(self, platform):
        m = Module()

        ring = self.ring

        m.d.sync += [
            ring.o.eq(ring.i)
        ]

        # Create the ring (TODO better ordering heuristics?)

        m.d.comb += [
            self.clients[0].ring.i.eq(ring.o),
            ring.i.eq(self.clients[-1].ring.o),
        ]
        for n in range(len(self.clients)-1):
            m.d.comb += self.clients[n+1].ring.i.eq(self.clients[n].ring.o)

        # Assign client tag IDs

        for n in range(len(self.clients)):
            m.d.comb += self.clients[n].tag.eq(n)

        # Respond to MAC requests

        with m.If((ring.i.kind == RingMessage.Kind.MUL) &
                  (ring.i.source == RingMessage.Source.CLIENT)):
            m.d.sync += [
                ring.o.source.eq(RingMessage.Source.SERVER),
                ring.o.payload.mul_server.z.eq(
                    ring.i.payload.mul_client.a *
                    ring.i.payload.mul_client.b),
            ]

        return m
