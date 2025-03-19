# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# Based on some work from LUNA project licensed under BSD. Anything new
# in this file is issued under the following license:
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Many Tiliqua projects contain an SoC alongside the DSP logic, in an arrangement like this:

.. image:: _static/tiliquasoc.png
  :width: 800

Overview
--------

At a very high level, we have a vexriscv RISCV softcore running firmware (written
in Rust), that interfaces with a bunch of peripherals through CSR registers. As
the Vex also runs the menu system, often there is a dedicated peripheral with
CSRs used to tweak parameters of the DSP pipeline.

PSRAM
-----

PSRAM bandwidth is important to keep under control. For this reason, the SoC
only interfaces with the PSRAM for text/line draw operations. Normal instruction
and data fetches are to a local SRAM and so do not touch external PSRAM (which
is usually hammered with video traffic).

TODO: describe each peripheral in detail
"""

import enum
import shutil
import subprocess
import os

from amaranth                                    import *
from amaranth.build                              import Attrs, Pins, PinsN, Platform, Resource, Subsignal
from amaranth.hdl.rec                            import Record
from amaranth.lib                                import wiring, data
from amaranth.lib.wiring                         import Component, In, Out, flipped, connect

from amaranth_soc                                import csr, gpio, wishbone
from amaranth_soc.csr.wishbone                   import WishboneCSRBridge

from vendor.soc.cores                            import sram, timer, uart, spiflash
from vendor.soc.cpu                              import InterruptController, VexRiscv
from vendor.soc                                  import readbin
from vendor.soc.generate                         import GenerateSVD


from tiliqua.tiliqua_platform                    import *
from tiliqua.raster                              import Persistance
from tiliqua.types                               import FirmwareLocation

from tiliqua                                     import psram_peripheral, i2c, encoder, dtr, eurorack_pmod_peripheral, dma_framebuffer
from tiliqua                                     import sim, eurorack_pmod, tiliqua_pll

class VideoPeripheral(wiring.Component):

    class PersistReg(csr.Register, access="w"):
        persist: csr.Field(csr.action.W, unsigned(16))

    class DecayReg(csr.Register, access="w"):
        decay: csr.Field(csr.action.W, unsigned(8))

    class PaletteReg(csr.Register, access="w"):
        position: csr.Field(csr.action.W, unsigned(8))
        red:      csr.Field(csr.action.W, unsigned(8))
        green:    csr.Field(csr.action.W, unsigned(8))
        blue:     csr.Field(csr.action.W, unsigned(8))

    class PaletteBusyReg(csr.Register, access="r"):
        busy: csr.Field(csr.action.R, unsigned(1))

    def __init__(self, fb, bus_dma):
        self.en = Signal()
        self.fb = fb
        self.persist = Persistance(fb=self.fb)
        bus_dma.add_master(self.persist.bus)

        regs = csr.Builder(addr_width=5, data_width=8)

        self._persist      = regs.add("persist",      self.PersistReg(),     offset=0x0)
        self._decay        = regs.add("decay",        self.DecayReg(),       offset=0x4)
        self._palette      = regs.add("palette",      self.PaletteReg(),     offset=0x8)
        self._palette_busy = regs.add("palette_busy", self.PaletteBusyReg(), offset=0xC)

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        m.submodules.persist = self.persist

        connect(m, flipped(self.bus), self._bridge.bus)

        m.d.comb += self.persist.enable.eq(self.en)

        with m.If(self._persist.f.persist.w_stb):
            m.d.sync += self.persist.holdoff.eq(self._persist.f.persist.w_data)

        with m.If(self._decay.f.decay.w_stb):
            m.d.sync += self.persist.decay.eq(self._decay.f.decay.w_data)

        # palette update logic
        palette_busy = Signal()
        m.d.comb += self._palette_busy.f.busy.r_data.eq(palette_busy)

        with m.If(self._palette.element.w_stb & ~palette_busy):
            m.d.sync += [
                palette_busy                            .eq(1),
                self.fb.palette.update.valid            .eq(1),
                self.fb.palette.update.payload.position .eq(self._palette.f.position.w_data),
                self.fb.palette.update.payload.red      .eq(self._palette.f.red.w_data),
                self.fb.palette.update.payload.green    .eq(self._palette.f.green.w_data),
                self.fb.palette.update.payload.blue     .eq(self._palette.f.blue.w_data),
            ]

        with m.If(palette_busy & self.fb.palette.update.ready):
            # coefficient has been written
            m.d.sync += [
                palette_busy.eq(0),
                self.fb.palette.update.valid.eq(0),
            ]

        return m

class TiliquaSoc(Component):
    def __init__(self, *, firmware_bin_path, default_modeline, ui_name, ui_sha, platform_class, clock_settings,
                 touch=False, finalize_csr_bridge=True, video_rotate_90=False, poke_outputs=False,
                 mainram_size=0x2000, fw_location=None, fw_offset=None, cpu_variant="tiliqua_rv32im"):

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
        self.video_periph_base    = 0x00000900

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
        self.cpu = VexRiscv(
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
        self.mainram = sram.Peripheral(size=self.mainram_size)
        self.wb_decoder.add(self.mainram.bus, addr=self.mainram_base, name="mainram")

        # csr decoder
        self.csr_decoder = csr.Decoder(addr_width=28, data_width=8)

        # uart0
        uart_baud_rate = 115200
        divisor = int(self.clock_settings.frequencies.sync // uart_baud_rate)
        self.uart0 = uart.Peripheral(divisor=divisor)
        self.csr_decoder.add(self.uart0.bus, addr=self.uart0_base, name="uart0")

        # FIXME: timer events / isrs currently not implemented, adding the event
        # bus to the csr decoder segfaults yosys somehow ...

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
        self.wb_decoder.add(self.psram_periph.bus, addr=self.psram_base, name="psram")

        # video PHY (DMAs from PSRAM starting at self.psram_base)
        self.fb = dma_framebuffer.DMAFramebuffer(
                fb_base_default=self.psram_base, fixed_modeline=default_modeline)
        self.psram_periph.add_master(self.fb.bus)

        # mobo i2c
        self.i2c0 = i2c.Peripheral()
        self.i2c_stream0 = i2c.I2CStreamer(period_cyc=256)
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

        # video persistance effect (all writes gradually fade) -
        # this is an interesting alternative to double-buffering that looks
        # kind of like an old CRT with slow-scanning.
        self.video_periph = VideoPeripheral(
            fb=self.fb,
            bus_dma=self.psram_periph)
        self.csr_decoder.add(self.video_periph.bus, addr=self.video_periph_base, name="video_periph")

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
            uart0_provider = uart.Provider(0)
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
        m.submodules.fb = self.fb

        # video periph / persist
        m.submodules.video_periph = self.video_periph

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
        with m.If(on_delay < 0xFF):
            m.d.comb += self.cpu.ext_reset.eq(1)
        with m.If(on_delay < 0xFFFF):
            m.d.sync += on_delay.eq(on_delay+1)
        with m.Else():
            m.d.sync += self.permit_bus_traffic.eq(1)
            m.d.sync += self.fb.enable.eq(1)
            m.d.sync += self.video_periph.en.eq(1)

        return m

    def gensvd(self, dst_svd):
        """Generate top-level SVD."""
        print("Generating SVD ...", dst_svd)
        with open(dst_svd, "w") as f:
            GenerateSVD(self).generate(file=f)
        print("Wrote SVD ...", dst_svd)

    def genmem(self, dst_mem):
        """Generate linker regions for Rust (memory.x)."""
        print("Generating (rust) memory.x ...", dst_mem)
        if self.fw_location == FirmwareLocation.BRAM:
            # .text, .rodata in shared block RAM region
            memory_x = (
                "MEMORY {{\n"
                "    mainram : ORIGIN = {mainram_base}, LENGTH = {mainram_size}\n"
                "}}\n"
                "REGION_ALIAS(\"REGION_TEXT\", mainram);\n"
                "REGION_ALIAS(\"REGION_RODATA\", mainram);\n"
                "REGION_ALIAS(\"REGION_DATA\", mainram);\n"
                "REGION_ALIAS(\"REGION_BSS\", mainram);\n"
                "REGION_ALIAS(\"REGION_HEAP\", mainram);\n"
                "REGION_ALIAS(\"REGION_STACK\", mainram);\n"
            )
            with open(dst_mem, "w") as f:
                f.write(memory_x.format(mainram_base=hex(self.mainram_base),
                                        mainram_size=hex(self.mainram.size),
                                        ))
        else:
            # .text, .rodata stored elsewhere (SPI flash or PSRAM)
            memory_x = (
                "MEMORY {{\n"
                "    mainram : ORIGIN = {mainram_base}, LENGTH = {mainram_size}\n"
                "    {text_region} : ORIGIN = {spiflash_base}, LENGTH = {spiflash_size}\n"
                "}}\n"
                "REGION_ALIAS(\"REGION_TEXT\", {text_region});\n"
                "REGION_ALIAS(\"REGION_RODATA\", {text_region});\n"
                "REGION_ALIAS(\"REGION_DATA\", mainram);\n"
                "REGION_ALIAS(\"REGION_BSS\", mainram);\n"
                "REGION_ALIAS(\"REGION_HEAP\", mainram);\n"
                "REGION_ALIAS(\"REGION_STACK\", mainram);\n"
            )
            with open(dst_mem, "w") as f:
                f.write(memory_x.format(mainram_base=hex(self.mainram_base),
                                        mainram_size=hex(self.mainram.size),
                                        spiflash_base=hex(self.fw_base),
                                        spiflash_size=hex(self.fw_max_size),
                                        text_region=self.fw_location.value,
                                        ))

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
            f.write(f"pub const MANIFEST_BASE: usize     = SPIFLASH_BASE + SPIFLASH_SZ_BYTES - 4096;\n")
            f.write(f"pub const MANIFEST_SZ_BYTES: usize = 4096;\n")
            f.write("// Extra constants specified by an SoC subclass:\n")
            for l in self.extra_rust_constants:
                f.write(l)

    def regenerate_pac_from_svd(svd_path):
        """
        Generate Rust PAC from an SVD.
        Currently all SoC reuse the same `pac_dir`, however this
        should become local to each SoC at some point.
        """
        pac_dir = "src/rs/pac"
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

        subprocess.check_call([
            "cargo", "fmt", "--", "--emit", "files"
            ], env=os.environ, cwd=pac_dir)

        print("Rust PAC updated at ...", pac_dir)

    def compile_firmware(rust_fw_root, target_dir):
        manifest_path = os.path.join(rust_fw_root, "Cargo.toml")
        config_path = os.path.join(rust_fw_root, ".cargo/config.toml")
        firmware_elf_path = os.path.join(target_dir, "riscv32im-unknown-none-elf/release/tiliqua-fw")
        firmware_bin_path = os.path.join(target_dir, "firmware.bin")
        subprocess.check_call([
            "cargo", "build", "--release",
            "--manifest-path", manifest_path,
            "--config", config_path,
            "--target-dir", target_dir
            ], env=os.environ)
        subprocess.check_call([
            "riscv-none-elf-objcopy",
            "-Obinary", firmware_elf_path, firmware_bin_path
            ], env=os.environ)
