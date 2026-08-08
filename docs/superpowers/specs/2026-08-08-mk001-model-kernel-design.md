# MK-001 — Typed Entity/Relationship Kernel and Hierarchy View (final, self-contained)

Status: **Accepted by the project owner** (candidate design + specialist reviews
+ one owner correction pass + six final normative amendments, 2026-08-08).
This document incorporates the complete accepted design and stands alone.

## Objective

The smallest trustworthy kernel slice answering: *what exists in this model,
how is it typed and connected, why does each connection exist, and what does
the containment hierarchy look like — for an exact replayable model revision
and an explicit engineering-view context.*

```text
data_sources → temporal_state → identity_binding → model_kernel
                        system_identity ────────→ model_kernel
```

In scope: canonical entities via anchors; typed directional evidence-backed
relationships; type-definition vs instance; ONE hierarchy projection derived
from declared containment semantics (a projection over the typed graph — no
generic `connected_to`); immutable content-addressed revisions with exact
replay; structured conflict/invalidity results; incoming/outgoing/parent/
child/ancestor/descendant queries.

Excluded: ports, variables-in-kernel, behaviors, constraints, causal
reasoning, live state, planning, change-impact, commands, fuzzy matching,
automatic CAD/BOM hierarchy derivation, LLM-generated truth, graph databases,
UI, Excel, configuration/version timeline, validity intervals on
relationships (time-varying structure has NO MK-001 representation),
symmetric relationship types, edge attributes, sibling-order semantics,
registration or type-definition withdrawal, multi-model composition,
knowledge-time revision queries.

## Module boundary and dependency rules

```text
backend/model_kernel/
  __init__.py   README.md
  contracts.py  # authority, contexts, evidence, 4 record kinds, revision,
                #   summaries/results, ModelKernelError tree
  canonical.py  # canonical serialization + hashing (duck-typed; imports NO contracts)
  store.py      # ModelStore (validating append / load / replay),
                #   validate_record_collection, LoadedModel
  hierarchy.py  # HierarchyView projection per (type lineage × lifecycle view)
  queries.py    # ModelQueries (+ hierarchy_health)
models/<model_id>/records/            # model ledgers (committed demo: models/demo-printer/)
bindings/demo-printer-model/records/  # committed synthetic DECLARATION FIXTURE (3 anchors)
tests/model_kernel/
```

Runtime `model_kernel` code imports ONLY `backend.system_identity`, the
standard library, and pydantic — verified by AST inspection, not raw text
search (evidence discriminator literals such as `identity_binding_record` are
data, not dependencies). Runtime kernel code contains no path-based access to
binding, temporal, or evidence stores, and the kernel operates identically
when those stores do not exist. `tests/model_kernel/` may additionally import
`identity_binding`, `data_sources.contracts`, and `temporal_state` contracts
**for constant/shape pinning and seam verification only**.

**Enforceable upstream boundary:** (a) no changes to accepted code under
`backend/{data_sources, temporal_state, identity_binding, system_identity}`;
(b) no edits or deletions to existing records under `bindings/demo-printer/`;
(c) the approved synthetic declaration fixture `bindings/demo-printer-model/`
is the only upstream-layer data addition; (d) no `model_kernel` runtime code
reads or writes any binding set — among MK-001's additions, only
`tests/model_kernel/test_cross_layer_seam.py` reads binding sets (existing
identity-binding tests and its runtime legitimately do so and are untouched).

The kernel never copies observations, never mutates evidence, never
reinterprets temporal coverage, and performs no identity matching.

## Identity consumption and trust boundary

The kernel provides no anchor-creation API. Synthetic demo anchor IDs are
**externally allocated as fixed fixture constants and authoritatively
declared through `AnchorDeclaration` records in an identity-binding ledger**;
the kernel only consumes the resulting `EntityAnchor` values.
`bindings/demo-printer-model/` is a declaration fixture, not an
anchor-generation service.

Precise guarantee (never overstated): the kernel accepts a structurally valid
`EntityAnchor` and treats its complete value as immutable; it cannot prove at
runtime that the anchor was previously declared; committed fixtures are
verified field-for-field against `AnchorDeclaration` records by the test-only
seam; arbitrary runtime model sets require the documented external
declaration-verification procedure (load the model set, load the relevant
binding sets through `identity_binding`, compare every registration's
embedded anchor field-for-field). The stronger "exactly as declared" claim
holds only for the seam-verified committed demo.

