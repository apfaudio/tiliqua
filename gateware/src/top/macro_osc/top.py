# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
'Macro-Oscillator' runs a downsampled version of the DSP code from a
famous Eurorack module (credits below), on a softcore, to demonstrate the
compute capabilities available if you do everything in software, using
a really large CPU that has big caches and an FPU.

.. code-block:: text

        ┌────┐
        │in0 │◄─ frequency modulation
        │in1 │◄─ trigger
        │in2 │◄─ timbre modulation
        │in3 │◄─ morph modulation
        └────┘
        ┌────┐
        │out0│─► -
        │out1│─► -
        │out2│─► 'out' output (mono)
        │out3│─► 'aux' output (mono)
        └────┘

Most engines are available for tweaking and patching via the UI.
A couple of engines use a bit more compute and may cause the UI to
slow down or audio to glitch, so these ones are disabled.
A scope and vectorscope is included and hooked up to the oscillator
outputs so you can visualize exactly what the softcore is spitting out.

.. code-block:: text

                          (write samples to)
                         ┌─────────────────┐
                         │                 ▼
         poll       ┌────┴─────┐┌───────────────────┐
        audio/ ────►│VexiiRiscv││AudioFifoPeripheral│
          CV        └──────────┘└──────────┬────────┘
                     (plaits               ▼
                       engines)      ┌──[SPLIT]────────►
                                     │             (audio out)
                                     ▼
                            ┌────────────┐
                            │Vectorscope/│
                            │Oscilloscope│
                            └────────────┘

The original module was designed to run at 48kHz. Here, we instantiate
a powerful (rv32imafc) softcore (this one includes an FPU), which
is enough to run most engines at ~24kHz-48kHz, however with the video
and menu system running simultaneously, it's necessary to clock
this down to 24kHz. Surprisingly, most engines still sound reasonable.
The resampling from 24kHz <-> 48kHz is performed in hardware below.

There is quite some heavy compute here and RAM usage, as a result,
the audio buffers are too big to fit in BRAM. In this demo,
both the firmware and the DSP buffers are allocated from external PSRAM.

Credits to Emilie Gillet for the original Plaits module and firmware.

Credits to Oliver Rockstedt for the Rust port of said firmware:
    https://github.com/sourcebox/mi-plaits-dsp-rs

