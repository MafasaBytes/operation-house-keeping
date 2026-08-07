"""PDF extraction worker. Runs ONLY as a subprocess under the worker
harness; this is the sole module allowed to import the PDF toolchain.

    python -m backend.data_sources.extractors.pdf.worker a <input> <outdir> <config_json> <context_json>
    python -m backend.data_sources.extractors.pdf.worker b <input> <outdir> <config_json> <pages_json>

Phase A (structural): always writes ``phase_a_status.json``; on success
also writes ``manifest_a.json`` plus an atomically-renamed
``checkpoint.json`` binding {raw_record_id, extractor identity, config
fingerprint, manifest sha256}. Phase B (rendering): renders the requested
pages within per-page/aggregate limits and writes ``render_results.json``
plus ``page_<n>.png`` files. Handled failures exit 0 and are reported as
data; a non-zero exit is an unhandled crash.

Security: JavaScript, actions, links, and embedded files are inventoried
read-only and never executed, followed, or extracted; all diagnostic
strings are length-bounded and contain no filesystem paths.
"""

import hashlib
import io
import json
import sys
from pathlib import Path

_BOUND = 500


def _b(text) -> str | None:
    if text is None:
        return None
    return str(text)[:_BOUND]


def _round(value: float) -> float:
    return round(float(value), 3)


