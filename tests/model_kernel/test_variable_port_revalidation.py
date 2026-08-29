"""VP-001 Slice A trust-boundary, history, freeze, and isolation reds."""

import ast
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from backend.model_kernel import ModelIntegrityError, ModelQueries, ModelStore
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.test_demo_model import (
    CN001_MEMBERSHIP, CURRENT_REVISION, FROZEN_CN001_MODEL_RECORDS,
    FROZEN_ES001_MODEL_RECORDS, FROZEN_MK001_RECORDS,
    FROZEN_PT001_MODEL_RECORDS, FROZEN_SN001_MODEL_RECORDS,
    FROZEN_VM001_RECORD, FROZEN_VS001_RECORD, PRE_CN001_MEMBERSHIP,
    PRE_ES001_MEMBERSHIP, PRE_SPECIFICATION_MEMBERSHIP,
    PRE_VARIABLE_MEMBERSHIP, PT001_MEMBERSHIP, VS001_MEMBERSHIP,
)
from tests.model_kernel.test_demo_pt001 import (
    ARTIFACT_BYTES, ARTIFACT_SHA256, _artifact_bytes,
)
from tests.model_kernel.test_variable_port_records import (
    CONTEXT, association, withdrawal,
)
from tests.model_kernel.test_variable_port_store import base


DEMO_MODEL = Path("models/demo-printer")


def test_model_construct_copy_nested_and_stale_id_forgeries_fail_boundaries(
        tmp_path):
    valid = association()
    stale = valid.model_copy(update={"note": "forged stale id"})
    hostile_context = CONTEXT.model_copy(update={"view": "future_view"})
    nested = valid.model_copy(update={"context": hostile_context})
    for forged in (stale, nested):
        with pytest.raises(ModelIntegrityError):
            validate_record_collection("demo-printer", {
                forged.record_id: forged})
        with pytest.raises(ModelIntegrityError):
            base(tmp_path / forged.note.replace(" ", "-")).append(forged)


def test_hostile_on_disk_record_and_filename_content_mismatch_fail_typed(
        tmp_path):
    store = base(tmp_path)
    valid = association()
    path = store.records_dir / f"{valid.record_id}.json"
    payload = valid.model_dump(mode="json")
    payload["context"]["view"] = "future_view"
    path.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_INVALID"

    other = base(tmp_path / "mismatch")
    wrong = other.records_dir / ("vpa_" + "0" * 64 + ".json")
    wrong.write_text(json.dumps(valid.model_dump(mode="json")), encoding="utf-8")
    with pytest.raises(ModelIntegrityError) as error:
        other.load()
    assert error.value.error_code in {
        "MODEL_RECORD_KEY_MISMATCH", "MODEL_RECORD_HASH_MISMATCH"}


