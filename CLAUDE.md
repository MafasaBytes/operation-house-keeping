# Project Guidance for Claude

## Mission

We are building the backend foundation for a system that can maintain a living,
hierarchical, stateful, and constraint-aware representation of an engineered
system.

The intended product is not a document chatbot, a conventional digital twin, or
an information library. It should eventually be able to answer questions such
as:

- What exists in this system, and how is it connected?
- What is the current state of this particular system?
- Why might the system be behaving this way?
- What is the next best measurement or test?
- What would be affected if this component, parameter, or software version changed?
- What is the smallest valid set of changes needed to reach a desired state?
- Which conclusions are observed, calculated, inferred, assumed, or unknown?

The architecture is **model-centric, not LLM-centric**. An LLM may help extract,
query, explain, and propose changes, but it is never the source of engineering
truth. Deterministic code, explicit models, constraints, evidence, and provenance
must remain authoritative.

## Status (added 2026-08-07 — historical guidance below is preserved)

Application delivery update (2026-09-17): finite-world admissibility enforcement
is [owner accepted](docs/superpowers/reports/2026-09-17-maintained-admissibility-final-owner-acceptance.md)
at `15f773ba9c675b553283669fbf72c76407c0eabd`. The explicit governed route
enforces declared membership before numerical evaluation; denied permission blocks
projection even when the gate completes successfully. Exact local-attestation,
declaration, adoption and build references support 23-row review and persistent
verification/recomputing replay. Local attestation is not authenticated identity
or physical truth; historical replay is not current adoption. The finite gate
does not implement general correlated-support reasoning or discover assumptions.
Legacy invocation remains available without this enforcement guarantee.
The [current seven-objective reconciliation](docs/superpowers/reports/2026-09-17-post-admissibility-reconciliation.md)
supersedes the publication/status assessment below, not its historical evidence.
C remains unresolved; IN-001 and CI-001 remain open and unselected.

Earlier application delivery (2026-09-16): the maintained
[bounded decision workflow](applications/bounded_decision_workflow/README.md) is
[owner accepted through S1–S7](docs/superpowers/reports/2026-09-16-bounded-decision-workflow-final-owner-acceptance.md)
at `64f4389b6d93484339afa29cbb7f7f21f6ef2758`. Its local evaluate/verify/replay
commands provide public input admission, rational one-step projection,
target/feasibility assessment, tied finite-set action selection, fixed named
dependency review, retention and recomputing replay. Hypotheses, action/effect
premises and policy are supplied within the fixed supported profile. This does
not deliver generated hypotheses/actions/tests, next-test ranking, arbitrary-law
evaluation, multi-step planning, global optimality or causal truth.
Historical disposable experiments are evidence within their accepted scope,
not maintained application entry points. The
[post-delivery objective and integration report](docs/superpowers/reports/2026-09-16-bounded-decision-workflow-post-delivery-reconciliation.md)
supersedes older general statements of application absence; it leaves the
backend contracts and ADR frontier unchanged. IN-001 and CI-001 remain open
and unselected. No successor, integration, push or artifact cleanup is authorized
by this documentation checkpoint.

The "Current Phase" and DS-001 sections below are the original milestone
record, retained as historical guidance. Their sentence "Only `data_sources`
is currently in scope" is superseded by this Status section. All other general
boundaries remain binding.

The owner-accepted milestone sequence is DS-001, DS-002, DS-003, DS-004,
TS-001, IB-001, MK-001, VM-001, VS-001, SN-001, ES-001, CN-001, PT-001,
VP-001, BH-001, ST-001, ST-002, FL-001, EA-001, TA-001, FM-001, and FC-001.
FL-001, EA-001, TA-001, FM-001, and FC-001 are complete and owner accepted.
FM-001's corrected design and repaired Slice A are owner accepted at exact tested implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`; Slice B and the complete FM-001
milestone are owner accepted at exact tested implementation
`4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`.
FL-001 is adversarially reviewed; EA-001 is adversarially repaired; TA-001 is
adversarially hardened. All completed milestones are full-suite and
dual-clean-checkout verified.
TA-001 Slice A is owner accepted at exact tested implementation
`76738ac0d098eb59b0fec4f6970aa862528647d9`. Slice B adversarial hardening is
implemented and verified at exact tested implementation
`2ec18f7234273dba98098d268df4568d5cc84d85`. TA-001 complete, owner accepted,
adversarially hardened, and dual-clean-checkout verified.
Accepted designs and decisions are indexed in
`README.md`, `docs/superpowers/specs/`, and `docs/adr/`.

Also accepted: ES-001, adversarially reviewed, repaired, and
dual-clean-checkout verified. CN-001 is owner accepted. These explicit status
sentences are retained for the accepted documentation guard; the complete
sequence above is authoritative for current milestone status.

The accepted backend comprises `data_sources`, `temporal_state`,
`system_identity`, `identity_binding`, `model_kernel`, `structural_evidence`,
`model_state`, `observation_compatibility`, `source_interpretation`,
`semantic_compatibility`, `constraint_evaluation`, `behavior_evaluation`, and
`state_classification`, plus the read-only `evidence_assurance` and
`evidence_alignment` composition layers, plus the pure read-only
`transition_assessment` leaf. Lower evidence and identity packages do not
import upper model or evaluation packages. Read-only composition layers own no
authoritative ledger.

