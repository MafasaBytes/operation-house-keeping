"""Callback-free, bounded validation for FC-001 Slice B result graphs."""

import json
import math
from datetime import UTC, datetime, timezone
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import (
    BaseModel, ConfigDict, Discriminator, Tag, TypeAdapter, ValidationError,
)

import backend.model_kernel.contracts as _contracts
import backend.system_identity as _identity


_MAX_BYTES = 4_194_304
_MAX_NODES = 262_144
_MAX_CONTAINERS = 65_536
_MAX_DEPTH = 64
_MAX_STRING_BYTES = 65_536
_MAX_ITEMS = 4_096
_PARSED_TIMEZONE_TYPE = type(TypeAdapter(datetime).validate_python(
    "2000-01-01T00:00:00+00:00").tzinfo)


class FCResultInvalid(ValueError):
    """A supplied FC result is structurally invalid."""


class FCResultLimit(ValueError):
    """A supplied or derived FC result exceeds its fixed resource budget."""


def _missing_error_tag(value):
    # The adapters receive only None; caller data never reaches a discriminator.
    return None


_ERROR_ADAPTERS = {
    limit: TypeAdapter(
        Annotated[
            Annotated[str, Tag("text")] | Annotated[int, Tag("integer")],
            Discriminator(
                _missing_error_tag,
                custom_error_type=message,
                custom_error_message=message,
            ),
        ],
        config=ConfigDict(
            title="FlowOperatingCriterionResult",
            hide_input_in_errors=True,
        ),
    )
    for limit, message in (
        (False, "FC_RESULT_INVALID"),
        (True, "FC_RESULT_LIMIT_EXCEEDED"),
    )
}


def result_validation_error(*, limit: bool) -> ValidationError:
    """Create one fixed, value-free public validation failure."""
    try:
        _ERROR_ADAPTERS[limit].validate_python(None)
    except ValidationError as error:
        return error
    raise AssertionError("fixed FC result error discriminator unexpectedly matched")


def _module_model_types(module) -> tuple[type[BaseModel], ...]:
    return tuple(value for value in vars(module).values()
                 if isinstance(value, type) and issubclass(value, BaseModel))


# Freeze the accepted lower model vocabulary when this module is imported.
_TRUSTED_LOWER_MODELS = (
    *_module_model_types(_contracts),
    *_module_model_types(_identity),
)


def plain_result(value, result_models: tuple[type[BaseModel], ...]):
    """Return callback-free plain data while charging every expanded edge."""
    trusted = (*_TRUSTED_LOWER_MODELS, *result_models)
    active: set[int] = set()
    nodes = containers = byte_count = 0

    def charge(amount: int) -> None:
        nonlocal byte_count
        byte_count += amount
        if byte_count > _MAX_BYTES:
            raise FCResultLimit

    def walk(item, depth=0):
        nonlocal nodes, containers
        nodes += 1
        if nodes > _MAX_NODES or depth > _MAX_DEPTH:
            raise FCResultLimit
        kind = type(item)
        if kind is str:
            try:
                encoded = item.encode("utf-8")
            except UnicodeError as error:
                raise FCResultInvalid from error
            if len(encoded) > _MAX_STRING_BYTES:
                raise FCResultLimit
            charge(len(json.dumps(
                item, ensure_ascii=False, allow_nan=False).encode("utf-8")))
            return item
        if item is None or kind is bool:
            charge(4 if item is None or item is True else 5)
            return item
        if kind is int:
            if item.bit_length() > 4096:
                raise FCResultLimit
            magnitude = abs(item)
            digits = 1
            while magnitude >= 10:
                magnitude //= 10
                digits += 1
            charge(digits + (item < 0))
            return item
        if kind is float:
            if not math.isfinite(item):
                raise FCResultInvalid
            charge(len(json.dumps(item, allow_nan=False)))
            return item
        if kind is datetime:
            if type(item.tzinfo) not in (
                    timezone, ZoneInfo, _PARSED_TIMEZONE_TYPE):
                raise FCResultInvalid
            normalized = item.astimezone(UTC)
            charge(len(json.dumps(normalized.isoformat())))
            return normalized

        model = any(kind is candidate for candidate in trusted)
        if model:
            try:
                contents = object.__getattribute__(item, "__dict__")
                extra = object.__getattribute__(item, "__pydantic_extra__")
                private = object.__getattribute__(item, "__pydantic_private__")
                fields_set = object.__getattribute__(
                    item, "__pydantic_fields_set__")
            except AttributeError as error:
                raise FCResultInvalid from error
            declared = kind.model_fields
            if (type(contents) is not dict
                    or (extra is not None
                        and (type(extra) is not dict or extra))
                    or (private is not None
                        and (type(private) is not dict or private))
                    or type(fields_set) is not set
                    or any(type(name) is not str for name in fields_set)
                    or any(name not in declared for name in fields_set)
                    or any(type(name) is not str for name in contents)
                    or any(name not in declared for name in contents)):
                raise FCResultInvalid
            item = contents
            kind = dict
        if kind not in (dict, list, tuple):
            raise FCResultInvalid
        identity = id(item)
        if identity in active:
            raise FCResultInvalid
        containers += 1
        if containers > _MAX_CONTAINERS or len(item) > _MAX_ITEMS:
            raise FCResultLimit
        active.add(identity)
        try:
            charge(2 + max(0, len(item) - 1))
            if kind is dict:
                result = {}
                for key, child in item.items():
                    if type(key) is not str:
                        raise FCResultInvalid
                    plain_key = walk(key, depth + 1)
                    charge(1)
                    result[plain_key] = walk(child, depth + 1)
                return result
            return [walk(child, depth + 1) for child in item]
        finally:
            active.remove(identity)

    try:
        return walk(value)
    except (MemoryError, RecursionError, OverflowError) as error:
        raise FCResultLimit from error


