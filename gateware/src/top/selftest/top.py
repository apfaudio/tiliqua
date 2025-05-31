# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Collect some information about Tiliqua health, display it on the video
output and log it over serial. This is mostly used to check for
hardware issues and for bringup.
"""

import os

from amaranth                    import *

from tiliqua.tiliqua_soc         import TiliquaSoc
from tiliqua.cli                 import top_level_cli

from luna.gateware.applets.speed_test import USBSpeedTestDevice, VENDOR_ID, PRODUCT_ID

class SelftestSoc(TiliquaSoc):
    brief = "Test & calibration utilities"

    def elaborate(self, platform):

        m = Module()

        m.submodules += super().elaborate(platform)

        m.submodules += USBSpeedTestDevice(generate_clocks=False,
                                           phy_name=platform.default_usb_connection,
                                           vid=VENDOR_ID,
                                           pid=PRODUCT_ID)

        return m

if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(SelftestSoc, path=this_path,
                  argparse_fragment=lambda _: {
                      # direct codec output registers
                      "poke_outputs": True,
                      "mainram_size": 0x4000,
                  })
