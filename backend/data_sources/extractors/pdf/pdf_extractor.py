"""Parent-side PDF extraction orchestration (two-phase).

Never imports the PDF toolchain. Invokes the worker for Phase A
(structural), validates the atomic completion checkpoint, decides the
render plan against the configured limits, invokes Phase B (rendering),
and assembles the contract manifest with page-level outcomes and a single
final extraction envelope.
"""

import hashlib
import json
import platform
import sys
from dataclasses import dataclass, field
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from backend.data_sources.contracts import (
    ExtractionError,
    ExtractionResult,
    ExtractorIdentity,
    PageRegionLocator,
    PageRenderDerivativeRecord,
    PdfAnnotation,
    PdfCoordinateFrame,
    PdfDocumentMetadata,
    PdfExtractionManifest,
    PdfImage,
    PdfManifestResult,
    PdfPage,
    PdfPageOutcome,
    PdfTableCandidate,
    PdfTableCell,
    PdfTextBlock,
    PdfTextSpan,
    PdfVectorSummary,
)
from backend.data_sources.extractors.pdf.phase_a_schema import PhaseAResult
from backend.data_sources.extractors.pdf.coordinates import (
    canonical_page_size,
    forward_matrix,
    inverse_matrix,
    transform_bbox,
)
from backend.data_sources.extractors.worker_harness import (
    WorkerLimits,
    invoke_worker,
)
from backend.data_sources.provenance import (
    derive_entity_id,
    payload_checksum,
    safe_basename,
    sanitize_source_text,
    sanitize_uri,
)

PDF_EXTRACTOR_VERSION = "1.0.0"
LEVELS_SUPPORTED = [0, 1, 2, 3]
_REPO_ROOT = Path(__file__).resolve().parents[4]

SOURCE_COORDINATE_SYSTEM = "pdf_user_space_bottom_left_y_up"
PAGE_KIND_METHOD = (
    "char_count>0 and image_count==0 -> born_digital_text; "
    "char_count==0 and image_count>0 -> image_only; "
    "both -> mixed; neither -> empty"
)
BLOCK_METHOD = "geometric_line_grouping(top_tolerance=2.0)"
CELL_LINK_METHOD = "span_bbox_center_within_cell_bbox"
CELL_LINK_TOLERANCE = 2.0


