from abc import ABCMeta, abstractmethod
from inspect import Parameter
from functools import lru_cache

from .util import slice_repr


class protocol(metaclass=ABCMeta):
    """
    This is a tool to design protocols with an associated function,
    is more or less based on the cls.__len__ -> len and cls.__iter__ -> iter
    pattern, mixed with some 'trait' style concepts

    This probably will change
    """

    # As of now, the protocol is implemented via
    # a hidden field prefixed with '~' in the class by convention,
    # it works like the '@@' Symbols in JS, and 'protocol' subclasses
    # should be used to aid in implementing

    # I can't use normal '_field' convention, so I dont interfere
    # with the user `x._field expressions, and '__field' mangling
    # doesnt play well in inheritance and its conceptually weird

    # This 'friend member' or 'traits' paradigm is conceptually solid
    # for this use case

    @property
    @abstractmethod
    def getter_name(self):
        pass

    @classmethod
    def impl(cls, target_cls):
        """
        Utility to implement 'placeholders' protol in target_cls

        eg:
        @placeholders.impl
        def _(self):
            yield self._placeholder_field
        """

        def _impl(f):
            setattr(target_cls, "~" + cls.__name__, f)
            return f

        return _impl

    @classmethod
    def hasattr(cls, obj):
        return hasattr(obj, "~" + cls.__name__)


class placeholders(protocol):
    def __new__(cls, obj):
        return getattr(obj, "~" + cls.__name__)()


class substitute(protocol):
    def __new__(cls, obj, mapping):
        return getattr(obj, '~')


class placeholder_meta(type):
    def __getattr__(cls, attr):
        return KeywordOnlyPlaceholder(attr)

    def __getitem__(cls, item):
        # eg _[0] -> `0
        if isinstance(item, int):
            return PositionalOnlyPlaceholder(item)

        # eg _['x':int:42] -> `x:int=42
        if isinstance(item, slice):
            return KeywordOnlyPlaceholder(*_fill_slice(item))

        if isinstance(item, tuple) and len(item) == 2:
            position, keyword = item

            # eg _[3, 'x'] -> `3.x
            if isinstance(keyword, str):
                return PositionalOrKeywordPlaceholder(position, keyword)

            # eg _[3, 'x':int:42] -> `3.x:int=42
            return PositionalOrKeywordPlaceholder(position, *_fill_slice(keyword))

        raise NotImplementedError

    def __call__(cls, *args, **kwargs):
        pass
        # TODO
        # return FunctionOrArguments(*args, **kwargs)


class placeholder(metaclass=placeholder_meta):
    pass


def _fill_slice(s):
    name, annotation, default = s.start, s.stop, s.step

    if annotation is None:
        annotation = Parameter.empty

    if default is None:
        default = Parameter.empty

    return (name, annotation, default)


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

    def __getattr__(self, attr):
        return GetAttr(self, attr)

    def __getitem__(self, item):
        return GetItem(self, item)

    def __call__(self, *args, **kwargs):
        return Call(self, *args, **kwargs)


class Placeholder(LazyOperations):
    @lru_cache(None)
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)


@placeholders.impl(Placeholder)  # type: ignore
def _(self):
    yield self


@substitute.impl(Placeholder)  # type: ignore
def _(self, mapping):
    pass


class KeywordOnlyPlaceholder(Placeholder):
    def __init__(self, name, annotation=Parameter.empty, default=Parameter.empty):
        self.__parameter = Parameter(
            name, kind=Parameter.KEYWORD_ONLY, annotation=annotation, default=default
        )

    def __repr__(self):
        name, annotation, default = (
            self.__parameter.name,
            self.__parameter.annotation,
            self.__parameter.default,
        )

        acc = f"`{name}"
        if annotation is not Parameter.empty:
            acc += f":{annotation}"
        if default is not Parameter.empty:
            acc += f"={default}"
        return acc


class PositionalOnlyPlaceholder(Placeholder):
    def __init__(self, position):
        self.__parameter = Parameter(f"_{position}", kind=Parameter.POSITIONAL_ONLY)

    def __repr__(self):
        return f"`{self.__parameter.name[1:]}"


class PositionalOrKeywordPlaceholder(Placeholder):
    def __init__(
        self, position, name, annotation=Parameter.empty, default=Parameter.empty
    ):
        self.__position = position
        self.__parameter = Parameter(
            name,
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=annotation,
            default=default,
        )

    def __repr__(self):
        position, name, annotation, default = (
            self.__position,
            self.__parameter.name,
            self.__parameter.annotation,
            self.__parameter.default,
        )

        acc = f"`{position}.{name}"
        if annotation is not Parameter.empty:
            acc += f":{annotation}"
        if default is not Parameter.empty:
            acc += f"={default}"
        return acc


class Expression(LazyOperations, metaclass=ABCMeta):
    def __init__(self, *args):
        setattr(self, "~args", args)


@placeholders.impl(Expression)  # type: ignore
def _(self):
    args = getattr(self, "~args")

    for el in map(placeholders, filter(placeholders.hasattr, args)):
        yield from el


class Associative(Expression):
    def __init_subclass__(cls, *, symbol, method, rmethod=None):
        setattr(cls, "~symbol", symbol)
        setattr(cls, method, _associate)
        if method.startswith("__") and method.endswith("__"):
            setattr(cls, f"__r{method[2:]}", _rassociate)

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


class GetAttr(Expression):
    def __init__(self, obj, attr):
        super().__init__(obj, attr)

    def __repr__(self):
        obj, attr = getattr(self, "~args")
        return f"{obj}.{attr}"


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


class Call(Expression):
    def __init__(self, f, *args, **kwargs):
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


@placeholders.impl(Call)  # type: ignore
def _(self):
    f = getattr(self, "~f")
    args, kwargs = getattr(self, "~args"), getattr(self, "~kwargs")

    all_args = [f, *args, *kwargs.values()]
    for el in map(placeholders, filter(placeholders.hasattr, all_args)):
        yield from el
