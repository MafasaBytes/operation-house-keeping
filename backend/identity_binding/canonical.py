"""Deterministic serialization and content-derived record identity.

The digest input is the VALIDATED model, never raw file bytes: keys
sorted, compact separators, timestamps UTC-normalized and serialized with
Python's ``+00:00`` ISO form, and ``record_id`` excluded from its own
hash. Equal instants under different offsets therefore hash identically,
and any edit to a stored record is self-evident (content no longer
matches its id).
"""

import hashlib
import json
from datetime import UTC, datetime

_PREFIX_BY_KIND = {
    "anchor_declaration": "anc",
    "binding_assertion": "iba",
    "binding_retraction": "ibr",
    "applicability_closure": "ibc",
    "binding_rejection": "ibj",
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
    dumped = record.model_dump(mode="python", exclude={"record_id"})
    return _canonical_value(dumped)


def canonical_bytes(record) -> bytes:
    return json.dumps(
        canonical_payload(record), sort_keys=True, separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def compute_record_id(record) -> str:
    prefix = _PREFIX_BY_KIND[record.record_kind]
    digest = hashlib.sha256(canonical_bytes(record)).hexdigest()
    return f"{prefix}_{digest}"


def verify_record_id(record) -> bool:
    return compute_record_id(record) == record.record_id


def build_record(record_cls, **fields):
    """Construct a ledger record with its content-derived id. A placeholder
    id satisfies the pattern during the first validation pass; the real id
    is computed from the validated content, which excludes the id itself."""
    kind = record_cls.model_fields["record_kind"].default
    placeholder = f"{_PREFIX_BY_KIND[kind]}_{'0' * 64}"
    draft = record_cls(record_id=placeholder, **fields)
    return draft.model_copy(update={"record_id": compute_record_id(draft)})


def compute_revision_id(binding_set_id: str, record_ids) -> str:
    material = "\n".join([binding_set_id, *sorted(record_ids)])
    return "rev_" + hashlib.sha256(material.encode("utf-8")).hexdigest()
