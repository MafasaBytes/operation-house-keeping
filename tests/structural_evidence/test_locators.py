"""SN-001 payload-pinned locators (L1, L2, L3).

A structural locator is an evidence ADDRESS — "row 3 of these bytes" —
never an identity. The canonical locator value must be injective per
scheme, and its length bound is on the CANONICAL value (percent-encoding
expands up to 3x), enforced as a typed error, never a raw pydantic error
at the kernel boundary.
"""

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.structural_evidence.errors import StructuralEvidenceError
from backend.structural_evidence.locators import (
    CsvCellLocator,
    CsvRowLocator,
    StepDefinitionLocator,
    StepUsageLocator,
    StructuralAddress,
    StructuralSourceRef,
    canonical_locator_value,
)

EXTRACTOR = ExtractorIdentity(
    name="csv_extractor", version="1.1.0", toolchain="cpython-3.13 stdlib csv",
    config_fingerprint="6f1c2a9d0b3e4517")
CHECKSUM = "sha256:" + "ab" * 32
RAW_ID = "cd" * 16


def source_ref() -> StructuralSourceRef:
    return StructuralSourceRef(
        source_id="showcase-printer-bom", raw_record_id=RAW_ID,
        payload_checksum=CHECKSUM, extractor=EXTRACTOR)


class TestL1Construction:
    def test_source_ref_requires_all_four_dimensions(self):
        ref = source_ref()
        assert ref.extractor.config_fingerprint == "6f1c2a9d0b3e4517"
        with pytest.raises(ValidationError):
            StructuralSourceRef(source_id="x", raw_record_id="not-hex",
                                payload_checksum=CHECKSUM, extractor=EXTRACTOR)
        with pytest.raises(ValidationError):
            StructuralSourceRef(source_id="x", raw_record_id=RAW_ID,
                                payload_checksum="md5:00", extractor=EXTRACTOR)

    def test_row_and_cell_locators_reject_negative_indices(self):
        with pytest.raises(ValidationError):
            CsvRowLocator(kind="csv_row", physical_row_index=-1)
        with pytest.raises(ValidationError):
            CsvCellLocator(kind="csv_cell", physical_row_index=0,
                           column_index=-1, column_name_as_extracted="q")

    def test_parent_definition_path_rejects_empty_string(self):
        """K3: None, empty, and present are distinct states; the empty
        string is REJECTED so None and "" can never share a canonical
        value."""
        with pytest.raises(ValidationError):
            StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1:1:3:1",
                             upstream_instance_id="aa" * 16,
                             definition_path_id="0:1:1:4",
                             parent_definition_path_id="")

    def test_none_parent_is_the_synthesized_root_state(self):
        root = StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1:1",
                                upstream_instance_id="aa" * 16,
                                definition_path_id="0:1:1",
                                parent_definition_path_id=None)
        assert root.parent_definition_path_id is None

    def test_locators_are_frozen_and_forbid_extras(self):
        row = CsvRowLocator(kind="csv_row", physical_row_index=2)
        with pytest.raises(ValidationError):
            row.physical_row_index = 3
        with pytest.raises(ValidationError):
            CsvRowLocator(kind="csv_row", physical_row_index=2, name="bolt")

    def test_address_pairs_source_and_locator(self):
        address = StructuralAddress(
            source=source_ref(),
            locator=CsvRowLocator(kind="csv_row", physical_row_index=2))
        assert address.locator.kind == "csv_row"


