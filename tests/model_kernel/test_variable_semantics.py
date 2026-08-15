"""ES-001 Group 4: model-side engineering meaning."""

import json
from datetime import UTC, datetime, timedelta, tzinfo

import pytest
from pydantic import ValidationError

from backend.model_kernel import (
    ModelQueries,
    ModelKernelError,
    ModelRecordEvidence,
    ModelStore,
    ObservationRoleDeclaration,
    ObservationRoleReference,
    OwnerDeclarationEvidence,
    QuantityKindDeclaration,
    QuantityKindReference,
    VariableSemanticDeclaration,
    VariableSemanticsResult,
    VariableValueSpecification,
    build_record,
)
from backend.model_kernel.canonical import canonical_payload
from backend.model_kernel.contracts import SemanticDimensionResult
from backend.model_kernel.store import validate_record_collection
from tests.model_kernel.builders import (
    AUTHORITY, ENT_A, T0, VAR_A, VAR_B, contains_type, registration,
    specification, store_with, variable_registration, withdrawal, assertion,
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


def snapshot(store):
    return {path.name: path.read_bytes()
            for path in sorted(store.records_dir.iterdir())}


def test_semantic_declaration_requires_registration_at_every_boundary(tmp_path):
    record = meaning()
    store = store_with(tmp_path, registration(ENT_A))
    before = snapshot(store)
    with pytest.raises(ModelKernelError, match="unregistered variable") as error:
        store.append(record)
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"
    assert snapshot(store) == before

    crafted = ModelStore(tmp_path / "crafted")
    for item in (registration(ENT_A), record):
        (crafted.records_dir / f"{item.record_id}.json").write_text(
            json.dumps({**canonical_payload(item), "record_id": item.record_id},
                       sort_keys=True, indent=2) + "\n")
    with pytest.raises(ModelKernelError) as error:
        crafted.load()
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    complete = world(tmp_path / "replay", record)
    with pytest.raises(ModelKernelError) as error:
        complete.replay((registration(ENT_A).record_id, record.record_id))
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"


def test_parent_validation_is_typed_and_dimension_scoped(tmp_path):
    parent = meaning()
    missing = meaning(supersedes=("vsm_" + "f" * 64,))
    with pytest.raises(ModelKernelError) as error:
        world(tmp_path / "missing", missing)
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"

    cross_variable = meaning(variable=VAR_B, supersedes=(parent.record_id,))
    with pytest.raises(ModelKernelError) as error:
        store_with(tmp_path / "variable", registration(ENT_A),
                   variable_registration(), variable_registration(VAR_B),
                   parent, cross_variable)
    assert error.value.error_code == "MODEL_SEMANTIC_LINEAGE_INVALID"

    cross_dimension = meaning("observation_role",
                              supersedes=(parent.record_id,))
    with pytest.raises(ModelKernelError) as error:
        world(tmp_path / "dimension", parent, cross_dimension)
    assert error.value.error_code == "MODEL_SEMANTIC_LINEAGE_INVALID"

    forged = VariableSemanticDeclaration.model_construct(
        **{**parent.model_dump(), "supersedes": (parent.record_id,)})
    with pytest.raises(ModelKernelError) as error:
        world(tmp_path / "self").append(forged)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def test_crafted_semantic_cycle_is_rejected_by_dag_guard():
    first = meaning()
    second = meaning(supersedes=(first.record_id,))
    cyclic_first = VariableSemanticDeclaration.model_construct(
        **{**first.model_dump(), "supersedes": (second.record_id,)})
    records = {r.record_id: r for r in (
        registration(ENT_A), variable_registration(), cyclic_first, second)}
    with pytest.raises(ModelKernelError, match="supersession cycle") as error:
        validate_record_collection("demo-printer", records, verify_hashes=False)
    assert error.value.error_code == "MODEL_SEMANTIC_LINEAGE_INVALID"


def test_independent_tips_conflict_and_history_is_per_dimension_and_variable(tmp_path):
    first = meaning()
    second = build_record(
        VariableSemanticDeclaration, variable_anchor_id=VAR_A,
        declaration=QuantityKindDeclaration(
            dimension="quantity_kind", quantity_kind=QuantityKindReference(
                system_id="project_local", system_edition="ohk-quantities-1",
                code="pressure")), evidence=first.evidence, recorded_at=T0,
        authority=AUTHORITY)
    role_old = meaning("observation_role")
    role_new = meaning("observation_role", supersedes=(role_old.record_id,))
    other_old = meaning(variable=VAR_B)
    other_new = meaning(variable=VAR_B, supersedes=(other_old.record_id,))
    store = store_with(tmp_path, registration(ENT_A), variable_registration(),
                       variable_registration(VAR_B), first, second, role_old,
                       role_new, other_old, other_new)
    result = ModelQueries(store.load()).variable_semantics(VAR_A)
    assert result.quantity_kind.status == "conflicted"
    assert result.quantity_kind.declaration is None
    assert result.quantity_kind.conflicting_declarations == tuple(
        sorted((first, second), key=lambda record: record.record_id))
    assert result.quantity_kind.superseded_declaration_ids == ()
    assert result.observation_role.superseded_declaration_ids == (
        role_old.record_id,)


def test_conflict_is_independent_of_append_order_time_and_authority(tmp_path):
    from backend.model_kernel import AuthorityRef

    early = meaning()
    late = build_record(
        VariableSemanticDeclaration, variable_anchor_id=VAR_A,
        declaration=QuantityKindDeclaration(
            dimension="quantity_kind", quantity_kind=QuantityKindReference(
                system_id="project_local", system_edition="ohk-quantities-1",
                code="pressure")), evidence=early.evidence,
        recorded_at=datetime(2027, 1, 1, tzinfo=UTC),
        authority=AuthorityRef(kind="human_owner", agent="owner",
                               method="manual_declaration"))
    forward = ModelQueries(world(tmp_path / "a", early, late).load())
    backward = ModelQueries(world(tmp_path / "b", late, early).load())
    assert forward.variable_semantics(VAR_A) == backward.variable_semantics(VAR_A)


def test_partial_and_repeated_convergence_remain_honest(tmp_path):
    a = meaning()
    b = build_record(VariableSemanticDeclaration, **{
        **canonical_payload(meaning()),
        "declaration": QuantityKindDeclaration(
            dimension="quantity_kind", quantity_kind=QuantityKindReference(
                system_id="project_local", system_edition="ohk-quantities-1",
                code="pressure"))})
    partial = meaning(supersedes=(a.record_id,))
    assert len(ModelQueries(world(tmp_path / "partial", a, b, partial).load())
               .variable_semantics(VAR_A).quantity_kind.conflicting_declarations) == 2
    merge_a = meaning(supersedes=(a.record_id, b.record_id))
    merge_b = build_record(VariableSemanticDeclaration,
        variable_anchor_id=VAR_A, declaration=merge_a.declaration,
        evidence=merge_a.evidence, supersedes=merge_a.supersedes,
        recorded_at=T0, authority=AUTHORITY, note="other merge")
    store = world(tmp_path / "repeat", a, b, merge_a, merge_b)
    assert ModelQueries(store.load()).variable_semantics(
        VAR_A).quantity_kind.status == "conflicted"
    final = meaning(supersedes=(merge_a.record_id, merge_b.record_id))
    store.append(final)
    assert ModelQueries(store.load()).variable_semantics(
        VAR_A).quantity_kind.declaration == final


@pytest.mark.parametrize("bad", ["", "Temperature", " temperature", "temp erature",
                                  "temperature.*", "temperature\n"])
def test_semantic_identity_tokens_have_behavioral_closed_grammar(bad):
    with pytest.raises(ValidationError):
        QuantityKindReference(system_id="project_local",
                              system_edition="ohk-quantities-1", code=bad)
    with pytest.raises(ValidationError):
        ObservationRoleReference(system_id="project_local",
                                 system_edition="ohk-roles-1", code=bad)


def test_semantic_record_forbids_source_vocabulary_fields():
    record = meaning()
    for field, value in (("source_id", "printer-1"),
                         ("adapter_id", "moonraker"),
                         ("json_pointer", "/temperature"),
                         ("declared_unit", "degC")):
        with pytest.raises(ValidationError):
            VariableSemanticDeclaration(**{**record.model_dump(), field: value})


def test_semantics_never_change_value_specification_result(tmp_path):
    spec = specification()
    without = world(tmp_path / "without", spec).load()
    with_semantics = world(tmp_path / "with", spec, meaning()).load()
    assert ModelQueries(without).variable_value_specification(VAR_A).model_dump(
        exclude={"revision"}) == ModelQueries(
            with_semantics).variable_value_specification(VAR_A).model_dump(
                exclude={"revision"})
    assert with_semantics.specifications == {spec.record_id: spec}


def test_reappend_is_noop_and_disk_tamper_is_detected(tmp_path):
    record = meaning()
    store = world(tmp_path, record)
    before, revision = snapshot(store), store.load().revision
    assert store.append(record) == record.record_id
    assert snapshot(store) == before
    assert store.load().revision == revision
    path = store.records_dir / f"{record.record_id}.json"
    payload = json.loads(path.read_text())
    payload["declaration"]["quantity_kind"]["code"] = "pressure"
    path.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n")
    with pytest.raises(ModelKernelError) as error:
        store.load()
    assert error.value.error_code == "MODEL_RECORD_HASH_MISMATCH"


def test_vsm_model_record_evidence_closes_at_append_load_and_replay(tmp_path):
    cited = registration("ent_" + "b" * 32)
    dangling = "reg_" + "f" * 64
    bad = build_record(VariableSemanticDeclaration,
        variable_anchor_id=VAR_A, declaration=meaning().declaration,
        evidence=(ModelRecordEvidence(kind="model_record", record_id=dangling),),
        recorded_at=T0, authority=AUTHORITY)
    store = world(tmp_path / "append")
    with pytest.raises(ModelKernelError) as error:
        store.append(bad)
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"
    good = build_record(VariableSemanticDeclaration,
        variable_anchor_id=VAR_A, declaration=meaning().declaration,
        evidence=(ModelRecordEvidence(kind="model_record",
                                      record_id=cited.record_id),),
        recorded_at=T0, authority=AUTHORITY)
    complete = store_with(tmp_path / "replay", registration(ENT_A), cited,
                          variable_registration(), good)
    with pytest.raises(ModelKernelError) as error:
        complete.replay((registration(ENT_A).record_id,
                         variable_registration().record_id, good.record_id))
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"
    # Crafted load exercises the same all-or-nothing collection boundary.
    crafted = world(tmp_path / "load")
    (crafted.records_dir / f"{bad.record_id}.json").write_text(
        json.dumps({**canonical_payload(bad), "record_id": bad.record_id},
                   sort_keys=True, indent=2) + "\n")
    with pytest.raises(ModelKernelError) as error:
        crafted.load()
    assert error.value.error_code == "MODEL_REFERENCE_INVALID"


def test_vsm_is_citable_but_withdrawal_is_not():
    semantic_id = meaning().record_id
    assert ModelRecordEvidence(kind="model_record", record_id=semantic_id)
    rtd = contains_type()
    rel = assertion(rtd)
    withdrawn = withdrawal(rel)
    with pytest.raises(ValidationError):
        ModelRecordEvidence(kind="model_record", record_id=withdrawn.record_id)


class NoneOffset(tzinfo):
    def utcoffset(self, dt):
        return None


@pytest.mark.parametrize("bad", [datetime(2026, 1, 1),
                                  datetime(2026, 1, 1, tzinfo=NoneOffset())])
def test_semantic_record_refuses_naive_recorded_at(bad):
    with pytest.raises(ModelKernelError) as error:
        build_record(VariableSemanticDeclaration,
            variable_anchor_id=VAR_A, declaration=meaning().declaration,
            evidence=meaning().evidence, recorded_at=bad, authority=AUTHORITY)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


@pytest.mark.parametrize("bad", [ENT_A, None, 123, [], ""])
def test_semantics_query_rejects_malformed_anchor_ids(tmp_path, bad):
    with pytest.raises(ModelKernelError) as error:
        ModelQueries(world(tmp_path).load()).variable_semantics(bad)
    assert error.value.error_code == "MODEL_ANCHOR_ID_INVALID"


def test_forged_semantic_record_and_result_are_revalidated(tmp_path):
    record = meaning()
    forged = VariableSemanticDeclaration.model_construct(
        **{**record.model_dump(), "variable_anchor_id": "broken"})
    with pytest.raises(ModelKernelError) as error:
        world(tmp_path).append(forged)
    assert error.value.error_code == "MODEL_RECORD_INVALID"
    invalid_result = SemanticDimensionResult.model_construct(
        dimension="quantity_kind", status="declared", declaration=None)
    with pytest.raises(ValidationError):
        SemanticDimensionResult.model_validate(invalid_result)


def test_result_rejects_a_declaration_for_the_wrong_dimension():
    role = meaning("observation_role")
    with pytest.raises(ValidationError):
        SemanticDimensionResult(
            dimension="quantity_kind", status="declared", declaration=role)


def test_result_rejects_duplicate_conflict_declarations():
    record = meaning()
    with pytest.raises(ValidationError):
        SemanticDimensionResult(
            dimension="quantity_kind", status="conflicted",
            conflicting_declarations=(record, record))


def test_result_rejects_declarations_for_another_anchor(tmp_path):
    loaded = store_with(tmp_path, registration(ENT_A),
                        variable_registration(), variable_registration(VAR_B),
                        meaning(variable=VAR_B)).load()
    other = ModelQueries(loaded).variable_semantics(VAR_B)
    with pytest.raises(ValidationError):
        VariableSemanticsResult(
            anchor_id=VAR_A, quantity_kind=other.quantity_kind,
            observation_role=SemanticDimensionResult(
                dimension="observation_role", status="not_declared"),
            revision=loaded.revision)
