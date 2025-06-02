"""
4-channel USB2 audio interface, no video, no SoC.

Enumerates as a 4-in, 4-out 48kHz sound card.
"""

import os

from amaranth                 import *
from amaranth.lib             import cdc, wiring

from tiliqua.cli              import top_level_cli
from tiliqua                  import eurorack_pmod, usb_audio
from tiliqua.tiliqua_platform import RebootProvider
from vendor.ila               import AsyncSerialILA

class USBAudioTop(Elaboratable):

    brief = "USB soundcard, 4in + 4out."

    def __init__(self, clock_settings):
        super().__init__()
        self.clock_settings = clock_settings

    def elaborate(self, platform):
        m = Module()

        m.submodules.car = car = platform.clock_domain_generator(self.clock_settings)
        m.submodules.reboot = reboot = RebootProvider(car.settings.frequencies.sync)
        m.submodules.btn = cdc.FFSynchronizer(
                platform.request("encoder").s.i, reboot.button)

        m.submodules.pmod0_provider = pmod0_provider = eurorack_pmod.FFCProvider()
        m.submodules.pmod0 = pmod0 = eurorack_pmod.EurorackPmod(self.clock_settings.audio_clock)
        wiring.connect(m, pmod0.pins, pmod0_provider.pins)
        m.d.comb += pmod0.codec_mute.eq(reboot.mute)

        m.submodules.usbif = usbif = usb_audio.USB2AudioInterface(
                audio_clock=self.clock_settings.audio_clock, nr_channels=4)

        wiring.connect(m, pmod0.o_cal, usbif.i)
        wiring.connect(m, usbif.o, pmod0.i_cal)

        if platform.ila:

            # TODO: unbitrot ILA flag
            # https://github.com/apfaudio/tiliqua/issues/113

            test_signal = Signal(16, reset=0xFEED)

            pmod_sample_o0 = Signal(16)
            m.d.comb += pmod_sample_o0.eq(pmod0.i_cal.payload[0])

            ila_signals = [
                test_signal,
                pmod_sample_o0,
                pmod0.i_cal.valid,
                usbif.dbg.dac_fifo_level,
                usbif.dbg.adc_fifo_level,
                usbif.dbg.sof_detected,
            ]

            self.ila = AsyncSerialILA(signals=ila_signals,
                                      sample_depth=8192, divisor=521,
                                      domain='usb', sample_rate=60e6) # ~115200 baud on USB clock
            m.submodules += self.ila

            m.d.comb += [
                self.ila.trigger.eq((pmod_sample_o0 > Const(1000)) & pmod0.i_cal.valid),
                platform.request("uart").tx.o.eq(self.ila.tx), # needs FFSync?
            ]


        return m

if __name__ == "__main__":
    top_level_cli(USBAudioTop, video_core=False, ila_supported=True)
