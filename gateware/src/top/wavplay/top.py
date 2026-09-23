# Copyright (c) 2025 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""
Play a WAV file straight out of PSRAM, with no CPU.

The bitstream uses a ``UsbLoad`` region in its manifest, instructing the
bootloader to copy ``m.wav`` off a USB thumbdrive into a fixed region of
PSRAM, before the FPGA is reconfigured with this bitstream. This lets us
employ all the complex USB Host logic having existed in the bootloader,
without actually consuming any FPGA resources for it in our bitstream here.

``WavLoop`` is deliberately dumb gateware which will walk that PSRAM window
with a wishbone initiator, emitting audio samples. It does NOT check the .wav
sample rate or channel count. So, be careful to only use a 48kHz 16-bit PCM
mono .wav file! (or 192kHz if you synth with --fs-192kHz).

Copy ``m.wav`` to the root of a FAT32 thumbdrive, plug it into the USB
port, then boot this bitstream from the bootloader.
"""

import os

from amaranth import *
from amaranth.build import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.cdc import FFSynchronizer
from amaranth.lib.wiring import In, Out
from amaranth_soc import wishbone

from tiliqua.build import sim
from tiliqua.build.cli import top_level_cli
from tiliqua.build.types import BitstreamHelp
from tiliqua.dsp import ASQ
from tiliqua.periph import eurorack_pmod, psram
from tiliqua.platform import RebootProvider

# file the bootloader looks for in the thumbdrive's root directory.
# check the bootloader serial logs for errors if you have issues.
WAV_FILENAME = "m.wav"

# PSRAM base the bootloader drops the WAV file into (bytes not words).
#
# Keep clear of low PSRAM and high PSRAM, which are both used by the bootloader
# for framebuffer dma and manifest storage (respectively). TODO: the bootloader
# should really stop touching those PSRAM regions before it loads other bitstreams...
WAV_PSRAM_DST = 0x400000

# Max .wav file samples. WARN: if you drop a file longer than this, the bootloader
# will fail out! The actual length is read from the file.
WAV_SAMPLES = 0x100000  # ~21s @ 48kHz


class WavLoop(wiring.Component):

    o: Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    bus: Out(wishbone.Signature(addr_width=22,
                                data_width=32,
                                granularity=8,
                                features={'bte', 'cti'}))

    def __init__(self, base, n_samples):
        self.base = base
        self.n_samples = n_samples
        super().__init__()

    def elaborate(self, platform):
        m = Module()

        # .wav header ref:
        # https://ccrma.stanford.edu/courses/422-winter-2014/projects/WaveFormat/
        DATA_SZ_WORD = 10 # byte 40 (NumSamples * NumChannels * BitsPerSample / 8
        DATA_WORD    = 11 # byte 44

        max_words = self.n_samples // 2 - DATA_WORD

        word = Signal(range(self.n_samples // 2), init=DATA_SZ_WORD)
        loop_words = Signal(range(max_words + 1))
        half = Signal()  # which 16-bit half of `dat` goes next
        dat  = Signal(32)
        sz_words = Signal(32)
        m.d.comb += sz_words.eq(self.bus.dat_r >> 2)

        with m.FSM():

            with m.State('READ'):
                # only issuing classing reads - bursts would be much more bandwidth
                # efficient, but at 48kHz, this is not a concern :)
                m.d.comb += [
                    self.bus.stb.eq(1),
                    self.bus.cyc.eq(1),
                    self.bus.we .eq(0),
                    self.bus.sel.eq(-1),
                    self.bus.adr.eq((self.base >> 2) + word),
                ]
                with m.If(self.bus.ack):
                    with m.If(loop_words == 0):
                        # header read
                        m.d.sync += [
                            loop_words.eq(self.bus.dat_r >> 2),
                            word.eq(DATA_WORD)
                        ]
                    with m.Else():
                        # audio sample read
                        m.d.sync += dat.eq(self.bus.dat_r)
                        m.next = 'EMIT'

            with m.State('EMIT'):
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload[0].as_value().eq(dat.word_select(half, 16)),
                ]
                with m.If(self.o.ready):
                    m.d.sync += half.eq(~half)
                    with m.If(half):
                        with m.If(word == DATA_WORD + loop_words - 1):
                            m.d.sync += word.eq(DATA_WORD)
                        with m.Else():
                            m.d.sync += word.eq(word + 1)
                        m.next = 'READ'

        return m


class WavPlayerTop(Elaboratable):

    bitstream_help = BitstreamHelp(
        brief="Loop mono WAV file from USB drive",
        io_left=['', '', '', '', 'mono out', '', '', ''],
        io_right=['', WAV_FILENAME, '', '', '', '']
    )

    def __init__(self, *, clock_settings):
        self.clock_settings = clock_settings
        self.pmod0 = eurorack_pmod.EurorackPmod(clock_settings.audio_clock)
        # well, actually the psram is 32MiB on SC R3, but 16MiB is backwards
        # compat with SC R2 - this should come from platform.py...
        self.psram_periph = psram.Peripheral(size=16*1024*1024)
        self.wavloop = WavLoop(base=WAV_PSRAM_DST, n_samples=WAV_SAMPLES)

    def elaborate(self, platform):
        m = Module()

        m.submodules.pmod0 = pmod0 = self.pmod0

        m.submodules.car = platform.clock_domain_generator(self.clock_settings)
        m.submodules.provider = provider = eurorack_pmod.FFCProvider()
        wiring.connect(m, pmod0.pins, provider.pins)
        m.submodules.reboot = reboot = RebootProvider(
                self.clock_settings.frequencies.sync)
        m.submodules.btn = FFSynchronizer(
                platform.request("encoder").s.i, reboot.button)
        m.d.comb += pmod0.codec_mute.eq(reboot.mute)

        m.submodules.wavloop = self.wavloop
        m.submodules.psram_periph = self.psram_periph

        wiring.connect(m, self.wavloop.bus, self.psram_periph.bus)
        wiring.connect(m, self.wavloop.o, pmod0.i_cal)

        # audio inputs unused, but must be drained
        m.d.comb += pmod0.o_cal.ready.eq(1)

        return m


if __name__ == "__main__":
    this_path = os.path.dirname(os.path.realpath(__file__))
    top_level_cli(
        WavPlayerTop,
        video_core=False,
        path=this_path,
        archiver_callback=lambda archiver: archiver.with_usb_load(
            filename=WAV_FILENAME,
            psram_dst=WAV_PSRAM_DST,
            max_size=WAV_SAMPLES*2,
        ),
    )
