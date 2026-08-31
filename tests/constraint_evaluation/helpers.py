"""CN-001 Slice B test fixtures.

The committed ``models/demo-printer`` ledger contains the two accepted Slice C
fixture records. Additional constraint records are built into an
isolated ``tmp_path`` model store that COPIES the committed demo records
and appends synthetic ``crg_`` / ``vcn_`` records. The committed bindings,
interpretations, and temporal stack are read-only.

The default fixture targets ``HOTEND`` with ``expected_semantics`` matching
the demo's declared semantics (temperature / measured_actual /
degree_celsius) so the lock gates pass and the predicate comparison runs.
Knobs vary one piece at a time to reach each refusal reason.
"""

from datetime import UTC, datetime
from pathlib import Path

from backend.constraint_evaluation import ConstraintEvaluationQueries
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.model_kernel import (
    AuthorityRef, ConstraintRegistration, ConstraintSemanticSignature,
    ModelQueries, ModelStore, OwnerDeclarationEvidence,
    UnitReference, VariableConstraintDeclaration, build_record)
from backend.model_state import ModelStateQueries
from backend.observation_compatibility import ObservationCompatibilityQueries
from backend.semantic_compatibility import SemanticCompatibilityQueries
from backend.source_interpretation import InterpretationResolver, InterpretationStore
from backend.system_identity import ConstraintAnchor

from tests.model_state.helpers import full_timeline_stack
from tests.observation_compatibility.test_demo_compatibility import (
    AS_OF, EXTRUDER, HOTEND)

T0 = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="cn001_fixture",
                         method="manual_declaration")
EVIDENCE = (OwnerDeclarationEvidence(
    kind="owner_declaration", statement="synthetic test constraint"),)
DEMO_MODEL = Path("models/demo-printer")
DEMO_BINDINGS = Path("bindings/demo-printer")
DEMO_INTERPRETATIONS = Path("interpretations/demo-printer")

# The demo's declared semantics for HOTEND (read once from the committed
# model). The constraint's ``expected_semantics`` defaults to these so the
# quantity-kind / observation-role / unit-identity lock gates pass.
_DEMO = ModelStore(DEMO_MODEL).load()
_DEMO_SEM = ModelQueries(_DEMO).variable_semantics(HOTEND)
_DEMO_SPEC = ModelQueries(_DEMO).variable_value_specification(HOTEND)
DEMO_QUANTITY_KIND = _DEMO_SEM.quantity_kind.declaration.declaration.quantity_kind
DEMO_OBSERVATION_ROLE = _DEMO_SEM.observation_role.declaration.declaration.observation_role
DEMO_UNIT = _DEMO_SPEC.specification.unit.unit


def expected_semantics(*, quantity_kind=DEMO_QUANTITY_KIND,
                       observation_role=DEMO_OBSERVATION_ROLE,
                       unit=DEMO_UNIT) -> ConstraintSemanticSignature:
    return ConstraintSemanticSignature(
        quantity_kind=quantity_kind, observation_role=observation_role,
        unit=unit)


def _make_other_qk():
    from backend.model_kernel import QuantityKindReference
    return QuantityKindReference(system_id="project_local",
                                  system_edition="ohk-quantities-1",
                                  code="pressure")


def _make_other_or():
    from backend.model_kernel import ObservationRoleReference
    return ObservationRoleReference(
        system_id="project_local",
        system_edition="ohk-observation-roles-1",
        code="commanded_target")


def _make_other_unit():
    return UnitReference(system_id="project_local",
                          system_edition="ohk-units-1",
                          code="pascal")


_OTHER_QK = _make_other_qk()
_OTHER_OR = _make_other_or()
_OTHER_UNIT = _make_other_unit()


def other_quantity_kind_ref():
    return _OTHER_QK


def other_observation_role_ref():
    return _OTHER_OR


def other_unit_ref():
    return _OTHER_UNIT


def constraint_registration(constraint_anchor_id="con_" + "a" * 32,
                            variable_anchor_id=HOTEND,
                            evidence=EVIDENCE, recorded_at=T0,
                            note="", **overrides):
    fields = dict(
        anchor=ConstraintAnchor(anchor_id=constraint_anchor_id,
                                namespace="demo-printer",
                                display_name="Synthetic constraint"),
        variable_anchor_id=variable_anchor_id, evidence=evidence,
        recorded_at=recorded_at, authority=AUTHORITY, note=note)
    fields.update(overrides)
    return build_record(ConstraintRegistration, **fields)


def constraint_declaration(constraint_anchor_id="con_" + "a" * 32,
                            expected_sem_sig=None, predicate=None,
                            evidence=EVIDENCE, supersedes=(),
                            recorded_at=T0, note="", **overrides):
    from backend.model_kernel import (ExactNumericUpperBound, NumericBoundary)
    if predicate is None:
        predicate = ExactNumericUpperBound(
            upper=NumericBoundary(value="80", inclusion="inclusive"))
    fields = dict(
        constraint_anchor_id=constraint_anchor_id,
        expected_semantics=(expected_sem_sig if expected_sem_sig is not None
                            else expected_semantics()),
        predicate=predicate, evidence=evidence, supersedes=supersedes,
        recorded_at=recorded_at, authority=AUTHORITY, note=note)
    fields.update(overrides)
    return build_record(VariableConstraintDeclaration, **fields)


_RECORD_KIND_ORDER = {
    "entity_registration": 0,
    "relationship_type_definition": 1,
    "variable_registration": 2,
    "relationship_assertion": 3,
    "variable_value_specification": 4,
    "variable_semantic_declaration": 5,
    "constraint_registration": 6,
    "variable_constraint_declaration": 7,
}


