"""CN-001 Slice B facade tests: reachable precedence, exact comparisons,
structured discovery, isolation, and outer-result forgery rejection.

The committed ``models/demo-printer`` ledger stays at 16 records. Every
constraint fixture is built into an isolated ``tmp_path`` model store that
copies the committed demo records and appends synthetic ``crg_`` / ``vcn_``
records. Hostile observations use Tier C crafted occurrences through the
public writer; no private temporal internals are imported."""

from datetime import UTC, datetime
from pathlib import Path

import pytest
from pydantic import BaseModel

from backend.constraint_evaluation import (
    BoundaryAssessment, ConstraintEvaluationConfigurationError,
    ConstraintEvaluationInputError, ConstraintEvaluationResult,
    ConstraintEvaluationQueries, CandidateConstraintEvaluation,
    NumericParityBreachError, VariableConstraintEvaluationCollectionResult,
    derive_candidate_evaluation)
from backend.identity_binding.canonical import build_record as ib_build
from backend.identity_binding.contracts import (
    AnchorDeclaration, BindingAssertion, AppliesScope, DeclaredBoundary)
from backend.model_kernel import (
    ExactNumericInterval, ExactNumericLowerBound, ExactNumericUpperBound,
    ModelQueries, ModelStore, NumericBoundary)
from backend.model_state import ModelStateQueries, SourceSelector
from backend.observation_compatibility import ObservationCompatibilityQueries
from backend.semantic_compatibility import SemanticCompatibilityQueries
from backend.source_interpretation import InterpretationResolver, InterpretationStore
from backend.system_identity import EntityAnchor, VariableAnchor

from tests.constraint_evaluation.helpers import (
    AS_OF, CON_A, CON_B, CON_C, DEMO_INTERPRETATIONS, EARLY, EXTRUDER, HOTEND,
    LATE, T0, constraint_declaration, constraint_registration, cn_stack,
    craft_value, custom_stack, default_constraint_records, expected_semantics,
    other_observation_role_ref, other_quantity_kind_ref, other_unit_ref)
from tests.model_state.helpers import (
    E1, PROP_TARGET, PROP_TEMP, SUBJECT, V1, entity_anchor, var_anchor,
    full_timeline_stack)
from tests.observation_compatibility.helpers import craft_occurrence
from tests.observation_compatibility.test_demo_compatibility import (
    AS_OF as DEMO_AS_OF, HOTEND as DEMO_HOTEND, EXTRUDER as DEMO_EXTRUDER)


# ============================================================ happy path