The authoritative synthetic demo model contains exactly 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
including one FRG, one FLD, zero FLW, and zero TRG/TRD/TRW. Source evidence
and observations, model declarations, evaluation/classification, transition
or flow declarations, and accountable physical occurrence remain distinct.
ST-002 declares transition identity and possibility but performs no transition
assessment or occurrence assertion. FL-001 declares one synthetic logical
directed flow but performs no measurement assessment and asserts no physical
flow occurrence.

TA-001 Slice A implements `backend.transition_assessment` as a pure, read-only
leaf composition over carried public transition-declaration,
state-classification, and evidence-alignment results. Its fixed admission
limits are 134,217,728 canonical-request bytes, 200,000 reconstructed nodes,
and nesting depth 128. Every governing observed condition requires a supplied,
matched expected fingerprint. The design adds no facade, demonstration,
occurrence or non-occurrence claim, store, ledger, identity, or persistence.
The documentation checkpoint is owner accepted at
`a4754d8659c08af8fb86bf18bd3c5aac4ea355fe`. TA-001 Slice A is separately
owner accepted at exact tested implementation
`76738ac0d098eb59b0fec4f6970aa862528647d9` for the exact contracts, bounded
preflight, pure derivation, authoritative reconstruction, tests, and
documentation in the accepted design. Slice B adversarial hardening and final
verification are implemented at
`2ec18f7234273dba98098d268df4568d5cc84d85`; final milestone acceptance is
recorded in the owner-acceptance report. TA-001 remains a pure, read-only leaf
with no occurrence claim, durable identity, ledger, store, facade,
demonstration, or second consumer.

FM-001 is complete and owner accepted. Its repaired Slice A remains accepted
at `6210d3c250b96f54b764a365cb0a3a988d9bf9f6`; its exact 225-name public
surface and five read-only Slice B query responsibilities are accepted at
tested implementation `4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`.
There is no Slice C or demonstration. The authoritative model retains zero
FMA/FMW records. The [FA feasibility owner decision](docs/superpowers/reports/2026-09-09-fa001-feasibility-owner-decision.md)
accepts the proposal and challenger audit because they correctly reject
baseline-only FA implementation; its earlier FA deferral is superseded by
the final FC acceptance and cancellation below. FC-001 — Explicit Flow Operating
Criterion Declaration — is complete, owner accepted, adversarially hardened, and dual-clean-checkout
verified at exact tested implementation `9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`. See
[ADR-0022](docs/adr/0022-explicit-flow-operating-criterion.md) and the
[design approval](docs/superpowers/reports/2026-09-09-fc001-final-design-owner-approval.md).
FC establishes evidence-bearing designation and applicability of one operating
criterion for an exact FM effective body; it does not evaluate the criterion or
establish physical flow, occurrence, causality, safety, or operating health.
The direct public-result proof rejects substitution of satisfied ungoverned B
for violated governing A, and its satisfied-A twin passes. FA-001 is cancelled
at this checkpoint. Reconsideration requires a new owner-approved proposal
demonstrating a concrete integrity attack that existing public-result validation
cannot prevent; convenience or aggregation preference is insufficient.
ADR-0022 is the latest accepted ADR. No successor milestone has been approved;
ADR-0023 remains absent, unallocated, and unreserved. The backend architectural frontier is
the owner-accepted [post-FC objective-gap reconciliation](docs/superpowers/reports/2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md),
which supersedes inherited roadmap ordering. CS-001 was investigated and is
closed without implementation as commissioning application policy, not deferred
architecture; the [CS-001 owner decision](docs/superpowers/reports/2026-09-10-cs001-application-policy-owner-decision.md)
accepts the challenger verdict and RC-1/RC-2 corrections. Existing public results
suffice; no new package, shared runtime function, durable contract or ADR is
justified. Policy/schema/version, authority, receipt-age threshold/boundary,
exact EA coverage requirement, inputs and disposition are explicitly supplied
and retained by the caller; hidden defaults are forbidden. Receipt-age failure
means `evidence_not_usable_under_policy` / `receipt_age_exceeded`; honest
`multiple_matching_candidates` means `criterion_evaluation_unavailable`, not
incoherence. Concrete thresholds and authority are application configuration.
This closure authorizes no successor proposal or milestone.
DI-001 was investigated and is closed without implementation: cancelled as a
backend architecture milestone and reclassified as bounded application
composition; see the [DI-001 owner decision](docs/superpowers/reports/2026-09-10-di001-application-composition-owner-decision.md).
CS-001 and DI-001 both concluded existing public-result composition is sufficient.
DI is limited to explicit before/proposed model material and named supplied
decisions; unknown or omitted scopes are never unaffected. Lifecycle, currentness,
closure, effective-body semantics and result revalidation remain kernel-owned;
the application owns its bounded inventory, documented field map, generic
traversal and explicit limits. No reusable traversal package is justified without
a second concrete consumer or demonstrated correctness failure. CV-001 backend
additions are cancelled; CV-001 application delivery is deferred pending concrete
application requirements; see the [CV-001 owner decision](docs/superpowers/reports/2026-09-10-cv001-deferral-owner-decision.md).
Existing APIs suffice for correct in-process composition; the complete CV
commissioning application remains deferred. The separately accepted bounded
workflow now exposes its narrower current-condition and provenance/replay answer,
advancing objectives 2 and 7. Further application scopes require the eleven
consumer requirements listed in that
decision, including ingress/invocation, authentication/authorization, policy
authority and schema/version/retention, decision-result retention, application/user
identity, confidentiality, capacity/latency, error presentation,
deployment/resource ownership, and scope completeness. Further backend abstraction
requires a demonstrated integrity gap. General causal diagnosis, maintained
next-test ranking, complete impact discovery and multi-step planning remain
undelivered and unauthorized. The accepted application supplies only its bounded
named-decision review and one-step action projections. No generic backend wrapper
may conceal the application prerequisites.
No successor milestone has been approved.
Physical-flow occurrence, candidate generation, causal identification, maintained
next-test recommendation, general impact propagation, multi-step desired-state
planning and safety or health verdicts remain absent. Finite-set action selection
is delivered within the accepted application profile, without global optimality.
Accountable occurrence/history still requires
explicit time-window, continuity, and authenticity semantics. Shared backend goal,
action and optimization contracts, configuration timelines and control remain
deferred; application-owned targets, supplied actions and finite selection are
limited to the accepted workflow above.

