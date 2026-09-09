# FC-001 Slice A completion report

Implementation and verification complete; awaiting owner acceptance of Slice A.

Date: 2026-09-09. Branch: `fc001`.
Exact tested implementation: `87473729a2d7cd9c62c2c5660a54f34de2e590e9`.
Scope: accepted documentation reconciliation and Slice A only.

## 1. Outcome and owner boundary

Slice A implements the durable, evidence-bearing governing designation and its
withdrawal, exact structural dependency closure, canonical identity, lifecycle,
store/replay integration and twelve immutable indexes. It adds no FC anchor,
minter, sibling store, evaluator, query/result/status surface or upper dependency.

The execution clarification is preserved: stale content-derived IDs, forged or
substituted support and invalid structural closure reject. Valid retained
historical/non-current support remains structurally admissible. Slice A does
not calculate applicability or support-currentness conclusions. A retained
historical witness never floats to another FMA record.

Slice B is unstarted and unauthorized. The completion report does not claim
FC-001 is complete or owner accepted. Separate Slice A acceptance and Slice B
authorization are required. No authoritative append or demonstration slice has
been performed. Nothing was pushed or merged.

## 2. Verified baseline, frozen authority and commit topology

The accepted local `main` checkpoint remains
`c0e1c8fe930e10243fec16a4950a3d34d4c85df4`; `origin/main` remains
`d888ba6fbfb313cf2f85ce5cb07168fb528ec059`. Their one-commit difference is the
accepted documentation-only FA feasibility closeout, not a discrepancy.
`fc001` was created from that accepted local checkpoint.

Before production changes, the live repository guidance, architecture/frontier
documents, ADRs 0001–0021, accepted FM/CN/FL/VP specifications and all three
frozen FC artifacts were read. Architecture/backend/test/reviewer instructions
were inspected and applied to bounded implementation and review tasks.

| Frozen artifact | SHA-256, unchanged |
| --- | --- |
| [Lead proposal](../proposals/2026-09-09-fc001-codex-lead-proposal.md) | `8a65e3a4721fc0ba3dc28b0772e920f2dcc3008a9e1411ce07c9a8d1b204749e` |
| [Challenger audit](2026-09-09-fc001-codex-lead-proposal-challenger-audit.md) | `35d8537e2b1dc17775e2e96b0c021c4387ee1b6cd02265d861d17974b6e3d94f` |
| [Corrected final synthesis](../specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md) | `7aa5007058c1733720fc624839c19efd98258c800c67461d1afc5ade674a3453` |

All 27 fixed decisions, C1 and N1–N5 remain normative; none was amended.
The [design-owner approval](2026-09-09-fc001-final-design-owner-approval.md),
[ADR-0022](../../adr/0022-explicit-flow-operating-criterion.md),
[Slice A plan](../plans/2026-09-09-fc001-slice-a-implementation-plan.md) and
[adversarial matrix](../plans/2026-09-09-fc001-slice-a-adversarial-acceptance-matrix.md)
record the authorization and historical-support clarification.

| Commit | Purpose |
| --- | --- |
| `874775985071edca027cda8fdfc491324bfe31b3` | Separate documentation checkpoint: frozen inputs, approval, ADR-0022, bounded plan/matrix and frontier wording |
| `934041ef84e4ab6d819b9c818b1b1246463cd343` | Exact bounded record contracts, canonical/builders and append-only exports |
| `dedeffda8de139500e9023550f460d38c59b31ae` | Store, retained closure, lifecycle/indexes, replay and compatibility-test reconciliation |
| `e49e7364c1ef14be6dbbf749f007baa9004363a5` | Deterministic failure-order repair, review coverage and permanent disposable witness |
| `87473729a2d7cd9c62c2c5660a54f34de2e590e9` | Complete-kernel import-isolation and inventory repairs; exact tested implementation |

The subsequent report commit contains this report only. No amend, rebase,
reset, cherry-pick or history rewrite was performed.

## 3. Changed files

The tested range changes 35 files; the report adds one documentation file.

