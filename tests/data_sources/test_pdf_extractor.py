"""PDF extractor tests.

Golden tests (marker: pdf) run the real two-phase worker against the frozen
fixtures and compare with the hand-authored oracle in golden_pdf_fixtures.
Parent-logic tests (no marker) stub the worker harness.
"""

import hashlib
import json
from pathlib import Path

import pytest

from backend.data_sources.contracts import ExtractionError
from backend.data_sources.extractors.pdf import (
    PdfExtractionConfig,
    extract_pdf,
)
from backend.data_sources.extractors.worker_harness import WorkerLimits, WorkerOutcome
from backend.data_sources.provenance import payload_checksum

from tests.data_sources import golden_pdf_fixtures as golden

FIXTURES = Path("backend/data_sources/testing/fixtures")
RID = "a" * 32
LIMITS = WorkerLimits(timeout_seconds=120.0, max_payload_bytes=50_000_000)


def run_fixture(name: str, tmp_path, config: PdfExtractionConfig | None = None):
    payload = (FIXTURES / name).read_bytes()
    return extract_pdf(
        payload=payload,
        raw_record_id=RID,
        config=config or PdfExtractionConfig(),
        limits=LIMITS,
        scratch_root=tmp_path / "scratch",
    )


def find_word(manifest, page_index: int, text: str):
    for span in manifest.spans:
        if span.locator.page_index == page_index and span.text == text:
            return span
    raise AssertionError(f"word {text!r} not found on page {page_index}")


@pytest.mark.pdf
class TestGoldenManual:
    def test_structure_labels_and_designed_coordinates(self, tmp_path):
        product = run_fixture("manual_multipage.pdf", tmp_path)
        manifest = product.result.manifest_view()

        assert len(manifest.pages) == golden.MANUAL["page_count"]
        assert [p.page_label for p in manifest.pages] == golden.MANUAL["page_labels"]
        assert manifest.metadata.page_label_spec_present is True
        for page in manifest.pages:
            assert (page.width, page.height) == golden.MANUAL["page_size"]
            assert page.page_kind == golden.MANUAL["all_pages_kind"]

        for page_index, text, x0, approx_top in golden.MANUAL["words"]:
            span = find_word(manifest, page_index, text)
            assert span.locator.bbox[0] == pytest.approx(x0, abs=golden.TOLERANCE_PT)
            assert span.locator.bbox[1] == pytest.approx(
                approx_top, abs=golden.TOLERANCE_PT
            )
            # source coordinates preserved: y flips around page height
            assert span.locator.source_bbox is not None
            source_y0 = span.locator.source_bbox[1]
            assert source_y0 == pytest.approx(
                golden.MANUAL["page_size"][1] - span.locator.bbox[3], abs=0.01
            )

        # frame declarations
        frame = manifest.pages[0].coordinate_frame
        assert frame.origin == "top_left" and frame.y_axis == "downward"
        assert frame.units == "pdf_points" and frame.rounding_decimals == 3

    def test_provenance_chain_span_to_raw_checksum(self, tmp_path):
        payload = (FIXTURES / "manual_multipage.pdf").read_bytes()
        product = run_fixture("manual_multipage.pdf", tmp_path)
        result = product.result
        span = find_word(result.manifest_view(), 1, "TORQUE")
        # item -> method+version -> region -> page -> raw record id
        assert span.locator.method
        assert result.extractor.version
        assert 0 <= span.locator.bbox[0] < result.manifest_view().pages[1].width
        assert result.raw_record_id == RID  # runtime binds RID to the checksum
        assert payload_checksum(payload).startswith("sha256:")

    def test_succeeded_with_renders_and_conservative_levels(self, tmp_path):
        product = run_fixture("manual_multipage.pdf", tmp_path)
        result = product.result
        assert result.outcome == "succeeded"
        manifest = result.manifest_view()
        assert manifest.levels_achieved == [0, 1, 2, 3]
        assert len(manifest.derivatives) == 3
        for derivative in manifest.derivatives:
            png = product.derivative_payloads[derivative.payload_reference]
            assert png[:8] == b"\x89PNG\r\n\x1a\n"
            assert payload_checksum(png) == derivative.checksum
            assert derivative.dpi == 150 and derivative.colorspace == "RGB"
            assert derivative.environment.component_versions.get("pdfium")
        outcome_by_page = {o.page_index: o for o in manifest.page_outcomes}
        assert all(o.render_status == "rendered" for o in outcome_by_page.values())

    def test_determinism_double_run(self, tmp_path):
        first = run_fixture("manual_multipage.pdf", tmp_path)
        second = run_fixture("manual_multipage.pdf", tmp_path / "second")
        assert first.result.model_dump_json() == second.result.model_dump_json()
        assert first.derivative_payloads == second.derivative_payloads