EA-001 is complete and owner accepted. Its accepted lineage includes the Slice
A lower read seams and integrity repair at
`ceee1446f18ae9b7134005089046a5a4d69e10ae`; repaired Slice B at
`932514a456bcafe690a94d2d774b61913c352fbf`; Slice C1 contracts, pure
derivation, adversarial tests, and expected-fingerprint repair at
`64c0a8ba7678c7567c2b596947167535cf8fbab3`; and the exact tested Slice C2
public surface at `96d0dfec1a73c6250159dae0df498880ac5e26b0`. EA-001 is
adversarially repaired, full-suite verified, and dual-clean-checkout verified.
It adds no demonstration or committed alignment-result artifact, and every
later demonstration remains unauthorized.

[ADR-0019](docs/adr/0019-content-bound-operational-evidence-selection-and-assurance.md)
records the accepted EA-001 architecture.
[ADR-0020](docs/adr/0020-evidence-gated-declared-transition-assessment.md)
records the owner-accepted TA-001 design. TA-001 is complete, owner accepted,
adversarially hardened, and dual-clean-checkout verified.

## Source-agnostic boundary — owner clarification, 2026-09-14

The [prospective physical-model validation investigation](docs/superpowers/proposals/2026-09-14-prospective-model-validation-feasibility.md)
is closed without acquisition; its [owner closeout](docs/superpowers/reports/2026-09-14-prospective-model-validation-closeout.md)
supersedes its historical next-action recommendation. It is not a pending backend
dependency. The backend remains source-agnostic. Physical equipment, Moonraker
access and independent empirical measurements are not architectural prerequisites.
Backend correctness concerns explicit semantics, reference integrity, lifecycle,
provenance, inference rules and computation under declared assumptions. Synthetic
fixtures, mathematical checks, adversarial tests and replay validate these
properties within their tested scope; they do not establish empirical adequacy
of particular equations, parameter bounds or hypotheses for particular equipment.
Source authenticity, calibration and empirical accuracy are distinct from content
integrity and deterministic reconstruction. The backend may carry evidence and
disclose limitations without certifying it as physically true. A specific adapter
or demonstration must not determine general hypothesis, prediction, influence or
change-impact semantics. Accepted experimental findings and their limits remain
unchanged; that empirical closeout authorized no production capability or new
experiment. The later bounded application has its separate acceptance above.

Future empirical validation requires a separate explicit application/domain request
identifying a concrete application or predictive claim. Another backend milestone's
use of observations, predictions or reasoning does not reopen this investigation.
Measurements, if later authorized, must follow that particular model's variables,
uncertainty, applicability and evaluation criteria, not a universal list. IN-001
and CI-001 remain available architectural options; neither is authorized here.

The next architectural question is: “Given a complete explicitly supplied
hypothetical system model, which missing semantics or reasoning operations still
prevent the backend from answering the original objectives?” This names a question,
not an authorized successor proposal or a predetermined architectural answer.

## Current Phase

Start with the backend. Do not build the 3D interface, conversational interface,
reasoning engine, or a device-specific showcase yet.

The first backend module is:

```text
data_sources
```

We will validate each module before expanding the architecture. Work in small,
demonstrable vertical slices. Avoid scaffolding the entire future platform in
advance.

## Superpowers Skills

The project owner has Superpowers skills available for Claude. At the beginning
of a work session, inspect the available project and Superpowers skills and use
the relevant ones.

In particular, use the installed equivalents of:

- brainstorming before making a new architectural or product decision;
- writing plans before multi-step implementation;
- test-driven development while implementing behavior;
- systematic debugging when behavior differs from expectations;
- verification before claiming that work is complete.

If the installed skill names differ, use the closest available equivalents. Do
not invoke every skill mechanically; use the smallest set that materially helps
the current task. Follow skill instructions faithfully.

Project-local skills or supporting guidance may be created when genuinely
useful. Do not modify global Claude configuration, install machine-wide tools, or
change the user's global skills without explicit approval.

## Conceptual Architecture

The intended information flow is:

```text
Source systems
    -> data_sources
    -> normalization and identity resolution
    -> model kernel
       - typed system graph
       - configuration and version model
       - live state model
       - evidence and artifact references
    -> reasoning engines
       - constraint validation
       - diagnosis and causal reasoning
       - change-impact analysis
       - desired-state planning
    -> stable application API
    -> engineering UI, 3D UI, and conversational interface
```

Only `data_sources` is currently in scope. The downstream boxes explain its
contracts and boundaries; they are not authorization to implement them now.

## Important Model Distinctions

The future model must not collapse these views into one:

```text
As-designed
    -> As-built
    -> As-configured
    -> As-operated
    -> As-maintained
```

It must also distinguish:

- a reusable system or component type from a particular physical instance;
- structure from current state;
- an observation from an inference;
- connectivity from causality;
- commanded state from measured state;
- source time from ingestion time;
- an absent value from a value known to be zero or false;
- a current fact from a fact valid only for an older configuration or version.

