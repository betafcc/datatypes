from inspect import Parameter
from functools import lru_cache


class placeholder_meta(type):
    def __getattr__(cls, attr):
        return KeywordOnlyPlaceholder(attr)

    def __getitem__(cls, item):
        if isinstance(item, int):
            return PositionalOnlyPlaceholder(item)
        if isinstance(item, tuple) and len(item) == 2:
            position, keyword = item
            if isinstance(keyword, str):
                return PositionalOrKeywordPlaceholder(position, keyword)
            name, annotation, default = keyword.start, keyword.stop, keyword.step
            if annotation is None:
                annotation = Parameter.empty
            if default is None:
                default = Parameter.empty
            return PositionalOrKeywordPlaceholder(position, name, annotation, default)

        raise NotImplementedError


class placeholder(metaclass=placeholder_meta):
    pass


class Placeholder:
    @lru_cache(None)
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)


class KeywordOnlyPlaceholder(Placeholder):
    def __init__(self, name):
        self.__parameter = Parameter(name, kind=Parameter.KEYWORD_ONLY)

    def __repr__(self):
        return f"`{self.__parameter.name}"


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
