# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Utilities for frequency-domain analysis and synthesis."""

from enum import Enum

from amaranth import *
from amaranth.lib import memory, wiring, data, stream, fifo
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2

from amaranth_future import fixed

from tiliqua.complex import CQ, connect_sq_to_real, connect_real_to_sq
from tiliqua.block   import Block

from math import cos, sin, pi, sqrt

class FFT(wiring.Component):

    """Fixed-point Fast Fourier Transform.

    Overview
    --------

    This core computes the DFT of complex, fixed-point samples (specifically,
    power-of-two chunks, represented by :class:`Block` of :class:`CQ`). It can be run
    in 'forward' or 'inverse' mode, and is generally designed to match the behaviour
    of ``scipy.fft(norm="forward")``.

    Input and output samples are clocked in FIFO order. Block processing only begins
    once ``sz`` elements (an entire block) has been clocked at ``self.i``. Some time
    later, the core clocks the transformed block out ``self.o``, before clocking in
    the next block. See the 'Design' section for further details on throughput.

    Switching modes
    ---------------

    When the core is idle (nothing is clocked into the core and ``i.ready`` is strobed),
    the ``ifft`` signal may be set to 1 to put the core into 'inverse FFT' mode.
    Otherwise, it is in 'forward FFT' mode.

        - In forward mode, this FFT core normalizes the outputs by 1/N, and the
          twiddle factors are not conjugated.
        - In 'inverse FFT' mode, there is no normalization, and the twiddle factors
          are conjugated as required.

    Design
    ------

    There are many tradeoffs an FFT implementation can make. This one aims
    for low area and DSP tile usage. It is an iterative implementation that
    only performs 2 multiplies at a time. The core FFT loop takes 6 cycles,
    where 2 of these are arithmetic and the rest are memory operations.
    The algorithm implemented here is 'Cooley-Tukey, Decimation-in-Time, Radix-2'.

    Latency, resource usage
    ^^^^^^^^^^^^^^^^^^^^^^^
    As this core only performs 2 multiplies at a time, it only requires 2 DSP tiles,
    assuming the ``shape`` specified is small enough. For 16-bit samples at an
    FFT size of 1024, the extra bits needed to account for overflow requires 4x
    18-bit multipliers on an ECP5.

    Outputs take ``sz*log2(sz)*6`` system clocks to be computed after all the
    inputs have been clocked in. That is, an FFT of size 1024 would take about
    ``log2(1024)*6 == 60`` system clocks per sample, for a maximum throughput around
    1Msample/sec if we had a 60MHz master clock (in reality a bit less accounting for
    the input and output clocking times).

    This core instantiates 3 memories, which all scale with ``sz``. A ROM for the
    twiddle factor (coefficient) memory, and 2 RAMs which are shared for input
    and output sample storage as well as intermediate calculations. An interesting
    addition to this core in the future may be to support external memory for huge
    FFT sizes.

    Internals
    ^^^^^^^^^

    .. note::

        Reading this is not necessary to use the core. I advise reading up a bit on how
        FFT algorithms work before diving deeper into this. It's just a few notes to anyone
        interested in understanding this core more deeply.

    This core has 3 main 'phases' in its overall state machine - an input phase (``LOAD1`` and
    ``LOAD2``), calculation/loop phases (``FFTLOOP`` to ``WRITE-D``) and an output phase
    (``READ-OUTPUT``).

    The loop phase has an inner counter ``idx``, for the index of the current sample compared
    to the total block size, and an outer counter ``stage`` which goes from 0 to ``log2(sz)``.
    Once ``stage`` reaches ``log2(sz)``, the calculations are complete. The input and output
    phases are simpler to understand, so we'll focus on this loop phase.

    On every loop iteration, we read all needed values from memory and calculate the butterfly
    sum/difference outputs. Muxes are shown to represent the A / B ping-ponging between
    which memory they fetch from in even and odd stages (Stage 0 ``X->A, Y->B``, Stage 1
    ``X->B, Y->A`` and so on up to Stage ``log2(sz)``).

    .. code-block:: text

        ┌─────────┐     ┌─────────┐     ┌─────────┐
        │  X RAM  │-\\ /-│  Y RAM  │     │  W ROM  │
        └────┬────┘  X  └────┬────┘     └────┬────┘
             ▼      / \\      ▼               │
            MUX<────   ────>MUX              │
             │               │               │
             A               B               │
             │               │               │
             │         ┌─────┴─────┐         │
             └────────>┤ Butterfly ├<────────┘
                       │  S=A+B×W  │
                       │  D=A-B×W  │
                       └─────┬─────┘
                             │S,D

    Once the calculation is complete, the S, D values are written back in a similar ping-pong
    way to either the X or Y RAMs, depending on which 'stage' we are in. There are 6 states
    inside the FFT loop required for each iteration of this calculation. Some of them do
    arithmetic and memory accesses in the same state - in general the timing of each state is
    optimized to hit around 80MHz on a slowest speed-grade ECP5.

    Members
    -------
    i : :py:`In(stream.Signature(Block(CQ(self.shape))))`
        Incoming stream of blocks of complex samples.
    o : :py:`Out(stream.Signature(Block(CQ(self.shape))))`
        Outgoing stream of blocks of complex samples.
    ifft : :py:`In(1, init=default_ifft)`
        ``0`` for forward FFT with ``1/N`` normalization. ``1`` for inverse FFT.
        May only be changed when the core is idle ('ready' and not midway through
        a block!).
    """

    def __init__(self,
                 shape:        fixed.SQ=fixed.SQ(1, 15),
                 sz:           int=1024,
                 default_ifft: bool=False) -> None:
        """
        shape : fixed.SQ
            Shape of the fixed-point types used for inputs and outputs. This is
            the shape of a single number, this core wraps it in :class:`Block`\\(:class:`CQ`\\(shape)).
        sz : int
            Size of the FFT/IFFT blocks. Must be a power of 2.
        default_ifft : bool
            Default state of the ``self.ifft`` signal, can be used to create an IFFT
            instead of an FFT by default, without needing to explicitly connect the signal.
        """
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

    """Pointwise window function.

    Apply a real window function of size ``sz`` to blocks of ``shape``.
    The window function is synchronized to the block ``payload.first``.

    Design
    ------

    This core is iterative and uses a single multiplier. It does not
    store any samples, the windowed samples are available at the output
    2 clocks after they are provided at the input.

    Members
    -------
    i : :py:`In(stream.Signature(Block(self.shape)))`
        Incoming stream of blocks of real samples.
        at intervals matching the ``sz`` of this component.
    o : :py:`Out(stream.Signature(Block(self.shape)))`
        Outgoing stream of blocks of real samples.
        at intervals matching the ``sz`` of this component.
    """

    class Function(Enum):
        """Enumeration representing different window functions for :class:`Window`."""
        #:
        HANN      = lambda k, sz: 0.5 - 0.5*cos(k*2*pi/sz)
        #:
        SQRT_HANN = lambda k, sz: sqrt(0.5 - 0.5*cos(k*2*pi/sz))
        #:
        RECT      = lambda k, sz: 1.

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int,
                 # Default: sqrt(Hann) window for STFT
                 window_function = Function.SQRT_HANN) -> None:

        """
        shape : fixed.SQ
            Shape of the fixed-point types used for inputs and outputs. This is
            the shape of a single number, this core wraps it in :class:`Block`\\(shape).
        sz : int
            Size of the window function.
        window_function : Function
            Function used to calculate window function constants (type of window).
        """
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

    """Real sample stream to (overlapping) :class:`Block` stream conversion.

    This core is a building block for the :class:`STFTProcessor` family of components. It takes
    a continuous (non-delineated) stream of samples, and sends delineated blocks
    of samples, which may be overlapping, for use by further processing.

    Here is a quick example to illustrate. From the input perspective, each sample
    would correspond to the following output samples (taking sz=8, n_overlap=4):

    .. code-block:: text

        Input:    0 1 2 3 4 5 6 7 8 9 A B C D E F ...
        Block 1:  0 1 2 3 4 5 6 7
        Block 2:          4 5 6 7 8 9 A B
        Block 3:                  8 9 A B C D E F

    Looking at this from the output perspective:

    .. code-block:: text

        payload.sample:  0 1 2 3 4 5 6 7 4 5 6 7 8 9 A B 8 9 A B C D E F
        payload.first:   1               1               1

    To avoid backpressure on the input stream, the incoming sample rate should be much
    slower than the system clock, and rate of processing the output blocks (which is easily
    achievable with audio signals).

    Design
    ------

    This core uses a single ``SyncFIFO`` for storage of size ``n_overlap``, which is
    continuously filled and drained between blocks to create overlapping outputs.

    Members
    -------
    i : :py:`In(stream.Signature(self.shape))`
        Incoming (continuous) stream of real samples.
    o : :py:`Out(stream.Signature(Block(self.shape)))`
        Outgoing stream of blocks of real samples.
        at intervals matching the ``sz`` of this component.
    """

    def __init__(self,
                 shape:     fixed.SQ,
                 sz:        int,
                 n_overlap: int):
        """
        shape : fixed.SQ
            Shape of the fixed-point types used for inputs and outputs. This is
            the shape of a single number, this core wraps it in :class:`Block`\\(shape).
        sz : int
            Size of the output blocks.
        n_overlap : int
            Number of elements shared between adjacent output blocks.
        """

        # TODO: currently, only even overlap is tested, as required by STFT.
        assert n_overlap == (sz // 2)

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
    """Convert :class:`Block` stream to continuous samples by 'Overlap-Add'.

    This core is a building block for the :class:`STFTProcessor` family of components. It takes
    overlapping, delineated blocks of samples, adds up the overlapping elements
    and sends a stream of (non-delineated) continuous samples.

    Again, an example for (sz=8, n_overlap=4). From the input perspective, say we have:

    .. code-block:: text

        payload.sample:  0 1 2 3 4 5 6 7 8 9 A B C D E F G H I J ...
        payload.first:   1               1               1

    This core would send out the following stream:

    .. code-block:: text

        Block 1:  0 1 2 3 4 5 6 7
        Block 2:          8 9 A B C D E F
        Block 3:                  G H I J ...

        Out:      0 1 2 3 4 5 6 7 C D E J
                  + + + + + + + + + + + +
                  X X X X 8 9 A B G H I F ... (X == zero padding)

    From above, it should be clear that each output sample is formed by summing the
    'overlapping' parts of each input block, and that there are less output samples
    than input samples as a result.

    Note that connecting a :class:`ComputeOverlappingBlocks` straight to an :class:`OverlapAddBlocks`
    will not reconstruct the original signal, unless the samples are windowed (tapered)
    for perfect reconstruction. For an example, see the :class:`STFTProcessor` family of components.

    Design
    ------

    This core uses two ``SyncFIFO`` for storage of size ``sz``, which are both
    continuously filled and drained as necessary to add up the correct overlapping parts.

    Members
    -------
    i : :py:`In(stream.Signature(Block(self.shape)))`
        Incoming stream of blocks of overlapping real samples.
    o : :py:`Out(stream.Signature(self.shape))`
        Outgoing stream of continuous real samples.
    """

    def __init__(self,
                 shape:     fixed.SQ,
                 sz:        int,
                 n_overlap: int):
        """
        shape : fixed.SQ
            Shape of the fixed-point types used for inputs and outputs. This is
            the shape of a single number, this core wraps it in :class:`Block`\\(shape).
        sz : int
            Size of the input blocks.
        n_overlap : int
            Number of elements shared between adjacent input blocks.
        """

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

class STFTProcessor(wiring.Component):

    """Short-Time Fourier Transform ('Overlap-Add') with shared FFT core.

    This core performs both analysis and re-synthesis of time-domain samples by passing
    them through the frequency domain for spectral processing by user logic.

    The general flow of operations:

        - ``i`` (samples in) -> :class:`ComputeOverlappingBlocks` -> :class:`Window` -> :class:`FFT` -> ``o_freq``
        - ``i_freq`` -> :class:`FFT` (inverse) -> :class:`Window` -> :class:`OverlapAddBlocks` -> ``o`` (samples out)

    If ``o_freq`` and ``i_freq`` frequency-domain streams are directly connected together
    with no processing logic, this core will perfectly resynthesize the original signal.

    :class:`Window.Function.SQRT_HANN` windowing is used in both the analysis and synthesis stages.

    Design
    ------

    Unlike :class:`STFTProcessorPipelined`, this implementation saves area by time-multiplexing
    :class:`FFT` and :class:`Window` cores between analysis and synthesis operations, at the cost of
    reduced throughput. For audio purposes, this core is easily still fast enough for real-time
    processing.

    At a high level, the components are connected in a different sequence depending
    on which state the core is in. The core contains a single `SyncFIFO` used to buffer
    all the outputs of user (frequency domain) processing logic. This is required to
    avoid backpressure on the user logic while it is disconnected from the IFFT stage.

    Members
    -------
    i : :py:`In(stream.Signature(shape))`
        Continuous time-domain input stream
    o : :py:`Out(stream.Signature(shape))`
        Continuous time-domain output stream (reconstructed)
    o_freq : :py:`Out(stream.Signature(Block(CQ(shape))))`
        Frequency-domain output blocks for processing by user logic
    i_freq : :py:`In(stream.Signature(Block(CQ(shape))))`
        Frequency-domain input blocks after processing by user logic
    """

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int):
        """
        shape : fixed.SQ
            Shape of the fixed-point samples used for inputs and outputs.
        sz : int
            Size of the frequency-domain blocks used internally and exposed for frequency
            domain processing. ``o_freq`` and ``i_freq`` are delineated by blocks
            with a ``payload.first`` strobe every ``sz`` elements.
        """

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


        m.submodules.ififo = ififo = fifo.SyncFIFOBuffered(
            width=self.shape.as_shape().width, depth=self.sz//4)
        wiring.connect(m, wiring.flipped(self.i), ififo.w_stream)
        wiring.connect(m, ififo.r_stream, self.overlap_blocks.i)

        m.submodules.ofifo = ofifo = fifo.SyncFIFOBuffered(
            width=self.shape.as_shape().width, depth=self.sz)
        wiring.connect(m, self.overlap_add.o, ofifo.w_stream)
        wiring.connect(m, ofifo.r_stream, wiring.flipped(self.o))

        m.submodules.pfifo = pfifo = fifo.SyncFIFOBuffered(
            width=self.i_freq.payload.shape().size, depth=self.sz)

        n_samples = Signal(range(self.sz+1), init=0)

        with m.FSM():
            with m.State("LOAD"):
                m.d.comb += self.fft.ifft.eq(0)
                wiring.connect(m, self.overlap_blocks.o, self.window.i)
                connect_sq_to_real(m, self.window.o, self.fft.i)
                with m.If(self.overlap_blocks.o.valid & self.overlap_blocks.o.ready):
                    m.d.sync += n_samples.eq(n_samples+1)
                with m.If(n_samples == self.sz):
                    m.next = "ANALYZE"
            with m.State("ANALYZE"):
                connect_sq_to_real(m, self.window.o, self.fft.i)
                wiring.connect(m, self.fft.o, wiring.flipped(self.o_freq))
                wiring.connect(m, wiring.flipped(self.i_freq), pfifo.w_stream)
                with m.If(pfifo.w_level == self.sz):
                    m.next = "SYNTHESIZE"
            with m.State("SYNTHESIZE"):
                m.d.comb += self.fft.ifft.eq(1)
                wiring.connect(m, pfifo.r_stream, self.fft.i)
                connect_real_to_sq(m, self.fft.o, self.window.i)
                wiring.connect(m, self.window.o, self.overlap_add.i)
                with m.If(self.window.o.valid & self.window.o.ready):
                    m.d.sync += n_samples.eq(n_samples-1)
                with m.If(n_samples == 0):
                    m.next = "LOAD"

        return m

class STFTAnalyzer(wiring.Component):

    """Short-Time Fourier Transform for spectral analysis.

    This core allows frequency-domain analysis of time-domain samples by passing them through
    the following signal flow:

        - ``i`` (samples in) -> :class:`ComputeOverlappingBlocks` -> :class:`Window` -> :class:`FFT` -> ``o``

    For a more resource-efficient STFT that performs both analysis and synthesis, see :class:`STFTProcessor`.

    Members
    -------
    i : :py:`In(stream.Signature(shape))`
        Continuous time-domain input stream
    o : :py:`Out(stream.Signature(Block(CQ(shape))))`
        Frequency-domain output blocks for processing by user logic
    """

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int,
                 window_function = Window.Function.HANN):
        """
        shape : fixed.SQ
            Shape of the fixed-point samples used for inputs and outputs.
        sz : int
            Size of the frequency-domain blocks used internally and exposed for frequency
            domain processing.
        window : Window.Function
            Window function applied to time-domain blocks the FFT.
        """

        self.sz        = sz
        self.shape     = shape

        self.overlap_blocks   = ComputeOverlappingBlocks(sz=sz, shape=shape, n_overlap=sz//2)
        self.window_analysis  = Window(sz=sz, shape=shape, window_function=window_function)
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
        connect_sq_to_real(m, self.window_analysis.o, self.fft.i)
        wiring.connect(m, self.fft.o, wiring.flipped(self.o))

        return m

class STFTSynthesizer(wiring.Component):

    """Short-Time Fourier Transform for spectral synthesis.

    This core allows frequency-domain synthesis of time-domain samples by passing them through
    the following signal flow:

        - ``i_freq`` -> :class:`FFT` (inverse) -> :class:`Window` -> :class:`OverlapAddBlocks` -> ``o`` (samples out)

    For a more resource-efficient STFT that performs both analysis and synthesis, see :class:`STFTProcessor`.

    Members
    -------
    i : :py:`In(stream.Signature(Block(CQ(shape))))`
        Frequency-domain input blocks used for synthesis.
    o : :py:`Out(stream.Signature(shape))`
        Continuous time-domain output stream
    """

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int,
                 window_function = Window.Function.HANN):
        """
        shape : fixed.SQ
            Shape of the fixed-point samples used for inputs and outputs.
        sz : int
            Size of the frequency-domain blocks used internally and exposed for frequency
            domain processing.
        window : Window.Function
            Window function applied to time-domain blocks after the IFFT, but before overlap-add.
        """

        self.sz        = sz
        self.shape     = shape

        self.ifft             = FFT(sz=sz, shape=shape, default_ifft=True)
        self.window_synthesis = Window(sz=sz, shape=shape, window_function=window_function)
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
        connect_real_to_sq(m, self.ifft.o, self.window_synthesis.i)
        wiring.connect(m, self.window_synthesis.o, self.overlap_add.i)
        wiring.connect(m, self.overlap_add.o, wiring.flipped(self.o))

        return m

