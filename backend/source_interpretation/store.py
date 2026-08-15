"""Write-once, validating source-interpretation ledger store.

Every append validates the complete current collection and the prospective
collection before staging a byte. Load and explicit replay are all-or-nothing;
current tips and lifecycle indexes are membership-relative.
"""

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Iterable, Mapping
from uuid import uuid4

from pydantic import TypeAdapter, ValidationError

from backend.identity_binding.contracts import AppliesScope, DeclaredBoundary
from backend.source_interpretation.canonical import (
    canonical_payload, compute_revision_id, verify_record_id)
from backend.source_interpretation.contracts import (
    INTERPRETATION_RECORD_ID_PATTERN, INTERPRETATION_SET_ID_PATTERN,
    InterpretationClosure, InterpretationRecord, InterpretationRejection,
    InterpretationRetraction, InterpretationRevision,
    SourcePropertyInterpretation)
from backend.source_interpretation.errors import (
    InterpretationConfigurationError, InterpretationIntegrityError)
from backend.temporal_state.contracts import SourcePropertyRef, SourceSubjectRef

_RECORD_ADAPTER: TypeAdapter = TypeAdapter(InterpretationRecord)
_RECORD_ID = re.compile(INTERPRETATION_RECORD_ID_PATTERN)
_FILENAME = re.compile(r"^(spi|spr|spc|spj)_[0-9a-f]{64}\.json$")
_EMPTY: Mapping = MappingProxyType({})

InterpretationKey = tuple[SourceSubjectRef, SourcePropertyRef, str]


def _frozen_mapping(mapping: Mapping) -> Mapping:
    return MappingProxyType(dict(mapping))


@dataclass(frozen=True)
class LoadedInterpretationSet:
    """One immutable validated revision and its derived lifecycle indexes."""

    revision: InterpretationRevision
    records: Mapping[str, InterpretationRecord]
    interpretations: Mapping[str, SourcePropertyInterpretation]
    retractions: Mapping[str, InterpretationRetraction]
    closures: Mapping[str, InterpretationClosure]
    rejections: Mapping[str, InterpretationRejection]
    current_interpretation_tips_by_property_dimension: Mapping[
        InterpretationKey, tuple[SourcePropertyInterpretation, ...]] = _EMPTY
    interpretation_superseded_by: Mapping[str, tuple[str, ...]] = _EMPTY
    retracted_by: Mapping[str, tuple[str, ...]] = _EMPTY
    closure_records: Mapping[str, tuple[str, ...]] = _EMPTY
    effective_applies: Mapping[str, AppliesScope] = _EMPTY


def _fail(code: str, message: str) -> None:
    raise InterpretationIntegrityError(code, message)


def _key(record: SourcePropertyInterpretation) -> InterpretationKey:
    return (record.subject, record.property, record.interpretation.dimension)


def revalidate(record) -> InterpretationRecord:
    """Revalidate a possibly forged instance at an operational boundary."""
    try:
        payload = record.model_dump(mode="python", warnings=False)
        return _RECORD_ADAPTER.validate_python(payload)
    except (ValidationError, ValueError, TypeError, AttributeError, KeyError,
            UnicodeError, Warning) as error:
        record_id = getattr(record, "record_id", None)
        subject = record_id if isinstance(record_id, str) else "<unidentified>"
        raise InterpretationIntegrityError(
            "INTERPRETATION_RECORD_INVALID",
            f"record {subject} is not structurally valid") from error


def _check_acyclic(interpretations: Mapping[str, SourcePropertyInterpretation]
                   ) -> None:
    """Iterative three-colour traversal over the multi-parent DAG."""
    colour: dict[str, int] = {}
    for root_id in sorted(interpretations):
        if colour.get(root_id) == 2:
            continue
        stack: list[tuple[str, bool]] = [(root_id, False)]
        while stack:
            record_id, exiting = stack.pop()
            if exiting:
                colour[record_id] = 2
                continue
            state = colour.get(record_id, 0)
            if state == 2:
                continue
            if state == 1:
                _fail("INTERPRETATION_SUPERSEDES_INVALID",
                      "interpretation supersession cycle")
            colour[record_id] = 1
            stack.append((record_id, True))
            for parent_id in reversed(interpretations[record_id].supersedes):
                parent_state = colour.get(parent_id, 0)
                if parent_state == 1:
                    _fail("INTERPRETATION_SUPERSEDES_INVALID",
                          "interpretation supersession cycle")
                if parent_state == 0:
                    stack.append((parent_id, False))


