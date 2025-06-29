#!/usr/bin/env python3
#
# from 'https://github.com/amaranth-farm/amlib/blob/main/amlib/dsp/fixedpointfft.py'
# with some modifications to work in this repository.
#
# Copyright (c) 2022-2023 Kaz Kojima <kkojima@rr.iij4u.or.jp>
#
# SPDX-License-Identifier: CERN-OHL-W-2.0

from amaranth import *
from amaranth.lib import memory, wiring
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import cos, sin, pi

class FixedPointFFT(wiring.Component):

    def __init__(self,
                 shape: fixed.Shape=fixed.SQ(1, 17),
                 pts:   int=1024,
                 ifft = False) -> None:

        self.ifft     = ifft
        self.shape    = shape
        self.wshape   = fixed.SQ(self.shape.i_bits+1, self.shape.f_bits)
        self.pts      = pts
        self.stages   = exact_log2(pts)

        self.Wr = [cos(k*2*pi/pts) for k in range(pts)]
        if self.ifft:
            self.Wi = [sin(k*2*pi/pts) for k in range(pts)]
        else:
            self.Wi = [-sin(k*2*pi/pts) for k in range(pts)]

        super().__init__({
            "start":      In(1),
            "done":       Out(1, init=1),

            "in_i":       In(self.shape),
            "in_q":       In(self.shape),
            "out_real":   Out(self.shape),
            "out_imag":   Out(self.shape),

            "strobe_in":  In(1),
            "strobe_out": Out(1),

            "wf_start": In(1),
            "wf_strobe": In(1),
            "wf_real": In(self.wshape),
            "wf_imag": In(self.wshape),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        bshape = fixed.SQ(self.shape.i_bits + self.stages, self.shape.f_bits-1)
        m.submodules.xr = xr = memory.Memory(shape=bshape, depth=self.pts, init=[])
        m.submodules.xi = xi = memory.Memory(shape=bshape, depth=self.pts, init=[])
        m.submodules.yr = yr = memory.Memory(shape=bshape, depth=self.pts, init=[])
        m.submodules.yi = yi = memory.Memory(shape=bshape, depth=self.pts, init=[])

        m.submodules.Wr = Wr = memory.Memory(
                shape=self.wshape, depth=self.pts, init=self.Wr)
        m.submodules.Wi = Wi = memory.Memory(
                shape=self.wshape, depth=self.pts, init=self.Wi)

        xr_rd = xr.read_port()
        xr_wr = xr.write_port()
        xi_rd = xi.read_port()
        xi_wr = xi.write_port()
        yr_rd = yr.read_port()
        yr_wr = yr.write_port()
        yi_rd = yi.read_port()
        yi_wr = yi.write_port()

        Wr_rd = Wr.read_port()
        Wi_rd = Wi.read_port()

        N = self.stages
        idx = Signal(N+1)
        revidx = Signal(N)
        m.d.comb += revidx.eq(Cat([idx.bit_select(i,1) for i in reversed(range(N))]))

        # FFT
        widx = Signal(N)
        stage = Signal(range(N+1))
        mask = Signal(signed(N))

        ar = Signal(bshape)
        ai = Signal(bshape)
        br = Signal(bshape)
        bi = Signal(bshape)

        # Coefficients
        m.d.comb += [
            widx.eq(idx & mask),
            Wr_rd.addr.eq(widx),
            Wi_rd.addr.eq(widx),
        ]

        # complex multiplication
        bwr = Signal(bshape)
        bwi = Signal(bshape)
        m.d.comb += [
            bwr.eq((br * Wr_rd.data) - (bi * Wi_rd.data)),
            bwi.eq((br * Wi_rd.data) + (bi * Wr_rd.data)),
        ]

        # butterfly
        si = Signal(bshape)
        sr = Signal(bshape)
        di = Signal(bshape)
        dr = Signal(bshape)
        m.d.comb += [
            sr.eq(ar + bwr),
            si.eq(ai + bwi),
            dr.eq(ar - bwr),
            di.eq(ai - bwi),
        ]

        # Control FSM
        with m.FSM(init="IDLE"):
            with m.State("IDLE"):
                with m.If(self.start):
                    m.d.sync += [
                        self.done.eq(0),
                        idx.eq(0),
                    ]
                    m.next = "LOAD1"

            with m.State("LOAD1"):
                m.d.sync += xr_wr.en.eq(0)
                m.d.sync += xi_wr.en.eq(0)
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
                with m.If(self.strobe_in):
                    m.d.sync += [
                        xr_wr.data.eq(self.in_i),
                        xi_wr.data.eq(self.in_q),
                        xr_wr.addr.eq(revidx),
                        xi_wr.addr.eq(revidx),
                        xr_wr.en.eq(1),
                        xi_wr.en.eq(1),
                        idx.eq(idx+1),
                    ]
                    m.next = "LOAD1"

            with m.State("FFTLOOP"):
                m.d.sync += [
                    xr_wr.en.eq(0),
                    xi_wr.en.eq(0),
                    yr_wr.en.eq(0),
                    yi_wr.en.eq(0),
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
                    m.d.sync += [
                        yr_rd.addr.eq(2*idx+1),
                        yi_rd.addr.eq(2*idx+1),
                    ]
                with m.Else():
                    m.d.sync += [
                        xr_rd.addr.eq(2*idx+1),
                        xi_rd.addr.eq(2*idx+1),
                    ]
                m.next = "ADDRB_LATCHED"

            with m.State("ADDRB_LATCHED"):
                m.next = "READB"

            with m.State("READB"):
                with m.If(stage & 1):
                    m.d.sync += [
                        br.eq(yr_rd.data),
                        bi.eq(yi_rd.data),
                    ]
                with m.Else():
                    m.d.sync += [
                        br.eq(xr_rd.data),
                        bi.eq(xi_rd.data),
                    ]
                m.next = "ADDRA"

            with m.State("ADDRA"):
                with m.If(stage & 1):
                    m.d.sync += [
                        yr_rd.addr.eq(2*idx),
                        yi_rd.addr.eq(2*idx),
                    ]
                with m.Else():
                    m.d.sync += [
                        xr_rd.addr.eq(2*idx),
                        xi_rd.addr.eq(2*idx),
                    ]
                m.next = "ADDRA_LATCHED"

            with m.State("ADDRA_LATCHED"):
                m.next = "READA"

            with m.State("READA"):
                with m.If(stage & 1):
                    m.d.sync += [
                        ar.eq(yr_rd.data),
                        ai.eq(yi_rd.data),
                    ]
                with m.Else():
                    m.d.sync += [
                        ar.eq(xr_rd.data),
                        ai.eq(xi_rd.data),
                    ]
                m.next = "BUTTERFLY"

            with m.State("BUTTERFLY"):
                with m.If(stage & 1):
                    m.d.sync += [
                        xr_wr.data.eq(sr),
                        xi_wr.data.eq(si),
                        xr_wr.addr.eq(idx),
                        xi_wr.addr.eq(idx),
                    ]
                with m.Else():
                    m.d.sync += [
                        yr_wr.data.eq(sr),
                        yi_wr.data.eq(si),
                        yr_wr.addr.eq(idx),
                        yi_wr.addr.eq(idx),
                    ]
                m.next = "WRITESUM"

            with m.State("WRITESUM"):
                with m.If(stage & 1):
                    m.d.sync += [
                        xr_wr.en.eq(1),
                        xi_wr.en.eq(1),
                    ]
                with m.Else():
                    m.d.sync += [
                        yr_wr.en.eq(1),
                        yi_wr.en.eq(1),
                    ]
                m.next = "ADDRDIFF"

            with m.State("ADDRDIFF"):
                with m.If(stage & 1):
                    m.d.sync += [
                        xr_wr.en.eq(0),
                        xi_wr.en.eq(0),
                        xr_wr.data.eq(dr),
                        xi_wr.data.eq(di),
                        xr_wr.addr.eq(idx+(self.pts>>1)),
                        xi_wr.addr.eq(idx+(self.pts>>1)),
                    ]
                with m.Else():
                    m.d.sync += [
                        yr_wr.en.eq(0),
                        yi_wr.en.eq(0),
                        yr_wr.data.eq(dr),
                        yi_wr.data.eq(di),
                        yr_wr.addr.eq(idx+(self.pts>>1)),
                        yi_wr.addr.eq(idx+(self.pts>>1)),
                    ]
                m.next = "WRITEDIFF"

            with m.State("WRITEDIFF"):
                with m.If(stage & 1):
                    m.d.sync += [
                        xr_wr.en.eq(1),
                        xi_wr.en.eq(1),
                    ]
                with m.Else():
                    m.d.sync += [
                        yr_wr.en.eq(1),
                        yi_wr.en.eq(1),
                    ]
                m.d.sync += idx.eq(idx+1)
                m.next = "FFTLOOP"

            with m.State("OUTPUT"):
                m.d.sync += self.strobe_out.eq(0)
                with m.If(idx >= self.pts):
                    m.next = "DONE"
                with m.Else():
                    with m.If(N & 1):
                        m.d.sync += [
                            yr_rd.addr.eq(idx),
                            yi_rd.addr.eq(idx),
                        ]
                    with m.Else():
                        m.d.sync += [
                            xr_rd.addr.eq(idx),
                            xi_rd.addr.eq(idx),
                        ]
                    m.next = "READOUT"

            with m.State("READOUT"):
                if self.ifft:
                    with m.If(N & 1):
                        m.d.sync += [
                            self.out_real.eq(yr_rd.data),
                            self.out_imag.eq(yi_rd.data),
                        ]
                    with m.Else():
                        m.d.sync += [
                            self.out_real.eq(xr_rd.data),
                            self.out_imag.eq(xi_rd.data),
                        ]
                else:
                    with m.If(N & 1):
                        m.d.sync += [
                            self.out_real.eq(yr_rd.data>>N),
                            self.out_imag.eq(yi_rd.data>>N),
                        ]
                    with m.Else():
                        m.d.sync += [
                            self.out_real.eq(xr_rd.data>>N),
                            self.out_imag.eq(xi_rd.data>>N),
                        ]
                m.d.sync += [
                    idx.eq(idx+1),
                    self.strobe_out.eq(1),
                ]
                m.next = "OUTPUT"

            with m.State("DONE"):
                m.d.sync += self.done.eq(1)
                m.next = "IDLE"

        return m
