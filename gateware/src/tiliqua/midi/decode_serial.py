# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Serial MIDI decoding."""

from amaranth import *
from amaranth.lib import stream, wiring
from amaranth.lib.fifo import SyncFIFOBuffered
from amaranth.lib.wiring import In, Out
from amaranth_stdio.serial import AsyncSerialRX

from ..dsp.stream_util import SyncFIFOBuffered as StreamFIFO
from .types import *


class SerialRx(wiring.Component):

    """Extract a stream of raw MIDI bytes from a serial port."""

    MIDI_BAUD_RATE = 31250

    o: Out(stream.Signature(unsigned(8)))

    def __init__(self, *, system_clk_hz, pins, rx_depth=64):
        self.phy = AsyncSerialRX(
            divisor=int(system_clk_hz // self.MIDI_BAUD_RATE),
            pins=pins)
        self.rx_fifo = SyncFIFOBuffered(
            width=self.phy.data.width, depth=rx_depth)
        super().__init__()

    def elaborate(self, platform):
        m = Module()
        m.submodules._phy = self.phy
        m.submodules._rx_fifo = self.rx_fifo
        m.d.comb += [
            self.rx_fifo.w_data.eq(self.phy.data),
            self.rx_fifo.w_en.eq(self.phy.rdy),
            self.phy.ack.eq(self.rx_fifo.w_rdy),
        ]
        wiring.connect(m, self.rx_fifo.r_stream, wiring.flipped(self.o))
        return m

class MidiRTFilter(wiring.Component):

    """
    Extract System Real-Time messages (0xF8-0xFF) from a byte stream.

    RT messages can appear mid-message, at any time. This component drops them
    so later stages don't need to handle RT messages.

    Extracted RT messages may be forwarded on a sideband stream through
    :py:`o_rt` if desired (backpressure on ``o_rt`` is ignored!)
    """

    def __init__(self, forward=False):
        self.forward = forward
        sig = {
            "i": In(stream.Signature(unsigned(8))),
            "o": Out(stream.Signature(unsigned(8))),
        }
        if forward:
            sig["o_rt"] = Out(stream.Signature(Status.RT))
        super().__init__(sig)

    def elaborate(self, platform):
        m = Module()

        i_status = Status(self.i.payload)

        is_realtime = Signal()
        m.d.comb += is_realtime.eq(
            i_status.is_status &
            (i_status.kind == Status.Kind.SYSEX) &
            i_status.nibble.sys.is_rt)

        m.d.comb += [
            self.o.payload.eq(self.i.payload),
            self.o.valid.eq(self.i.valid & ~is_realtime),
            self.i.ready.eq(self.o.ready | is_realtime),
        ]

        if self.forward:
            m.submodules.rt_fifo = rt_fifo = StreamFIFO(shape=Status.RT, depth=4)
            m.d.comb += [
                rt_fifo.i.payload.eq(i_status.nibble.sys.sub.rt),
                rt_fifo.i.valid.eq(self.i.valid & is_realtime),
            ]
            wiring.connect(m, rt_fifo.o, wiring.flipped(self.o_rt))

        return m

class MidiSysexFilter(wiring.Component):

    """
    Drop SysEx messages (0xF0 .. 0xF7) from a MIDI byte stream.

    Expects real-time messages to already be dropped by
    :py:`MidiRTFilter`. All sysex bytes are consumed and discarded.

    TODO: add a sideband stream for sysex messages.
    """

    i: In(stream.Signature(unsigned(8)))
    o: Out(stream.Signature(unsigned(8)))

    def elaborate(self, platform):
        m = Module()

        i_status = Status(self.i.payload)

        is_sysex_start = Signal()
        m.d.comb += is_sysex_start.eq(
            i_status.is_status &
            (i_status.kind == Status.Kind.SYSEX) &
            (i_status.nibble.sys.sub.com == Status.SysCom.SYSEX))

        with m.FSM():
            with m.State('PASS'):
                with m.If(self.i.valid & is_sysex_start):
                    # Enter sysex mode
                    m.d.comb += self.i.ready.eq(1)
                    m.next = 'SYSEX'
                with m.Else():
                    # Pass through
                    m.d.comb += [
                        self.o.payload.eq(self.i.payload),
                        self.o.valid.eq(self.i.valid),
                        self.i.ready.eq(self.o.ready),
                    ]

            with m.State('SYSEX'):
                # Drain until any status byte terminates.
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid & i_status.is_status):
                    m.next = 'PASS'

        return m

