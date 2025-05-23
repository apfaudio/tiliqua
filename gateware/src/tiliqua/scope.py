# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Multi-channel oscilloscope and vectorscope SoC peripherals.
"""

from amaranth                                    import *
from amaranth.lib                                import wiring, data, stream, fifo
from amaranth.lib.wiring                         import In, Out

from amaranth_soc                                import csr

from tiliqua                                     import dsp
from tiliqua.raster_stroke                       import Stroke
from tiliqua.eurorack_pmod                       import ASQ

class VectorTracePeripheral(wiring.Component):

    class Flags(csr.Register, access="w"):
        enable: csr.Field(csr.action.W, unsigned(1))
        rotate_left: csr.Field(csr.action.W, unsigned(1))

    class HueReg(csr.Register, access="w"):
        hue: csr.Field(csr.action.W, unsigned(8))

    class IntensityReg(csr.Register, access="w"):
        intensity: csr.Field(csr.action.W, unsigned(8))

    class XScaleReg(csr.Register, access="w"):
        xscale: csr.Field(csr.action.W, unsigned(8))

    class YScaleReg(csr.Register, access="w"):
        yscale: csr.Field(csr.action.W, unsigned(8))

    def __init__(self, fb, bus_dma, **kwargs):

        self.stroke = Stroke(fb=fb, **kwargs)
        bus_dma.add_master(self.stroke.bus)

        regs = csr.Builder(addr_width=5, data_width=8)

        self._flags     = regs.add("flags",     self.Flags(),        offset=0x0)
        self._hue       = regs.add("hue",       self.HueReg(),       offset=0x4)
        self._intensity = regs.add("intensity", self.IntensityReg(), offset=0x8)
        self._xscale    = regs.add("xscale",    self.XScaleReg(),    offset=0xC)
        self._yscale    = regs.add("yscale",    self.YScaleReg(),    offset=0x10)

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "i": In(stream.Signature(data.ArrayLayout(ASQ, 4))),
            "en": In(1),
            "soc_en": In(1),
            "rotate_left": In(1),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        m.submodules += self.stroke

        wiring.connect(m, wiring.flipped(self.i), self.stroke.i)
        wiring.connect(m, wiring.flipped(self.bus), self._bridge.bus)

        m.d.comb += self.stroke.enable.eq(self.en & self.soc_en)
        m.d.comb += self.stroke.rotate_left.eq(self.rotate_left)

        with m.If(self._hue.f.hue.w_stb):
            m.d.sync += self.stroke.hue.eq(self._hue.f.hue.w_data)

        with m.If(self._intensity.f.intensity.w_stb):
            m.d.sync += self.stroke.intensity.eq(self._intensity.f.intensity.w_data)

        with m.If(self._xscale.f.xscale.w_stb):
            m.d.sync += self.stroke.scale_x.eq(self._xscale.f.xscale.w_data)

        with m.If(self._yscale.f.yscale.w_stb):
            m.d.sync += self.stroke.scale_y.eq(self._yscale.f.yscale.w_data)

        with m.If(self._flags.f.enable.w_stb):
            m.d.sync += self.soc_en.eq(self._flags.f.enable.w_data)

        with m.If(self._flags.f.rotate_left.w_stb):
            m.d.sync += self.rotate_left.eq(self._flags.f.rotate_left.w_data)

        return m

class ScopeTracePeripheral(wiring.Component):

    class Flags(csr.Register, access="w"):
        enable: csr.Field(csr.action.W, unsigned(1))
        rotate_left: csr.Field(csr.action.W, unsigned(1))
        trigger_always: csr.Field(csr.action.W, unsigned(1))

    class Hue(csr.Register, access="w"):
        hue: csr.Field(csr.action.W, unsigned(8))

    class Intensity(csr.Register, access="w"):
        intensity: csr.Field(csr.action.W, unsigned(8))

    class Timebase(csr.Register, access="w"):
        timebase: csr.Field(csr.action.W, unsigned(16))

    class XScale(csr.Register, access="w"):
        xscale: csr.Field(csr.action.W, unsigned(8))

    class YScale(csr.Register, access="w"):
        yscale: csr.Field(csr.action.W, unsigned(8))

    class TriggerLevel(csr.Register, access="w"):
        trigger_level: csr.Field(csr.action.W, unsigned(16))

    class XPosition(csr.Register, access="w"):
        xpos: csr.Field(csr.action.W, unsigned(16))

    class YPosition(csr.Register, access="w"):
        ypos: csr.Field(csr.action.W, unsigned(16))

    def __init__(self, fb, bus_dma, **kwargs):

        self.strokes = [Stroke(fb=fb, n_upsample=None, **kwargs)
                        for _ in range(4)]

        for s in self.strokes:
            bus_dma.add_master(s.bus)

        regs = csr.Builder(addr_width=6, data_width=8)
        self._flags          = regs.add("flags",          self.Flags(),         offset=0x0)
        self._hue            = regs.add("hue",            self.Hue(),           offset=0x4)
        self._intensity      = regs.add("intensity",      self.Intensity(),     offset=0x8)
        self._timebase       = regs.add("timebase",       self.Timebase(),      offset=0xC)
        self._xscale         = regs.add("xscale",         self.XScale(),        offset=0x10)
        self._yscale         = regs.add("yscale",         self.YScale(),        offset=0x14)
        self._trigger_lvl    = regs.add("trigger_lvl",    self.TriggerLevel(),  offset=0x18)
        self._xpos           = regs.add("xpos",           self.XPosition(),     offset=0x1C)
        self._ypos           = [regs.add(f"ypos{i}",      self.YPosition(),     offset=(0x20+i*4)) for i in range(4)]

        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "i": In(stream.Signature(data.ArrayLayout(ASQ, 4))),
            "en": In(1),
            "soc_en": In(1),
            "rotate_left": In(1),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()

        timebase = Signal(shape=dsp.ASQ)
        trigger_lvl = Signal(shape=dsp.ASQ)
        trigger_always = Signal()

        m.submodules.plot_fifo = plot_fifo = fifo.SyncFIFOBuffered(
            width=data.ArrayLayout(ASQ, 4).as_shape().width, depth=64)
        self.isplit4 = dsp.Split(4)

        wiring.connect(m, wiring.flipped(self.i), plot_fifo.w_stream)
        wiring.connect(m, plot_fifo.r_stream, self.isplit4.i)

        m.submodules.bridge = self._bridge
        wiring.connect(m, wiring.flipped(self.bus), self._bridge.bus)

        m.submodules += self.strokes

        for s in self.strokes:
            m.d.comb += s.enable.eq(self.en & self.soc_en)
            m.d.comb += s.rotate_left.eq(self.rotate_left)

        # Scope and trigger
        # Ch0 is routed through trigger, the rest are not.
        m.submodules.isplit4 = self.isplit4

        # 2 copies of input channel 0
        m.submodules.irep2 = irep2 = dsp.Split(2, replicate=True, source=self.isplit4.o[0])

        # Send one copy to trigger => ramp => X
        m.submodules.trig = trig = dsp.Trigger()
        m.submodules.ramp = ramp = dsp.Ramp()
        # Audio => Trigger
        dsp.connect_remap(m, irep2.o[0], trig.i, lambda o, i: [
            i.payload.sample.eq(o.payload),
            i.payload.threshold.eq(trigger_lvl),
        ])
        # Trigger => Ramp
        dsp.connect_remap(m, trig.o, ramp.i, lambda o, i: [
            i.payload.trigger.eq(o.payload | trigger_always),
            i.payload.td.eq(timebase),
        ])

        # Split ramp into 4 streams, one for each channel
        m.submodules.rampsplit4 = rampsplit4 = dsp.Split(4, replicate=True, source=ramp.o)

        # Rasterize ch0: Ramp => X, Audio => Y
        m.submodules.ch0_merge4 = ch0_merge4 = dsp.Merge(4, sink=self.strokes[0].i)
        ch0_merge4.wire_valid(m, [2, 3])
        wiring.connect(m, rampsplit4.o[0], ch0_merge4.i[0])
        wiring.connect(m, irep2.o[1], ch0_merge4.i[1])

        # Rasterize ch1-ch3: Ramp => X, Audio => Y
        for ch in range(1, 4):
            ch_merge4 = dsp.Merge(4, sink=self.strokes[ch].i)
            m.submodules += ch_merge4
            ch_merge4.wire_valid(m, [2, 3])
            wiring.connect(m, rampsplit4.o[ch], ch_merge4.i[0])
            wiring.connect(m, self.isplit4.o[ch], ch_merge4.i[1])

        # Wishbone tweakables

        with m.If(self._flags.f.enable.w_stb):
            m.d.sync += self.soc_en.eq(self._flags.f.enable.w_data)

        with m.If(self._flags.f.trigger_always.w_stb):
            m.d.sync += trigger_always.eq(self._flags.f.trigger_always.w_data)

        with m.If(self._flags.f.rotate_left.w_stb):
            m.d.sync += self.rotate_left.eq(self._flags.f.rotate_left.w_data)

        with m.If(self._hue.f.hue.w_stb):
            for ch, s in enumerate(self.strokes):
                m.d.sync += s.hue.eq(self._hue.f.hue.w_data + ch*3)

        with m.If(self._intensity.f.intensity.w_stb):
            for s in self.strokes:
                m.d.sync += s.intensity.eq(self._intensity.f.intensity.w_data)

        with m.If(self._timebase.f.timebase.w_stb):
            m.d.sync += timebase.as_value().eq(self._timebase.f.timebase.w_data)

        with m.If(self._xscale.f.xscale.w_stb):
            for s in self.strokes:
                m.d.sync += s.scale_x.eq(self._xscale.f.xscale.w_data)

        with m.If(self._yscale.f.yscale.w_stb):
            for s in self.strokes:
                m.d.sync += s.scale_y.eq(self._yscale.f.yscale.w_data)

        with m.If(self._trigger_lvl.f.trigger_level.w_stb):
            m.d.sync += trigger_lvl.as_value().eq(self._trigger_lvl.f.trigger_level.w_data)

        with m.If(self._xpos.f.xpos.w_stb):
            for s in self.strokes:
                m.d.sync += s.x_offset.eq(self._xpos.f.xpos.w_data)

        for i, ypos_reg in enumerate(self._ypos):
            with m.If(ypos_reg.f.ypos.w_stb):
                m.d.sync += self.strokes[i].y_offset.eq(ypos_reg.f.ypos.w_data)

        return m

