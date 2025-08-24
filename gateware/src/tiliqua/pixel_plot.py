# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Hardware-accelerated pixel plotting for framebuffer operations.

Provides a single-word command FIFO interface for fast pixel operations, replacing 
the slow read-modify-write loop in embedded-graphics DrawTarget implementations.

Command format: [X:12|Y:12|Color:4|Intensity:4] (single 32-bit word)
"""

from amaranth              import *
from amaranth.build        import *
from amaranth.lib          import wiring, data, stream, fifo
from amaranth.lib.wiring   import In, Out
from amaranth.utils        import exact_log2

from amaranth_soc          import wishbone, csr
from amaranth_soc.memory   import MemoryMap

from tiliqua.dma_framebuffer import DMAFramebuffer

class PixelPlotPeripheral(wiring.Component):
    """
    Hardware-accelerated pixel plotter with single-word command FIFO interface.
    
    Command Format (32-bit):
    - Bits [31:20]: X coordinate (12 bits, 0-4095)
    - Bits [19:8]:  Y coordinate (12 bits, 0-4095)  
    - Bits [7:4]:   Color (4 bits, 0-15)
    - Bits [3:0]:   Intensity (4 bits, 0-15)
    
    Features:
    - Single bus write per pixel command
    - Deep command FIFO for pixel operations 
    - Asynchronous pixel processing with read-modify-write
    - Additive blending with saturation
    - Optional 90° rotation support
    """

    class StatusReg(csr.Register, access="r"):
        fifo_level: csr.Field(csr.action.R, unsigned(16))
        busy:       csr.Field(csr.action.R, unsigned(1))

    class ControlReg(csr.Register, access="w"):
        rotate_left: csr.Field(csr.action.W, unsigned(1))

    def __init__(self, fb: DMAFramebuffer, fifo_depth=512, granularity=8):
        self.fb = fb
        self.fifo_depth = fifo_depth
        
        # Single-word command FIFO - much more efficient!
        self._cmd_fifo = fifo.SyncFIFOBuffered(width=32, depth=fifo_depth)

        # CSR registers for status and control
        regs = csr.Builder(addr_width=6, data_width=8)
        self._status  = regs.add("status",  self.StatusReg(),  offset=0x00)
        self._control = regs.add("control", self.ControlReg(), offset=0x04)
        self._bridge = csr.Bridge(regs.as_memory_map())

        # Memory region for fast command writes (single 32-bit word = 4 bytes)
        cmd_fifo_size = 4
        mem_depth = max(1, (cmd_fifo_size * granularity) // 32)

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "wb_bus":  In(wishbone.Signature(addr_width=exact_log2(mem_depth),
                                           data_width=32, granularity=granularity)),
            "bus_dma": Out(wishbone.Signature(addr_width=fb.bus.addr_width, 
                                            data_width=32, granularity=8)),
            "enable": In(1),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map
        
        # Memory map for command writes
        wb_memory_map = MemoryMap(addr_width=exact_log2(cmd_fifo_size), data_width=granularity)
        wb_memory_map.add_resource(name=("pixel_cmd_fifo",), size=cmd_fifo_size, resource=self)
        self.wb_bus.memory_map = wb_memory_map

    def elaborate(self, platform) -> Module:
        m = Module()
        
        m.submodules.bridge = self._bridge
        m.submodules._cmd_fifo = self._cmd_fifo

        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        # Store CSR register values 
        rotate_left = Signal()
        with m.If(self._control.f.rotate_left.w_stb):
            m.d.sync += rotate_left.eq(self._control.f.rotate_left.w_data)

        # Single-word command interface - immediate processing!
        wstream = self._cmd_fifo.w_stream
        with m.If(self.wb_bus.cyc & self.wb_bus.stb & self.wb_bus.we):
            m.d.comb += [
                # Direct FIFO write - single command word
                wstream.valid.eq(1),
                wstream.payload.eq(self.wb_bus.dat_w),
                # ACK immediately if FIFO accepts, otherwise stall
                self.wb_bus.ack.eq(wstream.ready),
            ]

        # Status register updates
        m.d.comb += [
            self._status.f.fifo_level.r_data.eq(self._cmd_fifo.level),
            self._status.f.busy.r_data.eq(self._cmd_fifo.level != 0),
        ]

        # Pixel plotting engine - all inline in elaborate()
        # Framebuffer parameters
        fb_hwords = ((self.fb.timings.h_active * self.fb.bytes_per_pixel) // 4)
        
        # Define pixel structure: 4-bit color + 4-bit intensity  
        pixel_layout = data.StructLayout({
            "color": unsigned(4),
            "intensity": unsigned(4),
        })
        pixels_per_word = 32 // pixel_layout.as_shape().width
        pixel_array_layout = data.ArrayLayout(pixel_layout, pixels_per_word)

        # Command FIFO read stream
        rstream = self._cmd_fifo.r_stream
        
        # Extract single-word command: [X:12|Y:12|Color:4|Intensity:4]
        x_coord = Signal(12)
        y_coord = Signal(12) 
        color = Signal(4)
        intensity = Signal(4)
        
        m.d.comb += [
            x_coord.eq(rstream.payload[20:32]),    # Bits [31:20]
            y_coord.eq(rstream.payload[8:20]),     # Bits [19:8]
            color.eq(rstream.payload[4:8]),        # Bits [7:4]
            intensity.eq(rstream.payload[0:4]),    # Bits [3:0]
        ]
        
        # Pixel position calculations
        x_offs = Signal(unsigned(16))
        y_offs = Signal(unsigned(16))
        pixel_index = Signal(unsigned(2))  # Which of the 4 pixels in the word
        pixel_addr = Signal(unsigned(32))
        
        # Pixel data for read-modify-write
        pixels_read = Signal(pixel_array_layout)
        pixels_write = Signal(pixel_array_layout)
        
        # DMA bus
        bus = self.bus_dma
        
        # Coordinate transformation and bounds checking
        with m.If(rotate_left):
            # 90° left rotation (like in Stroke component)
            m.d.comb += [
                pixel_index.eq((-y_coord)[0:2]),
                x_offs.eq((fb_hwords//2) + ((-y_coord)>>2)),
                y_offs.eq(x_coord + (self.fb.timings.v_active>>1)),
            ]
        with m.Else():
            m.d.comb += [
                pixel_index.eq(x_coord[0:2]),
                x_offs.eq((fb_hwords//2) + (x_coord>>2)),
                y_offs.eq(y_coord + (self.fb.timings.v_active>>1)),
            ]
        
        m.d.comb += pixel_addr.eq(self.fb.fb_base + y_offs*fb_hwords + x_offs)

        # Pixel plotting FSM - processes commands from FIFO
        with m.FSM() as fsm:
            
            with m.State('IDLE'):
                with m.If(self.enable & rstream.valid):
                    m.next = 'CHECK_BOUNDS'
            
            with m.State('CHECK_BOUNDS'):
                # Only plot pixels within framebuffer bounds (12-bit coords)
                with m.If((x_offs < fb_hwords) & (y_offs < self.fb.timings.v_active)):
                    m.d.sync += [
                        bus.sel.eq(0xf),
                        bus.adr.eq(pixel_addr),
                    ]
                    m.next = 'READ'
                with m.Else():
                    # Skip out-of-bounds pixels
                    m.d.comb += rstream.ready.eq(1)
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
                # Calculate new pixel values with additive blending
                current_intensity = Signal(unsigned(4))
                new_intensity = Signal(unsigned(4))
                
                m.d.comb += current_intensity.eq(pixels_read[pixel_index].intensity)
                
                # Additive blending with saturation
                with m.If(current_intensity + intensity >= 0xF):
                    m.d.comb += new_intensity.eq(0xF)
                with m.Else():
                    m.d.comb += new_intensity.eq(current_intensity + intensity)
                
                # Update the target pixel, preserve others
                for i in range(pixels_per_word):
                    with m.If(pixel_index == i):
                        m.d.sync += [
                            pixels_write[i].color.eq(color),
                            pixels_write[i].intensity.eq(new_intensity),
                        ]
                    with m.Else():
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
                    # Command complete, get next one
                    m.d.comb += rstream.ready.eq(1)
                    m.next = 'IDLE'

        return m
