"""ST-002 Slice B red-first public surface and authoritative absence gates."""

import inspect
import json
from pathlib import Path
import typing

import pytest

import backend.model_kernel as kernel
from tests.model_kernel.test_demo_model import (
    BH001_MEMBERSHIP,
    CN001_MEMBERSHIP,
    CURRENT_REVISION,
    FL001_MEMBERSHIP,
    GOLDEN_REVISION,
    PRE_BH001_REVISION,
    PRE_CN001_MEMBERSHIP,
    PRE_CN001_REVISION,
    PRE_ES001_MEMBERSHIP,
    PRE_ES001_REVISION,
    PRE_PT001_REVISION,
    PRE_SPECIFICATION_MEMBERSHIP,
    PRE_SPECIFICATION_REVISION,
    PRE_ST001_REVISION,
    PRE_FL001_REVISION,
    PRE_VARIABLE_MEMBERSHIP,
    PRE_VARIABLE_REVISION,
    PRE_VP001_REVISION,
    PT001_MEMBERSHIP,
    ST001_MEMBERSHIP,
    VP001_MEMBERSHIP,
    VS001_MEMBERSHIP,
)


DEMO_MODEL = Path("models/demo-printer")
ABSENT_TRANSITION = "trn_" + "0" * 32
ABSENT_RECORDS = tuple(prefix + "_" + "0" * 64
                       for prefix in ("trg", "trd", "trw"))
ENTITY = "ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50"
CONTEXT = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_operated")


EXPECTED_METHODS = {
    "ancestors", "behavior", "behavior_assertion", "behavior_declaration",
    "behaviors_involving_variable", "children", "connections_containing",
    "connections_exact", "connections_of_port", "constraint_declaration",
    "constraints_of_variable", "descendants", "entity", "hierarchy_health",
    "interface_compatibility", "parents", "port", "port_assertion",
    "port_interface", "ports_associated_with_variable", "ports_of_entity",
    "relationships", "state", "state_assertion", "state_declaration",
    "states_of_entity", "transition", "transition_assertion",
    "transition_declaration", "transitions_of_entity", "flow",
    "flow_assertion", "flow_declaration", "flows_involving_port", "variable",
    "variable_port_assertion", "variable_port_association",
    "variable_semantics", "variable_value_specification",
    "variables_associated_with_port", "variables_of",
    "flow_measurement_association",
    "flow_measurement_associations_for_flow",
    "flow_measurement_associations_for_variable",
    "flow_measurement_associations_at_port", "flow_measurement_assertion",
}


def public_methods():
    return {
        name for name, value in vars(kernel.ModelQueries).items()
        if not name.startswith("_") and callable(value)
    }


def without_material(result):
    return result.model_dump(mode="python", exclude={"material"})


def test_exactly_four_transition_methods_and_signatures_are_public():
    assert public_methods() == EXPECTED_METHODS
    expected = {
        "transition": (("self", "transition_anchor_id"),
                       kernel.TransitionLookupResult),
        "transition_declaration": (
            ("self", "transition_anchor_id", "context"),
            kernel.TransitionDeclarationResult),
        "transitions_of_entity": (
            ("self", "entity_anchor_id", "context"),
            kernel.EntityTransitionsResult),
        "transition_assertion": (
            ("self", "record_id"),
            kernel.TransitionAssertionDisclosureResult),
    }
    for name, (parameters, return_annotation) in expected.items():
        signature = inspect.signature(getattr(kernel.ModelQueries, name))
        assert tuple(signature.parameters) == parameters
        assert signature.return_annotation is return_annotation
        if "context" in parameters:
            assert signature.parameters["context"].kind is \
                inspect.Parameter.KEYWORD_ONLY
            assert signature.parameters["context"].default is \
                inspect.Parameter.empty
    for forbidden in (
        "current_transition", "detect_transition", "assess_transition",
        "possible_transitions", "enabled_transitions", "next_state",
        "transitions_from_state", "transition_path", "transition_history",
        "transition_assessment", "transition_occurrence",
    ):
        assert forbidden not in public_methods()


