"""Private bounded structural admission and deterministic JSON encoding."""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterator, get_args

from pydantic import BaseModel


MAXIMUM_CANONICAL_REQUEST_BYTES = 134_217_728
MAXIMUM_RECONSTRUCTED_NODES = 200_000
MAXIMUM_NESTING_DEPTH = 128

_JSON_NUMBER = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:e[+-]?[0-9]+)?\Z"
)
_STRICT_INTEGER_NAMES = {"sweep_position"}
_TRUSTED_MODEL_TYPES: frozenset[type[BaseModel]] = frozenset()


@dataclass(frozen=True)
class _PreflightResult:
    nodes: int
    maximum_depth: int
    canonical_bytes: int


def _float_token(value: float) -> str:
    if type(value) is not float or not math.isfinite(value):
        raise ValueError("invalid scalar")
    token = float.__repr__(value).replace("E", "e")
    if _JSON_NUMBER.fullmatch(token) is None:
        raise ValueError("invalid scalar")
    return token


def _datetime_token(value: datetime) -> str:
    if type(value) is not datetime or value.tzinfo is None:
        raise ValueError("invalid scalar")
    normalized = value.astimezone(UTC)
    if normalized.microsecond:
        fraction = f"{normalized.microsecond:06d}".rstrip("0")
        return normalized.strftime("%Y-%m-%dT%H:%M:%S") + f".{fraction}Z"
    return normalized.strftime("%Y-%m-%dT%H:%M:%SZ")


def _string_content_size(value: str, *, maximum: int | None = None) -> int:
    if type(value) is not str:
        raise ValueError("invalid scalar")
    size = 0
    for character in value:
        code = ord(character)
        if character in ('"', "\\") or character in "\b\f\n\r\t":
            size += 2
        elif code < 0x20:
            size += 6
        else:
            try:
                size += len(character.encode("utf-8"))
            except UnicodeError as error:
                raise ValueError("invalid scalar") from error
        if maximum is not None and size > maximum:
            raise ValueError("canonical byte limit exceeded")
    return size


def _string_size(value: str, *, maximum: int | None = None) -> int:
    if maximum is not None and maximum < 2:
        raise ValueError("canonical byte limit exceeded")
    content_maximum = None if maximum is None else maximum - 2
    return _string_content_size(value, maximum=content_maximum) + 2


def _register_trusted_model_types(roots: tuple[type[BaseModel], ...]) -> None:
    """Pin exact nominal model classes reachable from the public TA roots."""
    pending = list(roots)
    trusted: set[type[BaseModel]] = set()
    while pending:
        candidate = pending.pop()
        if candidate in trusted:
            continue
        if not isinstance(candidate, type) or not issubclass(candidate, BaseModel):
            continue
        trusted.add(candidate)
        for field in candidate.model_fields.values():
            annotations = [field.annotation]
            while annotations:
                annotation = annotations.pop()
                if isinstance(annotation, type) and issubclass(
                    annotation, BaseModel,
                ):
                    pending.append(annotation)
                else:
                    annotations.extend(get_args(annotation))
    global _TRUSTED_MODEL_TYPES
    _TRUSTED_MODEL_TYPES = frozenset(trusted)


def _model_items(
    value: BaseModel,
    inherited_material: object | None = None,
    *,
    validate_binding: bool = False,
) -> tuple[tuple[tuple[str, object], ...], object | None]:
    if type(value) not in _TRUSTED_MODEL_TYPES:
        raise ValueError("invalid model type")
    field_map = type(value).model_fields
    fields = tuple(field_map)
    stored = object.__getattribute__(value, "__dict__")
    if type(stored) is not dict or any(type(name) is not str for name in stored):
        raise ValueError("model storage contains invalid field names")
    private_names = set(getattr(type(value), "__private_attributes__", {}))
    extras_value = object.__getattribute__(value, "__pydantic_extra__")
    private_value = object.__getattribute__(value, "__pydantic_private__")
    if extras_value is None:
        extras = {}
    elif type(extras_value) is dict and all(
        type(name) is str for name in extras_value
    ):
        extras = extras_value
    else:
        raise ValueError("model extra storage is invalid")
    if private_value is None:
        private = {}
    elif type(private_value) is dict and all(
        type(name) is str for name in private_value
    ):
        private = private_value
    else:
        raise ValueError("model private storage is invalid")
    hidden = set(stored) - set(fields) - private_names
    missing = set(fields) - set(stored)
    if hidden or missing or extras:
        raise ValueError("model contains hidden, missing, or extra content")
    if set(private) - private_names:
        raise ValueError("model contains unexpected private content")
    local_material = stored["material"] if "material" in field_map else (
        inherited_material
    )
    if validate_binding and "_material" in private_names:
        private_material = (
            stored.get("_material")
            if "_material" in stored else private.get("_material")
        )
        if local_material is None or private_material is not local_material:
            raise ValueError("model private material binding is substituted")
    return (
        tuple((name, stored[name]) for name in fields),
        local_material,
    )


