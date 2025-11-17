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
"""

from amaranth import *
from amaranth.lib import data, enum, wiring
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from dataclasses import dataclass

from amaranth_future import fixed

from . import ASQ
from .. import ringnoc

# Maximum multiplier argument for native 18-bit multipliers..
SQNative = fixed.SQ(3, ASQ.f_bits)
# Maximum multiplier result for native 18-bit multipliers.
SQRNative = fixed.SQ(SQNative.i_bits*2, SQNative.f_bits*2)

class MAC(wiring.Component):

    """
    Base class for MAC strategies. Subclasses provide the concrete strategy.

    Users of this component perform multiplications using :py:`MAC.Multiply(m, ...)`,
    which may have different latency depending on the concrete strategy.
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
        Compute ``z = a*b``, returning a context object which is active
        in the same clock that the answer is available on ``self.result.z``.

        Ensure operands do NOT change until the operation completes.

        For example:

        .. code-block:: python

            s_a = fixed.Const(0.5, shape=mac.SQNative)
            s_b = fixed.Const(0.25, shape=mac.SQNative)
            s_z = Signal(ASQ)

            with m.FSM() as fsm:
                # ... some states ...
                with m.State('MAC'):
                    # Set up multiplication
                    # Read as: ``m.If(result_available)``
                    with mp.Multiply(m, a=s_a, b=s_b):
                        m.d.sync += s_z.eq(mp.result.z)
                        m.next = 'DONE'
                # ... some more states ...
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
    MuxMAC using time division multiplexing.

    When sharing amongst lots of cores, the required multiplexer
    size can quickly become unusably large.
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
    steps. That is, the :py:`RingMAC` itself is Mux'd *within* a
    core, however all requests land on the same shared bus
    which is a message ring connecting *different* cores.

    This provides near-optimal scheduling for message rings composed
    of components that have the same state machines.

    Contains no multiplier, :py:`ring` must be hooked up to a
    message ring on which a :py:`RingMACServer` can be found.
    :py:`tag` MUST uniquely identify the underlying :py:`ringnoc.Client`
    instantiated inside this :py:`RingMAC`. If you are careful to only
    use :py:`RingMACServer.new_client()` to create these, all of
    these assumptions will be held.
    """

    def __init__(self, tag: int, cfg: ringnoc.Config):
        self.tag = tag
        self.ring_client = ringnoc.Client(cfg)
        mtype = cfg.payload_type_client["a"].shape
        super().__init__(mtype=mtype, attrs={
            "ring": Out(ringnoc.NodeSignature(cfg)),
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
    Factory for creating a MAC message ring.

    Prior to elaboration, :py:`Server.new_client()` may be used to
    add additional client nodes to this ring.

    During elaboration, all clients (and this server) are connected in
    a ring, and a single shared DSP tile is instantiated to serve requests.

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
