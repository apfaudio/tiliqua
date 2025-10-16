# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#
"""
Designs demoing parts of the DSP library. Build any of them as follows:

.. code-block:: bash

   # from `gateware` directory. Show all available example cores -
   pdm dsp -h

   # build an example core
   pdm dsp build --dsp-core nco

"""

import math
import sys

from amaranth import *
from amaranth.build import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.cdc import FFSynchronizer
from amaranth.lib.wiring import In, Out
from amaranth_soc import wishbone

from tiliqua import dsp, midi
from tiliqua.build import sim
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.dsp import ASQ
from tiliqua.periph import eurorack_pmod, psram
from tiliqua.platform import RebootProvider


class Mirror(wiring.Component):

    """
    Route audio inputs straight to outputs (in the audio domain).
    This is the simplest possible core, useful for basic tests.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Audio passthrough",
        io_left=['in0', 'in1', 'in2', 'in3', 'in0 (copy)', 'in1 (copy)', 'in2 (copy)', 'in3 (copy)'],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()
        wiring.connect(m, wiring.flipped(self.i), wiring.flipped(self.o))
        return m

class QuadNCO(wiring.Component):

    """
    Audio-rate oscillator (NCO) with internal oversampling.
    4 different waveform outputs.

    TODO: We should really inject the cal for this one as
    otherwise the V/oct is not calibrated. Yet to figure
    out the easiest way to do so without an SoC.

    in0: V/oct pitch
    in1: phase modulation
    out0: sine
    out1: saw
    out2: tri
    out3: square
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Quad oscillator (audio only!)",
        io_left=['V/oct', 'phase mod', '', '', 'sine', 'saw', 'tri', 'square'],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.split4 = split4 = dsp.Split(n_channels=4)
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)

        m.submodules.rep4 = rep4 = dsp.Split(n_channels=4,
                                             replicate=True)

        m.submodules.merge2 = merge2 = dsp.Merge(n_channels=2)

        m.submodules.nco    = nco    = dsp.SawNCO(shift=4)

        def v_oct_lut(x, clamp_lo=-8.0, clamp_hi=6.0):
            def volts_to_freq(volts, a3_freq_hz=440.0):
                return (a3_freq_hz / 8.0) * 2 ** (volts + 2.0 - 3.0/4.0)
            def volts_to_delta(volts, sample_rate_hz=48000):
                return (1.0 / sample_rate_hz) * volts_to_freq(volts)
            # convert audio sample [-1, 1] to volts
            x = x*(2**15/4000)
            if x > clamp_hi:
                x = clamp_hi
            if x < clamp_lo:
                x = clamp_lo
            out = volts_to_delta(x) * 16
            return out

        m.submodules.v_oct = v_oct = dsp.WaveShaper(
                lut_function=v_oct_lut, lut_size=128, continuous=False)

        amplitude = 0.4

        def sine_osc(x):
            return amplitude*math.sin(math.pi*x)

        def saw_osc(x):
            return amplitude*x

        def tri_osc(x):
            return amplitude * (2*abs(x) - 1.0)

        def square_osc(x):
            return amplitude if x > 0 else -amplitude

        waveshapers = [
            dsp.WaveShaper(lut_function=sine_osc,
                           lut_size=128, continuous=True),
            dsp.WaveShaper(lut_function=saw_osc,
                           lut_size=128, continuous=True),
            dsp.WaveShaper(lut_function=tri_osc,
                           lut_size=128, continuous=True),
            dsp.WaveShaper(lut_function=square_osc,
                           lut_size=128, continuous=True),
        ]

        m.submodules += waveshapers

        N_UP = 16
        M_DOWN = 16

        m.submodules.resample_up0 = resample_up0 = dsp.Resample(
                fs_in=48000, n_up=N_UP, m_down=1)
        m.submodules.resample_up1 = resample_up1 = dsp.Resample(
                fs_in=48000, n_up=N_UP, m_down=1)

        m.submodules.down0 = resample_down0 = dsp.Resample(
                fs_in=48000*N_UP, n_up=1, m_down=M_DOWN)
        m.submodules.down1 = resample_down1 = dsp.Resample(
                fs_in=48000*N_UP, n_up=1, m_down=M_DOWN)
        m.submodules.down2 = resample_down2 = dsp.Resample(
                fs_in=48000*N_UP, n_up=1, m_down=M_DOWN)
        m.submodules.down3 = resample_down3 = dsp.Resample(
                fs_in=48000*N_UP, n_up=1, m_down=M_DOWN)

        wiring.connect(m, wiring.flipped(self.i), split4.i)

        wiring.connect(m, split4.o[0], resample_up0.i)
        wiring.connect(m, split4.o[1], resample_up1.i)
        wiring.connect(m, split4.o[2], dsp.ASQ_READY)
        wiring.connect(m, split4.o[3], dsp.ASQ_READY)

        wiring.connect(m, resample_up0.o, v_oct.i)
        wiring.connect(m, v_oct.o, merge2.i[0])
        wiring.connect(m, resample_up1.o, merge2.i[1])
        wiring.connect(m, merge2.o, nco.i)
        wiring.connect(m, nco.o, rep4.i)
        wiring.connect(m, rep4.o[0], waveshapers[0].i)
        wiring.connect(m, rep4.o[1], waveshapers[1].i)
        wiring.connect(m, rep4.o[2], waveshapers[2].i)
        wiring.connect(m, rep4.o[3], waveshapers[3].i)

        wiring.connect(m, waveshapers[0].o, resample_down0.i)
        wiring.connect(m, waveshapers[1].o, resample_down1.i)
        wiring.connect(m, waveshapers[2].o, resample_down2.i)
        wiring.connect(m, waveshapers[3].o, resample_down3.i)

        wiring.connect(m, resample_down0.o, merge4.i[0])
        wiring.connect(m, resample_down1.o, merge4.i[1])
        wiring.connect(m, resample_down2.o, merge4.i[2])
        wiring.connect(m, resample_down3.o, merge4.i[3])

        wiring.connect(m, merge4.o, wiring.flipped(self.o))

        return m

