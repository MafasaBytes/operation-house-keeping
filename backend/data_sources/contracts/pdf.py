"""PDF extraction contracts (DS-003).

Honesty rules enforced here:

- every positioned item carries a canonical locator plus preserved
  source-native coordinates; nothing hides the coordinate transformation;
- classifications and inferred orderings declare their method, basis, and
  confidence — inferred reading order can never claim to be source truth;
- table structure is a candidate with declared strategy and declared
  cell↔span linking heuristic; unknown row/column spans stay None;
- document metadata is source-declared (``declared_*``), not authoritative;
- ``eof_marker_count`` is a byte-scan heuristic, not an edit-history claim;
- document-level ``levels_achieved`` must be a conservative aggregation of
  the per-page outcomes.
"""

from typing import Literal

from pydantic import Field, model_validator

from backend.data_sources.contracts.cad import (
    EntityId,
    PageRenderDerivativeRecord,
)
from backend.data_sources.contracts.identity import ExtractorIdentity
from backend.data_sources.contracts.models import RecordId, _FrozenModel


class PdfCoordinateFrame(_FrozenModel):
    canonical_basis: Literal["cropbox", "mediabox_fallback"]
    canonical_width: float = Field(gt=0)
    canonical_height: float = Field(gt=0)
    source_box: str
    source_to_canonical_matrix: list[float] = Field(min_length=6, max_length=6)
    rotation_degrees: Literal[0, 90, 180, 270]
    rotation_normalized: bool
    origin: Literal["top_left"]
    y_axis: Literal["downward"]
    units: Literal["pdf_points"]
    rounding_decimals: int = Field(ge=0, le=6)


class PageRegionLocator(_FrozenModel):
    page_index: int = Field(ge=0)
    page_label: str | None
    bbox: list[float] = Field(min_length=4, max_length=4)
    source_bbox: list[float] | None = Field(default=None, min_length=4, max_length=4)
    source_coordinate_system: str
    method: str
    confidence: float | None = Field(default=None, ge=0, le=1)


class PdfEncryption(_FrozenModel):
    present: bool
    method: str | None
    authentication_outcome: Literal[
        "not_required", "empty_password_ok", "password_required"
    ]


class PdfDocumentMetadata(_FrozenModel):
    """Source-declared metadata — recorded, never treated as authoritative."""

    declared_title: str | None
    declared_author: str | None
    declared_subject: str | None
    declared_producer: str | None
    declared_creator: str | None
    declared_creation_date_raw: str | None
    declared_mod_date_raw: str | None
    pdf_version: str | None
    page_label_spec_present: bool
    eof_marker_count: int = Field(ge=0)  # byte-scan heuristic only
    encryption: PdfEncryption


PageKind = Literal["born_digital_text", "image_only", "mixed", "empty"]


class PdfPage(_FrozenModel):
    page_index: int = Field(ge=0)
    page_label: str | None
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    rotation_degrees: Literal[0, 90, 180, 270]
    coordinate_frame: PdfCoordinateFrame
    boxes: dict[str, list[float]] = Field(default_factory=dict)
    page_kind: PageKind  # derived classification, not source structure
    page_kind_method: str
    page_kind_confidence: float = Field(ge=0, le=1)
    char_count: int = Field(ge=0)
    image_count: int = Field(ge=0)
    vector_path_count: int = Field(ge=0)
    annotation_count: int = Field(ge=0)
    warnings: list[str] = Field(default_factory=list)


class PdfTextSpan(_FrozenModel):
    span_id: EntityId  # extractor-derived identifier, never source-native
    locator: PageRegionLocator
    text: str
    extraction_order_index: int = Field(ge=0)  # order of extraction, no more
    font_name: str | None
    font_size: float | None
    upright: bool


ReadingOrderBasis = Literal[
    "source_object_order", "geometric_top_left", "extractor_inferred"
]


class PdfTextBlock(_FrozenModel):
    block_id: EntityId
    locator: PageRegionLocator
    span_ids: list[EntityId]
    reading_order_index: int = Field(ge=0)
    reading_order_basis: ReadingOrderBasis
    reading_order_method: str
    reading_order_confidence: float | None = Field(default=None, ge=0, le=1)

    @model_validator(mode="after")
    def _inferred_needs_method_and_confidence(self) -> "PdfTextBlock":
        if self.reading_order_basis == "extractor_inferred" and (
            not self.reading_order_method.strip()
            or self.reading_order_confidence is None
        ):
            raise ValueError(
                "extractor_inferred reading order must declare its method "
                "and confidence; it is never source-native truth"
            )
        return self


