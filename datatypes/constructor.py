import re
import inspect
from types import new_class
from dataclasses import dataclass
from typing import Optional, Mapping, Dict, Tuple, Any, Callable


def make_constructor(
    cls_name: str,
    signature: inspect.Signature,
    *,
    bases: Tuple[type, ...] = (),
    namespace: Optional[Mapping[str, Any]] = None,
    init: bool = True,
    repr: bool = True,
):
    namespace_: Mapping[str, Any]
    if namespace is None:
        namespace_ = {}

    namespace_ = {
        **make_namespace(signature, init=init, repr=repr),
        **namespace_,  # user provided namespace will be preserved
    }

    cls = new_class(
        name=cls_name, bases=bases, kwds={}, exec_body=lambda ns: ns.update(namespace_)
    )

    # Kind of indiferent if use dataclass here
    # the only real reason if to maintain consistency with the behavior with frozen=True
    cls = dataclass(frozen=True, init=False, repr=False, eq=False)(cls)

    if cls._no_parameters_constructor:
        # NOTE: THIS IS WEIRD AND MAY CHANGE
        cls = cls()

    return cls


def make_namespace(
    signature: inspect.Signature, init: bool, repr: bool
) -> Dict[str, Any]:
    namespace = dict(
        __annotations__=make_annotations(signature),
        __signature__=signature,
        __eq__=lambda self, other: self._bound_signature == other._bound_signature,
    )
    if init:
        namespace["__init__"] = make_init(signature)
    if repr:
        namespace["__repr__"] = make_repr(signature)
    if not len(signature.parameters):
        # Constructors with no parameters shall be idempotent in construction
        # The reason is so `Nothing is Nothing()` and `match` and `fold` dont
        # need a awkward `{Nothing(): ...}`
        # NOTE: this may change
        namespace["__call__"] = lambda self: self
        namespace["_no_parameters_constructor"] = True
    else:
        namespace["_no_parameters_constructor"] = False
    return namespace


def make_init(signature: inspect.Signature) -> Callable[..., None]:
    def _init(self, *args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        object.__setattr__(self, "_bound_signature", bound)

    return _init


def make_annotations(signature: inspect.Signature) -> Dict[str, Any]:
    return {k: v.annotation for k, v in signature.parameters.items()}


def make_repr(signature: inspect.Signature) -> Callable[[Any], str]:
    if not len(signature.parameters):
        # NOTE: this is weird and may change
        def _repr(self):
            return self.__class__.__qualname__

    elif all(
        parameter.kind is inspect.Parameter.POSITIONAL_ONLY
        for parameter in signature.parameters.values()
    ):

        def _repr(self):
            return (
                self.__class__.__qualname__
                + "("
                + ", ".join(map(repr, self._bound_signature.args))
                + ")"
            )

    else:
        # FIXME: super hacky, parsing Signature.__repr__ result
        def _repr(self):
            return (
                self.__class__.__qualname__
                + re.findall(r"^.+?(\(.+\)).+", repr(self._bound_signature))[0]
            )

    return _repr
