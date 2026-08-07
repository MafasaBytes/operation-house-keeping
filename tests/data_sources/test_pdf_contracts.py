"""Contract tests for the DS-003 PDF models and their honesty rules."""

import pytest
from pydantic import ValidationError

from backend.data_sources.contracts import (
    ExtractionResult,
    ExtractorIdentity,
    PageRegionLocator,
    PdfCoordinateFrame,
    PdfDocumentMetadata,
    PdfEncryption,
    PdfExtractionManifest,
    PdfManifestResult,
    PdfPage,
    PdfPageOutcome,
    PdfTableCandidate,
    PdfTableCell,
    PdfTextBlock,
    PdfTextSpan,
)

RID = "a" * 32

IDENTITY = ExtractorIdentity(
    name="pdf_extractor",
    version="1.0.0",
    toolchain="pdfplumber 0.11.10 / pypdf 6.15.0 / pypdfium2 5.12.1",
    config_fingerprint="ab" * 8,
)

FRAME = PdfCoordinateFrame(
    canonical_basis="cropbox",
    canonical_width=612.0,
    canonical_height=792.0,
    source_box="CropBox",
    source_to_canonical_matrix=[1.0, 0.0, 0.0, -1.0, 0.0, 792.0],
    rotation_degrees=0,
    rotation_normalized=True,
    origin="top_left",
    y_axis="downward",
    units="pdf_points",
    rounding_decimals=3,
)


def make_locator(**overrides) -> PageRegionLocator:
    base = dict(
        page_index=0,
        page_label="1",
        bbox=[72.0, 62.484, 176.028, 74.484],
        source_bbox=[72.0, 717.516, 176.028, 729.516],
        source_coordinate_system="pdfminer_bottom_left_y_up",
        method="pdfplumber.extract_words",
        confidence=None,
    )
    base.update(overrides)
    return PageRegionLocator(**base)


def make_page(**overrides) -> PdfPage:
    base = dict(
        page_index=0,
        page_label="1",
        width=612.0,
        height=792.0,
        rotation_degrees=0,
        coordinate_frame=FRAME,
        boxes={"MediaBox": [0.0, 0.0, 612.0, 792.0]},
        page_kind="born_digital_text",
        page_kind_method="char_count>=10 and image_coverage<0.5",
        page_kind_confidence=0.9,
        char_count=42,
        image_count=0,
        vector_path_count=1,
        annotation_count=0,
        warnings=[],
    )
    base.update(overrides)
    return PdfPage(**base)


def make_span(order: int = 0, **overrides) -> PdfTextSpan:
    base = dict(
        span_id="b" * 32,
        locator=make_locator(),
        text="TORQUE",
        extraction_order_index=order,
        font_name="Helvetica",
        font_size=12.0,
        upright=True,
    )
    base.update(overrides)
    return PdfTextSpan(**base)


def make_outcome(**overrides) -> PdfPageOutcome:
    base = dict(
        page_index=0,
        levels_achieved=[0, 1, 2, 3],
        render_status="rendered",
        ocr_required=False,
        warnings=[],
        derivative_ids=[],
        failure_reason=None,
    )
    base.update(overrides)
    return PdfPageOutcome(**base)


def make_manifest(**overrides) -> PdfExtractionManifest:
    base = dict(
        raw_record_id=RID,
        extractor=IDENTITY,
        metadata=PdfDocumentMetadata(
            declared_title="Manual",
            declared_author=None,
            declared_subject=None,
            declared_producer="generator",
            declared_creator=None,
            declared_creation_date_raw=None,
            declared_mod_date_raw=None,
            pdf_version="1.4",
            page_label_spec_present=True,
            eof_marker_count=1,
            encryption=PdfEncryption(
                present=False, method=None, authentication_outcome="not_required"
            ),
        ),
        pages=[make_page()],
        spans=[make_span()],
        blocks=[],
        images=[],
        annotations=[],
        vector_summaries=[],
        table_candidates=[],
        page_outcomes=[make_outcome()],
        derivatives=[],
        levels_supported=[0, 1, 2, 3],
        levels_achieved=[0, 1, 2, 3],
        unsupported_features=[],
        lossy_conversions=[],
        warnings=[],
    )
    base.update(overrides)
    return PdfExtractionManifest(**base)