def _sort_by_dependency(records):
    """Sort records so type definitions precede the assertions that
    reference them, satisfying per-append validation."""
    return sorted(records, key=lambda r: (_RECORD_KIND_ORDER.get(
        getattr(r, "record_kind", ""), 99), r.record_id))


def cn_stack(tmp_path, *, constraint_records=(), model_records_override=None,
             interpretations_path=DEMO_INTERPRETATIONS, binding_records=None,
             include_committed_constraints=False, model_membership=None):
    """Build a full CN evaluation stack in an isolated ``tmp_path`` model
    store. The committed demo records are copied; synthetic constraint
    records are appended. The committed bindings and interpretations are
    read-only unless ``binding_records`` or ``interpretations_path`` overrides
    them."""
    import shutil
    temporal = full_timeline_stack(tmp_path)
    dst_dir = tmp_path / "model" / "demo-printer"
    if model_records_override is None:
        # Copy the entire committed demo model directory so ``load()``
        # validates the full collection at once (per-append validation
        # would reject forward references from rel_ to rtd_ records that
        # sort later alphabetically). Constraint records are appended
        # afterwards one at a time.
        shutil.copytree(DEMO_MODEL, dst_dir)
        if model_membership is not None:
            retained = {f"{record_id}.json" for record_id in model_membership}
            for path in (dst_dir / "records").glob("*.json"):
                if path.name not in retained:
                    path.unlink()
        if not include_committed_constraints:
            # Slice B fixtures retain their accepted isolated pre-CN model.
            # Only disposable copied files are removed; the authoritative
            # ledger is never touched.
            for prefix in ("crg_", "vcn_", "srg_", "std_", "stw_"):
                for path in (dst_dir / "records").glob(f"{prefix}*.json"):
                    path.unlink()
        dst_store = ModelStore(dst_dir)
    else:
        dst_store = ModelStore(dst_dir)
        for record in _sort_by_dependency(model_records_override):
            dst_store.append(record)
    for record in constraint_records:
        dst_store.append(record)
    loaded = dst_store.load()
    if binding_records is not None:
        bstore = BindingStore(tmp_path / "bindings" / "demo-printer")
        for record in binding_records:
            bstore.append(record)
        resolver = BindingResolver(bstore.load())
    else:
        resolver = BindingResolver(BindingStore(DEMO_BINDINGS).load())
    state = ModelStateQueries(loaded, resolver, temporal)
    values = ObservationCompatibilityQueries(state)
    interpretations = InterpretationStore(interpretations_path).load()
    es = SemanticCompatibilityQueries(values, InterpretationResolver(interpretations))
    cn = ConstraintEvaluationQueries(es)
    return cn, es, values, temporal


def default_constraint_records(*, predicate=None, expected_semantics_sig=None,
                               constraint_anchor_id="con_" + "a" * 32):
    """One registration + one declaration targeting HOTEND with the demo's
    declared semantics (lock-passing) and an upper bound of 80 inclusive."""
    return (
        constraint_registration(constraint_anchor_id=constraint_anchor_id),
        constraint_declaration(constraint_anchor_id=constraint_anchor_id,
                               expected_sem_sig=expected_semantics_sig,
                               predicate=predicate),
    )


def stack_with_default_constraint(tmp_path, **kwargs):
    return cn_stack(tmp_path, constraint_records=default_constraint_records(
        **kwargs))


def custom_stack(tmp_path, *, model_records, binding_records,
                  temporal=None, interpretations_path=None,
                  interpretation_records=None):
    """Build a fully custom CN stack for fixtures the committed demo cannot
    express (non-numeric VSP, nullable null, divergent anchors, multiple
    locators, a second variable, etc.)."""
    from backend.identity_binding.store import BindingStore
    from backend.identity_binding.resolver import BindingResolver
    from backend.identity_binding.canonical import build_record as ib_build
    if temporal is None:
        temporal = full_timeline_stack(tmp_path)
    store = ModelStore(tmp_path / "model" / "demo-printer")
    for record in model_records:
        store.append(record)
    loaded = store.load()
    bstore = BindingStore(tmp_path / "bindings" / "demo-printer")
    for record in binding_records:
        bstore.append(record)
    resolver = BindingResolver(bstore.load())
    state = ModelStateQueries(loaded, resolver, temporal)
    values = ObservationCompatibilityQueries(state)
    if interpretation_records is not None:
        from backend.source_interpretation import InterpretationStore
        from pathlib import Path as _P
        ipath = tmp_path / "interpretations" / "demo-printer"
        istore = InterpretationStore(ipath)
        for rec in interpretation_records:
            istore.append(rec)
        interpretations = istore.load()
    elif interpretations_path is not None:
        from backend.source_interpretation import InterpretationStore
        interpretations = InterpretationStore(interpretations_path).load()
    else:
        from backend.source_interpretation import InterpretationStore
        interpretations = InterpretationStore(DEMO_INTERPRETATIONS).load()
    es = SemanticCompatibilityQueries(values, InterpretationResolver(interpretations))
    cn = ConstraintEvaluationQueries(es)
    return cn, es, values, temporal


def craft_value(temporal, *, value_json, json_type, declared_unit=None):
    """Insert a crafted occurrence reusing a real attempt row (Tier C)."""
    from tests.observation_compatibility.helpers import craft_occurrence, SUBJECT, PROP_TEMP
    return craft_occurrence(temporal, value_json=value_json, json_type=json_type,
                             declared_unit=declared_unit)


EARLY = datetime(2026, 8, 7, 19, 0, 0, tzinfo=UTC)
LATE = datetime(2026, 8, 7, 23, 0, 0, tzinfo=UTC)
CON_A = "con_" + "a" * 32
CON_B = "con_" + "b" * 32
CON_C = "con_" + "c" * 32