def validate_record_collection(
    interpretation_set_id: str,
    records: Mapping[str, InterpretationRecord],
    *,
    verify_hashes: bool = True,
) -> LoadedInterpretationSet:
    """Validate a whole set, prospective set, or reference-closed replay."""
    if (not isinstance(interpretation_set_id, str)
            or not re.fullmatch(INTERPRETATION_SET_ID_PATTERN,
                                interpretation_set_id)):
        raise InterpretationConfigurationError(
            "INTERPRETATION_SET_ID_INVALID",
            "interpretation set id does not match the required grammar")
    if not isinstance(records, Mapping):
        _fail("INTERPRETATION_RECORD_INVALID",
              "a record collection must be a mapping")

    validated: dict[str, InterpretationRecord] = {}
    for supplied_key, supplied_record in records.items():
        record = revalidate(supplied_record)
        if supplied_key != record.record_id:
            _fail("INTERPRETATION_RECORD_KEY_MISMATCH",
                  f"collection key does not match {record.record_id}")
        if verify_hashes and not verify_record_id(record):
            _fail("INTERPRETATION_RECORD_HASH_MISMATCH",
                  f"content of {record.record_id} does not match its id")
        validated[supplied_key] = record

    interpretations: dict[str, SourcePropertyInterpretation] = {}
    retractions: dict[str, InterpretationRetraction] = {}
    closures: dict[str, InterpretationClosure] = {}
    rejections: dict[str, InterpretationRejection] = {}
    for record_id, record in validated.items():
        bucket = {
            "source_property_interpretation": interpretations,
            "interpretation_retraction": retractions,
            "interpretation_closure": closures,
            "interpretation_rejection": rejections,
        }[record.record_kind]
        bucket[record_id] = record

    superseded_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in interpretations}
    for record in interpretations.values():
        for parent_id in record.supersedes:
            parent = interpretations.get(parent_id)
            if parent is None or _key(parent) != _key(record):
                _fail("INTERPRETATION_SUPERSEDES_INVALID",
                      f"{record.record_id} has an invalid supersession parent")
            superseded_by[parent_id] = tuple(sorted(
                (*superseded_by[parent_id], record.record_id)))
    _check_acyclic(interpretations)

    retracted_by: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in interpretations}
    for record in retractions.values():
        if record.retracts not in interpretations:
            _fail("INTERPRETATION_RETRACTS_INVALID",
                  f"{record.record_id} retracts a missing interpretation")
        retracted_by[record.retracts] = tuple(sorted(
            (*retracted_by[record.retracts], record.record_id)))

    closure_records: dict[str, tuple[str, ...]] = {
        record_id: () for record_id in interpretations}
    effective_applies: dict[str, AppliesScope] = {
        record_id: record.applies
        for record_id, record in interpretations.items()}
    for closure_id in sorted(closures):
        closure = closures[closure_id]
        target = interpretations.get(closure.closes)
        if target is None:
            _fail("INTERPRETATION_CLOSURE_INVALID",
                  f"{closure.record_id} closes a missing interpretation")
        if closure_records[target.record_id]:
            _fail("INTERPRETATION_MULTIPLE_CLOSURES",
                  f"interpretation {target.record_id} has multiple closures")
        scope = target.applies
        if scope.end_boundary.kind == "declared":
            _fail("INTERPRETATION_CLOSURE_INVALID",
                  "a closure may only narrow an unknown or unbounded end")
        if (scope.start_boundary.kind == "declared"
                and closure.end <= scope.start_boundary.at):
            _fail("INTERPRETATION_CLOSURE_INVALID",
                  "closure end must exceed the declared start")
        closure_records[target.record_id] = (closure.record_id,)
        effective_applies[target.record_id] = scope.model_copy(update={
            "end_boundary": DeclaredBoundary(kind="declared", at=closure.end)})

    tips: dict[InterpretationKey, tuple[SourcePropertyInterpretation, ...]] = {}
    grouped: dict[InterpretationKey, list[SourcePropertyInterpretation]] = {}
    for record in interpretations.values():
        grouped.setdefault(_key(record), []).append(record)
    for key, lineage in grouped.items():
        current = tuple(sorted(
            (record for record in lineage if not superseded_by[record.record_id]),
            key=lambda record: record.record_id))
        if not current:
            _fail("INTERPRETATION_SUPERSEDES_INVALID",
                  "an interpretation lineage has no current tip")
        tips[key] = current

    record_ids = tuple(sorted(validated))
    revision = InterpretationRevision(
        revision_id=compute_revision_id(interpretation_set_id, record_ids),
        record_ids=record_ids, record_count=len(record_ids),
        interpretation_set_id=interpretation_set_id)
    return LoadedInterpretationSet(
        revision=revision, records=_frozen_mapping(validated),
        interpretations=_frozen_mapping(interpretations),
        retractions=_frozen_mapping(retractions),
        closures=_frozen_mapping(closures), rejections=_frozen_mapping(rejections),
        current_interpretation_tips_by_property_dimension=_frozen_mapping(tips),
        interpretation_superseded_by=_frozen_mapping(superseded_by),
        retracted_by=_frozen_mapping(retracted_by),
        closure_records=_frozen_mapping(closure_records),
        effective_applies=_frozen_mapping(effective_applies))


