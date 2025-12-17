# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

import unittest

from amaranth import *
from amaranth.sim import *
from parameterized import parameterized

from tiliqua import midi
from tiliqua.test import stream


class MidiTests(unittest.TestCase):

    @parameterized.expand([
        ["trs", False], # 3-byte
        ["usb", True],  # 4-byte
    ])
    def test_midi_decode(self, name, is_usb):

        dut = midi.MidiDecode(usb=is_usb)

        async def testbench(ctx):

            if is_usb:
                await stream.put(ctx, dut.i, {'first': 1, 'last': 0, 'data': 0x00}) # jack (ignored)
                await stream.put(ctx, dut.i, {'first': 0, 'last': 0, 'data': 0x92})
                await stream.put(ctx, dut.i, {'first': 0, 'last': 0, 'data': 0x48})
                await stream.put(ctx, dut.i, {'first': 0, 'last': 1, 'data': 0x96})
            else:
                await stream.put(ctx, dut.i, 0x92)
                await stream.put(ctx, dut.i, 0x48)
                await stream.put(ctx, dut.i, 0x96)

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.midi_type, midi.MessageType.NOTE_ON)
            self.assertEqual(p.midi_channel, 2)
            self.assertEqual(p.midi_payload.note_on.note, 0x48)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x96)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_midi_decode_{name}.vcd", "w")):
            sim.run()

    def test_midi_voice_tracker(self):

        dut = midi.MidiVoiceTracker()

        note_range = list(range(40, 48))

        async def stimulus_notes(ctx):
            """Send some MIDI NOTE_ON events."""
            for note in note_range:
                await stream.put(ctx, dut.i, {
                    'midi_type': midi.MessageType.NOTE_ON,
                    'midi_channel': 1,
                    'midi_payload': {
                        'note_on': {
                            'note': note,
                            'velocity': 0x60
                        }
                    }
                })

            await ctx.tick().repeat(50)

            for note in note_range:
                await stream.put(ctx, dut.i, {
                    'midi_type': midi.MessageType.NOTE_OFF,
                    'midi_channel': 1,
                    'midi_payload': {
                        'note_off': {
                            'note': note,
                            'velocity': 0x30
                        }
                    }
                })

        async def testbench(ctx):
            """Check that the NOTE_ON / OFF events correspond to voice slots."""
            for ticks in range(400):
                for n in range(dut.max_voices):
                    note_in_slot = ctx.get(dut.o[n].note)
                    vel_in_slot  = ctx.get(dut.o[n].velocity)
                    gate_in_slot = ctx.get(dut.o[n].gate)
                    print(f"{ticks} slot{n}: note={note_in_slot} vel={vel_in_slot} gate={gate_in_slot}")
                    if n < len(note_range):
                        if ticks > 180 and ticks < 200:
                            # Verify NOTE_ON events written to voice slots.
                            self.assertEqual(note_in_slot, note_range[n])
                            self.assertEqual(vel_in_slot,  0x60)
                            self.assertEqual(gate_in_slot, 1)
                        if ticks > 380:
                            # Verify NOTE_OFF events removed from voice slots.
                            self.assertEqual(note_in_slot, note_range[n])
                            self.assertEqual(gate_in_slot, 0)
                            if dut.zero_velocity_gate:
                                self.assertEqual(vel_in_slot,  0x0)
                            else:
                                self.assertEqual(vel_in_slot,  0x30)
                await ctx.tick()

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_notes)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_midi_voice_tracker.vcd", "w")):
            sim.run()
