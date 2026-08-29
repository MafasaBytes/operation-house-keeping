# BH-001 Slice A Final Independent Integrity Review

Date: 2026-08-29
Reviewer role: independent `code-reviewer` specialist
Reviewed branch: `bh001`
Reviewed repair HEAD: `1fb10097c2d0a97ecc007cef4034028c9a5668a2`
Accepted repository base: `46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`
Accepted design input: `docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md` at owner-accepted SHA-256 `2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978`
Review mode: read-only inspection and bounded verification; this report is the reviewer's only file change.

## 1. Review mandate

This review independently evaluates whether BH-001 Slice A implements only
the accepted identity and model-kernel record foundation and whether it does
so without weakening existing canonical, store, replay, or import boundaries.
It covers:

1. exact identity and record contracts;
2. public exports and the absence of premature public APIs;
3. canonical identity and evidence closure;
4. store validation order and atomicity assumptions;
5. lifecycle, ancestry, withdrawal, and immutable-index semantics;
6. hostile nested-instance and stale-ID revalidation;
7. deterministic ordering and input-order independence;
8. import direction and Slice B-D exclusion;
9. explicit historical replay and byte preservation;
10. reconciliation of the architecture, backend, and test specialist reports.

The review does not authorize or assess Slice B query behavior, Slice C
numeric evaluation, or Slice D ledger demonstration beyond proving that none
of them was started.

## 2. Verdict

**GREEN — no blocking defect remains in the reviewed Slice A implementation.**

The implementation matches the accepted narrow primitive: a permanent,
evidence-bearing registration of exactly two distinct unordered variables,
plus exact-context equality declarations and dedicated membership-relative
withdrawals. It does not add behavior inference, roles, direction, ports,
VPA meaning, evaluation, computed equality, or runtime composition.

One documentation-integrity defect was found during this final review: the
acceptance matrix still contained three superseded handwritten BRG/BHD/BHW
placeholder IDs while the executable public-builder golden tests pinned the
actual identities. The lead repaired the matrix before this verdict. Section
3 records the finding and closure. No production record vector or existing
record identity changed.

Full-suite and dual-clean-checkout execution remain completion activities for
the lead. The independent bounded checks in Section 14 are green.

## 3. Final-review finding and closure

### F1 — acceptance-matrix golden identities disagreed with executable vectors

Initial final-review observation:

- matrix C01 named `brg_61285...`;
- matrix C02 named `bhd_11a3...`;
- matrix C03 named `bhw_f422...`;
- the committed public-builder tests instead deterministically produced the
  three identities below.

Root cause recorded in the repaired matrix: the initial handwritten
placeholders cited variable-registration IDs not produced by the matrix's own
frozen builders. Red-first execution exposed the internal contradiction.

Closed state:

| Record | Accepted measured Slice A vector |
|---|---|
| BRG | `brg_ecd5a9b669f91dca639fde20202ce4f3c4ff17006d7f0ffd23f09ed44f1f9e3e` |
| BHD | `bhd_9e3af9219521d1b3c5dfd5d41ae359dc8d3fb4c5db4b002586998e52f0a823eb` |
| BHW | `bhw_4c2456b2a6473f6a37c47b9aadedc10b1a8610c80e6650ba70cdbd7b2dd938f6` |

The matrix now identifies these as measured public-builder identities, pins
the complete canonical bytes through the executable tests, and explains the
discarded placeholders. This is a documentation correction only. Finding F1
is **closed**.

## 4. Exact system-identity contract

The public identity surface is bounded and conforms to the repository's
existing conventions:

```text
BehaviorAnchor
  anchor_id
  namespace
  display_name
  role_name
```

- identity grammar is exactly `^bhv_[0-9a-f]{32}$`;
- `mint_behavior_anchor()` produces `bhv_` plus a lowercase UUID4 hex body;
- the anchor is frozen, extra-forbidden, and fully revalidated;
- the anchor has no owner, participant, context, rule, evidence, lifecycle,
  direction, state, or causal field;
- its inherited human-facing `role_name` field is naming metadata and is not
  a BH participant role or operational direction.

The exact `backend.system_identity.__all__` contains 13 established and BH
symbols, with only these three BH additions:

