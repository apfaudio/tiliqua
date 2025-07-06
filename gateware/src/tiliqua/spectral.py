from amaranth import *
from amaranth.lib import wiring, data, stream, memory
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import atan, pi

from tiliqua.fft import CQ
from tiliqua import dsp, mac, cordic

class BlockLPF(wiring.Component):

    """
    This is an array (size `sz`) of one-pole low-pass filters with a single
    adjustable smoothing constant `beta`. The `i.payload.first` and `o.payload.first`
    flags are used to track which filter memory should be addressed for each
    sample, without requiring separate streams for each channel.

    For each element, we compute:

        self.y[n] = self.y[n]*self.beta + self.x[n]*(1-self.beta)

    This is intended for filtering blocks of real spectral envelopes, but could
    also be used for other purposes in the future.
    """

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int,
                 macp = None):
        self.shape = shape
        self.sz    = sz
        self.macp = macp or mac.MAC.default()
        super().__init__({
            # Low-pass 1-pole smoothing constant, 0 (slow response) to 1 (fast response).
            "beta": In(self.shape, init=fixed.Const(0.75, shape=self.shape)),
            # Blockwise sets of signals to filter.
            "i": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": self.shape
            }))),
            "o": Out(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": self.shape
            }))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.macp = mp = self.macp

        m.submodules.mem = mem = memory.Memory(shape=self.shape, depth=self.sz, init=[])
        mem_rd = mem.read_port()
        mem_wr = mem.write_port()

        idx = Signal(range(self.sz+1))
        l_in = Signal(self.shape)

        m.d.comb += [
            mem_rd.en.eq(1),
            mem_rd.addr.eq(idx),
            mem_wr.addr.eq(idx),
        ]

        m.d.sync += mem_wr.en.eq(0)

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
                    m.d.sync += mem_wr.data.eq(mp.z)
                    m.next = "MAC2"

            with m.State("MAC2"):
                with mp.Multiply(m, a=l_in, b=(fixed.Const(0.99, shape=self.shape)-self.beta)):
                    m.d.sync += mem_wr.data.eq(mem_wr.data + mp.z)
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

    """
    Given a block of complex frequency-domain samples, extract the
    amplitude from each one and filter each amplitude in the block
    independently with a one-pole smoother, emitting a corresponding
    block representing the evolving spectral envelope.

    The rect-to-polar CORDIC is run without magnitude correction, which
    saves another multiplier at the cost of everything being multiplied
    by a constant factor (which makes no difference here).
    """

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int):
        self.shape = shape
        self.sz    = sz
        super().__init__({
            "i": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
            "o": Out(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": self.shape
            }))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()
        m.submodules.rect_to_polar = rect_to_polar = cordic.RectToPolarCordic(
                self.shape, magnitude_correction=False)
        m.submodules.block_lpf = block_lpf = BlockLPF(
                self.shape, self.sz)
        wiring.connect(m, wiring.flipped(self.i), rect_to_polar.i)
        dsp.connect_remap(m, rect_to_polar.o, block_lpf.i, lambda o, i : [
            i.payload.sample.eq(o.payload.magnitude),
            i.payload.first.eq(o.payload.first),
        ])
        wiring.connect(m, block_lpf.o, wiring.flipped(self.o))
        return m

class SpectralCrossSynthesis(wiring.Component):

    """
    Consume 2 sets of frequency-domain information representing a
    'carrier' and 'modulator'. The (real) envelope of the 'modulator'
    spectra is multiplied by the (complex) 'carrier' spectra, creating
    a classic vocoder effect where the timbre of the 'carrier' dominates,
    but is filtered spectrally by the 'modulator'

    This core computes the spectral envelope of the modulator by filtering
    the magnitude of each frequency band, see ``SpectralEnvelope`` for details.
    Put simply, this core computes:

        out.real = carrier.real * modulator.envelope_magnitude
        out.imag = carrier.imag * modulator.envelope_magnitude

    """

    def __init__(self,
                 shape: fixed.Shape,
                 sz: int):

        self.shape = shape
        self.sz    = sz

        super().__init__({
            # All frequency domain spectra in blocks.
            "i_carrier": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
            "i_modulator": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
            "o": Out(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.spectral_envelope = spectral_envelope = SpectralEnvelope(
            shape=self.shape, sz=self.sz)

        l_carrier   = Signal.like(self.i_carrier.payload.sample)
        l_first     = Signal()

        m.submodules.merge2 = merge2 = dsp.Merge(n_channels=2, shape=self.i_carrier.payload.shape())
        wiring.connect(m, wiring.flipped(self.i_carrier), merge2.i[0])
        wiring.connect(m, wiring.flipped(self.i_modulator), spectral_envelope.i)
        dsp.connect_remap(m, spectral_envelope.o, merge2.i[1], lambda o, i : [
            i.payload.sample.real.eq(o.payload.sample),
            i.payload.first.eq(o.payload.first),
        ])

        # Shared multiplier for carrier * mag(modulator) terms
        modulator_a = Signal(self.shape)
        modulator_b = Signal(self.shape)
        modulator_z = Signal(self.shape)
        m.d.comb += modulator_z.eq((modulator_a * modulator_b)<<3)

        with m.FSM():
            with m.State("IDLE"):
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
