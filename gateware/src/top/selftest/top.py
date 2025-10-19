# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Collect some information about Tiliqua health, display it on the video
output and log it over serial. This is mostly used to check for
hardware issues and for calibration.
"""

import os

from amaranth import *
from amaranth.build import *
from amaranth.lib import wiring
from amaranth_soc import gpio
from luna.gateware.applets.speed_test import (PRODUCT_ID, VENDOR_ID,
                                              USBSpeedTestDevice)

from tiliqua.build import sim
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.tiliqua_soc import TiliquaSoc


class SelftestSoc(TiliquaSoc):
    help = BitstreamHelp(
        brief="Test & calibration utilities",
        io_left=['adc0', 'adc1', 'adc2', 'adc3', 'dac0', 'dac1', 'dac2', 'dac3'],
        io_right=['navigate menu', 'speedtest device', 'video out', 'gpio in (0)', 'gpio in (1)', '']
    )

    def __init__(self, **kwargs):

        # don't finalize the CSR bridge in TiliquaSoc, we're adding more peripherals.
        super().__init__(finalize_csr_bridge=False, **kwargs)

        self.gpio0_base = 0x00001000
        self.gpio1_base = 0x00001100

        self.gpio0 = gpio.Peripheral(pin_count=8, addr_width=3, data_width=8)
        self.csr_decoder.add(self.gpio0.bus, addr=self.gpio0_base, name="gpio0")

        self.gpio1 = gpio.Peripheral(pin_count=8, addr_width=3, data_width=8)
        self.csr_decoder.add(self.gpio1.bus, addr=self.gpio1_base, name="gpio1")

        # now we can freeze the memory map
        self.finalize_csr_bridge()

    def elaborate(self, platform):

        m = Module()

        if sim.is_hw(platform):

            def pmod_gpio(platform, ix):
                pmod_gpio = [
                    Resource(f"pmod_gpio", ix,
                        Subsignal("gpio0", Pins("1",  conn=("pmod", ix), dir='io')),
                        Subsignal("gpio1", Pins("2",  conn=("pmod", ix), dir='io')),
                        Subsignal("gpio2", Pins("3",  conn=("pmod", ix), dir='io')),
                        Subsignal("gpio3", Pins("4",  conn=("pmod", ix), dir='io')),
                        Subsignal("gpio4", Pins("7",  conn=("pmod", ix), dir='io')),
                        Subsignal("gpio5", Pins("8",  conn=("pmod", ix), dir='io')),
                        Subsignal("gpio6", Pins("9",  conn=("pmod", ix), dir='io')),
                        Subsignal("gpio7", Pins("10", conn=("pmod", ix), dir='io')),
                        Attrs(IO_TYPE="LVCMOS33", PULLMODE="DOWN"),
                    )
                ]
                platform.add_resources(pmod_gpio)
                return platform.request(f"pmod_gpio", ix)

            pmod_gpio0 = pmod_gpio(platform, 0)
            for n in range(8):
                wiring.connect(m, self.gpio0.pins[n], getattr(pmod_gpio0, f"gpio{n}"))

            pmod_gpio1 = pmod_gpio(platform, 1)
            for n in range(8):
                wiring.connect(m, self.gpio1.pins[n], getattr(pmod_gpio1, f"gpio{n}"))

            m.submodules += USBSpeedTestDevice(generate_clocks=False,
                                               phy_name=platform.default_usb_connection,
                                               vid=VENDOR_ID,
                                               pid=PRODUCT_ID)

        m.submodules += [self.gpio0, self.gpio1]


        m.submodules += super().elaborate(platform)

        return m

if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(SelftestSoc, path=this_path,
                  argparse_fragment=lambda _: {
                      # direct codec output registers
                      "poke_outputs": True,
                  })