@pytest.mark.pdf
class TestGoldenTable:
    def test_table_candidate_matches_designed_grid(self, tmp_path):
        manifest = run_fixture("table_page.pdf", tmp_path).result.manifest_view()
        [candidate] = manifest.table_candidates
        assert candidate.row_count == golden.TABLE["row_count"]
        assert candidate.column_count == golden.TABLE["column_count"]
        assert candidate.method.startswith("pdfplumber")
        assert candidate.cell_span_link_method
        x0, top, x1, bottom = golden.TABLE["bbox_canonical"]
        assert candidate.locator.bbox[0] == pytest.approx(x0, abs=golden.TOLERANCE_PT)
        assert candidate.locator.bbox[3] == pytest.approx(bottom, abs=golden.TOLERANCE_PT)

        cells = {(c.row_index, c.column_index): c for c in candidate.cells}
        span_by_id = {s.span_id: s for s in manifest.spans}
        for (row, col), expected_text in golden.TABLE["cells"].items():
            cell = cells[(row, col)]
            assert (cell.text or "").strip() == expected_text
            assert cell.row_span is None and cell.column_span is None
            assert cell.span_refs, f"cell {(row, col)} lost its span links"
            linked_text = " ".join(span_by_id[s].text for s in cell.span_refs)
            assert expected_text.split()[0] in linked_text


@pytest.mark.pdf
class TestGoldenOtherPages:
    def test_drawing_vector_inventory_and_callouts(self, tmp_path):
        manifest = run_fixture("drawing_callouts.pdf", tmp_path).result.manifest_view()
        [summary] = manifest.vector_summaries
        assert summary.rect_count == golden.DRAWING["rect_count"]
        assert summary.line_count == golden.DRAWING["line_count"]
        for text, x0 in golden.DRAWING["callouts"]:
            span = find_word(manifest, 0, text)
            assert span.locator.bbox[0] == pytest.approx(x0, abs=golden.TOLERANCE_PT)
        assert any("drawing-region" in u for u in manifest.unsupported_features)

    def test_scanned_only_is_partial_with_ocr_required(self, tmp_path):
        result = run_fixture("scanned_only.pdf", tmp_path).result
        assert result.outcome == "partial"
        manifest = result.manifest_view()
        page = manifest.pages[0]
        assert page.page_kind == "image_only"
        assert page.page_kind_method  # derived classification declares itself
        [outcome] = manifest.page_outcomes
        assert outcome.ocr_required is True
        assert manifest.spans == []  # no fabricated text
        [image] = manifest.images
        x0, top, x1, bottom = golden.SCANNED["image_bbox_canonical"]
        assert image.locator.bbox[0] == pytest.approx(x0, abs=golden.TOLERANCE_PT)
        assert image.locator.bbox[1] == pytest.approx(top, abs=golden.TOLERANCE_PT)

    def test_mixed_page_kind(self, tmp_path):
        manifest = run_fixture("mixed_text_image.pdf", tmp_path).result.manifest_view()
        assert manifest.pages[0].page_kind == "mixed"
        find_word(manifest, 0, golden.MIXED["first_word"][0])
        assert len(manifest.images) == golden.MIXED["image_count"]

    def test_rotated_page_normalized_frame(self, tmp_path):
        manifest = run_fixture("rotated_page.pdf", tmp_path).result.manifest_view()
        page = manifest.pages[0]
        assert page.rotation_degrees == golden.ROTATED["rotation_degrees"]
        assert (page.width, page.height) == golden.ROTATED["canonical_size"]
        assert page.coordinate_frame.rotation_normalized is True
        find_word(manifest, 0, golden.ROTATED["contains_word"])

    def test_active_content_inventoried_never_executed(self, tmp_path):
        manifest = run_fixture("active_content.pdf", tmp_path).result.manifest_view()
        joined = " ".join(manifest.unsupported_features)
        assert "javascript" in joined.lower()
        assert "embedded file" in joined.lower()
        uris = [a.uri_target for a in manifest.annotations if a.uri_target]
        assert uris == golden.ACTIVE_CONTENT["uri_targets"]

    def test_encrypted_quarantines(self, tmp_path):
        with pytest.raises(ExtractionError) as excinfo:
            run_fixture("encrypted.pdf", tmp_path)
        assert excinfo.value.error_code == golden.ENCRYPTED_ERROR_CODE

    def test_malformed_quarantines(self, tmp_path):
        with pytest.raises(ExtractionError) as excinfo:
            run_fixture("malformed.pdf", tmp_path)
        assert excinfo.value.error_code == golden.MALFORMED_ERROR_CODE