class TestL2CanonicalValueInjectivity:
    def test_csv_schemes_have_explicit_prefixes(self):
        assert canonical_locator_value(
            CsvRowLocator(kind="csv_row", physical_row_index=3)) == "r=3"
        assert canonical_locator_value(
            CsvCellLocator(kind="csv_cell", physical_row_index=3,
                           column_index=2,
                           column_name_as_extracted="quantity")) == "r=3;c=2"

    def test_step_definition_scheme(self):
        value = canonical_locator_value(StepDefinitionLocator(
            kind="step_part_definition", extractor_path_id="0:1:1:5",
            upstream_definition_id="b0" * 16))
        assert value == "p=0%3A1%3A1%3A5;d=" + "b0" * 16

    def test_none_parent_encodes_as_empty_tail_not_a_sentinel(self):
        """quote("-", safe="") == "-", so "-" IS a valid quoted path and
        cannot be the None sentinel. None encodes as the empty tail; a
        REAL single-hyphen parent path stays distinct."""
        common = dict(kind="step_nauo_usage", upstream_instance_id="aa" * 16,
                      extractor_path_id="0:1:1:3:1", definition_path_id="0:1:1:4")
        root = canonical_locator_value(
            StepUsageLocator(**common, parent_definition_path_id=None))
        hyphen = canonical_locator_value(
            StepUsageLocator(**common, parent_definition_path_id="-"))
        assert root.endswith(";pp=")
        assert hyphen.endswith(";pp=-")
        assert root != hyphen

    def test_adversarial_paths_cannot_forge_field_boundaries(self):
        """Separators ; and = inside a path percent-encode, so a crafted
        path can never masquerade as another field."""
        crafted = canonical_locator_value(StepDefinitionLocator(
            kind="step_part_definition",
            extractor_path_id="0:1;d=deadbeef", upstream_definition_id="b0" * 16))
        assert crafted == "p=0%3A1%3Bd%3Ddeadbeef;d=" + "b0" * 16
        assert crafted.count(";d=") == 1

    def test_no_scheme_admits_a_bare_32_hex_string(self):
        """K7: a bare hex id (the raw-record/upstream-id shape) satisfies
        no scheme — every canonical value starts r= or p=."""
        for locator in (
            CsvRowLocator(kind="csv_row", physical_row_index=0),
            CsvCellLocator(kind="csv_cell", physical_row_index=0,
                           column_index=0, column_name_as_extracted="a"),
            StepDefinitionLocator(kind="step_part_definition",
                                  extractor_path_id="0:1",
                                  upstream_definition_id="aa" * 16),
            StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1",
                             upstream_instance_id="aa" * 16,
                             definition_path_id="0:1",
                             parent_definition_path_id=None),
        ):
            value = canonical_locator_value(locator)
            assert value.startswith(("r=", "p="))
            assert value != "aa" * 16

    def test_distinct_locators_distinct_values(self):
        """Pairwise injectivity across a representative value set."""
        values = [canonical_locator_value(loc) for loc in (
            CsvRowLocator(kind="csv_row", physical_row_index=1),
            CsvRowLocator(kind="csv_row", physical_row_index=12),
            CsvCellLocator(kind="csv_cell", physical_row_index=1,
                           column_index=2, column_name_as_extracted="a"),
            CsvCellLocator(kind="csv_cell", physical_row_index=12,
                           column_index=2, column_name_as_extracted="a"),
            StepDefinitionLocator(kind="step_part_definition",
                                  extractor_path_id="0:1:1",
                                  upstream_definition_id="aa" * 16),
            StepDefinitionLocator(kind="step_part_definition",
                                  extractor_path_id="0:1:12",
                                  upstream_definition_id="aa" * 16),
            StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1:1",
                             upstream_instance_id="aa" * 16,
                             definition_path_id="0:1:2",
                             parent_definition_path_id=None),
            StepUsageLocator(kind="step_nauo_usage", extractor_path_id="0:1:1",
                             upstream_instance_id="aa" * 16,
                             definition_path_id="0:1:2",
                             parent_definition_path_id="0:1"),
        )]
        assert len(set(values)) == len(values)

    def test_display_name_never_enters_the_canonical_value(self):
        a = CsvCellLocator(kind="csv_cell", physical_row_index=1,
                           column_index=2, column_name_as_extracted="quantity")
        b = CsvCellLocator(kind="csv_cell", physical_row_index=1,
                           column_index=2, column_name_as_extracted="Qty (renamed)")
        assert canonical_locator_value(a) == canonical_locator_value(b)


class TestL3LengthBounds:
    def test_path_fields_carry_the_1024_early_guard(self):
        with pytest.raises(ValidationError):
            StepDefinitionLocator(kind="step_part_definition",
                                  extractor_path_id="0" * 1025,
                                  upstream_definition_id="aa" * 16)

    def test_legal_length_path_with_overrunning_canonical_value_is_typed(self):
        """A 400-char all-colon path is contract-legal (<= 1024) but its
        quoted form is 1200 chars — the canonical value must fail with the
        TYPED error, never a raw pydantic error downstream."""
        locator = StepDefinitionLocator(
            kind="step_part_definition", extractor_path_id=":" * 400,
            upstream_definition_id="aa" * 16)
        with pytest.raises(StructuralEvidenceError) as err:
            canonical_locator_value(locator)
        assert err.value.error_code == "SN_LOCATOR_TOO_LONG"

    def test_canonical_values_at_the_bound_are_accepted(self):
        # 155 raw colons quote to 465 chars; +45-char fixed overhead
        # for the definition scheme stays exactly at the 510 cap.
        locator = StepDefinitionLocator(
            kind="step_part_definition", extractor_path_id=":" * 155,
            upstream_definition_id="aa" * 16)
        value = canonical_locator_value(locator)
        assert len(value) <= 510
