import inspect
from collections import abc
from functools import reduce
from itertools import zip_longest
from operator import eq
from typing import (
    Any,
    Callable,
    Dict,
    Generic,
    Iterable,
    Iterator,
    Tuple,
    Type,
    TypeVar,
    Union,
)


A = TypeVar("A")
B = TypeVar("B")


def call(f):
    return f()


def method(cls: Type, name: str = None) -> Callable[[Callable], Callable]:
    def _method(f):
        setattr(cls, name or f.__name__, f)
        return f

    return _method


def parse_signature(signature: str) -> inspect.Signature:
    locals().update(get_environment(1))

    if not signature.startswith("("):
        signature = "(" + signature + ")"

    exec(f"def dummy_function{signature}: pass")

    return inspect.signature(eval("dummy_function"))


def get_environment(from_level: int) -> Dict[str, Any]:
    """
    Returns the lexical scope, eg:

    x = 1
    y = 2
    z = 3
    def foo():
        x = 4
        y = 5
        def bar():
            y = 6
            return get_environment(0)
        return bar()

    # returns:
    {
        '__name__': '__main__',

        ...

        'x': 4,
        'y': 6,
        'z': 3
    }
    """

    # list the locals of the frames
    acc = []
    for frame_info in inspect.stack()[from_level + 1 :]:
        f_locals = frame_info.frame.f_locals.copy()
        f_globals = frame_info.frame.f_globals.copy()
        acc.append(f_locals)
        # check if it's a module frame
        if f_locals == f_globals:
            break
    # reduce from module level to inner scopes
    return reduce(lambda acc, n: {**acc, **n}, reversed(acc), {})


def ismatch(a: Any, b: Any) -> bool:
    # print(f"{a} ~= {b}")

    # try:
    #     if hasattr(a, "_ismatch_"):
    #         _r = a._ismatch_(b)
    #         if not isinstance(_r, bool):
    #             return False
    #         return _r
    #     if hasattr(b, "_ismatch_"):
    #         _r = b._ismatch_(a)
    #         if not isinstance(_r, bool):
    #             return False
    #         return _r
    # except TypeError:
    #     return False

    if hasattr(type(a), "_ismatch_"):
        return bool(a._ismatch_(b))
    elif hasattr(type(b), "_ismatch_"):
        return bool(b._ismatch_(a))

    if a is b:  # may be unnecessary given next check
        return True
    if a == b:
        return True
    if a is ... or b is ...:
        return True

    if type(a) == type(b):
        if isinstance(a, set):  # TODO
            raise NotImplementedError("ismatch not implemented for set subclasses")
        if isinstance(a, dict):
            return (set(a.keys()) == set(b.keys())) and all(
                ismatch(a[k], b[k]) for k in a.keys()
            )
        if isinstance(a, abc.Sequence):
            return all(ismatch(_a, _b) for _a, _b in zip_longest(a, b))
        if isinstance(a, inspect.BoundArguments):
            return ismatch(a.args, b.args) and ismatch(a.kwargs, b.kwargs)

    return False


def slice_repr(s):
    if not isinstance(s, slice):
        return repr(s)

    _ = (s.start, s.stop, s.step)
    _ = (repr(v) if v is not None else "" for v in _)
    return ":".join(_)


class UnhasheableKeysMapping(Generic[A, B], abc.MutableMapping):
    def __init__(
        self, items: Iterable[Tuple[A, B]] = None, eq: Callable[[A, Any], bool] = eq
    ) -> None:
        if items is None:
            items = []
        self._items = list(items)
        self._eq = eq

    @classmethod
    def from_getitem_arg(cls, arg: Union[slice, Tuple[slice, ...]]):
        if isinstance(arg, slice):
            arg = (arg,)
        if isinstance(arg, tuple):
            return cls([(s.start, s.stop) for s in arg])
        raise TypeError

    def __getitem__(self, key: A) -> B:
        for k, v in self._items:
            if self._eq(k, key):
                return v
        raise KeyError(key)

    def __setitem__(self, key: A, value: B) -> None:
        self._items.append((key, value))

    def __delitem__(self, key: A) -> None:
        for i, (k, v) in enumerate(self._items):
            if self._eq(k, key):
                del self._items[i]
                return
        raise KeyError(key)

    def __iter__(self) -> Iterator[A]:
        return (k for k, _ in self._items)

    def __len__(self):
        return len(self._items)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self._items)

    # def items(self):
    #     return self._items[:]

    # def keys(self) -> Iterable[A]:
    #     return [k for k, _ in self._items]

    # def values(self) -> Iterable[B]:
    #     return [v for _, v in self._items]
