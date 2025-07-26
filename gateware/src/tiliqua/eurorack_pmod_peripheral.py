# Peripheral for accessing eurorack-pmod hardware from an SoC.
#
# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

import os

from amaranth                   import *
from amaranth.build             import *
from amaranth.lib               import wiring, data, stream
from amaranth.lib.wiring        import In, Out, flipped, connect
from amaranth.lib.cdc           import FFSynchronizer

from amaranth_soc               import csr

from amaranth_future            import fixed

class Peripheral(wiring.Component):

    class ISampleReg(csr.Register, access="r"):
        sample: csr.Field(csr.action.R, unsigned(16))

    class OSampleReg(csr.Register, access="w"):
        sample: csr.Field(csr.action.W, unsigned(16))

    class TouchReg(csr.Register, access="r"):
        touch: csr.Field(csr.action.R, unsigned(8))

    class TouchErrorsReg(csr.Register, access="r"):
        value: csr.Field(csr.action.R, unsigned(8))

    class LEDReg(csr.Register, access="w"):
        led: csr.Field(csr.action.W, unsigned(8))

    class JackReg(csr.Register, access="r"):
        jack: csr.Field(csr.action.R, unsigned(8))

    class InfoReg(csr.Register, access="r"):
        f_bits: csr.Field(csr.action.R, unsigned(8))

    class FlagsReg(csr.Register, access="w"):
        mute: csr.Field(csr.action.W, unsigned(1))
        hard_reset: csr.Field(csr.action.W, unsigned(1))

    class CalibrationConstant(csr.Register, access="w"):
        value: csr.Field(csr.action.W, signed(32))

    class CalibrationReg(csr.Register, access="rw"):
        channel: csr.Field(csr.action.W, unsigned(3))
        write:   csr.Field(csr.action.W, unsigned(1))
        done:    csr.Field(csr.action.R, unsigned(1))

    def __init__(self, *, pmod, poke_outputs=False, **kwargs):
        self.pmod = pmod
        self.poke_outputs = poke_outputs

        regs = csr.Builder(addr_width=6, data_width=8)

        # Calibration constant writing
        self._cal_a = regs.add("cal_a", self.CalibrationConstant())
        self._cal_b = regs.add("cal_b", self.CalibrationConstant())
        self._cal_reg = regs.add("cal_reg", self.CalibrationReg())

        # ADC and input samples
        self._sample_i = [regs.add(f"sample_i{i}", self.ISampleReg()) for i in range(4)]

        if self.poke_outputs:
            self._sample_o = [regs.add(f"sample_o{ch}", self.OSampleReg()) for ch in range(4)]

        # Touch sensing
        self._touch = [regs.add(f"touch{i}", self.TouchReg()) for i in range(8)]
        self._touch_err = regs.add("touch_err", self.TouchErrorsReg())

        # LED control
        self._led_mode = regs.add("led_mode", self.LEDReg())
        self._led = [regs.add(f"led{i}", self.LEDReg()) for i in range(8)]

        # I2C peripheral data
        self._jack = regs.add("jack", self.JackReg())
        self._info = regs.add("info", self.InfoReg())

        self._flags = regs.add("flags", self.FlagsReg())

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "mute": In(1, init=1),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge

        connect(m, flipped(self.bus), self._bridge.bus)

        m.d.comb += [
            self._touch_err.f.value.r_data.eq(self.pmod.touch_err),
            self._jack.f.jack.r_data.eq(self.pmod.jack),
            self._info.f.f_bits.r_data.eq(self.pmod.i_cal.payload[0].shape().f_bits),
        ]

        mute_reg = Signal(init=1)
        m.d.comb += self.pmod.codec_mute.eq(mute_reg | self.mute)
        with m.If(self._flags.f.mute.w_stb):
            m.d.sync += mute_reg.eq(self._flags.f.mute.w_data)

        with m.If(self._flags.f.hard_reset.w_stb & self._flags.f.hard_reset.w_data):
            # Strobe PMOD hard reset.
            m.d.comb += self.pmod.hard_reset.eq(1)

        with m.If(self._led_mode.f.led.w_stb):
            m.d.sync += self.pmod.led_mode.eq(self._led_mode.f.led.w_data)

        for i in range(8):
            m.d.comb += self._touch[i].f.touch.r_data.eq(self.pmod.touch[i])
            with m.If(self._led[i].f.led.w_stb):
                m.d.sync += self.pmod.led[i].eq(self._led[i].f.led.w_data)

        for i in range(4):
            m.d.comb += self._sample_i[i].f.sample.r_data.eq(self.pmod.calibrator.o_cal_peek[i])

        if self.poke_outputs:
            m.d.comb += self.pmod.i_cal.valid.eq(1)
            for i in range(4):
                with m.If(self._sample_o[i].f.sample.w_stb):
                    m.d.sync += self.pmod.i_cal.payload[i].eq(
                            self._sample_o[i].f.sample.w_data)

        #
        # Writing calibration constants.
        # Write calibration constants, then write a '1' to the 'write' flag.
        # When 'done' is 1, the constant has been committed and another one
        # may be written.
        #

        with m.If(self._cal_a.f.value.w_stb):
            m.d.sync += self.pmod.calibrator.cal_mem_write.payload.a.eq(self._cal_a.f.value.w_data)
        with m.If(self._cal_b.f.value.w_stb):
            m.d.sync += self.pmod.calibrator.cal_mem_write.payload.b.eq(self._cal_b.f.value.w_data)
        with m.If(self._cal_reg.f.channel.w_stb):
            m.d.sync += self.pmod.calibrator.cal_mem_write.payload.channel.eq(self._cal_reg.f.channel.w_data)

        with m.If(self._cal_reg.f.write.w_stb & self._cal_reg.f.write.w_data):
            m.d.sync += self.pmod.calibrator.cal_mem_write.valid.eq(1)
            m.d.sync += self._cal_reg.f.done.r_data.eq(0)

        with m.If(self.pmod.calibrator.cal_mem_write.valid & self.pmod.calibrator.cal_mem_write.ready):
            m.d.sync += self.pmod.calibrator.cal_mem_write.valid.eq(0)
            m.d.sync += self._cal_reg.f.done.r_data.eq(1)

        return m
