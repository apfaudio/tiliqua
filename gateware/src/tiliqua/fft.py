# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Fixed-point FFT and utility components."""

from enum import Enum

from amaranth import *
from amaranth.lib import memory, wiring, data, stream, fifo
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from math import cos, sin, pi, sqrt

class CQ(data.StructLayout):
    """Complex number formed by a pair of fixed.SQ"""
    def __init__(self, shape: fixed.SQ):
        super().__init__({
            "real": shape,
            "imag": shape,
        })

class Block(data.StructLayout):
    """Block of samples, first of each has 'first' flag asserted."""
    def __init__(self, shape):
        super().__init__({
            "first": unsigned(1),
            "sample": shape
        })

def cq_real(s):
    """Stream adapter: take the 'real' component of a CQ stream."""
    a = stream.Signature(Block(s.payload.sample.real.shape()))
    if isinstance(s.signature, wiring.FlippedSignature):
        a = a.flip()
    o = a.create()
    o.payload.sample = s.payload.sample.real
    o.valid = s.valid
    o.ready = s.ready
    if hasattr(o.payload, 'first') or hasattr(s.payload, 'first'):
        o.payload.first = s.payload.first
    return o

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
                 shape:        fixed.SQ=fixed.SQ(1, 15),
                 sz:           int=1024,
                 default_ifft: bool=False) -> None:
        self.sz   = sz
        self.shape = shape
        super().__init__({
            "ifft": In(1, init=1 if default_ifft else 0),
            "i": In(stream.Signature(Block(CQ(self.shape)))),
            "o": Out(stream.Signature(Block(CQ(self.shape)))),
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

class Window(wiring.Component):

    """
    Apply a real window function of size ``sz`` to samples of
    ``CQ(shape)``. Uses a single multiplier. ``payload.first`` is
    used to synchronize the start of windowing.

    Note: this core takes and emits 'complex' samples ready for
    an FFT operation, however it currently zeroes `imag` and
    only windows the `real` component.
    """

    class Function(Enum):
        HANN      = lambda k, sz: 0.5 - 0.5*cos(k*2*pi/sz)
        SQRT_HANN = lambda k, sz: sqrt(0.5 - 0.5*cos(k*2*pi/sz))
        RECT      = lambda k, sz: 1.

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int,
                 # Default: sqrt(Hann) window for STFT
                 window_function = Function.SQRT_HANN) -> None:
        self.sz   = sz
        self.shape = shape
        self.window_function = window_function
        super().__init__({
            "i": In(stream.Signature(Block(self.shape))),
            "o": Out(stream.Signature(Block(self.shape))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        wFr = [self.window_function(k, self.sz) for k in range(self.sz)]

        wshape = fixed.SQ(self.shape.i_bits+1, self.shape.f_bits)
        m.submodules.wFr = wFr = memory.Memory(
                shape=wshape, depth=self.sz, init=wFr)

        wFr_rd = wFr.read_port()

        i_latch = Signal.like(self.i.payload.sample)
        wfidx = Signal(range(self.sz+1))
        m.d.comb += wFr_rd.addr.eq(wfidx)
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
                m.d.sync += self.o.payload.sample.eq(wFr_rd.data*i_latch),
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


class ComputeOverlappingBlocks(wiring.Component):

    def __init__(self,
                 shape:     fixed.SQ,
                 sz:        int,
                 n_overlap: int):

        self.sz        = sz
        self.shape     = shape
        self.n_overlap = n_overlap

        super().__init__({
            "i": In(stream.Signature(self.shape)),
            "o": Out(stream.Signature(Block(self.shape))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.overlap_fifo = overlap_fifo = fifo.SyncFIFOBuffered(
            width=self.shape.as_shape().width, depth=self.n_overlap)

        n_samples = Signal(range(self.sz), init=0)
        with m.If(self.i.valid & self.i.ready):
            m.d.sync += n_samples.eq(n_samples+1)

        m.d.comb += [
            self.o.payload.sample.eq(self.i.payload),
            self.o.payload.first.eq(
                overlap_fifo.r_level == self.n_overlap),
            overlap_fifo.w_data.eq(self.i.payload),
            self.o.valid.eq(self.i.valid),
            self.i.ready.eq(self.o.ready),
        ]

        with m.FSM():
            with m.State("START"):
                m.d.comb += self.o.payload.first.eq(1)
                with m.If(n_samples == (self.sz - self.n_overlap)):
                    m.next = "FILL"
            with m.State("FILL"):
                with m.If(overlap_fifo.r_level == self.n_overlap):
                    m.d.comb += [
                        self.i.ready.eq(0),
                        self.o.valid.eq(0),
                    ]
                    m.next = "DRAIN"
                with m.Else():
                    m.d.comb += overlap_fifo.w_en.eq(self.i.valid & self.i.ready)
            with m.State("DRAIN"):
                with m.If(overlap_fifo.r_level != 0):
                    m.d.comb += [
                        self.i.ready.eq(0),
                        self.o.valid.eq(1),
                        self.o.payload.sample.eq(overlap_fifo.r_data),
                        overlap_fifo.r_en.eq(self.o.ready),
                    ]
                with m.Else():
                    m.next = "FILL"

        return m

class OverlapAddBlocks(wiring.Component):

    def __init__(self,
                 shape:     fixed.SQ,
                 sz:        int,
                 n_overlap: int):

        self.sz        = sz
        self.shape     = shape
        self.n_overlap = n_overlap

        super().__init__({
            "i": In(stream.Signature(Block(self.shape))),
            "o": Out(stream.Signature(self.shape))
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.fifo1 = fifo1 = fifo.SyncFIFOBuffered(
            width=self.shape.as_shape().width, depth=self.sz)
        m.submodules.fifo2 = fifo2 = fifo.SyncFIFOBuffered(
            width=self.shape.as_shape().width, depth=self.sz)

        swap_fifos = Signal()
        m.d.comb += [
            swap_fifos.eq(
                self.i.valid & self.i.ready & self.i.payload.first),
            fifo1.w_data.eq(self.i.payload.sample),
            fifo2.w_data.eq(self.i.payload.sample),
        ]

        with m.FSM():
            with m.State("PRE-FILL"):
                with m.If(fifo2.w_level != self.n_overlap):
                    m.d.comb += [
                        fifo2.w_en.eq(1),
                        fifo2.w_data.eq(0),
                    ]
                with m.Else():
                    m.d.comb += self.i.ready.eq(1)
                    with m.If(swap_fifos):
                        m.d.comb += fifo1.w_en.eq(1)
                        m.next = "FIFO1"
            with m.State("FIFO1"):
                m.d.comb += [
                    self.i.ready.eq(fifo1.w_rdy),
                    fifo1.w_en.eq(self.i.valid & ~self.i.payload.first),
                ]
                with m.If(swap_fifos):
                    m.d.comb += fifo2.w_en.eq(1)
                    m.next = "FIFO2"
            with m.State("FIFO2"):
                m.d.comb += [
                    self.i.ready.eq(fifo2.w_rdy),
                    fifo2.w_en.eq(self.i.valid & ~self.i.payload.first),
                ]
                with m.If(swap_fifos):
                    m.d.comb += fifo1.w_en.eq(1)
                    m.next = "FIFO1"

        out_a = Signal(self.shape)
        out_b = Signal(self.shape)
        m.d.comb += [
            self.o.valid.eq(fifo1.r_rdy & fifo2.r_rdy),
            out_a.eq(fifo1.r_data),
            out_b.eq(fifo2.r_data),
            self.o.payload.eq(out_a + out_b),
            fifo1.r_en.eq(self.o.valid & self.o.ready),
            fifo2.r_en.eq(self.o.valid & self.o.ready),
        ]

        return m

class STFTAnalyzer(wiring.Component):

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int):

        self.sz        = sz
        self.shape     = shape

        self.overlap_blocks   = ComputeOverlappingBlocks(sz=sz, shape=shape, n_overlap=sz//2)
        self.window_analysis  = Window(sz=sz, shape=shape, window_function=Window.Function.HANN)
        self.fft              = FFT(sz=sz, shape=shape)

        super().__init__({
            "i": In(stream.Signature(self.shape)),
            "o": Out(stream.Signature(Block(CQ(self.shape)))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.overlap_blocks   = self.overlap_blocks
        m.submodules.window_analysis  = self.window_analysis
        m.submodules.fft              = self.fft

        # Continuous time-domain input -> windowed overlapping frequency domain blocks
        wiring.connect(m, wiring.flipped(self.i), self.overlap_blocks.i)
        wiring.connect(m, self.overlap_blocks.o, self.window_analysis.i)
        wiring.connect(m, self.window_analysis.o, cq_real(self.fft.i))
        wiring.connect(m, self.fft.o, wiring.flipped(self.o))

        return m

class STFTSynthesizer(wiring.Component):

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int):

        self.sz        = sz
        self.shape     = shape

        self.ifft             = FFT(sz=sz, shape=shape, default_ifft=True)
        self.window_synthesis = Window(sz=sz, shape=shape)
        self.overlap_add      = OverlapAddBlocks(sz=sz, shape=shape, n_overlap=sz//2)

        super().__init__({
            "i": In(stream.Signature(Block(CQ(self.shape)))),
            "o": Out(stream.Signature(self.shape)),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.ifft             = self.ifft
        m.submodules.window_synthesis = self.window_synthesis
        m.submodules.overlap_add      = self.overlap_add

        # Processed frequency-domain blocks -> continuous time-domain output (using overlap-add)
        wiring.connect(m, wiring.flipped(self.i), self.ifft.i)
        wiring.connect(m, cq_real(self.ifft.o), self.window_synthesis.i)
        wiring.connect(m, self.window_synthesis.o, self.overlap_add.i)
        wiring.connect(m, self.overlap_add.o, wiring.flipped(self.o))

        return m

class STFTProcessorPipelined(wiring.Component):

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int):

        self.sz        = sz
        self.shape     = shape

        self.analyzer    = STFTAnalyzer(shape=shape, sz=sz)
        self.synthesizer = STFTSynthesizer(shape=shape, sz=sz)

        super().__init__({
            # Time domain input and resynthesized output
            "i": In(stream.Signature(self.shape)),
            "o": Out(stream.Signature(self.shape)),
            # Frequency domain analysis and resynthesis blocks, to be hooked
            # up to user frequency-domain block processing logic. If `o_freq`
            # is connected straight to `i_freq` the output will simply
            # resynthesize the input unmodified.
            "o_freq": Out(stream.Signature(Block(CQ(self.shape)))),
            "i_freq": In(stream.Signature(Block(CQ(self.shape)))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.analyzer = self.analyzer
        m.submodules.synthesizer = self.synthesizer

        wiring.connect(m, wiring.flipped(self.i), self.analyzer.i)
        wiring.connect(m, self.analyzer.o, wiring.flipped(self.o_freq))

        # Processed frequency-domain blocks -> continuous time-domain output (using overlap-add)
        wiring.connect(m, wiring.flipped(self.i_freq), self.synthesizer.i)
        wiring.connect(m, self.synthesizer.o, wiring.flipped(self.o))

        return m

class STFTProcessorSmall(wiring.Component):

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int):

        self.sz        = sz
        self.shape     = shape

        self.overlap_blocks = ComputeOverlappingBlocks(sz=sz, shape=shape, n_overlap=sz//2)
        self.window         = Window(sz=sz, shape=shape, window_function=Window.Function.SQRT_HANN)
        self.fft            = FFT(sz=sz, shape=shape)
        self.overlap_add    = OverlapAddBlocks(sz=sz, shape=shape, n_overlap=sz//2)

        super().__init__({
            # Time domain input and resynthesized output
            "i": In(stream.Signature(self.shape)),
            "o": Out(stream.Signature(self.shape)),
            # Frequency domain analysis and resynthesis blocks, to be hooked
            # up to user frequency-domain block processing logic. If `o_freq`
            # is connected straight to `i_freq` the output will simply
            # resynthesize the input unmodified.
            "o_freq": Out(stream.Signature(Block(CQ(self.shape)))),
            "i_freq": In(stream.Signature(Block(CQ(self.shape)))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.overlap_blocks   = self.overlap_blocks
        m.submodules.window           = self.window
        m.submodules.fft              = self.fft
        m.submodules.overlap_add      = self.overlap_add

        m.submodules.pfifo = pfifo = fifo.SyncFIFOBuffered(
            width=self.i_freq.payload.shape().size, depth=self.sz)

        wiring.connect(m, wiring.flipped(self.i), self.overlap_blocks.i)
        wiring.connect(m, self.overlap_add.o, wiring.flipped(self.o))

        n_samples = Signal(range(self.sz+1), init=0)

        with m.FSM():
            with m.State("LOAD"):
                m.d.comb += self.fft.ifft.eq(0)
                wiring.connect(m, self.overlap_blocks.o, self.window.i)
                wiring.connect(m, self.window.o, cq_real(self.fft.i))
                with m.If(self.overlap_blocks.o.valid & self.overlap_blocks.o.ready):
                    m.d.sync += n_samples.eq(n_samples+1)
                with m.If(n_samples == self.sz):
                    m.next = "ANALYZE"
            with m.State("ANALYZE"):
                wiring.connect(m, self.window.o, cq_real(self.fft.i))
                wiring.connect(m, self.fft.o, wiring.flipped(self.o_freq))
                wiring.connect(m, wiring.flipped(self.i_freq), pfifo.w_stream)
                with m.If(pfifo.w_level == self.sz):
                    m.next = "SYNTHESIZE"
            with m.State("SYNTHESIZE"):
                m.d.comb += self.fft.ifft.eq(1)
                wiring.connect(m, pfifo.r_stream, self.fft.i)
                wiring.connect(m, cq_real(self.fft.o), self.window.i)
                wiring.connect(m, self.window.o, self.overlap_add.i)
                with m.If(self.window.o.valid & self.window.o.ready):
                    m.d.sync += n_samples.eq(n_samples-1)
                with m.If(n_samples == 0):
                    m.next = "LOAD"

        return m
