# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Fixed-point FFT and utility components."""

from amaranth import *
from amaranth.lib import memory, wiring, data, stream
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import cos, sin, pi

class CQ(data.StructLayout):
    """Complex number formed by a pair of fixed.SQ"""
    def __init__(self, shape: fixed.SQ):
        super().__init__({
            "real": shape,
            "imag": shape,
        })

class FFT(wiring.Component):

    """Fixed-point forward or inverse Fast Fourier Transform.

    This processes blocks of fixed-point numbers of shape ``shape`` in
    blocks of size ``sz``. Outputs are available / clocked out ``sz*log2(sz)*6``
    clocks after all the inputs have been clocked in.

    When the core is idle, the ``ifft`` signal may be set to 1 to put the core
    into 'inverse FFT' mode. Otherwise, it is in 'forward FFT' mode. This FFT
    core normalizes the forward pass by 1/N. This matches the behaviour
    of ``scipy.fft(norm="forward")``. In 'inverse FFT' mode, there is no
    normalization and the twiddle factors are conjugated as necessary.

    There are many tradeoffs an FFT implementation can make. This one aims
    for low area and DSP tile usage. It is an iterative implementation that
    only performs 2 multiplies at a time. The core FFT loop takes 6 cycles,
    where 2 of these are arithmetic and the rest are memory operations.
    The algorithm implemented here is Radix-2, Cooley-Tukey.
    """

    def __init__(self,
                 shape: fixed.Shape=fixed.SQ(1, 15),
                 sz:    int=1024) -> None:
        self.sz   = sz
        self.shape = shape
        super().__init__({
            "ifft": In(1, init=0),
            "i": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            }))),
            "o": Out(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            })))
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # number of stages in FFT
        n_stages = exact_log2(self.sz)
        # butterfly / accumulator shape
        bshape = fixed.SQ(self.shape.i_bits + n_stages, self.shape.f_bits)
        # twiddle factor / window shape
        wshape = fixed.SQ(self.shape.i_bits+1, self.shape.f_bits)

        # Complex ping-pong RAM for FFT stages (input, processing and output)
        m.submodules.x = x = memory.Memory(shape=CQ(bshape), depth=self.sz, init=[])
        m.submodules.y = y = memory.Memory(shape=CQ(bshape), depth=self.sz, init=[])
        x_rd = x.read_port()
        x_wr = x.write_port()
        y_rd = y.read_port()
        y_wr = y.write_port()

        # complex ROM for FFT twiddle factors
        twiddle = [
            {'real': cos(k*2*pi/self.sz),
             'imag': sin(k*2*pi/self.sz)}
            for k in range(self.sz)
        ]
        m.submodules.W = W = memory.Memory(
                shape=CQ(wshape), depth=self.sz, init=twiddle)
        W_rd = W.read_port()

        # FFT addressing
        idx = Signal(n_stages+1)
        revidx = Signal(n_stages)
        stage = Signal(range(n_stages+1))
        m.d.comb += revidx.eq(Cat([idx.bit_select(i,1) for i in reversed(range(n_stages))]))

        # Twiddle factor addressing
        widx = Signal(n_stages)
        mask = Signal(signed(n_stages))
        m.d.comb += [
            widx.eq(idx & mask),
            W_rd.addr.eq(widx),
        ]

        # Complex multiplication by twiddle factors requires 4
        # multiplies. Instead we supply 2 multipliers wired up
        # to the current twiddle factor real/imag components, so a mux
        # is only needed on one side of the DSP tile inputs.
        bw = Signal(CQ(bshape))
        W_rd_l = Signal(CQ(wshape))
        mW_rd_r_a = Signal(bshape)
        mW_rd_r_z = Signal(bshape)
        m.d.comb += mW_rd_r_z.eq(mW_rd_r_a * W_rd_l.real)
        mW_rd_i_a = Signal(bshape)
        mW_rd_i_z = Signal(bshape)
        m.d.comb += mW_rd_i_z.eq(mW_rd_i_a * W_rd_l.imag)

        # Butterfly sum and difference calculation based on
        # result of twiddle factor multiplication.
        a = Signal(CQ(bshape))
        b = Signal(CQ(bshape))
        s = Signal(CQ(bshape))
        d = Signal(CQ(bshape))
        m.d.comb += [
            s.real.eq(a.real + bw.real),
            s.imag.eq(a.imag + bw.imag),
            d.real.eq(a.real - bw.real),
            d.imag.eq(a.imag - bw.imag),
        ]

        # Output and normalization based on ifft / n_stages
        if n_stages & 1:
            m.d.comb += self.o.payload.sample.real.eq(y_rd.data.real>>Mux(self.ifft, 0, n_stages))
            m.d.comb += self.o.payload.sample.imag.eq(y_rd.data.imag>>Mux(self.ifft, 0, n_stages))
        else:
            m.d.comb += self.o.payload.sample.real.eq(x_rd.data.real>>Mux(self.ifft, 0, n_stages))
            m.d.comb += self.o.payload.sample.imag.eq(x_rd.data.imag>>Mux(self.ifft, 0, n_stages))

        # Default RAM addressing and write enable
        m.d.comb += [
            y_rd.addr.eq(idx),
            x_rd.addr.eq(idx),
        ]
        m.d.sync += [
            x_wr.en.eq(0),
            y_wr.en.eq(0),
        ]

        # Control FSM
        with m.FSM():
            with m.State("RESET"):
                m.d.sync += idx.eq(0)
                m.d.sync += self.o.payload.first.eq(1)
                m.next = "LOAD1"

            with m.State("LOAD1"):
                with m.If(idx >= self.sz):
                    m.d.sync += [
                        stage.eq(0),
                        idx.eq(0),
                        mask.eq(~((2 << (n_stages-2))-1)),
                    ]
                    m.next = "FFTLOOP"
                with m.Else():
                    m.next = "LOAD2"

            with m.State("LOAD2"):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid & ((idx > 0) | self.i.payload.first)):
                    m.d.sync += [
                        x_wr.data.real.eq(self.i.payload.sample.real),
                        x_wr.data.imag.eq(self.i.payload.sample.imag),
                        x_wr.addr.eq(revidx),
                        x_wr.en.eq(1),
                        idx.eq(idx+1),
                    ]
                    m.next = "LOAD1"

            with m.State("FFTLOOP"):
                # Don't write anything to RAM until necessary.
                with m.If(idx >= self.sz):
                    # This stage is complete. Move to next stage.
                    m.d.sync += [
                        idx.eq(0),
                        mask.eq(mask>>1),
                        stage.eq(stage+1),
                    ]
                with m.If(stage >= n_stages):
                    # FFT calculation is complete. Output result.
                    m.d.sync += idx.eq(0)
                    m.next = "OUTPUT"
                with m.Else():
                    # This stage requires more processing. Set up
                    # a read for 'B' from RAM.
                    m.d.comb += y_rd.addr.eq(2*idx+1)
                    m.d.comb += x_rd.addr.eq(2*idx+1)
                    m.next = "READB"

            with m.State("READB"):
                # Read out 'B' from RAM, latch it to the complex multiplier
                # inputs, and simultaneously set up a read for 'A' from RAM.
                m.d.comb += y_rd.addr.eq(2*idx)
                m.d.comb += x_rd.addr.eq(2*idx)
                with m.If(stage & 1):
                    m.d.sync += [
                        b.real.eq(y_rd.data.real),
                        b.imag.eq(y_rd.data.imag),
                        mW_rd_r_a.eq(y_rd.data.real),
                        mW_rd_i_a.eq(y_rd.data.real),
                    ]
                with m.Else():
                    m.d.sync += [
                        b.real.eq(x_rd.data.real),
                        b.imag.eq(x_rd.data.imag),
                        mW_rd_r_a.eq(x_rd.data.real),
                        mW_rd_i_a.eq(x_rd.data.real),
                    ]
                # Latch current twiddle factors from memory to cut timing.
                with m.If(self.ifft):
                    # conjugate twiddle factors on inverse fft.
                    m.d.sync += W_rd_l.real.eq(W_rd.data.real)
                    m.d.sync += W_rd_l.imag.eq(W_rd.data.imag)
                with m.Else():
                    m.d.sync += W_rd_l.real.eq(W_rd.data.real)
                    m.d.sync += W_rd_l.imag.eq(-W_rd.data.imag)
                m.next = "READA-BUTTERFLY0"

            with m.State("READA-BUTTERFLY0"):
                # Read out 'A' from RAM, latch it to the butterfly inputs.
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
                # Latch first 2 multiplies into 'bw' and set up the next 2
                # multiplies (4 needed for the overall complex multiply).
                m.d.sync += mW_rd_i_a.eq(b.imag)
                m.d.sync += mW_rd_r_a.eq(b.imag)
                m.d.sync += bw.real.eq(mW_rd_r_z)
                m.d.sync += bw.imag.eq(mW_rd_i_z)
                m.next = "BUTTERFLY1"

            with m.State("BUTTERFLY1"):
                # Accumulate second 2 multiplies into 'bw'.
                m.d.sync += bw.real.eq(bw.real - mW_rd_i_z)
                m.d.sync += bw.imag.eq(bw.imag + mW_rd_r_z)
                m.next = "WRITE-S"

            with m.State("WRITE-S"):
                # Set up a write to RAM of the butterfly sum term.
                with m.If(stage & 1):
                    m.d.sync += [
                        x_wr.en.eq(1),
                        x_wr.data.real.eq(s.real),
                        x_wr.data.imag.eq(s.imag),
                        x_wr.addr.eq(idx),
                    ]
                with m.Else():
                    m.d.sync += [
                        y_wr.en.eq(1),
                        y_wr.data.real.eq(s.real),
                        y_wr.data.imag.eq(s.imag),
                        y_wr.addr.eq(idx),
                    ]
                m.next = "WRITE-D"

            with m.State("WRITE-D"):
                # Set up a write to RAM of the butterfly diff term.
                with m.If(stage & 1):
                    m.d.sync += [
                        x_wr.en.eq(1),
                        x_wr.data.real.eq(d.real),
                        x_wr.data.imag.eq(d.imag),
                        x_wr.addr.eq(idx+(self.sz>>1)),
                    ]
                with m.Else():
                    m.d.sync += [
                        y_wr.en.eq(1),
                        y_wr.data.real.eq(d.real),
                        y_wr.data.imag.eq(d.imag),
                        y_wr.addr.eq(idx+(self.sz>>1)),
                    ]
                m.d.sync += idx.eq(idx+1)
                m.next = "FFTLOOP"

            with m.State("OUTPUT"):
                with m.If(idx >= self.sz):
                    m.next = "RESET"
                with m.Else():
                    m.next = "READOUT"

            with m.State("READOUT"):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.d.sync += [
                        idx.eq(idx+1),
                        self.o.payload.first.eq(0),
                    ]
                    m.next = "OUTPUT"

        return m

