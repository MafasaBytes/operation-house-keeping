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
import warnings
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
    VariableRegistration,
    VariableValueSpecification,
)

_RECORD_ADAPTER: TypeAdapter = TypeAdapter(ModelRecord)
_RECORD_ID = re.compile(MODEL_RECORD_ID_PATTERN)
_FILENAME = re.compile(r"^(reg|rtd|rel|rwd|vrg|vsp)_[0-9a-f]{64}\.json$")

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
    variable_registrations_by_anchor: Mapping[str, VariableRegistration] = _EMPTY
    specifications: Mapping[str, VariableValueSpecification] = _EMPTY
    current_specification_tips_by_variable: Mapping[
        str, tuple[VariableValueSpecification, ...]] = _EMPTY
    specification_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY


def _fail(code: str, message: str) -> None:
    raise ModelIntegrityError(code, message)


def revalidate(record) -> ModelRecord:
    """Structurally revalidate a supplied record from plain serialized field
    data at a public trust boundary.

    Belonging to a record class proves nothing: ``model_copy``,
    ``model_construct``, and stale or hand-deserialized instances all
    bypass field validation, and a caller can rehash the result so its
    content-derived id looks authentic. Every public boundary therefore
    re-validates from data and uses the RESULT as the authoritative value —
    so a structurally invalid record can never reach hashing, semantic
    validation, or the ledger. Shape failures (and any serializer warning
    they would raise) surface as a typed, path-free
    ``MODEL_RECORD_INVALID``."""
    try:
        # warnings=False keeps pydantic's serializer warnings from escaping
        # as the public outcome without mutating global warning filters
        payload = record.model_dump(mode="python", warnings=False)
        return _RECORD_ADAPTER.validate_python(payload)
    except (ValidationError, ValueError, TypeError, AttributeError,
            KeyError, UnicodeError, Warning) as error:
        record_id = getattr(record, "record_id", None)
        subject = record_id if isinstance(record_id, str) else "<unidentified>"
        raise ModelIntegrityError(
            "MODEL_RECORD_INVALID",
            f"record {subject} is not structurally valid") from error


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
    variable_registrations: dict[str, VariableRegistration] = {}
    specifications: dict[str, VariableValueSpecification] = {}
    types: dict[str, RelationshipTypeDefinition] = {}
    assertions: dict[str, RelationshipAssertion] = {}
    withdrawals: dict[str, RelationshipWithdrawal] = {}

    if not isinstance(model_id, str) or not re.fullmatch(MODEL_ID_PATTERN,
                                                         model_id):
        raise ModelConfigurationError(
            "MODEL_SET_ID_INVALID", f"{model_id!r} is not a valid model id")
    if not isinstance(records, Mapping):
        _fail("MODEL_RECORD_INVALID",
              "a record collection must be a mapping of record id to record")

    # This is itself a public boundary: revalidate structurally BEFORE any
    # key binding, hashing, or semantic check, and keep the revalidated
    # instances as the authoritative collection.
    records = {key: revalidate(record) for key, record in records.items()}

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
            "variable_registration": variable_registrations,
            "variable_value_specification": specifications,
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

    # -- variable registrations: one per variable anchor; the OWNER entity
    # must belong to the same collection (reference closure — including
    # explicitly supplied replay subsets)
    variable_registrations_by_anchor: dict[str, VariableRegistration] = {}
    for record_id in sorted(variable_registrations):
        variable = variable_registrations[record_id]
        anchor_id = variable.anchor.anchor_id
        existing = variable_registrations_by_anchor.get(anchor_id)
        if existing is not None:
            # agreeing or divergent embedded fields alike: never tie-broken
            # by recorded_at, authority, or record id
            _fail("MODEL_DUPLICATE_REGISTRATION",
                  f"variable {anchor_id} is registered more than once "
                  f"({existing.record_id}, {record_id})")
        variable_registrations_by_anchor[anchor_id] = variable
    for variable in variable_registrations_by_anchor.values():
        owner_id = variable.anchor.entity_anchor_id
        if owner_id not in registrations_by_anchor:
            _fail("MODEL_REFERENCE_INVALID",
                  f"variable registration {variable.record_id} references "
                  f"unregistered owner entity {owner_id}")

    # -- value specifications: a multi-parent DAG per variable anchor.
    # Competing current tips are SURFACED, never fatal: the revision stays
    # loadable, queryable, and replayable, and a record superseding every
    # tip converges the lineage.
    for record_id in sorted(specifications):
        record = specifications[record_id]
        if record.variable_anchor_id not in variable_registrations_by_anchor:
            _fail("MODEL_REFERENCE_INVALID",
                  f"specification {record_id} references unregistered "
                  f"variable {record.variable_anchor_id}")
        if record_id in record.supersedes:
            _fail("MODEL_SPECIFICATION_LINEAGE_INVALID",
                  f"specification {record_id} supersedes itself")
        for parent_id in record.supersedes:
            parent = specifications.get(parent_id)
            if parent is None:
                _fail("MODEL_REFERENCE_INVALID",
                      f"specification {record_id} supersedes missing "
                      f"specification {parent_id}")
            if parent.variable_anchor_id != record.variable_anchor_id:
                _fail("MODEL_SPECIFICATION_LINEAGE_INVALID",
                      f"specification {record_id} supersedes {parent_id}, "
                      "which specifies a different variable")

    # acyclicity over the DAG (iterative three-colour walk — a chain walk
    # cannot express multiple parents)
    _visiting, _done = set(), set()
    for start in sorted(specifications):
        if start in _done:
            continue
        stack = [(start, iter(specifications[start].supersedes))]
        _visiting.add(start)
        while stack:
            node, parents = stack[-1]
            advanced = False
            for parent_id in parents:
                if parent_id in _visiting:
                    _fail("MODEL_SPECIFICATION_LINEAGE_INVALID",
                          "specification supersession cycle")
                if parent_id not in _done:
                    _visiting.add(parent_id)
                    stack.append(
                        (parent_id, iter(specifications[parent_id].supersedes)))
                    advanced = True
                    break
            if not advanced:
                stack.pop()
                _visiting.discard(node)
                _done.add(node)

    specification_superseded_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in specifications}
    for record_id in sorted(specifications):
        for parent_id in specifications[record_id].supersedes:
            specification_superseded_by[parent_id] = tuple(sorted(
                (*specification_superseded_by[parent_id], record_id)))
    tips_by_variable: dict[str, tuple[VariableValueSpecification, ...]] = {}
    for record_id in sorted(specifications):
        record = specifications[record_id]
        if specification_superseded_by[record_id]:
            continue  # superseded by another member of this collection
        tips_by_variable[record.variable_anchor_id] = (
            *tips_by_variable.get(record.variable_anchor_id, ()), record)
    # defence in depth: unreachable while the DAG is acyclic, since a finite
    # acyclic graph always contains an unreferenced node
    for anchor_id in {record.variable_anchor_id
                      for record in specifications.values()}:
        if not tips_by_variable.get(anchor_id):
            _fail("MODEL_SPECIFICATION_LINEAGE_INVALID",
                  f"variable {anchor_id} has specifications but no current "
                  "tip")

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
        variable_registrations_by_anchor=_frozen_mapping(
            variable_registrations_by_anchor),
        specifications=_frozen_mapping(specifications),
        current_specification_tips_by_variable=_frozen_mapping(
            tips_by_variable),
        specification_superseded_by=_frozen_mapping(
            specification_superseded_by),
        superseded_by=_frozen_mapping(superseded_by),
        withdrawn_by=_frozen_mapping(withdrawn_by))


