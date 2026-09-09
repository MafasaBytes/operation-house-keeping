"""Private, callback-free FC record reconstruction and bounded JSON admission.

Costs are charged on every edge, before expansion. The active path detects
cycles without mistaking shared DAG nodes for free serialized material.
"""

import json
import math
from datetime import UTC, datetime, timezone
from zoneinfo import ZoneInfo

from pydantic import ValidationError
from pydantic_core import PydanticCustomError, TzInfo


class _Invalid(ValueError):
    pass


class _Limit(ValueError):
    pass


def _validation_error(cls, limit=False):
    message = "FC_RECORD_LIMIT_EXCEEDED" if limit else "FC_RECORD_INVALID"
    return ValidationError.from_exception_data(cls.__name__, [{
        "type": PydanticCustomError(message, message), "loc": (), "input": None,
    }], hide_input=True)


def _trusted_classes():
    from backend.model_kernel import contracts as c
    return (c.AuthorityRef, c.OwnerDeclarationEvidence, c.ModelRecordEvidence,
            c.IdentityBindingRecordEvidence, c.SourceRawRecordEvidence,
            c.TemporalOccurrenceEvidence, c.StructuralSourceLocatorEvidence,
            c.FlowOperatingCriterionDeclaration, c.FlowOperatingCriterionWithdrawal)


def _plain_record(value):
    """Reconstruct trusted values, enforcing every supplied-graph budget."""
    trusted = _trusted_classes()
    active = set()
    nodes = containers = byte_count = 0

    def charge(amount):
        nonlocal byte_count
        byte_count += amount
        if byte_count > 131072:
            raise _Limit

    def walk(item, depth=0, path=()):
        nonlocal nodes, containers
        nodes += 1
        if nodes > 8192 or depth > 32:
            raise _Limit
        kind = type(item)
        if kind is str:
            limit = 8192 if path == ("note",) else 1024 if path == ("authority", "agent") else 16384
            if len(item) > limit or len(item.encode("utf-8")) > limit:
                raise _Limit
            charge(len(json.dumps(item, ensure_ascii=False).encode("utf-8")))
            return item
        if item is None or kind is bool:
            charge(4 if item is None or item is True else 5)
            return item
        if kind is int:
            if item.bit_length() > 4096:
                raise _Limit
            # Count decimal digits without the interpreter's configurable
            # integer/string conversion guard (the FC bit ceiling is fixed).
            magnitude = abs(item)
            digits = 1
            while magnitude >= 10:
                magnitude //= 10
                digits += 1
            charge(digits + (item < 0))
            return item
        if kind is float:
            if not math.isfinite(item):
                raise _Invalid
            charge(len(json.dumps(item, allow_nan=False)))
            return item
        if kind is datetime:
            if type(item.tzinfo) not in (timezone, ZoneInfo, TzInfo):
                raise _Invalid
            normalized = item.astimezone(UTC)
            charge(len(json.dumps(normalized.isoformat())))
            return normalized
        model = any(kind is cls for cls in trusted)
        if not model and kind not in (dict, list, tuple):
            raise _Invalid
        identity = id(item)
        if identity in active:
            raise _Invalid
        containers += 1
        if containers > 2048:
            raise _Limit
        active.add(identity)
        try:
            if model:
                contents = object.__getattribute__(item, "__dict__")
                extra = object.__getattribute__(item, "__pydantic_extra__")
                private = object.__getattribute__(item, "__pydantic_private__")
                fields_set = object.__getattribute__(item, "__pydantic_fields_set__")
                declared = kind.model_fields
                if type(contents) is not dict or extra is not None or private is not None:
                    raise _Invalid
                # Check keys safely before hashing or set comparisons.
                if any(type(key) is not str for key in contents):
                    raise _Invalid
                if any(key not in declared for key in contents):
                    raise _Invalid
                if (type(fields_set) is not set
                        or any(type(key) is not str for key in fields_set)
                        or any(key not in declared for key in fields_set)):
                    raise _Invalid
                item = contents
            count = len(item)
            limit = 64 if path in (("evidence",), ("supersedes",)) else 256
            if count > limit:
                raise _Limit
            charge(2 + max(0, count - 1))
            if model or kind is dict:
                result = {}
                for key, child in item.items():
                    if type(key) is not str:
                        raise _Invalid
                    walk(key, depth + 1)
                    charge(1)
                    result[key] = walk(child, depth + 1, path + (key,))
                return result
            return [walk(child, depth + 1, path + (index,))
                    for index, child in enumerate(item)]
        finally:
            active.remove(identity)

    try:
        return walk(value)
    except UnicodeError as error:
        raise _Invalid from error
    except (MemoryError, RecursionError, OverflowError) as error:
        raise _Limit from error


def _parse_record_json(value):
    """Raw length/depth scan precedes duplicate-rejecting recursive parsing."""
    if type(value) not in (str, bytes):
        raise _Invalid
    try:
        # The character check avoids a large UTF-8 allocation for raw strings.
        if len(value) > 1048576:
            raise _Limit
        if type(value) is str:
            if len(value.encode("utf-8")) > 1048576:
                raise _Limit
        else:
            value = value.decode("utf-8")
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
                # Root container is depth zero; nested containers are edges.
                if depth > 33:
                    raise _Limit
            elif char in "]}":
                depth -= 1

        def pairs(items):
            result = {}
            for key, child in items:
                if key in result:
                    raise _Invalid
                result[key] = child
            return result

        def integer(text):
            if len(text.removeprefix("-")) > 1234:
                raise _Limit
            digits = text.removeprefix("-")
            result = 0
            for start in range(0, len(digits), 9):
                chunk = digits[start:start + 9]
                result = result * 10 ** len(chunk) + int(chunk)
            if text.startswith("-"):
                result = -result
            if result.bit_length() > 4096:
                raise _Limit
            return result

        def constant(text):
            raise _Invalid

        return _plain_record(json.loads(value, object_pairs_hook=pairs,
                                       parse_int=integer, parse_constant=constant))
    except (_Invalid, _Limit):
        raise
    except (MemoryError, RecursionError, OverflowError) as error:
        raise _Limit from error
    except (ValueError, UnicodeError) as error:
        raise _Invalid from error
