from amaranth import *
from amaranth.lib import wiring
from amaranth.lib.wiring import In, Out, connect, flipped
from amaranth_soc import csr

class UsbVbusPeripheral(wiring.Component):

    """Tiny periph for USB host port VBUS control."""

    class Flags(csr.Register, access="w"):
        en: csr.Field(csr.action.W, unsigned(1))

    def __init__(self):
        regs = csr.Builder(addr_width=2, data_width=8)
        self._flags = regs.add("flags", self.Flags(), offset=0x0)
        self._bridge = csr.Bridge(regs.as_memory_map())
        super().__init__({
            "en": Out(1),
            "bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
        })
        self.bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform):
        m = Module()
        m.submodules.bridge = self._bridge
        connect(m, flipped(self.bus), self._bridge.bus)
        with m.If(self._flags.f.en.w_stb):
            m.d.sync += self.en.eq(self._flags.f.en.w_data)
        return m
