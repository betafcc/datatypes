from inspect import Parameter
from functools import lru_cache

from .util import LazyArguments
from .protocols import case, compare
from .expression import LazyOperations, Shifts


class placeholder_meta(type):
    def __getattr__(cls, attr):
        return KeywordOnlyPlaceholder(attr)

    def __getitem__(cls, item):
        # eg _[0] -> `0
        if isinstance(item, int):
            return PositionalOnlyPlaceholder(item)

        # eg _['x':int:42] -> `x:int=42
        if isinstance(item, slice):
            return KeywordOnlyPlaceholder(*_fill_slice(item))

        if isinstance(item, tuple) and len(item) == 2:
            position, keyword = item

            # eg _[3, 'x'] -> `3.x
            if isinstance(keyword, str):
                return PositionalOrKeywordPlaceholder(position, keyword)

            # eg _[3, 'x':int:42] -> `3.x:int=42
            return PositionalOrKeywordPlaceholder(position, *_fill_slice(keyword))

        raise NotImplementedError

    def __call__(cls, *args, **kwargs):
        return LazyArguments(*args, **kwargs)


class placeholder(metaclass=placeholder_meta):
    pass


def _fill_slice(s):
    name, annotation, default = s.start, s.stop, s.step

    if annotation is None:
        annotation = Parameter.empty

    if default is None:
        default = Parameter.empty

    return (name, annotation, default)


class Placeholder(LazyOperations, Shifts):
    # FIXME: implement __hash__ instead of this?
    # may have problemns with non-hasheable annotations or default
    # (eg _[0, xs:['non hasheable annotation']:[1, 2, 3]])
    # maybe use weak map here? Maybe lru_cache already uses weak map?
    @lru_cache(None)
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def _placeholders_(self):
        yield self

    def _substitute_(self, cases):
        return cases.get(self, self)

    def _compare_(self, other):
        return compare.positive([(self, other)])

    def _rcompare_(self, other):
        return compare.positive([(other, self)])

    def _case_(self, a, b, c):
        if self is a:
            return case.accept(b)
        return case.reject(c)


class KeywordOnlyPlaceholder(Placeholder):
    def __init__(self, name, annotation=Parameter.empty, default=Parameter.empty):
        self._parameter = Parameter(
            name, kind=Parameter.KEYWORD_ONLY, annotation=annotation, default=default
        )

    def __repr__(self):
        name, annotation, default = (
            self._parameter.name,
            self._parameter.annotation,
            self._parameter.default,
        )

        acc = f"`{name}"
        if annotation is not Parameter.empty:
            acc += f":{annotation}"
        if default is not Parameter.empty:
            acc += f"={default}"
        return acc


class PositionalOnlyPlaceholder(Placeholder):
    def __init__(self, position):
        self._parameter = Parameter(f"_{position}", kind=Parameter.POSITIONAL_ONLY)

    def __repr__(self):
        return f"`{self._parameter.name[1:]}"


class PositionalOrKeywordPlaceholder(Placeholder):
    def __init__(
        self, position, name, annotation=Parameter.empty, default=Parameter.empty
    ):
        self._position = position
        self._parameter = Parameter(
            name,
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=annotation,
            default=default,
        )

    def __repr__(self):
        position, name, annotation, default = (
            self._position,
            self._parameter.name,
            self._parameter.annotation,
            self._parameter.default,
        )

        acc = f"`{position}.{name}"
        if annotation is not Parameter.empty:
            acc += f":{annotation}"
        if default is not Parameter.empty:
            acc += f"={default}"
        return acc