These distinctions should influence data contracts from the beginning, even
though the full model kernel will be implemented later.

## The Future Modelling Kernel

Do not implement this kernel during the `data_sources` milestone, but preserve a
clean path toward these primitives:

- **Entity**: component, subsystem, software module, requirement, process, or
  environmental object.
- **Port**: a typed interface through which energy, material, motion, data, or
  control is exchanged.
- **Relationship**: a typed, directional, evidence-backed connection between
  entities or ports.
- **Variable**: a measurable, calculated, inferred, or configured property.
- **Behavior**: an equation, rule, state machine, lookup table, or external
  simulation.
- **Constraint**: a condition that must remain true.
- **Observation**: a time-bound measurement or manually reported fact.
- **Evidence**: the artifact, sensor, source record, or authority supporting a
  claim.
- **Goal**: a desired condition or performance outcome.
- **Action**: a permitted intervention that may change state.

The hierarchy will be one view of the system. Cross-domain reasoning will
require a typed graph layered over that hierarchy. Do not reduce every
relationship to a generic `connected_to` edge.

## `data_sources` Purpose

`data_sources` is the controlled boundary between external reality and the
platform.

Its job is to discover, describe, connect to, and reliably acquire data from
external sources while preserving the original payload, source context, timing,
identity, integrity, and provenance.

Candidate source families include:

- tabular and structured files: CSV, Excel, JSON, XML, YAML, BOMs, and
  configuration files;
- documents: PDF, Word, scanned manuals, requirements, procedures, reports, and
  service records;
- engineering artifacts: native CAD, neutral CAD exchange formats, 2D drawings,
  3D assemblies, electrical schematics, and simulation exports;
- enterprise systems: relational databases, time-series databases, PLM, ERP,
  MES, CMMS, and requirements-management systems;
- network services: REST, GraphQL, vendor APIs, file stores, and object stores;
- software sources: repositories, releases, firmware, configuration history;
- operational sources: WebSockets, MQTT, OPC UA, ROS topics, industrial
  protocols, serial connections, and device logs;
- telemetry: sensors, events, alarms, commands, and measured state;
- human observations: inspections, maintenance notes, and validated manual input;
- environmental sources: weather, ambient sensors, maps, or test conditions.

The physical showcase has not been selected. Keep the core source contracts
device-neutral. Device- or vendor-specific behavior belongs in adapters.

## What "Data Source" Means

A data source is any external authority or observation channel that can provide
evidence about one or more of the following:

- what the system is designed to be;
- what was actually built or installed;
- how hardware and software are configured;
- how the system is expected to behave;
- what the system is doing now or did historically;
- what humans observed, decided, changed, or repaired;
- what environment the system is operating in.

The module is therefore broader than telemetry ingestion. It is an extensible
**evidence acquisition and format-extraction layer**.

There are two steps at the source boundary:

```text
Acquire
    Preserve the original file, response, row set, message, or signal.

Extract
    Decode source-format structure without yet deciding its canonical
    engineering meaning.
```

For example, an Excel extractor may identify workbooks, sheets, cells, formulas,
cached values, and tables. It must not decide by itself that column `Item No.` is
the platform's canonical component identity. That decision belongs to the later
normalization and identity-resolution layer.

## Connector Catalog Versus Active Connectors

The architecture should know about a broad connector landscape, but it must not
pretend that every connector works.

Keep these concepts distinct:

1. **Declared**: the connector or format is described in the capability catalog.
2. **Available**: a real implementation and its dependencies are installed.
3. **Configured**: a source instance has valid, non-secret configuration.
4. **Connected**: the platform can currently reach and read the source.
5. **Validated**: representative application data has passed contract and
   acceptance tests.
6. **Unsupported**: the source or required extraction level cannot currently be
   handled.

A planned entry in the catalog is not an implementation. Do not create dummy
connectors that report success or return empty data. Every connector and
extractor should publish an honest capability and maturity manifest such as:

```text
connector_type
source_families
supported_formats_or_protocols
acquisition_modes: snapshot | poll | stream
supported_extraction_levels
read_only
incremental_read_support
required_dependencies
licensing_or_runtime_requirements
maturity: planned | experimental | validated
known_limitations
```

The selected application should define a **source profile** containing only its
required and optional sources. The runtime loads that profile rather than
initializing every connector in the catalog.

## Source-Family Extraction Boundaries

Different sources require different format-aware extraction while producing the
same stable raw-record and provenance contracts.

### CSV and Excel

Preserve the original file and extract, as supported:

- file, workbook, sheet, table, row, and cell identity;
- headers and source-native data types;
- formulas separately from displayed or cached values;
- merged cells, hidden sheets, named ranges, and units when explicitly supplied;
- row and column location so every extracted value can be traced back.

Do not assume the first row is always a header, guess engineering units silently,
or flatten formulas into unexplained values.

### PDF and Document Sources

Preserve the original document and extract, as supported:

- pages, text blocks, reading order, headings, tables, images, and annotations;
- document metadata, revision identifiers, and page coordinates;
- OCR output for scanned pages, clearly marked as OCR-derived;
- links between extracted content and the exact page or region it came from.

Text extraction, OCR, and table detection are evidence-producing operations, not
proof that the extracted content is correct. Preserve confidence and extraction
method.

### APIs and Databases

Preserve request and query provenance without recording secrets. Capture:

