from typing import Any, Tuple

from .case import default_case_handler


class NoMatchError(Exception):
    pass


class match:
    def __init__(self, to_match: Any) -> None:
        self._to_match = to_match

        try:
            self._handler = type(to_match)._match_
        except AttributeError:
            pass
        try:
            self._handler = match_handler_from_case_handler(type(to_match)._case_)
        except AttributeError:
            self._handler = match_handler_from_case_handler(default_case_handler)

    def __getitem__(self, cases: Tuple[slice, ...]) -> Any:
        if not (isinstance(cases, slice) or isinstance(cases, tuple)):
            raise TypeError

        if isinstance(cases, slice):
            cases = (cases,)

        return self._handler(
            self._to_match, tuple((s.start, s.stop, s.step) for s in cases)
        )

    def __repr__(self):
        return f"match({self._to_match})"


def match_handler_from_case_handler(case_handler):
    def _match_handler(obj, cases):
        _ = cases
        _ = (case_handler(*case) for case in _)
        _ = (value for did_match, value in _ if did_match)

        try:
            return next(_)
        except StopIteration:
            raise NoMatchError

    return _match_handler
