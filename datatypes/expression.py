import operator
from abc import ABCMeta
from functools import reduce
from inspect import Signature

from .util import slice_repr
from .protocols import substitute, placeholders, run


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

    def __matmul__(self, other):
        return MatMul(self, other)

    def __rmatmul__(self, other):
        return MatMul(other, self)

    def __pow__(self, other):
        return Pow(self, other)

    def __rpow__(self, other):
        return Pow(other, self)

    def __or__(self, other):
        return Or(self, other)

    def __ror__(self, other):
        return Or(other, self)

    def __getattr__(self, attr):
        return GetAttr(self, attr)

    def __getitem__(self, item):
        return GetItem(self, item)

    def __call__(self, *args, **kwargs):
        return Call(self, *args, **kwargs)

    def __invert__(self):
        return make_function(self)


class Shifts:
    def __lshift__(self, other):
        if isinstance(other, LazyArguments):
            return other >> self
        return Call(self, other)

    def __rlshift__(self, other):
        return Call(other, self)

    def __rshift__(self, other):
        return Call(other, self)

    def __rrshift__(self, other):
        return Call(self, other)


class LazyArguments:
    def __init__(self, *args, **kwargs):
        self.__args = args
        self.__kwargs = kwargs

    def __rshift__(self, other):
        return Call(other, *self.__args, **self.__kwargs)

    def __rlshift__(self, other):
        return Call(other, *self.__args, **self.__kwargs)

    def __repr__(self):
        args, kwargs = self.__args, self.__kwargs

        acc = "`.("

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


class Expression(LazyOperations, Shifts, metaclass=ABCMeta):
    def __init__(self, *args):
        setattr(self, "~args", args)

    def _placeholders_(self):
        args = getattr(self, "~args")

        for el in map(placeholders, args):
            yield from el

    def _substitute_(self, cases):
        _ = getattr(self, "~args")
        _ = (substitute(el, cases) for el in _)

        return self.__class__(*_)


class Associative(Expression):
    def __init_subclass__(cls, *, symbol, method, rmethod=None):
        setattr(cls, "~symbol", symbol)
        setattr(cls, method, _associate)
        if method.startswith("__") and method.endswith("__"):
            setattr(cls, f"__r{method[2:]}", _rassociate)

        # turns out every subclass of this can be evaluated simply by calling
        # its equivalent on `operator` module, reducing in the same order as provided
        # in the constructor
        cls._run_ = lambda self: reduce(
            getattr(operator, method),  # get the equivalent operation
            map(run, getattr(self, "~args")),  # first, run each of the args
        )

    def __repr__(self):
        _ = map(repr, getattr(self, "~args"))
        _ = f" {getattr(self, '~symbol')} ".join(_)
        return f"({_})"


def _associate(self, other):
    lcls, rcls = self.__class__, other.__class__

    if lcls == rcls:
        return lcls(*getattr(self, "~args"), *other._args)

    return lcls(*getattr(self, "~args"), other)


def _rassociate(self, other):
    return self.__class__(other, *getattr(self, "~args"))


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


class Or(Associative, symbol="|", method="__or__"):
    pass


class GetAttr(Expression):
    def __init__(self, obj, attr):
        super().__init__(obj, attr)

    def __repr__(self):
        obj, attr = getattr(self, "~args")
        return f"{obj}.{attr}"

    def _run_(self):
        obj, attr = getattr(self, "~args")

        return getattr(run(obj), run(attr))


class GetItem(Expression):
    def __init__(self, obj, item):
        super().__init__(obj, item)

    def __repr__(self):
        obj, item = getattr(self, "~args")

        acc = repr(obj) + "["

        if isinstance(item, slice):
            return acc + slice_repr(item) + "]"

        if not isinstance(item, tuple):
            return acc + repr(item) + "]"

        else:
            return acc + ",".join(map(slice_repr, item)) + "]"

    def _run_(self):
        obj, item = getattr(self, "~args")

        return operator.getitem(run(obj), run(item))


class Call(Expression):
    def __init__(self, f, *args, **kwargs):  # FIXME: standardize arguments keeping
        setattr(self, "~f", f)
        setattr(self, "~args", args)
        setattr(self, "~kwargs", kwargs)

    def __repr__(self):
        args, kwargs = getattr(self, "~args"), getattr(self, "~kwargs")

        acc = repr(getattr(self, "~f")) + "("

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

    def _placeholders_(self):
        f = getattr(self, "~f")
        args, kwargs = getattr(self, "~args"), getattr(self, "~kwargs")

        all_args = [f, *args, *kwargs.values()]
        for el in map(placeholders, all_args):
            yield from el

    def _substitute_(self, cases):
        f = getattr(self, "~f")
        args = getattr(self, "~args")
        kwargs = getattr(self, "~kwargs")

        return Call(
            substitute(f, cases), *substitute(args, cases), **substitute(kwargs, cases)
        )

    def _run_(self):
        f = getattr(self, "~f")
        args = getattr(self, "~args")
        kwargs = getattr(self, "~kwargs")

        return f(*map(run, args), **{k: run(v) for k, v in kwargs.items()})


def make_function(expression):
    _placeholders = set(placeholders(expression))
    _mapping = {el._parameter.name: el for el in _placeholders}

    signature = signature_from_placeholders(_placeholders)

    def _(*args, **kwargs):
        _bound_signature = signature.bind(*args, **kwargs)
        _bound_signature.apply_defaults()

        return run(
            substitute(
                expression,
                [(_mapping[k], v) for k, v in _bound_signature.arguments.items()],
            )
        )

    _.__qualname__ = "<placeholder_function>"
    _.__signature__ = signature
    _.__doc__ = repr(expression)

    return _


def signature_from_placeholders(placeholders):
    from .placeholder import PositionalOnlyPlaceholder, PositionalOrKeywordPlaceholder

    positional = []
    rest = []
    for el in placeholders:
        if isinstance(el, PositionalOnlyPlaceholder) or isinstance(
            el, PositionalOrKeywordPlaceholder
        ):
            positional.append(el)
        else:
            rest.append(el)
    return Signature([el._parameter for el in positional + rest])
