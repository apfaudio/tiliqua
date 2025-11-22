# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: BSD-3-Clause

import unittest

from amaranth import *
from amaranth.sim import *
from luna.gateware.test.contrib import usb_packet as testp
from parameterized import parameterized

from tiliqua.usb_host import *
from tiliqua.test import stream

from luna.usb2 import USBDevice, USBStreamInEndpoint
from usb_protocol.emitters import DeviceDescriptorCollection

class USBDeviceExample(Elaboratable):

    def __init__(self):
        self.utmi = UTMIInterface()
        super().__init__()

    def create_descriptors(self):
        descriptors = DeviceDescriptorCollection()
        with descriptors.DeviceDescriptor() as d:
            d.idVendor           = 0x16d0
            d.idProduct          = 0xf3b
            d.iManufacturer      = "LUNA"
            d.iProduct           = "Test Device"
            d.iSerialNumber      = "1234"
            d.bNumConfigurations = 1

        with descriptors.ConfigurationDescriptor() as c:
            with c.InterfaceDescriptor() as i:
                i.bInterfaceNumber = 0
                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = 0x01
                    e.wMaxPacketSize   = 64
                with i.EndpointDescriptor() as e:
                    e.bEndpointAddress = 0x81
                    e.wMaxPacketSize   = 64
        return descriptors

    def elaborate(self, platform):

        m = Module()
        m.submodules.usb = usb = USBDevice(bus=self.utmi)
        descriptors = self.create_descriptors()
        usb.add_standard_control_endpoint(descriptors)

        # Counting endpoint OUT
        stream_ep = USBStreamInEndpoint(
            endpoint_number=1,
            max_packet_size=64
        )
        usb.add_endpoint(stream_ep)
        counter = Signal(8)
        with m.If(stream_ep.stream.ready):
            m.d.usb += counter.eq(counter + 1)
        m.d.comb += [
            stream_ep.stream.valid    .eq(1),
            stream_ep.stream.payload  .eq(counter)
        ]

        m.d.comb += [
            usb.connect          .eq(1),
            usb.full_speed_only  .eq(1),
        ]
        return m


