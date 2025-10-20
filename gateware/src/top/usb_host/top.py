# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Extremely bare-bones gateware-only USB MIDI host. EXPERIMENTAL.

***WARN*** because there is no SoC to do USB CC negotiation, this demo
hardwires the VBUS output to ON !!!

At the moment, all the MIDI traffic is routed to CV outputs according
to the existing example (see docstring) in ``tiliqua.midi:MonoMidiCV``.
"""

import sys

from amaranth import *
from amaranth.build import *
from amaranth.lib.cdc import FFSynchronizer

from tiliqua import midi
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.periph import eurorack_pmod
from tiliqua.platform import RebootProvider
from tiliqua.usb_host import *
from vendor.ila import AsyncSerialILA


class USB2HostTest(Elaboratable):

    bitstream_help = BitstreamHelp(
        brief="USB host MIDI to CV conversion (EXPERIMENT).",
        io_left=midi.MonoMidiCV.bitstream_help.io_left,
        io_right=['', 'USB MIDI host', '', '', '', '']
    )

    def __init__(self, clock_settings):
        self.clock_settings = clock_settings
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        m.submodules.car = car = platform.clock_domain_generator(self.clock_settings)
        m.submodules.reboot = reboot = RebootProvider(car.settings.frequencies.sync)
        m.submodules.btn = FFSynchronizer(
                platform.request("encoder").s.i, reboot.button)

        ulpi = platform.request(platform.default_usb_connection)
        m.submodules.usb = usb = SimpleUSBMIDIHost(
                bus=ulpi,
        )

        m.submodules.midi_decode = midi_decode = midi.MidiDecode(usb=True)
        wiring.connect(m, usb.o_midi_bytes, midi_decode.i)

        m.submodules.pmod0_provider = pmod0_provider = eurorack_pmod.FFCProvider()
        m.submodules.pmod0 = pmod0 = eurorack_pmod.EurorackPmod(
                car.settings.audio_clock)
        wiring.connect(m, pmod0.pins, pmod0_provider.pins)
        m.d.comb += pmod0.codec_mute.eq(reboot.mute)

        m.submodules.midi_cv = self.midi_cv = midi.MonoMidiCV()
        wiring.connect(m, pmod0.o_cal, self.midi_cv.i)
        wiring.connect(m, self.midi_cv.o, pmod0.i_cal)
        wiring.connect(m, midi_decode.o, self.midi_cv.i_midi)

        # XXX: this demo enables VBUS output
        m.d.comb += platform.request("usb_vbus_en").o.eq(1)

        if platform.ila:
            test_signal = Signal(16, reset=0xFEED)
            ila_signals = [
                test_signal,
                usb.translator.tx_valid,
                usb.translator.tx_data,
                usb.translator.tx_ready,
                usb.translator.rx_valid,
                usb.translator.rx_data,
                usb.translator.rx_active,
                usb.translator.busy,
                usb.receiver.packet_complete,
                usb.receiver.crc_mismatch,
                usb.receiver.stream.payload,
                usb.receiver.stream.next,
                usb.o_midi_bytes.valid,
                usb.o_midi_bytes.payload,
                midi_decode.o.payload.as_value(),
                midi_decode.o.valid,
                usb.midi_fifo.r_level,
                usb.handshake_detector.detected.ack,
                usb.handshake_detector.detected.nak,
                usb.handshake_detector.detected.stall,
                usb.handshake_detector.detected.nyet,
            ]

            self.ila = AsyncSerialILA(signals=ila_signals,
                                      sample_depth=8192, divisor=521,
                                      domain='usb', sample_rate=60e6) # ~115200 baud on USB clock
            m.submodules += self.ila

            m.d.comb += [
                self.ila.trigger.eq(midi_decode.o.payload.midi_type == midi.MessageType.NOTE_ON),
                platform.request("uart").tx.o.eq(self.ila.tx),
            ]

        return m

if __name__ == "__main__":
    top_level_cli(
        USB2HostTest,
        video_core=False,
        ila_supported=True,
    )
