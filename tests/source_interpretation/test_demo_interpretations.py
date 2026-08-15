"""ES-001 committed interpretation set: exact membership and integrity."""

import hashlib
import json
from pathlib import Path

from backend.source_interpretation import InterpretationStore, verify_record_id

ROOT = Path("interpretations/demo-printer")
RECORD_IDS = (
    "spi_07548575f798119990ac283484f81f183208223abc31f314ae042242b72848cc",
    "spi_2fef48f888b20a82a9c6f535262112527b194de31f07e02e36a7954a78433b92",
    "spi_5a4eca7a600e2f682514e574d443b22dd0110337c5097902a0920fb6a930682a",
)
REVISION = ("irv_6b65d609f8074091e1e09aee99c8b4a0360ecacd672ff99ede5a076"
            "c2b3cd57f")
FROZEN = {
    f"{RECORD_IDS[0]}.json":
    "935655a321f3f0fceb317e1ce1e8e0c51e0c5a2a2ebe1599395bfc2a53c7b19c",
    f"{RECORD_IDS[1]}.json":
    "1851dadef578f49489d1d2555996b168d383044cff56bf3dc81b8471887b2d48",
    f"{RECORD_IDS[2]}.json":
    "e34c0c7bc0b16af364b1bca3d50130575b2bdd38683c4a6f1566eda7f5c103cd",
}


def test_exact_revision_membership_and_explicit_replay():
    store = InterpretationStore(ROOT)
    loaded = store.load()
    assert loaded.revision.revision_id == REVISION
    assert loaded.revision.record_ids == tuple(sorted(RECORD_IDS))
    assert loaded.revision.record_count == 3
    replayed = store.load_revision(RECORD_IDS)
    assert replayed.revision == loaded.revision
    assert all(verify_record_id(record) for record in loaded.records.values())


def test_exhaustive_authority_dimensions_and_no_rejection():
    loaded = InterpretationStore(ROOT).load()
    assert not loaded.rejections
    assert not list((ROOT / "records").glob("spj_*.json"))
    expected_dimensions = {
        RECORD_IDS[0]: "observation_role",
        RECORD_IDS[1]: "quantity_kind",
        RECORD_IDS[2]: "unit",
    }
    assert set(loaded.records) == set(expected_dimensions)
    for record_id, record in loaded.records.items():
        assert record.authority.kind == "test_fixture"
        assert record.authority.agent == "es001_demo_fixture"
        assert record.interpretation.dimension == expected_dimensions[record_id]
        assert record.supersedes == ()
        assert "authority knowledge" in record.note
        assert "never source-supplied evidence" in record.note


def test_new_files_are_byte_frozen_and_contain_no_secrets_or_values():
    paths = sorted((ROOT / "records").glob("*.json"))
    assert [path.name for path in paths] == sorted(FROZEN)
    for path in paths:
        raw = path.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == FROZEN[path.name]
        text = raw.decode()
        for needle in ("/home/", "/mnt/", "C:\\", "password", "secret",
                       "Bearer", "api_key", "60.1", "60.4", "value_json",
                       "occurrence", "payload_checksum"):
            assert needle not in text, (path.name, needle)
        payload = json.loads(text)
        assert payload["recorded_at"] == "2026-08-13T12:00:00+00:00"


def test_binding_ledgers_remain_at_accepted_membership_counts():
    assert len(list(Path("bindings/demo-printer/records").glob("*.json"))) == 6
    assert len(list(Path(
        "bindings/demo-printer-model/records").glob("*.json"))) == 5

