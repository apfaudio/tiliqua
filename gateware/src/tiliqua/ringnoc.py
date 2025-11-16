# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""
Basic 'Message Ring' Network-on-Chip (NoC) implementation.

Provides message ring components for connecting clients and a server
in a circular shift register topology. This enables efficient resource
sharing (e.g., DSP tiles) across many components without consuming
huge multiplexers or routing resources.
"""

from dataclasses import dataclass

from amaranth import *
from amaranth.lib import data, enum, wiring
from amaranth.lib.wiring import In, Out

class MessageKind(enum.Enum, shape=unsigned(1)):
    INVALID     = 0
    VALID       = 1

class MessageSource(enum.Enum, shape=unsigned(1)):
    CLIENT     = 0
    SERVER     = 1

@dataclass
class Config:
    """
    Metadata associated with a message ring.
    """
    tag_bits: int
    payload_type_client: data.StructLayout
    payload_type_server: data.StructLayout

    @property
    def max_clients(self):
        return 1 << self.tag_bits

    @property
    def msg_layout(self):
        """
        Message ring message layout.
        This message may be populated by a client or a server on the NoC.

        Returns a data.StructLayout configured for this metadata.
        """
        return data.StructLayout({
            "source"  : MessageSource,
            "kind"    : MessageKind,
            "tag"     : unsigned(self.tag_bits),
            "payload" : data.UnionLayout({
                "client": self.payload_type_client,
                "server": self.payload_type_server,
            }),
        })

class Signature(wiring.Signature):

    """
    Connection of a Client or Server to a message ring.
    Messages shift in on :py:`i` and out on :py:`o`.
    """

    def __init__(self, cfg: Config):
        super().__init__({
            "i":  In(cfg.msg_layout),
            "o":  Out(cfg.msg_layout),
        })

class Client(wiring.Component):

    """
    Message ring client participant.

    :py:`ring` should connect to the ring bus.

    To issue a request, :py:`i` and :py:`tag` should be set,
    and :py:`strobe` asserted, until :py:`valid` is asserted. On
    the same clock that :py:`valid` is asserted, :py:`o` contains
    the answer from the server to our request.

    Under the hood, :py:`Client` will take care of not
    sending our request until the bus is free, and not asserting
    :py:`valid` until an appropriate response has arrived.
    """

    def __init__(self, cfg: Config):
        super().__init__({
            # Connection to Ring NoC
            "ring":   Out(Signature(cfg)),

            # Connections to the NoC participant (your logic).
            "i":      In(cfg.payload_type_client),
            "o":      Out(cfg.payload_type_server),

            "tag":    In(unsigned(cfg.tag_bits)),
            "strobe": In(1),
            "valid":  Out(1),
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

        with m.If((ring.i.kind == MessageKind.INVALID) & self.strobe & ~wait):
            m.d.sync += [
                wait.eq(1),
                ring.o.source.eq(MessageSource.CLIENT),
                ring.o.kind.eq(MessageKind.VALID),
                ring.o.tag.eq(self.tag),
                ring.o.payload.client.eq(self.i),
            ]

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
