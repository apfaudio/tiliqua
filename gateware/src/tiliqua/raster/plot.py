# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Hardware-accelerated pixel plotting for framebuffer operations.

This module provides:
- Peripheral: Single-word command FIFO interface for fast pixel operations
- FramebufferBackend: Shared read-modify-write pixel plotting backend
- Arbiter: Round-robin arbitration for multiple clients

Command format: [X:12|Y:12|Pixel:8] (single 32-bit word)
"""

from amaranth              import *
from amaranth.build        import *
from amaranth.lib          import wiring, data, stream, fifo, enum
from amaranth.lib.wiring   import In, Out

from amaranth_soc          import wishbone, csr

from .cache                import Cache

from ..video.framebuffer import DMAFramebuffer
from ..types import Rotation, Pixel

class BlendMode(enum.Enum, shape=unsigned(1)):
    REPLACE  = 0  # Direct pixel replacement
    ADDITIVE = 1  # Additive blending with saturation

class OffsetMode(enum.Enum, shape=unsigned(1)):
    ABSOLUTE = 0  # Absolute coordinates
    CENTER   = 1  # Relative to center coordinates

class PlotRequest(data.Struct):
    """Single pixel plotting request."""
    x:         signed(12)    # X coordinate (signed, -2048 to +2047)
    y:         signed(12)    # Y coordinate (signed, -2048 to +2047)
    pixel:     Pixel         # Color and intensity
    blend:     BlendMode     # Blending mode (replace vs additive)
    offset:    OffsetMode    # Coordinate system (absolute vs center-relative)


class Peripheral(wiring.Component):
    """
    Hardware-accelerated pixel plotter with CSR command interface.

    Command Interface:
    PLOT: [x:12|y:12|pixel:8] - Plot pixel with specified parameters

    Features:
    - CSR-based command interface for single pixel plots
    - Deep command FIFO for pixel operations
    - Uses shared FramebufferBackend for actual plotting
    - Direct pixel replacement (REPLACE blend mode)
    - Absolute coordinate positioning
    """

    class StatusReg(csr.Register, access="r"):
        fifo_level: csr.Field(csr.action.R, unsigned(16))
        busy:       csr.Field(csr.action.R, unsigned(1))

    class PlotReg(csr.Register, access="w"):
        x: csr.Field(csr.action.W, signed(12))
        y: csr.Field(csr.action.W, signed(12))
        pixel: csr.Field(csr.action.W, Pixel)
        # Note: Writing to this register triggers the plot operation

    def __init__(self, fifo_depth=32):
        self.fifo_depth = fifo_depth

        # Command FIFO for queuing plot operations
        # Stores PlotRequest structs directly
        self._cmd_fifo = fifo.SyncFIFOBuffered(width=PlotRequest.as_shape().size, depth=fifo_depth)

        # CSR registers
        regs = csr.Builder(addr_width=6, data_width=8)
        self._status = regs.add("status", self.StatusReg(), offset=0x00)
        self._plot = regs.add("plot", self.PlotReg(), offset=0x04)
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

        # Enqueue command when plot register is written
        cmd_fifo_w = self._cmd_fifo.w_stream

        # Build PlotRequest from CSR fields
        plot_request = Signal(PlotRequest)
        m.d.comb += [
            plot_request.x.eq(self._plot.f.x.w_data),
            plot_request.y.eq(self._plot.f.y.w_data),
            plot_request.pixel.eq(self._plot.f.pixel.w_data),
            plot_request.blend.eq(BlendMode.REPLACE),  # Plot uses direct replacement
            plot_request.offset.eq(OffsetMode.ABSOLUTE),  # Absolute coordinates
        ]

        with m.If(self._plot.element.w_stb & cmd_fifo_w.ready):
            m.d.comb += [
                cmd_fifo_w.valid.eq(1),
                cmd_fifo_w.payload.eq(plot_request),
            ]

        # Status register updates
        m.d.comb += [
            self._status.f.fifo_level.r_data.eq(self._cmd_fifo.level),
            self._status.f.busy.r_data.eq(~cmd_fifo_w.ready),  # Busy when FIFO full
        ]

        # Command FIFO read stream - directly contains PlotRequest
        rstream = self._cmd_fifo.r_stream

        # Generate plot requests for shared backend - no unpacking needed!
        m.d.comb += [
            self.plot_req.valid.eq(self.enable & rstream.valid),
            self.plot_req.payload.eq(rstream.payload),
            rstream.ready.eq(self.plot_req.ready),
        ]

        return m


class _FramebufferBackend(wiring.Component):
    """
    Private framebuffer backend implementation.

    This is the core plotting engine that handles read-modify-write cycles.
    Use FramebufferPlotter for the public API which includes caching and arbitration.
    """

    def __init__(self, fb: DMAFramebuffer):
        self.fb = fb

        # Use standard Pixel structure
        self.pixels_per_word = 32 // Pixel.as_shape().size
        self.word_layout = data.ArrayLayout(Pixel, self.pixels_per_word)

        super().__init__({
            # Pixel request stream
            "req": In(stream.Signature(PlotRequest)),
            # DMA bus for framebuffer access
            "bus": Out(wishbone.Signature(addr_width=fb.bus.addr_width,
                                        data_width=32, granularity=8)),
            # Control signals
            "enable": In(1),
            "rotation": In(Rotation),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        bus = self.bus
        req = self.req

        # Framebuffer parameters
        fb_hwords = ((self.fb.timings.h_active * self.fb.bytes_per_pixel) // 4)

        # Pixel data for read-modify-write
        pixels_read = Signal(self.word_layout)
        pixels_write = Signal(self.word_layout)

        # Current request being processed
        current_req = Signal(PlotRequest)

        # Pixel position calculations
        x_offs = Signal(unsigned(16))
        y_offs = Signal(unsigned(16))
        pixel_index = Signal(unsigned(2))  # Which of the 4 pixels in the word
        pixel_addr = Signal(unsigned(32))

        # Coordinate transformation with center-relative support
        abs_x = Signal(signed(16))
        abs_y = Signal(signed(16))

        # Convert to absolute coordinates if offset is CENTER
        # Center calculation depends on rotation
        with m.If(current_req.offset == OffsetMode.CENTER):
            with m.Switch(self.rotation):
                with m.Case(Rotation.NORMAL):
                    m.d.comb += [
                        abs_x.eq(current_req.x + (self.fb.timings.h_active >> 1)),
                        abs_y.eq(current_req.y + (self.fb.timings.v_active >> 1)),
                    ]
                with m.Case(Rotation.LEFT):
                    # 90° CCW: swap dimensions
                    m.d.comb += [
                        abs_x.eq(current_req.x + (self.fb.timings.v_active >> 1)),
                        abs_y.eq(current_req.y + (self.fb.timings.h_active >> 1)),
                    ]
                with m.Case(Rotation.INVERTED):
                    # 180°: same dimensions
                    m.d.comb += [
                        abs_x.eq(current_req.x + (self.fb.timings.h_active >> 1)),
                        abs_y.eq(current_req.y + (self.fb.timings.v_active >> 1)),
                    ]
                with m.Case(Rotation.RIGHT):
                    # 90° CW: swap dimensions
                    m.d.comb += [
                        abs_x.eq(current_req.x + (self.fb.timings.v_active >> 1)),
                        abs_y.eq(current_req.y + (self.fb.timings.h_active >> 1)),
                    ]
        with m.Else():
            m.d.comb += [
                abs_x.eq(current_req.x),
                abs_y.eq(current_req.y),
            ]

        # Handle rotation and pixel addressing
        final_x = Signal(signed(16))
        final_y = Signal(signed(16))

        with m.Switch(self.rotation):
            with m.Case(Rotation.NORMAL):
                # 0°: no change
                m.d.comb += [
                    final_x.eq(abs_x),
                    final_y.eq(abs_y),
                ]
            with m.Case(Rotation.LEFT):
                # 90° CCW: (x,y) -> (-y, x) -> (h_active-1-y, x)
                m.d.comb += [
                    final_x.eq(self.fb.timings.h_active - 1 - abs_y),
                    final_y.eq(abs_x),
                ]
            with m.Case(Rotation.INVERTED):
                # 180°: (x,y) -> (-x, -y) -> (h_active-1-x, v_active-1-y)
                m.d.comb += [
                    final_x.eq(self.fb.timings.h_active - 1 - abs_x),
                    final_y.eq(self.fb.timings.v_active - 1 - abs_y),
                ]
            with m.Case(Rotation.RIGHT):
                # 90° CW: (x,y) -> (y, -x) -> (y, v_active-1-x)
                m.d.comb += [
                    final_x.eq(abs_y),
                    final_y.eq(self.fb.timings.v_active - 1 - abs_x),
                ]

        m.d.comb += [
            pixel_index.eq(final_x[0:2]),
            x_offs.eq(final_x >> 2),
            y_offs.eq(final_y),
        ]

        m.d.comb += pixel_addr.eq(self.fb.fb_base + y_offs*fb_hwords + x_offs)

        # Pixel plotting FSM
        with m.FSM() as fsm:

            with m.State('IDLE'):
                # Only assert ready when we're actually ready to accept and process a new request
                m.d.comb += req.ready.eq(self.enable)
                with m.If(self.enable & req.valid):
                    m.d.sync += current_req.eq(req.payload)
                    m.next = 'CHECK_BOUNDS'

            with m.State('CHECK_BOUNDS'):
                # Only plot pixels within framebuffer bounds
                with m.If((x_offs < fb_hwords) & (y_offs < self.fb.timings.v_active)):
                    m.d.sync += [
                        bus.adr.eq(pixel_addr),
                    ]
                    # Fast path for REPLACE mode - use byte select to write single pixel
                    with m.If(current_req.blend == BlendMode.REPLACE):
                        # Set byte select to write only the target pixel (8 bits each)
                        m.d.sync += bus.sel.eq(1 << pixel_index)
                        m.next = 'WRITE_DIRECT'
                    with m.Else():
                        # Need read-modify-write for additive blending
                        m.d.sync += bus.sel.eq(0xf)
                        m.next = 'READ'
                with m.Else():
                    # Skip out-of-bounds pixels - go directly to IDLE
                    # req.ready will be asserted by IDLE state
                    m.next = 'IDLE'

            with m.State('READ'):
                # Read current pixel data
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(0),
                ]

                with m.If(bus.stb & bus.ack):
                    m.d.sync += pixels_read.as_value().eq(bus.dat_r)
                    m.next = 'PROCESS'

            with m.State('PROCESS'):
                # Update the target pixel, preserve others
                for i in range(self.pixels_per_word):
                    with m.If(pixel_index == i):
                        # Choose blending mode
                        with m.If(current_req.blend == BlendMode.ADDITIVE):
                            # Additive blending with saturation
                            current_intensity = Signal(unsigned(4))
                            new_intensity = Signal(unsigned(4))
                            m.d.comb += current_intensity.eq(pixels_read[i].intensity)

                            with m.If(current_intensity + current_req.pixel.intensity >= 0xF):
                                m.d.comb += new_intensity.eq(0xF)
                            with m.Else():
                                m.d.comb += new_intensity.eq(current_intensity + current_req.pixel.intensity)

                            m.d.sync += [
                                pixels_write[i].color.eq(current_req.pixel.color),
                                pixels_write[i].intensity.eq(new_intensity),
                            ]
                        with m.Else():
                            # Direct replacement
                            m.d.sync += [
                                pixels_write[i].color.eq(current_req.pixel.color),
                                pixels_write[i].intensity.eq(current_req.pixel.intensity),
                            ]
                    with m.Else():
                        # Preserve other pixels unchanged
                        m.d.sync += [
                            pixels_write[i].color.eq(pixels_read[i].color),
                            pixels_write[i].intensity.eq(pixels_read[i].intensity),
                        ]
                m.next = 'WRITE'

            with m.State('WRITE_DIRECT'):
                # Fast path for REPLACE mode - direct write using byte select
                # Only the selected byte (pixel) will be written
                pixel_data_word = Signal(32)

                # Position the pixel data in the correct byte of the 32-bit word
                for i in range(self.pixels_per_word):
                    with m.If(pixel_index == i):
                        m.d.comb += pixel_data_word[i*8:(i+1)*8].eq(
                            Cat(current_req.pixel.color, current_req.pixel.intensity)
                        )

                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(1),
                    bus.dat_w.eq(pixel_data_word),
                ]

                with m.If(bus.stb & bus.ack):
                    # Bus transaction complete - return to IDLE to signal ready for next request
                    m.next = 'IDLE'

            with m.State('WRITE'):
                # Write modified pixel data back (for additive blending)
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(1),
                    bus.dat_w.eq(pixels_write.as_value()),
                ]

                with m.If(bus.stb & bus.ack):
                    # Bus transaction complete - return to IDLE to signal ready for next request
                    m.next = 'IDLE'

        return m


class FramebufferPlotter(wiring.Component):
    """
    Complete framebuffer plotting solution with integrated cache, arbiter, and backend.

    This is the main public API for framebuffer plotting. It automatically includes:
    - Caching for performance
    - Multi-port arbitration (if n_ports > 1)
    - Read-modify-write backend
    - Coordinate transformation and bounds checking

    Usage:
    - Single port: plotter = FramebufferPlotter(fb)
    - Multi-port: plotter = FramebufferPlotter(fb, n_ports=4)

    Connect enable and rotation signals in elaborate().
    """

    def __init__(self, fb: DMAFramebuffer, n_ports: int = 1, cachesize_words: int = 64):
        self.fb = fb
        self.n_ports = n_ports
        self.cachesize_words = cachesize_words
        super().__init__({
            # Multiple plot request ports with automatic arbitration
            "ports": In(stream.Signature(PlotRequest)).array(n_ports),
            # DMA bus to PSRAM (via integrated cache)
            "bus": Out(wishbone.Signature(addr_width=fb.bus.addr_width,
                                        data_width=32, granularity=8,
                                        features={"cti", "bte"})),
            # Control signals
            "enable": In(1),
            "rotation": In(Rotation),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # Internal components
        backend = _FramebufferBackend(self.fb)
        cache = Cache(self.fb, cachesize_words=self.cachesize_words)

        m.submodules.backend = backend
        m.submodules.cache = cache

        # Connect control signals to backend
        m.d.comb += [
            backend.enable.eq(self.enable),
            backend.rotation.eq(self.rotation),
        ]

        # Multiple ports - create internal arbiter
        arbiter = PlotArbiter(n_ports=self.n_ports)
        m.submodules.arbiter = arbiter

        # Connect ports to arbiter
        for i in range(self.n_ports):
            wiring.connect(m, wiring.flipped(self.ports[i]), arbiter.ports[i])

        # Connect arbiter output to backend
        wiring.connect(m, arbiter.req, backend.req)

        # Connect backend to cache, cache to external bus
        cache.add_port(backend.bus)
        wiring.connect(m, cache.bus, wiring.flipped(self.bus))

        return m


class PlotArbiter(wiring.Component):
    """
    Round-robin arbiter for multiple plot request streams.

    Allows multiple ports to share a single backend efficiently.
    """

    def __init__(self, n_ports: int):
        self.n_ports = n_ports

        super().__init__({
            # Input ports
            "ports": In(stream.Signature(PlotRequest)).array(n_ports),
            # Arbitrated output
            "req": Out(stream.Signature(PlotRequest)),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        # Round-robin counter
        current_port = Signal(range(self.n_ports))

        # Connect current port to output (direct combinatorial connection)
        # This is safe because we only switch ports when transactions are idle
        req_valid = Signal()
        req_payload = Signal(self.req.payload.shape())

        # Multiplex based on current_port
        with m.Switch(current_port):
            for i in range(self.n_ports):
                with m.Case(i):
                    m.d.comb += [
                        req_valid.eq(self.ports[i].valid),
                        req_payload.eq(self.ports[i].payload),
                    ]

        m.d.comb += [
            self.req.valid.eq(req_valid),
            self.req.payload.eq(req_payload),
        ]

        # Ready signal back to current port
        for i in range(self.n_ports):
            with m.If(current_port == i):
                m.d.comb += self.ports[i].ready.eq(self.req.ready)
            with m.Else():
                m.d.comb += self.ports[i].ready.eq(0)

        # Round-robin: only advance ports when no transaction is active
        # This prevents payload corruption by ensuring we only switch during idle periods
        can_switch_port = Signal()
        m.d.comb += can_switch_port.eq(~self.req.valid | (self.req.valid & self.req.ready))

        with m.If(can_switch_port):
            # Safe to advance port - either idle or completing transfer this cycle
            port_has_data = Signal()

            # Check if current port has valid data
            with m.Switch(current_port):
                for i in range(self.n_ports):
                    with m.Case(i):
                        m.d.comb += port_has_data.eq(self.ports[i].valid)

            # Advance to next port if current port completed transfer or has no data
            advance_port = Signal()
            m.d.comb += advance_port.eq(
                (self.req.valid & self.req.ready) |  # Just completed a transfer
                (~port_has_data)                     # Current port has no data
            )

            with m.If(advance_port):
                with m.If(current_port == (self.n_ports - 1)):
                    m.d.sync += current_port.eq(0)
                with m.Else():
                    m.d.sync += current_port.eq(current_port + 1)

        return m


# Legacy aliases for backward compatibility
PixelPlotPeripheral = Peripheral
PixelPlotBackend = FramebufferPlotter  # Now points to full plotter
FramebufferBackend = FramebufferPlotter  # Redirect old name to new API
PixelPlotArbiter = PlotArbiter
PixelRequest = PlotRequest
Arbiter = PlotArbiter  # Legacy alias
