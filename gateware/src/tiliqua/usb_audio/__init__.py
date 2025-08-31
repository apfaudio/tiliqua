# Copyright (c) 2021 Hans Baier <hansfbaier@gmail.com>
# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD--3-Clause

"""
USB2 class-compliant audio interface.
Some parts adapted from: https://github.com/hansfbaier/adat-usb2-audio-interface
"""

from amaranth import *
from amaranth.build import *
from amaranth.lib import data, stream, wiring
from amaranth.lib.cdc import FFSynchronizer
from amaranth.lib.wiring import In, Out
from luna.gateware.stream.generator import StreamSerializer
from luna.gateware.usb.stream import USBInStreamInterface
from luna.gateware.usb.usb2.device import USBDevice
from luna.gateware.usb.usb2.request import (StallOnlyRequestHandler,
                                            USBRequestHandler)
from luna.usb2 import (USBDevice, USBIsochronousInEndpoint,
                       USBIsochronousStreamInEndpoint,
                       USBIsochronousStreamOutEndpoint)
from usb_protocol.emitters import DeviceDescriptorCollection
from usb_protocol.emitters.descriptors import standard, uac2
from usb_protocol.types import (USBDirection, USBRequestRecipient,
                                USBRequestType, USBStandardRequests,
                                USBSynchronizationType, USBTransferType,
                                USBUsageType)
from usb_protocol.types.descriptors.uac2 import AudioClassSpecificRequestCodes

from tiliqua import pll
from tiliqua.periph import eurorack_pmod

from .audio_to_channels import AudioToChannels
from .channels_to_usb_stream import ChannelsToUSBStream
from .usb_stream_to_channels import USBStreamToChannels
from .util import EdgeToPulse


