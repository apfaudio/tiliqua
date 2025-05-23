# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Collect some information about Tiliqua health, display it on the video
output and log it over serial. This is mostly used to check for
hardware issues and for bringup.
"""

import os

from tiliqua.tiliqua_soc         import TiliquaSoc
from tiliqua.cli                 import top_level_cli

class SelftestSoc(TiliquaSoc):
    brief = "Test & calibration utilities"

if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(SelftestSoc, path=this_path,
                  argparse_fragment=lambda _: {
                      # direct codec output registers
                      "poke_outputs": True,
                      "mainram_size": 0x4000,
                  })