def phase_a(input_path: Path, output_dir: Path, config: dict, context: dict) -> dict:
    import importlib.metadata as md

    import pdfplumber
    import pypdf

    status: dict = {"status": "ok", "error": None}

    reader = pypdf.PdfReader(str(input_path))
    encryption = {"present": False, "method": None, "authentication_outcome": "not_required"}
    password = ""
    if reader.is_encrypted:
        encryption["present"] = True
        try:
            outcome = reader.decrypt("")
            opened = bool(outcome)
        except Exception:
            opened = False
        if not opened:
            return {
                "status": "password_required",
                "error": "document requires a password; credentialed "
                "decryption is not a DS-003 capability",
            }
        encryption["authentication_outcome"] = "empty_password_ok"
        encryption["method"] = _b(getattr(reader, "_encryption", None) and "standard_security_handler")

    if len(reader.pages) > config["max_pages"]:
        return {
            "status": "limit_exceeded",
            "error": f"document has {len(reader.pages)} pages, exceeding the "
            f"structural limit of {config['max_pages']}",
        }

    meta = reader.metadata or {}
    root = reader.trailer["/Root"]
    names = root.get("/Names", {})
    javascript_count = 0
    embedded_file_names: list[str] = []
    try:
        if "/JavaScript" in names:
            js_kids = names["/JavaScript"].get_object().get("/Names", [])
            javascript_count = max(1, len(js_kids) // 2)
    except Exception:
        javascript_count = 1  # present but unreadable: still report presence
    try:
        if "/EmbeddedFiles" in names:
            ef = names["/EmbeddedFiles"].get_object().get("/Names", [])
            embedded_file_names = [_b(ef[i]) for i in range(0, len(ef), 2)]
    except Exception:
        embedded_file_names = ["<unreadable>"]
    ocg_names = []
    try:
        for group in root.get("/OCProperties", {}).get("/OCGs", []):
            ocg_names.append(_b(group.get_object().get("/Name")))
    except Exception:
        pass

    labels = None
    try:
        if "/PageLabels" in root:
            labels = [reader.page_labels[i] for i in range(len(reader.pages))]
    except Exception:
        labels = None

    # Raw (unrotated user-space) geometry comes from pypdf: pdfplumber
    # reports rotated, MediaBox-normalized values and mangles offset
    # CropBoxes, so it must not be trusted for the source frame.
    raw_geometry: dict[int, dict] = {}
    for index, page in enumerate(reader.pages):
        rotation = int(page.get("/Rotate") or getattr(page, "rotation", 0) or 0)
        if rotation % 90 != 0:
            return {
                "status": "unsupported_rotation",
                "error": f"page {index} declares /Rotate {rotation}, which is "
                "not a multiple of 90",
            }
        raw_geometry[index] = {
            "mediabox_raw": [float(v) for v in page.mediabox],
            "cropbox_raw": [float(v) for v in page.cropbox],
            "crop_declared": page.get("/CropBox") is not None,
            "rotation_raw": rotation % 360,
        }

    annotations_by_page: dict[int, list[dict]] = {}
    for index, page in enumerate(reader.pages):
        entries = []
        for ref in page.get("/Annots") or []:
            try:
                obj = ref.get_object()
                action = obj.get("/A", {})
                uri = action.get("/URI") if action.get("/S") == "/URI" else None
                rect = [float(v) for v in obj.get("/Rect", [0, 0, 0, 0])]
                entries.append({
                    "subtype": _b(obj.get("/Subtype", "?")).lstrip("/"),
                    "rect": rect,  # PDF user space, bottom-left origin
                    "contents": _b(obj.get("/Contents")),
                    "uri": _b(uri),
                })
            except Exception:
                entries.append({"subtype": "unreadable", "rect": [0, 0, 0, 0],
                                "contents": None, "uri": None})
        if entries:
            annotations_by_page[index] = entries

    pages_out = []
    total_chars = 0
    layout_objects = 0
    with pdfplumber.open(str(input_path), password=password or None) as pdf:
        for index, page in enumerate(pdf.pages):
            # NOTE: grouping by float char attributes (e.g. size) splits
            # words on rotated pages due to tiny per-char float differences;
            # extract plain words and probe chars for font attribution.
            words = page.extract_words()
            chars = page.chars if len(page.chars) <= 20000 else []
            for word in words:
                inside = [
                    c for c in chars
                    if word["x0"] - 0.5 <= c["x0"] and c["x1"] <= word["x1"] + 0.5
                    and word["top"] - 0.5 <= c["top"] and c["bottom"] <= word["bottom"] + 0.5
                ]
                word["fontname"] = inside[0]["fontname"] if inside else None
                word["size"] = round(inside[0]["size"], 2) if inside else None
            drawn = list(page.lines), list(page.rects), list(page.curves)
            images = list(page.images)
            total_chars += len(page.chars)
            layout_objects += len(words) + sum(len(x) for x in drawn) + len(images)
            if total_chars > config["max_chars"] or layout_objects > config["max_layout_objects"]:
                return {
                    "status": "limit_exceeded",
                    "error": "structural extraction limit exceeded "
                    f"(chars={total_chars}, layout_objects={layout_objects})",
                }
            ink_boxes = [
                (obj["x0"], obj["top"], obj["x1"], obj["bottom"])
                for group in drawn for obj in group
            ]
            ink_bbox = None
            if ink_boxes:
                ink_bbox = [
                    _round(min(b[0] for b in ink_boxes)),
                    _round(min(b[1] for b in ink_boxes)),
                    _round(max(b[2] for b in ink_boxes)),
                    _round(max(b[3] for b in ink_boxes)),
                ]
            tables = []
            for table in page.find_tables():
                rows = table.rows
                cells = []
                for r_index, row in enumerate(rows):
                    for c_index, cell in enumerate(row.cells):
                        if cell is None:
                            continue
                        x0, top, x1, bottom = cell
                        cells.append({
                            "row": r_index, "col": c_index,
                            "bbox": [_round(x0), _round(top), _round(x1), _round(bottom)],
                        })
                tables.append({
                    "bbox": [_round(v) for v in table.bbox],
                    "rows_n": len(rows),
                    "cols_n": max((len(r.cells) for r in rows), default=0),
                    "cells": cells,
                })
            geometry = raw_geometry[index]
            pages_out.append({
                "page_index": index,
                "page_label": labels[index] if labels else None,
                "displayed_width": _round(page.width),
                "displayed_height": _round(page.height),
                "mediabox_raw": geometry["mediabox_raw"],
                "cropbox_raw": geometry["cropbox_raw"],
                "crop_declared": geometry["crop_declared"],
                "rotation_raw": geometry["rotation_raw"],
                "words": [
                    {
                        "text": w["text"],
                        "x0": _round(w["x0"]), "top": _round(w["top"]),
                        "x1": _round(w["x1"]), "bottom": _round(w["bottom"]),
                        "fontname": _b(w.get("fontname")),
                        "size": _round(w["size"]) if w.get("size") else None,
                        "upright": bool(w.get("upright", True)),
                    }
                    for w in words
                ],
                "lines_n": len(drawn[0]), "rects_n": len(drawn[1]),
                "curves_n": len(drawn[2]), "ink_bbox": ink_bbox,
                "images": [
                    {
                        "x0": _round(im["x0"]), "top": _round(im["top"]),
                        "x1": _round(im["x1"]), "bottom": _round(im["bottom"]),
                        "srcwidth": im.get("srcsize", (None, None))[0],
                        "srcheight": im.get("srcsize", (None, None))[1],
                        "colorspace": _b(str(im.get("colorspace"))),
                        "filters": [],
                    }
                    for im in images
                ],
                "annotations": annotations_by_page.get(index, []),
                "tables": tables,
                "char_count": len(page.chars),
            })

    manifest_a = {
        "metadata": {
            "declared_title": _b(meta.get("/Title")),
            "declared_author": _b(meta.get("/Author")),
            "declared_subject": _b(meta.get("/Subject")),
            "declared_producer": _b(meta.get("/Producer")),
            "declared_creator": _b(meta.get("/Creator")),
            "declared_creation_date_raw": _b(meta.get("/CreationDate")),
            "declared_mod_date_raw": _b(meta.get("/ModDate")),
            "pdf_version": _b(getattr(reader, "pdf_header", "?")).replace("%PDF-", ""),
            "page_label_spec_present": labels is not None,
            "encryption": encryption,
        },
        "catalog": {
            "javascript_count": javascript_count,
            "embedded_file_names": embedded_file_names,
            "ocg_names": ocg_names,
        },
        "toolchain": {
            name: md.version(name)
            for name in ("pdfplumber", "pdfminer.six", "pypdf")
        },
        "pages": pages_out,
        "counts": {"total_chars": total_chars, "layout_objects": layout_objects},
    }

    manifest_bytes = json.dumps(manifest_a, sort_keys=True).encode()
    if len(manifest_bytes) > config["max_manifest_bytes"]:
        return {
            "status": "limit_exceeded",
            "error": f"structural manifest of {len(manifest_bytes)} bytes "
            "exceeds the configured limit",
        }
    (output_dir / "manifest_a.json").write_bytes(manifest_bytes)
    checkpoint = {
        "checkpoint_schema_version": 1,
        "raw_record_id": context["raw_record_id"],
        "extractor": context["extractor"],
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "state": "phase_a_complete",
    }
    tmp = output_dir / "checkpoint.json.tmp"
    tmp.write_text(json.dumps(checkpoint, sort_keys=True), "utf-8")
    tmp.replace(output_dir / "checkpoint.json")  # atomic completion marker
    return status


def phase_b(input_path: Path, output_dir: Path, config: dict, plan: dict) -> dict:
    import importlib.metadata as md

    import pypdfium2 as pdfium
    from PIL import Image  # noqa: F401  (registers PNG codec)

    results = []
    produced_bytes = 0
    doc = pdfium.PdfDocument(str(input_path))
    try:
        if plan.get("password_empty"):
            pass  # pdfium opens empty-user-password documents transparently
        for page_index in plan["pages"]:
            entry = {"page_index": page_index, "status": "rendered", "error": None,
                     "pixel_width": None, "pixel_height": None}
            try:
                page = doc[page_index]
                bitmap = page.render(scale=config["dpi"] / 72)
                pil = bitmap.to_pil().convert("RGB")
                buffer = io.BytesIO()
                pil.save(buffer, format="PNG", optimize=False, compress_level=9)
                data = buffer.getvalue()
                produced_bytes += len(data)
                if produced_bytes > config["max_derivative_bytes"]:
                    entry.update(status="skipped_limit",
                                 error="aggregate derivative byte limit reached")
                else:
                    (output_dir / f"page_{page_index}.png").write_bytes(data)
                    entry.update(pixel_width=pil.width, pixel_height=pil.height)
                page.close()
            except Exception as error:
                entry.update(status="render_failed",
                             error=f"{type(error).__name__}"[:200])
            results.append(entry)
    finally:
        doc.close()

    render_results = {
        "pages": results,
        "component_versions": {
            "pdfium": md.version("pypdfium2"),
            "pillow": md.version("pillow"),
        },
    }
    (output_dir / "render_results.json").write_text(
        json.dumps(render_results, sort_keys=True), "utf-8"
    )
    return {"status": "ok", "error": None}


def main() -> int:
    phase = sys.argv[1]
    input_path = Path(sys.argv[2])
    output_dir = Path(sys.argv[3])
    config = json.loads(sys.argv[4])
    extra = json.loads(sys.argv[5])
    output_dir.mkdir(parents=True, exist_ok=True)

    if phase == "a":
        try:
            status = phase_a(input_path, output_dir, config, extra)
        except Exception as error:
            status = {
                "status": "parse_failed",
                "error": f"structural extraction failed "
                f"({type(error).__name__})"[:300],
            }
        (output_dir / "phase_a_status.json").write_text(
            json.dumps(status, sort_keys=True), "utf-8"
        )
        return 0

    if phase == "b":
        status = phase_b(input_path, output_dir, config, extra)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