- Frontier wording: `CLAUDE.md`, root `README.md`, `backend/model_kernel/README.md`.
- Design checkpoint: the three frozen artifacts above, ADR-0022, owner approval,
  Slice A implementation plan and adversarial acceptance matrix.
- Runtime, all within `backend/model_kernel`: `contracts.py`, `canonical.py`,
  `flow_operating_criterion_validation.py`, `store.py`, `__init__.py`.
- New disposable tests/helpers: `fc001_slice_a_helpers.py`,
  `fc001_slice_a_reproduction.py`, `test_flow_operating_criterion_records.py`,
  `test_flow_operating_criterion_store.py`,
  `test_flow_operating_criterion_determinism.py`, all under `tests/model_kernel`.
- Existing export assertions reconciled, preserving their historical surfaces:
  `test_flow_measurement_slice_a.py`, `test_flow_measurement_slice_b.py`,
  `test_variable_registration.py`, `test_variable_port_records.py`,
  `test_variable_port_query_contracts.py`, `test_behavior_records.py`,
  `test_behavior_query_contracts.py`, `test_state_query_contracts.py`,
  `test_transition_architecture.py`, `test_transition_query_contracts.py`,
  `test_flow_architecture.py`, `test_flow_query_contracts.py`,
  `test_structural_evidence_arm.py`, `test_port_records.py`,
  `test_variable_value_specification.py`.

No identity, authoritative model, fixture, captured evidence, interpretation,
showcase, accepted disclosure/artifact or local settings file changed.

## 4. Exact record, canonical and public-surface contracts

`FlowOperatingCriterionDeclaration` uses kind
`flow_operating_criterion_declaration`, schema version `1`, prefix `fcd_` and
these eleven fields in order:

1. `record_kind` — fixed discriminator, defaulted.
2. `schema_version` — fixed `1`, defaulted.
3. `record_id` — required exact `fcd_` plus 64 lowercase hex digits.
4. `flow_measurement_association_record_id` — required exact positive FMA ID.
5. `constraint_registration_record_id` — required exact CRG ID.
6. `constraint_declaration_record_id` — required exact VCN ID.
7. `evidence` — required nonempty tuple of the six accepted EvidenceRef arms,
   canonically deduplicated and ordered.
8. `supersedes` — unique sorted tuple of positive FCD parents, default `()`.
9. `recorded_at` — required accepted UTC-normalized datetime.
10. `authority` — required accepted AuthorityRef.
11. `note` — exact string, default `""`.

`FlowOperatingCriterionWithdrawal` uses kind
`flow_operating_criterion_withdrawal`, schema `1`, prefix `fcw_` and these seven
fields in order: `record_kind`, `schema_version`, `record_id`, `withdraws`,
`recorded_at`, `authority`, `note`. The target is one eligible positive FCD.
The withdrawal carries no evidence or parents and is uncitable.

Both contracts are frozen, extra-forbid and fully revalidating. Public semantic
construction remains the accepted generic `build_record`; no FC builder alias
or minter is exported. The existing plain `ModelRecord` union appends the two
arms, without a global union redesign. Filename grammar and canonical dispatch
admit only the new exact prefixes. Positive FCD citations are admitted; FCW
citations are not.

Record IDs hash sorted compact UTF-8 canonical content, normalized UTC, without
the record's own ID or final newline. Evidence, authority, ancestry and the
exact witness remain in record identity. Independent literal golden vectors:

| Record | Hash-input bytes | SHA-256 / record-ID suffix |
| --- | ---: | --- |
| FCD | 620 | `349beafa7c5a8ada903aab71744ea2c114663d2f8a4b60d4f216e90c407bff82` |
| FCW | 293 | `f009e4dff05c619c394c4fe86b8a66cee936750fd8647bab4bc347a96b929486` |

`backend.model_kernel.__all__` is exactly **227 unique ordered names**. The
accepted 225-name prefix is unchanged, followed only by:

```text
FlowOperatingCriterionDeclaration
FlowOperatingCriterionWithdrawal
```

