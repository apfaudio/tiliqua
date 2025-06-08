# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Vectorscope and 4-channel oscilloscope with menu system.

In vectorscope mode, rasterize X/Y (audio channel 0, 1) and
color (audio channel 3) to a simulated CRT.

In oscilloscope mode, all 4 input channels are plotted simultaneosly
in classic oscilloscope fashion.
"""

import logging
import os
import sys

from amaranth                                    import *
from amaranth.lib                                import wiring, data, stream, fifo
from amaranth.lib.wiring                         import In, Out, flipped, connect

from amaranth_soc                                import csr, wishbone

from amaranth_future                             import fixed

from tiliqua                                     import eurorack_pmod, dsp, scope, usb_audio, cache, sim, delay_line
from tiliqua.tiliqua_soc                         import TiliquaSoc
from tiliqua.cli                                 import top_level_cli

class XbeamPeripheral(wiring.Component):

    class Flags(csr.Register, access="w"):
        usb_en:   csr.Field(csr.action.W, unsigned(1))
        show_outputs: csr.Field(csr.action.W, unsigned(1))

    class Delay(csr.Register, access="w"):
        value:   csr.Field(csr.action.W, unsigned(16))

    def __init__(self):
        regs = csr.Builder(addr_width=5, data_width=8)
        self._flags = regs.add("flags", self.Flags(), offset=0x0)
        self._delay0 = regs.add("delay0", self.Delay(), offset=0x4)
        self._delay1 = regs.add("delay1", self.Delay(), offset=0x8)
        self._delay2 = regs.add("delay2", self.Delay(), offset=0xC)
        self._delay3 = regs.add("delay3", self.Delay(), offset=0x10)
        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "usb_en": Out(1),
            "show_outputs": Out(1),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "delay_i": In(stream.Signature(data.ArrayLayout(eurorack_pmod.ASQ, 4))),
            "delay_o": Out(stream.Signature(data.ArrayLayout(eurorack_pmod.ASQ, 4))),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()

        m.submodules.bridge  = self._bridge
        connect(m, flipped(self.bus), self._bridge.bus)

        with m.If(self._flags.f.usb_en.w_stb):
            m.d.sync += self.usb_en.eq(self._flags.f.usb_en.w_data)

        with m.If(self._flags.f.show_outputs.w_stb):
            m.d.sync += self.show_outputs.eq(self._flags.f.show_outputs.w_data)

        m.submodules.split4 = split4 = dsp.Split(n_channels=4, source=wiring.flipped(self.delay_i))
        m.submodules.merge4 = merge4 = dsp.Merge(n_channels=4, sink=wiring.flipped(self.delay_o))

        delay = [Signal(16) for _ in range(4)]

        for ch in range(4):
            delayln = delay_line.DelayLine(max_delay=0x1000, write_triggers_read=False)
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

        return m

class XbeamSoc(TiliquaSoc):

    brief = "Graphical vectorscope and oscilloscope."

    def __init__(self, **kwargs):

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False, **kwargs)

        # WARN: TiliquaSoc ends at 0x00000900
        self.vector_periph_base = 0x00001000
        self.scope_periph_base  = 0x00001100
        self.xbeam_periph_base  = 0x00001200

        # Small localized write-back cache for plotting operations.
        self.plotter_cache = cache.PlotterCache(fb=self.fb)
        self.psram_periph.add_master(self.plotter_cache.bus)

        # Vectorscope with upsampling and CSR registers
        self.vector_periph = scope.VectorTracePeripheral(
            fb=self.fb,
            n_upsample=8)
        self.csr_decoder.add(self.vector_periph.bus, addr=self.vector_periph_base, name="vector_periph")
        self.plotter_cache.add(self.vector_periph.bus_dma)

        # 4-ch oscilloscope with CSR registers
        self.scope_periph = scope.ScopeTracePeripheral(
            fb=self.fb)
        self.csr_decoder.add(self.scope_periph.bus, addr=self.scope_periph_base, name="scope_periph")
        for bus in self.scope_periph.bus_dma:
            self.plotter_cache.add(bus)

        # Extra peripheral for some global control flags.
        self.xbeam_periph = XbeamPeripheral()
        self.csr_decoder.add(self.xbeam_periph.bus, addr=self.xbeam_periph_base, name="xbeam_periph")

        # now we can freeze the memory map
        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        m.submodules += self.plotter_cache

        m.submodules += self.vector_periph

        m.submodules += self.scope_periph

        m.submodules += self.xbeam_periph

        m.submodules += super().elaborate(platform)

        pmod0 = self.pmod0_periph.pmod

        if sim.is_hw(platform):
            m.submodules.usbif = usbif = usb_audio.USB2AudioInterface(
                    audio_clock=self.clock_settings.audio_clock, nr_channels=4)

        with m.If(self.xbeam_periph.usb_en):
            if sim.is_hw(platform):
                wiring.connect(m, pmod0.o_cal, usbif.i)
                wiring.connect(m, usbif.o, pmod0.i_cal)
            else:
                pass
        with m.Else():
            wiring.connect(m, pmod0.o_cal, pmod0.i_cal)

        m.submodules.plot_fifo = plot_fifo = fifo.SyncFIFOBuffered(
            width=data.ArrayLayout(eurorack_pmod.ASQ, 4).as_shape().width, depth=256)

        with m.If(self.xbeam_periph.show_outputs):
            dsp.connect_peek(m, pmod0.i_cal, plot_fifo.w_stream)
        with m.Else():
            dsp.connect_peek(m, pmod0.o_cal, plot_fifo.w_stream)

        wiring.connect(m, plot_fifo.r_stream, self.xbeam_periph.delay_i)

        with m.If(self.scope_periph.soc_en):
            wiring.connect(m, self.xbeam_periph.delay_o, self.scope_periph.i)
        with m.Else():
            wiring.connect(m, self.xbeam_periph.delay_o, self.vector_periph.i)

        # Memory controller hangs if we start making requests to it straight away.
        with m.If(self.permit_bus_traffic):
            m.d.sync += self.vector_periph.en.eq(1)
            m.d.sync += self.scope_periph.en.eq(1)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(XbeamSoc, path=this_path)
