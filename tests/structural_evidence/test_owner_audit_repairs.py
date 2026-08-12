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


