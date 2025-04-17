# from https://github.com/amaranth-lang/amaranth/pull/1005
# slightly modified to work out-of-tree with Amaranth ~= 0.4

from amaranth import hdl
from amaranth.utils import bits_for

__all__ = ["Shape", "SQ", "UQ", "Value", "Const"]

class Shape(hdl.ShapeCastable):

    def __init__(self, shape, f_bits=0):
        self._storage_shape = shape
        self.i_bits, self.f_bits = shape.width-f_bits, f_bits
        if shape.signed:
            assert self.i_bits > 0

    @property
    def signed(self):
        return self._storage_shape.signed

    @staticmethod
    def cast(shape, f_bits=0):
        if not isinstance(shape, hdl.Shape):
            raise TypeError(f"Object {shape!r} cannot be converted to a fixed.Shape")
        return Shape(shape, f_bits)

    def const(self, value):
        if value is None:
            value = 0
        return Const(value, self)._target

    def as_shape(self):
        return self._storage_shape

    def __call__(self, target):
        return Value(self, target)

    def min(self):
        c = Const(0, self)
        c._value = c._min_value()
        return c

    def max(self):
        c = Const(0, self)
        c._value = c._max_value()
        return c

    def from_bits(self, raw):
        c = Const(0, self)
        c._value = raw
        return c

    def __repr__(self):
        return f"fixed.Shape({self._storage_shape}, f_bits={self.f_bits})"


class SQ(Shape):
    def __init__(self, i_bits, f_bits):
        super().__init__(hdl.Shape(i_bits + f_bits, signed=True), f_bits)


class UQ(Shape):
    def __init__(self, i_bits, f_bits):
        super().__init__(hdl.Shape(i_bits + f_bits, signed=False), f_bits)


class Value(hdl.ValueCastable):
    def __init__(self, shape, target):
        self._shape = shape
        self._target = target

    @property
    def signed(self):
        return self._shape.signed

    @staticmethod
    def cast(value, f_bits=0):
        return Shape.cast(value.shape(), f_bits)(value)

    @property
    def i_bits(self):
        return self._shape.i_bits

    @property
    def f_bits(self):
        return self._shape.f_bits

    def shape(self):
        return self._shape

    def as_value(self):
        return self._target

    def eq(self, other):

        # Regular values are assigned directly to the underlying value.
        if isinstance(other, hdl.Value):
            return self.numerator().eq(other)

        # int and float are cast to fixed.Const.
        elif isinstance(other, int) or isinstance(other, float):
            other = Const(other, self.shape())

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        other = other.reshape(self.f_bits)

        return self.numerator().eq(other.numerator())


    def numerator(self):
        # Adding an `s ( )` signedness wrapper in `as_value` when needed
        # breaks lib.wiring for some reason. How to combine numerator() and
        # `as_value()`?.
        if self.signed:
            return self._target.as_signed()
        return self._target

    def reshape(self, f_bits):

        # If we're increasing precision, extend with more fractional bits. If we're
        # reducing precision, truncate bits.

        shape = hdl.Shape(self.i_bits + f_bits, signed=self.signed)

        if f_bits > self.f_bits:
            return Shape(shape, f_bits)(hdl.Cat(hdl.Const(0, f_bits - self.f_bits), self.numerator()))
        else:
            return Shape(shape, f_bits)(self.numerator()[self.f_bits - f_bits:])

    def __mul__(self, other):
        # Regular values are cast to fixed.Value
        if isinstance(other, hdl.Value):
            other = Value.cast(other)

        # int are cast to fixed.Const
        elif isinstance(other, int):
            other = Const(other)

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        return Value.cast(self.numerator() * other.numerator(), self.f_bits + other.f_bits)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):

        # Regular values are cast to fixed.Value
        if isinstance(other, hdl.Value):
            other = Value.cast(other)

        # int are cast to fixed.Const
        elif isinstance(other, int):
            other = Const(other)

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        f_bits  = max(self.f_bits, other.f_bits)

        return Value.cast(self.reshape(f_bits).numerator() +
                          other.reshape(f_bits).numerator(), f_bits)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        # Regular values are cast to fixed.Value
        if isinstance(other, hdl.Value):
            other = Value.cast(other)

        # int are cast to fixed.Const
        elif isinstance(other, int):
            other = Const(other)

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        f_bits = max(self.f_bits, other.f_bits)

        return Value.cast(self.reshape(f_bits).numerator() -
                          other.reshape(f_bits).numerator(), f_bits)

    def __rsub__(self, other):
        return -self.__sub__(other)

    def __pos__(self):
        return self

    def __neg__(self):
        return Value.cast(-self.numerator(), self.f_bits)

    def __abs__(self):
        return Value.cast(abs(self.numerator()), self.f_bits)

    def __lshift__(self, other):
        if isinstance(other, int):
            if other < 0:
                raise ValueError("Shift amount cannot be negative")

            if other > self.f_bits:
                return Value.cast(hdl.Cat(hdl.Const(0, other - self.f_bits), self.numerator()))
            else:
                return Value.cast(self.numerator(), self.f_bits - other)

        elif not isinstance(other, hdl.Value):
            raise TypeError("Shift amount must be an integer value")

        if other.signed:
            raise TypeError("Shift amount must be unsigned")

        return Value.cast(self.numerator() << other, self.f_bits)

    def __rshift__(self, other):
        if isinstance(other, int):
            if other < 0:
                raise ValueError("Shift amount cannot be negative")

            return Value.cast(self.numerator(), self.f_bits + other)

        elif not isinstance(other, hdl.Value):
            raise TypeError("Shift amount must be an integer value")

        if other.signed:
            raise TypeError("Shift amount must be unsigned")

        # Extend f_bits by maximal shift amount.
        f_bits = self.f_bits + 2**other.bits - 1

        return Value.cast(self.reshape(f_bits).numerator() >> other, f_bits)

    def __lt__(self, other):
        if isinstance(other, hdl.Value):
            other = Value.cast(other)
        elif isinstance(other, int):
            other = Const(other)
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")
        f_bits = max(self.f_bits, other.f_bits)
        return self.reshape(f_bits).numerator() < other.reshape(f_bits).numerator()

    def __ge__(self, other):
        return ~self.__lt__(other)

    def __eq__(self, other):
        if isinstance(other, hdl.Value):
            other = Value.cast(other)
        elif isinstance(other, int):
            other = Const(other)
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")
        f_bits = max(self.f_bits, other.f_bits)
        return self.reshape(f_bits).numerator() == other.reshape(f_bits).numerator()

    def __repr__(self):
        return f"fixed.{'SQ' if self.signed else 'UQ'}({self.i_bits}, {self.f_bits}) {self._target!r}"


