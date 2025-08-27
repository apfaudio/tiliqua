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
from tiliqua.pixel_plot_backend import PixelRequest

class PixelPlotPeripheral(wiring.Component):
    """
    Hardware-accelerated pixel plotter with single-word command FIFO interface.
    
    Command Format (32-bit):
    - Bits [31:20]: X coordinate (12 bits, signed -2048 to +2047)
    - Bits [19:8]:  Y coordinate (12 bits, signed -2048 to +2047)  
    - Bits [7:4]:   Color (4 bits, 0-15)
    - Bits [3:0]:   Intensity (4 bits, 0-15)
    
    Features:
    - Single bus write per pixel command
    - Deep command FIFO for pixel operations 
    - Uses shared PixelPlotBackend for actual plotting
    - Direct pixel replacement (non-additive)
    - Absolute coordinate positioning
    """

    class StatusReg(csr.Register, access="r"):
        fifo_level: csr.Field(csr.action.R, unsigned(16))
        busy:       csr.Field(csr.action.R, unsigned(1))

    def __init__(self, fifo_depth=8, granularity=8):
        self.fifo_depth = fifo_depth
        
        # Single-word command FIFO - much more efficient!
        self._cmd_fifo = fifo.SyncFIFOBuffered(width=32, depth=fifo_depth)

        # CSR registers for status
        regs = csr.Builder(addr_width=6, data_width=8)
        self._status  = regs.add("status",  self.StatusReg(),  offset=0x00)
        self._bridge = csr.Bridge(regs.as_memory_map())

        # Memory region for fast command writes (single 32-bit word = 4 bytes)
        cmd_fifo_size = 4
        mem_depth = max(1, (cmd_fifo_size * granularity) // 32)

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "wb_bus":  In(wishbone.Signature(addr_width=exact_log2(mem_depth),
                                           data_width=32, granularity=granularity)),
            "pixel_req": Out(stream.Signature(PixelRequest)),
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

        # Command FIFO read stream
        rstream = self._cmd_fifo.r_stream
        
        # Extract single-word command: [X:12|Y:12|Color:4|Intensity:4] (signed coordinates)
        x_coord = Signal(signed(12))
        y_coord = Signal(signed(12)) 
        color = Signal(4)
        intensity = Signal(4)
        
        m.d.comb += [
            x_coord.eq(rstream.payload[20:32]),    # Bits [31:20] (signed)
            y_coord.eq(rstream.payload[8:20]),     # Bits [19:8] (signed)
            intensity.eq(rstream.payload[4:8]),    # Bits [7:4]
            color.eq(rstream.payload[0:4]),        # Bits [3:0]
        ]

        # Generate pixel requests for shared backend
        m.d.comb += [
            self.pixel_req.valid.eq(self.enable & rstream.valid),
            self.pixel_req.payload.x.eq(x_coord),
            self.pixel_req.payload.y.eq(y_coord),
            self.pixel_req.payload.color.eq(color),
            self.pixel_req.payload.intensity.eq(intensity),
            self.pixel_req.payload.additive.eq(0),  # PixelPlot uses direct replacement
            self.pixel_req.payload.center_relative.eq(0),  # Assume absolute coordinates
            rstream.ready.eq(self.pixel_req.ready),
        ]

        return m
