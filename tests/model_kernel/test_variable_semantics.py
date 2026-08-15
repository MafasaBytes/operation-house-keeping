"""ES-001 Group 4: model-side engineering meaning."""

from backend.model_kernel import (
    ModelQueries,
    ObservationRoleDeclaration,
    ObservationRoleReference,
    OwnerDeclarationEvidence,
    QuantityKindDeclaration,
    QuantityKindReference,
    VariableSemanticDeclaration,
    build_record,
)
from tests.model_kernel.builders import (
    AUTHORITY, ENT_A, T0, VAR_A, registration, store_with,
    variable_registration,
)


def meaning(dimension="quantity_kind", supersedes=(), variable=VAR_A):
    declaration = (
        QuantityKindDeclaration(
            dimension="quantity_kind",
            quantity_kind=QuantityKindReference(
                system_id="project_local", system_edition="ohk-quantities-1",
                code="temperature"))
        if dimension == "quantity_kind" else
        ObservationRoleDeclaration(
            dimension="observation_role",
            observation_role=ObservationRoleReference(
                system_id="project_local",
                system_edition="ohk-observation-roles-1",
                code="measured_actual")))
    return build_record(
        VariableSemanticDeclaration, variable_anchor_id=variable,
        declaration=declaration,
        evidence=(OwnerDeclarationEvidence(
            kind="owner_declaration", statement="synthetic meaning"),),
        supersedes=supersedes, recorded_at=T0, authority=AUTHORITY)


def world(tmp_path, *records):
    return store_with(tmp_path, registration(ENT_A),
                      variable_registration(), *records)


def test_each_dimension_is_independent_and_queryable(tmp_path):
    quantity = meaning()
    role = meaning("observation_role")
    result = ModelQueries(world(tmp_path, quantity, role).load()).variable_semantics(VAR_A)
    assert result.quantity_kind.status == "declared"
    assert result.quantity_kind.declaration == quantity
    assert result.observation_role.status == "declared"
    assert result.observation_role.declaration == role


def test_missing_and_unregistered_are_distinct(tmp_path):
    queries = ModelQueries(world(tmp_path).load())
    result = queries.variable_semantics(VAR_A)
    assert (result.quantity_kind.status, result.observation_role.status) == (
        "not_declared", "not_declared")
    absent = queries.variable_semantics("var_" + "9" * 32)
    assert (absent.quantity_kind.status, absent.observation_role.status) == (
        "not_registered", "not_registered")


def test_multi_parent_convergence_and_membership_relative_replay(tmp_path):
    first = meaning()
    left = meaning(supersedes=(first.record_id,))
    right = meaning(supersedes=(first.record_id,))
    # make the bodies genuinely distinct while retaining the dimension
    right = build_record(
        VariableSemanticDeclaration, variable_anchor_id=VAR_A,
        declaration=QuantityKindDeclaration(
            dimension="quantity_kind",
            quantity_kind=QuantityKindReference(
                system_id="project_local", system_edition="ohk-quantities-1",
                code="temperature_alternative")),
        evidence=right.evidence, supersedes=right.supersedes,
        recorded_at=T0, authority=AUTHORITY)
    converged = meaning(supersedes=(left.record_id, right.record_id))
    store = world(tmp_path, first, left, right, converged)
    current = ModelQueries(store.load()).variable_semantics(VAR_A)
    assert current.quantity_kind.status == "declared"
    assert current.quantity_kind.declaration == converged
    replay = store.replay((registration(ENT_A).record_id,
                           variable_registration().record_id,
                           first.record_id, left.record_id, right.record_id))
    conflict = ModelQueries(replay).variable_semantics(VAR_A).quantity_kind
    assert conflict.status == "conflicted"
    assert tuple(r.record_id for r in conflict.conflicting_declarations) == tuple(
        sorted((left.record_id, right.record_id)))
