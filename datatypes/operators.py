from collections import OrderedDict
from typing import Mapping, Callable, Any


class NoMatchException(TypeError):
    pass


def fold(obj, cases: Mapping[Any, Callable]):
    sig = obj._bound_signature
    cases = OrderedDict(cases)
    default = cases.pop(
        ..., None
    )  # Need to pop it here so `isinstance` doesnt complain

    for case, handler in cases.items():
        if isinstance(obj, case):
            return handler(*sig.args, **sig.kwargs)

    if default is not None:
        return default(*sig.args, **sig.kwargs)

    raise NoMatchException(f'No case provided for "{obj}" instance')
