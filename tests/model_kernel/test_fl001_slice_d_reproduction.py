"""Permanent, minter-free FL-001 Slice D frozen-contract reproduction."""

from __future__ import annotations

import ast
import json
import os
from pathlib import Path
import subprocess
import sys

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
        expected_authoritative="proposed",
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


def test_embedded_checksums_are_independently_enforced(monkeypatch):
    manifest = json.loads(reproduction.MANIFEST_PATH.read_bytes())
    manifest["content"]["semantic_inputs"]["registration"]["anchor"][
        "display_name"] += " forged"
    manifest_bytes = reproduction.canonical_json_bytes(manifest)
    monkeypatch.setattr(reproduction, "MANIFEST_BYTES", len(manifest_bytes))
    monkeypatch.setattr(
        reproduction, "MANIFEST_SHA256",
        reproduction.sha256_bytes(manifest_bytes))
    with pytest.raises(reproduction.FrozenContractError,
                       match="embedded checksum"):
        reproduction.load_frozen_contract(manifest_bytes=manifest_bytes)

    disclosure = json.loads(reproduction.DISCLOSURE_PATH.read_bytes())
    disclosure["content"]["scope"]["statement"] += " forged"
    disclosure_bytes = reproduction.canonical_json_bytes(disclosure)
    monkeypatch.setattr(
        reproduction, "DISCLOSURE_BYTES", len(disclosure_bytes))
    monkeypatch.setattr(
        reproduction, "DISCLOSURE_SHA256",
        reproduction.sha256_bytes(disclosure_bytes))
    with pytest.raises(reproduction.FrozenContractError,
                       match="embedded checksum"):
        reproduction.validate_disclosure_bytes(disclosure_bytes)


def test_resigned_semantic_substitution_still_cannot_rebuild_candidate(
        monkeypatch):
    manifest = json.loads(reproduction.MANIFEST_PATH.read_bytes())
    manifest["content"]["semantic_inputs"]["registration"]["anchor"][
        "display_name"] += " forged"
    manifest["manifest_checksum"]["value"] = reproduction.sha256_bytes(
        reproduction.canonical_json_bytes(manifest["content"]))
    manifest_bytes = reproduction.canonical_json_bytes(manifest)
    monkeypatch.setattr(reproduction, "MANIFEST_BYTES", len(manifest_bytes))
    monkeypatch.setattr(
        reproduction, "MANIFEST_SHA256",
        reproduction.sha256_bytes(manifest_bytes))
    frozen = reproduction.load_frozen_contract(
        manifest_bytes=manifest_bytes)
    with pytest.raises(reproduction.FrozenContractError,
                       match="candidate IDs/order changed"):
        reproduction.candidate_records(frozen)


@pytest.mark.parametrize("mutation", ("reorder", "extra"))
def test_append_order_or_extra_membership_fails_external_pin(mutation):
    manifest = json.loads(reproduction.MANIFEST_PATH.read_bytes())
    contract = manifest["content"]["candidate_contract"]
    if mutation == "reorder":
        contract["append_order"].reverse()
    else:
        contract["proposed_membership"].append("frg_" + "0" * 64)
    with pytest.raises(reproduction.FrozenContractError):
        reproduction.load_frozen_contract(
            manifest_bytes=reproduction.canonical_json_bytes(manifest))


def test_disposable_root_guards_reject_authoritative_and_nonempty_paths(
        tmp_path):
    with pytest.raises(reproduction.FrozenContractError,
                       match="overlaps authoritative"):
        reproduction._safe_root(reproduction.AUTHORITATIVE_MODEL)
    occupied = tmp_path / "occupied"
    occupied.mkdir()
    (occupied / "sentinel").touch()
    with pytest.raises(reproduction.FrozenContractError,
                       match="absent or empty"):
        reproduction._safe_root(occupied)


def test_reproduction_is_hash_seed_independent():
    script = """
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.model_kernel import fl001_slice_d_reproduction as r
with TemporaryDirectory(prefix='fl001-seed-') as temporary:
    result = r.run_reproduction(Path(temporary) / 'root')
print(json.dumps({
    'artifact_sha256': result.artifact_sha256,
    'artifact_bytes': result.artifact_bytes,
    'record_ids': result.record_ids,
    'record_file_sha256': result.record_file_sha256,
    'intermediate_revision_id': result.intermediate_revision_id,
    'revision_id': result.revision_id,
    'predecessor_aggregate_sha256': result.predecessor_aggregate_sha256,
}, sort_keys=True, separators=(',', ':')))
"""
    outputs = []
    for seed in ("1", "7", "12345"):
        environment = dict(os.environ)
        environment.update({
            "PYTHONHASHSEED": seed,
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        completed = subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(),
            env=environment, check=True, capture_output=True, text=True)
        outputs.append(completed.stdout)
    assert outputs[0] == outputs[1] == outputs[2]


def test_authoritative_proposed_gate_is_exact_and_read_only():
    before = reproduction.authoritative_snapshot()
    reproduction.verify_authoritative_ledger("proposed")
    assert reproduction.authoritative_snapshot() == before
