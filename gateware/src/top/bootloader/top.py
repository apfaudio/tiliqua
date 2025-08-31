# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import os

from tiliqua.build.cli import top_level_cli
from tiliqua.tiliqua_soc import TiliquaSoc

if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    # FIXME: more RAM needed for this bitstream because `serde` has quite huge code size.
    top_level_cli(TiliquaSoc, path=this_path,
                  argparse_fragment=lambda _: {
                      "cpu_variant": "tiliqua_rv32im_xip",
                      "mainram_size": 0x8000,
                  })
