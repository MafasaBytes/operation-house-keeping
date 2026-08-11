"""Multi-set reconciliation (M-, CS-, J-, CP-, S-, A-series, commit 13).

The join rule has no fallback: two subjects join iff accepted binding
resolutions positively bind both to the same canonical anchor at the
required instant. Names are never keys; every finding carries its basis
and its disclosed proof; the digest is recomputable from disclosed
fields only.
"""

import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.reconcile import (
    BASIS_BY_FINDING,
    ClaimComparison,
    ComparisonOperand,
    ModelDisclosure,
    ReconciliationFinding,
    StructuralReconciler,
    compute_inputs_digest,
)
from backend.structural_evidence.rules import SUBJECT_RULES

from tests.model_kernel.builders import registration, store_with
from tests.structural_evidence.helpers import (
    ENT_X,
    ENT_Y,
    RESOLUTION_AT,
    anchor_declaration,
    bom_claim,
    bom_claim_set,
    bom_source,
    closed_scope,
    declared_context,
    resolver_with,
    retraction,
    step_claim_set,
    step_definition_claim,
    step_source,
    subject_assertion,
    subject_for,
)

RULES = tuple(SUBJECT_RULES.values())


def model_with(tmp_path, *anchor_ids):
    return store_with(tmp_path, *(registration(a) for a in anchor_ids)).load()


def corroborated_pair(tmp_path):
    """BOM EXT-100 and a STEP definition, both mapped to ENT_X."""
    bom_set = bom_claim_set()
    step_set = step_claim_set()
    bom_subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
    step_subject = subject_for(step_set.subject_claims[0],
                               "step-ocaf-entry-v1")
    resolver = resolver_with(
        tmp_path, "set-a", anchor_declaration(ENT_X),
        subject_assertion(bom_subject, ENT_X),
        subject_assertion(step_subject, ENT_X))
    model = model_with(tmp_path, ENT_X)
    return bom_set, step_set, resolver, model


def reconcile(claim_sets, resolvers, model, **kwargs):
    reconciler = StructuralReconciler(resolvers=resolvers, rules=RULES,
                                      model=model, **kwargs)
    return reconciler.reconcile(claim_sets, resolution_at=RESOLUTION_AT)


def literals(result):
    return Counter(f.finding for f in result.findings)


class TestJoinAndCorroboration:
    def test_both_sources_bound_to_one_anchor_corroborate(self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        result = reconcile([bom_set, step_set], [resolver], model)
        found = literals(result)
        assert found["corroborated_by_all_mapped_sources"] == 1
        [finding] = [f for f in result.findings
                     if f.finding == "corroborated_by_all_mapped_sources"]
        assert finding.anchor_id == ENT_X
        assert finding.basis == "accepted_model_record"
        assert all(d.registration_record_id for d in finding.model_disclosures)

    def test_j2_renaming_changes_no_join_but_changes_the_digest(
            self, tmp_path):
        """K8/3: names are never join keys; the digest honestly covers
        verbatim claims, so it changes."""
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        renamed_bom = bom_claim_set(claims=(
            bom_claim(bom_source(), 1, "EXT-100",
                      name="Totally Renamed Part", quantity="4"),))
        base = reconcile([bom_set, step_set], [resolver], model)
        renamed = reconcile([renamed_bom, step_set], [resolver], model)
        key = lambda r: [(f.finding, f.anchor_id) for f in r.findings]
        assert key(renamed) == key(base)
        joined = lambda r: {s.join_anchor_id
                            for d in r.claim_sets
                            for s in d.resolved_subjects
                            if s.join_anchor_id}
        assert joined(renamed) == joined(base) == {ENT_X}
        assert renamed.inputs_digest != base.inputs_digest

    def test_j3_no_non_bound_status_ever_joins(self, tmp_path):
        """Retracted mapping: status != bound => no join, and the mapping
        finding carries the resolution verbatim."""
        bom_set = bom_claim_set()
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        assertion = subject_assertion(subject, ENT_X)
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X), assertion,
            retraction(assertion))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([bom_set], [resolver], model)
        subjects = [s for d in result.claim_sets
                    for s in d.resolved_subjects if s.subject is not None]
        assert all(s.join_anchor_id is None for s in subjects)
        assert literals(result)["source_subject_unmapped"] >= 1

    def test_m8_competing_anchors_are_conflicted_never_picked(
            self, tmp_path):
        """Two applicable assertions to different anchors: IB-001's
        verbatim status is `conflicted`, carried unchanged with both
        candidates — never resolved to candidates[0]."""
        bom_set = bom_claim_set()
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            anchor_declaration(ENT_Y, role="other-thing"),
            subject_assertion(subject, ENT_X),
            subject_assertion(subject, ENT_Y))
        model = model_with(tmp_path, ENT_X, ENT_Y)
        result = reconcile([bom_set], [resolver], model)
        assert literals(result)["mapping_conflicted"] == 1
        [finding] = [f for f in result.findings
                     if f.finding == "mapping_conflicted"]
        assert finding.basis == "authority_interpretation"
        [res] = finding.supporting_resolutions
        assert res.resolution.status == "conflicted"
        assert len(res.resolution.candidate_targets) == 2

    def test_m8b_unknown_applicability_competitor_is_ambiguous(
            self, tmp_path):
        """One applicable target plus a competitor whose applicability is
        unknown: IB-001's verbatim status is `ambiguous` — SN-001 joins
        nothing and re-expresses nothing."""
        from tests.structural_evidence.helpers import unknown_scope

        bom_set = bom_claim_set()
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            anchor_declaration(ENT_Y, role="other-thing"),
            subject_assertion(subject, ENT_X),
            subject_assertion(subject, ENT_Y, applies=unknown_scope()))
        model = model_with(tmp_path, ENT_X, ENT_Y)
        result = reconcile([bom_set], [resolver], model)
        assert literals(result)["mapping_ambiguous"] == 1
        [finding] = [f for f in result.findings
                     if f.finding == "mapping_ambiguous"]
        [res] = finding.supporting_resolutions
        assert res.resolution.status == "ambiguous"


