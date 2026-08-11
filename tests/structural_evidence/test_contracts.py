"""SN-001 claim, field, and engineering-context contracts (C0).

The engineering context has NO default anywhere: constructing a claim set
without one is a validation error, and the three arms are pairwise
distinct states — a positive view claim, a positive view-independence
claim, and honest absence of knowledge.
"""

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.identity_binding.contracts import AuthorityRef
from backend.structural_evidence.contracts import (
    DeclaredEngineeringContext,
    DerivedUsagePath,
    QuantityFieldRef,
    SourceContainmentClaim,
    SourceNativeField,
    SourceStructuralClaim,
    SourceStructuralClaimSet,
    UnknownEngineeringContext,
    UnresolvedParentReference,
    ViewIndependentEngineeringContext,
)
from backend.structural_evidence.locators import (
    CsvCellLocator,
    CsvRowLocator,
    StepUsageLocator,
    StructuralAddress,
    StructuralSourceRef,
)

EXTRACTOR = ExtractorIdentity(
    name="csv_extractor", version="1.1.0", toolchain="cpython-3.13 stdlib csv",
    config_fingerprint="6f1c2a9d0b3e4517")
AUTHORITY = AuthorityRef(kind="test_fixture", agent="sn001_showcase_fixture",
                         method="manual_declaration")
SOURCE = StructuralSourceRef(
    source_id="showcase-printer-bom", raw_record_id="cd" * 16,
    payload_checksum="sha256:" + "ab" * 32, extractor=EXTRACTOR)


def row_address(row: int) -> StructuralAddress:
    return StructuralAddress(
        source=SOURCE, locator=CsvRowLocator(kind="csv_row",
                                             physical_row_index=row))


def cell_address(row: int, col: int, name: str) -> StructuralAddress:
    return StructuralAddress(
        source=SOURCE,
        locator=CsvCellLocator(kind="csv_cell", physical_row_index=row,
                               column_index=col,
                               column_name_as_extracted=name))


def field(name: str, lexeme, row: int, col: int) -> SourceNativeField:
    return SourceNativeField(field_name_as_extracted=name, lexeme=lexeme,
                             address=cell_address(row, col, name))


def bom_claim(row: int) -> SourceStructuralClaim:
    return SourceStructuralClaim(
        claim_kind="bom_row", address=row_address(row),
        fields=(field("item_no", "EXT-100", row, 0),
                field("quantity", "4", row, 2)))


class TestC0Fields:
    def test_lexeme_none_is_absent_never_empty_string_coercion(self):
        absent = field("unit", None, 2, 3)
        assert absent.lexeme is None
        present = field("unit", "", 2, 3)
        assert present.lexeme == ""
        assert absent != present

    def test_fields_must_be_canonically_ordered(self):
        with pytest.raises(ValidationError):
            SourceStructuralClaim(
                claim_kind="bom_row", address=row_address(2),
                fields=(field("quantity", "4", 2, 2),
                        field("item_no", "EXT-100", 2, 0)))

    def test_quantity_field_ref_is_index_identity(self):
        ref = QuantityFieldRef(column_index=2,
                               column_name_as_extracted="quantity")
        assert ref.column_index == 2
        with pytest.raises(ValidationError):
            QuantityFieldRef(column_index=-1, column_name_as_extracted="q")


