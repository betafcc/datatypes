import inspect
from dataclasses import FrozenInstanceError
from functools import reduce, lru_cache
from collections import abc
from itertools import zip_longest
from typing import Dict, Any, Type, Callable


def call(f):
    return f()


def method(cls: Type) -> Callable[[Callable], Callable]:
    def _method(f):
        setattr(cls, f.__name__, f)
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


# NOTE: for some reason if I `from .magic import dot_construct`, mypy complains
class dot_construct(type):
    def __getattr__(cls, attr):
        return cls(attr)


class atom(metaclass=dot_construct):
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

    def _ismatch_(self, other):
        return True


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
