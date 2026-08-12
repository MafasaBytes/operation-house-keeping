"""Owner-audit integrity-repair regressions (2026-08-12).

Each class encodes one reproduction from the independent owner audit of
branch sn001 at 81cd0fc. Every test in this file FAILED against that
commit exactly as recorded in
docs/superpowers/plans/2026-08-12-sn001-owner-audit-red-baseline.md,
except where a docstring marks a test as the retained valid twin. The
kernel-side grammar reproductions (defect 4's constructor half) live in
tests/model_kernel/test_structural_evidence_arm.py.
"""

import pytest
from pydantic import ValidationError

from backend.model_kernel import StructuralSourceLocatorEvidence
from backend.structural_evidence.contracts import (
    DerivedUsagePath,
    SourceContainmentClaim,
    SourceNativeField,
    SourceStructuralClaim,
    SourceStructuralClaimSet,
    UnresolvedParentReference,
)
from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.locators import (
    CsvCellLocator,
    CsvRowLocator,
    StepDefinitionLocator,
    StepUsageLocator,
    StructuralAddress,
    StructuralSourceRef,
    canonical_locator_value,
    from_kernel_evidence,
    to_kernel_evidence,
    toolchain_fingerprint,
)
from backend.structural_evidence.reconcile import (
    ClaimSetDisclosure,
    ResolvedSubject,
    StructuralReconciler,
    compute_inputs_digest,
)
from backend.structural_evidence.rules import (
    SUBJECT_RULES,
    CsvColumnLexemeRuleBody,
    CsvPhysicalRowRuleBody,
    StepPathRuleBody,
    SubjectIdentityRule,
    parse_structural_namespace,
)

from tests.model_kernel.builders import registration, store_with
from tests.structural_evidence.helpers import (
    CSV_EXTRACTOR,
    RESOLUTION_AT,
    STEP_EXTRACTOR,
    UNKNOWN,
    anchor_declaration,
    bom_claim,
    bom_claim_set,
    bom_source,
    declared_context,
    resolver_with,
    step_claim_set,
    step_definition_claim,
    step_source,
    subject_assertion,
    subject_for,
)

ENT_PA = "ent_" + "1a" * 16
ENT_CA = "ent_" + "2b" * 16
ENT_PB = "ent_" + "3c" * 16
ENT_CB = "ent_" + "4d" * 16

ITEM_NO_RULE = (SUBJECT_RULES["bom-item-no-v1"],)


def foreign_bom_source() -> StructuralSourceRef:
    return StructuralSourceRef(
        source_id="b-bom", raw_record_id="ce" * 16,
        payload_checksum="sha256:" + "ef" * 32, extractor=CSV_EXTRACTOR)


def model_with(tmp_path, *anchor_ids):
    return store_with(tmp_path,
                      *(registration(a) for a in anchor_ids)).load()


def two_source_world(tmp_path, *, a_context, b_context):
    """Two BOM sources whose rows occupy IDENTICAL physical locators
    (r=1, r=2) but name four different subjects bound to four different
    anchors. Only source A carries a containment claim."""
    source_a = bom_source("a-bom")
    source_b = foreign_bom_source()
    a_parent = bom_claim(source_a, 1, "A-PRN")
    a_child = bom_claim(source_a, 2, "A-EXT")
    b_parent = bom_claim(source_b, 1, "B-PRN")
    b_child = bom_claim(source_b, 2, "B-EXT")
    containment = SourceContainmentClaim(
        claim_kind="bom_parent_column", child=a_child.address,
        parent=a_parent.address)
    set_a = bom_claim_set(source=source_a, claims=(a_parent, a_child),
                          containment=(containment,), context=a_context)
    set_b = bom_claim_set(source=source_b, claims=(b_parent, b_child),
                          context=b_context)
    resolver = resolver_with(
        tmp_path, "set-a",
        anchor_declaration(ENT_PA, role="a-parent"),
        anchor_declaration(ENT_CA, role="a-child"),
        anchor_declaration(ENT_PB, role="b-parent"),
        anchor_declaration(ENT_CB, role="b-child"),
        subject_assertion(subject_for(a_parent, "bom-item-no-v1"), ENT_PA),
        subject_assertion(subject_for(a_child, "bom-item-no-v1"), ENT_CA),
        subject_assertion(subject_for(b_parent, "bom-item-no-v1"), ENT_PB),
        subject_assertion(subject_for(b_child, "bom-item-no-v1"), ENT_CB))
    model = model_with(tmp_path, ENT_PA, ENT_CA, ENT_PB, ENT_CB)
    return [set_a, set_b], [resolver], model