class TestCoordinateFrame:
    def test_literals_enforced(self):
        with pytest.raises(ValidationError):
            PdfCoordinateFrame(
                canonical_basis="cropbox", canonical_width=612, canonical_height=792,
                source_box="CropBox",
                source_to_canonical_matrix=[1, 0, 0, -1, 0, 792],
                rotation_degrees=45,  # only 0/90/180/270
                rotation_normalized=True, origin="top_left", y_axis="downward",
                units="pdf_points", rounding_decimals=3,
            )

    def test_matrix_is_affine_six(self):
        with pytest.raises(ValidationError):
            PdfCoordinateFrame(
                canonical_basis="cropbox", canonical_width=612, canonical_height=792,
                source_box="CropBox", source_to_canonical_matrix=[1, 0, 0, 1],
                rotation_degrees=0, rotation_normalized=True, origin="top_left",
                y_axis="downward", units="pdf_points", rounding_decimals=3,
            )


class TestLocator:
    def test_source_coordinates_preserved(self):
        locator = make_locator()
        assert locator.source_bbox is not None
        assert locator.source_coordinate_system == "pdfminer_bottom_left_y_up"

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            make_locator(confidence=1.5)


class TestReadingOrderHonesty:
    def test_inferred_basis_requires_method_and_confidence(self):
        with pytest.raises(ValidationError):
            PdfTextBlock(
                block_id="c" * 32,
                locator=make_locator(),
                span_ids=["b" * 32],
                reading_order_index=0,
                reading_order_basis="extractor_inferred",
                reading_order_method="",
                reading_order_confidence=None,
            )
        ok = PdfTextBlock(
            block_id="c" * 32,
            locator=make_locator(),
            span_ids=["b" * 32],
            reading_order_index=0,
            reading_order_basis="extractor_inferred",
            reading_order_method="pdfminer_laparams(line_margin=0.5)",
            reading_order_confidence=0.7,
        )
        assert ok.reading_order_basis == "extractor_inferred"

    def test_source_native_basis_is_not_available_for_inferred_order(self):
        with pytest.raises(ValidationError):
            PdfTextBlock(
                block_id="c" * 32, locator=make_locator(), span_ids=[],
                reading_order_index=0,
                reading_order_basis="source_native_truth",  # not a literal
                reading_order_method="x", reading_order_confidence=0.5,
            )


class TestTableHonesty:
    def test_cell_spans_optional_and_link_method_required(self):
        cell = PdfTableCell(
            locator=make_locator(method="pdfplumber.table_cells"),
            row_index=0, column_index=0,
            row_span=None, column_span=None,  # not established -> stays None
            span_refs=["b" * 32], text="TORQUE", ambiguous=False,
        )
        candidate = PdfTableCandidate(
            candidate_id="d" * 32,
            locator=make_locator(method="pdfplumber.find_tables"),
            method="pdfplumber.find_tables(strategy=lines)",
            settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"},
            confidence=0.8,
            warnings=[],
            row_count=1, column_count=1, cells=[cell],
            cell_span_link_method="span_bbox_center_within_cell_bbox",
            cell_span_link_tolerance_points=2.0,
        )
        assert candidate.cells[0].row_span is None


class TestPageOutcomeAggregation:
    def test_document_level_must_be_conservative(self):
        # page 1 reached L3, page 0 did not -> document may not claim L3
        with pytest.raises(ValidationError) as excinfo:
            make_manifest(
                pages=[make_page(), make_page(page_index=1)],
                page_outcomes=[
                    make_outcome(levels_achieved=[0, 1, 2], render_status="render_failed",
                                 failure_reason="pdfium error"),
                    make_outcome(page_index=1),
                ],
                levels_achieved=[0, 1, 2, 3],
            )
        assert "conservative" in str(excinfo.value)

    def test_conservative_aggregation_accepts_intersection(self):
        manifest = make_manifest(
            pages=[make_page(), make_page(page_index=1)],
            page_outcomes=[
                make_outcome(levels_achieved=[0, 1, 2], render_status="skipped_limit",
                             failure_reason="aggregate render pixel limit"),
                make_outcome(page_index=1),
            ],
            levels_achieved=[0, 1, 2],
        )
        assert manifest.levels_achieved == [0, 1, 2]

    def test_ocr_required_page(self):
        outcome = make_outcome(
            levels_achieved=[0, 1], render_status="rendered",
            ocr_required=True, warnings=["ocr_required: page has no text objects"],
        )
        assert outcome.ocr_required is True


class TestManifestResultUnion:
    def test_pdf_manifest_result_round_trips_and_views(self):
        result = ExtractionResult(
            raw_record_id=RID,
            extractor=IDENTITY,
            outcome="succeeded",
            warnings=[],
            result=PdfManifestResult(manifest=make_manifest()),
        )
        restored = ExtractionResult.model_validate_json(result.model_dump_json())
        assert restored == result
        assert restored.result.kind == "pdf_manifest"
        assert restored.manifest_view().raw_record_id == RID