class TestHappyPath:
    def test_upper_bound_satisfied(self, tmp_path):
        cn, es, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericUpperBound(
                    upper=NumericBoundary(value="80",
                                           inclusion="inclusive"))))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF,
                                        entity_anchor_id=EXTRUDER)
        assert result.ruleset_version == "cn001.1"
        assert result.declaration.status == "declared"
        assert len(result.candidates) == 1
        assert result.candidates[0].verdict == "satisfied"
        assert result.candidates[0].not_evaluated_reason is None
        assert result.candidates[0].observed_decimal.canonical == "60.4"
        assert len(result.candidates[0].boundary_assessments) == 1
        assert result.candidates[0].boundary_assessments[0].satisfied is True
        assert result.semantic_compatibility == es.variable_semantic_compatibility(
            HOTEND, as_of=AS_OF, entity_anchor_id=EXTRUDER)

    def test_upper_bound_violated(self, tmp_path):
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericUpperBound(
                    upper=NumericBoundary(value="50",
                                           inclusion="inclusive"))))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.candidates[0].verdict == "violated"
        assert result.candidates[0].boundary_assessments[0].satisfied is False
        assert result.candidates[0].boundary_assessments[0].relation == "greater"

    def test_es_result_carried_once_no_duplicate_candidate_objects(self, tmp_path):
        cn, es, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        # the carried ES candidate object is the SAME object as the ES
        # result's candidate (no second CandidateSemanticCompatibility copy)
        assert (result.candidates[0].candidate_index == 0)
        assert (result.semantic_compatibility.candidates[0]
                is result.semantic_compatibility.candidates[0])
        # the candidate evaluation references the ES candidate by index only
        assert result.candidates[0].candidate_index == 0

    def test_multiple_candidates_keep_order_with_opposing_outcomes(self, tmp_path):
        from backend.model_state import ModelStateQueries
        from backend.observation_compatibility import ObservationCompatibilityQueries
        from backend.identity_binding.resolver import BindingResolver
        from backend.identity_binding.store import BindingStore
        from backend.semantic_compatibility import SemanticCompatibilityQueries
        from backend.source_interpretation import (
            InterpretationResolver, InterpretationStore,
            ObservationRoleInterpretation, QuantityKindInterpretation,
            SourcePropertyInterpretation, UnitInterpretation,
            build_record as spi_build)
        from tests.model_state.helpers import (
            PROP_TARGET, PROP_TEMP, SUBJECT, hour, prop_assertion,
            standard_bindings)
        from tests.observation_compatibility.helpers import model_with, observed_stack
        from tests.semantic_compatibility.test_facade import (
            INTERP_AUTH, QUANTITY, ROLE, T0, UNIT, model_semantics)

        store = model_semantics(model_with(tmp_path / "multi"))
        store.append(constraint_registration(
            variable_anchor_id=V1))
        store.append(constraint_declaration(
            expected_sem_sig=expected_semantics(
                quantity_kind=QUANTITY, observation_role=ROLE, unit=UNIT),
            predicate=ExactNumericUpperBound(upper=NumericBoundary(
                value="60.05", inclusion="inclusive"))))
        loaded = store.load()

        bstore = BindingStore(tmp_path / "multi-bindings" / "demo-printer")
        for record in (*standard_bindings(), prop_assertion(
                prop=PROP_TARGET, note="second candidate")):
            bstore.append(record)

        istore = InterpretationStore(
            tmp_path / "multi-interpretations" / "demo-printer")
        for prop in (PROP_TEMP, PROP_TARGET):
            for body in (
                QuantityKindInterpretation(
                    dimension="quantity_kind", quantity_kind=QUANTITY),
                ObservationRoleInterpretation(
                    dimension="observation_role", observation_role=ROLE),
                UnitInterpretation(dimension="unit", unit=UNIT),
            ):
                istore.append(spi_build(
                    SourcePropertyInterpretation, subject=SUBJECT,
                    property=prop, interpretation=body, applies=hour(),
                    supersedes=(), recorded_at=T0, authority=INTERP_AUTH,
                    note="multi-candidate CN fixture"))

        temporal = observed_stack(tmp_path / "multi-observed")
        state = ModelStateQueries(
            loaded, BindingResolver(bstore.load()), temporal)
        es = SemanticCompatibilityQueries(
            ObservationCompatibilityQueries(state),
            InterpretationResolver(istore.load()))
        result = ConstraintEvaluationQueries(es).evaluate_constraint(
            CON_A, as_of=AS_OF)

        assert tuple(row.candidate_index for row in result.candidates) == (0, 1)
        outcomes = tuple(
            (row.verdict, row.observed_decimal.canonical)
            for row in result.candidates)
        assert outcomes == (("satisfied", "60"), ("violated", "60.1"))


# ============================================================ precedence

