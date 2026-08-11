"""StructuralAddress <-> kernel evidence conversion (X1, X1b, X2, X3, X4, X6).

The locator half is a bijection on IDENTITY: the canonical value and every
identity field round-trip exactly. Disclosure-only display names
(`column_name_as_extracted`) are — like `source_id` and the toolchain
prose — not carried by a citation: the canonical value deliberately
excludes them (L2), so reconstruction yields an empty disclosure name.
The source half is a documented projection whose two drops are REQUIRED
keyword arguments of the inverse — a typed obligation, never a silent
default.
"""

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.model_kernel import StructuralSourceLocatorEvidence
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

EXTRACTOR = ExtractorIdentity(
    name="step_extractor", version="1.0.0",
    toolchain="cadquery-ocp 7.9.3.1.1",
    config_fingerprint="2b7e91c4a05d6f38")
SOURCE = StructuralSourceRef(
    source_id="showcase-printer-cad", raw_record_id="bf" * 16,
    payload_checksum="sha256:" + "ab" * 32, extractor=EXTRACTOR)

LOCATORS = [
    CsvRowLocator(kind="csv_row", physical_row_index=3),
    CsvCellLocator(kind="csv_cell", physical_row_index=3, column_index=2,
                   column_name_as_extracted=""),
    StepDefinitionLocator(kind="step_part_definition",
                          extractor_path_id="0:1:1:2",
                          upstream_definition_id="27" * 16),
    StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1:1:3:1",
                     upstream_instance_id="83" * 16,
                     definition_path_id="0:1:1:4",
                     parent_definition_path_id="0:1:1:3"),
    # the synthesized-root case: None parent
    StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1:1:1",
                     upstream_instance_id="93" * 16,
                     definition_path_id="0:1:1:1",
                     parent_definition_path_id=None),
    # adversarial separators and a single-hyphen parent path
    StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1;d=x",
                     upstream_instance_id="aa" * 16,
                     definition_path_id="a/b%3A",
                     parent_definition_path_id="-"),
]


def address(locator) -> StructuralAddress:
    return StructuralAddress(source=SOURCE, locator=locator)


class TestX1LocatorRoundTrip:
    @pytest.mark.parametrize("locator", LOCATORS,
                             ids=lambda l: l.kind + ":" +
                             canonical_locator_value(l)[:24])
    def test_identity_round_trips_exactly(self, locator):
        projection = to_kernel_evidence(address(locator))
        back = from_kernel_evidence(
            projection.evidence, source_id=SOURCE.source_id,
            extractor_toolchain=EXTRACTOR.toolchain)
        assert canonical_locator_value(back.locator) == \
            canonical_locator_value(locator)
        assert back.locator.kind == locator.kind
        assert back.source == SOURCE

    def test_x1b_evidence_round_trips_byte_exactly(self):
        for locator in LOCATORS:
            projection = to_kernel_evidence(address(locator))
            back = from_kernel_evidence(
                projection.evidence, source_id=SOURCE.source_id,
                extractor_toolchain=EXTRACTOR.toolchain)
            again = to_kernel_evidence(back)
            assert again.evidence == projection.evidence


class TestX2VerbatimSourceCarriage:
    def test_source_fields_carried_verbatim(self):
        evidence = to_kernel_evidence(address(LOCATORS[0])).evidence
        assert evidence.raw_record_id == SOURCE.raw_record_id
        assert evidence.payload_checksum == SOURCE.payload_checksum
        assert evidence.extractor_name == EXTRACTOR.name
        assert evidence.extractor_version == EXTRACTOR.version
        assert evidence.extractor_config_fingerprint == \
            EXTRACTOR.config_fingerprint
        assert evidence.extractor_toolchain_fingerprint == \
            toolchain_fingerprint(EXTRACTOR)


class TestX3NamedDrops:
    def test_dropped_is_the_exact_sorted_literal(self):
        projection = to_kernel_evidence(address(LOCATORS[0]))
        assert projection.dropped == ("extractor_toolchain", "source_id")

    def test_the_drops_are_required_keywords_of_the_inverse(self):
        evidence = to_kernel_evidence(address(LOCATORS[0])).evidence
        with pytest.raises(TypeError):
            from_kernel_evidence(evidence)  # noqa - deliberate


class TestX4NoBindingVocabularyInTheArm:
    def test_arm_field_names_and_values_avoid_the_accepted_needles(self):
        """Commit 16 lifts the accepted sweeps' needle lists into
        importable constants and re-anchors this test to import them;
        until then the list is restated verbatim from
        tests/model_state/test_isolation.py."""
        needles = ("source_id", "adapter_id", "json_pointer",
                   "extraction_route", "item_key", "value_json",
                   "received_at", "occurrence", "staleness", "moonraker")
        assert len(needles) == 10
        field_names = set(StructuralSourceLocatorEvidence.model_fields)
        for needle in needles:
            for name in field_names:
                assert needle not in name, (needle, name)
        corpus = [to_kernel_evidence(address(l)).evidence.model_dump_json()
                  for l in LOCATORS]
        assert len(corpus) >= 5
        for dumped in corpus:
            for needle in needles:
                assert needle not in dumped, needle


class TestX6TypedOverflow:
    def test_oversized_canonical_value_is_typed_never_raw(self):
        locator = StepDefinitionLocator(
            kind="step_part_definition", extractor_path_id=":" * 400,
            upstream_definition_id="aa" * 16)
        with pytest.raises(StructuralEvidenceError) as err:
            to_kernel_evidence(address(locator))
        assert err.value.error_code == "SN_LOCATOR_TOO_LONG"
        with pytest.raises(ValidationError):
            # and the kernel contract itself rejects it independently
            StructuralSourceLocatorEvidence(
                kind="structural_source_locator", raw_record_id="bf" * 16,
                payload_checksum="sha256:" + "ab" * 32,
                extractor_name="step_extractor", extractor_version="1.0.0",
                extractor_config_fingerprint="2b7e91c4a05d6f38",
                extractor_toolchain_fingerprint="1be707a7751618e9",
                locator_scheme="step_part_definition",
                locator_value="p=" + "%3A" * 400)
