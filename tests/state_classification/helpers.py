"""Disposable ST-001 Slice C worlds built through accepted public APIs."""

from datetime import UTC, datetime

from backend.constraint_evaluation import ConstraintEvaluationQueries
from backend.model_state import SourceSelector
from backend.state_classification import (
    StateClassificationQueries,
    StateConditionSource,
)
from tests.behavior_evaluation.helpers import (
    PROP_TARGET,
    PROP_TEMP,
    SUBJECT,
    semantic_queries,
)
from tests.model_kernel.builders import (
    CON_A,
    CON_B,
    VAR_A,
    VAR_B,
    constraint_declaration,
    constraint_registration,
    constraint_signature,
    observation_role,
    upper_bound,
)
from tests.model_kernel.st001_slice_a_helpers import (
    AS_DESIGNED,
    AS_OPERATED,
    STATE_A,
    T1,
    pins,
    state_declaration,
    state_registration,
    state_withdrawal,
)
from tests.behavior_evaluation.helpers import E1, model_store


AS_OF = datetime(2026, 8, 7, 20, 30, tzinfo=UTC)


def condition_records(*, upper_a="80", upper_b="80",
                      declaration_a=None, declaration_b=None):
    first = declaration_a or constraint_declaration(
        CON_A, predicate=upper_bound(upper_a))
    second = declaration_b or constraint_declaration(
        CON_B, predicate=upper_bound(upper_b),
        expected_semantics=constraint_signature().model_copy(update={
            "observation_role": observation_role("reported")}))
    return (
        constraint_registration(CON_A, variable_anchor_id=VAR_A),
        first,
        constraint_registration(CON_B, variable_anchor_id=VAR_B),
        second,
    ), {CON_A: first, CON_B: second}


def state_model(tmp_path, *, include_registration=True,
                declaration_records=None, upper_a="80", upper_b="80",
                extra_records=()):
    constraints, declarations = condition_records(
        upper_a=upper_a, upper_b=upper_b)
    registration = state_registration(
        subject=E1, constraints=(CON_A, CON_B), second_owner=E1)
    if declaration_records is None:
        declaration_records = (state_declaration(
            registration,
            context=AS_OPERATED,
            condition_pins=pins(
                constraints=(CON_A, CON_B), declarations=declarations),
        ),)
    extras = [*constraints]
    if include_registration:
        extras.append(registration)
    extras.extend(extra_records)
    extras.extend(declaration_records)
    return model_store(tmp_path, extra_records=tuple(extras)), registration, declarations


def condition_sources(*, reverse=False):
    rows = (
        StateConditionSource(
            constraint_anchor_id=CON_A,
            source=SourceSelector(subject=SUBJECT, property=PROP_TEMP),
        ),
        StateConditionSource(
            constraint_anchor_id=CON_B,
            source=SourceSelector(subject=SUBJECT, property=PROP_TARGET),
        ),
    )
    return tuple(reversed(rows)) if reverse else rows


def facade(tmp_path, *, model=None):
    model = model or state_model(tmp_path)[0]
    return StateClassificationQueries(ConstraintEvaluationQueries(
        semantic_queries(tmp_path, model=model)))


def classify(tmp_path, *, model=None, context=AS_OPERATED,
             sources=None, as_of=AS_OF):
    return facade(tmp_path, model=model).state_classification(
        STATE_A,
        context=context,
        as_of=as_of,
        condition_sources=condition_sources() if sources is None else sources,
    )


def inactive_model(tmp_path):
    constraints, declarations = condition_records()
    registration = state_registration(
        subject=E1, constraints=(CON_A, CON_B), second_owner=E1)
    root = state_declaration(
        registration, context=AS_OPERATED,
        condition_pins=pins(declarations=declarations))
    return model_store(
        tmp_path,
        extra_records=(*constraints, registration, root,
                       state_withdrawal(root))), registration


def conflicted_model(tmp_path):
    constraints, declarations = condition_records()
    registration = state_registration(
        subject=E1, constraints=(CON_A, CON_B), second_owner=E1)
    root = state_declaration(
        registration, context=AS_OPERATED,
        condition_pins=pins(declarations=declarations))
    left = state_declaration(
        registration, context=AS_OPERATED,
        condition_pins=pins(declarations=declarations),
        supersedes=(root.record_id,), recorded_at=T1, note="left")
    right = state_declaration(
        registration, context=AS_OPERATED,
        condition_pins=pins(declarations=declarations),
        supersedes=(root.record_id,),
        recorded_at=T1.replace(minute=1), note="right")
    return model_store(
        tmp_path,
        extra_records=(*constraints, registration, root, left, right)), registration


__all__ = [
    "AS_DESIGNED", "AS_OF", "AS_OPERATED", "CON_A", "CON_B", "E1",
    "STATE_A", "VAR_A", "VAR_B", "classify", "condition_records",
    "condition_sources", "conflicted_model", "facade", "inactive_model",
    "state_model",
]
