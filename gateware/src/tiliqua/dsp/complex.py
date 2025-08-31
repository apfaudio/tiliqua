# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Utilities for dealing with fixed-point complex numbers."""

from amaranth.lib import data

from amaranth_future import fixed

from . import block


class CQ(data.StructLayout):
    """:class:`data.StructLayout` representing a complex number, formed by a pair of numbers.

    shape : fixed.SQ
        Shape of the fixed-point types used for real and imaginary components.

    Members
    -------
    real : :py:`shape`
        Real component of complex number.
    imag : :py:`shape`
        Imaginary component of complex number.
    """
    def __init__(self, shape: fixed.SQ):
        super().__init__({
            "real": shape,
            "imag": shape,
        })

class Polar(data.StructLayout):
    """:class:`data.StructLayout` representing a complex number in polar form.

    shape : fixed.SQ
        Shape of the fixed-point types used for magnitude and phase components.

    Members
    -------
    magnitude : :py:`shape`
        Magnitude component of complex number.
    phase : :py:`shape`
        Phase component of complex number.
    """
    def __init__(self, shape: fixed.SQ):
        super().__init__({
            "magnitude": shape,
            "phase": shape,
        })

def connect_sq_to_real(m, stream_o, stream_i):
    """Adapter: connect a real ``stream_o`` to a complex ``stream_i``, forwarding
    only the real component.
    """
    block.connect_without_payload(m, stream_o, stream_i)
    m.d.comb += [
        stream_i.payload.sample.real.eq(stream_o.payload.sample),
        stream_i.payload.sample.imag.eq(0),
    ]

def connect_real_to_sq(m, stream_o, stream_i):
    """Adapter: connect a complex ``stream_o`` to a real ``stream_i``, forwarding
    only the real component.
    """
    block.connect_without_payload(m, stream_o, stream_i)
    m.d.comb += [
        stream_i.payload.sample.eq(stream_o.payload.sample.real),
    ]


def connect_magnitude_to_sq(m, stream_o, stream_i):
    """Adapter: connect a polar ``stream_o`` to a real ``stream_i``, forwarding
    only the magnitude component.
    """
    block.connect_without_payload(m, stream_o, stream_i)
    m.d.comb += [
        stream_i.payload.sample.eq(stream_o.payload.sample.magnitude),
    ]
