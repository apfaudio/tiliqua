# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Spectral processing components."""

from amaranth import *
from amaranth.lib import memory, stream, wiring
from amaranth.lib.wiring import In, Out

from amaranth_future import fixed

from . import block, cordic, mac
from .block import Block
from .complex import CQ, connect_magnitude_to_sq
from .stream_util import Merge, connect_remap


class BlockLPF(wiring.Component):

    """Block-based (point-wise) one-pole low-pass filter array.

    This is an array (size `sz`) of one-pole low-pass filters with a single
    adjustable smoothing constant `beta`. That is, an independent filter is
    tracked for every element in each block. The :class:`Block` ``payload.first``
    flags are used to track which filter memory should be addressed for each
    sample, without requiring separate streams for each channel.

    For each element, we compute:

    .. code-block:: text

        self.y[n] = self.y[n]*self.beta + self.x[n]*(1-self.beta)

    This is useful for morphing between blocks of real spectral envelopes, but could
    also be used for other purposes.

    Members
    -------
    i : :py:`In(stream.Signature(Block(self.shape)))`
        Incoming stream of blocks of real samples.
    o : :py:`Out(stream.Signature(Block(self.shape)))`
        Outgoing stream of blocks of real samples.
    """

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int,
                 macp = None):
        """
        shape : Shape
            Shape of fixed-point number to use for block streams.
        sz : int
            Number of independent filters, must exactly match the size of each block.
        macp : bool
            A :class:`mac.MAC` provider, for multiplies.
        """
        self.shape = shape
        self.sz    = sz
        self.macp = macp or mac.MAC.default()
        super().__init__({
            # Low-pass 1-pole smoothing constant, 0 (slow response) to 1 (fast response).
            "beta": In(self.shape, init=fixed.Const(0.75, shape=self.shape)),
            # Blockwise sets of signals to filter.
            "i": In(stream.Signature(Block(self.shape))),
            "o": Out(stream.Signature(Block(self.shape))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.macp = mp = self.macp

        #
        # Filter memory and ports
        #

        m.submodules.mem = mem = memory.Memory(shape=self.shape, depth=self.sz, init=[])
        mem_rd = mem.read_port()
        mem_wr = mem.write_port()

        #
        # Filter memory addressing
        #

        idx = Signal(range(self.sz+1))
        l_in = Signal(self.shape)
        m.d.comb += [
            mem_rd.en.eq(1),
            mem_rd.addr.eq(idx),
            mem_wr.addr.eq(idx),
        ]
        m.d.sync += mem_wr.en.eq(0)

        #
        # Iterative MAC state machine
        #

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                    m.d.sync += l_in.eq(self.i.payload.sample)
                    with m.If(self.i.payload.first):
                        m.d.sync += idx.eq(0)
                    with m.Else():
                        m.d.sync += idx.eq(idx+1)
                    m.next = "READ"

            with m.State("READ"):
                m.next = "MAC1"

            with m.State("MAC1"):
                with mp.Multiply(m, a=mem_rd.data, b=self.beta):
                    m.d.sync += mem_wr.data.eq(mp.result.z)
                    m.next = "MAC2"

            with m.State("MAC2"):
                with mp.Multiply(m, a=l_in, b=(fixed.Const(1.0, shape=self.shape, clamp=True)-self.beta)):
                    m.d.sync += mem_wr.data.eq(mem_wr.data + mp.result.z)
                    m.next = "UPDATE"

            with m.State("UPDATE"):
                m.d.sync += [
                    mem_wr.en.eq(1),
                    self.o.payload.first.eq(idx == 0),
                    self.o.payload.sample.eq(mem_wr.data),
                ]
                m.next = "OUTPUT"

            with m.State("OUTPUT"):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.next = "IDLE"

        return m

class SpectralEnvelope(wiring.Component):

    """Compute a smoothed, real spectral envelope.

    Given a block of complex frequency-domain spectra, extract the
    magnitude from each point and filter each magnitude in the block
    independently with a one-pole smoother, emitting a corresponding
    block representing the evolving (smoothed)  spectral envelope.

    The rect-to-polar CORDIC is run without magnitude correction, which
    saves another multiplier at the cost of everything being multiplied
    by a constant factor (may or may not matter depending on the use).

    Members
    -------
    i : :py:`In(stream.Signature(Block(CQ(self.shape))))`
        Incoming stream of blocks of complex spectra.
    o : :py:`Out(stream.Signature(Block(self.shape)))`
        Outgoing stream of blocks of real (smoothed) magnitude spectra.
    """

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int):
        """
        shape : Shape
            Shape of fixed-point number to use for streams.
        sz : int
            The size of each input block and outgoing spectral envelope blocks.
        """
        self.shape = shape
        self.sz    = sz
        super().__init__({
            "i": In(stream.Signature(Block(CQ(self.shape)))),
            "o": Out(stream.Signature(Block(self.shape))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()
        m.submodules.rect_to_polar = rect_to_polar = block.WrapCore(cordic.RectToPolarCordic(
                self.shape, magnitude_correction=False))
        m.submodules.block_lpf = block_lpf = BlockLPF(
                self.shape, self.sz)
        wiring.connect(m, wiring.flipped(self.i), rect_to_polar.i)
        connect_magnitude_to_sq(m, rect_to_polar.o, block_lpf.i)
        wiring.connect(m, block_lpf.o, wiring.flipped(self.o))
        return m


class SpectralCrossSynthesis(wiring.Component):

    """Apply the spectral envelope of 'modulator' on a 'carrier'.

    Consume 2 sets of frequency-domain spectra (blocks) representing a
    'carrier' and 'modulator'. The (real) envelope of the 'modulator'
    spectra is multiplied by the (complex) 'carrier' spectra, creating
    a classic vocoder effect where the timbre of the 'carrier' dominates,
    but is filtered spectrally by the 'modulator'

    This core computes the spectral envelope of the modulator by filtering
    the magnitude of each frequency band, see :class:`SpectralEnvelope` for details.
    Put simply, this core computes:

    .. code-block:: text

        out.real = carrier.real * modulator.envelope_magnitude
        out.imag = carrier.imag * modulator.envelope_magnitude

    Members
    -------
    i_carrier : :py:`In(stream.Signature(Block(CQ(self.shape))))`
        Incoming stream of blocks of complex spectra of the 'carrier'.
    i_modulator : :py:`In(stream.Signature(Block(CQ(self.shape))))`
        Incoming stream of blocks of complex spectra of the 'modulator'.
    o : :py:`Out(stream.Signature(Block(CQ(self.shape))))`
        Outgoing stream of cross-synthesized 'carrier' and 'modulator'.
    """

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int):
        """
        shape : Shape
            Shape of fixed-point number to use for block streams.
        sz : int
            Size of each block of complex spectra.
        """
        self.shape = shape
        self.sz    = sz
        super().__init__({
            # All frequency domain spectra in blocks.
            "i_carrier": In(stream.Signature(Block(CQ(self.shape)))),
            "i_modulator": In(stream.Signature(Block(CQ(self.shape)))),
            "o": Out(stream.Signature(Block(CQ(self.shape)))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # Connect modulator spectra to spectral envelope detector

        m.submodules.spectral_envelope = spectral_envelope = SpectralEnvelope(
            shape=self.shape, sz=self.sz)
        wiring.connect(m, wiring.flipped(self.i_modulator), spectral_envelope.i)

        # Time-synchronize output of 'spectral_envelope' with 'i_carrier' by
        # merging these two streams together, so we can multiply them pointwise.

        m.submodules.merge2 = merge2 = Merge(n_channels=2, shape=self.i_carrier.payload.shape())
        wiring.connect(m, wiring.flipped(self.i_carrier), merge2.i[0])
        connect_remap(m, spectral_envelope.o, merge2.i[1], lambda o, i : [
            i.payload.sample.real.eq(o.payload.sample),
            i.payload.first.eq(o.payload.first),
        ])

        # Shared multiplier for carrier * mag(modulator) terms

        modulator_a = Signal(self.shape)
        modulator_b = Signal(self.shape)
        modulator_z = Signal(self.shape)
        m.d.comb += modulator_z.eq((modulator_a * modulator_b)<<3)

        # Input latch
        l_carrier   = Signal.like(self.i_carrier.payload.sample)
        l_first     = Signal()

        with m.FSM():
            with m.State("IDLE"):
                # Wait for time-synchronized carrier and spectral envelope block
                m.d.comb += merge2.o.ready.eq(1)
                with m.If(merge2.o.valid):
                    m.d.sync += [
                        l_carrier.eq(merge2.o.payload[0].sample),
                        modulator_b.eq(merge2.o.payload[1].sample.real),
                        # TODO frame alignment (not needed for STFT cores
                        # with shared reset.)
                        l_first.eq(merge2.o.payload[0].first),
                    ]
                    m.next = "REAL"

            # Multiply real/imag components of carrier by modulator spectra
            # computed by SpectralEnvelope, pointwise

            with m.State("REAL"):
                m.d.comb += modulator_a.eq(l_carrier.real)
                m.d.sync += self.o.payload.sample.real.eq(modulator_z)
                m.next = "IMAG"

            with m.State("IMAG"):
                m.d.comb += modulator_a.eq(l_carrier.imag)
                m.d.sync += self.o.payload.sample.imag.eq(modulator_z)
                m.next = "OUTPUT"

            with m.State("OUTPUT"):
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload.first.eq(l_first),
                ]
                with m.If(self.o.ready):
                    m.next = "IDLE"

        return m