- endpoint, operation, or query identity;
- response schema or database schema information when available;
- pagination, cursor, transaction, snapshot, and change-token information;
- source-native primary keys and revision fields;
- the distinction between full snapshots and incremental changes.

Database access is read-only by default. Queries must be parameterized, bounded,
timed out, and observable. A BOM may arrive through CSV, Excel, an API, a SQL
view, PLM, or ERP; its transport does not define its engineering meaning.

### CAD Models and Engineering Drawings

Treat "CAD" as several different source classes:

1. **Native authoring formats** from systems such as CATIA, NX, SolidWorks,
   Inventor, or AutoCAD. These may require a vendor SDK, licensed installation,
   or controlled export process.
2. **Neutral exchange formats** such as STEP, IGES, JT, DXF, or IFC, which may
   preserve different amounts of product structure, geometry, and metadata.
3. **Visualization and mesh formats** such as glTF, STL, or OBJ, which are useful
   for display but usually contain less engineering meaning.
4. **Rendered engineering drawings** such as drawing PDFs or scanned sheets,
   which require layout, vector, table, text, symbol, and sometimes OCR
   extraction.

CAD support must declare extraction levels rather than a single misleading
`supported` flag:

```text
Level 0: raw artifact, metadata, checksum, and revision
Level 1: document or assembly/product structure
Level 2: parts, instances, coordinate systems, transforms, layers, and properties
Level 3: geometry/topology or a traceable visualization derivative
Level 4: dimensions, tolerances, PMI/GD&T, annotations, and drawing tables
Level 5: native mates, constraints, parameters, and design intent when available
```

Not every format can preserve every level. A mesh can show shape without proving
part identity, tolerances, assembly constraints, material, or function.

The CAD pipeline should conceptually be:

```text
CAD connector
    -> raw immutable artifact
    -> format detector
    -> isolated format-specific extractor
    -> extraction manifest
       - assembly tree
       - parts and instances
       - transforms and units
       - properties and annotations
       - references to geometry/visual derivatives
       - warnings and unsupported features
    -> later engineering normalization
```

Native and untrusted CAD processing may require isolated workers because parsers
can be large, licensed, platform-specific, or unsafe to run in the main service.
Never execute embedded macros or acquired code as part of extraction.

Most importantly, CAD can provide evidence of geometry, containment, spatial
relationships, interfaces, mates, and annotations. It does not automatically
tell us why a component exists or prove a causal relationship. Functional and
causal meaning must be supported by additional sources or validated engineering
rules.

### Sensors and Operational Streams

For live sources, capture:

- sensor or topic identity;
- message schema and source-native field names;
- source timestamp, receipt timestamp, sequence, and clock information;
- supplied units, quality codes, calibration identity, and sampling rate;
- connection loss, dropped-message, duplicate, and out-of-order behavior;
- command values separately from measured values.

Streaming is a connector capability, not the default mode for the whole module.
Only start the streams required by the selected application profile.

## `data_sources` Responsibilities

The module should eventually provide:

1. **Source catalog**
   - Stable source identity.
   - Source type and ownership.
   - Location or connection metadata.
   - Declared capabilities.
   - Expected schema or content type when known.
   - Configuration and credential references.
   - Lifecycle status and health.

2. **Connector contracts**
   - A small common interface for snapshot, polling, and streaming sources.
   - Explicit capability declaration rather than a large interface full of
     unsupported methods.
   - Separate acquisition contracts from format-extraction contracts.
   - Honest maturity and supported-extraction-level declarations.
   - Clear connection, authentication, timeout, retry, checkpoint, and shutdown
     behavior.
   - Read-only behavior in the initial milestone.

3. **Acquisition runtime**
   - Start, stop, and observe connector runs.
   - Support bounded snapshots first; introduce continuous execution only when a
     validated use case requires it.
   - Backpressure, reconnect, and checkpoint behavior for streaming sources when
     streaming is introduced.

4. **Raw record envelope**
   - Wrap every acquired payload in a stable platform-owned envelope.
   - Preserve the original payload or an immutable reference to it.
   - Record source identity, timing, integrity, and acquisition context.
   - Never silently convert an inference into a source fact.

5. **Format-aware extraction**
   - Decode supported document, table, engineering, API, database, and stream
     structures into traceable intermediate records.
   - Produce warnings for unsupported or lossy source features.
   - Preserve a link from every extracted item to its raw artifact and source
     location.

6. **Provenance and integrity**
   - Record where each payload came from and how it was acquired.
   - Preserve source-native identifiers when available.
   - Calculate an integrity checksum for persisted raw content.
   - Make acquisition replayable and auditable.

7. **Failure isolation**
   - Represent connector and record-level errors explicitly.
   - Quarantine malformed or unsupported records without losing them.
   - Never allow one failed source to corrupt or block unrelated sources.
   - Redact secrets and sensitive connection details from errors and logs.

8. **Observability**
   - Structured logs and stable error codes.
   - Run status, source health, record counts, lag, and last successful cursor.
   - Enough context to diagnose failures without logging raw secrets.

## Suggested Logical Submodules

Use names appropriate to the selected language, but preserve these boundaries:

```text
backend/
  data_sources/
    contracts/       # Source, connector, record, run, and error contracts
    catalog/         # Source definitions and lifecycle
    connectors/      # Vendor/protocol/file-specific adapters
    extractors/      # Format-aware, pre-semantic extraction
    runtime/         # Execution, retry, cancellation, checkpointing
    provenance/      # Origin, timestamps, checksums, trace context
    raw_store/       # Immutable raw payload persistence or references
    derivatives/     # Traceable CAD/document visual or structural derivatives
    testing/         # Contract tests, fixtures, and fake sources
```