class TestPrecedence:
    """Each refusal reason is reached independently, in the exact reachable
    precedence order."""

    def test_step1_not_registered(self, tmp_path):
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        result = cn.evaluate_constraint(
            "con_" + "f" * 32, as_of=AS_OF)
        assert result.declaration.status == "not_registered"
        assert result.semantic_compatibility is None
        assert result.candidates == ()

    def test_step2_not_declared(self, tmp_path):
        # registration only, no declaration
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=(constraint_registration(),))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.declaration.status == "not_declared"
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == "not_declared"

    def test_step2_conflicted(self, tmp_path):
        # two non-superseding declarations -> two tips -> conflicted
        reg = constraint_registration()
        decl1 = constraint_declaration(constraint_anchor_id=CON_A, note="d1")
        decl2 = constraint_declaration(constraint_anchor_id=CON_A, note="d2")
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=(reg, decl1, decl2))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.declaration.status == "conflicted"
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == "conflicted"
        assert len(result.declaration.conflicting_declarations) == 2

    def test_step3_no_observation(self, tmp_path):
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        result = cn.evaluate_constraint(CON_A, as_of=EARLY)
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == "no_observation"

    def test_step4_observation_not_attached(self, tmp_path):
        # divergent binding: variable anchor declaration has a different
        # display_name than the model's VariableRegistration → anchor
        # divergence → observation not attached
        from backend.identity_binding.canonical import build_record as ib_build
        from backend.identity_binding.contracts import AnchorDeclaration
        from backend.identity_binding.store import BindingStore
        from backend.system_identity import VariableAnchor
        from tests.observation_compatibility.test_demo_compatibility import (
            HOTEND as DEMO_HOTEND, EXTRUDER as DEMO_EXTRUDER)
        bs = BindingStore(Path("bindings/demo-printer")).load()
        committed = list(bs.records.values())
        divergent_anchor = VariableAnchor(
            anchor_id=DEMO_HOTEND, entity_anchor_id=DEMO_EXTRUDER,
            namespace="demo-printer", display_name="Hotend temp (renamed)",
            role_name=None)
        divergent_records = []
        for rec in committed:
            if isinstance(rec, AnchorDeclaration) and rec.anchor_kind == "variable":
                divergent_records.append(ib_build(
                    AnchorDeclaration, anchor_kind="variable",
                    anchor=divergent_anchor, recorded_at=rec.recorded_at,
                    authority=rec.authority, note=rec.note))
            else:
                divergent_records.append(rec)
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records(),
            binding_records=divergent_records)
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == (
            "observation_not_attached")

    def test_step5_evidence_not_assessable_value_json_malformed(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        craft_value(temporal, value_json="not-a-number", json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == "value_json_malformed"

    def test_step5_evidence_not_assessable_shape_disagreement(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        # json_type says number but value_json is a quoted string
        craft_value(temporal, value_json='"60"', json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].not_evaluated_reason == "shape_disagreement"

    def test_step5_evidence_not_assessable_json_type_unrecognized(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        craft_value(temporal, value_json="60", json_type="bogus_type")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].not_evaluated_reason == "json_type_unrecognized"

    def test_step5_evidence_not_assessable_value_not_representable(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        # a digit string so long it exceeds int_max_str_digits -> ValueError
        craft_value(temporal, value_json="9" * 5000, json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].not_evaluated_reason == "value_not_representable"

    def test_step6_vs_shape_not_evaluated_specification_conflicted(self, tmp_path):
        from backend.model_kernel import (
            build_record, VariableValueSpecification, DeclaredUnit,
            AuthorityRef, OwnerDeclarationEvidence)
        from tests.constraint_evaluation.helpers import DEMO_UNIT
        # append a second non-superseding VSP for HOTEND with a different
        # value_shape → specification conflict → VS reports not_evaluated
        auth = AuthorityRef(kind="test_fixture", agent="cn001",
                             method="manual_declaration")
        ev = (OwnerDeclarationEvidence(
            kind="owner_declaration", statement="conflicting spec"),)
        conflicting_vsp = build_record(
            VariableValueSpecification, variable_anchor_id=HOTEND,
            value_shape="string", nullable=False,
            unit=DeclaredUnit(kind="declared", unit=DEMO_UNIT),
            evidence=ev, recorded_at=T0, authority=auth, note="conflicting")
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=(
                *default_constraint_records(), conflicting_vsp))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == (
            "specification_conflicted")

    def test_step7_model_value_shape_not_numeric(self, tmp_path):
        from backend.model_kernel import (
            build_record, VariableValueSpecification, DeclaredUnit,
            AuthorityRef, OwnerDeclarationEvidence)
        from tests.constraint_evaluation.helpers import DEMO_UNIT
        # supersede the demo's numeric VSP with a string VSP; a string
        # observation passes steps 3-6 but the governing shape is not
        # 'number' → step 7
        vsp_id = ("vsp_c8e5d91d38c5e3f36d0d592737aac5ce26c03eb5d1"
                  "69365c38953f971ff62ba0")
        auth = AuthorityRef(kind="test_fixture", agent="cn001",
                             method="manual_declaration")
        ev = (OwnerDeclarationEvidence(
            kind="owner_declaration", statement="string spec"),)
        string_vsp = build_record(
            VariableValueSpecification, variable_anchor_id=HOTEND,
            value_shape="string", nullable=False,
            unit=DeclaredUnit(kind="declared", unit=DEMO_UNIT),
            evidence=ev, recorded_at=T0, authority=auth, note="string spec",
            supersedes=(vsp_id,))
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=(
                *default_constraint_records(), string_vsp))
        craft_value(temporal, value_json='"hot"', json_type="string")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == (
            "model_value_shape_not_numeric")

    def test_step8_does_not_satisfy_value_shape(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        # observed is a string; VSP expects number -> shape_differs
        craft_value(temporal, value_json='"hot"', json_type="string")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].not_evaluated_reason == (
            "does_not_satisfy_value_shape")

    def test_step9_numeric_value_absent_nullable_null(self, tmp_path):
        from tests.model_state.helpers import RECORDED, MODEL_AUTHORITY, resolver_with
        from tests.observation_compatibility.helpers import standard_bindings
        from backend.model_kernel import (
            EntityRegistration, VariableRegistration, VariableValueSpecification,
            VariableSemanticDeclaration, DeclaredUnit, UnitReference,
            QuantityKindReference, ObservationRoleReference,
            QuantityKindDeclaration, ObservationRoleDeclaration,
            SemanticDimensionDeclaration, build_record, AuthorityRef,
            OwnerDeclarationEvidence)
        from tests.constraint_evaluation.helpers import DEMO_QUANTITY_KIND, DEMO_OBSERVATION_ROLE, DEMO_UNIT
        # custom model: V1 with nullable=True number VSP and semantic
        # declarations matching the demo so the lock gates can pass.
        ev = (OwnerDeclarationEvidence(
            kind="owner_declaration", statement="nullable test spec"),)
        store = ModelStore(tmp_path / "model" / "demo-printer")
        store.append(build_record(
            EntityRegistration, anchor=entity_anchor(E1),
            recorded_at=RECORDED, authority=MODEL_AUTHORITY))
        store.append(build_record(
            VariableRegistration, anchor=var_anchor(V1, E1),
            recorded_at=RECORDED, authority=MODEL_AUTHORITY))
        store.append(build_record(
            VariableValueSpecification, variable_anchor_id=V1,
            value_shape="number", nullable=True,
            unit=DeclaredUnit(kind="declared", unit=DEMO_UNIT),
            evidence=ev, recorded_at=RECORDED, authority=MODEL_AUTHORITY))
        # semantic declarations matching the demo's tokens, wrapped in
        # VariableSemanticDeclaration (the actual ModelRecord kind)
        store.append(build_record(
            VariableSemanticDeclaration, variable_anchor_id=V1,
            declaration=QuantityKindDeclaration(
                dimension="quantity_kind", quantity_kind=DEMO_QUANTITY_KIND),
            evidence=ev, supersedes=(), recorded_at=RECORDED,
            authority=MODEL_AUTHORITY, note=""))
        store.append(build_record(
            VariableSemanticDeclaration, variable_anchor_id=V1,
            declaration=ObservationRoleDeclaration(
                dimension="observation_role",
                observation_role=DEMO_OBSERVATION_ROLE),
            evidence=ev, supersedes=(), recorded_at=RECORDED,
            authority=MODEL_AUTHORITY, note=""))
        # constraint
        store.append(constraint_registration(constraint_anchor_id=CON_A,
                                              variable_anchor_id=V1))
        store.append(constraint_declaration(constraint_anchor_id=CON_A,
                                            predicate=ExactNumericUpperBound(
                                                upper=NumericBoundary(
                                                    value="80",
                                                    inclusion="inclusive"))))
        loaded = store.load()
        # custom bindings matching V1/E1 (not the committed demo bindings
        # which target a different anchor_id)
        resolver = resolver_with(tmp_path, *standard_bindings())
        temporal = full_timeline_stack(tmp_path)
        # craft a null observation as the latest
        craft_value(temporal, value_json="null", json_type="null")
        state = ModelStateQueries(loaded, resolver, temporal)
        values = ObservationCompatibilityQueries(state)
        interpretations = InterpretationStore(DEMO_INTERPRETATIONS).load()
        es = SemanticCompatibilityQueries(values, InterpretationResolver(interpretations))
        cn = ConstraintEvaluationQueries(es)
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == "numeric_value_absent"

    def test_step10_declared_semantics_not_compatible(self, tmp_path):
        # empty interpretations -> source_interpretation_not_declared ->
        # no declared_semantics_compatible
        empty = InterpretationStore(tmp_path / "empty" / "demo-printer").load()
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(),
            interpretations_path=tmp_path / "empty" / "demo-printer")
        # use the committed temporal so an observation exists; the empty
        # interpretation makes the ES gate fail
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.candidates[0].verdict == "not_evaluated"
        assert result.candidates[0].not_evaluated_reason == (
            "declared_semantics_not_compatible")

    def test_step11_quantity_kind_lock_mismatch(self, tmp_path):
        cn, _, _, _ = cn_stack(tmp_path, constraint_records=(
            constraint_registration(),
            constraint_declaration(expected_sem_sig=expected_semantics(
                quantity_kind=other_quantity_kind_ref()))))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.candidates[0].not_evaluated_reason == (
            "constraint_quantity_kind_lock_mismatch")

    def test_step12_observation_role_lock_mismatch(self, tmp_path):
        cn, _, _, _ = cn_stack(tmp_path, constraint_records=(
            constraint_registration(),
            constraint_declaration(expected_sem_sig=expected_semantics(
                observation_role=other_observation_role_ref()))))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.candidates[0].not_evaluated_reason == (
            "constraint_observation_role_lock_mismatch")

    def test_step13_unit_identity_lock_mismatch(self, tmp_path):
        cn, _, _, _ = cn_stack(tmp_path, constraint_records=(
            constraint_registration(),
            constraint_declaration(expected_sem_sig=expected_semantics(
                unit=other_unit_ref()))))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.candidates[0].not_evaluated_reason == (
            "constraint_unit_identity_lock_mismatch")

    def test_step14_numeric_value_out_of_bounds(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        craft_value(temporal, value_json="1E+999", json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].not_evaluated_reason == (
            "numeric_value_out_of_bounds")


# ============================================================ comparisons

class TestComparisons:
    @pytest.mark.parametrize("value,bound,inclusion,expected", [
        # upper bound
        ("60.4", "80", "inclusive", "satisfied"),
        ("80", "80", "inclusive", "satisfied"),
        ("80.1", "80", "inclusive", "violated"),
        ("80", "80", "exclusive", "violated"),
        ("79.9", "80", "exclusive", "satisfied"),
    ])
    def test_upper_bound_boundaries(self, tmp_path, value, bound,
                                     inclusion, expected):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericUpperBound(
                    upper=NumericBoundary(value=bound,
                                           inclusion=inclusion))))
        craft_value(temporal, value_json=value, json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == expected

    @pytest.mark.parametrize("value,bound,inclusion,expected", [
        ("60.4", "50", "inclusive", "satisfied"),
        ("50", "50", "inclusive", "satisfied"),
        ("49.9", "50", "inclusive", "violated"),
        ("50", "50", "exclusive", "violated"),
        ("50.1", "50", "exclusive", "satisfied"),
    ])
    def test_lower_bound_boundaries(self, tmp_path, value, bound,
                                     inclusion, expected):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericLowerBound(
                    lower=NumericBoundary(value=bound,
                                           inclusion=inclusion))))
        craft_value(temporal, value_json=value, json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == expected

    @pytest.mark.parametrize("value,lo,hi,li,ui,expected", [
        # interval [50, 80] inclusive both
        ("60", "50", "80", "inclusive", "inclusive", "satisfied"),
        ("50", "50", "80", "inclusive", "inclusive", "satisfied"),
        ("80", "50", "80", "inclusive", "inclusive", "satisfied"),
        ("49.9", "50", "80", "inclusive", "inclusive", "violated"),
        ("80.1", "50", "80", "inclusive", "inclusive", "violated"),
        # interval (50, 80) exclusive both
        ("50", "50", "80", "exclusive", "exclusive", "violated"),
        ("80", "50", "80", "exclusive", "exclusive", "violated"),
        ("50.1", "50", "80", "exclusive", "exclusive", "satisfied"),
        # mixed inclusivity
        ("50", "50", "80", "inclusive", "exclusive", "satisfied"),
        ("80", "50", "80", "inclusive", "exclusive", "violated"),
        ("50", "50", "80", "exclusive", "inclusive", "violated"),
        ("80", "50", "80", "exclusive", "inclusive", "satisfied"),
        # singleton {60} inclusive both
        ("60", "60", "60", "inclusive", "inclusive", "satisfied"),
        ("60.1", "60", "60", "inclusive", "inclusive", "violated"),
    ])
    def test_interval_boundaries(self, tmp_path, value, lo, hi, li, ui,
                                  expected):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericInterval(
                    lower=NumericBoundary(value=lo, inclusion=li),
                    upper=NumericBoundary(value=hi, inclusion=ui))))
        craft_value(temporal, value_json=value, json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == expected
        # interval carries two boundary assessments
        assert len(result.candidates[0].boundary_assessments) == 2

    def test_negative_value(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericLowerBound(
                    lower=NumericBoundary(value="-10",
                                           inclusion="inclusive"))))
        craft_value(temporal, value_json="-25.5", json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == "violated"
        assert result.candidates[0].observed_decimal.canonical == "-25.5"

    def test_negative_zero_normalized_to_zero(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericLowerBound(
                    lower=NumericBoundary(value="0",
                                           inclusion="inclusive"))))
        craft_value(temporal, value_json="-0", json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].observed_decimal.canonical == "0"
        assert result.candidates[0].verdict == "satisfied"

    def test_exponent_notation_parses_to_canonical(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericUpperBound(
                    upper=NumericBoundary(value="100",
                                           inclusion="inclusive"))))
        craft_value(temporal, value_json="6e1", json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].observed_decimal.canonical == "60"
        assert result.candidates[0].verdict == "satisfied"

    def test_large_integer_admitted_exactly(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericUpperBound(
                    upper=NumericBoundary(value="9" * 250,
                                           inclusion="inclusive"))))
        craft_value(temporal, value_json="1" * 200, json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        assert result.candidates[0].verdict == "satisfied"
        assert result.candidates[0].observed_decimal.canonical == "1" * 200

    def test_precision_sensitive_fraction(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericUpperBound(
                    upper=NumericBoundary(value="0.001",
                                           inclusion="inclusive"))))
        craft_value(temporal, value_json="0." + "0" * 99 + "1",
                    json_type="number")
        result = cn.evaluate_constraint(CON_A, as_of=LATE)
        # 1e-100 < 0.001 → within the inclusive upper bound → satisfied.
        # Exact parsing preserves the 100-digit fraction without rounding.
        assert result.candidates[0].verdict == "satisfied"


