"""FL-001 Slice A canonical flow identity and stored-byte vectors."""

from datetime import timedelta, timezone
import hashlib
import json
import re

import pytest
from pydantic import TypeAdapter, ValidationError

import backend.model_kernel as kernel
from backend.model_kernel.canonical import (
    _flow_effective_body_bytes,
    canonical_bytes,
    compute_record_id,
    verify_record_id,
)
from backend.model_kernel.contracts import MODEL_RECORD_ID_PATTERN
from backend.model_kernel.store import _FILENAME

from tests.model_kernel.fl001_slice_a_helpers import (
    FLOW_A,
    FLOW_B,
    PORT_A,
    PORT_B,
    T0,
    flow_declaration,
    flow_fixture,
    flow_kind,
    flow_registration,
    flow_withdrawal,
)


FRG_ID = "frg_5bc6c9f50b93f626575e8da6755db2c47db1f0a55a9979cb6156d55bc20b75ff"
FLD_ID = "fld_b5ee7eb849e45f335b33aa90778e88f0281d5be7ef6d33bb50a92ac4974ec477"
FLW_ID = "flw_5ad024b9701624184435bba93be313786dae82cae31386b45ab671c979ce91a8"
CANONICAL_BYTES = (963, 1585, 296)
STORED_BYTES = (1264, 2001, 430)
STORED_SHA256 = (
    "2d41fdae1bd26c4a4dbe4fada00ddb9e3139619201f069c5a506e9d0ed65e9c7",
    "6faa2919b9a5392498384dc1c94b73b26955589031a1ea1de9c12c7878c33311",
    "4ce2bbc5f90a97404d28ca77b9b2aa1af6c2edce5e49e8f46de58e2121ce7191",
)


def claims():
    records, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    declaration = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs)
    withdrawal = flow_withdrawal(declaration)
    return records, registration, declaration, withdrawal


def test_ids_equal_normative_canonical_sha256_and_use_plus_utc():
    _, registration, declaration, withdrawal = claims()
    values = (registration, declaration, withdrawal)
    assert tuple(record.record_id for record in values) == (
        FRG_ID, FLD_ID, FLW_ID)
    assert tuple(len(canonical_bytes(record)) for record in values) == \
        CANONICAL_BYTES
    for record in values:
        payload = canonical_bytes(record)
        assert record.record_id.rsplit("_", 1)[1] == hashlib.sha256(
            payload).hexdigest()
        assert compute_record_id(record) == record.record_id
        assert verify_record_id(record) is True
        assert b"+00:00" in payload
        assert b"Z" not in payload


def test_record_and_filename_grammar_accept_exactly_three_flow_prefixes():
    for prefix in ("frg", "fld", "flw"):
        value = prefix + "_" + "a" * 64
        assert re.fullmatch(MODEL_RECORD_ID_PATTERN, value)
        assert _FILENAME.fullmatch(value + ".json")
    for malformed in (
        "FLD_" + "a" * 64,
        "flr_" + "a" * 64,
        "fld_" + "A" * 64,
        "fld_" + "a" * 63,
    ):
        assert not re.fullmatch(MODEL_RECORD_ID_PATTERN, malformed)
        assert not _FILENAME.fullmatch(malformed + ".json")


def test_permutations_are_stable_but_roles_partitions_and_tokens_are_semantic():
    _, base, ports, *_ = flow_fixture()
    many_ports = tuple((*base.source_port_anchor_ids,
                        *base.sink_port_anchor_ids))
    alternate = flow_registration(
        source_ports=(PORT_B, PORT_A),
        sink_ports=("prt_" + "4" * 32, "prt_" + "3" * 32),
        port_records=(), evidence=base.evidence)
    permuted = flow_registration(
        source_ports=(PORT_A, PORT_B),
        sink_ports=("prt_" + "3" * 32, "prt_" + "4" * 32),
        port_records=(), evidence=tuple(reversed(base.evidence)))
    assert alternate == permuted
    assert canonical_bytes(alternate) == canonical_bytes(permuted)

    reverse = flow_registration(
        flow_anchor_id=FLOW_B,
        source_ports=base.sink_port_anchor_ids,
        sink_ports=base.source_port_anchor_ids,
        port_records=ports,
        evidence=base.evidence)
    different_kind = flow_registration(
        flow_anchor_id=FLOW_B,
        source_ports=base.source_port_anchor_ids,
        sink_ports=base.sink_port_anchor_ids,
        port_records=ports,
        kind=flow_kind(code="other_kind"),
        evidence=base.evidence)
    assert many_ports == (PORT_A, PORT_B)
    assert reverse.record_id != base.record_id
    assert different_kind.record_id != base.record_id


def test_equivalent_instant_and_parent_order_have_stable_identity():
    records, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    root = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs, note="root")
    other = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs,
        recorded_at=T0.replace(hour=14), note="other")
    eastern = timezone(timedelta(hours=2))
    forward = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs,
        supersedes=(other.record_id, root.record_id),
        recorded_at=T0.astimezone(eastern), note="merge")
    reverse = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs,
        supersedes=(root.record_id, other.record_id),
        recorded_at=T0, note="merge")
    assert records
    assert forward == reverse
    assert canonical_bytes(forward) == canonical_bytes(reverse)


def test_effective_body_is_exact_and_excludes_audit_or_evidence_fields():
    _, registration, ports, pcn, source_pifs, sink_pifs = flow_fixture()
    first = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs, note="first")
    second = flow_declaration(
        registration, port_records=ports, pcn=pcn,
        source_pifs=source_pifs, sink_pifs=sink_pifs,
        recorded_at=T0.replace(hour=15), note="second")
    decoded = json.loads(_flow_effective_body_bytes(first))
    assert tuple(sorted(decoded)) == tuple(sorted((
        "flow_anchor_id", "context", "connection_assertion_record_id",
        "source_direction_pins", "sink_direction_pins")))
    assert _flow_effective_body_bytes(first) == \
        _flow_effective_body_bytes(second)


def test_stale_id_kind_substitution_and_hostile_nested_pin_fail():
    adapter = TypeAdapter(kernel.ModelRecord)
    _, _, declaration, _ = claims()
    stale = adapter.validate_python({
        **declaration.model_dump(), "record_id": "fld_" + "0" * 64})
    assert verify_record_id(stale) is False
    with pytest.raises(ValidationError):
        adapter.validate_python({
            **declaration.model_dump(), "record_id": "flw_" + "0" * 64})
    hostile_pin = declaration.source_direction_pins[0].model_copy(update={
        "declaration_record_id": "pif_NOT_HEX"})
    hostile = declaration.model_copy(update={
        "source_direction_pins": (hostile_pin,)})
    with pytest.raises(ValidationError):
        adapter.validate_python(hostile)


def test_literal_stored_json_bytes_and_hashes_are_golden(tmp_path):
    records, registration, declaration, withdrawal = claims()
    store = kernel.ModelStore(tmp_path / "test-model")
    for record in (*records, registration, declaration, withdrawal):
        store.append(record)
    values = (registration, declaration, withdrawal)
    stored = tuple((store.records_dir / f"{record.record_id}.json").read_bytes()
                   for record in values)
    assert tuple(len(value) for value in stored) == STORED_BYTES
    assert tuple(hashlib.sha256(value).hexdigest() for value in stored) == \
        STORED_SHA256
