# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Vectorscope/oscilloscope with menu system, USB audio and tunable delay lines.

    - In **vectorscope mode**, rasterize X/Y, intensity and color to a simulated
      CRT, with adjustable beam settings, scale and offset for each channel.

    - In **oscilloscope mode**, all 4 input channels are plotted simultaneosly
      with adjustable timebase, trigger settings and so on.

The channels are assigned as follows:

    .. code-block:: text

                 Vectorscope │ Oscilloscope
        ┌────┐               │
        │in0 │◄─ x           │ channel 0 + trig
        │in1 │◄─ y           │ channel 1
        │in2 │◄─ intensity   │ channel 2
        │in3 │◄─ color       │ channel 3
        └────┘

A USB audio interface, tunable delay lines, and series of switches is included
in the signal path to open up more applications. The overall signal flow looks
like this:

    .. code-block:: text

        in0/x ───────►┌───────┐
        in1/y ───────►│Audio  │
        in2/i ───────►│IN (4x)│
        in3/c ───────►└───┬───┘
                          ▼
                 ┌───◄─[SPLIT]─►────┐
                 │        │         ▼
                 │        ▼  ┌──────────────┐     ┌────────┐
                 │        │  │4in/4out USB  ├────►│Computer│
                 │        │  │Audio I/F     │◄────│(USB2)  │
                 │        │  └──────┬───────┘     └────────┘
                 │        └───┐ ┌───┘
                 │ usb=bypass ▼ ▼ usb=enabled
                 │           [MUX]
                 │      ┌──────────────┐
                 │      │4x Delay Lines│ (tunable)
                 │      └──────┬───────┘
                 │             ▼
                 └────┐ ┌─◄─[SPLIT]─►────┐
                      │ │                │
           src=inputs ▼ ▼ src=outputs    │
                     [MUX]               │
                       │                 ▼
                 ┌─────▼──────┐     ┌────────┬──────► out0
                 │Vectorscope/│     │Audio   ├──────► out1
                 │Oscilloscope│     │OUT (4x)├──────► out2
                 └────────────┘     └────────┴──────► out3

The ``[MUX]`` elements pictured above can be switched by the menu system, for
viewing different parts of the signal path (i.e inputs or outputs to delay
lines, USB streams).  Some usage ideas:

    - With ``plot_src=inputs`` and ``usb_mode=bypass``, we can visualize our
      analog audio inputs.
    - With ``plot_src=outputs`` and ``usb_mode=bypass``, we can visualize our
      analog audio inputs after being affected by the delay lines (this is fun
      to get patterns out of duplicated mono signals)
    - With ``plot_src=outputs`` and ``usb_mode=enable``, we can visualize a USB
      audio stream as it is sent to the analog outputs. This is perfect for
      visualizing oscilloscope music being streamed from a computer.
    - With ``plot_src=inputs`` and ``usb_mode=enable``, we can visualize what we
      are sending back to the computer on our analog inputs.

    .. note::

        The USB audio interface will always enumerate if it is connected to a
        computer, however it is only part of the signal flow if
        ``usb_mode=enabled`` in the menu system.

