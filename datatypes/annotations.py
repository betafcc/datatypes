from collections import abc
from inspect import Signature, Parameter
from typing import Any, Tuple, Dict


Annotation = Any


def process_annotations(cls: type) -> type:
    """
    Process the annotations in a class.

    The target is to transform all annotations to Signatures,
    so a Constructor can be made of them afterwards.

    The processing pipeline will work as follow:

    `Any -> Tuple[Any, ...] -> Signature` for every annotation.

    Note that the processing will be incremental and
    self-adapting to not process already processed items,
    that means you can give a `Signature` or a `Typle[Any,...]`
    to start and the processing will only take to the rest of the pipeline.
    """
    cls.__annotations__ = annotations_to_signatures(cls.__annotations__)
    return cls


def annotations_to_signatures(
    annotations: Dict[str, Annotation]
) -> Dict[str, Signature]:
    annotations = annotations.copy()
    for k in annotations:
        v = annotations[k]

        if isinstance(v, dict):
            annotations[k] = dict_to_signature(v)
            continue

        if not isinstance(v, tuple) and not isinstance(v, Signature):
            annotations[k] = annotation_to_tuple(v)

        v = annotations[k]
        if not isinstance(v, Signature):
            annotations[k] = tuple_to_signature(v)
    return annotations


def annotation_to_tuple(a: Annotation) -> Tuple[Annotation, ...]:
    if isinstance(a, abc.Iterable):
        return tuple(a)
    return (a,)


def tuple_to_signature(t: Tuple[Annotation, ...]) -> Signature:
    return Signature(
        [
            Parameter(
                name=f"_{n}", kind=Parameter.POSITIONAL_ONLY, annotation=annotation
            )
            for n, annotation in enumerate(t)
        ]
    )


def dict_to_signature(d: Dict[str, Annotation]) -> Signature:
    return Signature(
        [
            Parameter(name=k, kind=Parameter.KEYWORD_ONLY, annotation=v)
            for k, v in d.items()
        ]
    )