## Contracts

All models: pydantic v2, `frozen=True`, `extra="forbid"`,
`schema_version: "1"` per ledger kind, UTC-normalized `AwareDatetime`
(naive rejected; equal instants under different offsets hash identically),
`recorded_at` audit-only — it never selects winners anywhere. No mutable
container types on any model: tuples with sorted-unique validators only.

`record_id = <prefix>_<full 64-hex SHA-256>` over the validated model's
canonical serialization: sorted keys, compact separators, `record_id`
excluded from its own hash, timestamps as `astimezone(UTC).isoformat()`
(`+00:00`), enums as strings, discriminated unions carrying their
discriminator. Byte-parity with `identity_binding.canonical` is enforced by
shared golden vectors at the test seam — never by shared code and never by
modifying accepted IB code.

```text
AuthorityRef        kind human_owner|test_fixture · agent (min 1) ·
                    method manual_declaration        # a recorded CLAIM — nothing
                                                     #   is authenticated or signed

LifecycleViewContext   { kind:"lifecycle_view", view: as_designed|as_built|
                         as_configured|as_operated|as_maintained }
ViewIndependentContext { kind:"view_independent" }
AssertionContext = discriminated union of the two (also the query-context type)

EvidenceRef (discriminated union; foreign kinds NEVER dereferenced or verified):
  owner_declaration        { statement: str min 1 }        # the only prose-bearing kind
  model_record             { record_id: ^(reg|rtd|rel)_[0-9a-f]{64}$ }   # must exist in
                                                           #   revision → "verified_in_revision"
  identity_binding_record  { binding_set_id: ^[a-z0-9-]+$,
                             record_id: ^(anc|iba|ibr|ibc|ibj)_[0-9a-f]{64}$ }
  source_raw_record        { raw_record_id: ^[0-9a-f]{32}$,
                             payload_checksum: ^sha256:[0-9a-f]{64}$ }
  temporal_occurrence      { occurrence_id: ^[0-9a-f]{32}$ }
  # restated patterns are pinned to the upstream constants by seam tests;
  # all non-model kinds are labeled "declared_reference" in results
```

Ledger record kinds (prefixes reg/rtd/rel/rwd):

```text
EntityRegistration            reg_    # NO lifecycle — no supersedes, no withdrawal
  anchor          EntityAnchor        # embedded verbatim; NO kernel path alters any
                                      #   field (display_name, role_name, namespace,
                                      #   referent_kind included). A mistaken or
                                      #   unknown anchor is corrected by a future
                                      #   identity-layer decision or a different
                                      #   anchor — never by the model kernel.
  recorded_at / authority / note
  # Two DISTINCT reg_ records embedding one anchor_id ⇒ invalid revision;
  # identical content is a same-hash idempotent no-op at append.

RelationshipTypeDefinition    rtd_
  type_name       ^[a-z][a-z0-9_]*$
  forward_label / inverse_label       # both required (min 1); inverse is a reading,
                                      #   never a second stored edge
  directionality  Literal["directed"]
  source_referent_kinds / target_referent_kinds
                  tuple, sorted-unique, min 1, over ALL FOUR literals
                  {physical_instance, logical_instance, type_definition, unknown}
                  # "unknown" is an EXPLICIT opt-in member, never a wildcard: a
                  # type listing only physical_instance fails an unknown endpoint
                  # closed; a type explicitly listing unknown accepts it. The
                  # committed contains/instance_of remain strict (no unknown).
  self_relation_allowed  bool         # containment + True rejected at construction
  hierarchy_semantics    Literal["containment", "none"]
  context_requirement    Literal["lifecycle_view", "view_independent"]
  supersedes      rtd_-id | None      # correction within a LINEAGE; must preserve
                                      #   {type_name, directionality,
                                      #    hierarchy_semantics, context_requirement};
                                      #   changing any of these requires a NEW type
                                      #   name. Changeable: labels, endpoint-kind
                                      #   tuples, self_relation_allowed, note/authority.
  recorded_at / authority / note
  # Terminology: assertions are ACTIVE/inactive; type-definition chain tips are
  # CURRENT. Exactly one current rtd_ per type_name: unlinked duplicates AND
  # branching supersession chains (two current tips) ⇒ invalid revision.

RelationshipAssertion         rel_
  type_id         rtd_-id             # explicit citation; validated against the
                                      #   EXACT cited definition (endpoint kinds
                                      #   incl. opt-in unknown, self-rule, context
                                      #   arm). Citing a superseded definition is
                                      #   VALID and stale-marked, never invalid.
  source_anchor_id / target_anchor_id  ^ent_[0-9a-f]{32}$   # both registered, or
                                                            #   invalid revision
  context         AssertionContext    # arm must match the cited type's requirement
  evidence        tuple[EvidenceRef, ...] min 1
                  # CANONICALIZED at validation: each ref's canonical serialized
                  # bytes are the ordering key; duplicates are normalized away
                  # (repeating identical evidence adds no support — documented
                  # rule); permuted/duplicated inputs yield the same record_id;
                  # min length 1 applies after normalization.
  supersedes      rel_-id | None      # correction; same LINEAGE (type_name of the
                                      #   cited definitions), same source, target,
                                      #   and context; a successor may cite a
                                      #   different type_id only within the lineage
  recorded_at / authority / note

RelationshipWithdrawal        rwd_    # "no longer asserted" — NO claim the original
  withdraws       rel_-id (must exist)#   was wrong and NO claim about when it
  recorded_at / authority / note      #   stopped being true; may coexist with
                                      #   supersession; multiple withdrawals valid,
                                      #   all disclosed sorted

ModelRevision                 mrv_    # COMPUTED ONLY — never a file, never a ledger
  revision_id  = "mrv_" + sha256(model_id + "\n" + "\n".join(sorted record_ids))
  record_ids   sorted unique, ^(reg|rtd|rel|rwd)_[0-9a-f]{64}$   # mrv_ excluded
  record_count · model_id ^[a-z0-9-]+$
  # self-validating: sortedness, uniqueness, count, recomputed id, member patterns
```

