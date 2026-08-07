"""Write-once binding-set store.

One binding set per directory (``<set_dir>/records/<record_id>.json``),
atomic temp+rename appends, honest single-writer assumption (no lock
pretended). Validation is all-or-nothing: any integrity violation
invalidates the complete set and nothing resolves. Files are
pretty-printed for review; identity is the canonical hash of the
validated model, never raw file bytes. Revisions are exact sorted
memberships and can be replayed from the still-present append-only
records after later appends.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping

from pydantic import TypeAdapter, ValidationError

from backend.identity_binding.canonical import (
    canonical_payload,
    compute_revision_id,
    verify_record_id,
)
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    ApplicabilityClosure,
    AppliesScope,
    BINDING_SET_ID_PATTERN,
    BindingAssertion,
    BindingConfigurationError,
    BindingIntegrityError,
    BindingRejection,
    BindingRetraction,
    BindingRevision,
    DeclaredBoundary,
    LedgerRecord,
)
from backend.system_identity import EntityAnchor, VariableAnchor

_RECORD_ADAPTER: TypeAdapter = TypeAdapter(LedgerRecord)
_FILENAME = re.compile(r"^(anc|iba|ibr|ibc|ibj)_[0-9a-f]{64}\.json$")


@dataclass(frozen=True)
class LoadedBindingSet:
    """A validated revision plus derived in-memory indexes."""

    revision: BindingRevision
    records: dict[str, LedgerRecord]
    anchors_by_id: dict[str, EntityAnchor | VariableAnchor]
    declarations: dict[str, AnchorDeclaration]
    assertions: dict[str, BindingAssertion]
    retractions: dict[str, BindingRetraction]
    closures: dict[str, ApplicabilityClosure]
    rejections: dict[str, BindingRejection]
    superseded_by: dict[str, tuple[str, ...]] = field(default_factory=dict)
    retracted_by: dict[str, tuple[str, ...]] = field(default_factory=dict)
    closure_records: dict[str, tuple[str, ...]] = field(default_factory=dict)
    effective_applies: dict[str, AppliesScope] = field(default_factory=dict)


def _fail(code: str, message: str) -> None:
    raise BindingIntegrityError(code, message)


def _same_locator(a: BindingAssertion, b: BindingAssertion) -> bool:
    return a.subject == b.subject and a.property == b.property


def validate_record_collection(
    binding_set_id: str,
    records: Mapping[str, LedgerRecord],
    *,
    verify_hashes: bool = True,
) -> LoadedBindingSet:
    """All-or-nothing validation of a record collection (the whole set or
    an explicitly supplied reference-closed subset)."""
    declarations: dict[str, AnchorDeclaration] = {}
    assertions: dict[str, BindingAssertion] = {}
    retractions: dict[str, BindingRetraction] = {}
    closures: dict[str, ApplicabilityClosure] = {}
    rejections: dict[str, BindingRejection] = {}

    for record_id, record in records.items():
        if verify_hashes and not verify_record_id(record):
            _fail("BINDING_RECORD_HASH_MISMATCH",
                  f"content of {record_id} does not match its id")
        bucket = {
            "anchor_declaration": declarations,
            "binding_assertion": assertions,
            "binding_retraction": retractions,
            "applicability_closure": closures,
            "binding_rejection": rejections,
        }[record.record_kind]
        bucket[record_id] = record

    # -- anchors: exactly one declaration owns each canonical ID ---------
    anchors_by_id: dict[str, EntityAnchor | VariableAnchor] = {}
    seen_identifiers: dict[str, str] = {}  # 32-hex tail -> anchor_id
    for declaration in declarations.values():
        anchor = declaration.anchor
        tail = anchor.anchor_id.split("_", 1)[1]
        if anchor.anchor_id in anchors_by_id or tail in seen_identifiers:
            _fail("BINDING_DUPLICATE_ANCHOR_ID",
                  f"{anchor.anchor_id} is declared more than once or shares "
                  "its identifier across anchor kinds")
        anchors_by_id[anchor.anchor_id] = anchor
        seen_identifiers[tail] = anchor.anchor_id
    for anchor in anchors_by_id.values():
        if isinstance(anchor, VariableAnchor):
            if anchor.entity_anchor_id not in anchors_by_id:
                _fail("BINDING_ANCHOR_REFERENCE_INVALID",
                      f"variable {anchor.anchor_id} references undeclared "
                      f"entity {anchor.entity_anchor_id}")

    # -- assertions: targets and supersession ----------------------------
    for assertion in assertions.values():
        if assertion.target_anchor_id not in anchors_by_id:
            _fail("BINDING_ANCHOR_REFERENCE_INVALID",
                  f"assertion {assertion.record_id} targets undeclared "
                  f"anchor {assertion.target_anchor_id}")
        if assertion.supersedes is not None:
            predecessor = assertions.get(assertion.supersedes)
            if predecessor is None:
                _fail("BINDING_SUPERSEDES_INVALID",
                      f"{assertion.record_id} supersedes a missing assertion")
            if (predecessor.binding_kind != assertion.binding_kind
                    or not _same_locator(predecessor, assertion)):
                _fail("BINDING_SUPERSEDES_INVALID",
                      "supersession requires the same binding kind and the "
                      "exact same locator")
    for assertion in assertions.values():  # acyclicity (defense in depth)
        seen: set[str] = set()
        cursor = assertion
        while cursor.supersedes is not None:
            if cursor.record_id in seen:
                _fail("BINDING_SUPERSEDES_INVALID", "supersession cycle")
            seen.add(cursor.record_id)
            cursor = assertions[cursor.supersedes]

    for retraction in retractions.values():
        if retraction.retracts not in assertions:
            _fail("BINDING_RETRACTS_INVALID",
                  f"{retraction.record_id} retracts a missing assertion")

    for rejection in rejections.values():
        if rejection.rejected_anchor_id not in anchors_by_id:
            _fail("BINDING_ANCHOR_REFERENCE_INVALID",
                  f"rejection {rejection.record_id} references undeclared "
                  f"anchor {rejection.rejected_anchor_id}")

    # -- closures: narrowing-only, at most one per assertion -------------
    closure_records: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in assertions}
    effective_applies: dict[str, AppliesScope] = {
        record_id: assertion.applies
        for record_id, assertion in assertions.items()}
    for closure_id in sorted(closures):  # deterministic validation order
        closure = closures[closure_id]
        target = assertions.get(closure.closes)
        if target is None:
            _fail("BINDING_CLOSURE_INVALID",
                  f"{closure.record_id} closes a missing assertion")
        if closure_records[target.record_id]:
            _fail("BINDING_MULTIPLE_CLOSURES",
                  f"assertion {target.record_id} has contradictory closures; "
                  "no silent winner is selected")
        scope = target.applies
        if scope.end_boundary.kind == "declared":
            _fail("BINDING_CLOSURE_INVALID",
                  "a closure may only narrow an unknown or unbounded end; "
                  "changing a declared end is a correction (supersede)")
        if (scope.start_boundary.kind == "declared"
                and closure.end <= scope.start_boundary.at):
            _fail("BINDING_CLOSURE_INVALID",
                  "closure end must exceed the declared start")
        closure_records[target.record_id] = (closure.record_id,)
        effective_applies[target.record_id] = scope.model_copy(update={
            "end_boundary": DeclaredBoundary(kind="declared", at=closure.end)})

    superseded_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in assertions}
    retracted_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in assertions}
    for assertion in assertions.values():
        if assertion.supersedes is not None:
            superseded_by[assertion.supersedes] = tuple(sorted(
                (*superseded_by[assertion.supersedes], assertion.record_id)))
    for retraction in retractions.values():
        retracted_by[retraction.retracts] = tuple(sorted(
            (*retracted_by[retraction.retracts], retraction.record_id)))

    record_ids = tuple(sorted(records))
    revision = BindingRevision(
        revision_id=compute_revision_id(binding_set_id, record_ids),
        record_ids=record_ids, record_count=len(record_ids),
        binding_set_id=binding_set_id)
    return LoadedBindingSet(
        revision=revision, records=dict(records),
        anchors_by_id=anchors_by_id, declarations=declarations,
        assertions=assertions, retractions=retractions, closures=closures,
        rejections=rejections, superseded_by=superseded_by,
        retracted_by=retracted_by, closure_records=closure_records,
        effective_applies=effective_applies)


class BindingStore:
    def __init__(self, set_dir: Path | str) -> None:
        set_dir = Path(set_dir)
        if not re.fullmatch(BINDING_SET_ID_PATTERN, set_dir.name):
            raise BindingConfigurationError(
                "BINDING_SET_ID_INVALID",
                f"binding-set directory name {set_dir.name!r} must match "
                f"{BINDING_SET_ID_PATTERN}")
        self.binding_set_id = set_dir.name
        self.records_dir = set_dir / "records"
        self.records_dir.mkdir(parents=True, exist_ok=True)

    # -- append (write-once, atomic, single-writer) -----------------------

    def append(self, record: LedgerRecord) -> str:
        if not verify_record_id(record):
            raise BindingIntegrityError(
                "BINDING_RECORD_HASH_MISMATCH",
                "record content does not match its record_id")
        payload = {**canonical_payload(record), "record_id": record.record_id}
        text = json.dumps(payload, sort_keys=True, indent=2,
                          ensure_ascii=False) + "\n"
        final = self.records_dir / f"{record.record_id}.json"
        if final.exists():
            return record.record_id  # identical content by construction
        temp = final.with_suffix(".json.tmp")
        temp.write_text(text, encoding="utf-8")
        temp.replace(final)
        return record.record_id

    # -- load --------------------------------------------------------------

    def _read_record(self, path: Path) -> LedgerRecord:
        try:
            record = _RECORD_ADAPTER.validate_json(
                path.read_text(encoding="utf-8"))
        except (ValidationError, ValueError, OSError) as error:
            raise BindingIntegrityError(
                "BINDING_RECORD_INVALID",
                f"{path.name} is not a valid ledger record") from error
        if path.name != f"{record.record_id}.json" or not verify_record_id(record):
            raise BindingIntegrityError(
                "BINDING_RECORD_HASH_MISMATCH",
                f"{path.name} does not match its content-derived id")
        return record

    def load(self) -> LoadedBindingSet:
        records: dict[str, LedgerRecord] = {}
        for path in self.records_dir.iterdir():
            if not _FILENAME.fullmatch(path.name):
                raise BindingIntegrityError(
                    "BINDING_RECORD_INVALID",
                    f"unexpected file in the ledger: {path.name}")
            record = self._read_record(path)
            records[record.record_id] = record
        return validate_record_collection(
            self.binding_set_id, records, verify_hashes=False)

    def load_revision(self, record_ids: Iterable[str]) -> LoadedBindingSet:
        """Replay an explicitly supplied membership from the still-present
        append-only records. The subset must be reference-closed."""
        records: dict[str, LedgerRecord] = {}
        for record_id in record_ids:
            path = self.records_dir / f"{record_id}.json"
            if not path.exists():
                raise BindingIntegrityError(
                    "BINDING_REVISION_INVALID",
                    f"revision member {record_id} is not present in the set")
            records[record_id] = self._read_record(path)
        return validate_record_collection(
            self.binding_set_id, records, verify_hashes=False)