class DWO(wiring.Component):

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    def elaborate(self, platform):

        m = Module()

        m.submodules.split4 = split4 = dsp.Split(
                n_channels=4, source=wiring.flipped(self.i))
        m.submodules.merge4 = merge4 = dsp.Merge(
                n_channels=4, sink=wiring.flipped(self.o))

        split4.wire_ready(m, [1, 2, 3])
        merge4.wire_valid(m, [1, 2, 3])

        m.submodules.dwo = dwo = dsp.oscillators.DWO()
        wiring.connect(m, dwo.o, merge4.i[0])

        return m


class Resampler(wiring.Component):

    """
    Resample different channels to a different sample rate (and back).
    Not very musically interesting
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Up/downsampling round-trip test",
        io_left=['in0', 'in1', 'in2', 'in3', 'out0 (6kHz)', 'out1 (192kHz)', 'out2 (44.1kHz)', 'out3 (unchanged)'],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.split4 = split4 = dsp.Split(n_channels=4, source=wiring.flipped(self.i))
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4, sink=wiring.flipped(self.o))

        # ch0: 48kHz => 6kHz => 48kHz

        m.submodules.resample0a = resample0a = dsp.Resample(
            fs_in=48000,    n_up=1, m_down=8)
        m.submodules.resample0b = resample0b = dsp.Resample(
            fs_in=48000//8, n_up=8, m_down=1)

        wiring.connect(m, split4.o[0], resample0a.i)
        wiring.connect(m, resample0a.o, resample0b.i)
        wiring.connect(m, resample0b.o, merge4.i[0])

        # ch1: 48kHz => 192kHz => 48kHz

        m.submodules.resample1a = resample1a = dsp.Resample(
            fs_in=48000,    n_up=4, m_down=1)
        m.submodules.resample1b = resample1b = dsp.Resample(
            fs_in=48000*4,  n_up=1, m_down=4)

        wiring.connect(m, split4.o[1], resample1a.i)
        wiring.connect(m, resample1a.o, resample1b.i)
        wiring.connect(m, resample1b.o, merge4.i[1])

        # ch2: 48kHz => 44.1kHz => 48kHz (odd ratio)

        m.submodules.resample2a = resample2a = dsp.Resample(
            fs_in=48000, n_up=441, m_down=480)
        m.submodules.resample2b = resample2b = dsp.Resample(
         fs_in=48000*(441/480), n_up=480, m_down=441)

        wiring.connect(m, split4.o[2], resample2a.i)
        wiring.connect(m, resample2a.o, resample2b.i)
        wiring.connect(m, resample2b.o, merge4.i[2])

        # ch3: passthrough

        wiring.connect(m, split4.o[3], merge4.i[3])

        return m

class ResonantFilter(wiring.Component):

    """
    High-, Low-, Bandpass with cutoff & resonance control.

    in0: audio in
    in1: cutoff (0V == off, ~5V == open)
    in2: resonance (0V == min, ~5V == crazy)

    out0: LPF out
    out1: HPF out
    out2: BPF out
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Resonant filter (SVF)",
        io_left=['audio in', 'cutoff', 'resonance', '', 'LPF out', 'HPF out', 'BPF out', ''],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):

        m = Module()

        m.submodules.svf0 = svf0 = dsp.SVF()

        # connect without 'wiring.connect' so we can see the payload field names.

        m.d.comb += [
            svf0.i.valid.eq(self.i.valid),
            self.i.ready.eq(svf0.i.ready),

            svf0.i.payload.x.eq(self.i.payload[0]),
            svf0.i.payload.cutoff.eq(self.i.payload[1]),
            svf0.i.payload.resonance.eq(ASQ.max() - self.i.payload[2]),
        ]

        m.d.comb += [
            svf0.o.ready.eq(self.o.ready),
            self.o.valid.eq(svf0.o.valid),

            self.o.payload[0].eq(svf0.o.payload.lp),
            self.o.payload[1].eq(svf0.o.payload.hp),
            self.o.payload[2].eq(svf0.o.payload.bp),
        ]

        return m

