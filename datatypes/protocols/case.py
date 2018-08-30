from functools import singledispatch
from typing import Tuple, Any, Callable

from .run import run
from .substitute import substitute
from .compare import compare


CaseResult = Tuple[bool, Any]
CaseHandler = Callable[[Any, Any, Any, Any], CaseResult]


class case:
    def __init__(self, obj):
        self._obj = obj

    @staticmethod
    def accept(value: Any = None) -> CaseResult:
        return (True, value)

    @staticmethod
    def reject(value: Any = None) -> CaseResult:
        return (False, value)

    def __getitem__(self, s: slice) -> CaseResult:
        if not isinstance(s, slice):
            raise TypeError

        args = s.start, s.stop, s.step

        try:
            return type(self._obj)._case_(self._obj, *args)
        except AttributeError:
            return default_case_handler(self._obj, *args)


@singledispatch
def default_case_handler(obj, a, b, c) -> CaseResult:
    if a is ...:
        return case.accept(b)

    did_match, matches = compare(a, obj)  # type: ignore

    if not did_match:
        return case.reject(c)

    print(matches)

    return case.accept(run(substitute(b, matches)))


@default_case_handler.register(str)
def _(obj, a, b, c):
    if a is ... or a == obj:
        return case.accept(b)
    return case.reject(c)
