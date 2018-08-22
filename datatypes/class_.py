from typing import Iterable, Optional, Dict, Any, Callable
import inspect


def make_contructor(
    cls_name: str,
    signature: inspect.Signature,
    *,
    bases: Iterable[type] = (),
    namespace: Optional[Dict[str, Any]] = None,
    init: Optional[bool] = True,
    repr: Optional[bool] = True,
):
    pass


def make_init(signature: inspect.Signature) -> Callable[..., None]:
    def _init(self, *args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()

        self._bound_signature = bound

    return _init


def make_annotations(signature: inspect.Signature) -> Dict[str, Any]:
    return {k: v.annotation for k, v in signature.parameters.items()}


def make_repr(signature: inspect.Signature) -> Callable[[Any], str]:
    if all(
        parameter.kind is Parameter.POSITIONAL_ONLY
        for parameter in signature.parameters.values()
    ):

        def _repr(self):
            return self.__class__.__qualname__ + ", ".join(
                map(repr, self._bound_signature.args)
            )

    else:

        def _repr(self):
            return (
                self.__class__.__qualname__
                + re.findall(r"^.+?(\(.+\)).+", repr(self._bound_signature))[0]
            )

    return _repr
