"""MK-001 isolation: AST-based import enforcement, no path-based store
access, stores-absent operation, and byte-for-byte non-writes to accepted
stores under the enforceable upstream boundary."""

import ast
import hashlib
import shutil
from pathlib import Path

import pytest

from backend.model_kernel.contracts import ModelIntegrityError
from backend.model_kernel.queries import ModelQueries
from backend.model_kernel.store import ModelStore

from tests.model_kernel.builders import (
    AS_BUILT,
    ENT_A,
    ENT_B,
    ENT_C,
    assertion,
    contains_type,
    containment_world,
    registration,
)

import backend.model_kernel as kernel_package

# anchored via the package itself, never the cwd (audit finding F4: a
# relative path from the wrong cwd silently globbed zero files)
KERNEL_DIR = Path(kernel_package.__file__).parent
FORBIDDEN_MODULES = ("backend.identity_binding", "backend.temporal_state",
                     "backend.data_sources",
    "backend.model_state",  # the kernel never imports the upper facade,
                     "backend.observation_compatibility")
ALLOWED_ROOTS = ("backend.system_identity", "backend.model_kernel", "pydantic")


def _kernel_sources():
    sources = sorted(KERNEL_DIR.glob("*.py"))
    assert len(sources) >= 6, "kernel sources not found — vacuous scan"
    return sources


class TestImportBoundary:
    def test_ast_imports_are_system_identity_stdlib_pydantic_only(self):
        """AST inspection, not raw text search: evidence discriminator
        literals such as 'identity_binding_record' are data, not
        dependencies."""
        import sys

        stdlib = sys.stdlib_module_names
        for source in _kernel_sources():
            tree = ast.parse(source.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [node.module or ""]
                for name in names:
                    root = name.split(".")[0]
                    assert not any(
                        name == banned or name.startswith(banned + ".")
                        for banned in FORBIDDEN_MODULES), (
                        f"{source.name} imports {name}")
                    assert (root in stdlib
                            or any(name == allowed
                                   or name.startswith(allowed + ".")
                                   for allowed in ALLOWED_ROOTS)), (
                        f"{source.name} imports unexpected module {name}")

    def test_no_path_based_store_access_in_runtime_source(self):
        for source in _kernel_sources():
            text = source.read_text(encoding="utf-8")
            for needle in ("bindings/", "raw_store", "temporal.db",
                           "var/raw", "evidence_root"):
                assert needle not in text, f"{needle!r} in {source.name}"

    def test_no_dynamic_import_escape_hatches(self):
        """The AST import scan cannot see importlib.import_module or
        __import__ — so their mere presence in kernel source is banned."""
        for source in _kernel_sources():
            tree = ast.parse(source.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    assert node.id != "__import__", source.name
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    names = ([alias.name for alias in node.names]
                             if isinstance(node, ast.Import)
                             else [node.module or ""])
                    assert "importlib" not in names, source.name


class TestStoresAbsent:
    def test_kernel_operates_identically_without_any_upstream_store(
        self, tmp_path, monkeypatch
    ):
        """The kernel must behave identically when binding, temporal, and
        evidence store roots simply do not exist: run from an empty cwd."""
        kind = contains_type()
        store = containment_world(tmp_path,
                                  assertion(kind, source=ENT_A, target=ENT_B))
        empty_world = tmp_path / "empty-world"
        empty_world.mkdir()
        monkeypatch.chdir(empty_world)
        assert not Path("bindings").exists()
        assert not Path("var").exists()
        loaded = store.load()
        result = ModelQueries(loaded).parents(ENT_B, "contains",
                                              view="as_built")
        assert result.status == "resolved"


def sweep(*roots: Path) -> dict[str, str]:
    hashes = {}
    for root in roots:
        assert root.exists(), f"sweep root missing: {root.name} (vacuous)"
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            hashes[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert hashes, "sweep found no files (vacuous)"
    return hashes


class TestUpstreamBoundary:
    def test_kernel_ops_write_nothing_outside_the_model_set(self, tmp_path):
        """Enforceable boundary (b)+(d): existing bindings/demo-printer
        records untouched byte-for-byte, and no binding set is read or
        written by runtime kernel operations — including failure paths."""
        accepted = [Path("bindings/demo-printer"),
                    Path("bindings/demo-printer-model")]
        before = sweep(*accepted)

        kind = contains_type()
        store = containment_world(tmp_path)
        store.append(assertion(kind, source=ENT_A, target=ENT_B))
        queries = ModelQueries(store.load())
        queries.parents(ENT_B, "contains", view="as_built")
        queries.descendants(ENT_A, "contains", view="as_built")
        store.replay(store.load().revision.record_ids)
        with pytest.raises(ModelIntegrityError):
            store.append(assertion(kind, source=ENT_A, target=ENT_C))
        with pytest.raises(ModelIntegrityError):
            store.replay(("rel_" + "9" * 64,))

        assert sweep(*accepted) == before

    def test_committed_demo_model_lives_under_models_only(self):
        model_files = list(Path("models/demo-printer/records").glob("*.json"))
        assert len(model_files) == 32
        assert all(p.name.split("_")[0] in (
            "reg", "rtd", "rel", "rwd", "vrg", "vsp", "vsm", "crg", "vcn",
            "prg", "pif", "pcn", "pcm", "ptw", "vpa", "vpw",
            "brg", "bhd", "bhw")
                   for p in model_files)
        # no anc_ records in the model ledger; no model records in bindings
        binding_files = list(
            Path("bindings/demo-printer-model/records").glob("*.json"))
        assert len(binding_files) == 5
        assert all(p.name.split("_")[0] in ("anc", "iba")
                   for p in binding_files)
