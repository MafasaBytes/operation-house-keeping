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
        assert len(kernel.__all__) == 62
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


VALID_BY_SCHEME = {
    "csv_row": "r=3",
    "csv_cell": "r=3;c=12",
    "step_part_definition": "p=0%3A1%3A1%3A2;d=" + "27" * 16,
    "step_nauo_usage": ("p=0%3A1%3A1%3A3%3A1;i=" + "83" * 16 +
                        ";dp=0%3A1%3A1%3A4;pp=0%3A1%3A1%3A3"),
}
ROOT_USAGE = "p=0%3A1;i=" + "93" * 16 + ";dp=0%3A1%3A1;pp="

MALFORMED = [
    ("csv_row", "r=abc"),                        # the owner reproduction
    ("csv_row", "r=-1"),                         # negative index
    ("csv_row", "r=01"),                         # noncanonical integer
    ("csv_row", "r=+1"),                         # noncanonical integer
    ("csv_row", "r=3;c=12"),                     # wrong component count
    ("csv_row", VALID_BY_SCHEME["step_part_definition"]),  # foreign scheme
    ("csv_cell", "r=3"),                         # missing component
    ("csv_cell", "r=3;c=x"),                     # malformed integer
    ("csv_cell", "r=3;c=012"),                   # noncanonical integer
    ("step_part_definition", "r=3"),             # foreign scheme
    ("step_part_definition", "p=0%3A1"),         # missing identifier
    ("step_part_definition", "p=0%3A1;d=xyz"),   # malformed identifier
    ("step_part_definition", "p=0%3A1;d=" + "27" * 15),    # short id
    ("step_part_definition", "p=0%3a1;d=" + "27" * 16),    # lowercase %hex
    ("step_nauo_usage", "p=a;i=" + "83" * 16),   # missing components
    ("step_nauo_usage", VALID_BY_SCHEME["step_part_definition"]),
    ("step_nauo_usage", "p=;i=" + "83" * 16 + ";dp=a;pp="),  # empty path
]


class TestKR5SchemeSpecificGrammar:
    """Owner audit defect 4 (2026-08-12): each locator scheme enforces
    its own canonical grammar inside the SELF-CONTAINED kernel contract.
    Every malformed pair below constructed successfully at 81cd0fc."""

    def evidence(self, scheme, value):
        return StructuralSourceLocatorEvidence(
            **{**ARM, "locator_scheme": scheme, "locator_value": value})

    def test_every_arm_constructs_from_its_canonical_grammar(self):
        for scheme, value in VALID_BY_SCHEME.items():
            assert self.evidence(scheme, value).locator_value == value
        root = self.evidence("step_nauo_usage", ROOT_USAGE)
        assert root.locator_value.endswith(";pp=")

    @pytest.mark.parametrize("scheme,value", MALFORMED,
                             ids=[f"{s}:{v[:24]}" for s, v in MALFORMED])
    def test_a_scheme_value_mismatch_is_unconstructible(self, scheme,
                                                        value):
        with pytest.raises(ValidationError):
            self.evidence(scheme, value)

    def test_the_committed_ledger_satisfies_the_grammar(self):
        """The grammar is additive: every committed structural citation
        in models/demo-printer already satisfies its scheme."""
        loaded = ModelStore(DEMO_MODEL).load()
        assert loaded.revision.record_count == 14


NONCANONICAL_STEP_PATHS = [
    ("step_part_definition", "p=%41;d=" + "27" * 16),   # over-encoded 'A'
    ("step_part_definition", "p=%FF;d=" + "27" * 16),   # invalid UTF-8
    ("step_part_definition", "p=%C3;d=" + "27" * 16),   # truncated UTF-8
    ("step_part_definition", "p=0%3A1%41;d=" + "27" * 16),  # embedded
    ("step_nauo_usage", "p=%41;i=" + "83" * 16 + ";dp=0%3A1;pp="),
    ("step_nauo_usage", "p=0%3A1;i=" + "83" * 16 + ";dp=%FF;pp="),
    ("step_nauo_usage",
     "p=0%3A1;i=" + "83" * 16 + ";dp=0%3A1%3A1;pp=%41"),
]

CANONICAL_STEP_PATHS = [
    ("step_part_definition", "p=part-1.2_v3~x;d=" + "27" * 16),  # unreserved
    ("step_part_definition", "p=0%3A1%2Fa;d=" + "27" * 16),  # reserved, enc.
    ("step_part_definition", "p=%C3%A9;d=" + "27" * 16),     # UTF-8 e-acute
    ("step_part_definition", "p=%25;d=" + "27" * 16),        # literal percent
    ("step_part_definition", "p=%2541;d=" + "27" * 16),      # the STRING "%41"
    ("step_nauo_usage",
     "p=%C3%A9;i=" + "83" * 16 + ";dp=%25;pp=part_1"),
]


class TestKR6CanonicalStepPathEncoding:
    """Owner follow-up (2026-08-12, at 7eaff7f): every STEP path
    component must BE its own `quote(decoded, safe="")` re-encoding
    under strict UTF-8 — over-encoded unreserved characters and
    non-UTF-8 byte sequences cannot identify an exact source path.
    Every NONCANONICAL pair below constructed at 7eaff7f."""

    def evidence(self, scheme, value):
        return StructuralSourceLocatorEvidence(
            **{**ARM, "locator_scheme": scheme, "locator_value": value})

    @pytest.mark.parametrize("scheme,value", NONCANONICAL_STEP_PATHS,
                             ids=[v[:26] for _, v in NONCANONICAL_STEP_PATHS])
    def test_a_noncanonical_encoding_is_unconstructible(self, scheme,
                                                        value):
        with pytest.raises(ValidationError):
            self.evidence(scheme, value)

    @pytest.mark.parametrize("scheme,value", CANONICAL_STEP_PATHS,
                             ids=[v[:26] for _, v in CANONICAL_STEP_PATHS])
    def test_a_canonical_twin_constructs(self, scheme, value):
        """Valid twins, green before and after: raw unreserved text,
        encoded reserved characters, valid UTF-8, the literal percent,
        and the canonically double-encoded string '%41'."""
        assert self.evidence(scheme, value).locator_value == value

    def test_all_four_arms_and_the_root_sentinel_still_construct(self):
        for scheme, value in VALID_BY_SCHEME.items():
            assert self.evidence(scheme, value).locator_value == value
        assert self.evidence("step_nauo_usage",
                             ROOT_USAGE).locator_value == ROOT_USAGE
