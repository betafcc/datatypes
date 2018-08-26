from typing import Any, Tuple


class NoMatchError(Exception):
    pass


def default_protocol(obj: Any, a: Any, b: Any, c: Any) -> Tuple[bool, Any]:
    if a is ... or obj == a:
        return match.accept(b)
    return match.reject()


class match:
    @staticmethod
    def accept(value=None) -> Tuple[bool, Any]:
        return (True, value)

    @staticmethod
    def reject(value=None) -> Tuple[bool, Any]:
        return (False, value)

    def __init__(self, to_match: Any, protocol=default_protocol) -> None:
        self._to_match = to_match
        if hasattr(type(to_match), "_match_"):
            self._protocol = type(to_match)._match_
        else:
            self._protocol = protocol

    def __getitem__(self, args: Tuple[slice, ...]) -> Any:
        if isinstance(args, slice):
            args = (args,)
        protocol = self._protocol
        to_match = self._to_match

        for arg in args:
            done, result = protocol(to_match, arg.start, arg.stop, arg.step)
            if done:
                return result
        raise NoMatchError

    def __repr__(self):
        if self._protocol is default_protocol:
            return f"match({self._to_match})"
        return f"match({self._to_match}, {self._protocol.__name__})"