class DualVCA(wiring.Component):

    """Audio-rate VCA."""

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Dual audio-rate VCA",
        io_left=['VCA0 audio', 'VCA0 CV', 'VCA1 audio', 'VCA1 CV', 'VCA0 out', 'VCA1 out', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.split4 = split4 = dsp.Split(n_channels=4)
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)

        m.submodules.merge2a = merge2a = dsp.Merge(n_channels=2)
        m.submodules.merge2b = merge2b = dsp.Merge(n_channels=2)

        m.submodules.vca0 = vca0 = dsp.VCA(itype=ASQ)
        m.submodules.vca1 = vca1 = dsp.VCA(itype=ASQ)

        # connect with 'wiring.connect' to show how this works.

        wiring.connect(m, wiring.flipped(self.i), split4.i)

        wiring.connect(m, split4.o[0], merge2a.i[0])
        wiring.connect(m, split4.o[1], merge2a.i[1])
        wiring.connect(m, split4.o[2], merge2b.i[0])
        wiring.connect(m, split4.o[3], merge2b.i[1])

        wiring.connect(m, merge2a.o, vca0.i)
        wiring.connect(m, vca0.o, merge4.i[0])

        wiring.connect(m, merge2b.o, vca1.i)
        wiring.connect(m, vca1.o, merge4.i[1])

        wiring.connect(m, dsp.ASQ_VALID, merge4.i[2])
        wiring.connect(m, dsp.ASQ_VALID, merge4.i[3])
        wiring.connect(m, merge4.o, wiring.flipped(self.o))

        return m

