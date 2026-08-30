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
import stat
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
    BehaviorRegistration,
    BehaviorRuleDeclaration,
    BehaviorRuleWithdrawal,
    ConstraintRegistration,
    EntityRegistration,
    MODEL_ID_PATTERN,
    MODEL_RECORD_ID_PATTERN,
    ModelConfigurationError,
    ModelIntegrityError,
    ModelRecord,
    ModelRevision,
    PortClaimWithdrawal,
    PortCompatibilityDeclaration,
    PortConnectionAssertion,
    PortInterfaceDeclaration,
    PortRegistration,
    RelationshipAssertion,
    RelationshipTypeDefinition,
    RelationshipWithdrawal,
    VariableConstraintDeclaration,
    VariablePortAssociation,
    VariablePortAssociationWithdrawal,
    VariableRegistration,
    VariableSemanticDeclaration,
    VariableValueSpecification,
)

_RECORD_ADAPTER: TypeAdapter = TypeAdapter(ModelRecord)
_RECORD_ID = re.compile(MODEL_RECORD_ID_PATTERN)
_FILENAME = re.compile(
    r"^(reg|rtd|rel|rwd|vrg|vsp|vsm|crg|vcn|prg|pif|pcn|pcm|ptw|vpa|vpw|brg|bhd|bhw|srg|std|stw)_[0-9a-f]{64}\.json$")

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
    semantic_declarations: Mapping[str, VariableSemanticDeclaration] = _EMPTY
    current_semantic_tips_by_variable_dimension: Mapping[
        tuple[str, str], tuple[VariableSemanticDeclaration, ...]] = _EMPTY
    semantic_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    constraint_registrations_by_anchor: Mapping[
        str, ConstraintRegistration] = _EMPTY
    constraint_anchor_ids_by_variable: Mapping[
        str, tuple[str, ...]] = _EMPTY
    constraint_declarations: Mapping[str, VariableConstraintDeclaration] = _EMPTY
    current_constraint_tips_by_anchor: Mapping[
        str, tuple[VariableConstraintDeclaration, ...]] = _EMPTY
    constraint_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    port_registrations_by_anchor: Mapping[str, PortRegistration] = _EMPTY
    port_anchor_ids_by_owner: Mapping[str, tuple[str, ...]] = _EMPTY
    port_interface_declarations: Mapping[
        str, PortInterfaceDeclaration] = _EMPTY
    port_interface_root_by_id: Mapping[str, str] = _EMPTY
    port_interface_ids_by_key: Mapping[tuple, tuple[str, ...]] = _EMPTY
    port_interface_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    current_port_interface_tips_by_key: Mapping[
        tuple, tuple[PortInterfaceDeclaration, ...]] = _EMPTY
    port_interface_withdrawn_by: Mapping[str, tuple[str, ...]] = _EMPTY
    port_connections: Mapping[str, PortConnectionAssertion] = _EMPTY
    port_connection_root_by_id: Mapping[str, str] = _EMPTY
    port_connection_ancestry_by_id: Mapping[str, tuple[str, ...]] = _EMPTY
    port_connection_ids_by_subject: Mapping[
        tuple, tuple[str, ...]] = _EMPTY
    port_connection_ids_by_port: Mapping[str, tuple[str, ...]] = _EMPTY
    port_connection_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    current_port_connection_tips_by_root: Mapping[
        str, tuple[PortConnectionAssertion, ...]] = _EMPTY
    port_connection_withdrawn_by: Mapping[str, tuple[str, ...]] = _EMPTY
    port_compatibility_declarations: Mapping[
        str, PortCompatibilityDeclaration] = _EMPTY
    port_compatibility_root_by_id: Mapping[str, str] = _EMPTY
    port_compatibility_ids_by_key: Mapping[tuple, tuple[str, ...]] = _EMPTY
    port_compatibility_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    current_port_compatibility_tips_by_key: Mapping[
        tuple, tuple[PortCompatibilityDeclaration, ...]] = _EMPTY
    port_compatibility_withdrawn_by: Mapping[str, tuple[str, ...]] = _EMPTY
    port_compatibility_citations: Mapping[str, tuple[str, ...]] = _EMPTY
    port_compatibility_ids_by_citation: Mapping[
        str, tuple[str, ...]] = _EMPTY
    port_claim_withdrawals: Mapping[str, PortClaimWithdrawal] = _EMPTY
    port_withdrawals_by_target: Mapping[str, tuple[str, ...]] = _EMPTY
    variable_port_associations: Mapping[
        str, VariablePortAssociation] = _EMPTY
    variable_port_association_withdrawals: Mapping[
        str, VariablePortAssociationWithdrawal] = _EMPTY
    variable_port_association_root_by_id: Mapping[str, str] = _EMPTY
    variable_port_association_ancestry_by_id: Mapping[
        str, tuple[str, ...]] = _EMPTY
    variable_port_association_ids_by_subject: Mapping[
        tuple, tuple[str, ...]] = _EMPTY
    variable_port_association_ids_by_variable_context: Mapping[
        tuple, tuple[str, ...]] = _EMPTY
    variable_port_association_ids_by_port_context: Mapping[
        tuple, tuple[str, ...]] = _EMPTY
    variable_port_association_superseded_by: Mapping[
        str, tuple[str, ...]] = _EMPTY
    current_variable_port_association_tips_by_root: Mapping[
        str, tuple[VariablePortAssociation, ...]] = _EMPTY
    variable_port_association_withdrawn_by: Mapping[
        str, tuple[str, ...]] = _EMPTY
    variable_port_association_withdrawals_by_target: Mapping[
        str, tuple[str, ...]] = _EMPTY
    behavior_registrations: Mapping[str, BehaviorRegistration] = _EMPTY
    behavior_registrations_by_anchor: Mapping[
        str, BehaviorRegistration] = _EMPTY
    behavior_anchor_ids_by_variable: Mapping[str, tuple[str, ...]] = _EMPTY
    behavior_rule_declarations: Mapping[
        str, BehaviorRuleDeclaration] = _EMPTY
    behavior_rule_ids_by_key: Mapping[tuple, tuple[str, ...]] = _EMPTY
    behavior_rule_root_by_id: Mapping[str, str] = _EMPTY
    behavior_rule_ancestry_by_id: Mapping[str, tuple[str, ...]] = _EMPTY
    behavior_rule_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    current_behavior_rule_tips_by_root: Mapping[
        str, tuple[BehaviorRuleDeclaration, ...]] = _EMPTY
    behavior_rule_withdrawals: Mapping[str, BehaviorRuleWithdrawal] = _EMPTY
    behavior_rule_withdrawn_by: Mapping[str, tuple[str, ...]] = _EMPTY
    behavior_rule_withdrawals_by_target: Mapping[
        str, tuple[str, ...]] = _EMPTY


