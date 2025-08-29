# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Resampling."""

import math
from amaranth import *
from amaranth.lib import wiring, stream
from amaranth.lib.wiring import In, Out

from .filters import FIR
from ..eurorack_pmod import ASQ


class Resample(wiring.Component):

    """
    Polyphase fractional resampler.

    Upsamples by factor N, filters the result, then downsamples by factor M.
    The upsampling action zero-pads before applying the low-pass filter, so
    the low-pass filter coefficients are prescaled by N to preserve total energy.

    The underlying FIR interpolator only performs MACs on non-padded input samples,
    (and for output samples which are not discarded), which can make a big difference
    for large upsampling/interpolating ratios, and is what makes this a polyphase
    resampler - time complexity per output sample proportional to O(fir_order/N).

    Members
    -------
    i : :py:`In(stream.Signature(ASQ))`
        Input stream for sending samples to the resampler at sample rate :py:`fs_in`.
    o : :py:`In(stream.Signature(ASQ))`
        Output stream for getting samples from the resampler. Samples are produced
        at a rate determined by :py:`fs_in * (n_up / m_down)`.
    """

    i: In(stream.Signature(ASQ))
    o: Out(stream.Signature(ASQ))

    def __init__(self,
                 fs_in:      int,
                 n_up:       int,
                 m_down:     int,
                 bw:         float=0.4,
                 order_mult: int=5):
        """
        fs_in : int
            Expected sample rate of incoming samples, used for calculating filter coefficients.
        n_up : int
            Numerator of the resampling ratio. Samples are produced at :py:`fs_in * (n_up / m_down)`.
            If :py:`n_up` and :py:`m_down` share a common factor, the internal resampling ratio is reduced.
        m_down : int
            Denominator of the resampling ratio. Samples are produced at :py:`fs_in * (n_up / m_down)`.
            If :py:`n_up` and :py:`m_down` share a common factor, the internal resampling ratio is reduced.
        bw : float
            Bandwidth (0 to 1, proportion of the nyquist frequency) of the resampling filter.
        order_mult : int
            Filter order multiplier, determines number of taps in underlying FIR filter. The
            underlying tap count is determined as :py:`order_factor*max(self.n_up, self.m_down)`,
            rounded up to the next multiple of :py:`n_up` (required for even zero padding).
        """

        gcd = math.gcd(n_up, m_down)
        if gcd > 1:
            print(f"WARN: Resample {n_up}/{m_down} has GCD {gcd}. Using {n_up//gcd}/{m_down//gcd}.")
            n_up = n_up//gcd
            m_down = m_down//gcd

        self.fs_in  = fs_in
        self.n_up   = n_up
        self.m_down = m_down
        self.bw     = bw

        # determine filter order
        filter_order = order_mult*max(n_up, m_down)
        if filter_order % n_up != 0:
            filter_order = ((filter_order // n_up) + 1) * n_up

        self.fir = FIR(
            fs=fs_in * n_up,
            filter_cutoff_hz=int(fs_in*bw/2),
            filter_order=filter_order,
            filter_type='lowpass',
            prescale=n_up,
            stride_i=n_up,
            stride_o=m_down)

        super().__init__()

    def elaborate(self, platform):
        m = Module()
        m.submodules.fir = self.fir
        wiring.connect(m, wiring.flipped(self.i), self.fir.i)
        wiring.connect(m, self.fir.o, wiring.flipped(self.o))
        return m