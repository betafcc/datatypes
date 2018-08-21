import inspect


def parse_signature(signature):
    exec(f"def _f{signature}: pass")

    return inspect.signature(locals()["_f"])
