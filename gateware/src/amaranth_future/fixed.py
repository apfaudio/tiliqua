# from https://github.com/amaranth-lang/amaranth/pull/1005
# slightly modified to work out-of-tree with Amaranth ~= 0.4

from amaranth.hdl import ast
from amaranth.utils import bits_for

__all__ = ["Shape", "SQ", "UQ", "Value", "Const"]

class Shape(ast.ShapeCastable):
    def __init__(self, i_or_f_width, f_width = None, /, *, signed):
        if f_width is None:
            self.i_width, self.f_width = 0, i_or_f_width
        else:
            self.i_width, self.f_width = i_or_f_width, f_width

        self.signed = bool(signed)

    @staticmethod
    def cast(shape, f_width=0):
        if not isinstance(shape, ast.Shape):
            raise TypeError(f"Object {shape!r} cannot be converted to a fixed.Shape")

        # i_width is what's left after subtracting f_width and sign bit, but can't be negative.
        i_width = max(0, shape.width - shape.signed - f_width)

        return Shape(i_width, f_width, signed = shape.signed)

    def as_shape(self):
        return ast.Shape(self.signed + self.i_width + self.f_width, self.signed)

    def __call__(self, target):
        return Value(self, target)

    def const(self, value):
        if value is None:
            value = 0
        return Const(value, self)._target

    def max(self):
        c = Const(0, self)
        c._value = c._max_value()
        return c

    def min(self):
        c = Const(0, self)
        c._value = c._min_value()
        return c

    def __repr__(self):
        return f"fixed.Shape({self.i_width}, {self.f_width}, signed={self.signed})"


class SQ(Shape):
    def __init__(self, *args):
        super().__init__(*args, signed = True)


class UQ(Shape):
    def __init__(self, *args):
        super().__init__(*args, signed = False)


