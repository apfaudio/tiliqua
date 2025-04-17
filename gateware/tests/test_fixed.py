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

        # Try casting with invalid input
        with self.assertRaises(TypeError):
            fixed.Shape.cast("not a shape")

    def test_cast_to_shape(self):

        fixed_shape = fixed.Shape(unsigned(11), f_bits=5)
        hdl_shape = fixed_shape.as_shape()
        self.assertEqual(hdl_shape.width, 11)
        self.assertFalse(hdl_shape.signed)

class TestFixedValue(unittest.TestCase):

    def assertBinaryOp(self, operator, const_a, const_b, expected):

        m = Module()
        result = getattr(const_a, operator)(const_b)
        output = Signal.like(result)
        m.d.comb += output.eq(result)

        async def testbench(ctx):
            out = ctx.get(output)
            self.assertEqual(out.i_bits, expected.i_bits)
            self.assertEqual(out.f_bits, expected.f_bits)
            self.assertEqual(out.as_float(), expected.as_float())
            self.assertEqual(out.as_value().value, expected.as_value().value)

        sim = Simulator(m)
        sim.add_testbench(testbench)
        with sim.write_vcd(vcd_file=open("test_fixed_sim.vcd", "w")):
            sim.run()

    def test_mul(self):

        a = Signal(fixed.UQ(3, 2))
        b = Signal(fixed.SQ(1, 2))
        result = a * b

        self.assertEqual(result.i_bits, a.i_bits + b.i_bits)
        self.assertEqual(result.f_bits, a.f_bits + b.f_bits)
        self.assertTrue(result.signed)

        self.assertBinaryOp(
            '__mul__',
            fixed.Const(1.5, fixed.UQ(3, 2)),
            fixed.Const(0.25, fixed.SQ(1, 2)),
            fixed.Const(0.375, fixed.SQ(4, 4)),
        )

        self.assertBinaryOp(
            '__mul__',
            fixed.Const(1.5, fixed.UQ(3, 2)),
            fixed.Const(-0.25, fixed.SQ(1, 2)),
            fixed.Const(-0.375, fixed.SQ(4, 4)),
        )

    def test_add(self):

        a = Signal(fixed.UQ(3, 2))
        b = Signal(fixed.SQ(1, 2))
        result = a + b

        self.assertEqual(result.i_bits, a.i_bits + b.i_bits + 1)
        self.assertEqual(result.f_bits, max(a.f_bits, b.f_bits))
        self.assertTrue(result.signed)

        self.assertBinaryOp(
            '__add__',
            fixed.Const(1.5, fixed.UQ(3, 2)),
            fixed.Const(0.25, fixed.SQ(1, 2)),
            fixed.Const(1.75, fixed.SQ(5, 2)),
        )

        self.assertBinaryOp(
            '__add__',
            fixed.Const(0.5, fixed.UQ(3, 2)),
            fixed.Const(-0.75, fixed.SQ(1, 2)),
            fixed.Const(-0.25, fixed.SQ(5, 2)),
        )

class TestFixedConst(unittest.TestCase):

    def test_min_max(self):

        self.assertEqual(fixed.UQ(2, 4).max().as_value().__repr__(), "(const 6'd63)")
        self.assertEqual(fixed.UQ(2, 4).min().as_value().__repr__(), "(const 6'd0)")
        self.assertEqual(fixed.UQ(2, 4).max().as_float(), 3.9375)
        self.assertEqual(fixed.UQ(2, 4).min().as_float(), 0)

        self.assertEqual(fixed.SQ(2, 4).max().as_value().__repr__(), "(const 6'sd31)")
        self.assertEqual(fixed.SQ(2, 4).min().as_value().__repr__(), "(const 6'sd-32)")
        self.assertEqual(fixed.SQ(2, 4).max().as_float(), 1.9375)
        self.assertEqual(fixed.SQ(2, 4).min().as_float(), -2)