```text
BEHAVIOR_ANCHOR_ID_PATTERN
BehaviorAnchor
mint_behavior_anchor
```

No behavior query, evaluator, source selector, or computed-result symbol is
exported from this layer.

## 5. Exact model-record contracts

All new models use frozen, `extra="forbid"`, and
`revalidate_instances="always"` configuration. Their exact public fields are:

```text
BehaviorVariableSemanticLock
  variable_anchor_id
  signature

ExactNumericEqualityRule
  kind

BehaviorRegistration
  record_kind
  schema_version
  record_id
  anchor
  participant_variable_anchor_ids
  rule_family
  evidence
  recorded_at
  authority
  note

BehaviorRuleDeclaration
  record_kind
  schema_version
  record_id
  behavior_anchor_id
  context
  participant_semantics
  rule
  evaluation_basis
  evidence
  supersedes
  recorded_at
  authority
  note

BehaviorRuleWithdrawal
  record_kind
  schema_version
  record_id
  withdraws
  recorded_at
  authority
  note
```

The discriminator and identity contracts are exact:

| Type | `record_kind` | version | ID grammar |
|---|---|---|---|
| registration | `behavior_registration` | `1` | `^brg_[0-9a-f]{64}$` |
| declaration | `behavior_rule_declaration` | `1` | `^bhd_[0-9a-f]{64}$` |
| withdrawal | `behavior_rule_withdrawal` | `1` | `^bhw_[0-9a-f]{64}$` |

The registration pair is exactly two distinct variable anchor IDs. It is
canonically sorted and has no directional ordering. Its only rule family is
`exact_numeric_equality`. Registration has no assertion context, parents,
withdrawal target, lifecycle, participant roles, tolerance, or result.

Each declaration has exactly two unique semantic locks, canonically ordered
by variable ID. The lock signatures require exact quantity-kind and exact
unit identity across the pair; observation-role identity may differ. The rule
body contains only `kind="exact_numeric_equality"`. The basis contains only
`same_acquisition_cohort`. There is no expression, coefficient, offset,
tolerance, inequality, arithmetic operation, port, VPA, source selector, or
computed outcome.

The withdrawal targets exactly one shaped `bhd_` identity and contains no
evidence, context, parents, replacement, reason code, outcome, or negative
behavior assertion.

## 6. Canonical identity and serialization

Canonical support is complete and isolated:

- the model-record ID grammar and filename grammar admit `brg_`, `bhd_`, and
  `bhw_` with lowercase 64-hex digests only;
- the canonical `ModelRecord` discriminated union contains all three arms;
- prefix mapping is exact: BRG to `brg`, BHD to `bhd`, BHW to `bhw`;
- the public `build_record()` path revalidates nested content, canonicalizes
  unordered pair/lock/evidence/parent input, excludes `record_id`, and hashes
  canonical JSON bytes;
- reversed valid pair, lock, evidence, and parent inputs produce identical
  canonical bytes and IDs;
- duplicate parents are rejected before canonical sorting;
- malformed, wrong-prefix, wrong-kind, uppercase, short, long, or non-hex IDs
  fail the typed contract;
- stale IDs after content mutation and filename/content mismatches fail closed.

No existing canonical prefix mapping or serializer was altered beyond adding
the three new discriminated arms. Preservation tests replay existing records
and verify their record IDs rather than regenerating history from filenames.

Slice A also supplies one private deterministic effective-body primitive. Its
projection contains exactly:

```text
behavior_anchor_id
context
participant_semantics
rule
evaluation_basis
```

It excludes evidence, authority, recorded time, note, record ID, filename,
and append order. That is the accepted engineering-body identity required by
future Slice B corroboration. It is private, non-persisted, and does not
prematurely publish a conclusion or grouping API.

## 7. Evidence contracts and closure

The evidence boundary is correct:

- BRG and BHD are valid `ModelRecordEvidence` targets;
- BHW is deliberately not citable;
- all evidence tuples are non-empty and canonically ordered;
- hostile preconstructed evidence instances are reconstructed from serialized
  field content;