This is a logical structure, not a demand to create empty directories. Add a
submodule only when the current vertical slice needs it.

## Minimum Source Contract

The first implementation should develop a small contract around concepts similar
to the following. Names may change through design and tests.

### SourceDefinition

```text
source_id
display_name
source_kind
connector_type
capabilities
supported_formats_or_protocols
supported_extraction_levels
implementation_maturity
configuration
credential_reference (never the credential value)
declared_content_types
enabled
```

### RawRecord

```text
record_id
source_id
source_native_id (optional)
ingestion_run_id
captured_at
source_observed_at (optional)
content_type
schema_reference (optional)
payload OR immutable_payload_reference
payload_checksum
cursor_or_sequence (optional)
provenance
quality_flags
```

### IngestionRun

```text
run_id
source_id
started_at
finished_at
status
checkpoint_before
checkpoint_after
records_seen
records_accepted
records_quarantined
error_summary
```

### SourceHealth

```text
source_id
status
checked_at
last_success_at
last_record_at
lag (when meaningful)
diagnostic_code
```

Do not turn these sketches into a needlessly elaborate inheritance hierarchy.
Prefer composition, explicit capabilities, and small interfaces.

## Data Semantics and Provenance Rules

The following rules are non-negotiable:

1. Preserve raw source data before semantic normalization.
2. Never overwrite a raw record in place.
3. Distinguish `captured_at`, `source_observed_at`, and any validity interval.
4. Preserve source-native identifiers and versions.
5. Every transformed record must be traceable to its raw record or records.
6. Unknown, missing, invalid, and not-applicable are different states.
7. Units must be explicit when known; do not silently guess or convert units.
8. Duplicates must be detectable. Prefer deterministic idempotency keys when the
   source provides enough information.
9. Schema drift must be observable. Do not silently ignore new fields or changed
   meanings.
10. Correlation, proximity, sequence, and connectivity must not be labelled as
    causality by the ingestion layer.

## Out of Scope for `data_sources`

This module must not:

- decide the canonical engineering meaning of every source field;
- build or directly mutate the future system graph;
- infer physical or causal relationships;
- diagnose failures;
- recommend maintenance or engineering actions;
- calculate the authoritative live state of an asset;
- contain device-specific logic in the common contracts;
- use an LLM response as an unqualified source fact;
- control or command physical hardware during the first milestone;
- introduce production infrastructure solely because it might be useful later.

Parsing transport-level structures is in scope. Domain normalization and
identity resolution belong to the next layer. Format-aware extraction of sheets,
pages, tables, CAD assembly structure, geometry references, and message schemas
is also in scope, provided that outputs remain traceable and do not claim
unvalidated engineering semantics.

## First Vertical Slice: DS-001

The first implementation should prove the source boundary without depending on a
specific physical device.

Build the smallest end-to-end slice that can:

1. Register one local, deterministic source definition.
2. Read a small BOM-like CSV fixture through a real connector and format
   extractor.
3. Emit platform-owned raw record envelopes.
4. Preserve the original payload and its checksum.
5. Distinguish source observation time from capture time.
6. Persist the raw records using a simple local implementation.
7. Re-run the same acquisition without silently creating uncontrolled duplicates.
8. Report an ingestion run result and source health.
9. Quarantine one deliberately malformed fixture with a useful, redacted error.
10. Demonstrate replay of accepted raw records.
11. Expose an honest connector manifest that distinguishes declared, available,
    configured, connected, and validated status.
12. Trace every extracted BOM row and field back to its raw file location.

Use an in-memory or local development implementation where appropriate. A
message broker, cloud service, graph database, Kubernetes deployment, and public
HTTP API are not required for DS-001.

After DS-001 is verified, stop and present the evidence. Do not automatically
continue into Excel, PDF, CAD, databases, APIs, or a live device connector. The
next source family should be selected from the intended application's source
profile and based on what DS-001 teaches us.

Potential future validation slices, selected only when the application needs
them, are:

```text
Tabular:     Excel workbook and formula-preserving extraction
Document:    Native and scanned PDF with page-level provenance
Engineering: STEP assembly plus a related 2D drawing
Enterprise:  Read-only API or bounded SQL snapshot
Operational: One live sensor or telemetry stream
```

These are a capability roadmap, not a requirement to implement every connector.

## DS-001 Acceptance Criteria

DS-001 is complete only when:

- contracts and module boundaries are documented;
- behavior is covered by focused unit and contract tests;
- an end-to-end test ingests the valid fixture;
- an end-to-end test quarantines the invalid fixture;
- replay and duplicate behavior are tested;
- raw records retain provenance and verifiable checksums;
- extracted BOM fields trace back to exact raw rows and columns;
- connector availability and validation status cannot be confused;
- cancellation and resource cleanup are handled where applicable;
- no secrets or local absolute paths are embedded in committed fixtures;
- the documented verification commands pass from a clean checkout;
- known limitations and the next validation question are recorded.

## Engineering Workflow

For every backend module or meaningful change:

1. Restate the decision or capability being validated.
2. Inspect the repository and existing decisions before designing.
3. Use the relevant Superpowers brainstorming skill.
4. Write a bounded implementation plan for non-trivial work.
5. Define acceptance tests before or alongside implementation.
6. Implement the smallest coherent vertical slice.
7. Run focused tests, then the broader relevant suite.
8. Inspect the final diff and verify behavior from the user's perspective.
9. Report evidence, limitations, assumptions, and the next open question.
10. Pause for validation before expanding to the next backend module.

