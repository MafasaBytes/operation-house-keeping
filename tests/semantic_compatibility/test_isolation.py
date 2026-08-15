"""ES-001 composition and reverse-dependency boundaries."""

import ast
from pathlib import Path

PACKAGE = Path("backend/semantic_compatibility")


def trees():
    paths = sorted(PACKAGE.glob("*.py"))
    assert len(paths) == 3
    return [(path, ast.parse(path.read_text())) for path in paths]


def test_facade_has_no_store_write_path_or_repository_literal():
    forbidden_calls = {"ModelStore", "BindingStore", "TemporalStore",
                       "InterpretationStore", "open"}
    forbidden_text = ("models/", "bindings/", "interpretations/", "temporal.db",
                      "/home/", "/mnt/", "sqlite3")
    for path, tree in trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                name = (getattr(node.func, "id", None)
                        or getattr(node.func, "attr", None))
                assert name not in forbidden_calls
                assert name != "append"
        assert not any(needle in path.read_text() for needle in forbidden_text)


def test_forbidden_imports_and_private_foreign_access():
    forbidden = ("backend.data_sources", "backend.identity_binding",
                 "backend.structural_evidence", "sqlite3")
    for path, tree in trees():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not any(node.module == item or node.module.startswith(
                    item + ".") for item in forbidden), (path, node.module)
            if (isinstance(node, ast.Attribute) and node.attr.startswith("_")
                    and not node.attr.startswith("__")):
                assert isinstance(node.value, ast.Name) and node.value.id == "self"


def test_accepted_lower_layers_never_import_es001_upward():
    for root in ("backend/data_sources", "backend/temporal_state",
                 "backend/system_identity", "backend/identity_binding",
                 "backend/model_kernel", "backend/model_state",
                 "backend/observation_compatibility"):
        for path in Path(root).rglob("*.py"):
            text = path.read_text()
            assert "semantic_compatibility" not in text
            assert "source_interpretation" not in text
