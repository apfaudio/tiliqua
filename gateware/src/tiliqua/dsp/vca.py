# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.wiring import In, Out

from . import ASQ, mac


class VCA(wiring.Component):

    """
    Voltage Controlled Amplifier (simple multiplier with saturation).
    Output values are clipped to fit in the output type.

    Members
    -------
    i : :py:`In(stream.Signature(data.ArrayLayout(itype, 2)))`
        2-channel input stream.
    o : :py:`Out(stream.Signature(otype))`
        Output stream, :py:`i.payload[0] * i.payload[1]`.
    """

    def __init__(self, itype=mac.SQNative, otype=ASQ, macp=None):
        self.macp = macp or mac.MAC.default()
        super().__init__({
            "i": In(stream.Signature(data.ArrayLayout(itype, 2))),
            "o": Out(stream.Signature(otype))
        })

    def elaborate(self, platform):
        m = Module()

        m.submodules.macp = mp = self.macp

        with m.FSM() as fsm:

            with m.State('WAIT-VALID'):
                m.d.comb += self.i.ready.eq(1),
                with m.If(self.i.valid):
                   m.next = 'MAC'

            with m.State('MAC'):
                with mp.Multiply(m, a=self.i.payload[0], b=self.i.payload[1]):
                    m.d.sync += self.o.payload.eq(mp.result.z.saturate(self.o.payload.shape()))
                    m.next = 'WAIT-READY'

            with m.State('WAIT-READY'):
                m.d.comb += self.o.valid.eq(1),
                with m.If(self.o.ready):
                    m.next = 'WAIT-VALID'

        return m