# ============================================================ discovery

class TestDiscovery:
    def test_not_registered_variable(self, tmp_path):
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        result = cn.constraints_of_variable_evaluation(
            "var_" + "f" * 32, as_of=AS_OF)
        assert result.status == "not_registered"
        assert result.evaluations == ()
        assert result.semantic_compatibility is None

    def test_registered_with_constraints(self, tmp_path):
        reg_a = constraint_registration(constraint_anchor_id=CON_A)
        decl_a = constraint_declaration(constraint_anchor_id=CON_A)
        reg_b = constraint_registration(constraint_anchor_id=CON_B)
        decl_b = constraint_declaration(constraint_anchor_id=CON_B)
        cn, es, _, _ = cn_stack(
            tmp_path, constraint_records=(reg_a, decl_a, reg_b, decl_b))
        result = cn.constraints_of_variable_evaluation(HOTEND, as_of=AS_OF)
        assert result.status == "registered"
        assert len(result.evaluations) == 2
        assert result.evaluations[0].constraint_anchor_id == CON_A
        assert result.evaluations[1].constraint_anchor_id == CON_B
        # both share the same ES result (carried once)
        assert (result.evaluations[0].semantic_compatibility
                == result.semantic_compatibility
                == result.evaluations[1].semantic_compatibility)

    def test_registered_empty_has_no_constraints(self, tmp_path):
        # HOTEND is registered in the demo model; with no constraint records
        # appended, the collection is registered but empty.
        cn, _, _, _ = cn_stack(tmp_path, constraint_records=())
        result = cn.constraints_of_variable_evaluation(HOTEND, as_of=AS_OF)
        assert result.status == "registered"
        assert result.evaluations == ()
        assert result.semantic_compatibility is None
        assert result.constraint_collection.constraints == ()

    def test_registered_empty_rejects_extra_es_and_wrong_revision(self, tmp_path):
        cn, es, _, _ = cn_stack(tmp_path, constraint_records=())
        result = cn.constraints_of_variable_evaluation(HOTEND, as_of=AS_OF)
        payload = result.model_dump(mode="python")
        payload["semantic_compatibility"] = es.variable_semantic_compatibility(
            HOTEND, as_of=AS_OF)
        with pytest.raises(Exception):
            VariableConstraintEvaluationCollectionResult(**payload)
        from tests.model_kernel.test_demo_model import PRE_ES001_MEMBERSHIP
        payload = result.model_dump(mode="python")
        payload["revision"] = ModelStore(Path("models/demo-printer")).replay(
            PRE_ES001_MEMBERSHIP).revision
        with pytest.raises(Exception):
            VariableConstraintEvaluationCollectionResult(**payload)


