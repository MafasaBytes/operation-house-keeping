"""VP-001 Slice C red baseline: exact public composition contract."""

import inspect
from typing import get_args

import backend.model_state as model_state


EXPECTED_STATUS = (
    "endpoint_not_admitted",
    "association_not_declared",
    "association_conflicted",
    "association_inactive",
    "associated",
)
EXPECTED_FIELDS = {
    "variable_anchor_id", "port_anchor_id", "context", "as_of", "status",
    "association", "variable_state",
}


def test_exact_slice_c_public_alias_result_fields_and_exports():
    alias = getattr(model_state, "AssociatedPortVariableStateStatus")
    result = getattr(model_state, "AssociatedPortVariableStateResult")
    assert get_args(alias) == EXPECTED_STATUS
    assert set(result.model_fields) == EXPECTED_FIELDS
    assert result.model_config["frozen"] is True
    assert result.model_config["extra"] == "forbid"
    assert {
        name for name in model_state.__all__ if "AssociatedPort" in name
    } == {
        "AssociatedPortVariableStateStatus",
        "AssociatedPortVariableStateResult",
    }


def test_exact_slice_c_method_signature_and_return_annotation():
    method = getattr(model_state.ModelStateQueries,
                     "associated_port_variable_state")
    signature = inspect.signature(method)
    assert tuple(signature.parameters) == (
        "self", "variable_anchor_id", "port_anchor_id", "context", "as_of",
        "entity_anchor_id", "source",
    )
    for name in ("context", "as_of", "entity_anchor_id", "source"):
        assert signature.parameters[name].kind is \
            inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["entity_anchor_id"].default is None
    assert signature.parameters["source"].default is None
    assert signature.return_annotation in {
        getattr(model_state, "AssociatedPortVariableStateResult"),
        "AssociatedPortVariableStateResult",
    }


def test_public_surface_forbids_state_at_port_and_implication_fields():
    result = getattr(model_state, "AssociatedPortVariableStateResult")
    forbidden = {
        "value", "port_value", "observation_at_port", "observed_at_port",
        "signal", "direction", "flow", "causality", "influence", "control",
        "compatibility", "health", "safety", "behavior", "current_operation",
        "temporal_revision", "model_as_of",
    }
    assert forbidden.isdisjoint(result.model_fields)
    assert not hasattr(model_state.ModelStateQueries, "port_variable_state")
    assert not hasattr(model_state.ModelStateQueries, "observed_at_port")
