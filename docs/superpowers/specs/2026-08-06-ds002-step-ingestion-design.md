# DS-002 Neutral CAD (STEP) Ingestion & Extraction — Design

Date: 2026-08-06
Status: Approved by project owner with mandatory amendments (incorporated
below). No further design round required unless the spike invalidates the
toolchain or assembly-traceability assumptions.

## What this slice validates

That the platform can acquire and immutably preserve a STEP assembly through
the existing DS-001 source boundary, extract assembly structure with honest
extraction-level declarations (targeting Levels 0–3), produce a traceable
glTF visualization derivative, support partial extraction outcomes, and
replay everything from the raw store after the external source is removed.

Out of scope (unchanged from the approved brief): native CATIA/NX/
SolidWorks/Inventor/AutoCAD extraction; PMI/GD&T interpretation; functional
or causal inference; BOM↔CAD identity reconciliation; contact detection as
engineering truth; a production 3D viewer; cloud/distributed infrastructure.

## Application Source Profile v0

Planning state is separate from runtime state. `SourceProfileEntry` carries
planning fields only:

```text
source_family
requirement:        required | optional
roadmap_stage:      validated | next | later | not_started
enabled_for_profile: bool
justification
```

Profile v0: CSV BOM (required, validated, enabled); STEP assembly (required,
next, enabled); PDF drawing/manual (required, later, disabled); one
operational API/telemetry source (required, later, disabled); Excel, SQL,
additional APIs, native CAD, other sensor protocols (optional, not_started,
disabled). Connector availability, configuration, connectivity, health, and
validation evidence remain exclusively in the operational models
(`ConnectorStatusReport`, `SourceHealth`, runs) — the profile never claims
runtime capability.

## Architecture

```
LocalFileConnector (unchanged, DS-001)
  → raw store: payload + envelope persisted first (unchanged)
  → format detector (pure Python, conservative)
  → StepExtractor
      parent side: controlled temp materialization, checksum re-verify,
                   worker invocation, staged publication
      worker side: isolated subprocess (OCP/OCCT), XCAF traversal,
                   manifest + glb emission to a scratch dir
  → runtime: extractor registry, outcome handling
             (succeeded | partial | quarantined), staged publication
  → replay: re-extraction from stored payload only
```

Boundary rules:

- The connector layer is format-blind and unchanged.
- The extractor never accesses the raw store directly. The runtime
  materializes a controlled temporary copy of the payload, re-verifies its
  checksum against the envelope before parsing, and hands the worker only
  that sanitized temp path.
- The worker writes only to its scratch directory. The runtime publishes
  content-addressed derivatives first and writes the extraction-result
  envelope last as the commit record.

## Toolchain (see ADR-0002)

`cadquery-ocp==7.9.3.1.1` (pip wheels, cp310–cp314, win/linux/mac), used
only inside the worker. Installed via `requirements-cad.txt` with hashes
(`pip install --require-hashes`). No source distribution exists, so on
platforms without a wheel the `available` status rung fails honestly; no
fallback is faked. Licensing recorded in ADR-0002 and
`THIRD_PARTY_NOTICES.md` (bindings Apache-2.0; OCCT LGPL-2.1 with the Open
CASCADE exception, including redistribution obligations).

## Contracts

### Extraction result envelope (amends DS-001)

```text
ExtractionResult
  schema_version: 1
  raw_record_id
  extractor: ExtractorIdentity
  outcome: succeeded | partial
  warnings: [str]           # result-level, e.g. derivative failure
  result: CsvTableResult | StepManifestResult   (discriminated by `kind`)
```

Quarantined extractions produce a `QuarantineRecord`, never an
`ExtractionResult`. DS-001 compatibility: the store's read path detects
legacy bare `ExtractedTable` JSON (no `schema_version` key) and wraps it as
a schema_version-1 `succeeded` result with extractor identity
`csv_extractor/legacy` — a documented development-time legacy reader; no
production data exists.

`ExtractorIdentity`: `{name, version, toolchain, config_fingerprint}`.
Stamped on every extraction output, including CSV from now on.

`IngestionRun` gains `records_partial` (default 0; old JSON remains valid).
`QuarantineRecord.stage` widens to `format_detection | extraction`.

### Identity fields (amended)

An XCAF label path is a toolchain identifier, not a STEP entity number.
Every extracted object carries:

- `extractor_path_id` — the XCAF/OCAF label entry (e.g. `0:1:1:2:1`);
  always present; meaningful only relative to the extractor identity.
- `source_native_id` — optional; populated **only** when a verified
  STEP-to-XCAF mapping exists. DS-002 does not implement that mapping, so
  it is always `None` here, and the manifest's limitations say so.
- `raw_locator` — optional source byte/record locator when defensibly
  available; `None` in DS-002.

`#123`-style identifiers are never emitted unless the mapping is proven.

`declared_schemas: list[str]` — parsed from the Part 21 `FILE_SCHEMA`
header record (a file may declare several or long schema identifiers).
Parsed by the pure-Python detector, not trusted from the toolchain.