class InterpretationStore:
    def __init__(self, set_dir: Path | str) -> None:
        if not isinstance(set_dir, (str, os.PathLike)):
            raise InterpretationConfigurationError(
                "INTERPRETATION_SET_ID_INVALID",
                "an interpretation set directory must be path-like")
        set_dir = Path(set_dir)
        if not re.fullmatch(INTERPRETATION_SET_ID_PATTERN, set_dir.name):
            raise InterpretationConfigurationError(
                "INTERPRETATION_SET_ID_INVALID",
                "interpretation set directory name is invalid")
        self.interpretation_set_id = set_dir.name
        self.records_dir = set_dir / "records"
        self.staging_dir = set_dir / ".staging"
        try:
            self.records_dir.mkdir(parents=True, exist_ok=True)
        except OSError as error:
            raise InterpretationIntegrityError(
                "INTERPRETATION_STORAGE_FAILURE",
                f"could not open interpretation set {self.interpretation_set_id}") from error

    def append(self, record: InterpretationRecord) -> str:
        record = revalidate(record)
        if not verify_record_id(record):
            _fail("INTERPRETATION_RECORD_HASH_MISMATCH",
                  "record content does not match its record_id")
        current = self.load()
        if record.record_id in current.records:
            if current.records[record.record_id] != record:
                _fail("INTERPRETATION_RECORD_HASH_MISMATCH",
                      f"stored {record.record_id} differs from the append")
            return record.record_id
        prospective = {**current.records, record.record_id: record}
        validate_record_collection(self.interpretation_set_id, prospective,
                                   verify_hashes=False)
        payload = {**canonical_payload(record), "record_id": record.record_id}
        text = json.dumps(payload, sort_keys=True, indent=2,
                          ensure_ascii=False) + "\n"
        temp = None
        try:
            self.staging_dir.mkdir(parents=True, exist_ok=True)
            temp = self.staging_dir / f"{record.record_id}.{uuid4().hex}.tmp"
            temp.write_text(text, encoding="utf-8")
            os.replace(temp, self.records_dir / f"{record.record_id}.json")
        except OSError as error:
            if temp is not None:
                try:
                    temp.unlink(missing_ok=True)
                except OSError:
                    pass
            raise InterpretationIntegrityError(
                "INTERPRETATION_STORAGE_FAILURE",
                f"could not persist {record.record_id} to interpretation set "
                f"{self.interpretation_set_id}") from error
        return record.record_id

    def _read_record(self, path: Path) -> InterpretationRecord:
        try:
            record = _RECORD_ADAPTER.validate_json(path.read_text(encoding="utf-8"))
        except (ValidationError, ValueError, OSError) as error:
            raise InterpretationIntegrityError(
                "INTERPRETATION_RECORD_INVALID",
                "a stored file is not a valid interpretation record") from error
        if path.name != f"{record.record_id}.json" or not verify_record_id(record):
            _fail("INTERPRETATION_RECORD_HASH_MISMATCH",
                  f"stored record {record.record_id} does not match its "
                  "content-derived id")
        return record

    def load(self) -> LoadedInterpretationSet:
        records: dict[str, InterpretationRecord] = {}
        try:
            paths = sorted(self.records_dir.iterdir())
        except OSError as error:
            raise InterpretationIntegrityError(
                "INTERPRETATION_STORAGE_FAILURE",
                f"could not read interpretation set {self.interpretation_set_id}") from error
        for path in paths:
            if not _FILENAME.fullmatch(path.name):
                _fail("INTERPRETATION_RECORD_INVALID",
                      "the interpretation ledger contains an unexpected file")
            record = self._read_record(path)
            records[record.record_id] = record
        return validate_record_collection(self.interpretation_set_id, records,
                                          verify_hashes=False)

    def load_revision(self, record_ids: Iterable[str]) -> LoadedInterpretationSet:
        try:
            supplied = list(record_ids)
        except Exception as error:
            raise InterpretationIntegrityError(
                "INTERPRETATION_REVISION_INVALID",
                "revision membership could not be materialized") from error
        for record_id in supplied:
            if not isinstance(record_id, str) or not _RECORD_ID.fullmatch(record_id):
                raise InterpretationIntegrityError(
                    "INTERPRETATION_REVISION_INVALID",
                    "revision membership contains an invalid record id")
        if len(set(supplied)) != len(supplied):
            raise InterpretationIntegrityError(
                "INTERPRETATION_REVISION_INVALID",
                "revision membership contains duplicates")
        try:
            with os.scandir(self.records_dir):
                pass
        except OSError as error:
            raise InterpretationIntegrityError(
                "INTERPRETATION_STORAGE_FAILURE",
                f"could not read interpretation set "
                f"{self.interpretation_set_id}") from error
        records: dict[str, InterpretationRecord] = {}
        for record_id in supplied:
            path = self.records_dir / f"{record_id}.json"
            if not path.exists():
                raise InterpretationIntegrityError(
                    "INTERPRETATION_REVISION_INVALID",
                    f"revision member {record_id} is not present in the set")
            records[record_id] = self._read_record(path)
        return validate_record_collection(self.interpretation_set_id, records,
                                          verify_hashes=False)
