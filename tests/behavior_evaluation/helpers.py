"""Disposable BH-001 Slice C worlds built through accepted public APIs."""

from datetime import UTC, datetime

from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import (
    ModelStore,
    ObservationRoleDeclaration,
    QuantityKindDeclaration,
    VariableSemanticDeclaration,
    build_record,
)
from backend.model_state import ModelStateQueries, SourceSelector
from backend.observation_compatibility import ObservationCompatibilityQueries
from backend.semantic_compatibility import SemanticCompatibilityQueries
from backend.source_interpretation import (
    InterpretationResolver,
    InterpretationStore,
    ObservationRoleInterpretation,
    QuantityKindInterpretation,
    SourcePropertyInterpretation,
    UnitInterpretation,
    build_record as interpretation_build,
)

from tests.model_kernel.bh001_slice_a_helpers import (
    AS_BUILT,
    AS_DESIGNED,
    AUTHORITY,
    BEHAVIOR_A,
    T0,
    behavior_declaration,
    behavior_registration,
    semantic_lock,
    variable_records,
)
from tests.model_kernel.builders import (
    VAR_A,
    VAR_B,
    observation_role,
    quantity_kind,
    specification,
)
from tests.model_state.helpers import (
    PROP_TARGET,
    PROP_TEMP,
    SUBJECT,
    entity_declaration,
    hour,
    observed_stack,
    prop_assertion,
    var_declaration,
)

AS_OF = datetime(2026, 8, 7, 20, 30, tzinfo=UTC)
E1 = "ent_" + "9" * 32


def _semantic_record(variable_anchor_id, declaration):
    return build_record(
        VariableSemanticDeclaration,
        variable_anchor_id=variable_anchor_id,
        declaration=declaration,
        evidence=(__import__(
            "backend.model_kernel", fromlist=["OwnerDeclarationEvidence"]
        ).OwnerDeclarationEvidence(
            kind="owner_declaration", statement="synthetic BH semantic lock"
        ),),
        supersedes=(),
        recorded_at=T0,
        authority=AUTHORITY,
        note="",
    )


def model_store(tmp_path, *, include_behavior=True, declaration_context=AS_DESIGNED,
                declaration_records=None, specification_overrides=None,
                omit_specifications=(), omit_semantics=(), extra_records=(),
                owners=(E1, E1)):
    store = ModelStore(tmp_path / "model" / "demo-printer")
    for record in variable_records(owners=owners):
        store.append(record)
    spec_overrides = specification_overrides or {}
    for variable_id in (VAR_A, VAR_B):
        if variable_id not in omit_specifications:
            store.append(specification(
                variable_id, **spec_overrides.get(variable_id, {})))
        if (variable_id, "quantity_kind") not in omit_semantics:
            store.append(_semantic_record(
                variable_id,
                QuantityKindDeclaration(
                    dimension="quantity_kind", quantity_kind=quantity_kind()),
            ))
        role = "measured" if variable_id == VAR_A else "reported"
        if (variable_id, "observation_role") not in omit_semantics:
            store.append(_semantic_record(
                variable_id,
                ObservationRoleDeclaration(
                    dimension="observation_role",
                    observation_role=observation_role(role),
                ),
            ))
    for record in extra_records:
        store.append(record)
    registration = behavior_registration(owners=(E1, E1))
    if include_behavior:
        store.append(registration)
        records = declaration_records
        if records is None:
            records = (behavior_declaration(
                registration, context=declaration_context,
                locks=(semantic_lock(VAR_A), semantic_lock(VAR_B, role="reported"))),)
        for record in records:
            store.append(record)
    return store


def _interpretation_record(prop, interpretation):
    from backend.identity_binding.contracts import AuthorityRef

    return interpretation_build(
        SourcePropertyInterpretation,
        subject=SUBJECT,
        property=prop,
        interpretation=interpretation,
        applies=hour(),
        supersedes=(),
        recorded_at=T0,
        authority=AuthorityRef(
            kind="test_fixture", agent="bh001_evaluator_fixture",
            method="manual_declaration"),
        note="",
    )


def interpretation_resolver(tmp_path, *, overrides=None, extra_records=()):
    overrides = overrides or {}
    store = InterpretationStore(tmp_path / "interpretations" / "demo-printer")
    for prop in (PROP_TEMP, PROP_TARGET):
        role = "measured" if prop == PROP_TEMP else "reported"
        values = overrides.get(prop, {})
        for body in (
            QuantityKindInterpretation(
                dimension="quantity_kind", quantity_kind=values.get(
                    "quantity_kind", quantity_kind())),
            ObservationRoleInterpretation(
                dimension="observation_role", observation_role=values.get(
                    "observation_role", observation_role(role))),
            UnitInterpretation(
                dimension="unit", unit=values.get(
                    "unit", semantic_lock(VAR_A).signature.unit)),
        ):
            store.append(_interpretation_record(prop, body))
    for record in extra_records:
        store.append(record)
    return InterpretationResolver(store.load())


def semantic_queries(tmp_path, *, model=None, temporal=None,
                     binding_records=None, interpretations=None):
    model = model or model_store(tmp_path)
    temporal = temporal or observed_stack(tmp_path)
    binding_store = BindingStore(tmp_path / "bindings" / "demo-printer")
    records = binding_records or (
        entity_declaration(E1, "Demo entity"),
        var_declaration(VAR_A, E1, "Variable A"),
        var_declaration(VAR_B, E1, "Variable B"),
        prop_assertion(VAR_A, PROP_TEMP),
        prop_assertion(VAR_B, PROP_TARGET),
    )
    for record in records:
        binding_store.append(record)
    state = ModelStateQueries(
        model.load(), BindingResolver(binding_store.load()), temporal)
    compatibility = ObservationCompatibilityQueries(state)
    return SemanticCompatibilityQueries(
        compatibility, interpretations or interpretation_resolver(tmp_path))


def participant_sources(*, reverse=False):
    from backend.behavior_evaluation import BehaviorParticipantSource

    values = (
        BehaviorParticipantSource(
            variable_anchor_id=VAR_A,
            entity_anchor_id=E1,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP)),
        BehaviorParticipantSource(
            variable_anchor_id=VAR_B,
            entity_anchor_id=E1,
            source=SourceSelector(subject=SUBJECT, property=PROP_TARGET)),
    )
    return tuple(reversed(values)) if reverse else values


def evaluate(tmp_path, *, context=AS_DESIGNED, model=None, temporal=None,
             participants=None, as_of=AS_OF, semantic=None):
    from backend.behavior_evaluation import BehaviorEvaluationQueries

    facade = BehaviorEvaluationQueries(
        semantic or semantic_queries(tmp_path, model=model, temporal=temporal))
    return facade.behavior_evaluation(
        BEHAVIOR_A,
        context=context,
        as_of=as_of,
        participants=participants or participant_sources(),
    )


__all__ = [
    "AS_BUILT", "AS_DESIGNED", "AS_OF", "BEHAVIOR_A", "E1", "PROP_TARGET",
    "PROP_TEMP", "SUBJECT", "VAR_A", "VAR_B", "evaluate", "model_store",
    "participant_sources", "semantic_queries",
]
