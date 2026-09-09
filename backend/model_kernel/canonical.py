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

from backend.model_kernel.errors import ModelIntegrityError

_PREFIX_BY_KIND = {
    "entity_registration": "reg",
    "variable_registration": "vrg",
    "variable_value_specification": "vsp",
    "variable_semantic_declaration": "vsm",
    "constraint_registration": "crg",
    "variable_constraint_declaration": "vcn",
    "relationship_type_definition": "rtd",
    "relationship_assertion": "rel",
    "relationship_withdrawal": "rwd",
    "port_registration": "prg",
    "port_interface_declaration": "pif",
    "port_connection_assertion": "pcn",
    "port_compatibility_declaration": "pcm",
    "port_claim_withdrawal": "ptw",
    "variable_port_association": "vpa",
    "variable_port_association_withdrawal": "vpw",
    "behavior_registration": "brg",
    "behavior_rule_declaration": "bhd",
    "behavior_rule_withdrawal": "bhw",
    "state_registration": "srg",
    "state_declaration": "std",
    "state_declaration_withdrawal": "stw",
    "transition_registration": "trg",
    "transition_declaration": "trd",
    "transition_declaration_withdrawal": "trw",
    "flow_registration": "frg",
    "flow_declaration": "fld",
    "flow_declaration_withdrawal": "flw",
    "flow_measurement_association": "fma",
    "flow_measurement_association_withdrawal": "fmw",
    "flow_operating_criterion_declaration": "fcd",
    "flow_operating_criterion_withdrawal": "fcw",
}

_BEHAVIOR_EFFECTIVE_BODY_FIELDS = (
    "behavior_anchor_id",
    "context",
    "participant_semantics",
    "rule",
    "evaluation_basis",
)

_STATE_EFFECTIVE_BODY_FIELDS = (
    "state_anchor_id",
    "context",
    "conditions",
    "evaluation_basis",
)

_TRANSITION_EFFECTIVE_BODY_FIELDS = (
    "transition_anchor_id",
    "context",
    "from_endpoint",
    "to_endpoint",
)

_FLOW_EFFECTIVE_BODY_FIELDS = (
    "flow_anchor_id",
    "context",
    "connection_assertion_record_id",
    "source_direction_pins",
    "sink_direction_pins",
)

_FLOW_MEASUREMENT_EFFECTIVE_BODY_FIELDS = (
    "flow_anchor_id",
    "variable_anchor_id",
    "participant_port_anchor_id",
    "context",
    "orientation",
    "flow_registration_record_id",
    "variable_registration_record_id",
    "port_registration_record_id",
    "flow_declaration_record_id",
    "variable_port_association_record_id",
    "variable_semantic_declaration_record_id",
)


def _canonical_value(value):
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat()
    if isinstance(value, dict):
        return {key: _canonical_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_canonical_value(item) for item in value]
    return value


def _validated_flow_criterion(record):
    """New-family strict boundary; old canonical dispatch remains unchanged."""
    from backend.model_kernel.contracts import (
        FlowOperatingCriterionDeclaration, FlowOperatingCriterionWithdrawal,
    )
    from pydantic import ValidationError
    classes = (FlowOperatingCriterionDeclaration, FlowOperatingCriterionWithdrawal)
    kind = type(record)
    if not any(base is cls for base in type.__getattribute__(kind, "__mro__")
               for cls in classes):
        return record
    if not any(kind is cls for cls in classes):
        raise ModelIntegrityError("MODEL_RECORD_INVALID", "invalid flow criterion record")
    try:
        return kind.model_validate(record)
    except ValidationError as error:
        limit = any(item["type"] == "FC_RECORD_LIMIT_EXCEEDED" for item in error.errors())
        code = "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED" if limit else "MODEL_RECORD_INVALID"
        raise ModelIntegrityError(code, "invalid flow criterion record") from error


def canonical_payload(record) -> dict:
    record = _validated_flow_criterion(record)
    dumped = record.model_dump(mode="python", exclude={"record_id"})
    return _canonical_value(dumped)


def canonical_bytes(record) -> bytes:
    """Canonical bytes of a record. Content that cannot be serialized or
    UTF-8 encoded — a lone surrogate from hand-deserialized JSON, for
    instance — is a structural defect, not an escape hatch."""
    try:
        return json.dumps(
            canonical_payload(record), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (UnicodeError, TypeError, ValueError) as error:
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            "record content is not canonically serializable") from error


def _behavior_effective_body_bytes(record) -> bytes:
    """Canonical, non-persisted BH engineering-body projection.

    Slice A provides only this private deterministic primitive. Public body
    groups, corroboration findings, and conflict conclusions remain Slice B.
    The caller supplies an authoritative reconstructed declaration.
    """
    try:
        dumped = record.model_dump(
            mode="python", include=set(_BEHAVIOR_EFFECTIVE_BODY_FIELDS))
        if tuple(sorted(dumped)) != tuple(sorted(
                _BEHAVIOR_EFFECTIVE_BODY_FIELDS)):
            raise ValueError("record is not a behavior rule declaration")
        return json.dumps(
            _canonical_value(dumped), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (AttributeError, UnicodeError, TypeError, ValueError) as error:
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            "behavior body is not canonically serializable") from error


