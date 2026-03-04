# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Vectorscope/oscilloscope with menu system, USB audio and optional expander PMODs.

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

A USB audio interface and a series of switches is included in the signal path
to open up more applications. The overall signal flow looks like this:

    .. code-block:: text

    (repeated for every 4x4 channels, all shared on USB I/F, select
    channel for visualization with MISC->plot_io option)

        in0/x ───────►┌───────┐
        in1/y ───────►│Audio  │
        in2/i ───────►│IN (4x)│
        in3/c ───────►└───┬───┘
                          ▼
                 ┌───◄─[SPLIT]─►────┐
                 │        │         ▼ (USB interface for all channels shared)
                 │        ▼  ┌──────────────┐     ┌────────┐
                 │        │  │Xin/Xout USB  ├────►│Computer│
                 │        │  │Audio I/F     │◄────│(USB2)  │
                 │        │  └──────┬───────┘     └────────┘
                 │        └───┐ ┌───┘
                 │ usb=bypass ▼ ▼ usb=enabled
                 │           [MUX]
                 │             │
                 └────┐ ┌──────┘
                      │ │
           src=inputs ▼ ▼ src=outputs
                     [MUX]
                       │
                 ┌─────▼──────┐     ┌────────┬──────► out0
                 │Vectorscope/│     │Audio   ├──────► out1
                 │Oscilloscope│     │OUT (4x)├──────► out2
                 └────────────┘     └────────┴──────► out3

The ``[MUX]`` elements pictured above can be switched by the menu system, for
viewing different parts of the signal path.  Some usage ideas:

    - With ``plot_src=inputs`` and ``usb_mode=bypass``, we can visualize our
      analog audio inputs.
    - With ``plot_src=outputs`` and ``usb_mode=enable``, we can visualize a USB
      audio stream as it is sent to the analog outputs. This is perfect for
      visualizing oscilloscope music being streamed from a computer.
    - With ``plot_src=inputs`` and ``usb_mode=enable``, we can visualize what we
      are sending back to the computer on our analog inputs.
    - With expanders enabled and ``plot_io=ex0``, we can visualize audio on an
      expander board instead of the builtin PMOD.

    .. note::

        The USB audio interface will always enumerate if it is connected to a
        computer, however it is only part of the signal flow if
        ``usb_mode=enabled`` in the menu system.

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
from amaranth.lib.wiring import In, Out, connect, flipped
from amaranth_soc import csr

from tiliqua import dsp, usb_audio
from tiliqua.build import sim
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.periph import eurorack_pmod, i2c
from tiliqua.periph import overlay
from tiliqua.raster import PSQ, scope
from tiliqua.raster.plot import FramebufferPlotter
from tiliqua.tiliqua_soc import TiliquaSoc


class XbeamPeripheral(wiring.Component):

    class Flags(csr.Register, access="w"):
        usb_en:   csr.Field(csr.action.W, unsigned(1))
        usb_connect:   csr.Field(csr.action.W, unsigned(1))
        show_outputs: csr.Field(csr.action.W, unsigned(1))
        plot_io: csr.Field(csr.action.W, unsigned(2))

    def __init__(self):
        regs = csr.Builder(addr_width=5, data_width=8)
        self._flags = regs.add("flags", self.Flags(), offset=0x0)
        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "usb_en": Out(1),
            "usb_connect": Out(1),
            "show_outputs": Out(1),
            "plot_io": Out(2),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
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

        with m.If(self._flags.f.plot_io.w_stb):
            m.d.sync += self.plot_io.eq(self._flags.f.plot_io.w_data)

        return m