class Pitch(wiring.Component):

    """
    PSRAM-backed pitch shifter with CV-controlled pitch.
    Grain size is quite large (~250ms) to reduce fluttering.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    # shared bus to external memory
    bus: Out(wishbone.Signature(addr_width=22,
                                data_width=32,
                                granularity=8,
                                features={'bte', 'cti'}))

    bitstream_help = BitstreamHelp(
        brief="Crossfade pitch shifter",
        io_left=['audio in', 'pitch CV', '', '', 'shifted out', '', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.split4 = split4 = dsp.Split(n_channels=4)
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)

        m.submodules.delay_line = delay_line = dsp.DelayLine(
            max_delay=0x8000,
            psram_backed=True,
            write_triggers_read=False,
            addr_width_o=self.bus.addr_width,
            base=0x00000,
        )

        m.submodules.pitch_shift = pitch_shift = dsp.PitchShift(
            tap=delay_line.add_tap(), xfade=delay_line.max_delay//4)

        wiring.connect(m, wiring.flipped(self.i), split4.i)

        # write audio samples to delay line
        wiring.connect(m, split4.o[0], delay_line.i)

        # hook up 2nd input channel as pitch control, use fixed grain_sz
        m.d.comb += [
            split4.o[1].ready.eq(pitch_shift.i.ready),
            pitch_shift.i.valid.eq(split4.o[1].valid),
            pitch_shift.i.payload.pitch.eq(split4.o[1].payload.as_value() >> 8),
            pitch_shift.i.payload.grain_sz.eq(delay_line.max_delay//2),
        ]

        wiring.connect(m, split4.o[2], dsp.ASQ_READY)
        wiring.connect(m, split4.o[3], dsp.ASQ_READY)

        # first channel is pitch shift output
        wiring.connect(m, pitch_shift.o, merge4.i[0])
        wiring.connect(m, dsp.ASQ_VALID, merge4.i[1])
        wiring.connect(m, dsp.ASQ_VALID, merge4.i[2])
        wiring.connect(m, dsp.ASQ_VALID, merge4.i[3])

        wiring.connect(m, merge4.o, wiring.flipped(self.o))

        wiring.connect(m, delay_line.bus, wiring.flipped(self.bus))

        return m

class Matrix(wiring.Component):

    """Matrix mixer with fixed coefficients."""

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Mix inputs with fixed coefficients.",
        io_left=['in0', 'in1', 'in2', 'in3', 'mixed0', 'mixed1', 'mixed2', 'mixed3'],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.matrix_mix = matrix_mix = dsp.MatrixMix(
            i_channels=4, o_channels=4,
            coefficients=[[0.4, 0.3, 0.2, 0.1],
                          [0.1, 0.4, 0.3, 0.2],
                          [0.2, 0.1, 0.4, 0.3],
                          [0.3, 0.2, 0.1, 0.4]])

        wiring.connect(m, wiring.flipped(self.i), matrix_mix.i)
        wiring.connect(m, matrix_mix.o, wiring.flipped(self.o))

        return m

class DualWaveshaper(wiring.Component):

    """Soft distortion, channel 1/2 inputs, 3 is overdrive gain."""

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Dual waveshaper / distortion",
        io_left=['audio in 0', 'audio in 1', 'drive', '-', 'distorted 0', 'distorted 1', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)

        def scaled_tanh(x):
            return math.tanh(3.0*x)

        m.submodules.vca0 = vca0 = dsp.VCA()
        m.submodules.vca1 = vca1 = dsp.VCA()
        m.submodules.waveshaper0 = waveshaper0 = dsp.WaveShaper(lut_function=scaled_tanh)
        m.submodules.waveshaper1 = waveshaper1 = dsp.WaveShaper(lut_function=scaled_tanh)

        m.d.comb += [
            vca0.i.valid.eq(self.i.valid),
            vca1.i.valid.eq(self.i.valid),
            self.i.ready.eq(vca0.i.ready),

            vca0.i.payload[0].eq(self.i.payload[0]),
            vca1.i.payload[0].eq(self.i.payload[1]),
            vca0.i.payload[1].eq(self.i.payload[2] << 2),
            vca1.i.payload[1].eq(self.i.payload[2] << 2),
        ]

        wiring.connect(m, vca0.o, waveshaper0.i)
        wiring.connect(m, vca1.o, waveshaper1.i)

        wiring.connect(m, waveshaper0.o, merge4.i[0])
        wiring.connect(m, waveshaper1.o, merge4.i[1])

        wiring.connect(m, dsp.ASQ_VALID, merge4.i[2])
        wiring.connect(m, dsp.ASQ_VALID, merge4.i[3])
        wiring.connect(m, merge4.o, wiring.flipped(self.o))

        return m

class TouchMixTop(wiring.Component):

    """Matrix mixer, combine touch inputs in interesting ways."""

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Mix touch inputs to outputs 0-3",
        io_left=['touch0', 'touch1', 'touch2', 'touch3', 'out0', 'out1', 'out2', 'out3'],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.matrix_mix = matrix_mix = dsp.MatrixMix(
            i_channels=4, o_channels=4,
            coefficients=[[0.5, -0.5, 0.25, 0.1],
                          [0.5, -0.5, 0.25, 0.2],
                          [-0.5, 0.5, 0.25, 0.3],
                          [-0.5, 0.5, 0.25, 0.4]])

        wiring.connect(m, wiring.flipped(self.i), matrix_mix.i)
        wiring.connect(m, matrix_mix.o, wiring.flipped(self.o))

        return m

class PSRAMPingPongDelay(wiring.Component):

    """
    2-channel stereo ping-pong delay, backed by external PSRAM.

    2 delay lines are instantiated in isolated slices of the external
    memory address space. Using external memory allows for much longer
    delay times whilst using less resources, compared to SRAM-backed
    delay lines, however on a larger design, you have to be careful
    that PSRAM-backed delay lines don't get starved by other PSRAM
    traffic (i.e video framebuffer operations).

    Tiliqua input 0/1 is stereo in, output 0/1 is stereo out.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    # shared bus to external memory
    bus: Out(wishbone.Signature(addr_width=22,
                                data_width=32,
                                granularity=8,
                                features={'bte', 'cti'}))

    bitstream_help = BitstreamHelp(
        brief="Ping-pong delay (PSRAM)",
        io_left=['in L', 'in R', '', '', 'out L', 'out R', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def __init__(self):
        super().__init__()

        # 2 delay lines, backed by 2 different slices of PSRAM address space.

        self.delayln1 = dsp.DelayLine(
            max_delay=0x4000, # careful this doesn't collide with delayln2.base!
            psram_backed=True,
            addr_width_o=self.bus.addr_width,
            base=0x00000,
        )

        self.delayln2 = dsp.DelayLine(
            max_delay=0x4000,
            psram_backed=True,
            addr_width_o=self.bus.addr_width,
            base=0x4000,
        )

        # Both delay lines share our memory bus round-robin for all operations.

        self._arbiter = wishbone.Arbiter(addr_width=self.bus.addr_width,
                                         data_width=self.bus.data_width,
                                         granularity=self.bus.granularity,
                                         features=self.bus.features)
        self._arbiter.add(self.delayln1.bus)
        self._arbiter.add(self.delayln2.bus)

        # Create the PingPongCore using the above delay lines.

        self.pingpong = dsp.delay_effect.PingPongDelay(self.delayln1, self.delayln2)

    def elaborate(self, platform):
        m = Module()

        m.submodules.arbiter  = self._arbiter
        m.submodules.delayln1 = self.delayln1
        m.submodules.delayln2 = self.delayln2
        m.submodules.pingping = self.pingpong

        wiring.connect(m, self._arbiter.bus, wiring.flipped(self.bus))

        # Map hardware in/out channels 0, 1 (of 4) to pingpong stereo channels 0, 1

        dsp.channel_remap(m, wiring.flipped(self.i), self.pingpong.i, {0: 0, 1: 1})
        dsp.channel_remap(m, self.pingpong.o, wiring.flipped(self.o), {0: 0, 1: 1})

        return m

class SRAMPingPongDelay(wiring.Component):

    """
    2-channel stereo ping-pong delay, backed by internal SRAM.

    Tiliqua input 0/1 is stereo in, output 0/1 is stereo out.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Ping-pong delay (SRAM)",
        io_left=['in L', 'in R', '', '', 'out L', 'out R', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def __init__(self):
        super().__init__()

        # 2 delay lines, backed by independent slabs of internal SRAM.

        self.delayln1 = dsp.DelayLine(max_delay=0x4000)
        self.delayln2 = dsp.DelayLine(max_delay=0x4000)

        # Create the PingPongCore using the above delay lines.

        self.pingpong = dsp.delay_effect.PingPongDelay(self.delayln1, self.delayln2)

    def elaborate(self, platform):
        m = Module()

        m.submodules.delayln1 = self.delayln1
        m.submodules.delayln2 = self.delayln2

        m.submodules.pingping = self.pingpong

        # Map hardware in/out channels 0, 1 (of 4) to pingpong stereo channels 0, 1

        dsp.channel_remap(m, wiring.flipped(self.i), self.pingpong.i, {0: 0, 1: 1})
        dsp.channel_remap(m, self.pingpong.o, wiring.flipped(self.o), {0: 0, 1: 1})

        return m

class PSRAMDiffuser(wiring.Component):

    """
    PSRAM-backed 4-channel feedback delay, diffused by a matrix mixer.

    A block diagram of the signal flow inside this demo:

    .. image:: /_static/diffusor.png
      :width: 800

    All 4 input channels are inputs.
    All 4 output channels are outputs.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))
    bus: Out(wishbone.Signature(addr_width=22,
                                data_width=32,
                                granularity=8,
                                features={'bte', 'cti'}))

    bitstream_help = BitstreamHelp(
        brief="4ch diffusion delay (short, PSRAM-backed)",
        io_left=['in0', 'in1', 'in2', 'in3', 'out0', 'out1', 'out2', 'out3'],
        io_right=['', '', '', '', '', '']
    )

    def __init__(self):
        super().__init__()

        # 4 delay lines, backed by 4 different slices of PSRAM address space.

        self.delay_lines = [
            dsp.DelayLine(
                max_delay=0x10000,
                psram_backed=True,
                addr_width_o=self.bus.addr_width,
                base=0x00000,
            ),
            dsp.DelayLine(
                max_delay=0x10000,
                psram_backed=True,
                addr_width_o=self.bus.addr_width,
                base=0x10000,
            ),
            dsp.DelayLine(
                max_delay=0x10000,
                psram_backed=True,
                addr_width_o=self.bus.addr_width,
                base=0x20000,
            ),
            dsp.DelayLine(
                max_delay=0x10000,
                psram_backed=True,
                addr_width_o=self.bus.addr_width,
                base=0x30000,
            ),
        ]

        # All delay lines share our top-level bus for read/write operations.

        self._arbiter = wishbone.Arbiter(addr_width=self.bus.addr_width,
                                         data_width=self.bus.data_width,
                                         granularity=self.bus.granularity,
                                         features=self.bus.features)
        for delayln in self.delay_lines:
            self._arbiter.add(delayln.bus)

        self.diffuser = dsp.delay_effect.Diffuser(self.delay_lines)

    def elaborate(self, platform):
        m = Module()

        m.submodules.arbiter = self._arbiter
        wiring.connect(m, self._arbiter.bus, wiring.flipped(self.bus))

        dsp.named_submodules(m.submodules, self.delay_lines)

        m.submodules.diffuser = self.diffuser

        wiring.connect(m, wiring.flipped(self.i), self.diffuser.i)
        wiring.connect(m, self.diffuser.o, wiring.flipped(self.o))

        return m