### CAD models

```text
PropertyValue
  name                      # source-native property name
  value: str                # normalized textual value
  value_type: string | integer | real | boolean | enumeration | unknown
  unit: str | None          # only when supplied by the source
  raw_representation: str   # exactly as seen
  locator: str | None       # provenance locator when available

UnitContext
  context_id
  length_unit: str | None
  angle_unit: str | None
  provenance: explicitly_declared | verified_context |
              configuration_supplied | unavailable
  source_representation: str | None
```

A missing STEP unit is `unavailable` — never silently defaulted to
millimetres. The OCCT import unit (a reader configuration) is recorded as a
separate `configuration_supplied` context; the two are never merged.

```text
TransformSpec
  matrix: [16 floats]
  layout: row_major_4x4
  source_frame / destination_frame: str
  handedness: right_handed | left_handed
  length_unit_ref: UnitContext.context_id    # interpretation of translations

PartDefinition
  definition_id             # deterministic platform id
  extractor_path_id
  source_native_id: None    # (DS-002; see identity rules)
  raw_locator: None
  name: str | None
  properties: [PropertyValue]
  unit_context_ref

ComponentInstance
  instance_id               # deterministic platform id
  definition_ref
  parent_instance_ref: str | None
  occurrence_name: str | None
  extractor_path_id
  source_native_id: None
  raw_locator: None
  transform: TransformSpec

DerivativeRecord
  derivative_id
  raw_record_id
  kind: visualization_gltf
  media_type: model/gltf-binary
  payload_reference          # content-addressed in the store
  checksum
  generator: ExtractorIdentity
  tessellation: {linear_deflection, angular_deflection, relative}
  coordinate_conversion: {source_frame, target_frame, target_length_unit,
                          converter}
  node_map: {gltf_node_index -> instance_id}   # sidecar map, index-keyed
  environment: {platform, architecture, occt_version}

StepExtractionManifest
  raw_record_id
  extractor: ExtractorIdentity
  declared_schemas: [str]
  unit_contexts: [UnitContext]
  definitions: [PartDefinition]
  instances: [ComponentInstance]
  root_instance_ids: [str]
  derivatives: [DerivativeRecord]
  levels_supported: [0,1,2,3]
  levels_achieved: [int]
  unsupported_features: [str]
  lossy_conversions: [str]
  warnings: [str]
```

### glTF traceability (amended)

Node **names are not used for identity**. Before export, each XCAF
component label's name is set to the platform `instance_id` (unique by
construction); after export, the glb JSON chunk is parsed and a sidecar
`node_map` from **glTF node index** to `instance_id` is built and verified
(bijective over mapped instances; duplicates are an extraction error).
Original occurrence names are preserved in the manifest; the renaming is
recorded under `lossy_conversions`. The manifest records the
coordinate-system conversion applied by the writer (CAD frame → glTF
Y-up right-handed, metres) in `DerivativeRecord.coordinate_conversion`.

## Determinism (amended)

Semantic determinism is separated from byte determinism:

- **Manifest JSON**: canonical, byte-stable for the same input bytes,
  extractor version, and configuration. Acceptance criterion, tested by
  double extraction.
- **GLB**: actual checksum recorded for every produced artifact; byte
  stability tested on the same pinned platform/toolchain only.
  Cross-platform (Windows vs WSL) comparison is over **semantic
  invariants** (node count, node_map shape, mesh count, total triangle
  count within tolerance) where both platforms are available — not byte
  identity. Platform, architecture, OCCT version, and tessellation
  parameters are recorded in the derivative. If universal byte identity is
  ever required, the worker runtime gets standardized; no fragile
  post-processing to hide platform differences.

Deterministic platform ids: `definition_id`/`instance_id` derive from
`(raw_record_id, extractor version, extractor_path_id)` so the same payload
and toolchain always yield the same ids.

### Spike results (2026-08-06, Task 0 — gate PASSED)

Environment: WSL2 Ubuntu x86_64, CPython 3.13.11, `cadquery-ocp==7.9.3.1.1`
(manylinux_2_31 wheel). Findings:

- `STEPCAFControl_Writer/Reader` round-trips a two-level assembly with a
  shared part definition (`bolt-m6` referenced by two component instances)
  and preserves names and designed translations exactly.
- Renaming XCAF component labels before export is honored by
  `RWGltf_CafWriter`: glb node names carry the synthetic instance ids, and
  the glb JSON chunk yields a clean node-index scan for the sidecar map.
- Two independent read→rename→mesh(0.1/0.5)→export runs produced
  **byte-identical glb** (sha256 `ec2a9460…`) on this platform.
- `FILE_SCHEMA` is regex-parseable from the Part 21 header
  (`AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }` for the AP214IS writer
  configuration).
- STEP output itself embeds a `FILE_NAME` timestamp, confirming the frozen-
  fixture strategy (the generator cannot be re-run to reproduce identical
  bytes; the frozen file is canonical).

## Extraction outcomes (amended)

