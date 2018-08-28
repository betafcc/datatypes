from typing import Any, Iterator

from datatypes.placeholder import Placeholder


def placeholders(obj: Any) -> Iterator[Placeholder]:
    try:
        handler = type(obj)._placeholders_
    except AttributeError:
        handler = lambda obj: []

    yield from handler(obj)