def test_nested_authority_and_hostile_vpw_file_fail_typed(tmp_path):
    hostile_authority = association().authority.model_copy(
        update={"kind": "future_authority"})
    for forged in (
        association().model_copy(update={"authority": hostile_authority}),
        withdrawal().model_copy(update={"authority": hostile_authority}),
    ):
        with pytest.raises(ModelIntegrityError) as error:
            base(tmp_path / forged.record_kind).append(forged)
        assert error.value.error_code == "MODEL_RECORD_INVALID"

    store = base(tmp_path / "vpw-file")
    target = association()
    store.append(target)
    event = withdrawal(target.record_id)
    payload = event.model_dump(mode="json")
    payload["authority"]["kind"] = "future_authority"
    (store.records_dir / f"{event.record_id}.json").write_text(
        json.dumps(payload), encoding="utf-8")
    with pytest.raises(ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def _replace_with_external_symlink(store, record, outside):
    path = store.records_dir / f"{record.record_id}.json"
    outside.write_bytes(path.read_bytes())
    path.unlink()
    path.symlink_to(outside)


def test_load_refuses_validly_named_external_record_symlink_but_file_twin_loads(
        tmp_path):
    store = base(tmp_path / "load")
    claim = association()
    store.append(claim)
    assert store.load().records[claim.record_id] == claim
    _replace_with_external_symlink(store, claim, tmp_path / "outside-load.json")
    with pytest.raises(ModelIntegrityError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_replay_refuses_validly_named_external_record_symlink_but_file_twin(
        tmp_path):
    store = base(tmp_path / "replay")
    claim = association()
    store.append(claim)
    membership = store.load().revision.record_ids
    assert store.replay(membership).records[claim.record_id] == claim
    _replace_with_external_symlink(
        store, claim, tmp_path / "outside-replay.json")
    with pytest.raises(ModelIntegrityError) as error:
        store.replay(membership)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_cycle_is_rejected_even_for_crafted_records_without_hash_verification(
        tmp_path):
    first_id = "vpa_" + "1" * 64
    second_id = "vpa_" + "2" * 64
    first = association().model_copy(update={
        "record_id": first_id, "supersedes": (second_id,)})
    second = association().model_copy(update={
        "record_id": second_id, "supersedes": (first_id,)})
    records = {record.record_id: record
               for record in base(tmp_path).load().records.values()}
    records.update({first_id: first, second_id: second})
    with pytest.raises(ModelIntegrityError) as error:
        validate_record_collection(
            "demo-printer", records, verify_hashes=False)
    assert error.value.error_code == "MODEL_VARIABLE_PORT_LINEAGE_INVALID"


def test_all_explicit_histories_replay_with_empty_immutable_vp_indexes():
    store = ModelStore(DEMO_MODEL)
    for membership in (
        PRE_VARIABLE_MEMBERSHIP, PRE_SPECIFICATION_MEMBERSHIP,
        VS001_MEMBERSHIP, PRE_ES001_MEMBERSHIP, PRE_CN001_MEMBERSHIP,
        CN001_MEMBERSHIP, PT001_MEMBERSHIP,
    ):
        loaded = store.replay(membership)
        assert loaded.variable_port_associations == {}
        assert loaded.variable_port_association_withdrawals == {}
        assert loaded.variable_port_association_ids_by_subject == {}
        with pytest.raises(TypeError):
            loaded.variable_port_associations["forged"] = association()
    assert store.replay(PT001_MEMBERSHIP).revision.revision_id == CURRENT_REVISION


def test_demo_28_bytes_revision_and_artifact_are_frozen_without_vp_fixture():
    paths = sorted((DEMO_MODEL / "records").glob("*.json"))
    assert len(paths) == 28
    assert not any(path.name.startswith(("vpa_", "vpw_")) for path in paths)
    assert ModelStore(DEMO_MODEL).load().revision.revision_id == CURRENT_REVISION
    frozen = {
        **FROZEN_MK001_RECORDS, **FROZEN_VM001_RECORD,
        **FROZEN_VS001_RECORD, **FROZEN_SN001_MODEL_RECORDS,
        **FROZEN_ES001_MODEL_RECORDS, **FROZEN_CN001_MODEL_RECORDS,
        **FROZEN_PT001_MODEL_RECORDS,
    }
    assert len(frozen) == 28
    for filename, digest in frozen.items():
        assert hashlib.sha256((DEMO_MODEL / "records" / filename).read_bytes(
        )).hexdigest() == digest
    artifact = _artifact_bytes()
    assert len(artifact) == ARTIFACT_BYTES
    assert hashlib.sha256(artifact).hexdigest() == ARTIFACT_SHA256


def test_slice_b_is_present_while_c_d_and_upper_layer_imports_are_absent():
    for method in (
        "variable_port_association", "ports_associated_with_variable",
        "variables_associated_with_port", "variable_port_assertion",
    ):
        assert hasattr(ModelQueries, method)
    assert not hasattr(ModelQueries, "associated_port_variable_state")
    assert not Path("backend/variable_port_association").exists()
    assert not Path("backend/variable_port_state").exists()
    assert not any(path.name.startswith(("vpa_", "vpw_"))
                   for path in (DEMO_MODEL / "records").glob("*.json"))
    tree = ast.parse(Path("backend/model_kernel/store.py").read_text())
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert not any(name.startswith((
        "backend.model_state", "backend.temporal_state",
        "backend.identity_binding", "backend.structural_evidence",
        "backend.data_sources")) for name in imports)


def test_slice_c_status_records_review_and_preserves_prior_acceptance():
    accepted = (
        "Slice B is owner accepted at "
        "`81179700513bb671cf9955c6a5d7163e3bcc7e1b`.")
    surfaces = (
        Path("docs/adr/0014-explicit-variable-port-association.md"),
        Path("docs/superpowers/specs/"
             "2026-08-28-vp001-explicit-variable-port-association-design.md"),
        Path("CLAUDE.md"),
        Path("backend/model_kernel/README.md"),
    )
    for path in surfaces:
        text = " ".join(path.read_text(encoding="utf-8").split())
        assert accepted in text
        assert "VP-001 Slices A and B are owner accepted" in text
        assert "Slice D has not started" in text

    reviewed = (
        "VP-001 Slices A and B are owner accepted. Slice C is implemented "
        "and adversarially reviewed; awaiting owner acceptance. Slice D has "
        "not started.")
    reviewed_surfaces = (
        Path("CLAUDE.md"),
        Path("backend/model_state/README.md"),
        Path("backend/model_kernel/README.md"),
        Path("docs/adr/0014-explicit-variable-port-association.md"),
        Path("docs/superpowers/specs/"
             "2026-08-28-vp001-explicit-variable-port-association-design.md"),
        Path("docs/superpowers/plans/"
             "2026-08-28-vp001-adversarial-acceptance-matrix.md"),
        Path("docs/superpowers/plans/"
             "2026-08-29-vp001-slice-c-implementation-plan.md"),
    )
    for path in reviewed_surfaces:
        text = " ".join(path.read_text(encoding="utf-8").split())
        assert reviewed in text
        assert ("displaying variable state beside a port is not a claim that "
                "an observation occurred at the port" in text.lower())

    for path in (Path("CLAUDE.md"), Path("backend/model_kernel/README.md")):
        text = " ".join(path.read_text(encoding="utf-8").split())
        assert "role-free positive" in text
        assert "strict same-owner admission" in text
        assert "independent corroborating roots" in text
        assert "dedicated `vpw_` withdrawals" in text

    specification = surfaces[1].read_text(encoding="utf-8")
    assert "demo ledger remains exactly 28 records" in specification


def test_vp_index_order_is_independent_of_python_hash_seed():
    script = r'''
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from tests.model_kernel.test_variable_port_records import association, withdrawal
from tests.model_kernel.test_variable_port_store import append_all, base
with TemporaryDirectory() as directory:
    root = association(note="root")
    left = association(supersedes=(root.record_id,), note="left")
    right = association(supersedes=(root.record_id,), note="right")
    event = withdrawal(left.record_id)
    loaded = append_all(base(Path(directory)), root, right, left, event).load()
    print(json.dumps({
        "records": list(loaded.variable_port_associations),
        "roots": list(loaded.current_variable_port_association_tips_by_root),
        "tips": {key: [item.record_id for item in value] for key, value in
                 loaded.current_variable_port_association_tips_by_root.items()},
        "ancestry": dict(loaded.variable_port_association_ancestry_by_id),
    }, sort_keys=True))
'''
    outputs = []
    for seed in ("1", "2", "999"):
        environment = dict(os.environ, PYTHONHASHSEED=seed,
                           PYTHONDONTWRITEBYTECODE="1")
        outputs.append(subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(), env=environment,
            check=True, capture_output=True, text=True).stdout)
    assert outputs[0] == outputs[1] == outputs[2]
