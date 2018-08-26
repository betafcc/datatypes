from abc import ABCMeta


class LazyOperations:
    def __add__(self, other):
        return Add(self, other)

    def __radd__(self, other):
        return Add(other, self)

    def __sub__(self, other):
        return Sub(self, other)

    def __rsub__(self, other):
        return Sub(other, self)

    def __mul__(self, other):
        return Mul(self, other)

    def __rmul__(self, other):
        return Mul(other, self)

    def __truediv__(self, other):
        return TrueDiv(self, other)

    def __rtruediv__(self, other):
        return TrueDiv(other, self)

    def __getattr__(self, attr):
        return GetAttr(self, attr)

    def __getitem__(self, item):
        return GetItem(self, item)

    def __call__(self, *args, **kwargs):
        return Call(self, *args, **kwargs)


class Expression(LazyOperations, metaclass=ABCMeta):
    pass


class Associative(Expression):
    def __init__(self, *args):
        self._args = args

    def __init_subclass__(cls, *, symbol, method, rmethod=None):
        setattr(cls, "_symbol", symbol)
        setattr(cls, method, _associate)
        if method.startswith("__") and method.endswith("__"):
            setattr(cls, f"__r{method[2:]}", _rassociate)

    def __repr__(self):
        _ = map(repr, self._args)
        _ = f" {self._symbol} ".join(_)
        return f"({_})"


def _associate(self, other):
    lcls, rcls = self.__class__, other.__class__

    if lcls == rcls:
        return lcls(*self._args, *other._args)

    return lcls(*self._args, other)


def _rassociate(self, other):
    return self.__class__(other, *self._args)


class Add(Associative, symbol="+", method="__add__"):
    pass


class Sub(Associative, symbol="-", method="__sub__"):
    pass


class Mul(Associative, symbol="*", method="__mul__"):
    pass


class Pow(Associative, symbol="**", method="__pow__"):
    pass


class MatMul(Associative, symbol="@", method="__matmul__"):
    pass


class TrueDiv(Associative, symbol="/", method="__truediv__"):
    pass


class GetAttr(Expression):
    def __init__(self, obj, attr):
        self._obj = obj
        self._attr = attr

    def __repr__(self):
        return f"{self._obj}.{self._attr}"


class GetItem(Expression):
    def __init__(self, obj, item):
        self._obj = obj
        self._item = item

    def __repr__(self):
        item = self._item
        acc = repr(self._obj) + "["

        if isinstance(item, slice):
            return acc + _slice_repr(item) + "]"

        if not isinstance(item, tuple):
            return acc + repr(item) + "]"

        else:
            return acc + ",".join(map(_slice_repr, item)) + "]"


def _slice_repr(s):
    if not isinstance(s, slice):
        return repr(s)

    _ = (s.start, s.stop, s.step)
    _ = (repr(v) if v is not None else "" for v in _)
    return ":".join(_)


class Call(Expression):
    def __init__(self, f, *args, **kwargs):
        self._f = f
        self._args = args
        self._kwargs = kwargs

    def __repr__(self):
        args, kwargs = self._args, self._kwargs

        acc = repr(self._f) + "("

        if args:
            args_repr = ", ".join(map(repr, args))
        if kwargs:
            kwargs_repr = ", ".join(f"{k}={v}" for k, v in kwargs.items())

        if kwargs and args:
            acc += f"{args_repr}, {kwargs_repr}"
        elif args:
            acc += args_repr
        elif kwargs:
            acc += kwargs_repr

        return acc + ")"
