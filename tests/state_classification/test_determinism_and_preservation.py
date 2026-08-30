"""Deterministic disclosure and accepted-ledger preservation gates."""

import os
from pathlib import Path
import shutil
import subprocess
import sys

from backend.model_kernel import ModelStore
from tests.state_classification.helpers import classify, state_model


DEMO_MODEL = Path("models/demo-printer")
ACCEPTED_REVISION = (
    "mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b")


def test_physical_record_creation_order_cannot_change_classification(tmp_path):
    original, _, _ = state_model(tmp_path / "original")
    reverse = ModelStore(tmp_path / "reverse" / "demo-printer")
    reverse.records_dir.mkdir(parents=True, exist_ok=True)
    paths = tuple(sorted(original.records_dir.glob("*.json"), reverse=True))
    for path in paths:
        shutil.copyfile(path, reverse.records_dir / path.name)
    assert reverse.load().revision == original.load().revision
    first = classify(tmp_path / "first-evidence", model=original)
    second = classify(tmp_path / "second-evidence", model=reverse)
    assert first.model_dump_json() == second.model_dump_json()


def test_serialized_classification_is_hash_seed_independent():
    script = (
        "from pathlib import Path\n"
        "from tempfile import mkdtemp\n"
        "from tests.state_classification.helpers import classify\n"
        "print(classify(Path(mkdtemp())).model_dump_json())\n")
    outputs = []
    for seed in ("1", "9173"):
        environment = dict(os.environ)
        environment.update({
            "PYTHONHASHSEED": seed,
            "PYTHONDONTWRITEBYTECODE": "1",
        })
        completed = subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(),
            env=environment, check=True, capture_output=True, text=True)
        outputs.append(completed.stdout)
    assert outputs[0] == outputs[1]


def test_authoritative_ledger_remains_pre_st_and_byte_membership_frozen():
    paths = tuple(sorted((DEMO_MODEL / "records").glob("*.json")))
    assert len(paths) == 32
    assert not any(path.name.startswith(("srg_", "std_", "stw_"))
                   for path in paths)
    loaded = ModelStore(DEMO_MODEL).load()
    assert loaded.revision.record_count == 32
    assert loaded.revision.revision_id == ACCEPTED_REVISION
