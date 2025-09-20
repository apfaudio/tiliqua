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

from dataclasses import dataclass

import git
import hashlib
import os
import portalocker
import logging
import shutil
import subprocess

CPU_BASE = [
    '--xlen=32',
    '--with-rvm',
    '--lsu-l1',
    '--lsu-wishbone',
    '--lsu-l1-wishbone',
    '--fetch-l1',
    '--fetch-wishbone',
]

CPU_VARIANTS = {
    # enough performance for most control plane use
    # cases, assuming we are running from PSRAM
    "tiliqua_rv32im": CPU_BASE + [
        '--lsu-l1-sets=8',
        '--lsu-l1-ways=1',
        '--fetch-l1-sets=8',
        '--fetch-l1-ways=1',
    ],
    # special variant with big icache, necessary if
    # the CPU is directly fetching instructions from spiflash
    "tiliqua_rv32im_xip": CPU_BASE + [
        '--lsu-l1-sets=16',
        '--lsu-l1-ways=1',
        '--fetch-l1-sets=32',
        '--fetch-l1-ways=2',
        '--with-btb',
        '--relaxed-btb',
        '--with-late-alu',
    ],
    # Most performant variant that reasonably fits on the
    # ECP5-25, consumes about half the LUTs and has FPU
    # performance comparable to a low-end STM32.
    "tiliqua_rv32imafc": CPU_BASE + [
        '--with-rvc',
        '--with-rva',
        '--with-rvf',
        '--fma-reduced-accuracy',
        '--fpu-ignore-subnormal',
        '--with-btb',
        '--relaxed-btb',
        '--with-late-alu',
        '--lsu-l1-ways=2',
        '--lsu-l1-sets=16',
        '--fetch-l1-ways=2',
        '--fetch-l1-sets=16',
        '--with-gshare',
        '--with-ras',
        '--regfile-async',
        '--with-aligner-buffer',
        '--with-dispatcher-buffer',
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

    @dataclass
    class MemoryRegion:
        base: int
        size: int
        cacheable: bool
        executable: bool
        def get_flag(self):
            return f'--region base={self.base:x},size={self.size:x},main={int(self.cacheable)},exe={int(self.executable)}'

    def __init__(self, regions, variant="tiliqua", reset_addr=0x0):

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
        ] + [region.get_flag() for region in regions]
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
            # Prohibit simultaneous netlist generation when building multiple SoCs
            # in parallel. This only affects the first time SoCs are built with
            # new VexiiRiscv arguments or a bumped VexiiRiscv repository.
            with portalocker.TemporaryFileLock(
                    os.path.join(vexiiriscv_root, "tiliqua_sbt.lock"),
                    fail_when_locked=False,
                    timeout=60):
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
