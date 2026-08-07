# DS-003 PDF Drawing/Manual Ingestion — Design

Date: 2026-08-07
Status: Approved by project owner with required amendments (incorporated).
No further design round unless the spike invalidates the toolchain or the
two-phase worker boundary.

## What this slice validates

Acquire a PDF engineering document through the existing source boundary and
extract format-level structure with a defensible trace for every item:

```
Raw PDF → checksum → physical page → exact page region
        → extraction method and version → extracted item
```

Not document chat, not semantic interpretation, not cross-source
reconciliation. OCR is deliberately deferred (Level 4 slot reserved).

## Extraction levels

```
L0  raw PDF, checksum, media type, acquisition metadata      (runtime, DS-001)
L1  document + page structure: page count, physical index, labels,
    dimensions, rotation, boxes, encryption state, source-declared
    metadata, eof_marker_count heuristic, derived page_kind
L2  positioned native content: text spans, images, annotations, links,
    vector inventory (counts + ink bbox)
L3  method-declared heuristics + derivatives: page renders, table
    candidates, inferred reading order
L4  OCR (deferred; unclaimable in DS-003)
L5  engineering semantics (unclaimable)
```

`levels_supported = [0,1,2,3]`. Drawing-region candidates are **declared
unsupported** in DS-003 (no deterministic algorithm with oracle tests yet);
the vector inventory is the honest substitute.

## Toolchain (ADR-0003)

`pdfplumber==0.11.10` + `pypdf==6.15.0`, hash-pinned closure in
`requirements-pdf.txt` (brings `pdfminer.six==20260107`, `pypdfium2==5.12.1`,
Pillow, cryptography, and their deps). PyMuPDF 1.28.2 rejected
(AGPL-3.0/commercial). The closure is **not** pure Python — PDFium, Pillow,
and cryptography ship native components — so worker isolation remains
mandatory. All four libraries import only inside the worker.

Roles: pdfminer/pdfplumber — positioned chars/words/lines, layout analysis,
table candidates, vector + image + annotation inventory; pypdfium2 + Pillow —
Phase B page rendering and PNG encoding; pypdf — declared metadata, page
labels, encryption state, and the read-only active-content catalog scan.

### Spike results (2026-08-07, Task 0 — gate PASSED)

Environment: WSL2 Ubuntu x86_64, CPython 3.13.11, resolved closure
pdfplumber 0.11.10 / pdfminer.six 20260107 / pypdfium2 5.12.1 /
Pillow 12.3.0 / pypdf 6.15.0 / cryptography 50.0.0. Findings:

- A stdlib-generated PDF (self-computed xref) parses in pdfplumber with
  the exact designed coordinates (word x0 = 72.0 for text placed at
  Td 72 720; top = 792 − 720 − ascent, consistent with Helvetica metrics)
  — the fixture-generator approach is viable and oracle-friendly.
- Extraction output (words, bboxes rounded to 3 decimals, counts) is
  identical across repeated runs in-process and **across separate
  processes**.
- pypdfium2 (scale 150/72) + Pillow PNG (RGB, optimize=False,
  compress_level=9) produced **byte-identical renders across separate
  processes** on this platform (sha256 791ea72e…, 1275×1651 px).
- pypdf surfaces page labels, `is_encrypted`, and a read-only catalog
  scan that inventories JavaScript name-tree entries, embedded-file
  declarations, and URI link annotations without executing anything.
- Encrypted (AES-256, non-empty user password): pypdf detects;
  pdfplumber raises `PdfminerException` without the password.
  Malformed (50% truncation): `PdfminerException` / `PdfStreamError`.
- The pypdfium2 wheel ships its license inventory in-wheel
  (`dist-info/licenses/LICENSES/`: Apache-2.0, BSD-3-Clause, CC-BY-4.0,
  plus `BUILD_LICENSES` for bundled PDFium components — abseil, agg23,
  fast_float, freetype, icu, and others) — recorded in
  THIRD_PARTY_NOTICES.md.
- Resolved closure is 8 packages (adds charset-normalizer and
  typing_extensions; cryptography 50 needs no cffi on CPython 3.13),
  hash-pinned in `requirements-pdf.txt`.

## Two-phase worker (amendment 2)