def propose(claim_sets, resolvers, model, rules=ITEM_NO_RULE):
    reconciler = StructuralReconciler(resolvers=resolvers, rules=rules,
                                      model=model)
    return reconciler.propose(
        reconciler.reconcile(claim_sets, resolution_at=RESOLUTION_AT))


# --------------------------------------------------------------- defect 1
class TestD1CrossSourceEndpointContamination:
    def test_a_relationship_resolves_exclusively_to_source_a_anchors(
            self, tmp_path):
        """Owner reproduction: with locator-only endpoint keys, source
        B's r=1/r=2 joins overwrote source A's and A's containment claim
        proposed a relationship between B's anchors."""
        claim_sets, resolvers, model = two_source_world(
            tmp_path, a_context=declared_context("as_designed"),
            b_context=declared_context("as_designed"))
        result = propose(claim_sets, resolvers, model)
        edges = [p for p in result.proposals
                 if p.proposal_kind == "relationship_assertion"]
        assert len(edges) == 1
        [edge] = edges
        assert (edge.source_anchor_id, edge.target_anchor_id) == \
            (ENT_PA, ENT_CA)

    def test_declared_context_on_b_never_unlocks_a_unknown_containment(
            self, tmp_path):
        """Owner reproduction (unknown-context twin): B's declared
        context at the same locator must never make A's unknown-context
        containment proposable."""
        claim_sets, resolvers, model = two_source_world(
            tmp_path, a_context=UNKNOWN,
            b_context=declared_context("as_designed"))
        result = propose(claim_sets, resolvers, model)
        assert [p for p in result.proposals
                if p.proposal_kind == "relationship_assertion"] == []
        assert any(f.finding == "context_unknown"
                   for f in result.blocking_findings)

    def test_two_rules_joining_one_claim_apart_is_not_proposable(
            self, tmp_path):
        """Same complete address, two rules, two different accepted
        anchors: silent last-rule-wins is the same defect class, so the
        endpoint is treated as unresolved and nothing is proposed."""
        source = bom_source("a-bom")
        parent = bom_claim(source, 1, "A-PRN")
        child = bom_claim(source, 2, "A-EXT")
        containment = SourceContainmentClaim(
            claim_kind="bom_parent_column", child=child.address,
            parent=parent.address)
        claim_set = bom_claim_set(source=source, claims=(parent, child),
                                  containment=(containment,),
                                  context=declared_context("as_designed"))
        resolver = resolver_with(
            tmp_path, "set-a",
            anchor_declaration(ENT_PA, role="parent"),
            anchor_declaration(ENT_CA, role="child-by-item-no"),
            anchor_declaration(ENT_CB, role="child-by-row"),
            subject_assertion(subject_for(parent, "bom-item-no-v1"),
                              ENT_PA),
            subject_assertion(subject_for(parent, "bom-physical-row-v1"),
                              ENT_PA),
            subject_assertion(subject_for(child, "bom-item-no-v1"),
                              ENT_CA),
            subject_assertion(subject_for(child, "bom-physical-row-v1"),
                              ENT_CB))
        model = model_with(tmp_path, ENT_PA, ENT_CA, ENT_CB)
        result = propose(
            [claim_set], [resolver], model,
            rules=(SUBJECT_RULES["bom-item-no-v1"],
                   SUBJECT_RULES["bom-physical-row-v1"]))
        assert [p for p in result.proposals
                if p.proposal_kind == "relationship_assertion"] == []