# --------------------------------------------------------------------------
# Parent logic with a stubbed harness (no PDF closure required)
# --------------------------------------------------------------------------

STUB_PDF = b"%PDF-1.4\nstub"


def stub_manifest_a() -> dict:
    from backend.data_sources.extractors.pdf.pdf_extractor import (
        pdf_extractor_identity,
    )
    identity = pdf_extractor_identity(PdfExtractionConfig(), {}).model_dump()
    return {
        "phase_a_schema_version": 1,
        "raw_record_id": RID,
        "extractor_name": identity["name"],
        "extractor_version": identity["version"],
        "config_fingerprint": identity["config_fingerprint"],
        "metadata": {
            "declared_title": None, "declared_author": None,
            "declared_subject": None, "declared_producer": None,
            "declared_creator": None, "declared_creation_date_raw": None,
            "declared_mod_date_raw": None, "pdf_version": "1.4",
            "page_label_spec_present": False,
            "encryption": {"present": False, "method": None,
                           "authentication_outcome": "not_required"},
        },
        "catalog": {"javascript_count": 0, "embedded_file_names": [],
                    "ocg_names": [], "open_action_present": False,
                    "additional_actions_present": False},
        "toolchain": {"pdfplumber": "0.11.10", "pdfminer.six": "20260107",
                      "pypdf": "6.15.0"},
        "pages": [{
            "page_index": 0, "page_label": None,
            "displayed_width": 612.0, "displayed_height": 792.0,
            "mediabox_raw": [0.0, 0.0, 612.0, 792.0],
            "cropbox_raw": [0.0, 0.0, 612.0, 792.0],
            "crop_declared": False, "rotation_raw": 0,
            "words": [{"text": "HELLO", "x0": 72.0, "top": 62.5, "x1": 110.0,
                        "bottom": 74.5, "fontname": "Helvetica", "size": 12.0,
                        "upright": True}],
            "lines_n": 0, "rects_n": 0, "curves_n": 0, "ink_bbox": None,
            "images": [], "annotations": [],
            "tables": [], "char_count": 5,
        }],
        "counts": {"total_chars": 5, "layout_objects": 1},
    }


def phase_a_outputs(manifest_a: dict, rid: str, identity: dict) -> dict[str, bytes]:
    manifest_bytes = json.dumps(manifest_a, sort_keys=True).encode()
    checkpoint = {
        "checkpoint_schema_version": 1,
        "raw_record_id": rid,
        "extractor": identity,
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "state": "phase_a_complete",
    }
    return {
        "phase_a_status.json": json.dumps({"status": "ok", "error": None}).encode(),
        "manifest_a.json": manifest_bytes,
        "checkpoint.json": json.dumps(checkpoint).encode(),
    }


class StubHarness:
    def __init__(self, outcomes: list[WorkerOutcome]):
        self.outcomes = list(outcomes)
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.outcomes.pop(0)


def ok_outcome(outputs: dict[str, bytes]) -> WorkerOutcome:
    return WorkerOutcome(status="ok", returncode=0, stdout_tail="",
                         stderr_tail="", outputs=outputs)


