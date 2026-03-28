# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Misc MIDI utilities, e.g. domain crossing from MIDI to audio or sync domains"""

from amaranth import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.memory import Memory
from amaranth.lib.wiring import In, Out

from amaranth_future import fixed

from ..dsp import ASQ, block
from .types import *

from tiliqua.build.types import BitstreamHelp

class MonoMidiCV(wiring.Component):

    """
    Simple monophonic MIDI stream to CV conversion.

    in (midi stream): midi data for conversion
    in (audio): not used
    out0: Gate
    out1: V/oct CV
    out2: Velocity
    out3: Mod Wheel (CC1)
    """

    bitstream_help = BitstreamHelp(
        brief="TRS MIDI to CV conversion.",
        io_left=['','','','','gate', 'V/oct', 'velocity', 'mod wheel'],
        io_right=['', '', '', '', '', 'TRS MIDI in']
    )

    i: In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    # Note: MIDI is valid at a much lower rate than audio streams
    i_midi: In(stream.Signature(MidiMessage))

    def elaborate(self, platform):
        m = Module()

        m.d.comb += [
            # Always forward our audio payload
            self.i.ready.eq(1),
            self.o.valid.eq(1),

            # Always ready for MIDI messages
            self.i_midi.ready.eq(1),
        ]

        # Create a LUT from midi note to voltage (output ASQ).
        lut = []
        for i in range(128):
            volts_per_note = 1.0/12.0
            volts = i*volts_per_note - 5
            # convert volts to audio sample
            x = volts/(2**15/4000)
            lut.append(fixed.Const(x, shape=ASQ)._value)

        # Store it in a memory where the address is the midi note,
        # and the data coming out is directly routed to V/Oct out.
        m.submodules.mem = mem = Memory(
            shape=signed(ASQ.as_shape().width), depth=len(lut), init=lut)
        rport = mem.read_port()
        m.d.comb += [
            rport.en.eq(1),
        ]

        # Route memory straight out to our note payload.
        m.d.sync += self.o.payload[1].as_value().eq(rport.data),

        # Track the most recent NOTE_ON so we can ignore NOTE_OFF for
        # notes that aren't the current one (basic legato behavior).
        current_note = Signal(8)

        with m.If(self.i_midi.valid):
            msg = self.i_midi.payload
            with m.Switch(msg.status.kind):
                with m.Case(Status.Kind.NOTE_ON):
                    with m.If(msg.midi_payload.note_on.velocity == 0):
                        # NOTE_ON with velocity=0 is equivalent to NOTE_OFF.
                        with m.If(msg.midi_payload.note_on.note == current_note):
                            m.d.sync += [
                                self.o.payload[0].eq(0),
                                self.o.payload[2].eq(0),
                            ]
                    with m.Else():
                        m.d.sync += [
                            current_note.eq(msg.midi_payload.note_on.note),
                            # Gate output on
                            self.o.payload[0].eq(fixed.Const(0.5, shape=ASQ)),
                            # Set velocity output
                            self.o.payload[2].as_value().eq(
                                msg.midi_payload.note_on.velocity << 8),
                            # Set note index in LUT
                            rport.addr.eq(msg.midi_payload.note_on.note),
                        ]
                with m.Case(Status.Kind.NOTE_OFF):
                    with m.If(msg.midi_payload.note_off.note == current_note):
                        m.d.sync += [
                            self.o.payload[0].eq(0),
                            self.o.payload[2].eq(0),
                        ]
                with m.Case(Status.Kind.CONTROL_CHANGE):
                    # mod wheel is CC 1
                    with m.If(msg.midi_payload.control_change.controller_number == 1):
                        m.d.sync += [
                            self.o.payload[3].as_value().eq(
                                msg.midi_payload.control_change.data << 8),
                        ]

        return m

