from functools import singledispatch


@singledispatch
def run(expr):
    try:
        handler = type(expr)._run_
    except AttributeError:
        handler = lambda a: a  # NOQA

    return handler(expr)


@run.register(dict)  # type: ignore
def _(expr):
    return {run(k): run(v) for k, v in expr.items()}


@run.register(list)  # type: ignore
def _(expr):
    return [run(v) for v in expr]


@run.register(tuple)  # type: ignore
def _(expr):
    return tuple(run(v) for v in expr)