class Const(Value):
    def __init__(self, value, shape=None, clamp=False):

        if isinstance(value, float) or isinstance(value, int):
            num, den = value.as_integer_ratio()
        elif isinstance(value, Const):
            # FIXME: Memory inits seem to construct a fixed.Const with fixed.Const
            self._shape = value._shape
            self._value = value._value
            return
        else:
            raise TypeError(f"Object {value!r} cannot be converted to a fixed.Const")

        # Determine smallest possible shape if not already selected.
        if shape is None:
            signed = num < 0
            f_bits = bits_for(den) - 1
            i_bits = max(0, bits_for(abs(num)) - f_bits)
            shape = SQ(i_bits+1, f_bits) if signed else UQ(i_bits, f_bits)

        # Scale value to given precision.
        if 2**shape.f_bits > den:
            num *= 2**shape.f_bits // den
        elif 2**shape.f_bits < den:
            num = round(num / (den // 2**shape.f_bits))
        value = num

        self._shape = shape

        if value > self._max_value():
            if clamp:
                value = self._max_value()
            else:
                raise TypeError(f"{value!r} does not fit in {shape!r}, max is {self._max_value()}."
                                f"Try using `fixed.Const(..., clamp=True)` to keep it within bounds.")

        if value < self._min_value():
            if clamp:
                value = self._min_value()
            else:
                raise TypeError(f"{value!r} does not fit in {shape!r}, min is {self._min_value()}."
                                f"Try using `fixed.Const(..., clamp=True)` to keep it within bounds.")

        self._value = value

    def _max_value(self):

        return 2**(self._shape.i_bits +
                   self._shape.f_bits - (1 if self.signed else 0)) - 1

    def _min_value(self):
        if self._shape.signed:
            return -1 * 2**(self._shape.i_bits +
                            self._shape.f_bits - 1)
        else:
            return 0

    @property
    def _target(self):
        return hdl.Const(self._value, self._shape.as_shape())

    def as_integer_ratio(self):
        return self._value, 2**self.f_bits

    def as_float(self):
        if self._value > self._max_value():
            v = self._min_value() + self._value - self._max_value()
        else:
            v = self._value
        return v / 2**self.f_bits

    # TODO: Operators on constants
