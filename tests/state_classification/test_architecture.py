"""ST-001 Slice C import, capability, and non-inference boundaries."""

import ast
from pathlib import Path


MODULES = tuple(sorted(Path("backend/state_classification").glob("*.py")))


def test_classifier_owns_no_store_path_database_socket_or_write_capability():
    forbidden_imports = (
        "backend.model_kernel.store", "backend.identity_binding.store",
        "backend.temporal_state.store", "backend.source_interpretation.store",
        "backend.data_sources", "sqlite3", "pathlib", "socket",
    )
    forbidden_names = (
        "ModelStore", "BindingStore", "TemporalStore", "InterpretationStore",
        "open(", ".write_", "parse_observed_decimal", "Decimal(", "float(",
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
        assert not any(name in source for name in forbidden_names)


def test_lower_layers_never_import_state_classification():
    lower_packages = (
        "system_identity", "model_kernel", "model_state",
        "observation_compatibility", "semantic_compatibility",
        "identity_binding", "temporal_state", "source_interpretation",
        "data_sources", "constraint_evaluation", "behavior_evaluation",
    )
    for package in lower_packages:
        for path in Path("backend", package).rglob("*.py"):
            assert "backend.state_classification" not in path.read_text(
                encoding="utf-8"), path


def test_only_public_lower_facades_and_legal_model_chain_are_used():
    facade = Path("backend/state_classification/facade.py").read_text(
        encoding="utf-8")
    derivation = Path("backend/state_classification/derivation.py").read_text(
        encoding="utf-8")
    assert "self.constraints.semantic.compatibility.state.model" in facade
    assert "ModelQueries(model)" in facade
    assert "ConstraintEvaluationQueries" in facade
    assert "constraint_evaluation(" in facade
    assert "._model" not in facade + derivation
    assert "._store" not in facade + derivation
    assert "derive_candidate_evaluation" not in facade + derivation
    assert "parse_observed_decimal" not in facade + derivation


def test_no_transition_or_aggregate_current_state_vocabulary():
    import backend.state_classification as classification

    forbidden = (
        "state_transition", "from_state", "to_state", "trigger", "guard",
        "matched_state_anchor_ids", "current_state", "rank", "priority",
        "recommended_action", "state_family", "state_space",
    )
    public_names = set(classification.__all__)
    public_fields = set(classification.StateClassificationResult.model_fields)
    public_fields.update(
        classification.StateClassificationConditionResult.model_fields)
    assert not public_names.intersection(forbidden)
    assert not public_fields.intersection(forbidden)