class USB2AudioInterface(wiring.Component):

    class DebugInterface(wiring.Signature):
        def __init__(self):
            super().__init__({
                "sof_detected": Out(1),
                "dac_fifo_level": Out(8),
                "adc_fifo_level": Out(8),
                "garbage_seen_out": Out(1),
                "channel_stream_out_valid": Out(1),
                "channel_stream_out_first": Out(1),
                "usb_stream_in_valid": Out(1),
                "usb_stream_in_ready": Out(1),
                "usb_stream_in_payload": Out(8),
            })

    """ USB Audio Class v2 interface """

    def __init__(self, *, audio_clock: pll.AudioClock, nr_channels):
        self.fs = 192000 if audio_clock.is_192khz() else 48000
        self.nr_channels = nr_channels
        self.max_packet_size = int(32 * (self.fs // 48000) * self.nr_channels)
        super().__init__({
            "i":  In(stream.Signature(data.ArrayLayout(eurorack_pmod.ASQ, self.nr_channels))),
            "o": Out(stream.Signature(data.ArrayLayout(eurorack_pmod.ASQ, self.nr_channels))),

            "dbg": Out(self.DebugInterface())
        })

    def create_descriptors(self):
        """ Creates the descriptors that describe our audio topology. """

        descriptors = DeviceDescriptorCollection()

        with descriptors.DeviceDescriptor() as d:
            d.bcdUSB             = 2.00
            d.bDeviceClass       = 0xEF
            d.bDeviceSubclass    = 0x02
            d.bDeviceProtocol    = 0x01
            d.idVendor           = 0x1209
            d.idProduct          = 0xAA62

            d.iManufacturer      = "apf.audio"
            d.iProduct           = "Tiliqua"
            d.iSerialNumber      = "beta-0000"
            d.bcdDevice          = 0.01

            d.bNumConfigurations = 1

        with descriptors.ConfigurationDescriptor() as configDescr:
            # Interface Association
            interfaceAssociationDescriptor                 = uac2.InterfaceAssociationDescriptorEmitter()
            interfaceAssociationDescriptor.bInterfaceCount = 3 # Audio Control + Inputs + Outputs
            configDescr.add_subordinate_descriptor(interfaceAssociationDescriptor)

            # Interface Descriptor (Control)
            interfaceDescriptor = uac2.StandardAudioControlInterfaceDescriptorEmitter()
            interfaceDescriptor.bInterfaceNumber = 0
            configDescr.add_subordinate_descriptor(interfaceDescriptor)

            # AudioControl Interface Descriptor
            audioControlInterface = self.create_audio_control_interface_descriptor()
            configDescr.add_subordinate_descriptor(audioControlInterface)

            # Audio I/O stream descriptors
            self.create_output_channels_descriptor(configDescr)
            self.create_input_channels_descriptor(configDescr)

        return descriptors


    def create_audio_control_interface_descriptor(self):
        audioControlInterface = uac2.ClassSpecificAudioControlInterfaceDescriptorEmitter()

        # AudioControl Interface Descriptor (ClockSource)
        clockSource = uac2.ClockSourceDescriptorEmitter()
        clockSource.bClockID     = 1
        clockSource.bmAttributes = uac2.ClockAttributes.INTERNAL_FIXED_CLOCK
        clockSource.bmControls   = uac2.ClockFrequencyControl.HOST_READ_ONLY
        audioControlInterface.add_subordinate_descriptor(clockSource)


        # streaming input port from the host to the USB interface
        inputTerminal               = uac2.InputTerminalDescriptorEmitter()
        inputTerminal.bTerminalID   = 2
        inputTerminal.wTerminalType = uac2.USBTerminalTypes.USB_STREAMING
        # The number of channels needs to be 2 here in order to be recognized
        # default audio out device by Windows. We provide an alternate
        # setting with the full channel count, which also references
        # this terminal ID
        inputTerminal.bNrChannels   = self.nr_channels
        inputTerminal.bCSourceID    = 1
        audioControlInterface.add_subordinate_descriptor(inputTerminal)

        # audio output port from the USB interface to the outside world
        outputTerminal               = uac2.OutputTerminalDescriptorEmitter()
        outputTerminal.bTerminalID   = 3
        outputTerminal.wTerminalType = uac2.OutputTerminalTypes.SPEAKER
        outputTerminal.bSourceID     = 2
        outputTerminal.bCSourceID    = 1
        audioControlInterface.add_subordinate_descriptor(outputTerminal)

        # audio input port from the outside world to the USB interface
        inputTerminal               = uac2.InputTerminalDescriptorEmitter()
        inputTerminal.bTerminalID   = 4
        inputTerminal.wTerminalType = uac2.InputTerminalTypes.MICROPHONE
        inputTerminal.bNrChannels   = self.nr_channels
        inputTerminal.bCSourceID    = 1
        audioControlInterface.add_subordinate_descriptor(inputTerminal)

        # audio output port from the USB interface to the host
        outputTerminal               = uac2.OutputTerminalDescriptorEmitter()
        outputTerminal.bTerminalID   = 5
        outputTerminal.wTerminalType = uac2.USBTerminalTypes.USB_STREAMING
        outputTerminal.bSourceID     = 4
        outputTerminal.bCSourceID    = 1
        audioControlInterface.add_subordinate_descriptor(outputTerminal)

        return audioControlInterface


    def create_output_streaming_interface(self, c, *, nr_channels, alt_setting_nr):
        # Interface Descriptor (Streaming, OUT, active setting)
        activeAudioStreamingInterface                   = uac2.AudioStreamingInterfaceDescriptorEmitter()
        activeAudioStreamingInterface.bInterfaceNumber  = 1
        activeAudioStreamingInterface.bAlternateSetting = alt_setting_nr
        activeAudioStreamingInterface.bNumEndpoints     = 2
        c.add_subordinate_descriptor(activeAudioStreamingInterface)

        # AudioStreaming Interface Descriptor (General)
        audioStreamingInterface               = uac2.ClassSpecificAudioStreamingInterfaceDescriptorEmitter()
        audioStreamingInterface.bTerminalLink = 2
        audioStreamingInterface.bFormatType   = uac2.FormatTypes.FORMAT_TYPE_I
        audioStreamingInterface.bmFormats     = uac2.TypeIFormats.PCM
        audioStreamingInterface.bNrChannels   = nr_channels
        c.add_subordinate_descriptor(audioStreamingInterface)

        # AudioStreaming Interface Descriptor (Type I)
        typeIStreamingInterface  = uac2.TypeIFormatTypeDescriptorEmitter()
        typeIStreamingInterface.bSubslotSize   = 4
        typeIStreamingInterface.bBitResolution = 24 # we use all 24 bits
        c.add_subordinate_descriptor(typeIStreamingInterface)

        # Endpoint Descriptor (Audio out)
        audioOutEndpoint = standard.EndpointDescriptorEmitter()
        audioOutEndpoint.bEndpointAddress     = USBDirection.OUT.to_endpoint_address(1) # EP 1 OUT
        audioOutEndpoint.bmAttributes         = USBTransferType.ISOCHRONOUS  | \
                                                (USBSynchronizationType.ASYNC << 2) | \
                                                (USBUsageType.DATA << 4)
        audioOutEndpoint.wMaxPacketSize = self.max_packet_size
        audioOutEndpoint.bInterval       = 1
        c.add_subordinate_descriptor(audioOutEndpoint)

        # AudioControl Endpoint Descriptor
        audioControlEndpoint = uac2.ClassSpecificAudioStreamingIsochronousAudioDataEndpointDescriptorEmitter()
        c.add_subordinate_descriptor(audioControlEndpoint)

        # Endpoint Descriptor (Feedback IN)
        feedbackInEndpoint = standard.EndpointDescriptorEmitter()
        feedbackInEndpoint.bEndpointAddress  = USBDirection.IN.to_endpoint_address(1) # EP 1 IN
        feedbackInEndpoint.bmAttributes      = USBTransferType.ISOCHRONOUS  | \
                                               (USBSynchronizationType.NONE << 2)  | \
                                               (USBUsageType.FEEDBACK << 4)
        feedbackInEndpoint.wMaxPacketSize    = 4
        feedbackInEndpoint.bInterval         = 4
        c.add_subordinate_descriptor(feedbackInEndpoint)


    def create_output_channels_descriptor(self, c):
        #
        # Interface Descriptor (Streaming, OUT, quiet setting)
        #
        quietAudioStreamingInterface = uac2.AudioStreamingInterfaceDescriptorEmitter()
        quietAudioStreamingInterface.bInterfaceNumber  = 1
        quietAudioStreamingInterface.bAlternateSetting = 0
        c.add_subordinate_descriptor(quietAudioStreamingInterface)

        # we need the default alternate setting to be stereo
        # out for windows to automatically recognize
        # and use this audio interface
        self.create_output_streaming_interface(c, nr_channels=self.nr_channels, alt_setting_nr=1)


    def create_input_streaming_interface(self, c, *, nr_channels, alt_setting_nr, channel_config=0):
        # Interface Descriptor (Streaming, IN, active setting)
        activeAudioStreamingInterface = uac2.AudioStreamingInterfaceDescriptorEmitter()
        activeAudioStreamingInterface.bInterfaceNumber  = 2
        activeAudioStreamingInterface.bAlternateSetting = alt_setting_nr
        activeAudioStreamingInterface.bNumEndpoints     = 1
        c.add_subordinate_descriptor(activeAudioStreamingInterface)

        # AudioStreaming Interface Descriptor (General)
        audioStreamingInterface                 = uac2.ClassSpecificAudioStreamingInterfaceDescriptorEmitter()
        audioStreamingInterface.bTerminalLink   = 5
        audioStreamingInterface.bFormatType     = uac2.FormatTypes.FORMAT_TYPE_I
        audioStreamingInterface.bmFormats       = uac2.TypeIFormats.PCM
        audioStreamingInterface.bNrChannels     = nr_channels
        audioStreamingInterface.bmChannelConfig = channel_config
        c.add_subordinate_descriptor(audioStreamingInterface)

        # AudioStreaming Interface Descriptor (Type I)
        typeIStreamingInterface  = uac2.TypeIFormatTypeDescriptorEmitter()
        typeIStreamingInterface.bSubslotSize   = 4
        typeIStreamingInterface.bBitResolution = 24 # we use all 24 bits
        c.add_subordinate_descriptor(typeIStreamingInterface)

        # Endpoint Descriptor (Audio out)
        audioOutEndpoint = standard.EndpointDescriptorEmitter()
        audioOutEndpoint.bEndpointAddress     = USBDirection.IN.to_endpoint_address(2) # EP 2 IN
        audioOutEndpoint.bmAttributes         = USBTransferType.ISOCHRONOUS  | \
                                                (USBSynchronizationType.ASYNC << 2) | \
                                                (USBUsageType.DATA << 4)
        audioOutEndpoint.wMaxPacketSize = self.max_packet_size
        audioOutEndpoint.bInterval      = 1
        c.add_subordinate_descriptor(audioOutEndpoint)

        # AudioControl Endpoint Descriptor
        audioControlEndpoint = uac2.ClassSpecificAudioStreamingIsochronousAudioDataEndpointDescriptorEmitter()
        c.add_subordinate_descriptor(audioControlEndpoint)


    def create_input_channels_descriptor(self, c):
        #
        # Interface Descriptor (Streaming, IN, quiet setting)
        #
        quietAudioStreamingInterface = uac2.AudioStreamingInterfaceDescriptorEmitter()
        quietAudioStreamingInterface.bInterfaceNumber  = 2
        quietAudioStreamingInterface.bAlternateSetting = 0
        c.add_subordinate_descriptor(quietAudioStreamingInterface)

        # Windows wants a stereo pair as default setting, so let's have it
        self.create_input_streaming_interface(c, nr_channels=self.nr_channels, alt_setting_nr=1, channel_config=0x3)

    def elaborate(self, platform):
        m = Module()

        ulpi = platform.request(platform.default_usb_connection)
        m.submodules.usb = usb = USBDevice(bus=ulpi)

        # Add our standard control endpoint to the device.
        descriptors = self.create_descriptors()
        control_ep = usb.add_control_endpoint()
        control_ep.add_standard_request_handlers(descriptors, blacklist=[
            lambda setup:   (setup.type    == USBRequestType.STANDARD)
                          & (setup.request == USBStandardRequests.SET_INTERFACE)
        ])

        # Attach our class request handlers.
        class_request_handler = UAC2RequestHandlers(fs=self.fs)
        control_ep.add_request_handler(class_request_handler)

        # Attach class-request handlers that stall any vendor or reserved requests,
        # as we don't have or need any.
        stall_condition = lambda setup : \
            (setup.type == USBRequestType.VENDOR) | \
            (setup.type == USBRequestType.RESERVED)
        control_ep.add_request_handler(StallOnlyRequestHandler(stall_condition))

        ep1_out = USBIsochronousStreamOutEndpoint(
            endpoint_number=1, # EP 1 OUT
            max_packet_size=self.max_packet_size)
        usb.add_endpoint(ep1_out)

        ep1_in = USBIsochronousInEndpoint(
            endpoint_number=1, # EP 1 IN
            max_packet_size=4)
        usb.add_endpoint(ep1_in)

        ep2_in = USBIsochronousStreamInEndpoint(
            endpoint_number=2, # EP 2 IN
            max_packet_size=self.max_packet_size)
        usb.add_endpoint(ep2_in)

        # calculate bytes in frame for audio in
        audio_in_frame_bytes = Signal(range(self.max_packet_size), reset=24 * self.nr_channels)
        audio_in_frame_bytes_counting = Signal()

        with m.If(ep1_out.stream.valid & ep1_out.stream.ready):
            with m.If(audio_in_frame_bytes_counting):
                m.d.usb += audio_in_frame_bytes.eq(audio_in_frame_bytes + 1)

            with m.If(ep1_out.stream.payload.first):
                m.d.usb += [
                    audio_in_frame_bytes.eq(1),
                    audio_in_frame_bytes_counting.eq(1),
                ]
            with m.Elif(ep1_out.stream.payload.last):
                m.d.usb += audio_in_frame_bytes_counting.eq(0)

        # Connect our device as a high speed device
        m.d.comb += [
            ep1_in.bytes_in_frame.eq(4),
            ep2_in.bytes_in_frame.eq(audio_in_frame_bytes),
            usb.connect          .eq(1),
            usb.full_speed_only  .eq(0),
        ]

        # feedback endpoint
        feedbackValue      = Signal(32, reset=0x60000)
        bitPos             = Signal(5)

        # this tracks the number of audio frames since the last USB frame
        # 12.288MHz / 8kHz = 1536, so we need at least 11 bits = 2048
        # we need to capture 32 micro frames to get to the precision
        # required by the USB standard, so and that is 0xc000, so we
        # need 16 bits here
        audio_clock_counter = Signal(24)
        sof_counter         = Signal(8)
        audio_clock_usb = Signal()
        m.submodules.audio_clock_usb_pulse = audio_clock_usb_pulse = DomainRenamer("usb")(EdgeToPulse())
        audio_clock_tick = Signal()
        m.d.usb += [
            audio_clock_usb_pulse.edge_in.eq(audio_clock_usb),
            audio_clock_tick.eq(audio_clock_usb_pulse.pulse_out),
        ]

        match self.fs:
            case 192000:
                # Audio clock dangerously close to USB clock, divide it down before synchronizing into USB domain
                audio_clkdiv = Signal(2)
                m.d.audio += audio_clkdiv.eq(audio_clkdiv+1)
                m.submodules.audio_clock_usb_sync = FFSynchronizer(audio_clkdiv[-1], audio_clock_usb, o_domain="usb")
                with m.If(audio_clock_tick):
                    m.d.usb += audio_clock_counter.eq(audio_clock_counter + 4)
            case 48000:
                # Audio clock not close to USB clock, no need for divider.
                m.submodules.audio_clock_usb_sync = FFSynchronizer(ClockSignal("audio"), audio_clock_usb, o_domain="usb")
                with m.If(audio_clock_tick):
                    m.d.usb += audio_clock_counter.eq(audio_clock_counter + 1)
            case _:
                raise ValueError("audio clock tracking only tested for 48khz/192khz")

        m.d.comb += [
            bitPos.eq(ep1_in.address << 3),
            ep1_in.value.eq(0xff & (feedbackValue >> bitPos)),
        ]

        m.submodules.usb_to_channel_stream = usb_to_channel_stream = \
            DomainRenamer("usb")(USBStreamToChannels(self.nr_channels))

        m.submodules.channels_to_usb_stream = channels_to_usb_stream = \
            DomainRenamer("usb")(ChannelsToUSBStream(self.nr_channels, max_packet_size=self.max_packet_size))

        def detect_active_audio_in(m, name: str, usb, ep2_in):
            audio_in_seen   = Signal(name=f"{name}_audio_in_seen")
            audio_in_active = Signal(name=f"{name}_audio_in_active")

            # detect if we don't have a USB audio IN packet
            with m.If(usb.sof_detected):
                m.d.usb += [
                    audio_in_active.eq(audio_in_seen),
                    audio_in_seen.eq(0),
                ]

            with m.If(ep2_in.data_requested):
                m.d.usb += audio_in_seen.eq(1)

            return audio_in_active

            usb_audio_in_active  = detect_active_audio_in(m, "usb", usb, ep2_in)

        usb_audio_in_active = detect_active_audio_in(m, "usb", usb, ep2_in)

        wiring.connect(m, wiring.flipped(usb_to_channel_stream.usb_stream_in), ep1_out.stream)
        wiring.connect(m,  wiring.flipped(ep2_in.stream), channels_to_usb_stream.usb_stream_out)

        m.d.comb += [
            channels_to_usb_stream.no_channels_in.eq(self.nr_channels),
            channels_to_usb_stream.data_requested_in.eq(ep2_in.data_requested),
            channels_to_usb_stream.frame_finished_in.eq(ep2_in.frame_finished),
            channels_to_usb_stream.audio_in_active.eq(usb_audio_in_active),
            usb_to_channel_stream.no_channels_in.eq(self.nr_channels),
        ]

        m.submodules.audio_to_channels = audio_to_channels = AudioToChannels(
                nr_channels=self.nr_channels,
                to_usb_stream=channels_to_usb_stream.channel_stream_in,
                from_usb_stream=usb_to_channel_stream.channel_stream_out,
                fifo_depth=16 * (self.fs // 48000))
        wiring.connect(m, wiring.flipped(self.i), audio_to_channels.i)
        wiring.connect(m, audio_to_channels.o, wiring.flipped(self.o))

        with m.If(usb.sof_detected):
            m.d.usb += sof_counter.eq(sof_counter + 1)

            # according to USB2 standard chapter 5.12.4.2
            # we need 2**13 / 2**8 = 2**5 = 32 SOF-frames of
            # sample master frequency counter to get enough
            # precision for the sample frequency estimate
            # / 2**8 because the ADAT-clock = 256 times = 2**8
            # the sample frequency and sof_counter is 5 bits
            # so it wraps automatically every 32 SOFs
            with m.If(sof_counter == 0):
                m.d.usb += [
                    # FIFO feedback?
                    feedbackValue.eq((audio_clock_counter + 1) -
                                     (audio_to_channels.dac_fifo_level >> 3)),
                    audio_clock_counter.eq(0),
                ]

        # Debug interface for introspection / ILA usage
        m.d.comb += [
            self.dbg.dac_fifo_level.eq(audio_to_channels.dac_fifo_level),
            self.dbg.adc_fifo_level.eq(audio_to_channels.adc_fifo_level),
            self.dbg.sof_detected.eq(usb.sof_detected),
            self.dbg.channel_stream_out_valid.eq(usb_to_channel_stream.channel_stream_out.valid),
            self.dbg.channel_stream_out_first.eq(usb_to_channel_stream.channel_stream_out.first),
            self.dbg.usb_stream_in_valid.eq(usb_to_channel_stream.usb_stream_in.valid),
            self.dbg.usb_stream_in_payload.eq(usb_to_channel_stream.usb_stream_in.payload),
            self.dbg.usb_stream_in_ready.eq(usb_to_channel_stream.usb_stream_in.ready),
        ]

        return m

class UAC2RequestHandlers(USBRequestHandler):
    """ request handlers to implement UAC2 functionality. """
    def __init__(self, fs):
        super().__init__()

        self.fs = fs
        self.output_interface_altsetting_nr = Signal(3)
        self.input_interface_altsetting_nr  = Signal(3)
        self.interface_settings_changed     = Signal()

    def elaborate(self, platform):
        m = Module()

        interface         = self.interface
        setup             = self.interface.setup

        m.submodules.transmitter = transmitter = \
            StreamSerializer(data_length=14, domain="usb", stream_type=USBInStreamInterface, max_length_width=14)

        m.d.usb += self.interface_settings_changed.eq(0)

        #
        # Class request handlers.
        #
        with m.If(setup.type == USBRequestType.STANDARD):
            with m.If((setup.recipient == USBRequestRecipient.INTERFACE) &
                      (setup.request == USBStandardRequests.SET_INTERFACE)):

                m.d.comb += interface.claim.eq(1)

                interface_nr   = setup.index
                alt_setting_nr = setup.value

                m.d.usb += [
                    self.output_interface_altsetting_nr.eq(0),
                    self.input_interface_altsetting_nr.eq(0),
                    self.interface_settings_changed.eq(1),
                ]

                with m.Switch(interface_nr):
                    with m.Case(1):
                        m.d.usb += self.output_interface_altsetting_nr.eq(alt_setting_nr)
                    with m.Case(2):
                        m.d.usb += self.input_interface_altsetting_nr.eq(alt_setting_nr)

                # Always ACK the data out...
                with m.If(interface.rx_ready_for_response):
                    m.d.comb += interface.handshakes_out.ack.eq(1)

                # ... and accept whatever the request was.
                with m.If(interface.status_requested):
                    m.d.comb += self.send_zlp()

        request_clock_freq = (setup.value == 0x100) & (setup.index == 0x0100)
        with m.Elif(setup.type == USBRequestType.CLASS):
            with m.Switch(setup.request):
                with m.Case(AudioClassSpecificRequestCodes.RANGE):
                    m.d.comb += interface.claim.eq(1)
                    m.d.comb += transmitter.stream.attach(self.interface.tx)

                    with m.If(request_clock_freq):
                        m.d.comb += [
                            Cat(transmitter.data).eq(
                                Cat(Const(0x1, 16), # no triples
                                    Const(self.fs, 32), # MIN
                                    Const(self.fs, 32), # MAX
                                    Const(0, 32))),   # RES
                            transmitter.max_length.eq(setup.length)
                        ]
                    with m.Else():
                        m.d.comb += interface.handshakes_out.stall.eq(1)

                    # ... trigger it to respond when data's requested...
                    with m.If(interface.data_requested):
                        m.d.comb += transmitter.start.eq(1)

                    # ... and ACK our status stage.
                    with m.If(interface.status_requested):
                        m.d.comb += interface.handshakes_out.ack.eq(1)

                with m.Case(AudioClassSpecificRequestCodes.CUR):
                    m.d.comb += interface.claim.eq(1)
                    m.d.comb += transmitter.stream.attach(self.interface.tx)
                    with m.If(request_clock_freq & (setup.length == 4)):
                        m.d.comb += [
                            Cat(transmitter.data[0:4]).eq(Const(self.fs, 32)),
                            transmitter.max_length.eq(4)
                        ]
                    with m.Else():
                        m.d.comb += interface.handshakes_out.stall.eq(1)

                    # ... trigger it to respond when data's requested...
                    with m.If(interface.data_requested):
                        m.d.comb += transmitter.start.eq(1)

                    # ... and ACK our status stage.
                    with m.If(interface.status_requested):
                        m.d.comb += interface.handshakes_out.ack.eq(1)

                return m
