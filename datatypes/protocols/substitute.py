import collections.abc
from typing import Union, Tuple, Any
from functools import singledispatch

from datatypes.util import UnhasheableKeysMapping


class substitute:
    _obj : Any

    def __new__(cls, obj: Any, cases=None):
        if cases is None:
            self = super().__new__(cls)  # type: ignore
            self._obj = obj
            return self

        return _substitute(obj, cases)

    def __getitem__(self, s: Union[slice, Tuple[slice, ...]]) -> Any:
        return _substitute(self._obj, UnhasheableKeysMapping.from_getitem_arg(s))


def _substitute(obj, cases):
    try:
        handler = type(obj)._substitute_
    except AttributeError:
        handler = default_substitute_handler

    if isinstance(cases, collections.abc.Mapping):
        _cases = cases
    else:
        try:
            _cases = dict(cases)
        except TypeError:
            _cases = UnhasheableKeysMapping(cases)

    return handler(obj, _cases)


@singledispatch
def default_substitute_handler(obj, cases):
    return cases.get(obj, obj)


@default_substitute_handler.register(dict)  # type: ignore
def _(obj, cases):
    return {k: substitute(v, cases) for k, v in obj.items()}


@default_substitute_handler.register(list)  # type: ignore
def _(obj, cases):
    return [substitute(el, cases) for el in obj]
