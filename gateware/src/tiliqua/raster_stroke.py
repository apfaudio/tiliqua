# Utilities and effects for rasterizing information to a framebuffer.
#
# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import colorsys
import os

from amaranth                import *
from amaranth.build          import *
from amaranth.lib            import wiring, data, stream
from amaranth.lib.wiring     import In, Out
from amaranth.lib.fifo       import SyncFIFOBuffered
from amaranth.lib.cdc        import FFSynchronizer

from amaranth_future         import fixed

from tiliqua                 import dsp
from tiliqua.dma_framebuffer import DMAFramebuffer
from tiliqua.eurorack_pmod   import ASQ

from amaranth_soc            import wishbone, csr

class Stroke(wiring.Component):

    """
    Read samples, upsample them, and draw to a framebuffer.
    Pixels are DMA'd to PSRAM as a wishbone master, NOT in bursts, as we have no idea
    where each pixel is going to land beforehand. This is the most expensive use of
    PSRAM time in this project as we spend ages waiting on memory latency.

    TODO: can we somehow cache bursts of pixels here?

    Each pixel must be read before we write it for 2 reasons:
    - We have 4 pixels per word, so we can't just write 1 pixel as it would erase the
      adjacent ones.
    - We don't just set max intensity on drawing a pixel, rather we read the current
      intensity and add to it. Otherwise, we get no intensity gradient and the display
      looks nowhere near as nice :)

    To obtain more points, the pixels themselves are upsampled using an FIR-based
    fractional resampler. This is kind of analogous to sin(x)/x interpolation.
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
            # Rotate all draws 90 degrees to the left (screen_rotation)
            "rotate_left": In(1),
            # We are a DMA master (no burst support)
            "bus":  Out(wishbone.Signature(addr_width=fb.bus.addr_width, data_width=32, granularity=8)),
            # Kick this to start the core
            "enable": In(1),
            # Internal point stream, upsampled from self.i (TODO no need to expose this)
            "point_stream": In(stream.Signature(data.ArrayLayout(ASQ, 4)))
        })


    def elaborate(self, platform) -> Module:
        m = Module()

        bus = self.bus

        fb_len_words = (self.fb.timings.active_pixels * self.fb.bytes_per_pixel) // 4
        fb_hwords = ((self.fb.timings.h_active*self.fb.bytes_per_pixel)//4)

        # Define pixel structure: 4-bit color + 4-bit intensity
        pixel_layout = data.StructLayout({
            "color": unsigned(4),
            "intensity": unsigned(4),
        })
        pixels_per_word = self.bus.data_width // pixel_layout.as_shape().width
        pixel_array_layout = data.ArrayLayout(pixel_layout, pixels_per_word)

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

        # Structured pixel data
        pixels_read = Signal(pixel_array_layout)
        pixels_write = Signal(pixel_array_layout)

        # pixel position
        x_offs = Signal(unsigned(16))
        y_offs = Signal(unsigned(16))
        pixel_index = Signal(unsigned(2))  # Which of the 4 pixels in the word
        pixel_offs = Signal(unsigned(32))

        # last sample
        sample_x = Signal(signed(16))
        sample_y = Signal(signed(16))
        sample_p = Signal(signed(16)) # intensity modulation TODO
        sample_c = Signal(signed(16)) # color modulation DONE

        m.d.comb += pixel_offs.eq(y_offs*fb_hwords + x_offs),
        with m.If(self.rotate_left):
            # remap pixel offset for 90deg rotation
            m.d.comb += [
                pixel_index.eq((-sample_y)[0:2]),
                x_offs.eq((fb_hwords//2) + ((-sample_y)>>2)),
                y_offs.eq(sample_x + (self.fb.timings.v_active>>1)),
            ]
        with m.Else():
            m.d.comb += [
                pixel_index.eq(sample_x[0:2]),
                x_offs.eq((fb_hwords//2) + (sample_x>>2)),
                y_offs.eq(sample_y + (self.fb.timings.v_active>>1)),
            ]

        # Overall x / y scale depends on ASQ fractional bits as we often take raw counts.
        # This ensures this component still works as expected with 10/16/24-bit samples.
        def normalize_scale_down(sq: fixed.Value, scale: Signal(unsigned(4))):
            asq_extra_bits = ASQ.f_bits - 15
            if asq_extra_bits >= 0:
                return (sq.as_value() >> scale) >> asq_extra_bits
            else:
                return (sq.as_value() << -asq_extra_bits) >> scale

        with m.FSM() as fsm:

            with m.State('OFF'):
                with m.If(self.enable):
                    m.next = 'LATCH0'

            with m.State('LATCH0'):

                m.d.comb += self.point_stream.ready.eq(1)
                # Fired on every audio sample fs_strobe
                with m.If(self.point_stream.valid):
                    m.d.sync += [
                        sample_x.eq(normalize_scale_down(self.point_stream.payload[0], self.scale_x) + self.x_offset),
                        # invert sample_y for positive scope -> up
                        sample_y.eq(normalize_scale_down(-self.point_stream.payload[1], self.scale_y) + self.y_offset),
                        sample_p.eq(Mux(self.scale_p != 0xf, normalize_scale_down(self.point_stream.payload[2], self.scale_p), 0)),
                        sample_c.eq(Mux(self.scale_c != 0xf, normalize_scale_down(self.point_stream.payload[3], self.scale_c), 0)),
                    ]
                    m.next = 'LATCH1'

            with m.State('LATCH1'):

                with m.If((x_offs < fb_hwords) & (y_offs < self.fb.timings.v_active)):
                    m.d.sync += [
                        bus.sel.eq(0xf),
                        bus.adr.eq(self.fb.fb_base + pixel_offs),
                    ]
                    m.next = 'READ'
                with m.Else():
                    # don't draw outside the screen boundaries
                    m.next = 'LATCH0'

            with m.State('READ'):

                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(0),
                ]

                with m.If(bus.stb & bus.ack):
                    m.d.sync += pixels_read.as_value().eq(bus.dat_r)
                    m.next = 'WAIT'

            with m.State('WAIT'):
                m.next = 'WAIT2'

            with m.State('WAIT2'):
                m.next = 'WAIT3'

            with m.State('WAIT3'):
                m.next = 'WRITE'

            with m.State('WRITE'):

                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(1),
                ]

                # Calculate new pixel values
                new_color = Signal(unsigned(4))
                sample_intensity = Signal(unsigned(4))
                current_intensity = Signal(unsigned(4))
                new_intensity = Signal(unsigned(4))

                # Extract current pixel data
                m.d.comb += current_intensity.eq(pixels_read[pixel_index].intensity)

                # Calculate new color (sample color + base hue)
                m.d.comb += new_color.eq(sample_c + self.hue)

                # Calculate sample intensity with bounds checking
                with m.If((sample_p + self.intensity > 0) & (sample_p + self.intensity <= 0xf)):
                    m.d.sync += sample_intensity.eq(sample_p + self.intensity)
                with m.Else():
                    m.d.sync += sample_intensity.eq(0)

                # Calculate new intensity (add with saturation)
                with m.If(current_intensity + sample_intensity >= 0xF):
                    m.d.comb += new_intensity.eq(0xF)
                with m.Else():
                    m.d.comb += new_intensity.eq(current_intensity + sample_intensity)

                # Copy new pixel from read data to write data
                for i in range(pixels_per_word):
                    with m.If(pixel_index == i):
                        m.d.comb += [
                            pixels_write[i].color.eq(new_color),
                            pixels_write[i].intensity.eq(new_intensity),
                        ]
                    # Preserve other pixels unchanged
                    with m.Else():
                        m.d.comb += [
                            pixels_write[i].color.eq(pixels_read[i].color),
                            pixels_write[i].intensity.eq(pixels_read[i].intensity),
                        ]

                # Write pixel data back to bus
                m.d.comb += bus.dat_w.eq(pixels_write.as_value())

                with m.If(bus.stb & bus.ack):
                    m.next = 'LATCH0'

        return ResetInserter({'sync': ~self.fb.enable})(m)