def enforce_result_cardinality(value) -> None:
    """Enforce the FC-specific limits not implied by the generic graph caps."""
    if type(value) is not dict:
        return
    material = value.get("material")
    if type(material) is dict:
        records = material.get("records")
        if type(records) in (list, tuple) and len(records) > 2_048:
            raise FCResultLimit
    subject = value.get("subject")
    if subject is None:
        return
    if type(subject) is not dict:
        return
    roots = subject.get("roots", ())
    fm_roots = subject.get("fm_roots", ())
    groups = subject.get("body_groups", ())
    for rows in (roots, fm_roots, groups):
        if type(rows) in (list, tuple) and len(rows) > 512:
            raise FCResultLimit
    fc_records = sum(len(row.get("lineage_record_indices", ()))
                     for row in roots if type(row) is dict)
    fm_records = sum(len(row.get("lineage_record_indices", ()))
                     for row in fm_roots if type(row) is dict)
    if fc_records > 512 or fm_records > 512:
        raise FCResultLimit
    support_count = 0
    for group in groups:
        if type(group) is not dict:
            continue
        support = group.get("support_rows", ())
        if type(support) in (list, tuple):
            if len(support) > 73:
                raise FCResultLimit
            support_count += len(support)
    if len(roots) + len(fm_roots) + len(groups) + support_count > 8_192:
        raise FCResultLimit


def parse_result_json(value):
    """Bound and duplicate-check JSON before Pydantic recursive parsing."""
    if type(value) not in (str, bytes):
        raise FCResultInvalid
    try:
        if len(value) > _MAX_BYTES:
            raise FCResultLimit
        if type(value) is bytes:
            value = value.decode("utf-8")
        elif len(value.encode("utf-8")) > _MAX_BYTES:
            raise FCResultLimit
        depth = 0
        quoted = escaped = False
        for char in value:
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in "[{":
                depth += 1
                if depth > _MAX_DEPTH + 1:
                    raise FCResultLimit
            elif char in "]}":
                depth -= 1

        def pairs(items):
            result = {}
            for key, child in items:
                if key in result:
                    raise FCResultInvalid
                result[key] = child
            return result

        def integer(text):
            digits = text.removeprefix("-")
            if len(digits) > 1_234:
                raise FCResultLimit
            result = 0
            for start in range(0, len(digits), 9):
                chunk = digits[start:start + 9]
                result = result * 10 ** len(chunk) + int(chunk)
            if text.startswith("-"):
                result = -result
            if result.bit_length() > 4_096:
                raise FCResultLimit
            return result

        def constant(text):
            raise FCResultInvalid

        return json.loads(
            value,
            object_pairs_hook=pairs,
            parse_int=integer,
            parse_constant=constant,
        )
    except (FCResultInvalid, FCResultLimit):
        raise
    except (MemoryError, RecursionError, OverflowError) as error:
        raise FCResultLimit from error
    except (ValueError, UnicodeError) as error:
        raise FCResultInvalid from error