class TestParentPhaseLogic:
    def _identity_dict(self):
        from backend.data_sources.extractors.pdf.pdf_extractor import (
            pdf_extractor_identity,
        )
        return pdf_extractor_identity(
            PdfExtractionConfig(), {"pdfplumber": "0.11.10"}
        ).model_dump()

    def _patch(self, monkeypatch, harness):
        monkeypatch.setattr(
            "backend.data_sources.extractors.pdf.pdf_extractor.invoke_worker",
            harness,
        )

    def test_missing_checkpoint_quarantines(self, monkeypatch):
        outputs = phase_a_outputs(stub_manifest_a(), RID, self._identity_dict())
        del outputs["checkpoint.json"]
        self._patch(monkeypatch, StubHarness([ok_outcome(outputs)]))
        with pytest.raises(ExtractionError) as excinfo:
            extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                        config=PdfExtractionConfig(), limits=LIMITS)
        assert excinfo.value.error_code == "EXTRACT_PDF_CHECKPOINT_INVALID"

    def test_checkpoint_sha_mismatch_quarantines(self, monkeypatch):
        outputs = phase_a_outputs(stub_manifest_a(), RID, self._identity_dict())
        checkpoint = json.loads(outputs["checkpoint.json"])
        checkpoint["manifest_sha256"] = "0" * 64
        outputs["checkpoint.json"] = json.dumps(checkpoint).encode()
        self._patch(monkeypatch, StubHarness([ok_outcome(outputs)]))
        with pytest.raises(ExtractionError) as excinfo:
            extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                        config=PdfExtractionConfig(), limits=LIMITS)
        assert excinfo.value.error_code == "EXTRACT_PDF_CHECKPOINT_INVALID"

    def test_phase_a_crash_is_worker_crashed(self, monkeypatch):
        crash = WorkerOutcome(status="crashed", returncode=-11, stdout_tail="",
                              stderr_tail="boom", outputs={})
        self._patch(monkeypatch, StubHarness([crash]))
        with pytest.raises(ExtractionError) as excinfo:
            extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                        config=PdfExtractionConfig(), limits=LIMITS)
        assert excinfo.value.error_code == "EXTRACT_WORKER_CRASHED"

    def test_password_required_status_maps(self, monkeypatch):
        outputs = {"phase_a_status.json": json.dumps(
            {"status": "password_required", "error": "password required"}).encode()}
        self._patch(monkeypatch, StubHarness([ok_outcome(outputs)]))
        with pytest.raises(ExtractionError) as excinfo:
            extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                        config=PdfExtractionConfig(), limits=LIMITS)
        assert excinfo.value.error_code == "EXTRACT_PDF_PASSWORD_REQUIRED"

    def test_phase_b_crash_yields_partial_without_derivatives(self, monkeypatch):
        outputs = phase_a_outputs(stub_manifest_a(), RID, self._identity_dict())
        crash_b = WorkerOutcome(status="crashed", returncode=-9, stdout_tail="",
                                stderr_tail="render boom", outputs={})
        harness = StubHarness([ok_outcome(outputs), crash_b])
        self._patch(monkeypatch, harness)
        product = extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                              config=PdfExtractionConfig(), limits=LIMITS)
        assert harness.calls == 2
        result = product.result
        assert result.outcome == "partial"
        manifest = result.manifest_view()
        assert manifest.derivatives == []
        assert product.derivative_payloads == {}
        [outcome] = manifest.page_outcomes
        assert outcome.render_status == "render_failed"
        assert outcome.levels_achieved == [0, 1, 2]
        assert manifest.levels_achieved == [0, 1, 2]

    def test_oversized_page_precheck_skips_render(self, monkeypatch):
        manifest_a = stub_manifest_a()
        manifest_a["pages"][0]["mediabox_raw"] = [0.0, 0.0, 10000.0, 10000.0]
        manifest_a["pages"][0]["cropbox_raw"] = [0.0, 0.0, 10000.0, 10000.0]
        # 150 dpi -> ~434 MP > 40 MP per-page cap
        outputs = phase_a_outputs(manifest_a, RID, self._identity_dict())
        harness = StubHarness([ok_outcome(outputs)])
        self._patch(monkeypatch, harness)
        product = extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                              config=PdfExtractionConfig(), limits=LIMITS)
        assert harness.calls == 1  # Phase B never invoked: nothing to render
        [outcome] = product.result.manifest_view().page_outcomes
        assert outcome.render_status == "skipped_limit"
        assert product.result.outcome == "partial"