class ModelStore:
    def __init__(self, set_dir: Path | str) -> None:
        if not isinstance(set_dir, (str, os.PathLike)):
            raise ModelConfigurationError(
                "MODEL_SET_ID_INVALID",
                "a model set directory must be a path or path-like value")
        set_dir = Path(set_dir)
        if not re.fullmatch(MODEL_ID_PATTERN, set_dir.name):
            raise ModelConfigurationError(
                "MODEL_SET_ID_INVALID",
                f"model directory name {set_dir.name!r} must match "
                f"{MODEL_ID_PATTERN}")
        self.model_id = set_dir.name
        self.records_dir = set_dir / "records"
        self.staging_dir = set_dir / ".staging"
        try:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise ModelIntegrityError(
                "MODEL_STORAGE_FAILURE",
                f"could not open the records directory of model "
                f"{self.model_id}") from error

    # -- append (VALIDATING; single-writer; atomic promote) ----------------

    def append(self, record: ModelRecord) -> str:
        # Structural revalidation FIRST: a caller-supplied instance may have
        # bypassed field validation and been rehashed, so its hash is not
        # trustworthy until the shape is proven from data.
        record = revalidate(record)
        # hashing itself can fail on content that validates but cannot be
        # canonically serialized (a lone surrogate, say) — typed, not raw
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
        from uuid import uuid4

        temp = None
        try:
            self.staging_dir.mkdir(parents=True, exist_ok=True)
            temp = self.staging_dir / f"{record.record_id}.{uuid4().hex}.tmp"
            temp.write_text(text, encoding="utf-8")
            final = self.records_dir / f"{record.record_id}.json"
            os.replace(temp, final)
        except OSError as error:
            # environment failures surface through the typed contract with
            # ids only — never an absolute path
            if temp is not None:
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    # cleanup is best-effort; staging residue must never
                    # mask the typed storage failure
                    pass
            raise ModelIntegrityError(
                "MODEL_STORAGE_FAILURE",
                f"could not persist {record.record_id} to model "
                f"{self.model_id}") from error
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
        try:
            entries = sorted(self.records_dir.iterdir())
        except OSError as error:
            raise ModelIntegrityError(
                "MODEL_STORAGE_FAILURE",
                f"could not read the records directory of model "
                f"{self.model_id}") from error
        for path in entries:
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
        try:
            supplied = list(record_ids)
        except Exception as error:
            # non-iterable input AND an iterator that raises mid-iteration
            # (a file-backed id source, say) both fail typed
            raise ModelIntegrityError(
                "MODEL_REVISION_INVALID",
                "the revision membership could not be materialized into "
                "record ids") from error
        for record_id in supplied:
            if not isinstance(record_id, str) or not _RECORD_ID.fullmatch(
                    record_id):
                raise ModelIntegrityError(
                    "MODEL_REVISION_INVALID",
                    f"{record_id!r} is not a valid model record id")
        if len(set(supplied)) != len(supplied):
            raise ModelIntegrityError(
                "MODEL_REVISION_INVALID",
                "revision membership contains duplicates")
        # Light store-availability probe: an empty (or any) membership is
        # valid only against an existing, readable records directory — a
        # destroyed store must not be misreported as a missing member.
        try:
            with os.scandir(self.records_dir):
                pass
        except OSError as error:
            raise ModelIntegrityError(
                "MODEL_STORAGE_FAILURE",
                f"could not read the records directory of model "
                f"{self.model_id}") from error
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
