# operation-house-keeping

Backend foundation for a living, constraint-aware representation of an
engineered system. The project is model-centric, not LLM-centric:
deterministic code, explicit model declarations, evidence, and provenance are
authoritative; an LLM is never the source of engineering truth. `CLAUDE.md`
contains the binding project guidance.

## Current status

Maintained measurement-result reassessment has separate
[Slice 5 and final milestone owner acceptance](docs/superpowers/reports/2026-09-30-reassessment-slice5-and-final-owner-acceptance.md).
The accepted application candidate is `c321f2e096a71a43bf65787f6f1605c4031266e7`;
FINAL executed at `f28de9e900c700d910eb5edf2b0e6f8c336472fe`.
The claim is bounded reassessment of supplied scalar observations against
nominated hypotheses and qualified support, with explicit uncertainty,
provenance, manual adoption and independently recomputing replay. It establishes
no empirical accuracy, causal diagnosis, automatic hypothesis generation,
automatic adoption or general robustness. Historical failures and exceptions
remain disclosed. IN-001 and CI-001 remain open and unselected; no successor
milestone is selected.

Maintained bounded [next-measurement selection](docs/next-measurement/README.md)
has owner-accepted Slices 1–6. It adds qualified supplied predictions, prior-free
minimax over nominated procedures, explicit whole-set withholding and standalone
recomputing replay. [Final owner acceptance](docs/superpowers/reports/2026-09-23-next-measurement-final-owner-acceptance.md)
is recorded at tested implementation `23b60a42c2279fc228168967d47491b8983658fb`.
No backend extension or physical acquisition follows.


The maintained [bounded decision workflow](applications/bounded_decision_workflow/README.md)
is owner accepted through S1–S7 at implementation
`64f4389b6d93484339afa29cbb7f7f21f6ef2758`; see the
[acceptance record](docs/superpowers/reports/2026-09-16-bounded-decision-workflow-final-owner-acceptance.md).
Its local evaluate/verify/replay commands deliver public input admission, rational
one-step projection, target/feasibility assessment, tied selection among supplied
actions, named dependency review and retained recomputing replay. The supported
profile fixes two supplied hypotheses and four supplied actions; it generates
neither alternatives nor measurement tests and is not a general planner.
Finite-world admissibility enforcement is also
[owner accepted](docs/superpowers/reports/2026-09-17-maintained-admissibility-final-owner-acceptance.md)
at `15f773ba9c675b553283669fbf72c76407c0eabd`. The explicit governed route
checks declaration, local-attestation, adoption and executable-build references
before numerical evaluation, adds a 23-row dependency review, and retains
verification and recomputing replay. A completed gate is not necessarily granted
permission: denied scenarios cannot reach prohibited numerical work. Legacy
commands retain their original meaning and do not enforce admissibility.
The [current reconciliation](docs/superpowers/reports/2026-09-17-post-admissibility-reconciliation.md)
maps all seven objectives, recovery and publication boundaries; the
[earlier reconciliation](docs/superpowers/reports/2026-09-16-bounded-decision-workflow-post-delivery-reconciliation.md)
is historical. Local attestation is not authentication, declared validity is not
physical truth, and historical replay does not establish current adoption.
Finite-world membership is not general correlated-support projection.
Historical-retention disposition is recorded in the
[retention decision](docs/superpowers/reports/2026-09-17-historical-retention-decision.md):
the 242 existing untracked artifacts remain preserved, no historical source is
added, and 16 locally available historical targets lack located committed
recovery. They are not required for accepted authority, reproduction or runtime
behavior; frozen historical links remain unchanged.
The earlier BRC, conditional-prediction, model-derived-prediction and one-step
proofs remain historical disposable experiments; their test-ranking capabilities
were not promoted into the maintained application.

The accepted implemented milestone sequence through FC-001 is complete.
EA-001 is adversarially repaired, full-suite verified, and
dual-clean-checkout verified. TA-001 Slice A is owner accepted at exact tested
implementation `76738ac0d098eb59b0fec4f6970aa862528647d9`. Slice B adversarial
hardening is implemented and verified at
`2ec18f7234273dba98098d268df4568d5cc84d85`. TA-001 complete, owner accepted,
adversarially hardened, and dual-clean-checkout verified.

