# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Accelerated line strip plotting peripheral.
Plots line segments to a framebuffer using Bresenham's algorithm.
"""

from amaranth import *
from amaranth.build import *
from amaranth.lib import data, enum, fifo, stream, wiring
from amaranth.lib.wiring import In, Out
from amaranth_soc import csr

from ..video.types import Pixel
from .plot import BlendMode, OffsetMode, PlotRequest


class LineStripCmd(enum.Enum, shape=unsigned(1)):
    CONTINUE = 0  # Continue current line strip
    END      = 1  # End current line strip


class LineCmd(data.Struct):
    """
    Single entry in line plotter command FIFO.
    """
    x: signed(12)
    y: signed(11)
    pixel: Pixel
    # Whether this is completing or continuing an existing line strip.
    cmd:   LineStripCmd


class _LinePlotter(wiring.Component):

    """
    Line plotting engine. Use ``Peripheral`` for the public CSR API.

    This core turns an incoming stream of ``LineCmd``s into an outgoing
    stream of (many more) ``PlotRequest``s, using Bresenham's algorithm.
    """

    def __init__(self):
        super().__init__({
            "cmd": In(stream.Signature(LineCmd)),
            "plot_req": Out(stream.Signature(PlotRequest)),
            "enable": In(1),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        cmd = self.cmd

        # Previous line segment
        prev_x = Signal(signed(12))
        prev_y = Signal(signed(11))
        has_prev_point = Signal()

        # Current line segmenet
        current_x = Signal(signed(12))
        current_y = Signal(signed(11))
        target_x = Signal(signed(12))
        target_y = Signal(signed(11))
        current_pixel = Signal(Pixel)
        end_strip = Signal()

        # Bresenham algorithm
        dx = Signal(signed(13))
        dy = Signal(signed(13))
        sx = Signal(signed(2))
        sy = Signal(signed(2))
        err = Signal(signed(14))
        e2 = Signal(signed(14))

        with m.FSM() as fsm:

            with m.State('IDLE'):
                m.d.comb += cmd.ready.eq(self.enable)
                with m.If(cmd.ready & cmd.valid):
                    with m.If(has_prev_point):
                        # Draw line from previous to new point
                        m.d.sync += [
                            current_x.eq(prev_x),
                            current_y.eq(prev_y),
                            target_x.eq(cmd.payload.x),
                            target_y.eq(cmd.payload.y),
                            end_strip.eq(cmd.payload.cmd == LineStripCmd.END),
                        ]
                        m.next = 'SETUP_BRESENHAM'
                    with m.Else():
                        # First point in strip - store it and plot single point
                        m.d.sync += [
                            prev_x.eq(cmd.payload.x),
                            prev_y.eq(cmd.payload.y),
                            current_pixel.eq(cmd.payload.pixel),
                            end_strip.eq(cmd.payload.cmd == LineStripCmd.END),
                            has_prev_point.eq(cmd.payload.cmd == LineStripCmd.CONTINUE),
                        ]
                        m.next = 'PLOT_SINGLE_POINT'

            with m.State('PLOT_SINGLE_POINT'):
                # First point in strip, or isolated point in zero-length line
                m.d.comb += [
                    self.plot_req.valid.eq(1),
                    self.plot_req.payload.x.eq(prev_x),
                    self.plot_req.payload.y.eq(prev_y),
                    self.plot_req.payload.pixel.eq(current_pixel),
                    self.plot_req.payload.blend.eq(BlendMode.REPLACE),
                    self.plot_req.payload.offset.eq(OffsetMode.ABSOLUTE),
                ]
                with m.If(self.plot_req.ready):
                    with m.If(end_strip):
                        m.d.sync += has_prev_point.eq(0)
                    m.next = 'IDLE'

            with m.State('SETUP_BRESENHAM'):

                with m.If(target_x >= current_x):
                    m.d.sync += [
                        dx.eq(target_x - current_x),
                        sx.eq(1),
                    ]
                with m.Else():
                    m.d.sync += [
                        dx.eq(current_x - target_x),
                        sx.eq(-1),
                    ]

                with m.If(target_y >= current_y):
                    m.d.sync += [
                        dy.eq(target_y - current_y),
                        sy.eq(1),
                    ]
                with m.Else():
                    m.d.sync += [
                        dy.eq(current_y - target_y),
                        sy.eq(-1),
                    ]

                # Skip drawing zero-length lines (same start and end point)
                # First point was guaranteed to already plot at least 1 pixel.
                with m.If((target_x == current_x) & (target_y == current_y)):
                    m.d.sync += [
                        prev_x.eq(target_x),
                        prev_y.eq(target_y),
                        has_prev_point.eq(~end_strip),
                    ]
                    m.next = 'IDLE'
                with m.Else():
                    m.next = 'INIT_BRESENHAM'

            with m.State('INIT_BRESENHAM'):
                m.d.sync += err.eq(dx - dy)
                m.next = 'DRAW_LINE'

            with m.State('DRAW_LINE'):
                m.d.comb += [
                    self.plot_req.valid.eq(1),
                    self.plot_req.payload.x.eq(current_x),
                    self.plot_req.payload.y.eq(current_y),
                    self.plot_req.payload.pixel.eq(current_pixel),
                    self.plot_req.payload.blend.eq(BlendMode.REPLACE),
                    self.plot_req.payload.offset.eq(OffsetMode.ABSOLUTE),
                ]

                with m.If(self.plot_req.ready):
                    # Are we done?
                    with m.If((current_x == target_x) & (current_y == target_y)):
                        # Line complete - update previous point for next line
                        m.d.sync += [
                            prev_x.eq(target_x),
                            prev_y.eq(target_y),
                            current_pixel.eq(cmd.payload.pixel),
                            has_prev_point.eq(~end_strip),
                        ]
                        m.next = 'IDLE'
                    with m.Else():
                        m.next = 'BRESENHAM_STEP'

            # TODO: there's probably enough timing slack to collapse
            # all of these states into one...

            with m.State('BRESENHAM_STEP'):
                m.d.sync += e2.eq(err << 1)
                m.next = 'BRESENHAM_UPDATE_X'

            with m.State('BRESENHAM_UPDATE_X'):
                with m.If(e2 > -dy):
                    m.d.sync += [
                        err.eq(err - dy),
                        current_x.eq(current_x + sx),
                    ]
                m.next = 'BRESENHAM_UPDATE_Y'

            with m.State('BRESENHAM_UPDATE_Y'):
                with m.If(e2 < dx):
                    m.d.sync += [
                        err.eq(err + dx),
                        current_y.eq(current_y + sy),
                    ]
                m.next = 'DRAW_LINE'

        return m


class Peripheral(wiring.Component):
    """
    CSR-driven line strip plotter.

    Usage:
    - SoC checks ``status.full`` CSR is deasserted (space for new ops)
    - SoC writes line strip points to the ``point`` CSR, where every
      field for a single point should always be set in a single store.
    - SoC must use ``point.cmd == END`` on the final segment in each strip.
    - SoC must always check that ``status.full`` is not asserted before
      enqueuing more line strips.
    """

    class StatusReg(csr.Register, access="r"):
        full: csr.Field(csr.action.R, unsigned(1))
        empty: csr.Field(csr.action.R, unsigned(1))

    class PointReg(csr.Register, access="w"):
        # Note: Writing to this register enqueues the point
        # be careful the CPU issues a single store for each point.
        x: csr.Field(csr.action.W, signed(12))
        y: csr.Field(csr.action.W, signed(11))
        pixel: csr.Field(csr.action.W, Pixel)
        cmd: csr.Field(csr.action.W, LineStripCmd)

    def __init__(self, fifo_depth=16):
        self.fifo_depth = fifo_depth

        # FIFO of line strip commands in flight.
        self._cmd_fifo = fifo.SyncFIFOBuffered(width=LineCmd.as_shape().size, depth=fifo_depth)

        regs = csr.Builder(addr_width=6, data_width=8)
        self._status = regs.add("status", self.StatusReg(), offset=0x00)
        self._point = regs.add("point", self.PointReg(), offset=0x04)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "plot_req": Out(stream.Signature(PlotRequest)),
            "enable": In(1),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge
        m.submodules._cmd_fifo = self._cmd_fifo
        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        m.submodules.line_plotter = line_plotter = _LinePlotter()

        # Connect enable signal
        m.d.comb += line_plotter.enable.eq(self.enable)

        # Build LineCmd from CSR fields
        line_cmd = Signal(LineCmd)
        m.d.comb += [
            line_cmd.x.eq(self._point.f.x.w_data),
            line_cmd.y.eq(self._point.f.y.w_data),
            line_cmd.pixel.eq(self._point.f.pixel.w_data),
            line_cmd.cmd.eq(self._point.f.cmd.w_data),
        ]

        cmd_fifo_w = self._cmd_fifo.w_stream
        with m.If(self._point.element.w_stb & cmd_fifo_w.ready):
            m.d.comb += [
                cmd_fifo_w.valid.eq(1),
                cmd_fifo_w.payload.eq(line_cmd),
            ]

        m.d.comb += [
            self._status.f.full.r_data.eq(~cmd_fifo_w.ready),
            self._status.f.empty.r_data.eq(~self._cmd_fifo.r_stream.valid),
        ]

        wiring.connect(m, self._cmd_fifo.r_stream, line_plotter.cmd)

        wiring.connect(m, line_plotter.plot_req, wiring.flipped(self.plot_req))

        return m
