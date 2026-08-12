"""Owner follow-up integrity-repair regressions (2026-08-12, at 7eaff7f).

Two additional contract reproductions from the owner's independent
verification of the audit repair. Failing-before evidence:
docs/superpowers/plans/2026-08-12-sn001-owner-followup-red-baseline.md.
The kernel-constructor half of reproduction 1 lives in
tests/model_kernel/test_structural_evidence_arm.py
(TestKR6CanonicalStepPathEncoding); this file holds the structural
inversion twins and the derived-path reproduction.
"""

import pytest
from pydantic import ValidationError

from backend.model_kernel import StructuralSourceLocatorEvidence
from backend.structural_evidence.contracts import (
    DerivedUsagePath,
    SourceStructuralClaim,
    SourceStructuralClaimSet,
)
from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.locators import (
    StepUsageLocator,
    StructuralAddress,
    from_kernel_evidence,
    toolchain_fingerprint,
)

from tests.structural_evidence.helpers import (
    STEP_EXTRACTOR,
    UNKNOWN,
    step_source,
)


def usage_locator(path, definition, parent) -> StepUsageLocator:
    return StepUsageLocator(kind="step_nauo_usage", extractor_path_id=path,
                            upstream_instance_id="cc" * 16,
                            definition_path_id=definition,
                            parent_definition_path_id=parent)


# MID uses definition 0:1:1 inside the root definition 0:1; LEAF uses
# definition 0:1:1:2 inside MID's definition — a coherent two-level chain.
MID = usage_locator("0:1:2", "0:1:1", "0:1")
LEAF = usage_locator("0:1:3", "0:1:1:2", "0:1:1")
STRAY = usage_locator("0:9:9", "0:9:1", "0:9")
INCOHERENT = usage_locator("0:8:1", "0:8", "0:1")  # wrong definition for LEAF


def usage_claim(source, locator) -> SourceStructuralClaim:
    return SourceStructuralClaim(
        claim_kind="step_nauo_usage",
        address=StructuralAddress(source=source, locator=locator))


def unique_path(for_usage, steps) -> DerivedUsagePath:
    return DerivedUsagePath(derivation="nauo_parent_definition_chain_v1",
                            for_usage=for_usage, steps=steps,
                            ambiguity="unique")


def claim_set_with(source, claims, paths) -> SourceStructuralClaimSet:
    return SourceStructuralClaimSet(
        source_ref=source, engineering_context=UNKNOWN,
        subject_claims=claims, derived_paths=paths,
        quantity_field=None, extraction_outcome="succeeded")


class TestF2DerivedPathStepsEvidenceBacked:
    def test_the_owner_reproduction_is_unconstructible(self):
        """A unique path whose steps smuggle a StepUsageLocator absent
        from the claim set constructed at 7eaff7f."""
        source = step_source()
        with pytest.raises(ValidationError):
            claim_set_with(source, (usage_claim(source, LEAF),),
                           (unique_path(LEAF, (STRAY, LEAF)),))

    def test_a_unique_path_ends_at_its_for_usage(self):
        source = step_source()
        claims = (usage_claim(source, MID), usage_claim(source, LEAF))
        with pytest.raises(ValidationError):
            claim_set_with(source, claims, (unique_path(LEAF, (MID,)),))

    def test_adjacent_steps_must_chain_parent_to_child(self):
        """INCOHERENT is disclosed, but LEAF's parent_definition_path_id
        (0:1:1) is not INCOHERENT's definition_path_id (0:8)."""
        source = step_source()
        claims = (usage_claim(source, INCOHERENT),
                  usage_claim(source, LEAF))
        with pytest.raises(ValidationError):
            claim_set_with(source, claims,
                           (unique_path(LEAF, (INCOHERENT, LEAF)),))

    def test_repeated_steps_are_rejected(self):
        source = step_source()
        with pytest.raises(ValidationError):
            claim_set_with(source, (usage_claim(source, LEAF),),
                           (unique_path(LEAF, (LEAF, LEAF)),))

    def test_valid_twin_direct_root_usage(self):
        """Valid twin: a single-step chain for a usage directly under
        the root definition."""
        source = step_source()
        claim_set = claim_set_with(source, (usage_claim(source, MID),),
                                   (unique_path(MID, (MID,)),))
        assert claim_set.derived_paths[0].steps == (MID,)

    def test_valid_twin_multi_level_unique_chain(self):
        """Valid twin: a coherent root-first two-level chain whose every
        step is a disclosed usage claim."""
        source = step_source()
        claims = (usage_claim(source, MID), usage_claim(source, LEAF))
        claim_set = claim_set_with(source, claims,
                                   (unique_path(LEAF, (MID, LEAF)),))
        assert claim_set.derived_paths[0].steps == (MID, LEAF)

    def test_ambiguous_paths_still_carry_no_steps(self):
        """Retained rule: ambiguity gates steps at the DerivedUsagePath
        contract itself."""
        with pytest.raises(ValidationError):
            DerivedUsagePath(derivation="nauo_parent_definition_chain_v1",
                             for_usage=LEAF, steps=(MID,),
                             ambiguity="multiple_parent_uses")


class TestF1ForgedNoncanonicalCitationsStayTyped:
    """Retained twins (green at 7eaff7f): the structural inversion
    already refuses noncanonical spellings via the canonical
    re-encoding guard with the typed error; the kernel-constructor half
    is the failing-before reproduction (TestKR6)."""

    def forge(self, value):
        return StructuralSourceLocatorEvidence.model_construct(
            kind="structural_source_locator", raw_record_id="bf" * 16,
            payload_checksum="sha256:" + "ab" * 32,
            extractor_name=STEP_EXTRACTOR.name,
            extractor_version=STEP_EXTRACTOR.version,
            extractor_config_fingerprint=STEP_EXTRACTOR.config_fingerprint,
            extractor_toolchain_fingerprint=toolchain_fingerprint(
                STEP_EXTRACTOR),
            locator_scheme="step_part_definition", locator_value=value)

    @pytest.mark.parametrize("value", ["p=%41;d=" + "27" * 16,
                                       "p=%FF;d=" + "27" * 16])
    def test_a_forged_noncanonical_citation_is_typed(self, value):
        with pytest.raises(StructuralEvidenceError) as err:
            from_kernel_evidence(
                self.forge(value), source_id="showcase-printer-cad",
                extractor_toolchain=STEP_EXTRACTOR.toolchain)
        assert err.value.error_code == "SN_LOCATOR_VALUE_INVALID"
