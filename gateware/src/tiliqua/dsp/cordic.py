# Copyright (c) 2024 S. Holzapfel <me@sebholzapfel.com>
#
# SPDX-License-Identifier: CERN-OHL-S-2.0
#

"""Utilities for computing trigonometric functions in hardware."""

from math import atan, pi

from amaranth import *
from amaranth.lib import memory, stream, wiring
from amaranth.lib.wiring import In, Out

from amaranth_future import fixed

from .complex import CQ, Polar


class RectToPolarCordic(wiring.Component):

    """Iteratively compute magnitude and phase of complex numbers.

    This core uses a CORDIC (Coordinate Rotation Digital Computer) approach
    to convert rectangular to polar complex numbers using only shifts and adds.

    This is useful for extracting power spectra from frequency-domain blocks.

    Given a complex number in rectangular coordinates, this core emits:

    .. code-block:: text

        o.payload.magnitude = S*sqrt(i.payload.real**2 + i.payload.imag**2)
        o.payload.phase     = atan2(i.payload.imag, i.payload.real) / pi

        S: =1 if 'magnitude_correction' is True, and =K (CORDIC gain) otherwise

    Members
    -------
    i : :py:`In(stream.Signature(CQ(shape)))`
        Stream of incoming complex numbers in rectangular coordinates.
    o : :py:`Out(stream.Signature(Polar(self.internal_shape)))`
        Stream of outgoing complex numbers in polar coordinates.
    """

    #: CORDIC gain constant.
    K = 1.646760258121

    def __init__(self, shape: fixed.Shape, iterations: int = None,
                 magnitude_correction=True):
        """
        shape : Shape
            Shape of fixed-point number to use for incoming :class:`CQ` stream.
        iterations : int
            Number of iterations of computation. Higher is better accuracy, but
            requires more clock cycles. This defaults to the number of bits
            in the provided ``shape``.
        magnitude_correction : bool
            Whether to consume an additional multiplier to correct for the CORDIC gain
            constant. For some applications, this is not needed and can be used to
            save a multiplier.
        """

        self.shape = shape
        self.iterations = iterations or shape.i_bits + shape.f_bits
        self.internal_shape = fixed.SQ(self.shape.i_bits + 2, self.shape.f_bits)
        self.magnitude_correction = magnitude_correction

        super().__init__({
            "i": In(stream.Signature(CQ(shape))),
            "o": Out(stream.Signature(Polar(self.internal_shape))),
        })

    def elaborate(self, platform) -> Module:
        m = Module()

        #
        # Arctangent ROM initialization
        #

        atan_values = []
        for i in range(self.iterations):
            angle = atan(1.0 / (1<<i)) / pi
            atan_values.append(angle)
        m.submodules.atan_rom = atan_rom = memory.Memory(
            shape=self.internal_shape,
            depth=self.iterations,
            init=atan_values
        )
        atan_rd = atan_rom.read_port(domain='comb')

        #
        # State and iteration registers
        #

        in_latch = Signal.like(self.i.payload)
        x = Signal(self.internal_shape)
        y = Signal(self.internal_shape)
        z = Signal(self.internal_shape)
        iteration = Signal(range(self.iterations + 1))

        #
        # Combinatorial
        #

        x_shift = Signal(self.internal_shape)
        y_shift = Signal(self.internal_shape)
        d = Signal()
        m.d.comb += [
            atan_rd.addr.eq(iteration),
            # Shifted values for current iteration
            x_shift.eq(x >> iteration),
            y_shift.eq(y >> iteration),
            # Direction
            d.eq((x<0)^(y<0)),
        ]

        #
        # Output assignments
        #

        quadrant_adjust = Signal(self.internal_shape)
        m.d.comb += self.o.payload.phase.eq(z + quadrant_adjust),
        if self.magnitude_correction:
            # Scale magnitude by 1/K to compensate for CORDIC gain
            m.d.comb += self.o.payload.magnitude.eq(
                x * fixed.Const(1.0/self.K, self.internal_shape))
        else:
            m.d.comb += self.o.payload.magnitude.eq(x)

        with m.FSM():
            with m.State("IDLE"):
                m.d.comb += self.i.ready.eq(1)
                with m.If(self.i.valid):
                    m.d.sync += in_latch.eq(self.i.payload)
                    m.next = "QUADRANT"

            #
            # Determine which of 4 quadrants this is in
            #

            with m.State("QUADRANT"):
                m.d.sync += [
                    z.eq(0),
                    iteration.eq(0),
                    quadrant_adjust.eq(0)
                ]
                with m.If((in_latch.real >= 0)):  # Q1, Q4
                    m.d.sync += [
                        x.eq(in_latch.real),
                        y.eq(in_latch.imag),
                    ]
                with m.Else():
                    m.d.sync += [
                        x.eq(-in_latch.real),
                        y.eq(-in_latch.imag),
                    ]
                    with m.If(in_latch.imag >= 0):
                        m.d.sync += quadrant_adjust.eq(fixed.Const(1.0))  # Q2
                    with m.Else():
                        m.d.sync += quadrant_adjust.eq(fixed.Const(-1.0)) # Q3
                m.next = "ITERATE"

            #
            # CORDIC rotation for self.iterations
            #

            with m.State("ITERATE"):
                with m.If(iteration < self.iterations):
                    with m.If(d):  # y >= 0, rotate clockwise
                        m.d.sync += [
                            x.eq(x - y_shift),
                            y.eq(y + x_shift),
                            z.eq(z - atan_rd.data),
                        ]
                    with m.Else():  # y < 0, rotate counter-clockwise
                        m.d.sync += [
                            x.eq(x + y_shift),
                            y.eq(y - x_shift),
                            z.eq(z + atan_rd.data),
                        ]
                    m.d.sync += iteration.eq(iteration + 1)
                    m.next = "ITERATE"
                with m.Else():
                    m.next = "OUTPUT"

            with m.State("OUTPUT"):
                m.d.comb += self.o.valid.eq(1)
                with m.If(self.o.ready):
                    m.next = "IDLE"

        return m
