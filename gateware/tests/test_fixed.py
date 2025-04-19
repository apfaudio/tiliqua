import unittest

import math
import itertools

from amaranth              import *
from amaranth.sim          import *
from amaranth_future       import fixed

class TestFixedShape(unittest.TestCase):

    def test_shape_uq_init(self):

        s = fixed.UQ(6, 5)
        self.assertEqual(s.i_bits, 6)
        self.assertEqual(s.f_bits, 5)
        self.assertFalse(s.signed)

        s = fixed.UQ(0, 1)
        self.assertEqual(s.i_bits, 0)
        self.assertEqual(s.f_bits, 1)
        self.assertFalse(s.signed)

        s = fixed.UQ(1, 0)
        self.assertEqual(s.i_bits, 1)
        self.assertEqual(s.f_bits, 0)
        self.assertFalse(s.signed)

        with self.assertRaises(TypeError):
            fixed.UQ(-1, 0)

        with self.assertRaises(TypeError):
            fixed.UQ(1, -1)

    def test_shape_sq_init(self):

        s = fixed.SQ(6, 5)
        self.assertEqual(s.i_bits, 6)
        self.assertEqual(s.f_bits, 5)
        self.assertTrue(s.signed)

        s = fixed.SQ(1, 0)
        self.assertEqual(s.i_bits, 1)
        self.assertEqual(s.f_bits, 0)
        self.assertTrue(s.signed)

        with self.assertRaises(TypeError):
            fixed.SQ(0, 1)

        with self.assertRaises(TypeError):
            fixed.SQ(-1, 0)

        with self.assertRaises(TypeError):
            fixed.SQ(1, -1)

    def test_cast_from_shape(self):

        s = fixed.Shape.cast(signed(12), f_bits=4)
        self.assertEqual(s.i_bits, 8)
        self.assertEqual(s.f_bits, 4)
        self.assertTrue(s.signed)

        with self.assertRaises(TypeError):
            fixed.Shape.cast("not a shape")

    def test_cast_to_shape(self):

        fixed_shape = fixed.Shape(unsigned(11), f_bits=5)
        hdl_shape = fixed_shape.as_shape()
        self.assertEqual(hdl_shape.width, 11)
        self.assertFalse(hdl_shape.signed)

    def test_min_max(self):

        self.assertEqual(fixed.UQ(2, 4).max().as_value().__repr__(), "(const 6'd63)")
        self.assertEqual(fixed.UQ(2, 4).min().as_value().__repr__(), "(const 6'd0)")
        self.assertEqual(fixed.UQ(2, 4).max().as_float(), 3.9375)
        self.assertEqual(fixed.UQ(2, 4).min().as_float(), 0)

        self.assertEqual(fixed.UQ(0, 2).max().as_value().__repr__(), "(const 2'd3)")
        self.assertEqual(fixed.UQ(0, 2).min().as_value().__repr__(), "(const 2'd0)")
        self.assertEqual(fixed.UQ(0, 2).max().as_float(), 0.75)
        self.assertEqual(fixed.UQ(0, 2).min().as_float(), 0)

        self.assertEqual(fixed.SQ(2, 4).max().as_value().__repr__(), "(const 6'sd31)")
        self.assertEqual(fixed.SQ(2, 4).min().as_value().__repr__(), "(const 6'sd-32)")
        self.assertEqual(fixed.SQ(2, 4).max().as_float(), 1.9375)
        self.assertEqual(fixed.SQ(2, 4).min().as_float(), -2)

        self.assertEqual(fixed.SQ(1, 0).max().as_value().__repr__(), "(const 1'sd0)")
        self.assertEqual(fixed.SQ(1, 0).min().as_value().__repr__(), "(const 1'sd-1)")
        self.assertEqual(fixed.SQ(1, 0).max().as_float(), 0)
        self.assertEqual(fixed.SQ(1, 0).min().as_float(), -1)

    def test_from_bits(self):

        self.assertEqual(fixed.UQ(2, 4).from_bits(0b10000).as_float(), 1.0)
        self.assertEqual(fixed.UQ(2, 4).from_bits(0b01000).as_float(), 0.5)
        self.assertEqual(fixed.UQ(2, 4).from_bits(0b00100).as_float(), 0.25)