FM-001 is complete and owner accepted at exact tested implementation
`4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`. Its exact 225-name public surface
and five read-only Slice B query responsibilities are accepted. There is no
Slice C or demonstration, and the authoritative model still contains zero
FMA/FMW records.

FC-001 is complete and owner accepted at exact tested implementation
`9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`, adversarially hardened and
dual-clean-checkout verified. The current model-kernel public surface has
exactly 236 ordered exports. The authoritative model contains zero FCD/FCW
records. See the [final owner acceptance](docs/superpowers/reports/2026-09-09-fc001-final-owner-acceptance.md).

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
| `backend/transition_assessment` | Pure carried-result assessment of whether two independently classified endpoint views support one declared transition pattern; no I/O, occurrence claim, facade, or persistence. |
| `backend/source_interpretation` | Append-only authority declarations for exact source-property quantity, role, and unit meaning. |
| `backend/semantic_compatibility` | Read-only comparison of accepted model semantics, source interpretation, and observation compatibility. |
| `backend/constraint_evaluation` | Read-only evidence-gated evaluation of explicit variable constraints. |
| `backend/behavior_evaluation` | Read-only evaluation of the bounded explicit BH-001 behavior declaration. |
| `backend/state_classification` | Read-only evidence-gated classification of an explicit state declaration. |
| `applications/bounded_decision_workflow` | Accepted supplied-alternative workflow plus explicit governed finite-world admission before projection; application-owned authority/build binding, 23-row review and retained recomputing replay. Legacy routing remains distinct; no backend ledger or contract extension. |

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
| 20 | TA-001 | Complete, owner accepted, adversarially hardened, and dual-clean-checkout verified | [ADR-0020](docs/adr/0020-evidence-gated-declared-transition-assessment.md) |
| 21 | FM-001 | Complete and owner accepted: explicit flow-to-measurement declarations and five read-only queries over the exact 225-name surface | [ADR-0021](docs/adr/0021-explicit-flow-to-measurement-association.md) |
| 22 | FC-001 | Complete and owner accepted: explicit governing VCN designation for an exact FM effective body and selected-model applicability | [ADR-0022](docs/adr/0022-explicit-flow-operating-criterion.md) |

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

FC-001 is the current completed backend boundary; ADR-0022 is the latest accepted ADR.
The accepted bounded application is a separate delivery boundary over these contracts.
FC determines which explicit VCN governs one exact FM effective body and
whether that designation is applicable under the selected model revision.
The existing FC + EA/alignment + CN public-result join answers the bounded
commissioning question for one independently nominated sample and cutoff. It
rejects substitution of satisfied ungoverned B for violated governing A; the
satisfied governing-A twin passes. FC supplies applicability, CN evaluation.

FA-001 is cancelled under the [final owner decision](docs/superpowers/reports/2026-09-09-fc001-final-owner-acceptance.md).
Reconsideration requires a new owner-approved proposal demonstrating a concrete
integrity attack that existing public-result validation cannot prevent.
Convenience or aggregation preference is insufficient.

