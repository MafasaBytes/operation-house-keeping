"""D3: the additive StructuralSourceLocatorEvidence union arm (KR1-KR4, X5).

The arm is SELF-CONTAINED in the kernel contract: canonical scalars only,
nothing imported, nothing resolved, nothing verified — disclosure is
always declared_reference. Every committed record id must remain
byte-for-byte valid under the six-arm union.
"""

from pathlib import Path

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from backend.model_kernel import (
    AuthorityRef,
    ModelQueries,
    ModelStore,
    OwnerDeclarationEvidence,
    StructuralSourceLocatorEvidence,
    build_record,
)
from backend.model_kernel.canonical import verify_record_id

DEMO_MODEL = Path("models/demo-printer")
CURRENT_REVISION = ("mrv_702c840f7da00617feb1be252838105d8b001b2e199788"
                    "42bdcbec56996c99ff")  # 14 records (SN-001)

ARM = dict(
    kind="structural_source_locator",
    raw_record_id="bf4c84d44f569cd712d9281aa2f8d428",
    payload_checksum="sha256:" + "ab" * 32,
    extractor_name="step_extractor",
    extractor_version="1.0.0",
    extractor_config_fingerprint="2b7e91c4a05d6f38",
    extractor_toolchain_fingerprint="1be707a7751618e9",
    locator_scheme="step_part_definition",
    locator_value="p=0%3A1%3A1%3A2;d=" + "27" * 16,
)


class TestKR1CommittedLedgerUnchanged:
    def test_all_committed_ids_verify_under_the_six_arm_union(self):
        loaded = ModelStore(DEMO_MODEL).load()
        assert loaded.revision.record_count == 14
        assert loaded.revision.revision_id == CURRENT_REVISION
        for record in loaded.records.values():
            assert verify_record_id(record), record.record_id


class TestKR2ArmContract:
    def test_constructs_from_canonical_scalars_only(self):
        arm = StructuralSourceLocatorEvidence(**ARM)
        assert arm.locator_value.startswith("p=")

    def test_locator_value_rejects_a_bare_32_hex_and_wrong_prefixes(self):
        for bad in ("ab" * 16, "x=1", "", "r" * 511):
            with pytest.raises(ValidationError):
                StructuralSourceLocatorEvidence(**{**ARM,
                                                   "locator_value": bad})

    def test_every_field_is_pattern_bound(self):
        for field, bad in (("raw_record_id", "zz"),
                           ("payload_checksum", "md5:00"),
                           ("extractor_name", "Step Extractor"),
                           ("extractor_version", ""),
                           ("extractor_config_fingerprint", "xyz"),
                           ("extractor_toolchain_fingerprint", "ab")):
            with pytest.raises(ValidationError):
                StructuralSourceLocatorEvidence(**{**ARM, field: bad})

    def test_csv_scheme_value(self):
        arm = StructuralSourceLocatorEvidence(
            **{**ARM, "locator_scheme": "csv_row", "locator_value": "r=2"})
        assert arm.locator_scheme == "csv_row"


class TestKR3PublicSurface:
    def test_all_has_54_names_and_every_name_resolves(self):
        assert len(kernel.__all__) == 54
        assert "StructuralSourceLocatorEvidence" in kernel.__all__
        for name in kernel.__all__:
            assert getattr(kernel, name) is not None


class TestX5DeclaredReferenceDisclosure:
    def test_a_real_assertion_carrying_the_arm_discloses_declared(
            self, tmp_path):
        from tests.model_kernel.builders import (
            AS_BUILT,
            ENT_A,
            ENT_B,
            assertion,
            contains_type,
            registration,
            store_with,
        )

        rtd = contains_type()
        rel = assertion(
            rtd, evidence=(
                OwnerDeclarationEvidence(
                    kind="owner_declaration",
                    statement="Synthetic; carries the structural arm."),
                StructuralSourceLocatorEvidence(**ARM)))
        store = store_with(tmp_path, registration(ENT_A),
                           registration(ENT_B), rtd, rel)
        loaded = store.load()
        result = ModelQueries(loaded).relationships(
            ENT_A, direction="outgoing", context=AS_BUILT)
        [summary] = result.active
        disclosures = {d.ref.kind: d.verification for d in summary.evidence}
        assert disclosures["structural_source_locator"] == \
            "declared_reference"
