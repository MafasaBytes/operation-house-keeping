"""Vendor-neutral operational-extraction helpers.

Shared by API adapters: hardened bounded JSON parsing (Task 4 wires the
adapter), canonical serialization with lossless number tokens, and
RFC 6901 JSON Pointer construction. Makes no vendor claims about payload
semantics.
"""

import json
from decimal import Decimal

# ------------------------------------------------------------ canonical
def canonical_json(value) -> str:
    """Deterministic canonical JSON text.

    Numbers (int / Decimal number-tokens) are emitted as JSON numeric
    lexemes, never quoted; strings stay quoted JSON strings; arrays keep
    order; object keys are sorted; no whitespace. ``[1.0, 2.0]`` is
    therefore always distinguishable from ``["1.0", "2.0"]``.
    """
    if isinstance(value, bool):  # bool before int: True is an int in Python
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ",".join(canonical_json(item) for item in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(
            f"{json.dumps(key, ensure_ascii=False)}:{canonical_json(item)}"
            for key, item in sorted(value.items())
        ) + "}"
    raise TypeError(f"not a JSON-native value: {type(value).__name__}")


def json_type_of(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if value is None:
        return "null"
    if isinstance(value, (int, Decimal)):
        return "number"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    raise TypeError(f"not a JSON-native value: {type(value).__name__}")


# -------------------------------------------------------------- pointer
def escape_pointer_token(token: str) -> str:
    """RFC 6901: '~' escapes to '~0', '/' to '~1' (in that order)."""
    return token.replace("~", "~0").replace("/", "~1")


def json_pointer_of(*tokens: str) -> str:
    return "".join("/" + escape_pointer_token(token) for token in tokens)
