"""Vendor-neutral operational-extraction helpers.

Shared by API adapters: hardened bounded JSON parsing (Task 4 wires the
adapter), canonical serialization with lossless number tokens, and
RFC 6901 JSON Pointer construction. Makes no vendor claims about payload
semantics.
"""

import json
from dataclasses import dataclass
from decimal import Decimal

from backend.data_sources.contracts import ExtractionError


# -- hard parsing
@dataclass(frozen=True)
class JsonLimits:
    max_depth: int = 64
    max_nodes: int = 100_000
    max_string_length: int = 64 * 1024


def _reject_constant(name: str):
    raise ValueError(f"non-finite JSON constant {name!r} rejected")


def parse_bounded_json(data: bytes, limits: JsonLimits):
    """Hardened, bounded JSON parsing for untrusted API responses.

    Strict UTF-8; duplicate object keys rejected (silent last-wins collapse
    would make field-level provenance ambiguous); NaN/Infinity rejected;
    numbers parsed losslessly (int / Decimal number tokens); iterative
    post-parse audit enforces depth, node-count, and string-length limits.
    """

    def strict_pairs(pairs):
        keys = [key for key, _ in pairs]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate object keys")
        return dict(pairs)

    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ExtractionError(
            "EXTRACT_API_MALFORMED_JSON",
            "payload is not decodable as strict UTF-8",
        ) from error
    try:
        value = json.loads(
            text,
            object_pairs_hook=strict_pairs,
            parse_int=int,
            parse_float=Decimal,
            parse_constant=_reject_constant,
        )
    except ValueError as error:
        raise ExtractionError(
            "EXTRACT_API_MALFORMED_JSON",
            f"payload is not acceptable JSON ({error})"[:300],
        ) from error

    nodes = 0
    stack = [(value, 1)]
    while stack:
        node, depth = stack.pop()
        nodes += 1
        if depth > limits.max_depth:
            raise ExtractionError(
                "EXTRACT_API_LIMIT_EXCEEDED",
                f"JSON nesting depth exceeds the limit of {limits.max_depth}",
            )
        if nodes > limits.max_nodes:
            raise ExtractionError(
                "EXTRACT_API_LIMIT_EXCEEDED",
                f"JSON node count exceeds the limit of {limits.max_nodes}",
            )
        if isinstance(node, str) and len(node) > limits.max_string_length:
            raise ExtractionError(
                "EXTRACT_API_LIMIT_EXCEEDED",
                "a JSON string exceeds the configured length limit",
            )
        if isinstance(node, list):
            stack.extend((item, depth + 1) for item in node)
        elif isinstance(node, dict):
            for key, item in node.items():
                if len(key) > limits.max_string_length:
                    raise ExtractionError(
                        "EXTRACT_API_LIMIT_EXCEEDED",
                        "a JSON object key exceeds the configured length limit",
                    )
                stack.append((item, depth + 1))
    return value


# -- canonical
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


# -- pointer
def escape_pointer_token(token: str) -> str:
    """RFC 6901: '~' escapes to '~0', '/' to '~1' (in that order)."""
    return token.replace("~", "~0").replace("/", "~1")


def json_pointer_of(*tokens: str) -> str:
    return "".join("/" + escape_pointer_token(token) for token in tokens)
