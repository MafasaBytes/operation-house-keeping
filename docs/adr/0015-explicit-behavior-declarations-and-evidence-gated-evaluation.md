# ADR-0015 — Explicit behavior declarations and evidence-gated evaluation

Status: BH-001 corrected final design and Slice A owner accepted. Slice A is
accepted at `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. Slice B is implemented
and adversarially reviewed; awaiting owner acceptance. Slices C and D remain
separately owner-gated and unstarted.

Accepted base: `main` at
`46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`.

Authoritative specification:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`
at SHA-256
`2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978`.

## Context

The accepted model can register variables, declare their value and semantic
specifications, constrain admitted numeric observations, register ports and
typed interface claims, explicitly associate a variable with a same-owner
port, and disclose variable state beside that association. None of those facts
declares behavior. Names, common ownership, hierarchy, CAD, topology, PIF
direction, PCN connectivity, PCM compatibility, VPA association, semantic
compatibility, constraint findings, temporal correlation, and observed value
changes must not manufacture behavioral truth.

BH-001 needs the smallest explicit behavior primitive that preserves this
boundary. Its v1 claim is intentionally narrower than general engineering
behavior: two distinct registered variables participate in a declared exact
numeric-equality relation under one exact assertion context. Source-backed
evaluation is useful only when it remains a separate, read-only, evidence-gated
composition.

## Decisions

1. Add a stable `BehaviorAnchor` to `backend.system_identity` with prefix
   `bhv_`. It is an opaque UUID4-backed identity containing only `anchor_id`,
   `namespace`, `display_name`, and optional `role_name`. It contains no owner,
   participant, context, rule, evidence, direction, state, causal meaning, or
   lifecycle. `mint_behavior_anchor()` is pure and performs no I/O.
2. Store BH declaration knowledge in the existing append-only model ledger and
   existing `mrv_` revision. Add no behavior ledger, store, repository,
   projection, cache, database, or revision.
3. Add permanent `BehaviorRegistration` records with prefix `brg_`. One BRG
   embeds one behavior anchor and permanently owns exactly two distinct,
   unordered, canonically variable-ID-sorted registered variable anchors plus
   `rule_family="exact_numeric_equality"`. It has evidence but no context,
   parents, withdrawal, lifecycle, owner, port, role, or direction. Changing a
   participant or rule family requires a new behavior anchor and registration.
4. BRG admission requires both exact variable registrations, both variable
   owner entity registrations, `ModelRecordEvidence` citations to both exact
   VRG IDs, at least one `OwnerDeclarationEvidence`, and closure of every other
   cited model record. Cross-owner pairs are allowed when explicitly
   registered with this evidence. Shared ownership neither creates nor
   strengthens behavior.
5. Add correctable `BehaviorRuleDeclaration` records with prefix `bhd_`. A BHD
   carries the behavior anchor, exact `AssertionContext`, exactly two
   variable-keyed `BehaviorVariableSemanticLock` values, an
   `ExactNumericEqualityRule` whose sole field is
   `kind="exact_numeric_equality"`,
   `evaluation_basis="same_acquisition_cohort"`, evidence, canonical parents,
   recorded time, authority, and note.
6. BHD locks must correspond exactly to the registered variable pair. Their
   quantity-kind and unit identities must be exactly equal; observation-role
   identities may differ. Locks do not create or replace VSP, VSM, source
   interpretation, or unit declarations. The model store does not compare
   them with current VSP/VSM/source knowledge; those are Slice C evaluation
   gates.
7. BHD admission requires the exact BRG citation, at least one
   `OwnerDeclarationEvidence`, complete evidence closure, exact subject and
   context preservation across parents, and fully reconstructed nested
   contracts. Pre-existing Pydantic instances are never trusted without
   serialization and revalidation.
8. The lineage key is `(behavior_anchor_id, exact AssertionContext)`. A
   parentless BHD starts an independent root. Corrections may converge only
   within their root. Cross-root convergence, cycles, self-supersession,
   duplicate parents, wrong-kind parents, cross-anchor parents, and
   cross-context parents are invalid.
9. Within one root, no active tip is inactive, one active tip is healthy, and
   multiple active tips are conflicted even when their engineering bodies are
   identical. Partial convergence remains conflicted; complete same-root
   convergence may restore one healthy tip.