- generic model-record evidence closure runs for both BRG and BHD;
- a BRG must cite the exact two selected variable-registration records and
  contain at least one `OwnerDeclarationEvidence` claim basis;
- a BHD must cite its exact BRG and contain at least one
  `OwnerDeclarationEvidence` claim basis;
- both variable registrations and their owner entity registrations must close
  in the selected membership through existing registration validation;
- unrelated extra citations do not substitute for either exact required
  citation;
- missing and stale citations fail the prospective membership before write.

Cross-owner pairs are admitted only when an explicit evidence-bearing BRG is
present. The implementation neither rejects them merely for different owners
nor infers them from shared ownership. That preserves the accepted separation
between ownership and explicit behavior knowledge.

## 8. Validation order and atomic store behavior

The reviewed collection-validation order is defensible and preserves older
error precedence:

1. serialized union reconstruction and content-ID verification occur at the
   store boundary;
2. existing entity, variable, constraint, port, VP, relationship, and other
   pre-BH validation completes first;
3. only then are behavior registrations, declarations, DAGs, and withdrawals
   admitted;
4. withdrawals are checked after the complete successor graph exists;
5. the immutable `LoadedModel` is built only from the fully validated set.

This order was repaired after specialist review so an unrelated invalid
pre-BH record retains its accepted typed error precedence even when BH records
are present.

`ModelStore.append()` revalidates the candidate, verifies its content-derived
ID, loads and validates the current set, validates the entire prospective set,
and only then atomically promotes a staged canonical JSON file. Failed
reference, evidence, lineage, or withdrawal admission therefore occurs before
the authorized record file is written. Idempotent append still validates the
current ledger first.

Load rejects hostile on-disk union arms, malformed JSON, symlinks/non-ordinary
files, stale record IDs, and filename/content disagreement through typed model
integrity errors.

## 9. Lifecycle, correction, conflict, and withdrawal semantics

The declaration lineage key is exactly:

```text
(behavior_anchor_id, exact AssertionContext)
```

The store enforces:

- a parentless BHD starts one independent root;
- parents must be known BHD records with the exact same lineage key;
- duplicate parents and self-parenting are rejected structurally;
- cycles are rejected;
- a correction remains inside one root;
- multi-parent convergence is allowed only when all parents share that root;
- cross-root convergence is rejected;
- independent roots remain independently indexed for future Slice B body
  comparison;
- no authority, timestamp, note, filename, append order, or record ID selects
  a winner.

Forking is preserved as multiple current tips in one root. Slice A does not
collapse the fork or declare a public winner. A root with zero, one, or
multiple current tips can later be disclosed as inactive, healthy, or
conflicted by the separately gated Slice B query layer.

Withdrawal validation accepts only a current, unsuperseded, not-yet-withdrawn
BHD tip. It rejects unknown, wrong-kind, superseded, and duplicate targets.
Selective withdrawal of one current fork tip is admitted. A membership may
not contain both a successor and a withdrawal for the same target because the
complete successor graph is checked first. Replaying a membership that omits
a later BHW revives the target membership-relatively and does not rewrite the
earlier revision.

Withdrawal remains an event that stops the positive claim in the selected
membership. It is not evidence that the behavior was false, impossible,
physically removed, unhealthy, or unsafe.

## 10. Immutable index contract and deterministic ordering

`LoadedModel` carries exactly 12 BH-specific immutable mappings:

1. `behavior_registrations`;
2. `behavior_registrations_by_anchor`;
3. `behavior_anchor_ids_by_variable`;
4. `behavior_rule_declarations`;
5. `behavior_rule_ids_by_key`;
6. `behavior_rule_root_by_id`;
7. `behavior_rule_ancestry_by_id`;
8. `behavior_rule_superseded_by`;
9. `current_behavior_rule_tips_by_root`;
10. `behavior_rule_withdrawals`;
11. `behavior_rule_withdrawn_by`;
12. `behavior_rule_withdrawals_by_target`.

All maps are frozen before exposure. Record collections, reverse indexes,
ancestry, successors, current tips, and withdrawals are ordered by canonical
record or anchor identity, not caller mapping order. Four mappings initially
found input-order-sensitive by specialist review were repaired to insert in
sorted record-ID order. Tests exercise reversed mappings and different hash
seeds and compare the full BH index projection.