class SRAMDiffuser(wiring.Component):

    """
    SRAM-backed 4-channel feedback delay, diffused by a matrix mixer.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="4ch diffusion delay (short, SRAM-backed)",
        io_left=['in0', 'in1', 'in2', 'in3', 'out0', 'out1', 'out2', 'out3'],
        io_right=['', '', '', '', '', '']
    )

    def __init__(self):
        super().__init__()

        # 4 delay lines, backed by 4 independent SRAM banks.

        self.delay_lines = [
            dsp.DelayLine(max_delay=2048),
            dsp.DelayLine(max_delay=4096),
            dsp.DelayLine(max_delay=8192),
            dsp.DelayLine(max_delay=8192),
        ]

        self.diffuser = dsp.delay_effect.Diffuser(self.delay_lines)

    def elaborate(self, platform):
        m = Module()

        dsp.named_submodules(m.submodules, self.delay_lines)

        m.submodules.diffuser = self.diffuser

        wiring.connect(m, wiring.flipped(self.i), self.diffuser.i)
        wiring.connect(m, self.diffuser.o, wiring.flipped(self.o))

        return m

class PSRAMMultiDiffuser(wiring.Component):

    """
    Kind of ridiculous 3x chained diffusers (4x4 diffuser into 4x4 diffuser into 4x4 diffuser).

    All 4 input channels are inputs.
    All 4 output channels are outputs.

    Be careful with the input amplitude on this one, it clips inside the diffuser multipliers
    pretty easily and can be a bit unstable.

    Sounds pretty close to a REALLY long reverb. A single diffuser suffices
    for most real audio applications, but this one is a bit crazy :).

    Its also useful for stress-testing the memory interface logic.

    With 2x PSRAM-backed diffusers that's 8x simultaneous 48kHz audio streams hitting the
    PSRAM (4 write streams, 4 read streams). In simulation the PSRAM controller is blocking
    ~15% of the time. Looking at the traces it seems the cache is bursting twice as often
    as it really needs to (in theory), so probably tweaking the cache architecture could
    get the PSRAM bandwidth consumption down considerably.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))
    bus: Out(wishbone.Signature(addr_width=22,
                                data_width=32,
                                granularity=8,
                                features={'bte', 'cti'}))

    bitstream_help = BitstreamHelp(
        brief="4x4 diffusion delay (audio-only!)",
        io_left=['in0', 'in1', 'in2', 'in3', 'out0', 'out1', 'out2', 'out3'],
        io_right=['', '', '', '', '', '']
    )

    def __init__(self):
        super().__init__()

        # tap lengths of each feedback delay section, each one longer than the last
        self.delay_set = {
            0: [150,       290,    580,    720], # 1x 4x4 diffuser - sram-backed
            1: [1*2000, 1*3000, 1*5000, 1*7000], # 1x 4x4 diffuser - psram-backed (short)
            2: [5*2300, 5*3700, 5*5900, 5*6900]  # 1x 4x4 diffuser - psram-backed (long)
        }

        max_delay = 0x10000
        sram_max_delay = 1024 # if taps are smaller than this, use SRAM delay line.
        spacing   = max_delay*len(self.delay_set[0])
        self.delay_lines = {}
        for n in self.delay_set:
            self.delay_lines[n] = []
            psram_backed = max(self.delay_set[n]) >= sram_max_delay
            for ix, _ in enumerate(self.delay_set[n]):
                if psram_backed:
                    self.delay_lines[n].append(
                        dsp.DelayLine(
                            max_delay=max_delay,
                            psram_backed=True,
                            addr_width_o=self.bus.addr_width,
                            base=n*spacing + max_delay*ix,
                        )
                    )
                else:
                    self.delay_lines[n].append(
                        dsp.DelayLine(
                            max_delay=sram_max_delay,
                            psram_backed=False,
                        )
                    )

        self._arbiter = wishbone.Arbiter(addr_width=self.bus.addr_width,
                                         data_width=self.bus.data_width,
                                         granularity=self.bus.granularity,
                                         features=self.bus.features)
        for n in self.delay_set:
            for delayln in self.delay_lines[n]:
                if delayln.psram_backed:
                    self._arbiter.add(delayln.bus)

        self.diffusers = {}
        for n in self.delay_set:
            self.diffusers[n] = dsp.delay_effect.Diffuser(self.delay_lines[n], delays=self.delay_set[n])

    def elaborate(self, platform):
        m = Module()

        m.submodules.arbiter = self._arbiter
        wiring.connect(m, self._arbiter.bus, wiring.flipped(self.bus))

        for n in self.delay_set:
            m.submodules += self.diffusers[n]
            m.submodules += self.delay_lines[n]

        wiring.connect(m, wiring.flipped(self.i), self.diffusers[0].i)
        wiring.connect(m, self.diffusers[0].o, self.diffusers[1].i)
        wiring.connect(m, self.diffusers[1].o, self.diffusers[2].i)
        wiring.connect(m, self.diffusers[2].o, wiring.flipped(self.o))

        return m