class RealWindow(wiring.Component):
    def __init__(self,
                 shape: fixed.Shape,
                 sz:    int) -> None:
        self.sz   = sz
        self.shape = shape
        super().__init__({
            "i": In(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": self.shape
            }))),
            "o": Out(stream.Signature(data.StructLayout({
                "first": unsigned(1),
                "sample": CQ(self.shape)
            })))
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # 4-term Blackman-Harris window
        wFr = [0.35875-0.48829*cos(k*2*pi/self.sz)
               +0.14128*cos(k*4*pi/self.sz)
               -0.01168*cos(k*6*pi/self.sz)
               for k in range(self.sz)]

        wshape = fixed.SQ(self.shape.i_bits+1, self.shape.f_bits)
        m.submodules.wFr = wFr = memory.Memory(
                shape=wshape, depth=self.sz, init=wFr)

        wFr_rd = wFr.read_port()

        i_latch = Signal.like(self.i.payload.sample)
        wfidx = Signal(range(self.sz+1))
        m.d.comb += wFr_rd.addr.eq(wfidx)
        m.d.comb += self.o.payload.sample.imag.eq(0)
        with m.FSM():
            with m.State("RESET"):
                m.d.sync += wfidx.eq(0)
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid & self.i.payload.first):
                    m.d.sync += i_latch.eq(self.i.payload.sample)
                    m.d.sync += self.o.payload.first.eq(1)
                    m.next = "WINDOW"
            with m.State("NEXT"):
                m.d.comb += self.i.ready.eq(1)
                m.d.sync += self.o.payload.first.eq(0)
                with m.If(self.i.valid):
                    m.d.sync += i_latch.eq(self.i.payload.sample)
                    m.next = "WINDOW"
            with m.State("WINDOW"):
                m.d.sync += self.o.payload.sample.real.eq(
                        wFr_rd.data*self.i.payload.sample),
                m.next = "OUT"
            with m.State("OUT"):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    with m.If(wfidx != (self.sz - 1)):
                        m.d.sync += wfidx.eq(wfidx+1)
                        m.next = "NEXT"
                    with m.Else():
                        m.next = "RESET"
        return m

