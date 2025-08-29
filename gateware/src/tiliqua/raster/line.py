# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Hardware-accelerated line strip plotter with CSR command interface.

Builds connected line segments by enqueueing points sequentially using
Bresenham's line algorithm for pixel-perfect rendering.
"""

from amaranth              import *
from amaranth.build        import *
from amaranth.lib          import wiring, data, stream, fifo, enum
from amaranth.lib.wiring   import In, Out
from amaranth.utils        import exact_log2

from amaranth_soc          import wishbone, csr
from amaranth_soc.memory   import MemoryMap

from tiliqua.types         import Pixel

from tiliqua.raster.plot import PlotRequest, BlendMode, OffsetMode


class LineStripCommand(enum.Enum, shape=unsigned(1)):
    CONTINUE = 0  # Continue current line strip
    END      = 1  # End current line strip


class LineCommand(data.Struct):
    """Command structure for line point queue."""
    x:     signed(12)        # X coordinate
    y:     signed(11)        # Y coordinate  
    pixel: Pixel             # Color and intensity
    cmd:   LineStripCommand  # Line strip command


class Peripheral(wiring.Component):
    """
    Hardware-accelerated line strip plotter with CSR command interface.
    
    Builds connected line segments by enqueueing points sequentially.
    Each point connects to the previous point in the strip using
    Bresenham's line algorithm.
    
    Command Interface:
    POINT: [x:12|y:12|pixel:8|end_strip:1] - Add point to current line strip
    
    Features:
    - Sequential point enqueueing for continuous line strips
    - Bresenham line algorithm for pixel-perfect lines
    - Command FIFO for asynchronous line operations
    - Direct pixel replacement (REPLACE blend mode)
    - Absolute coordinate positioning
    - Automatic line strip management
    """

    class StatusReg(csr.Register, access="r"):
        full: csr.Field(csr.action.R, unsigned(1))    # FIFO full (can't accept new commands)
        empty: csr.Field(csr.action.R, unsigned(1))   # FIFO empty (no pending operations)

    class PointReg(csr.Register, access="w"):
        x: csr.Field(csr.action.W, signed(12))         # Point X coordinate
        y: csr.Field(csr.action.W, signed(11))         # Point Y coordinate
        pixel: csr.Field(csr.action.W, Pixel)          # Pixel color/intensity
        cmd: csr.Field(csr.action.W, LineStripCommand)  # Line strip command
        # Note: Writing to this register enqueues the point

    def __init__(self, fifo_depth=16):
        """
        Initialize line plotter with configurable command FIFO depth.
        
        Args:
            fifo_depth: Depth of command FIFO for queuing line operations
        """
        self.fifo_depth = fifo_depth
        
        # Command FIFO to queue line points
        # Each command contains: [x:12|y:11|pixel:8|cmd:1]
        # Total: 32 bits per command
        self._cmd_fifo = fifo.SyncFIFOBuffered(width=LineCommand.as_shape().size, depth=fifo_depth)
        
        # CSR registers
        regs = csr.Builder(addr_width=6, data_width=8)
        self._status = regs.add("status", self.StatusReg(), offset=0x00)
        self._point = regs.add("point", self.PointReg(), offset=0x04)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            # CSR interface for commands and status
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            # Output to shared plot backend
            "plot_req": Out(stream.Signature(PlotRequest)),
            "enable": In(1),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge
        m.submodules._cmd_fifo = self._cmd_fifo
        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        # Enqueue command when point register is written
        cmd_fifo_w = self._cmd_fifo.w_stream
        
        # Build LineCommand from CSR fields
        line_cmd = Signal(LineCommand)
        m.d.comb += [
            line_cmd.x.eq(self._point.f.x.w_data),
            line_cmd.y.eq(self._point.f.y.w_data),
            line_cmd.pixel.eq(self._point.f.pixel.w_data),
            line_cmd.cmd.eq(self._point.f.cmd.w_data),
        ]
        
        with m.If(self._point.element.w_stb & cmd_fifo_w.ready):
            m.d.comb += [
                cmd_fifo_w.valid.eq(1),
                cmd_fifo_w.payload.eq(line_cmd),
            ]

        # Status register
        m.d.comb += [
            # full = FIFO is full (can't accept new commands)
            self._status.f.full.r_data.eq(~cmd_fifo_w.ready),
            # empty = FIFO is empty (no pending operations)
            self._status.f.empty.r_data.eq(~self._cmd_fifo.r_stream.valid),
        ]

        # Line drawing state
        prev_x = Signal(signed(12))
        prev_y = Signal(signed(11))
        has_prev_point = Signal()  # Track if we have a previous point for line drawing

        # Current line being drawn (Bresenham algorithm state)
        current_x = Signal(signed(12))
        current_y = Signal(signed(11))
        target_x = Signal(signed(12))
        target_y = Signal(signed(11))
        current_pixel = Signal(Pixel)
        end_strip = Signal()

        # Bresenham algorithm variables
        dx = Signal(signed(13))  # One extra bit for abs(target_x - current_x)
        dy = Signal(signed(13))  # One extra bit for abs(target_y - current_y)
        sx = Signal(signed(2))   # Step direction for X (-1 or +1)
        sy = Signal(signed(2))   # Step direction for Y (-1 or +1)
        err = Signal(signed(14)) # Error term (needs extra bits for dx + dy)
        e2 = Signal(signed(14))  # 2 * err

        # Command FIFO read stream
        cmd_fifo_r = self._cmd_fifo.r_stream

        with m.FSM() as fsm:
            
            with m.State('IDLE'):
                # Wait for command from FIFO
                with m.If(self.enable & cmd_fifo_r.valid):
                    # Unpack command from FIFO using struct
                    new_cmd = Signal(LineCommand)
                    m.d.comb += new_cmd.eq(cmd_fifo_r.payload)
                    
                    with m.If(has_prev_point):
                        # We have a previous point - draw line from prev to new point
                        m.d.sync += [
                            current_x.eq(prev_x),
                            current_y.eq(prev_y),
                            target_x.eq(new_cmd.x),
                            target_y.eq(new_cmd.y),
                            current_pixel.eq(new_cmd.pixel),
                            end_strip.eq(new_cmd.cmd == LineStripCommand.END),
                        ]
                        m.d.comb += cmd_fifo_r.ready.eq(1)
                        m.next = 'SETUP_BRESENHAM'
                    with m.Else():
                        # First point in strip - just store it and plot the point
                        m.d.sync += [
                            prev_x.eq(new_cmd.x),
                            prev_y.eq(new_cmd.y),
                            current_pixel.eq(new_cmd.pixel),
                            end_strip.eq(new_cmd.cmd == LineStripCommand.END),
                            has_prev_point.eq(new_cmd.cmd == LineStripCommand.CONTINUE),  # Set if continuing strip
                        ]
                        m.d.comb += cmd_fifo_r.ready.eq(1)
                        m.next = 'PLOT_SINGLE_POINT'
            
            with m.State('PLOT_SINGLE_POINT'):
                # Plot the single point (first point in strip or isolated point)
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
                # Setup Bresenham algorithm parameters
                # Calculate absolute differences
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
                
                m.next = 'INIT_BRESENHAM'
                
            with m.State('INIT_BRESENHAM'):
                # Initialize error term: err = dx - dy
                m.d.sync += err.eq(dx - dy)
                m.next = 'DRAW_LINE'

            with m.State('DRAW_LINE'):
                # Draw current pixel
                m.d.comb += [
                    self.plot_req.valid.eq(1),
                    self.plot_req.payload.x.eq(current_x),
                    self.plot_req.payload.y.eq(current_y),
                    self.plot_req.payload.pixel.eq(current_pixel),
                    self.plot_req.payload.blend.eq(BlendMode.REPLACE),
                    self.plot_req.payload.offset.eq(OffsetMode.ABSOLUTE),
                ]
                
                with m.If(self.plot_req.ready):
                    # Check if we've reached the target
                    with m.If((current_x == target_x) & (current_y == target_y)):
                        # Line complete - update previous point for next line
                        m.d.sync += [
                            prev_x.eq(target_x),
                            prev_y.eq(target_y),
                            has_prev_point.eq(~end_strip),  # Clear if ending strip
                        ]
                        m.next = 'IDLE'
                    with m.Else():
                        # Continue Bresenham algorithm
                        m.next = 'BRESENHAM_STEP'

            with m.State('BRESENHAM_STEP'):
                # Bresenham step calculation
                m.d.sync += e2.eq(err << 1)  # e2 = 2 * err
                m.next = 'BRESENHAM_UPDATE'

            with m.State('BRESENHAM_UPDATE'):
                # Update coordinates based on error term
                with m.If(e2 > -dy):
                    # err -= dy; x += sx
                    m.d.sync += [
                        err.eq(err - dy),
                        current_x.eq(current_x + sx),
                    ]
                
                with m.If(e2 < dx):
                    # err += dx; y += sy
                    m.d.sync += [
                        err.eq(err + dx),
                        current_y.eq(current_y + sy),
                    ]
                
                m.next = 'DRAW_LINE'

        return m