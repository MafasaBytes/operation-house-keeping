# operation-house-keeping

Backend foundation for a living, constraint-aware representation of an
engineered system. The project is model-centric, not LLM-centric:
deterministic code, explicit model declarations, evidence, and provenance are
authoritative; an LLM is never the source of engineering truth. `CLAUDE.md`
contains the binding project guidance.

## Current status

The accepted implemented milestone sequence through EA-001 is complete.
EA-001 is adversarially repaired, full-suite verified, and
dual-clean-checkout verified. The TA-001 design is owner accepted, but its
implementation has not started and no transition-assessment runtime capability
exists.

The authoritative synthetic demo model contains exactly 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
It contains one FRG, one FLD, and zero FLW, and still contains zero TRG, TRD,
or TRW records. The flow fixture is an explicit declaration only; it is not a
claim that physical flow was active, observed, commanded, measured, conserved,
or occurred.

EA-001 adds bounded, content-bound operational-evidence selection and
assurance plus one pure carried-result alignment to an already-computed
variable-value compatibility result. Its fingerprints are not signatures,
source or sensor authority, trusted time, global atomicity, or physical truth.

## Architecture

| Module | Accepted responsibility |
| --- | --- |
| `backend/data_sources` | Read-only evidence acquisition, immutable raw storage, format extraction, provenance, and quarantine for CSV/BOM, STEP, PDF, and the bounded operational API. |
| `backend/temporal_state` | Rebuildable source-native observation projection with explicit receipt-axis cutoffs; never model truth. |
| `backend/evidence_assurance` | Read-only, bounded selection and content-fingerprint assurance over captured operational source and temporal material; no ledger, durable identity, semantic admission, or truth claim. |
| `backend/system_identity` | Pure opaque anchor value contracts and public minters; no storage or authority. |
| `backend/identity_binding` | Append-only explicit source-to-model identity decisions and read-only resolution. |
| `backend/model_kernel` | Append-only typed, evidence-bearing model declarations, exact `mrv_` replay, lifecycle/index derivation, and read-only model queries. |
| `backend/structural_evidence` | Read-only normalization and reconciliation of source-reported structure; no model acceptance or ledger ownership. |
| `backend/model_state` | Read-only composition of one loaded model with explicitly selected identity-bound temporal evidence. |
| `backend/observation_compatibility` | Read-only comparison of an attached observation with explicit model value-shape and unit declarations. |
| `backend/evidence_alignment` | Pure carried-result alignment of one EA selection with one variable-value compatibility result; no I/O, reselection, persistence, or generic consumer framework. |
| `backend/source_interpretation` | Append-only authority declarations for exact source-property quantity, role, and unit meaning. |
| `backend/semantic_compatibility` | Read-only comparison of accepted model semantics, source interpretation, and observation compatibility. |
| `backend/constraint_evaluation` | Read-only evidence-gated evaluation of explicit variable constraints. |
| `backend/behavior_evaluation` | Read-only evaluation of the bounded explicit BH-001 behavior declaration. |
| `backend/state_classification` | Read-only evidence-gated classification of an explicit state declaration. |

Dependencies point from upper composition layers toward accepted lower
contracts. `system_identity` has no backend dependency; `model_kernel` depends
on it but does not read source, temporal, binding, or upper evaluation stores.
The read-only composition modules own no authoritative ledger. Committed
knowledge lives beside the code in `models/` and `bindings/`; frozen synthetic
sources and disclosures are test artifacts, never engineering truth.

## Milestones

