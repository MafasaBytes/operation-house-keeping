# DS-001 `data_sources` First Vertical Slice — Design

Date: 2026-08-06
Status: Approved by project owner (Pydantic contracts, filesystem raw store,
stdlib CSV extraction, pytest, per-task commits).

## What this slice validates

That the platform can acquire evidence from one deterministic local source
through a real connector and format extractor, while preserving the original
payload, timing, identity, integrity, and provenance — and that failure,
duplication, and replay behave honestly. See `CLAUDE.md` → "First Vertical
Slice: DS-001" for the twelve requirements and the acceptance criteria; this
design does not restate them.

## Stack

- Python 3.13 (Linux `.venv`; a Windows `venv/` also exists but is not used
  for development or CI).
- Pydantic v2 for contract models (owner-selected over stdlib dataclasses).
- Stdlib `csv`, `hashlib`, `json`, `pathlib`, `datetime` for mechanics.
- pytest for unit, contract, and end-to-end tests.
- No other runtime dependencies. See ADR-0001.

## Module layout

```
backend/data_sources/
  contracts/    # Pydantic models + typed errors (the module's public contract)
  provenance/   # checksums, deterministic ids, redaction
  raw_store/    # filesystem raw store
  catalog/      # in-memory source catalog
  connectors/   # LocalFileConnector
  extractors/   # CSV extractor
  runtime/      # IngestionRunner orchestration
  testing/      # committed fixtures (valid + malformed BOM CSV)
tests/data_sources/   # all tests, mirroring the module layout
```

`data_sources/notebooks/` at the repository root is the owner's exploration
area and is not part of the module.

## Contracts (Pydantic v2, `frozen=True` where the value is a record)

- **SourceDefinition** — `source_id`, `display_name`, `source_kind`,
  `connector_type`, `configuration` (non-secret), `credential_reference`
  (opaque name only; never a secret value), `declared_content_types`,
  `enabled`.
- **ConnectorManifest** — `connector_type`, `source_families`,
  `supported_formats_or_protocols`, `acquisition_modes`,
  `supported_extraction_levels`, `read_only`, `incremental_read_support`,
  `required_dependencies`, `maturity` (`planned | experimental | validated`),
  `known_limitations`. LocalFileConnector ships as `experimental`; nothing in
  DS-001 is allowed to claim `validated` maturity until the acceptance tests
  pass and the owner confirms.
- **ConnectorStatusReport** — the five-rung ladder as explicit fields:
  `declared`, `available`, `configured`, `connected`, `validated`, each a
  `StatusCheck {passed: bool, evidence: str}`. Computed at runtime, never
  hard-coded true.
- **RawRecord** — envelope per acquired payload: `record_id` (deterministic),
  `source_id`, `source_native_id` (relative file path), `ingestion_run_id`,
  `captured_at` (acquisition clock, UTC), `source_observed_at` (file mtime,
  UTC, explicitly labeled as mtime-derived in provenance), `content_type`,
  `payload_checksum` (`sha256:<hex>`), `immutable_payload_reference`
  (checksum-addressed store key; payload bytes are stored once, not embedded
  in the envelope), `provenance` (acquisition context), `quality_flags`.
- **IngestionRun** — `run_id`, `source_id`, `started_at`, `finished_at`,
  `status` (`succeeded | completed_with_quarantine | failed`),
  `records_seen`, `records_accepted`, `records_duplicate`,
  `records_quarantined`, `error_summary`.
- **SourceHealth** — `source_id`, `status` (`ok | degraded | failed |
  unknown`), `checked_at`, `last_success_at`, `last_record_at`,
  `diagnostic_code`.
- **QuarantineRecord** — `record_id` of the preserved raw record,
  `stage` (`extraction`), `error_code`, `redacted_message`, `quarantined_at`.
- **ExtractedTable / ExtractedRow / ExtractedCell** — extraction output.
  Every cell carries `raw_record_id`, `physical_row_index` (0-based line in
  the file, header included), `column_index`, `column_name`, and its value
  **as a string** (or `None` for an empty field). No type coercion, no unit
  guessing, no header guessing: the header row index is explicit
  configuration (`header_row_index`, default 0 but always recorded).
- **Typed errors** — `DataSourceError` base with `error_code`;
  `AcquisitionError`, `ExtractionError`, `DuplicatePayloadError` (internal),
  `StoreIntegrityError`. Messages must already be redacted when raised
  outward (no absolute paths, no secrets).

