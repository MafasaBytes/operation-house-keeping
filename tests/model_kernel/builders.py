"""Shared fixture builders for the MK-001 test suite."""

from datetime import UTC, datetime

from backend.model_kernel.canonical import build_record
from backend.model_kernel.contracts import (
    AuthorityRef,
    EntityRegistration,
    LifecycleViewContext,
    OwnerDeclarationEvidence,
    RelationshipAssertion,
    RelationshipTypeDefinition,
    RelationshipWithdrawal,
    ViewIndependentContext,
)
from backend.model_kernel.store import ModelStore
from backend.system_identity import EntityAnchor

T0 = datetime(2026, 8, 8, 12, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="mk001_demo_fixture",
                         method="manual_declaration")
AS_BUILT = LifecycleViewContext(kind="lifecycle_view", view="as_built")
AS_DESIGNED = LifecycleViewContext(kind="lifecycle_view", view="as_designed")
VIEW_FREE = ViewIndependentContext(kind="view_independent")
EVIDENCE = (OwnerDeclarationEvidence(kind="owner_declaration",
                                     statement="synthetic test structure"),)

ENT_A = "ent_" + "a" * 32
ENT_B = "ent_" + "b" * 32
ENT_C = "ent_" + "c" * 32
ENT_D = "ent_" + "d" * 32
ENT_TYPE = "ent_" + "e" * 32


def anchor(anchor_id=ENT_A, kind="physical_instance", name="Demo entity"):
    return EntityAnchor(anchor_id=anchor_id, namespace="demo-printer",
                        display_name=name, referent_kind=kind)


def registration(anchor_id=ENT_A, kind="physical_instance", note=""):
    return build_record(EntityRegistration,
                        anchor=anchor(anchor_id, kind=kind),
                        recorded_at=T0, authority=AUTHORITY, note=note)