Compact ASCII JSON of the prefix is 5,838 bytes, SHA-256
`097fe647d38bfd0947d1cac94583a1fd50bda5c15b5386ac3137c781097e414a`.
The complete surface is 5,909 bytes, SHA-256
`756698e83e44948ed24646d2808b9cfeb1f0d8c6f7d7650b2d61c455851afefd`.
Historical tests inspect their accepted prefix/suffix positions, not an expanded
fictional historical surface. No Slice B export is present.

## 5. Structural closure, lifecycle and retained-history boundary

The immutable correction subject S is the exact FM subject: flow, variable,
participant port, context, fixed direct-measurement-relevance relationship and
orientation. The governed FM body B includes its exact six support pins.
FC body equality is canonical full-byte equality of reconstructed FM body,
exact CRG ID and exact VCN ID. It excludes nominated-witness identity, authority,
evidence and ancestry without removing any of that provenance from stored records.

Collection admission reconstructs trusted instances and IDs, reruns all lower
registration/constraint/port/FL/VPA/VSM/FM invariants, resolves the exact retained
witness and CRG/VCN, checks variable/anchor/role coherence, evidence closure,
parent/root/cycle/withdrawal rules, then publishes complete indexes and revision.
The exact measured-actual token is
`project_local/ohk-observation-roles-1/measured_actual`. VSM remains
context-independent. No quantity/unit/predicate/source evaluation is introduced.

Retained superseded, withdrawn, conflicted and inactive support loads and
replays. Omitting the nominated witness rejects even if an equal-body FMA exists.
The old FC VCN pin does not float after an apparently identical VCN correction.
An explicit same-root FC renewal changes the exact pin/body while retaining S,
root and history. Currentness-based applicability belongs exclusively to Slice B.

Same-root equal-body forks remain forks; explicit convergence preserves one
root. Independent equal-body assertions remain separate corroborating roots;
different bodies remain separate groups. Inactive roots retain history without
being erased. No ID, authority, timestamp or ordering becomes a winner.
Withdrawals target exact eligible positive tips; duplicate/ineligible targets
and successors of withdrawn parents reject. Membership-closed replay may revive
a tip by omitting its withdrawal, but cannot omit its required dependencies.

Twelve copied immutable mappings are provided on LoadedModel, each prefixed
`flow_operating_criterion_`:

```text
declarations                    withdrawals
subject_by_id                   ids_by_subject
parent_ids                      successor_ids
root_by_id                      ancestry_by_id
current_tips_by_root             withdrawn_by
effective_body_by_id             ids_by_effective_body
```

Tip values are sorted FCD IDs, not records. Index iteration, subject ordering,
orientation rank and full effective-body group preservation are deterministic.
These are structural lifecycle facts, not new applicability statuses.

Append validates candidate/hash, complete existing membership (including
idempotent append), then prospective membership before staging or atomic
promotion. Failed structural validation leaves record bytes, membership,
revision and staging unchanged. Historical replay rebuilds all closure/indexes.

## 6. Genuine red-before/fixed-after evidence

The repository TDD, subagent-driven implementation and verification skills were
used. Counts below are observed executions, not fabricated acceptance counts.
Repeated red rounds overlap; they must not be summed as distinct failing tests.