class PdfExtractionConfig(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dpi: int = Field(default=150, gt=0)
    colorspace: str = "RGB"
    max_pages: int = Field(default=500, gt=0)
    max_chars: int = Field(default=5_000_000, gt=0)
    max_layout_objects: int = Field(default=500_000, gt=0)
    max_page_pixels: int = Field(default=40_000_000, gt=0)
    max_total_pixels: int = Field(default=250_000_000, gt=0)
    max_derivative_bytes: int = Field(default=256 * 1024 * 1024, gt=0)
    max_manifest_bytes: int = Field(default=64 * 1024 * 1024, gt=0)


@dataclass
class PdfExtractionProduct:
    result: ExtractionResult
    derivative_payloads: dict[str, bytes] = field(default_factory=dict)


def pdf_extractor_identity(
    config: PdfExtractionConfig, toolchain_versions: dict[str, str]
) -> ExtractorIdentity:
    fingerprint = hashlib.sha256(config.model_dump_json().encode()).hexdigest()[:16]
    toolchain = " / ".join(
        f"{name} {version}" for name, version in sorted(toolchain_versions.items())
    ) or "pdf toolchain"
    return ExtractorIdentity(
        name="pdf_extractor",
        version=PDF_EXTRACTOR_VERSION,
        toolchain=toolchain,
        config_fingerprint=fingerprint,
    )


def extract_pdf(
    payload: bytes,
    raw_record_id: str,
    config: PdfExtractionConfig,
    limits: WorkerLimits,
    scratch_root: Path | None = None,
) -> PdfExtractionProduct:
    expected_identity = pdf_extractor_identity(config, {})
    context = {
        "raw_record_id": raw_record_id,
        "extractor": expected_identity.model_dump(),
    }
    outcome_a = _invoke(payload, config, limits, scratch_root, "a", context)
    _raise_on_worker_failure(outcome_a, phase="A")
    status = _read_json(outcome_a.outputs, "phase_a_status.json", "Phase A status")
    if status["status"] != "ok":
        raise ExtractionError(_CODE_BY_STATUS[status["status"]], status["error"])

    manifest_bytes = outcome_a.outputs.get("manifest_a.json")
    checkpoint_bytes = outcome_a.outputs.get("checkpoint.json")
    _validate_checkpoint(checkpoint_bytes, manifest_bytes, raw_record_id, expected_identity)
    worker_a = _validate_phase_a(manifest_bytes, raw_record_id, expected_identity)

    identity = pdf_extractor_identity(config, worker_a.get("toolchain", {}))

    # ---- render plan (per-page + aggregate pixel prechecks) -------------
    render_plan: list[int] = []
    precheck_status: dict[int, tuple[str, str | None]] = {}
    total_pixels = 0
    for page in worker_a["pages"]:
        display_w, display_h = canonical_page_size(
            page["rotation_raw"], tuple(page["cropbox_raw"])
        )
        pixels = int(display_w * config.dpi / 72) * int(display_h * config.dpi / 72)
        if pixels > config.max_page_pixels:
            precheck_status[page["page_index"]] = (
                "skipped_limit",
                f"page render of ~{pixels} px exceeds the per-page limit",
            )
            continue
        if total_pixels + pixels > config.max_total_pixels:
            precheck_status[page["page_index"]] = (
                "skipped_limit",
                "aggregate render pixel limit for the document reached",
            )
            continue
        total_pixels += pixels
        render_plan.append(page["page_index"])

    render_pages: dict[int, dict] = {}
    render_versions: dict[str, str] = {}
    page_pngs: dict[int, bytes] = {}
    phase_b_failure: str | None = None
    if render_plan:
        plan = {
            "pages": render_plan,
            "password_empty": worker_a["metadata"]["encryption"][
                "authentication_outcome"
            ]
            == "empty_password_ok",
        }
        outcome_b = _invoke(payload, config, limits, scratch_root, "b", plan)
        if outcome_b.status != "ok":
            phase_b_failure = (
                f"phase B worker {outcome_b.status} "
                f"(returncode {outcome_b.returncode})"
            )
        else:
            render_results = _read_json(
                outcome_b.outputs, "render_results.json", "render results"
            )
            render_versions = render_results["component_versions"]
            for entry in render_results["pages"]:
                render_pages[entry["page_index"]] = entry
                png = outcome_b.outputs.get(f"page_{entry['page_index']}.png")
                if entry["status"] == "rendered" and png is not None:
                    page_pngs[entry["page_index"]] = png

    return _assemble(
        payload, raw_record_id, config, identity, worker_a,
        precheck_status, render_plan, render_pages, render_versions,
        page_pngs, phase_b_failure,
    )


_CODE_BY_STATUS = {
    "parse_failed": "EXTRACT_PDF_PARSE_FAILED",
    "password_required": "EXTRACT_PDF_PASSWORD_REQUIRED",
    "limit_exceeded": "EXTRACT_PDF_LIMIT_EXCEEDED",
    "unsupported_rotation": "EXTRACT_PDF_UNSUPPORTED_ROTATION",
}


def _invoke(payload, config, limits, scratch_root, phase, extra):
    def build_argv(input_path: Path, output_dir: Path) -> list[str]:
        return [
            sys.executable, "-m", "backend.data_sources.extractors.pdf.worker",
            phase, str(input_path), str(output_dir),
            config.model_dump_json(), json.dumps(extra),
        ]

    return invoke_worker(
        build_argv,
        payload=payload,
        expected_checksum=payload_checksum(payload),
        limits=limits,
        scratch_root=scratch_root,
        payload_filename="payload.pdf",
        extra_env={"PYTHONPATH": str(_REPO_ROOT)},
    )


def _raise_on_worker_failure(outcome, phase: str) -> None:
    if outcome.status == "timeout":
        raise ExtractionError(
            "EXTRACT_WORKER_TIMEOUT", f"PDF worker phase {phase} timed out"
        )
    if outcome.status == "crashed":
        raise ExtractionError(
            "EXTRACT_WORKER_CRASHED",
            f"PDF worker phase {phase} terminated abnormally (returncode "
            f"{outcome.returncode}); stderr tail: {outcome.stderr_tail[-200:]!r}",
        )


def _read_json(outputs: dict[str, bytes], name: str, description: str) -> dict:
    if name not in outputs:
        raise ExtractionError(
            "EXTRACT_WORKER_CRASHED", f"worker produced no {description}"
        )
    return json.loads(outputs[name])


def _validate_checkpoint(
    checkpoint_bytes, manifest_bytes, raw_record_id, expected_identity
) -> None:
    def fail(reason: str):
        raise ExtractionError(
            "EXTRACT_PDF_CHECKPOINT_INVALID",
            f"phase A completion checkpoint rejected: {reason}",
        )

    if checkpoint_bytes is None or manifest_bytes is None:
        fail("checkpoint or structural manifest missing")
    try:
        checkpoint = json.loads(checkpoint_bytes)
    except Exception:
        fail("checkpoint is not parseable JSON")
    if checkpoint.get("checkpoint_schema_version") != 1:
        fail("unknown checkpoint schema version")
    if checkpoint.get("state") != "phase_a_complete":
        fail(f"unexpected state {checkpoint.get('state')!r}")
    if checkpoint.get("raw_record_id") != raw_record_id:
        fail("raw_record_id mismatch")
    expected = expected_identity.model_dump()
    got = checkpoint.get("extractor", {})
    for key in ("name", "version", "config_fingerprint"):
        if got.get(key) != expected[key]:
            fail(f"extractor identity mismatch on {key!r}")
    digest = hashlib.sha256(manifest_bytes).hexdigest()
    if checkpoint.get("manifest_sha256") != digest:
        fail("structural manifest checksum mismatch")


def _validate_phase_a(
    manifest_bytes: bytes, raw_record_id: str, expected_identity: ExtractorIdentity
) -> dict:
    """Validate the structural manifest against the versioned Phase A
    contract. Every failure — malformed JSON, structurally invalid or
    unknown-version content, identity/record mismatches — maps to
    EXTRACT_PDF_CHECKPOINT_INVALID, never an unhandled exception."""
    from pydantic import ValidationError

    def fail(reason: str):
        raise ExtractionError(
            "EXTRACT_PDF_CHECKPOINT_INVALID",
            f"phase A structural manifest rejected: {reason}",
        )

    try:
        phase_a = PhaseAResult.model_validate_json(manifest_bytes)
    except ValidationError as error:
        first = error.errors()[0]
        location = ".".join(str(part) for part in first.get("loc", ())) or "<root>"
        fail(f"schema violation at {location} ({first.get('type', 'invalid')})")
    except Exception:
        fail("manifest is not parseable JSON")

    if phase_a.raw_record_id != raw_record_id:
        fail("raw_record_id mismatch between manifest and expectation")
    expected = expected_identity.model_dump()
    if (
        phase_a.extractor_name != expected["name"]
        or phase_a.extractor_version != expected["version"]
        or phase_a.config_fingerprint != expected["config_fingerprint"]
    ):
        fail("extractor identity or configuration fingerprint mismatch")
    return phase_a.model_dump()


def _assemble(
    payload, raw_record_id, config, identity, worker_a,
    precheck_status, render_plan, render_pages, render_versions,
    page_pngs, phase_b_failure,
) -> PdfExtractionProduct:
    def eid(kind: str, *parts) -> str:
        path = ":".join(str(p) for p in parts)
        return derive_entity_id(raw_record_id, PDF_EXTRACTOR_VERSION, f"{kind}:{path}")

    environment = {
        "platform": platform.system().lower(),
        "architecture": platform.machine(),
        "component_versions": dict(sorted(render_versions.items())),
    }

    pages: list[PdfPage] = []
    spans: list[PdfTextSpan] = []
    blocks: list[PdfTextBlock] = []
    images: list[PdfImage] = []
    annotations: list[PdfAnnotation] = []
    vector_summaries: list[PdfVectorSummary] = []
    tables: list[PdfTableCandidate] = []
    outcomes: list[PdfPageOutcome] = []
    derivatives: list[PageRenderDerivativeRecord] = []
    derivative_payloads: dict[str, bytes] = {}
    document_warnings: list[str] = []

    for page in worker_a["pages"]:
        index = page["page_index"]
        rotation = page["rotation_raw"]
        media_box = tuple(page["mediabox_raw"])
        crop_box = tuple(page["cropbox_raw"])
        crop_declared = page["crop_declared"]
        canonical_box = crop_box  # pypdf's cropbox falls back to mediabox
        canonical_w, canonical_h = canonical_page_size(rotation, canonical_box)
        # pdfplumber's displayed coordinates use the rotated-MediaBox frame;
        # invert that to recover raw user space, then map forward into the
        # canonical (CropBox-relative, displayed, top-left) frame.
        to_canonical = forward_matrix(rotation, canonical_box)
        displayed_to_raw = inverse_matrix(rotation, media_box)
        frame = PdfCoordinateFrame(
            canonical_basis="cropbox" if crop_declared else "mediabox_fallback",
            canonical_width=canonical_w,
            canonical_height=canonical_h,
            source_box="CropBox" if crop_declared else "MediaBox",
            source_to_canonical_matrix=to_canonical,
            rotation_degrees=rotation,
            rotation_normalized=True,
            origin="top_left",
            y_axis="downward",
            units="pdf_points",
            rounding_decimals=3,
        )

        def locator(bbox, method, source_bbox=None, confidence=None,
                    label=page["page_label"], _to_canonical=to_canonical,
                    _displayed_to_raw=displayed_to_raw, _index=index):
            """Build a locator. ``bbox`` is a pdfplumber displayed bbox
            unless ``source_bbox`` (raw user space) is given, in which case
            the canonical bbox is derived from it via the forward
            transform."""
            if source_bbox is None:
                source_bbox = transform_bbox(_displayed_to_raw, list(bbox))
            canonical = transform_bbox(_to_canonical, list(source_bbox))
            return PageRegionLocator(
                page_index=_index, page_label=label,
                bbox=[round(v, 3) for v in canonical],
                source_bbox=[round(v, 3) for v in source_bbox],
                source_coordinate_system=SOURCE_COORDINATE_SYSTEM,
                method=method, confidence=confidence,
            )

        char_count = page["char_count"]
        image_count = len(page["images"])
        if char_count > 0 and image_count == 0:
            kind = "born_digital_text"
        elif char_count == 0 and image_count > 0:
            kind = "image_only"
        elif char_count > 0:
            kind = "mixed"
        else:
            kind = "empty"

        page_warnings: list[str] = []
        ocr_required = kind == "image_only"
        if ocr_required:
            page_warnings.append(
                "ocr_required: page has no text objects; content exists only "
                "as raster pixels and was not fabricated"
            )

        page_spans: list[PdfTextSpan] = []
        for order, word in enumerate(page["words"]):
            span = PdfTextSpan(
                span_id=eid("span", index, order),
                locator=locator(
                    [word["x0"], word["top"], word["x1"], word["bottom"]],
                    method="pdfplumber.extract_words",
                ),
                text=word["text"],
                extraction_order_index=order,
                font_name=word["fontname"],
                font_size=word["size"],
                upright=word["upright"],
            )
            page_spans.append(span)
        spans.extend(page_spans)

        # geometric line grouping into blocks (top tolerance 2 pt)
        by_line: list[list[PdfTextSpan]] = []
        for span in sorted(page_spans, key=lambda s: (s.locator.bbox[1], s.locator.bbox[0])):
            if by_line and abs(by_line[-1][0].locator.bbox[1] - span.locator.bbox[1]) <= 2.0:
                by_line[-1].append(span)
            else:
                by_line.append([span])
        for order, line in enumerate(by_line):
            bbox = [
                min(s.locator.bbox[0] for s in line),
                min(s.locator.bbox[1] for s in line),
                max(s.locator.bbox[2] for s in line),
                max(s.locator.bbox[3] for s in line),
            ]
            blocks.append(
                PdfTextBlock(
                    block_id=eid("block", index, order),
                    locator=locator(bbox, method=BLOCK_METHOD),
                    span_ids=[s.span_id for s in line],
                    reading_order_index=order,
                    reading_order_basis="geometric_top_left",
                    reading_order_method=BLOCK_METHOD,
                    reading_order_calibration="uncalibrated_heuristic",
                    reading_order_confidence=None,
                )
            )

        for i_index, image in enumerate(page["images"]):
            images.append(
                PdfImage(
                    image_id=eid("image", index, i_index),
                    locator=locator(
                        [image["x0"], image["top"], image["x1"], image["bottom"]],
                        method="pdfplumber.page.images",
                    ),
                    pixel_width=image["srcwidth"],
                    pixel_height=image["srcheight"],
                    colorspace=image["colorspace"],
                    filter_names=image["filters"],
                )
            )

        for a_index, annotation in enumerate(page["annotations"]):
            rect = annotation["rect"]  # raw user-space /Rect from pypdf
            annotations.append(
                PdfAnnotation(
                    annotation_id=eid("annot", index, a_index),
                    locator=locator(
                        None, method="pypdf.page.annotations",
                        source_bbox=rect,
                    ),
                    subtype=annotation["subtype"],
                    contents=sanitize_source_text(annotation["contents"]),
                    uri_target=(
                        sanitize_uri(annotation["uri"]) if annotation["uri"] else None
                    ),
                )
            )

        if page["lines_n"] or page["rects_n"] or page["curves_n"]:
            vector_summaries.append(
                PdfVectorSummary(
                    page_index=index,
                    line_count=page["lines_n"],
                    curve_count=page["curves_n"],
                    rect_count=page["rects_n"],
                    ink_bbox=(
                        [round(v, 3) for v in transform_bbox(
                            to_canonical,
                            transform_bbox(displayed_to_raw, page["ink_bbox"]),
                        )]
                        if page["ink_bbox"] else None
                    ),
                )
            )

        for t_index, table in enumerate(page["tables"]):
            cells = []
            for cell in table["cells"]:
                cx0, ctop, cx1, cbottom = cell["bbox"]
                linked = [
                    s for s in page_spans
                    if cx0 - CELL_LINK_TOLERANCE
                    <= (s.locator.bbox[0] + s.locator.bbox[2]) / 2
                    <= cx1 + CELL_LINK_TOLERANCE
                    and ctop - CELL_LINK_TOLERANCE
                    <= (s.locator.bbox[1] + s.locator.bbox[3]) / 2
                    <= cbottom + CELL_LINK_TOLERANCE
                ]
                cells.append(
                    PdfTableCell(
                        locator=locator(cell["bbox"], method="pdfplumber.table.cells"),
                        row_index=cell["row"],
                        column_index=cell["col"],
                        span_refs=[s.span_id for s in linked],
                        text=" ".join(s.text for s in linked) or None,
                        ambiguous=False,
                    )
                )
            tables.append(
                PdfTableCandidate(
                    candidate_id=eid("table", index, t_index),
                    locator=locator(
                        table["bbox"], method="pdfplumber.find_tables",
                        confidence=0.7,
                    ),
                    method="pdfplumber.find_tables(default lines strategy)",
                    settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"},
                    confidence=0.7,
                    warnings=[],
                    row_count=table["rows_n"],
                    column_count=table["cols_n"],
                    cells=cells,
                    cell_span_link_method=CELL_LINK_METHOD,
                    cell_span_link_tolerance_points=CELL_LINK_TOLERANCE,
                )
            )

        # ---- page outcome -----------------------------------------------
        levels = [0, 1, 2]
        render_status = "not_attempted"
        failure_reason = None
        derivative_ids: list[str] = []
        if index in precheck_status:
            render_status, failure_reason = precheck_status[index]
        elif phase_b_failure is not None and index in render_plan:
            render_status, failure_reason = "render_failed", phase_b_failure
        elif index in render_pages:
            entry = render_pages[index]
            render_status = entry["status"]
            failure_reason = entry["error"]
            if entry["status"] == "rendered" and index in page_pngs:
                png = page_pngs[index]
                reference = payload_checksum(png)
                derivative = PageRenderDerivativeRecord(
                    derivative_id=eid("render", index, reference),
                    raw_record_id=raw_record_id,
                    media_type="image/png",
                    payload_reference=reference,
                    checksum=reference,
                    generator=identity,
                    environment=environment,
                    page_index=index,
                    dpi=config.dpi,
                    colorspace=config.colorspace,
                    pixel_width=entry["pixel_width"],
                    pixel_height=entry["pixel_height"],
                )
                derivatives.append(derivative)
                derivative_payloads[reference] = png
                derivative_ids.append(derivative.derivative_id)
                levels = [0, 1, 2, 3]

        outcomes.append(
            PdfPageOutcome(
                page_index=index,
                levels_achieved=levels,
                render_status=render_status,
                ocr_required=ocr_required,
                warnings=page_warnings,
                derivative_ids=derivative_ids,
                failure_reason=failure_reason,
            )
        )

        pages.append(
            PdfPage(
                page_index=index,
                page_label=page["page_label"],
                width=round(canonical_w, 3),
                height=round(canonical_h, 3),
                rotation_degrees=rotation,
                coordinate_frame=frame,
                boxes={
                    # raw (unrotated user-space) box values, stored verbatim
                    "MediaBox": page["mediabox_raw"],
                    **({"CropBox": page["cropbox_raw"]} if crop_declared else {}),
                },
                page_kind=kind,
                page_kind_method=PAGE_KIND_METHOD,
                page_kind_confidence=0.9,
                char_count=char_count,
                image_count=image_count,
                vector_path_count=page["lines_n"] + page["rects_n"] + page["curves_n"],
                annotation_count=len(page["annotations"]),
                warnings=page_warnings,
            )
        )

    # ---- document-level aggregation ------------------------------------
    document_levels = sorted(
        set.intersection(*(set(o.levels_achieved) for o in outcomes))
    ) if outcomes else [0, 1]
    if any(3 not in o.levels_achieved for o in outcomes) and any(
        3 in o.levels_achieved for o in outcomes
    ):
        reached = sum(1 for o in outcomes if 3 in o.levels_achieved)
        document_warnings.append(
            f"level 3 achieved on {reached}/{len(outcomes)} pages"
        )
    if phase_b_failure:
        document_warnings.append(f"rendering incomplete: {phase_b_failure}")

    catalog = worker_a["catalog"]
    unsupported = ["drawing-region candidates unsupported in DS-003"]
    # Active-content inventory covers exactly: JavaScript name-tree
    # entries, URI link annotations, embedded-file declarations, and
    # OpenAction//AA *presence*. Other action types (Launch, GoToR,
    # SubmitForm, ...) are not inspected — see the module README.
    if catalog["javascript_count"]:
        unsupported.append(
            f"JavaScript name-tree entries present: "
            f"{catalog['javascript_count']} (declarations recorded, never "
            "executed)"
        )
    if catalog.get("open_action_present"):
        unsupported.append(
            "document OpenAction present (presence recorded, never executed "
            "or inspected in detail)"
        )
    if catalog.get("additional_actions_present"):
        unsupported.append(
            "additional-action (/AA) entries present (presence recorded, "
            "never executed or inspected in detail)"
        )
    if catalog["embedded_file_names"]:
        names = ", ".join(safe_basename(n) for n in catalog["embedded_file_names"])
        unsupported.append(
            f"embedded files present: {names} (names recorded as safe "
            "basenames, bytes not extracted)"
        )
    if catalog["ocg_names"]:
        ocg = ", ".join(
            sanitize_source_text(n, max_len=80) or "<unnamed>"
            for n in catalog["ocg_names"]
        )
        unsupported.append(f"optional content groups: names only ({ocg})")

    ocr_pages = [o.page_index for o in outcomes if o.ocr_required]
    if ocr_pages:
        document_warnings.append(
            f"ocr_required on page(s) {ocr_pages}; OCR (level 4) is deferred"
        )

    fully_rendered = all(o.render_status == "rendered" for o in outcomes)
    outcome_value = "succeeded" if fully_rendered and not ocr_pages else "partial"

    metadata_raw = dict(worker_a["metadata"])
    for key, value in metadata_raw.items():
        if key.startswith("declared_"):
            metadata_raw[key] = sanitize_source_text(value)
    manifest = PdfExtractionManifest(
        raw_record_id=raw_record_id,
        extractor=identity,
        metadata=PdfDocumentMetadata(
            **{**metadata_raw, "eof_marker_count": payload.count(b"%%EOF")}
        ),
        pages=pages,
        spans=spans,
        blocks=blocks,
        images=images,
        annotations=annotations,
        vector_summaries=vector_summaries,
        table_candidates=tables,
        page_outcomes=outcomes,
        derivatives=derivatives,
        levels_supported=LEVELS_SUPPORTED,
        levels_achieved=document_levels,
        unsupported_features=unsupported,
        lossy_conversions=[
            f"page renders rasterized at {config.dpi} dpi; vector fidelity reduced"
        ] if derivatives else [],
        warnings=document_warnings,
    )
    result = ExtractionResult(
        raw_record_id=raw_record_id,
        extractor=identity,
        outcome=outcome_value,
        warnings=document_warnings,
        result=PdfManifestResult(manifest=manifest),
    )
    return PdfExtractionProduct(result=result, derivative_payloads=derivative_payloads)
