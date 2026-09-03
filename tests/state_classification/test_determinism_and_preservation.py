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
    "mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee")


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


def test_authoritative_ledger_is_the_approved_st_append():
    paths = tuple(sorted((DEMO_MODEL / "records").glob("*.json")))
    assert len(paths) == 36
    assert sum(path.name.startswith("srg_") for path in paths) == 1
    assert sum(path.name.startswith("std_") for path in paths) == 1
    assert not any(path.name.startswith("stw_") for path in paths)
    loaded = ModelStore(DEMO_MODEL).load()
    assert loaded.revision.record_count == 36
    assert loaded.revision.revision_id == ACCEPTED_REVISION
