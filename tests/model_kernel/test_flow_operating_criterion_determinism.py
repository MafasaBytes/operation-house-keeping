"""Permanent FC canonical/storage/index replay determinism regression."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from tests.model_kernel.fc001_slice_a_helpers import INDEX_NAMES
from tests.model_kernel.fc001_slice_a_reproduction import witness_bytes


def test_independent_public_store_worlds_and_five_hash_seeds():
    forward = witness_bytes()
    assert witness_bytes(reverse=True) == forward
    payload = json.loads(forward)
    rows = payload["collection_index_rows"]
    assert set(rows) == set(INDEX_NAMES)
    assert all(rows.values())
    assert rows == payload["loaded_index_rows"] == payload["replayed_index_rows"]
    assert len(rows["ids_by_subject"]) == 2
    assert len(rows["ids_by_effective_body"]) == 3
    assert len(rows["current_tips_by_root"]) == 4
    assert payload["canonical_records"] and payload["stored_records"]
    expected = hashlib.sha256(forward).hexdigest()
    script = (
        "import hashlib; "
        "from tests.model_kernel.fc001_slice_a_reproduction import witness_bytes; "
        "a = witness_bytes(); b = witness_bytes(reverse=True); "
        "assert a == b; print(hashlib.sha256(a).hexdigest())"
    )
    for seed in (0, 1, 7, 42, 12345):
        completed = subprocess.run(
            [sys.executable, "-c", script],
            cwd=Path(__file__).resolve().parents[2],
            env={**os.environ, "PYTHONHASHSEED": str(seed), "PYTHONDONTWRITEBYTECODE": "1"},
            capture_output=True, text=True, check=True, timeout=60)
        assert completed.stdout.strip() == expected, seed
        assert completed.stderr == "", seed
