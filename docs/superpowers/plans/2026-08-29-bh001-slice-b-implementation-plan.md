# BH-001 Slice B — read-only kernel query implementation plan

Status: Slice A implementation owner accepted at
`57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`, with acceptance recorded by the
separate administrative commit
`c39c674a95ad04c68250e23e86b169399a9547dd`. Slice B is owner accepted at
`05177f7306ce745d093bd5f11abafc13a6274d0f`. BH-001 Slices A and B are owner
accepted. Slice C is implemented and adversarially reviewed; awaiting owner
acceptance. Slice D has not started.

Slice B starting HEAD: `c39c674a95ad04c68250e23e86b169399a9547dd`.

Authoritative specification:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`.

## 1. Slice boundary

Slice B adds exactly four read-only methods to the existing `ModelQueries`:

```text
behavior(behavior_anchor_id)
behavior_declaration(behavior_anchor_id, *, context)
behaviors_involving_variable(variable_anchor_id, *, context)
behavior_assertion(record_id)
```

It adds only their model-kernel result contracts, literal aliases, public
exports, deterministic derivation, store-independent hostile revalidation,
tests, and documentation. It composes one injected `LoadedModel` and owns no
store, path, cache, projection, database, or write capability.

Slice B does not add `backend/behavior_evaluation`, numeric parsing, temporal
selection, model-state composition, ports, VPA, participant roles, inference,
or committed records. It does not change Slice A contracts, canonical bytes,
effective-body definition, store admission, indexes, memberships, or fixtures.

## 2. Exact public surface gate

Red-first tests pin the four method names and signatures, with `context`
keyword-only, and reject aliases or behavior-by-port methods.

Add exactly these six BH-specific aliases in their stated literal order:

```text
BehaviorLookupStatus
  not_registered | registered

BehaviorDeclarationConclusion
  not_registered | not_declared | declared | conflicted | inactive

BehaviorRuleLineageSummary
  not_applicable | healthy | conflicted | inactive

BehaviorAgreementFinding
  one_healthy_root
  corroborating_healthy_roots
  same_root_conflict
  cross_root_effective_body_disagreement
  inactive_roots_present

VariableBehaviorsStatus
  variable_not_registered | registered

BehaviorAssertionLookupStatus
  not_found | found
```

Reuse the accepted `AssertionActivity` and `ContainingLineageHealth` aliases.
The public package surface contains no evaluator or outcome vocabulary.

## 3. Exact result contracts

Pin exact ordered field sets and strict nonnegative integer indices:

```text
BehaviorEffectiveBodyGroupResult
  group_index
  representative_declaration_index
  current_tip_indices
  root_record_indices

BehaviorRuleRootResult
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health
  effective_body_group_indices

BehaviorLookupResult
  material
  behavior_anchor_id
  status
  registration_index
  participant_variable_registration_indices
  participant_owner_registration_indices

BehaviorRuleResult
  material
  behavior_anchor_id
  context
  conclusion
  lineage_summary
  agreement_findings
  registration_index
  roots
  effective_body_groups
  current_declaration_indices

VariableBehaviorEntry
  entry_index
  behavior_anchor_id
  other_variable_anchor_id
  behavior_registration_index
  other_variable_registration_index
  other_owner_registration_index
  conclusion
  lineage_summary
  agreement_findings
  roots
  effective_body_groups
  current_declaration_indices

VariableBehaviorsResult
  material
  variable_anchor_id
  context
  status
  variable_registration_index
  owner_registration_index
  entries

BehaviorAssertionDisclosureResult
  material
  record_id
  lookup_status
  record_index
  activity
  containing_lineage_health
  containing_subject_conclusion
  containing_agreement_findings
  root_record_index
  successor_indices
  withdrawal_indices
