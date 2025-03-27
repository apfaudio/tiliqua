# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Helpers for dealing with MIDI over serial or USB."""

from dataclasses import dataclass

from amaranth              import *
from amaranth.lib.fifo     import SyncFIFOBuffered
from amaranth.lib          import wiring, data, enum, stream
from amaranth.lib.wiring   import In, Out
from amaranth.lib.memory   import Memory

from amaranth_stdio.serial import AsyncSerialRX

from amaranth_future       import fixed
from tiliqua.eurorack_pmod import ASQ # hardware native fixed-point sample type

MIDI_BAUD_RATE = 31250

CC_ALL_NOTES_OFF = 0x7B

class Status(enum.Enum, shape=unsigned(4)):
    # Messages associated with MIDI channels
    NOTE_OFF         = 0x8
    NOTE_ON          = 0x9
    POLY_PRESSURE    = 0xA
    CONTROL_CHANGE   = 0xB
    PROGRAM_CHANGE   = 0xC
    CHANNEL_PRESSURE = 0xD
    PITCH_BEND       = 0xE
    # Messages NOT associated with MIDI channels
    SUBCLASS         = 0xF

class Subclass(enum.Enum, shape=unsigned(4)):
    # System Exclusive
    SYSEX_START      = 0x0
    SYSEX_END        = 0x7
    # System Common
    SONG_POINTER     = 0x2
    SONG_SELECT      = 0x2
    TUNE_REQUEST     = 0x6
    # MIDI Time Code
    QUARTER_FRAME    = 0x1
    # System Realtime
    TIMING_CLOCK     = 0x8
    MEASURE_END      = 0x9
    START            = 0xA
    CONTINUE         = 0xB
    STOP             = 0xC
    ACTIVE_SENSING   = 0xE
    RESET            = 0xF

class MidiMessage(data.Struct):
    status1: data.UnionLayout({
        "channel": unsigned(4),           # for channel specific messages
        "subclass": Subclass        # for SUBCLASS messages
    })
    status0: Status                       # 4-bit MIDI status type
    data1: data.UnionLayout({
        "note":              unsigned(8), # for NOTE_OFF, NOTE_ON, POLY_PRESSURE
        "controller_number": unsigned(8), # for CONTROL_CHANGE
        "program_number":    unsigned(8), # for PROGRAM_CHANGE
        "song_number":       unsigned(8), # for SUBCLASS.SONG_SELECT
        "lsb":               unsigned(8), # for PITCH_BEND, SUBCLASS.SONG_POINTER
        "mfg_id":            unsigned(8), # for SYSEX_START
    })
    data2: data.UnionLayout({
        "velocity":          unsigned(8), # for NOTE_OFF, NOTE_ON
        "pressure":          unsigned(8), # for POLY_PRESSURE
        "cc_data":           unsigned(8), # for CONTROL_CHANGE
        "msb":               unsigned(8), # for PITCH_BEND, SUBCLASS.SONG_POINTER
    })

@dataclass
class StandardMsgLength:

    status: Status
    payload_bytes: int

    @classmethod
    def all(cls):
        return [
            cls(Status.NOTE_OFF, 2),
            cls(Status.NOTE_ON, 2),
            cls(Status.POLY_PRESSURE, 2),
            cls(Status.CONTROL_CHANGE, 2),
            cls(Status.PROGRAM_CHANGE, 1),
            cls(Status.CHANNEL_PRESSURE, 1),
            cls(Status.PITCH_BEND, 2),
        ]

@dataclass
class SubclassMsgLength:

    subclass: Subclass
    payload_bytes: int

    @classmethod
    def all(cls):
        return [
            cls(Subclass.SYSEX_START, 1), # variable, data2 until SYSEX_END
            cls(Subclass.SYSEX_END, 0),
            cls(Subclass.SONG_POINTER, 2),
            cls(Subclass.SONG_SELECT, 1),
            cls(Subclass.TUNE_REQUEST, 0),
            cls(Subclass.QUARTER_FRAME, 1),
            cls(Subclass.TIMING_CLOCK, 0),
            cls(Subclass.MEASURE_END, 1),
            cls(Subclass.START, 0),
            cls(Subclass.CONTINUE, 0),
            cls(Subclass.STOP, 0),
            cls(Subclass.ACTIVE_SENSING, 0),
            cls(Subclass.RESET, 0),
        ]

