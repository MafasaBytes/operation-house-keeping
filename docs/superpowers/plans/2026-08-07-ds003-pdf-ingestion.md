# DS-003 PDF Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** PDF engineering documents acquired through the existing boundary
and extracted to honest Levels 0–3 manifests with page/region provenance,
two-phase worker semantics, page-level outcomes, render derivatives, and
replay — per the spec
(`docs/superpowers/specs/2026-08-07-ds003-pdf-ingestion-design.md`), which
is the authority on every contract field, outcome rule, and amendment.

**Tech stack:** ADR-0003 (`pdfplumber==0.11.10` + `pypdf==6.15.0`,
hash-pinned closure, worker-isolated).

## Global Constraints

- All DS-001/DS-002 global constraints continue (read-only, redaction, UTC,
  TDD, suite green per commit, no push).
- PDF libraries import only inside the worker and the fixture generator.
- Never execute/open/follow JavaScript, actions, links, embedded files.
- Coordinates canonicalized per spec (CropBox basis, top-left/y-down,
  points, 3-decimal rounding); source coords preserved; tolerance-based
  geometry tests.
- Extractor-derived identifiers named as such; no content-stream claims.
- Phase A checkpoint validated before Phase B; single final envelope.
- Tests needing the closure carry marker `pdf`, loud skip otherwise.

## Tasks

### Task 0: Spike (gate)
Install pinned closure; verify: pdfplumber span coordinates stable across
runs; pypdfium2+Pillow PNG byte-stable same-platform with pinned settings;
pypdf catalog scan surfaces JS/URI/embedded-file declarations read-only;
encrypted + malformed behavior; record wheel license inventory. **Stop if
coordinates are unstable or rendering is unusable headless.** Record
results in the spec; generate `requirements-pdf.txt` from the resolved
closure with PyPI hashes.

### Task 1: Contract refactors
Tests then code: `DerivativeCore` + discriminated
`GltfDerivativeRecord | PageRenderDerivativeRecord`;
`ExtractionEnvironment.component_versions` with legacy `occt_version`
read-conversion; `ExtractionResult.schema_version ∈ {1,2}` (writes=2,
v1 readable); orphan scan generalized over manifests exposing
`derivatives`; DS-002 tests updated, STEP artifacts never rewritten.

### Task 2: PDF contracts
Tests then models per spec: `PdfCoordinateFrame`, `PageRegionLocator`,
`PdfDocumentMetadata` (declared_*), `PdfPage` (+derived page_kind fields),
`PdfTextSpan`/`PdfTextBlock` (extraction_order vs reading_order+basis),
`PdfImage`, `PdfAnnotation`, `PdfVectorSummary`, `PdfTableCandidate`/
`PdfTableCell` (optional spans, link method+tolerance),
`PdfPageOutcome`, `PdfExtractionManifest` (conservative document levels
validator), `PdfManifestResult`, new error codes.

### Task 3: Detector + availability
`%PDF-` within first 1024 bytes → `confirmed_pdf`; connector `available`
rung checks the extraction dependency closure for the source's declared
content type (OCP / pdf closure); tests for both.

### Task 4: Fixtures + oracle
Committed stdlib generator (self-computed xref offsets, documented);
pypdf-generated encrypted fixture; nine frozen fixtures + checksums +
FIXTURES.md; hand-authored `golden_pdf_fixtures.py` (designed coordinates,
±2 pt tolerances) independent of extractor output.

### Task 5: Two-phase worker + parent extractor
Worker `--phase a|b`: A = structural extraction + atomic checkpoint;
B = per-page renders with per-page/aggregate limits and
`render_results.json`. Parent: checkpoint validation (all fields + sha256),
quarantine mapping, partial assembly (B crash ⇒ partial with surviving
derivatives only), single envelope build, staging until publication.
Stubbed-harness tests for every failure path; golden `pdf` tests for
structure, coordinates, tables, page kinds, active-content inventory,
determinism double-run.

### Task 6: Runtime + profile + e2e
Registry entry `application/pdf`; `FAMILY_BY_CONTENT_TYPE` update;
Profile v1 (pdf enabled/next) with v0 retained; e2e: ingest succeeded,
image-only partial, encrypted + malformed quarantines, rerun duplicate,
replay-after-delete, orphan injection with page renders; DS-001/002 green.

### Task 7: Verification + evidence
README; clean checkout with all four requirements files (base suite and
PDF-enabled); diff inspection; acceptance walkthrough incl. span→page→
coordinates→checksum provenance demo; report. No push.
