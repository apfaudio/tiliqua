# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""
'Message Ring' Network-on-Chip (NoC) implementation.

Components for connecting N 'clients' and 1 'server' in a circular shift
register topology. This enables efficient resource sharing (e.g., DSP tiles)
across many components without needing huge muxes. For example:

    .. code-block:: text

          tag=0      tag=1      tag=2      tag=3
        ┌───────┐  ┌───────┐  ┌───────┐  ┌───────┐
        │client0┼──►client1┼──►client2┼──►client3│
        └───▲───┘  └───────┘  └───────┘  └───┬───┘
            │                                │
            │            ┌──────┐            │
            └────────────┼server│◄───────────┘
                         └──────┘

On the message ring, messages are shifted in a large circular shift register
by one node every clock. Each message is of layout ``Config.msg_layout``.

A client may only send a message if there is an INVALID message being shifted
into it. This keeps latency bounded and removes the need for extra storage.
A server may 'respond' to a client message by shifting in the payload and
shifting out the response. Each message contains a unique ``tag`` per client,
so servers know where a request came from, and clients know if an incoming
message is destined for it.

Assuming all N clients send a request message in the same clock, and the
server processes one request per clock, the result will arrive at all clients
N+1 clocks later, with the server busy for N out of N+1 of those clocks.

To use this, you will want to create your components building on ``ringnoc.Client``
and ``ringnoc.Server``. An example of this (sharing DSP tiles) is found in
this repository as ``mac.RingMAC`` (client) and ``mac.RingMACServer``.
"""

from dataclasses import dataclass

from amaranth import *
from amaranth.lib import data, enum, wiring
from amaranth.lib.wiring import In, Out

class MessageKind(enum.Enum, shape=unsigned(1)):
    # This message may be ignored.
    INVALID     = 0
    # This message must be forwarded (by clients)
    # or processed (by the server)
    VALID       = 1

class MessageSource(enum.Enum, shape=unsigned(1)):
    # This message came from a Client.
    CLIENT     = 0
    # This message is the Server responding to a Client
    SERVER     = 1

@dataclass
class Config:
    """
    Configuration (message layout) of a message ring.
    """
    # Number of bits in unique message tag. Affects the maximum
    # number of clients on the ring.
    tag_bits: int
    # Data in a client message (shifted out by clients)
    payload_type_client: data.StructLayout
    # Data in a server message (shifted out by the server)
    payload_type_server: data.StructLayout

    @property
    def max_clients(self):
        return 1 << self.tag_bits

    @property
    def msg_layout(self):
        return data.StructLayout({
            "source"  : MessageSource,
            "kind"    : MessageKind,
            "tag"     : unsigned(self.tag_bits),
            "payload" : data.UnionLayout({
                "client": self.payload_type_client,
                "server": self.payload_type_server,
            }),
        })

class NodeSignature(wiring.Signature):

    """
    Both Client and Server nodes must have these connections in order to participate
    in the message ring.

    Messages shift in on :py:`i` and out on :py:`o`. ``Server`` is currently responsible
    for connecting these as appropriate after all ``Client`` instances are created.
    """

    def __init__(self, cfg: Config):
        super().__init__({
            "i":  In(cfg.msg_layout),
            "o":  Out(cfg.msg_layout),
        })

class Client(wiring.Component):

    """
    Client node. Nominally transparent (shifting incoming messages
    to outgoing messages unmodified).

    To issue a request, :py:`i` should be set,
    and :py:`strobe` asserted, until :py:`valid` is asserted. On
    the same clock that :py:`valid` is asserted, :py:`o` contains
    the answer from the server to our request.

    Under the hood, :py:`Client` will take care of not
    sending our request until the bus is free, and not asserting
    :py:`valid` until an appropriate response has arrived.
    """

    def __init__(self, cfg: Config):
        super().__init__({
            # Connection to Ring NoC (`Server` handles this)
            "ring":   Out(NodeSignature(cfg)),

            # Connections to your logic.

            # Unique ID of this client. Must be set by a superclass.
            "tag":    In(unsigned(cfg.tag_bits)),

            # Outgoing request shifted out to server
            "i":      In(cfg.payload_type_client),
            "strobe": In(1),

            # Incoming request arriving from server
            "valid":  Out(1),
            "o":      Out(cfg.payload_type_server),
        })

    def elaborate(self, platform):
        m = Module()

        ring = self.ring

        m.d.sync += [
            ring.o.eq(ring.i)
        ]

        wait = Signal()

        # TODO: latch message after strobe until bus free?
        # => not really needed assuming current contract in MAC() baseclass.

        # Client: If no pending message on our input, we can shift a message out onto the ring.
        with m.If((ring.i.kind == MessageKind.INVALID) & self.strobe & ~wait):
            m.d.sync += [
                wait.eq(1),
                ring.o.source.eq(MessageSource.CLIENT),
                ring.o.kind.eq(MessageKind.VALID),
                ring.o.tag.eq(self.tag),
                ring.o.payload.client.eq(self.i),
            ]

        # Client: If a message arrives from the server with our tag, we can consume it.
        with m.If((ring.i.kind == MessageKind.VALID) &
                  (ring.i.source == MessageSource.SERVER) &
                  (ring.i.tag == self.tag) &
                  wait):

            m.d.comb += [
                self.valid.eq(1),
                self.o.eq(ring.i.payload.server),
            ]

            m.d.sync += [
                ring.o.kind.eq(MessageKind.INVALID),
                wait.eq(0),
            ]

        return m

class Server(wiring.Component):
    """
    Process client requests. This component also manages the ring topology by
    creating clients and wiring them into a ring. When a valid client message
    arrives, ``process_request`` is used to compute a response.

    ``client_class`` can be any class that exposes a ``NodeSignature``, as
    long as it has a constructor that can take ``tag: int`` and ``cfg: Config``.
    A new instance of this is created whenever the user calls ``new_client``.
    """

    def __init__(self, cfg: Config, process_request, client_class):
        self.cfg = cfg
        self.client_class = client_class
        self.clients = []
        self.process_request = process_request

    def new_client(self):
        """Create and add a new client to the ring."""
        tag = len(self.clients)
        assert len(self.clients) < self.cfg.max_clients
        client = self.client_class(tag=tag, cfg=self.cfg)
        self.clients.append(client)
        return client

    def elaborate(self, platform):
        m = Module()

        assert len(self.clients) > 0, "Server must have at least one client"

        # The Server's own ring connections (i / o)
        ring = NodeSignature(self.cfg).create()

        # Server: default behavior: pass messages through
        m.d.sync += ring.o.eq(ring.i)

        # Wire up all clients in a ring, inserting ourselves at the end.
        m.d.comb += [
            self.clients[0].ring.i.eq(ring.o),
            ring.i.eq(self.clients[-1].ring.o),
        ]
        for n in range(len(self.clients)-1):
            m.d.comb += self.clients[n+1].ring.i.eq(self.clients[n].ring.o)

        # Server: valid client message: respond to it.
        with m.If((ring.i.kind == MessageKind.VALID) &
                  (ring.i.source == MessageSource.CLIENT)):
            result = self.process_request(m, ring.i.payload.client)
            m.d.sync += [
                ring.o.source.eq(MessageSource.SERVER),
                ring.o.payload.server.eq(result),
            ]

        return m