class PdfImage(_FrozenModel):
    image_id: EntityId
    locator: PageRegionLocator
    pixel_width: int | None = Field(default=None, gt=0)
    pixel_height: int | None = Field(default=None, gt=0)
    colorspace: str | None
    filter_names: list[str] = Field(default_factory=list)
    embedded_data_extracted: Literal[False] = False  # placement only in DS-003


class PdfAnnotation(_FrozenModel):
    annotation_id: EntityId
    locator: PageRegionLocator
    subtype: str
    contents: str | None = Field(default=None, max_length=1000)
    uri_target: str | None = Field(default=None, max_length=500)  # never followed
    flags: list[str] = Field(default_factory=list)


class PdfVectorSummary(_FrozenModel):
    """Honest vector inventory; drawing-region candidates are unsupported
    in DS-003 (no deterministic algorithm with oracle tests)."""

    page_index: int = Field(ge=0)
    line_count: int = Field(ge=0)
    curve_count: int = Field(ge=0)
    rect_count: int = Field(ge=0)
    ink_bbox: list[float] | None = Field(default=None, min_length=4, max_length=4)


class PdfTableCell(_FrozenModel):
    locator: PageRegionLocator
    row_index: int = Field(ge=0)
    column_index: int = Field(ge=0)
    row_span: int | None = Field(default=None, ge=1)  # None = not established
    column_span: int | None = Field(default=None, ge=1)
    span_refs: list[EntityId] = Field(default_factory=list)
    text: str | None
    ambiguous: bool = False


class PdfTableCandidate(_FrozenModel):
    candidate_id: EntityId
    locator: PageRegionLocator
    method: str
    settings: dict[str, str] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0, le=1)
    warnings: list[str] = Field(default_factory=list)
    row_count: int = Field(ge=0)
    column_count: int = Field(ge=0)
    cells: list[PdfTableCell]
    cell_span_link_method: str  # spatial heuristic, declared
    cell_span_link_tolerance_points: float = Field(ge=0)


RenderStatus = Literal["rendered", "render_failed", "skipped_limit", "not_attempted"]


class PdfPageOutcome(_FrozenModel):
    page_index: int = Field(ge=0)
    levels_achieved: list[int]
    render_status: RenderStatus
    ocr_required: bool
    warnings: list[str] = Field(default_factory=list)
    derivative_ids: list[EntityId] = Field(default_factory=list)
    failure_reason: str | None = None


class PdfExtractionManifest(_FrozenModel):
    raw_record_id: RecordId
    extractor: ExtractorIdentity
    metadata: PdfDocumentMetadata
    pages: list[PdfPage]
    spans: list[PdfTextSpan] = Field(default_factory=list)
    blocks: list[PdfTextBlock] = Field(default_factory=list)
    images: list[PdfImage] = Field(default_factory=list)
    annotations: list[PdfAnnotation] = Field(default_factory=list)
    vector_summaries: list[PdfVectorSummary] = Field(default_factory=list)
    table_candidates: list[PdfTableCandidate] = Field(default_factory=list)
    page_outcomes: list[PdfPageOutcome]
    derivatives: list[PageRenderDerivativeRecord] = Field(default_factory=list)
    levels_supported: list[int]
    levels_achieved: list[int]
    unsupported_features: list[str] = Field(default_factory=list)
    lossy_conversions: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _levels_honest(self) -> "PdfExtractionManifest":
        extra = set(self.levels_achieved) - set(self.levels_supported)
        if extra:
            raise ValueError(
                f"levels_achieved {sorted(extra)} exceed levels_supported"
            )
        if self.page_outcomes:
            common = set.intersection(
                *(set(o.levels_achieved) for o in self.page_outcomes)
            )
            overclaim = set(self.levels_achieved) - common
            if overclaim:
                raise ValueError(
                    f"document levels_achieved must be a conservative "
                    f"aggregation of page outcomes; levels {sorted(overclaim)} "
                    "were not achieved on every page"
                )
        return self
