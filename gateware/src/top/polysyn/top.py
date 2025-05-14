# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
8-voice polyphonic synthesizer with video display and menu system.

The synthesizer can be controlled through touching jacks 0-5 or using a
MIDI keyboard through TRS midi. The control source must be selected in
the menu system.

In touch mode, the touch magnitude controls the filter envelopes of
each voice. In MIDI mode, the velocity of each note as well as the
value of the modulation wheel affects the filter envelopes.

Output audio is sent to output channels 2 and 3 (last 2 jacks).

Input jack 0 also controls phase modulation of all oscillators,
so you can patch input jack 0 to an LFO for retro-sounding slow
vibrato, or to an oscillator for some wierd FM effects.

A block diagram of the core components of this polysynth:

.. image:: /_static/polysynth.png
  :width: 800

"""

import logging
import os
import sys
import math

from amaranth                  import *
from amaranth.lib              import wiring, data, stream
from amaranth.lib.wiring       import In, Out, connect, flipped
from amaranth.lib.fifo         import SyncFIFOBuffered

from amaranth_soc              import csr

from amaranth_future           import fixed

from tiliqua                   import eurorack_pmod, dsp, mac, midi, scope, sim, delay
from tiliqua.delay_line        import DelayLine
from tiliqua.eurorack_pmod     import ASQ
from tiliqua.tiliqua_soc       import TiliquaSoc
from tiliqua.cli               import top_level_cli
from tiliqua.usb_host          import SimpleUSBMIDIHost

class Diffuser(wiring.Component):

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    def __init__(self):
        super().__init__()

        # 4 delay lines, backed by 4 independent SRAM banks.

        self.delay_lines = [
            DelayLine(max_delay=2048),
            DelayLine(max_delay=4096),
            DelayLine(max_delay=8192),
            DelayLine(max_delay=8192),
        ]

        self.diffuser = delay.Diffuser(self.delay_lines)

        # Coefficients of this are tweaked by the SoC

        self.matrix   = self.diffuser.matrix_mix

    def elaborate(self, platform):
        m = Module()

        dsp.named_submodules(m.submodules, self.delay_lines)

        m.submodules.diffuser = self.diffuser

        wiring.connect(m, wiring.flipped(self.i), self.diffuser.i)
        wiring.connect(m, self.diffuser.o, wiring.flipped(self.o))

        return m

class PolySynth(wiring.Component):

    N_VOICES = 8

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    i_midi: In(stream.Signature(midi.MidiMessage))

    drive: In(unsigned(16))
    reso: In(unsigned(16))

    voice_states: Out(midi.MidiVoice).array(N_VOICES)

    def elaborate(self, platform):
        m = Module()

        # supported simultaneous voices
        n_voices = self.N_VOICES

        m.submodules.voice_tracker = voice_tracker = midi.MidiVoiceTracker(
            max_voices=n_voices, velocity_mod=True, zero_velocity_gate=True)
        # 1 oscillator and filter per oscillator
        ncos = [dsp.SawNCO(shift=0) for _ in range(n_voices)]

        # All SVFs share the same multiplier tile through a RingMAC.
        m.submodules.server = server = mac.RingMACServer()
        svfs = [dsp.SVF(macp=server.new_client()) for _ in range(n_voices)]

        m.submodules.merge = merge = dsp.Merge(n_channels=n_voices)

        dsp.named_submodules(m.submodules, ncos)
        dsp.named_submodules(m.submodules, svfs)

        # Connect MIDI stream -> voice tracker
        wiring.connect(m, wiring.flipped(self.i_midi), voice_tracker.i)

        # analog ins
        m.submodules.cv_in = cv_in = dsp.Split(
                n_channels=4, source=wiring.flipped(self.i))
        cv_in.wire_ready(m, [2, 3])

        for n in range(n_voices):

            m.d.comb += self.voice_states[n].eq(voice_tracker.o[n])

            # Connect audio in -> NCO.i
            dsp.connect_remap(m, cv_in.o[0], ncos[n].i, lambda o, i : [
                # For fun, phase mod on audio in #0
                i.payload.phase   .eq(o.payload),
                i.payload.freq_inc.eq(voice_tracker.o[n].freq_inc)
            ])

            # Simple counting smoother for the filter cutoff.
            follower = dsp.CountingFollower(bits=8)
            m.submodules += follower
            m.d.comb += [
                follower.i.valid.eq(cv_in.o[0].valid), # hack to clock at audio rate
                follower.i.payload.eq(voice_tracker.o[n].velocity_mod),
                follower.o.ready.eq(1)
            ]

            # Connect voice.vel and NCO.o -> SVF.
            dsp.connect_remap(m, ncos[n].o, svfs[n].i, lambda o, i : [
                i.payload.x                    .eq(o.payload >> 1),
                i.payload.resonance.as_value().eq(self.reso),
                i.payload.cutoff               .eq(follower.o.payload << 5)
            ])

            # Connect SVF LPF -> merge channel
            dsp.connect_remap(m, svfs[n].o, merge.i[n], lambda o, i : [
                i.payload.eq(o.payload.lp),
            ])

        # Voice mixdown to stereo. Alternate left/right
        o_channels = 2
        coefficients = [[0.75*o_channels/n_voices, 0.0                ],
                        [0.0,                      0.75*o_channels/n_voices]] * (n_voices // 2)
        m.submodules.matrix_mix = matrix_mix = dsp.MatrixMix(
            i_channels=n_voices, o_channels=o_channels,
            coefficients=coefficients)
        wiring.connect(m, merge.o, matrix_mix.i),

        # Output diffuser

        m.submodules.diffuser = diffuser = Diffuser()
        self.diffuser = diffuser

        # Stereo HPF to remove DC from any voices in 'zero cutoff'
        # Route to audio output channels 2 & 3

        output_hpfs = [dsp.DCBlock() for _ in range(o_channels)]
        dsp.named_submodules(m.submodules, output_hpfs, override_name="output_hpf")

        m.submodules.hpf_split2 = hpf_split2 = dsp.Split(n_channels=2, source=matrix_mix.o)
        m.submodules.hpf_merge4 = hpf_merge4 = dsp.Merge(n_channels=4, sink=diffuser.i)
        hpf_merge4.wire_valid(m, [0, 1])

        for lr in [0, 1]:
            wiring.connect(m, hpf_split2.o[lr], output_hpfs[lr].i)
            wiring.connect(m, output_hpfs[lr].o, hpf_merge4.i[2+lr])

        # Implement stereo distortion effect after diffuser.

        m.submodules.diffuser_split4 = diffuser_split4 = dsp.Split(
                n_channels=4, source=diffuser.o)
        diffuser_split4.wire_ready(m, [0, 1])

        m.submodules.cv_gain_split2 = cv_gain_split2 = dsp.Split(
                n_channels=2, replicate=True, source=cv_in.o[1])

        def scaled_tanh(x):
            return math.tanh(3.0*x)

        outs = []
        for lr in [0, 1]:
            vca = dsp.VCA()
            waveshaper = dsp.WaveShaper(lut_function=scaled_tanh)
            vca_merge2 = dsp.Merge(n_channels=2)
            setattr(m.submodules, f"out_gainvca_{lr}", vca)
            setattr(m.submodules, f"out_waveshaper_{lr}", waveshaper)
            setattr(m.submodules, f"out_vca_merge2_{lr}", vca_merge2)

            wiring.connect(m, diffuser_split4.o[2+lr], vca_merge2.i[0])
            wiring.connect(m, cv_gain_split2.o[lr],    vca_merge2.i[1])

            dsp.connect_remap(m, vca_merge2.o, vca.i, lambda o, i : [
                i.payload[0].eq(o.payload[0]),
                i.payload[1].eq(self.drive << 2)
            ])

            wiring.connect(m, vca.o, waveshaper.i)
            outs.append(waveshaper.o)

        # Final outputs on channel 2, 3
        m.submodules.merge4 = merge4 = dsp.Merge(
                n_channels=4, sink=wiring.flipped(self.o))
        merge4.wire_valid(m, [0, 1])
        wiring.connect(m, outs[0], merge4.i[2])
        wiring.connect(m, outs[1], merge4.i[3])

        return m

class SynthPeripheral(wiring.Component):

    class Drive(csr.Register, access="w"):
        value: csr.Field(csr.action.W, unsigned(16))

    class Reso(csr.Register, access="w"):
        value: csr.Field(csr.action.W, unsigned(16))

    class Voice(csr.Register, access="r"):
        note:   csr.Field(csr.action.R, unsigned(8))
        cutoff: csr.Field(csr.action.R, unsigned(8))

    class Matrix(csr.Register, access="w"):
        """Mixing matrix coefficient: commit on write strobe, MatrixBusy set until done."""
        o_x:   csr.Field(csr.action.W, unsigned(4))
        i_y:   csr.Field(csr.action.W, unsigned(4))
        value: csr.Field(csr.action.W, signed(24))

    class MatrixBusy(csr.Register, access="r"):
        busy: csr.Field(csr.action.R, unsigned(1))

    class MidiWrite(csr.Register, access="w"):
        msg: csr.Field(csr.action.W, unsigned(32))

    class MidiRead(csr.Register, access="r"):
        msg: csr.Field(csr.action.R, unsigned(32))

    class UsbMidiHost(csr.Register, access="w"):
        """USB MIDI host settings."""
        # 0 = off. 1 = enable VBUS and forward USB MIDI.
        host:     csr.Field(csr.action.W, unsigned(1))

    class UsbMidiCfg(csr.Register, access="w"):
        # Hardcoded MIDI streaming endpoint location (device specific)
        value: csr.Field(csr.action.W, unsigned(4))

    def __init__(self, synth=None):
        self.synth = synth
        regs = csr.Builder(addr_width=7, data_width=8)
        voices_csr_end = 0x8+PolySynth.N_VOICES*4
        self._drive         = regs.add("drive",         self.Drive(),        offset=0x0)
        self._reso          = regs.add("reso",          self.Reso(),         offset=0x4)
        self._voices        = [regs.add(f"voices{i}",   self.Voice(),
                               offset=0x8+i*4) for i in range(PolySynth.N_VOICES)]
        self._matrix        = regs.add("matrix",        self.Matrix(),       offset=voices_csr_end + 0x0)
        self._matrix_busy   = regs.add("matrix_busy",   self.MatrixBusy(),   offset=voices_csr_end + 0x4)
        self._midi_write    = regs.add("midi_write",    self.MidiWrite(),    offset=voices_csr_end + 0x8)
        self._midi_read     = regs.add("midi_read",     self.MidiRead(),     offset=voices_csr_end + 0xC)
        self._midi_host     = regs.add("usb_midi_host", self.UsbMidiHost(),  offset=voices_csr_end + 0x10)
        self._midi_cfg      = regs.add("usb_midi_cfg",  self.UsbMidiCfg(),   offset=voices_csr_end + 0x14)
        self._midi_endp     = regs.add("usb_midi_endp", self.UsbMidiCfg(),   offset=voices_csr_end + 0x18)
        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "i_midi": In(stream.Signature(midi.MidiMessage)),
            "usb_midi_host": Out(1),
            "usb_midi_cfg_id": Out(4),
            "usb_midi_endpt_id": Out(4),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        connect(m, flipped(self.bus), self._bridge.bus)

        # top-level tweakables
        with m.If(self._drive.f.value.w_stb):
            m.d.sync += self.synth.drive.eq(self._drive.f.value.w_data)
        with m.If(self._reso.f.value.w_stb):
            m.d.sync += self.synth.reso.eq(self._reso.f.value.w_data)

        # USB MIDI flags
        with m.If(self._midi_host.f.host.w_stb):
            m.d.sync += self.usb_midi_host.eq(self._midi_host.f.host.w_data)
        with m.If(self._midi_cfg.f.value.w_stb):
            m.d.sync += self.usb_midi_cfg_id.eq(self._midi_cfg.f.value.w_data)
        with m.If(self._midi_endp.f.value.w_stb):
            m.d.sync += self.usb_midi_endpt_id.eq(self._midi_endp.f.value.w_data)

        # voice tracking
        for i, voice in enumerate(self._voices):
            m.d.comb += [
                voice.f.note.r_data  .eq(self.synth.voice_states[i].note),
                voice.f.cutoff.r_data.eq(self.synth.voice_states[i].velocity_mod)
            ]

        # matrix coefficient update logic
        matrix_busy = Signal()
        m.d.comb += self._matrix_busy.f.busy.r_data.eq(matrix_busy)
        with m.If(self._matrix.element.w_stb & ~matrix_busy):
            m.d.sync += [
                matrix_busy.eq(1),
                self.synth.diffuser.matrix.c.payload.o_x         .eq(self._matrix.f.o_x.w_data),
                self.synth.diffuser.matrix.c.payload.i_y         .eq(self._matrix.f.i_y.w_data),
                self.synth.diffuser.matrix.c.payload.v.as_value().eq(self._matrix.f.value.w_data),
                self.synth.diffuser.matrix.c.valid.eq(1),
            ]
        with m.If(matrix_busy & self.synth.diffuser.matrix.c.ready):
            # coefficient has been written
            m.d.sync += [
                matrix_busy.eq(0),
                self.synth.diffuser.matrix.c.valid.eq(0),
            ]

        # MIDI injection and arbiter between SoC MIDI and HW MIDI -> synth MIDI.
        m.submodules.soc_midi_fifo = soc_midi_fifo = SyncFIFOBuffered(
            width=24, depth=8)
        m.d.comb += [
            soc_midi_fifo.w_data.eq(self._midi_write.f.msg.w_data),
            soc_midi_fifo.w_en.eq(self._midi_write.element.w_stb),
        ]
        wiring.connect(m, wiring.flipped(self.i_midi), self.synth.i_midi)
        with m.If(soc_midi_fifo.r_stream.valid):
            wiring.connect(m, soc_midi_fifo.r_stream, self.synth.i_midi)

        # Pipe TRS MIDI -> SoC read FIFO so SoC can inspect external
        # MIDI traffic
        m.submodules.read_midi_fifo = read_midi_fifo = SyncFIFOBuffered(
            width=24, depth=8)
        m.d.comb += [
            read_midi_fifo.w_data.eq(self.i_midi.payload),
            read_midi_fifo.w_en.eq(self.i_midi.valid & self.i_midi.ready),
            read_midi_fifo.r_en.eq(self._midi_read.element.r_stb),
        ]

        with m.If(read_midi_fifo.r_level != 0):
            m.d.comb += self._midi_read.f.msg.r_data.eq(read_midi_fifo.r_data)
        with m.Else():
            m.d.comb += self._midi_read.f.msg.r_data.eq(0)


        return m

class PolySoc(TiliquaSoc):

    brief = "Polyphonic synthesizer, touch & MIDI control."

    def __init__(self, **kwargs):

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False, **kwargs)

        # WARN: TiliquaSoc ends at 0x00000900
        self.vector_periph_base = 0x00001000
        self.synth_periph_base  = 0x00001100

        self.vector_periph = scope.VectorTracePeripheral(
            fb=self.fb,
            bus_dma=self.psram_periph,
            fs=48000,
            n_upsample=8)
        self.csr_decoder.add(self.vector_periph.bus, addr=self.vector_periph_base, name="vector_periph")

        # synth controls
        self.synth_periph = SynthPeripheral()
        self.csr_decoder.add(self.synth_periph.bus, addr=self.synth_periph_base, name="synth_periph")

        self.add_rust_constant(
            f"pub const N_VOICES: usize = {PolySynth.N_VOICES};\n")

        # now we can freeze the memory map
        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        m.submodules.vector_periph = self.vector_periph

        m.submodules.polysynth = polysynth = PolySynth()
        self.synth_periph.synth = polysynth

        m.submodules.synth_periph = self.synth_periph

        m.submodules += super().elaborate(platform)

        pmod0 = self.pmod0_periph.pmod

        if sim.is_hw(platform):
            # Polysynth hardware MIDI sources

            # TRS MIDI (serial)
            midi_pins = platform.request("midi")
            m.submodules.serialrx = serialrx = midi.SerialRx(
                    system_clk_hz=60e6, pins=midi_pins)
            m.submodules.midi_decode_trs = midi_decode_trs = midi.MidiDecode()
            wiring.connect(m, serialrx.o, midi_decode_trs.i)

            # USB MIDI host (experimental)
            ulpi = platform.request(platform.default_usb_connection)
            m.submodules.usb = usb = SimpleUSBMIDIHost(
                    bus=ulpi,
                    hardcoded_configuration_id=1,
                    hardcoded_midi_endpoint=1,
            )
            m.submodules.midi_decode_usb = midi_decode_usb = midi.MidiDecode(usb=True)
            wiring.connect(m, usb.o_midi_bytes, midi_decode_usb.i)
            m.d.comb += [
                usb.configuration_id.eq(self.synth_periph.usb_midi_cfg_id),
                usb.midi_endpoint_id.eq(self.synth_periph.usb_midi_endpt_id),
            ]

            # Only enable VBUS if MIDI HOST is enabled.
            vbus_o = platform.request("usb_vbus_en").o
            with m.If(self.synth_periph.usb_midi_host):
                wiring.connect(m, midi_decode_usb.o, self.synth_periph.i_midi)
                m.d.comb += vbus_o.eq(1)
            with m.Else():
                wiring.connect(m, midi_decode_trs.o, self.synth_periph.i_midi)
                m.d.comb += vbus_o.eq(0)

        # polysynth audio
        wiring.connect(m, pmod0.o_cal, polysynth.i)
        wiring.connect(m, polysynth.o, pmod0.i_cal)

        with m.If(self.vector_periph.soc_en):
            # polysynth out -> vectorscope TODO use true split
            m.d.comb += [
                self.vector_periph.i.valid.eq(polysynth.o.valid),
                self.vector_periph.i.payload[0].eq(polysynth.o.payload[2]),
                self.vector_periph.i.payload[1].eq(polysynth.o.payload[3]),
            ]

        # Memory controller hangs if we start making requests to it straight away.
        with m.If(self.permit_bus_traffic):
            m.d.sync += self.vector_periph.en.eq(1)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(PolySoc, path=this_path)
