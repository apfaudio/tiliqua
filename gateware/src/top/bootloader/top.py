# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import os

from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, connect, flipped

from tiliqua.build import sim
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.tiliqua_soc import TiliquaSoc
from tiliqua.periph import vbus

from guh.engines.msc import MAX_BLOCKS_PER_XFER
from guh.periph import msc

# PSRAM window reserved for the bootloader's USB MSC scratch buffers.
# HACK/TODO: pretty ugly, swap these out for dynamic allocs?
USB_SCRATCH_PSRAM_SIZE = 3 * MAX_BLOCKS_PER_XFER * 512

class BootloaderSoc(TiliquaSoc):

    bitstream_help = BitstreamHelp(
        brief="Tiliqua Bootloader",
        io_left=['', '', '', '', '(muted)', '(muted)', '(muted)', '(muted)'],
        io_right=['navigate menu', 'USB host', 'video out', '', '', '']
    )

    def __init__(self, **kwargs):

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False, **kwargs)

        self.usb_msc_base  = 0x00001000
        self.usb_vbus_base = 0x00001100

        # USB MSC host
        self.usb_msc = msc.Peripheral(
            addr_width=self.psram_periph.bus.signature.addr_width)
        self.csr_decoder.add(self.usb_msc.csr_bus, addr=self.usb_msc_base, name="usb_msc")
        self.psram_periph.add_master(self.usb_msc.dma_bus)

        # VBUS control
        self.usb_vbus = vbus.UsbVbusPeripheral()
        self.csr_decoder.add(self.usb_vbus.bus, addr=self.usb_vbus_base, name="usb_vbus")

        self.add_rust_constant(
            f"pub const USB_MSC_MAX_BLOCKS_PER_READ: u32 = {MAX_BLOCKS_PER_XFER};\n")
        scratch_offset = self.bootinfo_base - self.psram_base - USB_SCRATCH_PSRAM_SIZE
        self.add_rust_constant(
            f"pub const USB_SCRATCH_PSRAM_OFFSET: u32 = 0x{scratch_offset:x};\n")
        self.add_rust_constant(
            f"pub const USB_SCRATCH_PSRAM_SIZE: u32 = 0x{USB_SCRATCH_PSRAM_SIZE:x};\n")

        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        m.submodules.usb_msc  = self.usb_msc
        m.submodules.usb_vbus = self.usb_vbus

        m.d.comb += platform.request("usb_vbus_en").o.eq(self.usb_vbus.en)

        m.submodules += super().elaborate(platform)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    # FIXME: more RAM needed for this bitstream because `serde` has quite huge code size.
    top_level_cli(BootloaderSoc, path=this_path,
                  argparse_fragment=lambda _: {
                      "cpu_variant": "tiliqua_rv32im_xip",
                      "mainram_size": 0x10000,
                  })
