"""Deterministic serialization and content-derived record identity for the
model ledger.

Byte-parity with ``identity_binding.canonical`` is a normative claim held
by shared golden test vectors — the rules are identical: the digest input
is the VALIDATED model, keys sorted, compact separators, timestamps
UTC-normalized to Python's ``+00:00`` ISO form, ``record_id`` excluded
from its own hash. Equal instants under different offsets hash
identically, and any edit to a stored record is self-evident. This module
is duck-typed and imports nothing from ``contracts`` (the import direction
mirrors identity_binding exactly).
"""

import hashlib
import json
from datetime import UTC, datetime

_PREFIX_BY_KIND = {
    "entity_registration": "reg",
    "relationship_type_definition": "rtd",
    "relationship_assertion": "rel",
    "relationship_withdrawal": "rwd",
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


def canonical_sort_key(model) -> bytes:
    """Full canonical serialization INCLUDING any record_id field. For
    evidence references, record_id is DATA naming the cited record — not
    self-identity — so two references differing only in record_id are
    distinct evidence and must never share an identity key."""
    return json.dumps(
        _canonical_value(model.model_dump(mode="python")), sort_keys=True,
        separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")


def compute_revision_id(model_id: str, record_ids) -> str:
    material = "\n".join([model_id, *sorted(record_ids)])
    return "mrv_" + hashlib.sha256(material.encode("utf-8")).hexdigest()
