# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Accelerated sprite/text blitter peripheral.
Blits sub-rectangles from a spritesheet to a framebuffer.
"""

from amaranth import *
from amaranth.build import *
from amaranth.lib import fifo, stream, wiring, data, enum
from amaranth.lib.memory import Memory
from amaranth.lib.wiring import In, Out
from amaranth.utils import exact_log2
from amaranth_soc import csr, wishbone
from amaranth_soc.memory import MemoryMap

from ..video.types import Pixel
from ..dsp import stream_util
from .plot import BlendMode, OffsetMode, PlotRequest


class Peripheral(wiring.Component):
    """
    Simple sprite/text blitter.

    Spritesheets are stored in memory-mapped BRAM local to this core.
    Sub-rectangles of the spritesheet can then be efficiently blitted to
    the framebuffer by performing CSR writes.

    Storage:
    - 1-bit per pixel sprite data (1=draw pixel, 0=transparent)
    - Spritesheet in-memory format matches 32-bit-per-word packing of 1-bit info
      as used by Rust's ``embedded-graphics`` library for mono fontsheets, so that
      a simple ``memcpy`` of raw fontsheet data into the spritesheet memory is
      sufficient for this core to work as expected.

    Usage:
    - SoC waits for ``status.empty`` to be asserted (command FIFO must be empty
      to guarantee it's safe to change the spritesheet).
    - SoC writes the spritesheet to memory-mapped ``sprite_mem_bus``, 32 pixels
      per word. The data must be no larger than ``status.mem_words``, and the SoC
      must update the ``sheet_width.width`` register with the horizontal width of
      the sheet in pixels. This ensures the core indexes the sheet correctly.
    - SoC selects a source rectangle of the spritesheet with a single write to
      the ``src`` register.
    - SoC blits the source rectangle to the desired position with a single
      write to the ``blit`` register.
    - SoC may enqueue as many ``src`` and ``blit`` ops as it wants, without
      blocking, but must always poll ``status.full`` to make sure it is not
      asserted before each op, as this is used to indicate the command FIFO
      has no space left for new ops.

    WARN: at the moment, sprite sheet width (in pixels) MUST be divisible by 8
    for the indexing logic below to work correctly.
    """

    class StatusReg(csr.Register, access="r"):
        # Command FIFO full (can't accept new commands)
        full: csr.Field(csr.action.R, unsigned(1))
        # Command FIFO empty (safe to change spritesheet, no pending commands)
        empty: csr.Field(csr.action.R, unsigned(1))
        # Size of spritesheet memory in 32-bit words
        mem_words: csr.Field(csr.action.R, unsigned(15))

    class SheetWidthReg(csr.Register, access="w"):
        # Size of spritesheet width in pixels, used by this core for indexing calculations
        width: csr.Field(csr.action.W, unsigned(16))

    class SrcReg(csr.Register, access="w"):
        # Command to change the source rectangle in the spritesheet.
        # Should always be a single-word write for all fields.
        src_x: csr.Field(csr.action.W, unsigned(8))
        src_y: csr.Field(csr.action.W, unsigned(8))
        width: csr.Field(csr.action.W, unsigned(8))
        height: csr.Field(csr.action.W, unsigned(8))

    class BlitReg(csr.Register, access="w"):
        # Command to blit the last SrcReg command to the provided destination,
        # with the provided color. Should always be a single-word write for all fields.
        dst_x: csr.Field(csr.action.W, signed(12))
        dst_y: csr.Field(csr.action.W, signed(12))
        pixel: csr.Field(csr.action.W, Pixel)

    class BlitCmd(data.Struct):
        """
        Single entry in internal command FIFO, used to store pending
        commands issued by CSR writes, that yet to be executed..
        """
        class Kind(enum.Enum):
            SRC = 0
            BLIT = 1
        kind: Kind
        params: data.UnionLayout({
            "src": data.StructLayout({
                "src_x": unsigned(8),
                "src_y": unsigned(8),
                "width": unsigned(8),
                "height": unsigned(8),
            }),
            "blit": data.StructLayout({
                "dst_x": signed(12),
                "dst_y": signed(12),
                "pixel": Pixel,
            }),
        })

    def __init__(self, memory_words=1024, fifo_depth=8):

        self.memory_words = memory_words
        self.memory_addr_width = exact_log2(memory_words)
        self.fifo_depth = fifo_depth

        self._sprite_mem = Memory(shape=unsigned(32), depth=memory_words, init=[])
        self._cmd_fifo = stream_util.SyncFIFOBuffered(shape=self.BlitCmd, depth=fifo_depth)

        regs = csr.Builder(addr_width=6, data_width=8)
        self._status = regs.add("status", self.StatusReg(), offset=0x00)
        self._src = regs.add("src", self.SrcReg(), offset=0x04)
        self._blit = regs.add("blit", self.BlitReg(), offset=0x08)
        self._sheet_width = regs.add("sheet_width", self.SheetWidthReg(), offset=0x0C)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            "sprite_mem_bus": In(wishbone.Signature(addr_width=self.memory_addr_width,
                                                    data_width=32, granularity=8)),
            "o": Out(stream.Signature(PlotRequest)),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map

        # Memory map for sprite memory
        memory_bytes = memory_words*4
        sprite_mem_map = MemoryMap(addr_width=exact_log2(memory_bytes), data_width=8)
        sprite_mem_map.add_resource(name=("sprite_memory",), size=memory_bytes, resource=self)
        self.sprite_mem_bus.memory_map = sprite_mem_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge
        m.submodules._cmd_fifo = cmd_fifo = self._cmd_fifo
        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        m.submodules.sprite_mem = self._sprite_mem
        sprite_r_port = self._sprite_mem.read_port()
        sprite_w_port = self._sprite_mem.write_port()

        # Sheet width CSR (SoC must set this)
        sheet_width_px = Signal(16)
        with m.If(self._sheet_width.element.w_stb):
            m.d.sync += sheet_width_px.eq(self._sheet_width.f.width.w_data)

        # Status register (SoC must check this before issuing commands)
        m.d.comb += [
            # full = FIFO can't accept new commands
            self._status.f.full.r_data.eq(~cmd_fifo.i.ready),
            # empty = FIFO is empty and no command executing (safe to change spritesheet)
            self._status.f.empty.r_data.eq(~cmd_fifo.o.valid & cmd_fifo.o.ready),
            self._status.f.mem_words.r_data.eq(self.memory_words),
        ]

        # Connect spritesheet memory to wishbone interface (write-only)
        m.d.comb += [
            sprite_w_port.addr.eq(self.sprite_mem_bus.adr),
            sprite_w_port.data.eq(self.sprite_mem_bus.dat_w),
            sprite_w_port.en.eq(self.sprite_mem_bus.cyc & self.sprite_mem_bus.stb & self.sprite_mem_bus.we),
            self.sprite_mem_bus.ack.eq(self.sprite_mem_bus.cyc & self.sprite_mem_bus.stb),
        ]

        # Enqueue command on 'src' register write
        with m.If(self._src.element.w_stb):
            m.d.comb += [
                cmd_fifo.i.valid.eq(1),
                cmd_fifo.i.payload.kind.eq(self.BlitCmd.Kind.SRC),
                cmd_fifo.i.payload.params.src.src_x.eq(self._src.f.src_x.w_data),
                cmd_fifo.i.payload.params.src.src_y.eq(self._src.f.src_y.w_data),
                cmd_fifo.i.payload.params.src.width.eq(self._src.f.width.w_data),
                cmd_fifo.i.payload.params.src.height.eq(self._src.f.height.w_data),
            ]

        # Enqueue command on 'blit' register write
        with m.If(self._blit.element.w_stb & cmd_fifo.i.ready):
            m.d.comb += [
                cmd_fifo.i.valid.eq(1),
                cmd_fifo.i.payload.kind.eq(self.BlitCmd.Kind.BLIT),
                cmd_fifo.i.payload.params.blit.dst_x.eq(self._blit.f.dst_x.w_data),
                cmd_fifo.i.payload.params.blit.dst_y.eq(self._blit.f.dst_y.w_data),
                cmd_fifo.i.payload.params.blit.pixel.eq(self._blit.f.pixel.w_data),
            ]

        # Current command being executed (i.e. last command taken from command FIFO)
        current_src_x = Signal(8)
        current_src_y = Signal(8)
        current_width = Signal(8)
        current_height = Signal(8)
        current_dst_x = Signal(signed(12))
        current_dst_y = Signal(signed(12))
        current_pixel = Signal(Pixel)

        # Calculate source position within the sprite sheet.
        # `plot_x` and `plot_y` are the relative position within the sprite
        # rectangle, which is iterated across during a blit operation.
        plot_x = Signal(8)
        plot_y = Signal(8)
        sprite_x = Signal(16)
        sprite_y = Signal(16)

        # Calculate sprite memory address and bit position (in sprite memory) for current source pixel
        # TODO/WARN: currently this will only work if width (px) is divisible by 8!
        # TODO: these bit ops are a bit tricky to understand, although I can't immediately figure out
        # a nice way to make them a bit easier to read...
        bytes_per_row = Signal(16)
        byte_addr = Signal(16)
        sprite_memory_addr = Signal(self.memory_addr_width)
        pixel_bit_index = Signal(5)
        m.d.comb += [
            bytes_per_row.eq((sheet_width_px + 7) >> 3),
            byte_addr.eq(sprite_y * bytes_per_row + (sprite_x >> 3)),
            sprite_memory_addr.eq(byte_addr>>2),
            pixel_bit_index.eq(((byte_addr & 3) << 3) | (sprite_x & 7)),
        ]

        # Check if current pixel should be drawn (handle MSB-first bytes in little-endian words, as we
        # will get from a `memcpy` of raw fontsheet data)
        draw_pixel = Signal()
        corrected_bit_index = Signal(5)
        m.d.comb += [
            corrected_bit_index.eq(((pixel_bit_index>>3)<<3) | (7 - pixel_bit_index[0:3])),
            draw_pixel.eq(sprite_r_port.data.bit_select(corrected_bit_index, 1)),
        ]

        m.d.comb += [
            self.o.payload.x.eq(current_dst_x + plot_x),
            self.o.payload.y.eq(current_dst_y + plot_y),
            self.o.payload.pixel.eq(current_pixel),
            self.o.payload.blend.eq(BlendMode.REPLACE),
            self.o.payload.offset.eq(OffsetMode.ABSOLUTE),
        ]

        m.d.comb += sprite_r_port.addr.eq(sprite_memory_addr)

        with m.FSM() as fsm:

            with m.State('IDLE'):
                m.d.comb += cmd_fifo.o.ready.eq(1)
                with m.If(cmd_fifo.o.valid):
                    with m.Switch(cmd_fifo.o.payload.kind):
                        with m.Case(self.BlitCmd.Kind.SRC):
                            m.d.sync += [
                                current_src_x .eq(cmd_fifo.o.payload.params.src.src_x),
                                current_src_y .eq(cmd_fifo.o.payload.params.src.src_y),
                                current_height.eq(cmd_fifo.o.payload.params.src.height),
                                current_width .eq(cmd_fifo.o.payload.params.src.width),
                            ]
                            # Stay in 'IDLE' state on spritesheet source commands.
                        with m.Case(self.BlitCmd.Kind.BLIT):
                            m.d.sync += [
                                plot_x.eq(0),
                                plot_y.eq(0),
                                sprite_x.eq(current_src_x),
                                sprite_y.eq(current_src_y),
                                current_dst_x.eq(cmd_fifo.o.payload.params.blit.dst_x),
                                current_dst_y.eq(cmd_fifo.o.payload.params.blit.dst_y),
                                current_pixel.eq(cmd_fifo.o.payload.params.blit.pixel),
                            ]
                            m.next = 'READ_SPRITE_DATA'

            with m.State('READ_SPRITE_DATA'):
                m.next = 'CHECK_PIXEL'

            with m.State('CHECK_PIXEL'):
                with m.If(draw_pixel):
                    # Send request to plotting backend, wait until it is accepted.
                    m.d.comb += self.o.valid.eq(1),
                    with m.If(self.o.ready):
                        m.next = 'NEXT_PIXEL'
                with m.Else():
                    # Pixel is transparent - skip to next
                    m.next = 'NEXT_PIXEL'

            with m.State('NEXT_PIXEL'):
                with m.If(plot_x == (current_width - 1)):
                    m.d.sync += plot_x.eq(0)
                    m.d.sync += sprite_x.eq(current_src_x)
                    with m.If(plot_y == (current_height - 1)):
                        m.next = 'IDLE'
                    with m.Else():
                        m.d.sync += plot_y.eq(plot_y + 1)
                        m.d.sync += sprite_y.eq(sprite_y + 1)
                        m.next = 'READ_SPRITE_DATA'
                with m.Else():
                    m.d.sync += plot_x.eq(plot_x + 1)
                    m.d.sync += sprite_x.eq(sprite_x + 1)
                    m.next = 'READ_SPRITE_DATA'

        return m