class TestFixedValue(unittest.TestCase):

    def assertFixedEqual(self, expression, expected):

        m = Module()
        output = Signal.like(expected)
        m.d.comb += output.eq(expression)

        async def testbench(ctx):
            out = ctx.get(output)
            self.assertEqual(out.i_bits, expected.i_bits)
            self.assertEqual(out.f_bits, expected.f_bits)
            self.assertEqual(out.as_float(), expected.as_float())
            self.assertEqual(out.as_value().value, expected.as_value().value)
            self.assertEqual(out.signed, expected.signed)

        sim = Simulator(m)
        sim.add_testbench(testbench)
        sim.run()

    def assertFixedBool(self, expression, expected):

        m = Module()
        output = Signal.like(expression)
        m.d.comb += output.eq(expression)

        async def testbench(ctx):
            self.assertEqual(ctx.get(output), 1 if expected else 0)

        sim = Simulator(m)
        sim.add_testbench(testbench)
        sim.run()

    def test_mul(self):

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 2)) * fixed.Const(0.25, fixed.SQ(1, 2)),
            fixed.Const(0.375, fixed.SQ(4, 4))
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 2)) * fixed.Const(-0.25, fixed.SQ(1, 2)),
            fixed.Const(-0.375, fixed.SQ(4, 4))
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 2)) * 3,
            fixed.Const(4.5, fixed.UQ(5, 2))
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 2)) * -3,
            fixed.Const(-4.5, fixed.SQ(6, 2))
        )

        with self.assertRaises(TypeError):

            self.assertFixedEqual(
                fixed.Const(1.5, fixed.UQ(3, 2)) * 3.5,
                fixed.Const(4.5, fixed.UQ(5, 2))
            )


    def test_add(self):

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 3)) + fixed.Const(0.25, fixed.SQ(1, 2)),
            fixed.Const(1.75, fixed.SQ(5, 3)),
        )

        self.assertFixedEqual(
            fixed.Const(0.5, fixed.UQ(3, 3)) + fixed.Const(-0.75, fixed.SQ(1, 2)),
            fixed.Const(-0.25, fixed.SQ(5, 3))
        )

    def test_shift(self):

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 3)) << 1,
            fixed.Const(3.0, fixed.UQ(4, 2)),
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 3)) >> 1,
            fixed.Const(0.75, fixed.UQ(2, 4)),
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.SQ(3, 3)) >> 3,
            fixed.Const(0.1875, fixed.SQ(1, 6)),
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.SQ(3, 3)) >> Const(3, unsigned(2)),
            fixed.Const(0.1875, fixed.SQ(1, 6)),
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 3)) >> Const(3, unsigned(2)),
            fixed.Const(0.1875, fixed.UQ(0, 6)),
        )

        self.assertFixedEqual(
            fixed.Const(1.5, fixed.UQ(3, 3)) >> 3,
            fixed.Const(0.1875, fixed.UQ(0, 6)),
        )

        with self.assertRaises(ValueError):
            fixed.Const(1.5, fixed.UQ(3, 3)) << -1

        with self.assertRaises(ValueError):
            fixed.Const(1.5, fixed.UQ(3, 3)) >> -1

        with self.assertRaises(TypeError):
            fixed.Const(1.5, fixed.UQ(3, 3)) >> Const(-1, signed(2))

    def test_abs(self):

        self.assertFixedEqual(
            abs(fixed.Const(-1.5, fixed.SQ(3, 3))),
            fixed.Const(1.5, fixed.UQ(3, 3))
        )

        self.assertFixedEqual(
            abs(fixed.Const(-1, fixed.SQ(1, 2))),
            fixed.Const(1, fixed.UQ(1, 2))
        )

    def test_neg(self):

        self.assertFixedEqual(
            -fixed.Const(-1.5, fixed.SQ(3, 3)),
            fixed.Const(1.5, fixed.SQ(4, 3))
        )

        self.assertFixedEqual(
            -fixed.Const(-1, fixed.SQ(1, 2)),
            fixed.Const(1, fixed.SQ(2, 2))
        )

    def test_clamp(self):

        self.assertFixedEqual(
            fixed.Const(3, fixed.SQ(3, 3)).clamp(
                fixed.Const(-1),
                fixed.Const(1)),
            fixed.Const(1, fixed.SQ(3, 3))
        )

        self.assertFixedEqual(
            fixed.Const(3, fixed.SQ(3, 3)).clamp(
                fixed.Const(-3),
                fixed.Const(-2)),
            fixed.Const(-2, fixed.SQ(3, 3))
        )

        self.assertFixedEqual(
            fixed.Const(3, fixed.SQ(3, 3)).clamp(
                fixed.Const(-0.5),
                fixed.Const(0.5)),
            fixed.Const(0.5, fixed.SQ(3, 3))
        )

    def test_saturate(self):

        self.assertFixedEqual(
            fixed.Const(-2, fixed.SQ(3, 3)).saturate(fixed.SQ(1, 1)),
            fixed.Const(-1, fixed.SQ(1, 1))
        )

        self.assertFixedEqual(
            fixed.Const(-10.25, fixed.SQ(5, 3)).saturate(fixed.SQ(3, 1)),
            fixed.Const(-4, fixed.SQ(3, 1))
        )

        self.assertFixedEqual(
            fixed.Const(14.25, fixed.SQ(8, 3)).saturate(fixed.SQ(4, 2)),
            fixed.Const(7.75, fixed.SQ(4, 2))
        )

        self.assertFixedEqual(
            fixed.Const(14.25, fixed.SQ(8, 3)).saturate(fixed.UQ(2, 2)),
            fixed.Const(3.75, fixed.UQ(2, 2))
        )

        self.assertFixedEqual(
            fixed.Const(-14.25, fixed.SQ(8, 3)).saturate(fixed.UQ(2, 2)),
            fixed.Const(0, fixed.UQ(2, 2))
        )

    def test_lt(self):

        self.assertFixedBool(
            fixed.Const(0.75, fixed.SQ(1, 2)) < fixed.Const(0.5, fixed.SQ(1, 2)), False)
        self.assertFixedBool(
            fixed.Const(0.5, fixed.SQ(1, 2)) < fixed.Const(0.75, fixed.SQ(1, 2)), True)
        self.assertFixedBool(
            fixed.Const(0.75, fixed.SQ(1, 2)) < fixed.Const(-0.5, fixed.SQ(1, 2)), False)
        self.assertFixedBool(
            fixed.Const(-0.5, fixed.SQ(1, 2)) < fixed.Const(0.75, fixed.SQ(1, 2)), True)
        self.assertFixedBool(
            fixed.Const(-0.25, fixed.SQ(1, 2)) < fixed.Const(0, fixed.SQ(1, 2)), True)
        self.assertFixedBool(
            fixed.Const(0.25, fixed.SQ(1, 2)) < fixed.Const(0, fixed.SQ(1, 2)), False)
        self.assertFixedBool(
            fixed.Const(-0.25, fixed.SQ(1, 2)) < fixed.Const(0), True)
        self.assertFixedBool(
            fixed.Const(0.25, fixed.SQ(1, 2)) < fixed.Const(0), False)
        self.assertFixedBool(
            fixed.Const(0, fixed.SQ(1, 2)) < fixed.Const(0), False)
        self.assertFixedBool(
            fixed.Const(0) < fixed.Const(0), False)
        self.assertFixedBool(
            fixed.Const(0) < 1, True)
        self.assertFixedBool(
            fixed.Const(0) < -1, False)

    def test_float_size_determination(self):

        self.assertFixedEqual(
            fixed.Const(0.03125),
            fixed.Const(0.03125, fixed.UQ(0, 5))
        )

        self.assertFixedEqual(
            fixed.Const(-0.03125),
            fixed.Const(-0.03125, fixed.SQ(1, 5))
        )

        self.assertFixedEqual(
            fixed.Const(-0.5),
            fixed.Const(-0.5, fixed.SQ(1, 1))
        )

        self.assertFixedEqual(
            fixed.Const(10),
            fixed.Const(10, fixed.UQ(4, 0))
        )

        self.assertFixedEqual(
            fixed.Const(-10),
            fixed.Const(-10, fixed.SQ(5, 0))
        )
