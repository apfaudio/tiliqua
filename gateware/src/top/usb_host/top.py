# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
"""
Extremely bare-bones gateware-only USB MIDI host to CV. EXPERIMENTAL.

***WARN*** because there is no SoC to do USB CC negotiation, this demo
hardwires the VBUS output to ON !!!

At the moment, all the MIDI traffic is routed to CV outputs according
to the existing example (see docstring) in ``tiliqua.midi:MonoMidiCV``.
"""

import sys

from amaranth import *
from amaranth.build import *
from amaranth.lib.cdc import FFSynchronizer
from amaranth.lib import wiring

from tiliqua import midi
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.periph import eurorack_pmod
from tiliqua.platform import RebootProvider
from guh.engines.midi import USBMIDIHost
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
        m.submodules.usb = usb = USBMIDIHost(
                bus=ulpi,
        )

        m.submodules.midi_decode = midi_decode = midi.MidiDecode(usb=True)
        wiring.connect(m, usb.o_midi, midi_decode.i)

        m.submodules.pmod0_provider = pmod0_provider = eurorack_pmod.FFCProvider()
        m.submodules.pmod0 = pmod0 = eurorack_pmod.EurorackPmod(
                car.settings.audio_clock)
        wiring.connect(m, pmod0.pins, pmod0_provider.pins)
        m.d.comb += pmod0.codec_mute.eq(reboot.mute)

        m.submodules.midi_cv = self.midi_cv = midi.MonoMidiCV()
        wiring.connect(m, pmod0.o_cal, self.midi_cv.i)
        wiring.connect(m, self.midi_cv.o, pmod0.i_cal)
        wiring.connect(m, midi_decode.o, self.midi_cv.i_midi)

        # XXX: this demo hardwares VBUS output ON
        m.d.comb += platform.request("usb_vbus_en").o.eq(1)

        return m

if __name__ == "__main__":
    top_level_cli(
        USB2HostTest,
        video_core=False,
    )
