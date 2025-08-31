import unittest

from amaranth import *
from amaranth.sim import *

from amaranth_future import fixed
from amaranth_future.fixed import SQ, UQ
from amaranth_future.fixed import Const as FConst


class TestFixedShape(unittest.TestCase):

    def test_shape_uq_init(self):

        s = UQ(6, 5)
        self.assertEqual(s.i_bits, 6)
        self.assertEqual(s.f_bits, 5)
        self.assertFalse(s.signed)

        s = UQ(0, 1)
        self.assertEqual(s.i_bits, 0)
        self.assertEqual(s.f_bits, 1)
        self.assertFalse(s.signed)

        s = UQ(1, 0)
        self.assertEqual(s.i_bits, 1)
        self.assertEqual(s.f_bits, 0)
        self.assertFalse(s.signed)

        with self.assertRaises(TypeError):
            UQ(-1, 0)

        with self.assertRaises(TypeError):
            UQ(1, -1)

    def test_shape_sq_init(self):

        s = SQ(6, 5)
        self.assertEqual(s.i_bits, 6)
        self.assertEqual(s.f_bits, 5)
        self.assertTrue(s.signed)

        s = SQ(1, 0)
        self.assertEqual(s.i_bits, 1)
        self.assertEqual(s.f_bits, 0)
        self.assertTrue(s.signed)

        with self.assertRaises(TypeError):
            SQ(0, 1)

        with self.assertRaises(TypeError):
            SQ(-1, 0)

        with self.assertRaises(TypeError):
            SQ(1, -1)

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

        self.assertEqual(UQ(2, 4).max().as_value().__repr__(), "(const 6'd63)")
        self.assertEqual(UQ(2, 4).min().as_value().__repr__(), "(const 6'd0)")
        self.assertEqual(UQ(2, 4).max().as_float(), 3.9375)
        self.assertEqual(UQ(2, 4).min().as_float(), 0)

        self.assertEqual(UQ(0, 2).max().as_value().__repr__(), "(const 2'd3)")
        self.assertEqual(UQ(0, 2).min().as_value().__repr__(), "(const 2'd0)")
        self.assertEqual(UQ(0, 2).max().as_float(), 0.75)
        self.assertEqual(UQ(0, 2).min().as_float(), 0)

        self.assertEqual(SQ(2, 4).max().as_value().__repr__(), "(const 6'sd31)")
        self.assertEqual(SQ(2, 4).min().as_value().__repr__(), "(const 6'sd-32)")
        self.assertEqual(SQ(2, 4).max().as_float(), 1.9375)
        self.assertEqual(SQ(2, 4).min().as_float(), -2)

        self.assertEqual(SQ(1, 0).max().as_value().__repr__(), "(const 1'sd0)")
        self.assertEqual(SQ(1, 0).min().as_value().__repr__(), "(const 1'sd-1)")
        self.assertEqual(SQ(1, 0).max().as_float(), 0)
        self.assertEqual(SQ(1, 0).min().as_float(), -1)

    def test_from_bits(self):

        self.assertEqual(UQ(2, 4).from_bits(0b100000).as_float(), 2.0)
        self.assertEqual(UQ(2, 4).from_bits(0b010000).as_float(), 1.0)
        self.assertEqual(UQ(2, 4).from_bits(0b001000).as_float(), 0.5)
        self.assertEqual(UQ(2, 4).from_bits(0b000100).as_float(), 0.25)
        self.assertEqual(UQ(2, 4).from_bits(0b000000).as_float(), 0)

        self.assertEqual(SQ(2, 4).from_bits(0b000000).as_float(), 0)
        self.assertEqual(SQ(2, 4).from_bits(0b000001).as_float(), 0.0625)
        self.assertEqual(SQ(2, 4).from_bits(0b111111).as_float(), -0.0625)
        self.assertEqual(SQ(2, 4).from_bits(0b010000).as_float(), 1)
        self.assertEqual(SQ(2, 4).from_bits(0b100000).as_float(), -2)

