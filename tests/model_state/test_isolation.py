"""VM-001 architectural boundaries for backend/model_state: import rules,
no store construction, no sqlite3, no path literals, no private access to
injected objects — plus repo-level ledger-vocabulary sweeps."""

import ast
import json
import sys
from pathlib import Path

import backend.model_state as model_state_package

PACKAGE_DIR = Path(model_state_package.__file__).parent
ALLOWED_ROOTS = ("backend.system_identity", "backend.model_kernel",
                 "backend.identity_binding", "backend.temporal_state",
                 "backend.model_state", "pydantic")
FORBIDDEN_MODULES = ("backend.data_sources", "sqlite3",
                     "backend.observation_compatibility")
FORBIDDEN_CALLS = ("ModelStore", "BindingStore", "TemporalStore")


def sources():
    files = sorted(PACKAGE_DIR.glob("*.py"))
    assert len(files) >= 3  # never vacuous
    return [(path, ast.parse(path.read_text())) for path in files]


def imported_roots(tree):
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
            for module in imported_roots(tree):
                root = module.split(".")[0]
                assert not any(module == banned or module.startswith(
                    banned + ".") for banned in FORBIDDEN_MODULES), (
                    f"{path.name} imports forbidden {module}")
                assert (root in stdlib or any(
                    module == allowed or module.startswith(allowed + ".")
                    for allowed in ALLOWED_ROOTS)), (
                    f"{path.name} imports unexpected {module}")

    def test_no_dynamic_imports(self):
        for path, tree in sources():
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = getattr(node.func, "id", None)
                    assert name not in ("__import__", "import_module"), path

    def test_no_store_construction(self):
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
        """Correction 2: composition uses public APIs only — no
        underscore-attribute access except on self."""
        for path, tree in sources():
            for node in ast.walk(tree):
                if isinstance(node, ast.Attribute) and node.attr.startswith(
                        "_") and not node.attr.startswith("__"):
                    on_self = (isinstance(node.value, ast.Name)
                               and node.value.id == "self")
                    assert on_self, (
                        f"{path.name}: private access .{node.attr}")

    def test_no_device_vocabulary_in_contracts(self):
        for needle in ("moonraker", "klipper", "printer", "extruder",
                       "hotend"):
            for path, _ in sources():
                assert needle not in path.read_text().lower(), (
                    f"device word {needle!r} in {path.name}")


class TestLedgerVocabulary:
    """No source locator and no temporal value is persisted as model
    membership — swept over ALL committed model records (must see all 10,
    or the sweep is vacuous)."""

    def test_no_locator_or_value_vocabulary_in_model_ledger(self):
        records = sorted(Path("models/demo-printer/records").glob("*.json"))
        assert len(records) == 11
        for path in records:
            payload = json.loads(path.read_text())
            text = json.dumps(payload)
            for needle in ("source_id", "adapter_id", "json_pointer",
                           "extraction_route", "item_key", "value_json",
                           "received_at", "occurrence", "staleness",
                           "moonraker"):
                assert needle not in text, f"{needle!r} in {path.name}"


class TestLimitationWording:
    def test_latest_per_locator_limitation_stated_verbatim(self):
        def flat(path):
            return " ".join((PACKAGE_DIR / path).read_text().split())

        phrase = "no latest candidate observation attachable"
        assert phrase in flat("contracts.py")
        assert phrase in flat("README.md").replace("**", "")
        assert 'never "no observation ever"' in flat("contracts.py")
