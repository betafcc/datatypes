from typing import Any, Iterator


def placeholders(obj: Any) -> Iterator:
    try:
        handler = type(obj)._placeholders_
    except AttributeError:
        handler = lambda obj: []  # NOQA

    yield from handler(obj)
