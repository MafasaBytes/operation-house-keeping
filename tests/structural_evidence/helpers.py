"""Shared SN-001c test builders: tmp binding sets, claim sets, resolvers.

Tier-2 style: synthetic records appended through the REAL identity_binding
store and resolved by the REAL resolver; claim sets built through the real
contracts. Nothing here touches the committed ledgers.
"""

from datetime import UTC, datetime

from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.identity_binding.canonical import build_record as ib_build
from backend.identity_binding.contracts import (
    AnchorDeclaration,
    AppliesScope,
    AuthorityRef,
    BindingAssertion,
    BindingRetraction,
    DeclaredBoundary,
    UnboundedBoundary,
)
from backend.identity_binding.resolver import BindingResolver
from backend.identity_binding.store import BindingStore
from backend.structural_evidence.contracts import (
    DeclaredEngineeringContext,
    LabelFieldRef,
    QuantityFieldRef,
    SourceContainmentClaim,
    SourceNativeField,
    SourceStructuralClaim,
    SourceStructuralClaimSet,
    UnknownEngineeringContext,
)
from backend.structural_evidence.locators import (
    CsvCellLocator,
    CsvRowLocator,
    StepDefinitionLocator,
    StructuralAddress,
    StructuralSourceRef,
)
from backend.structural_evidence.rules import (
    SUBJECT_RULES,
    to_source_subject_ref,
)
from backend.system_identity import EntityAnchor

T0 = datetime(2026, 8, 11, 12, 0, 0, tzinfo=UTC)
RESOLUTION_AT = datetime(2026, 8, 11, 13, 0, 0, tzinfo=UTC)
AUTHORITY = AuthorityRef(kind="test_fixture", agent="sn001_showcase_fixture",
                         method="manual_declaration")
UNBOUNDED = AppliesScope(
    axis="ingestion_received_at",
    start_boundary=UnboundedBoundary(kind="unbounded"),
    end_boundary=UnboundedBoundary(kind="unbounded"),
    interval_semantics="half_open")
UNKNOWN = UnknownEngineeringContext(kind="unknown",
                                    reason="authority_has_not_declared")

CSV_EXTRACTOR = ExtractorIdentity(
    name="csv_extractor", version="1.1.0", toolchain="python-stdlib-csv",
    config_fingerprint="6f1c2a9d0b3e4517")
STEP_EXTRACTOR = ExtractorIdentity(
    name="step_extractor", version="1.0.0",
    toolchain="cadquery-ocp 7.9.3.1.1",
    config_fingerprint="2b7e91c4a05d6f38")

ENT_X = "ent_" + "1a" * 16
ENT_Y = "ent_" + "2b" * 16


def bom_source(source_id="bom-src") -> StructuralSourceRef:
    return StructuralSourceRef(
        source_id=source_id, raw_record_id="cd" * 16,
        payload_checksum="sha256:" + "ab" * 32, extractor=CSV_EXTRACTOR)


def step_source(source_id="step-src") -> StructuralSourceRef:
    return StructuralSourceRef(
        source_id=source_id, raw_record_id="ef" * 16,
        payload_checksum="sha256:" + "cd" * 32, extractor=STEP_EXTRACTOR)


def bom_claim(source, row, item_no, name="Part", quantity="1"):
    def cell(col, header, lexeme):
        return SourceNativeField(
            field_name_as_extracted=header, lexeme=lexeme,
            address=StructuralAddress(
                source=source,
                locator=CsvCellLocator(kind="csv_cell",
                                       physical_row_index=row,
                                       column_index=col,
                                       column_name_as_extracted=header)))
    fields = sorted(
        (cell(0, "item_no", item_no), cell(1, "name", name),
         cell(2, "quantity", quantity)),
        key=lambda f: (f.field_name_as_extracted,
                       f.address.locator.column_index))
    return SourceStructuralClaim(
        claim_kind="bom_row",
        address=StructuralAddress(
            source=source,
            locator=CsvRowLocator(kind="csv_row", physical_row_index=row)),
        fields=tuple(fields))


