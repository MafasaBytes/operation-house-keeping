"""Canonical serialization and identity for interpretation records.

This module deliberately imports no contract module. Its byte behavior
parallels the accepted ledger canonicalizers without sharing their code.
"""

import hashlib
import json
from datetime import UTC, datetime

from backend.source_interpretation.errors import InterpretationIntegrityError

_PREFIX_BY_KIND = {
    "source_property_interpretation": "spi",
    "interpretation_retraction": "spr",
    "interpretation_closure": "spc",
    "interpretation_rejection": "spj",
}


def _canonical_value(value):
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, dict):
        return {key: _canonical_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    return value


def canonical_payload(record) -> dict:
    try:
        dumped = record.model_dump(
            mode="python", exclude={"record_id"}, warnings=False)
        return _canonical_value(dumped)
    except (AttributeError, TypeError, ValueError, UnicodeError, Warning) as error:
        raise InterpretationIntegrityError(
            "INTERPRETATION_RECORD_INVALID",
            "record content is not canonically serializable") from error


def canonical_bytes(record) -> bytes:
    try:
        return json.dumps(
            canonical_payload(record), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as error:
        raise InterpretationIntegrityError(
            "INTERPRETATION_RECORD_INVALID",
            "record content is not canonically serializable") from error


def canonical_sort_key(model) -> bytes:
    """Canonical bytes including ids when an id is data rather than self."""
    try:
        return json.dumps(
            _canonical_value(model.model_dump(mode="python", warnings=False)),
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")
    except (AttributeError, TypeError, ValueError, UnicodeError, Warning) as error:
        raise InterpretationIntegrityError(
            "INTERPRETATION_RECORD_INVALID",
            "record content is not canonically serializable") from error


def compute_record_id(record) -> str:
    try:
        prefix = _PREFIX_BY_KIND[record.record_kind]
    except (AttributeError, KeyError, TypeError) as error:
        raise InterpretationIntegrityError(
            "INTERPRETATION_RECORD_INVALID",
            "record does not declare a known interpretation record kind") from error
    return f"{prefix}_{hashlib.sha256(canonical_bytes(record)).hexdigest()}"


def verify_record_id(record) -> bool:
    return compute_record_id(record) == record.record_id


def build_record(record_cls, **fields):
    """Build a validated record with its content-derived id.

    Both validation passes stay inside the typed boundary; attacker-shaped
    field values and raw Pydantic failures are never echoed to callers.
    """
    try:
        kind = record_cls.model_fields["record_kind"].default
        placeholder = f"{_PREFIX_BY_KIND[kind]}_{'0' * 64}"
        draft = record_cls(record_id=placeholder, **fields)
        final = draft.model_copy(update={"record_id": compute_record_id(draft)})
        return record_cls.model_validate(final.model_dump(mode="python"))
    except InterpretationIntegrityError:
        raise
    except (AttributeError, KeyError, TypeError, ValueError, UnicodeError) as error:
        name = getattr(record_cls, "__name__", "record")
        if not isinstance(name, str) or not name.isidentifier():
            name = "record"
        raise InterpretationIntegrityError(
            "INTERPRETATION_RECORD_INVALID",
            f"could not build a valid {name} interpretation record") from error


def compute_revision_id(interpretation_set_id: str, record_ids) -> str:
    material = ("interpretations\n" + interpretation_set_id + "\n"
                + "\n".join(sorted(record_ids)))
    return "irv_" + hashlib.sha256(material.encode("utf-8")).hexdigest()

