from typing import Any, Iterator

from datatypes.placeholder import Placeholder


def placeholders(obj: Any) -> Iterator[Placeholder]:
    yield from type(obj)._placeholders_(obj)