def step_definition_claim(source, path, name):
    address = StructuralAddress(
        source=source,
        locator=StepDefinitionLocator(kind="step_part_definition",
                                      extractor_path_id=path,
                                      upstream_definition_id="b0" * 16))
    return SourceStructuralClaim(
        claim_kind="step_part_definition", address=address,
        fields=(SourceNativeField(field_name_as_extracted="name",
                                  lexeme=name, address=address),))


def bom_claim_set(source=None, claims=None, context=UNKNOWN,
                  quantity_field=QuantityFieldRef(
                      column_index=2, column_name_as_extracted="quantity"),
                  containment=(), outcome="succeeded",
                  label_column_index=None):
    source = source or bom_source()
    if claims is None:
        claims = (bom_claim(source, 1, "EXT-100", quantity="4"),)
    label_field = (LabelFieldRef(column_index=label_column_index,
                                 column_name_as_extracted="name")
                   if label_column_index is not None else None)
    return SourceStructuralClaimSet(
        source_ref=source, engineering_context=context,
        subject_claims=tuple(claims), containment_claims=tuple(containment),
        quantity_field=quantity_field, label_field=label_field,
        extraction_outcome=outcome)


def step_claim_set(source=None, claims=None, context=UNKNOWN,
                   containment=(), outcome="succeeded"):
    source = source or step_source()
    if claims is None:
        claims = (step_definition_claim(source, "0:1:1:2", "extruder-unit"),)
    return SourceStructuralClaimSet(
        source_ref=source, engineering_context=context,
        subject_claims=tuple(claims), containment_claims=tuple(containment),
        quantity_field=None, extraction_outcome=outcome)


def subject_for(claim, rule_id):
    rule = SUBJECT_RULES[rule_id]
    from backend.structural_evidence.rules import apply_rule
    value = apply_rule(rule.body, claim)
    assert value is not None
    return to_source_subject_ref(claim.address, rule, value)


def anchor_declaration(anchor_id, role="mapped-thing",
                       kind="physical_instance"):
    return ib_build(AnchorDeclaration, anchor_kind="entity",
                    anchor=EntityAnchor(anchor_id=anchor_id,
                                        namespace="sn001-test",
                                        display_name=f"Synthetic {role}",
                                        role_name=role, referent_kind=kind),
                    recorded_at=T0, authority=AUTHORITY, note="")


def subject_assertion(subject, target, applies=UNBOUNDED, supersedes=None):
    return ib_build(BindingAssertion, binding_kind="subject",
                    subject=subject, property=None, target_anchor_id=target,
                    applies=applies, recorded_at=T0, authority=AUTHORITY,
                    supersedes=supersedes, note="")


def retraction(assertion):
    return ib_build(BindingRetraction, retracts=assertion.record_id,
                    recorded_at=T0, authority=AUTHORITY, note="")


def unknown_scope():
    from backend.identity_binding.contracts import UnknownBoundary
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=UnknownBoundary(kind="unknown"),
        end_boundary=UnknownBoundary(kind="unknown"),
        interval_semantics="half_open")


def closed_scope(end=RESOLUTION_AT):
    return AppliesScope(
        axis="ingestion_received_at",
        start_boundary=UnboundedBoundary(kind="unbounded"),
        end_boundary=DeclaredBoundary(kind="declared", at=end),
        interval_semantics="half_open")


def resolver_with(tmp_path, set_id, *records):
    store = BindingStore(tmp_path / set_id)
    for record in records:
        store.append(record)
    return BindingResolver(store.load())


def declared_context(view="as_designed"):
    return DeclaredEngineeringContext(
        kind="declared_lifecycle_view", view=view, declared_by=AUTHORITY,
        statement="Synthetic declared reading context for the test.")