class TestCrossSet:
    def two_sets(self, tmp_path, target_b=ENT_X):
        bom_set = bom_claim_set()
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        resolver_a = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(subject, ENT_X))
        role = "other-thing" if target_b == ENT_Y else "mapped-thing"
        resolver_b = resolver_with(
            tmp_path, "set-b", anchor_declaration(target_b, role=role),
            subject_assertion(subject, target_b))
        model = model_with(tmp_path, ENT_X, ENT_Y)
        return bom_set, resolver_a, resolver_b, model

    def test_cs2_resolver_order_never_changes_the_result(self, tmp_path):
        bom_set, a, b, model = self.two_sets(tmp_path)
        forward = reconcile([bom_set], [a, b], model)
        reverse = reconcile([bom_set], [b, a], model)
        assert forward == reverse
        assert forward.inputs_digest == reverse.inputs_digest
        assert [p.binding_set_id for p in forward.participations] == \
            ["set-a", "set-b"]

    def test_cs3_consistent_multi_set_binding_is_disclosed_not_deduped(
            self, tmp_path):
        bom_set, a, b, model = self.two_sets(tmp_path)
        result = reconcile([bom_set], [a, b], model)
        assert literals(result)[
            "subject_bound_in_multiple_sets_consistently"] == 1
        [finding] = [f for f in result.findings if f.finding ==
                     "subject_bound_in_multiple_sets_consistently"]
        assert len(finding.supporting_resolutions) == 2
        [subject] = [s for d in result.claim_sets
                     for s in d.resolved_subjects
                     if s.subject and s.rule_id == "bom-item-no-v1"]
        assert subject.join_anchor_id == ENT_X

    def test_cs4_competing_anchors_across_sets_never_resolve(self, tmp_path):
        bom_set, a, b, model = self.two_sets(tmp_path, target_b=ENT_Y)
        result = reconcile([bom_set], [a, b], model)
        assert literals(result)["mapping_conflicted_across_sets"] == 1
        [subject] = [s for d in result.claim_sets
                     for s in d.resolved_subjects
                     if s.subject and s.rule_id == "bom-item-no-v1"]
        assert subject.join_anchor_id is None
        assert literals(result)["corroborated_by_all_mapped_sources"] == 0

    def test_cs5_duplicate_anchor_declarations_reported_never_merged(
            self, tmp_path):
        bom_set = bom_claim_set()
        a = resolver_with(tmp_path, "set-a", anchor_declaration(ENT_X))
        b = resolver_with(tmp_path, "set-b", anchor_declaration(ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([bom_set], [a, b], model)
        assert literals(result)["anchor_declared_in_multiple_sets"] == 1

    def test_cs6_missing_required_set_is_never_partial_success(
            self, tmp_path):
        bom_set, a, _, model = self.two_sets(tmp_path)
        result = reconcile(
            [bom_set], [a], model,
            required_binding_set_ids=frozenset({"set-a", "set-b"}))
        assert literals(result)["required_binding_set_missing"] == 1

    def test_cs7_empty_and_duplicate_resolver_inputs_are_typed(
            self, tmp_path):
        model = model_with(tmp_path, ENT_X)
        with pytest.raises(StructuralEvidenceError) as err:
            StructuralReconciler(resolvers=[], rules=RULES, model=model)
        assert err.value.error_code == "SN_NO_BINDING_RESOLVER"
        a = resolver_with(tmp_path, "set-a", anchor_declaration(ENT_X))
        with pytest.raises(StructuralEvidenceError) as err:
            StructuralReconciler(resolvers=[a, a], rules=RULES, model=model)
        assert err.value.error_code == "SN_DUPLICATE_BINDING_SET"

    def test_cs9_naive_resolution_at_is_typed(self, tmp_path):
        bom_set, a, _, model = self.two_sets(tmp_path)
        reconciler = StructuralReconciler(resolvers=[a], rules=RULES,
                                          model=model)
        with pytest.raises(StructuralEvidenceError) as err:
            reconciler.reconcile([bom_set],
                                 resolution_at=datetime(2026, 8, 11, 13))
        assert err.value.error_code == "SN_NAIVE_RESOLUTION_AT"


class TestMappingLifecycle:
    def test_m23_retracted_superseded_conflicted_are_three_outcomes(
            self, tmp_path):
        bom_set = bom_claim_set()
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        model = model_with(tmp_path, ENT_X, ENT_Y)

        first = subject_assertion(subject, ENT_X)
        retracted = reconcile([bom_set], [resolver_with(
            tmp_path, "set-r", anchor_declaration(ENT_X), first,
            retraction(first))], model)

        base = subject_assertion(subject, ENT_X)
        superseding = subject_assertion(subject, ENT_X,
                                        supersedes=base.record_id)
        closed = reconcile([bom_set], [resolver_with(
            tmp_path, "set-s", anchor_declaration(ENT_X), base,
            superseding, retraction(superseding))], model)

        conflicted = reconcile([bom_set], [resolver_with(
            tmp_path, "set-c", anchor_declaration(ENT_X),
            anchor_declaration(ENT_Y, role="other-thing"),
            subject_assertion(subject, ENT_X),
            subject_assertion(subject, ENT_Y))], model)

        results = [retracted, closed, conflicted]
        for left in range(len(results)):
            for right in range(left + 1, len(results)):
                assert results[left].findings != results[right].findings


class TestQuantityVsModel:
    @pytest.mark.parametrize("lexeme,expected", [
        ("4", True), ("8", True), ("1.0", True), ("01", True),
        ("1", False)])
    def test_m15_lexical_against_the_joined_registered_count(
            self, tmp_path, lexeme, expected):
        bom_set = bom_claim_set(claims=(
            bom_claim(bom_source(), 1, "EXT-100", quantity=lexeme),))
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        resolver = resolver_with(tmp_path, "set-a",
                                 anchor_declaration(ENT_X),
                                 subject_assertion(subject, ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([bom_set], [resolver], model)
        count = literals(result)[
            "quantity_not_reconcilable_with_registered_instances"]
        assert count == (1 if expected else 0)

    def test_m15_absent_lexeme_on_a_declared_quantity_field(self, tmp_path):
        bom_set = bom_claim_set(claims=(
            bom_claim(bom_source(), 1, "EXT-100", quantity=""),))
        subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        resolver = resolver_with(tmp_path, "set-a",
                                 anchor_declaration(ENT_X),
                                 subject_assertion(subject, ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([bom_set], [resolver], model)
        assert literals(result)["evidence_incomplete"] >= 1

    def test_m17_absence_is_informational_and_scoped_to_the_absent_side(
            self, tmp_path):
        """The joined anchor has an accepted relationship to an anchor no
        source supports; the finding names the ABSENT counterpart and no
        RelationshipWithdrawal is ever suggested."""
        from backend.model_kernel import RelationshipWithdrawal  # noqa: F401
        from tests.model_kernel.builders import assertion, contains_type

        bom_set, step_set, resolver, _ = corroborated_pair(tmp_path)
        rtd = contains_type()
        edge = assertion(rtd, source=ENT_X, target=ENT_Y)
        model = store_with(tmp_path, registration(ENT_X),
                           registration(ENT_Y), rtd, edge).load()
        result = reconcile([bom_set, step_set], [resolver], model)
        absent = [f for f in result.findings
                  if f.finding == "absence_is_not_evidence_of_absence"]
        assert [f.anchor_id for f in absent] == [ENT_Y]
        assert all("withdraw" not in f.detail.lower() for f in absent)


class TestContext:
    def test_m20_unknown_and_declared_and_independent_differ(self, tmp_path):
        results = []
        for context in (None,  # unknown default
                        declared_context("as_designed"),
                        declared_context("as_built")):
            bom_set = (bom_claim_set() if context is None
                       else bom_claim_set(context=context))
            subject = subject_for(bom_set.subject_claims[0],
                                  "bom-item-no-v1")
            resolver = resolver_with(tmp_path,
                                     f"set-{len(results)}",
                                     anchor_declaration(ENT_X),
                                     subject_assertion(subject, ENT_X))
            model = model_with(tmp_path, ENT_X)
            results.append(reconcile([bom_set], [resolver], model))
        assert literals(results[0])["context_unknown"] >= 1
        assert literals(results[1])["context_unknown"] == 0
        for left in range(3):
            for right in range(left + 1, 3):
                assert results[left].findings != results[right].findings

    def test_m21_differing_declared_views_block_corroboration(
            self, tmp_path):
        bom_set = bom_claim_set(context=declared_context("as_designed"))
        step_set = step_claim_set(context=declared_context("as_built"))
        bom_subject = subject_for(bom_set.subject_claims[0],
                                  "bom-item-no-v1")
        step_subject = subject_for(step_set.subject_claims[0],
                                   "step-ocaf-entry-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(bom_subject, ENT_X),
            subject_assertion(step_subject, ENT_X))
        model = model_with(tmp_path, ENT_X)
        incompatible = reconcile([bom_set, step_set], [resolver], model)
        assert literals(incompatible)["context_incompatible"] == 1
        assert literals(incompatible)[
            "corroborated_by_all_mapped_sources"] == 0
        # positive twin: same declared view corroborates
        same = reconcile(
            [bom_claim_set(context=declared_context("as_designed")),
             step_claim_set(context=declared_context("as_designed"))],
            [resolver], model)
        assert literals(same)["corroborated_by_all_mapped_sources"] == 1


class TestEvidenceIntegrity:
    def test_m4_declared_payload_universe_missing_a_cited_payload(
            self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        result = StructuralReconciler(
            resolvers=[resolver], rules=RULES, model=model,
            payloads={}).reconcile([bom_set, step_set],
                                   resolution_at=RESOLUTION_AT)
        assert literals(result)["evidence_unavailable"] == 2

    def test_a1_changed_payload_is_named_with_both_checksums(self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        result = StructuralReconciler(
            resolvers=[resolver], rules=RULES, model=model,
            payloads={bom_set.source_ref.raw_record_id: b"other bytes",
                      }).reconcile([bom_set, step_set],
                                   resolution_at=RESOLUTION_AT)
        differs = [f for f in result.findings
                   if f.finding == "cited_payload_checksum_differs"]
        assert len(differs) == 1
        assert "sha256:" in differs[0].detail
        assert bom_set.source_ref.payload_checksum in differs[0].detail

    def test_m24_partial_extraction_blocks_corroboration(self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        partial_bom = bom_claim_set(outcome="partial")
        result = reconcile([partial_bom, step_set], [resolver], model)
        assert literals(result)["evidence_incomplete"] >= 1
        assert literals(result)["corroborated_by_all_mapped_sources"] == 0


class TestComparators:
    def test_cp1_numeric_spellings_are_contradictory(self, tmp_path):
        source_a = bom_source("bom-a")
        source_b = bom_source("bom-b")
        set_a = bom_claim_set(source=source_a, claims=(
            bom_claim(source_a, 1, "EXT-100", quantity="2"),))
        set_b = bom_claim_set(source=source_b, claims=(
            bom_claim(source_b, 1, "EXT-100", quantity="2.0"),))
        subject_a = subject_for(set_a.subject_claims[0], "bom-item-no-v1")
        subject_b = subject_for(set_b.subject_claims[0], "bom-item-no-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(subject_a, ENT_X),
            subject_assertion(subject_b, ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([set_a, set_b], [resolver], model)
        contradictions = [f for f in result.findings
                          if f.finding == "claims_mutually_contradictory"]
        assert len(contradictions) == 1
        [comparison] = [c for c in contradictions[0].comparisons
                        if c.verdict == "mutually_contradictory"]
        assert {comparison.left.operand,
                comparison.right.operand} == {"2", "2.0"}

    def test_cp4_no_comparator_row_is_not_comparable_never_agreement(
            self, tmp_path):
        """BOM quantity vs a STEP set with no quantity column: the only
        honest answer is claims_not_comparable."""
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        result = reconcile([bom_set, step_set], [resolver], model)
        assert literals(result)["claims_not_comparable"] == 1

    def test_cp6_forged_comparison_is_rejected_on_validation(self):
        source = bom_source()
        claim = bom_claim(source, 1, "EXT-100")
        operand = ComparisonOperand(
            subject=subject_for(claim, "bom-item-no-v1"),
            address=claim.address, operand=None)
        forged = ClaimComparison.model_construct(
            comparable="quantity_lexeme", left=operand, right=operand,
            verdict="mutually_contradictory")
        with pytest.raises(ValidationError):
            ClaimComparison.model_validate(forged.model_dump())


class TestSupportInvariants:
    def test_s1_s3_per_basis_empty_support_rejected(self):
        with pytest.raises(ValidationError):
            ReconciliationFinding(finding="duplicate_source_label_not_identity",
                                  basis="source_claim")
        with pytest.raises(ValidationError):
            ReconciliationFinding(finding="mapping_ambiguous",
                                  basis="authority_interpretation")
        with pytest.raises(ValidationError):
            ReconciliationFinding(finding="corroborated_by_all_mapped_sources",
                                  basis="accepted_model_record",
                                  anchor_id=ENT_X)

    def test_basis_must_match_the_frozen_table(self, tmp_path):
        claim = bom_claim(bom_source(), 1, "EXT-100")
        with pytest.raises(ValidationError):
            ReconciliationFinding(
                finding="duplicate_source_label_not_identity",
                basis="accepted_model_record", anchor_id=ENT_X,
                supporting_claims=(claim,),
                model_disclosures=(ModelDisclosure(
                    anchor_id=ENT_X, model_revision_id="mrv_" + "0" * 64,
                    registration_record_id="reg_" + "0" * 64,
                    verified="verified_in_supplied_revision"),))

    def test_anchor_not_registered_exemption_is_record_free(self):
        finding = ReconciliationFinding(
            finding="anchor_not_registered", basis="accepted_model_record",
            anchor_id=ENT_X,
            model_disclosures=(ModelDisclosure(
                anchor_id=ENT_X, model_revision_id="mrv_" + "0" * 64,
                verified="verified_in_supplied_revision"),))
        assert finding.model_disclosures[0].registration_record_id is None
        # the converse: the other two model findings demand a record id
        with pytest.raises(ValidationError):
            ReconciliationFinding(
                finding="corroborated_by_all_mapped_sources",
                basis="accepted_model_record", anchor_id=ENT_X,
                model_disclosures=(ModelDisclosure(
                    anchor_id=ENT_X, model_revision_id="mrv_" + "0" * 64,
                    verified="verified_in_supplied_revision"),))

    def test_s4_fabricated_support_is_unconstructible_in_a_result(
            self, tmp_path):
        """A finding citing a claim that is not a disclosed input fails
        result validation."""
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        result = reconcile([bom_set, step_set], [resolver], model)
        alien = bom_claim(bom_source("alien"), 9, "GHOST-1")
        tampered = result.model_copy(update={"findings": tuple(
            f if f.finding != "corroborated_by_all_mapped_sources"
            else f.model_copy(update={"supporting_claims": (alien,)})
            for f in result.findings)})
        with pytest.raises(ValidationError):
            type(result).model_validate(tampered.model_dump())

    def test_a4_the_basis_table_matches_an_independent_restatement(self):
        expected_authority = {
            "source_subject_unmapped", "mapping_ambiguous",
            "mapping_conflicted", "mappings_jointly_incoherent",
            "context_unknown", "context_incompatible",
            "subject_bound_in_multiple_sets_consistently",
            "mapping_conflicted_across_sets",
            "anchor_declared_in_multiple_sets",
            "required_binding_set_missing", "cited_extraction_not_found"}
        expected_model = {
            "anchor_not_registered",
            "quantity_not_reconcilable_with_registered_instances",
            "corroborated_by_all_mapped_sources"}
        assert len(BASIS_BY_FINDING) == 25
        for finding, basis in BASIS_BY_FINDING.items():
            if finding in expected_model:
                assert basis == "accepted_model_record", finding
            elif finding in expected_authority:
                assert basis == "authority_interpretation", finding
            else:
                assert basis == "source_claim", finding


class TestDuplicateLabels:
    def test_m7_duplicate_label_reported_and_subjects_stay_distinct(
            self, tmp_path):
        source = bom_source()
        bom_set = bom_claim_set(claims=(
            bom_claim(source, 4, "BRK-400", name="Corner bracket"),
            bom_claim(source, 5, "BRK-401", name="Corner bracket")),
            label_column_index=1)
        model = model_with(tmp_path, ENT_X)
        resolver = resolver_with(tmp_path, "set-a",
                                 anchor_declaration(ENT_X))
        result = reconcile([bom_set], [resolver], model)
        duplicates = [f for f in result.findings
                      if f.finding == "duplicate_source_label_not_identity"]
        assert len(duplicates) == 1
        assert len(duplicates[0].supporting_claims) == 2
        distinct = {s.subject.subject_identifier
                    for d in result.claim_sets
                    for s in d.resolved_subjects
                    if s.subject and s.rule_id == "bom-item-no-v1"}
        assert distinct == {"BRK-400", "BRK-401"}


class TestDeterminismAndDigest:
    def test_m1_reversed_claim_set_order_changes_nothing(self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        forward = reconcile([bom_set, step_set], [resolver], model)
        reverse = reconcile([step_set, bom_set], [resolver], model)
        assert forward == reverse
        assert forward.inputs_digest == reverse.inputs_digest

    def test_a7_cs8_digest_sensitivity(self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        base = reconcile([bom_set, step_set], [resolver], model)
        digests = {base.inputs_digest}
        # a claim lexeme
        digests.add(reconcile(
            [bom_claim_set(claims=(bom_claim(bom_source(), 1, "EXT-100",
                                             quantity="8"),)), step_set],
            [resolver], model).inputs_digest)
        # the model revision
        bigger = model_with(tmp_path, ENT_X, ENT_Y)
        digests.add(reconcile([bom_set, step_set], [resolver],
                              bigger).inputs_digest)
        # the binding revision
        richer = resolver_with(
            tmp_path, "set-a2", anchor_declaration(ENT_X),
            subject_assertion(subject_for(bom_set.subject_claims[0],
                                          "bom-item-no-v1"), ENT_X))
        digests.add(reconcile([bom_set, step_set], [richer],
                              model).inputs_digest)
        # resolution_at
        reconciler = StructuralReconciler(resolvers=[resolver], rules=RULES,
                                          model=model)
        digests.add(reconciler.reconcile(
            [bom_set, step_set],
            resolution_at=RESOLUTION_AT.replace(hour=14)).inputs_digest)
        # required set ids
        digests.add(StructuralReconciler(
            resolvers=[resolver], rules=RULES, model=model,
            required_binding_set_ids=frozenset({"set-a", "ghost"})
        ).reconcile([bom_set, step_set],
                    resolution_at=RESOLUTION_AT).inputs_digest)
        assert len(digests) == 6

    def test_digest_recomputes_from_disclosed_fields_only(self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        result = reconcile([bom_set, step_set], [resolver], model)
        assert result.inputs_digest == compute_inputs_digest(result)
        assert result.inputs_digest.startswith("sid_")

    def test_m2_digest_is_stable_across_hash_seeds(self, tmp_path):
        """Golden-form determinism: the digest formula over a fixed
        arrangement is identical under different PYTHONHASHSEED values."""
        program = (
            "from tests.structural_evidence.test_reconcile import "
            "corroborated_pair, reconcile;"
            "import tempfile, pathlib;"
            "tmp = pathlib.Path(tempfile.mkdtemp());"
            "bom_set, step_set, resolver, model = corroborated_pair(tmp);"
            "print(reconcile([bom_set, step_set], [resolver], model)"
            ".inputs_digest)")
        outputs = set()
        for seed in ("1", "2"):
            run = subprocess.run(
                [sys.executable, "-c", program], capture_output=True,
                text=True, env={"PYTHONHASHSEED": seed, "PYTHONPATH": ".",
                                "PATH": "/usr/bin:/bin"}, check=True)
            outputs.add(run.stdout.strip())
        assert len(outputs) == 1

    def test_m29_no_wall_clock_and_no_network(self, tmp_path):
        import ast
        from pathlib import Path

        for path in sorted(Path("backend/structural_evidence").glob("*.py")):
            text = path.read_text("utf-8")
            for needle in ("datetime.now", "utcnow", "time.time", "socket",
                           "urllib.request", "requests", "http.client"):
                assert needle not in text, (needle, path.name)

    def test_a3_the_finding_multiset_covers_every_subject(self, tmp_path):
        bom_set, step_set, resolver, model = corroborated_pair(tmp_path)
        result = reconcile([bom_set, step_set], [resolver], model)
        expected = Counter({
            "corroborated_by_all_mapped_sources": 1,
            "claims_not_comparable": 1,
            "quantity_not_reconcilable_with_registered_instances": 1,
            "context_unknown": 2,
            "subject_bound_in_multiple_sets_consistently": 0,
        })
        found = literals(result)
        for literal, count in expected.items():
            assert found[literal] == count, literal
        # coverage: every subject-bearing resolved subject appears
        covered = {f.subject for f in result.findings if f.subject}
        covered |= {s.subject
                    for d in result.claim_sets
                    for s in d.resolved_subjects
                    if s.join_anchor_id and s.join_anchor_id in
                    {f.anchor_id for f in result.findings if f.anchor_id}}
        for disclosure in result.claim_sets:
            for subject in disclosure.resolved_subjects:
                if subject.subject is not None:
                    assert subject.subject in covered


class TestA12NegativeCorpus:
    def test_committed_incoherent_fixtures_yield_only_unmapped(
            self, tmp_path):
        """bom_valid.csv against BOTH committed binding sets: zero
        structural mappings exist, so every subject is unmapped and
        nothing else is reachable."""
        import shutil
        from datetime import timedelta
        from pathlib import Path

        from backend.data_sources.catalog import InMemorySourceCatalog
        from backend.data_sources.connectors import LocalFileConnector
        from backend.data_sources.contracts import SourceDefinition
        from backend.data_sources.raw_store import FilesystemRawStore
        from backend.data_sources.runtime import IngestionRunner
        from backend.identity_binding.resolver import BindingResolver
        from backend.identity_binding.store import BindingStore
        from backend.model_kernel import ModelStore
        from backend.structural_evidence.claims import (
            CsvStructuralReading,
            csv_structural_claims,
        )
        from backend.structural_evidence.contracts import (
            UnknownEngineeringContext,
        )

        path = tmp_path / "bom.csv"
        shutil.copy(Path("backend/data_sources/testing/fixtures/"
                         "bom_valid.csv"), path)
        catalog = InMemorySourceCatalog()
        catalog.register(SourceDefinition(
            source_id="bom-neg", display_name="b",
            source_kind="tabular_file", connector_type="local_file",
            configuration={"path": str(path)}, credential_reference=None,
            declared_content_types=["text/csv"], enabled=True))
        store = FilesystemRawStore(tmp_path / "raw_store")
        clock_state = [datetime(2026, 8, 11, 12, 0, tzinfo=UTC)]

        def clock():
            clock_state[0] += timedelta(seconds=1)
            return clock_state[0]

        IngestionRunner(catalog=catalog, store=store,
                        connectors={"local_file": LocalFileConnector()},
                        clock=clock).run("bom-neg")
        envelope = next(store.iter_accepted_envelopes("bom-neg"))
        claims = csv_structural_claims(
            store.get_extraction(envelope.record_id), source_id="bom-neg",
            payload_checksum=envelope.payload_checksum,
            engineering_context=UnknownEngineeringContext(
                kind="unknown", reason="authority_has_not_declared"),
            reading=CsvStructuralReading(quantity_column_index=2,
                                         parent_column_index=4,
                                         parent_matches_column_index=0))
        resolvers = [
            BindingResolver(BindingStore(Path("bindings/demo-printer")
                                         ).load()),
            BindingResolver(BindingStore(Path("bindings/demo-printer-model")
                                         ).load())]
        model = ModelStore(Path("models/demo-printer")).load()
        result = StructuralReconciler(
            resolvers=resolvers, rules=RULES, model=model).reconcile(
            [claims], resolution_at=RESOLUTION_AT)
        found = literals(result)
        # 6 rows x 2 applicable BOM rules = 12 unmapped subjects; the
        # context-unknown disclosure is NOT emitted for unmapped subjects.
        # Since the SN-001c appends, the committed sets also carry three
        # sx1 structural mappings (iba_S1, iba_S2, iba_S4) whose showcase
        # sources this negative arrangement deliberately does NOT supply:
        # the honest multiset therefore includes exactly three
        # cited_extraction_not_found findings.
        assert found["source_subject_unmapped"] == 12
        assert found["cited_extraction_not_found"] == 3
        for absent in ("claims_mutually_contradictory",
                       "corroborated_by_all_mapped_sources",
                       "quantity_not_reconcilable_with_registered_instances",
                       "anchor_not_registered"):
            assert found[absent] == 0, absent
        assert set(found) == {"source_subject_unmapped",
                              "cited_extraction_not_found"}


class TestOneSidedSupport:
    def test_m16_bom_only_and_step_only_are_distinct_per_anchor(
            self, tmp_path):
        bom_set = bom_claim_set()
        step_source_ref = step_source()
        step_set = step_claim_set(source=step_source_ref, claims=(
            step_definition_claim(step_source_ref, "0:1:1:5", "hotend-fan"),))
        bom_subject = subject_for(bom_set.subject_claims[0], "bom-item-no-v1")
        step_subject = subject_for(step_set.subject_claims[0],
                                   "step-ocaf-entry-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            anchor_declaration(ENT_Y, role="other-thing"),
            subject_assertion(bom_subject, ENT_X),
            subject_assertion(step_subject, ENT_Y))
        model = model_with(tmp_path, ENT_X, ENT_Y)
        result = reconcile([bom_set, step_set], [resolver], model)
        by_anchor = {f.anchor_id: f.finding for f in result.findings
                     if f.finding in ("supported_by_bom_only",
                                      "supported_by_step_only")}
        assert by_anchor == {ENT_X: "supported_by_bom_only",
                             ENT_Y: "supported_by_step_only"}

    def test_m18_contradiction_carries_both_claims_verbatim(self, tmp_path):
        source_a = bom_source("bom-a")
        source_b = bom_source("bom-b")
        set_a = bom_claim_set(source=source_a, claims=(
            bom_claim(source_a, 1, "EXT-100", quantity="2"),))
        set_b = bom_claim_set(source=source_b, claims=(
            bom_claim(source_b, 1, "EXT-100", quantity="8"),))
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(subject_for(set_a.subject_claims[0],
                                          "bom-item-no-v1"), ENT_X),
            subject_assertion(subject_for(set_b.subject_claims[0],
                                          "bom-item-no-v1"), ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([set_a, set_b], [resolver], model)
        [finding] = [f for f in result.findings
                     if f.finding == "claims_mutually_contradictory"]
        assert set_a.subject_claims[0] in finding.supporting_claims
        assert set_b.subject_claims[0] in finding.supporting_claims


class TestJointIncoherenceAndIdentityDrift:
    def test_a2_definition_and_usage_on_one_anchor_is_jointly_incoherent(
            self, tmp_path):
        """One anchor cannot be both the reusable definition and a
        particular usage; each mapping is legal alone."""
        from backend.structural_evidence.locators import StepUsageLocator
        from backend.structural_evidence.contracts import (
            SourceNativeField,
            SourceStructuralClaim,
        )
        from backend.structural_evidence.locators import StructuralAddress

        source = step_source()
        definition_claim = step_definition_claim(source, "0:1:1:2",
                                                 "extruder-unit")
        usage_address = StructuralAddress(
            source=source,
            locator=StepUsageLocator(
                kind="step_nauo_usage", extractor_path_id="0:1:1:1:1",
                upstream_instance_id="cc" * 16,
                definition_path_id="0:1:1:2",
                parent_definition_path_id="0:1:1:1"))
        usage_claim = SourceStructuralClaim(
            claim_kind="step_nauo_usage", address=usage_address,
            fields=(SourceNativeField(field_name_as_extracted="name",
                                      lexeme="extruder-1",
                                      address=usage_address),))
        step_set = step_claim_set(source=source,
                                  claims=(definition_claim, usage_claim))
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(subject_for(definition_claim,
                                          "step-ocaf-entry-v1"), ENT_X),
            subject_assertion(subject_for(usage_claim,
                                          "step-ocaf-entry-v1"), ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([step_set], [resolver], model)
        assert literals(result)["mappings_jointly_incoherent"] == 1
        assert literals(result)["corroborated_by_all_mapped_sources"] == 0

    def test_f5_a_mapping_citing_an_unsupplied_structural_source(
            self, tmp_path):
        """An sx1-namespaced mapping exists but no claim set from that
        source was supplied: the mapping cites an extraction that is not
        there."""
        bom_set = bom_claim_set()
        ghost = subject_for(
            bom_claim(bom_source("ghost-source"), 1, "GHOST-1"),
            "bom-item-no-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(ghost, ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([bom_set], [resolver], model)
        assert literals(result)["cited_extraction_not_found"] == 1

    def test_f6_a_toolchain_shift_is_named_not_silently_unmapped(
            self, tmp_path):
        """The mapping was authored against a different toolchain
        fingerprint for the same source/extractor/rule: the finding says
        'the toolchain moved under you', never just 'unmapped'."""
        step_set = step_claim_set()
        old_extractor = step_source().extractor.model_copy(
            update={"toolchain": "cadquery-ocp 7.8.0"})
        old_source = step_source().model_copy(
            update={"extractor": old_extractor})
        old_claim = step_definition_claim(old_source, "0:1:1:2",
                                          "extruder-unit")
        old_subject = subject_for(old_claim, "step-ocaf-entry-v1")
        resolver = resolver_with(
            tmp_path, "set-a", anchor_declaration(ENT_X),
            subject_assertion(old_subject, ENT_X))
        model = model_with(tmp_path, ENT_X)
        result = reconcile([step_set], [resolver], model)
        assert literals(result)["extractor_identity_changed"] == 1


class TestA5fPublishedWording:
    def test_resolution_at_semantics_verbatim(self):
        from pathlib import Path
        text = " ".join(Path("backend/structural_evidence/README.md")
                        .read_text("utf-8").split())
        assert ("`resolution_at` is a required, timezone-aware instant on "
                "the ingestion-receipt axis") in text
        assert "It is not a wall clock" in text
