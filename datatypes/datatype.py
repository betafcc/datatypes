from operator import setitem
from typing import Optional, Dict, Any, Type, Callable, List

from .annotations import annotations_to_signatures
from .constructor import make_constructor
from .magic import data
from .util import call


@call
class datatype:
    def __call__(
        self,
        _cls: Optional[type] = None,
        *,
        init: bool = True,
        repr: bool = True,
        expose: Optional[Dict[str, Any]] = None,
        expose_with: Callable[[Any, str, Type], None] = setitem,
    ):
        return _datatype(
            _cls=_cls, init=init, repr=repr, expose=expose, expose_with=expose_with
        )

    def __repr__(self):
        return self.__class__.__name__

    def __getattr__(self, name):
        return data(name)


def _datatype(
    _cls: Optional[type],
    *,
    init: bool,
    repr: bool,
    expose: Optional[Dict[str, Any]],
    expose_with: Callable[[Any, str, Type], None],
):
    def wrap(cls):
        return _process_class(
            cls, init=init, repr=repr, expose=expose, expose_with=expose_with
        )

    if _cls is None:
        return wrap
    return wrap(_cls)


def _process_class(
    cls: type,
    init: bool,
    repr: bool,
    expose: Dict[str, Any],
    expose_with: Callable[[Any, str, Type], None],
):
    should_expose = expose is not None

    # TODO: refactor this mess
    signatures = [
        *annotations_to_signatures(cls.__dict__.get('__annotations__', {})).items(),
        *((k, v.signature) for k, v in cls.__dict__.items() if isinstance(v, ProtoConstructor)),
    ]

    constructors : List[Any]
    constructors = []
    for cls_name, signature in signatures:  # type: ignore
        constructor = make_constructor(
            cls_name=cls_name, signature=signature, bases=(cls,), init=init, repr=repr
        )

        setattr(cls, cls_name, constructor)
        constructors.append(constructor)
        if should_expose:
            expose_with(expose, cls_name, constructor)
    setattr(cls, "_constructors", constructors)

    def init_(*args, **kwargs):
        raise TypeError("Can't instantiate datatype, use one of the constructors")

    setattr(cls, "__init__", init_)
    return cls


# TODO: handle the name of this thing or of the other module
# (they are not related)
def constructor(f):
    from inspect import signature
    return ProtoConstructor(signature(f))


class ProtoConstructor:
    def __init__(self, signature):
        self.signature = signature
