"""BH-001 Slice C dependency, non-write, and public-boundary isolation."""

import ast
import hashlib
import os
from pathlib import Path
import subprocess
import sys

from backend.model_kernel import ModelQueries, ModelStore


MODULES = tuple(sorted(Path("backend/behavior_evaluation").glob("*.py")))


def test_evaluator_owns_no_store_path_database_socket_or_write_capability():
    forbidden_imports = (
        "backend.model_kernel.store", "backend.identity_binding.store",
        "backend.temporal_state.store", "backend.source_interpretation.store",
        "backend.data_sources", "sqlite3", "pathlib", "socket",
    )
    for path in MODULES:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module or "")
        assert not any(name.startswith(forbidden_imports) for name in imports)
        assert "ModelStore" not in source
        assert "BindingStore" not in source
        assert "TemporalStore" not in source
        assert "InterpretationStore" not in source
        assert "open(" not in source
        assert ".write_" not in source


def test_kernel_has_no_upward_behavior_evaluator_import():
    lower_packages = (
        "system_identity", "model_kernel", "model_state",
        "observation_compatibility", "semantic_compatibility",
        "identity_binding", "temporal_state", "source_interpretation",
        "data_sources", "constraint_evaluation",
    )
    for package in lower_packages:
        for path in Path("backend", package).rglob("*.py"):
            assert "backend.behavior_evaluation" not in path.read_text(
                encoding="utf-8"), path


def test_cn_dependency_is_narrow_and_no_parser_is_reexported():
    init = Path("backend/behavior_evaluation/__init__.py").read_text(
        encoding="utf-8")
    derivation = Path("backend/behavior_evaluation/derivation.py").read_text(
        encoding="utf-8")
    assert "ConstraintEvaluationQueries" not in init + derivation
    assert "Constraint" not in derivation
    assert "parse_observed_decimal" in derivation
    assert '"parse_observed_decimal"' not in init
    assert '"CanonicalObservedDecimal"' not in init
    assert "from decimal import" not in derivation
    assert "Decimal(" not in derivation
    assert "float(" not in derivation
    assert "import re" not in derivation


def test_slice_d_fixture_is_exact_and_has_no_persisted_evaluation_artifact():
    records = tuple(Path("models/demo-printer/records").glob("*.json"))
    assert len(records) == 36
    assert sum(path.name.startswith("brg_") for path in records) == 1
    assert sum(path.name.startswith("bhd_") for path in records) == 1
    assert not any(path.name.startswith("bhw_") for path in records)
    assert not Path("artifacts/bh001").exists()
    loaded = ModelStore(Path("models/demo-printer")).load()
    assert loaded.revision.revision_id == (
        "mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee")
    vpa = Path(
        "models/demo-printer/records/"
        "vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49.json")
    assert hashlib.sha256(vpa.read_bytes()).hexdigest() == (
        "95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e")


def test_all_explicit_pre_bh_memberships_replay_structured_absence():
    from tests.model_kernel.test_demo_model import (
        CN001_MEMBERSHIP,
        PRE_CN001_MEMBERSHIP,
        PRE_ES001_MEMBERSHIP,
        PRE_SPECIFICATION_MEMBERSHIP,
        PRE_VARIABLE_MEMBERSHIP,
        PT001_MEMBERSHIP,
        VP001_MEMBERSHIP,
        VS001_MEMBERSHIP,
    )
    from tests.model_kernel.bh001_slice_a_helpers import BEHAVIOR_A

    memberships = (
        PRE_VARIABLE_MEMBERSHIP, PRE_SPECIFICATION_MEMBERSHIP,
        VS001_MEMBERSHIP, PRE_ES001_MEMBERSHIP, PRE_CN001_MEMBERSHIP,
        CN001_MEMBERSHIP, PT001_MEMBERSHIP, VP001_MEMBERSHIP,
    )
    assert tuple(map(len, memberships)) == (9, 10, 11, 14, 16, 18, 28, 29)
    store = ModelStore(Path("models/demo-printer"))
    for membership in memberships:
        loaded = store.replay(membership)
        assert loaded.revision.record_ids == tuple(sorted(membership))
        assert ModelQueries(loaded).behavior(BEHAVIOR_A).status == (
            "not_registered")


def test_serialized_output_is_hash_seed_independent():
    script = (
        "from pathlib import Path\n"
        "from tempfile import mkdtemp\n"
        "from tests.behavior_evaluation.helpers import evaluate\n"
        "print(evaluate(Path(mkdtemp())).model_dump_json())\n")
    outputs = []
    for seed in ("1", "9173"):
        environment = dict(os.environ)
        environment.update({"PYTHONHASHSEED": seed,
                            "PYTHONDONTWRITEBYTECODE": "1"})
        completed = subprocess.run(
            [sys.executable, "-c", script], cwd=Path.cwd(),
            env=environment, check=True, capture_output=True, text=True)
        outputs.append(completed.stdout)
    assert outputs[0] == outputs[1]
