# CV-001 Deferral Owner Decision

Owner-directed documentation closeout — 2026-09-10.

## 1. Accepted decision and frozen authority

The owner accepts the challenger verdict `approve_with_corrections`: zero
blocking findings, one required correction (RC-1), and three non-blocking
observations retained as limitations. The design investigation is closed without
implementation. Unconditional cancellation is replaced by cancelled backend
additions and deferred application delivery.

Baseline: `main = origin/main = 1b9b31dc56be7e7d4da120cac0dc1c9ba31f8675`,
`docs: close DI-001 as application composition`, verified before editing.

| Record | SHA-256 |
| --- | --- |
| Frozen proposal before correction | `7d1714076204bdff1169c6215370ae7207ed80beeb6b0aeb1ff8ba8993cbc6a2` |
| [Corrected proposal](../proposals/2026-09-10-cv001-codex-lead-proposal.md) | `1646fc662ae2ae0bc15e2b50173efad88e73d6728036bbf54ed56429393fd99e` |
| [Unchanged challenger audit](2026-09-10-cv001-codex-lead-proposal-challenger-audit.md) | `7cafecf638ee3024282b58369bebaae78cb293262aee0ceceff54bcf74f13580` |

The [correction report](2026-09-10-cv001-proposal-correction-report.md) maps the
wording changes and records preservation and bounded verification.

## 2. Exact architectural disposition

1. No backend CV-001 implementation is justified.
2. No kernel, evidence, evaluation, facade, CLI, HTTP, ledger, fixture, or
   durable-record addition is authorized.
3. The commissioning application boundary is deferred until a concrete consumer
   supplies every requirement in section 3. Deferral is not permission to design
   a generic backend wrapper or begin a narrower implementation milestone.
4. The proposal remains guidance for that future application design.
5. Disposable integration worlds are sufficient; no authoritative FMA/FCD append
   is justified. Maximum authorized append: zero records.
6. ADR-0023 remains absent, unallocated, and unreserved.

## 3. Concrete consumer prerequisites

The named use case remains a commissioning/operations verification workflow,
but its application boundary is not specified. All eleven prerequisites must
come from a concrete consumer before further application work begins:

| Requirement | Consumer must establish |
| --- | --- |
| 1. Ingress and invocation mode | Actual caller, entry channel and invocation lifecycle; no assumed library, CLI, report or HTTP form. |
| 2. Authentication and authorization | How the actor is authenticated and allowed to commission, use policy and see evidence. A token string alone is not proof. |
| 3. Commissioning-policy authority | Who may issue and renew the policy and approve its actual operational thresholds. |
| 4. Policy schema/version and retention | Exact policy semantics/content/version, system of record, retention and historical replay rules; no hidden defaults or latest-policy substitution. |
| 5. Decision-result retention | Whether/how complete inputs, independent commitments, disposition and decision trace are retained, for whom and for how long. |
| 6. Application/user identity | Accountable application, service and/or human identity attached to the request and retained decision. |
| 7. Confidentiality requirements | Admission and disclosure rules for complete carried proof, sensitive values and error content; no redaction that silently invalidates canonical proof. |
| 8. Capacity and latency requirements | Measured workload, size/work limits, latency expectations, concurrency and refusal behavior. Exploratory limits are not production commitments. |
| 9. Error presentation | Audience, channel, safe translation and exact lower-reason preservation; not every refusal is staleness or criterion violation. |
| 10. Deployment and resource ownership | Runtime/trust boundary, owners of storage/resources, lifecycle and cleanup; no implicit service or new store. |
| 11. Scope-completeness expectations | Explicit supported review scope and omission/unknown disclosure; no claim of completeness for unavailable material. |

These are unresolved application-design inputs, not new lower-layer engineering
facts. No value or authority is selected by this decision, and none may be guessed
or hidden inside a generic backend wrapper. Satisfying this list does not itself
authorize implementation; a later owner gate remains necessary.

## 4. Public join, witnesses and product capability

Existing public APIs are sufficient for correct in-process composition. The
accepted FC integrated witness proves the lower public join, including violated
governing A, satisfied ungoverned B and rejection of B substitution. The original
satisfied-A twin was CN-only. The separately acquired W40 full-path satisfied-A
witness closes test coverage but adds no new architectural or user-facing capability.

No stable application entry point currently exposes the complete answer:

> For this exact logical flow, participant port, context, governing criterion,
> and nominated measured-actual sample at an explicit receipt cutoff: is the
> evidence usable under the caller's explicit policy, which criterion governs
> the sample, and is that criterion satisfied?

Public lower results plus caller-owned joins/policy can compute it; the backend
must not be credited with a user-facing workflow that has not been built.

| Original objective | Accepted contribution and limit |
| --- | --- |
| 1. What exists and how connected? | Existing declared flow/port/variable/governing-criterion support; no new CV capability. |
| 2. Current state? | Architecture/test support for one nominated sample and criterion at a cutoff; not delivered application capability or physical system state/health. |
| 3. Why this behavior? | No causal diagnosis; lower refusal explanations are not causal explanations. |
| 4. Next best measurement/test? | Still absent. Withholding one nominated evidence path can inform an application refresh choice, not ranking or best-test selection. |
| 5. Change impact? | No new impact capability or prediction; DI remains bounded application composition, not physical propagation. |
| 6. Smallest desired-state changes? | No goals, planning, optimization or control. |
| 7. Observed/calculated/inferred/assumed/unknown? | Architecture/test support for explicit lower evidence, declaration, verdict, policy and unknown/refused distinctions; not delivered application capability. |

## 5. Spill and policy boundaries

All 26 proposal spill-register entries remain unchanged. Existing lower boundaries
prevent backend spill; they do not supply application authentication and
authorization, policy authority, result retention, error translation,
confidentiality, resource ownership, deployment or scope completeness. Those
remain application-design prerequisites. A future application must invoke all
public validations and preserve all exact joins/refusals; no lower result can
force a caller not to omit a required step.

Policy remains explicitly caller-supplied and retained. Coverage means exactly
EA's `complete_within_declared_horizon`, not a generic Boolean. Age is receipt-side
only; source-observed/effective time cannot rescue receipt-age failure. The
accepted disposition/reason is `evidence_not_usable_under_policy` /
`receipt_age_exceeded`, not physical-measurement staleness or necessarily a new
physical measurement. Byte-identical evidence with a valid new receipt remains
a valid twin. Honest `multiple_matching_candidates` retains
`criterion_evaluation_unavailable`, not input/revision incoherence.

Usability does not establish observation truth, criterion satisfaction, physical
flow occurrence, observation at a port, causal direction, safety or health. A
criterion verdict and a policy disposition remain separate axes. Synthetic
worlds prove contracts, not real printer knowledge.

## 6. Corrected frontier and exclusions

CS-001 is commissioning application policy. DI-001 is bounded application
composition. CV-001 backend additions are cancelled; CV-001 application delivery
is deferred pending concrete application requirements. FC-001 remains complete
and owner accepted; ADR-0022 remains the latest accepted ADR.

No successor milestone is approved. Causal diagnosis remains premature;
causal diagnosis, next-test ranking, impact prediction, and planning remain
unauthorized. Further backend abstraction must not begin without a demonstrated
integrity gap. Further application work must not begin without all the concrete
consumer requirements in section 3 and its separate owner gate. No package,
ledger, durable engineering identity, authoritative fixture append or ADR is
reserved by this deferral.

## 7. Preservation, verification and authorized closeout

The documentation closeout preserves 36 model records and exact replay at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
236 exports with the accepted digest, zero FMA/FMW and FCD/FCW, all protected
document/artifact inventories, and both accepted FC witness bytes/digests.
ADRs remain unique and contiguous through ADR-0022; ADR-0023 is absent,
unallocated and unreserved. Preservation details and commands are in the
correction report.

Frozen/updated digests, document structure/markers, status assertions, local
links, preservation, scope allowlists and working-tree/staged/post-FC-range
whitespace are the closeout verification scope. A full repository or
clean-checkout matrix is unnecessary and was not run for this documentation-only
closeout. The last complete accounting remains 4,074 passes; no new full-suite
claim is made.

Authorized commit: `docs: defer CV-001 pending application requirements`.
It includes only the corrected proposal, unchanged audit, correction report,
this decision and minimum current root/status documentation. No implementation,
successor proposal, ledger/fixture mutation, ADR allocation, push, merge or
history rewrite is authorized. The investigation closes here; application
delivery remains deferred, not silently cancelled or delivered.

END OF CV-001 DEFERRAL OWNER DECISION