# --------------------------------------------------------------- defect 2
class TestD2ProvenanceCoherence:
    def row_address(self, source, row):
        return StructuralAddress(
            source=source,
            locator=CsvRowLocator(kind="csv_row", physical_row_index=row))

    def cell_address(self, source, row, col, name):
        return StructuralAddress(
            source=source,
            locator=CsvCellLocator(kind="csv_cell", physical_row_index=row,
                                   column_index=col,
                                   column_name_as_extracted=name))

    def test_the_owner_reproduction_is_unconstructible(self):
        """claim_set.source_ref names 'declared-source' while the claim's
        address names 'foreign-source' — this constructed at 81cd0fc."""
        declared = bom_source("declared-source")
        with pytest.raises(ValidationError):
            SourceStructuralClaimSet(
                source_ref=declared, engineering_context=UNKNOWN,
                subject_claims=(bom_claim(foreign_bom_source(), 1, "X-1"),),
                extraction_outcome="succeeded")

    def test_a_field_from_a_foreign_source_cannot_join_a_claim(self):
        a = bom_source("a-bom")
        foreign = SourceNativeField(
            field_name_as_extracted="item_no", lexeme="X-1",
            address=self.cell_address(foreign_bom_source(), 1, 0,
                                      "item_no"))
        with pytest.raises(ValidationError):
            SourceStructuralClaim(claim_kind="bom_row",
                                  address=self.row_address(a, 1),
                                  fields=(foreign,))

    def test_bom_row_requires_a_csv_row_locator(self):
        a = bom_source("a-bom")
        with pytest.raises(ValidationError):
            SourceStructuralClaim(
                claim_kind="bom_row",
                address=self.cell_address(a, 1, 0, "item_no"))

    def test_bom_row_fields_are_cells_on_the_claims_physical_row(self):
        a = bom_source("a-bom")
        row_locator_field = SourceNativeField(
            field_name_as_extracted="item_no", lexeme="X-1",
            address=self.row_address(a, 1))
        with pytest.raises(ValidationError):
            SourceStructuralClaim(claim_kind="bom_row",
                                  address=self.row_address(a, 1),
                                  fields=(row_locator_field,))
        other_row_cell = SourceNativeField(
            field_name_as_extracted="item_no", lexeme="X-1",
            address=self.cell_address(a, 2, 0, "item_no"))
        with pytest.raises(ValidationError):
            SourceStructuralClaim(claim_kind="bom_row",
                                  address=self.row_address(a, 1),
                                  fields=(other_row_cell,))

    def test_field_name_disclosure_agrees_with_its_cell_locator(self):
        a = bom_source("a-bom")
        renamed = SourceNativeField(
            field_name_as_extracted="item_no", lexeme="X-1",
            address=self.cell_address(a, 1, 0, "quantity"))
        with pytest.raises(ValidationError):
            SourceStructuralClaim(claim_kind="bom_row",
                                  address=self.row_address(a, 1),
                                  fields=(renamed,))

    def step_definition_address(self, source, path="0:1:1:2"):
        return StructuralAddress(
            source=source,
            locator=StepDefinitionLocator(kind="step_part_definition",
                                          extractor_path_id=path,
                                          upstream_definition_id="b0" * 16))

    def step_usage_address(self, source, path="0:1:1:1:1",
                           parent="0:1:1:1"):
        return StructuralAddress(
            source=source,
            locator=StepUsageLocator(kind="step_nauo_usage",
                                     extractor_path_id=path,
                                     upstream_instance_id="cc" * 16,
                                     definition_path_id="0:1:1:2",
                                     parent_definition_path_id=parent))

    def test_step_claim_kinds_require_their_own_locator_schemes(self):
        source = step_source()
        with pytest.raises(ValidationError):
            SourceStructuralClaim(
                claim_kind="step_part_definition",
                address=self.step_usage_address(source))
        with pytest.raises(ValidationError):
            SourceStructuralClaim(
                claim_kind="step_nauo_usage",
                address=self.step_definition_address(source))

    def test_step_fields_address_the_containing_claim_exactly(self):
        source = step_source()
        address = self.step_definition_address(source)
        elsewhere = SourceNativeField(
            field_name_as_extracted="name", lexeme="extruder",
            address=self.step_definition_address(source, path="0:1:1:9"))
        with pytest.raises(ValidationError):
            SourceStructuralClaim(claim_kind="step_part_definition",
                                  address=address, fields=(elsewhere,))

    def test_bom_parent_column_endpoints_are_same_source_row_addresses(
            self):
        a = bom_source("a-bom")
        with pytest.raises(ValidationError):
            SourceContainmentClaim(
                claim_kind="bom_parent_column",
                child=self.row_address(a, 2),
                parent=self.row_address(foreign_bom_source(), 1))
        with pytest.raises(ValidationError):
            SourceContainmentClaim(
                claim_kind="bom_parent_column",
                child=self.cell_address(a, 2, 0, "item_no"),
                parent=self.row_address(a, 1))

    def test_step_nauo_usage_edge_endpoint_grammar(self):
        source = step_source()
        usage = self.step_usage_address(source, parent="0:1:1:1")
        parent = self.step_definition_address(source, path="0:1:1:1")
        SourceContainmentClaim(claim_kind="step_nauo_usage_edge",
                               child=usage, parent=parent)  # the twin
        with pytest.raises(ValidationError):  # child must be the usage
            SourceContainmentClaim(claim_kind="step_nauo_usage_edge",
                                   child=parent, parent=usage)
        with pytest.raises(ValidationError):  # parent path must match
            SourceContainmentClaim(
                claim_kind="step_nauo_usage_edge", child=usage,
                parent=self.step_definition_address(source, path="0:1:1:9"))

    def test_containment_endpoints_must_be_disclosed_subject_claims(self):
        a = bom_source("a-bom")
        parent = bom_claim(a, 1, "A-PRN")
        undisclosed_child = self.row_address(a, 7)
        with pytest.raises(ValidationError):
            bom_claim_set(source=a, claims=(parent,), containment=(
                SourceContainmentClaim(claim_kind="bom_parent_column",
                                       child=undisclosed_child,
                                       parent=parent.address),))

    def test_unresolved_parent_child_belongs_to_the_set_source(self):
        a = bom_source("a-bom")
        with pytest.raises(ValidationError):
            SourceStructuralClaimSet(
                source_ref=a, engineering_context=UNKNOWN,
                subject_claims=(bom_claim(a, 1, "A-PRN"),),
                unresolved_parent_references=(UnresolvedParentReference(
                    child=self.row_address(foreign_bom_source(), 3),
                    parent_lexeme="x", reason="no_matching_row"),),
                extraction_outcome="succeeded")

    def test_derived_path_for_an_undisclosed_usage_is_rejected(self):
        source = step_source()
        definition = step_definition_claim(source, "0:1:1:2",
                                           "extruder-unit")
        stray = self.step_usage_address(source).locator
        with pytest.raises(ValidationError):
            SourceStructuralClaimSet(
                source_ref=source, engineering_context=UNKNOWN,
                subject_claims=(definition,),
                derived_paths=(DerivedUsagePath(
                    derivation="nauo_parent_definition_chain_v1",
                    for_usage=stray, steps=(),
                    ambiguity="multiple_parent_uses"),),
                quantity_field=None, extraction_outcome="succeeded")

    def test_disclosure_coverage_compares_exact_addresses(self):
        """At 81cd0fc a resolved subject at (foreign source, r=1) passed
        coverage because the disclosed claim at (own source, r=1) shares
        its locator STRING."""
        a = bom_source("a-bom")
        claim = bom_claim(a, 1, "A-PRN")
        claim_set = bom_claim_set(source=a, claims=(claim,))
        foreign_address = StructuralAddress(
            source=foreign_bom_source(), locator=claim.address.locator)
        stray = ResolvedSubject(
            claim_address=foreign_address, rule_id="bom-item-no-v1",
            rule_fingerprint="0" * 16, toolchain_fingerprint="0" * 16,
            subject=None, no_subject_reason="rule_yielded_none")
        with pytest.raises(ValidationError):
            ClaimSetDisclosure(claim_set=claim_set,
                               resolved_subjects=(stray,))