| Stage | Actual red or diagnostic evidence | Fixed/covering evidence |
| --- | --- | --- |
| Record foundation, before production changes | 41 failed in 5.12s: absent FC contracts and 225-versus-227 surface; no collection errors | Final record module 52 passed; canonical/FM group 161 passed in 49.97s |
| Canonical forged-instance boundary | 2 failed, 43 passed | Full-instance canonical revalidation repaired; included in 52/161 |
| Metadata and value-free errors | 1 failed, 50 passed; then 3 failed, 48 passed, including repeated metadata failure | Strict fields-set checks and fixed input-free parent errors repaired |
| Ambient JSON integer conversion | Strengthened regression genuinely failed once; initial weaker probe passed and was not counted as a defect | Chunked bounded parsing independent of interpreter digit cap |
| Store/lifecycle, corrected pre-production tests | 38 failed, 3 passed in 4.39s; no collection/setup failures | First integration 41 passed in 3.68s |
| Arbitrary serializer impersonation | 1 failed, 59 passed | Exact accepted record-class gate; both FC modules 112 passed |
| Subject and mapping order | 2 failed, 60 passed | Frozen orientation rank and deterministic map iteration; 114 passed |
| Missing trusted-instance metadata | 3 failed, 81 deselected | Strict outer validator normalization; 136 FC tests passed |
| Post-default stored-record size error | 1 failed, 84 deselected | New-prefix limit translation repaired; 137 FC tests passed |
| Historical current-export assertions | 10 failed plus 1 separate failure, all `227 == 225` | Fifteen selected export tests passed; historical prefix meanings retained |
| Post-review deterministic errors/key callback | 4 failed, 1 already-green: two invalid/limit permutations, stale-ID hash diagnostic order, hostile key callback | Five covering checks passed; structural-before-hash was already correct |
| A04/A12/A21 review coverage additions | Eleven cases passed immediately; not claimed as failing-before fixes | Six evidence arms, authority cross-product and same-root exact-edition renewal covered |
| Independent store/index witness | New permanent five-seed test passed | Twelve separately constructed worlds; direct/load/replay and actual index iteration agree |
| First complete-kernel candidate at e49e736 | 4 failed, 1900 passed in 1070.76s; independently reproduced 4 failed in 3.42s | Public-Pydantic-only validation mechanism and three inventory assertions repaired; 455 focused tests passed in 71.73s |
| Parsed-timezone/error preservation | Seven timezone cases already passed before the import repair; four exact error-route cases added | Exact trusted timezone type and fixed error shapes preserved; no fabricated red claim |

Test-authoring mistakes were corrected and excluded from feature-defect
evidence: two golden tests referenced the canonical helper from the wrong module
during the initial implementation run, after the first genuine 41-red checkpoint.
Store setup briefly used an invalid role system and placeholder parent; those
were corrected before the cited 38-red store checkpoint. Two exploratory long
kernel runs were interrupted before completion. A later agent-owned pre-last-fix
kernel run had no recoverable completion receipt; it is not counted. The final
exact-commit suite below supersedes those incomplete runs.

The post-review covering group passed 347 tests in 99.06s. Production/witness
code was final at start; an extra FC-alone assertion was added during that run
and rerun separately (4 passed). Final exact-commit focused verification is
reported separately and includes every committed assertion.

The first complete-kernel run found an actual import-boundary violation
(`pydantic_core` in the new helper) and three stale inventory assertions (225
exports / 30 record families). The allowlist was not weakened. Public Pydantic
validation of a static timestamp obtains the exact trusted timezone class;
four fixed public discriminator-error adapters preserve the required error
shapes without private imports. Inventory checks retain all old names/vectors
and add the exact two FC names / 32-family consistency. Both backend and
adversarial scoped reviews approved the repair without new findings.
Four other incomplete long runs at e49e736 were interrupted with exit 130.
No partial candidate run is counted as final verification. New clean checkouts
and new environments were created for the complete replacement matrix.

## 7. Architecture, backend, test and adversarial reviews

Four specialized post-green reviews assessed both the accepted contract and
the original mission. Review judgments are not test counts.

| Review | Findings and final disposition |
| --- | --- |
| Architecture | Task 1 and integrated Task 2 approved. No critical/important issue. One Task 1 minor observation: redundant bounded canonical revalidation is correct; profiling-only consolidation was not pursued. |
| Backend | No critical/important defect. One minor deterministic malformed-FC failure-order discrepancy, reproduced and repaired with red regressions. Scoped re-review approved. |
| Test | Three important coverage gaps, not observed runtime defects: authority-dependent withdrawals, explicit same-root VCN renewal, six evidence arms. All added and independently re-reviewed as addressed. |
| Independent adversarial | Approved with no confirmed implementation finding. Disposable probes independently verified retained withdrawn witness plus superseded VCN, omission refusal, stale-ID rejection, and withdrawal/successor rejection. Scoped repair review approved. |

