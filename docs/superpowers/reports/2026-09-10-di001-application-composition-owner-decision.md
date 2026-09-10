# DI-001 Application Composition Owner Decision

2026-09-10 — owner-accepted documentation-only closeout.

## 1. Verified baseline and accepted frozen inputs

Before editing, branch `main` and both `HEAD` and `origin/main` were verified at
`181f5c8484ce31b7f4ef377e4af2399ed946dfa0`, with latest commit
`docs: close CS-001 as application policy`. There were no uncommitted tracked
changes; the frozen DI proposal and audit were the two untracked inputs.

The owner accepts the [DI-001 lead proposal](../proposals/2026-09-10-di001-codex-lead-proposal.md)
as retained design guidance, unchanged at 739 lines, 74,874 bytes, 13 numbered
sections and SHA-256
`447a345417dbd6ff4ff88685fffdfe20fc677a6f5517527e564165609e5cffe7`.
Its final marker is `END OF DI-001 CODEX LEAD PROPOSAL`.

The [independent challenger audit](2026-09-10-di001-codex-lead-proposal-challenger-audit.md)
is accepted unchanged at 369 lines, 25,403 bytes, 15 numbered sections and
SHA-256 `f0e05a8a599f258f999c281c19b698dac9644ca4b3cfb96fbefe092634e7396b`.
Its final marker is `END OF DI-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT`.
The accepted verdict is `approve`: zero blocking findings, zero required
corrections, and four non-blocking observations accepted as limitations.
No proposal correction or additional challenger audit is required or performed.

This decision supersedes the proposal's pending owner-gate language without
rewriting either frozen input or any historical accepted document.

## 2. Final disposition and explicit non-authorizations

DI-001 is investigated and closed without implementation. It is cancelled as a
backend architecture milestone and reclassified as bounded application
composition, not deferred architecture. The proposal remains design guidance
for the engineering change-review and configuration-management workflow.

No missing kernel integrity property was demonstrated. Existing public model
material, owning queries and carried-result validation suffice for the bounded
question. No reusable traversal package is justified without a second concrete
consumer or demonstrated correctness failure. Either trigger would require a
separate justified owner decision; it is not automatic implementation approval.

No durable dependency records, model-impact component, kernel query extension,
prerequisite repair, shared runtime implementation or new ADR is authorized.
This closeout does not authorize even application implementation, another
proposal, a new decision registry or an authoritative fixture/ledger append.

## 3. Exact supported question and completeness boundary

The strongest honest claim is:

> For the explicit model material and named decisions supplied to this bounded review, disclose which dependencies changed, through which typed paths, and which supplied decisions require reevaluation.

Existing public APIs permit comparison of complete before/proposed memberships
and disclosure of typed dependency paths for a bounded, explicitly supplied
decision inventory. `ModelRevision`, `ModelQueryMaterial`, `.loaded()` and
`ModelQueries` provide the public model seam; owning public result validators
retain authority for their respective carried results. Field-path disclosure
does not replace requerying the owning semantics in each exact membership.

Completeness is relative to the explicitly supplied material, admitted typed
relations and named decision inventory. It is not globally complete decision
discovery, nor discovery of all decisions known to an application unless that
application independently supplies and warrants that exact inventory. Omitted,
unsupported or unavailable scopes must be disclosed as `unknown`, never
`unaffected`. An unknown scope is not a negative reachability proof.

DI does not establish physical change impact, causal propagation, behavior
prediction, safety or risk impact, cost or schedule impact, or automatic
reversal of a prior decision. Reevaluation is not a predicted new result.
Provenance dependency is not automatically semantic dependency; semantic
dependency is not causality. Shared names, entities, variables, ports, contexts,
tokens or temporal proximity do not create unstated dependency edges.

## 4. Kernel and application responsibilities

Lifecycle, currentness, structural closure, effective-body semantics and result
revalidation remain kernel-owned for the model; accepted upper result families
retain their own composition/evaluation authority. The application must invoke
those public contracts, not reproduce private derivation rules or establish a
second model kernel. No lower package imports an upper impact composition.

The application owns only its bounded decision inventory, documented field map,
generic graph traversal and explicit limits. It must retain the comparison
intent, exact material and independent expected commitments needed to interpret
that inventory. Compare its expected decision key set to all returned rows,
including unknown, refused and no-longer-evaluable decisions; omissions may not
silently disappear. Foreign references terminate at an explicit unknown frontier
unless the independently supplied supported foreign material and review scope
justify further disclosure. Kernel membership is not foreign-ledger authority.

Complete before and proposed memberships are validated independently. Append
candidates retain all before records and identical bytes for shared IDs;
corrections append successors, withdrawals append the allowed withdrawal record,
and replacement identities require explicitly new downstream declarations.
Changing immutable bytes or silently deleting records is not change modeling.
Historical comparison is an explicit reference-closed membership selection,
not ledger deletion or undo. Invalid proposed membership is refused rather than
described as ordinary impact. Combined changes are evaluated together; a union
of singleton findings is not a substitute for the proposed world.

Typed direct and transitive disclosure retains exact field roles and query
selection dependencies. Traversal does not decide applicability from reachability.
Use the proposal's explicit cycle, duplicate, ordering and all-simple-labelled-
path discipline only within a declared bounded review; limits apply in aggregate
across both worlds and changed inputs. Exhaustion refuses the whole review,
not silent truncation or a favorable unaffected result. No production capacity
or hidden default is approved by this decision. Result validation opens no store
or filesystem and authenticates no uncarried ledger or source bytes.

