# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Shared pixel plotting backend for framebuffer operations.

Provides common read-modify-write pixel plotting functionality that can be 
shared between multiple clients (raster_stroke, pixel_plot, etc.) with
optional round-robin arbitration.
"""

from amaranth              import *
from amaranth.build        import *
from amaranth.lib          import wiring, data, stream
from amaranth.lib.wiring   import In, Out
from amaranth.utils        import exact_log2

from amaranth_soc          import wishbone

from tiliqua.dma_framebuffer import DMAFramebuffer

class PixelRequest(data.Struct):
    """Single pixel plotting request."""
    x:         signed(12)    # X coordinate (signed, -2048 to +2047)
    y:         signed(12)    # Y coordinate (signed, -2048 to +2047)  
    color:     unsigned(4)   # Color (0-15)
    intensity: unsigned(4)   # Intensity (0-15)
    additive:  unsigned(1)   # 1=additive blend, 0=replace
    center_relative: unsigned(1)  # 1=relative to center, 0=absolute coordinates

class PixelPlotBackend(wiring.Component):
    """
    Shared pixel plotting backend with read-modify-write capability.
    
    Features:
    - Handles common pixel read-modify-write cycle
    - Supports both additive blending and direct replacement
    - Coordinate transformation (rotation) support
    - Bounds checking
    - Stream interface for pixel requests
    """

    def __init__(self, fb: DMAFramebuffer):
        self.fb = fb
        
        # Define pixel structure: 4-bit color + 4-bit intensity
        self.pixel_layout = data.StructLayout({
            "color": unsigned(4),
            "intensity": unsigned(4),
        })
        self.pixels_per_word = 32 // self.pixel_layout.as_shape().width
        self.pixel_array_layout = data.ArrayLayout(self.pixel_layout, self.pixels_per_word)

        super().__init__({
            # Pixel request stream
            "req": In(stream.Signature(PixelRequest)),
            # DMA bus for framebuffer access
            "bus": Out(wishbone.Signature(addr_width=fb.bus.addr_width, 
                                        data_width=32, granularity=8)),
            # Control signals
            "enable": In(1),
            "rotate_left": In(1),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        bus = self.bus
        req = self.req
        
        # Framebuffer parameters
        fb_hwords = ((self.fb.timings.h_active * self.fb.bytes_per_pixel) // 4)
        
        # Pixel data for read-modify-write
        pixels_read = Signal(self.pixel_array_layout)
        pixels_write = Signal(self.pixel_array_layout)
        
        # Current request being processed
        current_req = Signal(PixelRequest)
        
        # Pixel position calculations
        x_offs = Signal(unsigned(16))
        y_offs = Signal(unsigned(16))
        pixel_index = Signal(unsigned(2))  # Which of the 4 pixels in the word
        pixel_addr = Signal(unsigned(32))
        
        # Coordinate transformation with center-relative support
        abs_x = Signal(signed(16))
        abs_y = Signal(signed(16))
        
        # Convert to absolute coordinates if center_relative is set
        # Center calculation depends on rotation
        with m.If(current_req.center_relative):
            with m.If(self.rotate_left):
                # When rotated, X maps to Y and Y maps to X
                m.d.comb += [
                    abs_x.eq(current_req.x + (self.fb.timings.v_active >> 1)),
                    abs_y.eq(current_req.y + (self.fb.timings.h_active >> 1)),
                ]
            with m.Else():
                m.d.comb += [
                    abs_x.eq(current_req.x + (self.fb.timings.h_active >> 1)),
                    abs_y.eq(current_req.y + (self.fb.timings.v_active >> 1)),
                ]
        with m.Else():
            m.d.comb += [
                abs_x.eq(current_req.x),
                abs_y.eq(current_req.y),
            ]
        
        # Handle rotation and pixel addressing
        with m.If(self.rotate_left):
            # 90° clockwise rotation: (x,y) -> (v_active-1-y, x)
            rotated_y = Signal(signed(16))
            m.d.comb += rotated_y.eq(self.fb.timings.v_active - 1 - abs_y)
            m.d.comb += [
                pixel_index.eq(rotated_y[0:2]),
                x_offs.eq(rotated_y >> 2),
                y_offs.eq(abs_x),
            ]
        with m.Else():
            m.d.comb += [
                pixel_index.eq(abs_x[0:2]),
                x_offs.eq((abs_x>>2)),
                y_offs.eq(abs_y),
            ]
        
        m.d.comb += pixel_addr.eq(self.fb.fb_base + y_offs*fb_hwords + x_offs)

        # Pixel plotting FSM
        with m.FSM() as fsm:
            
            with m.State('IDLE'):
                with m.If(self.enable & req.valid):
                    m.d.sync += current_req.eq(req.payload)
                    m.next = 'CHECK_BOUNDS'
            
            with m.State('CHECK_BOUNDS'):
                # Only plot pixels within framebuffer bounds
                with m.If((x_offs < fb_hwords) & (y_offs < self.fb.timings.v_active)):
                    m.d.sync += [
                        bus.sel.eq(0xf),
                        bus.adr.eq(pixel_addr),
                    ]
                    m.next = 'READ'
                with m.Else():
                    # Skip out-of-bounds pixels
                    m.d.comb += req.ready.eq(1)
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
                        with m.If(current_req.additive):
                            # Additive blending with saturation
                            current_intensity = Signal(unsigned(4))
                            new_intensity = Signal(unsigned(4))
                            m.d.comb += current_intensity.eq(pixels_read[i].intensity)
                            
                            with m.If(current_intensity + current_req.intensity >= 0xF):
                                m.d.comb += new_intensity.eq(0xF)
                            with m.Else():
                                m.d.comb += new_intensity.eq(current_intensity + current_req.intensity)
                                
                            m.d.sync += [
                                pixels_write[i].color.eq(current_req.color),
                                pixels_write[i].intensity.eq(new_intensity),
                            ]
                        with m.Else():
                            # Direct replacement
                            m.d.sync += [
                                pixels_write[i].color.eq(current_req.color),
                                pixels_write[i].intensity.eq(current_req.intensity),
                            ]
                    with m.Else():
                        # Preserve other pixels unchanged
                        m.d.sync += [
                            pixels_write[i].color.eq(pixels_read[i].color),
                            pixels_write[i].intensity.eq(pixels_read[i].intensity),
                        ]
                m.next = 'WRITE'

            with m.State('WRITE'):
                # Write modified pixel data back
                m.d.comb += [
                    bus.stb.eq(1),
                    bus.cyc.eq(1),
                    bus.we.eq(1),
                    bus.dat_w.eq(pixels_write.as_value()),
                ]
                
                with m.If(bus.stb & bus.ack):
                    # Request complete, get next one
                    m.d.comb += req.ready.eq(1)
                    m.next = 'IDLE'

        return m


class PixelPlotArbiter(wiring.Component):
    """
    Round-robin arbiter for multiple pixel plotting clients.
    
    Allows multiple clients (e.g., multiple Stroke instances) to share
    a single PixelPlotBackend efficiently.
    """
    
    def __init__(self, backend: PixelPlotBackend, n_clients: int):
        self.backend = backend
        self.n_clients = n_clients
        
        super().__init__({
            # Client request streams
            "clients": In(stream.Signature(PixelRequest)).array(n_clients),
            # Backend connection
            "backend_req": Out(stream.Signature(PixelRequest)),
        })
    
    def elaborate(self, platform) -> Module:
        m = Module()
        
        # Round-robin counter
        current_client = Signal(range(self.n_clients))
        
        # Connect current client to backend (using multiplexing since we can't use dynamic indexing)
        backend_valid = Signal()
        backend_payload = Signal(self.backend_req.payload.shape())
        
        # Multiplex based on current_client
        with m.Switch(current_client):
            for i in range(self.n_clients):
                with m.Case(i):
                    m.d.comb += [
                        backend_valid.eq(self.clients[i].valid),
                        backend_payload.eq(self.clients[i].payload),
                    ]
        
        m.d.comb += [
            self.backend_req.valid.eq(backend_valid),
            self.backend_req.payload.eq(backend_payload),
        ]
        
        # Ready signal back to current client
        for i in range(self.n_clients):
            with m.If(current_client == i):
                m.d.comb += self.clients[i].ready.eq(self.backend_req.ready)
            with m.Else():
                m.d.comb += self.clients[i].ready.eq(0)
        
        # Simple round-robin: advance to next client every cycle, skip if not valid
        # Always advance to next client after serving current one
        with m.If(self.backend_req.valid & self.backend_req.ready):
            # Move to next client
            with m.If(current_client == (self.n_clients - 1)):
                m.d.sync += current_client.eq(0)
            with m.Else():
                m.d.sync += current_client.eq(current_client + 1)
        # If current client has no request, also move to next
        with m.Elif(~backend_valid):
            with m.If(current_client == (self.n_clients - 1)):
                m.d.sync += current_client.eq(0)
            with m.Else():
                m.d.sync += current_client.eq(current_client + 1)

        return m