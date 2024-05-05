# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD--3-Clause

import os

from amaranth              import *
from amaranth.build        import *

from amaranth.lib.fifo     import AsyncFIFO

from amaranth_future       import stream

from tiliqua.tiliqua_platform import TiliquaPlatform
from tiliqua.eurorack_pmod import EurorackPmod

class AudioStream(Elaboratable):

    """
    Domain crossing logic to move samples from `eurorack-pmod` logic in the audio domain
    to logic in a different domain using a stream interface.
    """

    def __init__(self, eurorack_pmod, stream_domain="sync", fifo_depth=8):

        self.eurorack_pmod = eurorack_pmod
        self.stream_domain = stream_domain
        self.fifo_depth = fifo_depth

        self.adc_fifo = AsyncFIFO(width=eurorack_pmod.width*4, depth=self.fifo_depth, w_domain="audio", r_domain=self.stream_domain)
        self.dac_fifo = AsyncFIFO(width=eurorack_pmod.width*4, depth=self.fifo_depth, w_domain=self.stream_domain, r_domain="audio")

        self.adc_stream = stream.fifo_r_stream(self.adc_fifo)
        self.dac_stream  = stream.fifo_w_stream(self.dac_fifo)

    def elaborate(self, platform) -> Module:

        m = Module()

        SW = self.eurorack_pmod.width

        m.submodules.adc_fifo = adc_fifo = self.adc_fifo
        m.submodules.dac_fifo = dac_fifo = self.dac_fifo

        eurorack_pmod = self.eurorack_pmod

        # (audio domain) on every sample strobe, latch and write all channels concatenated into one entry
        # of adc_fifo.
        m.d.audio += [
            # FIXME: ignoring rdy in write domain. Should be fine as write domain
            # will always be slower than the read domain, but should be fixed.
            adc_fifo.w_en.eq(eurorack_pmod.fs_strobe),
            adc_fifo.w_data[    :SW*1].eq(eurorack_pmod.sample_i[0]),
            adc_fifo.w_data[SW*1:SW*2].eq(eurorack_pmod.sample_i[1]),
            adc_fifo.w_data[SW*2:SW*3].eq(eurorack_pmod.sample_i[2]),
            adc_fifo.w_data[SW*3:SW*4].eq(eurorack_pmod.sample_i[3]),
        ]

        # (audio domain) once fs_strobe hits, write the next pending sample to eurorack_pmod.
        with m.FSM(domain="audio") as fsm:
            with m.State('READ'):
                with m.If(eurorack_pmod.fs_strobe & dac_fifo.r_rdy):
                    m.d.audio += dac_fifo.r_en.eq(1)
                    m.next = 'SEND'
            with m.State('SEND'):
                m.d.audio += [
                    dac_fifo.r_en.eq(0),
                    eurorack_pmod.sample_o[0].eq(dac_fifo.r_data[    :SW*1]),
                    eurorack_pmod.sample_o[1].eq(dac_fifo.r_data[SW*1:SW*2]),
                    eurorack_pmod.sample_o[2].eq(dac_fifo.r_data[SW*2:SW*3]),
                    eurorack_pmod.sample_o[3].eq(dac_fifo.r_data[SW*3:SW*4]),
                ]
                m.next = 'READ'

        return m

class MirrorTop(Elaboratable):
    """Route audio inputs straight to outputs (in the audio domain)."""

    def elaborate(self, platform):
        m = Module()

        m.submodules.car = platform.clock_domain_generator()

        m.submodules.pmod0 = pmod0 = EurorackPmod(
                pmod_pins=platform.request("audio_ffc"),
                hardware_r33=True)

        m.submodules.audio_stream = audio_stream = AudioStream(pmod0)

        m.d.comb += [
            audio_stream.dac_stream.payload.eq(audio_stream.adc_stream.payload),
            audio_stream.dac_stream.valid.eq(audio_stream.adc_stream.valid),
            audio_stream.adc_stream.ready.eq(audio_stream.dac_stream.ready),
        ]

        return m

def build():
    os.environ["AMARANTH_verbose"] = "1"
    os.environ["AMARANTH_debug_verilog"] = "1"
    TiliquaPlatform().build(MirrorTop())