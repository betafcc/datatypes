import operator
from typing import Callable, Tuple, Any
from dataclasses import dataclass, FrozenInstanceError
from functools import lru_cache


def expression_from(evaluate):
    return lambda *args: Expression(evaluate, Args(args))


def call(f, *args, **kwargs):
    return f(*args, **kwargs)


def flip(f):
    return lambda a, b: f(b, a)


class Operations:
    """
    Meant to be subclassed
    """

    __add__ = expression_from(operator.__add__)
    __radd__ = expression_from(flip(operator.__add__))
    __sub__ = expression_from(operator.__sub__)
    __mul__ = expression_from(operator.__mul__)
    __matmul__ = expression_from(operator.__matmul__)
    __truediv__ = expression_from(operator.__truediv__)
    __call__ = expression_from(call)

    __lshift__ = __call__


class DotConstructMeta(type):
    def __getattr__(cls, attr):
        return cls(attr)


class DotConstruct(metaclass=DotConstructMeta):
    pass


@dataclass
class Args:
    raw_args: Tuple[Any, ...]

    def map_run(self):
        for raw_arg in self.raw_args:
            try:
                yield raw_arg.run()
            except:
                yield raw_arg

    def bind(self, **kwargs):
        atomargs = {atom(k): v for k, v in kwargs.items()}

        acc = []
        for raw_arg in self.raw_args:
            if isinstance(raw_arg, atom) and raw_arg in atomargs:
                acc.append(atomargs[raw_arg])
            else:
                try:
                    acc.append(raw_arg.bind(**kwargs))
                except:
                    acc.append(raw_arg)
        return Args(tuple(acc))


@dataclass
class Expression(Operations):
    evaluate: Callable
    args: Args

    def run(self):
        return self.evaluate(*self.args.map_run())

    def bind(self, **kwargs):
        return Expression(self.evaluate, self.args.bind(**kwargs))


class atom(Operations, DotConstruct):
    @lru_cache(None)  # TODO: cache with weakmap? Add __hash__?
    def __new__(cls, name):
        instance = super().__new__(cls)
        object.__setattr__(instance, "_name", name)
        return instance

    def __setattr__(self, attr, value):
        raise FrozenInstanceError

    def __delattr__(self, attr):
        raise FrozenInstanceError

    def __repr__(self):
        return self._name

    def _compare_(self, other):
        return (True, [(self, other)])

    def _rcompare_(self, other):
        return (True, [(other, self)])
