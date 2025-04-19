# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
High-level delay effects, built on components from the DSP library.
"""

from amaranth                 import *
from amaranth.build           import *
from amaranth.lib             import wiring, data, stream
from amaranth.lib.wiring      import In, Out
from amaranth_soc             import wishbone
from amaranth_future          import fixed
from amaranth.utils           import exact_log2, ceil_log2

from tiliqua                  import eurorack_pmod, dsp, midi, psram_peripheral, delay_line
from tiliqua.cache            import WishboneL2Cache
from tiliqua.eurorack_pmod    import ASQ

class PingPongDelay(wiring.Component):

    """
    2-channel stereo ping-pong delay.

    Based on 2 equal-length delay lines, fed back into each other.

    Delay lines are created external to this component, and may be
    SRAM-backed or PSRAM-backed depending on the application.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 2)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 2)))

    def __init__(self, delayln1, delayln2, delay_samples=15000):
        super().__init__()

        self.delayln1 = delayln1
        self.delayln2 = delayln2

        assert self.delayln1.write_triggers_read
        assert self.delayln2.write_triggers_read

        # Each delay has a single read tap. `write_triggers_read` above ensures
        # stream is connected such that it emits a sample stream synchronized
        # with writes, rather than us needing to connect up tapX.i. (this is
        # only needed if you want multiple delayline reads per write per tap).

        self.tap1 = self.delayln1.add_tap(fixed_delay=delay_samples)
        self.tap2 = self.delayln2.add_tap(fixed_delay=delay_samples)

    def elaborate(self, platform):
        m = Module()

        # Feedback network of ping-ping delay. Each tap is fed back into the input of the
        # opposite tap, mixed 50% with the audio input.

        m.submodules.matrix_mix = matrix_mix = dsp.MatrixMix(
            i_channels=4, o_channels=4,
            coefficients=[[0.5, 0.0, 0.5, 0.0],  # in0
                          [0.0, 0.5, 0.0, 0.5],  # in1
                          [0.5, 0.0, 0.0, 0.5],  # tap1.o
                          [0.0, 0.5, 0.5, 0.0]]) # tap2.o
                        # out0 out1 tap1.i tap2.i

        # Split matrix input / output into independent streams

        m.submodules.imix4 = imix4 = dsp.Merge(n_channels=4)
        m.submodules.omix4 = omix4 = dsp.Split(n_channels=4, source=matrix_mix.o)

        # Close feedback path

        dsp.connect_feedback_kick(m, imix4.o, matrix_mix.i)

        # Split left/right channels of self.i / self.o into independent streams

        m.submodules.isplit2 = isplit2 = dsp.Split(n_channels=2, source=wiring.flipped(self.i))
        m.submodules.omerge2 = omerge2 = dsp.Merge(n_channels=2, sink=wiring.flipped(self.o))

        # Connect up delayln writes, read tap, audio in / out as described above
        # to the matrix feedback network.

        wiring.connect(m, isplit2.o[0], imix4.i[0])
        wiring.connect(m, isplit2.o[1], imix4.i[1])
        wiring.connect(m,  self.tap1.o, imix4.i[2])
        wiring.connect(m,  self.tap2.o, imix4.i[3])

        wiring.connect(m, omix4.o[0],  omerge2.i[0])
        wiring.connect(m, omix4.o[1],  omerge2.i[1])
        wiring.connect(m, omix4.o[2],  self.delayln1.i)
        wiring.connect(m, omix4.o[3],  self.delayln2.i)

        return m

