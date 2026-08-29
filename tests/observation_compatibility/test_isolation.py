"""VS-001 architectural boundaries for backend/observation_compatibility.

Written and failing before the facade exists, so the bans are not shaped
to fit the implementation."""

import ast
import json
import sys
from pathlib import Path

import backend.observation_compatibility as package

PACKAGE_DIR = Path(package.__file__).parent
ALLOWED_ROOTS = ("backend.system_identity", "backend.model_kernel",
                 "backend.model_state", "backend.temporal_state",
                 "backend.observation_compatibility", "pydantic")
FORBIDDEN_MODULES = ("backend.data_sources", "backend.identity_binding",
                     "backend.source_interpretation",
                     "backend.semantic_compatibility", "sqlite3")
FORBIDDEN_CALLS = ("ModelStore", "BindingStore", "TemporalStore")


def sources():
    files = sorted(PACKAGE_DIR.glob("*.py"))
    assert len(files) >= 3  # never vacuous
    return [(path, ast.parse(path.read_text())) for path in files]


def imported_modules(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name
        elif isinstance(node, ast.ImportFrom) and node.module:
            yield node.module


class TestImportBoundary:
    def test_only_allowed_roots(self):
        stdlib = set(sys.stdlib_module_names)
        for path, tree in sources():
            for module in imported_modules(tree):
                assert not any(module == banned or module.startswith(
                    banned + ".") for banned in FORBIDDEN_MODULES), (
                    f"{path.name} imports forbidden {module}")
                assert (module.split(".")[0] in stdlib or any(
                    module == allowed or module.startswith(allowed + ".")
                    for allowed in ALLOWED_ROOTS)), (
                    f"{path.name} imports unexpected {module}")

    def test_no_dynamic_imports(self):
        for path, tree in sources():
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    assert getattr(node.func, "id", None) not in (
                        "__import__", "import_module"), path.name

    def test_no_store_construction(self):
        """ModelQueries is deliberately permitted — it is the composition
        seam. Constructing a STORE never is."""
        for path, tree in sources():
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = (getattr(node.func, "id", None)
                            or getattr(node.func, "attr", None))
                    assert name not in FORBIDDEN_CALLS, (
                        f"{path.name} constructs {name}")

    def test_no_path_literals(self):
        needles = ("models/", "bindings/", "temporal.db", "var/raw",
                   "evidence_root", "/home/", "/mnt/")
        for path, _ in sources():
            text = path.read_text()
            for needle in needles:
                assert needle not in text, f"{needle!r} in {path.name}"

    def test_no_private_access_to_foreign_objects(self):
        for path, tree in sources():
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr.startswith(
                        "_") and not node.attr.startswith("__"):
                    on_self = (isinstance(node.value, ast.Name)
                               and node.value.id == "self")
                    assert on_self, f"{path.name}: private access .{node.attr}"

    def test_no_device_vocabulary(self):
        for needle in ("moonraker", "klipper", "printer", "extruder",
                       "hotend", "celsius"):
            for path, _ in sources():
                assert needle not in path.read_text().lower(), (
                    f"device/unit word {needle!r} in {path.name}")

    def test_no_float_conversion_of_evidence(self):
        """float() on a parsed value is the crash surface: 1E+999 becomes
        inf and a 400-digit integer raises OverflowError, which is not a
        ValueError and would escape untyped."""
        for path, tree in sources():
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    assert getattr(node.func, "id", None) != "float", (
                        f"{path.name} converts evidence with float()")


class TestReverseBoundaries:
    def test_lower_layers_never_import_the_facade(self):
        for module in ("backend/model_kernel", "backend/model_state",
                       "backend/identity_binding", "backend/temporal_state"):
            for path in Path(module).rglob("*.py"):
                assert "observation_compatibility" not in path.read_text(), (
                    f"{path} imports upward")

    def test_kernel_isolation_forbids_the_facade(self):
        from tests.model_kernel import test_isolation as kernel_isolation

        assert "backend.observation_compatibility" in (
            kernel_isolation.FORBIDDEN_MODULES)

    def test_model_state_isolation_forbids_the_facade(self):
        from tests.model_state import test_isolation as state_isolation

        assert "backend.observation_compatibility" in (
            state_isolation.FORBIDDEN_MODULES)


class TestLedgerVocabulary:
    """The kernel gained a unit code; it must still contain no source
    locator and no observed value."""

    def test_committed_model_ledger_has_no_source_or_value_vocabulary(self):
        records = sorted(Path("models/demo-printer/records").glob("*.json"))
        assert len(records) == 29
        for path in records:
            text = json.dumps(json.loads(path.read_text()))
            for needle in ("source_id", "adapter_id", "json_pointer",
                           "extraction_route", "item_key", "value_json",
                           "received_at", "occurrence", "staleness",
                           "moonraker", "declared_unit"):
                assert needle not in text, f"{needle!r} in {path.name}"

    def test_the_specification_record_declares_only_model_intent(self):
        path = next(Path("models/demo-printer/records").glob("vsp_*.json"))
        payload = json.loads(path.read_text())
        assert set(payload["unit"]["unit"]) == {
            "system_id", "system_edition", "code"}
        assert "display_symbol" not in json.dumps(payload)
