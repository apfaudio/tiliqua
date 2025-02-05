# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD--3-Clause

from amaranth              import *
from amaranth.lib.fifo     import AsyncFIFO
from amaranth.lib          import wiring, data, stream
from amaranth.lib.wiring   import In, Out
from tiliqua.eurorack_pmod import I2STDM, ASQ

class AudioToChannels(wiring.Component):

    """
    Domain crossing logic to move samples from `eurorack-pmod` logic in the audio domain
    to `channels_to_usb_stream` and `usb_stream_to_channels` logic in the USB domain.
    """

    # streams for hooking up to audio source / sink, sent / recieved over USB.
    i:    In(stream.Signature(data.ArrayLayout(ASQ, 4)))
    o:   Out(stream.Signature(data.ArrayLayout(ASQ, 4)))

    # TODO: legacy: internal USB streams should be exposed as an ordinary wiring.Component.

    def __init__(self, to_usb_stream, from_usb_stream):
        self.to_usb = to_usb_stream
        self.from_usb = from_usb_stream
        self.dac_fifo_level = Signal(16)
        super().__init__()

    def elaborate(self, platform) -> Module:

        m = Module()

        # Sample widths
        SW      = I2STDM.S_WIDTH            # Sample width used in underlying I2S driver.
        SW_USB  = self.to_usb.payload.width # Sample width used for USB transfers.
        N_ZFILL = SW_USB - SW               # Zero padding if SW < SW_USB

        assert(N_ZFILL >= 0)

        #
        # INPUT SIDE
        # eurorack-pmod calibrated INPUT samples -> USB Channel stream -> HOST
        #

        m.submodules.adc_fifo = adc_fifo = AsyncFIFO(width=SW*4, depth=64, w_domain="sync", r_domain="usb")

        # (sync domain) on every sample strobe, latch and write all channels concatenated into one entry
        # of adc_fifo.
        wiring.connect(m, wiring.flipped(self.i), adc_fifo.w_stream);

        # (usb domain) unpack samples from the adc_fifo (one big concatenated
        # entry with samples for all channels once per sample strobe) and feed them
        # into ChannelsToUSBStream with one entry per channel, i.e 1 -> 4 entries
        # per sample strobe in the audio domain.

        # Storage for samples in the USB domain as we send them to the channel stream.
        adc_latched = Signal(SW*4)

        with m.FSM(domain="usb") as fsm:

            with m.State('WAIT'):
                m.d.usb += self.to_usb.valid.eq(0),
                with m.If(adc_fifo.r_rdy):
                    m.d.usb += adc_fifo.r_en.eq(1)
                    m.next = 'LATCH'

            with m.State('LATCH'):
                m.d.usb += [
                    adc_fifo.r_en.eq(0),
                    adc_latched.eq(adc_fifo.r_data)
                ]
                m.next = 'CH0'

            def generate_channel_states(channel, next_state_name):
                with m.State(f'CH{channel}'):
                    m.d.usb += [
                        # FIXME: currently filling bottom bits with zeroes for SW bit -> SW_USB bit
                        # sample conversion. Better to just switch native rate of I2S driver.
                        self.to_usb.payload.eq(
                            Cat(Const(0, N_ZFILL), adc_latched[channel*SW:(channel+1)*SW])),
                        self.to_usb.channel_nr.eq(channel),
                        self.to_usb.valid.eq(1),
                    ]
                    m.next = f'CH{channel}-SEND'
                with m.State(f'CH{channel}-SEND'):
                    with m.If(self.to_usb.ready):
                        m.d.usb += self.to_usb.valid.eq(0)
                        m.next = next_state_name

            generate_channel_states(0, 'CH1')
            generate_channel_states(1, 'CH2')
            generate_channel_states(2, 'CH3')
            generate_channel_states(3, 'WAIT')

        #
        # OUTPUT SIDE
        # HOST -> USB Channel stream -> eurorack-pmod calibrated OUTPUT samples.
        #

        m.submodules.dac_fifo = dac_fifo = AsyncFIFO(width=SW*4, depth=64, w_domain="usb", r_domain="sync")
        wiring.connect(m, dac_fifo.r_stream, wiring.flipped(self.o));

        m.d.usb += dac_fifo.w_en.eq(0)
        for n in range(4):
            with m.If((self.from_usb.channel_nr == n) & self.from_usb.valid):
                m.d.usb += dac_fifo.w_data[n*SW:(n+1)*SW].eq(self.from_usb.payload[N_ZFILL:])
                # Write all channels on every incoming zero'th channel
                # This should work even if < 4 channels are used.
                if n == 0:
                    m.d.usb += dac_fifo.w_en.eq(1)

        m.d.comb += [
            self.dac_fifo_level.eq(m.submodules.dac_fifo.r_level),
            self.from_usb.ready.eq(dac_fifo.w_rdy),
        ]

        return m