class TripleMirror(wiring.Component):

    """
    Example of using extra (external) audio boards.

    Route audio inputs to outputs on 3 audio boards simultaneously: the internal
    one, and one on each PMOD expansion port. This core assumes all are connected,
    but nothing bad will happen if one is missing (as long as the unused expansion
    ports are left disconnected!)
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Audio passthrough on ex0 & ex1",
        io_left=['in0', 'in1', 'in2', 'in3', 'in0 (copy)', 'in1 (copy)', 'in2 (copy)', 'in3 (copy)'],
        io_right=['', '', '', 'send ins -> outs', 'send ins -> outs', '']
    )

    def elaborate(self, platform):
        m = Module()

        # Instantiate 2 extra external audio boards

        pmod0 = eurorack_pmod.EurorackPmod(self.audio_clock)
        provider0 = eurorack_pmod.PMODProvider(0)
        wiring.connect(m, pmod0.pins, provider0.pins)
        m.submodules += [pmod0, provider0]

        pmod1 = eurorack_pmod.EurorackPmod(self.audio_clock)
        provider1 = eurorack_pmod.PMODProvider(1)
        wiring.connect(m, pmod1.pins, provider1.pins)
        m.submodules += [pmod1, provider1]

        # Route inputs to outputs on all of them
        #
        # Since these connections are all streams in the `sync` clock domain,
        # you can easily change the routing here (i.e route internal audio ins
        # to external pmod outputs and so forth).

        # Internal 4 inputs -> 4 outputs
        wiring.connect(m, wiring.flipped(self.i), wiring.flipped(self.o))
        # ex0 pmod 4 inputs -> 4 outputs
        wiring.connect(m, pmod0.o_cal, pmod0.i_cal)
        # ex1 pmod 4 inputs -> 4 outputs
        wiring.connect(m, pmod1.o_cal, pmod1.i_cal)

        return m

class STFTMirror(wiring.Component):

    """
    Simple test of the ``STFTProcessor`` component. Take channel 0,
    convert blocks into frequency-domain spectra and back again, and
    then emit the same time-domain signal out channel 0.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="STFT round-trip test",
        io_left=['audio in', '', '', '', 'audio out', '', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.stft = stft = dsp.fft.STFTProcessor(
            sz=256, shape=ASQ)
        # Passthrough (resynthesize) in frequency domain.
        wiring.connect(m, stft.o_freq, stft.i_freq)

        m.submodules.split4 = split4 = dsp.Split(n_channels=4)
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)
        wiring.connect(m, wiring.flipped(self.i), split4.i)
        wiring.connect(m, merge4.o, wiring.flipped(self.o))

        wiring.connect(m, split4.o[0], stft.i)
        wiring.connect(m, stft.o, merge4.i[0])

        split4.wire_ready(m, [1, 2, 3])
        merge4.wire_valid(m, [1, 2, 3])

        return m