@pytest.mark.pdf
class TestRotationProvenance:
    """Repair-slice evidence: transforms are correct under rotation and
    offset CropBoxes, in both directions, within the declared tolerance."""

    def _round_trip(self, manifest, span):
        from backend.data_sources.extractors.pdf.coordinates import (
            forward_matrix, inverse_matrix, transform_bbox,
        )
        page = manifest.pages[span.locator.page_index]
        box_name = page.coordinate_frame.source_box
        box = tuple(page.boxes[box_name])
        rotation = page.rotation_degrees
        forward = forward_matrix(rotation, box)
        inverse = inverse_matrix(rotation, box)
        # source -> canonical reproduces the stored canonical bbox
        assert transform_bbox(forward, span.locator.source_bbox) == pytest.approx(
            span.locator.bbox, abs=0.002
        )
        # canonical -> source round-trips within the 3-decimal tolerance
        assert transform_bbox(inverse, span.locator.bbox) == pytest.approx(
            span.locator.source_bbox, abs=0.002
        )

    def test_rotated_fixture_source_bboxes_in_raw_mediabox(self, tmp_path):
        manifest = run_fixture("rotated_page.pdf", tmp_path).result.manifest_view()
        # no /CropBox is declared: the basis must say so honestly
        assert manifest.pages[0].coordinate_frame.canonical_basis == "mediabox_fallback"
        assert manifest.pages[0].coordinate_frame.source_box == "MediaBox"
        assert "CropBox" not in manifest.pages[0].boxes
        mx0, my0, mx1, my1 = manifest.pages[0].boxes["MediaBox"]
        assert (mx0, my0, mx1, my1) == (0.0, 0.0, 612.0, 792.0)  # raw, unrotated
        for span in manifest.spans:
            sx0, sy0, sx1, sy1 = span.locator.source_bbox
            assert mx0 <= sx0 <= sx1 <= mx1
            assert my0 <= sy0 <= sy1 <= my1

    def test_rotated_fixture_raw_placement_recovered(self, tmp_path):
        manifest = run_fixture("rotated_page.pdf", tmp_path).result.manifest_view()
        span = find_word(manifest, 0, "ROTATED")
        # designed raw baseline (72, 720) at 12pt
        assert span.locator.source_bbox[0] == pytest.approx(72.0, abs=1.0)
        assert 716.0 <= span.locator.source_bbox[1] <= span.locator.source_bbox[3] <= 731.0
        self._round_trip(manifest, span)

    def test_rotated_cropbox_fixture_full_chain(self, tmp_path):
        product = run_fixture("rotated_cropbox.pdf", tmp_path)
        manifest = product.result.manifest_view()
        expected = golden.ROTATED_CROPBOX
        page = manifest.pages[0]

        assert tuple(page.boxes["MediaBox"]) == expected["raw_mediabox"]
        assert tuple(page.boxes["CropBox"]) == expected["raw_cropbox"]
        assert page.coordinate_frame.canonical_basis == "cropbox"
        assert page.coordinate_frame.source_box == "CropBox"
        assert page.rotation_degrees == expected["rotation_degrees"]
        assert (page.width, page.height) == expected["canonical_size"]

        span = find_word(manifest, 0, expected["word"])
        assert span.locator.source_bbox[0] == pytest.approx(
            expected["word_source_x0"], abs=1.0
        )
        low, high = expected["word_source_y_range"]
        assert low <= span.locator.source_bbox[1] <= span.locator.source_bbox[3] <= high
        assert span.locator.bbox[0] == pytest.approx(
            expected["word_canonical_x0"], abs=golden.TOLERANCE_PT
        )
        assert span.locator.bbox[1] == pytest.approx(
            expected["word_canonical_y0"], abs=golden.TOLERANCE_PT
        )
        mx0, my0, mx1, my1 = expected["raw_mediabox"]
        for item in manifest.spans:
            sx0, sy0, sx1, sy1 = item.locator.source_bbox
            assert mx0 <= sx0 <= sx1 <= mx1 and my0 <= sy0 <= sy1 <= my1
        self._round_trip(manifest, span)

        # annotation: raw /Rect preserved, forward transform to canonical
        [annotation] = manifest.annotations
        assert tuple(annotation.locator.source_bbox) == expected["annotation_raw_rect"]
        assert annotation.locator.bbox == pytest.approx(
            list(expected["annotation_canonical_bbox"]), abs=0.002
        )
        assert annotation.uri_target == expected["annotation_uri"]
        self._round_trip(manifest, annotation)


