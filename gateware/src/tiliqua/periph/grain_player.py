# Copyright (c) 2024 Seb Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0

"""Utility for playing back sections from audio delay lines."""

from amaranth import *
from amaranth.lib import stream, wiring, enum
from amaranth.lib.wiring import In, Out

from amaranth_future import fixed
from amaranth_soc import csr

from ..dsp import ASQ, delay_line
from ..dsp.stream_util import Merge, Split, connect_feedback_kick

class Peripheral(wiring.Component):

    """
    SoC peripheral for `GrainPlayer`, a DMA core which reads samples from
    sections of a `DelayLine`, with adjustable start, stop, speed and
    loop settings. Playback can be triggered with CSR writes or connected
    to a hardware gate trigger with `hw_gate_enable`.
    """

    class ControlReg(csr.Register, access="rw"):
        gate: csr.Field(csr.action.RW, unsigned(1))
        mode: csr.Field(csr.action.RW, unsigned(2))
        reverse: csr.Field(csr.action.RW, unsigned(1))
        hw_gate_enable: csr.Field(csr.action.RW, unsigned(1))

    class SpeedReg(csr.Register, access="rw"):
        speed: csr.Field(csr.action.RW, unsigned(16))

    class StartReg(csr.Register, access="rw"):
        start: csr.Field(csr.action.RW, unsigned(32))

    class LengthReg(csr.Register, access="rw"):
        length: csr.Field(csr.action.RW, unsigned(32))

    class StatusReg(csr.Register, access="r"):
        position: csr.Field(csr.action.R, unsigned(32))

    def __init__(self, delayln):
        self._delayln = delayln
        self._grain_player = GrainPlayer(delayln)

        regs = csr.Builder(addr_width=5, data_width=8)
        self._control = regs.add("control", self.ControlReg(), offset=0x00)
        self._speed = regs.add("speed", self.SpeedReg(), offset=0x04)
        self._start = regs.add("start", self.StartReg(), offset=0x08)
        self._length = regs.add("length", self.LengthReg(), offset=0x0C)
        self._status = regs.add("status", self.StatusReg(), offset=0x10)
        self._bridge = csr.Bridge(regs.as_memory_map())

        super().__init__({
            "csr_bus": In(csr.Signature(addr_width=regs.addr_width, data_width=regs.data_width)),
            # Hardware gate used for triggering if `control.hw_gate_enable` is asserted.
            "hw_gate": In(1),
            "o": Out(stream.Signature(ASQ)),
        })

        self.csr_bus.memory_map = self._bridge.bus.memory_map

    def elaborate(self, platform) -> Module:
        m = Module()

        m.submodules.bridge = self._bridge
        m.submodules.grain_player = grain_player = self._grain_player

        wiring.connect(m, wiring.flipped(self.csr_bus), self._bridge.bus)

        # Select between hw/rtl gate and CSR (cpu)-triggered gate.
        effective_gate = Mux(self._control.f.hw_gate_enable.data,
                             self.hw_gate,
                             self._control.f.gate.data)

        m.d.comb += [
            grain_player.gate.eq(effective_gate),
            grain_player.mode.eq(self._control.f.mode.data),
            grain_player.reverse.eq(self._control.f.reverse.data),
            grain_player.start.eq(self._start.f.start.data),
            grain_player.length.eq(self._length.f.length.data),
            grain_player.speed.as_value().eq(self._speed.f.speed.data),
            self._status.f.position.r_data.eq(grain_player.position),
        ]

        wiring.connect(m, grain_player.o, wiring.flipped(self.o))

        return m