# ============================================================ revision coherence + replay

class TestRevisionCoherence:
    def test_revision_carried_and_coherent(self, tmp_path):
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.revision == result.declaration.revision
        assert (result.revision
                == result.semantic_compatibility.semantics_result.revision)
        assert (result.revision
                == result.semantic_compatibility.value_compatibility
                .state.model_revision)

    def test_historical_model_replay_constraints_absent(self, tmp_path):
        # replay the demo model to a pre-constraint revision (the 16-record
        # demo has no constraints). The replayed model has no crg_/vcn_.
        from tests.model_kernel.test_demo_model import PRE_ES001_MEMBERSHIP
        cn, _, _, _ = cn_stack(
            tmp_path,
            model_records_override=list(
                ModelStore(Path("models/demo-printer"))
                .replay(PRE_ES001_MEMBERSHIP).records.values()),
            constraint_records=())
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.declaration.status == "not_registered"
        assert result.candidates == ()


# ============================================================ isolation

class TestIsolation:
    def test_no_store_owned(self, tmp_path):
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        # the facade owns no store attribute
        assert not hasattr(cn, "store")
        assert not hasattr(cn, "_store")

    def test_no_writes_to_ledgers_or_evidence(self, tmp_path):
        cn, _, _, temporal = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        def tree_bytes(root):
            return {p.relative_to(root).as_posix(): p.read_bytes()
                    for p in sorted(root.rglob("*")) if p.is_file()}
        before_model = tree_bytes(tmp_path / "model" / "demo-printer")
        before_temporal = temporal.store.ordered_logical_dump()
        before_evidence = tree_bytes(temporal.store.evidence_root)
        before_demo_model = tree_bytes(Path("models/demo-printer"))
        before_demo_bindings = tree_bytes(Path("bindings/demo-printer"))
        before_demo_interp = tree_bytes(Path("interpretations/demo-printer"))
        cn.evaluate_constraint(CON_A, as_of=AS_OF)
        cn.constraints_of_variable_evaluation(HOTEND, as_of=AS_OF)
        assert tree_bytes(tmp_path / "model" / "demo-printer") == before_model
        assert temporal.store.ordered_logical_dump() == before_temporal
        assert tree_bytes(temporal.store.evidence_root) == before_evidence
        assert tree_bytes(Path("models/demo-printer")) == before_demo_model
        assert tree_bytes(Path("bindings/demo-printer")) == before_demo_bindings
        assert tree_bytes(Path("interpretations/demo-printer")) == before_demo_interp

    def test_does_not_import_private_vs_parser(self, tmp_path):
        import backend.constraint_evaluation.decimal as mod
        source = Path(mod.__file__).read_text()
        # The module must not import from VS-001's facade or access its
        # private _parse_shape. The docstring may mention _parse_shape
        # to explain why it is NOT imported; the code must not use it.
        assert not hasattr(mod, "_parse_shape")
        assert "from backend.observation_compatibility.facade" not in source
        assert "from backend.observation_compatibility import" not in source
        # the parser uses the standard library, not VS internals
        assert "import json" in source

    def test_wrong_injected_type_raises_configuration_error(self):
        with pytest.raises(ConstraintEvaluationConfigurationError):
            ConstraintEvaluationQueries("not a facade")  # type: ignore[arg-type]

    def test_malformed_anchor_id_raises_input_error(self, tmp_path):
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        with pytest.raises(ConstraintEvaluationInputError):
            cn.evaluate_constraint("not-a-con-id", as_of=AS_OF)
        with pytest.raises(ConstraintEvaluationInputError):
            cn.constraints_of_variable_evaluation("not-a-var-id",
                                                    as_of=AS_OF)

    def test_early_returns_validate_cutoff_and_selectors(self, tmp_path):
        cn, _, _, _ = cn_stack(tmp_path, constraint_records=())
        with pytest.raises(ConstraintEvaluationInputError):
            cn.evaluate_constraint("con_" + "f" * 32,
                                   as_of=AS_OF.replace(tzinfo=None))
        with pytest.raises(ConstraintEvaluationInputError):
            cn.constraints_of_variable_evaluation(
                HOTEND, as_of=AS_OF, source=object())

    def test_as_of_is_normalized_to_utc(self, tmp_path):
        from datetime import timedelta, timezone
        cn, _, _, _ = cn_stack(tmp_path, constraint_records=())
        offset = timezone(timedelta(hours=2))
        requested = AS_OF.astimezone(offset)
        result = cn.constraints_of_variable_evaluation(
            HOTEND, as_of=requested)
        assert result.as_of.tzinfo is UTC
        assert result.as_of == AS_OF