| Order | Milestone | Accepted capability | ADR or accepted design |
| ---: | --- | --- | --- |
| 1 | DS-001 | CSV/BOM source boundary | [ADR-0001](docs/adr/0001-ds001-python-pydantic-stack.md) |
| 2 | DS-002 | STEP ingestion and OCP boundary | [ADR-0002](docs/adr/0002-step-toolchain-ocp.md) |
| 3 | DS-003 | PDF ingestion toolchain | [ADR-0003](docs/adr/0003-pdf-toolchain-pdfplumber-pypdf-pypdfium2.md) |
| 4 | DS-004 | Bounded read-only operational API | [ADR-0004](docs/adr/0004-operational-api-moonraker-stdlib-http.md) |
| 5 | TS-001 | Temporal evidence projection | [ADR-0005](docs/adr/0005-temporal-state-sqlite-projection.md) |
| 6 | IB-001 | Opaque identity and explicit binding | [ADR-0006](docs/adr/0006-identity-binding-ledger.md) |
| 7 | MK-001 | Typed graph model ledger | [ADR-0007](docs/adr/0007-model-kernel-typed-graph-ledger.md) |
| 8 | VM-001 | Variable membership and bound model-state facade | [ADR-0008](docs/adr/0008-model-state-composition-facade.md) |
| 9 | VS-001 | Value specification and observation compatibility | [ADR-0009](docs/adr/0009-variable-value-specification-and-observation-compatibility.md) |
| 10 | SN-001 | Structural evidence normalization and reconciliation | [ADR-0010](docs/adr/0010-structural-evidence-normalization-and-cross-source-binding.md) |
| 11 | ES-001 | Engineering semantics and source interpretation | [ADR-0011](docs/adr/0011-engineering-semantics-and-source-property-interpretation.md) |
| 12 | CN-001 | Explicit constraints and evidence-gated evaluation | [ADR-0012](docs/adr/0012-explicit-variable-constraints-and-evidence-gated-evaluation.md) |
| 13 | PT-001 | Explicit ports and typed connectivity | [ADR-0013](docs/adr/0013-explicit-ports-and-typed-interface-connectivity.md) |
| 14 | VP-001 | Explicit variable-port association | [ADR-0014](docs/adr/0014-explicit-variable-port-association.md) |
| 15 | BH-001 | Explicit behavior declarations and bounded evaluation | [ADR-0015](docs/adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md) |
| 16 | ST-001 | Explicit state identity and evidence-gated classification | [ADR-0016](docs/adr/0016-explicit-state-identity-and-evidence-gated-classification.md) |
| 17 | ST-002 | Explicit transition identity and declaration-only disclosure | [ADR-0017](docs/adr/0017-explicit-state-transition-identity-and-declaration.md) |
| 18 | FL-001 | Explicit flow identity and declaration-only disclosure | [ADR-0018](docs/adr/0018-explicit-flow-identity-and-declaration.md) |
| 19 | EA-001 | Content-bound operational-evidence selection, assurance, and bounded value-compatibility alignment | [ADR-0019](docs/adr/0019-content-bound-operational-evidence-selection-and-assurance.md) |
| 20 | TA-001 | Owner-accepted design for pure evidence-gated declared-transition assessment; implementation not started | [ADR-0020](docs/adr/0020-evidence-gated-declared-transition-assessment.md) |

Accepted specifications live in `docs/superpowers/specs/`; accepted decisions
live in `docs/adr/`; owner gates and verification evidence live in
`docs/superpowers/reports/`.

## Truth boundaries

The repository keeps source evidence and observations, model declarations,
evaluation/classification, transition or flow declarations, and accountable
physical occurrence as separate concepts. A connection, compatible
interface, changed observation, classification at two cutoffs, transition
declaration, or flow declaration does not establish a physical transition,
transfer, influence, cause, or occurrence.

An EA snapshot fingerprint or successful evidence-alignment result establishes
only the accepted bounded content and relation. It does not authenticate the
source, sensor, signer, clock, engineering conclusion, or physical condition.

## Architectural frontier

TA-001 has an [owner-accepted design](docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md),
recorded by [ADR-0020](docs/adr/0020-evidence-gated-declared-transition-assessment.md),
for a pure, read-only assessment of whether two independently classified
endpoint views support one declared transition pattern. Implementation has not
started. It will not establish transition occurrence or non-occurrence, add an
orchestration facade or demonstration, or create a generic immutable
assessment identity.

The unapproved frontier beyond that design includes flow measurement
association and assessment and, eventually, configuration identity, causality,
diagnosis, impact analysis, goals, actions, and planning. These remain possible
future concerns only; this status authorizes none of them.

## Verification

```
.venv/bin/python -m pytest        # base-only: CAD/PDF-marked tests skip
# all-extras: install requirements-cad.txt + requirements-pdf.txt first
```
