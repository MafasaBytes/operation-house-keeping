# data_sources

The controlled boundary between external reality and the platform: acquire
evidence from external sources and extract its format-level structure, while
preserving the original payload, timing, identity, integrity, and provenance.
No engineering semantics are decided here — that belongs to the later
normalization and identity-resolution layer.

Status: **DS-001 complete** (CSV snapshot slice, owner-accepted),
**DS-002 complete** (neutral CAD / STEP slice, owner-accepted), and
**DS-003 complete** (PDF drawing/manual slice). Designs:
`docs/superpowers/specs/` (DS-001/DS-002/DS-003); stack decisions:
`docs/adr/` (ADR-0001 Python+Pydantic, ADR-0002 OCP/STEP, ADR-0003 PDF
toolchain).

## Layout

| Package | Responsibility |
| --- | --- |
| `contracts/` | Pydantic contract models + typed errors (the public surface) |
| `provenance/` | sha256 checksums, deterministic record/entity ids, path redaction |
| `raw_store/` | write-once filesystem store (payloads, envelopes, runs, quarantine, extraction envelopes, derivatives) |
| `catalog/` | stable source identities, definitions, Application Source Profile v0 |
| `connectors/` | acquisition only; `LocalFileConnector` (read-only snapshot) |
| `extractors/` | format detector; CSV extractor; STEP extractor (parent + isolated OCP worker); worker harness |
| `runtime/` | `IngestionRunner`: registry dispatch, staged publication, quarantine, replay, health |
| `testing/fixtures/` | committed frozen fixtures (see `testing/fixtures/FIXTURES.md`) |