def _container(
    value: object,
    inherited_material: object | None,
) -> tuple[
    Iterator[tuple[str | int, object]], int, int, object | None, bool, int,
] | None:
    """Return children and O(1) structural facts for a container."""
    if isinstance(value, BaseModel):
        items, local_material = _model_items(
            value, inherited_material, validate_binding=True,
        )
        punctuation = 2 + max(len(items) - 1, 0)
        return (
            iter(items), punctuation, id(value), local_material, True,
            len(items),
        )
    if type(value) is dict:
        punctuation = 2 + max(len(value) - 1, 0)
        return (
            iter(value.items()), punctuation, id(value), inherited_material,
            True, len(value),
        )
    if type(value) in (tuple, list):
        punctuation = 2 + max(len(value) - 1, 0)
        return (
            iter(enumerate(value)), punctuation, id(value), inherited_material,
            False, len(value),
        )
    return None


def _scalar_size(value: object, *, maximum: int) -> int:
    if value is None:
        return 4
    if type(value) is bool:
        return 4 if value else 5
    if type(value) is str:
        return _string_size(value, maximum=maximum)
    if type(value) is int:
        digit_budget = maximum - (1 if value < 0 else 0)
        if digit_budget < 1:
            raise ValueError("canonical byte limit exceeded")
        # 3.32193 is a strict upper bound for log2(10).  Beyond this
        # threshold the decimal representation cannot fit, so refuse before
        # allocating it.  The narrow ambiguous boundary can allocate at most
        # the admitted digit budget plus one character.
        maximum_bits = (digit_budget * 332_193 + 99_999) // 100_000
        if value and value.bit_length() > maximum_bits:
            raise ValueError("canonical byte limit exceeded")
        try:
            size = len(str(value))
        except (ValueError, OverflowError) as error:
            raise ValueError("invalid scalar") from error
        if size > maximum:
            raise ValueError("canonical byte limit exceeded")
        return size
    if type(value) is float:
        size = len(_float_token(value))
        if size > maximum:
            raise ValueError("canonical byte limit exceeded")
        return size
    if type(value) is datetime:
        return _string_size(_datetime_token(value), maximum=maximum)
    raise ValueError("invalid scalar")


def _boolean_index(name: str | int | None, parent_name: str | None) -> bool:
    if type(name) is str and (
        name.endswith("_index")
        or name.endswith("_count")
        or name in _STRICT_INTEGER_NAMES
    ):
        return True
    return type(parent_name) is str and parent_name.endswith("_indices")


def _preflight_graph(
    value: object,
    *,
    max_nodes: int = MAXIMUM_RECONSTRUCTED_NODES,
    max_depth: int = MAXIMUM_NESTING_DEPTH,
    max_bytes: int = MAXIMUM_CANONICAL_REQUEST_BYTES,
) -> _PreflightResult:
    """Inspect without serialization, recursive descent, or caller equality."""
    if (
        type(max_nodes) is not int
        or max_nodes < 1
        or type(max_depth) is not int
        or max_depth < 0
        or type(max_bytes) is not int
        or max_bytes < 1
    ):
        raise ValueError("invalid preflight configuration")

    nodes = 0
    maximum_depth = 0
    byte_count = 0
    active: set[int] = set()
    current = (None, None, value, 0, None)
    frames: list[tuple[
        Iterator[tuple[str | int, object]], int, int, str | None, object | None,
        bool,
    ]] = []

    while True:
        name, parent_name, item, depth, inherited_material = current
        if depth > max_depth:
            raise ValueError("nesting depth limit exceeded")
        nodes += 1
        if nodes > max_nodes:
            raise ValueError("reconstructed node limit exceeded")
        maximum_depth = max(maximum_depth, depth)

        if type(item) is bool and _boolean_index(name, parent_name):
            raise ValueError("boolean index is invalid")
        container = _container(item, inherited_material)
        if container is None:
            byte_count += _scalar_size(item, maximum=max_bytes - byte_count)
        else:
            (
                children, structural_bytes, identity, local_material,
                mapping, child_count,
            ) = container
            if identity in active:
                raise ValueError("cyclic content is invalid")
            if nodes + child_count > max_nodes:
                raise ValueError("reconstructed node limit exceeded")
            if (
                name == "evidence_alignments" and child_count > 128
            ) or (
                name == "conditions"
                and parent_name in {"from_classification", "to_classification"}
                and child_count > 64
            ) or (
                name == "condition_traces" and child_count > 128
            ) or (
                name == "condition_trace_indices" and child_count > 64
            ):
                raise ValueError("fixed container cardinality exceeded")
            active.add(identity)
            byte_count += structural_bytes
            frames.append((children, depth, identity,
                           name if type(name) is str else parent_name,
                           local_material, mapping))

        if byte_count > max_bytes:
            raise ValueError("canonical byte limit exceeded")

        while frames:
            (
                children, container_depth, identity, container_name, material,
                mapping,
            ) = frames[-1]
            try:
                child_name, child = next(children)
            except StopIteration:
                frames.pop()
                active.remove(identity)
                continue
            if mapping:
                if type(child_name) is not str:
                    raise ValueError("mapping key must be an ordinary string")
                key_budget = max_bytes - byte_count
                if key_budget < 1:
                    raise ValueError("canonical byte limit exceeded")
                byte_count += (
                    _string_size(child_name, maximum=key_budget - 1) + 1
                )
            current = (
                child_name,
                container_name,
                child,
                container_depth + 1,
                material,
            )
            break
        else:
            return _PreflightResult(nodes, maximum_depth, byte_count)


