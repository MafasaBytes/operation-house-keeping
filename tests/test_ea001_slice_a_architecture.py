"""Architecture boundaries for the two EA-001 Slice A lower seams."""

import ast
from pathlib import Path

import backend.data_sources.contracts.operational_evidence as source_contracts
import backend.data_sources.evidence as source_evidence


SOURCE_FILES = (
    Path("backend/data_sources/contracts/operational_evidence.py"),
    Path("backend/data_sources/evidence/operational_api.py"),
)
TEMPORAL_FILES = (
    Path("backend/temporal_state/contracts.py"),
    Path("backend/temporal_state/queries.py"),
)
FORBIDDEN = {
    "backend.identity_binding", "backend.source_interpretation",
    "backend.model_kernel", "backend.model_state",
    "backend.observation_compatibility", "backend.semantic_compatibility",
    "backend.constraint_evaluation", "backend.behavior_evaluation",
    "backend.state_classification", "backend.evidence_assurance",
}


def _imports(path):
    tree = ast.parse(path.read_text("utf-8"), filename=str(path))
    found = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module)
    return found


def test_lower_seams_have_no_forbidden_imports():
    for path in SOURCE_FILES + TEMPORAL_FILES:
        imports = _imports(path)
        assert not {name for name in imports
                    if any(name == root or name.startswith(root + ".")
                           for root in FORBIDDEN)}, path


def test_data_sources_does_not_import_temporal_state():
    for path in SOURCE_FILES:
        assert not any(name == "backend.temporal_state" or
                       name.startswith("backend.temporal_state.")
                       for name in _imports(path))


def test_authorized_slice_b_package_is_a_sibling_of_lower_seams():
    assert (Path("backend/evidence_assurance") / "__init__.py").is_file()
    for path in SOURCE_FILES + TEMPORAL_FILES:
        assert "backend.evidence_assurance" not in _imports(path)


def test_source_reader_has_no_network_or_write_dependencies():
    imports = set().union(*(_imports(path) for path in SOURCE_FILES))
    forbidden = {"socket", "urllib", "http", "requests", "subprocess"}
    assert not {name for name in imports if name.split(".")[0] in forbidden}
    source = Path("backend/data_sources/evidence/operational_api.py").read_text("utf-8")
    for operation in ("put_payload(", "put_attempt(", "put_envelope(",
                      "put_extraction(", "put_quarantine(", "write_bytes(",
                      "write_text("):
        assert operation not in source


def test_slice_a_source_exports_are_exact_and_bounded():
    assert source_contracts.__all__ == [
        "Ds004OperationalEvidenceMaterial",
        "Ds004OperationalEvidenceScope",
        "OperationalApiArtifactDescriptor",
        "OperationalApiArtifactKind",
        "OperationalApiInventoryToken",
        "OperationalEvidenceReadError",
    ]
    assert source_evidence.__all__ == [
        "Ds004OperationalEvidenceReader",
        "FilesystemDs004OperationalEvidenceReader",
    ]