Result contracts (all frozen; impossible states rejected by validators):

```text
RelationshipSummary
  record_id · type_id · type_name · forward_label · inverse_label ·
  cited_type_current: bool · source_anchor_id · target_anchor_id · context ·
  authority · evidence: tuple[EvidenceDisclosure{ref, verification:
  verified_in_revision|declared_reference}] · supersedes · superseded_by:
  tuple (sorted rel_) · withdrawn_by: tuple (sorted rwd_) ·
  active: bool ⇔ both link tuples empty · recorded_at

LineageConflict      { predecessor_id: rel_, competing_successor_ids:
                       sorted unique tuple of rel_, min 2 }

RelationshipsResult  { status registered|not_registered, anchor_id, direction,
                       type_name|None, context,
                       active: tuple[RelationshipSummary], inactive: tuple[...],
                       lineage_conflicts: tuple[LineageConflict], revision }
                     # not_registered ⇒ all three tuples empty

EntityResult         { status registered|not_registered, anchor_id,
                       registration summary|None, revision }

ParentResult         { status resolved|no_declared_parent|conflicted|cyclic|
                       not_registered, child_anchor_id, parent|None (resolved),
                       supporting: tuple[RelationshipSummary] (every supporting
                       assertion preserved — corroboration is never merged away),
                       candidate_parents: tuple[EntityAnchor] (conflicted only),
                       cycle_members: sorted tuple (cyclic only), type_name,
                       view|None, revision }

ChildEntry           { anchor, supporting: tuple[RelationshipSummary],
                       annotations: tuple[TraversalAnnotation] }
ChildrenResult       { status listed|not_registered|cyclic, entries, ... , revision }

TraversalAnnotation  { kind: Literal["multiple_parents"],
                       candidate_parent_anchor_ids: sorted, via_assertion_ids: sorted }
TraversalStep        { anchor, supporting: tuple[RelationshipSummary],
                       annotations: tuple[TraversalAnnotation] }
TraversalBlock       { anchor_id, reason: Literal["conflicted", "cyclic"] }
TraversalResult      { status complete|partial|not_registered, origin_anchor_id,
                       steps: tuple[TraversalStep], blocked: tuple[TraversalBlock]
                       (partial ⇔ non-empty), type_name, view|None, revision }

HierarchyHealth      { type_name, view, cycles: tuple[{members sorted,
                       via_assertion_ids sorted}], parent_conflicts:
                       tuple[{child_anchor_id, candidate_parent_anchor_ids,
                       via_assertion_ids}], stale_type_assertions: sorted tuple,
                       revision }
```