## 5. Four accepted audit limitations

| Observation | Owner disposition |
| --- | --- |
| NBO-1 — audit execution environment | Accept the disclosed limit: the frozen audit traced live derivation and helper signatures but did not independently re-execute the authoring experiments. This closeout does not rewrite that audit or claim it ran another suite. |
| NBO-2 — disposable capacity observations | Accept their non-load-bearing character and the audit's independent-reproduction limitation. Counts and serialized sizes are observations, not durable identities or production performance evidence. Protected FC witness hashes are checked separately. |
| NBO-3 — field-map drift | Accept the documented taxonomy as maintained application guidance. Future owner-approved record/result families require an explicit field-map review before claiming complete coverage; unsupported relations remain unknown. |
| NBO-4 — exploratory limits | Accept the profile as exploratory and owner-gated, not production sizing. Any application needing larger scope must measure actual consumer material and explicitly choose capacity and refusal behavior. |

The named application still chooses its exact decision inventory and completeness
authority, comparison mode, admitted foreign scope and measured capacity.
Those choices do not represent missing foundational architecture or authorize
implementation here. The final DI backend disposition itself is resolved.

## 6. Original-objective contribution and architectural frontier

| Original objective | Accepted contribution; no new backend capability |
| --- | --- |
| 1. What exists and how is it connected? | Existing explicit declaration references become reviewable as typed dependency paths; no new connectivity fact. |
| 2. Current state of this particular system? | Partial model-level support currentness/applicability and result-reuse disclosure under exact memberships; not physical state, freshness or health. |
| 3. Why might the system behave this way? | No causal or diagnostic capability. A dependency-based refusal explanation is not a cause of behavior. |
| 4. Next best measurement or test? | No measurement selection or ranking. A decision needing reevaluation does not identify the next best test. |
| 5. What would be affected by a component, parameter or software change? | Bounded explicit declaration dependency and supplied-decision reevaluation only. Structural membership validity is available; physical propagation, behavioral consequence, causal, safety/risk and cost/schedule impact are not established. |
| 6. Smallest valid change set for a desired state? | No goals, action generation, minimization, planning or control. Validating a supplied membership does not find an optimal change set. |
| 7. Observed, calculated, inferred, assumed or unknown? | Partial: preserve declared facts, calculated query differences, application completeness assertions and unknown scope separately; no new observation truth. |

The [post-FC reconciliation](2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md)
remains owner accepted. [CS-001](2026-09-10-cs001-application-policy-owner-decision.md)
and DI-001 both concluded existing public-result composition is sufficient for
their bounded questions: commissioning application policy and engineering
change-review application composition respectively. Neither adds a backend
capability or leaves an unimplemented architectural milestone waiting in line.

FC-001 remains the completed foundational boundary. FA-001 remains cancelled
under its accepted integrity-attack reconsideration rule. No successor milestone
has been approved. Causal diagnosis remains premature. Further progress should
begin from a concrete application decision or a demonstrated integrity gap,
not another generic kernel abstraction or the next unused roadmap noun.
ADR-0022 remains the latest accepted ADR; ADR-0001 through ADR-0022 are contiguous
and unique. ADR-0023 remains absent, unallocated, and unreserved.

## 7. Preservation and verification

| Protected checkpoint | Preserved value |
| --- | --- |
| Authoritative model records | 36 |
| Accepted revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| Model-kernel exports | 236 unique ordered names; compact-JSON SHA-256 `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |
| FCD/FCW; FMA/FMW | `0/0`; `0/0` |
| FC witness | 14,677 bytes; SHA-256 `a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca` |
| Integrated witness | 174,490 bytes; SHA-256 `1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e` |
| Accepted reconciliation | SHA-256 `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5` |

Verification covers frozen proposal/audit digests; their structures and markers;
this decision's structure and marker; documentation/status assertions; local
links for every committed document; unique contiguous accepted ADRs and absent
ADR-0023; live ledger load/replay, revision and export digest; the six protected
tree inventories and seven protected document hashes recorded in the proposal;
FC and integrated witness preservation; and the exact six-document allowlist.
Witness reproduction uses disposable temporary material only, never an append
to the authoritative repository ledgers or a fixture/artifact rewrite.

Whitespace checks cover the working tree, staged index and full post-FC range
from `7693f1acf763f652947dff28b5dbb8a8dfee2505`, including newly staged files.
The verification-before-completion skill informs fresh checks and bounded claims.
A full repository or clean-checkout matrix is unnecessary and was not run for
this documentation-only closeout. Historical 4,074-pass coverage is not claimed
as a new run; the earlier independent probe runs are not closeout verification.

## 8. Changed-document list and bounded commit

The bounded commit is `docs: close DI-001 as application composition` and contains
only these six documents:

- The unchanged frozen DI proposal.
- The unchanged frozen challenger audit.
- This owner-decision record.
- Root `README.md` architectural-frontier status.
- `CLAUDE.md` current status guidance.
- `backend/model_kernel/README.md` current package status.

No historical accepted record is rewritten. No implementation, production code,
new tests beyond documentation assertions, authoritative fixture/ledger mutation,
new identity, canonical record, membership, generated artifact, successor proposal,
branch, ADR allocation, push, merge or history rewrite is authorized or performed.
Only the explicitly requested documentation commit is made. Stop after the receipt.

END OF DI-001 APPLICATION COMPOSITION OWNER DECISION
