# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Utilities for dealing with contiguous blocks of samples."""

from amaranth import *
from amaranth.lib import data

class Block(data.StructLayout):
    """:class:`data.StructLayout` representing a 'Block' of samples.

    shape : Shape
        Shape of the ``sample`` payload of elements in this block.

    This is normally used in combination with  :class:`stream.Signature`, where
    ``valid``, ``ready`` and ``payload.first`` are used to delineate samples
    inside. Blocks are transferred one sample at a time - a practical example
    with blocks of length 8:

    .. code-block:: text

                         |-- block 1 --| |-- block 2 --| |---
        payload.sample:  0 1 2 3 4 5 6 7 8 A B C D E F G H I ...
        payload.first:   -_______________-_______________-__
        valid:           -_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-_-
        ready:           (all ones)

    Most cores here are assuming they are working with blocks of some predefined
    size - that is, each producer/consumer must expect the same size of :class:`Block`.

    Members
    -------
    first : :py:`unsigned(1)`
        Strobe asserted for first sample in a block, deasserted otherwise.
    sample : :py:`shape`
        Payload of this sample in the block.
    """
    def __init__(self, shape):
        super().__init__({
            "first": unsigned(1),
            "sample": shape
        })

def connect_without_payload(m, stream_o, stream_i):
    m.d.comb += [
        stream_i.valid.eq(stream_o.valid),
        stream_o.ready.eq(stream_i.ready),
    ]
    if hasattr(stream_o.payload, 'first') or hasattr(stream_i.payload, 'first'):
        m.d.comb += stream_i.payload.first.eq(stream_o.payload.first)

