import inspect
from dataclasses import FrozenInstanceError
from functools import reduce, lru_cache
from typing import Dict, Any


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


class boson(type):
    def __new__(meta, clsname, bases, clsdict):
        return super().__new__(meta, clsname, bases, clsdict)

    def __getattr__(self, attr):
        return self(attr)


class atom(metaclass=boson):
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