Errors: `ModelKernelError(error_code, message)` → `ModelConfigurationError`
(bad model root/id — `MODEL_SET_ID_INVALID`) / `ModelIntegrityError`
(invalid revision — all-or-nothing; includes `MODEL_REVISION_INVALID` for a
malformed, duplicated, or absent replay membership, and
`MODEL_STORAGE_FAILURE` for environment failures) / `ModelQueryError`
(contract misuse). All codes `MODEL_*`.
**Path-leakage rule:** error messages expose model IDs, record IDs, file
*names*, and stable error codes — never the temporary-directory absolute
path, the model-store root absolute path, or unrelated filesystem locations.
Environment failures during append are wrapped as
`ModelIntegrityError("MODEL_STORAGE_FAILURE", …)` carrying ids only, with
the operating-system error chained as the cause.

## Integrity invariants (all-or-nothing; enforced at validating append AND load)

1. collection key == record's own `record_id` (`MODEL_RECORD_KEY_MISMATCH`);
2. content hash verifies; filename == `<record_id>.json`; unexpected files
   invalid (`MODEL_RECORD_HASH_MISMATCH` / `MODEL_RECORD_INVALID`);
3. unknown `record_kind`/`schema_version` invalid;
4. two distinct registrations embedding one `anchor_id`
   (`MODEL_DUPLICATE_REGISTRATION`);
5. `rtd_` supersession: target exists, lineage-invariant fields preserved,
   chains acyclic (`MODEL_SUPERSEDES_INVALID`); exactly one current `rtd_`
   per `type_name` — unlinked duplicates and branched chains invalid
   (`MODEL_DUPLICATE_TYPE_NAME`);
6. `rel_`: cited `type_id` exists (`MODEL_REFERENCE_INVALID`); both endpoints
   registered (`MODEL_REFERENCE_INVALID`); context arm matches the cited
   definition's requirement (`MODEL_CONTEXT_INVALID`); endpoint referent
   kinds within the cited definition's declared tuples
   (`MODEL_ENDPOINT_KIND_INVALID`); source==target only when the cited
   definition allows it (`MODEL_SELF_RELATION_INVALID`); supersession same
   lineage + source + target + context, chains acyclic
   (`MODEL_SUPERSEDES_INVALID`); `model_record` evidence targets exist in the
   collection (`MODEL_REFERENCE_INVALID`);
7. `rwd_.withdraws` references an existing assertion
   (`MODEL_WITHDRAWAL_INVALID`).

NOT invalid — structured results instead: **distinct-parent/same-child
conflicts**, containment cycles, active assertions citing superseded
definitions (stale-marked), lineages ending with no active assertion.

## Hierarchy and traversal semantics

A containment assertion is stored `source = parent → target = child`.
Assertion supersession preserves source and target, so competing successors
of one assertion can never assert different parents.

- **Multiple-parent conflict** = active assertions from two or more
  independent assertion lineages with **different source/parent anchors and
  the same target/child anchor**, in the same type lineage and lifecycle
  view. Multiple active assertions for the same parent, child, lineage, and
  context are **corroborating support for one hierarchy edge** — every
  supporting assertion ID is preserved.
- Competing successors within one lineage are reported exclusively through
  `lineage_conflicts`; if a hierarchy edge also has a lineage conflict, both
  facts are disclosed independently — a second parent candidate is never
  fabricated.
- Hierarchy identity = *(containment type lineage × lifecycle view)* within
  one revision; contexts never merge; old and corrected assertions project
  into one hierarchy (the lineage-invariant fields are exactly the
  projection-relevant ones).
- Cycles are always semantically invalid *for the projection*: detected
  deterministically and iteratively at `HierarchyView` build, every member
  and assertion cited, unaffected subtrees still answer; the revision stays
  loadable. Cycles block traversal in BOTH directions (termination).
- **Traversal asymmetry (by design, no symmetry claim):** a multiple-parent
  conflict is an *incoming* ambiguity on the child. `parents()`/`ancestors()`
  block: `conflicted` / `partial` with the blocking node and the exact
  competing assertions. `children()`/`descendants()` proceed through a
  multiple-parent child — the outgoing edge is a well-formed active claim —
  with each affected step annotated `multiple_parents`. `descendants(root)`
  may therefore include a node whose own `ancestors()` is conflicted.
