# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

"""
Wrapper for VexiiRiscv netlist generation.

All netlists required for normal project compilation are checked into
this repository, so SpinalHDL/Scala does not need to be installed.

Arguments to CPU generation are hashed to a netlist verilog file. If
the CPU generation flags are changed, the cache of netlists in this
repository will not be hit and `sbt` is invoked to generate a new core.
"""

from amaranth             import *
from amaranth.lib.wiring  import Component, In, Out

from amaranth_soc         import wishbone
from amaranth_soc.periph  import ConstantMap

import git
import hashlib
import os
import logging
import shutil
import subprocess

CPU_VARIANTS = {
    "tiliqua_rv32im": [
        '--xlen=32',
        '--with-rvm',
        '--lsu-l1',
        '--lsu-wishbone',
        '--lsu-l1-wishbone',
        '--fetch-l1',
        '--fetch-wishbone',
        '--with-btb',
        '--with-gshare',
        '--with-ras',
        '--regfile-async',
        '--with-aligner-buffer',
        '--with-dispatcher-buffer',
        '--with-late-alu',
    ]
}

class VexiiRiscv(Component):

    # Commands used to generate a VexiiRiscv netlist using SpinalHDL
    # if we miss our local cache of pre-generated netlists. In general
    # users should never need to generate their own netlists unless
    # they are actually tweaking the CPU architecture flags.

    # Directory of VexiiRiscv submodule and generated netlist
    PATH_GENERATE = 'deps/VexiiRiscv/VexiiRiscv.v'

    # Command used to create a new netlist
    CMD_GENERATE = 'sbt "Test/runMain vexiiriscv.Generate {args}"'

    # Local storage (in this repository) of cached netlists
    PATH_CACHE = os.path.join(os.path.dirname(__file__), "verilog")

    def __init__(self, variant="tiliqua", reset_addr=0x0,
                 cached_base=0x0, cached_size=0x80000000,
                 csr_base=0xf0000000, csr_size=0x10000):

        self._variant    = variant
        self._reset_addr = reset_addr

        super().__init__({
            "ext_reset":     In(unsigned(1)),

            "irq_external":  In(unsigned(1)),
            "irq_timer":     In(unsigned(1)),
            "irq_software":  In(unsigned(1)),

            "ibus": Out(wishbone.Signature(
                addr_width=30,
                data_width=32,
                granularity=8,
                features=("err", "cti", "bte")
            )),
            "dbus": Out(wishbone.Signature(
                addr_width=30,
                data_width=32,
                granularity=8,
                features=("err", "cti", "bte")
            )),
            "pbus": Out(wishbone.Signature(
                addr_width=30,
                data_width=32,
                granularity=8,
                features=("err", "cti", "bte")
            )),
        })

        if not variant in CPU_VARIANTS:
            raise ValueError(f"VexiiRiscv: unsupported CPU variant: {variant}")

        vexiiriscv_root, vexiiriscv_gen_file = os.path.split(self.PATH_GENERATE)
        netlist_arguments = CPU_VARIANTS[variant]
        # Add required reset vector and PMP region arguments.
        netlist_arguments = netlist_arguments + [
            f'--reset-vector {hex(reset_addr)}',
            f'--region base={cached_base:x},size={cached_size:x},main=1,exe=1',
            f'--region base={csr_base:x},size={csr_size:x},main=0,exe=0',
        ]
        vexiiriscv_hash = git.Repo(vexiiriscv_root).head.object.hexsha
        netlist_name = self.generate_netlist_name(vexiiriscv_hash, netlist_arguments)

        # Where we expect the netlist to be, if it's already been generated.
        self._source_file = f"{netlist_name}.v"
        self._source_path = os.path.join(self.PATH_CACHE, self._source_file)

        # If it's missing, the user has changed some CPU flags - generate a new netlist.
        if not os.path.exists(self._source_path):
            logging.info(f"VexiiRiscv source file not cached at: {self._source_path}")
            logging.info(f"Generate VexiiRiscv using 'sbt' with {netlist_arguments}...")
            cmd = self.CMD_GENERATE.format(args=' '.join(netlist_arguments))
            subprocess.check_call(cmd, shell=True, cwd=vexiiriscv_root)
            logging.info(f"Copy netlist from {self.PATH_GENERATE} to {self._source_file}...")
            shutil.copyfile(self.PATH_GENERATE, self._source_path)
        else:
            logging.info(f"VexiiRiscv verilog netlist already present: {self._source_path}")

        with open(self._source_path, "r") as f:
            logging.info(f"Reading VexiiRiscv netlist: {self._source_path}")
            self._source_verilog = f.read()

    @staticmethod
    def generate_netlist_name(vexii_hash, arguments):
        md5_hash = hashlib.md5()
        md5_hash.update(vexii_hash.encode('utf-8'))
        for arg in arguments:
            md5_hash.update(arg.encode('utf-8'))
        return "VexiiRiscv_" + md5_hash.hexdigest()

    @property
    def reset_addr(self):
        return self._reset_addr

    def elaborate(self, platform):
        m = Module()

        platform.add_file(self._source_file, self._source_verilog)
        self._cpu = Instance(
            "VexiiRiscv",

            # clock and reset
            i_clk                    = ClockSignal("sync"),
            i_reset                  = ResetSignal("sync") | self.ext_reset,

            # interrupts
            i_PrivilegedPlugin_logic_harts_0_int_m_software = self.irq_software,
            i_PrivilegedPlugin_logic_harts_0_int_m_timer    = self.irq_timer,
            i_PrivilegedPlugin_logic_harts_0_int_m_external = self.irq_external,

            # instruction bus
            o_FetchL1WishbonePlugin_logic_bus_ADR       = self.ibus.adr,
            o_FetchL1WishbonePlugin_logic_bus_DAT_MOSI  = self.ibus.dat_w,
            o_FetchL1WishbonePlugin_logic_bus_SEL       = self.ibus.sel,
            o_FetchL1WishbonePlugin_logic_bus_CYC       = self.ibus.cyc,
            o_FetchL1WishbonePlugin_logic_bus_STB       = self.ibus.stb,
            o_FetchL1WishbonePlugin_logic_bus_WE        = self.ibus.we,
            o_FetchL1WishbonePlugin_logic_bus_CTI       = self.ibus.cti,
            o_FetchL1WishbonePlugin_logic_bus_BTE       = self.ibus.bte,
            i_FetchL1WishbonePlugin_logic_bus_DAT_MISO  = self.ibus.dat_r,
            i_FetchL1WishbonePlugin_logic_bus_ACK       = self.ibus.ack,
            i_FetchL1WishbonePlugin_logic_bus_ERR       = self.ibus.err,

            # data bus
            o_LsuL1WishbonePlugin_logic_bus_ADR       = self.dbus.adr,
            o_LsuL1WishbonePlugin_logic_bus_DAT_MOSI  = self.dbus.dat_w,
            o_LsuL1WishbonePlugin_logic_bus_SEL       = self.dbus.sel,
            o_LsuL1WishbonePlugin_logic_bus_CYC       = self.dbus.cyc,
            o_LsuL1WishbonePlugin_logic_bus_STB       = self.dbus.stb,
            o_LsuL1WishbonePlugin_logic_bus_WE        = self.dbus.we,
            o_LsuL1WishbonePlugin_logic_bus_CTI       = self.dbus.cti,
            o_LsuL1WishbonePlugin_logic_bus_BTE       = self.dbus.bte,
            i_LsuL1WishbonePlugin_logic_bus_DAT_MISO  = self.dbus.dat_r,
            i_LsuL1WishbonePlugin_logic_bus_ACK       = self.dbus.ack,
            i_LsuL1WishbonePlugin_logic_bus_ERR       = self.dbus.err,

            # peripheral bus
            o_LsuCachelessWishbonePlugin_logic_bridge_down_ADR       = self.pbus.adr,
            o_LsuCachelessWishbonePlugin_logic_bridge_down_DAT_MOSI  = self.pbus.dat_w,
            o_LsuCachelessWishbonePlugin_logic_bridge_down_SEL       = self.pbus.sel,
            o_LsuCachelessWishbonePlugin_logic_bridge_down_CYC       = self.pbus.cyc,
            o_LsuCachelessWishbonePlugin_logic_bridge_down_STB       = self.pbus.stb,
            o_LsuCachelessWishbonePlugin_logic_bridge_down_WE        = self.pbus.we,
            o_LsuCachelessWishbonePlugin_logic_bridge_down_CTI       = self.pbus.cti,
            o_LsuCachelessWishbonePlugin_logic_bridge_down_BTE       = self.pbus.bte,
            i_LsuCachelessWishbonePlugin_logic_bridge_down_DAT_MISO  = self.pbus.dat_r,
            i_LsuCachelessWishbonePlugin_logic_bridge_down_ACK       = self.pbus.ack,
            i_LsuCachelessWishbonePlugin_logic_bridge_down_ERR       = self.pbus.err,
        )

        m.submodules.vexriscv = self._cpu

        return m
