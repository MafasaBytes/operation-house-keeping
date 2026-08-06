# DS-001 `data_sources` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** Prove the source boundary end-to-end: a local BOM CSV acquired
through a real connector, preserved as checksummed immutable raw records with
provenance, extracted with cell-level traceability, with honest quarantine,
duplicate, replay, run-report, health, and connector-status behavior.

**Architecture:** Layered small modules under `backend/data_sources/`
(contracts → provenance → raw_store → catalog/connectors → extractors →
runtime), each with tests written first. Persistence is a write-once
filesystem store. All orchestration lives in `IngestionRunner`.

**Tech Stack:** Python 3.13 (`.venv`), Pydantic v2, stdlib csv/hashlib/json,
pytest. See ADR-0001 and the spec
(`docs/superpowers/specs/2026-08-06-ds001-data-sources-design.md`) — the spec
is the authority on model fields and behaviors; this plan sequences the work.

## Global Constraints

- Read-only connectors; no writes to any external system.
- No secrets, credentials, or absolute paths in code, fixtures, errors, or
  committed files. `credential_reference` holds an opaque name only.
- Extracted values remain strings; no type/unit/header guessing;
  `header_row_index` is explicit configuration.
- Raw payloads are persisted before extraction and never overwritten.
- All timestamps are timezone-aware UTC; the runner's clock is injectable.
- No new runtime dependencies beyond `pydantic`.
- Every commit leaves the full test suite green: `.venv/bin/python -m pytest`.
- Commit after each task with a conventional message; do not push.

---

### Task 1: Project scaffolding
**Files:** `pyproject.toml`, `requirements.txt`, package `__init__.py` files,
`.gitignore` (add `var/`).
Configure pytest (`testpaths=["tests"]`, `pythonpath=["."]`). Verify
`pytest` collects zero tests and exits cleanly.

### Task 2: Contracts (tests: `tests/data_sources/test_contracts.py`)
Models and errors exactly as specified in the spec §Contracts. Test that:
records are frozen (mutation raises); invalid maturity/status literals are
rejected; `payload_checksum` must match `sha256:<64 hex>`;
`SourceDefinition` rejects a field named `credential` or a secret-looking
`configuration` key (`password`, `token`, `secret`, `api_key`);
`ConnectorStatusReport.validated.passed` requires non-empty evidence;
JSON round-trip (`model_dump_json` → `model_validate_json`) is lossless.

### Task 3: Provenance (tests: `tests/data_sources/test_provenance.py`)
`payload_checksum(data: bytes) -> str` (`sha256:<hex>`);
`derive_record_id(source_id, checksum, position: int) -> str` (32 hex chars,
deterministic, distinct across any argument change); `redact_text(text,
base_dir) -> str` replacing base-dir and absolute-path prefixes with
`<store>` / `<abs>`. Property-style tests for determinism and redaction.

### Task 4: Raw store (tests: `tests/data_sources/test_raw_store.py`)
`FilesystemRawStore(base_dir)` with: `put_payload(bytes) -> checksum` (write
once, content-addressed, idempotent for identical bytes);
`put_envelope(RawRecord)` (write once; identical re-put is a detected
duplicate → returns `False`; different content under same id raises
`StoreIntegrityError`); same write-once semantics for runs, quarantine, and
extracted tables; `iter_accepted_envelopes(source_id)`;
`get_payload(reference) -> bytes` verifying checksum on read. All under
`tmp_path`.

### Task 5: Catalog + LocalFileConnector
(tests: `tests/data_sources/test_catalog.py`, `test_local_file_connector.py`)
`InMemorySourceCatalog`: `register`, `get` (unknown id raises), `enabled`
filtering, no silent re-register of a different definition under the same id.
`LocalFileConnector`: class-level `MANIFEST` (experimental maturity, snapshot
mode, read-only, csv format); `probe(source) -> StatusCheck` (file exists +
readable); `acquire(source) -> Acquisition {payload: bytes,
source_native_id: relative path, source_observed_at: mtime as aware UTC}`;
missing file → `AcquisitionError` with redacted message;
`status_report(source, store) -> ConnectorStatusReport` computing all five
rungs honestly (`validated` only if a successful validation run for this
source exists in the store).

### Task 6: CSV extractor (tests: `tests/data_sources/test_csv_extractor.py`)
`extract_csv(payload: bytes, raw_record_id, config: CsvExtractionConfig
{encoding='utf-8', delimiter=',', header_row_index=0}) -> ExtractedTable`.
Tests: header taken from configured row and recorded; every cell carries
raw_record_id + physical_row_index + column_index + column_name; values stay
strings; empty field → `None` with a table-level note distinguishing empty
from absent; quoted commas survive; ragged rows produce warnings, not
silence; undecodable bytes raise `ExtractionError`
(code `EXTRACT_UNDECODABLE`); output JSON round-trips.

### Task 7: Fixtures + runtime
(tests: `tests/data_sources/test_ingestion_runner.py` — end-to-end)
Fixtures per spec §Fixtures in `backend/data_sources/testing/fixtures/`.
`IngestionRunner(catalog, store, connectors, clock)`:
`run(source_id) -> IngestionRun` implementing spec §Runtime flow, and
`replay(source_id) -> list[ExtractedTable]`. E2E tests:
1. valid fixture → run `succeeded`, seen=1 accepted=1, payload+envelope+
   extracted persisted, checksum verifies, cells trace to file rows/cols;
2. malformed fixture → raw preserved, quarantine record with redacted
   message (no absolute path), run `completed_with_quarantine`, health
   `degraded`;
3. re-run valid → `records_duplicate`=1, accepted=0, no new files;
4. replay equals original extraction without touching the source path
   (delete source file first to prove it);
5. disabled/unknown source and missing file → honest failures, health
   `failed`, other sources unaffected.

### Task 8: Verification + evidence
Run full suite; walk CLAUDE.md DS-001 acceptance criteria one by one;
write `backend/data_sources/README.md` (purpose, verification commands,
connector status semantics, known limitations, next open question);
final commit.

## Self-review notes

Spec coverage checked against CLAUDE.md's 12 DS-001 requirements: reqs 1–12
map to Tasks 5, 5/6, 2/7, 4, 2/5, 4, 4/7, 7, 6/7, 4/7, 5, 6/7 respectively.
Type names used across tasks are defined in Task 2 (contracts) or the spec.
