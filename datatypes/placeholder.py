from inspect import Parameter
from functools import lru_cache


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


class placeholder_meta(type):
    def __getattr__(cls, attr):
        return Parameter(attr, kind=Parameter.KEYWORD_ONLY)


class placeholder(metaclass=placeholder_meta):
    pass