10. Across independent active healthy roots, identical effective engineering
    bodies corroborate and different effective engineering bodies conflict.
    The effective body contains exactly behavior anchor, exact context,
    variable-keyed semantic locks, rule, and evaluation basis. Evidence,
    parents, authority, recorded time, note, record ID, schema, filename, and
    append order do not distinguish bodies. Comparison uses the accepted
    canonical JSON rules, not timestamps, object equality, or record-ID
    ordering. Inactive roots remain disclosed but do not vote.
11. Add `BehaviorRuleWithdrawal` with prefix `bhw_`. BHW targets one current,
    unsuperseded, unwithdrawn BHD tip and carries only target, recorded time,
    authority, and note. It has no evidence, context, parents, result, reason,
    replacement, or negative-behavior meaning and is not citable. Selective
    fork-tip withdrawal is allowed. One membership cannot both supersede and
    withdraw the same target. Replay without a later withdrawal revives the
    target membership-relatively.
12. Add `brg_` and `bhd_` to citable model-record evidence; exclude `bhw_`.
    Add all three record kinds to the canonical model-record and filename
    grammars, discriminated union, kind-prefix map, public builder path, and
    immutable loaded-model indexes. Existing canonical bytes, IDs, schemas,
    revisions, and evidence meanings remain unchanged.
13. BH-001 v1 contains no participant role, ordering, port, VPA, input/output,
    source/dependent, command/response, flow, influence, causality, control,
    compatibility, correctness, health, safety, or operating-state meaning.
    It permits no coefficient, offset, tolerance, expression, operator graph,
    inequality, lookup table, state transition, executable script, external
    model, recursion, or unit conversion. Affine behavior and other rule
    families are deferred to BH-002 and cannot reinterpret BH-001 records.
14. Slice A implements identity, record contracts, canonical support, store
    admission, lifecycle indexes, builders, exports, replay, adversarial tests,
    and documentation only. It adds no kernel query or result contract, no
    evaluator, no observation selection or comparison, and no fixture record.
15. Slice B adds exactly the four accepted read-only kernel queries after
    Slice A owner acceptance. It is implemented and adversarially reviewed;
    awaiting owner acceptance. Slice C may then add the separate read-only
    `backend.behavior_evaluation` composition with explicit source selectors,
    exact same-acquisition-envelope admission, and the public bounded CN
    exact-number parser. Slice D remains a separately gated declaration-only
    29-to-32-record demonstration after deterministic disposable rehearsal and
    owner approval of its exact derived identities and artifact contract.

## Consequences

The model gains a durable identity for one explicit relationship and can retain
context-specific declaration history without inferring behavior from any
existing record family. Permanent registration preserves continuity; a new
anchor is required when the participant pair or rule family changes.

Independent roots can represent independent authority claims without an
implicit winner. Audit and evidence differences remain fully disclosed while
engineering-body equality alone controls corroboration. Correction, conflict,
withdrawal, and historical revival remain revision-relative.

The kernel dependency boundary remains `system_identity`, Pydantic, and the
standard library. Evaluation, when separately authorized, remains above model
state and semantic compatibility, owns no store, and never persists equality
as model or temporal truth.

The accepted 29-record demo and every explicit 9/10/11/14/16/18/28/29-record
historical membership remain unchanged in Slice A. Pre-BH memberships contain
no migration or inferred behavior. The VP and PT deterministic artifacts and
all model, binding, interpretation, temporal, source, and structural evidence
remain byte-frozen.

## Rejected alternatives

- Declaration-lineage-only identity is rejected because it cannot preserve
  permanent participant and rule-family continuity.
- A BH-specific ledger or revision is rejected because it adds an unnecessary
  provenance axis and cross-ledger closure problem.
- Reusing generic relationships, ports, or VPA is rejected because their
  accepted meanings do not declare behavior.
- Context-free declarations are rejected because behavior claims may differ by
  assertion context.
- Directional or affine rules, tolerance, arbitrary expressions, external
  execution, implicit source discovery, temporal proximity, and persisted
  evaluation are outside BH-001.

END OF ADR-0015
