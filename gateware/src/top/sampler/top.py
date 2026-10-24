# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
3-channel sampler with CV+touch control.

Record audio into a single shared sample buffer (~5 sec). Three
independent grain channels read from different positions in the same
buffer. Toggle recording from the DELAYLINE page.

    .. code-block:: text

        ┌────┐
        │in0 │◄─ audio in (record source)
        │in1 │◄─ gate ch0 (CV or touch)
        │in2 │◄─ gate ch1 (CV or touch)
        │in3 │◄─ gate ch2 (CV or touch)
        └────┘
        ┌────┐
        │out0│──► channel 0
        │out1│──► channel 1
        │out2│──► channel 2
        │out3│──► mix (ch0+ch1+ch2)
        └────┘

Each 'Grain Channel' is independent, with a start and stop position
and playback mode. The behaviour of touch/CV is different in each mode:

    - **Gate**: Play while gate is high. Stop and reset on release.
    - **Oneshot**: Trigger full grain on rising edge.
    - **Loop**: Continuously loop from start to end (gated by touch/CV).
    - **LoopOn**: Loop with gate stuck on. Touch/CV controls playback speed.
    - **Bounce**: Ping-pong between start and end (gated by touch/CV).
    - **BounceOn**: Bounce with gate stuck on. Touch/CV controls playback speed.
    - **ScrubFast**: CV scrubs position within grain.
    - **ScrubSlow**: CV scrubs position (with one-pole filter)

When no cable is plugged into a gate input, the corresponding jack
captouch (1/2/3) acts as a gate. If a jack is plugged in, gate trigger
is 2V with 1V hysteresis. Jack CV may also be used to control pitch or
scrub grain position, depending on the playback mode.

Record may be toggled ON and OFF at any time, to bring in new material
and freeze the sample buffer. Alternatively, record may be left permanently
ON and gates triggered while new material is arriving. This can be used for
slewable delayline and Karplus-strong effects (especially in SCRUB mode).

    .. note::

        WARN: saving / loading settings and playback buffers happens to a fixed
        region in SPI flash at the moment, which is a bit slow!

    .. note::

        WARN: pop prevention is not implemented yet, you might need to fiddle
        with the grain start/end positions to get clean gates.