class MidiDecodeSerial(wiring.Component):

    """
    Parse serial byte stream into a structured :py:`MidiMessage` stream.

    Set :py:`forward_rt` to expose real-time messages on :py:`o_rt`. Warn:
    backpressure on ``o_rt`` is ignored!
    """

    def __init__(self, forward_rt=False):
        self.forward_rt = forward_rt
        sig = {
            "i": In(stream.Signature(unsigned(8))),
            "o": Out(stream.Signature(MidiMessage)),
        }
        if forward_rt:
            sig["o_rt"] = Out(stream.Signature(Status.RT))
        super().__init__(sig)

    def elaborate(self, platform):
        m = Module()

        # Step 1: extract/drop (and maybe forward) real-time messages
        m.submodules.rt_filter = rt_filter = MidiRTFilter(
            forward=self.forward_rt)
        wiring.connect(m, wiring.flipped(self.i), rt_filter.i)
        if self.forward_rt:
            wiring.connect(m, rt_filter.o_rt, wiring.flipped(self.o_rt))

        # Step 2: drop sysex messages
        m.submodules.sysex_filter = sysex_filter = MidiSysexFilter()
        wiring.connect(m, rt_filter.o, sysex_filter.i)

        # Step 3: parse remaining messages (normal channel events)

        # Filtered: no RT or Sysex messages
        filtered = sysex_filter.o

        timeout = Signal(24)
        timeout_cycles = 60000 # 1msec
        m.d.sync += timeout.eq(timeout-1)

        i_status = Status(filtered.payload)

        # Running status: reuse last channel message status byte
        # when a data byte arrives where a status byte is expected.
        running_status = Signal(Status)
        running_status_valid = Signal()

        with m.FSM() as fsm:
            with m.State('IDLE'):
                m.d.comb += filtered.ready.eq(1)
                with m.If(filtered.valid & i_status.is_status):
                    with m.If(i_status.kind == Status.Kind.SYSEX):
                        # System Common: clear running status, skip data bytes
                        m.d.sync += running_status_valid.eq(0)
                        with m.Switch(i_status.nibble.sys.sub.com):
                            with m.Case(Status.SysCom.SONG_POSITION):
                                m.next = 'SKIP-2'
                            with m.Case(Status.SysCom.MTC_QF,
                                        Status.SysCom.SONG_SELECT):
                                m.next = 'SKIP-1'
                            with m.Default():
                                pass
                    with m.Else():
                        # Channel message status byte
                        m.d.sync += [
                            running_status.eq(i_status),
                            running_status_valid.eq(1),
                            timeout.eq(timeout_cycles),
                            self.o.payload.status.eq(i_status),
                        ]
                        m.next = 'READ0'
                with m.Elif(filtered.valid & ~i_status.is_status & running_status_valid):
                    # Running status: data byte reuses last status byte.
                    # Already have the first data byte, skip READ0.
                    m.d.sync += [
                        timeout.eq(timeout_cycles),
                        self.o.payload.status.eq(running_status),
                        self.o.payload.midi_payload.raw.byte0.eq(filtered.payload),
                    ]
                    with m.Switch(running_status.kind):
                        with m.Case(Status.Kind.CHANNEL_PRESSURE,
                                    Status.Kind.PROGRAM_CHANGE):
                            m.next = 'WAIT-READY'
                        with m.Default():
                            m.next = 'READ1'

            with m.State('SKIP-2'):
                m.d.comb += filtered.ready.eq(1)
                with m.If(filtered.valid):
                    m.next = 'SKIP-1'
            with m.State('SKIP-1'):
                m.d.comb += filtered.ready.eq(1)
                with m.If(filtered.valid):
                    m.next = 'IDLE'

            with m.State('READ0'):
                m.d.comb += filtered.ready.eq(1)
                with m.If(timeout == 0):
                    m.next = 'IDLE'
                with m.Elif(filtered.valid):
                    m.d.sync += self.o.payload.midi_payload.raw.byte0.eq(filtered.payload)
                    with m.Switch(self.o.payload.status.kind):
                        with m.Case(Status.Kind.CHANNEL_PRESSURE,
                                    Status.Kind.PROGRAM_CHANGE):
                            m.next = 'WAIT-READY'
                        with m.Default():
                            m.next = 'READ1'
            with m.State('READ1'):
                m.d.comb += filtered.ready.eq(1)
                with m.If(timeout == 0):
                    m.next = 'IDLE'
                with m.Elif(filtered.valid):
                    m.d.sync += self.o.payload.midi_payload.raw.byte1.eq(filtered.payload)
                    m.next = 'WAIT-READY'
            with m.State('WAIT-READY'):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.next = 'IDLE'

        return m