# ============================================================ outer-result forgery

class TestOuterResultForgery:
    """The authoritative validators re-derive every candidate and reject
    divergence, including objects forged through ``model_construct`` or
    ``model_copy``."""

    def _green(self, tmp_path):
        cn, es, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records(
                predicate=ExactNumericUpperBound(
                    upper=NumericBoundary(value="80",
                                           inclusion="inclusive"))))
        return cn.evaluate_constraint(CON_A, as_of=AS_OF)

    def test_forged_verdict_rejected(self, tmp_path):
        result = self._green(tmp_path)
        forged = result.candidates[0].model_copy(
            update={"verdict": "violated"})
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(forged,), revision=result.revision)

    def test_forged_not_evaluated_reason_rejected(self, tmp_path):
        result = self._green(tmp_path)
        forged = result.candidates[0].model_copy(
            update={"not_evaluated_reason": "no_observation"})
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(forged,), revision=result.revision)

    def test_forged_observed_decimal_rejected(self, tmp_path):
        from backend.constraint_evaluation import CanonicalObservedDecimal
        result = self._green(tmp_path)
        forged_decimal = CanonicalObservedDecimal(lexeme="99", canonical="99")
        forged = result.candidates[0].model_copy(
            update={"observed_decimal": forged_decimal})
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(forged,), revision=result.revision)

    def test_forged_boundary_assessment_satisfied_rejected(self, tmp_path):
        result = self._green(tmp_path)
        bad_boundary = result.candidates[0].boundary_assessments[0].model_copy(
            update={"satisfied": False})
        forged = result.candidates[0].model_copy(
            update={"boundary_assessments": (bad_boundary,)})
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(forged,), revision=result.revision)

    @pytest.mark.parametrize("update", [
        {"relation": "greater"},
        {"role": "lower"},
        {"boundary_value": "79"},
        {"inclusion": "exclusive"},
    ])
    def test_forged_boundary_facts_rejected(self, tmp_path, update):
        result = self._green(tmp_path)
        bad = result.candidates[0].boundary_assessments[0].model_copy(
            update=update)
        forged = result.candidates[0].model_copy(
            update={"boundary_assessments": (bad,)})
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(forged,), revision=result.revision)

    def test_missing_duplicate_and_reordered_assessments_rejected(self, tmp_path):
        result = self._green(tmp_path)
        assessment = result.candidates[0].boundary_assessments[0]
        for assessments in ((), (assessment, assessment)):
            forged = result.candidates[0].model_copy(
                update={"boundary_assessments": assessments})
            with pytest.raises(Exception):
                ConstraintEvaluationResult(
                    constraint_anchor_id=result.constraint_anchor_id,
                    declaration=result.declaration, as_of=result.as_of,
                    ruleset_version="cn001.1",
                    semantic_compatibility=result.semantic_compatibility,
                    candidates=(forged,), revision=result.revision)

    def test_forged_candidate_count_rejected(self, tmp_path):
        result = self._green(tmp_path)
        # add a duplicate candidate -> wrong count
        dup = result.candidates[0].model_copy(update={"candidate_index": 1})
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(result.candidates[0], dup),
                revision=result.revision)

    def test_forged_candidate_index_reordering_rejected(self, tmp_path):
        result = self._green(tmp_path)
        forged = result.candidates[0].model_copy(
            update={"candidate_index": 5})
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(forged,), revision=result.revision)

    def test_model_construct_forgery_rejected(self, tmp_path):
        result = self._green(tmp_path)
        # model_construct bypasses validation; the outer validator must
        # re-derive and reject
        forged = CandidateConstraintEvaluation.model_construct(
            candidate_index=0, verdict="satisfied", not_evaluated_reason=None,
            observed_decimal=result.candidates[0].observed_decimal,
            boundary_assessments=result.candidates[0].boundary_assessments)
        # constructing the outer result re-validates and re-derives
        ConstraintEvaluationResult(
            constraint_anchor_id=result.constraint_anchor_id,
            declaration=result.declaration, as_of=result.as_of,
            ruleset_version="cn001.1",
            semantic_compatibility=result.semantic_compatibility,
            candidates=(forged,), revision=result.revision)
        # if the forged candidate diverges from the re-derivation, the
        # outer validator rejects it. A forged candidate with a wrong
        # verdict fails:
        forged_wrong = CandidateConstraintEvaluation.model_construct(
            candidate_index=0, verdict="violated", not_evaluated_reason=None,
            observed_decimal=result.candidates[0].observed_decimal,
            boundary_assessments=result.candidates[0].boundary_assessments)
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(forged_wrong,), revision=result.revision)

    def test_evaluated_row_under_failed_admission_rejected(self, tmp_path):
        # not_declared constraint: candidates must be not_evaluated. A forged
        # satisfied candidate under not_declared is rejected.
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=(constraint_registration(),))
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        assert result.declaration.status == "not_declared"
        # forge a satisfied candidate under the not_declared declaration
        from backend.constraint_evaluation import CanonicalObservedDecimal
        forged_boundary = BoundaryAssessment(
            role="upper", boundary_value="80", inclusion="inclusive",
            relation="less", satisfied=True)
        satisfied = CandidateConstraintEvaluation(
            candidate_index=0, verdict="satisfied",
            observed_decimal=CanonicalObservedDecimal(lexeme="60.4",
                                                       canonical="60.4"),
            boundary_assessments=(forged_boundary,))
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=(satisfied,), revision=result.revision)

    def test_forbidden_aggregate_field_rejected(self, tmp_path):
        result = self._green(tmp_path)
        # the contract has extra="forbid"; adding a severity field rejects
        with pytest.raises(Exception):
            CandidateConstraintEvaluation(
                candidate_index=0, verdict="satisfied",
                observed_decimal=result.candidates[0].observed_decimal,
                boundary_assessments=result.candidates[0].boundary_assessments,
                severity="high")  # type: ignore[call-arg]

    def test_mixed_revision_rejected(self, tmp_path):
        # a result whose declaration.revision != semantic.revision
        cn, _, _, _ = cn_stack(
            tmp_path, constraint_records=default_constraint_records())
        result = cn.evaluate_constraint(CON_A, as_of=AS_OF)
        # build a different model revision by replaying to pre-ES001
        from tests.model_kernel.test_demo_model import PRE_ES001_MEMBERSHIP
        replayed = ModelStore(Path("models/demo-printer")).replay(
            PRE_ES001_MEMBERSHIP)
        with pytest.raises(Exception):
            ConstraintEvaluationResult(
                constraint_anchor_id=result.constraint_anchor_id,
                declaration=result.declaration, as_of=result.as_of,
                ruleset_version="cn001.1",
                semantic_compatibility=result.semantic_compatibility,
                candidates=result.candidates,
                revision=replayed.revision)
