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

    class ScaleReg(csr.Register, access="w"):
        scale: csr.Field(csr.action.W, unsigned(8))

    class Position(csr.Register, access="w"):
        value: csr.Field(csr.action.W, unsigned(16))

    def __init__(self, fb, **kwargs):

        self.stroke = Stroke(fb=fb, **kwargs)

        regs = csr.Builder(addr_width=6, data_width=8)

        self._flags     = regs.add("flags",     self.Flags(),        offset=0x0)
        self._hue       = regs.add("hue",       self.HueReg(),       offset=0x4)
        self._intensity = regs.add("intensity", self.IntensityReg(), offset=0x8)
        self._xoffset   = regs.add("xoffset",   self.Position(),     offset=0xC)
        self._yoffset   = regs.add("yoffset",   self.Position(),     offset=0x10)
        self._xscale    = regs.add("xscale",    self.ScaleReg(),     offset=0x14)
        self._yscale    = regs.add("yscale",    self.ScaleReg(),     offset=0x18)
        self._pscale    = regs.add("pscale",    self.ScaleReg(),     offset=0x1C)
        self._cscale    = regs.add("cscale",    self.ScaleReg(),     offset=0x20)

        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "i": In(stream.Signature(data.ArrayLayout(ASQ, 4))),
            "en": In(1),
            "soc_en": In(1),
            "rotate_left": In(1),
            # CSR bus
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            # DMA bus (plotting)
            "bus_dma": Out(self.stroke.bus.signature),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        m.submodules += self.stroke

        wiring.connect(m, wiring.flipped(self.i), self.stroke.i)
        wiring.connect(m, self.stroke.bus, wiring.flipped(self.bus_dma))
        wiring.connect(m, wiring.flipped(self.bus), self._bridge.bus)

        m.d.comb += self.stroke.enable.eq(self.en & self.soc_en)
        m.d.comb += self.stroke.rotate_left.eq(self.rotate_left)

        with m.If(self._hue.f.hue.w_stb):
            m.d.sync += self.stroke.hue.eq(self._hue.f.hue.w_data)

        with m.If(self._intensity.f.intensity.w_stb):
            m.d.sync += self.stroke.intensity.eq(self._intensity.f.intensity.w_data)

        with m.If(self._xscale.f.scale.w_stb):
            m.d.sync += self.stroke.scale_x.eq(self._xscale.f.scale.w_data)

        with m.If(self._yscale.f.scale.w_stb):
            m.d.sync += self.stroke.scale_y.eq(self._yscale.f.scale.w_data)

        with m.If(self._xoffset.f.value.w_stb):
            m.d.sync += self.stroke.x_offset.eq(self._xoffset.f.value.w_data)

        with m.If(self._yoffset.f.value.w_stb):
            m.d.sync += self.stroke.y_offset.eq(self._yoffset.f.value.w_data)

        with m.If(self._pscale.f.scale.w_stb):
            m.d.sync += self.stroke.scale_p.eq(self._pscale.f.scale.w_data)

        with m.If(self._cscale.f.scale.w_stb):
            m.d.sync += self.stroke.scale_c.eq(self._cscale.f.scale.w_data)

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

    def __init__(self, fb, n_channels=4, **kwargs):

        self.n_channels = n_channels
        self.strokes = [Stroke(fb=fb, **kwargs)
                        for _ in range(self.n_channels)]

        regs = csr.Builder(addr_width=6, data_width=8)
        self._flags          = regs.add("flags",          self.Flags(),         offset=0x0)
        self._hue            = regs.add("hue",            self.Hue(),           offset=0x4)
        self._intensity      = regs.add("intensity",      self.Intensity(),     offset=0x8)
        self._timebase       = regs.add("timebase",       self.Timebase(),      offset=0xC)
        self._xscale         = regs.add("xscale",         self.XScale(),        offset=0x10)
        self._yscale         = regs.add("yscale",         self.YScale(),        offset=0x14)
        self._trigger_lvl    = regs.add("trigger_lvl",    self.TriggerLevel(),  offset=0x18)
        self._xpos           = regs.add("xpos",           self.XPosition(),     offset=0x1C)
        self._ypos           = [regs.add(f"ypos{i}",      self.YPosition(),
                                offset=(0x20+i*4)) for i in range(self.n_channels)]

        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "i": In(stream.Signature(data.ArrayLayout(ASQ, self.n_channels))),
            "en": In(1),
            "soc_en": In(1),
            "rotate_left": In(1),
            # CSR bus
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            # DMA buses, one for plotting each channel
            "bus_dma": Out(self.strokes[0].bus.signature).array(self.n_channels),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()

        timebase = Signal(shape=dsp.ASQ)
        trigger_lvl = Signal(shape=dsp.ASQ)
        trigger_always = Signal()

        self.isplit4 = dsp.Split(self.n_channels)

        wiring.connect(m, wiring.flipped(self.i), self.isplit4.i)

        m.submodules.bridge = self._bridge
        wiring.connect(m, wiring.flipped(self.bus), self._bridge.bus)

        m.submodules += self.strokes

        for i, s in enumerate(self.strokes):
            m.d.comb += s.enable.eq(self.en & self.soc_en)
            m.d.comb += s.rotate_left.eq(self.rotate_left)
            wiring.connect(m, s.bus, wiring.flipped(self.bus_dma[i]))

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
        m.submodules.rampsplit4 = rampsplit4 = dsp.Split(self.n_channels, replicate=True, source=ramp.o)

        # Rasterize ch0: Ramp => X, Audio => Y
        m.submodules.ch0_merge4 = ch0_merge4 = dsp.Merge(4)
        # HACK for stable trigger despite periodic cache misses
        # TODO: modify ramp generation instead?
        dsp.connect_peek(m, ch0_merge4.o, self.strokes[0].i, always_ready=True)
        ch0_merge4.wire_valid(m, [2, 3])
        wiring.connect(m, rampsplit4.o[0], ch0_merge4.i[0])
        wiring.connect(m, irep2.o[1], ch0_merge4.i[1])

        # Rasterize ch1-ch3: Ramp => X, Audio => Y
        for ch in range(1, self.n_channels):
            ch_merge4 = dsp.Merge(4)
            dsp.connect_peek(m, ch_merge4.o, self.strokes[ch].i, always_ready=True)
            m.submodules += ch_merge4
            ch_merge4.wire_valid(m, [2, 3])
            wiring.connect(m, rampsplit4.o[ch], ch_merge4.i[0])
            wiring.connect(m, self.isplit4.o[ch], ch_merge4.i[1])

        # Wishbone tweakables

        def normalize_scale_up(data: Signal(signed(16))):
            asq_extra_bits = ASQ.f_bits - 15
            if asq_extra_bits >= 0:
                return data << asq_extra_bits
            else:
                return data >> -asq_extra_bits

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
            m.d.sync += timebase.as_value().eq(normalize_scale_up(self._timebase.f.timebase.w_data))

        with m.If(self._xscale.f.xscale.w_stb):
            for s in self.strokes:
                m.d.sync += s.scale_x.eq(self._xscale.f.xscale.w_data)

        with m.If(self._yscale.f.yscale.w_stb):
            for s in self.strokes:
                m.d.sync += s.scale_y.eq(self._yscale.f.yscale.w_data)

        with m.If(self._trigger_lvl.f.trigger_level.w_stb):
            m.d.sync += trigger_lvl.as_value().eq(normalize_scale_up(self._trigger_lvl.f.trigger_level.w_data))

        with m.If(self._xpos.f.xpos.w_stb):
            for s in self.strokes:
                m.d.sync += s.x_offset.eq(self._xpos.f.xpos.w_data)

        for i, ypos_reg in enumerate(self._ypos):
            with m.If(ypos_reg.f.ypos.w_stb):
                m.d.sync += self.strokes[i].y_offset.eq(ypos_reg.f.ypos.w_data)

        return m

