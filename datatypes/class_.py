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
    pass


def make_annotations(signature: inspect.Signature) -> Dict[str, Any]:
    pass


def make_repr(signature: inspect.Signature) -> Callable[[Any], str]:
    pass