Prefer test-driven development. A test should describe observable behavior, not
mirror private implementation details.

## File-First Architecture and Verification Artifacts

Substantial architecture proposals, synthesized designs, implementation plans,
acceptance matrices, adversarial reviews, repair reports, and completion
reports must be written to repository files. Never rely on terminal or chat
scrollback as the authoritative copy.

Terminal or chat delivery for one of these artifacts is limited to a concise
receipt, normally no more than 30 lines. Where applicable, the receipt reports:

- the artifact path;
- line and byte counts;
- SHA-256;
- section or acceptance-item count;
- confirmation of the required ending marker;
- the `git diff --check` result;
- concise `git status --short` output;
- confirmation of the work's authorized scope;
- genuine unresolved owner questions.

Use `apply_patch` for repository documentation. A large document may be built
through several sequential patches organized by numbered sections. Subsequent
work must reference the artifact by path and SHA-256 instead of repasting it.

When Codex and GLM produce independent proposals, each proposal must be written
to a distinct file. Neither model may silently modify the other model's
proposal. A synthesized specification is a separate authoritative file, never
an in-place rewrite of either independent input.

Writing a design or review artifact does not authorize implementation, fixture
or ledger mutation, commits, pushes, merges, rebases, or other history
operations. Files remain uncommitted until the applicable owner gate explicitly
authorizes commitment.

Completion reports must include the evidence and commands needed to reproduce
verification. Large test transcripts are summarized or placed in a dedicated
report file rather than pasted into terminal or chat output.

## Technology Decisions

The repository currently may not have an established language or backend stack.
Do not make a large framework choice implicitly.

If no stack exists when implementation begins:

1. Identify the minimum capabilities DS-001 requires.
2. Compare a small number of appropriate options.
3. Recommend one option with explicit trade-offs.
4. Record the accepted decision in a short architecture decision record.
5. Keep the first implementation portable at the contract boundary.

Do not add distributed infrastructure before tests demonstrate a need. Prefer
boring, inspectable local components for the first slice.

## Security and Safety

- Connectors are read-only by default.
- Physical control requires a later, explicit safety design and user approval.
- Credentials must come from an approved secret mechanism and must never be
  serialized into source definitions, raw records, fixtures, logs, or errors.
- Treat source payloads as untrusted input.
- Apply size, timeout, path, and parsing limits.
- Avoid executing content acquired from a source.
- Preserve access-control and licensing metadata where supplied.

## Design Principles

- **Evidence before explanation.** Every future conclusion must be traceable to
  relationships, state, observations, and sources.
- **Unknown is a valid result.** Never manufacture completeness.
- **Interfaces before integrations.** Prove the contract with one source before
  adding many connectors.
- **Thin kernel, extensible domains.** Keep universal primitives small and add
  domain semantics through packages or adapters.
- **Configuration and time matter.** Facts and relationships may be valid only
  for a particular version, instance, or interval.
- **Replayability is foundational.** We must be able to reproduce how data entered
  the platform.
- **Validation over volume.** One trustworthy vertical slice is more valuable
  than ten partially working integrations.
- **No information-library drift.** Model only what is needed to support concrete
  decisions and validations.

## Communication With the Project Owner

Lead with the decision or verified outcome. Explain trade-offs plainly. Surface
assumptions and uncertainty instead of hiding them.

Ask for direction before:

- materially expanding the current milestone;
- selecting a physical showcase that commits significant time or money;
- adding a cloud dependency or externally hosted service;
- enabling writes or commands against a real device;
- changing an accepted architectural boundary.

Reasonable, reversible implementation details inside an accepted milestone do
not require repeated confirmation.

CN-001 complete, owner accepted, adversarially reviewed, and dual-clean-checkout verified.

PT-001 complete, owner accepted, adversarially reviewed, and
dual-clean-checkout verified. Slice A is owner accepted. The qualified-token
repair is owner accepted. Slice B is owner accepted. The public-contract repair
is owner accepted. The accepted Slice B HEAD is
`ec9ea7d8c20016e267fae16a2554d5e7f1a0ebce`. Slice C is owner accepted. The
accepted PT-001 membership contains exactly 28 records. Its model revision is
`mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`.
The deterministic artifact SHA-256 is
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.

VP-001 complete, owner accepted, adversarially reviewed, and
dual-clean-checkout verified. The final implementation HEAD before the
administrative acceptance commit is
`82fcb93b233db180d5d2d6c54d465dad390f08a5`.
Slice A is accepted at
`60b739182e423a05eac7f3c531145d90c65fe9bc`; it adds only role-free positive
`vpa_` association claims with strict same-owner admission, independent
corroborating roots, and dedicated `vpw_` withdrawals, plus canonical/store
validation, immutable indexes, builders, exports, replay, and tests. Slice B is
owner accepted at `81179700513bb671cf9955c6a5d7163e3bcc7e1b`. It adds only the
four accepted read-only kernel query methods and their authoritative,
carry-once result contracts. Slice C adds only the accepted read-only
model-state composition; displaying variable state beside a port does not mean
the observation occurred at, originated at, travelled through, or describes
the port. Slice D adds exactly one
role-free parentless VPA, with no VPW, correction, or additional root. The
explicit final VP / pre-BH membership contains 29 records at
`mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`;
the explicit 28-record PT membership remains unchanged historical replay. The
approved VPA is
`vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49`,
its stored-file SHA-256 is
`95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e`, and
the deterministic VP artifact SHA-256 is
`a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`.
The accepted PT artifact SHA-256 is
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.

