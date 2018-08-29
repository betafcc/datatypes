def run(expr):
    try:
        handler = type(expr)._run_
    except AttributeError:
        handler = lambda a: a  # NOQA

    return handler(expr)