"""

import os
import sys

from amaranth import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.wiring import In, Out, connect, flipped
from amaranth_soc import csr

from tiliqua import dsp, usb_audio
from tiliqua.build import sim
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.dsp import ASQ
from tiliqua.periph import eurorack_pmod, grain_player, delay_line
from tiliqua.tiliqua_soc import TiliquaSoc

class SamplerPeripheral(wiring.Component):

    class Flags(csr.Register, access="rw"):
        record:           csr.Field(csr.action.RW, unsigned(1))

    class ScrubFilterReg(csr.Register, access="rw"):
        ch0: csr.Field(csr.action.RW, unsigned(4))
        ch1: csr.Field(csr.action.RW, unsigned(4))
        ch2: csr.Field(csr.action.RW, unsigned(4))

    def __init__(self):
        regs = csr.Builder(addr_width=5, data_width=8)
        self._flags = regs.add("flags", self.Flags(), offset=0x0)
        self._scrub_filter = regs.add("scrub_filter", self.ScrubFilterReg(), offset=0x4)
        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "record": Out(1),
            "scrub_filter0": Out(unsigned(4)),
            "scrub_filter1": Out(unsigned(4)),
            "scrub_filter2": Out(unsigned(4)),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()

        m.submodules.bridge  = self._bridge
        connect(m, flipped(self.bus), self._bridge.bus)

        m.d.comb += [
            self.record.eq(self._flags.f.record.data),
            self.scrub_filter0.eq(self._scrub_filter.f.ch0.data),
            self.scrub_filter1.eq(self._scrub_filter.f.ch1.data),
            self.scrub_filter2.eq(self._scrub_filter.f.ch2.data),
        ]

        return m

class SamplerSoc(TiliquaSoc):

    # Used by `tiliqua_soc.py` to create a MODULE_DOCSTRING rust constant used by the 'help' page.
    module_docstring = sys.modules[__name__].__doc__

    bitstream_help = BitstreamHelp(
        brief="3-ch granular sampler.",
        io_left=['audio in', 'gate ch0', 'gate ch1', 'gate ch2', 'ch0 out', 'ch1 out', 'ch2 out', 'mix out'],
        io_right=['navigate menu', '', 'video out', '', '', '']
    )

    N_GRAINS            = 3
    DELAYLN_SIZE        = 0x40000   # samples per delay line
    DELAYLN_SIZE_BYTES  = DELAYLN_SIZE * 2  # 2 bytes per i16 sample = 0x80000 (512 KiB)
    DELAYLN_START       = 0x800000  # byte offset in PSRAM (8 MiB)
                                    # be careful not to touch framebuffer or bootinfo!

    PERIPH_BASE = 0x00001000

    def __init__(self, **kwargs):

        super().__init__(finalize_csr_bridge=False, **kwargs)

        self.sampler_periph = SamplerPeripheral()
        self.csr_decoder.add(self.sampler_periph.bus, addr=self.PERIPH_BASE, name=f"sampler_periph")

        # Single shared delay line
        self.delayln = dsp.DelayLine(
            max_delay=self.DELAYLN_SIZE,
            psram_backed=True,
            addr_width_o=self.psram_periph.bus.addr_width,
            base=self.DELAYLN_START,
            write_triggers_read=False)
        self.psram_periph.add_master(self.delayln.bus)
        self.delayln_periph = delay_line.Peripheral(self.delayln, psram_base=self.psram_base)
        self.csr_decoder.add(self.delayln_periph.csr_bus, addr=self.PERIPH_BASE+0x100, name=f"delayln_periph0")

        # 3 grain players sharing the same delay line
        for n in range(self.N_GRAINS):
            grain = grain_player.Peripheral(self.delayln)
            setattr(self, f'grain{n}', grain)
            self.csr_decoder.add(grain.csr_bus, addr=self.PERIPH_BASE+0x200+(n*0x100), name=f"grain_periph{n}")

        self.add_rust_constant(
            f"pub const DELAYLN_SIZE_SAMPLES: usize = 0x{self.DELAYLN_SIZE:x};\n")

        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        m.submodules.sampler_periph = self.sampler_periph
        m.submodules.delayln = self.delayln
        m.submodules.delayln_periph = self.delayln_periph

        for n in range(self.N_GRAINS):
            grain = f'grain{n}'
            setattr(m.submodules, grain, getattr(self, grain))

        # FIXME: bit of a hack so we can pluck out peripherals from `tiliqua_soc`
        m.submodules += super().elaborate(platform)

        pmod0 = self.pmod0_periph.pmod

        # Input 0 -> single shared delay line
        m.submodules.split4 = split4 = dsp.Split(
            n_channels=4, source=pmod0.o_cal)
        # One-pole filters on scrub inputs (shift controlled by CPU)
        for n in range(self.N_GRAINS):
            filt = dsp.OnePole()
            setattr(m.submodules, f'scrub_filter{n}', filt)
            m.d.comb += filt.shift.eq(getattr(self.sampler_periph, f'scrub_filter{n}'))
            wiring.connect(m, split4.o[n + 1], filt.i)
            wiring.connect(m, filt.o, getattr(self, f'grain{n}').scrub)
        with m.If(self.sampler_periph.record):
            wiring.connect(m, split4.o[0], self.delayln.i)
        with m.Else():
            # Drop all incoming samples if not recording
            m.d.comb += split4.o[0].ready.eq(1)

        # Grain taps -> mixing matrix -> outputs
        # Mix channels 0,1,2 to output 3
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)
        for n in range(self.N_GRAINS):
            wiring.connect(m, getattr(self, f'grain{n}').o, merge4.i[n])
        merge4.wire_valid(m, [3])

        m.submodules.output_mix = output_mix = dsp.MatrixMix(
            i_channels=4, o_channels=4,
            coefficients=[[1.0,  0.0,  0.0,  0.33],   # in0 -> out0, out3
                          [0.0,  1.0,  0.0,  0.33],   # in1 -> out1, out3
                          [0.0,  0.0,  1.0,  0.33],   # in2 -> out2, out3
                          [0.0,  0.0,  0.0,  0.0]])   # in3 -> nothing
        wiring.connect(m, merge4.o, output_mix.i)
        wiring.connect(m, output_mix.o, pmod0.i_cal)

        # Hardware gate detectors for CV inputs
        # Channels 0,1,2 use input jacks 1,2,3 respectively (jack 0 is record!)
        for n in range(3):
            jack_idx = n + 1
            gate_det = dsp.GateDetector()
            setattr(m.submodules, f'gate_det{n}', gate_det)
            # TODO: synchronize to audio input stream. not really necessary
            # for gates, tbd if this can cause bugs...
            m.d.comb += [
                gate_det.i.payload.eq(pmod0.calibrator.o_cal_peek[jack_idx]),
                gate_det.i.valid.eq(1),
                gate_det.o.ready.eq(1),
            ]
            grain = getattr(self, f'grain{n}')
            m.d.comb += grain.hw_gate.eq(gate_det.o.payload)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(SamplerSoc, path=this_path, archiver_callback=lambda archiver: archiver.with_option_storage())
