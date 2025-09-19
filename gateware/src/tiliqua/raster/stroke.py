# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

from amaranth import *
from amaranth.build import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.wiring import In, Out

from .. import dsp
from ..dsp import ASQ
from ..video.framebuffer import DMAFramebuffer
from .plot import BlendMode, OffsetMode, PlotRequest


class Stroke(wiring.Component):

    """
    Frontend for stroke-raster converter (plotting of analog waveforms in CRT-style)

    Takes a synchronized stream of 4 channels (x, y, intensity, color), upsamples them
    and generates ``PlotRequest`` commands for blended drawing to a framebuffer.

    To obtain more points, the incoming stream is upsampled using an FIR-based
    fractional resampler. This is kind of analogous to sin(x)/x interpolation.

    To save resources, only the positions are upsampled, as the color and intensity
    are generally too quantized for upsampling to make any visual difference.

    There are a few optional signals exposed which can be used by user gateware or
    an SoC to scale or shift the waveforms around.
    """

    def __init__(self, *, fb: DMAFramebuffer, fs=192000, n_upsample=None,
                 default_hue=10, default_x=0, default_y=0):

        self.fb = fb
        self.fs = fs
        self.n_upsample = n_upsample

        self.hue       = Signal(4, init=default_hue);
        self.intensity = Signal(4, init=8);
        self.scale_x   = Signal(4, init=6);
        self.scale_y   = Signal(4, init=6);
        self.scale_p   = Signal(4, init=10);
        self.scale_c   = Signal(4, init=10);
        self.x_offset  = Signal(signed(16), init=default_x)
        self.y_offset  = Signal(signed(16), init=default_y)

        super().__init__({
            # Point stream to render
            # 4 channels: x, y, intensity, color
            "i": In(stream.Signature(data.ArrayLayout(ASQ, 4))),
            # Plot request output to shared backend
            "plot_req": Out(stream.Signature(PlotRequest)),
            # Internal point stream, upsampled from self.i (TODO no need to expose this)
            "point_stream": In(stream.Signature(data.ArrayLayout(ASQ, 4)))
        })


    def elaborate(self, platform) -> Module:
        m = Module()

        if self.n_upsample is not None and self.n_upsample != 1:
            # If interpolation is enabled, insert an FIR upsampling stage.
            m.submodules.split = split = dsp.Split(n_channels=4)
            m.submodules.merge = merge = dsp.Merge(n_channels=4)

            m.submodules.resample0 = resample0 = dsp.Resample(fs_in=self.fs, n_up=self.n_upsample, m_down=1)
            m.submodules.resample1 = resample1 = dsp.Resample(fs_in=self.fs, n_up=self.n_upsample, m_down=1)
            m.submodules.resample2 = resample2 = dsp.Duplicate(n=self.n_upsample)
            m.submodules.resample3 = resample3 = dsp.Duplicate(n=self.n_upsample)

            wiring.connect(m, wiring.flipped(self.i), split.i)

            wiring.connect(m, split.o[0], resample0.i)
            wiring.connect(m, split.o[1], resample1.i)
            wiring.connect(m, split.o[2], resample2.i)
            wiring.connect(m, split.o[3], resample3.i)

            wiring.connect(m, resample0.o, merge.i[0])
            wiring.connect(m, resample1.o, merge.i[1])
            wiring.connect(m, resample2.o, merge.i[2])
            wiring.connect(m, resample3.o, merge.i[3])

            wiring.connect(m, merge.o, self.point_stream)
        else:
            # No upsampling.
            wiring.connect(m, wiring.flipped(self.i), self.point_stream)

        # last sample
        sample_x = Signal(signed(16))
        sample_y = Signal(signed(16))
        sample_p = Signal(signed(16)) # intensity modulation
        sample_c = Signal(signed(16)) # color modulation

        # Overall x / y scale depends on ASQ fractional bits as we often take raw counts.
        # This ensures this component still works as expected with 10/16/24-bit samples.
        asq_extra_bits = ASQ.f_bits - 15

        # Pixel request generation
        new_color = Signal(unsigned(4))
        sample_intensity = Signal(unsigned(4))

        # Calculate new color (sample color + base hue)
        m.d.comb += new_color.eq(sample_c + self.hue)

        # Calculate sample intensity with bounds checking
        with m.If((sample_p + self.intensity > 0) & (sample_p + self.intensity <= 0xf)):
            m.d.comb += sample_intensity.eq(sample_p + self.intensity)
        with m.Else():
            m.d.comb += sample_intensity.eq(0)

        with m.FSM() as fsm:

            with m.State('LATCH0'):
                m.d.comb += self.point_stream.ready.eq(1)
                # Fired on every audio sample fs_strobe
                with m.If(self.point_stream.valid):
                    m.d.sync += [
                        sample_x.eq((self.point_stream.payload[0].as_value()>>(self.scale_x+asq_extra_bits)) + self.x_offset),
                        # invert sample_y for positive scope -> up
                        sample_y.eq((-self.point_stream.payload[1].as_value()>>(self.scale_y+asq_extra_bits)) + self.y_offset),
                        sample_p.eq(Mux(self.scale_p != 0xf, self.point_stream.payload[2].as_value()>>(self.scale_p+asq_extra_bits), 0)),
                        sample_c.eq(Mux(self.scale_c != 0xf, self.point_stream.payload[3].as_value()>>(self.scale_c+asq_extra_bits), 0)),
                    ]
                    m.next = 'SEND_PIXEL'

            with m.State('SEND_PIXEL'):
                # Generate pixel request for the shared `PlotRequest` backend
                m.d.comb += [
                    self.plot_req.valid.eq(1),
                    self.plot_req.payload.x.eq(sample_x),
                    self.plot_req.payload.y.eq(sample_y),
                    self.plot_req.payload.pixel.color.eq(new_color),
                    self.plot_req.payload.pixel.intensity.eq(sample_intensity),
                    self.plot_req.payload.blend.eq(BlendMode.ADDITIVE),  # CRT sim uses additive blending
                    self.plot_req.payload.offset.eq(OffsetMode.CENTER),  # Scope plots are centered
                ]

                with m.If(self.plot_req.ready):
                    m.next = 'LATCH0'

        return m