class TestPhaseASchemaValidation:
    """Repair-slice evidence: every invalid Phase A manifest maps to
    EXTRACT_PDF_CHECKPOINT_INVALID, never an unhandled exception."""

    def _identity(self):
        from backend.data_sources.extractors.pdf.pdf_extractor import (
            pdf_extractor_identity,
        )
        return pdf_extractor_identity(PdfExtractionConfig(), {}).model_dump()

    def _outputs_for_bytes(self, manifest_bytes: bytes) -> dict[str, bytes]:
        checkpoint = {
            "checkpoint_schema_version": 1,
            "raw_record_id": RID,
            "extractor": self._identity(),
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            "state": "phase_a_complete",
        }
        return {
            "phase_a_status.json": json.dumps({"status": "ok", "error": None}).encode(),
            "manifest_a.json": manifest_bytes,
            "checkpoint.json": json.dumps(checkpoint).encode(),
        }

    def _expect_invalid(self, monkeypatch, manifest_bytes: bytes):
        outcome = ok_outcome(self._outputs_for_bytes(manifest_bytes))
        monkeypatch.setattr(
            "backend.data_sources.extractors.pdf.pdf_extractor.invoke_worker",
            StubHarness([outcome]),
        )
        with pytest.raises(ExtractionError) as excinfo:
            extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                        config=PdfExtractionConfig(), limits=LIMITS)
        assert excinfo.value.error_code == "EXTRACT_PDF_CHECKPOINT_INVALID"

    def test_malformed_manifest_json(self, monkeypatch):
        self._expect_invalid(monkeypatch, b"{not json at all")

    def test_checksum_correct_but_structurally_invalid(self, monkeypatch):
        manifest = stub_manifest_a()
        del manifest["pages"][0]["mediabox_raw"]  # required section field gone
        self._expect_invalid(monkeypatch, json.dumps(manifest).encode())

    def test_unknown_schema_version(self, monkeypatch):
        manifest = stub_manifest_a()
        manifest["phase_a_schema_version"] = 2
        self._expect_invalid(monkeypatch, json.dumps(manifest).encode())

    def test_raw_record_id_mismatch(self, monkeypatch):
        manifest = stub_manifest_a()
        manifest["raw_record_id"] = "f" * 32
        self._expect_invalid(monkeypatch, json.dumps(manifest).encode())

    def test_extractor_configuration_mismatch(self, monkeypatch):
        manifest = stub_manifest_a()
        manifest["config_fingerprint"] = "tampered"
        self._expect_invalid(monkeypatch, json.dumps(manifest).encode())

    def test_missing_section_and_wrong_types(self, monkeypatch):
        manifest = stub_manifest_a()
        del manifest["counts"]
        self._expect_invalid(monkeypatch, json.dumps(manifest).encode())
        manifest = stub_manifest_a()
        manifest["pages"][0]["char_count"] = "five"
        self._expect_invalid(monkeypatch, json.dumps(manifest).encode())

    def test_extra_unknown_fields_forbidden(self, monkeypatch):
        manifest = stub_manifest_a()
        manifest["surprise_section"] = {"x": 1}
        self._expect_invalid(monkeypatch, json.dumps(manifest).encode())


class TestActiveContentInventoryScope:
    def test_open_action_and_aa_presence_reported(self, monkeypatch):
        from backend.data_sources.extractors.pdf.pdf_extractor import (
            pdf_extractor_identity,
        )
        manifest = stub_manifest_a()
        manifest["catalog"]["open_action_present"] = True
        manifest["catalog"]["additional_actions_present"] = True
        identity = pdf_extractor_identity(PdfExtractionConfig(), {}).model_dump()
        outputs = phase_a_outputs(manifest, RID, identity)
        crash_b = WorkerOutcome(status="crashed", returncode=-9, stdout_tail="",
                                stderr_tail="", outputs={})
        monkeypatch.setattr(
            "backend.data_sources.extractors.pdf.pdf_extractor.invoke_worker",
            StubHarness([ok_outcome(outputs), crash_b]),
        )
        product = extract_pdf(payload=STUB_PDF, raw_record_id=RID,
                              config=PdfExtractionConfig(), limits=LIMITS)
        joined = " ".join(product.result.manifest_view().unsupported_features)
        assert "OpenAction present" in joined
        assert "/AA" in joined
        # narrow claim: nothing pretends other action types were inspected
        assert "never executed or inspected in detail" in joined


