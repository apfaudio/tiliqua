# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Utilities for plotting pixels to a framebuffer.

Generally, all plotting operations to the framebuffer should go through
the ``FramebufferPlotter`` core in this file. This can be via direct
pixel writes from the SoC (using e.g. ``Peripheral`` here), through
hardware-accelerated SoC interfaces like those in ``line.py`` or ``blit.py``,
or indirectly through gateware-driven plotting requests like ``stroke.py``.

In general, a ``raster`` system may look like this:

.. code-block:: text

    SoC requests ────► [plot.Peripheral()] ─╮
              ╰──────► [line.Peripheral()] ─┼───► FramebufferPlotter ─► PSRAM
             ╰───────► [blit.Peripheral()] ─┤
                                            │
    RTL requests ────►   [stroke.Stroke()] ─╯

All pixel ``PlotRequest``s are streams, arbitered in a round-robin fashion by the
``FramebufferPlotter`` into a single (internal) ``PlotRequest``, which is fed into
the ``_FramebufferBackend`` to perform blending (and handle screen rotation). The
resulting memory accesses go through a  cache ``raster.cache.Cache``, before eventually
issuing requests on the PSRAM bus.

If higher pixel throughput is needed, one can instantiate multiple hardware accelerators
and ``FramebufferPlotters`` on the same (shared) PSRAM bus, at least as many as you
want until you run out of memory bandwidth or FPGA resources :). For the best performance,
it makes sense to share ``FramebufferPlotter``s between components that want to draw to
the same part of the screen, to avoid cache thrashing.
"""

from amaranth import *
from amaranth.build import *
from amaranth.lib import data, enum, fifo, stream, wiring
from amaranth.lib.wiring import In, Out
from amaranth_soc import csr, wishbone

from ..video.framebuffer import DMAFramebuffer
from ..video.types import Pixel, Rotation
from ..dsp import stream_util
from ..cache import WishboneL2Cache


class BlendMode(enum.Enum, shape=unsigned(1)):
    """
    Pixel blending mode for a `PlotRequest`.

    Note that ``REPLACE`` is faster than ``ADDITIVE``, as the latter requires
    a read-modify-write operation for blending.
    """
    REPLACE  = 0  # Direct pixel replacement (e.g. text)
    ADDITIVE = 1  # Additive blending with saturation (e.g. scope traces)

class OffsetMode(enum.Enum, shape=unsigned(1)):
    """
    Pixel coordinate offset mode for a `PlotRequest`.
    """
    ABSOLUTE = 0  # Absolute coordinates (e.g. text / boxes / lines)
    CENTER   = 1  # Relative to center coordinates (e.g. vectorscope traces)

class PlotRequest(data.Struct):
    """
    Command to plot a single pixel with provided intensity/color/blend-mode/offset
    """
    x:         signed(12) # X coordinate (signed, -2048 to +2047)
    y:         signed(12) # Y coordinate (signed, -2048 to +2047)
    pixel:     Pixel      # Pixel color and intensity
    blend:     BlendMode  # Blending mode (replace/additive)
    offset:    OffsetMode # Coordinate system (absolute/center-relative)


class Peripheral(wiring.Component):
    """
    Plot single pixels with CSR command interface.

    Usage from an SoC:
    - Wait for ``status.busy`` CSR field to be deasserted.
    - Write a pixel to the ``plot`` CSR (warn: set all fields in one store!)
    - The plot request is enqueued to the internal FIFO and will be executed as
      soon as possible.
    - Enqueue as many pixels as you want until ``status.busy`` is asserted (``fifo_depth``).

    This core always plots using OffsetMode.ABSOLUTE and BlendMode.REPLACE, which
    is generally what an SoC wants to do when drawing text/menus.
    """

    class StatusReg(csr.Register, access="r"):
        fifo_level: csr.Field(csr.action.R, unsigned(16))
        busy:       csr.Field(csr.action.R, unsigned(1))

    class PlotReg(csr.Register, access="w"):
        # Note: Writing to this register enqueues the plot operation!
        x: csr.Field(csr.action.W, signed(12))
        y: csr.Field(csr.action.W, signed(12))
        pixel: csr.Field(csr.action.W, Pixel)

    def __init__(self, fifo_depth=8):
        self.fifo_depth = fifo_depth

        # Command FIFO for enqueued pixel writes
        self._cmd_fifo = stream_util.SyncFIFOBuffered(shape=PlotRequest, depth=fifo_depth)

        regs = csr.Builder(addr_width=6, data_width=8)
        self._status = regs.add("status", self.StatusReg(), offset=0x00)
        self._plot = regs.add("plot", self.PlotReg(), offset=0x04)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "o": Out(stream.Signature(PlotRequest)),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge
        m.submodules._cmd_fifo = cmd_fifo = self._cmd_fifo
        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        # Build PlotRequest from CSR fields, commit on register write.
        m.d.comb += [
            cmd_fifo.i.payload.x.eq(self._plot.f.x.w_data),
            cmd_fifo.i.payload.y.eq(self._plot.f.y.w_data),
            cmd_fifo.i.payload.pixel.eq(self._plot.f.pixel.w_data),
            cmd_fifo.i.payload.blend.eq(BlendMode.REPLACE),
            cmd_fifo.i.payload.offset.eq(OffsetMode.ABSOLUTE),
        ]
        with m.If(self._plot.element.w_stb & cmd_fifo.i.ready):
            m.d.comb += cmd_fifo.i.valid.eq(1)

        # Status register fields
        m.d.comb += [
            self._status.f.fifo_level.r_data.eq(cmd_fifo.fifo.level),
            self._status.f.busy.r_data.eq(~cmd_fifo.i.ready), # Busy when FIFO full
        ]

        # Send plot requests to shared plotting backend on `o`
        wiring.connect(m, cmd_fifo.o, wiring.flipped(self.o))

        return m


class _FramebufferBackend(wiring.Component):

    """
    This is the core plotting engine that translates a ``PlotRequest`` stream into
    transformed coordinates, performs blending, eventually emitting the required
    read-modify-write cycles for each pixel memory address.

    Use ``FramebufferPlotter`` for the public API which includes caching and arbitration.
    Using this core directly will have terrible performance (as it does not collect
    contiguous pixels into bursts, the cache is needed for this).

    Note that ``BlendMode.REPLACE`` performs a (fast) WRITE operation, however
    ``BlendMode.ADDITIVE`` performs a READ-BLEND-WRITE operation, which is slower.
    """

    def __init__(self, bus_signature):
        self.pixel_bits = Pixel.as_shape().size
        self.pixel_bytes = self.pixel_bits // 8
        self.pixels_per_word = bus_signature.data_width // self.pixel_bits
        super().__init__({
            # Incoming plot request stream
            "i": In(stream.Signature(PlotRequest)),
            # DMA bus for framebuffer access
            "bus": Out(bus_signature),
            # Dynamic attributes of framebuffer needed for plotting.
            "fbp": In(DMAFramebuffer.Properties()),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        bus = self.bus

        # Current request being processed
        current_req = Signal(PlotRequest)

        # Pixel position calculations
        abs_x = Signal(signed(16))
        abs_y = Signal(signed(16))

        # Maybe convert absolute coordinates to center-relative, which depends
        # on the current rotation settings.
        with m.If(current_req.offset == OffsetMode.CENTER):
            with m.Switch(self.fbp.rotation):
                # Landscape centering
                with m.Case(Rotation.NORMAL, Rotation.INVERTED):
                    m.d.comb += [
                        abs_x.eq(current_req.x + (self.fbp.timings.h_active >> 1)),
                        abs_y.eq(current_req.y + (self.fbp.timings.v_active >> 1)),
                    ]
                # Portrait centering
                with m.Case(Rotation.LEFT, Rotation.RIGHT):
                    m.d.comb += [
                        abs_x.eq(current_req.x + (self.fbp.timings.v_active >> 1)),
                        abs_y.eq(current_req.y + (self.fbp.timings.h_active >> 1)),
                    ]
        with m.Else():
            m.d.comb += [
                abs_x.eq(current_req.x),
                abs_y.eq(current_req.y),
            ]

        # Handle rotation and pixel addressing
        final_x = Signal(signed(16))
        final_y = Signal(signed(16))
        with m.Switch(self.fbp.rotation):
            with m.Case(Rotation.NORMAL):
                m.d.comb += [
                    final_x.eq(abs_x),
                    final_y.eq(abs_y),
                ]
            with m.Case(Rotation.LEFT):
                m.d.comb += [
                    final_x.eq(self.fbp.timings.h_active - 1 - abs_y),
                    final_y.eq(abs_x),
                ]
            with m.Case(Rotation.INVERTED):
                m.d.comb += [
                    final_x.eq(self.fbp.timings.h_active - 1 - abs_x),
                    final_y.eq(self.fbp.timings.v_active - 1 - abs_y),
                ]
            with m.Case(Rotation.RIGHT):
                m.d.comb += [
                    final_x.eq(abs_y),
                    final_y.eq(self.fbp.timings.v_active - 1 - abs_x),
                ]


        # Finally, compute pixel address in framebuffer.
        # NOTE: single multiplier used here!
        x_offs = Signal(unsigned(16))
        y_offs = Signal(unsigned(16))
        pixel_index = Signal(range(self.pixels_per_word))  # Which of the 4 pixels in the word
        pixel_addr = Signal(unsigned(32))

        m.d.comb += [
            pixel_index.eq(final_x[0:2]),
            x_offs.eq(final_x >> 2),
            y_offs.eq(final_y),
        ]
        fb_hwords = ((self.fbp.timings.h_active * self.pixel_bytes)
                     // self.pixels_per_word)
        m.d.comb += pixel_addr.eq(
                self.fbp.base + y_offs*fb_hwords + x_offs)

        # Pixel data latched during read-modify-write / blending
        pixel_read = Signal(Pixel)
        pixel_write = Signal(Pixel)

        with m.FSM() as fsm:

            with m.State('IDLE'):
                # Note: if a ResetInserter is holding us in reset, we drain
                # all incoming points and don't draw them anywhere.
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                    m.d.sync += current_req.eq(self.i.payload)
                    m.next = 'CHECK-BOUNDS'

            with m.State('CHECK-BOUNDS'):
                m.d.sync += [
                    bus.adr.eq(pixel_addr),
                    bus.sel.eq(1 << pixel_index)
                ]
                with m.If((x_offs < fb_hwords) &
                          (y_offs < self.fbp.timings.v_active)):
                    with m.Switch(current_req.blend):
                        with m.Case(BlendMode.ADDITIVE):
                            m.next = 'BLEND-READ'
                        with m.Case(BlendMode.REPLACE):
                            # Fastpath for REPLACE mode (no RMW needed)
                            m.d.sync += pixel_write.eq(current_req.pixel)
                            m.next = 'WRITE'
                with m.Else():
                    m.next = 'IDLE'

            with m.State('BLEND-READ'):
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(0),
                ]
                with m.If(bus.stb & bus.ack):
                    m.d.sync += pixel_read.eq(
                        bus.dat_r.bit_select(pixel_index*self.pixel_bits, self.pixel_bits))
                    m.next = 'BLEND-PROCESS'

            with m.State('BLEND-PROCESS'):
                new_intensity = Signal.like(pixel_read.intensity)
                with m.If(pixel_read.intensity + current_req.pixel.intensity >= Pixel.intensity_max()):
                    m.d.comb += new_intensity.eq(Pixel.intensity_max())
                with m.Else():
                    m.d.comb += new_intensity.eq(pixel_read.intensity + current_req.pixel.intensity)
                m.d.sync += [
                    pixel_write.color.eq(current_req.pixel.color),
                    pixel_write.intensity.eq(new_intensity),
                ]
                m.next = 'WRITE'

            with m.State('WRITE'):
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(1),
                    bus.dat_w.eq(Cat([pixel_write]*self.pixels_per_word)),
                ]
                with m.If(bus.stb & bus.ack):
                    m.next = 'IDLE'

        return ResetInserter({'sync': ~self.fbp.enable})(m)


class FramebufferPlotter(wiring.Component):
    """
    Combined cache, arbiter, and plotting logic.
    Takes (one or many) streams of pixels to plot, and DMAs them to a framebuffer.
    """
    def __init__(self, bus_signature, n_ports: int = 1, cachesize_words: int = 64):
        self.n_ports = n_ports
        self.cachesize_words = cachesize_words
        super().__init__({
            # One (or many) incoming plot request streams
            "i": In(stream.Signature(PlotRequest)).array(n_ports),
            # Framebuffer DMA bus
            "bus": Out(bus_signature),
            # Dynamic attributes of framebuffer needed for plotting.
            "fbp": In(DMAFramebuffer.Properties()),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # Internal components
        m.submodules.cache = cache = WishboneL2Cache(
            addr_width=self.bus.addr_width,
            cachesize_words=self.cachesize_words,
            autoflush=True)
        m.submodules.backend = backend = _FramebufferBackend(
            bus_signature=cache.master.signature.flip())
        m.submodules.arbiter = arbiter = stream_util.Arbiter(
            n_channels=self.n_ports, shape=PlotRequest)

        # Framebuffer properties
        wiring.connect(m, wiring.flipped(self.fbp), backend.fbp)

        # Plot requests -> arbiter
        for n in range(self.n_ports):
            wiring.connect(m, wiring.flipped(self.i[n]), arbiter.i[n])
        # Arbiter -> plotting backend
        wiring.connect(m, arbiter.o, backend.i)
        # Backend -> cache
        wiring.connect(m, backend.bus, cache.master)
        # Cache -> exposed for connecting to PSRAM DMA
        wiring.connect(m, cache.slave, wiring.flipped(self.bus))

        return m


