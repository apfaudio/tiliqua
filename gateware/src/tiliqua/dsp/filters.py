# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.memory import Memory
from amaranth.lib.wiring import In, Out
from scipy import signal

from amaranth_future import fixed

from . import ASQ, mac


class SVF(wiring.Component):

    """
    Oversampled Chamberlin State Variable Filter.

    Filter `cutoff` and `resonance` are tunable at the system sample rate.

    Highpass, lowpass, bandpass routed out on stream payloads `hp`, `lp`, `bp`.

    Reference: Fig.3 in https://arxiv.org/pdf/2111.05592
    """

    def __init__(self, sq=ASQ, macp=None):
        self.sq = sq
        self.macp = macp or mac.MAC.default()
        super().__init__({
            "i": In(stream.Signature(data.StructLayout({
                    "x": sq,
                    "cutoff": sq,
                    "resonance": sq,
                }))),
            "o": Out(stream.Signature(data.StructLayout({
                    "hp": sq,
                    "lp": sq,
                    "bp": sq,
                }))),
        })

    def elaborate(self, platform):
        m = Module()

        m.submodules.macp = mp = self.macp

        x     = Signal(mac.SQNative)
        kK    = Signal.like(x)
        kQinv = Signal.like(x)

        abp   = Signal(fixed.SQ(mac.SQNative.i_bits, mac.SQNative.f_bits+2))
        alp   = Signal.like(abp)
        ahp   = Signal.like(alp)

        # internal oversampling iterations
        n_oversample = 2
        oversample = Signal(range(n_oversample))

        with m.FSM() as fsm:

            with m.State('WAIT-VALID'):
                m.d.comb += self.i.ready.eq(1),
                with m.If(self.i.valid):
                   m.d.sync += x.eq(self.i.payload.x),
                   m.d.sync += oversample.eq(0)
                   with m.If(self.i.payload.cutoff >= 0):
                       m.d.sync += kK.eq(self.i.payload.cutoff)
                   with m.If(self.i.payload.resonance >= 0):
                       m.d.sync += kQinv.eq(self.i.payload.resonance)
                   m.next = 'MAC0'

            with m.State('MAC0'):
                # alp = abp*kK + alp
                with mp.Multiply(m, a=abp, b=kK):
                    m.d.sync += alp.eq(mp.result.z + alp)
                    m.next = 'MAC1'

            with m.State('MAC1'):
                # ahp = abp*-kQinv + (x - alp)
                with mp.Multiply(m, a=abp, b=-kQinv):
                    m.d.sync += ahp.eq(mp.result.z + (x - alp))
                    m.next = 'MAC2'

            with m.State('MAC2'):
                # abp = ahp*kK + abp
                with mp.Multiply(m, a=ahp, b=kK):
                    m.d.sync += abp.eq(mp.result.z + abp)
                    m.next = 'OVER'

            with m.State('OVER'):
                with m.If(oversample == n_oversample - 1):
                    m.next = 'WAIT-READY'
                with m.Else():
                    m.d.sync += oversample.eq(oversample + 1)
                    m.next = 'MAC0'

            with m.State('WAIT-READY'):
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload.hp.eq(ahp >> 1),
                    self.o.payload.lp.eq(alp >> 1),
                    self.o.payload.bp.eq(abp >> 1),
                ]
                with m.If(self.o.ready):
                    m.next = 'WAIT-VALID'

        return m


class DCBlock(wiring.Component):

    """
    Loosely based on:
    https://dspguru.com/dsp/tricks/fixed-point-dc-blocking-filter-with-noise-shaping/
    """

    def __init__(self, pole=0.999, sq=ASQ, macp=None):
        self.macp = macp or mac.MAC.default()
        self.pole = pole
        self.sq = sq
        super().__init__({
            "i": In(stream.Signature(sq)),
            "o": Out(stream.Signature(sq)),
        })

    def elaborate(self, platform):

        m = Module()

        m.submodules.macp = mp = self.macp

        kA    = fixed.Const((1-self.pole), self.sq)

        x     = Signal(self.sq)
        y     = Signal(self.sq)

        acc   = Signal(mac.SQRNative)

        m.d.comb += self.o.payload.eq(acc)

        with m.FSM() as fsm:

            with m.State('WAIT-VALID'):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                   m.d.sync += [
                       x.eq(self.i.payload),
                       acc.eq(acc - x),
                   ]
                   m.next = 'MAC0'

            with m.State('MAC0'):
                with mp.Multiply(m, a=y, b=kA):
                    m.d.sync += acc.eq((acc - mp.result.z) + x)
                    m.next = 'WAIT-READY'

            with m.State('WAIT-READY'):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.d.sync += y.eq(acc)
                    m.next = 'WAIT-VALID'

        return m