All required findings are closed. Re-review found no new critical/important
breakage and verified that actual index-row order is not sorted away by the
deterministic witness. No reviewer changed production files or claimed broad
tests they did not run. Backend review independently ran six focused checks
(6 passed in 2.62s); other reviews used code inspection and bounded probes.

The complete-kernel gate subsequently detected the import/inventory failures
described in Section 6 despite those earlier reviews. The final repair received
separate backend and adversarial scoped approvals. Automated architecture and
complete-suite checks remain independent acceptance gates, not substitutes for
or consequences of reviewer approval.

The exact-class runtime gate intentionally rejects arbitrary serializer objects
and record subclasses before callbacks. Exact accepted old record classes keep
their existing reconstruction path. This bounded hardening prevents hostile
objects impersonating FC records; accepted old-family behavior and artifacts
are verified by the regression and preservation gates.

## 8. Exact-commit verification matrix

All final commands test `87473729a2d7cd9c62c2c5660a54f34de2e590e9`.

| Gate | Result |
| --- | --- |
| Focused FC records/store/determinism | 165 passed in 27.09s |
| Complete model-kernel | 1915 passed in 898.50s |
| Affected consumers/architecture/isolation | 1521 passed in 996.26s |
| Complete working repository | 4060 passed, 1 loopback setup error in 2280.69s; isolated permitted loopback rerun: 1 passed |
| Fresh base-only complete repository | 4025 passed, 35 optional-dependency skips, 1 loopback setup error in 1848.70s; isolated permitted loopback rerun: 1 passed |
| Fresh all-extras complete repository | 4060 passed, 1 loopback setup error in 1859.56s; isolated permitted loopback rerun: 1 passed |
| Separate CAD/STEP/PDF gate, fresh extras | 120 passed in 53.12s |
| Dependency consistency, all three environments | No broken requirements found |
| Backend compilation, all three environments | Exit zero |
| FC/FM/EA/TA artifact parity, all three environments | Exact bytes and hashes match Section 10 |
| Working and fresh preservation | Pass; ignored raw/settings checked in working tree only |
| Documentation/status links, markers and ADR sequence | Pass; local links resolve, exact ending markers match, ADRs 0001–0022 contiguous |
| Working-tree and full milestone whitespace | `git diff --check` and accepted-base-to-HEAD check pass |

FM/FL/VP/VS and their architecture/isolation coverage are included in the
complete kernel gate. The affected gate additionally covers CN, identity,
observation/semantic compatibility, ES, model state, ST, BH, TA, EA/alignment
and the EA architecture/reproduction tests. Full suites cover the remaining
source, temporal, connector and ingestion responsibilities.
The separate kernel and affected gates run from the final all-extras checkout
using its own environment. The complete working suite runs in the shared
repository using the existing working environment; all source commits match.

## 9. Fresh environments and sandbox reconciliation

Fresh detached checkouts, both verified clean at the exact tested commit:

- Base: `/tmp/fc001-slice-a-final-base-DIdH07/checkout`, with a newly created sibling
  `/tmp/fc001-slice-a-final-base-DIdH07/venv`.
- All-extras: `/tmp/fc001-slice-a-final-extras-5ZxAcO/checkout`, with its own newly
  created sibling `/tmp/fc001-slice-a-final-extras-5ZxAcO/venv`.

Both environments installed `requirements.txt` and `requirements-dev.txt`.
Extras additionally installed `pip install --require-hashes -r requirements-cad.txt
-r requirements-pdf.txt`. Environments were prepared separately before final
checkout creation; requirements remained byte-identical at the tested commit.
No failed-candidate or warmed verification environment was reused. Initial
candidate sandbox dependency installation failed DNS; explicitly permitted
installations succeeded. The new final environments were installed through
permitted invocations after that restriction was established.