class TestC0EngineeringContext:
    def test_three_arms_are_pairwise_distinct(self):
        declared = DeclaredEngineeringContext(
            kind="declared_lifecycle_view", view="as_designed",
            declared_by=AUTHORITY, statement="Showcase export is as-designed.")
        independent = ViewIndependentEngineeringContext(
            kind="view_independent", declared_by=AUTHORITY,
            statement="Holds regardless of view.")
        unknown = UnknownEngineeringContext(
            kind="unknown", reason="source_declares_no_view")
        assert len({declared.kind, independent.kind, unknown.kind}) == 3

    def test_declared_needs_a_kernel_view_and_a_statement(self):
        with pytest.raises(ValidationError):
            DeclaredEngineeringContext(
                kind="declared_lifecycle_view", view="as_imagined",
                declared_by=AUTHORITY, statement="x")
        with pytest.raises(ValidationError):
            DeclaredEngineeringContext(
                kind="declared_lifecycle_view", view="as_built",
                declared_by=AUTHORITY, statement="")

    def test_unknown_reasons_are_the_only_two(self):
        UnknownEngineeringContext(kind="unknown",
                                  reason="authority_has_not_declared")
        with pytest.raises(ValidationError):
            UnknownEngineeringContext(kind="unknown", reason="filename_said_so")

    def test_claim_set_without_a_context_is_unconstructible(self):
        """The mutation this kills: `= UnknownEngineeringContext(...)` as a
        default, which would satisfy 'never inferred' while destroying the
        unknown/absent distinction."""
        with pytest.raises(ValidationError):
            SourceStructuralClaimSet(
                source_ref=SOURCE, subject_claims=(bom_claim(2),),
                extraction_outcome="succeeded")


class TestC0ClaimSet:
    def make(self, **overrides) -> SourceStructuralClaimSet:
        payload = dict(
            source_ref=SOURCE,
            engineering_context=UnknownEngineeringContext(
                kind="unknown", reason="source_declares_no_view"),
            subject_claims=(bom_claim(2),),
            quantity_field=QuantityFieldRef(
                column_index=2, column_name_as_extracted="quantity"),
            extraction_outcome="succeeded")
        payload.update(overrides)
        return SourceStructuralClaimSet(**payload)

    def test_carries_extraction_outcome_and_warnings_verbatim(self):
        claim_set = self.make(extraction_outcome="partial",
                              extraction_warnings=("ragged row 7",))
        assert claim_set.extraction_outcome == "partial"
        assert claim_set.extraction_warnings == ("ragged row 7",)

    def test_quantity_field_none_means_no_quantity_column_declared(self):
        assert self.make(quantity_field=None).quantity_field is None

    def test_containment_claim_kinds_are_the_only_two(self):
        claim = SourceContainmentClaim(
            claim_kind="bom_parent_column",
            child=row_address(3), parent=row_address(1))
        assert claim.claim_kind == "bom_parent_column"
        with pytest.raises(ValidationError):
            SourceContainmentClaim(claim_kind="physical_containment",
                                   child=row_address(3), parent=row_address(1))

    def test_unresolved_parent_reference_reasons(self):
        ref = UnresolvedParentReference(
            child=row_address(3), parent_lexeme="100-009",
            reason="no_matching_row")
        assert ref.parent_lexeme == "100-009"
        with pytest.raises(ValidationError):
            UnresolvedParentReference(child=row_address(3), parent_lexeme="x",
                                      reason="fuzzy_match_found")


class TestC0DerivedUsagePath:
    def usage(self, path: str) -> StepUsageLocator:
        return StepUsageLocator(kind="step_nauo_usage", extractor_path_id=path,
                                upstream_instance_id="aa" * 16,
                                definition_path_id="0:1:1",
                                parent_definition_path_id=None)

    def test_steps_are_present_exactly_when_unique(self):
        unique = DerivedUsagePath(
            derivation="nauo_parent_definition_chain_v1",
            steps=(self.usage("0:1:1"),), ambiguity="unique")
        assert unique.steps
        ambiguous = DerivedUsagePath(
            derivation="nauo_parent_definition_chain_v1",
            steps=(), ambiguity="multiple_parent_uses")
        assert ambiguous.steps == ()
        with pytest.raises(ValidationError):
            DerivedUsagePath(derivation="nauo_parent_definition_chain_v1",
                             steps=(self.usage("0:1:1"),),
                             ambiguity="multiple_parent_uses")
        with pytest.raises(ValidationError):
            DerivedUsagePath(derivation="nauo_parent_definition_chain_v1",
                             steps=(), ambiguity="unique")