```

Complete model records, evidence, authority, context, ancestry, and revision
occur once in `ModelQueryMaterial`. Rows carry indices only. Read-only
properties may resolve those indices through private carried material.

## 4. Canonical root and body derivation

For one exact `(behavior_anchor_id, AssertionContext)` key:

1. collect declaration IDs only from `behavior_rule_ids_by_key`;
2. derive unique root IDs through `behavior_rule_root_by_id`;
3. order roots by root record ID;
4. order each complete lineage, active tips, and withdrawals by record ID;
5. set root health to `inactive`, `healthy`, or `conflicted` from active-tip
   count zero, one, or more than one;
6. project every active tip, including tips in a conflicted root, through the accepted private
   `_behavior_effective_body_bytes()` helper without changing its fields;
7. group tips by exact projected bytes and order groups by those bytes;
8. choose the lowest record ID in a group only as its disclosed deterministic
   representative, never as a winner;
9. order each group's tips and roots by record ID;
10. link each active root to the indices of every group containing one of its
    tips; inactive roots carry an empty group-index tuple.

Every active tip is grouped for disclosure. Only healthy roots vote for
cross-root corroboration or disagreement. Inactive roots cast no vote but
remain disclosed. A same-root fork is conflicted even if both tips fall in one
effective-body group, and its multiple groups alone do not create a
cross-root-disagreement finding.

## 5. Aggregate lifecycle and agreement derivation

Conclusion is derived exactly:

| Registration | Roots/current tips | Active engineering bodies | Conclusion | Summary |
|---|---|---|---|---|
| absent | not evaluated | not evaluated | `not_registered` | `not_applicable` |
| present | no roots | none | `not_declared` | `not_applicable` |
| present | roots, no active tips | none | `inactive` | `inactive` |
| present | any same-root fork | any | `conflicted` | `conflicted` |
| present | healthy active roots | one group | `declared` | `healthy` |
| present | healthy active roots | multiple groups | `conflicted` | `conflicted` |

Agreement findings are a canonical tuple in the public literal order. Include
each fact independently when true: exactly one healthy active root, at least
two healthy roots sharing one body, a same-root conflict, healthy roots
spanning more than one effective body, and any inactive root. Findings never
choose a winner and never describe real-system health. Thus A/A/B healthy
roots disclose both corroboration and cross-root disagreement; mixed healthy,
conflicted, and inactive roots retain every applicable finding.

## 6. Query semantics

`behavior()` returns permanent registration disclosure. A valid absent anchor
returns `not_registered`, `registration_index=None`, and empty participant and
owner tuples. A found registration aligns its two participant VRG and owner
registration indices with the canonical BRG pair; same-owner indices may
repeat.

`behavior_declaration()` returns only the exact requested context. Registration
absence, registered-without-declaration, inactive, same-root conflict,
cross-root disagreement, one healthy root, and corroborating roots are all
structured results, not exceptions.

`behaviors_involving_variable()` returns `variable_not_registered` and an
empty tuple for an absent variable. For a registered variable it returns every
permanent BRG containing that variable, ordered by behavior anchor ID,
including exact-context `not_declared` and inactive entries. It never infers a
behavior from ownership or other model facts. Entry indices are contiguous
from zero and no operand/input/output position is exposed.

`behavior_assertion()` validates `brg_`, `bhd_`, or `bhw_` shape before model
index access. A valid absent ID returns `not_found`. A BRG and BHW disclose
their record indices but no lifecycle/root fields. A BHD discloses direct
successors, withdrawals, activity, containing-root health, and aggregate
exact-subject conclusion/findings as independent dimensions.

For an absent ID or a found BRG/BHW, scalar lifecycle/root fields and the
subject-specific `containing_agreement_findings` field are explicitly `None`;
only `successor_indices` and `withdrawal_indices` are canonical empty tuples.
For a found BHD, `containing_agreement_findings` is the canonical tuple,
including an empty tuple when no finding applies.

## 7. Authoritative reconstruction gate

Every result is frozen, extra-forbidden, and fully revalidated. Outer
validation reconstructs nested serialized content, rebuilds the selected model
through `ModelQueryMaterial.loaded()`, and recomputes every registration,
owner, exact context, root, ancestry, successor, withdrawal, active tip,
engineering-body group, finding, conclusion, index, and ordering decision.

Reject `model_construct` and `model_copy` forgeries; stale record IDs; missing,
duplicate, extra, reordered, or substituted material/rows; mixed memberships,
contexts, subjects, and revisions; wrong union arms; forged representatives,
groups, tips, withdrawals, activity, root health, corroboration, findings,
conclusions, and contiguous indices; booleans and coercible index values.
Validation accesses no store or filesystem and performs no write.

## 8. Red-first test groups

Create focused files for:

1. exact public contracts, literals, fields, signatures, exports, and absent
   aliases;
2. registration lookup and reverse variable discovery;
3. exact-context declaration roots, body groups, findings, and ordering;
4. same-root chain/fork/convergence and independent-root corroboration versus
   disagreement;
5. withdrawals, inactive roots, selective fork-tip withdrawal, and historical
   revival;
6. BRG/BHD/BHW assertion disclosure;
7. authoritative hostile reconstruction and strict-index attacks;
8. pre-BH 9/10/11/14/16/18/28/29 structured absence;
9. non-inference and import/store/filesystem isolation;
10. deterministic serialized output under reversed inputs and hash seeds.

Record the public-contract failure count against the unmodified accepted Slice
A production boundary before implementing results or methods.

## 9. Production change boundary

Production changes are limited to:

```text
backend/model_kernel/behavior_results.py
backend/model_kernel/queries.py
backend/model_kernel/__init__.py
backend/model_kernel/README.md
```

Use a dedicated result module that reuses the accepted public
`ModelQueryMaterial`, `AssertionActivity`, and `ContainingLineageHealth`
contracts. Query/result derivation may import the private effective-body helper
inside `backend.model_kernel`; no private helper becomes public.

Do not edit Slice A contracts, canonical field projection, or store indexes.

## 10. Specialist review gate

Obtain independent software-architecture, backend-implementation,
software-test, and final code-integrity reviews. Require concrete reproductions
for suspected defects, reconcile every accepted correction red-first, and
reject scope expansion into Slices C or D.

## 11. Verification matrix

Run and record exact counts for:

1. focused Slice B public, semantic, lifecycle, and revalidation tests;
2. all BH Slice A+B tests;
3. complete `tests/model_kernel/`;
4. affected identity, VP, PT, CN, ES, VS, VM, and historical replay suites;
5. architecture/import-isolation tests;
6. complete repository suite, with loopback permission reported separately if
   needed;
7. fresh base-only checkout at final committed HEAD;
8. fresh all-extras checkout at final committed HEAD;
9. focused OCP/STEP and PDF suites;
10. backend compilation;
11. `git diff --check`, branch topology, remote status, and clean worktree.

## 12. Reviewable commits and stop gate

Use reviewable groups:

```text
docs: plan BH-001 Slice B
test: define BH-001 Slice B query contracts
feat: add BH-001 read-only kernel queries
test: harden BH-001 Slice B reconstruction
fix: repair BH-001 Slice B adversarial findings  # only if reproduced
docs: record BH-001 Slice B verification
```

Write the final report to
`docs/superpowers/reports/2026-08-29-bh001-slice-b-completion-report.md`, commit
it, and stop for owner acceptance. Do not begin Slice C or D.

END OF BH-001 SLICE B IMPLEMENTATION PLAN
