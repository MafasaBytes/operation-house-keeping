"""BH-001 Slice C dependency, non-write, and public-boundary isolation."""

import ast
from pathlib import Path


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
    for path in Path("backend/model_kernel").glob("*.py"):
        assert "backend.behavior_evaluation" not in path.read_text(
            encoding="utf-8")


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


def test_slice_d_remains_absent_and_committed_demo_is_unchanged():
    records = tuple(Path("models/demo-printer/records").glob("*.json"))
    assert len(records) == 29
    assert not any(path.name.startswith(("brg_", "bhd_", "bhw_"))
                   for path in records)
    assert not Path("artifacts/bh001").exists()