class Vocoder(wiring.Component):

    """
    STFT-based spectral cross-synthesis (vocoder-like)

    Channel 0 is the 'carrier', channel 1 is the 'modulator'.
    The spectral envelope of the modulator is applied to the
    carrier in the frequency domain, the result of which is
    emitted out channel 0.

    Use relatively high levels and some compression on the
    modulator to get decent intelligibility.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="Spectral cross-synthesis (audio-only!)",
        io_left=['carrier', 'modulator', '', '', 'vocoded out', '', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()

        m.submodules.split4 = split4 = dsp.Split(4)
        m.submodules.merge4 = merge4 = dsp.Merge(4)
        wiring.connect(m, wiring.flipped(self.i), split4.i)
        wiring.connect(m, merge4.o, wiring.flipped(self.o))

        fftsz = 256 # FFT block size
        m.submodules.stft0 = stft0 = dsp.fft.STFTProcessor(shape=ASQ, sz=fftsz)
        m.submodules.analyzer1 = analyzer1 = dsp.fft.STFTAnalyzer(shape=ASQ, sz=fftsz)
        m.submodules.vocoder0 = vocoder0 = dsp.spectral.SpectralCrossSynthesis(shape=ASQ, sz=fftsz)

        wiring.connect(m, stft0.o_freq, vocoder0.i_carrier)
        wiring.connect(m, analyzer1.o, vocoder0.i_modulator)
        wiring.connect(m, vocoder0.o, stft0.i_freq)

        wiring.connect(m, split4.o[0], stft0.i)
        wiring.connect(m, split4.o[1], analyzer1.i)
        wiring.connect(m, stft0.o, merge4.i[0])

        split4.wire_ready(m, [2, 3])
        merge4.wire_valid(m, [1, 2, 3])

        return m

class Noise(wiring.Component):

    """
    Digital white noise, output on channel 0.
    """

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bitstream_help = BitstreamHelp(
        brief="White noise",
        io_left=['', '', '', '', 'noise out', '', '', ''],
        io_right=['', '', '', '', '', '']
    )

    def elaborate(self, platform):
        m = Module()
        m.submodules.noise = noise = dsp.WhiteNoise()
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)
        wiring.connect(m, merge4.o, wiring.flipped(self.o))
        wiring.connect(m, noise.o, merge4.i[0])
        merge4.wire_valid(m, [1, 2, 3])
        return m

class CoreTop(Elaboratable):

    def __init__(self, dsp_core, enable_touch, clock_settings):
        self.core = dsp_core()
        self.core.audio_clock = clock_settings.audio_clock
        self.touch = enable_touch
        self.clock_settings = clock_settings
        self.pmod0 = eurorack_pmod.EurorackPmod(clock_settings.audio_clock)

        # Only if this core uses PSRAM
        if hasattr(self.core, "bus"):
            self.psram_periph = psram.Peripheral(size=16*1024*1024)

        # Forward bitstream_help from the core if it exists
        if hasattr(self.core, "bitstream_help"):
            self.bitstream_help = self.core.bitstream_help

        super().__init__()

    def elaborate(self, platform):
        m = Module()
        m.submodules.pmod0 = pmod0 = self.pmod0
        if sim.is_hw(platform):
            m.submodules.car = car = platform.clock_domain_generator(
                    self.clock_settings)
            m.submodules.provider = provider = eurorack_pmod.FFCProvider()
            wiring.connect(m, pmod0.pins, provider.pins)
            m.submodules.reboot = reboot = RebootProvider(
                    self.clock_settings.frequencies.sync)
            m.submodules.btn = FFSynchronizer(
                    platform.request("encoder").s.i, reboot.button)
            m.d.comb += pmod0.codec_mute.eq(reboot.mute)
        else:
            m.submodules.car = sim.FakeTiliquaDomainGenerator()

        m.submodules.core = self.core
        wiring.connect(m, pmod0.o_cal, self.core.i)
        wiring.connect(m, self.core.o, pmod0.i_cal)

        if hasattr(self.core, "i_midi") and sim.is_hw(platform):
            # For now, if a core requests midi input, we connect it up
            # to the type-A serial MIDI RX input. In theory this bytestream
            # could also come from LUNA in host or device mode.
            midi_pins = platform.request("midi")
            m.submodules.serialrx = serialrx = midi.SerialRx(
                    system_clk_hz=60e6, pins=midi_pins)
            m.submodules.midi_decode = midi_decode = midi.MidiDecode()
            wiring.connect(m, serialrx.o, midi_decode.i)
            wiring.connect(m, midi_decode.o, self.core.i_midi)

        if hasattr(self.core, "bus"):
            m.submodules.psram_periph = self.psram_periph
            wiring.connect(m, self.core.bus, self.psram_periph.bus)

        return m

# Different DSP cores that can be selected at top-level CLI.
CORES = {
    #                 (touch, class name)
    "mirror":         (False, Mirror),
    "nco":            (False, QuadNCO),
    "dwo":            (False, DWO),
    "svf":            (False, ResonantFilter),
    "vca":            (False, DualVCA),
    "pitch":          (False, Pitch),
    "matrix":         (False, Matrix),
    "touchmix":       (True,  TouchMixTop),
    "waveshaper":     (False, DualWaveshaper),
    "midicv":         (False, midi.MonoMidiCV),
    "psram_pingpong": (False, PSRAMPingPongDelay),
    "sram_pingpong":  (False, SRAMPingPongDelay),
    "psram_diffuser": (False, PSRAMDiffuser),
    "sram_diffuser":  (False, SRAMDiffuser),
    "mdiff":          (False, PSRAMMultiDiffuser),
    "resampler":      (False, Resampler),
    "triple_mirror":  (False, TripleMirror),
    "stft_mirror":    (False, STFTMirror),
    "vocode":         (False, Vocoder),
    "noise":          (False, Noise),
}

def simulation_ports(fragment):
    ports = {
        "clk_audio":      (ClockSignal("audio"),                       None),
        "rst_audio":      (ResetSignal("audio"),                       None),
        "clk_sync":       (ClockSignal("sync"),                        None),
        "rst_sync":       (ResetSignal("sync"),                        None),
        "clk_fast":       (ClockSignal("fast"),                        None),
        "rst_fast":       (ResetSignal("fast"),                        None),
        "i2s_sdin1":      (fragment.pmod0.pins.i2s.sdin1,            None),
        "i2s_sdout1":     (fragment.pmod0.pins.i2s.sdout1,           None),
        "i2s_lrck":       (fragment.pmod0.pins.i2s.lrck,             None),
        "i2s_bick":       (fragment.pmod0.pins.i2s.bick,             None),
    }
    # Maybe hook up PSRAM simulation interface
    if hasattr(fragment.core, "bus"):
        ports |= {
            "idle":           (fragment.psram_periph.simif.idle,           None),
            "address_ptr":    (fragment.psram_periph.simif.address_ptr,    None),
            "read_data_view": (fragment.psram_periph.simif.read_data_view, None),
            "write_data":     (fragment.psram_periph.simif.write_data,     None),
            "read_ready":     (fragment.psram_periph.simif.read_ready,     None),
            "write_ready":    (fragment.psram_periph.simif.write_ready,    None),
        }
    return ports

def argparse_callback(parser):
    parser.add_argument('--dsp-core', type=str, default="mirror",
                        help=f"One of {list(CORES)}")

def argparse_fragment(args):
    # Additional arguments to be provided to CoreTop
    if args.dsp_core not in CORES:
        print(f"provided '--dsp-core {args.dsp_core}' is not one of {list(CORES)}")
        sys.exit(-1)

    touch, cls_name = CORES[args.dsp_core]
    args.name = args.name + '-' + args.dsp_core.upper().replace('_','-')
    return {
        "dsp_core": cls_name,
        "enable_touch": touch,
    }

if __name__ == "__main__":
    top_level_cli(
        CoreTop,
        video_core=False,
        sim_ports=simulation_ports,
        sim_harness="../../src/top/dsp/sim_dsp_core.cpp",
        argparse_callback=argparse_callback,
        argparse_fragment=argparse_fragment,
    )
