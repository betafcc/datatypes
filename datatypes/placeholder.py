from inspect import Parameter
from functools import lru_cache


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
        return "hello"


class placeholder(metaclass=placeholder_meta):
    pass


def _fill_slice(s):
    name, annotation, default = s.start, s.stop, s.step

    if annotation is None:
        annotation = Parameter.empty

    if default is None:
        default = Parameter.empty

    return (name, annotation, default)


class Placeholder:
    @lru_cache(None)
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)


class KeywordOnlyPlaceholder(Placeholder):
    def __init__(self, name, annotation=Parameter.empty, default=Parameter.empty):
        self.__parameter = Parameter(
            name, kind=Parameter.KEYWORD_ONLY, annotation=annotation, default=default
        )

    def __repr__(self):
        name, annotation, default = (
            self.__parameter.name,
            self.__parameter.annotation,
            self.__parameter.default,
        )

        acc = f"`{name}"
        if annotation is not Parameter.empty:
            acc += f":{annotation}"
        if default is not Parameter.empty:
            acc += f"={default}"
        return acc


class PositionalOnlyPlaceholder(Placeholder):
    def __init__(self, position):
        self.__parameter = Parameter(f"_{position}", kind=Parameter.POSITIONAL_ONLY)

    def __repr__(self):
        return f"`{self.__parameter.name[1:]}"


class PositionalOrKeywordPlaceholder(Placeholder):
    def __init__(
        self, position, name, annotation=Parameter.empty, default=Parameter.empty
    ):
        self.__position = position
        self.__parameter = Parameter(
            name,
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=annotation,
            default=default,
        )

    def __repr__(self):
        position, name, annotation, default = (
            self.__position,
            self.__parameter.name,
            self.__parameter.annotation,
            self.__parameter.default,
        )

        acc = f"`{position}.{name}"
        if annotation is not Parameter.empty:
            acc += f":{annotation}"
        if default is not Parameter.empty:
            acc += f"={default}"
        return acc
