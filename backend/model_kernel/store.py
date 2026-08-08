"""Write-once model-ledger store with VALIDATING append.

Deliberate, owner-approved divergence from identity_binding's record-local
append: kernel records form a referential graph, so `append` fully
validates the current set and then the prospective set before promoting —
absent filesystem tampering, the on-disk ledger is a valid revision after
every successful append. Load-time full validation is retained because
crafted files bypass `append`. Honest single-writer assumption; staging
outside the scanned directory; atomic promote; no fsync-grade durability
claim. Error messages carry model ids, record ids, file names, and stable
codes — never absolute paths.
"""

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Mapping

from pydantic import TypeAdapter, ValidationError

from backend.model_kernel.canonical import (
    canonical_payload,
    compute_revision_id,
    verify_record_id,
)
from backend.model_kernel.contracts import (
    EntityRegistration,
    MODEL_ID_PATTERN,
    MODEL_RECORD_ID_PATTERN,
    ModelConfigurationError,
    ModelIntegrityError,
    ModelRecord,
    ModelRevision,
    RelationshipAssertion,
    RelationshipTypeDefinition,
    RelationshipWithdrawal,
)

_RECORD_ADAPTER: TypeAdapter = TypeAdapter(ModelRecord)
_RECORD_ID = re.compile(MODEL_RECORD_ID_PATTERN)
_FILENAME = re.compile(r"^(reg|rtd|rel|rwd)_[0-9a-f]{64}\.json$")

_EMPTY: Mapping = MappingProxyType({})

_LINEAGE_INVARIANTS = ("type_name", "directionality", "hierarchy_semantics",
                       "context_requirement")


def _frozen_mapping(mapping: Mapping) -> Mapping:
    """A COPIED read-only view: neither input mutation nor view mutation
    can alter a validated revision."""
    return MappingProxyType(dict(mapping))


@dataclass(frozen=True)
class LoadedModel:
    """A validated revision plus derived read-only indexes. Assertions are
    ACTIVE/inactive (lifecycle links); type chain tips are CURRENT."""

    revision: ModelRevision
    records: Mapping[str, ModelRecord]
    registrations_by_anchor: Mapping[str, EntityRegistration]
    types: Mapping[str, RelationshipTypeDefinition]
    current_type_by_name: Mapping[str, str]
    type_name_by_id: Mapping[str, str]
    assertions: Mapping[str, RelationshipAssertion]
    withdrawals: Mapping[str, RelationshipWithdrawal]
    superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    withdrawn_by: Mapping[str, tuple[str, ...]] = _EMPTY


def _fail(code: str, message: str) -> None:
    raise ModelIntegrityError(code, message)


