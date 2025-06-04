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


    def __init__(self, *, fb: DMAFramebuffer, fs=192000, n_upsample=4,
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

        self.px_read = Signal(32)
        self.px_sum = Signal(16)

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

        m.submodules.plot_fifo = plot_fifo = SyncFIFOBuffered(
            width=data.ArrayLayout(ASQ, 4).as_shape().width, depth=64)
        wiring.connect(m, wiring.flipped(self.i), plot_fifo.w_stream)

        if self.n_upsample is not None and self.n_upsample != 1:
            # If interpolation is enabled, insert an FIR upsampling stage.
            m.submodules.split = split = dsp.Split(n_channels=4)
            m.submodules.merge = merge = dsp.Merge(n_channels=4)

            m.submodules.resample0 = resample0 = dsp.Resample(fs_in=self.fs, n_up=self.n_upsample, m_down=1)
            m.submodules.resample1 = resample1 = dsp.Resample(fs_in=self.fs, n_up=self.n_upsample, m_down=1)
            m.submodules.resample2 = resample2 = dsp.Resample(fs_in=self.fs, n_up=self.n_upsample, m_down=1)
            m.submodules.resample3 = resample3 = dsp.Resample(fs_in=self.fs, n_up=self.n_upsample, m_down=1)

            wiring.connect(m, plot_fifo.r_stream, split.i)

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
            # Don't block progress of gateware feeding this core if memory is blocking read/writes.
            # TODO this is a hack for stable scope triggering.
            m.d.comb += self.i.ready.eq(1)
            # No upsampling. Just buffering to tolerate cache misses.
            wiring.connect(m, plot_fifo.r_stream, self.point_stream)

        px_read = self.px_read
        px_sum = self.px_sum

        # pixel position
        x_offs = Signal(unsigned(16))
        y_offs = Signal(unsigned(16))
        subpix_shift = Signal(unsigned(6))
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
                subpix_shift.eq((-sample_y)[0:2]*8),
                x_offs.eq((fb_hwords//2) + ((-sample_y)>>2)),
                y_offs.eq(sample_x + (self.fb.timings.v_active>>1)),
            ]
        with m.Else():
            m.d.comb += [
                subpix_shift.eq(sample_x[0:2]*8),
                x_offs.eq((fb_hwords//2) + (sample_x>>2)),
                y_offs.eq(sample_y + (self.fb.timings.v_active>>1)),
            ]

        with m.FSM() as fsm:

            with m.State('OFF'):
                with m.If(self.enable):
                    m.next = 'LATCH0'

            with m.State('LATCH0'):

                m.d.comb += self.point_stream.ready.eq(1)
                # Fired on every audio sample fs_strobe
                with m.If(self.point_stream.valid):
                    m.d.sync += [
                        sample_x.eq((self.point_stream.payload[0].as_value()>>self.scale_x) + self.x_offset),
                        # invert sample_y for positive scope -> up
                        sample_y.eq((-self.point_stream.payload[1].as_value()>>self.scale_y) + self.y_offset),
                        sample_p.eq(Mux(self.scale_p != 0xf, self.point_stream.payload[2].as_value()>>self.scale_p, 0)),
                        sample_c.eq(Mux(self.scale_c != 0xf, self.point_stream.payload[3].as_value()>>self.scale_c, 0)),
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
                    m.d.sync += px_read.eq(bus.dat_r)
                    m.d.sync += px_sum.eq(((bus.dat_r >> subpix_shift) & 0xff))
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

                # The actual drawing logic
                # Basically we just increment the intensity and clamp it to a maximum
                # for the correct bits of the native bus word for this pixel.
                #
                # TODO: color is always overridden, perhaps we should mix it?

                new_color = Signal(unsigned(4))
                sample_intensity = Signal(unsigned(4))
                white = Signal(unsigned(4))
                m.d.comb += white.eq(0xf)
                m.d.comb += new_color.eq(sample_c + self.hue)

                with m.If((sample_p + self.intensity > 0) & (sample_p + self.intensity <= 0xf)):
                    m.d.comb += sample_intensity.eq(sample_p + self.intensity)
                with m.Else():
                    m.d.comb += sample_intensity.eq(0)

                with m.If(px_sum[4:8] + sample_intensity >= 0xF):
                    m.d.comb += bus.dat_w.eq(
                        (px_read & ~(Const(0xFF, unsigned(32)) << subpix_shift)) |
                        (Cat(new_color, white) << (subpix_shift))
                         )
                with m.Else():
                    m.d.comb += bus.dat_w.eq(
                        (px_read & ~(Const(0xFF, unsigned(32)) << subpix_shift)) |
                        (Cat(new_color, (px_sum[4:8] + sample_intensity)) << subpix_shift)
                         )

                with m.If(bus.stb & bus.ack):
                    m.next = 'LATCH0'

        return ResetInserter({'sync': ~self.fb.enable})(m)
