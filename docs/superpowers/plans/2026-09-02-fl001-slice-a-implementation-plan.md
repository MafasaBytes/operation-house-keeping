# FL-001 Slice A Implementation Plan

Date: 2026-09-02

Status: owner-authorized implementation plan; execution in progress

Accepted base: `1d53d8adb22aada01bf808adb7dc7454a688543d`

Administrative design commit: `275f3ec` (`docs: accept FL-001 architecture`)

Accepted design:
`docs/superpowers/specs/2026-09-02-fl001-explicit-flow-identity-and-evidence-gated-flow-declaration-design.md`
at SHA-256
`4d6ea16b6f2c0f563934212f12dc15d130e39047341ee002e8dd759a8481856a`.

## 1. Capability being validated

Slice A adds only the model foundation for one durable logical directed
`FlowAnchor` and evidence-bearing `frg_`/`fld_`/`flw_` records. It validates
identity, canonical content, evidence closure, exact structural support,
correction/withdrawal lifecycle, replay, and immutable loaded-model indexes.

The slice does not add a public flow query/result facade, a demo fixture,
authoritative flow records, assessment, occurrence, observation, calculation,
rate, conservation, traversal, control, causal meaning, or
`ConnectionAnchor`.

## 2. Frozen baseline and preservation evidence

Before production edits:

- branch `fl001` descends directly from the accepted base;
- the three accepted design files retain their approved digests;
- the authoritative model contains exactly 34 records at
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
- its accepted stored-record inventory aggregate is
  `cf3a534b4b7d13a85fb1f23a3e81881b03e084fc508145950cbc8618f247d6cd`;
- no `frg_`, `fld_`, or `flw_` file exists in the authoritative ledger; and
- historical 9/10/11/14/16/18/28/29/32/34 memberships and accepted
  PT/VP/BH/ST artifacts remain protected by their existing pinned tests.

The same inventory, revision, membership, historical revisions, and accepted
artifact digests are checked after every implementation boundary and in both
clean-checkout columns.

## 3. Existing patterns to extend

The implementation follows the accepted transition/state/behavior patterns,
without copying their semantics:

- `backend.system_identity.anchors`: opaque frozen anchors with
  `revalidate_instances="always"`;
- `backend.system_identity.minting`: pure one-`uuid4()` public minter;
- `backend.model_kernel.contracts`: strict nested reconstruction, canonical
  tuple validators, exact field order, discriminated `ModelRecord` union;
- `backend.model_kernel.canonical`: one kind-prefix map, normative UTC
  `+00:00` canonical bytes, and a private effective-body projection;
- `backend.model_kernel.store`: full-set prospective validation, typed atomic
  append, exact replay, deterministic DAG derivation, and copied immutable
  mappings; and
- existing ST-002 Slice A helpers/tests: nearest lifecycle and forgery
  structure, adapted to ports and PCN/PIF pins rather than state endpoints.

No lower package may import the model kernel. No flow implementation may
import an upper evaluation, state, temporal, source, structural, binding,
interpretation, filesystem, environment, network, or clock package.

## 4. Planned production changes

### 4.1 System Identity

Add exactly:

- `FLOW_ANCHOR_ID_PATTERN = r"^flo_[0-9a-f]{32}$"`;
- frozen, extra-forbidden, always-revalidated `FlowAnchor` fields in the
  specified order: `anchor_id`, `namespace`, `display_name`, `role_name`;
- `mint_flow_anchor(namespace, display_name, role_name=None)` calling
  `uuid4()` exactly once and returning `flo_` plus `.hex`; and
- the exact public exports for the pattern, anchor, and minter.

### 4.2 Model record contracts

Add exactly:

- `FlowKindToken`;
- `FlowDirectionDeclarationPin`;
- canonical nonempty source/sink port tuples, with individual 1–63 and total
  disjoint-union 2–64 validation;
- canonical per-role direction-pin tuples;
- canonical `fld_` parent tuple;
- `FlowRegistration` (`frg_`), `FlowDeclaration` (`fld_`), and
  `FlowDeclarationWithdrawal` (`flw_`) with exact accepted field order; and
- `frg|fld` only in `ModelRecordEvidence`, while all withdrawal arms remain
  uncitable.

Every nested BaseModel supplied to a flow constructor is inspected before
dump/reconstruction so hidden extras, private state, cycles, and forged nested
instances cannot be laundered.

### 4.3 Canonicalization and builder integration

Add the three kind/prefix mappings and a private `_flow_effective_body_bytes()`
projection over exactly:

```text
flow_anchor_id
context
connection_assertion_record_id
source_direction_pins
sink_direction_pins
```

All public records continue through `build_record()`. Golden tests pin exact
canonical bytes, record IDs, stored JSON bytes/hashes, `+00:00` rendering,
and preservation of every pre-FL vector.

### 4.4 Store admission and immutable indexes