The following options are tweakable in the menu. Note that the MIDI TRS input
can also be used to control most of these through CCs as follows:

    .. code-block:: text

        Page    Parameter     CC  Description
        ────    ─────────     ──  ───────────
        HELP    scroll         -  scroll help text up/down

                                  (Hint: to hide HELP page --
                                   use 'MISC: help' below)

        VECTOR  x-offset      20  in0 (horizontal deflection) offset
        VECTOR  x-scale       21  in0 (horizontal deflection) volts/div
        VECTOR  y-offset      22  in1 (vertical deflection) offset
        VECTOR  y-scale       23  in1 (vertical deflection) volts/div
        VECTOR  i-offset      24  in2 (beam intensity) offset
        VECTOR  i-scale       25  in2 (beam intensity CV) scale
        VECTOR  c-offset      26  in3 (beam color) offset
        VECTOR  c-scale       27  in4 (beam color CV) scale

        DELAY   delay-x       30  in0/X channel delayline length
        DELAY   delay-y       31  in1/Y channel delayline length
        DELAY   delay-i       32  in2/intensity delayline length
        DELAY   delay-c       33  in3/color delayline length

        BEAM    persist       40  phosphor decay speed (high = slow)
        BEAM    decay         41  phosphor decay amount (low = slow)
        BEAM    rnd-skip      42  probabilistic decay skip (high = more)
        BEAM    ui-hue        43  menu and grid overlay hue
        BEAM    palette       44  color palette
        BEAM    grid          45  grid overlay style
        BEAM    grid-i        46  grid overlay intensity

        MISC    plot-type     50  vectorscope or oscilloscope
        MISC    plot-src      51  plot inputs or outputs
        MISC    usb-mode       -  enable/bypass USB audio
        MISC    rotation      52  screen rotation
        MISC    help           -  show/hide leftmost help page
        MISC    cc-highlight   -  highlight changed on CC input
        MISC    save-opts      -  save all options to flash
        MISC    wipe-opts      -  reset all options to defaults

        SCOPE1  ypos0         60  channel 0 vertical position
        SCOPE1  ypos1         61  channel 1 vertical position
        SCOPE1  ypos2         62  channel 2 vertical position
        SCOPE1  ypos3         63  channel 3 vertical position
        SCOPE1  n-channels    64  number of active channels

        SCOPE2  yscale        70  vertical volts/div
        SCOPE2  timebase      71  horizontal time/div
        SCOPE2  xzoom         72  horizontal zoom
        SCOPE2  trig-mode     73  trigger mode
        SCOPE2  trig-lvl      74  trigger level
        SCOPE2  intensity     75  trace intensity
        SCOPE2  hue           76  trace color

    .. note::

        By default, this core builds for ``48kHz/16bit`` sampling.  However,
        Tiliqua is shipped with ``--fs-192khz`` enabled, which provides much
        higher fidelity plots. If you're feeling adventurous, you can also
        synthesize with the environment variable ``TILIQUA_ASQ_WIDTH=24`` to use
        a completely 24-bit audio path.  This mostly works, but might break the
        scope triggering and use a bit more FPGA resources.

