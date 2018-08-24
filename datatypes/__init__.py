from typing import Optional, Dict, Any

from .annotations import annotations_to_signatures
from .constructor import make_constructor

__version__ = "0.1.0"


def datatype(
    _cls: Optional[type] = None,
    *,
    init: bool = True,
    repr: bool = True,
    expose: Optional[Dict[str, Any]] = None,
):
    def wrap(cls):
        return _process_class(cls, init=init, repr=repr, expose=expose)

    if _cls is None:
        return wrap
    return wrap(_cls)


def _process_class(cls: type, init: bool, repr: bool, expose: Dict[str, Any]):
    should_expose = expose is not None

    constructors = []
    for cls_name, signature in annotations_to_signatures(cls.__annotations__).items():
        constructor = make_constructor(
            cls_name=cls_name, signature=signature, bases=(cls,), init=init, repr=repr
        )

        setattr(cls, cls_name, constructor)
        constructors.append(constructor)
        if should_expose:
            expose[cls_name] = constructor
    setattr(cls, '_constructors', constructors)

    def init_(*args, **kwargs):
        raise TypeError("Can't instantiate datatype, use one of the constructors")

    setattr(cls, '__init__', init_)
    return cls