class MidiClockDivider(wiring.Component):

    """
    Read a stream of :py:`Status.RT`, create toggles in the ``sync`` domain.

    Divides 24 PPQN MIDI clock by :py:`divisor`, which determines how fast
    ``self.o`` toggles. RT messages for start/stop/continue will start/stop/
    continue the toggling.
    """

    i: In(stream.Signature(Status.RT))
    o: Out(unsigned(1))

    def __init__(self, divisor=24):
        self.divisor = divisor
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        counter = Signal(range(self.divisor))
        running = Signal()

        m.d.comb += [
            self.o.eq(running & (counter < self.divisor // 2)),
            self.i.ready.eq(1),
        ]

        with m.If(self.i.valid):
            with m.Switch(self.i.payload):
                with m.Case(Status.RT.CLOCK):
                    with m.If(counter == self.divisor - 1):
                        m.d.sync += counter.eq(0)
                    with m.Else():
                        m.d.sync += counter.eq(counter + 1)
                with m.Case(Status.RT.START):
                    m.d.sync += [
                        counter.eq(0),
                        running.eq(1),
                    ]
                with m.Case(Status.RT.CONTINUE):
                    m.d.sync += running.eq(1)
                with m.Case(Status.RT.STOP):
                    m.d.sync += running.eq(0)

        return m

class CCFilter(wiring.Component):

    """
    Latch MIDI CC values from a :py:`MidiMessage` stream and emit them as
    a :py:`Block(ASQ)` of length 128 (all CCs) on each :py:`strobe`.

    channel : int or None
        MIDI channel to listen to (0-15). None == all.
    """

    N_CCS = 128

    def __init__(self, channel=None, audio_taper=False):
        self.channel = channel
        self.audio_taper = audio_taper
        super().__init__({
            "strobe": In(1),
            "i": In(stream.Signature(MidiMessage)),
            "o": Out(stream.Signature(block.Block(ASQ))),
        })

    def elaborate(self, platform):
        m = Module()

        # Memory for all 128 CC values.
        m.submodules.mem = mem = Memory(
            shape=fixed.UQ(0, 7), depth=self.N_CCS, init=[])
        wr = mem.write_port()
        rd = mem.read_port()

        # Latch CC values from MIDI stream
        m.d.comb += self.i.ready.eq(1)
        m.d.sync += wr.en.eq(0)
        with m.If(self.i.valid):
            msg = self.i.payload
            channel_match = Signal()
            if self.channel is not None:
                m.d.comb += channel_match.eq(
                    msg.status.nibble.channel == self.channel)
            else:
                m.d.comb += channel_match.eq(1)
            with m.If(channel_match):
                with m.Switch(msg.status.kind):
                    with m.Case(Status.Kind.CONTROL_CHANGE):
                        cc = msg.midi_payload.control_change
                        m.d.sync += [
                            wr.addr.eq(cc.controller_number),
                            wr.data.eq(cc.data),
                            wr.en.eq(1),
                        ]

        # Emit CC snapshot block on every strobe.
        ix = Signal(range(self.N_CCS))
        m.d.comb += [
            rd.en.eq(1),
            rd.addr.eq(ix),
        ]

        # Convert CC UQ(0,7) to ASQ, optionally applying audio taper (x^2).
        sample_out = Signal(ASQ)
        if self.audio_taper:
            m.d.comb += sample_out.eq(rd.data * rd.data)
        else:
            m.d.comb += sample_out.eq(rd.data)

        with m.FSM():
            with m.State('IDLE'):
                with m.If(self.strobe):
                    m.d.sync += ix.eq(0)
                    m.next = 'READ'
            with m.State('READ'):
                # read latency
                m.next = 'EMIT'
            with m.State('EMIT'):
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload.sample.eq(sample_out),
                    self.o.payload.first.eq(ix == 0),
                ]
                with m.If(self.o.ready):
                    with m.If(ix == self.N_CCS - 1):
                        m.next = 'IDLE'
                    with m.Else():
                        m.d.sync += ix.eq(ix + 1)
                        m.next = 'READ'

        return m