"""

import os
import sys

from amaranth import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.fifo import SyncFIFOBuffered
from amaranth.lib.wiring import In, Out, connect, flipped
from amaranth_soc import csr

from tiliqua import dsp, midi, usb_audio
from tiliqua.build import sim
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.periph import eurorack_pmod
from tiliqua.periph import overlay
from tiliqua.raster import PSQ, scope
from tiliqua.raster.plot import FramebufferPlotter
from tiliqua.tiliqua_soc import TiliquaSoc


class XbeamPeripheral(wiring.Component):

    class Flags(csr.Register, access="w"):
        usb_en:   csr.Field(csr.action.W, unsigned(1))
        usb_connect:   csr.Field(csr.action.W, unsigned(1))
        show_outputs: csr.Field(csr.action.W, unsigned(1))

    class Delay(csr.Register, access="w"):
        value:   csr.Field(csr.action.W, unsigned(16))

    class MidiRead(csr.Register, access="r"):
        msg: csr.Field(csr.action.R, unsigned(32))

    def __init__(self):
        regs = csr.Builder(addr_width=5, data_width=8)
        self._flags = regs.add("flags", self.Flags(), offset=0x0)
        self._delay0 = regs.add("delay0", self.Delay(), offset=0x4)
        self._delay1 = regs.add("delay1", self.Delay(), offset=0x8)
        self._delay2 = regs.add("delay2", self.Delay(), offset=0xC)
        self._delay3 = regs.add("delay3", self.Delay(), offset=0x10)
        self._midi_read = regs.add("midi_read", self.MidiRead(), offset=0x14)
        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "usb_en": Out(1),
            "usb_connect": Out(1),
            "show_outputs": Out(1),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),

            # Streams in/out of plotting delay lines
            "delay_i": In(stream.Signature(data.ArrayLayout(eurorack_pmod.ASQ, 4))),
            "delay_o": Out(stream.Signature(data.ArrayLayout(eurorack_pmod.ASQ, 4))),

            # TRS MIDI input
            "i_midi": In(stream.Signature(midi.MidiMessage)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()

        m.submodules.bridge  = self._bridge
        connect(m, flipped(self.bus), self._bridge.bus)

        with m.If(self._flags.f.usb_en.w_stb):
            m.d.sync += self.usb_en.eq(self._flags.f.usb_en.w_data)

        with m.If(self._flags.f.usb_connect.w_stb):
            m.d.sync += self.usb_connect.eq(self._flags.f.usb_connect.w_data)

        with m.If(self._flags.f.show_outputs.w_stb):
            m.d.sync += self.show_outputs.eq(self._flags.f.show_outputs.w_data)

        # Tweakable plotting delay lines.
        m.submodules.split4 = split4 = dsp.Split(n_channels=4, source=wiring.flipped(self.delay_i))
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4, sink=wiring.flipped(self.delay_o))
        delay = [Signal(16) for _ in range(4)]
        for ch in range(4):
            delayln = dsp.DelayLine(max_delay=512, write_triggers_read=False)
            split2 = dsp.Split(n_channels=2, source=split4.o[ch], replicate=True)
            m.submodules += [delayln, split2]
            tap = delayln.add_tap()
            wiring.connect(m, split2.o[0], delayln.i)
            m.d.comb += [
                tap.i.valid.eq(split2.o[1].valid),
                split2.o[1].ready.eq(tap.i.ready),
                tap.i.payload.eq(delay[ch])
            ]
            wiring.connect(m, tap.o, merge4.i[ch])
            field = getattr(self, f'_delay{ch}')
            with m.If(field.f.value.w_stb):
                m.d.sync += delay[ch].eq(field.f.value.w_data)

        # TRS MIDI -> SoC read FIFO
        m.submodules.read_midi_fifo = read_midi_fifo = SyncFIFOBuffered(
            width=24, depth=8)
        m.d.comb += [
            self.i_midi.ready.eq(1),
            read_midi_fifo.w_data.eq(self.i_midi.payload),
            read_midi_fifo.w_en.eq(self.i_midi.valid),
            read_midi_fifo.r_en.eq(self._midi_read.element.r_stb),
        ]
        with m.If(read_midi_fifo.r_level != 0):
            m.d.comb += self._midi_read.f.msg.r_data.eq(read_midi_fifo.r_data)
        with m.Else():
            m.d.comb += self._midi_read.f.msg.r_data.eq(0)

        return m

class XbeamSoc(TiliquaSoc):

    # Used by `tiliqua_soc.py` to create a MODULE_DOCSTRING rust constant used by the 'help' page.
    module_docstring = sys.modules[__name__].__doc__

    # Stored in manifest and used by bootloader for brief summary of each bitstream.
    bitstream_help = BitstreamHelp(
        brief="Scope / Vectorscope / USB audio.",
        io_left=['x / in0', 'y / in1', 'intensity / in2', 'color / in3', 'out0', 'out1', 'out2', 'out3'],
        io_right=['navigate menu', '4x4 audio device', 'video out', '', '', '']
    )

    def __init__(self, **kwargs):

        self.overlay_periph = overlay.Peripheral()

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False,
                         fb_overlay=self.overlay_periph.overlay, **kwargs)

        # Extract module docstring for help page

        self.vector_periph_base = 0x00001000
        self.scope_periph_base  = 0x00001100
        self.xbeam_periph_base  = 0x00001200
        self.overlay_periph_base = 0x00001300

        # Dedicated framebuffer plotter for scope peripherals (5 ports: 1 vector + 4 scope channels)
        self.plotter = FramebufferPlotter(
            bus_signature=self.psram_periph.bus.signature.flip(), n_ports=5)
        self.psram_periph.add_master(self.plotter.bus)

        self.n_upsample = 8 if self.clock_settings.audio_clock.is_192khz() else 32

        # Vectorscope with CSR registers
        self.vector_periph = scope.VectorPeripheral()
        self.csr_decoder.add(self.vector_periph.bus, addr=self.vector_periph_base, name="vector_periph")

        # 4-ch oscilloscope with CSR registers
        self.scope_periph = scope.ScopePeripheral(
            fs=self.clock_settings.audio_clock.fs() * self.n_upsample)
        self.csr_decoder.add(self.scope_periph.bus, addr=self.scope_periph_base, name="scope_periph")

        # Extra peripheral for some global control flags.
        self.xbeam_periph = XbeamPeripheral()
        self.csr_decoder.add(self.xbeam_periph.bus, addr=self.xbeam_periph_base, name="xbeam_periph")

        # Grid overlay peripheral
        self.csr_decoder.add(self.overlay_periph.bus, addr=self.overlay_periph_base, name="overlay_periph")

        # now we can freeze the memory map
        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        # Scope plotting infrastructure
        m.submodules.plotter = self.plotter

        # Scope peripherals
        m.submodules.vector_periph = self.vector_periph
        m.submodules.scope_periph = self.scope_periph
        m.submodules.xbeam_periph = self.xbeam_periph
        m.submodules.overlay_periph = self.overlay_periph

        # Connect vector/scope pixel requests to plotter channels
        wiring.connect(m, self.vector_periph.o, self.plotter.i[0])
        for n in range(4):
            wiring.connect(m, self.scope_periph.o[n], self.plotter.i[n+1])

        # Connect framebuffer properties to plotter backend
        wiring.connect(m, wiring.flipped(self.fb.fbp), self.plotter.fbp)

        # FIXME: bit of a hack so we can pluck out peripherals from `tiliqua_soc`
        m.submodules += super().elaborate(platform)

        pmod0 = self.pmod0_periph.pmod

        if sim.is_hw(platform):
            m.submodules.usbif = usbif = usb_audio.USB2AudioInterface(
                    audio_clock=self.clock_settings.audio_clock, nr_channels=4)
            # SoC-controlled USB PHY connection (based on typeC CC status)
            m.d.comb += usbif.usb_connect.eq(self.xbeam_periph.usb_connect)

            # TRS MIDI
            midi_pins = platform.request("midi")
            m.submodules.serialrx = serialrx = midi.SerialRx(
                    system_clk_hz=60e6, pins=midi_pins)
            m.submodules.midi_decode = midi_decode = midi.MidiDecodeSerial()
            wiring.connect(m, serialrx.o, midi_decode.i)
            wiring.connect(m, midi_decode.o, self.xbeam_periph.i_midi)

        with m.If(self.xbeam_periph.usb_en):
            if sim.is_hw(platform):
                wiring.connect(m, pmod0.o_cal, usbif.i)
                wiring.connect(m, usbif.o, self.xbeam_periph.delay_i)
            else:
                pass
        with m.Else():
            wiring.connect(m, pmod0.o_cal, self.xbeam_periph.delay_i)

        wiring.connect(m, self.xbeam_periph.delay_o, pmod0.i_cal)

        m.submodules.plot_fifo = plot_fifo = dsp.SyncFIFOBuffered(
            shape=data.ArrayLayout(PSQ, 4), depth=256)

        with m.If(self.xbeam_periph.show_outputs):
            dsp.connect_peek(m, pmod0.i_cal, plot_fifo.i)
        with m.Else():
            dsp.connect_peek(m, pmod0.o_cal, plot_fifo.i)

        # Upsample all 4 channels before routing to scope/vector peripherals
        fs = self.clock_settings.audio_clock.fs()
        m.submodules.up_split4 = up_split4 = dsp.Split(n_channels=4, source=plot_fifo.o, shape=PSQ)
        m.submodules.up_merge4 = up_merge4 = dsp.Merge(n_channels=4, shape=PSQ)
        for ch in range(4):
            r = dsp.Resample(fs_in=fs, n_up=self.n_upsample, m_down=1, shape=PSQ)
            setattr(m.submodules, f"resample{ch}", r)
            wiring.connect(m, up_split4.o[ch], r.i)
            wiring.connect(m, r.o, up_merge4.i[ch])

        with m.If(self.scope_periph.soc_en):
            wiring.connect(m, up_merge4.o, self.scope_periph.i)
        with m.Else():
            wiring.connect(m, up_merge4.o, self.vector_periph.i)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(XbeamSoc, path=this_path, archiver_callback=lambda archiver: archiver.with_option_storage())
