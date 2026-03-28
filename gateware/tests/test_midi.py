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

        dut = midi.MidiDecodeUSB() if is_usb else midi.MidiDecodeSerial()

        async def testbench(ctx):

            if is_usb:
                await stream.put(ctx, dut.i, {'first': 1, 'last': 0, 'data': 0x09}) # CIN=NOTE_ON
                await stream.put(ctx, dut.i, {'first': 0, 'last': 0, 'data': 0x92})
                await stream.put(ctx, dut.i, {'first': 0, 'last': 0, 'data': 0x48})
                await stream.put(ctx, dut.i, {'first': 0, 'last': 1, 'data': 0x96})
            else:
                await stream.put(ctx, dut.i, 0x92)
                await stream.put(ctx, dut.i, 0x48)
                await stream.put(ctx, dut.i, 0x96)

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.status.nibble.channel, 2)
            self.assertEqual(p.midi_payload.note_on.note, 0x48)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x96)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_midi_decode_{name}.vcd", "w")):
            sim.run()

    def test_midi_decode_rt(self):

        dut = midi.MidiDecodeSerial(forward_rt=True)

        async def testbench(ctx):

            # Test 1: RT CLOCK between status and note
            await stream.put(ctx, dut.i, 0x92)        # NOTE_ON ch2
            await stream.put(ctx, dut.i, 0xF8)        # RT CLOCK
            await stream.put(ctx, dut.i, 0x48)        # note
            await stream.put(ctx, dut.i, 0x96)        # velocity

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.status.nibble.channel, 2)
            self.assertEqual(p.midi_payload.note_on.note, 0x48)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x96)

            rt = await stream.get(ctx, dut.o_rt)
            self.assertEqual(rt, midi.Status.RT.CLOCK)

            # Test 2: RT CLOCK and RT START status / note bytes
            await stream.put(ctx, dut.i, 0x93)        # NOTE_ON ch3
            await stream.put(ctx, dut.i, 0x50)        # note
            await stream.put(ctx, dut.i, 0xFA)        # RT START
            await stream.put(ctx, dut.i, 0xF8)        # RT CLOCK
            await stream.put(ctx, dut.i, 0x7F)        # velocity

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.status.nibble.channel, 3)
            self.assertEqual(p.midi_payload.note_on.note, 0x50)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x7F)

            rt = await stream.get(ctx, dut.o_rt)
            self.assertEqual(rt, midi.Status.RT.START)
            rt = await stream.get(ctx, dut.o_rt)
            self.assertEqual(rt, midi.Status.RT.CLOCK)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_midi_decode_rt.vcd", "w")):
            sim.run()

    def test_midi_decode_running_status(self):

        dut = midi.MidiDecodeSerial()

        async def testbench(ctx):
            await stream.put(ctx, dut.i, 0x92)        # NOTE_ON ch2
            await stream.put(ctx, dut.i, 0x48)        # note
            await stream.put(ctx, dut.i, 0x60)        # velocity

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.midi_payload.note_on.note, 0x48)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x60)

            # no status byte, just data
            await stream.put(ctx, dut.i, 0x4C)        # note
            await stream.put(ctx, dut.i, 0x70)        # velocity

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.status.nibble.channel, 2)
            self.assertEqual(p.midi_payload.note_on.note, 0x4C)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x70)

            # different note, vel
            await stream.put(ctx, dut.i, 0x3A)        # note
            await stream.put(ctx, dut.i, 0x61)        # velocity

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.status.nibble.channel, 2)
            self.assertEqual(p.midi_payload.note_on.note, 0x3A)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x61)

            # Normal status byte again (full msg) on a different channel
            await stream.put(ctx, dut.i, 0x93)        # NOTE_ON ch3
            await stream.put(ctx, dut.i, 0x48)        # note
            await stream.put(ctx, dut.i, 0x60)        # velocity

            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.status.nibble.channel, 3)
            self.assertEqual(p.midi_payload.note_on.note, 0x48)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x60)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_midi_decode_running_status.vcd", "w")):
            sim.run()

    def test_midi_decode_sysex_strip(self):

        dut = midi.MidiDecodeSerial()

        async def testbench(ctx):

            # Sysex: should be silently consumed, not cause backpressure.
            await stream.put(ctx, dut.i, 0xF0)        # sysex start
            await stream.put(ctx, dut.i, 0x7E)        # data
            await stream.put(ctx, dut.i, 0x01)        # data
            await stream.put(ctx, dut.i, 0x23)        # data
            await stream.put(ctx, dut.i, 0xF7)        # sysex end

            # Normal channel message
            await stream.put(ctx, dut.i, 0x93)        # NOTE_ON ch3
            await stream.put(ctx, dut.i, 0x50)        # note
            await stream.put(ctx, dut.i, 0x7F)        # velocity

            # Should only see the channel message
            p = await stream.get(ctx, dut.o)
            self.assertEqual(p.status.kind, midi.Status.Kind.NOTE_ON)
            self.assertEqual(p.status.nibble.channel, 3)
            self.assertEqual(p.midi_payload.note_on.note, 0x50)
            self.assertEqual(p.midi_payload.note_on.velocity, 0x7F)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_midi_decode_sysex_strip.vcd", "w")):
            sim.run()

    def test_midi_voice_tracker(self):

        dut = midi.MidiVoiceTracker()

        note_range = list(range(40, 48))

        async def stimulus_notes(ctx):
            """Send some MIDI NOTE_ON events."""
            for note in note_range:
                await stream.put(ctx, dut.i, {
                    'status': {
                        'kind': midi.Status.Kind.NOTE_ON,
                        'nibble': {'channel': 1},
                    },
                    'midi_payload': {
                        'note_on': {
                            'note': note,
                            'velocity': 0x60
                        }
                    }
                })

            await ctx.tick().repeat(150)

            for note in note_range:
                await stream.put(ctx, dut.i, {
                    'status': {
                        'kind': midi.Status.Kind.NOTE_OFF,
                        'nibble': {'channel': 1},
                    },
                    'midi_payload': {
                        'note_off': {
                            'note': note,
                            'velocity': 0x30
                        }
                    }
                })

        async def testbench(ctx):
            """Check that the NOTE_ON / OFF events correspond to voice slots."""
            for ticks in range(600):
                for n in range(dut.max_voices):
                    note_in_slot = ctx.get(dut.o[n].note)
                    vel_in_slot  = ctx.get(dut.o[n].velocity)
                    gate_in_slot = ctx.get(dut.o[n].gate)
                    print(f"{ticks} slot{n}: note={note_in_slot} vel={vel_in_slot} gate={gate_in_slot}")
                    if n < len(note_range):
                        if ticks > 250 and ticks < 350:
                            # Verify NOTE_ON events written to voice slots.
                            self.assertEqual(note_in_slot, note_range[n])
                            self.assertEqual(vel_in_slot,  0x60)
                            self.assertEqual(gate_in_slot, 1)
                        if ticks > 550:
                            # Verify NOTE_OFF events removed from voice slots.
                            self.assertEqual(note_in_slot, note_range[n])
                            self.assertEqual(gate_in_slot, 0)
                            if dut.zero_velocity_gate:
                                self.assertEqual(vel_in_slot,  0x0)
                            else:
                                self.assertEqual(vel_in_slot,  0x60)
                await ctx.tick()

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_process(stimulus_notes)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_midi_voice_tracker.vcd", "w")):
            sim.run()
