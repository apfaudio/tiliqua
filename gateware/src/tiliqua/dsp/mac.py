# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
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

from amaranth import *
from amaranth.lib import data, enum, wiring
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from .. import ringnoc

from dataclasses import dataclass

from . import ASQ

# Native 18-bit multiplier type.
SQNative = fixed.SQ(3, ASQ.f_bits)
SQRNative = fixed.SQ(SQNative.i_bits*2, SQNative.f_bits*2)

class MAC(wiring.Component):

    """
    Base class for MAC strategies.
    Subclasses provide the concrete strategy.

    Subclasses use this through :py:`mac.Multiply(m, ...)`
    """

    @staticmethod
    def operands_layout(mtype):
        return data.StructLayout({
            "a": mtype,
            "b": mtype,
        })

    @staticmethod
    def result_layout(mtype):
        return data.StructLayout({
            "z": fixed.SQ(mtype.i_bits*2, mtype.f_bits*2),
        })

    def __init__(self, mtype = SQNative, attrs={}):
        super().__init__({
            "operands": In(MAC.operands_layout(mtype)),
            "result": Out(MAC.result_layout(mtype)),
            # Assert strobe when operands are valid. Keep operands
            # valid and strobe asserted until `valid` is strobed,
            # at which point result can be considered valid.
            "strobe": Out(1),
            "valid": Out(1),
        } | attrs)

    def Multiply(self, m, **operands):
        """
        Contents of an FSM state, computing `z = a*b`.
        Ensure operands will NOT change until the operation completes.

        Returns a context object which may be used to perform more
        actions in the same clock the MAC is complete.
        """
        for name, value in operands.items():
            m.d.comb += getattr(self.operands, name).eq(value)
        m.d.comb += self.strobe.eq(1)
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
            self.result.z.eq(self.operands.a * self.operands.b),
            self.valid.eq(1),
        ]
        return m

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
    :py:`tag` MUST uniquely identify the underlying :py:`ringnoc.Client`
    instantiated inside this :py:`RingMAC`.
    """

    def __init__(self, tag: int, cfg: ringnoc.Config):
        self.tag = tag
        self.ring_client = ringnoc.Client(cfg)
        mtype = cfg.payload_type_client["a"].shape
        super().__init__(mtype=mtype, attrs={
            "ring": Out(ringnoc.Signature(cfg)),
        })

    def elaborate(self, platform):
        m = Module()

        # TODO: assert self.tag < self.ring.signature.tag_bits

        m.submodules.ring_client = self.ring_client
        wiring.connect(m, wiring.flipped(self.ring), self.ring_client.ring)

        m.d.comb += [
            self.ring_client.tag.eq(self.tag),
            self.ring_client.i.eq(self.operands),
            self.ring_client.strobe.eq(self.strobe),
            self.result.eq(self.ring_client.o),
            self.valid.eq(self.ring_client.valid),
        ]

        return m

def RingMACServer(max_clients=16, mtype=SQNative):
    """
    Factory function for creating a MAC message ring server.

    Prior to elaboration, :py:`new_client()` may be used to
    add additional client nodes to this ring.

    During elaboration, all clients (and this server) are
    connected in a ring, and a single shared DSP tile
    is instantiated to serve requests.

    Returns:
        ringnoc.Server configured for MAC operations
    """
    return ringnoc.Server(
        cfg=ringnoc.Config(
            tag_bits=exact_log2(max_clients),
            payload_type_client=MAC.operands_layout(mtype),
            payload_type_server=MAC.result_layout(mtype),
        ),
        process_request=lambda m, operands: operands.a * operands.b,
        client_class=RingMAC,
    )
