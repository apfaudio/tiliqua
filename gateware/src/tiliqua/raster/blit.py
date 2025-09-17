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

    class BlitCmd(data.Struct):
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

    def __init__(self, memory_words=1024, column_words=256//32, fifo_depth=16):
        """
        Initialize blitter (static spritesheet memory size and command fifo depth).

        Worked example:
        - ``memory_words``: size of sprite memory in 32-bit words.
        - ``column_words``: width of spritesheet in 32-bit words.
        - e.g. ``memory_words=1024`` and ``column_words=256//32=8`` is storage for
          32768 pixels in a 256 (width) x 128 (height) arrangement.
        """
        self.memory_words = memory_words
        self.column_words = column_words
        self.memory_addr_width = exact_log2(memory_words)
        self.fifo_depth = fifo_depth

        self._sprite_mem = Memory(shape=unsigned(32), depth=memory_words, init=[])
        self._cmd_fifo = stream_util.SyncFIFOBuffered(shape=self.BlitCmd, depth=fifo_depth)

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
        m.submodules._cmd_fifo = cmd_fifo = self._cmd_fifo
        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        m.submodules.sprite_mem = self._sprite_mem
        sprite_r_port = self._sprite_mem.read_port()
        sprite_w_port = self._sprite_mem.write_port()

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

        # Current command being executed
        current_src_x = Signal(8)
        current_src_y = Signal(8)
        current_width = Signal(8)
        current_height = Signal(8)
        current_dst_x = Signal(signed(12))
        current_dst_y = Signal(signed(12))
        current_pixel = Signal(Pixel)

        # Blit state machine
        plot_x = Signal(8)
        plot_y = Signal(8)
        pixel_bit_index = Signal(5)  # 0-31 for bit within word

        # Calculate memory address and bit position for current sprite pixel
        sprite_pixel_addr = Signal(self.memory_addr_width)
        sprite_pixel_index = Signal(range(self.memory_words*32)) 

        m.d.comb += [
            sprite_pixel_index.eq((current_src_y + plot_y) * (self.column_words * 32) + (current_src_x + plot_x)),
            sprite_pixel_addr.eq(sprite_pixel_index >> 5),  # / 32 (pixels per word)
            pixel_bit_index.eq(sprite_pixel_index[0:5]),    # % 32 (bit within word)
        ]

        # Status register
        m.d.comb += [
            # busy = FIFO is full (can't accept new commands)
            self._status.f.busy.r_data.eq(~cmd_fifo.i.ready),
            # empty = FIFO is empty (safe to change spritesheet)
            self._status.f.empty.r_data.eq(~cmd_fifo.o.valid),
            self._status.f.mem_words.r_data.eq(self.memory_words),
            self._status.f.column_words.r_data.eq(self.column_words),
        ]

        m.d.comb += sprite_r_port.addr.eq(sprite_pixel_addr)

        with m.FSM() as fsm:

            with m.State('IDLE'):
                # Wait for command from FIFO
                with m.If(self.enable & cmd_fifo.o.valid):
                    m.d.comb += cmd_fifo.o.ready.eq(1)
                    with m.Switch(cmd_fifo.o.payload.kind):
                        with m.Case(self.BlitCmd.Kind.SRC):
                            m.d.sync += [
                                current_src_x .eq(cmd_fifo.o.payload.params.src.src_x),
                                current_src_y .eq(cmd_fifo.o.payload.params.src.src_y),
                                current_height.eq(cmd_fifo.o.payload.params.src.height),
                                current_width .eq(cmd_fifo.o.payload.params.src.width),
                            ]
                            # Stay in 'IDLE' state on source changes.
                        with m.Case(self.BlitCmd.Kind.BLIT):
                            m.d.sync += [
                                plot_x.eq(0),
                                plot_y.eq(0),
                                current_dst_x.eq(cmd_fifo.o.payload.params.blit.dst_x),
                                current_dst_y.eq(cmd_fifo.o.payload.params.blit.dst_y),
                                current_pixel.eq(cmd_fifo.o.payload.params.blit.pixel),
                            ]
                            m.next = 'READ_SPRITE_DATA'

            with m.State('READ_SPRITE_DATA'):
                m.next = 'CHECK_PIXEL'

            with m.State('CHECK_PIXEL'):

                # Check if current pixel should be drawn (unpack `embedded-graphics` MSB-first bit ordering)
                # TODO: can we simplify this logic against the rust hal implementation a bit?

                current_pixel_bit = Signal()
                byte_in_word = Signal(3)
                bit_in_byte = Signal(3)
                corrected_bit_index = Signal(5)
                m.d.comb += [
                    byte_in_word.eq(pixel_bit_index >> 3),
                    bit_in_byte.eq(pixel_bit_index[0:3]),
                    corrected_bit_index.eq((byte_in_word << 3) | (7 - bit_in_byte)),
                    current_pixel_bit.eq(sprite_r_port.data.bit_select(corrected_bit_index, 1)),
                ]

                with m.If(current_pixel_bit):
                    # Pixel should be drawn - send request to plotting backend and wait
                    # until it is accepted.
                    m.d.comb += [
                        self.plot_req.valid.eq(1),
                        self.plot_req.payload.x.eq(current_dst_x + plot_x),
                        self.plot_req.payload.y.eq(current_dst_y + plot_y),
                        self.plot_req.payload.pixel.eq(current_pixel),
                        self.plot_req.payload.blend.eq(BlendMode.REPLACE),
                        self.plot_req.payload.offset.eq(OffsetMode.ABSOLUTE),
                    ]
                    with m.If(self.plot_req.ready):
                        m.next = 'NEXT_PIXEL'
                with m.Else():
                    # Pixel is transparent - skip to next
                    m.next = 'NEXT_PIXEL'

            with m.State('NEXT_PIXEL'):

                with m.If(plot_x == (current_width - 1)):
                    m.d.sync += plot_x.eq(0)
                    with m.If(plot_y == (current_height - 1)):
                        m.next = 'IDLE'
                    with m.Else():
                        m.d.sync += plot_y.eq(plot_y + 1)
                        m.next = 'READ_SPRITE_DATA'
                with m.Else():
                    m.d.sync += plot_x.eq(plot_x + 1)
                    m.next = 'READ_SPRITE_DATA'

        return m
