#
# This file is part of LUNA.
#
# Copyright (c) 2023 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

from amaranth             import *
from amaranth.lib.wiring  import Component, In, Out

from amaranth_soc         import wishbone
from amaranth_soc.periph  import ConstantMap

import os
import logging

# Variants --------------------------------------------------------------------

CPU_VARIANTS = {
    "tiliqua_rv32im":  "VexiiRiscv",
    "tiliqua_rv32imafc": "VexiiRiscv_fpu",
}

JTAG_VARIANTS = []

# - VexRiscv ------------------------------------------------------------------

class VexRiscv(Component):
    #name       = "vexriscv"
    #arch       = "riscv"
    #byteorder  = "little"
    #data_width = 32

    def __init__(self, variant="tiliqua", reset_addr=0x20000000):
        self._variant    = variant
        self._reset_addr = reset_addr

        super().__init__({
            "ext_reset":     In(unsigned(1)),

            "irq_external":  In(unsigned(32)),
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

            "jtag_tms":  In(unsigned(1)),
            "jtag_tdi":  In(unsigned(1)),
            "jtag_tdo":  Out(unsigned(1)),
            "jtag_tck":  In(unsigned(1)),
            "dbg_reset": In(unsigned(1)),
            "ndm_reset": In(unsigned(1)),
            "stop_time": In(unsigned(1)),
        })

        # read source verilog
        if not variant in CPU_VARIANTS:
            raise ValueError(f"unsupported variant: {variant}")
        self._source_file = f"{CPU_VARIANTS[variant]}.v"
        self._source_path = os.path.join(os.path.dirname(__file__), "verilog", "vexriscv", self._source_file)
        if not os.path.exists(self._source_path):
            FileNotFoundError(f"Verilog source file not found: {self._source_path}")
        with open(self._source_path, "r") as f:
            logging.info(f"reading verilog file: {self._source_path}")
            self._source_verilog = f.read()

    #@property
    #def reset_addr(self):
    #    return self._reset_addr

    #@property
    #def muldiv(self):
    #    return "hard" # "hard" if self._cpu.with_muldiv else "soft"

    #@property
    #def constant_map(self):
    #    return ConstantMap(
    #        VEXRISCV          = True,
    #        RESET_ADDR        = self._reset_addr,
    #        ARCH_RISCV        = True,
    #        RISCV_MULDIV_SOFT = self.muldiv == "soft",
    #        BYTEORDER_LITTLE  = True,
    #    )

    def elaborate(self, platform):
        m = Module()

        # optional signals
        optional_signals = {}
        if self._variant in JTAG_VARIANTS:
            optional_signals = {
                "i_jtag_tms":       self.jtag_tms,
                "i_jtag_tdi":       self.jtag_tdi,
                "o_jtag_tdo":       self.jtag_tdo,
                "i_jtag_tck":       self.jtag_tck,
                "i_debugReset":     self.dbg_reset,
                "o_ndmreset":       self.ndm_reset,
                "o_stoptime":       self.stop_time,
            }

        # instantiate VexRiscv
        platform.add_file(self._source_file, self._source_verilog)
        self._cpu = Instance(
            "VexiiRiscv",

            # clock and reset
            i_clk                    = ClockSignal("sync"),
            i_reset                  = ResetSignal("sync") | self.ext_reset,

            # interrupts
            i_PrivilegedPlugin_logic_harts_0_int_m_software = self.irq_software,
            i_PrivilegedPlugin_logic_harts_0_int_m_timer         = self.irq_timer,
            i_PrivilegedPlugin_logic_harts_0_int_m_external      = self.irq_external,

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

            # optional signals
            **optional_signals,
        )

        m.submodules.vexriscv = self._cpu

        return m