class Diffuser(wiring.Component):

    """
    4-channel shuffling feedback delay.

    Based on 4 separate delay lines with separate delay lengths,
    where the feedback paths are shuffled into different channels
    by a matrix mixer.

    Delay lines are created external to this component, and may be
    SRAM-backed or PSRAM-backed depending on the application.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    def __init__(self, delay_lines, delays=None):
        super().__init__()

        if delays is None:
            self.delays = [2000, 3000, 5000, 7000] # tap delays of each channel.
        else:
            self.delays = delays

        # Verify we were supplied 4 delay lines with the correct properties

        assert len(delay_lines) == 4
        self.delay_lines = delay_lines
        for delay_line, delay in zip(delay_lines, self.delays):
            assert delay_line.write_triggers_read
            assert delay_line.max_delay >= delay

        # Each delay has a single read tap. `write_triggers_read` above ensures
        # stream is connected such that it emits a sample stream synchronized
        # with writes, rather than us needing to connect up tapX.i. (this is
        # only needed if you want multiple delayline reads per write per tap).

        self.taps = []
        for delay, delayln in zip(self.delays, self.delay_lines):
            self.taps.append(delayln.add_tap(fixed_delay=delay))

        # quadrants in the below matrix are:
        #
        # [in    -> out] [in    -> delay]
        # [delay -> out] [delay -> delay] <- feedback
        #

        self.matrix_mix = dsp.MatrixMix(
            i_channels=8, o_channels=8,
            coefficients=[[0.6, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0, 0.0], # in0
                          [0.0, 0.6, 0.0, 0.0, 0.0, 0.8, 0.0, 0.0], #  |
                          [0.0, 0.0, 0.6, 0.0, 0.0, 0.0, 0.8, 0.0], #  |
                          [0.0, 0.0, 0.0, 0.6, 0.0, 0.0, 0.0, 0.8], # in3
                          [0.4, 0.0, 0.0, 0.0, 0.4,-0.4,-0.4,-0.4], # ds0
                          [0.0, 0.4, 0.0, 0.0,-0.4, 0.4,-0.4,-0.4], #  |
                          [0.0, 0.0, 0.4, 0.0,-0.4,-0.4, 0.4,-0.4], #  |
                          [0.0, 0.0, 0.0, 0.4,-0.4,-0.4,-0.4, 0.4]])# ds3
                          # out0 ------- out3  sw0 ---------- sw3

    def elaborate(self, platform):
        m = Module()

        m.submodules.matrix_mix = matrix_mix = self.matrix_mix

        m.submodules.split4 = split4 = dsp.Split(n_channels=4)
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)

        m.submodules.split8 = split8 = dsp.Split(n_channels=8)
        m.submodules.merge8 = merge8 = dsp.Merge(n_channels=8)

        wiring.connect(m, wiring.flipped(self.i), split4.i)

        # matrix <-> independent streams
        wiring.connect(m, matrix_mix.o, split8.i)
        dsp.connect_feedback_kick(m, merge8.o, matrix_mix.i)

        for n in range(4):
            # audio -> matrix [0-3]
            wiring.connect(m, split4.o[n], merge8.i[n])
            # delay -> matrix [4-7]
            wiring.connect(m, self.taps[n].o, merge8.i[4+n])

        for n in range(4):
            # matrix -> audio [0-3]
            wiring.connect(m, split8.o[n], merge4.i[n])
            # matrix -> delay [4-7]
            wiring.connect(m, split8.o[4+n], self.delay_lines[n].i)

        wiring.connect(m, merge4.o, wiring.flipped(self.o))

        return m

class Boxcar(wiring.Component):

    """
    Simple Boxcar Average.

    Average of previous N samples, implemented with an accumulator
    and delay line. The accumulator sums all incoming samples, and we
    subtract an N-sample-delayed version of the incoming signal. This
    is the same as taking the average over the last N samples, requiring
    no multiplies but instead requiring space for N samples.

    Can be used in low- or high-pass mode.
    """

    def __init__(self, n: int=32, hpf=False, sq=ASQ):
        # pow2 constraint on N allows us to shift instead of divide
        assert(2**exact_log2(n) == n)
        self.n = n
        self.hpf = hpf
        self.delayln = delay_line.DelayLine(max_delay=n)
        self.tap = self.delayln.add_tap(fixed_delay=n-1)
        assert self.delayln.write_triggers_read
        super().__init__({
            "i": In(stream.Signature(sq)),
            "o": Out(stream.Signature(sq)),
        })

    def elaborate(self, platform):

        m = Module()

        m.submodules.delayln = self.delayln

        wiring.connect(m, wiring.flipped(self.i), self.delayln.i)

        # accumulator must be large enough to fit N samples
        accumulator = Signal(fixed.SQ(3 + exact_log2(self.n), ASQ.f_bits))
        last_tap = Signal.like(self.tap.o.payload)

        if self.hpf:
            m.d.comb += self.o.payload.eq(last_tap - (accumulator >> exact_log2(self.n))),
        else:
            m.d.comb += self.o.payload.eq(accumulator >> exact_log2(self.n)),

        with m.FSM() as fsm:
            with m.State('WAIT-SAMPLE'):
                with m.If(self.i.valid & self.i.ready):
                    # Add an incoming sample
                    m.d.sync += accumulator.eq(accumulator + self.i.payload)
                    m.next = 'READ-DELAY'
            with m.State('READ-DELAY'):
                m.d.comb += self.tap.o.ready.eq(1)
                with m.If(self.tap.o.valid):
                    # Subtract the sample from N samples ago
                    m.d.sync += accumulator.eq(accumulator - self.tap.o.payload)
                    m.d.sync += last_tap.eq(self.tap.o.payload)
                    m.next = 'WAIT-READY'
            with m.State('WAIT-READY'):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    # Emit a sample
                    m.next = 'WAIT-SAMPLE'

        return m

