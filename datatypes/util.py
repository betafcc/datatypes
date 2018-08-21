from inspect import Signature, Parameter


def init_method(self, *args, **kwargs):
    signature = self.__signature__.bind(*args, **kwargs)
    signature.apply_defaults()

    self._bound_signature = signature


def repr_method(self):
    return "{}({})".format(
        self.__class__.__name__, ", ".join(map(str, self._bound_signature.args))
    )


def make_class_dict(constructor_arguments):
    __signature__ = make_signature(*constructor_arguments)

    return dict(
        __init__=init_method,
        __repr__=repr_method,
        __signature__=__signature__,
        __annotations__=extract_annotations(__signature__),
    )


def make_signature(*types):
    return Signature(
        [
            Parameter(
                name="_{}".format(n), kind=Parameter.POSITIONAL_ONLY, annotation=t
            )
            for n, t in enumerate(types)
        ]
    )


def extract_annotations(signature):
    return {k: v.annotation for k, v in signature.parameters.items()}
