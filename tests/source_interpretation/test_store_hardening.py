"""ES-001 Group 6 adversarial store regressions.

These tests exercise operational boundaries that ordinary validating append
cannot manufacture: hostile replay selectors, crafted on-disk collections,
forged lifecycle instances, and failed atomic promotion.
"""

import json
from datetime import timedelta

import pytest

from backend.source_interpretation import (
    InterpretationClosure,
    InterpretationIntegrityError,
    InterpretationRejection,
    InterpretationRetraction,
    InterpretationStore,
    build_record,
    canonical_payload,
)
from tests.source_interpretation.test_store import (
    AUTH,
    PROP,
    SUBJECT,
    T0,
    UNIT,
    close,
    retract,
    scope,
    spi,
    store,
)


def write_record(ledger, record, *, payload=None, filename=None):
    body = payload if payload is not None else {
        **canonical_payload(record), "record_id": record.record_id}
    path = ledger.records_dir / (filename or f"{record.record_id}.json")
    path.write_text(json.dumps(body, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8")
    return path


def files(ledger):
    return {path.name: path.read_bytes()
            for path in sorted(ledger.records_dir.iterdir())}


def test_malformed_replay_id_never_echoes_an_absolute_path(tmp_path):
    ledger = store(tmp_path)
    hostile = "/home/owner/private/interpretation.json"
    with pytest.raises(InterpretationIntegrityError) as error:
        ledger.load_revision((hostile,))
    assert error.value.error_code == "INTERPRETATION_REVISION_INVALID"
    assert hostile not in error.value.message
    assert "/home/" not in error.value.message


@pytest.mark.parametrize("mutation,expected_code", [
    ("malformed_json", "INTERPRETATION_RECORD_INVALID"),
    ("unknown_field", "INTERPRETATION_RECORD_INVALID"),
    ("naive_datetime", "INTERPRETATION_RECORD_INVALID"),
    ("wrong_digest", "INTERPRETATION_RECORD_HASH_MISMATCH"),
])
def test_one_corrupt_file_invalidates_the_whole_load(
        tmp_path, mutation, expected_code):
    ledger = store(tmp_path)
    good = spi(note="good")
    ledger.append(good)
    bad = spi(note="bad")
    payload = {**canonical_payload(bad), "record_id": bad.record_id}
    if mutation == "malformed_json":
        (ledger.records_dir / f"{bad.record_id}.json").write_text(
            "{not-json", encoding="utf-8")
    elif mutation == "unknown_field":
        payload["unexpected"] = True
        write_record(ledger, bad, payload=payload)
    elif mutation == "naive_datetime":
        payload["recorded_at"] = "2026-08-13T12:00:00"
        write_record(ledger, bad, payload=payload)
    else:
        payload["note"] = "tampered-with-id-kept"
        write_record(ledger, bad, payload=payload)
    with pytest.raises(InterpretationIntegrityError) as error:
        ledger.load()
    assert error.value.error_code == expected_code
    assert str(tmp_path) not in error.value.message


def test_crafted_missing_and_cross_key_parents_fail_whole_load(tmp_path):
    missing_ledger = store(tmp_path / "missing")
    orphan = spi(parents=("spi_" + "f" * 64,))
    write_record(missing_ledger, orphan)
    with pytest.raises(InterpretationIntegrityError) as error:
        missing_ledger.load()
    assert error.value.error_code == "INTERPRETATION_SUPERSEDES_INVALID"

    cross_ledger = store(tmp_path / "cross")
    parent = spi()
    changed_property = PROP.model_copy(update={"item_key": "other"})
    child = spi(prop=changed_property, parents=(parent.record_id,))
    write_record(cross_ledger, parent)
    write_record(cross_ledger, child)
    with pytest.raises(InterpretationIntegrityError) as error:
        cross_ledger.load()
    assert error.value.error_code == "INTERPRETATION_SUPERSEDES_INVALID"


def test_crafted_missing_and_multiple_closures_fail_whole_load(tmp_path):
    missing_ledger = store(tmp_path / "missing")
    absent = spi(note="absent")
    write_record(missing_ledger, close(absent))
    with pytest.raises(InterpretationIntegrityError) as error:
        missing_ledger.load()
    assert error.value.error_code == "INTERPRETATION_CLOSURE_INVALID"

    multiple_ledger = store(tmp_path / "multiple")
    root = spi()
    first = close(root)
    second = close(root, T0 + timedelta(minutes=45))
    for record in (root, first, second):
        write_record(multiple_ledger, record)
    with pytest.raises(InterpretationIntegrityError) as error:
        multiple_ledger.load()
    assert error.value.error_code == "INTERPRETATION_MULTIPLE_CLOSURES"


def test_closure_replay_omission_restores_original_scope(tmp_path):
    ledger = store(tmp_path)
    root = spi(applies=scope("unknown"))
    amendment = close(root)
    ledger.append(root)
    ledger.append(amendment)
    current = ledger.load()
    replay = ledger.load_revision((root.record_id,))
    assert current.effective_applies[root.record_id].end_boundary.kind == "declared"
    assert replay.effective_applies[root.record_id] == root.applies
    assert replay.closure_records[root.record_id] == ()


def test_tampered_existing_file_blocks_append_without_overwrite(tmp_path):
    ledger = store(tmp_path)
    record = spi()
    ledger.append(record)
    path = ledger.records_dir / f"{record.record_id}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["note"] = "different content under the old id"
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8")
    before = path.read_bytes()
    with pytest.raises(InterpretationIntegrityError) as error:
        ledger.append(record)
    assert error.value.error_code == "INTERPRETATION_RECORD_HASH_MISMATCH"
    assert path.read_bytes() == before


@pytest.mark.parametrize("record_cls,target_field,prefix", [
    (InterpretationRetraction, "retracts", "spr_"),
    (InterpretationClosure, "closes", "spc_"),
])
def test_forged_lifecycle_record_is_revalidated_before_write(
        tmp_path, record_cls, target_field, prefix):
    ledger = store(tmp_path)
    root = spi()
    ledger.append(root)
    valid = (retract(root) if record_cls is InterpretationRetraction
             else close(root))
    forged = record_cls.model_construct(
        **{**valid.model_dump(), target_field: "not-an-id"})
    before = files(ledger)
    with pytest.raises(InterpretationIntegrityError) as error:
        ledger.append(forged)
    assert error.value.error_code == "INTERPRETATION_RECORD_INVALID"
    assert files(ledger) == before


def test_forged_rejection_is_revalidated_before_write(tmp_path):
    ledger = store(tmp_path)
    valid = build_record(
        InterpretationRejection, subject=SUBJECT, property=PROP,
        rejected_interpretation={"dimension": "unit", "unit": UNIT},
        proposed_applies=scope(), recorded_at=T0, authority=AUTH, note="")
    forged = InterpretationRejection.model_construct(
        **{**valid.model_dump(), "subject": {"source_id": "incomplete"}})
    with pytest.raises(InterpretationIntegrityError) as error:
        ledger.append(forged)
    assert error.value.error_code == "INTERPRETATION_RECORD_INVALID"
    assert ledger.load().revision.record_count == 0


def test_failed_atomic_promotion_leaves_no_visible_record_or_temp(
        tmp_path, monkeypatch):
    import backend.source_interpretation.store as store_module

    ledger = store(tmp_path)
    record = spi()

    def fail_replace(source, target):
        raise OSError("synthetic promote failure")

    monkeypatch.setattr(store_module.os, "replace", fail_replace)
    with pytest.raises(InterpretationIntegrityError) as error:
        ledger.append(record)
    assert error.value.error_code == "INTERPRETATION_STORAGE_FAILURE"
    assert ledger.load().revision.record_count == 0
    assert not (ledger.records_dir / f"{record.record_id}.json").exists()
    assert list(ledger.staging_dir.iterdir()) == []
