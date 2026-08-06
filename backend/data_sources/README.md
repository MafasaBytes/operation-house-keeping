# data_sources

The controlled boundary between external reality and the platform: acquire
evidence from external sources and extract its format-level structure, while
preserving the original payload, timing, identity, integrity, and provenance.
No engineering semantics are decided here — that belongs to the later
normalization and identity-resolution layer.

Status: **DS-001 complete** (local CSV snapshot slice). Design:
`docs/superpowers/specs/2026-08-06-ds001-data-sources-design.md`; stack
decision: `docs/adr/0001-ds001-python-pydantic-stack.md`.

## Layout

| Package | Responsibility |
| --- | --- |
| `contracts/` | Pydantic contract models + typed errors (the public surface) |
| `provenance/` | sha256 checksums, deterministic record ids, path redaction |
| `raw_store/` | write-once filesystem store (payloads, envelopes, runs, quarantine, extractions) |
| `catalog/` | stable source identities and definitions |
| `connectors/` | acquisition only; `LocalFileConnector` (read-only snapshot) |
| `extractors/` | format-aware, pre-semantic extraction; CSV today |
| `runtime/` | `IngestionRunner`: orchestration, quarantine, replay, health |
| `testing/fixtures/` | committed fixtures: `bom_valid.csv`, `bom_malformed.bin` |

## Verification (from a clean checkout)

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pytest          # 76 tests: unit, contract, end-to-end
```

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

## Known limitations

- One payload per source per run (`position` is always 0); multi-file and
  incremental sources are future work.
- The extractor registry is a hard-coded `text/csv` check in the runtime;
  a real registry should arrive with the second format family.
- The catalog is in-memory; source definitions live in code, not in a
  persisted catalog store.
- `source_native_id` is the file basename; no directory identity.
- No streaming, polling, cancellation, or checkpointing — snapshot only,
  which is all DS-001 requires.

## Next open question

Which source family does the intended application profile need next —
Excel with formula preservation, document/PDF with page provenance, or a
bounded read-only SQL/API snapshot? To be decided with the project owner
based on what DS-001 taught us (see spec §Known open question).