The [post-FC objective-gap reconciliation](docs/superpowers/reports/2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md)
is owner accepted and replaces inherited roadmap ordering. Its recommended
investigation, CS-001, is closed without implementation and reclassified as
commissioning application policy, not deferred architecture; see the
[CS-001 owner decision](docs/superpowers/reports/2026-09-10-cs001-application-policy-owner-decision.md).
Existing public results suffice. The caller explicitly supplies and retains
policy, authority, receipt-age threshold/boundary, exact EA coverage requirement,
inputs and disposition; hidden defaults are forbidden. Receipt-age failure is
`evidence_not_usable_under_policy` with reason `receipt_age_exceeded`, not a
physical-measurement freshness claim. No new backend contract is justified.
DI-001 was investigated and is closed without implementation: cancelled as a
backend architecture milestone and reclassified as bounded application
composition; see the [DI-001 owner decision](docs/superpowers/reports/2026-09-10-di001-application-composition-owner-decision.md).
CS-001 and DI-001 both concluded existing public-result composition is sufficient
for their bounded questions. DI covers explicit model material and a supplied
decision inventory, not globally complete decision discovery or physical impact;
omitted or unavailable scopes remain unknown, not unaffected. No reusable
traversal package is justified without a second concrete consumer or demonstrated
correctness failure. CV-001 backend additions are cancelled; CV-001 application
delivery is deferred pending concrete application requirements, as recorded in
the [CV-001 owner decision](docs/superpowers/reports/2026-09-10-cv001-deferral-owner-decision.md).
CV's complete commissioning application remains deferred. The separately accepted
bounded decision workflow now delivers a local entry point for its narrower
current-condition and provenance/replay scope, advancing objectives 2 and 7.
Further application scopes must supply the consumer requirements listed in that
decision: ingress/invocation, authentication/authorization, policy authority,
policy schema/version/retention, decision-result retention, application/user
identity, confidentiality, capacity/latency, error presentation,
deployment/resource ownership, and scope completeness. Further backend abstraction
must not begin without a demonstrated integrity gap. General causal diagnosis,
maintained next-test ranking, complete impact discovery and multi-step planning
remain undelivered and unauthorized. The accepted application does deliver its
fixed named-decision review and supplied-action one-step projections.
No successor milestone has been approved.
ADR-0023 remains absent, unallocated, and unreserved.

The [prospective physical-model validation investigation](docs/superpowers/proposals/2026-09-14-prospective-model-validation-feasibility.md)
is closed without acquisition under the [owner closeout](docs/superpowers/reports/2026-09-14-prospective-model-validation-closeout.md).
Its historical equipment-confirmation recommendation is not a pending backend
dependency. The backend remains source-agnostic: equipment, Moonraker access and
independently collected measurements are not prerequisites for architecture work.
Backend correctness concerns explicit semantics, reference integrity, lifecycle,
provenance, inference rules and computation under declared assumptions; synthetic,
mathematical, adversarial and replay evidence validates those properties within
its tested scope, not physical truth. Accepted experimental findings remain valid
within their original scope; those experiments added no production capability.
The subsequent maintained application has its own explicit acceptance above.

Empirical adequacy of particular equations, bounds and hypotheses belongs to a
separately authorized application/domain activity for a concrete predictive claim.
Source authenticity, calibration and empirical accuracy remain distinct from
content integrity and deterministic reconstruction. A specific adapter or demo
does not determine general hypothesis, prediction, influence or change-impact
semantics. Future empirical work requires an explicit application-specific request;
using observations or reasoning in a backend milestone does not reopen it.
IN-001 and CI-001 remain open and unselected, neither authorized here.

The next architectural question, without a successor proposal or predetermined
answer, is: “Given a complete explicitly supplied hypothetical system model,
which missing semantics or reasoning operations still prevent the backend from
answering the original objectives?”

Physical-flow occurrence, generated candidates, causal identification,
maintained next-test recommendation, general impact propagation, multi-step
desired-state planning and safety or health verdicts remain absent. Finite-set
action selection is delivered only within the accepted application profile;
it establishes no global optimality. Occurrence/history needs explicit
time-window, continuity, and authenticity semantics; graph traversal, ranking,
reasoning, and optimization each need an identified consumer and explicit rules.

## Verification

Application acceptance retains 4,648 full-repository passes, 35 optional CAD/PDF
skips and one sandbox socket setup error, followed by that case passing in a
permitted isolated rerun; no product failures were recorded. Earlier command,
clean-build, recovery, replay, determinism and 27-row evidence remains applicable.
Observed platform evidence is locked CPython 3.13.11 on ext4; XFS, reboot and
power-loss durability remain unverified. Integration documentation does not
change the accepted implementation or its exact-build replay requirement.

```
.venv/bin/python -m pytest        # base-only: CAD/PDF-marked tests skip
# all-extras: install requirements-cad.txt + requirements-pdf.txt first
```