class GrainPlayer(wiring.Component):

    class Mode(enum.Enum, shape=unsigned(2)):
        GATE    = 0  # Play while gate high, stop when low, reset on rising edge
        ONESHOT = 1  # Play full length ignoring gate, restart on rising edge
        LOOP    = 2  # Loop while gate high, stop when low, reset on rising edge
        BOUNCE  = 3  # Like loop but alternate direction at boundaries

    def __init__(self, delayln, sq=ASQ):
        self.delayln = delayln
        self.tap = self.delayln.add_tap()
        self.sq = sq
        assert not self.delayln.write_triggers_read
        super().__init__({
            # Control
            "gate": In(unsigned(1)),
            "mode": In(GrainPlayer.Mode),
            "reverse": In(unsigned(1)),
            "speed": In(fixed.UQ(8, 8)),
            "start": In(unsigned(self.delayln.address_width)),
            "length": In(unsigned(self.delayln.address_width)),
            # Status
            "position": Out(unsigned(self.delayln.address_width)),
            # Outgoing sample stream
            "o": Out(stream.Signature(sq)),
        })

    def elaborate(self, platform):

        m = Module()

        start    = Signal.like(self.start)
        length   = Signal.like(self.length)
        mode     = Signal.like(self.mode)
        l_gate   = Signal.like(self.gate)
        reverse  = Signal.like(self.reverse)
        bouncing = Signal()  # Toggles fwd/rev in BOUNCE mode
        pos      = Signal(fixed.UQ(len(self.length), 8))

        m.d.sync += l_gate.eq(self.gate)

        # Bouncing toggles between forward/reverse
        eff_reverse = Signal()
        m.d.comb += eff_reverse.eq(reverse ^ bouncing)

        gate_rising = Signal()
        m.d.comb += gate_rising.eq(~l_gate & self.gate)

        with m.FSM():
            with m.State('WAIT-READY-ZERO'):
                m.d.comb += [
                    self.o.valid.eq(1),
                    self.o.payload.eq(0),
                ]
                with m.If(gate_rising):
                    m.next = 'START-GATE'
            with m.State('START-GATE'):
                m.d.sync += [
                    reverse.eq(self.reverse),
                    mode.eq(self.mode),
                    start.eq(self.start),
                    length.eq(self.length),
                    pos.eq(0),
                    bouncing.eq(0),
                ]
                m.next = 'FETCH-SAMPLE'
            with m.State('FETCH-SAMPLE'):
                m.d.comb += [
                    self.tap.i.valid.eq(1),
                ]
                with m.If(eff_reverse):
                    delay = start-length+pos.truncate()+1
                    m.d.comb += self.tap.i.payload.eq(delay),
                    m.d.sync += self.position.eq(delay)
                with m.Else():
                    delay = start-pos.truncate()
                    m.d.comb += self.tap.i.payload.eq(delay),
                    m.d.sync += self.position.eq(delay)
                with m.If(self.tap.i.ready):
                    m.next = 'OUTPUT-SAMPLE'
            with m.State('OUTPUT-SAMPLE'):
                wiring.connect(m, self.tap.o, wiring.flipped(self.o))
                with m.If(self.tap.o.valid & self.tap.o.ready):
                    # Always restart on rising edge
                    with m.If(gate_rising):
                        m.next = 'START-GATE'
                    with m.Elif(~self.gate):
                        with m.If(mode == GrainPlayer.Mode.ONESHOT):
                            # ONESHOT: continue playing even if gate low
                            with m.If(pos.truncate() >= (length-1)):
                                m.next = 'WAIT-READY-ZERO'
                            with m.Else():
                                m.d.sync += pos.eq(pos+self.speed)
                                m.next = 'FETCH-SAMPLE'
                        with m.Else():
                            # GATE, LOOP, BOUNCE: stop when gate low
                            m.next = 'WAIT-READY-ZERO'
                    # End of grain
                    with m.Elif(pos.truncate() >= (length-1)):
                        with m.If(mode == GrainPlayer.Mode.GATE):
                            m.next = 'WAIT-READY-ZERO'
                        with m.Elif(mode == GrainPlayer.Mode.ONESHOT):
                            m.next = 'WAIT-READY-ZERO'
                        with m.Elif(mode == GrainPlayer.Mode.LOOP):
                            m.next = 'START-GATE'
                        with m.Elif(mode == GrainPlayer.Mode.BOUNCE):
                            # Toggle direction, reset position
                            m.d.sync += [
                                bouncing.eq(~bouncing),
                                pos.eq(0),
                            ]
                            m.next = 'FETCH-SAMPLE'
                    with m.Else():
                        m.d.sync += pos.eq(pos+self.speed)
                        m.next = 'FETCH-SAMPLE'

        return m
