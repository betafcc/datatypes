from collections import OrderedDict
from typing import Mapping, Callable, Any


class NoMatchException(TypeError):
    pass


def fold(obj, cases: Mapping[Any, Callable]):
    cases = OrderedDict(cases)
    for case in cases:
        if isinstance(obj, case):
            match = case
    else:
        if ... in cases:
            match = ...
        else:
            raise NoMatchException(f'No case provided for "{obj}" instance')

    sig = obj._bound_signature
    return cases[match](*sig.args, **sig.kwargs)