def _state_effective_body_bytes(record) -> bytes:
    """Canonical, non-persisted ST engineering-body projection.

    Slice A exposes no public lifecycle result. This private primitive gives
    later kernel disclosure a deterministic projection without confusing
    evidence or audit metadata with state engineering content.
    """
    try:
        dumped = record.model_dump(
            mode="python", include=set(_STATE_EFFECTIVE_BODY_FIELDS))
        if tuple(sorted(dumped)) != tuple(sorted(_STATE_EFFECTIVE_BODY_FIELDS)):
            raise ValueError("record is not a state declaration")
        return json.dumps(
            _canonical_value(dumped), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (AttributeError, UnicodeError, TypeError, ValueError) as error:
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            "state body is not canonically serializable") from error


def _transition_effective_body_bytes(record) -> bytes:
    """Canonical, non-persisted ST-002 declaration-body projection.

    Slice A exposes no public transition lifecycle result. The projection
    preserves the semantic from/to roles and excludes evidence and audit
    fields so a later read-only disclosure can group exact engineering bodies.
    """
    try:
        dumped = record.model_dump(
            mode="python", include=set(_TRANSITION_EFFECTIVE_BODY_FIELDS))
        if tuple(sorted(dumped)) != tuple(sorted(
                _TRANSITION_EFFECTIVE_BODY_FIELDS)):
            raise ValueError("record is not a transition declaration")
        return json.dumps(
            _canonical_value(dumped), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (AttributeError, UnicodeError, TypeError, ValueError) as error:
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            "transition body is not canonically serializable") from error


def _flow_effective_body_bytes(record) -> bytes:
    """Canonical, non-persisted FL-001 declaration-body projection."""
    try:
        dumped = record.model_dump(
            mode="python", include=set(_FLOW_EFFECTIVE_BODY_FIELDS))
        if tuple(sorted(dumped)) != tuple(sorted(
                _FLOW_EFFECTIVE_BODY_FIELDS)):
            raise ValueError("record is not a flow declaration")
        return json.dumps(
            _canonical_value(dumped), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (AttributeError, UnicodeError, TypeError, ValueError) as error:
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            "flow body is not canonically serializable") from error


def _flow_measurement_effective_body_bytes(record) -> bytes:
    """Canonical, non-persisted FM-001 effective-body projection."""
    try:
        dumped = record.model_dump(
            mode="python", include=set(_FLOW_MEASUREMENT_EFFECTIVE_BODY_FIELDS))
        if tuple(sorted(dumped)) != tuple(sorted(
                _FLOW_MEASUREMENT_EFFECTIVE_BODY_FIELDS)):
            raise ValueError("record is not a flow-measurement association")
        return json.dumps(
            _canonical_value(dumped), sort_keys=True, separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    except (AttributeError, UnicodeError, TypeError, ValueError) as error:
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            "flow-measurement body is not canonically serializable") from error


def compute_record_id(record) -> str:
    record = _validated_flow_criterion(record)
    try:
        prefix = _PREFIX_BY_KIND[record.record_kind]
    except (KeyError, AttributeError, TypeError) as error:
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            "record does not declare a known model record kind") from error
    digest = hashlib.sha256(canonical_bytes(record)).hexdigest()
    return f"{prefix}_{digest}"


def verify_record_id(record) -> bool:
    return compute_record_id(record) == record.record_id


def build_record(record_cls, **fields):
    """Construct a ledger record with its content-derived id. A placeholder
    id satisfies the pattern during the first validation pass; the real id
    is computed from the validated content, which excludes the id itself.

    An operational public entry point: a class that is not a known record
    kind, missing or invalid fields, and pydantic ``ValidationError`` (a
    ``ValueError``) all fail typed. The message is path-free and never
    echoes field values — the record class name at most."""
    from typing import get_args
    from backend.model_kernel.contracts import (
        FlowOperatingCriterionDeclaration, FlowOperatingCriterionWithdrawal, ModelRecord,
    )
    # Identity comparisons never inspect caller-controlled class attributes.
    if not any(record_cls is known for known in get_args(ModelRecord)):
        raise ModelIntegrityError("MODEL_RECORD_INVALID", "could not build a valid model record")
    if record_cls is FlowOperatingCriterionDeclaration or record_cls is FlowOperatingCriterionWithdrawal:
        from pydantic import ValidationError
        try:
            prefix = "fcd" if record_cls is FlowOperatingCriterionDeclaration else "fcw"
            draft = record_cls(record_id=prefix + "_" + "0" * 64, **fields)
            final = draft.model_dump(mode="python")
            final["record_id"] = compute_record_id(draft)
            return record_cls.model_validate(final)
        except (TypeError, ValueError) as error:
            limit = isinstance(error, ValidationError) and any(
                item["type"] == "FC_RECORD_LIMIT_EXCEEDED" for item in error.errors())
            code = "MODEL_FLOW_CRITERION_RECORD_LIMIT_EXCEEDED" if limit else "MODEL_RECORD_INVALID"
            raise ModelIntegrityError(code, "could not build a valid flow criterion record") from error
    try:
        kind = record_cls.model_fields["record_kind"].default
        placeholder = f"{_PREFIX_BY_KIND[kind]}_{'0' * 64}"
        draft = record_cls(record_id=placeholder, **fields)
        # finalization stays inside the typed net: a duck-typed draft can
        # fail here first (model_copy/model_dump lookup precedes hashing)
        return draft.model_copy(update={"record_id": compute_record_id(draft)})
    except (AttributeError, KeyError, TypeError, ValueError) as error:
        name = getattr(record_cls, "__name__", "record")
        if not isinstance(name, str) or not name.isidentifier():
            name = "record"  # never interpolate an attacker-shaped name
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            f"could not build a valid {name} model record") from error


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
