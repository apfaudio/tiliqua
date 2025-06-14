# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
CRT / Vectorscope simulator.
Rasterizes X/Y (audio channel 0, 1) and color (audio channel 3) to a simulated
CRT display, with intensity gradient and afterglow effects.

Simple gateware-only version, this is mostly useful for debugging the
memory and video subsystems with an ILA or simulation, as it's smaller.

See 'xbeam' for SoC version of the scope with a menu system.

.. code-block:: bash

    # for visualizing the color palette
    $ pdm colors_vectorscope

"""

import os
import math
import shutil
import subprocess

from amaranth                 import *
from amaranth.build           import *
from amaranth.lib             import wiring, data, stream
from amaranth.lib.wiring      import In, Out
from amaranth.lib.fifo        import AsyncFIFO, SyncFIFO
from amaranth.lib.cdc         import FFSynchronizer
from amaranth.utils           import log2_int
from amaranth.back            import verilog

from amaranth_future          import fixed
from amaranth_soc             import wishbone

from tiliqua.tiliqua_platform import *
from tiliqua                  import eurorack_pmod, dsp, sim, cache, dma_framebuffer, palette
from tiliqua.eurorack_pmod    import ASQ
from tiliqua                  import psram_peripheral
from tiliqua.cli              import top_level_cli
from tiliqua.sim              import FakeTiliquaDomainGenerator
from tiliqua.raster_persist   import Persistance
from tiliqua.raster_stroke    import Stroke

from vendor.ila               import AsyncSerialILA

class VectorScopeTop(Elaboratable):

    """
    Top-level Vectorscope design.
    """

    def __init__(self, *, clock_settings):

        self.clock_settings = clock_settings

        # One PSRAM with an internal arbiter to support multiple DMA masters.
        self.psram_periph = psram_peripheral.Peripheral(size=16*1024*1024)


        self.pmod0 = eurorack_pmod.EurorackPmod(self.clock_settings.audio_clock)

        if not clock_settings.modeline:
            raise ValueError("This design requires a fixed modeline, use `--modeline`.")

        # All of our DMA masters
        self.palette = palette.ColorPalette()
        self.fb = dma_framebuffer.DMAFramebuffer(fixed_modeline=clock_settings.modeline,
                                                 palette=self.palette)
        self.psram_periph.add_master(self.fb.bus)

        self.persist = Persistance(fb=self.fb)
        self.psram_periph.add_master(self.persist.bus)

        self.stroke = Stroke(fb=self.fb, n_upsample=8, fs=clock_settings.audio_clock.fs())
        self.plotter_cache = cache.PlotterCache(fb=self.fb)
        self.psram_periph.add_master(self.plotter_cache.bus)
        self.plotter_cache.add(self.stroke.bus)

        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.submodules.pmod0 = pmod0 = self.pmod0

        m.submodules.plotter_cache = self.plotter_cache

        if sim.is_hw(platform):
            m.submodules.car = car = platform.clock_domain_generator(self.clock_settings)
            m.submodules.reboot = reboot = RebootProvider(self.clock_settings.frequencies.sync)
            m.submodules.btn = FFSynchronizer(
                    platform.request("encoder").s.i, reboot.button)
            m.submodules.pmod0_provider = pmod0_provider = eurorack_pmod.FFCProvider()
            wiring.connect(m, self.pmod0.pins, pmod0_provider.pins)
            m.d.comb += self.pmod0.codec_mute.eq(reboot.mute)
        else:
            m.submodules.car = FakeTiliquaDomainGenerator()

        self.stroke.pmod0 = pmod0

        m.submodules.palette = self.palette
        m.submodules.fb = self.fb
        m.submodules.persist = self.persist
        m.submodules.stroke = self.stroke

        wiring.connect(m, self.pmod0.o_cal, self.stroke.i)

        # Memory controller hangs if we start making requests to it straight away.
        on_delay = Signal(32)
        with m.If(on_delay < 0xFFFF):
            m.d.sync += on_delay.eq(on_delay+1)
        with m.Else():
            m.d.sync += self.fb.enable.eq(1)
            m.d.sync += self.persist.enable.eq(1)
            m.d.sync += self.stroke.enable.eq(1)

        # Optional ILA, very useful for low-level PSRAM debugging...
        if not platform.ila:
            m.submodules.psram_periph = self.psram_periph
        else:
            # HACK: eager elaboration so ILA has something to attach to
            m.submodules.psram_periph = self.psram_periph.elaborate(platform)

            test_signal = Signal(16, reset=0xFEED)
            ila_signals = [
                test_signal,
                self.psram_periph.psram.idle,
                self.psram_periph.psram.perform_write,
                self.psram_periph.psram.start_transfer,
                self.psram_periph.psram.final_word,
                self.psram_periph.psram.read_ready,
                self.psram_periph.psram.write_ready,
                self.psram_periph.psram.fsm,
                self.psram_periph.psram.phy.datavalid,
                self.psram_periph.psram.phy.burstdet,
                self.psram_periph.psram.phy.cs,
                self.psram_periph.psram.phy.clk_en,
                self.psram_periph.psram.phy.ready,
                self.psram_periph.psram.phy.readclksel,
            ]
            self.ila = AsyncSerialILA(signals=ila_signals,
                                      sample_depth=4096, divisor=521,
                                      domain='sync', sample_rate=60e6) # ~115200 baud on USB clock
            m.submodules += self.ila
            m.d.comb += [
                self.ila.trigger.eq(self.psram_periph.psram.start_transfer),
                platform.request("uart").tx.o.eq(self.ila.tx), # needs FFSync?
            ]

        return m

def colors():
    """
    Render image of intensity/color palette used internally by DMAFramebuffer.
    This is useful for quickly tweaking it.
    """
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib import colors
    import numpy as np
    rs, gs, bs = palette.compute_color_palette()

    i_levels = 16
    c_levels = 16
    data = np.empty((i_levels, c_levels, 3), dtype=np.uint8)
    for i in range(i_levels):
        for c in range(c_levels):
            data[i,c,:] = (rs[i*i_levels + c],
                           gs[i*i_levels + c],
                           bs[i*i_levels + c])

    fig, ax = plt.subplots()
    ax.imshow(data)
    ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=2)
    ax.set_xticks(np.arange(-.5, 16, 1));
    ax.set_yticks(np.arange(-.5, 16, 1));
    save_to = 'vectorscope_palette.png'
    print(f'save palette render to {save_to}')
    plt.savefig(save_to)

def simulation_ports(fragment):
    return {
        "clk_sync":       (ClockSignal("sync"),                        None),
        "rst_sync":       (ResetSignal("sync"),                        None),
        "clk_dvi":        (ClockSignal("dvi"),                         None),
        "rst_dvi":        (ResetSignal("dvi"),                         None),
        "clk_audio":      (ClockSignal("audio"),                       None),
        "rst_audio":      (ResetSignal("audio"),                       None),
        "i2s_sdin1":      (fragment.pmod0.pins.i2s.sdin1,              None),
        "i2s_sdout1":     (fragment.pmod0.pins.i2s.sdout1,             None),
        "i2s_lrck":       (fragment.pmod0.pins.i2s.lrck,               None),
        "i2s_bick":       (fragment.pmod0.pins.i2s.bick,               None),
        "idle":           (fragment.psram_periph.simif.idle,           None),
        "address_ptr":    (fragment.psram_periph.simif.address_ptr,    None),
        "read_data_view": (fragment.psram_periph.simif.read_data_view, None),
        "write_data":     (fragment.psram_periph.simif.write_data,     None),
        "read_ready":     (fragment.psram_periph.simif.read_ready,     None),
        "write_ready":    (fragment.psram_periph.simif.write_ready,    None),
        "dvi_de":         (fragment.fb.simif.de,                    None),
        "dvi_vsync":      (fragment.fb.simif.vsync,                 None),
        "dvi_hsync":      (fragment.fb.simif.hsync,                 None),
        "dvi_r":          (fragment.fb.simif.r,                     None),
        "dvi_g":          (fragment.fb.simif.g,                     None),
        "dvi_b":          (fragment.fb.simif.b,                     None),
    }

if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(
        VectorScopeTop,
        ila_supported=True,
        sim_ports=simulation_ports,
        sim_harness="../../src/top/vectorscope_no_soc/sim/sim.cpp",
    )
