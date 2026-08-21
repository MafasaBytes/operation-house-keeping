"""PT-001 Slice A red baseline for the five immutable port claim records."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.system_identity import PortAnchor


T0 = datetime(2026, 8, 20, 12, 0, tzinfo=UTC)
AUTHORITY = kernel.AuthorityRef(
    kind="test_fixture", agent="pt001_test_fixture",
    method="manual_declaration")
CONTEXT = kernel.LifecycleViewContext(
    kind="lifecycle_view", view="as_designed")
EVIDENCE = (kernel.OwnerDeclarationEvidence(
    kind="owner_declaration", statement="synthetic PT-001 claim"),)
ENT = "ent_" + "a" * 32
PORT_A = "prt_" + "1" * 32
PORT_B = "prt_" + "2" * 32
PORT_C = "prt_" + "3" * 32


def anchor(anchor_id=PORT_A):
    return PortAnchor(anchor_id=anchor_id, namespace="demo-printer",
                      display_name="Synthetic interface")


def domain_token(code="electrical"):
    return kernel.InterfaceDomainToken(
        token_kind="interface_domain", system_id="project_local",
        system_edition="ohk-interface-domains-1", code=code)


def type_token(code="synthetic_discrete_signal"):
    return kernel.InterfaceTypeToken(
        token_kind="interface_type", system_id="project_local",
        system_edition="ohk-interface-types-1", code=code)


def declaration_body(dimension="interface_domain", value=None):
    if dimension == "interface_domain":
        return kernel.InterfaceDomainDeclaration(
            dimension=dimension,
            value=domain_token() if value is None else value)
    if dimension == "direction_role":
        return kernel.DirectionRoleDeclaration(
            dimension=dimension, value="output" if value is None else value)
    return kernel.InterfaceTypeDeclaration(
        dimension=dimension, value=type_token() if value is None else value)


def registration(**overrides):
    fields = dict(anchor=anchor(), owner_entity_anchor_id=ENT,
                  evidence=EVIDENCE, recorded_at=T0, authority=AUTHORITY,
                  note="")
    fields.update(overrides)
    return kernel.build_record(kernel.PortRegistration, **fields)


def interface(port=PORT_A, dimension="interface_domain", **overrides):
    fields = dict(port_anchor_id=port, context=CONTEXT,
                  declaration=declaration_body(dimension), evidence=EVIDENCE,
                  supersedes=(), recorded_at=T0, authority=AUTHORITY, note="")
    fields.update(overrides)
    return kernel.build_record(kernel.PortInterfaceDeclaration, **fields)


def connection(endpoints=(PORT_A, PORT_B), **overrides):
    fields = dict(endpoint_port_anchor_ids=endpoints, context=CONTEXT,
                  evidence=EVIDENCE, supersedes=(), recorded_at=T0,
                  authority=AUTHORITY, note="")
    fields.update(overrides)
    return kernel.build_record(kernel.PortConnectionAssertion, **fields)


def dimension_basis(dimension="interface_domain"):
    left = interface(PORT_A, dimension)
    right = interface(PORT_B, dimension)
    return kernel.CompatibilityDimensionBasis(
        dimension=dimension,
        citations=(
            kernel.PortInterfaceCitation(
                port_anchor_id=PORT_A, declaration_record_id=left.record_id),
            kernel.PortInterfaceCitation(
                port_anchor_id=PORT_B, declaration_record_id=right.record_id),
        ))


def compatibility(endpoints=(PORT_A, PORT_B), **overrides):
    fields = dict(
        endpoint_port_anchor_ids=endpoints, context=CONTEXT,
        outcome="declared_compatible",
        basis=kernel.PortCompatibilityBasis(
            statement="Synthetic explicit compatibility claim",
            dimensions=(dimension_basis(),)),
        evidence=EVIDENCE, supersedes=(), recorded_at=T0,
        authority=AUTHORITY, note="")
    fields.update(overrides)
    return kernel.build_record(kernel.PortCompatibilityDeclaration, **fields)


def withdrawal(withdraws="pif_" + "a" * 64, **overrides):
    fields = dict(withdraws=withdraws, recorded_at=T0,
                  authority=AUTHORITY, note="")
    fields.update(overrides)
    return kernel.build_record(kernel.PortClaimWithdrawal, **fields)


def test_five_record_shapes_are_exact_and_content_ids_use_accepted_prefixes():
    records = (
        (registration(), "port_registration", "prg", (
            "record_kind", "schema_version", "record_id", "anchor",
            "owner_entity_anchor_id", "evidence", "recorded_at", "authority",
            "note")),
        (interface(), "port_interface_declaration", "pif", (
            "record_kind", "schema_version", "record_id", "port_anchor_id",
            "context", "declaration", "evidence", "supersedes",
            "recorded_at", "authority", "note")),
        (connection(), "port_connection_assertion", "pcn", (
            "record_kind", "schema_version", "record_id",
            "endpoint_port_anchor_ids", "context", "evidence", "supersedes",
            "recorded_at", "authority", "note")),
        (compatibility(), "port_compatibility_declaration", "pcm", (
            "record_kind", "schema_version", "record_id",
            "endpoint_port_anchor_ids", "context", "outcome", "basis",
            "evidence", "supersedes", "recorded_at", "authority", "note")),
        (withdrawal(), "port_claim_withdrawal", "ptw", (
            "record_kind", "schema_version", "record_id", "withdraws",
            "recorded_at", "authority", "note")),
    )
    for record, kind, prefix, fields in records:
        assert record.record_kind == kind
        assert record.schema_version == "1"
        assert record.record_id.startswith(prefix + "_")
        assert len(record.record_id) == 4 + 64
        assert tuple(type(record).model_fields) == fields


def test_registration_embeds_the_complete_anchor_and_requires_evidence():
    record = registration()
    assert record.anchor == anchor()
    assert record.owner_entity_anchor_id == ENT
    with pytest.raises(kernel.ModelIntegrityError):
        registration(evidence=())


@pytest.mark.parametrize("dimension,value", [
    ("direction_role", "input"),
    ("direction_role", "output"),
    ("direction_role", "bidirectional"),
    ("direction_role", "non_directional"),
    ("interface_domain", None),
    ("interface_type", None),
])
def test_interface_declaration_union_accepts_exact_dimensions(dimension, value):
    body = declaration_body(dimension, value)
    record = interface(dimension=dimension, declaration=body)
    assert record.declaration == body


@pytest.mark.parametrize("value", ["in", "out", "both", "unknown", ""])
def test_direction_role_is_an_exact_closed_endpoint_vocabulary(value):
    with pytest.raises(ValidationError):
        declaration_body("direction_role", value)


def test_domain_and_type_tokens_are_distinct_and_not_substitutable():
    assert domain_token().token_kind == "interface_domain"
    assert type_token().token_kind == "interface_type"
    with pytest.raises(ValidationError):
        kernel.InterfaceDomainDeclaration(
            dimension="interface_domain", value=type_token())
    with pytest.raises(ValidationError):
        kernel.InterfaceTypeDeclaration(
            dimension="interface_type", value=domain_token())
    with pytest.raises(ValidationError):
        kernel.InterfaceDomainToken(
            token_kind="interface_type", system_id="project_local",
            system_edition="ohk-interface-domains-1", code="electrical")


@pytest.mark.parametrize("system_id", [
    "project_local", "iec", "iso", "opc-ua", "vendor.example",
])
@pytest.mark.parametrize("token_factory", [
    kernel.InterfaceDomainToken,
    kernel.InterfaceTypeToken,
])
def test_interface_tokens_accept_bounded_qualified_system_ids(
        token_factory, system_id):
    token_kind = (
        "interface_domain"
        if token_factory is kernel.InterfaceDomainToken
        else "interface_type"
    )
    token = token_factory(
        token_kind=token_kind,
        system_id=system_id,
        system_edition="1",
        code="power",
    )
    assert token.system_id == system_id


@pytest.mark.parametrize("system_id", [
    "", "IEC", "has space", "path/name", "café", "a" * 129,
    "iec\n", "iec\nignored",
])
@pytest.mark.parametrize("token_factory", [
    kernel.InterfaceDomainToken,
    kernel.InterfaceTypeToken,
])
def test_interface_tokens_reject_invalid_qualified_system_ids(
        token_factory, system_id):
    token_kind = (
        "interface_domain"
        if token_factory is kernel.InterfaceDomainToken
        else "interface_type"
    )
    with pytest.raises(ValidationError):
        token_factory(
            token_kind=token_kind,
            system_id=system_id,
            system_edition="1",
            code="power",
        )


def test_interface_token_public_field_shapes_remain_exact():
    assert tuple(kernel.InterfaceDomainToken.model_fields) == (
        "token_kind", "system_id", "system_edition", "code")
    assert tuple(kernel.InterfaceTypeToken.model_fields) == (
        "token_kind", "system_id", "system_edition", "code")


@pytest.mark.parametrize("endpoints", [
    (PORT_A,),
    (PORT_A, PORT_A),
    (PORT_A, PORT_B, PORT_A),
    tuple(f"prt_{index:032x}" for index in range(65)),
])
def test_connection_rejects_too_few_duplicate_and_too_many_endpoints(endpoints):
    with pytest.raises(kernel.ModelIntegrityError):
        connection(endpoints)


def test_connection_accepts_bounds_sorts_without_changing_cardinality():
    lower = connection((PORT_B, PORT_A))
    assert lower.endpoint_port_anchor_ids == (PORT_A, PORT_B)
    assert connection((PORT_A, PORT_B)).record_id == lower.record_id
    upper_input = tuple(
        reversed(tuple(f"prt_{index:032x}" for index in range(64))))
    upper = connection(upper_input)
    assert len(upper.endpoint_port_anchor_ids) == 64
    assert upper.endpoint_port_anchor_ids == tuple(sorted(upper_input))


def test_pcm_pair_and_basis_have_normative_canonical_order():
    domain = dimension_basis("interface_domain")
    direction = dimension_basis("direction_role")
    type_ = dimension_basis("interface_type")
    basis = kernel.PortCompatibilityBasis(
        statement="Synthetic basis", dimensions=(type_, domain, direction))
    record = compatibility((PORT_B, PORT_A), basis=basis)
    assert record.endpoint_port_anchor_ids == (PORT_A, PORT_B)
    assert tuple(item.dimension for item in record.basis.dimensions) == (
        "interface_domain", "direction_role", "interface_type")
    assert all(tuple(c.port_anchor_id for c in item.citations)
               == (PORT_A, PORT_B) for item in record.basis.dimensions)


def test_pcm_basis_rejects_empty_statement_dimensions_and_duplicates():
    item = dimension_basis()
    with pytest.raises(ValidationError):
        kernel.PortCompatibilityBasis(statement="", dimensions=(item,))
    with pytest.raises(ValidationError):
        kernel.PortCompatibilityBasis(statement="Synthetic", dimensions=())
    with pytest.raises(ValidationError):
        kernel.PortCompatibilityBasis(
            statement="Synthetic", dimensions=(item, item))
    with pytest.raises(ValidationError):
        kernel.CompatibilityDimensionBasis(
            dimension="interface_domain", citations=(item.citations[0],) * 2)


@pytest.mark.parametrize("target", [
    "pif_" + "a" * 64, "pcn_" + "b" * 64, "pcm_" + "c" * 64,
])
def test_withdrawal_targets_exactly_the_three_correctable_claim_kinds(target):
    assert withdrawal(target).withdraws == target


@pytest.mark.parametrize("target", [
    "prg_" + "a" * 64, "ptw_" + "a" * 64,
    "rel_" + "a" * 64, "pif_NOT_HEX",
])
def test_withdrawal_rejects_registration_withdrawal_non_pt_and_bad_ids(target):
    with pytest.raises(kernel.ModelIntegrityError):
        withdrawal(target)


@pytest.mark.parametrize("factory,extra", [
    (registration, {"context": CONTEXT}),
    (registration, {"supersedes": ()}),
    (connection, {"direction": "output"}),
    (connection, {"flow": "active"}),
    (connection, {"compatible": True}),
    (connection, {"source_port_anchor_id": PORT_A}),
    (connection, {"connection_anchor_id": "prt_" + "f" * 32}),
    (compatibility, {"severity": "safe"}),
    (withdrawal, {"evidence": EVIDENCE}),
])
def test_records_forbid_unaccepted_identity_state_flow_and_safety_fields(
        factory, extra):
    with pytest.raises(kernel.ModelIntegrityError):
        factory(**extra)


def test_model_kernel_public_exports_add_exactly_the_accepted_pt_names():
    added = {
        "PortRegistration", "InterfaceDomainToken", "InterfaceTypeToken",
        "InterfaceDomainDeclaration", "DirectionRoleDeclaration",
        "InterfaceTypeDeclaration", "PortInterfaceDeclaration",
        "PortConnectionAssertion", "PortInterfaceCitation",
        "CompatibilityDimensionBasis", "PortCompatibilityBasis",
        "PortCompatibilityDeclaration", "PortClaimWithdrawal",
        "ModelQueryMaterial", "PortResult", "EntityPortsResult",
        "InterfaceDimensionResult", "PortInterfaceResult",
        "PortAssertionResult", "ConnectionRootResult",
        "ExactConnectionsResult", "IncidentConnectionsResult",
        "ContainingConnectionsResult", "EndpointInterfaceResult",
        "InterfaceCompatibilityResult",
    }
    old = {
        "EntityRegistration", "VariableRegistration",
        "VariableValueSpecification", "VariableSemanticDeclaration",
        "ConstraintRegistration", "VariableConstraintDeclaration",
        "RelationshipTypeDefinition", "RelationshipAssertion",
        "RelationshipWithdrawal", "ModelRecord", "AssertionContext",
        "LifecycleViewContext", "ViewIndependentContext", "LifecycleView",
        "ReferentKind", "AuthorityRef", "EvidenceRef",
        "OwnerDeclarationEvidence", "ModelRecordEvidence",
        "IdentityBindingRecordEvidence", "SourceRawRecordEvidence",
        "StructuralSourceLocatorEvidence", "UnitReference", "DeclaredUnit",
        "UnitNotDeclared", "UnitDeclaration", "CanonicalDecimal",
        "canonical_constraint_decimal", "NumericBoundary",
        "ExactNumericLowerBound", "ExactNumericUpperBound",
        "ExactNumericInterval", "ConstraintSemanticSignature",
        "ConstraintPredicate", "QuantityKindReference",
        "ObservationRoleReference", "QuantityKindDeclaration",
        "ObservationRoleDeclaration", "SemanticDimensionDeclaration",
        "TemporalOccurrenceEvidence", "ModelKernelError",
        "ModelConfigurationError", "ModelIntegrityError", "ModelQueryError",
        "ModelRevision", "ConstraintDeclarationResult",
        "VariableConstraintCollectionResult", "EvidenceDisclosure",
        "RelationshipSummary", "LineageConflict", "RelationshipsResult",
        "RegistrationSummary", "VariableRegistrationSummary",
        "VariableResult", "VariableSpecificationResult",
        "SemanticDimensionResult", "VariableSemanticsResult", "EntityResult",
        "EntityVariablesResult", "ParentResult", "ParentStatus",
        "TraversalAnnotation", "ChildEntry", "ChildrenResult",
        "TraversalStep", "TraversalBlock", "TraversalResult", "CycleReport",
        "ParentConflictReport", "HierarchyHealth", "build_record",
        "ModelStore", "LoadedModel", "ModelQueries",
    }
    assert set(kernel.__all__) == old | added
    assert len(kernel.__all__) == len(old | added)