class Value(ast.ValueCastable):
    def __init__(self, shape, target):
        self._shape = shape
        self._target = target

    @staticmethod
    def cast(value, f_width=0):
        return Shape.cast(value.shape(), f_width)(value)

    def round(self, f_width=0):
        # If we're increasing precision, extend with more fractional bits.
        if f_width > self.f_width:
            return Shape(self.i_width, f_width, signed = self.signed)(ast.Cat(ast.Const(0, f_width - self.f_width), self.sas_value()))
        
        # If we're reducing precision, truncate bits and add the top truncated bits for rounding.
        elif f_width < self.f_width:
            return Shape(self.i_width, f_width, signed = self.signed)(self.sas_value()[self.f_width - f_width:] + self.sas_value()[self.f_width - f_width - 1])

        return self

    def truncate(self, f_width=0):
        return Shape(self.i_width, f_width, signed = self.signed)(self.sas_value()[self.f_width - f_width:])

    @property
    def i_width(self):
        return self._shape.i_width

    @property
    def f_width(self):
        return self._shape.f_width

    @property
    def signed(self):
        return self._shape.signed

    @ast.ValueCastable.lowermethod
    def as_value(self):
        # FIXME For some reason lib.wiring breaks if we return
        # signed values from here, not sure why.
        return self._target

    def sas_value(self):
        if self.signed:
            return self._target.as_signed()
        return self._target

    def shape(self):
        return self._shape

    def eq(self, other):
        # Regular values are assigned directly to the underlying value.
        if isinstance(other, ast.Value):
            return self.sas_value().eq(other)

        # int and float are cast to fixed.Const.
        elif isinstance(other, int) or isinstance(other, float):
            other = Const(other, self.shape())

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        # Match precision.
        other = other.round(self.f_width)

        return self.sas_value().eq(other.sas_value())

    def __mul__(self, other):
        # Regular values are cast to fixed.Value
        if isinstance(other, ast.Value):
            other = Value.cast(other)

        # int are cast to fixed.Const
        elif isinstance(other, int):
            other = Const(other)

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        return Value.cast(self.sas_value() * other.sas_value(), self.f_width + other.f_width)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __add__(self, other):
        # Regular values are cast to fixed.Value
        if isinstance(other, ast.Value):
            other = Value.cast(other)

        # int are cast to fixed.Const
        elif isinstance(other, int):
            other = Const(other)

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        f_width = max(self.f_width, other.f_width)

        return Value.cast(self.round(f_width).sas_value() + other.round(f_width).sas_value(), f_width)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        # Regular values are cast to fixed.Value
        if isinstance(other, ast.Value):
            other = Value.cast(other)

        # int are cast to fixed.Const
        elif isinstance(other, int):
            other = Const(other)

        # Other value types are unsupported.
        elif not isinstance(other, Value):
            raise TypeError(f"Object {other!r} cannot be converted to a fixed.Value")

        f_width = max(self.f_width, other.f_width)

        return Value.cast(self.round(f_width).sas_value() - other.round(f_width).sas_value(), f_width)

    def __rsub__(self, other):
        return -self.__sub__(other)
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return Value.cast(-self.sas_value(), self.f_width)

    def __abs__(self):
        return Value.cast(abs(self.sas_value()), self.f_width)

    def __lshift__(self, other):
        if isinstance(other, int):
            if other < 0:
                raise ValueError("Shift amount cannot be negative")

            if other > self.f_width:
                return Value.cast(ast.Cat(ast.Const(0, other - self.f_width), self.sas_value()))
            else:
                return Value.cast(self.sas_value(), self.f_width - other)

        elif not isinstance(other, ast.Value):
            raise TypeError("Shift amount must be an integer value")

        if other.signed:
            raise TypeError("Shift amount must be unsigned")

        return Value.cast(self.sas_value() << other, self.f_width)

    def __rshift__(self, other):
        if isinstance(other, int):
            if other < 0:
                raise ValueError("Shift amount cannot be negative")

            return Value.cast(self.sas_value(), self.f_width + other)

        elif not isinstance(other, ast.Value):
            raise TypeError("Shift amount must be an integer value")

        if other.signed:
            raise TypeError("Shift amount must be unsigned")

        # Extend f_width by maximal shift amount.
        f_width = self.f_width + 2**other.width - 1

        return Value.cast(self.round(f_width).sas_value() >> other, f_width)

    def __lt__(self, other):
        return self.__sub__(other).sas_value() < 0

    def __ge__(self, other):
        return ~self.__lt__(other)

    def __repr__(self):
        return f"(fixedpoint {'SQ' if self.signed else 'UQ'}{self.i_width}.{self.f_width} {self._target!r})"


class Const(Value):
    def __init__(self, value, shape=None):

        if isinstance(value, float) or isinstance(value, int):
            num, den = value.as_integer_ratio()

        else:
            raise TypeError(f"Object {value!r} cannot be converted to a fixed.Const")

        # Determine smallest possible shape if not already selected.
        if shape is None:
            f_width = bits_for(den) - 1
            i_width = max(0, bits_for(abs(num)) - f_width)
            shape = Shape(i_width, f_width, signed = num < 0)

        # Scale value to given precision.
        if 2**shape.f_width > den:
            num *= 2**shape.f_width // den
        elif 2**shape.f_width < den:
            num = round(num / (den // 2**shape.f_width))
        value = num

        self._shape = shape

        if value > self._max_value():
            print("WARN fixed.Const: clamp", value, "to", self._max_value())
            value = self._max_value()
        if value < self._min_value():
            print("WARN fixed.Const: clamp", value, "to", self._min_value())
            value = self._min_value()

        self._value = value

    def _max_value(self):
        return 2**(self._shape.i_width +
                   self._shape.f_width) - 1

    def _min_value(self):
        if self._shape.signed:
            return -1 * 2**(self._shape.i_width +
                            self._shape.f_width)
        else:
            return 0

    @property
    def _target(self):
        return ast.Const(self._value, self._shape.as_shape())

    def as_integer_ratio(self):
        return self._value, 2**self.f_width

    def as_float(self):
        return self._value / 2**self.f_width

    # TODO: Operators