- `parents()` precedence for child X: X unregistered → `not_registered`;
  X a cycle member → `cyclic`; ≥2 distinct parents → `conflicted`;
  1 → `resolved`; 0 → `no_declared_parent` (never called "root" — the kernel
  cannot distinguish a root from an undeclared parent).
- Sibling order carries no engineering meaning; all collections are in
  canonical order (ascending `anchor_id`, ties by `record_id`) as a
  determinism guarantee only. Traversal is depth-first preorder with
  children visited in canonical order.
- Transitive closure exists ONLY over `hierarchy_semantics=containment`
  within one (lineage, view). Hierarchy queries against a
  `hierarchy_semantics="none"` type raise `MODEL_NOT_A_HIERARCHY`.

## Lineage lifecycle (assertions)

Five disclosure states: one active assertion (in `active`, links
disclosed); competing active successors (all in `active` AND listed in
`lineage_conflicts`; recorded time never selects one); withdrawn
(`inactive`, `withdrawn_by ≠ ()`); superseded (`inactive`,
`superseded_by ≠ ()`); both (`inactive`, both disclosed — independent facts,
no precedence). Withdrawing a superseded predecessor does not affect its
successor; withdrawing an active successor never reactivates its predecessor
— a lineage may end with **no active assertion** (the claim is gone unless
re-asserted; disclosed).

## Storage: validating append, load, replay

One model set per directory (`models/<model_id>/records/<record_id>.json`,
pretty-printed; identity is the canonical hash of the validated model, never
file bytes); staging in `.staging/` outside the scanned directory; honest
single-writer assumption (no locks pretended; TOCTOU under concurrent
writers is out of contract); no fsync-grade durability claim.

**Structural revalidation at public trust boundaries (mandatory).** A
supplied object belonging to a record class proves nothing:
`model_copy`, `model_construct`, and stale or hand-deserialized instances
bypass field validation, and a caller can rehash the result so its
content-derived id looks authentic. Therefore `ModelStore.append` and
`validate_record_collection` — each a public boundary in its own right —
revalidate **every** supplied record from plain serialized field data
before key binding, hashing, or semantic checks, and use the revalidated
instances as the authoritative values in the normalized collection and in
`LoadedModel`. Shape failures, including any serializer warning they would
raise, surface as typed, path-free
`ModelIntegrityError("MODEL_RECORD_INVALID", …)`. This is what makes "every
successful append leaves an immediately loadable valid revision" true
rather than aspirational.

**Typed failure is kernel-wide, not query-only.** Every public entry point
— `ModelStore` construction, `append`, `load`, `replay`,
`validate_record_collection`, `build_record`, `ModelQueries` construction,
and every query method — fails through the `ModelKernelError` tree.
Nothing outside that tree escapes as the public outcome: not
`ValidationError`, `KeyError`, `AttributeError`, `TypeError`,
`UnicodeError` (content that validates but cannot be canonically
serialized, such as a lone surrogate from hand-deserialized JSON, is a
structural defect → `MODEL_RECORD_INVALID`), `OSError` (missing or
unusable store directories → `MODEL_STORAGE_FAILURE`), serializer errors,
or warnings. The error tree lives in `errors.py` so `canonical` can raise
it without an import cycle.

**`append(record)` — validating append (deliberate, owner-approved
divergence from IB-001's record-local append; kernel records form a
referential graph and late detection would poison the set for every
reader):**

1. structurally revalidate the supplied record, then verify its
   content-derived ID;
2. **load and fully validate the complete current model set** — a corrupted
   or invalid existing set fails the append with a typed integrity error
   before anything else happens, even for a would-be no-op;
3. if the ID already exists: compare with the validated stored record —
   identical ⇒ idempotent no-op; different or tampered ⇒ typed integrity
   error, never overwritten;
4. otherwise validate the complete prospective collection (current + new)
   under every invariant above;
5. stage a unique temp file and atomically promote only after prospective
   validation succeeds. On any failure: no member file written, the previous
   revision byte-for-byte unchanged and loadable, staging cleaned.

Consequences (documented): construction order — types and registrations
before assertions that cite them, predecessors before successors; O(set)
validation per append (trivial at MK-001 scale; a derived projection can
change this later without contract change); **absent filesystem tampering,
the on-disk ledger is a valid revision after every successful append.**
Load-time full validation is retained unchanged because crafted files bypass
`append`.

