# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# Based on some work from LUNA project licensed under BSD. Anything new
# in this file is issued under the following license:
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Background: Tiliqua SoC designs
-------------------------------

Many Tiliqua projects contain an SoC alongside the DSP logic, in an arrangement like this:

.. image:: /_static/tiliquasoc.png
  :width: 800

Overview
^^^^^^^^

At a very high level, we have a vexriscv RISCV softcore running firmware (written
in Rust), that interfaces with a bunch of peripherals through CSR registers. As
the Vex also runs the menu system, often there is a dedicated peripheral with
CSRs used to tweak parameters of the DSP pipeline.

PSRAM
^^^^^

PSRAM bandwidth is important to keep under control. For this reason, the SoC
only interfaces with the PSRAM for text/line draw operations. Normal instruction
and data fetches are to a local SRAM and so do not touch external PSRAM (which
is usually hammered with video traffic).

TODO: describe each peripheral in detail
"""

import enum
import shutil
import subprocess
import tempfile
import os

from amaranth                                    import *
from amaranth.build                              import Attrs, Pins, PinsN, Platform, Resource, Subsignal
from amaranth.hdl.rec                            import Record
from amaranth.lib                                import wiring, data
from amaranth.lib.wiring                         import Component, In, Out, flipped, connect

from amaranth_soc                                import csr, gpio, wishbone
from amaranth_soc.csr.wishbone                   import WishboneCSRBridge

from luna_soc.gateware.core                      import blockram, timer, uart, spiflash
from luna_soc.gateware.cpu                       import InterruptController
from luna_soc.gateware.provider.cynthion         import UARTProvider
from amaranth_soc          import wishbone, csr
from luna_soc.util                               import readbin
from luna_soc.generate                           import rust, introspect, svd

from vendor.vexiiriscv                           import VexiiRiscv

from tiliqua.tiliqua_platform                    import *
from tiliqua.types                               import FirmwareLocation

from tiliqua                                     import psram_peripheral, i2c, encoder, dtr, eurorack_pmod_peripheral, dma_framebuffer, raster_persist, palette
from tiliqua                                     import sim, eurorack_pmod, tiliqua_pll

class TiliquaSoc(Component):
    def __init__(self, *, firmware_bin_path, default_modeline, ui_name, ui_sha, platform_class, clock_settings,
                 touch=False, finalize_csr_bridge=True, video_rotate_90=False, poke_outputs=False,
                 mainram_size=0x2000, fw_location=None, fw_offset=None, cpu_variant="tiliqua_rv32im",
                 extra_cpu_regions=[]):

        super().__init__({})

        self.ui_name = ui_name
        self.ui_sha  = ui_sha

        self.sim_fs_strobe = Signal()

        self.firmware_bin_path = firmware_bin_path
        self.touch = touch
        self.clock_settings = clock_settings
        self.default_modeline = default_modeline
        self.video_rotate_90 = video_rotate_90

        self.platform_class = platform_class

        self.mainram_base         = 0x00000000
        self.mainram_size         = mainram_size
        self.spiflash_base        = 0x10000000
        self.spiflash_size        = 0x01000000 # 128Mbit / 16MiB
        self.psram_base           = 0x20000000
        self.psram_size           = 0x01000000 # 128Mbit / 16MiB
        self.csr_base             = 0xf0000000
        # offsets from csr_base
        self.spiflash_ctrl_base   = 0x00000100
        self.uart0_base           = 0x00000200
        self.timer0_base          = 0x00000300
        self.timer0_irq           = 0
        self.i2c0_base            = 0x00000400
        self.i2c1_base            = 0x00000500
        self.encoder0_base        = 0x00000600
        self.pmod0_periph_base    = 0x00000700
        self.dtr0_base            = 0x00000800
        self.persist_periph_base  = 0x00000900
        self.palette_periph_base  = 0x00000A00
        self.fb_periph_base       = 0x00000B00
        self.psram_csr_base       = 0x00000C00

        # Some settings depend on whether code is in block RAM or SPI flash
        self.fw_location = fw_location
        match fw_location:
            case FirmwareLocation.BRAM:
                self.reset_addr  = self.mainram_base
                self.fw_base     = None
            case FirmwareLocation.SPIFlash:
                # CLI provides the offset (indexed from 0 on the spiflash), however
                # on the Vex it is memory mapped from self.spiflash_base onward.
                self.fw_base     = self.spiflash_base + fw_offset
                self.reset_addr  = self.fw_base
                self.fw_max_size = 0x50000 # 320KiB
            case FirmwareLocation.PSRAM:
                self.fw_base     = self.psram_base + fw_offset
                self.reset_addr  = self.fw_base
                self.fw_max_size = 0x50000 # 320KiB


        # cpu
        self.cpu = VexiiRiscv(
            regions = [
                VexiiRiscv.MemoryRegion(base=self.mainram_base, size=self.mainram_size, cacheable=True, executable=False),
                VexiiRiscv.MemoryRegion(base=self.spiflash_base, size=self.spiflash_size, cacheable=True, executable=True),
                VexiiRiscv.MemoryRegion(base=self.psram_base, size=self.psram_size, cacheable=True, executable=True),
                VexiiRiscv.MemoryRegion(base=self.csr_base, size=0x10000, cacheable=False, executable=False),
            ] + extra_cpu_regions,
            variant=cpu_variant,
            reset_addr=self.reset_addr,
        )

        # interrupt controller
        self.interrupt_controller = InterruptController(width=len(self.cpu.irq_external))

        # bus
        self.wb_arbiter  = wishbone.Arbiter(
            addr_width=30,
            data_width=32,
            granularity=8,
            features={"cti", "bte", "err"}
        )
        self.wb_decoder  = wishbone.Decoder(
            addr_width=30,
            data_width=32,
            granularity=8,
            alignment=0,
            features={"cti", "bte", "err"}
        )

        # mainram
        self.mainram = blockram.Peripheral(size=self.mainram_size)
        self.wb_decoder.add(self.mainram.bus, addr=self.mainram_base, name="blockram")

        # csr decoder
        self.csr_decoder = csr.Decoder(addr_width=28, data_width=8)

        # uart0
        uart_baud_rate = 115200
        divisor = int(self.clock_settings.frequencies.sync // uart_baud_rate)
        self.uart0 = uart.Peripheral(divisor=divisor)
        self.csr_decoder.add(self.uart0.bus, addr=self.uart0_base, name="uart0")

        # timer0
        self.timer0 = timer.Peripheral(width=32)
        self.csr_decoder.add(self.timer0.bus, addr=self.timer0_base, name="timer0")
        self.interrupt_controller.add(self.timer0, number=self.timer0_irq, name="timer0")

        # spiflash peripheral
        self.spi0_phy        = spiflash.SPIPHYController(domain="sync", divisor=0)
        self.spiflash_periph = spiflash.Peripheral(phy=self.spi0_phy, mmap_size=self.spiflash_size,
                                                   mmap_name="spiflash")
        self.wb_decoder.add(self.spiflash_periph.bus, addr=self.spiflash_base, name="spiflash")
        self.csr_decoder.add(self.spiflash_periph.csr, addr=self.spiflash_ctrl_base, name="spiflash_ctrl")

        # psram peripheral
        self.psram_periph = psram_peripheral.Peripheral(size=self.psram_size)
        self.wb_decoder.add(self.psram_periph.bus, addr=self.psram_base,
                            name="psram")
        self.csr_decoder.add(self.psram_periph.csr_bus, addr=self.psram_csr_base, name="psram_csr")

        # mobo i2c
        self.i2c0 = i2c.Peripheral()
        # XXX: 100kHz bus speed. DO NOT INCREASE THIS. See comment on this bus in
        # tiliqua_platform.py for more details.
        self.i2c_stream0 = i2c.I2CStreamer(period_cyc=600)
        self.csr_decoder.add(self.i2c0.bus, addr=self.i2c0_base, name="i2c0")

        # eurorack-pmod i2c
        self.i2c1 = i2c.Peripheral()
        self.csr_decoder.add(self.i2c1.bus, addr=self.i2c1_base, name="i2c1")

        # encoder
        self.encoder0 = encoder.Peripheral()
        self.csr_decoder.add(self.encoder0.bus, addr=self.encoder0_base, name="encoder0")

        # pmod periph / audio interface (can be simulated)
        self.pmod0 = eurorack_pmod.EurorackPmod(
                self.clock_settings.audio_clock)
        self.pmod0_periph = eurorack_pmod_peripheral.Peripheral(
                pmod=self.pmod0, poke_outputs=poke_outputs)
        self.csr_decoder.add(self.pmod0_periph.bus, addr=self.pmod0_periph_base, name="pmod0_periph")

        # die temperature
        self.dtr0 = dtr.Peripheral()
        self.csr_decoder.add(self.dtr0.bus, addr=self.dtr0_base, name="dtr0")

        # framebuffer palette interface
        self.palette_periph = palette.Peripheral()
        self.csr_decoder.add(
                self.palette_periph.bus, addr=self.palette_periph_base, name="palette_periph")

        # video PHY (DMAs from PSRAM starting at self.psram_base)
        self.fb = dma_framebuffer.DMAFramebuffer(
                palette = self.palette_periph.palette,
                fb_base_default=self.psram_base, fixed_modeline=default_modeline)
        self.psram_periph.add_master(self.fb.bus)

        # Timing CSRs for video PHY
        self.framebuffer_periph = dma_framebuffer.Peripheral(fb=self.fb)
        self.csr_decoder.add(
                self.framebuffer_periph.bus, addr=self.fb_periph_base, name="framebuffer_periph")

        # Video persistance DMA effect
        self.persist_periph = raster_persist.Peripheral(
            fb=self.fb,
            bus_dma=self.psram_periph)
        self.csr_decoder.add(self.persist_periph.bus, addr=self.persist_periph_base, name="persist_periph")

        self.permit_bus_traffic = Signal()

        self.extra_rust_constants = []

        if finalize_csr_bridge:
            self.finalize_csr_bridge()

    def finalize_csr_bridge(self):

        # Finalizing the CSR bridge / peripheral memory map may not be desirable in __init__
        # if we want to add more after this class has been instantiated. So it's optional
        # during __init__ but MUST be called once before the design is elaborated.

        self.wb_to_csr = WishboneCSRBridge(self.csr_decoder.bus, data_width=32)
        self.wb_decoder.add(self.wb_to_csr.wb_bus, addr=self.csr_base, sparse=False, name="wb_to_csr")

    def add_rust_constant(self, line):
        self.extra_rust_constants.append(line)

    def elaborate(self, platform):

        m = Module()

        if self.fw_location == FirmwareLocation.BRAM:
            # Init BRAM program memory if we aren't loading from SPI flash.
            self.mainram.init = readbin.get_mem_data(self.firmware_bin_path, data_width=32, endianness="little")
            assert self.mainram.init

        # bus
        m.submodules.wb_arbiter = self.wb_arbiter
        m.submodules.wb_decoder = self.wb_decoder
        wiring.connect(m, self.wb_arbiter.bus, self.wb_decoder.bus)

        # cpu
        m.submodules.cpu = self.cpu
        self.wb_arbiter.add(self.cpu.ibus)
        self.wb_arbiter.add(self.cpu.dbus)
        self.wb_arbiter.add(self.cpu.pbus) # TODO: isolate pbus from ibus/dbus

        # interrupt controller
        m.submodules.interrupt_controller = self.interrupt_controller
        # TODO wiring.connect(m, self.cpu.irq_external, self.irqs.pending)
        m.d.comb += self.cpu.irq_external.eq(self.interrupt_controller.pending)

        # mainram
        m.submodules.mainram = self.mainram

        # csr decoder
        m.submodules.csr_decoder = self.csr_decoder

        # uart0
        m.submodules.uart0 = self.uart0
        if sim.is_hw(platform):
            uart0_provider = UARTProvider()
            m.submodules.uart0_provider = uart0_provider
            wiring.connect(m, self.uart0.pins, uart0_provider.pins)

        # timer0
        m.submodules.timer0 = self.timer0

        # i2c0
        m.submodules.i2c0 = self.i2c0
        m.submodules.i2c_stream0 = self.i2c_stream0
        wiring.connect(m, self.i2c0.i2c_stream, self.i2c_stream0.control)
        if sim.is_hw(platform):
            i2c0_provider = i2c.Provider()
            m.submodules.i2c0_provider = i2c0_provider
            wiring.connect(m, self.i2c_stream0.pins, i2c0_provider.pins)

        # encoder0
        m.submodules.encoder0 = self.encoder0
        if sim.is_hw(platform):
            encoder0_provider = encoder.Provider()
            m.submodules.encoder0_provider = encoder0_provider
            wiring.connect(m, self.encoder0.pins, encoder0_provider.pins)

        # psram
        m.submodules.psram_periph = self.psram_periph

        # spiflash
        if sim.is_hw(platform):
            spi0_provider = spiflash.ECP5ConfigurationFlashProvider()
            m.submodules.spi0_provider = spi0_provider
            wiring.connect(m, self.spi0_phy.pins, spi0_provider.pins)
        m.submodules.spi0_phy = self.spi0_phy
        m.submodules.spiflash_periph = self.spiflash_periph

        # video PHY
        m.submodules.palette_periph = self.palette_periph
        m.submodules.fb = self.fb
        m.submodules.framebuffer_periph = self.framebuffer_periph

        # video periph / persist
        m.submodules.persist_periph = self.persist_periph

        # audio interface
        m.submodules.pmod0 = self.pmod0
        m.submodules.pmod0_periph = self.pmod0_periph
        # i2c1 / pmod i2c override
        m.submodules.i2c1 = self.i2c1
        wiring.connect(m, self.i2c1.i2c_stream, self.pmod0.i2c_master.i2c_override)

        if sim.is_hw(platform):
            # hook up audio interface pins
            m.submodules.pmod0_provider = pmod0_provider = eurorack_pmod.FFCProvider()
            wiring.connect(m, self.pmod0.pins, pmod0_provider.pins)

            # die temperature
            m.submodules.dtr0 = self.dtr0

            # generate our domain clocks/resets
            m.submodules.car = car = platform.clock_domain_generator(self.clock_settings)

            # Enable LED driver on motherboard
            m.d.comb += platform.request("mobo_leds_oe").o.eq(1),

            # Connect encoder button to RebootProvider
            m.submodules.reboot = reboot = RebootProvider(self.clock_settings.frequencies.sync)
            m.d.comb += reboot.button.eq(self.encoder0._button.f.button.r_data)
            m.d.comb += self.pmod0_periph.mute.eq(reboot.mute)
        else:
            m.submodules.car = sim.FakeTiliquaDomainGenerator()

        # wishbone csr bridge
        m.submodules.wb_to_csr = self.wb_to_csr

        # Memory controller hangs if we start making requests to it straight away.
        on_delay = Signal(32)
        with m.If(on_delay < 0xFFFFF):
            m.d.comb += self.cpu.ext_reset.eq(1)
            m.d.sync += on_delay.eq(on_delay+1)
        with m.Else():
            m.d.sync += self.permit_bus_traffic.eq(1)

        return m

    def gensvd(self, dst_svd):
        """Generate top-level SVD."""
        print("Generating SVD ...", dst_svd)
        with open(dst_svd, "w") as f:
            soc = introspect.soc(self)
            memory_map = introspect.memory_map(soc)
            interrupts = introspect.interrupts(soc)
            svd.SVD(memory_map, interrupts).generate(file=f)
        print("Wrote SVD ...", dst_svd)

    def genmem(self, dst_mem):
        """Generate linker regions for Rust (memory.x)."""
        print("Generating (rust) memory.x ...", dst_mem)
        with open(dst_mem, "w") as f:
            soc        = introspect.soc(self)
            memory_map = introspect.memory_map(soc)
            reset_addr = introspect.reset_addr(soc)
            rust.LinkerScript(memory_map, reset_addr).generate(file=f)

    def genconst(self, dst):
        """Generate some high-level constants used by application code."""
        # TODO: better to move these to SVD vendor section?
        print("Generating (rust) constants ...", dst)
        with open(dst, "w") as f:
            f.write(f"pub const UI_NAME: &str            = \"{self.ui_name}\";\n")
            f.write(f"pub const UI_SHA: &str             = \"{self.ui_sha}\";\n")
            f.write(f"pub const HW_REV_MAJOR: u32        = {self.platform_class.version_major};\n")
            f.write(f"pub const CLOCK_SYNC_HZ: u32       = {self.clock_settings.frequencies.sync};\n")
            f.write(f"pub const CLOCK_FAST_HZ: u32       = {self.clock_settings.frequencies.fast};\n")
            f.write(f"pub const CLOCK_DVI_HZ: u32        = {self.clock_settings.frequencies.dvi};\n")
            f.write(f"pub const CLOCK_AUDIO_HZ: u32      = {self.clock_settings.frequencies.audio};\n")
            f.write(f"pub const PSRAM_BASE: usize        = 0x{self.psram_base:x};\n")
            f.write(f"pub const PSRAM_SZ_BYTES: usize    = 0x{self.psram_size:x};\n")
            f.write(f"pub const PSRAM_SZ_WORDS: usize    = PSRAM_SZ_BYTES / 4;\n")
            f.write(f"pub const SPIFLASH_BASE: usize     = 0x{self.spiflash_base:x};\n")
            f.write(f"pub const SPIFLASH_SZ_BYTES: usize = 0x{self.spiflash_size:x};\n")
            f.write(f"pub const H_ACTIVE: u32            = {self.fb.fixed_modeline.h_active};\n")
            f.write(f"pub const V_ACTIVE: u32            = {self.fb.fixed_modeline.v_active};\n")
            f.write(f"pub const VIDEO_ROTATE_90: bool    = {'true' if self.video_rotate_90 else 'false'};\n")
            f.write(f"pub const PSRAM_FB_BASE: usize     = 0x{self.fb.fb_base.init:x};\n")
            f.write(f"pub const N_BITSTREAMS: usize      = 8;\n")
            f.write(f"pub const BOOTINFO_SZ_BYTES: usize = 4096;\n")
            f.write(f"pub const BOOTINFO_BASE: usize     = PSRAM_BASE + PSRAM_SZ_BYTES - BOOTINFO_SZ_BYTES;\n")
            f.write("// Extra constants specified by an SoC subclass:\n")
            for l in self.extra_rust_constants:
                f.write(l)

    def generate_pac_from_svd(self, pac_dir, svd_path):
        """
        Generate Rust PAC from an SVD.
        """
        # Copy out the template and modify it for our SoC.
        shutil.rmtree(pac_dir, ignore_errors=True)
        shutil.copytree("src/rs/template/pac", pac_dir)
        pac_build_dir = os.path.join(pac_dir, "build")
        pac_gen_dir   = os.path.join(pac_dir, "src/generated")
        src_genrs     = os.path.join(pac_dir, "src/generated.rs")
        shutil.rmtree(pac_build_dir, ignore_errors=True)
        shutil.rmtree(pac_gen_dir, ignore_errors=True)
        os.makedirs(pac_build_dir)
        if os.path.isfile(src_genrs):
            os.remove(src_genrs)

        subprocess.check_call([
            "svd2rust",
            "-i", svd_path,
            "-o", pac_build_dir,
            "--target", "riscv",
            "--make_mod",
            "--ident-formats-theme", "legacy"
            ], env=os.environ)

        shutil.move(os.path.join(pac_build_dir, "mod.rs"), src_genrs)
        shutil.move(os.path.join(pac_build_dir, "device.x"),
                    os.path.join(pac_dir,       "device.x"))

        subprocess.check_call([
            "form",
            "-i", src_genrs,
            "-o", pac_gen_dir,
            ], env=os.environ)

        shutil.move(os.path.join(pac_gen_dir, "lib.rs"), src_genrs)

        self.genconst(os.path.join(pac_gen_dir, "../constants.rs"))

        subprocess.check_call([
            "cargo", "fmt", "--", "--emit", "files"
            ], env=os.environ, cwd=pac_dir)

        print("Rust PAC updated at ...", pac_dir)

    def compile_firmware(rust_fw_root, firmware_bin_path):
        subprocess.check_call([
            "cargo", "build", "--release"
            ], env=os.environ, cwd=rust_fw_root)
        subprocess.check_call([
            "cargo", "objcopy", "--release", "--", "-Obinary", firmware_bin_path
            ], env=os.environ, cwd=rust_fw_root)
