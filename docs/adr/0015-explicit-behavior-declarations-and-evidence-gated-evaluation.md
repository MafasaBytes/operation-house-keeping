# ADR-0015 — Explicit behavior declarations and evidence-gated evaluation

Status: BH-001 corrected final design and Slice A owner accepted. Slice A is
accepted at `57edec37b40c5da0c300cc1333fbb3cf5d7bb41a`. Slice B is owner accepted
at `05177f7306ce745d093bd5f11abafc13a6274d0f`. The Slice C discrepancy stop is
owner accepted at `eedae19a9b2542958f44e66af7117a981c7faeef`; all four contract
questions are resolved. BH-001 Slices A, B, and C are owner accepted. Slice C
is accepted at `8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`. The public
variable-minter discrepancy is owner resolved by the exact narrow API addition
described in Decision 17. The exact Slice D candidate identities, canonical
records, 32-record revision, and 122406-byte disclosure artifact are owner
approved. Slice D is implemented and adversarially reviewed at the exact
32-record revision and artifact contract; final owner acceptance is pending.
The frozen artifact remains explicitly a pre-append candidate disclosure; its
scope fields are historical rehearsal evidence, not current-state assertions.

Accepted base: `main` at
`46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`.

Original corrected-design acceptance specification:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`
at SHA-256
`2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978`.

Current owner-amended authoritative specification at the Slice D minter
resolution gate: SHA-256
`520bf74823ab5e206bef8a56de9ba872ef8f3167451ad9c57e02a364532cd873`.

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
    Slice A owner acceptance and is owner accepted at
    `05177f7306ce745d093bd5f11abafc13a6274d0f`. Slice C adds the separate
    read-only `backend.behavior_evaluation` composition and is owner accepted
    at `8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`. Slice D's deterministic
    disposable pre-append contract is owner approved at commit `0905de0`; the
    exact declaration-only 29-to-32 authoritative append and final
    verification are authorized.
16. Slice C validation proves internal coherence of carried public lower
    results and BH-derived fields, not raw-source authenticity. The exact
    22-reason refusal vocabulary, public three-class BH error tree, 21-name
    export list, and cohort/parser scheduling are fixed by the owner-resolved
    preimplementation discrepancy. Content-bound lower occurrence
    authentication remains separately owner-gated future work.
17. Owner resolution: add the narrowly scoped public `mint_variable_anchor()` API, commit it green before candidate allocation, then resume only the disposable pre-append rehearsal. The function is keyword-only, calls standard-library `uuid4()` exactly once, uses `uuid4().hex` with the `var_` prefix, and returns the unchanged `VariableAnchor` contract. Export `mint_variable_anchor` after `mint_port_anchor`. It adds no entity minter, storage, I/O, authority, registration, binding, persistence, injected randomness, or semantic meaning. No candidate may be minted before the minter commit is green. After the implementation commit, invoke each public minter exactly once, freeze both serialized anchors, and never invoke either minter again; reconstruct the frozen values in both independent disposable ledger roots.

Before the current owner decision, the authoritative append remained
prohibited until the exact candidates and artifact contract were approved.
That condition is now satisfied. The approved report SHA-256 is
`0a559255359440f54f370eaf11645122089d4c0744e537c9446e20c12ffd4778`;
the unchanged manifest SHA-256 is
`8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07`;
the approved 32-record revision is
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`;
and the approved 122406-byte artifact SHA-256 is
`4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.
No identity, record content, byte, ordering, revision, or artifact value may
change during the authorized append.

Owner approval: the exact Slice D candidate identities, canonical records,
32-record revision, and 122406-byte disclosure-artifact contract are approved;
the bounded authoritative append and final verification are authorized.

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
historical membership remain unchanged. The Slice D model is an explicit
32-record membership adding only VRG, BRG, and parentless BHD. Pre-BH memberships contain
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