```
Parent                             Worker (isolated subprocess)
──────                             ────────────────────────────
invoke Phase A ────────────────▶   structural extraction (L1–L2 + L3
                                   candidates), writes manifest_a.json,
                                   then atomically (tmp+rename) writes
                                   checkpoint.json:
                                     {checkpoint_schema_version,
                                      raw_record_id, extractor identity +
                                      config_fingerprint,
                                      manifest_sha256, state:
                                      "phase_a_complete"}
validate checkpoint:
  present, parseable, state OK,
  raw_record_id + identity +
  fingerprint match expectation,
  sha256(manifest_a.json) matches
  ── invalid/missing/crash ──▶ QUARANTINE
invoke Phase B ────────────────▶   render pages (per-page + aggregate
                                   limits), per-page try/except, writes
                                   page_<n>.png + render_results.json
assemble final result:
  A ok + B ok            → succeeded
  A ok + B crash/timeout/limit or page failures
                          → partial, with only the page derivatives that
                            actually completed (crash ⇒ possibly none)
publish once: derivatives first, single final envelope last
(validated Phase A output stays in parent staging until the final
 envelope is ready; no competing write-once results)
```

A `manifest_a.json` that merely *exists* after a crash is never trusted:
only a valid checkpoint admits it.

## Page-level outcomes and aggregation (amendment 3)

`PdfPageOutcome` per page: `levels_achieved`, `render_status`
(`rendered | render_failed | skipped_limit | not_attempted`), `warnings`,
`ocr_required`, `derivative_ids`, `failure_reason`. Document
`levels_achieved` is the **conservative aggregation**: a level is document-
achieved only if achieved on every content page; partial coverage is
explicit via the per-page outcomes plus a document warning
(`level 3 achieved on 4/6 pages`).

## Canonical coordinates (amendment 4)

`PageRegionLocator` declares, per region: 0-based `page_index`;
`page_label`; canonical `bbox`; and via the page's
`PdfCoordinateFrame`: canonical basis **CropBox** (fallback MediaBox when
absent, recorded), canonical page width/height, source box name, the
source→canonical transformation matrix, rotation value and whether
normalization to the displayed frame was applied, origin `top_left`,
y-axis `downward`, unit `pdf_points`, and declared rounding precision
(**3 decimals**). Source-native coordinates (`source_bbox`,
`source_coordinate_system`) are preserved verbatim. Geometry tests are
tolerance-based; bit-exact cross-platform floats are not promised.

Identifiers derived from extraction order or position are named
`extractor-derived` (`span_id`, `extraction_order_index`); no
content-stream index is claimed (pdfminer does not reliably expose one).

## Honesty rules (amendment 5)

- `page_kind` (`born_digital_text | image_only | mixed | empty`) is a
  derived classification with method + thresholds + confidence.
- `eof_marker_count` is a byte-scan heuristic, not an edit-history claim.
- Extracted order (`extraction_order_index`) is stored separately from
  inferred reading order (`reading_order_index` + method + confidence +
  basis literal); inferred order is never labeled source-native.
- Cell→span linking is spatial: `cell_span_link_method` +
  `cell_span_link_tolerance_points` recorded on the candidate;
  `row_span`/`column_span` are optional (None when not established).
- Document metadata fields are prefixed `declared_` — source-declared,
  not authoritative; date strings kept raw with optional parsed values.

## Encryption and hostile content (amendment 6)

Empty-user-password documents decrypt and proceed with warning
`encrypted_openable`; the manifest records
`encryption: {present, method, authentication_outcome}`. Password-required
→ quarantine `EXTRACT_PDF_PASSWORD_REQUIRED` (credentialed decryption is a
future capability tied to `credential_reference`). JavaScript, actions,
launch instructions, links, and embedded files are inventoried via a
read-only catalog scan and **never executed/opened/followed**; URI targets,
attachment names, metadata, and diagnostics are length-bounded and
redacted. A dedicated active-content fixture proves inventory-without-
execution.

## Resource limits (amendment 7, all configurable)