Extend store dispatch, filename grammar, revalidation, and full-set validation
in this order:

1. validate FRG anchor uniqueness and exact semantic-signature uniqueness;
2. validate role shape/bounds, every participant PRG, direct PRG citations,
   owner claim, and uniform evidence closure without looking up PCN/PIF;
3. validate FLD registration, exact context, exact-union PCN, complete
   one-per-participant PIF pins, the strict source/sink direction table,
   direct FRG/PRG/PCN/PIF citations, owner claim, and uniform closure;
4. build the exact `(flow_anchor_id, context)` DAG and reject cross-key,
   cross-root, missing, cyclic, or incomplete merges;
5. validate each FLW against one current unsuperseded/unwithdrawn tip and
   reject successor/withdrawal races independent of input order; and
6. freeze every sorted index defined by Section 21.3.

Stale, withdrawn, conflicted, or inactive but structurally valid PCN/PIF pins
remain admissible. The selected membership already contains the authoritative
PT lifecycle indexes needed by later Slice B disclosure; Slice A persists no
alignment or activity result.

RC3 is explicit: an FRG admits with all PRGs, citations, owner basis, and
evidence closure when no PCN/PIF exists or when matching support has no current
tip. This establishes identity only, never active support or physical flow.

## 5. Red-first execution waves

### Wave 1 — identity and exact schemas

Add failing tests for the `flo_` grammar, minter call count/purity, exact field
order, forbidden fields, canonical role tuples/pins/parents, nested forgeries,
evidence-arm grammar, and public exports. Record the expected import/attribute
failures, implement the minimal contracts, then rerun.

### Wave 2 — canonical identity and stored bytes

Add failing tests for the three prefixes, literal canonical payloads,
record-ID suffixes, golden IDs, stored JSON byte counts/hashes, UTC rendering,
permutation stability, role reversal, repartition, token changes, stale IDs,
and pre-existing vector preservation. Implement only canonical/union/store
dispatch integration needed to pass.

### Wave 3 — registration and support admission

Add failing disposable-store tests for FRG admission/uniqueness/RC3 and FLD
exact PCN/PIF/context/direction/citation gates. Cover stale/withdrawn support
admission separately from currentness and reject every malformed or incoherent
reference atomically.

### Wave 4 — lifecycle, replay, and immutable indexes

Add failing tests for independent roots, same-root forks, partial/full merge,
cross-root rejection, corroboration/body disagreement primitives, selective
withdrawal, duplicate/invalid withdrawal, successor/withdrawal races,
historical revival, missing replay dependencies, deep iterative DAGs, and
every immutable sorted index. Implement the smallest full-set derivation.

### Wave 5 — hostile storage, architecture, and preservation

Add hostile on-disk kind/prefix/hash/content/private-state cases, mixed
revision and file-order/hash-seed checks, import isolation, public-surface
exclusions, historical empty-flow-index replay, authoritative 34-record
preservation, and accepted artifact hashes. Repair only reproduced Slice A
defects.

The executable mapping for these waves is maintained in
`docs/superpowers/plans/2026-09-02-fl001-slice-a-adversarial-acceptance-matrix.md`.

## 6. Bounded commit plan

1. `docs: accept FL-001 architecture` — already complete at `275f3ec`.
2. `test: specify FL-001 Slice A foundation` — red-first tests, helpers,
   implementation plan, and adversarial matrix; tests must demonstrably fail
   because the production contracts are absent.
3. `feat: add FL-001 flow declaration foundation` — minimal identity/kernel
   implementation plus any narrowly necessary expected-surface updates.
4. `test: harden FL-001 Slice A integrity` — reproduced defect repairs and
   additional adversarial/preservation tests, if specialist review finds any.

The completion report remains uncommitted for the owner gate unless the owner
later authorizes its administrative acceptance commit.

## 7. Verification plan

Run, in order:

1. focused identity and FL-001 Slice A tests;
2. complete `tests/identity_binding`;
3. complete `tests/model_kernel`;
4. affected model-state, constraint, behavior, state, transition, semantic,
   and observation suites;
5. architecture/import-isolation tests and backend compilation;
6. the complete repository suite;
7. focused OCP/STEP and PDF paths where present;
8. fresh base-only and all-extras clean-checkout full suites;
9. the exact loopback test separately under the established permission path
   if sandbox denial is the sole failure;
10. deterministic hash-seed/file-order reproduction; and
11. working-tree and full-range `git diff --check`, exact status/topology,
    ledger inventory, historical replay, and artifact preservation.

## 8. Stop condition

Stop after the completion report proves Slice A and asks exactly whether the
owner accepts the reported implementation HEAD. Do not start public flow
queries or Slices B–D, mint/freeze a demo identity, append an authoritative
flow record, push, merge, rebase, reset, cherry-pick, amend, or rewrite
history.