BH-001's corrected final design and Slice A are owner accepted. Slice A is
accepted at `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. It adds only the opaque
`BehaviorAnchor` identity and the evidence-backed `brg_`/`bhd_`/`bhw_`
model-ledger foundation for an unordered, role-free pair of variables under
the exact `exact_numeric_equality` rule family. Registration is permanent;
declaration correction and withdrawal are membership-relative and
context-specific. Cross-owner registration is permitted only by an explicit
claim, while shared ownership, names, hierarchy, ports, VPA, topology,
semantics, constraints, and observations create no behavior. Slice A adds no
behavior query, evaluator, numeric comparison, state composition, or demo
record. Slice B is owner accepted at
`05177f7306ce745d093bd5f11abafc13a6274d0f`. It adds exactly the four
read-only model-kernel queries and their authoritatively revalidated carry-once
result contracts. The Slice C preimplementation discrepancy report is owner
accepted at `eedae19a9b2542958f44e66af7117a981c7faeef`; its refusal mapping,
carried-material integrity boundary, public errors/exports, and cohort/parser
scheduling questions are resolved. BH-001 Slices A, B, and C are owner
accepted. Slice C is accepted at
`8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`. The Slice D public-variable-
minter discrepancy is owner resolved; the exact minter is committed and the
two independent disposable rehearsals are complete. The pre-append contract
committed at `0905de0` is owner approved: fixed anchors
`var_ab2d312466054c20b0ac764e9bc0114e` and
`bhv_80e21f1682e449ca9c65a5e2ee051ea0`, revision
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`,
and 122406-byte artifact SHA-256
`4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.
Slice D is implemented and adversarially reviewed: the authoritative ledger
contains exactly the approved VRG, BRG, and parentless BHD at the explicit
32-record revision above. The owner-approved pre-append candidate disclosure
artifact reproduces its frozen 122406 bytes and SHA-256 from the committed
ledger, and its evaluator disclosure is honestly
`not_executed`. The 29-record VP membership remains the explicit predecessor.
BH-001 complete, owner accepted, adversarially reviewed, full-suite verified,
and dual-clean-checkout verified. The final implementation HEAD before this
administrative acceptance is
`6fdf4d009538ddd169c1342508a104c9d61560b6`. The accepted Slice D completion
report is
`docs/superpowers/reports/2026-08-30-bh001-slice-d-completion-report.md` at
SHA-256
`3d0485e92dff57df43f31fcd2774acf6099f4f61102246dc6d8777c7ee326b5a`.
Final acceptance does not convert the demonstration's `not_executed` result
into observed equality or any claim about real-machine truth.

ST-001's corrected final design is owner accepted at SHA-256
`febe18fa291896021708d09c10d5cf4ef955201bcd3e59199e74c6c4e630cc95`.
Slice A is owner accepted at
`9adcf4d9613ac96e5fb430a4b750f3053679b64d` on branch `st001` from accepted
base `0ed77df7ea4870faec1eae9b89668add97aa855d`. Slice A is limited to opaque
`StateAnchor` identity and the evidence-backed `srg_`/`std_`/`stw_`
model-ledger foundation, canonical/store integration, immutable indexes,
membership-relative declaration lifecycle, replay, tests, and documentation.
The permanent state subject is one registered entity; every registered
condition must target a variable whose embedded owner exactly equals that
entity. Declarations pin exact VCN records. Slice B implements exactly four
read-only model-kernel state queries and their carry-once, store-independent,
authoritatively reconstructed result contracts. Slice B is owner accepted at
`23eca10a52c0124d22b4e90d80bef952ef5f9381`. The preceding implementation
gate was recorded exactly as: ST-001 Slices A-D are implemented and verified;
Slice D final owner acceptance is pending. ST-001 is now complete, owner
accepted, adversarially reviewed, full-suite verified, and
dual-clean-checkout verified at implementation HEAD
`0f05903af4f11fd94d6e6987247ceb9795faebd6`. The accepted completion report
is `docs/superpowers/reports/2026-08-31-st001-slice-d-completion-report.md` at
SHA-256
`2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3`.
Slice C is accepted at `f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6`. The separately
approved Slice D append added only the frozen SRG followed by the frozen STD.
The accepted ST-001 historical boundary is the exact 34-record revision
`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
the 32-record BH-001 membership remains an explicit historical boundary.
State families and every transition capability remain excluded.
Final acceptance does not turn `matches` into current physical state,
exclusivity, completeness, transition, cause, control, safety, health,
diagnosis, correctness, or recommended action.

FL-001 Slices A, B, and D are owner accepted, Slice C is absent, and the exact
owner-approved Slice D append adds only
`frg_9b76a51bd6a1165572fad2dcf344dad90f17c68c0f5a6e1977874bd6224d7cd7`
followed by
`fld_f5a192053bc42c53ce9e4d3bd49b011589d17191bdb97f9bac93fcc359872192`.
The authoritative demo now contains exactly 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
with one FRG, one FLD, zero FLW, and unchanged 34-record predecessor bytes.
The fixture declares one synthetic logical directed flow in exact
`as_designed` context. Registration, declaration currentness, healthy model
lineage, consistent direction declarations, and aligned pinned support do not
establish physical flow, activity, occurrence, observation, command,
quantity, conservation, behavior, cause, safety, health, correctness,
diagnosis, or recommended action. FL-001 is complete, owner accepted,
adversarially reviewed, full-suite verified, and dual-clean-checkout verified
at implementation HEAD `fe3b15a3caf77974a795dad5b04c0a35abee37b4`.