def _plain_graph(value: object) -> object:
    """Create ordinary content only after a successful bounded preflight."""
    if isinstance(value, BaseModel):
        items, _ = _model_items(value)
        return {
            name: _plain_graph(item)
            for name, item in items
        }
    if type(value) is dict:
        return {key: _plain_graph(item) for key, item in value.items()}
    if type(value) is tuple:
        return tuple(_plain_graph(item) for item in value)
    if type(value) is list:
        return [_plain_graph(item) for item in value]
    return value


def _graphs_have_same_shape(left: object, right: object) -> bool:
    """Compare admitted content without coercive cross-type equality."""
    pending = [(left, right)]
    while pending:
        first, second = pending.pop()
        if isinstance(second, BaseModel):
            try:
                items, _ = _model_items(second)
            except ValueError:
                return False
            second = {name: item for name, item in items}
        if type(first) is dict:
            if (
                type(second) is not dict
                or len(first) != len(second)
                or set(first) != set(second)
            ):
                return False
            pending.extend((first[key], second[key]) for key in first)
        elif type(first) in (tuple, list):
            if type(second) not in (tuple, list) or len(first) != len(second):
                return False
            pending.extend(zip(first, second))
        elif type(first) is datetime and type(second) is datetime:
            if first.astimezone(UTC) != second.astimezone(UTC):
                return False
        elif type(first) is not type(second) or first != second:
            return False
    return True


class _CountingSink:
    def __init__(self) -> None:
        self.count = 0

    def write(self, chunk: bytes) -> None:
        self.count += len(chunk)


class _RetainingSink(_CountingSink):
    def __init__(self) -> None:
        super().__init__()
        self.content = bytearray()

    def write(self, chunk: bytes) -> None:
        super().write(chunk)
        self.content.extend(chunk)


def _write_quoted(value: str, sink: _CountingSink) -> None:
    sink.write(b'"')
    escapes = {
        '"': b'\\"', "\\": b"\\\\", "\b": b"\\b", "\f": b"\\f",
        "\n": b"\\n", "\r": b"\\r", "\t": b"\\t",
    }
    for character in value:
        if character in escapes:
            sink.write(escapes[character])
        elif ord(character) < 0x20:
            sink.write(f"\\u{ord(character):04x}".encode("ascii"))
        else:
            sink.write(character.encode("utf-8"))
    sink.write(b'"')


def _encode(value: object, sink: _CountingSink) -> None:
    if value is None:
        sink.write(b"null")
    elif type(value) is bool:
        sink.write(b"true" if value else b"false")
    elif type(value) is str:
        _write_quoted(value, sink)
    elif type(value) is int:
        sink.write(str(value).encode("ascii"))
    elif type(value) is float:
        sink.write(_float_token(value).encode("ascii"))
    elif type(value) is datetime:
        _write_quoted(_datetime_token(value), sink)
    elif type(value) is dict:
        sink.write(b"{")
        for index, key in enumerate(sorted(value)):
            if index:
                sink.write(b",")
            _write_quoted(key, sink)
            sink.write(b":")
            _encode(value[key], sink)
        sink.write(b"}")
    elif type(value) in (tuple, list):
        sink.write(b"[")
        for index, item in enumerate(value):
            if index:
                sink.write(b",")
            _encode(item, sink)
        sink.write(b"]")
    else:
        raise ValueError("invalid scalar")


def _verify_canonical_plain(value: object, expected_size: int) -> None:
    sink = _CountingSink()
    _encode(value, sink)
    if sink.count != expected_size:
        raise ValueError("canonical byte counter disagrees with encoder")


def _canonical_json_bytes(value: object) -> bytes:
    admission = _preflight_graph(value)
    plain = _plain_graph(value)
    sink = _RetainingSink()
    _encode(plain, sink)
    if sink.count != admission.canonical_bytes:
        raise ValueError("canonical byte counter disagrees with encoder")
    return bytes(sink.content)