# --------------------------------------------------------------- defect 3
CSV_BODY = CsvColumnLexemeRuleBody(
    rule_kind="csv_column_lexeme", semantics_version="v1",
    column_name_as_extracted="item_no", name_match="exact_as_extracted",
    empty_lexeme_outcome="no_subject_identity")
ROW_BODY = CsvPhysicalRowRuleBody(
    rule_kind="csv_physical_row", semantics_version="v1",
    include_payload_checksum=True)
STEP_BODY = StepPathRuleBody(
    rule_kind="step_extractor_path", semantics_version="v1",
    path_source="extractor_path_id")


class TestD3AppliesToIsABodyDerivedMirror:
    def rule(self, body, applies_to):
        return SubjectIdentityRule(
            rule_id="audit-rule", applies_to=applies_to, body=body,
            statement="Owner-audit reproduction rule.",
            stability="source_native_key")

    def test_widening_applies_to_is_unconstructible(self):
        """Owner reproduction: at 81cd0fc the widened rule constructed
        and kept the narrow rule's fingerprint byte-for-byte."""
        assert self.rule(CSV_BODY, ("bom_row",)).fingerprint \
            == "57241bb3231eac29"
        with pytest.raises(ValidationError):
            self.rule(CSV_BODY, ("bom_row", "step_part_definition"))

    def test_substitution_removal_and_reordering_are_rejected(self):
        for body, bad in (
                (CSV_BODY, ("step_part_definition",)),          # substitute
                (ROW_BODY, ("bom_row", "step_nauo_usage")),     # addition
                (STEP_BODY, ("step_part_definition",)),         # removal
                (STEP_BODY, ("step_nauo_usage",                 # reorder
                             "step_part_definition"))):
            with pytest.raises(ValidationError):
                self.rule(body, bad)

    def test_shipped_rules_fingerprints_and_mirrors_are_unchanged(self):
        """The repair must not migrate any identity: the shipped tuples
        already equal their body-derived mirrors and every fingerprint
        (hence every sx1 namespace and committed binding) is pinned."""
        expected = {
            "bom-item-no-v1": (("bom_row",), "57241bb3231eac29"),
            "bom-physical-row-v1": (("bom_row",), "569e04f2ed1277de"),
            "step-ocaf-entry-v1": (("step_part_definition",
                                    "step_nauo_usage"),
                                   "8496bcb773e204bf"),
        }
        assert {rid: (rule.applies_to, rule.fingerprint)
                for rid, rule in SUBJECT_RULES.items()} == expected


