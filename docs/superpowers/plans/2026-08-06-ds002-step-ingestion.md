# DS-002 STEP Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans
> to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax.

**Goal:** STEP assembly acquired through the existing boundary, extracted to
an honest Levels 0–3 manifest with a traceable glTF derivative, supporting
succeeded/partial/quarantined outcomes, deterministic ids and byte-stable
manifests, replayable from the store.

**Architecture / Tech stack:** See the spec
(`docs/superpowers/specs/2026-08-06-ds002-step-ingestion-design.md`) — the
spec is the authority on every model field, outcome rule, and amendment;
this plan sequences the work. ADR-0002 fixes the toolchain
(`cadquery-ocp==7.9.3.1.1`, hash-pinned, worker-isolated).

## Global Constraints

- All DS-001 global constraints continue to apply (read-only, redaction,
  UTC-aware timestamps, TDD, suite green at every commit, no push).
- OCP is imported only inside the worker subprocess and the fixture
  generator; never in core module import paths.
- `source_native_id` stays `None` unless a verified mapping exists.
- No silent unit defaults; unit provenance is always explicit.
- glTF traceability via index-keyed `node_map`; node names never used as
  identity.
- Derivatives published before the envelope; envelope is the commit record.
- Tests that need OCP carry marker `cad` and skip loudly when absent.

## Tasks

### Task 0: Spike (gate)
Install pinned OCP into `.venv`; script proves: STEPCAFControl read of a
generated assembly; XCAF traversal (definitions vs components, locations);
label renaming honored by RWGltf writer; glb JSON chunk parseable; two runs
byte-identical glb + stable structure on this platform. Record results in
the spec (Determinism section addendum). **Stop and report if any of:
OCP unusable on cp313/WSL; XCAF cannot expose assembly structure;
instance mapping impossible; no traceable derivative.**

### Task 1: Contract amendments + CAD contracts
Tests then models per spec §Contracts: `ExtractorIdentity`,
`ExtractionResult` (schema_version, outcome, discriminated result),
`PropertyValue`, `UnitContext`, `TransformSpec`, `PartDefinition`,
`ComponentInstance`, `DerivativeRecord`, `StepExtractionManifest`,
`SourceProfile`/`SourceProfileEntry` (planning fields only),
`IngestionRun.records_partial`, `QuarantineRecord.stage` widening,
new error codes. Commit.

### Task 2: Store — envelope migration, derivatives, staging, orphans
Tests then code: `put_extraction/get_extraction` over `ExtractionResult`
with legacy bare-`ExtractedTable` reader; content-addressed
`put_derivative_payload/get_derivative_payload`;
`find_orphan_derivatives()` + `purge_orphan_derivatives()` (payloads and
envelopes never GC'd); update DS-001 runner/store tests to the envelope.
Commit.

### Task 3: Format detector
Tests then code per spec §Format detection: BOM/whitespace-tolerant
`ISO-10303-21;` confirmation; high-confidence-only OLE-CFB and DWG
signatures (no vendor guessing); `unsupported_or_unknown_format` fallback;
`parse_declared_schemas()` from FILE_SCHEMA. Commit.

### Task 4: Worker harness
Tests with a fake worker script (happy/crash/timeout/oversize): controlled
temp materialization + checksum re-verify; no-shell, minimal-env spawn;
configurable limits (small in tests); process-tree termination
(`start_new_session` + group kill); scratch cleanup; `RLIMIT_AS` on Linux;
Windows memory-gap documented. Commit.

### Task 5: Fixtures + golden oracle
Committed generator (`generators/generate_step_assembly.py`, OCP) run once;
frozen `step_assembly.step` + `step_part_only.step`; hand-authored
`step_assembly_expected.py` (independent oracle — never generated);
`step_corrupted.step`, `native_cad_masquerade.step`; `FIXTURES.md` with
origin, parameters, toolchain, license, checksums, expected semantics.
Manual Part 21 inspection recorded. Commit.

### Task 6: STEP extractor
Worker module (OCP): XCAF read, traversal to definitions/instances with
`extractor_path_id`, deterministic ids, transforms (row-major, frames,
handedness, unit ref), unit contexts (declared-from-header via detector
output + configuration_supplied OCCT context), property passthrough,
label renaming to instance ids, glb write, node scan → index-keyed
node_map, scratch-dir manifest emission. Parent-side orchestration:
harness invocation, outcome mapping (succeeded/partial/quarantined),
golden-oracle unit tests (`cad` marker). Commit.

### Task 7: Runtime + e2e
Extractor registry by content type; staged publication (derivatives →
envelope last); partial handling with `records_partial`; failure-injection
test proving orphan detectability; full e2e set per spec §Test strategy
including double-extraction determinism, replay-after-delete, rerun,
quarantines, masquerade rejection. Commit.

### Task 8: Verification + evidence
Clean checkout + `requirements*.txt` incl. hash-pinned CAD extra; full
DS-001+DS-002 suites; diff inspection; acceptance-criteria walkthrough;
README updates (module README + FIXTURES); report commits, evidence,
levels achieved, partial behavior, limitations, next open question.
Commit. No push.