def contains_type(**overrides):
    fields = dict(
        type_name="contains", forward_label="contains",
        inverse_label="is contained in", directionality="directed",
        source_referent_kinds=("logical_instance", "physical_instance"),
        target_referent_kinds=("logical_instance", "physical_instance"),
        self_relation_allowed=False, hierarchy_semantics="containment",
        context_requirement="lifecycle_view", supersedes=None,
        recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(RelationshipTypeDefinition, **fields)


def instance_of_type(**overrides):
    fields = dict(
        type_name="instance_of", forward_label="is an instance of",
        inverse_label="has instance", directionality="directed",
        source_referent_kinds=("logical_instance", "physical_instance"),
        target_referent_kinds=("type_definition",),
        self_relation_allowed=False, hierarchy_semantics="none",
        context_requirement="view_independent", supersedes=None,
        recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return build_record(RelationshipTypeDefinition, **fields)


def assertion(type_record, source=ENT_A, target=ENT_B, context=AS_BUILT,
              supersedes=None, note="", evidence=EVIDENCE, recorded_at=T0):
    return build_record(RelationshipAssertion, type_id=type_record.record_id,
                        source_anchor_id=source, target_anchor_id=target,
                        context=context, evidence=evidence,
                        supersedes=supersedes, recorded_at=recorded_at,
                        authority=AUTHORITY, note=note)


def withdrawal(target_assertion, note=""):
    return build_record(RelationshipWithdrawal,
                        withdraws=target_assertion.record_id,
                        recorded_at=T0, authority=AUTHORITY, note=note)


def store_with(tmp_path, *records, model_id="demo-printer"):
    store = ModelStore(tmp_path / model_id)
    for record in records:
        store.append(record)
    return store


def containment_world(tmp_path, *extra):
    """A minimal valid world: contains type + registrations A, B."""
    return store_with(tmp_path, contains_type(), registration(ENT_A),
                      registration(ENT_B), *extra)


# ------------------------------------------------------------ VM-001 vars
VAR_A = "var_" + "1" * 32
VAR_B = "var_" + "2" * 32
VAR_C = "var_" + "3" * 32


def variable_anchor(anchor_id=VAR_A, owner=ENT_A, name="Demo variable",
                    role=None):
    from backend.system_identity import VariableAnchor

    return VariableAnchor(anchor_id=anchor_id, entity_anchor_id=owner,
                          namespace="demo-printer", display_name=name,
                          role_name=role)


def variable_registration(anchor_id=VAR_A, owner=ENT_A, name="Demo variable",
                          note="", role=None):
    from backend.model_kernel.contracts import VariableRegistration

    return build_record(VariableRegistration,
                        anchor=variable_anchor(anchor_id, owner, name, role),
                        recorded_at=T0, authority=AUTHORITY, note=note)


# ------------------------------------------------------- VS-001 specs
SPEC_EVIDENCE = (OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="synthetic model-side value specification"),)


def declared_unit(code="degree_celsius", system_edition="ohk-units-1"):
    from backend.model_kernel.contracts import DeclaredUnit, UnitReference

    return DeclaredUnit(kind="declared",
                        unit=UnitReference(system_id="project_local",
                                           system_edition=system_edition,
                                           code=code))


def specification(variable_anchor_id=VAR_A, value_shape="number",
                  nullable=False, unit=None, evidence=SPEC_EVIDENCE,
                  supersedes=(), recorded_at=T0, note="", **overrides):
    from backend.model_kernel.contracts import VariableValueSpecification

    fields = dict(variable_anchor_id=variable_anchor_id,
                  value_shape=value_shape, nullable=nullable,
                  unit=unit if unit is not None else declared_unit(),
                  evidence=evidence, supersedes=supersedes,
                  recorded_at=recorded_at, authority=AUTHORITY, note=note)
    fields.update(overrides)
    return build_record(VariableValueSpecification, **fields)


# ---------------------------------------------------------- CN-001 records
CON_A = "con_" + "a" * 32
CON_B = "con_" + "b" * 32
CONSTRAINT_EVIDENCE = (OwnerDeclarationEvidence(
    kind="owner_declaration",
    statement="synthetic test constraint registration"),)


def quantity_kind(code="temperature", system_edition="ohk-semantics-1"):
    from backend.model_kernel.contracts import QuantityKindReference

    return QuantityKindReference(system_id="project_local",
                                 system_edition=system_edition, code=code)


def observation_role(code="measured", system_edition="ohk-semantics-1"):
    from backend.model_kernel.contracts import ObservationRoleReference

    return ObservationRoleReference(system_id="project_local",
                                     system_edition=system_edition, code=code)


def numeric_boundary(value="80", inclusion="inclusive"):
    from backend.model_kernel.contracts import NumericBoundary

    return NumericBoundary(value=value, inclusion=inclusion)


def upper_bound(value="80", inclusion="inclusive"):
    from backend.model_kernel.contracts import ExactNumericUpperBound

    return ExactNumericUpperBound(
        upper=numeric_boundary(value=value, inclusion=inclusion))


def constraint_signature():
    from backend.model_kernel.contracts import (
        ConstraintSemanticSignature, UnitReference)

    return ConstraintSemanticSignature(
        quantity_kind=quantity_kind(), observation_role=observation_role(),
        unit=UnitReference(system_id="project_local",
                           system_edition="ohk-units-1",
                           code="degree_celsius"))


def constraint_registration(constraint_anchor_id=CON_A,
                            variable_anchor_id=VAR_A,
                            evidence=CONSTRAINT_EVIDENCE, recorded_at=T0,
                            note="", **overrides):
    from backend.model_kernel.contracts import ConstraintRegistration
    from backend.system_identity import ConstraintAnchor

    fields = dict(anchor=ConstraintAnchor(
                      anchor_id=constraint_anchor_id,
                      namespace="demo-printer",
                      display_name="Synthetic constraint"),
                  variable_anchor_id=variable_anchor_id, evidence=evidence,
                  recorded_at=recorded_at, authority=AUTHORITY, note=note)
    fields.update(overrides)
    return build_record(ConstraintRegistration, **fields)


def constraint_declaration(constraint_anchor_id=CON_A,
                           expected_semantics=None,
                           predicate=None, evidence=CONSTRAINT_EVIDENCE,
                           supersedes=(), recorded_at=T0, note="", **overrides):
    from backend.model_kernel.contracts import VariableConstraintDeclaration

    if predicate is None:
        predicate = upper_bound()
    fields = dict(constraint_anchor_id=constraint_anchor_id,
                  expected_semantics=(expected_semantics
                                      if expected_semantics is not None
                                      else constraint_signature()),
                  predicate=predicate, evidence=evidence,
                  supersedes=supersedes, recorded_at=recorded_at,
                  authority=AUTHORITY, note=note)
    fields.update(overrides)
    return build_record(VariableConstraintDeclaration, **fields)
