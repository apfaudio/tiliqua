# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Simple sprite blitter peripheral with configurable 1-bit sprite memory.

Provides efficient sprite/font rendering by storing 1-bit bitmaps in local BRAM
and blitting them to the shared PixelPlotBackend with configurable color and intensity.
"""

from amaranth              import *
from amaranth.build        import *
from amaranth.lib          import wiring, data, stream
from amaranth.lib.wiring   import In, Out
from amaranth.lib.memory   import Memory
from amaranth.utils        import exact_log2

from amaranth_soc          import wishbone, csr
from amaranth_soc.memory   import MemoryMap

from tiliqua.pixel_plot_backend import PixelRequest

class SimpleBlitterPeripheral(wiring.Component):
    """
    Simple sprite blitter with 1-bit per pixel local memory.
    
    Memory Layout:
    - 1-bit per pixel sprite data (1=draw pixel, 0=transparent)
    - Configurable memory size for different sprite sheet sizes
    - 32 pixels packed per 32-bit memory word
    
    Command Interface:
    CMD0: [src_x:8|src_y:8|width:8|height:8] - Define sprite region
    CMD1: [dst_x:12|dst_y:12|color:4|intensity:4] - Blit sprite with color/intensity
    
    Features:
    - CPU can directly write sprite bitmaps to local memory
    - Single command triggers efficient sprite blitting
    - 1-bit transparency: 1=draw pixel, 0=skip (transparent)
    - Color and intensity specified per blit operation
    """

    class StatusReg(csr.Register, access="r"):
        busy: csr.Field(csr.action.R, unsigned(1))
        mem_words: csr.Field(csr.action.R, unsigned(16))  # Memory size in words

    class SrcReg(csr.Register, access="w"):
        src_x: csr.Field(csr.action.W, unsigned(8))
        src_y: csr.Field(csr.action.W, unsigned(8))
        width: csr.Field(csr.action.W, unsigned(8))
        height: csr.Field(csr.action.W, unsigned(8))

    class BlitReg(csr.Register, access="w"):
        dst_x: csr.Field(csr.action.W, signed(12))
        dst_y: csr.Field(csr.action.W, signed(12))
        color: csr.Field(csr.action.W, unsigned(4))
        intensity: csr.Field(csr.action.W, unsigned(4))
        # Note: Writing to this register triggers the blit operation

    def __init__(self, memory_words=2048):  # Default 8KB for 64K pixels
        """
        Initialize blitter with configurable sprite memory size.
        
        Args:
            memory_words: Size of sprite memory in 32-bit words
                         Each word stores 32 pixels (1-bit each)
                         Example: 2048 words = 65536 pixels = 256x256 sprite sheet
        """
        self.memory_words = memory_words
        self.memory_addr_width = exact_log2(memory_words)
        
        # Local sprite memory (1-bit per pixel, 32 pixels per word)
        self._sprite_mem = Memory(shape=unsigned(32), depth=memory_words, init=[])
        
        # CSR registers
        regs = csr.Builder(addr_width=6, data_width=8)
        self._status = regs.add("status", self.StatusReg(), offset=0x00)
        self._src = regs.add("src", self.SrcReg(), offset=0x04)
        self._blit = regs.add("blit", self.BlitReg(), offset=0x08)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            # CSR interface for commands and status
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            # Sprite memory interface for CPU
            "sprite_mem_bus": In(wishbone.Signature(addr_width=self.memory_addr_width, 
                                                  data_width=32, granularity=8)),
            # Output to shared pixel plot backend
            "pixel_req": Out(stream.Signature(PixelRequest)),
            "enable": In(1),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map
        
        # Memory map for sprite memory
        sprite_mem_map = MemoryMap(addr_width=(self.memory_addr_width+2), data_width=8)
        sprite_mem_map.add_resource(name=("sprite_memory",), size=memory_words*4, resource=self)
        self.sprite_mem_bus.memory_map = sprite_mem_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge
        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        # Sprite memory ports
        m.submodules.sprite_mem = self._sprite_mem
        sprite_r_port = self._sprite_mem.read_port()
        sprite_w_port = self._sprite_mem.write_port()
        
        # Connect sprite memory to wishbone interface (write-only)
        m.d.comb += [
            sprite_w_port.addr.eq(self.sprite_mem_bus.adr),
            sprite_w_port.data.eq(self.sprite_mem_bus.dat_w),
            sprite_w_port.en.eq(self.sprite_mem_bus.cyc & self.sprite_mem_bus.stb & self.sprite_mem_bus.we),
            # Read port is only used internally by blitter
            self.sprite_mem_bus.ack.eq(self.sprite_mem_bus.cyc & self.sprite_mem_bus.stb),
            # No read data connection - CPU can't read back sprite data
        ]

        # Latched command parameters
        src_x = Signal(8)
        src_y = Signal(8) 
        width = Signal(8)
        height = Signal(8)
        dst_x = Signal(signed(12))
        dst_y = Signal(signed(12))
        color = Signal(4)
        intensity = Signal(4)
        
        # Latch source parameters when source register is written
        with m.If(self._src.element.w_stb):
            m.d.sync += [
                src_x.eq(self._src.f.src_x.w_data),
                src_y.eq(self._src.f.src_y.w_data),
                width.eq(self._src.f.width.w_data),
                height.eq(self._src.f.height.w_data),
            ]
        
        # Latch blit parameters and trigger blit when blit register is written
        start_blit = Signal()
        with m.If(self._blit.element.w_stb):
            m.d.sync += [
                dst_x.eq(self._blit.f.dst_x.w_data),
                dst_y.eq(self._blit.f.dst_y.w_data),
                color.eq(self._blit.f.color.w_data),
                intensity.eq(self._blit.f.intensity.w_data),
                start_blit.eq(1),
            ]

        # Blit state machine
        current_x = Signal(8)
        current_y = Signal(8)
        pixel_data = Signal(32)
        pixel_bit_index = Signal(5)  # 0-31 for bit within word
        
        # Calculate memory address and bit position for current sprite pixel
        sprite_pixel_addr = Signal(self.memory_addr_width)
        sprite_pixel_index = Signal(16)  # Linear pixel index in sprite memory
        
        m.d.comb += [
            sprite_pixel_index.eq((src_y + current_y) * 256 + (src_x + current_x)),  # Assumes max 256-wide sprite sheet
            sprite_pixel_addr.eq(sprite_pixel_index >> 5),  # Divide by 32 (pixels per word)
            pixel_bit_index.eq(sprite_pixel_index[0:5]),    # Modulo 32 (bit within word)
        ]

        with m.FSM() as fsm:
            
            with m.State('IDLE'):
                m.d.comb += self._status.f.busy.r_data.eq(0)  # Not busy in IDLE
                m.d.sync += start_blit.eq(0)
                with m.If(self.enable & start_blit):
                    m.d.sync += [
                        current_x.eq(0),
                        current_y.eq(0),
                    ]
                    m.next = 'READ_SPRITE_DATA'
            
            with m.State('READ_SPRITE_DATA'):
                # Read sprite data word from memory
                m.d.comb += sprite_r_port.addr.eq(sprite_pixel_addr)
                m.d.sync += pixel_data.eq(sprite_r_port.data)
                m.next = 'CHECK_PIXEL'
            
            with m.State('CHECK_PIXEL'):
                # Check if current sprite pixel should be drawn (bit = 1)
                current_pixel_bit = Signal()
                m.d.comb += current_pixel_bit.eq(pixel_data.bit_select(pixel_bit_index, 1))
                
                with m.If(current_pixel_bit):
                    # Pixel should be drawn - send request to backend
                    m.d.comb += [
                        self.pixel_req.valid.eq(1),
                        self.pixel_req.payload.x.eq(dst_x + current_x),
                        self.pixel_req.payload.y.eq(dst_y + current_y),
                        self.pixel_req.payload.color.eq(color),
                        self.pixel_req.payload.intensity.eq(intensity),
                        self.pixel_req.payload.additive.eq(0),  # Direct replacement
                        self.pixel_req.payload.center_relative.eq(0),  # Absolute coords
                    ]
                    
                    with m.If(self.pixel_req.ready):
                        m.next = 'NEXT_PIXEL'
                with m.Else():
                    # Pixel is transparent - skip to next
                    m.next = 'NEXT_PIXEL'
            
            with m.State('NEXT_PIXEL'):
                # Advance to next pixel
                with m.If(current_x == (width - 1)):
                    # End of row
                    m.d.sync += current_x.eq(0)
                    with m.If(current_y == (height - 1)):
                        # End of sprite - blit complete
                        m.next = 'IDLE'
                    with m.Else():
                        # Next row
                        m.d.sync += current_y.eq(current_y + 1)
                        m.next = 'READ_SPRITE_DATA'
                with m.Else():
                    # Next column
                    m.d.sync += current_x.eq(current_x + 1)
                    m.next = 'READ_SPRITE_DATA'

        # Status register
        m.d.comb += [
            self._status.f.busy.r_data.eq(1),  # Default: busy
            self._status.f.mem_words.r_data.eq(self.memory_words),
        ]

        return m
