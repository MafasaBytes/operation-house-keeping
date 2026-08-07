"""Hand-authored golden expectations for the frozen PDF fixtures.

Independent oracle: values derive from the DESIGNED content documented in
the fixture generator's docstring (baselines, grid lines, page setup) and
the manual inspection at freeze time — never from extractor output.

Coordinate expectations use the canonical frame (top-left origin, y down,
pdf points). For text placed at baseline y_b with font size s on a page of
height H, the glyph-box top is H - y_b - ascent(s); Helvetica's ascent is
roughly 0.72-0.8 em, so expectations carry a +/- tolerance instead of
bit-exact floats (spec: tolerance-based geometry tests).
"""

TOLERANCE_PT = 3.0

MANUAL = {
    "page_count": 3,
    "page_labels": ["i", "1", "2"],
    "page_size": (612.0, 792.0),
    # (page_index, word_text, designed x0, approx canonical top)
    "words": [
        (0, "OPERATION", 72.0, 792 - 720 - 11.0),   # 14 pt ascent ~11
        (1, "TORQUE", 72.0, 792 - 720 - 9.5),        # 12 pt ascent ~9.5
        (1, "BOLT", 200.0, 792 - 400 - 8.0),         # 10 pt ascent ~8
        (2, "SERVICE", 72.0, 792 - 720 - 9.5),
    ],
    "page1_line": {"from": (72.0, 100.0), "to": (300.0, 100.0)},  # source coords
    "all_pages_kind": "born_digital_text",
}

TABLE = {
    # designed ruled grid
    "verticals_x": [72.0, 222.0, 372.0, 522.0],
    "horizontals_y_source": [510.0, 540.0, 570.0, 600.0],
    "row_count": 3,
    "column_count": 3,
    # (row, col) -> designed cell text
    "cells": {
        (0, 0): "ITEM NO", (0, 1): "QTY", (0, 2): "UNIT",
        (1, 0): "100-002", (1, 1): "8", (1, 2): "piece",
        (2, 0): "100-003", (2, 1): "8", (2, 2): "piece",
    },
    # canonical top of the grid = 792 - 600 = 192; bottom = 792 - 510 = 282
    "bbox_canonical": (72.0, 192.0, 522.0, 282.0),
}

DRAWING = {
    "rect_count": 1,
    "line_count": 1,
    "callouts": [("BRACKET-A", 385.0), ("SEE", 385.0)],  # (first word, x0)
    "page_kind": "born_digital_text",
}

SCANNED = {
    "word_count": 0,
    "image_count": 1,
    # image placed at (100,300) size 400x400 -> canonical top = 792-700=92
    "image_bbox_canonical": (100.0, 92.0, 500.0, 492.0),
    "page_kind": "image_only",
    "ocr_required": True,
}

MIXED = {
    "image_count": 1,
    "first_word": ("FIGURE", 72.0),
    "page_kind": "mixed",
}

ROTATED = {
    "rotation_degrees": 90,
    # displayed (rotated) frame dimensions
    "canonical_size": (792.0, 612.0),
    "contains_word": "ROTATED",
}

ACTIVE_CONTENT = {
    "javascript_present": True,
    "embedded_files_present": True,
    "uri_targets": ["http://example.invalid/manual"],
}

ENCRYPTED_ERROR_CODE = "EXTRACT_PDF_PASSWORD_REQUIRED"
MALFORMED_ERROR_CODE = "EXTRACT_PDF_PARSE_FAILED"


# rotated_cropbox.pdf — designed raw content (see generator docstring):
# MediaBox [0 0 612 792], CropBox [50 40 562 742], /Rotate 90;
# text baseline raw (72, 700) 12pt; Link /Rect [100 600 200 640].
ROTATED_CROPBOX = {
    "raw_mediabox": (0.0, 0.0, 612.0, 792.0),
    "raw_cropbox": (50.0, 40.0, 562.0, 742.0),
    "rotation_degrees": 90,
    "canonical_size": (702.0, 512.0),          # (cy1-cy0, cx1-cx0)
    "word": "CROPPED",
    # raw glyph box for baseline (72, 700) at 12pt: x0=72, y in ~[697.5, 709.5]
    "word_source_x0": 72.0,
    "word_source_y_range": (696.0, 711.0),
    # canonical: x' = y_raw - 40, y' = x_raw - 50
    "word_canonical_x0": 657.5,
    "word_canonical_y0": 22.0,
    "annotation_raw_rect": (100.0, 600.0, 200.0, 640.0),
    "annotation_canonical_bbox": (560.0, 50.0, 600.0, 150.0),
    "annotation_uri": "http://example.invalid/detail",
}