class TestFixedValue(unittest.TestCase):

    def assertFixedEqual(self, expression, expected, force_expected_shape=False):

        m = Module()
        output = Signal.like(expected if force_expected_shape else expression)
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
            FConst(1.5, UQ(3, 2)) * FConst(0.25, SQ(1, 2)),
            FConst(0.375, SQ(4, 4))
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 2)) * FConst(-0.25, SQ(1, 2)),
            FConst(-0.375, SQ(4, 4))
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 2)) * 3,
            FConst(4.5, UQ(5, 2))
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 2)) * -3,
            FConst(-4.5, SQ(6, 2))
        )

        with self.assertRaises(TypeError):

            self.assertFixedEqual(
                FConst(1.5, UQ(3, 2)) * 3.5,
                FConst(4.5, UQ(5, 2))
            )


    def test_add(self):

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) + FConst(0.25, SQ(1, 2)),
            FConst(1.75, SQ(5, 3)),
        )

        self.assertFixedEqual(
            FConst(0.5, UQ(3, 3)) + FConst(-0.75, SQ(1, 2)),
            FConst(-0.25, SQ(5, 3))
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) + FConst(0.25, UQ(1, 2)),
            FConst(1.75, UQ(4, 3)),
        )

    def test_sub(self):

        self.assertFixedEqual(
            FConst(1.5, SQ(3, 3)) - FConst(1.75, SQ(2, 2)),
            FConst(-0.25, SQ(4, 3)),
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) - FConst(2, UQ(2, 2)),
            FConst(-0.5, SQ(4, 3)),
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) - 3,
            FConst(-1.5, SQ(4, 3)),
        )

        self.assertFixedEqual(
            3 - FConst(1.5, UQ(3, 3)),
            FConst(1.5, SQ(5, 3)),
        )

    def test_shift(self):

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) << 1,
            FConst(3.0, UQ(4, 2)),
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) >> 1,
            FConst(0.75, UQ(2, 4)),
        )

        self.assertFixedEqual(
            FConst(1.5, SQ(3, 3)) >> 3,
            FConst(0.1875, SQ(1, 6)),
        )

        self.assertFixedEqual(
            FConst(1.5, SQ(3, 3)) >> Const(3, unsigned(2)),
            FConst(0.1875, SQ(1, 6)),
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) >> Const(3, unsigned(2)),
            FConst(0.1875, UQ(0, 6)),
        )

        self.assertFixedEqual(
            FConst(1.5, UQ(3, 3)) >> 3,
            FConst(0.1875, UQ(0, 6)),
        )

        self.assertFixedEqual(
            FConst(-1.5, SQ(3, 3)) << 4,
            FConst(-24.0, SQ(7, 0)),
        )

        with self.assertRaises(ValueError):
            FConst(1.5, UQ(3, 3)) << -1

        with self.assertRaises(ValueError):
            FConst(1.5, UQ(3, 3)) >> -1

        with self.assertRaises(TypeError):
            FConst(1.5, UQ(3, 3)) >> Const(-1, signed(2))

    def test_abs(self):

        # SQ -> UQ

        self.assertFixedEqual(
            abs(FConst(-1.5, SQ(3, 3))),
            FConst(1.5, UQ(3, 3))
        )

        self.assertFixedEqual(
            abs(FConst(-1, SQ(1, 2))),
            FConst(1, UQ(1, 2))
        )

        self.assertFixedEqual(
            abs(FConst(-4, SQ(3, 3))),
            FConst(4, UQ(3, 3))
        )

        # UQ -> UQ

        self.assertFixedEqual(
            abs(FConst(7, UQ(3, 3))),
            FConst(7, UQ(3, 3))
        )

    def test_neg(self):

        # SQ -> SQ

        self.assertFixedEqual(
            -FConst(-1.5, SQ(3, 3)),
            FConst(1.5, SQ(4, 3))
        )

        self.assertFixedEqual(
            -FConst(-1, SQ(1, 2)),
            FConst(1, SQ(2, 2))
        )

        self.assertFixedEqual(
            -FConst(1.5, SQ(2, 2)),
            FConst(-1.5, SQ(3, 2))
        )

        # UQ -> SQ

        self.assertFixedEqual(
            -FConst(1.5, UQ(2, 2)),
            FConst(-1.5, SQ(3, 2))
        )

    def test_clamp(self):

        self.assertFixedEqual(
            FConst(3, SQ(3, 3)).clamp(
                FConst(-1),
                FConst(1)),
            FConst(1, SQ(3, 3))
        )

        self.assertFixedEqual(
            FConst(3, SQ(3, 3)).clamp(
                FConst(-3),
                FConst(-2)),
            FConst(-2, SQ(3, 3))
        )

        self.assertFixedEqual(
            FConst(3, SQ(3, 3)).clamp(
                FConst(-0.5),
                FConst(0.5)),
            FConst(0.5, SQ(3, 3))
        )

    def test_saturate(self):

        # SQ -> SQ

        self.assertFixedEqual(
            FConst(-2, SQ(3, 3)).saturate(SQ(1, 1)),
            FConst(-1, SQ(1, 1))
        )

        self.assertFixedEqual(
            FConst(-10.25, SQ(5, 3)).saturate(SQ(3, 1)),
            FConst(-4, SQ(3, 1))
        )

        self.assertFixedEqual(
            FConst(14.25, SQ(8, 3)).saturate(SQ(4, 2)),
            FConst(7.75, SQ(4, 2))
        )

        self.assertFixedEqual(
            FConst(0.995, SQ(1, 8)).saturate(SQ(1, 4)),
            FConst(0.9375, SQ(1, 4))
        )

        with self.assertRaises(ValueError):
            FConst(0, SQ(8, 0)).saturate(SQ(9, 0)),

        # XXX: this 'odd' behaviour is an artifact of truncation rounding,
        # and should be revisited when we have more rounding strategies.

        self.assertFixedEqual(
            FConst(-0.995, SQ(2, 8)).saturate(SQ(2, 4)),
            FConst(-1, SQ(2, 4))
        )

        # UQ -> UQ

        self.assertFixedEqual(
            FConst(15, UQ(5, 2)).saturate(UQ(3, 1)),
            FConst(7.5, UQ(3, 1))
        )

        # SQ -> UQ

        self.assertFixedEqual(
            FConst(14.25, SQ(8, 3)).saturate(UQ(2, 2)),
            FConst(3.75, UQ(2, 2))
        )

        self.assertFixedEqual(
            FConst(-14.25, SQ(8, 3)).saturate(UQ(2, 2)),
            FConst(0, UQ(2, 2))
        )

        # UQ -> SQ

        self.assertFixedEqual(
            FConst(255, UQ(8, 2)).saturate(SQ(8, 2)),
            FConst(127.75, SQ(8, 2))
        )

    def test_lt(self):

        self.assertFixedBool(
            FConst(0.75, SQ(1, 2)) < FConst(0.5, SQ(1, 2)), False)
        self.assertFixedBool(
            FConst(0.5, SQ(1, 2)) < FConst(0.75, SQ(1, 2)), True)
        self.assertFixedBool(
            FConst(0.75, SQ(1, 2)) < FConst(-0.5, SQ(1, 2)), False)
        self.assertFixedBool(
            FConst(-0.5, SQ(1, 2)) < FConst(0.75, SQ(1, 2)), True)
        self.assertFixedBool(
            FConst(-0.25, SQ(1, 2)) < FConst(0, SQ(1, 2)), True)
        self.assertFixedBool(
            FConst(0.25, SQ(1, 2)) < FConst(0, SQ(1, 2)), False)
        self.assertFixedBool(
            FConst(-0.25, SQ(1, 2)) < FConst(0), True)
        self.assertFixedBool(
            FConst(0.25, SQ(1, 2)) < FConst(0), False)
        self.assertFixedBool(
            FConst(0, SQ(1, 2)) < FConst(0), False)
        self.assertFixedBool(
            FConst(0) < FConst(0), False)
        self.assertFixedBool(
            FConst(0) < 1, True)
        self.assertFixedBool(
            FConst(0) < -1, False)

    def test_equality(self):

        self.assertFixedBool(FConst(0) == 0, True)
        self.assertFixedBool(FConst(0) == FConst(0), True)
        self.assertFixedBool(FConst(0.5) == FConst(0.5), True)
        self.assertFixedBool(FConst(0.5) == FConst(0.75), False)
        self.assertFixedBool(FConst(0.501) == FConst(0.5), False)

        with self.assertRaises(TypeError):
            self.assertFixedBool(0.5 == FConst(0.5), False)

    def test_eq(self):

        self.assertFixedEqual(
            FConst(-1, SQ(2, 1)),
            FConst(-1, SQ(5, 1)),
            force_expected_shape=True
        )

        self.assertFixedEqual(
            SQ(1, 1).max(),
            FConst(0.5, SQ(5, 1)),
            force_expected_shape=True
        )

        self.assertFixedEqual(
            SQ(1, 1).max(),
            FConst(0.5, SQ(5, 1)),
            force_expected_shape=True
        )

        self.assertFixedEqual(
            FConst(0.25, SQ(5, 5)),
            FConst(0.0, SQ(5, 1)),
            force_expected_shape=True
        )

        # XXX: truncation rounding again

        self.assertFixedEqual(
            FConst(-0.25, SQ(5, 5)),
            FConst(-0.5, SQ(5, 1)),
            force_expected_shape=True
        )

        # XXX: .eq() from SQ <-> UQ may over/underflow.
        # SQ -> UQ: may overflow if SQ is negative
        # UQ -> SQ: may overflow if i_bits (UQ) >= i_bits (SQ)
        # same signedness: may overflow if i_bits > i_bits
        # Should these really be prohibited completely?

        self.assertFixedEqual(
            FConst(-10, SQ(5, 2)),
            FConst(22, UQ(5, 2)),
            force_expected_shape=True
        )

        self.assertFixedEqual(
            FConst(15, UQ(4, 2)),
            FConst(-1, SQ(4, 2)),
            force_expected_shape=True
        )


    def test_float_size_determination(self):

        self.assertFixedEqual(
            FConst(0.03125),
            FConst(0.03125, UQ(0, 5))
        )

        self.assertFixedEqual(
            FConst(-0.03125),
            FConst(-0.03125, SQ(1, 5))
        )

        self.assertFixedEqual(
            FConst(-0.5),
            FConst(-0.5, SQ(1, 1))
        )

        self.assertFixedEqual(
            FConst(10),
            FConst(10, UQ(4, 0))
        )

        self.assertFixedEqual(
            FConst(-10),
            FConst(-10, SQ(5, 0))
        )