class FIR(wiring.Component):

    """
    Fixed-point FIR filter that uses a single multiplier.

    This filter contains some optional optimizations to act as an efficient
    interpolator/decimator. For details, see :py:`stride_i`, :py:`stride_o` below.

    Members
    -------
    i : :py:`In(stream.Signature(ASQ))`
        Input stream for sending samples to the filter.
    o : :py:`In(stream.Signature(ASQ))`
        Output stream for getting samples from the filter. There is 1 output
        sample per input sample, presented :py:`filter_order+1` cycles after
        the input sample. For :py:`stride_o > 1`, there is only 1 output
        sample per :py:`stride_o` input samples.
    """

    i: In(stream.Signature(ASQ))
    o: Out(stream.Signature(ASQ))

    def __init__(self,
                 fs:               int,
                 filter_cutoff_hz: int,
                 filter_order:     int,
                 filter_type:      str='lowpass',
                 prescale:         float=1,
                 stride_i:         int=1,
                 stride_o:         int=1):
        """
        fs : int
            Sample rate of the filter, used for calculating FIR coefficients.
        filter_cutoff_hz : int
            Cutoff frequency of the filter, used for calculating FIR coefficients.
        filter_order : int
            Size of the filter (number of coefficients).
        filter_type : str
            Type of the filter passed to :py:`signal.firwin` - :py:`"lowpass"`,
            :py:`"highpass"` or so on.
        prescale : float
            All taps are scaled by :py:`prescale`. This is used in cases where
            you are upsampling and need to preserve energy. Be careful with this,
            it can overflow the tap coefficients (you'll get a warning).
        stride_i : int
            When an FIR filter is used as an interpolator, a common pattern is
            to provide 1 'actual' sample and pad S-1 zeroes for every S
            output samples needed. For any :py:`stride > 1`, the :py:`stride`
            must evenly divide :py:`filter_order` (i.e. no remainder). For
            :py:`stride > 1`, this core applies some optimizations, assuming
            every S'th sample is nonzero, and the rest are zero. This results in
            a factor S reduction in MAC ops (latency) and a factor S reduction in
            RAM needed for sample storage. The tap storage remains of size
            :py:`filter_order` as all taps are still mathematically required.
            The nonzero sample must be the first sample to arrive.
        stride_o : int
            When an FIR filter is used as a decimator, it is common to keep only
            1 sample and discard M-1 samples (if decimating by factor M). For
            :py:`stride_o == M`, only 1 output sample is produced per M input
            samples. This does not reduce LUT/RAM usage, but avoids performing
            MACs to produce samples that will be discarded.
        """
        taps = signal.firwin(numtaps=filter_order, cutoff=filter_cutoff_hz,
                             fs=fs, pass_zero=filter_type, window='hamming')
        assert len(taps) % stride_i == 0
        self.taps_float = taps
        self.prescale   = prescale
        self.stride_i   = stride_i
        self.stride_o   = stride_o
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        # Tap and accumulator sizes

        self.ctype = fixed.SQ(2, ASQ.f_bits)

        n = len(self.taps_float)

        # Filter tap memory and read port

        # If t*prescale overflows, fixed.Const should provide a warning.
        m.submodules.taps_mem = taps_mem = Memory(
            shape=self.ctype, depth=n, init=[
                fixed.Const(t*self.prescale, shape=self.ctype)
                for t in self.taps_float
            ]
        )

        taps_rport = taps_mem.read_port()

        # Input sample memory, write and read port

        m.submodules.x_mem = x_mem = Memory(
            shape=self.ctype, depth=n//self.stride_i, init=[]
        )

        x_wport = x_mem.write_port()
        x_rport = x_mem.read_port(transparent_for=(x_wport,))

        # FIR filter logic

        # Number of MACs performed per sample, up to n/self.stride
        macs   = Signal(range(n))

        # Write position in input sample memory
        w_pos  = Signal(range(n), init=1)

        # Stride position from 0 .. self.stride_i, moves by 1 every
        # input sample to shift taps looked at (even if the input
        # is padded with zeroes)
        stride_i_pos  = Signal(range(self.stride_i), init=0)

        # Stride position from 0 .. self.stride_o, moves by 1 every
        # output sample. For 'stride_o' == M, output sample is only
        # calculated/emitted once per every M samples.
        stride_o_pos  = Signal(range(self.stride_o), init=0)

        # Read indices into tap and sample memories
        ix_tap = Signal(range(n))
        ix_rd  = Signal(range(n))

        # MAC variables: y = a * b
        a  = Signal(self.ctype)
        b  = Signal(self.ctype)
        y  = Signal(self.ctype)

        m.d.comb += taps_rport.en.eq(1)
        m.d.comb += taps_rport.addr.eq(ix_tap)
        m.d.comb += x_wport.data.eq(self.i.payload)
        m.d.comb += x_rport.addr.eq(ix_rd)
        m.d.comb += x_rport.en.eq(1)

        with m.If(w_pos == (n//self.stride_i - 1)):
            m.d.comb += x_wport.addr.eq(0)
        with m.Else():
            m.d.comb += x_wport.addr.eq(w_pos+1)

        valid = Signal()

        with m.FSM() as fsm:
            with m.State('WAIT-VALID'):
                m.d.comb += self.i.ready.eq(1),
                with m.If(self.i.valid):
                    with m.If(stride_i_pos == 0):
                        m.d.comb += x_wport.en.eq(1)
                    # Set up first MAC combinatorially
                    m.d.comb += x_rport.addr.eq(x_wport.addr)
                    m.d.comb += taps_rport.addr.eq(stride_i_pos)
                    # Subsequent MACs use ix_rd / ix_tap.
                    m.d.sync += [
                        ix_rd.eq(w_pos),
                        ix_tap.eq(stride_i_pos + self.stride_i),
                        y.eq(0),
                        macs.eq(0),
                    ]

                    with m.If(stride_o_pos == 0):
                        m.next = "MAC"
                    with m.Else():
                        m.next = "WAIT-READY"

            with m.State("MAC"):
                m.d.comb += [
                    a.eq(x_rport.data),
                    b.eq(taps_rport.data),
                ]
                m.d.sync += [
                    y.eq(y + (a * b)),
                    macs.eq(macs+1),
                ]
                # next tap read position
                m.d.sync += ix_tap.eq(ix_tap + self.stride_i),
                # next sample read position
                with m.If(ix_rd == 0):
                    m.d.sync += ix_rd.eq((n//self.stride_i - 1))
                with m.Else():
                    m.d.sync += ix_rd.eq(ix_rd - 1),
                # done?
                with m.If(macs == (n//self.stride_i - 1)):
                    m.next = "WAIT-READY"

            with m.State('WAIT-READY'):

                # if stride_o indicates this sample should be discarded, never
                # assert 'valid', simply update the stride counters and jump
                # straight back to 'WAIT-VALID'.

                m.d.comb += [
                    self.o.valid.eq(stride_o_pos == 0),
                    self.o.payload.eq(y)
                ]

                with m.If(self.o.ready | (stride_o_pos != 0)):

                    # update write and stride_i offsets.
                    with m.If(stride_i_pos == (self.stride_i - 1)):
                        m.d.sync += stride_i_pos.eq(0)
                        with m.If(w_pos == (n//self.stride_i - 1)):
                            m.d.sync += w_pos.eq(0)
                        with m.Else():
                            m.d.sync += w_pos.eq(w_pos+1)
                    with m.Else():
                        m.d.sync += stride_i_pos.eq(stride_i_pos+1)

                    # update stride_o index
                    with m.If(stride_o_pos == (self.stride_o - 1)):
                        m.d.sync += stride_o_pos.eq(0)
                    with m.Else():
                        m.d.sync += stride_o_pos.eq(stride_o_pos + 1)

                    m.next = 'WAIT-VALID'

        return m