## Verification (from a clean checkout)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pip install --require-hashes -r requirements-cad.txt
.venv/bin/python -m pip install --require-hashes -r requirements-pdf.txt
.venv/bin/python -m pytest    # full suite incl. cad- and pdf-marked e2e
```

Without an extra installed, its marked tests skip loudly and everything
else still runs; the connector `available` rung checks the extraction
dependency closure for each source's declared content type instead of
faking capability.

## PDF extraction semantics (DS-003)

- **Two-phase worker**: Phase A (structural) publishes an atomic
  completion checkpoint (schema version, record id, extractor identity +
  config fingerprint, manifest sha256) that the parent validates before
  Phase B (rendering) starts; an invalid or missing checkpoint quarantines
  the record, and a Phase B crash/timeout/limit yields an honest partial
  with only the page derivatives that actually completed. One final
  envelope, published derivatives-first.
- **Page/region provenance**: every item carries a canonical locator
  (CropBox-based frame, top-left origin, y-down, pdf points, 3-decimal
  rounding, source→canonical matrix) plus preserved source-native
  coordinates; identifiers are extractor-derived, never claimed as
  source-native; geometry tests are tolerance-based.
- **Honesty**: page_kind is a declared heuristic; eof_marker_count is a
  byte scan; inferred reading order carries basis/method/confidence and is
  never source truth; table candidates declare strategy and cell→span
  linking tolerance with optional row/column spans; document metadata is
  `declared_*`; drawing-region candidates are unsupported (vector
  inventory instead); image-only pages report `ocr_required` with no
  fabricated text (OCR/Level 4 deferred).
- **Hostile content**: JavaScript/actions/links/embedded files are
  inventoried read-only, bounded, and never executed, followed, or
  extracted; empty-password documents proceed with a warning;
  password-required documents quarantine
  (`EXTRACT_PDF_PASSWORD_REQUIRED`); structural limits quarantine, render
  limits produce partials with per-page `skipped_limit` coverage.
- **Determinism**: manifest JSON byte-stable (double-run tested); page
  render PNG byte-stability proven on the pinned platform/toolchain with
  dpi/colorspace/pdfium/pillow versions recorded per derivative;
  cross-platform claims are semantic only.

The end-to-end tests (`tests/data_sources/test_ingestion_runner.py`) cover:
valid ingestion with checksum + cell-level traceability; quarantine of the
malformed fixture with a redacted error while the raw payload is preserved;
idempotent re-run (duplicate detected, nothing new written except the run
report); replay from the store after the source file is deleted; failed-run
and health reporting; and the connector status ladder flipping `validated`
only after a successful accepting run.

## Connector status semantics

`declared → available → configured → connected → validated` are computed at
runtime with evidence (`ConnectorStatusReport`); a passing rung must state
its evidence, and `validated` requires a recorded successful run that
accepted records. A catalog entry is never treated as an implementation.

## Semantics worth knowing

- Raw payloads are persisted before extraction; nothing is overwritten in
  place, and identical re-acquisition is a detected duplicate
  (deterministic `record_id` from source, checksum, and position).
- `captured_at` is the acquisition clock; `source_observed_at` is the file
  modification time and provenance labels it `file_mtime` — it is *not* a
  true source-side observation timestamp.
- Extracted values stay strings; empty CSV fields become `None`; the header
  row is explicit configuration; ragged rows and duplicate headers become
  warnings, never silent repair.
- Persisted error messages are redacted: absolute paths are replaced with
  `<store>`/`<abs>`. (The redaction tests contain synthetic absolute paths
  as deliberately-rejected inputs.)

## STEP extraction semantics (DS-002)

- Every persisted extraction is an `ExtractionResult` envelope
  (`schema_version`, extractor identity, `succeeded | partial` outcome);
  quarantines are `QuarantineRecord`s, never results. Legacy DS-001 bare
  tables are wrapped on read.
- The OCP/OCCT toolchain runs only inside a worker subprocess — a
  **crash-isolation boundary, not a security sandbox** — with a
  checksum-verified temp payload copy, minimal environment, configurable
  time/size limits, and process-tree termination on timeout. Windows gap:
  no hard memory cap (timeout still applies).
- Extraction levels are declared honestly: supported 0–3, achieved per
  file per run. A valid assembly whose glTF derivative fails persists a
  trustworthy Levels 0–2 manifest as `partial` — quarantine is reserved
  for unparseable input or safety/resource failures.
- Identity honesty: `extractor_path_id` is an XCAF label path (toolchain
  identifier); `source_native_id` is only set with a stated verified
  basis — DS-002 never sets it. Instances model STEP usage occurrences
  (`parent_definition_ref`), not a flattened tree.
- Units are never defaulted: the declared unit context is parsed from the
  Part 21 data with its source representation; the pinned OCCT import
  unit (mm) is a separate `configuration_supplied` context.
- glTF traceability is an **index-keyed** node map (node names carry
  extractor path ids, verified and de-duplicated; names are never trusted
  as identity). The coordinate conversion (mm → metre, Z-up → Y-up) and
  tessellation parameters are recorded on the derivative.
- Determinism: manifest JSON is byte-stable for the same payload,
  extractor version, and config; glb byte stability is proven on the
  pinned platform/toolchain, with environment recorded — cross-platform
  comparison is semantic, not byte-level.
- Publication is staged: derivatives first, envelope last as the commit
  record; a failure in between leaves an orphan derivative that
  `find_orphan_derivatives()` detects and `purge_orphan_derivatives()`
  may safely delete (derivatives are recomputable; raw evidence never is).

## Known limitations

- One payload per source per run (`position` is always 0); multi-file and
  incremental sources are future work.
- The catalog is in-memory; source definitions live in code, not in a
  persisted catalog store.
- `source_native_id` on raw records is the file basename; no directory
  identity. On CAD entities it is always None (no verified STEP-entity
  mapping yet).
- STEP properties/colors/layers are not extracted; PMI/GD&T entities are
  detected (token scan) but never interpreted; flattened shared-subassembly
  glTF mapping is unsupported (duplicate nodes are left unmapped with a
  warning).
- No hard memory cap for the worker on Windows; `RLIMIT_AS` on Linux only.
- No streaming, polling, cancellation, or checkpointing — snapshot only.

## Next open question

Per Application Source Profile v0, which required family follows —
PDF drawing/manual (page-level provenance) or the operational
API/telemetry source — and how the DS-002 worker-isolation pattern
transfers to those parsers. To be decided with the project owner.
