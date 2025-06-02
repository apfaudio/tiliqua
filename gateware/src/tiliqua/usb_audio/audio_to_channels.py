# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD--3-Clause

from amaranth              import *
from amaranth.lib.fifo     import AsyncFIFOBuffered
from amaranth.lib          import wiring, data, stream
from amaranth.lib.wiring   import In, Out
from tiliqua.eurorack_pmod import I2STDM, ASQ

class AudioToChannels(wiring.Component):

    """
    Domain crossing logic to move samples from `eurorack-pmod` logic in the audio domain
    to `channels_to_usb_stream` and `usb_stream_to_channels` logic in the USB domain.
    """

    # TODO: legacy: internal USB streams should be exposed as an ordinary wiring.Component.

    def __init__(self, nr_channels, to_usb_stream, from_usb_stream, fifo_depth):
        self.nr_channels = nr_channels
        self.to_usb = to_usb_stream
        self.from_usb = from_usb_stream
        self.fifo_depth = fifo_depth
        self.dac_fifo_level = Signal(range(fifo_depth+1))
        self.adc_fifo_level = Signal(range(fifo_depth+1))
        super().__init__({
            # streams for hooking up to audio source / sink, sent / recieved over USB.
            "i":  In(stream.Signature(data.ArrayLayout(ASQ, self.nr_channels))),
            "o": Out(stream.Signature(data.ArrayLayout(ASQ, self.nr_channels)))
        })

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

        m.submodules.adc_fifo = adc_fifo = AsyncFIFOBuffered(width=SW*self.nr_channels, depth=self.fifo_depth, w_domain="sync", r_domain="usb")

        # (sync domain) on every sample strobe, latch and write all channels concatenated into one entry
        # of adc_fifo.
        wiring.connect(m, wiring.flipped(self.i), adc_fifo.w_stream);

        # (usb domain) unpack samples from the adc_fifo (one big concatenated
        # entry with samples for all channels once per sample strobe) and feed them
        # into ChannelsToUSBStream with one entry per channel, i.e 1 -> 4 entries
        # per sample strobe in the audio domain.

        # Storage for samples in the USB domain as we send them to the channel stream.
        adc_latched = Signal(SW*self.nr_channels)

        # ADC underrun/overrun handling
        adc_underrun = Signal()
        adc_overrun = Signal()
        with m.If(adc_fifo.r_level == 0):
            m.d.usb += adc_underrun.eq(1)
        with m.If(adc_fifo.r_level == self.fifo_depth+1):
            m.d.usb += adc_overrun.eq(1)
        with m.If(adc_underrun | adc_overrun):
            with m.If(adc_fifo.r_level == (self.fifo_depth//2)):
                m.d.usb += adc_underrun.eq(0)
                m.d.usb += adc_overrun.eq(0)

        with m.FSM(domain="usb") as fsm:

            with m.State('WAIT'):
                m.d.usb += self.to_usb.valid.eq(0),
                with m.If(adc_fifo.r_rdy):
                    m.d.usb += adc_fifo.r_en.eq(~adc_underrun)
                    with m.If(~adc_overrun):
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

            for n in range(self.nr_channels-1):
                generate_channel_states(n, f'CH{n+1}')
            generate_channel_states(self.nr_channels-1, 'WAIT')

        #
        # OUTPUT SIDE
        # HOST -> USB Channel stream -> eurorack-pmod calibrated OUTPUT samples.
        #

        m.submodules.dac_fifo = dac_fifo = AsyncFIFOBuffered(width=SW*self.nr_channels, depth=self.fifo_depth, w_domain="usb", r_domain="sync")

        dac_overrun = Signal()
        m.d.usb += dac_fifo.w_en.eq(0)
        for n in range(self.nr_channels):
            with m.If((self.from_usb.channel_nr == n) & self.from_usb.valid):
                m.d.usb += dac_fifo.w_data[n*SW:(n+1)*SW].eq(self.from_usb.payload[N_ZFILL:])
                # Write all channels on every incoming zero'th channel
                # This should work even if < 4 channels are used.
                if n == 0:
                    m.d.usb += dac_fifo.w_en.eq(~dac_overrun)

        # DAC underrun/overrun handling
        dac_underrun = Signal()
        with m.If(dac_fifo.w_level == 0):
            m.d.usb += dac_underrun.eq(1)
        with m.If(dac_fifo.w_level == self.fifo_depth+1):
            m.d.usb += dac_overrun.eq(1)
        with m.If(~dac_underrun):
            wiring.connect(m, dac_fifo.r_stream, wiring.flipped(self.o));
        with m.If(dac_underrun | dac_overrun):
            with m.If(dac_fifo.w_level == (self.fifo_depth//2)):
                m.d.usb += dac_underrun.eq(0)
                m.d.usb += dac_overrun.eq(0)

        dbg = platform.request('debug')
        m.d.comb += [
            self.dac_fifo_level.eq(dac_fifo.w_level),
            self.adc_fifo_level.eq(adc_fifo.r_level),
            self.from_usb.ready.eq(dac_fifo.w_rdy),
            dbg.debug0.o.eq(dac_fifo.w_rdy),
            dbg.debug1.o.eq(dac_fifo.r_rdy),
        ]

        return m
