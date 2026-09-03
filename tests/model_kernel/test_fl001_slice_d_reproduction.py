"""Permanent, minter-free FL-001 Slice D frozen-contract reproduction."""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from tests.model_kernel import fl001_slice_d_reproduction as reproduction


def test_frozen_files_and_candidate_records_are_exact():
    frozen = reproduction.load_frozen_contract()
    registration, declaration = reproduction.candidate_records(frozen)

    assert registration.record_id == reproduction.FRG_ID
    assert declaration.record_id == reproduction.FLD_ID
    assert tuple(record.record_id for record in (registration, declaration)) == \
        reproduction.APPEND_ORDER


def test_helper_is_statically_minter_free():
    source = Path(reproduction.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = {
        "mint_flow_anchor", "uuid4", "uuid1", "uuid3", "uuid5",
        "random", "randint", "token_bytes", "token_hex",
    }
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    attributes = {
        node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)
    }
    assert not forbidden.intersection(called | attributes)


@pytest.mark.parametrize("reverse_copy_order", (False, True))
def test_independent_disposable_reproduction_is_byte_exact(
        tmp_path, monkeypatch, reverse_copy_order):
    import backend.system_identity as identity

    def forbidden_minter(*args, **kwargs):
        raise AssertionError("the public minter must not run during replay")

    monkeypatch.setattr(identity, "mint_flow_anchor", forbidden_minter)
    result = reproduction.run_reproduction(
        tmp_path / ("reverse" if reverse_copy_order else "forward"),
        reverse_copy_order=reverse_copy_order,
        expected_authoritative="predecessor",
    )
    assert result.artifact_bytes == reproduction.DISCLOSURE_BYTES
    assert result.artifact_sha256 == reproduction.DISCLOSURE_SHA256
    assert result.revision_id == reproduction.PROPOSED_REVISION
    assert result.record_ids == reproduction.APPEND_ORDER


def test_manifest_and_disclosure_tampering_fail_closed():
    manifest = reproduction.MANIFEST_PATH.read_bytes()
    disclosure = reproduction.DISCLOSURE_PATH.read_bytes()

    changed = json.loads(manifest)
    changed["content"]["flow_anchor"]["display_name"] += " forged"
    with pytest.raises(reproduction.FrozenContractError):
        reproduction.load_frozen_contract(
            manifest_bytes=reproduction.canonical_json_bytes(changed))

    resigned = json.loads(manifest)
    resigned["content"]["flow_anchor"]["display_name"] += " forged"
    resigned["manifest_checksum"]["value"] = reproduction.sha256_bytes(
        reproduction.canonical_json_bytes(resigned["content"]))
    with pytest.raises(reproduction.FrozenContractError):
        reproduction.load_frozen_contract(
            manifest_bytes=reproduction.canonical_json_bytes(resigned))

    changed_disclosure = json.loads(disclosure)
    changed_disclosure["content"]["scope"]["statement"] += " forged"
    with pytest.raises(reproduction.FrozenContractError):
        reproduction.validate_disclosure_bytes(
            reproduction.canonical_json_bytes(changed_disclosure))


def test_authoritative_predecessor_gate_is_exact_and_read_only():
    before = reproduction.authoritative_snapshot()
    reproduction.verify_authoritative_ledger("predecessor")
    assert reproduction.authoritative_snapshot() == before
