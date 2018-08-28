import collections.abc
from typing import Union, Tuple, Any

from datatypes.util import UnhasheableKeysMapping


class substitute:
    def __new__(cls, obj, cases=None):
        if cases is None:
            self = super().__new__(cls)
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


def default_substitute_handler(obj, cases):
    return cases.get(obj, obj)