class SerialRx(wiring.Component):

    """Stream of raw bytes from a serial port at MIDI baud rates."""

    o: Out(stream.Signature(unsigned(8)))

    def __init__(self, *, system_clk_hz, pins, rx_depth=64):

        self.phy = AsyncSerialRX(
            divisor=int(system_clk_hz // MIDI_BAUD_RATE),
            pins=pins)
        self.rx_fifo = SyncFIFOBuffered(
            width=self.phy.data.width, depth=rx_depth)

        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.submodules._phy = self.phy
        m.submodules._rx_fifo = self.rx_fifo

        # serial PHY -> RX FIFO
        m.d.comb += [
            self.rx_fifo.w_data.eq(self.phy.data),
            self.rx_fifo.w_en.eq(self.phy.rdy),
            self.phy.ack.eq(self.rx_fifo.w_rdy),
        ]

        # RX FIFO -> output stream
        wiring.connect(m, self.rx_fifo.r_stream, wiring.flipped(self.o))

        return m

class MidiDecode(wiring.Component):

    """
    Convert raw MIDI bytes into a stream of MIDI messages.

    By default, this core expects 3-byte RS232-style MIDI
    byte streams. If :py:`usb == True`, this core expects
    4-byte USB-style MIDI byte streams (first byte padded).
    """

    i: In(stream.Signature(unsigned(8)))
    o: Out(stream.Signature(MidiMessage))

    def __init__(self, usb=False):
        self.usb = usb
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        # If we're halfway through a message and don't get the rest of it
        # for this timeout, we give up and ignore the message.
        timeout = Signal(24)
        timeout_cycles = 60000 # 1msec
        m.d.sync += timeout.eq(timeout-1)

        # Computed MIDI message payload length.
        remaining_bytes = Signal(2)

        with m.FSM() as fsm:
            with m.State('WAIT-VALID'):
                m.d.comb += self.i.ready.eq(1)
                # all valid command messages have highest bit set
                if self.usb:
                    # 4-byte sequence
                    with m.If(self.i.valid):
                        m.d.sync += timeout.eq(timeout_cycles)
                        m.next = 'READU'
                else:
                    # 3-byte sequence (read status byte straight away)
                    with m.If(self.i.valid & self.i.payload[7]):
                        m.d.sync += timeout.eq(timeout_cycles)
                        m.d.sync += self.o.payload.as_value()[:8].eq(self.i.payload)
                        m.next = 'COMPUTE-LEN'

            if self.usb:
                # Status byte arrives after 1-byte padding on USB bytestreams
                with m.State('READU'):
                    m.d.comb += self.i.ready.eq(1)
                    with m.If(timeout == 0):
                        m.next = 'WAIT-VALID'
                    with m.Elif(self.i.valid):
                        m.d.sync += self.o.payload.as_value()[:8].eq(self.i.payload)
                        m.next = 'COMPUTE-LEN'

            # Compute length of this MIDI message
            with m.State('COMPUTE-LEN'):
                payload_bytes = Signal(2)
                with m.Switch(self.o.payload.status0):
                    for msg in StandardMsgLength.all():
                        with m.Case(msg.status):
                            m.d.comb += payload_bytes.eq(msg.payload_bytes)
                    with m.Case(Status.SUBCLASS):
                        with m.Switch(self.o.payload.status1.subclass):
                            for msg in SubclassMsgLength.all():
                                with m.Case(msg.subclass):
                                    m.d.comb += payload_bytes.eq(msg.payload_bytes)
                m.d.sync += remaining_bytes.eq(payload_bytes)
                with m.If(payload_bytes == 0):
                    m.next = 'WAIT-READY'
                with m.Else():
                    m.next = 'READ0'

            # Read (optional) Data1 byte
            with m.State('READ0'):
                m.d.comb += self.i.ready.eq(1)
                with m.If(timeout == 0):
                    m.next = 'WAIT-VALID'
                with m.Elif(self.i.valid):
                    m.d.sync += self.o.payload.as_value()[8:16].eq(self.i.payload)
                    with m.If(remaining_bytes == 1):
                        m.next = 'WAIT-READY'
                    with m.Else():
                        m.next = 'READ1'

            # Read (optional) Data2 byte
            with m.State('READ1'):
                m.d.comb += self.i.ready.eq(1),
                with m.If(timeout == 0):
                    m.next = 'WAIT-VALID'
                with m.Elif(self.i.valid):
                    m.d.sync += self.o.payload.as_value()[16:24].eq(self.i.payload)
                    m.next = 'WAIT-READY'

            with m.State('WAIT-READY'):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.next = 'WAIT-VALID'
                    # SysEx start/stop is transmitted on self.o, but NOTE the sysex
                    # bytes themselves. TODO expose sysex bytes as a separate stream.
                    with m.If((self.o.payload.status0 == Status.SUBCLASS) &
                              (self.o.payload.status1.subclass == Subclass.SYSEX_START)):
                        m.next = 'SYSEX'

            with m.State('SYSEX'):
                m.d.comb += self.i.ready.eq(1),
                with m.If(self.i.valid):
                    # Consuming bytes until SYSEX_END, report the SYSEX_END and restart the state machine.
                    with m.If(self.i.payload == ((Status.SUBCLASS.value << 4) | Subclass.SYSEX_END.value)):
                        m.d.sync += self.o.payload.as_value()[:8].eq(self.i.payload)
                        m.next = 'WAIT-READY'

        return m

class MidiVoice(data.Struct):
    note:         unsigned(8)
    velocity:     unsigned(8)
    gate:         unsigned(1)
    freq_inc:     ASQ
    velocity_mod: unsigned(8)

class MidiVoiceTracker(wiring.Component):

    """
    Read a stream of MIDI messages. Decode it into :py:`max_voices` independent
    :py:`MidiVoice` registers, one per voice, with voice culling.

    After each :py:`NOTE_ON` event, a voice is selected, its :py:`MidiVoice.note` is set,
    the :py:`MidiVoice.gate` attribute is set to 1, and `freq_inc` (linearized
    frequency used for NCOs) is calculated.

    Pitch bend constantly updates :py:`freq_inc` on all channels. Mod wheel may optionally
    be used to cap velocity outputs on all channels using :py:`velocity_mod`.

    After each :py:`NOTE_OFF` event, :py:`MidiVoice.gate` is set to 0. If :py:`zero_velocity_gate`
    is set, the velocity is also set to 0 (instead of the MIDI release velocity).
    """

    def __init__(self, max_voices=8, velocity_mod=False, zero_velocity_gate=False):
        self.max_voices = max_voices
        self.velocity_mod = velocity_mod
        self.zero_velocity_gate = zero_velocity_gate
        super().__init__({
            "i": In(stream.Signature(MidiMessage)),
            "o": Out(MidiVoice).array(max_voices),
        });

    def elaborate(self, platform):
        m = Module()

        # MIDI note -> linearized frequency LUT memory (exponential converter)

        lut = []
        sample_rate_hz = 48000
        for i in range(128):
            freq = 440 * 2**((i-69)/12.0)
            freq_inc = freq * (1.0 / sample_rate_hz)
            lut.append(fixed.Const(freq_inc, shape=ASQ)._value)
        m.submodules.f_lut_mem = f_lut_mem = Memory(
                shape=signed(ASQ.as_shape().width), depth=len(lut), init=lut)
        f_lut_rport = f_lut_mem.read_port()
        m.d.comb += f_lut_rport.en.eq(1)

        # State captured on each incoming MIDI message

        msg = Signal(MidiMessage)      # last MIDI message
        last_cc1 = Signal(8, init=255) # last cc1 (mod wheel) position
        last_pb = Signal(shape=ASQ)    # last pitch bend position

        # write index for NOTE_ON select + commit
        voice_ix_write = Signal(range(self.max_voices), init=0)

        # voice mask (binary 1 is for an occupied voice slot)
        voice_mask = Signal(self.max_voices)

        # freq / mod / pb update index
        ix_update = Signal(range(self.max_voices))

        # FSM to process incoming MIDI messages one at a time and update
        # internal memories based on these messagse.

        with m.FSM() as fsm:

            with m.State('WAIT-VALID'):
                m.d.comb += self.i.ready.eq(1),
                with m.If(self.i.valid):
                    m.d.sync += msg.eq(self.i.payload)
                    with m.Switch(self.i.payload.status0):
                        with m.Case(Status.NOTE_ON):
                            with m.If(self.i.payload.data2.velocity == 0):
                                # According to the MIDI standard, a device may transmit a
                                # NOTE_ON with velocity=0, and this should be treated exactly
                                # the same as a note OFF.
                                m.next = 'NOTE-OFF'
                            with m.Else():
                                m.d.sync += voice_ix_write.eq(0)
                                m.next = 'NOTE-ON-SELECT'
                        with m.Case(Status.NOTE_OFF):
                            m.next = 'NOTE-OFF'
                        with m.Case(Status.CONTROL_CHANGE):
                            m.next = 'CONTROL-CHANGE'
                        with m.Case(Status.PITCH_BEND):
                            m.next = 'PITCH-BEND'
                        with m.Case(Status.POLY_PRESSURE):
                            m.next = 'POLY-PRESSURE'
                        with m.Default():
                            m.next = 'WAIT-VALID'

            with m.State('NOTE-ON-SELECT'):
                # find an empty note slot to write to
                # warn: need at least 1 clock for freq LUT RAM output to update
                # so best not to commit from the same FSM state.
                with m.If(~voice_mask.bit_select(voice_ix_write, 1)):
                    m.next = 'NOTE-ON-COMMIT'
                with m.Else():
                    m.d.sync += voice_ix_write.eq(voice_ix_write + 1)
                    with m.If(voice_ix_write == self.max_voices - 1):
                        # no free note slots
                        m.next = 'WAIT-VALID'

            with m.State('NOTE-ON-COMMIT'):
                # commit the new note to the found slot
                with m.Switch(voice_ix_write):
                    for n in range(self.max_voices):
                        with m.Case(n):
                            m.d.sync += [
                                voice_mask.bit_select(n, 1).eq(1),
                                self.o[n].note.eq(msg.data1.note),
                                self.o[n].velocity.eq(msg.data2.velocity),
                                self.o[n].gate.eq(1),
                            ]
                            if not self.velocity_mod:
                                m.d.sync += self.o[n].velocity_mod.eq(msg.data2.velocity)
                m.next = 'UPDATE'

            with m.State('NOTE-OFF'):
                # cull any voice that matches the MIDI payload note #
                for n in range(self.max_voices):
                    with m.If(self.o[n].note == msg.data1.note):
                        m.d.sync += [
                            voice_mask.bit_select(n, 1).eq(0),
                            self.o[n].gate.eq(0),
                        ]
                        if self.zero_velocity_gate:
                            m.d.sync += self.o[n].velocity.eq(0)
                        else:
                            m.d.sync += self.o[n].velocity.eq(msg.data2.velocity)
                m.next = 'UPDATE'

            with m.State('POLY-PRESSURE'):
                # update any voice that matches the MIDI payload note #
                # TODO: rather than piggybacking on velocity, this should probably be its own field?
                for n in range(self.max_voices):
                    with m.If((self.o[n].note == msg.data1.note) & self.o[n].gate):
                        m.d.sync += self.o[n].velocity.eq(msg.data2.pressure)
                m.next = 'UPDATE'

            with m.State('CONTROL-CHANGE'):
                with m.If((msg.data1.controller_number == 1) &
                          (msg.data2.cc_data != 0)):
                    m.d.sync += last_cc1.eq(msg.data2.cc_data)
                with m.If(msg.data1.controller_number == CC_ALL_NOTES_OFF):
                    # all stop
                    for n in range(self.max_voices):
                        m.d.sync += self.o[n].gate.eq(0)
                        if self.zero_velocity_gate:
                            m.d.sync += self.o[n].velocity.eq(0)
                m.next = 'UPDATE'

            with m.State('PITCH-BEND'):
                # convert 14-bit pitch bend to 16-bit signed ASQ -1 .. 1
                pb = Signal(signed(16))
                m.d.comb += pb.eq(Cat(msg.data1.lsb,
                                      msg.data2.msb))
                m.d.sync += last_pb.raw().eq(pb-(2*8192))
                m.next = 'UPDATE'

            with m.State('UPDATE'):
                # set LUT not address so we can calculate frequency from it
                with m.Switch(ix_update):
                    for n in range(self.max_voices):
                        with m.Case(n):
                            m.d.comb += f_lut_rport.addr.eq(self.o[n].note),
                m.next = 'UPDATE-FREQ-VEL'

            with m.State('UPDATE-FREQ-VEL'):

                # Update linear frequency and velocity based on note values,
                # pitch bend and (optionally) mod wheel.

                # pitch bend factor
                pb_factor = fixed.Const(0.1225, shape=ASQ)
                pb_scaled = Signal(shape=ASQ)
                # TODO: pipeline this multiply through properly!
                m.d.sync += pb_scaled.eq(pb_factor * last_pb)

                # linearized frequency from LUT * pitch bend
                calculated_freq = Signal(ASQ)
                f_inc_base = Signal(ASQ)
                m.d.comb += [
                    f_inc_base.raw().eq(f_lut_rport.data),
                    calculated_freq.eq(f_inc_base + f_inc_base*pb_scaled),
                ]

                # latch to correct output register
                with m.Switch(ix_update):
                    for n in range(self.max_voices):
                        with m.Case(n):
                            # latch linear frequency + pitch bend
                            m.d.sync += self.o[n].freq_inc.eq(calculated_freq)
                            # optional mod wheel caps `velocity_mod` field.
                            if self.velocity_mod:
                                with m.If(last_cc1 < self.o[n].velocity):
                                    m.d.sync += self.o[n].velocity_mod.eq(last_cc1)
                                with m.Else():
                                    m.d.sync += self.o[n].velocity_mod.eq(self.o[n].velocity)

                # Check if we've updated every slot.
                m.d.sync += ix_update.eq(ix_update + 1)
                with m.If(ix_update == self.max_voices - 1):
                    m.next = 'WAIT-VALID'
                with m.Else():
                    m.next = 'UPDATE'

        return m

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

        with m.If(self.i_midi.valid):
            msg = self.i_midi.payload
            with m.Switch(msg.status0):
                with m.Case(Status.NOTE_ON):
                    m.d.sync += [
                        # Gate output on
                        self.o.payload[0].eq(fixed.Const(0.5, shape=ASQ)),
                        # Set velocity output
                        self.o.payload[2].as_value().eq(
                            msg.midi_payload.note_on.velocity << 8),
                        # Set note index in LUT
                        rport.addr.eq(msg.data1.note),
                    ]
                with m.Case(MessageType.NOTE_OFF):
                    # Zero gate and velocity on NOTE_OFF
                    m.d.sync += [
                        self.o.payload[0].eq(0),
                        self.o.payload[2].eq(0),
                    ]
                with m.Case(MessageType.CONTROL_CHANGE):
                    # mod wheel is CC 1
                    with m.If(msg.data1.controller_number == 1):
                        m.d.sync += [
                            self.o.payload[3].as_value().eq(
                                msg.data2.cc_data << 8),
                        ]

        return m