def test_exact_transition_literals_are_public_in_normative_order():
    expected = {
        "TransitionLookupStatus": ("not_registered", "registered"),
        "TransitionDeclarationConclusion": (
            "not_registered", "not_declared", "declared", "conflicted",
            "inactive"),
        "TransitionDeclarationLineageSummary": (
            "not_applicable", "healthy", "conflicted", "inactive"),
        "TransitionAgreementFinding": (
            "one_healthy_root", "corroborating_healthy_roots",
            "same_root_conflict", "cross_root_effective_body_disagreement",
            "inactive_roots_present"),
        "TransitionEndpointRole": ("from", "to"),
        "TransitionEndpointPinAlignment": (
            "exact_current", "pinned_declaration_superseded",
            "pinned_declaration_withdrawn", "endpoint_state_conflicted",
            "endpoint_state_inactive"),
        "EntityTransitionsStatus": (
            "entity_not_registered", "registered"),
        "TransitionAssertionLookupStatus": ("not_found", "found"),
    }
    for name, literals in expected.items():
        value = getattr(kernel, name)
        assert typing.get_args(value) == literals
        assert name in kernel.__all__


def test_exact_transition_result_field_order_and_exports():
    assert len(kernel.__all__) == 227
    expected = {
        "TransitionEndpointResult": (
            "role", "state_anchor_id", "state_registration_index",
            "declaration_index", "state_declaration_conclusion",
            "pinned_declaration_activity", "alignment"),
        "TransitionEffectiveBodyGroupResult": (
            "group_index", "representative_declaration_index",
            "current_tip_indices", "root_record_indices", "from_endpoint",
            "to_endpoint"),
        "TransitionDeclarationRootResult": (
            "root_record_index", "lineage_record_indices",
            "current_tip_indices", "withdrawal_indices", "lineage_health",
            "effective_body_group_indices"),
        "TransitionLookupResult": (
            "material", "transition_anchor_id", "status",
            "registration_index", "subject_entity_registration_index",
            "from_state_registration_index", "to_state_registration_index"),
        "TransitionDeclarationResult": (
            "material", "transition_anchor_id", "context", "conclusion",
            "lineage_summary", "agreement_findings", "registration_index",
            "roots", "effective_body_groups", "current_declaration_indices"),
        "EntityTransitionEntry": (
            "entry_index", "transition_anchor_id",
            "transition_registration_index", "conclusion",
            "lineage_summary", "agreement_findings", "roots",
            "effective_body_groups", "current_declaration_indices"),
        "EntityTransitionsResult": (
            "material", "entity_anchor_id", "context", "status",
            "entity_registration_index", "entries"),
        "TransitionAssertionDisclosureResult": (
            "material", "record_id", "lookup_status", "record_index",
            "activity", "containing_lineage_health",
            "containing_subject_conclusion",
            "containing_agreement_findings", "root_record_index",
            "successor_indices", "withdrawal_indices"),
    }
    for name, fields in expected.items():
        contract = getattr(kernel, name)
        assert tuple(contract.model_fields) == fields
        assert name in kernel.__all__
    endpoint = kernel.TransitionEndpointResult.model_fields
    root = kernel.TransitionDeclarationRootResult.model_fields
    assert typing.get_args(endpoint["pinned_declaration_activity"].annotation) \
        == typing.get_args(kernel.AssertionActivity)
    assert typing.get_args(root["lineage_health"].annotation) == \
        typing.get_args(kernel.ContainingLineageHealth)