## Key behaviors

**Determinism / idempotency.** `record_id = sha256(source_id ‖
payload_checksum ‖ position)[:32]`, so re-acquiring identical content yields
the identical id. The store detects the existing envelope and the run counts
it as `records_duplicate`, not a new acceptance. Changed file content ⇒ new
checksum ⇒ new record (an update is new evidence, never an overwrite).

**Raw-first preservation.** Acquisition persists payload + envelope *before*
extraction is attempted. A malformed payload is still preserved; only its
extraction is quarantined. Nothing is ever lost or overwritten in place
(write-once store; attempting to overwrite an envelope with different content
raises `StoreIntegrityError`).

**Raw store layout** (base dir configurable; default `var/raw_store/`,
gitignored):

```
payloads/<sha256-hex>            # original bytes, content-addressed
envelopes/<record_id>.json       # RawRecord as JSON
runs/<run_id>.json               # IngestionRun as JSON
quarantine/<record_id>.json      # QuarantineRecord as JSON
extracted/<record_id>.json       # ExtractedTable as JSON (traceable derivative)
```

**Runtime flow.** `IngestionRunner.run(source_id)`: look up enabled source in
catalog → connector probe/acquire (read-only snapshot) → checksum → duplicate
check → persist payload + envelope → extract → persist extraction or
quarantine → write run report → derive health. One source's failure can never
touch another source's records (store paths are content/record addressed; the
runner isolates exceptions per record and per run). The runner takes an
injectable `clock` (callable returning aware-UTC `datetime`) so tests are
deterministic.

**Replay.** `replay(source_id)` iterates accepted envelopes from the store,
loads payloads by reference, re-runs extraction deterministically, and
returns results without re-acquiring from the external source. Test asserts
replay output equals original extraction output.

**Redaction.** A `redact_path` helper replaces the store base dir and any
absolute path prefix with placeholders (`<store>`, `<abs>`), applied to all
outward error messages and quarantine records. Tests assert no absolute path
appears in persisted errors.

**Health.** Derived from the latest run: `ok` (succeeded),
`degraded` (completed_with_quarantine), `failed` (failed), `unknown` (never
run). `diagnostic_code` carries the dominant error code if any.

## Fixtures

- `bom_valid.csv` — ~6-row bill-of-materials-like table (item number, name,
  quantity, unit, parent) with one quoted comma value and one empty cell, so
  quoting and absent-vs-empty behavior are exercised. Relative paths only; no
  secrets; units appear only as an explicit column, never guessed.
- `bom_malformed.bin` — bytes that are not decodable as UTF-8 (extraction
  must quarantine with error code `EXTRACT_UNDECODABLE`).

## Error handling summary

| Failure | Behavior |
| --- | --- |
| Source file missing/unreadable | `AcquisitionError`, run `failed`, health `failed`, no partial records |
| Payload undecodable / not CSV | Raw record preserved; `QuarantineRecord` with redacted error; run `completed_with_quarantine` |
| Ragged row (wrong column count) | Row-level warning recorded in `ExtractedTable.warnings`; cells still traceable; not silently dropped |
| Re-run, identical content | Counted `records_duplicate`; no new envelope; run `succeeded` |
| Envelope collision with different content | `StoreIntegrityError` (never overwrite) |

## Testing strategy

- Unit tests per module (contracts validation, checksum/id determinism,
  store write-once + duplicate + replay iteration, connector probe/acquire,
  extractor provenance and failure modes).
- Contract test: connector conforms to the acquisition protocol and its
  status ladder cannot report `validated` without recorded evidence.
- End-to-end tests through `IngestionRunner`: valid ingest, quarantine,
  idempotent re-run, replay equality.
- All persistence tests run under pytest `tmp_path`; committed fixtures
  contain no absolute paths or secrets.

## Out of scope (unchanged from CLAUDE.md)

No normalization, identity resolution, graph building, streaming, Excel/PDF/
CAD/API/DB connectors, HTTP API, broker, or cloud services. `records_seen`
semantics beyond single-file snapshots (multi-artifact sources) are deferred.

## Known open question for after DS-001

Which source family the intended application profile needs next (Excel with
formula preservation vs. document/PDF vs. a bounded SQL/API snapshot), to be
chosen with the owner based on what DS-001 teaches us.