All environments use Python 3.13.11 and pytest 9.1.1. Working Pydantic is 2.13.4;
both fresh environments resolved 2.13.5. Base has no OCP/pdfplumber/pypdf/pypdfium2;
extras has all four. Final `pip --no-cache-dir check` is clean in all three.
An earlier ordinary pip check emitted only the sandbox's unwritable-cache
warning; no dependency conflict was found.

Requirements SHA-256:

```text
requirements.txt      783e219f8fd03bd79eb7d0a21d96fc6bd31b4778d8c1509c684adcc5e4f7e9b7
requirements-dev.txt  e8df7d69da1b48125985fb4cb0b8c015103baa89db1f5f86796da1753522a3f1
requirements-cad.txt  30c4842f0824ee05149d5db2303a6bfd79dd009173d69b657f34cb4024dcd1d6
requirements-pdf.txt  bbe625db9d3748b3f475c3fb5d27505b5c8cf230029bf758a55577e10a246e43
```

The isolated real-loopback target is
`tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation`.
Sandbox probes fail at socket creation with `PermissionError: [Errno 1]
Operation not permitted`: working 1 error in 2.52s; base 1 error in 0.34s;
extras 1 error in 0.31s. Explicitly permitted isolated reruns at the final commit
pass: working 1 passed in 1.94s; base 1 passed in 0.76s; extras 1 passed in 0.75s.

All three final aggregate logs identify exactly that loopback setup error and
no test failures or additional errors. Each aggregate exits 1 because of the
sandbox setup restriction. The three permitted isolated reruns exit zero.
This is split verification evidence, not a claim of an uninterrupted passing
full-suite invocation. Base records 4025 passes and 35 skips; working and extras
each record 4060 passes. Together with each independently passing loopback
rerun, all 4061 collected cases are accounted for (including the base skips).

## 10. Deterministic witnesses and accepted artifact parity

The permanent FC test independently constructs twelve temporary public-builder/
ModelStore worlds: forward/reverse locally, then both orders under seeds
`0`, `1`, `7`, `42`, `12345`. Dependency order remains valid while independent
siblings, evidence/parent inputs, collection membership and replay selectors
are reversed. No authoritative file or generated fixture is used.

The FC witness contains 26 records: 7 FCD, 1 FCW, 3 FMA, 1 FMW and retained
lower support, including old/renewed VCNs; two subjects, four roots, three body
groups. Its disposable revision is
`mrv_c7df43e3003155cce136d2943644abff51601b9280d4e25eeea2873b7724060d`.
Canonical record bytes and actual stored bytes are preserved as hex. All twelve
indexes are captured as actual iteration arrays for direct validation, load
and replay; outer JSON key sorting cannot hide row-order defects.

Direct reproductions in working, fresh base and fresh extras all match:

| Witness | Bytes | SHA-256 |
| --- | ---: | --- |
| FC Slice A canonical/stored/index witness, forward and reverse | 207,058 | `4ac4e79c53c5e8c04c27c464e400f0d799d79df56a47279d99c9d00cce3abbc9` |
| Accepted FM Slice B witness, forward and reverse | 245,676 | `b65567aae97c7dc3c6913a12ab52c78e329a99fedcb40bfa1b9bc36f69a40839` |
| Accepted EA source/newline/temporal material | 24,766 | `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7` |
| Accepted TA private canonical result | 195,429 | `1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97` |

FC reproduction is
`tests/model_kernel/fc001_slice_a_reproduction.py:witness_bytes`;
FM uses the existing `fm001_slice_b_reproduction.py:witness_bytes`.
EA uses `_captured_lower_material`; TA uses disposable `build_world`, public
assessment and its accepted private canonical serializer. These latter calls
verify unchanged lower artifacts; FC runtime never imports or calls them.

## 11. Ledger, revision, identities and protected digests

The authoritative model remains exactly **36 records** at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW = **1/1/0**; TRG/TRD/TRW = **0/0/0**;
FMA/FMW = **0/0**; FCD/FCW = **0/0**.
An authoritative FC append over nonexistent FMA support was neither proposed
nor performed. Existing Constraint/Flow/Variable/Port anchors are unchanged.