class XbeamSoc(TiliquaSoc):

    # Used by `tiliqua_soc.py` to create a MODULE_DOCSTRING rust constant used by the 'help' page.
    __doc__ = sys.modules[__name__].__doc__

    # Stored in manifest and used by bootloader for brief summary of each bitstream.
    bitstream_help = BitstreamHelp(
        brief="Scope / Vectorscope / USB audio.",
        io_left=['x / in0', 'y / in1', 'intensity / in2', 'color / in3', 'out0', 'out1', 'out2', 'out3'],
        io_right=['navigate menu', '12x12 audio', 'video out', 'ex0 (ch3-7)', 'ex1 (ch8-11)', '']
    )

    def __init__(self, **kwargs):

        self.expander_ex0 = kwargs.pop("expander_ex0", False)
        self.expander_ex1 = kwargs.pop("expander_ex1", False)
        self.nr_channels = 4 + 4*self.expander_ex0 + 4*self.expander_ex1

        self.overlay_periph = overlay.Peripheral()

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False,
                         fb_overlay=self.overlay_periph.overlay, **kwargs)

        if self.clock_settings.audio_clock.is_192khz():
            assert self.nr_channels <= 8, \
                f"192kHz supports at most 8 channels (1024B packet limit), got {self.nr_channels}"

        if self.expander_ex0:
            self.ex0_pmod = eurorack_pmod.EurorackPmod(
                self.clock_settings.audio_clock)
        if self.expander_ex1:
            self.ex1_pmod = eurorack_pmod.EurorackPmod(
                self.clock_settings.audio_clock)

        n = self.nr_channels
        self.bitstream_help = BitstreamHelp(
            brief="Scope / Vectorscope / USB audio.",
            io_left=['x / in0', 'y / in1', 'intensity / in2', 'color / in3', 'out0', 'out1', 'out2', 'out3'],
            io_right=['navigate menu', f'{n}x{n} audio device', 'video out', '', '', '']
        )

        # Extract module docstring for help page

        self.vector_periph_base      = 0x00001000
        self.scope_periph_base       = 0x00001100
        self.xbeam_periph_base       = 0x00001200
        self.overlay_periph_base     = 0x00001300
        self.ex0_pmod_periph_base    = 0x00001400
        self.i2c_ex0_base            = 0x00001500
        self.ex1_pmod_periph_base    = 0x00001600
        self.i2c_ex1_base            = 0x00001700

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

        if self.expander_ex0:
            self.ex0_pmod_periph = eurorack_pmod.Peripheral(pmod=self.ex0_pmod)
            self.csr_decoder.add(self.ex0_pmod_periph.bus,
                                 addr=self.ex0_pmod_periph_base, name="ex0_pmod_periph")
            self.i2c_ex0 = i2c.Peripheral()
            self.csr_decoder.add(self.i2c_ex0.bus,
                                 addr=self.i2c_ex0_base, name="i2c2")
        if self.expander_ex1:
            self.ex1_pmod_periph = eurorack_pmod.Peripheral(pmod=self.ex1_pmod)
            self.csr_decoder.add(self.ex1_pmod_periph.bus,
                                 addr=self.ex1_pmod_periph_base, name="ex1_pmod_periph")
            self.i2c_ex1 = i2c.Peripheral()
            self.csr_decoder.add(self.i2c_ex1.bus,
                                 addr=self.i2c_ex1_base, name="i2c3")

        os.environ["TILIQUA_EXPANDER_EX0"] = "1" if self.expander_ex0 else "0"
        os.environ["TILIQUA_EXPANDER_EX1"] = "1" if self.expander_ex1 else "0"

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

        if self.expander_ex0:
            m.submodules.ex0_pmod = self.ex0_pmod
            m.submodules.ex0_pmod_periph = self.ex0_pmod_periph
            m.submodules.i2c_ex0 = self.i2c_ex0
            wiring.connect(m, self.i2c_ex0.i2c_stream,
                           self.ex0_pmod.i2c_master.i2c_override)
            if sim.is_hw(platform):
                m.submodules.ex0_provider = eurorack_pmod.PMODProvider(0)
                wiring.connect(m, self.ex0_pmod.pins, m.submodules.ex0_provider.pins)
                m.d.comb += self.ex0_pmod_periph.mute.eq(self.reboot.mute)
        if self.expander_ex1:
            m.submodules.ex1_pmod = self.ex1_pmod
            m.submodules.ex1_pmod_periph = self.ex1_pmod_periph
            m.submodules.i2c_ex1 = self.i2c_ex1
            wiring.connect(m, self.i2c_ex1.i2c_stream,
                           self.ex1_pmod.i2c_master.i2c_override)
            if sim.is_hw(platform):
                m.submodules.ex1_provider = eurorack_pmod.PMODProvider(1)
                wiring.connect(m, self.ex1_pmod.pins, m.submodules.ex1_provider.pins)
                m.d.comb += self.ex1_pmod_periph.mute.eq(self.reboot.mute)

        if sim.is_hw(platform):
            m.submodules.usbif = usbif = usb_audio.USB2AudioInterface(
                    audio_clock=self.clock_settings.audio_clock,
                    nr_channels=self.nr_channels)
            # SoC-controlled USB PHY connection (based on typeC CC status)
            m.d.comb += usbif.usb_connect.eq(self.xbeam_periph.usb_connect)

        if self.nr_channels == 4:
            with m.If(self.xbeam_periph.usb_en):
                if sim.is_hw(platform):
                    wiring.connect(m, pmod0.o_cal, usbif.i)
                    wiring.connect(m, usbif.o, pmod0.i_cal)
                else:
                    pass
            with m.Else():
                wiring.connect(m, pmod0.o_cal, pmod0.i_cal)
        else:
            expander_pmods = []
            if self.expander_ex0:
                expander_pmods.append(self.ex0_pmod)
            if self.expander_ex1:
                expander_pmods.append(self.ex1_pmod)

            m.submodules.in_split_pmod0 = in_split_pmod0 = dsp.Split(n_channels=4)
            in_splits_ex = []
            for idx, ex_pmod in enumerate(expander_pmods):
                s = dsp.Split(n_channels=4)
                setattr(m.submodules, f"in_split_ex{idx}", s)
                in_splits_ex.append(s)

            m.submodules.in_merge = in_merge = dsp.Merge(
                n_channels=self.nr_channels)

            for ch in range(4):
                wiring.connect(m, in_split_pmod0.o[ch], in_merge.i[ch])
            ch_offset = 4
            for s in in_splits_ex:
                for ch in range(4):
                    wiring.connect(m, s.o[ch], in_merge.i[ch_offset + ch])
                ch_offset += 4

            m.submodules.out_split = out_split = dsp.Split(
                n_channels=self.nr_channels)
            m.submodules.out_merge_pmod0 = out_merge_pmod0 = dsp.Merge(
                n_channels=4)
            out_merges_ex = []
            for idx, ex_pmod in enumerate(expander_pmods):
                mg = dsp.Merge(n_channels=4)
                setattr(m.submodules, f"out_merge_ex{idx}", mg)
                out_merges_ex.append(mg)

            for ch in range(4):
                wiring.connect(m, out_split.o[ch], out_merge_pmod0.i[ch])
            ch_offset = 4
            for mg in out_merges_ex:
                for ch in range(4):
                    wiring.connect(m, out_split.o[ch_offset + ch], mg.i[ch])
                ch_offset += 4

            with m.If(self.xbeam_periph.usb_en):
                wiring.connect(m, pmod0.o_cal, in_split_pmod0.i)
                for s, ex_pmod in zip(in_splits_ex, expander_pmods):
                    wiring.connect(m, ex_pmod.o_cal, s.i)
                if sim.is_hw(platform):
                    wiring.connect(m, in_merge.o, usbif.i)
                    wiring.connect(m, usbif.o, out_split.i)
                wiring.connect(m, out_merge_pmod0.o, pmod0.i_cal)
                for mg, ex_pmod in zip(out_merges_ex, expander_pmods):
                    wiring.connect(m, mg.o, ex_pmod.i_cal)
            with m.Else():
                wiring.connect(m, pmod0.o_cal, pmod0.i_cal)
                for ex_pmod in expander_pmods:
                    wiring.connect(m, ex_pmod.o_cal, ex_pmod.i_cal)

        m.submodules.plot_fifo = plot_fifo = dsp.SyncFIFOBuffered(
            shape=data.ArrayLayout(PSQ, 4), depth=256)

        with m.Switch(self.xbeam_periph.plot_io):
            with m.Case(0):  # builtin
                with m.If(self.xbeam_periph.show_outputs):
                    dsp.connect_peek(m, pmod0.i_cal, plot_fifo.i)
                with m.Else():
                    dsp.connect_peek(m, pmod0.o_cal, plot_fifo.i)
            if self.expander_ex0:
                with m.Case(1):  # ex0
                    with m.If(self.xbeam_periph.show_outputs):
                        dsp.connect_peek(m, self.ex0_pmod.i_cal, plot_fifo.i)
                    with m.Else():
                        dsp.connect_peek(m, self.ex0_pmod.o_cal, plot_fifo.i)
            if self.expander_ex1:
                with m.Case(2):  # ex1
                    with m.If(self.xbeam_periph.show_outputs):
                        dsp.connect_peek(m, self.ex1_pmod.i_cal, plot_fifo.i)
                    with m.Else():
                        dsp.connect_peek(m, self.ex1_pmod.o_cal, plot_fifo.i)

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


def argparse_callback(parser):
    parser.add_argument('--expander-ex0', action='store_true', default=False,
                        help="Enable extra audio board on PMOD expansion port 0 (+4ch USB audio)")
    parser.add_argument('--expander-ex1', action='store_true', default=False,
                        help="Enable extra audio board on PMOD expansion port 1 (+4ch USB audio)")

def argparse_fragment(args):
    if args.expander_ex0 or args.expander_ex1:
        args.name = args.name + '-EX'
    return {
        "expander_ex0": args.expander_ex0,
        "expander_ex1": args.expander_ex1,
    }

if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(XbeamSoc, path=this_path,
                  argparse_callback=argparse_callback,
                  argparse_fragment=argparse_fragment,
                  archiver_callback=lambda archiver: archiver.with_option_storage())
