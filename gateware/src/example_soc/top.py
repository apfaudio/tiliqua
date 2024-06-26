#
# This file is part of LUNA.
#
# Copyright (c) 2020 Great Scott Gadgets <info@greatscottgadgets.com>
# SPDX-License-Identifier: BSD-3-Clause

import logging
import os
import sys

from amaranth                                    import Elaboratable, Module, Cat
from amaranth.hdl.rec                            import Record

from luna_soc.gateware.cpu.vexriscv              import VexRiscv
from luna_soc.gateware.lunasoc                   import LunaSoC
from luna_soc.gateware.csr                       import GpioPeripheral, LedPeripheral

from luna_soc.util.readbin                       import get_mem_data

from tiliqua.tiliqua_platform                    import TiliquaPlatform
from tiliqua.psram_peripheral                    import PSRAMPeripheral

from tiliqua.i2c                                 import I2CPeripheral
from tiliqua.encoder                             import EncoderPeripheral
from tiliqua                                     import eurorack_pmod

CLOCK_FREQUENCIES_MHZ = {
    'sync': 60
}

# - HelloSoc ------------------------------------------------------------------

class HelloSoc(Elaboratable):
    def __init__(self, clock_frequency):

        # create a stand-in for our UART
        self.uart_pins = Record([
            ('rx', [('i', 1)]),
            ('tx', [('o', 1)])
        ])

        # create a stand-in for our I2C pins
        self.i2c_pins = Record([
            ('sda', [('i', 1), ('o', 1), ('oe', 1)]),
            ('scl', [('i', 1), ('o', 1), ('oe', 1)]),
        ])

        self.encoder_pins = Record([
            ('i', [('i', 1)]),
            ('q', [('i', 1)]),
            ('s', [('i', 1)])
        ])

        # create our SoC
        self.soc = LunaSoC(
            cpu=VexRiscv(reset_addr=0x40000000, variant="cynthion"),
            clock_frequency=clock_frequency,
        )

        # ... read our firmware binary ...
        firmware = get_mem_data("src/example_soc/fw/firmware.bin",
                                data_width=32, endianness="little")

        # ... add core peripherals: memory, timer, uart ...
        self.soc.add_core_peripherals(
            uart_pins=self.uart_pins,
            internal_sram_size=32768,
            internal_sram_init=firmware
        )

        # ... add memory-mapped psram/hyperram peripheral (128Mbit)
        psram_base = 0x20000000
        self.soc.psram = PSRAMPeripheral(size=16*1024*1024)
        self.soc.add_peripheral(self.soc.psram, addr=psram_base)

        # ... add our LED peripheral, for simple output ...
        self.leds = LedPeripheral()
        self.soc.add_peripheral(self.leds, addr=0xf0001000)

        # ... add an I2C transciever
        self.i2c0 = I2CPeripheral(pads=self.i2c_pins, period_cyc=240)
        self.soc.add_peripheral(self.i2c0, addr=0xf0002000)

        self.encoder0 = EncoderPeripheral(pins=self.encoder_pins)
        self.soc.add_peripheral(self.encoder0, addr=0xf0003000)

        super().__init__()

    def elaborate(self, platform):
        m = Module()
        m.submodules.soc = self.soc

        # generate our domain clocks/resets
        m.submodules.car = platform.clock_domain_generator(clock_frequencies=CLOCK_FREQUENCIES_MHZ)

        # Connect up our UART
        uart_io = platform.request("uart", 0)
        m.d.comb += [
            uart_io.tx.o.eq(self.uart_pins.tx),
            self.uart_pins.rx.eq(uart_io.rx)
        ]
        if hasattr(uart_io.tx, 'oe'):
            m.d.comb += uart_io.tx.oe.eq(~self.soc.uart._phy.tx.rdy),

        # Connect up the rotary encoder + switch
        enc = platform.request("encoder", 0)
        m.d.comb += [
            self.encoder_pins.i.i.eq(enc.i.i),
            self.encoder_pins.q.i.eq(enc.q.i),
            self.encoder_pins.s.i.eq(enc.s.i),
        ]

        # Connect i2c peripheral to mobo i2c
        mobo_i2c = platform.request("mobo_i2c")
        m.d.comb += [
            mobo_i2c.sda.o.eq(self.i2c_pins.sda.o),
            mobo_i2c.sda.oe.eq(self.i2c_pins.sda.oe),
            self.i2c_pins.sda.i.eq(mobo_i2c.sda.i),
            mobo_i2c.scl.o.eq(self.i2c_pins.scl.o),
            mobo_i2c.scl.oe.eq(self.i2c_pins.scl.oe),
            self.i2c_pins.scl.i.eq(mobo_i2c.scl.i),
        ]

        # Enable LED driver on motherboard
        m.d.comb += platform.request("mobo_leds_oe").o.eq(1),

        # add a eurorack pmod that does nothing
        m.submodules.pmod0 = pmod0 = eurorack_pmod.EurorackPmod(
                pmod_pins=platform.request("audio_ffc"),
                hardware_r33=True,
                touch_enabled=True)

        return m

if __name__ == "__main__":
    from luna_soc import top_level_cli
    os.environ["AMARANTH_verbose"] = "1"
    os.environ["AMARANTH_debug_verilog"] = "1"
    os.environ["AMARANTH_nextpnr_opts"] = "--timing-allow-fail"
    os.environ["LUNA_PLATFORM"] = "tiliqua.tiliqua_platform:TiliquaPlatform"
    design = HelloSoc(clock_frequency=int(60e6))
    top_level_cli(design)