**`load()`**: read every `records/*.json` (filename pattern gate), verify
every hash and key binding, run all-or-nothing validation, membership sorted
lexicographically, compute the revision. **`replay(record_ids)`**: every
supplied id pattern-checked BEFORE any path construction (traversal-proof),
duplicates rejected, subset must be reference-closed (cited types, endpoint
registrations, supersession predecessors, withdrawal targets, `model_record`
evidence), same validation on the subset; currentness is membership-relative
(a subset excluding a successor legitimately shows its predecessor current).
`LoadedModel` exposes only copied `MappingProxyType` views — a loaded
revision is genuinely immutable.

## Query surface

`ModelQueries(loaded_model)` — total functions over one explicit immutable
revision; no ambient model, no implicit clock; every result embeds the full
`ModelRevision`. **Public query arguments are validated and normalized
before evaluation** — anchor id, type name, direction, lifecycle view, and
assertion context: a valid context *mapping* is normalized into the
discriminated context model (so matching never compares against raw input
and malformed input never becomes a silently empty answer), a malformed
context raises `MODEL_CONTEXT_INVALID`, and an invalid view literal raises
`MODEL_VIEW_INVALID`. The semantic codes keep their meanings: malformed
ids → `MODEL_ANCHOR_ID_INVALID`, bad direction → `MODEL_DIRECTION_INVALID`,
unknown `type_name` → `MODEL_UNKNOWN_TYPE`, wrong/incompatible context arm
→ `MODEL_CONTEXT_MISMATCH`, missing/forbidden view →
`MODEL_VIEW_REQUIRED` / `MODEL_VIEW_FORBIDDEN`, hierarchy queries on
non-hierarchy types → `MODEL_NOT_A_HIERARCHY`. No public query path leaks
`ValidationError`, `AttributeError`, or `TypeError`. Absence and
disagreement are statuses, never exceptions.

**Relationship absence is structured**: `RelationshipsResult` carries
`status: registered | not_registered`, so an entity unknown to this
revision is never conflated with a registered entity that has no declared
edge. `not_registered` implies empty active, inactive, and lineage-conflict
tuples; `registered` may legitimately be empty; both carry the answering
revision and the normalized query context.

**Supported import surface**: callers import from `backend.model_kernel`,
which re-exports (with an explicit `__all__`) the ledger record contracts,
the assertion/query context contracts, the authority and evidence
contracts, the typed error tree, the result contracts, and `build_record`,
`ModelStore`, `LoadedModel`, `ModelQueries`. Canonicalization internals,
`validate_record_collection`, and the hierarchy projection are
implementation details and are deliberately not re-exported.

`relationships(anchor_id, direction=incoming|outgoing|both, type_name=None,
context: AssertionContext)` — strict context equality: the result contains
exactly the assertions whose stored context equals the query context; no
union form exists (two contexts = two explicit calls). With `type_name`,
the named lineage's `context_requirement` must match the supplied arm.
`entity`, `parents`, `children`, `ancestors`, `descendants`,
`hierarchy_health`, and `ModelStore.replay` behave per the sections above.

## Committed validation demo

`bindings/demo-printer-model/records/` — 3 `AnchorDeclaration`s (fixed
externally allocated uuid4-hex constants; authority `test_fixture`, agent
`mk001_demo_fixture`; notes stating synthetic status): demo printer root
(`physical_instance`), extrusion subsystem (`logical_instance`),
extruder-unit type (`type_definition`). Existing `bindings/demo-printer/`
records are not edited or deleted.

`models/demo-printer/records/` — **9 model records**, all `test_fixture`
authority: 2 `rtd_` (`contains`: lifecycle_view, containment,
source/target `{logical_instance, physical_instance}`, self false;
`instance_of`: view_independent, none, source `{logical_instance,
physical_instance}`, target `{type_definition}`, self false); 4 `reg_`
(root, subsystem, the existing extruder anchor
`ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`, the type anchor — embedded values
seam-verified equal to their declarations); 3 `rel_`: root —contains→
subsystem (`as_built`), subsystem —contains→ extruder (`as_built`),
extruder —instance_of→ extruder-unit-type (view-independent — the
non-hierarchical edge). Evidence: `owner_declaration` (synthetic-scenario
statement) plus `identity_binding_record` references to the extruder's
committed declaration on the extruder edges. No STEP/CAD reference anywhere;
no claim about a real printer. Golden revision-id constant pinned by test.