The Rust port is what is running on this softcore.
"""

import os

from amaranth import *
from amaranth.lib import data, fifo, stream, wiring
from amaranth.lib.wiring import In, Out, connect, flipped
from amaranth.utils import exact_log2
from amaranth_soc import csr, wishbone
from amaranth_soc.memory import MemoryMap

from tiliqua import dsp
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.dsp import ASQ
from tiliqua.raster import scope
from tiliqua.raster.plot import FramebufferPlotter
from tiliqua.tiliqua_soc import TiliquaSoc
from vendor.vexiiriscv import VexiiRiscv


# Simple 2-fifo DMA peripheral for writing glitch-free audio from a softcore.
class AudioFIFOPeripheral(wiring.Component):

    class FifoLenReg(csr.Register, access="r"):
        fifo_len: csr.Field(csr.action.R, unsigned(16))

    def __init__(self, fifo_sz=4*4, fifo_data_width=32, granularity=8, elastic_sz=128*4):
        regs = csr.Builder(addr_width=6, data_width=8)

        # Out and Aux FIFOs
        self.elastic_sz = elastic_sz
        self._fifo0 = fifo.SyncFIFOBuffered(
            width=ASQ.as_shape().width, depth=elastic_sz)
        self._fifo1 = fifo.SyncFIFOBuffered(
            width=ASQ.as_shape().width, depth=elastic_sz)

        # Amount of elements in fifo0, used by softcore for scheduling.
        self._fifo_len = regs.add(f"fifo_len", self.FifoLenReg(), offset=0x4)

        self._bridge = csr.Bridge(regs.as_memory_map())

        mem_depth  = (fifo_sz * granularity) // fifo_data_width
        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "wb_bus":  In(wishbone.Signature(addr_width=exact_log2(mem_depth),
                                             data_width=fifo_data_width,
                                             granularity=granularity)),
            "stream": Out(stream.Signature(data.ArrayLayout(ASQ, 4))),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map

        # Fixed memory region for the audio fifo rather than CSRs, so each 32-bit write
        # takes a single bus cycle (CSRs take longer).
        wb_memory_map = MemoryMap(addr_width=exact_log2(fifo_sz), data_width=granularity)
        wb_memory_map.add_resource(name=("audio_fifo",), size=fifo_sz, resource=self)
        self.wb_bus.memory_map = wb_memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        m.submodules._fifo0 = self._fifo0
        m.submodules._fifo1 = self._fifo1

        connect(m, flipped(self.csr_bus), self._bridge.bus)

        # Route writes to DMA region to audio FIFOs
        wstream0 = self._fifo0.w_stream
        wstream1 = self._fifo1.w_stream
        with m.If(self.wb_bus.cyc & self.wb_bus.stb & self.wb_bus.we):
            with m.Switch(self.wb_bus.adr):
                with m.Case(0):
                    m.d.comb += [
                        self.wb_bus.ack.eq(1),
                        wstream0.valid.eq(1),
                        wstream0.payload.eq(self.wb_bus.dat_w),
                    ]
                with m.Case(1):
                    m.d.comb += [
                        self.wb_bus.ack.eq(1),
                        wstream1.valid.eq(1),
                        wstream1.payload.eq(self.wb_bus.dat_w),
                    ]

        m.d.comb += self._fifo_len.f.fifo_len.r_data.eq(self._fifo0.level)

        # Resample 24kHz to 48kHz
        m.submodules.resample_up0 = resample_up0 = dsp.Resample(
                fs_in=24000, n_up=2, m_down=1)
        m.submodules.resample_up1 = resample_up1 = dsp.Resample(
                fs_in=24000, n_up=2, m_down=1)
        wiring.connect(m, self._fifo0.r_stream, resample_up0.i)
        wiring.connect(m, self._fifo1.r_stream, resample_up1.i)

        # Last 2 outputs
        m.submodules.merge = merge = dsp.Merge(4, wiring.flipped(self.stream))
        merge.wire_valid(m, [0, 1])
        wiring.connect(m, resample_up0.o, merge.i[2])
        wiring.connect(m, resample_up1.o, merge.i[3])

        return m


class MacroOscSoc(TiliquaSoc):

    help = BitstreamHelp(
        brief="Emulation of a famous Eurorack module.",
        io_left=['pitch', 'trigger', 'timbre', 'morph', '', '', 'out MAIN', 'out AUX'],
        io_right=['navigate menu', '', 'video out', '', '', '']
    )

    def __init__(self, **kwargs):

        self.vector_periph_base  = 0x00001000
        self.scope_periph_base   = 0x00001100
        self.audio_fifo_csr_base = 0x00001200
        # offset 0x0 is FIFO0, offset 0x4 is FIFO1
        self.audio_fifo_mem_base = 0xa0000000

        # Expose a special memory-mapped region for FIFO writes to the CPU, which is not in the
        # address range of normal CSRs so that we can perform true 32-bit wide writes.
        extra_cpu_regions = [
            VexiiRiscv.MemoryRegion(base=self.audio_fifo_mem_base, size=8, cacheable=0, executable=0)
        ]

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False, mainram_size=0x10000,
                         cpu_variant="tiliqua_rv32imafc", extra_cpu_regions=extra_cpu_regions, **kwargs)

        # Dedicated framebuffer plotter for scope peripherals (5 ports: 1 vector + 4 scope channels)
        self.plotter = FramebufferPlotter(
            bus_signature=self.psram_periph.bus.signature.flip(), n_ports=5)
        self.psram_periph.add_master(self.plotter.bus)

        self.vector_periph = scope.VectorPeripheral(
            n_upsample=16,
            fs=48000)
        self.csr_decoder.add(self.vector_periph.bus, addr=self.vector_periph_base, name="vector_periph")

        self.scope_periph = scope.ScopePeripheral()
        self.csr_decoder.add(self.scope_periph.bus, addr=self.scope_periph_base, name="scope_periph")

        self.audio_fifo = AudioFIFOPeripheral()
        self.csr_decoder.add(self.audio_fifo.csr_bus, addr=self.audio_fifo_csr_base, name="audio_fifo")
        self.wb_decoder.add(self.audio_fifo.wb_bus, addr=self.audio_fifo_mem_base, name="audio_fifo")

        # TODO: take this from parsed memory region list
        self.add_rust_constant(
            f"pub const AUDIO_FIFO_MEM_BASE: usize = 0x{self.audio_fifo_mem_base:x};\n")
        self.add_rust_constant(
            f"pub const AUDIO_FIFO_ELASTIC_SZ: usize = {self.audio_fifo.elastic_sz};\n")

        # now we can freeze the memory map
        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        m.submodules += self.plotter

        m.submodules += self.vector_periph

        m.submodules += self.scope_periph

        # Connect vector/scope pixel requests to plotter channels
        wiring.connect(m, self.vector_periph.o, self.plotter.i[0])
        for n in range(4):
            wiring.connect(m, self.scope_periph.o[n], self.plotter.i[n+1])

        # Connect framebuffer propreties to plotter backend
        wiring.connect(m, wiring.flipped(self.fb.fbp), self.plotter.fbp)

        m.submodules += self.audio_fifo

        m.submodules += super().elaborate(platform)

        pmod0 = self.pmod0_periph.pmod

        self.scope_periph.source = pmod0.i_cal

        wiring.connect(m, self.audio_fifo.stream, pmod0.i_cal)

        # Extra FIFO between audio out stream and plotting components
        # This FIFO does not block the audio stream.

        m.submodules.plot_fifo = plot_fifo = fifo.SyncFIFOBuffered(
            width=data.ArrayLayout(ASQ, 4).as_shape().width, depth=32)

        # Route audio outputs 2/3 to plotting stream (scope / vector)
        m.d.comb += [
            plot_fifo.w_stream.valid.eq(self.audio_fifo.stream.valid & pmod0.i_cal.ready),
            plot_fifo.w_stream.payload[0:16] .eq(self.audio_fifo.stream.payload[2]),
            plot_fifo.w_stream.payload[16:32].eq(self.audio_fifo.stream.payload[3]),
        ]

        # Switch to use scope or vectorscope
        with m.If(self.scope_periph.soc_en):
            wiring.connect(m, plot_fifo.r_stream, self.scope_periph.i)
        with m.Else():
            wiring.connect(m, plot_fifo.r_stream, self.vector_periph.i)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(MacroOscSoc, path=this_path, archiver_callback=lambda archiver: archiver.with_option_storage())