@pytest.mark.pdf
class TestFrameConsistency:
    """Follow-up repair evidence: no mixed-frame comparisons remain —
    block and table geometry live in the canonical frame with correct
    forward/inverse provenance on normal, rotated, and offset-CropBox
    pages."""

    FIXTURE_SET = ("manual_multipage.pdf", "rotated_cropbox.pdf",
                   "rotated_cropbox_table.pdf")

    def _frame_matrices(self, manifest, page_index):
        from backend.data_sources.extractors.pdf.coordinates import (
            forward_matrix, inverse_matrix,
        )
        page = manifest.pages[page_index]
        box = tuple(page.boxes[page.coordinate_frame.source_box])
        return (forward_matrix(page.rotation_degrees, box),
                inverse_matrix(page.rotation_degrees, box))

    def test_block_invariants_on_all_fixture_geometries(self, tmp_path):
        from backend.data_sources.extractors.pdf.coordinates import transform_bbox
        tol = 0.01
        for name in self.FIXTURE_SET:
            manifest = run_fixture(name, tmp_path / name).result.manifest_view()
            spans_by_id = {s.span_id: s for s in manifest.spans}
            assert manifest.blocks, name
            for block in manifest.blocks:
                forward, inverse = self._frame_matrices(
                    manifest, block.locator.page_index
                )
                bb = block.locator.bbox
                assert all(v >= -tol for v in bb), (name, bb)  # never negative
                for span_id in block.span_ids:
                    span = spans_by_id[span_id]  # exists
                    assert span.locator.page_index == block.locator.page_index
                    sb = span.locator.bbox
                    assert bb[0] <= sb[0] + tol and bb[1] <= sb[1] + tol
                    assert sb[2] <= bb[2] + tol and sb[3] <= bb[3] + tol
                assert transform_bbox(forward, block.locator.source_bbox) == (
                    pytest.approx(bb, abs=0.002)
                ), (name, "forward")
                assert transform_bbox(inverse, bb) == pytest.approx(
                    block.locator.source_bbox, abs=0.002
                ), (name, "inverse")

    def test_cropped_span_contained_by_its_block(self, tmp_path):
        manifest = run_fixture("rotated_cropbox.pdf", tmp_path).result.manifest_view()
        span = find_word(manifest, 0, "CROPPED")
        assert span.locator.bbox == pytest.approx(
            [657.516, 22.0, 669.516, 81.34], abs=0.002
        )
        [block] = [b for b in manifest.blocks if span.span_id in b.span_ids]
        bb = block.locator.bbox
        # a doubly-transformed (shifted/negative) block bbox fails this
        assert bb[0] <= 657.516 + 0.01 and bb[1] <= 22.0 + 0.01
        assert bb[2] >= 669.516 - 0.01 and bb[3] >= 81.34 - 0.01
        assert all(v >= 0 for v in bb)

    def test_rotated_cropbox_table_links_in_canonical_frame(self, tmp_path):
        from backend.data_sources.extractors.pdf.coordinates import transform_bbox
        manifest = run_fixture(
            "rotated_cropbox_table.pdf", tmp_path
        ).result.manifest_view()
        expected = golden.ROTATED_CROPBOX_TABLE

        page = manifest.pages[0]
        assert tuple(page.boxes["MediaBox"]) == expected["raw_mediabox"]
        assert tuple(page.boxes["CropBox"]) == expected["raw_cropbox"]
        # linking must not depend on the boxes sharing an origin:
        assert page.boxes["CropBox"][:2] != page.boxes["MediaBox"][:2]

        [candidate] = manifest.table_candidates
        assert candidate.row_count == expected["row_count"]
        assert candidate.column_count == expected["column_count"]
        assert candidate.locator.bbox == pytest.approx(
            list(expected["table_bbox_canonical"]), abs=golden.TOLERANCE_PT
        )
        forward, inverse = self._frame_matrices(manifest, 0)
        for item in [candidate, *candidate.cells]:
            assert transform_bbox(forward, item.locator.source_bbox) == (
                pytest.approx(item.locator.bbox, abs=0.002)
            )
            assert transform_bbox(inverse, item.locator.bbox) == pytest.approx(
                item.locator.source_bbox, abs=0.002
            )

        spans_by_id = {s.span_id: s for s in manifest.spans}
        linked_texts = set()
        tol = candidate.cell_span_link_tolerance_points
        for cell in candidate.cells:
            assert cell.span_refs, (cell.row_index, cell.column_index)
            cb = cell.locator.bbox
            for span_id in cell.span_refs:
                span = spans_by_id[span_id]
                linked_texts.add(span.text)
                cx = (span.locator.bbox[0] + span.locator.bbox[2]) / 2
                cy = (span.locator.bbox[1] + span.locator.bbox[3]) / 2
                assert cb[0] - tol <= cx <= cb[2] + tol
                assert cb[1] - tol <= cy <= cb[3] + tol
        assert linked_texts == expected["cell_texts"]
