# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""MIDI data types and message structures."""

from amaranth import unsigned
from amaranth.lib import data, enum

class Status(data.Struct):
    """Layout of a MIDI Status byte."""

    class Kind(enum.Enum, shape=unsigned(3)):
        NOTE_OFF         = 0
        NOTE_ON          = 1
        POLY_PRESSURE    = 2
        CONTROL_CHANGE   = 3
        PROGRAM_CHANGE   = 4
        CHANNEL_PRESSURE = 5
        PITCH_BEND       = 6
        SYSEX            = 7

    # If 'Kind == SYSEX && nibble.sys.is_rt == True', we have a real-time message:

    class RT(enum.Enum, shape=unsigned(3)):
        CLOCK            = 0
        START            = 2
        CONTINUE         = 3
        STOP             = 4
        ACTIVE_SENSING   = 6
        RESET            = 7

    # If 'Kind == SYSEX && nibble.sys.is_rt == False', we have a 'System Common' message:

    class SysCom(enum.Enum, shape=unsigned(3)):
        SYSEX            = 0
        MTC_QF           = 1
        SONG_POSITION    = 2
        SONG_SELECT      = 3
        TUNE_REQUEST     = 6
        EOX              = 7

    # All of which are organized as follows --

    nibble: data.UnionLayout({
        "channel": unsigned(4),
        "sys": data.StructLayout({
            "sub": data.UnionLayout({
                "com": SysCom,
                "rt":  RT,
            }),
            "is_rt": unsigned(1),
        }),
    })
    kind:      Kind
    is_status: unsigned(1)

class MidiMessage(data.Struct):
    """Layout of all MIDI messages that are not Sysex/RT messages."""

    status:       Status
    midi_payload: data.UnionLayout({
        "raw": data.StructLayout({
            "byte0": unsigned(8),
            "byte1": unsigned(8),
        }),
        "note_off": data.StructLayout({
            "note": unsigned(8),
            "velocity": unsigned(8),
        }),
        "note_on": data.StructLayout({
            "note": unsigned(8),
            "velocity": unsigned(8),
        }),
        "poly_pressure": data.StructLayout({
            "note": unsigned(8),
            "pressure": unsigned(8),
        }),
        "control_change": data.StructLayout({
            "controller_number": unsigned(8),
            "data": unsigned(8),
        }),
        "program_change": data.StructLayout({
            "program_number": unsigned(8),
            "_unused": unsigned(8),
        }),
        "channel_pressure": data.StructLayout({
            "pressure": unsigned(8),
            "_unused": unsigned(8),
        }),
        "pitch_bend": data.StructLayout({
            "lsb": unsigned(8),
            "msb": unsigned(8),
        }),
    })