def _fail(code: str, message: str) -> None:
    raise ModelIntegrityError(code, message)


def _check_model_record_evidence(records: Mapping, record,
                                 kind_label: str) -> None:
    """The UNIFORM evidence-reference closure rule (ES-001, owner-mandated
    repair): for every evidence-bearing model claim, each EvidenceRef of
    kind model_record must name a member of the supplied collection —
    load, prospective append, and explicit replay subsets alike. Foreign
    evidence arms remain declared references and are never dereferenced
    or validated against foreign ledgers."""
    for reference in record.evidence:
        if (reference.kind == "model_record"
                and reference.record_id not in records):
            _fail("MODEL_REFERENCE_INVALID",
                  f"{kind_label} {record.record_id} cites model-record "
                  f"evidence {reference.record_id} absent from the revision")


def _pt_dag_indexes(records: Mapping[str, object], key_of,
                    error_code: str, label: str):
    """Validate one PT correction DAG family without touching accepted DAGs.

    A parentless claim starts a root. Corrections may merge only branches
    derived from the same root. The caller separately decides whether several
    roots for one semantic key are forbidden (PIF/PCM) or corroborating (PCN).
    """
    for record_id in sorted(records):
        record = records[record_id]
        for parent_id in record.supersedes:
            parent = records.get(parent_id)
            if parent is None:
                _fail("MODEL_REFERENCE_INVALID",
                      f"{label} {record_id} supersedes missing {label} "
                      f"{parent_id}")
            if key_of(parent) != key_of(record):
                _fail(error_code,
                      f"{label} {record_id} has a parent from another "
                      "lineage")

    visiting: set[str] = set()
    done: set[str] = set()
    for start in sorted(records):
        if start in done:
            continue
        stack = [(start, iter(records[start].supersedes))]
        visiting.add(start)
        while stack:
            node, parents = stack[-1]
            for parent_id in parents:
                if parent_id in visiting:
                    _fail(error_code, f"{label} supersession cycle")
                if parent_id not in done:
                    visiting.add(parent_id)
                    stack.append((parent_id,
                                  iter(records[parent_id].supersedes)))
                    break
            else:
                stack.pop()
                visiting.discard(node)
                done.add(node)

    successors: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in records}
    for record_id in sorted(records):
        for parent_id in records[record_id].supersedes:
            successors[parent_id] = tuple(sorted((
                *successors[parent_id], record_id)))

    roots: dict[str, str] = {}
    pending = set(records)
    while pending:
        progressed = False
        for record_id in sorted(pending):
            parents = records[record_id].supersedes
            if not parents:
                roots[record_id] = record_id
            elif all(parent_id in roots for parent_id in parents):
                parent_roots = {roots[parent_id] for parent_id in parents}
                if len(parent_roots) != 1:
                    _fail(error_code,
                          f"{label} correction crosses independent roots")
                roots[record_id] = next(iter(parent_roots))
            else:
                continue
            pending.remove(record_id)
            progressed = True
        if not progressed:  # defence in depth after the cycle check
            _fail(error_code, f"{label} roots could not be derived")
    return successors, roots


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
    semantic_declarations: dict[str, VariableSemanticDeclaration] = {}
    constraint_registrations: dict[str, ConstraintRegistration] = {}
    constraint_declarations: dict[str, VariableConstraintDeclaration] = {}
    port_registrations: dict[str, PortRegistration] = {}
    port_interface_declarations: dict[str, PortInterfaceDeclaration] = {}
    port_connections: dict[str, PortConnectionAssertion] = {}
    port_compatibility_declarations: dict[
        str, PortCompatibilityDeclaration] = {}
    port_claim_withdrawals: dict[str, PortClaimWithdrawal] = {}
    variable_port_associations: dict[str, VariablePortAssociation] = {}
    variable_port_association_withdrawals: dict[
        str, VariablePortAssociationWithdrawal] = {}
    behavior_registrations: dict[str, BehaviorRegistration] = {}
    behavior_rule_declarations: dict[str, BehaviorRuleDeclaration] = {}
    behavior_rule_withdrawals: dict[str, BehaviorRuleWithdrawal] = {}
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
            "variable_semantic_declaration": semantic_declarations,
            "constraint_registration": constraint_registrations,
            "variable_constraint_declaration": constraint_declarations,
            "port_registration": port_registrations,
            "port_interface_declaration": port_interface_declarations,
            "port_connection_assertion": port_connections,
            "port_compatibility_declaration": port_compatibility_declarations,
            "port_claim_withdrawal": port_claim_withdrawals,
            "variable_port_association": variable_port_associations,
            "variable_port_association_withdrawal": (
                variable_port_association_withdrawals),
            "behavior_registration": behavior_registrations,
            "behavior_rule_declaration": behavior_rule_declarations,
            "behavior_rule_withdrawal": behavior_rule_withdrawals,
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
        _check_model_record_evidence(records, record, "specification")
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

    # -- semantic declarations: independent multi-parent DAG per variable
    # and semantic dimension. Competing tips remain queryable conflicts.
    for record_id in sorted(semantic_declarations):
        record = semantic_declarations[record_id]
        if record.variable_anchor_id not in variable_registrations_by_anchor:
            _fail("MODEL_REFERENCE_INVALID",
                  f"semantic declaration {record_id} references unregistered "
                  f"variable {record.variable_anchor_id}")
        _check_model_record_evidence(records, record, "semantic declaration")
        for parent_id in record.supersedes:
            parent = semantic_declarations.get(parent_id)
            if parent is None:
                _fail("MODEL_REFERENCE_INVALID",
                      f"semantic declaration {record_id} supersedes missing "
                      f"semantic declaration {parent_id}")
            if (parent.variable_anchor_id != record.variable_anchor_id
                    or parent.declaration.dimension != record.declaration.dimension):
                _fail("MODEL_SEMANTIC_LINEAGE_INVALID",
                      f"semantic declaration {record_id} has an incompatible parent")
    visiting, done = set(), set()
    for start in sorted(semantic_declarations):
        if start in done:
            continue
        stack = [(start, iter(semantic_declarations[start].supersedes))]
        visiting.add(start)
        while stack:
            node, parents = stack[-1]
            for parent_id in parents:
                if parent_id in visiting:
                    _fail("MODEL_SEMANTIC_LINEAGE_INVALID",
                          "semantic declaration supersession cycle")
                if parent_id not in done:
                    visiting.add(parent_id)
                    stack.append((parent_id, iter(
                        semantic_declarations[parent_id].supersedes)))
                    break
            else:
                stack.pop(); visiting.discard(node); done.add(node)
    semantic_superseded_by = {record_id: () for record_id in semantic_declarations}
    for record_id in sorted(semantic_declarations):
        for parent_id in semantic_declarations[record_id].supersedes:
            semantic_superseded_by[parent_id] = tuple(sorted((
                *semantic_superseded_by[parent_id], record_id)))
    semantic_tips: dict[tuple[str, str], tuple[VariableSemanticDeclaration, ...]] = {}
    for record_id in sorted(semantic_declarations):
        record = semantic_declarations[record_id]
        if not semantic_superseded_by[record_id]:
            key = (record.variable_anchor_id, record.declaration.dimension)
            semantic_tips[key] = (*semantic_tips.get(key, ()), record)
    for key in {(r.variable_anchor_id, r.declaration.dimension)
                for r in semantic_declarations.values()}:
        if not semantic_tips.get(key):
            _fail("MODEL_SEMANTIC_LINEAGE_INVALID",
                  f"semantic lineage {key[0]} {key[1]} has no current tip")

    # -- constraints: permanent evidence-backed registration plus a
    # multi-parent correction DAG keyed ONLY by constraint anchor id.
    constraint_registrations_by_anchor: dict[str, ConstraintRegistration] = {}
    constraint_anchor_ids_by_variable: dict[str, tuple[str, ...]] = {}
    for record_id in sorted(constraint_registrations):
        registration = constraint_registrations[record_id]
        anchor_id = registration.anchor.anchor_id
        existing = constraint_registrations_by_anchor.get(anchor_id)
        if existing is not None:
            _fail("MODEL_DUPLICATE_REGISTRATION",
                  f"constraint {anchor_id} is registered more than once "
                  f"({existing.record_id}, {record_id})")
        if registration.variable_anchor_id not in variable_registrations_by_anchor:
            _fail("MODEL_REFERENCE_INVALID",
                  f"constraint registration {record_id} references "
                  f"unregistered variable {registration.variable_anchor_id}")
        _check_model_record_evidence(
            records, registration, "constraint registration")
        constraint_registrations_by_anchor[anchor_id] = registration
        current = constraint_anchor_ids_by_variable.get(
            registration.variable_anchor_id, ())
        constraint_anchor_ids_by_variable[registration.variable_anchor_id] = (
            *current, anchor_id)
    constraint_anchor_ids_by_variable = {
        variable_id: tuple(sorted(anchor_ids))
        for variable_id, anchor_ids in constraint_anchor_ids_by_variable.items()
    }

    for record_id in sorted(constraint_declarations):
        record = constraint_declarations[record_id]
        if record.constraint_anchor_id not in constraint_registrations_by_anchor:
            _fail("MODEL_REFERENCE_INVALID",
                  f"constraint declaration {record_id} references "
                  f"unregistered constraint {record.constraint_anchor_id}")
        _check_model_record_evidence(
            records, record, "constraint declaration")
        for parent_id in record.supersedes:
            parent = constraint_declarations.get(parent_id)
            if parent is None:
                _fail("MODEL_REFERENCE_INVALID",
                      f"constraint declaration {record_id} supersedes "
                      f"missing declaration {parent_id}")
            if parent.constraint_anchor_id != record.constraint_anchor_id:
                _fail("MODEL_CONSTRAINT_LINEAGE_INVALID",
                      f"constraint declaration {record_id} has a parent "
                      "from another constraint anchor")

    visiting, done = set(), set()
    for start in sorted(constraint_declarations):
        if start in done:
            continue
        stack = [(start, iter(constraint_declarations[start].supersedes))]
        visiting.add(start)
        while stack:
            node, parents = stack[-1]
            for parent_id in parents:
                if parent_id in visiting:
                    _fail("MODEL_CONSTRAINT_LINEAGE_INVALID",
                          "constraint declaration supersession cycle")
                if parent_id not in done:
                    visiting.add(parent_id)
                    stack.append((parent_id, iter(
                        constraint_declarations[parent_id].supersedes)))
                    break
            else:
                stack.pop()
                visiting.discard(node)
                done.add(node)

    constraint_superseded_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in constraint_declarations}
    for record_id in sorted(constraint_declarations):
        for parent_id in constraint_declarations[record_id].supersedes:
            constraint_superseded_by[parent_id] = tuple(sorted((
                *constraint_superseded_by[parent_id], record_id)))
    constraint_tips: dict[
        str, tuple[VariableConstraintDeclaration, ...]] = {}
    for record_id in sorted(constraint_declarations):
        record = constraint_declarations[record_id]
        if not constraint_superseded_by[record_id]:
            constraint_tips[record.constraint_anchor_id] = (
                *constraint_tips.get(record.constraint_anchor_id, ()), record)
    for anchor_id in {record.constraint_anchor_id
                      for record in constraint_declarations.values()}:
        if not constraint_tips.get(anchor_id):
            _fail("MODEL_CONSTRAINT_LINEAGE_INVALID",
                  f"constraint {anchor_id} has declarations but no current tip")

    # -- ports: permanent registration plus three independent PT claim
    # families. This is deliberately separate from the accepted entity
    # relationship and variable/constraint lifecycle implementations.
    port_registrations_by_anchor: dict[str, PortRegistration] = {}
    port_anchor_ids_by_owner: dict[str, tuple[str, ...]] = {}
    for record_id in sorted(port_registrations):
        registration = port_registrations[record_id]
        anchor_id = registration.anchor.anchor_id
        existing = port_registrations_by_anchor.get(anchor_id)
        if existing is not None:
            _fail("MODEL_DUPLICATE_REGISTRATION",
                  f"port {anchor_id} is registered more than once "
                  f"({existing.record_id}, {record_id})")
        if registration.owner_entity_anchor_id not in registrations_by_anchor:
            _fail("MODEL_REFERENCE_INVALID",
                  f"port registration {record_id} references unregistered "
                  f"owner entity {registration.owner_entity_anchor_id}")
        _check_model_record_evidence(records, registration,
                                     "port registration")
        port_registrations_by_anchor[anchor_id] = registration
        owner_id = registration.owner_entity_anchor_id
        port_anchor_ids_by_owner[owner_id] = tuple(sorted((
            *port_anchor_ids_by_owner.get(owner_id, ()), anchor_id)))

    def interface_key(record):
        return (record.port_anchor_id, record.context,
                record.declaration.dimension)

    for record_id in sorted(port_interface_declarations):
        record = port_interface_declarations[record_id]
        if record.port_anchor_id not in port_registrations_by_anchor:
            _fail("MODEL_REFERENCE_INVALID",
                  f"port interface declaration {record_id} references "
                  f"unregistered port {record.port_anchor_id}")
        _check_model_record_evidence(records, record,
                                     "port interface declaration")
    port_interface_superseded_by, port_interface_root_by_id = _pt_dag_indexes(
        port_interface_declarations, interface_key,
        "MODEL_PORT_INTERFACE_LINEAGE_INVALID", "port interface declaration")
    interface_roots_by_key: dict[tuple, set[str]] = {}
    port_interface_ids_by_key: dict[tuple, tuple[str, ...]] = {}
    for record_id in sorted(port_interface_declarations):
        key = interface_key(port_interface_declarations[record_id])
        interface_roots_by_key.setdefault(key, set()).add(
            port_interface_root_by_id[record_id])
        port_interface_ids_by_key[key] = (
            *port_interface_ids_by_key.get(key, ()), record_id)
    if any(len(roots) != 1 for roots in interface_roots_by_key.values()):
        _fail("MODEL_PORT_INTERFACE_LINEAGE_INVALID",
              "a port interface lineage has more than one root")

    def connection_subject(record):
        return (record.endpoint_port_anchor_ids, record.context)

    port_connection_ids_by_subject: dict[tuple, tuple[str, ...]] = {}
    port_connection_ids_by_port: dict[str, tuple[str, ...]] = {}
    for record_id in sorted(port_connections):
        record = port_connections[record_id]
        for port_id in record.endpoint_port_anchor_ids:
            if port_id not in port_registrations_by_anchor:
                _fail("MODEL_REFERENCE_INVALID",
                      f"port connection {record_id} references unregistered "
                      f"port {port_id}")
            port_connection_ids_by_port[port_id] = (
                *port_connection_ids_by_port.get(port_id, ()), record_id)
        _check_model_record_evidence(records, record, "port connection")
        subject = connection_subject(record)
        port_connection_ids_by_subject[subject] = (
            *port_connection_ids_by_subject.get(subject, ()), record_id)
    port_connection_superseded_by, port_connection_root_by_id = _pt_dag_indexes(
        port_connections, connection_subject,
        "MODEL_PORT_CONNECTION_LINEAGE_INVALID", "port connection")
    port_connection_ancestry_by_id: dict[str, tuple[str, ...]] = {}
    pending_ancestry = set(port_connections)
    while pending_ancestry:
        for record_id in sorted(tuple(pending_ancestry)):
            parents = port_connections[record_id].supersedes
            if any(parent not in port_connection_ancestry_by_id
                   for parent in parents):
                continue
            ancestors = {
                ancestor
                for parent in parents
                for ancestor in (parent, *port_connection_ancestry_by_id[parent])
            }
            port_connection_ancestry_by_id[record_id] = tuple(sorted(ancestors))
            pending_ancestry.remove(record_id)

    def compatibility_key(record):
        return (record.endpoint_port_anchor_ids, record.context)

    port_compatibility_ids_by_key: dict[tuple, tuple[str, ...]] = {}
    compatibility_roots_by_key: dict[tuple, set[str]] = {}
    port_compatibility_citations: dict[str, tuple[str, ...]] = {}
    port_compatibility_ids_by_citation: dict[str, tuple[str, ...]] = {}
    for record_id in sorted(port_compatibility_declarations):
        record = port_compatibility_declarations[record_id]
        for port_id in record.endpoint_port_anchor_ids:
            if port_id not in port_registrations_by_anchor:
                _fail("MODEL_REFERENCE_INVALID",
                      f"port compatibility {record_id} references "
                      f"unregistered port {port_id}")
        _check_model_record_evidence(records, record, "port compatibility")
        citation_ids: list[str] = []
        for item in record.basis.dimensions:
            cited_ports: list[str] = []
            for citation in item.citations:
                declaration = port_interface_declarations.get(
                    citation.declaration_record_id)
                if declaration is None:
                    _fail("MODEL_REFERENCE_INVALID",
                          f"port compatibility {record_id} cites missing "
                          f"interface declaration "
                          f"{citation.declaration_record_id}")
                if (declaration.port_anchor_id != citation.port_anchor_id
                        or declaration.port_anchor_id
                        not in record.endpoint_port_anchor_ids
                        or declaration.declaration.dimension != item.dimension
                        or declaration.context != record.context):
                    _fail("MODEL_PORT_COMPATIBILITY_CITATION_INVALID",
                          f"port compatibility {record_id} has an "
                          "incoherent interface citation")
                cited_ports.append(citation.port_anchor_id)
                citation_ids.append(citation.declaration_record_id)
                current = port_compatibility_ids_by_citation.get(
                    citation.declaration_record_id, ())
                port_compatibility_ids_by_citation[
                    citation.declaration_record_id] = tuple(sorted((
                        *current, record_id)))
            if tuple(cited_ports) != record.endpoint_port_anchor_ids:
                _fail("MODEL_PORT_COMPATIBILITY_CITATION_INVALID",
                      f"port compatibility {record_id} citations do not "
                      "cover its exact endpoint pair")
        port_compatibility_citations[record_id] = tuple(citation_ids)
        key = compatibility_key(record)
        port_compatibility_ids_by_key[key] = (
            *port_compatibility_ids_by_key.get(key, ()), record_id)
    (port_compatibility_superseded_by,
     port_compatibility_root_by_id) = _pt_dag_indexes(
        port_compatibility_declarations, compatibility_key,
        "MODEL_PORT_COMPATIBILITY_LINEAGE_INVALID", "port compatibility")
    for record_id in sorted(port_compatibility_declarations):
        key = compatibility_key(port_compatibility_declarations[record_id])
        compatibility_roots_by_key.setdefault(key, set()).add(
            port_compatibility_root_by_id[record_id])
    if any(len(roots) != 1 for roots in compatibility_roots_by_key.values()):
        _fail("MODEL_PORT_COMPATIBILITY_LINEAGE_INVALID",
              "a port compatibility lineage has more than one root")

    # Withdrawals are evaluated after every successor index exists. A target
    # cannot be withdrawn twice or both superseded and withdrawn in one
    # selected membership; this also prevents later resurrection.
    port_claims = {
        **port_interface_declarations,
        **port_connections,
        **port_compatibility_declarations,
    }
    successors_by_target = {
        **port_interface_superseded_by,
        **port_connection_superseded_by,
        **port_compatibility_superseded_by,
    }
    port_withdrawals_by_target: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in port_claims}
    for withdrawal_id in sorted(port_claim_withdrawals):
        withdrawal = port_claim_withdrawals[withdrawal_id]
        target = withdrawal.withdraws
        if target not in port_claims:
            _fail("MODEL_PORT_WITHDRAWAL_INVALID",
                  f"port withdrawal {withdrawal_id} targets an unknown or "
                  "non-withdrawable claim")
        if successors_by_target[target]:
            _fail("MODEL_PORT_WITHDRAWAL_INVALID",
                  f"port withdrawal {withdrawal_id} targets a superseded "
                  "claim")
        if port_withdrawals_by_target[target]:
            _fail("MODEL_PORT_WITHDRAWAL_INVALID",
                  f"port claim {target} is withdrawn more than once")
        port_withdrawals_by_target[target] = (withdrawal_id,)

    port_interface_withdrawn_by = {
        record_id: port_withdrawals_by_target[record_id]
        for record_id in port_interface_declarations}
    port_connection_withdrawn_by = {
        record_id: port_withdrawals_by_target[record_id]
        for record_id in port_connections}
    port_compatibility_withdrawn_by = {
        record_id: port_withdrawals_by_target[record_id]
        for record_id in port_compatibility_declarations}

    current_port_interface_tips_by_key: dict[
        tuple, tuple[PortInterfaceDeclaration, ...]] = {
            key: () for key in port_interface_ids_by_key}
    for record_id in sorted(port_interface_declarations):
        if (not port_interface_superseded_by[record_id]
                and not port_interface_withdrawn_by[record_id]):
            record = port_interface_declarations[record_id]
            key = interface_key(record)
            current_port_interface_tips_by_key[key] = (
                *current_port_interface_tips_by_key[key], record)

    current_port_connection_tips_by_root: dict[
        str, tuple[PortConnectionAssertion, ...]] = {
            root: () for root in sorted(set(port_connection_root_by_id.values()))}
    for record_id in sorted(port_connections):
        if (not port_connection_superseded_by[record_id]
                and not port_connection_withdrawn_by[record_id]):
            root = port_connection_root_by_id[record_id]
            current_port_connection_tips_by_root[root] = (
                *current_port_connection_tips_by_root[root],
                port_connections[record_id])

    current_port_compatibility_tips_by_key: dict[
        tuple, tuple[PortCompatibilityDeclaration, ...]] = {
            key: () for key in port_compatibility_ids_by_key}
    for record_id in sorted(port_compatibility_declarations):
        if (not port_compatibility_superseded_by[record_id]
                and not port_compatibility_withdrawn_by[record_id]):
            record = port_compatibility_declarations[record_id]
            key = compatibility_key(record)
            current_port_compatibility_tips_by_key[key] = (
                *current_port_compatibility_tips_by_key[key], record)

    # -- explicit variable-to-port associations --------------------------
    # This positive claim family reuses the PT multi-root DAG mechanics
    # because its correction semantics match exactly. It remains separate
    # from entity relationships, variable identity, PT claims, and state.
    def variable_port_subject(record):
        return (record.variable_anchor_id, record.port_anchor_id,
                record.context)

    variable_port_association_ids_by_subject: dict[
        tuple, tuple[str, ...]] = {}
    variable_port_association_ids_by_variable_context: dict[
        tuple, tuple[str, ...]] = {}
    variable_port_association_ids_by_port_context: dict[
        tuple, tuple[str, ...]] = {}

    for record_id in sorted(variable_port_associations):
        record = variable_port_associations[record_id]
        variable_registration = variable_registrations_by_anchor.get(
            record.variable_anchor_id)
        if variable_registration is None:
            _fail("MODEL_REFERENCE_INVALID",
                  f"variable-port association {record_id} references "
                  f"unregistered variable {record.variable_anchor_id}")
        port_registration = port_registrations_by_anchor.get(
            record.port_anchor_id)
        if port_registration is None:
            _fail("MODEL_REFERENCE_INVALID",
                  f"variable-port association {record_id} references "
                  f"unregistered port {record.port_anchor_id}")
        variable_owner_id = variable_registration.anchor.entity_anchor_id
        port_owner_id = port_registration.owner_entity_anchor_id
        # Both owner registrations are already closure-validated by their
        # accepted registration families. Equality is an admission invariant,
        # never a source of an inferred association.
        if variable_owner_id != port_owner_id:
            _fail("MODEL_REFERENCE_INVALID",
                  f"variable-port association {record_id} has endpoints "
                  "owned by different entities")
        _check_model_record_evidence(
            records, record, "variable-port association")

        subject = variable_port_subject(record)
        variable_port_association_ids_by_subject[subject] = (
            *variable_port_association_ids_by_subject.get(subject, ()),
            record_id)
        variable_key = (record.variable_anchor_id, record.context)
        variable_port_association_ids_by_variable_context[variable_key] = (
            *variable_port_association_ids_by_variable_context.get(
                variable_key, ()), record_id)
        port_key = (record.port_anchor_id, record.context)
        variable_port_association_ids_by_port_context[port_key] = (
            *variable_port_association_ids_by_port_context.get(port_key, ()),
            record_id)

    (variable_port_association_superseded_by,
     variable_port_association_root_by_id) = _pt_dag_indexes(
        variable_port_associations, variable_port_subject,
        "MODEL_VARIABLE_PORT_LINEAGE_INVALID", "variable-port association")

    variable_port_association_ancestry_by_id: dict[
        str, tuple[str, ...]] = {}
    pending_variable_port_ancestry = set(variable_port_associations)
    while pending_variable_port_ancestry:
        progressed = False
        for record_id in sorted(tuple(pending_variable_port_ancestry)):
            parents = variable_port_associations[record_id].supersedes
            if any(parent not in variable_port_association_ancestry_by_id
                   for parent in parents):
                continue
            ancestors = {
                ancestor
                for parent in parents
                for ancestor in (
                    parent,
                    *variable_port_association_ancestry_by_id[parent])
            }
            variable_port_association_ancestry_by_id[record_id] = tuple(
                sorted(ancestors))
            pending_variable_port_ancestry.remove(record_id)
            progressed = True
        if not progressed:  # defence in depth after DAG validation
            _fail("MODEL_VARIABLE_PORT_LINEAGE_INVALID",
                  "variable-port association ancestry could not be derived")

    # Withdrawals are validated only after the complete successor graph is
    # known. Any unsuperseded current fork tip may be withdrawn; siblings do
    # not block the event and may leave the root healthy afterward.
    variable_port_association_withdrawals_by_target: dict[
        str, tuple[str, ...]] = {}
    for withdrawal_id in sorted(variable_port_association_withdrawals):
        withdrawal = variable_port_association_withdrawals[withdrawal_id]
        target = withdrawal.withdraws
        if target not in variable_port_associations:
            _fail("MODEL_REFERENCE_INVALID",
                  f"variable-port withdrawal {withdrawal_id} targets "
                  "a missing association")
        if variable_port_association_superseded_by[target]:
            _fail("MODEL_VARIABLE_PORT_WITHDRAWAL_INVALID",
                  f"variable-port withdrawal {withdrawal_id} targets "
                  "a superseded association")
        if target in variable_port_association_withdrawals_by_target:
            _fail("MODEL_VARIABLE_PORT_WITHDRAWAL_INVALID",
                  f"variable-port association {target} is withdrawn "
                  "more than once")
        variable_port_association_withdrawals_by_target[target] = (
            withdrawal_id,)

    variable_port_association_withdrawn_by = {
        record_id: variable_port_association_withdrawals_by_target.get(
            record_id, ())
        for record_id in variable_port_associations}
    current_variable_port_association_tips_by_root: dict[
        str, tuple[VariablePortAssociation, ...]] = {
            root: () for root in sorted(
                set(variable_port_association_root_by_id.values()))}
    for record_id in sorted(variable_port_associations):
        if (not variable_port_association_superseded_by[record_id]
                and not variable_port_association_withdrawn_by[record_id]):
            root = variable_port_association_root_by_id[record_id]
            current_variable_port_association_tips_by_root[root] = (
                *current_variable_port_association_tips_by_root[root],
                variable_port_associations[record_id])

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
        _check_model_record_evidence(records, claim, "assertion")
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

    # -- behaviors: permanent evidence-bearing registration plus an exact-
    # context, multi-root correction DAG. Registration says only that two
    # unordered variables participate in the declared rule family. It adds
    # no roles, direction, port/VPA relation, or operational truth.
    behavior_registrations_by_anchor: dict[str, BehaviorRegistration] = {}
    behavior_anchor_ids_by_variable: dict[str, tuple[str, ...]] = {}
    for record_id in sorted(behavior_registrations):
        registration = behavior_registrations[record_id]
        anchor_id = registration.anchor.anchor_id
        existing = behavior_registrations_by_anchor.get(anchor_id)
        if existing is not None:
            _fail("MODEL_DUPLICATE_REGISTRATION",
                  f"behavior {anchor_id} is registered more than once "
                  f"({existing.record_id}, {record_id})")
        variables = registration.participant_variable_anchor_ids
        missing = tuple(variable_id for variable_id in variables
                        if variable_id not in variable_registrations_by_anchor)
        if missing:
            _fail("MODEL_REFERENCE_INVALID",
                  f"behavior registration {record_id} references an "
                  "unregistered variable")
        _check_model_record_evidence(records, registration,
                                     "behavior registration")
        required_citations = {
            variable_registrations_by_anchor[variable_id].record_id
            for variable_id in variables
        }
        supplied_citations = {
            reference.record_id for reference in registration.evidence
            if reference.kind == "model_record"
        }
        has_claim_basis = any(reference.kind == "owner_declaration"
                              for reference in registration.evidence)
        if (not required_citations <= supplied_citations
                or not has_claim_basis):
            _fail("MODEL_BEHAVIOR_REGISTRATION_INVALID",
                  f"behavior registration {record_id} lacks its exact "
                  "variable-registration citations or claim basis")
        behavior_registrations_by_anchor[anchor_id] = registration
        for variable_id in variables:
            behavior_anchor_ids_by_variable[variable_id] = tuple(sorted((
                *behavior_anchor_ids_by_variable.get(variable_id, ()),
                anchor_id)))

    def behavior_rule_key(record):
        return (record.behavior_anchor_id, record.context)

    behavior_rule_ids_by_key: dict[tuple, tuple[str, ...]] = {}
    for record_id in sorted(behavior_rule_declarations):
        declaration = behavior_rule_declarations[record_id]
        registration = behavior_registrations_by_anchor.get(
            declaration.behavior_anchor_id)
        if registration is None:
            _fail("MODEL_REFERENCE_INVALID",
                  f"behavior declaration {record_id} references an "
                  "unregistered behavior")
        if tuple(lock.variable_anchor_id
                 for lock in declaration.participant_semantics) != (
                     registration.participant_variable_anchor_ids):
            _fail("MODEL_BEHAVIOR_DECLARATION_INVALID",
                  f"behavior declaration {record_id} locks variables other "
                  "than its permanent registered pair")
        _check_model_record_evidence(records, declaration,
                                     "behavior declaration")
        supplied_citations = {
            reference.record_id for reference in declaration.evidence
            if reference.kind == "model_record"
        }
        has_claim_basis = any(reference.kind == "owner_declaration"
                              for reference in declaration.evidence)
        if (registration.record_id not in supplied_citations
                or not has_claim_basis):
            _fail("MODEL_BEHAVIOR_DECLARATION_INVALID",
                  f"behavior declaration {record_id} lacks its exact "
                  "registration citation or claim basis")
        key = behavior_rule_key(declaration)
        behavior_rule_ids_by_key[key] = tuple(sorted((
            *behavior_rule_ids_by_key.get(key, ()), record_id)))

    behavior_rule_superseded_by, behavior_rule_root_by_id = _pt_dag_indexes(
        behavior_rule_declarations, behavior_rule_key,
        "MODEL_BEHAVIOR_LINEAGE_INVALID", "behavior declaration")

    behavior_rule_ancestry_by_id: dict[str, tuple[str, ...]] = {}
    pending_behavior_ancestry = set(behavior_rule_declarations)
    while pending_behavior_ancestry:
        progressed = False
        for record_id in sorted(tuple(pending_behavior_ancestry)):
            parents = behavior_rule_declarations[record_id].supersedes
            if any(parent not in behavior_rule_ancestry_by_id
                   for parent in parents):
                continue
            ancestors = {
                ancestor
                for parent in parents
                for ancestor in (
                    parent, *behavior_rule_ancestry_by_id[parent])
            }
            behavior_rule_ancestry_by_id[record_id] = tuple(sorted(ancestors))
            pending_behavior_ancestry.remove(record_id)
            progressed = True
        if not progressed:  # defence in depth after DAG validation
            _fail("MODEL_BEHAVIOR_LINEAGE_INVALID",
                  "behavior declaration ancestry could not be derived")

    # Withdrawal admission is evaluated only after the whole successor graph
    # is known. Any current fork tip may be withdrawn independently.
    behavior_rule_withdrawals_by_target: dict[str, tuple[str, ...]] = {}
    for withdrawal_id in sorted(behavior_rule_withdrawals):
        withdrawal = behavior_rule_withdrawals[withdrawal_id]
        target = withdrawal.withdraws
        if target not in behavior_rule_declarations:
            _fail("MODEL_REFERENCE_INVALID",
                  f"behavior withdrawal {withdrawal_id} targets a missing "
                  "declaration")
        if behavior_rule_superseded_by[target]:
            _fail("MODEL_BEHAVIOR_WITHDRAWAL_INVALID",
                  f"behavior withdrawal {withdrawal_id} targets a "
                  "superseded declaration")
        if target in behavior_rule_withdrawals_by_target:
            _fail("MODEL_BEHAVIOR_WITHDRAWAL_INVALID",
                  f"behavior declaration {target} is withdrawn more than "
                  "once")
        behavior_rule_withdrawals_by_target[target] = (withdrawal_id,)

    behavior_rule_withdrawn_by = {
        record_id: behavior_rule_withdrawals_by_target.get(record_id, ())
        for record_id in behavior_rule_declarations
    }
    current_behavior_rule_tips_by_root: dict[
        str, tuple[BehaviorRuleDeclaration, ...]] = {
            root: () for root in sorted(set(behavior_rule_root_by_id.values()))
        }
    for record_id in sorted(behavior_rule_declarations):
        if (not behavior_rule_superseded_by[record_id]
                and not behavior_rule_withdrawn_by[record_id]):
            root = behavior_rule_root_by_id[record_id]
            current_behavior_rule_tips_by_root[root] = (
                *current_behavior_rule_tips_by_root[root],
                behavior_rule_declarations[record_id])

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
        semantic_declarations=_frozen_mapping(semantic_declarations),
        current_semantic_tips_by_variable_dimension=_frozen_mapping(semantic_tips),
        semantic_superseded_by=_frozen_mapping(semantic_superseded_by),
        constraint_registrations_by_anchor=_frozen_mapping(
            constraint_registrations_by_anchor),
        constraint_anchor_ids_by_variable=_frozen_mapping(
            constraint_anchor_ids_by_variable),
        constraint_declarations=_frozen_mapping(constraint_declarations),
        current_constraint_tips_by_anchor=_frozen_mapping(constraint_tips),
        constraint_superseded_by=_frozen_mapping(constraint_superseded_by),
        port_registrations_by_anchor=_frozen_mapping(
            port_registrations_by_anchor),
        port_anchor_ids_by_owner=_frozen_mapping(port_anchor_ids_by_owner),
        port_interface_declarations=_frozen_mapping(
            port_interface_declarations),
        port_interface_root_by_id=_frozen_mapping(port_interface_root_by_id),
        port_interface_ids_by_key=_frozen_mapping(port_interface_ids_by_key),
        port_interface_superseded_by=_frozen_mapping(
            port_interface_superseded_by),
        current_port_interface_tips_by_key=_frozen_mapping(
            current_port_interface_tips_by_key),
        port_interface_withdrawn_by=_frozen_mapping(
            port_interface_withdrawn_by),
        port_connections=_frozen_mapping(port_connections),
        port_connection_root_by_id=_frozen_mapping(
            port_connection_root_by_id),
        port_connection_ancestry_by_id=_frozen_mapping(
            port_connection_ancestry_by_id),
        port_connection_ids_by_subject=_frozen_mapping(
            port_connection_ids_by_subject),
        port_connection_ids_by_port=_frozen_mapping(
            port_connection_ids_by_port),
        port_connection_superseded_by=_frozen_mapping(
            port_connection_superseded_by),
        current_port_connection_tips_by_root=_frozen_mapping(
            current_port_connection_tips_by_root),
        port_connection_withdrawn_by=_frozen_mapping(
            port_connection_withdrawn_by),
        port_compatibility_declarations=_frozen_mapping(
            port_compatibility_declarations),
        port_compatibility_root_by_id=_frozen_mapping(
            port_compatibility_root_by_id),
        port_compatibility_ids_by_key=_frozen_mapping(
            port_compatibility_ids_by_key),
        port_compatibility_superseded_by=_frozen_mapping(
            port_compatibility_superseded_by),
        current_port_compatibility_tips_by_key=_frozen_mapping(
            current_port_compatibility_tips_by_key),
        port_compatibility_withdrawn_by=_frozen_mapping(
            port_compatibility_withdrawn_by),
        port_compatibility_citations=_frozen_mapping(
            port_compatibility_citations),
        port_compatibility_ids_by_citation=_frozen_mapping(
            port_compatibility_ids_by_citation),
        port_claim_withdrawals=_frozen_mapping(port_claim_withdrawals),
        port_withdrawals_by_target=_frozen_mapping(
            port_withdrawals_by_target),
        variable_port_associations=_frozen_mapping(
            variable_port_associations),
        variable_port_association_withdrawals=_frozen_mapping(
            variable_port_association_withdrawals),
        variable_port_association_root_by_id=_frozen_mapping(
            variable_port_association_root_by_id),
        variable_port_association_ancestry_by_id=_frozen_mapping(
            variable_port_association_ancestry_by_id),
        variable_port_association_ids_by_subject=_frozen_mapping(
            variable_port_association_ids_by_subject),
        variable_port_association_ids_by_variable_context=_frozen_mapping(
            variable_port_association_ids_by_variable_context),
        variable_port_association_ids_by_port_context=_frozen_mapping(
            variable_port_association_ids_by_port_context),
        variable_port_association_superseded_by=_frozen_mapping(
            variable_port_association_superseded_by),
        current_variable_port_association_tips_by_root=_frozen_mapping(
            current_variable_port_association_tips_by_root),
        variable_port_association_withdrawn_by=_frozen_mapping(
            variable_port_association_withdrawn_by),
        variable_port_association_withdrawals_by_target=_frozen_mapping(
            variable_port_association_withdrawals_by_target),
        behavior_registrations=_frozen_mapping({
            record_id: behavior_registrations[record_id]
            for record_id in sorted(behavior_registrations)}),
        behavior_registrations_by_anchor=_frozen_mapping(
            behavior_registrations_by_anchor),
        behavior_anchor_ids_by_variable=_frozen_mapping(
            behavior_anchor_ids_by_variable),
        behavior_rule_declarations=_frozen_mapping({
            record_id: behavior_rule_declarations[record_id]
            for record_id in sorted(behavior_rule_declarations)}),
        behavior_rule_ids_by_key=_frozen_mapping(behavior_rule_ids_by_key),
        behavior_rule_root_by_id=_frozen_mapping(behavior_rule_root_by_id),
        behavior_rule_ancestry_by_id=_frozen_mapping(
            behavior_rule_ancestry_by_id),
        behavior_rule_superseded_by=_frozen_mapping({
            record_id: behavior_rule_superseded_by[record_id]
            for record_id in sorted(behavior_rule_superseded_by)}),
        current_behavior_rule_tips_by_root=_frozen_mapping(
            current_behavior_rule_tips_by_root),
        behavior_rule_withdrawals=_frozen_mapping({
            record_id: behavior_rule_withdrawals[record_id]
            for record_id in sorted(behavior_rule_withdrawals)}),
        behavior_rule_withdrawn_by=_frozen_mapping({
            record_id: behavior_rule_withdrawn_by[record_id]
            for record_id in sorted(behavior_rule_withdrawn_by)}),
        behavior_rule_withdrawals_by_target=_frozen_mapping(
            behavior_rule_withdrawals_by_target),
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
        # Ledger members are ordinary files owned by this store boundary.
        # A validly named symlink must never import bytes from elsewhere.
        # The store is explicitly single-writer; this pre-read check does not
        # claim protection against a concurrent hostile filesystem race.
        try:
            mode = path.stat(follow_symlinks=False).st_mode
        except OSError as error:
            raise ModelIntegrityError(
                "MODEL_RECORD_INVALID",
                f"{path.name} is not a readable model record file") from error
        if not stat.S_ISREG(mode):
            raise ModelIntegrityError(
                "MODEL_RECORD_INVALID",
                f"{path.name} is not an ordinary model record file")
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
