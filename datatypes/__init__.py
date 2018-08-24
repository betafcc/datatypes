from typing import Optional
from .annotations import annotations_to_signatures
from .constructor import make_constructor

__version__ = "0.1.0"


def datatype(_cls: Optional[type] = None, *, init: bool = True, repr: bool = True):
    def wrap(cls):
        return _process_class(cls, init=init, repr=repr)

    if _cls is None:
        return wrap
    return wrap(_cls)


def _process_class(cls: type, init: bool, repr: bool):
    for cls_name, signature in annotations_to_signatures(cls.__annotations__).items():
        setattr(
            cls,
            cls_name,
            make_constructor(
                cls_name=cls_name,
                signature=signature,
                bases=(cls,),
                init=init,
                repr=repr,
            ),
        )
    return cls