Sorted filename-to-file-SHA record inventory digest:
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The accepted inventory encoder uses compact sorted ASCII JSON plus a newline;
it is separate from record canonical hashing. All accepted historical replay
memberships remain covered by the kernel regression suite and unchanged files.

| Protected tree | Files | SHA-256 inventory digest, unchanged |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| Working `var/raw_store` | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

Tracked trees match in all three checkouts; ignored captured raw data is checked
only in the working checkout and is not copied into clean environments.
`.claude/settings.local.json` is unchanged, ignored and uncommitted, SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.
No pre-FC record, identity, membership, canonical byte, artifact logic or
accepted disclosure was rewritten.

## 12. Original product-objective contribution

The initial consumer is commissioning/operations verification. The durable fact
is an authority's exact criterion designation, independent of observations or
favorable predicate outcomes. It is not a repackaging of lower admission status.

| Original mission question | Slice A contribution | Still unavailable |
| --- | --- | --- |
| What exists in this system, and how is it connected? | Exact governing declaration and typed dependency closure exist in selected model membership. | No inferred physical connectivity or physical flow. |
| What is the current state of this particular system? | Foundation only: records the governing choice needed by later bounded sample verification. | No observation evaluation, applicability result or current physical state. |
| Why might the system be behaving this way? | None. | Causality, diagnosis and explanation. |
| What is the next best measurement or test? | None; missing premises are not test optimization. | Measurement/test recommendation or planning. |
| What would be affected if a component, parameter or software version changed? | Exact retained dependency pins are inspectable. | No impact propagation or counterfactual assessment. |
| What is the smallest valid set of changes needed to reach a desired state? | None. | Change planning, optimization or control. |
| Which conclusions are observed, calculated, inferred, assumed or unknown? | Governing choice is explicitly authority-declared with evidence and historical provenance, not measured or inferred. | No additional engineering truth classification or physical certainty. |

Contract-theatre review passes for this foundation: changing the exact VCN
changes governing meaning, while same-body witness changes preserve body
equality without erasing historical provenance. This is durable authority
selection that arbitrary same-variable constraints cannot supply automatically.
The A-violated/B-satisfied consumer substitution proof is deliberately not
claimed by Slice A. It requires separately authorized Slice B queries and
existing CN/evidence joins. Review obligations are not fabricated test counts.

## 13. Limits and explicit non-guarantees

New record limits are enforced before expansion/caller callbacks and after
normalization: 131,072 canonical bytes including ID; 8,192 expanded nodes;
2,048 containers; depth 32; 64 evidence items and parents; 16,384 UTF-8 bytes
per nested string/key; authority agent 1,024; note 8,192; other containers 256;
raw JSON 1,048,576 bytes; integer 4,096 bits and 1,234 JSON digits. Exact and
one-over tests distinguish invalid shape from size refusal. Shared DAGs charge
every incoming edge; cycles reject. Store new-prefix reads use cap-plus-one.
Old record grammars and other query budgets are not globally capped by FC.

The protected boundaries are the exact FC class methods, semantic builder,
canonical validation and operational store/replay reconstruction. Adversarial
probes reproduced permissive duplicate-key parsing and subclass callbacks in
bare caller-created `TypeAdapter(ModelRecord)`. The frozen contract preserves
that plain union and puts raw FC preparse protection before store adaptation
and in exact outer class methods. Generic adapter preparse protection is not
claimed; no unsupported global union redesign was introduced.

Authority/evidence fields are declarations and carried provenance, not identity
authentication or cryptographic signatures. Foreign evidence is opaque; model
evidence must close in selected membership but is not recursively interpreted
as proof. Store atomicity retains the accepted single-writer boundary, not a
new concurrent-writer transaction guarantee.

FC never records satisfaction, violation, state, activity, occurrence,
continuity, conservation, causality, correctness, safety, diagnosis,
recommendation or permission to act. Slice A also does not assert present
applicability. Multiple legitimate simultaneous criteria remain unsupported
in v1; they are not false or encodable through artificial contexts/orientations.