The store retains inactive roots with canonical empty current-tip tuples.
Ancestry is complete, transitive, unique, and canonically sorted. Independent
roots remain separate; no index manufactures cross-root convergence or
corroboration conclusions.

## 11. Hostile revalidation and forgery resistance

The public and store boundaries reconstruct nested objects from serialized
field content instead of trusting a nominal Pydantic instance. The focused
attack suite covers both `model_construct` and `model_copy` forgeries across:

- behavior anchors;
- assertion contexts;
- semantic locks;
- constraint semantic signatures;
- exact-equality rules;
- evidence arms and evidence tuples;
- authority references;
- record discriminators, IDs, parents, and withdrawal targets.

Rejected attacks include:

- missing, extra, or implication-bearing fields;
- coercible or boolean payloads where strict shapes are required;
- a forged nested signature or lock with a valid-looking outer instance;
- variable substitution under a stale record ID;
- pair, context, rule, basis, evidence, parent, or target substitution;
- duplicate/reordered-invalid parents;
- stale content IDs after `model_copy` mutation;
- forged on-disk records and filename/content substitution;
- mutated existing ledger members during prospective append.

Canonical rehashing is never treated as a substitute for structural
revalidation. A forged object that is rehashed still must pass the full public
union and prospective collection constraints.

## 12. Public surface and Slice B-D exclusions

The exact `backend.model_kernel.__all__` contains 131 names. The only Slice A
BH additions are:

```text
BehaviorRegistration
BehaviorRuleDeclaration
BehaviorRuleWithdrawal
BehaviorVariableSemanticLock
ExactNumericEqualityRule
```

The following accepted later-slice APIs are absent:

- `ModelQueries.behavior()`;
- `ModelQueries.behavior_declaration()`;
- `ModelQueries.behaviors_involving_variable()`;
- `ModelQueries.behavior_assertion()`;
- all BH query/result/status contracts;
- `backend.behavior_evaluation`;
- participant source selectors;
- numeric parsing or comparison;
- observation, semantic, binding, cohort, or state composition;
- any BH port or VPA query;
- any committed BH fixture or artifact.

The demo ledger remains at 29 records and contains zero BRG, zero BHD, and zero
BHW records. Slice D's new variable and records do not exist. No binding,
interpretation, temporal, source, structural, PT, VP, or demo record changed.

## 13. Import-direction and architecture review

Static inspection and the isolation tests establish the intended dependency
direction:

```text
backend.system_identity
          ↑
backend.model_kernel
```

The kernel does not import behavior evaluation, model state, temporal state,
identity binding, semantic compatibility, observation compatibility,
constraint evaluation, source interpretation, data sources, CAD, or PDF.
System identity does not import the kernel. There is no behavior store,
ledger, revision, cache, projection, database, runtime, or filesystem owner.

The new records reuse the existing model ledger, public builder, canonical
serializer, store, revision identity, and immutable loaded-model mechanism.
This is the smallest dependency-preserving Slice A architecture and leaves
numeric parsing and same-acquisition-cohort admission entirely to Slice C.

## 14. Independent bounded verification

### 14.1 Focused Slice A identity, record, canonical, store, and forgery suite

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_revalidation.py -q
```

Result: **110 passed in 13.85s**.

### 14.2 Architecture, historical replay, demo, PT, VP, and state preservation

Command:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider \
  tests/model_kernel/test_isolation.py \
  tests/model_kernel/test_demo_model.py \
  tests/model_kernel/test_demo_pt001.py \
  tests/model_kernel/test_demo_vp001.py \
  tests/model_state/test_demo_vp001.py -q
```

Result: **40 passed in 34.06s**.

### 14.3 Direct identity, export, exclusion, and preservation reproduction

The independent public-builder/index probe reproduced:

```text
BRG brg_ecd5a9b669f91dca639fde20202ce4f3c4ff17006d7f0ffd23f09ed44f1f9e3e
BHD bhd_9e3af9219521d1b3c5dfd5d41ae359dc8d3fb4c5db4b002586998e52f0a823eb
BHW bhw_4c2456b2a6473f6a37c47b9aadedc10b1a8610c80e6650ba70cdbd7b2dd938f6
demo records 29
demo BRG/BHD/BHW counts 0/0/0
system_identity exports 13
model_kernel exports 131
BH ModelQueries methods ()
backend.behavior_evaluation exists false
forbidden kernel imports ()
```

