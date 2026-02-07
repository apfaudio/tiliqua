# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
3-channel sampler with CV+touch control.

Record audio into 3 independent sample buffers (~5 sec each).
Select start, length of a grain in each sample buffer. Trigger grains
via CV, captouch, or set them to loop automatically.

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

When gate is in 'touch-cv' mode and no cable is plugged into a gate input, the
corresponding jack captouch (1/2/3) acts as a gate instead. If a jack is
plugged in, trigger level is 2V with 1V hysteresis.

    .. note::

        Recording is always from input 0. Select which channel to record to
        by navigating to that channel's page and toggling 'record'.

Gate control modes are:

    - **Gate**: Play while gate is high. Stop and reset on release.
    - **Oneshot**: Trigger full grain on rising edge. No retrigger mid-grain.
    - **Loop**: Continuously loop from start to end.
    - **Bounce**: Ping-pong between start and end (forward/reverse).

    .. note::

        WARN: pop prevention is not implemented yet, you might need to fiddle
        with the grain start/end positions to get clean gates.

    .. note::

        WARN: saving / loading settings or playback buffers is not implemented
        yet!! I need to do some work on the SPI flash peripheral before this
        is possible.

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
from tiliqua.periph import eurorack_pmod, grain_player, delay_line
from tiliqua.tiliqua_soc import TiliquaSoc

class GateDetector(wiring.Component):
    """Detect gate transitions from a CV input with hysteresis."""

    i: In(signed(16))
    gate: Out(1)

    def __init__(self, threshold_on=8000, threshold_off=4000):
        self.threshold_on = threshold_on
        self.threshold_off = threshold_off
        super().__init__()

    def elaborate(self, platform):
        m = Module()
        gate_reg = Signal(init=0)
        m.d.comb += self.gate.eq(gate_reg)

        with m.If(gate_reg):
            with m.If(self.i < self.threshold_off):
                m.d.sync += gate_reg.eq(0)
        with m.Else():
            with m.If(self.i > self.threshold_on):
                m.d.sync += gate_reg.eq(1)

        return m


class SamplerPeripheral(wiring.Component):

    class Flags(csr.Register, access="rw"):
        record:           csr.Field(csr.action.RW, unsigned(1))
        record_channel:   csr.Field(csr.action.RW, unsigned(2))

    def __init__(self):
        regs = csr.Builder(addr_width=5, data_width=8)
        self._flags = regs.add("flags", self.Flags(), offset=0x0)
        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "record": Out(1),
            "record_channel": Out(2),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()

        m.submodules.bridge  = self._bridge
        connect(m, flipped(self.bus), self._bridge.bus)

        m.d.comb += [
            self.record.eq(self._flags.f.record.data),
            self.record_channel.eq(self._flags.f.record_channel.data),
        ]

        return m

class SamplerSoc(TiliquaSoc):

    __doc__ = sys.modules[__name__].__doc__

    bitstream_help = BitstreamHelp(
        brief="3-ch granular sampler.",
        io_left=['audio in', 'gate ch0', 'gate ch1', 'gate ch2', 'ch0 out', 'ch1 out', 'ch2 out', 'mix out'],
        io_right=['navigate menu', '', 'video out', '', '', '']
    )

    N_DELAYLINES        = 4
    DELAYLN_SIZE        = 0x40000   # samples per delay line
    DELAYLN_SIZE_BYTES  = DELAYLN_SIZE * 2  # 2 bytes per i16 sample = 0x80000 (512 KiB)
    DELAYLN_START       = 0x800000  # byte offset in PSRAM (8 MiB)
                                    # be careful not to touch framebuffer or bootinfo!

    PERIPH_BASE = 0x00001000

    def __init__(self, **kwargs):

        super().__init__(finalize_csr_bridge=False, **kwargs)

        self.sampler_periph = SamplerPeripheral()
        self.csr_decoder.add(self.sampler_periph.bus, addr=self.PERIPH_BASE, name=f"sampler_periph")

        grain_periph_base = self.PERIPH_BASE + 0x100
        for n in range(self.N_DELAYLINES):
            delayln = dsp.DelayLine(
                max_delay=self.DELAYLN_SIZE,
                psram_backed=True,
                addr_width_o=self.psram_periph.bus.addr_width,
                base=self.DELAYLN_START + (n * self.DELAYLN_SIZE_BYTES),
                write_triggers_read=False)
            setattr(self, f'delayln{n}', delayln)
            self.psram_periph.add_master(delayln.bus)
            delayln_periph = delay_line.Peripheral(delayln, psram_base=self.psram_base)
            setattr(self, f'delayln_periph{n}', delayln_periph)
            self.csr_decoder.add(delayln_periph.csr_bus, addr=grain_periph_base+(n*0x200), name=f"delayln_periph{n}")
            grain = grain_player.Peripheral(delayln)
            setattr(self, f'grain{n}', grain)
            self.csr_decoder.add(grain.csr_bus, addr=grain_periph_base+(n*0x200+0x100), name=f"grain_periph{n}")

        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        m.submodules.sampler_periph = self.sampler_periph

        for n in range(self.N_DELAYLINES):
            delayln = f'delayln{n}'
            setattr(m.submodules, delayln, getattr(self, delayln))
            delayln_periph = f'delayln_periph{n}'
            setattr(m.submodules, delayln_periph, getattr(self, delayln_periph))
            grain = f'grain{n}'
            setattr(m.submodules, grain, getattr(self, grain))

        # FIXME: bit of a hack so we can pluck out peripherals from `tiliqua_soc`
        m.submodules += super().elaborate(platform)

        pmod0 = self.pmod0_periph.pmod

        # Input 0 -> record ch N muxing
        m.submodules.split4 = split4 = dsp.Split(
            n_channels=4, source=pmod0.o_cal)
        split4.wire_ready(m, [1, 2, 3])
        with m.If(self.sampler_periph.record):
            with m.Switch(self.sampler_periph.record_channel):
                for n in range(self.N_DELAYLINES):
                    with m.Case(n):
                        wiring.connect(m, split4.o[0], getattr(self, f'delayln{n}').i)
        with m.Else():
            # Drop all incoming samples if not recording
            m.d.comb += split4.o[0].ready.eq(1)

        # Grain taps -> mixing matrix -> outputs
        # Mix channels 0,1,2 to output 3
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4)
        for n in range(self.N_DELAYLINES):
            wiring.connect(m, getattr(self, f'grain{n}').o, merge4.i[n])

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
            gate_det = GateDetector(threshold_on=8000, threshold_off=4000)
            setattr(m.submodules, f'gate_det{n}', gate_det)
            # Feed CV input to gate detector, connect detector to hw_gate
            m.d.comb += gate_det.i.eq(pmod0.calibrator.o_cal_peek[jack_idx])
            grain = getattr(self, f'grain{n}')
            m.d.comb += grain.hw_gate.eq(gate_det.gate)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(SamplerSoc, path=this_path, archiver_callback=lambda archiver: archiver.with_option_storage())
