from typing import Dict, Any
import inspect


def parse_signature(
    signature: str, closure: Dict[str, Any] = None
) -> inspect.Signature:
    locals().update(closure or {})

    if not signature.startswith("("):
        signature = "(" + signature + ")"

    exec(f"def dummy_function{signature}: pass")

    return inspect.signature(eval("dummy_function"))