## Threat and failure model

Fabricated/undeclared anchors (structural validation + CI seam for committed
data + disclosed runtime boundary + documented external verification
procedure); identity authority (declaration only via identity-binding
ledgers; kernel consumes values; cross-set duplicate sweep over committed
sets); tampered files / forged keys / forged membership (hashes, key
binding, self-validating revisions, pre-path pattern checks); contradictory
parents and cycles (structured, never auto- or timestamp-resolved, subtree
isolation, deterministic detection); view mixing (required typed context, no
union path); evidence laundering (disjoint discriminated kinds, prose only
in `owner_declaration`, foreign refs never "verified", canonicalized
evidence prevents order/duplication games); semantic smuggling via type data
(no transitivity flag; containment obligations kernel-defined; lineage
invariants; `unknown` opt-in only); crash/partial writes (staging outside
scanned dir, atomic promote, residue harmless, on-disk-valid-after-append);
concurrency (honest single-writer statement); stale replay (typed errors;
results carry their revision); path leakage (error messages carry ids/names,
never absolute paths); secrets (ids, labels, notes only; authority is a
claimed name).

## Acceptance criteria

All `tests/model_kernel/` tests pass (189 as implemented, including the
owner-validation repair suite), including: structural revalidation at both
public store boundaries (rehashed `model_copy` and `model_construct`
corruption of all four record kinds and an unknown `record_kind` rejected
with typed path-free `MODEL_RECORD_INVALID`, no member file written, prior
revision byte-identical and still loadable, no serializer warning escaping,
and `validate_record_collection` rejecting a malformed instance directly);
typed query-input validation (`MODEL_VIEW_INVALID` across all five
hierarchy entry points, mapping-context normalization equalling the model
form, `MODEL_CONTEXT_INVALID` for malformed contexts, and a sweep proving
no public query raises anything outside the `ModelKernelError` tree); all
five lifecycle views as separate query partitions; registered-versus-
unregistered `RelationshipsResult.status` with its contract invariant; the
declared package import surface with internals staying private; plus: AST-based import
enforcement plus no-store-paths and stores-absent behavioral isolation;
byte-for-byte non-writes to accepted stores and existing binding records
including on failure paths; validating-append adversarial cases (dangling
relationship, duplicate registration, incompatible endpoint, context
mismatch, duplicate current type name — each rejected with the prior on-disk
revision intact) and tampered-other-member no-op refusal; registration
lifecycle absence (semantic duplicate rejection independent of field-shape
rejection); unknown opt-in positive and fail-closed cases; lineage rules
(invariant-field preservation, cross-lineage supersession invalid, stale
marking, branched-chain invalidity via crafted files, lineage-scoped
hierarchy); distinct-parent/same-child conflicts vs same-parent
corroboration; direct and 3+-node cycles with per-(lineage, view) scoping
and subtree isolation; five-state lineage disclosure incl. empty-lineage and
non-reactivation; traversal asymmetry and annotations; strict-context
queries incl. typed mismatch errors; evidence canonicalization golden tests
(permuted + duplicated inputs → same record id); canonical parity vectors
against `identity_binding.canonical`; seam verification (embedded anchors
field-for-field vs declarations, negative controls with teeth, cross-set
duplicate sweep, pattern-constant pinning); path-leakage negative
assertions; deterministic insertion-order independence; loaded-model deep
immutability; demo end-to-end with golden revision id. The pre-MK baseline
(544 all-extras / 511+33 base-only) is preserved; base-only and all-extras
clean checkouts pass; the enforceable upstream boundary holds.

## Known limitations (accepted)

No kernel correction path for registrations (upstream identity layer or a
different anchor); no registration or type-definition withdrawal —
membership and the type vocabulary are irrevocable in MK-001; a lineage may
end with no active assertion; disagreement detection exists only for
hierarchy types (multi-target `instance_of` is representable and unflagged);
no time-varying structure; runtime registration↔declaration consistency is
procedural, not enforced; no global cross-set anchor uniqueness at runtime;
no knowledge-time revision queries; single-writer stores; no fsync-grade
durability claim.