class UsbTests(unittest.TestCase):

    def _setup_token(pid, addr, endp):
        def _token(ctx, payload):
            ctx.set(payload.pid, pid)
            ctx.set(payload.data.addr, addr)
            ctx.set(payload.data.endp, endp)
        return _token

    def _setup_sof_token(frame_no):
        def _sof(ctx, payload):
            ctx.set(payload.pid, TokenPID.SOF)
            ctx.set(payload.data.as_value(), frame_no)
        return _sof

    @parameterized.expand([
        ["setup00", _setup_token(TokenPID.SETUP, 0, 0),   testp.token_packet(testp.PID.SETUP, 0, 0)],
        ["out00",   _setup_token(TokenPID.OUT, 0, 0),     testp.token_packet(testp.PID.OUT, 0, 0)],
        ["in00",    _setup_token(TokenPID.IN, 0, 0),      testp.token_packet(testp.PID.IN, 0, 0)],
        ["in01",    _setup_token(TokenPID.IN, 0, 1),      testp.token_packet(testp.PID.IN, 0, 1)],
        ["in10",    _setup_token(TokenPID.IN, 1, 0),      testp.token_packet(testp.PID.IN, 1, 0)],
        ["in7a",    _setup_token(TokenPID.IN, 0x70, 0xa), testp.token_packet(testp.PID.IN, 0x70, 0xa)],
        ["sof_min", _setup_sof_token(1),                  testp.sof_packet(1)],
        ["sof_max", _setup_sof_token(2**11-1),            testp.sof_packet(2**11-1)],
    ])
    def test_usb_tokens(self, name, test_payload, test_ref):

        """
        Verify our USBTokenPacketGenerator emits exactly the same bits
        as LUNA's test packet reference library.
        """

        dut = DomainRenamer({"usb": "sync"})(
            USBTokenPacketGenerator())

        async def testbench(ctx):
            data = []
            ctx.set(dut.tx.ready, 1)
            test_payload(ctx, dut.i.payload)
            ctx.set(dut.i.valid, 1)
            await ctx.tick()
            while ctx.get(dut.tx.valid):
                data.append(int(ctx.get(dut.tx.data)))
                await ctx.tick()
            print("[packet]", [hex(d) for d in data])
            bs = ("{0:08b}".format(data[0])[::-1] +
                  "{0:08b}".format(data[1])[::-1] +
                  "{0:08b}".format(data[2])[::-1])
            print("[ref]", test_ref)
            print("[got]", bs)
            self.assertEqual(bs, test_ref)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_usb_token_{name}.vcd", "w")):
            sim.run()

    @parameterized.expand([
        ["get_descriptor",    SetupPayload.init_get_descriptor(0x0100, 0x0040),
                              [0x80, 0x06, 0x00, 0x01, 0x00, 0x00, 0x40, 0x00]],
        ["set_address",       SetupPayload.init_set_address(0x0012),
                              [0x00, 0x05, 0x12, 0x00, 0x00, 0x00, 0x00, 0x00]],
        ["set_configuration", SetupPayload.init_set_configuration(0x0001),
                              [0x00, 0x09, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00]],
    ])
    def test_setup_payload(self, name, payload, ref):

        """
        Verify SetupPayload produces the same bits measured using Cynthion on the wire.
        """

        v = Signal(SetupPayload, init=payload)
        for n in range(len(ref)):
            self.assertEqual(ref[n], (v.as_value().init >> (n*8)) & 0xFF)

    def test_usb_integration(self):

        """
        Integration test to inspect what packets are spat out
        by SimpleUSBMIDIHost, and that things are sufficiently
        wired together for a functioning system.
        """

        m = Module()
        m.submodules.dut = dut = DomainRenamer({"usb": "sync"})(
                                               SimpleUSBMIDIHost(sim=True))
        m.submodules.dev = dev = DomainRenamer({"usb": "sync"})(USBDeviceExample())
        m.d.comb += [
            dev.utmi.rx_valid.eq(dut.utmi.tx_valid & dut.utmi.tx_ready),
            dev.utmi.rx_data.eq(dut.utmi.tx_data),

            dut.utmi.rx_valid.eq(dev.utmi.tx_valid & dev.utmi.tx_ready),
            dut.utmi.rx_data.eq(dev.utmi.tx_data),
        ]

        m.d.comb += dev.utmi.rx_active.eq(0)
        sync_cnt_dut = Signal(2, init=0)
        with m.If(dut.utmi.tx_valid):
            m.d.comb += dev.utmi.rx_active.eq(1)
            with m.If(sync_cnt_dut == 0x3):
                m.d.comb += dut.utmi.tx_ready.eq(1)
            with m.Else():
                m.d.sync += sync_cnt_dut.eq(sync_cnt_dut + 1)
        with m.Else():
            m.d.sync += sync_cnt_dut.eq(0)

        m.d.comb += dut.utmi.rx_active.eq(0)
        sync_cnt_dev = Signal(2, init=0)
        with m.If(dev.utmi.tx_valid):
            m.d.comb += dut.utmi.rx_active.eq(1)
            with m.If(sync_cnt_dev == 0x3):
                m.d.comb += dev.utmi.tx_ready.eq(1)
            with m.Else():
                m.d.sync += sync_cnt_dev.eq(sync_cnt_dev + 1)
        with m.Else():
            m.d.sync += sync_cnt_dev.eq(0)

        m.d.comb += dut.o_midi_bytes.ready.eq(1)

        async def testbench(ctx):
            for i in range(0, 100):
                data = []
                while ctx.get(~dut.utmi.tx_valid):
                    await ctx.tick()
                while ctx.get(dut.utmi.tx_valid):
                    data.append(int(ctx.get(dut.utmi.tx_data)))
                    await ctx.tick()
                print("[packet]", [hex(d) for d in data])

        sim = Simulator(m)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_usb_integration.vcd", "w")):
            sim.run()

    @parameterized.expand([
        ["arturia_keylabmkii", 1],
        ["oxi_one", 1],
        ["yamaha_cp73", 2],
        ["yamaha_pssa50", 2],
        ["android_uac_midi", 1],
        ["korg_microkey2", 2],
    ])
    def test_endpoint_extractor(self, name, expected_endp):

        dut = DomainRenamer({"usb": "sync"})(
                USBMIDIConfigurationEndpointExtractor())

        async def testbench(ctx):
            ctx.set(dut.enable, 1)
            with open(f'tests/data/usbdesc_config/{name}.bin', 'rb') as f:
                for byte in f.read():
                    await stream.put(ctx, dut.i, byte)
            ctx.tick()
            endp = ctx.get(dut.o.endp)
            endp_valid = ctx.get(dut.o.valid)
            self.assertEqual(endp_valid, 1)
            self.assertEqual(endp, expected_endp)

        sim = Simulator(dut)
        sim.add_clock(1e-6)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open(f"test_midi_endpoint_extractor_{name}.vcd", "w")):
            sim.run()