def validate_record_collection(
    model_id: str,
    records: Mapping[str, ModelRecord],
    *,
    verify_hashes: bool = True,
) -> LoadedModel:
    """All-or-nothing validation of a record collection (the whole set, a
    prospective append collection, or an explicitly supplied replay
    subset — subsets must be reference-closed and currentness is
    membership-relative)."""
    registrations: dict[str, EntityRegistration] = {}
    types: dict[str, RelationshipTypeDefinition] = {}
    assertions: dict[str, RelationshipAssertion] = {}
    withdrawals: dict[str, RelationshipWithdrawal] = {}

    for record_id, record in records.items():
        if record_id != record.record_id:
            _fail("MODEL_RECORD_KEY_MISMATCH",
                  f"collection key {record_id!r} does not match the record's "
                  f"own id {record.record_id}")
        if verify_hashes and not verify_record_id(record):
            _fail("MODEL_RECORD_HASH_MISMATCH",
                  f"content of {record_id} does not match its id")
        bucket = {
            "entity_registration": registrations,
            "relationship_type_definition": types,
            "relationship_assertion": assertions,
            "relationship_withdrawal": withdrawals,
        }[record.record_kind]
        bucket[record_id] = record

    # -- registrations: exactly one per anchor, no lifecycle --------------
    registrations_by_anchor: dict[str, EntityRegistration] = {}
    for registration in registrations.values():
        anchor_id = registration.anchor.anchor_id
        if anchor_id in registrations_by_anchor:
            _fail("MODEL_DUPLICATE_REGISTRATION",
                  f"{anchor_id} is registered more than once")
        registrations_by_anchor[anchor_id] = registration

    # -- type lineages: invariant fields, acyclic, one current per name ---
    for record_id in sorted(types):
        definition = types[record_id]
        if definition.supersedes is not None:
            predecessor = types.get(definition.supersedes)
            if predecessor is None:
                _fail("MODEL_SUPERSEDES_INVALID",
                      f"{record_id} supersedes a missing type definition")
            for field in _LINEAGE_INVARIANTS:
                if getattr(definition, field) != getattr(predecessor, field):
                    _fail("MODEL_SUPERSEDES_INVALID",
                          f"type supersession may not change {field}; a new "
                          "type name is required instead")
    for definition in types.values():  # acyclicity (defense in depth)
        seen: set[str] = set()
        cursor = definition
        while cursor.supersedes is not None:
            if cursor.record_id in seen:
                _fail("MODEL_SUPERSEDES_INVALID", "type supersession cycle")
            seen.add(cursor.record_id)
            cursor = types[cursor.supersedes]
    type_superseded: set[str] = {
        definition.supersedes for definition in types.values()
        if definition.supersedes is not None}
    current_type_by_name: dict[str, str] = {}
    for record_id in sorted(types):
        definition = types[record_id]
        if record_id in type_superseded:
            continue  # not a current tip
        if definition.type_name in current_type_by_name:
            _fail("MODEL_DUPLICATE_TYPE_NAME",
                  f"type name {definition.type_name!r} has more than one "
                  "current definition (duplicate or branched lineage)")
        current_type_by_name[definition.type_name] = record_id
    type_name_by_id = {record_id: definition.type_name
                       for record_id, definition in types.items()}

    # -- assertions: judged by the EXACT cited definition ------------------
    for record_id in sorted(assertions):
        claim = assertions[record_id]
        cited = types.get(claim.type_id)
        if cited is None:
            _fail("MODEL_REFERENCE_INVALID",
                  f"assertion {record_id} cites a missing type definition")
        for endpoint, kinds in (
                (claim.source_anchor_id, cited.source_referent_kinds),
                (claim.target_anchor_id, cited.target_referent_kinds)):
            registration = registrations_by_anchor.get(endpoint)
            if registration is None:
                _fail("MODEL_REFERENCE_INVALID",
                      f"assertion {record_id} references unregistered "
                      f"anchor {endpoint}")
            if registration.anchor.referent_kind not in kinds:
                _fail("MODEL_ENDPOINT_KIND_INVALID",
                      f"assertion {record_id}: anchor {endpoint} has kind "
                      f"{registration.anchor.referent_kind!r}, not permitted "
                      f"by type {cited.type_name!r}")
        if claim.context.kind != cited.context_requirement:
            _fail("MODEL_CONTEXT_INVALID",
                  f"assertion {record_id} carries a {claim.context.kind} "
                  f"context but type {cited.type_name!r} requires "
                  f"{cited.context_requirement}")
        if (claim.source_anchor_id == claim.target_anchor_id
                and not cited.self_relation_allowed):
            _fail("MODEL_SELF_RELATION_INVALID",
                  f"assertion {record_id}: type {cited.type_name!r} does not "
                  "permit self-relations")
        if claim.supersedes is not None:
            predecessor = assertions.get(claim.supersedes)
            if predecessor is None:
                _fail("MODEL_SUPERSEDES_INVALID",
                      f"assertion {record_id} supersedes a missing assertion")
            predecessor_type = types.get(predecessor.type_id)
            if (predecessor_type is None
                    or predecessor_type.type_name != cited.type_name
                    or predecessor.source_anchor_id != claim.source_anchor_id
                    or predecessor.target_anchor_id != claim.target_anchor_id
                    or predecessor.context != claim.context):
                _fail("MODEL_SUPERSEDES_INVALID",
                      "assertion supersession requires the same type "
                      "lineage, source, target, and context")
        for reference in claim.evidence:
            if (reference.kind == "model_record"
                    and reference.record_id not in records):
                _fail("MODEL_REFERENCE_INVALID",
                      f"assertion {record_id} cites model-record evidence "
                      f"{reference.record_id} absent from the revision")
    for claim in assertions.values():  # supersession acyclicity
        seen = set()
        cursor = claim
        while cursor.supersedes is not None:
            if cursor.record_id in seen:
                _fail("MODEL_SUPERSEDES_INVALID", "assertion supersession cycle")
            seen.add(cursor.record_id)
            cursor = assertions[cursor.supersedes]

    for withdrawal in withdrawals.values():
        if withdrawal.withdraws not in assertions:
            _fail("MODEL_WITHDRAWAL_INVALID",
                  f"{withdrawal.record_id} withdraws a missing assertion")

    superseded_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in assertions}
    withdrawn_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in assertions}
    for claim in assertions.values():
        if claim.supersedes is not None:
            superseded_by[claim.supersedes] = tuple(sorted(
                (*superseded_by[claim.supersedes], claim.record_id)))
    for withdrawal in withdrawals.values():
        withdrawn_by[withdrawal.withdraws] = tuple(sorted(
            (*withdrawn_by[withdrawal.withdraws], withdrawal.record_id)))

    record_ids = tuple(sorted(records))
    revision = ModelRevision(
        revision_id=compute_revision_id(model_id, record_ids),
        record_ids=record_ids, record_count=len(record_ids),
        model_id=model_id)
    return LoadedModel(
        revision=revision, records=_frozen_mapping(records),
        registrations_by_anchor=_frozen_mapping(registrations_by_anchor),
        types=_frozen_mapping(types),
        current_type_by_name=_frozen_mapping(current_type_by_name),
        type_name_by_id=_frozen_mapping(type_name_by_id),
        assertions=_frozen_mapping(assertions),
        withdrawals=_frozen_mapping(withdrawals),
        superseded_by=_frozen_mapping(superseded_by),
        withdrawn_by=_frozen_mapping(withdrawn_by))