## 14. Final verification commands and retained execution evidence

All pytest commands use `PYTHONDONTWRITEBYTECODE=1`,
`-m pytest -o addopts='' -p no:cacheprovider`, and `-q`.
Working executable is `.venv/bin/python`; each fresh checkout uses
`../venv/bin/python` from its own newly created environment. Kernel and affected
commands below are run from the fresh all-extras checkout.

```sh
# Focused FC
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/model_kernel/test_flow_operating_criterion_records.py tests/model_kernel/test_flow_operating_criterion_store.py tests/model_kernel/test_flow_operating_criterion_determinism.py -q

# Complete kernel, fresh extras checkout
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/model_kernel/ -q

# Affected consumers and isolation/architecture, fresh extras checkout
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/constraint_evaluation tests/identity_binding tests/observation_compatibility tests/semantic_compatibility tests/structural_evidence tests/model_state tests/state_classification tests/behavior_evaluation tests/transition_assessment tests/evidence_alignment tests/evidence_assurance tests/test_ea001_slice_a_architecture.py tests/test_ea001_slice_a_reproduction.py -q

# Complete working repository
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q

# Complete fresh base and extras, each from its checkout
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q

# Separate CAD/STEP/PDF gate from fresh extras checkout
PYTHONDONTWRITEBYTECODE=1 ../venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/data_sources/test_step_extractor.py tests/data_sources/test_ingestion_runner_step.py tests/data_sources/test_pdf_extractor.py tests/data_sources/test_pdf_detection_availability.py tests/data_sources/test_pdf_coordinates.py tests/data_sources/test_pdf_contracts.py tests/data_sources/test_ingestion_runner_pdf.py tests/structural_evidence/test_step_claims.py -q

# Each environment, using its own executable and separate temporary cache prefix
pip --no-cache-dir check
PYTHONPYCACHEPREFIX=/tmp/fc001-slice-a-final-verification-5dvYea/compile-working .venv/bin/python -m compileall -q backend

git diff --check
git diff --check c0e1c8fe930e10243fec16a4950a3d34d4c85df4..HEAD
git status --short
```

Actual stdout/stderr logs remain under
`/tmp/fc001-slice-a-final-verification-5dvYea`, with installation logs in
the two fresh environment parents. Superseded candidate logs remain separately
under `/tmp/fc001-slice-a-verification-oZnDss` and the earlier checkout parents.
Temporary logs are execution evidence, not
versioned product artifacts. Detailed task and review receipts remain in the
ignored `.superpowers/sdd/2026-09-09-fc001-slice-a-implementation-plan/` workspace;
the substantive results and limitations are recorded here for durable handoff.

## 15. Repository hygiene and final owner gate

The implementation working tree and both fresh checkouts are clean after
verification. The completion commit adds only this report. Working-tree and
full FC milestone `git diff --check` checks pass. Local settings remain ignored,
unchanged and uncommitted. The accepted local main and origin/main refs are
unchanged; no push or merge was performed.

The accepted 225-name prefix, historical ledgers/revisions, exact FMA witness
pins, frozen artifacts and local settings are preserved. ADR-0022 is the sole
new ADR and the sequence is contiguous through it. No successor ADR, branch,
authoritative append or milestone has been started.

FA-001 remains deferred during FC. After a successful accepted FC/CN/evidence
direct-join proof, cancel FA. Reconsideration requires a new owner-approved
proposal demonstrating a concrete integrity/substitution attack that explicit
checks over existing public results cannot prevent, stating the missing
property and why those checks fail. No identified attack qualifies. Convenience,
an aggregate object/status, smaller carriage or moving joins into a package
is insufficient.

Stop here for owner validation: accept Slice A and separately authorize Slice B?
Slice B, its applicability/query/result contracts and its disposable consumer
join demonstration remain unstarted and unauthorized. No push or merge occurred.

END OF FC-001 SLICE A COMPLETION REPORT