The accepted demo revision remains:

```text
mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

Artifact hashes remain:

```text
PT 53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8
VP a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3
```

`git diff --check` and `git diff --cached --check` were both clean before this
report was written. A final `git diff --check` is required after report and
completion-document assembly.

## 15. Historical replay and byte-preservation assessment

The regression suite uses explicit membership constants for the accepted
9-, 10-, 11-, 14-, 16-, 18-, 28-, and 29-record histories. It does not infer a
historical boundary through directory enumeration, filename prefixes,
timestamps, or append order.

All pre-BH memberships contain no BH record and therefore retain their exact
record tuples and revision identities. The current 29-record membership also
contains no BH record. No migration artifact is synthesized. Existing model
record content is read and verified in place, and the PT/VP artifacts remain
byte-frozen at their accepted hashes.

The committed-range inspection from accepted base through repair HEAD contains
BH changes only in:

- system-identity contracts, minter, and exports;
- model-kernel contracts, canonical support, store/index support, and exports;
- focused Slice A tests;
- owner-authorized BH design, plans, ADR, reviews, and status documentation.

It contains no committed changes under model ledgers, bindings,
interpretations, temporal evidence, source data, structural evidence, or
existing fixture artifacts.

## 16. Specialist-review reconciliation

### Architecture specialist

The architecture review challenged dependency direction, query/evaluator
leakage, public vocabulary, canonical preservation, and historical replay.
After repairs it reported no blocker. This review agrees: Slice A remains
inside `system_identity` and `model_kernel`, and no upper-layer dependency was
introduced.

### Backend specialist

The backend review identified three material issues:

1. BH index projections could depend on input mapping order;
2. the accepted private five-field effective-body primitive was absent;
3. BH validation ran before established pre-BH validation, changing failure
   precedence for mixed-invalid memberships.

All three were repaired at `1fb1009` and are independently confirmed here.

### Test specialist

The test review challenged exact public contracts, hostile nested instances,
lineage forks/convergence/withdrawal/revival, deterministic indexes, import
isolation, and byte preservation. The repair added the missing boundary and
ordering coverage. The focused 110-test and 40-test preservation runs are
green.

### Final code-review specialist

This review found only F1, the stale handwritten matrix vectors, and the lead
closed it before the verdict. No remaining contradiction was found between
the accepted normative design, executable golden tests, and implementation.

## 17. Non-blocking limitations and deferred work

These are intentional owner-gated exclusions, not Slice A defects:

- there is no public behavior lookup or lifecycle conclusion yet;
- identical effective-body roots are not yet publicly grouped as
  corroboration;
- different effective-body roots are not yet publicly concluded conflicted;
- there is no source selection, state acquisition, semantic admission,
  acquisition-cohort comparison, exact numeric parsing, execution status, or
  `equal`/`different` result;
- there is no committed synthetic behavior declaration;
- no design-time identity, revision, artifact size, or artifact hash has been
  invented for Slice D;
- full-suite and dual-clean-checkout totals must be taken from the lead's
  reproducible completion verification rather than inferred from these
  bounded reviewer runs.

Slice B may build read-only authoritative queries over the present indexes.
Slice C may add the separately gated evaluator and public CN parser reuse.
Slice D may rehearse its bounded 29-to-32-record append only after A-C owner
acceptance. None is authorized by this report.

## 18. Final integrity conclusion

BH-001 Slice A is implementation-ready for owner validation at the reviewed
repair HEAD, subject to the lead completing and recording the required full
verification. Exact contracts, canonical identities, evidence closure,
lineage admission, withdrawal semantics, immutable indexes, hostile
revalidation, import direction, explicit replay, and artifact preservation
are consistent with the accepted design.

There are **no open code-review blockers**. F1 is closed. Slices B, C, and D
remain unstarted.

END OF BH-001 SLICE A FINAL INTEGRITY REVIEW