Structural: 500 pages, 5M extracted characters, 500k layout objects,
64 MB canonical manifest. Exceeding a structural cap ⇒ quarantine
(`EXTRACT_PDF_LIMIT_EXCEEDED`) — no truncated "success".
Rendering: 150 DPI RGB PNG; 40 MP per page; 250 MP total per document;
256 MB derivative bytes. Reaching a render cap after successful Phase A ⇒
honest partial with per-page `skipped_limit` coverage. Existing harness
wall-clock/memory/payload limits unchanged.

## Contract changes (amendment 8)

- `DerivativeCore` (id, raw_record_id, media_type, payload_reference,
  checksum, generator, environment) with discriminated
  `GltfDerivativeRecord` (tessellation, coordinate_conversion, node_map)
  and `PageRenderDerivativeRecord` (page_index, dpi, colorspace,
  pixel_width/height).
- `ExtractionEnvironment.component_versions: dict[str,str]`; legacy
  `occt_version` JSON is converted on read. Existing STEP artifacts remain
  readable and are never rewritten or reinterpreted.
- `ExtractionResult` union gains `PdfManifestResult (kind="pdf_manifest")`;
  `schema_version` distinguishes 1 (DS-002-era) from 2 (current writes);
  both validate on read.
- Store orphan scan generalizes over any manifest exposing `derivatives`.
- Source Profile v1: `pdf_drawing_manual` → required/next/enabled. The
  connector `available` rung now verifies the extraction dependency
  closure for the source's declared content type (OCP for STEP; pdfplumber/
  pypdf/pypdfium2 for PDF) — profile entries never imply capability, and
  `validated` still requires a real accepted ingestion run.

## Determinism (amendment 9)

Manifest JSON: canonical and byte-stable (double-extraction test) — never
weakened. Geometry values rounded at the declared precision before
serialization. Render PNGs: checksums always recorded with platform,
architecture, pdfium/pillow versions, DPI, colorspace; byte stability
asserted on the pinned platform only; cross-platform comparison is over
declared semantic render properties (pixel dimensions, format), with
platform-scoped checksums if the spike shows divergence.

## Fixtures (amendment 9) and independent oracle

Generator-authored (committed stdlib generator that computes xref offsets
itself and documents how; pypdf used only to produce the encrypted
fixture), byte-frozen with checksums in FIXTURES.md:

1. `manual_multipage.pdf` — 3 pages, designed text at designed coordinates,
   page labels (i, 1, 2).
2. `table_page.pdf` — ruled 3×3 table, designed grid + cell text.
3. `drawing_callouts.pdf` — vector lines/rects + positioned callouts.
4. `scanned_only.pdf` — image XObject only, zero text objects.
5. `mixed_text_image.pdf` — text + image on one page.
6. `rotated_page.pdf` — /Rotate 90, designed text.
7. `malformed.pdf` — truncated xref.
8. `encrypted.pdf` — AES, non-empty user password (documented test vector,
   not a credential).
9. `active_content.pdf` — JavaScript name-tree entry, URI annotation,
   embedded-file declaration; inventory-without-execution proof.

Golden expectations are hand-authored from the designed coordinates
(tolerance ±2 pt) and maintained independently of extractor output.

## Test strategy

Marker `pdf` (loud skip without the extra). Non-marked parent tests with
stubbed worker outcomes: checkpoint validation (missing/corrupt/mismatched
→ quarantine), phase-B failure → partial, limit mapping, coordinate
canonicalization math against hand-computed values. Golden `pdf` tests per
fixture. E2E through the runner: ingest, rerun, replay-after-delete,
quarantines (malformed/encrypted), partial (image-only), orphan injection.
Determinism double-runs. DS-001/DS-002 suites green throughout; clean
checkout with all requirement files.

## Acceptance criteria

Every extracted item traces raw → checksum → page → region (with declared
frame) → method+version → item; the partial-outcome table above holds for
all nine fixtures; two-phase checkpoint semantics proven by failure
injection; page-level outcomes + conservative document aggregation; active
content inventoried, never executed; limits produce honest outcomes;
manifest byte-determinism; render checksums + environment recorded;
DS-002 artifacts still readable; suites green from clean checkout; docs,
limitations, and the next open question recorded.

## Next open question (after DS-003)

Per Profile v1, the remaining required family is the operational
API/telemetry source — and whether the page-kind classification plus OCR
(Level 4) should be brought forward before it.