def test_rc5_all_four_query_families_have_exact_36_record_absence():
    loaded = kernel.ModelStore(DEMO_MODEL).load()
    queries = kernel.ModelQueries(loaded)
    lookup = queries.transition(ABSENT_TRANSITION)
    assert without_material(lookup) == {
        "transition_anchor_id": ABSENT_TRANSITION,
        "status": "not_registered",
        "registration_index": None,
        "subject_entity_registration_index": None,
        "from_state_registration_index": None,
        "to_state_registration_index": None,
    }
    declaration = queries.transition_declaration(
        ABSENT_TRANSITION, context=CONTEXT)
    assert without_material(declaration) == {
        "transition_anchor_id": ABSENT_TRANSITION,
        "context": CONTEXT.model_dump(mode="python"),
        "conclusion": "not_registered",
        "lineage_summary": "not_applicable",
        "agreement_findings": (),
        "registration_index": None,
        "roots": (),
        "effective_body_groups": (),
        "current_declaration_indices": (),
    }
    collection = queries.transitions_of_entity(ENTITY, context=CONTEXT)
    assert without_material(collection) == {
        "entity_anchor_id": ENTITY,
        "context": CONTEXT.model_dump(mode="python"),
        "status": "registered",
        "entity_registration_index": 16,
        "entries": (),
    }
    for record_id in ABSENT_RECORDS:
        result = queries.transition_assertion(record_id)
        assert without_material(result) == {
            "record_id": record_id,
            "lookup_status": "not_found",
            "record_index": None,
            "activity": None,
            "containing_lineage_health": None,
            "containing_subject_conclusion": None,
            "containing_agreement_findings": None,
            "root_record_index": None,
            "successor_indices": (),
            "withdrawal_indices": (),
        }
    for result in (lookup, declaration, collection):
        assert result.material.revision.revision_id == CURRENT_REVISION
        assert result.material.revision.record_count == 36
        assert len(result.material.records) == 36


def test_carry_once_serialization_for_authoritative_absence():
    result = kernel.ModelQueries(kernel.ModelStore(DEMO_MODEL).load()
                                 ).transition_declaration(
                                     ABSENT_TRANSITION, context=CONTEXT)
    decoded = json.loads(result.model_dump_json())
    assert list(decoded).count("material") == 1
    assert len(decoded["material"]["records"]) == 36
    assert "material" not in json.dumps({
        "roots": decoded["roots"],
        "groups": decoded["effective_body_groups"],
    })


def test_historical_memberships_preserve_exact_absence_and_revisions():
    cases = (
        (PRE_VARIABLE_MEMBERSHIP, PRE_VARIABLE_REVISION, 9),
        (PRE_SPECIFICATION_MEMBERSHIP, PRE_SPECIFICATION_REVISION, 10),
        (VS001_MEMBERSHIP, GOLDEN_REVISION, 11),
        (PRE_ES001_MEMBERSHIP, PRE_ES001_REVISION, 14),
        (PRE_CN001_MEMBERSHIP, PRE_CN001_REVISION, 16),
        (CN001_MEMBERSHIP, PRE_PT001_REVISION, 18),
        (PT001_MEMBERSHIP, PRE_VP001_REVISION, 28),
        (VP001_MEMBERSHIP, PRE_BH001_REVISION, 29),
        (BH001_MEMBERSHIP, PRE_ST001_REVISION, 32),
        (ST001_MEMBERSHIP, PRE_FL001_REVISION, 34),
        (FL001_MEMBERSHIP, CURRENT_REVISION, 36),
    )
    store = kernel.ModelStore(DEMO_MODEL)
    for membership, revision, count in cases:
        loaded = store.replay(membership)
        queries = kernel.ModelQueries(loaded)
        assert loaded.revision.revision_id == revision
        assert loaded.revision.record_count == count
        assert queries.transition(ABSENT_TRANSITION).status == "not_registered"
        assert queries.transition_declaration(
            ABSENT_TRANSITION, context=CONTEXT).conclusion == "not_registered"
        assert queries.transitions_of_entity(
            ENTITY, context=CONTEXT).entries == ()
        for record_id in ABSENT_RECORDS:
            assert queries.transition_assertion(
                record_id).lookup_status == "not_found"


@pytest.mark.parametrize("method,args", [
    ("transition", ("bad",)),
    ("transition_declaration", ("bad",)),
    ("transitions_of_entity", ("bad",)),
    ("transition_assertion", ("std_" + "0" * 64,)),
])
def test_query_boundaries_reject_malformed_or_wrong_family_ids(method, args):
    query = getattr(kernel.ModelQueries(kernel.ModelStore(DEMO_MODEL).load()),
                    method)
    kwargs = {"context": CONTEXT} if method in {
        "transition_declaration", "transitions_of_entity"} else {}
    with pytest.raises(kernel.ModelQueryError):
        query(*args, **kwargs)