# --------------------------------------------------------------- defect 4
VALID_LOCATOR_VALUES = {
    "csv_row": "r=3",
    "csv_cell": "r=3;c=12",
    "step_part_definition": "p=0%3A1%3A1%3A2;d=" + "27" * 16,
    "step_nauo_usage": ("p=0%3A1%3A1%3A3%3A1;i=" + "83" * 16 +
                        ";dp=0%3A1%3A1%3A4;pp=0%3A1%3A1%3A3"),
}


class TestD4TypedConversionErrors:
    def evidence_with(self, scheme, value):
        """model_construct BYPASSES kernel validation deliberately: it
        simulates a malformed citation arriving from outside the
        constructor path (deserialized, legacy, or hand-edited)."""
        return StructuralSourceLocatorEvidence.model_construct(
            kind="structural_source_locator", raw_record_id="bf" * 16,
            payload_checksum="sha256:" + "ab" * 32,
            extractor_name=CSV_EXTRACTOR.name,
            extractor_version=CSV_EXTRACTOR.version,
            extractor_config_fingerprint=CSV_EXTRACTOR.config_fingerprint,
            extractor_toolchain_fingerprint=toolchain_fingerprint(
                CSV_EXTRACTOR),
            locator_scheme=scheme, locator_value=value)

    def convert(self, scheme, value):
        return from_kernel_evidence(
            self.evidence_with(scheme, value), source_id="a-bom",
            extractor_toolchain=CSV_EXTRACTOR.toolchain)

    def test_malformed_integer_is_a_typed_structural_error(self):
        """Owner reproduction: at 81cd0fc `r=abc` escaped as a raw
        ValueError from int()."""
        with pytest.raises(StructuralEvidenceError) as err:
            self.convert("csv_row", "r=abc")
        assert err.value.error_code == "SN_LOCATOR_VALUE_INVALID"

    def test_noncanonical_integer_never_silently_renormalizes(self):
        """`r=01` reconstructed as r=1 at 81cd0fc — a silently re-pointed
        citation."""
        with pytest.raises(StructuralEvidenceError) as err:
            self.convert("csv_row", "r=01")
        assert err.value.error_code == "SN_LOCATOR_VALUE_INVALID"

    def test_negative_index_is_typed_never_a_pydantic_leak(self):
        with pytest.raises(StructuralEvidenceError) as err:
            self.convert("csv_row", "r=-1")
        assert err.value.error_code == "SN_LOCATOR_VALUE_INVALID"

    def test_malformed_step_identifier_is_typed(self):
        """At 81cd0fc a non-32-hex `d=` escaped as a raw pydantic
        ValidationError from the locator constructor."""
        with pytest.raises(StructuralEvidenceError) as err:
            self.convert("step_part_definition", "p=0%3A1;d=xyz")
        assert err.value.error_code == "SN_LOCATOR_VALUE_INVALID"

    def test_wrong_component_count_stays_typed(self):
        """Valid twin of the reproductions: the component-count guard was
        already typed at 81cd0fc and must remain so."""
        with pytest.raises(StructuralEvidenceError) as err:
            self.convert("step_nauo_usage", "p=a;i=" + "83" * 16)
        assert err.value.error_code == "SN_LOCATOR_VALUE_INVALID"

    def test_valid_round_trip_twin_for_every_arm(self):
        """Valid twins: every scheme's canonical value converts and
        re-canonicalizes byte-exactly."""
        for scheme, value in VALID_LOCATOR_VALUES.items():
            back = self.convert(scheme, value)
            assert back.locator.kind == scheme
            assert canonical_locator_value(back.locator) == value
        root = "p=0%3A1;i=" + "93" * 16 + ";dp=0%3A1%3A1;pp="
        back = self.convert("step_nauo_usage", root)
        assert back.locator.parent_definition_path_id is None
        assert canonical_locator_value(back.locator) == root


