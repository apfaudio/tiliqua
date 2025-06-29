#!/usr/bin/env python3
#
# from 'https://github.com/amaranth-farm/amlib/blob/main/amlib/dsp/fixedpointfft.py'
# with some modifications to work in this repository.
#
# Copyright (c) 2022-2023 Kaz Kojima <kkojima@rr.iij4u.or.jp>
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from amaranth import *
from amaranth.lib import memory, wiring, data, stream
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import cos, sin, pi

class CQ(data.StructLayout):
    def __init__(self, shape: fixed.SQ):
        super().__init__({
            "real": shape,
            "imag": shape,
        })

class FixedPointFFT(wiring.Component):

    def __init__(self,
                 shape: fixed.Shape=fixed.SQ(1, 15),
                 pts:   int=1024,
                 ifft = False) -> None:

        self.ifft     = ifft
        self.shape    = shape
        self.wshape   = fixed.SQ(self.shape.i_bits+1, self.shape.f_bits)
        self.pts      = pts
        self.stages   = exact_log2(pts)

        super().__init__({
            "i": In(stream.Signature(data.StructLayout({
                "sample": CQ(self.shape)
            }))),
            "o": Out(stream.Signature(data.StructLayout({
                "sample": CQ(self.shape)
            })))
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        bshape = fixed.SQ(self.shape.i_bits + self.stages, self.shape.f_bits-1)
        m.submodules.x = x = memory.Memory(shape=CQ(bshape), depth=self.pts, init=[])
        m.submodules.y = y = memory.Memory(shape=CQ(bshape), depth=self.pts, init=[])

        twiddle = [
            {'real': cos(k*2*pi/self.pts),
             # conjugate twiddle factors for ifft
             'imag': (1 if self.ifft else -1) * sin(k*2*pi/self.pts)}
            for k in range(self.pts)
        ]

        m.submodules.W = W = memory.Memory(
                shape=CQ(self.wshape), depth=self.pts, init=twiddle)

        x_rd = x.read_port()
        x_wr = x.write_port()
        y_rd = y.read_port()
        y_wr = y.write_port()

        W_rd = W.read_port()

        N = self.stages
        idx = Signal(N+1)
        revidx = Signal(N)
        m.d.comb += revidx.eq(Cat([idx.bit_select(i,1) for i in reversed(range(N))]))

        # FFT
        widx = Signal(N)
        stage = Signal(range(N+1))
        mask = Signal(signed(N))

        a = Signal(CQ(bshape))
        b = Signal(CQ(bshape))

        # Coefficients
        m.d.comb += [
            widx.eq(idx & mask),
            W_rd.addr.eq(widx),
        ]

        # complex multiplication
        bw = Signal(CQ(bshape))
        m.d.comb += [
            bw.real.eq((b.real * W_rd.data.real) - (b.imag * W_rd.data.imag)),
            bw.imag.eq((b.real * W_rd.data.imag) + (b.imag * W_rd.data.real)),
        ]

        # butterfly
        s = Signal(CQ(bshape))
        d = Signal(CQ(bshape))
        m.d.comb += [
            s.real.eq(a.real + bw.real),
            s.imag.eq(a.imag + bw.imag),
            d.real.eq(a.real - bw.real),
            d.imag.eq(a.imag - bw.imag),
        ]

        # output and normalization based on ifft / stages
        rsh = 0 if self.ifft else N
        if N & 1:
            m.d.comb += self.o.payload.sample.real.eq(y_rd.data.real>>rsh)
            m.d.comb += self.o.payload.sample.imag.eq(y_rd.data.imag>>rsh)
        else:
            m.d.comb += self.o.payload.sample.real.eq(x_rd.data.real>>rsh)
            m.d.comb += self.o.payload.sample.imag.eq(x_rd.data.imag>>rsh)

        with m.If(N & 1):
            m.d.comb += y_rd.addr.eq(idx),
        with m.Else():
            m.d.comb += x_rd.addr.eq(idx),

        # Control FSM
        with m.FSM():
            with m.State("RESET"):
                m.d.sync += idx.eq(0)
                m.next = "LOAD1"

            with m.State("LOAD1"):
                m.d.sync += x_wr.en.eq(0)
                with m.If(idx >= self.pts):
                    m.d.sync += [
                        stage.eq(0),
                        idx.eq(0),
                        mask.eq(~((2 << (N-2))-1)),
                    ]
                    m.next = "FFTLOOP"
                with m.Else():
                    m.next = "LOAD2"

            with m.State("LOAD2"):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                    m.d.sync += [
                        x_wr.data.real.eq(self.i.payload.sample.real),
                        x_wr.data.imag.eq(self.i.payload.sample.imag),
                        x_wr.addr.eq(revidx),
                        x_wr.en.eq(1),
                        idx.eq(idx+1),
                    ]
                    m.next = "LOAD1"

            with m.State("FFTLOOP"):
                m.d.sync += [
                    x_wr.en.eq(0),
                    y_wr.en.eq(0),
                ]
                with m.If(idx >= self.pts):
                    m.d.sync += [
                        idx.eq(0),
                        mask.eq(mask>>1),
                        stage.eq(stage+1),
                    ]
                with m.If(stage >= N):
                    m.d.sync += idx.eq(0)
                    m.next = "OUTPUT"
                with m.Else():
                    m.next = "ADDRB"

            with m.State("ADDRB"):
                with m.If(stage & 1):
                    m.d.comb += y_rd.addr.eq(2*idx+1)
                with m.Else():
                    m.d.comb += x_rd.addr.eq(2*idx+1)
                m.next = "READB"

            with m.State("READB"):
                with m.If(stage & 1):
                    m.d.comb += y_rd.addr.eq(2*idx)
                    m.d.sync += [
                        b.real.eq(y_rd.data.real),
                        b.imag.eq(y_rd.data.imag),
                    ]
                with m.Else():
                    m.d.comb += x_rd.addr.eq(2*idx)
                    m.d.sync += [
                        b.real.eq(x_rd.data.real),
                        b.imag.eq(x_rd.data.imag),
                    ]
                m.next = "READA"

            with m.State("READA"):
                with m.If(stage & 1):
                    m.d.sync += [
                        a.real.eq(y_rd.data.real),
                        a.imag.eq(y_rd.data.imag),
                    ]
                with m.Else():
                    m.d.sync += [
                        a.real.eq(x_rd.data.real),
                        a.imag.eq(x_rd.data.imag),
                    ]
                m.next = "BUTTERFLY"

            with m.State("BUTTERFLY"):
                with m.If(stage & 1):
                    m.d.sync += [
                        x_wr.data.real.eq(s.real),
                        x_wr.data.imag.eq(s.imag),
                        x_wr.addr.eq(idx),
                    ]
                with m.Else():
                    m.d.sync += [
                        y_wr.data.real.eq(s.real),
                        y_wr.data.imag.eq(s.imag),
                        y_wr.addr.eq(idx),
                    ]
                m.next = "WRITESUM"

            with m.State("WRITESUM"):
                with m.If(stage & 1):
                    m.d.sync += [
                        x_wr.en.eq(1),
                    ]
                with m.Else():
                    m.d.sync += [
                        y_wr.en.eq(1),
                    ]
                m.next = "ADDRDIFF"

            with m.State("ADDRDIFF"):
                with m.If(stage & 1):
                    m.d.sync += [
                        x_wr.en.eq(0),
                        x_wr.data.eq(d),
                        x_wr.addr.eq(idx+(self.pts>>1)),
                    ]
                with m.Else():
                    m.d.sync += [
                        y_wr.en.eq(0),
                        y_wr.data.eq(d),
                        y_wr.addr.eq(idx+(self.pts>>1)),
                    ]
                m.next = "WRITEDIFF"

            with m.State("WRITEDIFF"):
                with m.If(stage & 1):
                    m.d.sync += [
                        x_wr.en.eq(1),
                    ]
                with m.Else():
                    m.d.sync += [
                        y_wr.en.eq(1),
                    ]
                m.d.sync += idx.eq(idx+1)
                m.next = "FFTLOOP"

            with m.State("OUTPUT"):
                with m.If(idx >= self.pts):
                    m.next = "RESET"
                with m.Else():
                    m.next = "READOUT"

            with m.State("READOUT"):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.d.sync += [
                        idx.eq(idx+1),
                    ]
                    m.next = "OUTPUT"

        return m
