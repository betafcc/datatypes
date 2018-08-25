from types import new_class
from typing import Generic


class dot_construct(type):
    def __getattr__(cls, attr):
        return cls(attr)


class iter_constructors(type):
    def __iter__(cls):
        yield from cls._constructors


class or_(metaclass=dot_construct):
    def __or__(self, other):
        return union(self, other)


class rshift(metaclass=dot_construct):
    def __rshift__(self, other):
        from . import datatype

        if isinstance(self, parametrized):
            bases = (Generic[self.parameters],)
        else:
            bases = tuple()

        cls = new_class(
            self.name,
            bases,
            kwds=dict(metaclass=iter_constructors),
            exec_body=lambda ns: ns.update(__annotations__=other.to_annotations()),
        )

        return datatype(cls)


class data(or_, rshift):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def __iter__(self):
        yield self

    def __getitem__(self, parameters):
        if not isinstance(parameters, tuple):
            parameters = (parameters,)
        return parametrized(self, parameters)

    def to_annotations(self):
        return {self.name: ()}


class parametrized(or_, rshift):
    def __init__(self, obj, parameters):
        self.obj = obj  # do i need this?
        self.name = obj.name
        self.parameters = parameters

    def __iter__(self):
        yield self

    def __repr__(self):
        _p = ", ".join(map(repr, self.parameters))
        return f"{self.name}[{_p}]"

    def to_annotations(self):
        return {self.name: self.parameters}


class union(or_):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def __iter__(self):
        yield from self.a
        yield from self.b

    def __repr__(self):
        return f"{self.a} | {self.b}"

    def to_annotations(self):
        acc = {}
        for el in self:
            acc = {**acc, **el.to_annotations()}
        return acc