class STFTProcessorPipelined(wiring.Component):

    """Short-Time Fourier Transform ('Overlap-Add') with separate FFT/IFFT cores.

    This core performs both analysis and re-synthesis of time-domain samples by passing
    them through the frequency domain for spectral processing by user logic.

    This is a simpler-to-understand version of :class:`STFTProcessor` as it does not share
    the :class:`Window` or :class:`FFT` cores, making it higher throughput, but also higher
    resource usage, because it can perform the FFT and IFFT at the same time.

    This core is mostly used for testing the :class:`STFTAnalyzer` and :class:`STFTSynthesizer`
    components in isolation, and doesn't make much sense to use in real projects compared
    to just using the :class:`STFTProcessor` above, which is much more resource efficient
    for audio applications. Unless you have super high sample rates.

    Members
    -------
    i : :py:`In(stream.Signature(shape))`
        Continuous time-domain input stream
    o : :py:`Out(stream.Signature(shape))`
        Continuous time-domain output stream (reconstructed)
    o_freq : :py:`Out(stream.Signature(Block(CQ(shape))))`
        Frequency-domain output blocks for processing by user logic
    i_freq : :py:`In(stream.Signature(Block(CQ(shape))))`
        Frequency-domain input blocks after processing by user logic
    """

    def __init__(self,
                 shape: fixed.SQ,
                 sz:    int):
        """
        shape : fixed.SQ
            Shape of the fixed-point samples used for inputs and outputs.
        sz : int
            Size of the frequency-domain blocks used internally and exposed for frequency
            domain processing.
        """

        self.sz        = sz
        self.shape     = shape

        # Symmetric sqrt(Hann) windows for resynthesis.
        self.analyzer    = STFTAnalyzer(shape=shape, sz=sz, window_function=Window.Function.SQRT_HANN)
        self.synthesizer = STFTSynthesizer(shape=shape, sz=sz, window_function=Window.Function.SQRT_HANN)

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