class ModelStore:
    def __init__(self, set_dir: Path | str) -> None:
        set_dir = Path(set_dir)
        if not re.fullmatch(MODEL_ID_PATTERN, set_dir.name):
            raise ModelConfigurationError(
                "MODEL_SET_ID_INVALID",
                f"model directory name {set_dir.name!r} must match "
                f"{MODEL_ID_PATTERN}")
        self.model_id = set_dir.name
        self.records_dir = set_dir / "records"
        self.staging_dir = set_dir / ".staging"
        self.records_dir.mkdir(parents=True, exist_ok=True)

    # -- append (VALIDATING; single-writer; atomic promote) ----------------

    def append(self, record: ModelRecord) -> str:
        if not verify_record_id(record):
            raise ModelIntegrityError(
                "MODEL_RECORD_HASH_MISMATCH",
                "record content does not match its record_id")
        # The complete current set is validated before EVERY result — a
        # corrupted sibling fails even an identical re-append.
        current = self.load()
        if record.record_id in current.records:
            if current.records[record.record_id] != record:
                raise ModelIntegrityError(
                    "MODEL_RECORD_HASH_MISMATCH",
                    f"stored {record.record_id} validates but does not "
                    "equal the record being appended")
            return record.record_id  # validated idempotent no-op
        prospective = {**current.records, record.record_id: record}
        validate_record_collection(self.model_id, prospective,
                                   verify_hashes=False)
        payload = {**canonical_payload(record), "record_id": record.record_id}
        text = json.dumps(payload, sort_keys=True, indent=2,
                          ensure_ascii=False) + "\n"
        self.staging_dir.mkdir(parents=True, exist_ok=True)
        from uuid import uuid4

        temp = self.staging_dir / f"{record.record_id}.{uuid4().hex}.tmp"
        temp.write_text(text, encoding="utf-8")
        final = self.records_dir / f"{record.record_id}.json"
        try:
            os.replace(temp, final)
        except OSError:
            temp.unlink(missing_ok=True)
            raise
        return record.record_id

    # -- load / replay -----------------------------------------------------

    def _read_record(self, path: Path) -> ModelRecord:
        try:
            record = _RECORD_ADAPTER.validate_json(
                path.read_text(encoding="utf-8"))
        except (ValidationError, ValueError, OSError) as error:
            raise ModelIntegrityError(
                "MODEL_RECORD_INVALID",
                f"{path.name} is not a valid model record") from error
        if path.name != f"{record.record_id}.json" or not verify_record_id(record):
            raise ModelIntegrityError(
                "MODEL_RECORD_HASH_MISMATCH",
                f"{path.name} does not match its content-derived id")
        return record

    def load(self) -> LoadedModel:
        records: dict[str, ModelRecord] = {}
        for path in self.records_dir.iterdir():
            if not _FILENAME.fullmatch(path.name):
                raise ModelIntegrityError(
                    "MODEL_RECORD_INVALID",
                    f"unexpected file in the model ledger: {path.name}")
            record = self._read_record(path)
            records[record.record_id] = record
        return validate_record_collection(self.model_id, records,
                                          verify_hashes=False)

    def replay(self, record_ids: Iterable[str]) -> LoadedModel:
        """Exact-revision replay from the still-present append-only records.
        Every supplied id is pattern-checked BEFORE any filesystem path is
        constructed; duplicates rejected; the subset must be
        reference-closed."""
        supplied = list(record_ids)
        for record_id in supplied:
            if not _RECORD_ID.fullmatch(record_id):
                raise ModelIntegrityError(
                    "MODEL_REVISION_INVALID",
                    f"{record_id!r} is not a valid model record id")
        if len(set(supplied)) != len(supplied):
            raise ModelIntegrityError(
                "MODEL_REVISION_INVALID",
                "revision membership contains duplicates")
        records: dict[str, ModelRecord] = {}
        for record_id in supplied:
            path = self.records_dir / f"{record_id}.json"
            if not path.exists():
                raise ModelIntegrityError(
                    "MODEL_REVISION_INVALID",
                    f"revision member {record_id} is not present in the set")
            records[record_id] = self._read_record(path)
        return validate_record_collection(self.model_id, records,
                                          verify_hashes=False)
