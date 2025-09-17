# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Accelerated sprite/text blitter peripheral.
Blits sub-rectangles from a spritesheet to a framebuffer.
"""

from amaranth import *
from amaranth.build import *
from amaranth.lib import fifo, stream, wiring
from amaranth.lib.memory import Memory
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2
from amaranth_soc import csr, wishbone
from amaranth_soc.memory import MemoryMap

from ..video.types import Pixel
from .plot import BlendMode, OffsetMode, PlotRequest


class Peripheral(wiring.Component):
    """
    Simple sprite/text blitter.

    Spritesheets are stored in memory-mapped BRAM local to this core.
    Sub-rectangles of the spritesheet can then be efficiently blitted to
    the framebuffer by executing single-word CSR writes.

    Storage:
    - 1-bit per pixel sprite data (1=draw pixel, 0=transparent)
    - Expected spritesheet format matches 32-bit packing of 1-bit info
      as used by Rust's `embedded-graphics` library for mono fontsheets.
    - This means a spritesheet can be written efficiently by the CPU, 32
      pixels at a time for every store.

    Usage:
    - SoC waits for ``status.empty`` to be asserted (command FIFO must be empty
      to guarantee it's safe to change the spritesheet).
    - SoC writes the spritesheet to memory-mapped ``sprite_mem_bus``, 32 pixels
      per word. The size of the spritesheet expected by this core is FIXED, so
      any unused horizontal bits must be padded. The size of the spritesheet
      may be queried by the SoC using the CSRs ``status.column_words`` and
      ``status.mem_words``.
    - SoC selects a source rectange of the spritesheet with a single write to
      the ``src`` register.
    - SoC blits the source rectangle to the desired position with a single
      write to the ``blit`` register.
    - SoC may enqueue as many ``src`` and ``blit`` ops as it wants, without
      blocking, but must always poll ``status.busy`` to make sure it is not
      asserted before each op, as this is used to indicate the command FIFO
      has no space left for new ops.
    """

    class StatusReg(csr.Register, access="r"):
        busy: csr.Field(csr.action.R, unsigned(1))  # FIFO full (can't accept new commands)
        empty: csr.Field(csr.action.R, unsigned(1))  # FIFO empty (safe to change spritesheet)
        mem_words: csr.Field(csr.action.R, unsigned(15))  # Memory size in words
        column_words: csr.Field(csr.action.R, unsigned(15))  # Spritesheet width in words

    class SrcReg(csr.Register, access="w"):
        src_x: csr.Field(csr.action.W, unsigned(8))
        src_y: csr.Field(csr.action.W, unsigned(8))
        width: csr.Field(csr.action.W, unsigned(8))
        height: csr.Field(csr.action.W, unsigned(8))

    class BlitReg(csr.Register, access="w"):
        dst_x: csr.Field(csr.action.W, signed(12))
        dst_y: csr.Field(csr.action.W, signed(12))
        pixel: csr.Field(csr.action.W, Pixel)

    def __init__(self, memory_words=1024, column_words=256//32, fifo_depth=16):
        """
        Initialize blitter with static spritesheet memory size.

        Parameters:
            memory_words: Size of sprite memory in 32-bit words
                         Each word stores 32 pixels (1-bit each)
                         Example: 1024 words = 32768 pixels = 256x128 sprite sheet
            column_words: Width of spritesheet in 32-bit words
                        Example: 256 pixels = 8 words
            fifo_depth: Depth of command FIFO for queuing blit operations
        """
        self.memory_words = memory_words
        self.column_words = column_words
        self.memory_addr_width = exact_log2(memory_words)
        self.fifo_depth = fifo_depth

        self._sprite_mem = Memory(shape=unsigned(32), depth=memory_words, init=[])

        # Command FIFO to queue blit operations
        # Each command contains: [src_x:8|src_y:8|width:8|height:8|dst_x:12|dst_y:12|pixel:8]
        # Total: 64 bits per command
        self._cmd_fifo = fifo.SyncFIFOBuffered(width=64, depth=fifo_depth)

        regs = csr.Builder(addr_width=6, data_width=8)
        self._status = regs.add("status", self.StatusReg(), offset=0x00)
        self._src = regs.add("src", self.SrcReg(), offset=0x04)
        self._blit = regs.add("blit", self.BlitReg(), offset=0x08)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "sprite_mem_bus": In(wishbone.Signature(addr_width=self.memory_addr_width,
                                                  data_width=32, granularity=8)),
            # Output to shared plot backend
            "plot_req": Out(stream.Signature(PlotRequest)),
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
        m.submodules._cmd_fifo = self._cmd_fifo
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

        # Latched source parameters (for next command)
        src_x = Signal(8)
        src_y = Signal(8)
        width = Signal(8)
        height = Signal(8)

        # Latch source parameters when source register is written
        with m.If(self._src.element.w_stb):
            m.d.sync += [
                src_x.eq(self._src.f.src_x.w_data),
                src_y.eq(self._src.f.src_y.w_data),
                width.eq(self._src.f.width.w_data),
                height.eq(self._src.f.height.w_data),
            ]

        # Enqueue command when blit register is written
        cmd_fifo_w = self._cmd_fifo.w_stream
        with m.If(self._blit.element.w_stb & cmd_fifo_w.ready):
            m.d.comb += [
                cmd_fifo_w.valid.eq(1),
                # Pack 64-bit command: [src_x:8|src_y:8|width:8|height:8|dst_x:12|dst_y:12|pixel:8]
                cmd_fifo_w.payload.eq(Cat(
                    self._blit.f.pixel.w_data,      # [7:0]
                    self._blit.f.dst_y.w_data,      # [19:8]
                    self._blit.f.dst_x.w_data,      # [31:20]
                    height,                         # [39:32]
                    width,                          # [47:40]
                    src_y,                          # [55:48]
                    src_x,                          # [63:56]
                ))
            ]

        # Current command being executed
        current_src_x = Signal(8)
        current_src_y = Signal(8)
        current_width = Signal(8)
        current_height = Signal(8)
        current_dst_x = Signal(signed(12))
        current_dst_y = Signal(signed(12))
        current_pixel = Signal(Pixel)

        # Blit state machine
        current_x = Signal(8)
        current_y = Signal(8)
        pixel_data = Signal(32)
        pixel_bit_index = Signal(5)  # 0-31 for bit within word

        # Calculate memory address and bit position for current sprite pixel
        sprite_pixel_addr = Signal(self.memory_addr_width)
        sprite_pixel_index = Signal(16)  # Linear pixel index in sprite memory

        m.d.comb += [
            sprite_pixel_index.eq((current_src_y + current_y) * (self.column_words * 32) + (current_src_x + current_x)),
            sprite_pixel_addr.eq(sprite_pixel_index >> 5),  # Divide by 32 (pixels per word)
            pixel_bit_index.eq(sprite_pixel_index[0:5]),    # Modulo 32 (bit within word)
        ]

        # Status register
        m.d.comb += [
            # busy = FIFO is full (can't accept new commands)
            self._status.f.busy.r_data.eq(~cmd_fifo_w.ready),
            # empty = FIFO is empty (safe to change spritesheet)
            self._status.f.empty.r_data.eq(~self._cmd_fifo.r_stream.valid),
            self._status.f.mem_words.r_data.eq(self.memory_words),
            self._status.f.column_words.r_data.eq(self.column_words),
        ]

        m.d.comb += sprite_r_port.addr.eq(sprite_pixel_addr)

        # Command FIFO read stream
        cmd_fifo_r = self._cmd_fifo.r_stream

        with m.FSM() as fsm:

            with m.State('IDLE'):
                # Wait for command from FIFO
                with m.If(self.enable & cmd_fifo_r.valid):
                    # Unpack command from FIFO
                    m.d.sync += [
                        current_pixel.eq(cmd_fifo_r.payload[0:8]),        # [7:0]
                        current_dst_y.eq(cmd_fifo_r.payload[8:20]),       # [19:8]
                        current_dst_x.eq(cmd_fifo_r.payload[20:32]),      # [31:20]
                        current_height.eq(cmd_fifo_r.payload[32:40]),     # [39:32]
                        current_width.eq(cmd_fifo_r.payload[40:48]),      # [47:40]
                        current_src_y.eq(cmd_fifo_r.payload[48:56]),      # [55:48]
                        current_src_x.eq(cmd_fifo_r.payload[56:64]),      # [63:56]
                        current_x.eq(0),
                        current_y.eq(0),
                    ]
                    m.d.comb += cmd_fifo_r.ready.eq(1)
                    m.next = 'READ_SPRITE_DATA1'

            with m.State('READ_SPRITE_DATA1'):
                m.next = 'READ_SPRITE_DATA2'

            with m.State('READ_SPRITE_DATA2'):
                m.d.sync += pixel_data.eq(sprite_r_port.data)
                m.next = 'CHECK_PIXEL'

            with m.State('CHECK_PIXEL'):
                # Check if current sprite pixel should be drawn (bit = 1)
                current_pixel_bit = Signal()
                # Handle MSB-first bit ordering within bytes from embedded-graphics
                # Convert bit index to account for byte-swapped storage
                byte_in_word = Signal(3)  # Which byte (0-3)
                bit_in_byte = Signal(3)   # Which bit in that byte (0-7)
                corrected_bit_index = Signal(5)  # Corrected bit index (0-31)

                m.d.comb += [
                    byte_in_word.eq(pixel_bit_index >> 3),  # Which byte (0-3)
                    bit_in_byte.eq(pixel_bit_index[0:3]),   # Which bit in that byte (0-7)
                    corrected_bit_index.eq((byte_in_word << 3) | (7 - bit_in_byte)),  # MSB-first within byte
                    current_pixel_bit.eq(pixel_data.bit_select(corrected_bit_index, 1)),
                ]

                with m.If(current_pixel_bit):
                    # Pixel should be drawn - send request to backend
                    m.d.comb += [
                        self.plot_req.valid.eq(1),
                        self.plot_req.payload.x.eq(current_dst_x + current_x),
                        self.plot_req.payload.y.eq(current_dst_y + current_y),
                        self.plot_req.payload.pixel.eq(current_pixel),
                        self.plot_req.payload.blend.eq(BlendMode.REPLACE),  # Direct replacement
                        self.plot_req.payload.offset.eq(OffsetMode.ABSOLUTE),  # Absolute coords
                    ]

                    with m.If(self.plot_req.ready):
                        m.next = 'NEXT_PIXEL'
                with m.Else():
                    # Pixel is transparent - skip to next
                    m.next = 'NEXT_PIXEL'

            with m.State('NEXT_PIXEL'):
                # Advance to next pixel
                with m.If(current_x == (current_width - 1)):
                    # End of row
                    m.d.sync += current_x.eq(0)
                    with m.If(current_y == (current_height - 1)):
                        # End of sprite - blit complete, return to IDLE for next command
                        m.next = 'IDLE'
                    with m.Else():
                        # Next row
                        m.d.sync += current_y.eq(current_y + 1)
                        m.next = 'READ_SPRITE_DATA1'
                with m.Else():
                    # Next column
                    m.d.sync += current_x.eq(current_x + 1)
                    m.next = 'READ_SPRITE_DATA1'

        return m