# --------------------------------------------------------------- defect 5
class TestD5OneToolchainFingerprint:
    def test_the_two_module_names_are_one_function(self):
        """Owner reproduction: rules.py and locators.py carried two
        independent implementations — byte-identical today, free to
        drift apart tomorrow."""
        from backend.structural_evidence import locators, rules
        assert rules.toolchain_fingerprint is locators.toolchain_fingerprint

    def test_namespace_disclosure_kernel_and_digest_material_agree(
            self, tmp_path):
        source = step_source()
        claim = step_definition_claim(source, "0:1:1:2", "extruder-unit")
        claim_set = step_claim_set(source=source, claims=(claim,))
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_PA),
            subject_assertion(subject_for(claim, "step-ocaf-entry-v1"),
                              ENT_PA))
        model = model_with(tmp_path, ENT_PA)
        reconciler = StructuralReconciler(
            resolvers=[resolver],
            rules=(SUBJECT_RULES["step-ocaf-entry-v1"],), model=model)
        result = reconciler.reconcile([claim_set],
                                      resolution_at=RESOLUTION_AT)
        [rs] = result.claim_sets[0].resolved_subjects
        expected = toolchain_fingerprint(STEP_EXTRACTOR)
        parsed = parse_structural_namespace(rs.subject.adapter_id)
        kernel_arm = to_kernel_evidence(rs.claim_address).evidence
        assert parsed.toolchain_fingerprint == expected
        assert rs.toolchain_fingerprint == expected
        assert kernel_arm.extractor_toolchain_fingerprint == expected
        assert result.toolchain_fingerprints_used == (expected,)
        assert result.inputs_digest == compute_inputs_digest(result)


class TestD5EndpointGrammarAdjudication:
    def test_contract_wording_matches_the_implemented_grammar(self):
        """Owner reproduction: the contract claimed both STEP endpoints
        are definitions while the implementation emits a usage-address
        child. Adjudicated: the usage-child grammar stays (it keeps
        repeated same-pair usages distinct and both definitions remain
        named through the usage locator); the wording moves."""
        doc = " ".join(SourceContainmentClaim.__doc__.split())
        assert "both endpoints are DEFINITIONS" not in doc
        assert "parent_definition_path_id" in doc