```text
Assembly extracted, derivative generated        → succeeded, Levels 0–3
Assembly extracted, derivative generation failed → partial, Levels 0–2,
                                                   warning names the failure
STEP parse failed                                → quarantined
Worker crashed / exceeded limits                 → quarantined
Optional metadata missing                        → succeeded or partial per
                                                   declared levels, never
                                                   automatic quarantine
```

Quarantine is reserved for "no trustworthy structured extraction is
possible" or a safety/resource failure that makes results unreliable. A
trustworthy Levels 0–2 manifest with a failed derivative is `partial`, is
persisted, and counts in `records_partial`.

## Worker isolation (amended wording)

The subprocess is a **crash-isolation boundary, not a complete security
sandbox**. The runtime: materializes a controlled temp copy with a
sanitized filename (`payload.step`); re-verifies the checksum before
parsing; invokes the worker without a shell; passes a minimal environment
(no secrets); enforces configurable limits (defaults 120 s wall clock,
100 MB payload; smaller in tests); terminates the full process tree on
timeout (`start_new_session` + process-group kill on POSIX); cleans all
temp files; and applies `RLIMIT_AS` on Linux. **Windows gap**: no hard
memory cap is enforced (no Job-object management in this slice) —
documented limitation, timeout still applies.

## Format detection (amended)

Conservative three-way outcome:

- `confirmed_step`: declared media type / extension consistent AND the
  payload begins (tolerating UTF-8 BOM and leading whitespace) with the
  `ISO-10303-21;` signature.
- `unsupported_native_cad`: only on high-confidence signatures — OLE
  compound-file magic (`D0 CF 11 E0 A1 B1 1A E1`, reported as
  `ole_compound_container`, no vendor guess) or DWG (`AC10..` version
  prefix). The message states that native CAD requires a vendor pipeline.
- `unsupported_or_unknown_format`: everything else. No guessing.

Detection failures quarantine with `stage=format_detection`.

## Failure and threat model

Untrusted STEP into a large C++ parser → worker isolation + limits as
above; crash/timeout → `EXTRACT_WORKER_CRASHED` / `EXTRACT_WORKER_TIMEOUT`
quarantine with raw preserved. Entity-explosion → the same limits. Strings
inside STEP are data: never used as paths, redacted in persisted errors.
STEP has no execution surface; the glb contains no scripts. Store
integrity: derivatives are published content-addressed **before** the
envelope; a failure between the two leaves an orphan derivative that
`find_orphan_derivatives()` detects and `purge_orphan_derivatives()` may
safely delete (derivatives are recomputable; envelopes and payloads are
never garbage-collected). A manifest can never reference a missing
derivative because the derivative is published first.

## Fixtures and the independent oracle (amended)

- `step_assembly.step` — generated **once** by a committed generator script
  (OCP) and frozen; the generator is documentation, the frozen file is the
  fixture. Small deterministic assembly: root `demo-unit` → subassembly
  `bracket-sub` (2 × `bolt-m6`, 1 × `bracket-plate`) + `base-plate`, simple
  box/cylinder solids, explicit millimetre units, distinct designed
  transforms.
- **Independent oracle**: the golden expectations
  (`step_assembly_expected.py`: product names, tree shape, instance count,
  designed translations) are hand-authored from the intended assembly
  design, not emitted by the generator; the frozen STEP file's structure is
  additionally inspected by eye (Part 21 text) at freeze time.
  `FIXTURES.md` records origin, generation parameters, toolchain version,
  license (project license; authored in-repo), checksum, and expected
  semantics.
- `step_part_only.step` — single part, no assembly.
- `step_corrupted.step` — valid header, truncated DATA section.
- `native_cad_masquerade.step` — OLE CFB magic under a `.step` name.
- A fake slow/crashing worker script for harness tests (no OCP required).

## Test strategy

Unit: detector, contracts, id determinism, store staging/orphans, harness
(fake worker: happy, crash, timeout, oversized payload). Golden-oracle
tests: manifest vs hand-authored expectations. E2E (marker `cad`, skipped
loudly without the extra installed; required for DS-002 acceptance):
ingest → manifest + glb persisted, node_map verified against glb bytes;
double-extraction manifest byte-stability + same-platform glb checksum
stability; partial outcome via injected derivative failure; replay after
source deletion; idempotent rerun; corrupted quarantine; masquerade
rejection; DS-001 suite stays green throughout.

## Acceptance criteria

All bullets from the approved brief plus the amendments: partial outcomes
persist trustworthy L0–2 manifests; identity fields never overclaim;
node_map is index-keyed and verified; unit provenance never defaults;
manifest byte-determinism proven; glb checksums recorded with environment;
staged publication proven by failure-injection test; clean-checkout run
with `requirements-cad.txt` (hash-pinned) green; limitations and next open
question recorded.

## Known open question for after DS-002

Which required source family follows per Profile v0 — PDF drawing/manual
(page-level provenance) or the operational API/telemetry source — and what
DS-002's worker-isolation pattern teaches us for those.
