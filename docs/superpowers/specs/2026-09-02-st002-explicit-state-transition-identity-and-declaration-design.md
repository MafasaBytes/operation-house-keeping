# ST-002 — Explicit State Transition Identity and Evidence-Gated Transition Disclosure

**Status:** corrected final architecture synthesis; pending final owner design approval

**Date:** 2026-09-02

**Repository baseline:** `main = origin/main = e44a18641ba6b440adcf9c10cd86d28376886942`

**Accepted model baseline:** 34 records at `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`

**Scope:** design and executable acceptance contracts only; this document authorizes no implementation, test, fixture, identity, record, ledger, artifact, commit, push, merge, or history operation

## 1. Source integrity and repository baseline

### 1.1 Reconciled sources

This final synthesis reconciles:

1. `docs/superpowers/proposals/2026-09-01-st002-codex-lead-proposal.md`,
   SHA-256 `2a26a9409a9307c49c9e665b3db70274b5c69546bde9871ae255d4a26bd6e34e`;
2. `docs/superpowers/reports/2026-09-01-st002-codex-lead-proposal-challenger-audit.md`,
   SHA-256 `4ce488ffc956758227227e634060df0448d44036eeccfa898ee996bcfbfa9602`;
3. the accepted ST-001 corrected final synthesis;
4. ADR-0016; and
5. the current System Identity, model-kernel, `ModelStore`,
   `ModelQueryMaterial`, `ModelQueries`, and state-result contracts at the
   repository baseline.

The lead proposal remains the architecture foundation. The challenger found
zero blocking architecture defects and five missing executable enforcement
rows. This synthesis incorporates all five corrections and the inexpensive
strengthenings without changing the lead record shape, identity policy,
query surface, declaration-only boundary, or lifecycle semantics.

### 1.2 Verified repository facts

| Fact | Verified value |
|---|---|
| `HEAD`, `main`, `origin/main` | `e44a18641ba6b440adcf9c10cd86d28376886942` |
| Authoritative model path | `models/demo-printer` |
| Authoritative membership | Exactly 34 records |
| Authoritative revision | `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41` |
| State registrations | Exactly one SRG |
| State declarations | Exactly one parentless STD |
| State withdrawals | Zero STW |
| Transition records | Zero TRG, TRD, and TRW |
| Existing state identity | `sta_ec739d80d5a843d28a91f4cf96de3883` |
| Existing state subject | `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50` |

The working tree was clean before the lead proposal was created. At synthesis
start, the lead proposal and challenger report were the only untracked files.
They are source artifacts and remain unmodified.

### 1.3 Binding repository conventions

ST-002 must preserve these accepted conventions:

1. System Identity owns opaque, frozen, extra-forbidden anchors and pure
   UUID4 minters.
2. Explicit engineering knowledge belongs to the existing model ledger.
3. Model record identity is
   `<prefix>_<sha256(normative canonical bytes excluding record_id)>`.
4. UTC canonical datetimes use Python `isoformat()` and therefore `+00:00`.
5. Evidence and parent tuples canonicalize; directed endpoint fields do not.
6. `ModelStore` validates the complete prospective membership before atomic
   promotion.
7. Historical replay is explicit, reference-closed, and membership-relative.
8. Public kernel results carry complete `ModelQueryMaterial` exactly once and
   reconstruct every conclusion without a store or filesystem.
9. Registrations are permanent. Declaration correction and withdrawal do not
   alter registration existence.
10. Model-kernel layers do not import state classification, evidence stores,
    source runtime, or temporal evaluation.

## 2. Reconciliation outcome and fixed owner decisions

### 2.1 Fixed decisions

The following decisions are closed and normative. They are not unresolved
implementation questions.

| ID | Fixed decision |
|---|---|
| D1 | ST-002 is declaration-only. Transition assessment and occurrence remain deferred. |
| D2 | Both endpoint states must belong to the exact same subject entity. |
| D3 | Self-transitions are rejected in v1. |
| D4 | One selected membership permits at most one permanent transition identity for each ordered same-subject `(from_state_anchor_id, to_state_anchor_id)` tuple. |
| D5 | State families and cross-context mapping remain deferred. |
| D6 | Endpoint-pin alignment is orthogonal to the transition-declaration lifecycle conclusion. |
| D7 | The authoritative demo ledger remains exactly 34 records by default; transition-positive coverage uses disposable fixtures. |
| D8 | Prefixes `trn_`, `trg_`, `trd_`, `trw_` and the four-query public surface in Section 12 are accepted. |

### 2.2 Exact mechanism distinction for D4

The one-identity-per-ordered-tuple rule separates three concepts:

- **Independent declaration roots** are multiple evidence claims about one
  transition identity. Identical healthy effective bodies corroborate;
  divergent bodies conflict. They do not create multiple transition
  identities.
- **Occurrence instances** would be particular claimed or assessed events of
  one declared transition. They belong entirely to the deferred occurrence
  plane and are not model registrations or declaration roots.
- **Genuinely distinct future mechanisms sharing endpoints** require a
  separately owner-gated additive identity discriminator or a new explicit
  contract. V1 has no trigger, event, action, or mechanism discriminator and
  must not create indistinguishable parallel registrations.

Any future relaxation is additive for new memberships. It must not reinterpret
an existing `trn_` identity, change any historical record's canonical meaning,
or change any historical `mrv_` replay conclusion.

### 2.3 Required challenger corrections incorporated

| Correction | Normative incorporation |
|---|---|
| RC1 | A new TRD may pin an already-superseded or already-withdrawn STD. No admission-time currentness gate or automatic retarget is allowed. |
| RC2 | Endpoint state conclusion and pin activity derive from the accepted kernel ST derivation, with parity or structural-unreachability coverage for the complete state-conclusion × pin-activity matrix. |
| RC3 | A two-parent merge within one root is admitted and resolves a fork; a parent tuple spanning independent roots rejects typed. |
| RC4 | `ModelRecordEvidence` gains `trg_` and `trd_` only; `trw_` remains uncitable and every existing evidence arm remains unchanged. |
| RC5 | All four queries execute against the untouched 34-record model and return the exact structured absence results in Section 21. |

### 2.4 Strengthenings incorporated

The final acceptance matrix also pins:

- uniform model-record evidence closure for TRG and TRD;
- idempotent equal-record re-append and contradictory same-ID rejection;
- exact `view_independent` context equality;
- forged alignment/activity-precedence rejection;
- coexistence of reversed ordered endpoint pairs as distinct transitions; and
- permanent `registered` lookup when every declaration root is inactive.

## 3. Objective and normative truth boundary

### 3.1 Objective

ST-002 adds the smallest model vocabulary able to say:

> Transition identity T is permanently registered for subject entity E as a
> directed relation from state identity A to state identity B. In exact
> context C, an authority declares T using exact endpoint state-declaration
> records DA and DB, with explicit evidence and a replayable declaration
> lifecycle.

The public kernel discloses that claim, its exact references, evidence,
lineage, current declaration agreement, endpoint pin activity and alignment,
and complete selected membership. It infers nothing from observations.

### 3.2 Normative short form

> `declared` means only that the selected model membership contains one
> admitted active transition-declaration effective body across healthy roots.
> It does not mean enabled, executable, occurring, observed, completed,
> physically possible now, causal, safe, healthy, correct, or recommended.

### 3.3 Six distinct concepts

| Concept | Meaning | ST-002 treatment |
|---|---|---|
| Observation | A source reported a value at one point occurrence. | Existing lower evidence; unchanged |
| State declaration | An authority declared one state-region meaning in an exact context. | Existing model knowledge; referenced exactly |
| State classification | Admitted observations satisfy or do not satisfy one declared state under a cutoff and revisions. | Existing returned result; not composed |
| Transition declaration | An authority declared one directed transition possibility between exact state-declaration meanings. | Included |
| Transition assessment | Evidence is consistent with a transition under an explicit temporal policy. | Deferred |
| Transition occurrence | An accountable claim that a particular transition occurred. | Deferred |

### 3.4 Non-creation rule

None of the following creates a transition identity, declaration, assessment,
or occurrence:

- names, roles, namespaces, shared subject ownership, hierarchy, or
  relationships;
- CAD, ports, VPA, PIF, PCN, PCM, behavior declarations, or semantic
  compatibility;
- CN satisfaction or one or more ST `matches` results;
- a changed observation, `change_class="changed"`, source-time order, receipt
  order, temporal proximity, or correlation;
- a later STD correction; or
- displaying endpoint states or observations beside one another.

## 4. Capability boundary and architecture decision

### 4.1 Included

- opaque directed transition identity;
- permanent same-subject endpoint registration;
- correctable exact-context transition declaration;
- exact from-state and to-state STD pins;
- evidence admission and complete reference closure;
- correction, same-root merge, conflict, independent-root corroboration,
  withdrawal, and historical replay;
- content-derived record IDs in the existing model revision;
- exactly four deterministic read-only kernel queries;
- endpoint state conclusion, exact pinned STD activity, and orthogonal
  alignment; and
- hostile carry-once outer-result reconstruction.

### 4.2 Excluded

- observation-derived transition assessment;
- occurrence identity, record, store, detector, or history;
- current transition, enablement, execution, or next-state selection;
- graph traversal, path finding, reachability, priority, or arbitration;
- trigger, event, guard, action, effect, mechanism, dwell, debounce,
  hysteresis, persistence, continuity, or temporal windows;
- state families, family-relative endpoints, exclusivity, completeness, or
  cross-context mapping;
- cross-entity and self-transitions; and
- control, commands, recommendations, safety, health, fault, diagnosis,
  correctness, or causality.

### 4.3 Architecture decision

ST-002 v1 is an additive System Identity and model-kernel extension only.
There is no `backend.transition_assessment` package, transition evaluator,
occurrence projection, secondary ledger, cache, or transition-specific
revision.

The title's “evidence-gated” term refers to admission of evidence-bearing TRG
and TRD model claims. It does not authorize evidence-gated occurrence
assessment.

## 5. Exact transition identity policy

### 5.1 Anchor contract

Add exactly:

```python
TRANSITION_ANCHOR_ID_PATTERN = r"^trn_[0-9a-f]{32}$"

class TransitionAnchor(...):
    anchor_id: str
    namespace: str
    display_name: str
    role_name: str | None = None
```

Field bounds and name grammar reuse the current `StateAnchor` and
`BehaviorAnchor` conventions. The model is frozen, extra-forbidden, and uses
`revalidate_instances="always"`.

The anchor contains no subject, endpoint, direction, context, evidence,
declaration, lifecycle, trigger, event, guard, action, effect, occurrence,
assessment, time, priority, outcome, or operational meaning.

### 5.2 Minter

Add exactly one public keyword-only minter:

```python
def mint_transition_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> TransitionAnchor:
    ...
```

It calls standard-library `uuid4()` once, uses `.hex`, prefixes `trn_`, and
constructs the frozen anchor. It performs no I/O, lookup, storage, authority
claim, timestamp capture, environment access, deterministic seeding, or
name-derived identity.

### 5.3 Permanent continuity

One TRG permanently fixes:

```text
(subject_entity_anchor_id, from_state_anchor_id, to_state_anchor_id)
```

Changing the subject or either state anchor requires a new transition anchor
and TRG. Changing the exact STD meaning while retaining both state anchors is
a TRD correction under the same transition identity.

### 5.4 Direction and tuple uniqueness

Endpoint order is semantic and is never sorted. `A → B` and `B → A` require
different `trn_` anchors and different TRGs; both may coexist in one
membership.

Within one selected membership, a second TRG with the same ordered
same-subject `(from_state_anchor_id, to_state_anchor_id)` tuple rejects whether
its evidence, names, time, authority, or note agree or differ.

### 5.5 Subject and self-transition constraints

Both endpoint SRGs must exist and both must name exactly the TRG's subject
entity. No hierarchy or relationship substitutes for direct identity
equality. `from_state_anchor_id == to_state_anchor_id` rejects.

### 5.6 Names

Names aid human disclosure only. Equal names do not merge identities;
different names do not split identities; names never select endpoints,
declarations, or query results.

## 6. Exact model-record contracts and prefixes

### 6.1 Record family

| Prefix | Record kind | Citable as `ModelRecordEvidence` |
|---|---|---|
| `trg_` | `transition_registration` | yes |
| `trd_` | `transition_declaration` | yes |
| `trw_` | `transition_declaration_withdrawal` | no |

All three enter the model record ID grammar, filename grammar,
discriminator-to-prefix map, discriminated adapter, `ModelRecord` union,
store partitions, and public model-kernel exports. Only `trg_` and `trd_`
enter the `ModelRecordEvidence.record_id` grammar.

No separate correction, fork, root, assessment, or occurrence record is
added. A correction or same-root merge is another TRD. An independent claim
root is a parentless TRD.

### 6.2 `TransitionRegistration`

```text
TransitionRegistration
  record_kind: Literal["transition_registration"]
  schema_version: Literal["1"]
  record_id: trg_[0-9a-f]{64}
  anchor: TransitionAnchor
  subject_entity_anchor_id: EntityAnchorId
  from_state_anchor_id: StateAnchorId
  to_state_anchor_id: StateAnchorId
  evidence: NonEmptyCanonicalEvidenceTuple
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

TRG has no context, parents, withdrawal target, endpoint STD pin,
`transition_family`, mechanism discriminator, classification, assessment,
occurrence, trigger, event, guard, action, effect, priority, timing, or
outcome.

### 6.3 `TransitionStateDeclarationPin`

```text
TransitionStateDeclarationPin
  state_anchor_id: StateAnchorId
  declaration_record_id: std_[0-9a-f]{64}
```

It is frozen, extra-forbidden, and always revalidates nested instances. The
containing field supplies role. The pin contains no role string, latest-tip
instruction, context, match, or observation.

### 6.4 `TransitionDeclaration`

```text
TransitionDeclaration
  record_kind: Literal["transition_declaration"]
  schema_version: Literal["1"]
  record_id: trd_[0-9a-f]{64}
  transition_anchor_id: TransitionAnchorId
  context: AssertionContext
  from_endpoint: TransitionStateDeclarationPin
  to_endpoint: TransitionStateDeclarationPin
  evidence: NonEmptyCanonicalEvidenceTuple
  supersedes: CanonicalTransitionDeclarationIdTuple = ()
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

TRD deliberately has no `evaluation_basis`: ST-002 defines no evaluation
algorithm. It has no enabled, executable, assessment, occurrence, trigger,
event, guard, action, effect, duration, priority, confidence, probability,
validity, or recommendation field.

Parents are distinct `trd_` IDs, canonicalized lexicographically. Duplicate,
self, malformed, missing, cross-transition, cross-context, cyclic, and
cross-root parentage reject.

### 6.5 `TransitionDeclarationWithdrawal`

```text
TransitionDeclarationWithdrawal
  record_kind: Literal["transition_declaration_withdrawal"]
  schema_version: Literal["1"]
  record_id: trw_[0-9a-f]{64}
  withdraws: trd_[0-9a-f]{64}
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

TRW has no evidence, context, anchor copy, parents, replacement, outcome,
reason code, occurrence, or negative transition claim. It means only that one
positive declaration tip is no longer asserted in the selected membership.

## 7. Evidence requirements and closure

### 7.1 Uniform evidence rule

For every evidence-bearing TRG or TRD, the store first applies the existing
uniform model-record evidence closure rule: every `ModelRecordEvidence`
reference must name a present record in the exact selected membership. Wrong
kind, malformed ID, dangling reference, and reference to a record omitted from
an explicit replay membership reject.

Required role-specific citations are additional to, never replacements for,
uniform closure. Additional admitted evidence is allowed but every additional
model-record citation remains subject to the same closure rule.

### 7.2 TRG evidence checklist

Every TRG requires:

1. a direct `ModelRecordEvidence` citation to the exact subject entity
   registration;
2. a direct citation to the exact from-state SRG;
3. a direct citation to the exact to-state SRG;
4. at least one claim-bearing `OwnerDeclarationEvidence`; and
5. closure for every additional model-record evidence reference.

The evidence tuple is nonempty and canonical. Subject equality, names,
hierarchy, topology, classifications, or observations do not substitute for
the claim-bearing arm.

### 7.3 TRD evidence checklist

Every TRD requires:

1. a direct citation to the exact TRG;
2. direct citations to both endpoint SRGs;
3. direct citations to both exact pinned endpoint STDs;
4. at least one claim-bearing `OwnerDeclarationEvidence` supporting this
   exact context and pin pair;
5. every parent TRD present through declaration closure; and
6. closure for every additional model-record evidence reference.

The deeper CRG/VCN evidence behind each STD remains the admitted STD's own
ST-001 responsibility. TRD does not duplicate that lower admission logic.

### 7.4 Evidence-arm compatibility

The existing evidence union and every existing record-ID arm remain unchanged.
The only regex additions are `trg` and `trd` to `ModelRecordEvidence`.
`trw_` and all existing withdrawal prefixes remain uncitable.

Evidence proves explicit support for a model claim. Kernel structural
validation does not authenticate foreign raw bytes and never converts a
citation into transition-occurrence evidence.

## 8. Store admission and validation order

### 8.1 Public append sequence

`ModelStore.append(record)` retains this exact order:

1. structurally revalidate the supplied record from field data;
2. verify `record_id` against normative canonical bytes;
3. load and fully validate the complete current membership;
4. if the ID already exists and content is exactly equal, return the ID as an
   idempotent no-op;
5. if the ID already exists but content differs, reject typed as a
   contradictory same-ID/hash-integrity failure;
6. form the prospective membership;
7. run complete prospective `validate_record_collection()`;
8. serialize the stored payload from normative canonical content plus the
   exact record ID; and
9. atomically promote one file.

Any validation or persistence failure writes no final record file.

### 8.2 Transition-family full-set validation order

Within full-set validation, after existing entity and ST records have been
authoritatively rebuilt and indexed:

1. partition exact TRG, TRD, and TRW records by discriminator;
2. validate each TRG's anchor uniqueness, ordered-tuple uniqueness, subject,
   endpoint SRGs, same-subject equality, non-self rule, uniform evidence
   closure, mandatory citations, and claim basis;
3. validate each TRD's TRG, ordered endpoint anchors, exact pinned STD
   existence and kind, STD anchor equality, exact context equality, uniform
   evidence closure, mandatory citations, claim basis, and parent shapes;
4. build the declaration DAG with the existing iterative lifecycle helper,
   requiring one `(transition_anchor_id, exact context)` key and one root for
   every parent tuple;
5. reject cycles and cross-root convergence;
6. validate each TRW against a present current unsuperseded TRD tip and reject
   duplicate withdrawals;
7. reject successor-plus-withdrawal in one membership;
8. derive ancestry, successors, roots, withdrawals, current tips, subject
   reverse indexes, and ordered-tuple indexes deterministically; and
9. compute the existing `mrv_` from sorted exact membership.

No transition validation reads current observations, state classifications,
bindings, interpretations, temporal stores, source runtime, filesystem
outside `ModelStore`, network, or wall clock.

### 8.3 TRG semantic admission

Reject:

- unknown subject, from-state, or to-state registration;
- endpoint SRGs whose permanent subjects differ from the TRG subject;
- equal from/to anchors;
- a second registration for one `trn_` anchor;
- a second transition identity for the same ordered same-subject endpoint
  tuple;
- reversed-role substitution inside one TRG;
- missing mandatory citations or claim basis; and
- any failure of uniform evidence closure.

Reversed pairs `A → B` and `B → A` are not duplicates and may coexist under
distinct anchors.

### 8.4 TRD semantic admission

Reject:

- missing TRG or endpoint STD;
- pin anchor differing from the permanent endpoint role;
- pinned STD naming another state anchor;
- pinned STD context differing by kind, lifecycle view, or any content from
  the TRD context;
- missing mandatory citations, claim basis, parent, or evidence dependency;
- parent from another transition, context, or independent root; and
- duplicate, noncanonical, self, or cyclic parentage.

Do **not** require a pinned STD to be current. A new TRD may deliberately pin
an STD that is already superseded or withdrawn. Existence, kind, anchor,
context, and evidence closure are admission facts; currency is query data.

### 8.5 Exact context equality

Both endpoint STDs must equal the TRD's exact `AssertionContext`.

- `LifecycleViewContext(kind="lifecycle_view", view="as_operated")` matches
  only that exact context.
- `ViewIndependentContext(kind="view_independent")` matches only the exact
  `view_independent` context.
- A disposable positive test must admit a TRD whose two endpoint STDs and TRD
  all use `view_independent`.
- Mixing `view_independent` with any lifecycle view, or two different
  lifecycle views, rejects typed.

No context conversion, default, inheritance, or mapping is available.

## 9. Endpoint declaration pins and alignment

### 9.1 Identity pin versus meaning pin

TRG pins permanent endpoint StateAnchors. TRD pins exact endpoint STD record
identities. This split lets state identity survive correction while preventing
a later STD from silently redefining an existing transition declaration.

### 9.2 Correction behavior

| Change | Required action |
|---|---|
| Endpoint STD corrected; state anchor unchanged | Explicit new TRD pinning the new STD |
| Both endpoint STDs corrected | One explicit new TRD pinning both |
| Subject changed | New `trn_` and TRG |
| From-state anchor changed | New `trn_` and TRG |
| To-state anchor changed | New `trn_` and TRG |
| Anchor metadata renamed | No identity or semantic retarget |
| No TRD correction after STD correction | Existing TRD stays exact; pin activity/alignment disclose historical meaning |

No query ever replaces a pin with “latest STD.” An engineering-identical STD
successor is still a different exact record.

### 9.3 One authoritative ST derivation source

Endpoint disclosure must use the accepted kernel ST derivation, not a copied
transition-specific implementation:

- state conclusion comes from the same
  `backend.model_kernel.state_results._state_declaration_payload()` semantic
  source used by public `state_declaration()`; and
- exact pin activity comes from the same
  `_state_assertion_payload()` semantic source used by public
  `state_assertion()`.

Implementation may factor these helpers into shared kernel-internal functions,
but there must remain exactly one semantic derivation per ST concept. The
transition result module is inside `backend.model_kernel`, so this reuse does
not reverse a package dependency or import `backend.state_classification`.

For identical `(material, state_anchor_id, exact context)`, every endpoint
`state_declaration_conclusion` must equal the public
`ModelQueries.state_declaration()` conclusion. For the exact pinned STD, every
`pinned_declaration_activity` must equal public `state_assertion()` activity.

### 9.4 Endpoint fields

Each active transition effective-body group contains fixed `from_endpoint`
and `to_endpoint` result rows with:

```text
role
state_anchor_id
state_registration_index
declaration_index
state_declaration_conclusion
pinned_declaration_activity
alignment
```

Role is `from` or `to`. Activity reuses accepted `AssertionActivity`:
`current`, `superseded`, or `withdrawn`.

### 9.5 Alignment vocabulary

```python
TransitionEndpointPinAlignment = Literal[
    "exact_current",
    "pinned_declaration_superseded",
    "pinned_declaration_withdrawn",
    "endpoint_state_conflicted",
    "endpoint_state_inactive",
]
```

Alignment is membership-relative and model-only. It is not temporal alignment,
observation freshness, transition validity, or occurrence evidence.

### 9.6 Complete conclusion/activity parity matrix

Every cell below requires an executable parity or structural-unreachability
assertion. “Unreachable” is proven by full-set validation; it is not silently
omitted from coverage.

| Accepted ST conclusion | Pin activity | Reachability for an admitted active TRD body | Alignment |
|---|---|---|---|
| `not_registered` | `current` / `superseded` / `withdrawn` | Unreachable: exact SRG and STD closure is mandatory | No endpoint row can carry this combination |
| `not_declared` | `current` / `superseded` / `withdrawn` | Unreachable: the pinned STD itself creates an exact-context root | No endpoint row can carry this combination |
| `declared` | `current` | Reachable | `exact_current` |
| `declared` | `superseded` | Reachable | `pinned_declaration_superseded` |
| `declared` | `withdrawn` | Reachable when another healthy root keeps the state declared | `pinned_declaration_withdrawn` |
| `conflicted` | `current` | Reachable | `endpoint_state_conflicted` |
| `conflicted` | `superseded` | Reachable | `endpoint_state_conflicted` |
| `conflicted` | `withdrawn` | Reachable | `endpoint_state_conflicted` |
| `inactive` | `current` | Unreachable: a current STD is an active tip | No endpoint row can carry this combination |
| `inactive` | `superseded` | Reachable when the terminal successor is withdrawn | `endpoint_state_inactive` |
| `inactive` | `withdrawn` | Reachable | `endpoint_state_inactive` |

Conflict and inactivity take precedence in the single alignment field. The
separate activity field preserves whether the exact pin is current,
superseded, or withdrawn. A forged result that swaps these precedence rules
must fail outer revalidation.

### 9.7 RC1 stale-at-admission behavior

A new TRD pinning an already-superseded STD is admitted. With the endpoint
state otherwise `declared`, transition lifecycle remains `declared`, pin
activity is `superseded`, alignment is
`pinned_declaration_superseded`, and the result still points to the exact old
STD.

A new TRD pinning an already-withdrawn STD is also admitted. The normative RC1
fixture includes another healthy state root so the endpoint state remains
`declared`; transition lifecycle is `declared`, pin activity is `withdrawn`,
alignment is `pinned_declaration_withdrawn`, and no current STD is substituted.
The separate inactive-state rows in Section 9.6 continue to govern a world in
which all endpoint-state roots are inactive.

## 10. Declaration lifecycle, conflict, withdrawal, and replay

### 10.1 Lineage key

The exact key is:

```text
(transition_anchor_id, exact AssertionContext)
```

Different contexts have independent declaration sets and cannot be connected
by parentage.

### 10.2 Roots and corrections

- `supersedes=()` creates an independent root.
- One parent creates an ordinary correction in that root.
- Two or more parents create a merge only when all parents belong to the same
  root.
- A parent tuple crossing independent roots rejects typed.
- Parent order is canonical and carries no precedence.
- DAG validation is iterative, membership-bounded, and recursion-independent.

### 10.3 Same-root merge

A same-root fork with tips T1 and T2 is conflicted. A new TRD T3 with
`supersedes=(T1, T2)` is admitted when both parents belong to that one root.
After T3:

- T1 and T2 are `superseded`;
- T3 is the sole current tip;
- root health is `healthy`; and
- the aggregate conclusion is recomputed from all roots and effective bodies.

Partial convergence that leaves two or more tips remains conflicted.

### 10.4 Effective body

The private transition effective body contains exactly:

```text
transition_anchor_id
exact AssertionContext
from_endpoint pin
to_endpoint pin
```

It excludes record ID, evidence, authority, `recorded_at`, note, parents,
filename, and append order.

### 10.5 Root health

| Current tips | Root health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2 or more | `conflicted` |

A same-root fork remains conflicted even if every active tip has an identical
effective body. No ID, timestamp, authority, evidence count, filename, or
append order chooses a winner.

### 10.6 Independent roots

| Active shape | Aggregate behavior |
|---|---|
| One healthy root/body | Declared; `one_healthy_root` |
| Two or more healthy roots with identical bodies | Declared; `corroborating_healthy_roots` |
| Healthy roots with different bodies | Conflicted; `cross_root_effective_body_disagreement` |
| Any same-root fork | Conflicted; `same_root_conflict` |
| Inactive roots beside active roots | Preserve active result and add `inactive_roots_present` |
| All roots inactive | `inactive` |

Independent roots remain separate evidence claims. Corroboration never merges
records or transition identity.

### 10.7 Withdrawal

TRW targets exactly one current unsuperseded TRD tip. Unknown, wrong-kind,
superseded, non-tip, already-withdrawn, and duplicate targets reject. A
membership containing both a successor and withdrawal of the same tip rejects
regardless of append order.

Selective withdrawal of one fork tip is allowed and recomputes root health.
A registration remains permanent even when every declaration root becomes
inactive.

### 10.8 Historical replay

All lifecycle and alignment conclusions are relative to the explicitly
selected membership. Replaying an older membership that omits a successor or
withdrawal makes the older declaration current again. Replay never uses
timestamps, directory enumeration, filename prefixes, or append order to
reconstruct history.

A later endpoint STD correction or withdrawal never invalidates the canonical
bytes or admission of an older TRD in a historical reference-closed
membership.

## 11. Canonicalization, record identity, and model revision

### 11.1 Normative record canonicalization

Transition records use only `backend.model_kernel.canonical`:

1. structurally validate the complete record;
2. `model_dump(mode="python", exclude={"record_id"})`;
3. recursively normalize every datetime to UTC `.isoformat()`;
4. preserve semantic list/tuple order, including from/to fields;
5. JSON-encode with sorted keys, compact separators, UTF-8, and
   `ensure_ascii=False`; and
6. compute SHA-256 over the exact bytes.

Every suffix must equal `sha256(canonical_bytes(record))`. Any field labeled
canonical must derive from `canonical_payload()` or `canonical_bytes()`.
JSON-mode `Z` timestamp rendering must never be labeled normative canonical;
the kernel contract uses `+00:00`.

### 11.2 Prefix mapping

Add exactly:

```text
transition_registration             -> trg
transition_declaration              -> trd
transition_declaration_withdrawal   -> trw
```

Unknown kinds and wrong prefix/kind combinations reject. All existing
canonical golden vectors remain byte-identical.

### 11.3 Canonical ordering

- evidence refs: existing full canonical evidence key;
- parents: unique lexicographic ID order;
- from/to fields: fixed semantic role order, never sorted;
- effective-body groups: canonical effective-body bytes; and
- stored JSON: canonical payload plus record ID, existing pretty-file format.

Equal instants with different offsets produce the same UTC canonical bytes.
Reversing evidence or parent input order preserves identity. Reversing from/to
roles changes canonical bytes and record ID.

### 11.4 Revision and store

TRG/TRD/TRW join the existing model ledger and `mrv_` algorithm. The revision
remains a hash of model ID plus sorted exact record membership. No `trv_`,
transition store, secondary model root, cache, projection, or persisted query
result is introduced.

## 12. Exact public query surface

ST-002 adds exactly these four read-only `ModelQueries` methods:

```python
transition(transition_anchor_id) -> TransitionLookupResult

transition_declaration(
    transition_anchor_id,
    *,
    context,
) -> TransitionDeclarationResult

transitions_of_entity(
    entity_anchor_id,
    *,
    context,
) -> EntityTransitionsResult

transition_assertion(
    record_id,
) -> TransitionAssertionDisclosureResult
```

Queries operate on one injected `LoadedModel`, own no store, perform no write,
and carry `ModelQueryMaterial` exactly once. They accept no name, cutoff,
source selector, observation, classification, endpoint-discovery criteria,
path, priority, or automatic context.

There are no aliases or methods named `current_transition`,
`detect_transition`, `assess_transition`, `possible_transitions`,
`enabled_transitions`, `next_state`, `transitions_from_state`,
`transition_path`, or `transition_history`.

### 12.1 `transition()`

Looks up permanent registration existence only. A registered transition
remains `registered` when it has no declaration, when all declaration roots
are inactive, or when declarations conflict.

### 12.2 `transition_declaration()`

Discloses the exact-context declaration lifecycle, roots, tips, withdrawals,
effective-body groups, current declaration indices, and endpoint state/pin
disclosures for active groups.

### 12.3 `transitions_of_entity()`

Returns every TRG whose permanent subject equals the exact requested entity,
including not-declared, declared, conflicted, and inactive contextual entries.
It infers nothing from endpoint names, hierarchy, evidence, or relationships.

### 12.4 `transition_assertion()`

Accepts only valid-shaped `trg_`, `trd_`, or `trw_` IDs. It returns structured
absence for a valid-shaped missing ID. Found TRGs and TRWs have null
declaration-lifecycle fields; found TRDs disclose activity, root health,
containing conclusion, findings, successors, and withdrawals.

## 13. Public result contracts and vocabulary

### 13.1 Exact literals

```python
TransitionLookupStatus = Literal[
    "not_registered",
    "registered",
]

TransitionDeclarationConclusion = Literal[
    "not_registered",
    "not_declared",
    "declared",
    "conflicted",
    "inactive",
]

TransitionDeclarationLineageSummary = Literal[
    "not_applicable",
    "healthy",
    "conflicted",
    "inactive",
]

TransitionAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]

TransitionEndpointRole = Literal["from", "to"]

EntityTransitionsStatus = Literal[
    "entity_not_registered",
    "registered",
]

TransitionAssertionLookupStatus = Literal[
    "not_found",
    "found",
]
```

Endpoint alignment uses Section 9.5. Reuse existing `AssertionActivity` and
`ContainingLineageHealth` exactly. No result literal says enabled, executable,
possible-now, detected, occurred, completed, valid, safe, healthy-transition,
causal, or recommended.

### 13.2 `TransitionLookupResult`

```text
material
transition_anchor_id
status
registration_index
subject_entity_registration_index
from_state_registration_index
to_state_registration_index
```

For `not_registered`, all four indices are `None`. For `registered`, each is
the exact strict non-boolean material index.

### 13.3 Lightweight lifecycle rows

```text
TransitionEndpointResult
  role
  state_anchor_id
  state_registration_index
  declaration_index
  state_declaration_conclusion
  pinned_declaration_activity
  alignment

TransitionEffectiveBodyGroupResult
  group_index
  representative_declaration_index
  current_tip_indices
  root_record_indices
  from_endpoint
  to_endpoint

TransitionDeclarationRootResult
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health
  effective_body_group_indices
```

Rows contain indices, not duplicated authoritative records. Convenience
properties resolve only through private binding to the one carried material.

### 13.4 `TransitionDeclarationResult`

```text
material
transition_anchor_id
context
conclusion
lineage_summary
agreement_findings
registration_index
roots
effective_body_groups
current_declaration_indices
```

Endpoint rows exist only inside active effective-body groups. An absent,
not-declared, or fully inactive transition has no endpoint group row even
though historical roots may remain disclosed for inactivity.

### 13.5 `EntityTransitionsResult`

```text
EntityTransitionEntry
  entry_index
  transition_anchor_id
  transition_registration_index
  conclusion
  lineage_summary
  agreement_findings
  roots
  effective_body_groups
  current_declaration_indices

EntityTransitionsResult
  material
  entity_anchor_id
  context
  status
  entity_registration_index
  entries
```

A registered entity with zero transitions returns `registered` and empty
entries.

### 13.6 `TransitionAssertionDisclosureResult`

```text
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

Activity and containing fields apply only to a found TRD. Conflict is a root
or subject conclusion, never an individual TRD activity.

### 13.7 Carry-once material

Every outer result carries exactly one complete `ModelQueryMaterial` with:

- exact `ModelRevision`;
- every selected record once in lexicographic ID order;
- record IDs exactly equal revision membership; and
- no second snapshot in nested rows.

All row and record indices are `StrictInt >= 0`; booleans reject.

## 14. Complete public decision tables

### 14.1 Registration lookup

| Exact TRG | `status` | Indices |
|---|---|---|
| Absent | `not_registered` | All `None` |
| Present and admitted | `registered` | Exact TRG, subject, from-SRG, to-SRG indices |

Declaration inactivity or conflict never changes a present TRG's lookup
status.

### 14.2 Declaration conclusion

| TRG | Exact-context roots | Active shape | `conclusion` |
|---|---:|---|---|
| Absent | Any | Not evaluated | `not_registered` |
| Present | 0 | Not applicable | `not_declared` |
| Present | 1+ | No active tips anywhere | `inactive` |
| Present | 1+ | Any same-root fork | `conflicted` |
| Present | 2+ healthy | Different effective bodies | `conflicted` |
| Present | 1+ healthy | One identical active body group | `declared` |

### 14.3 Lineage summary

| Conclusion | Summary |
|---|---|
| `not_registered` | `not_applicable` |
| `not_declared` | `not_applicable` |
| `declared` | `healthy` |
| `conflicted` | `conflicted` |
| `inactive` | `inactive` |

### 14.4 Agreement findings

Findings are independently derived and emitted in this exact order:

| Condition | Finding |
|---|---|
| Exactly one healthy root | `one_healthy_root` |
| At least two healthy roots share one body | `corroborating_healthy_roots` |
| At least one same-root fork | `same_root_conflict` |
| Healthy roots contain more than one body | `cross_root_effective_body_disagreement` |
| At least one inactive root | `inactive_roots_present` |

### 14.5 Root health

| Active tips after withdrawals | Health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2+ | `conflicted` |

### 14.6 Endpoint alignment

The complete parity/precedence table is Section 9.6. For reachable cells:

| State conclusion | Pin activity | Alignment |
|---|---|---|
| `declared` | `current` | `exact_current` |
| `declared` | `superseded` | `pinned_declaration_superseded` |
| `declared` | `withdrawn` | `pinned_declaration_withdrawn` |
| `conflicted` | Any | `endpoint_state_conflicted` |
| `inactive` | `superseded` or `withdrawn` | `endpoint_state_inactive` |

Endpoint alignment never changes transition declaration conclusion.

### 14.7 Entity collection

| Entity | Status | Entries |
|---|---|---|
| Not registered | `entity_not_registered` | Empty |
| Registered | `registered` | Every exact-subject TRG, possibly empty |

Each entry reuses the same transition declaration derivation as the direct
query.

### 14.8 Assertion lookup

| Valid-shaped transition record ID | Selected matching record | Lookup |
|---|---|---|
| `trg_`, `trd_`, or `trw_` | Absent | `not_found` |
| Exact kind and ID | Present | `found` |

Malformed or non-transition IDs fail typed before model index access.

### 14.9 Assertion activity

Only found TRDs have activity:

| Direct successors | Withdrawal | Activity |
|---:|---:|---|
| 1+ | Any defensively supplied state | `superseded` |
| 0 | 1 | `withdrawn` |
| 0 | 0 | `current` |

The successors-first row matches accepted ST defensive precedence even though
full-set validation rejects successor-plus-withdrawal.

### 14.10 Containing lineage health

| Containing root tips | Health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2+ | `conflicted` |

Containing conclusion and findings are exactly those for the TRD's
transition/context key.

## 15. Authoritative outer-result reconstruction

### 15.1 Trust boundary

No caller-supplied result field, nested Pydantic instance, private attribute,
cached object, index, conclusion, activity, or alignment is trusted. A valid
result means only that its entire supplied payload equals fresh authoritative
derivation from its carried model material.

### 15.2 Required validation sequence

Every transition outer result must:

1. inspect the supplied object graph before serialization and reject hidden
   `model_copy`/`model_construct` extras;
2. use bounded iterative traversal and reject hostile cycles or excessive
   depth deterministically;
3. require strict non-boolean integers for revision counts and every index;
4. reconstruct `ModelRevision` and every record from serialized field data;
5. require unique lexicographically ordered records;
6. require exact equality between carried records and revision membership;
7. call authoritative `validate_record_collection()` on the complete set;
8. require recomputed revision equality;
9. reconstruct contexts and nested rows from plain content;
10. derive the expected transition payload from the rebuilt `LoadedModel`;
11. derive endpoint state conclusions and pin activities through the shared ST
    derivation specified in Section 9.3;
12. compare every supplied field, ordering, activity, and alignment exactly;
13. bind private material access only after equality succeeds; and
14. perform no store, filesystem, network, environment, clock, cache, or write
    access.

### 15.3 Mandatory forgery rejection

Reject:

- missing, duplicate, extra, reordered, or mixed-revision material;
- stale IDs, filename/content substitutions, and wrong union arms;
- forged subject, endpoint role, endpoint anchor, STD pin, or context;
- forged roots, ancestry, tips, successors, withdrawals, body groups,
  corroboration, conflict, or conclusion;
- forged state conclusion, pin activity, or alignment;
- an activity/alignment precedence swap, including
  `pinned_declaration_superseded` supplied while authoritative state
  conclusion is `conflicted`;
- bool, float, string, negative, out-of-range, or wrong-arm indices;
- hidden implication-bearing fields such as `occurred`, `triggered_by`,
  `confidence`, or `recommended_action`; and
- a nested row or result built against another material snapshot.

### 15.4 Authenticity limitation

Carry-once reconstruction proves internal coherence of the selected model
membership. It does not authenticate external evidence bytes beyond the
existing evidence contracts and does not prove a transition occurred.

## 16. Import direction and package ownership

### 16.1 Ownership table

| Concern | Owner |
|---|---|
| `TransitionAnchor`, pattern, minter | `backend.system_identity` |
| TRG/TRD/TRW contracts, builders, canonical identity | `backend.model_kernel` |
| Full-set admission, lifecycle, indexes, replay | `backend.model_kernel.store` |
| Transition query/result derivation | `backend.model_kernel` |
| Accepted ST lifecycle derivation reused by endpoints | `backend.model_kernel.state_results` |
| Observations and temporal point history | Existing lower packages; unchanged |
| State classification | `backend.state_classification`; unchanged and not imported by kernel |
| Future transition assessment | Later upper layer; absent in ST-002 |

### 16.2 Permitted direction

```text
system_identity
      ↑
model_kernel (including state_results and transition results)
      ↑
future transition_assessment, if separately designed
```

Arrows mean “may be depended on by the layer above.” Reusing
`state_results` from another model-kernel module is same-layer reuse, not a
dependency reversal.

### 16.3 Forbidden dependencies and capabilities

- `system_identity` must not import model-kernel code.
- Model kernel must not import `state_classification`, constraint evaluation,
  behavior evaluation, binding or interpretation stores, temporal stores,
  source connectors, ingestion, structural evidence, CAD, PDF, filesystem
  paths, sockets, environment, or clocks for transition derivation.
- `ModelQueries` owns no `ModelStore` and performs no persistence.
- No lower package imports a future transition-assessment layer.
- No result validator accesses a repository, cache, database, network, or
  write capability.

## 17. Temporal and evidence-assessment boundary

### 17.1 Why transition assessment is unsupported

ST-001 evaluates each condition from independently latest evidence at or
before one cutoff. Its temporal alignment is `not_asserted`. Evidence may be
stale, conditions may have different receipt times, and multiple states may
simultaneously `match`.

`TemporalOccurrence` is a point fact and explicitly does not prove persistence
until another poll. Temporal `change_class` is only exact source-value change.
BH same-acquisition cohort proves one shared acquisition envelope, not
longitudinal continuity.

Therefore:

| Available fact | Permitted ST-002 conclusion |
|---|---|
| From-state `matches` at cutoff A | No transition conclusion |
| To-state `matches` at cutoff B | No transition conclusion |
| Both in that order | No exit, entry, continuity, or occurrence conclusion |
| Observation value changed | No semantic transition conclusion |
| Receipt/source times are ordered or close | No causal or persistence conclusion |
| BH reports same cohort | No cross-cutoff continuity conclusion |
| One TRD is `declared` and pins exact-current endpoints | Declared model claim only |

### 17.2 Deferred prerequisites

A later assessment milestone must separately define and owner-accept:

- explicit ordered assessment instants and governing time axis;
- cohort-aligned evidence for all endpoint conditions;
- cross-source skew/cohort rules;
- interval coverage plus gap, failure, quarantine, and omission policy;
- overlap/exclusivity policy;
- exact persistence, dwell, debounce, and hysteresis algorithms if used;
- bounded deterministic history/window selection;
- binding, interpretation, model, and temporal revision pins;
- raw-occurrence authenticity; and
- separate evidence-consistency and accountable-occurrence contracts.

No future milestone may reinterpret old ST `matches`, `change_class`, TRD
`declared`, or receipt order as proof that an occurrence happened.

## 18. Determinism, historical replay, and preservation

### 18.1 Deterministic ordering

- material records: lexicographic record ID;
- evidence: existing canonical evidence key;
- parents: lexicographic unique IDs;
- roots: root record ID;
- lineage, tips, successors, withdrawals: record ID;
- body groups: canonical body bytes;
- representative declaration: smallest ID in the group;
- findings: fixed Section 14.4 order;
- entity entries: transition anchor ID, then first root ID;
- endpoints: fixed `from`, then `to` role.

Hash seed, caller order, filesystem enumeration, append order, thread
schedule, timezone spelling before normalization, locale, and current clock
must not affect identity or query serialization.

### 18.2 Historical memberships

Explicit 9/10/11/14/16/18/28/29/32/34 record memberships retain exact IDs,
bytes, and revisions. They are never reconstructed from directory contents.
Every pre-transition membership returns structured transition absence.

Transition lifecycle tests add explicit disposable memberships for
registration, declaration, fork, same-root merge, independent roots,
withdrawal, stale pins, and historical revival.

### 18.3 Reproduction

Disposable deterministic columns initialize from explicit byte-identical
predecessors. At least one uses reversed predecessor copy/input order.
Candidate records are independently reconstructed through public builders and
appended through public `ModelStore`; record files are never copied between
roots.

Base-only and all-extras clean checkouts must reproduce canonical bytes,
record IDs, stored hashes, memberships, revisions, query serialization,
historical replay, and predecessor aggregates.

### 18.4 Preservation

Slices A–C modify no authoritative model, binding, interpretation, temporal,
source, structural, PT, VP, BH, or ST fixture/artifact. The model remains 34
records at the accepted revision with zero transition records. Existing
canonical vectors and artifact hashes remain unchanged.

## 19. Threat model

| Threat | Required defense |
|---|---|
| Name-derived identity | Opaque `trn_`; names non-semantic |
| Endpoint reversal or sorting | Fixed roles; reversal changes bytes and identity |
| Cross-entity endpoint | Direct same-subject equality at full-set validation |
| Self-transition laundering | Unequal endpoint rule |
| Indistinguishable parallel edge | Ordered tuple uniqueness |
| Silent endpoint correction adoption | Exact STD pins; no currentness gate or retarget |
| Stale pin incorrectly rejected | RC1 admission fixtures |
| Parallel ST lifecycle logic | RC2 shared derivation and parity matrix |
| Cross-root merge | Single-root parent invariant and typed rejection |
| All multi-parent merge rejected | RC3 positive same-root two-parent merge |
| Withdrawal cited as claim | RC4 evidence grammar negative case |
| Missing zero-transition behavior | RC5 authoritative 34-record query pins |
| Classification/value change called occurrence | No assessment API or occurrence vocabulary |
| Timestamp used as truth | Audit time excluded from conclusion logic |
| Same-root winner | Fork conflict regardless of ID/body |
| Cross-root winner | Body disagreement conflicts; IDs only order |
| Withdrawal treated as deletion | Immutable TRW and historical replay |
| Successor after withdrawal | Full-membership rejection |
| Hidden transition fields | `extra="forbid"` and nested revalidation |
| Forged activity/alignment precedence | Shared ST derivation and exact outer comparison |
| Bool/index coercion | Strict non-boolean integer indices |
| Cyclic/deep hostile payload | Iterative bounded traversal |
| Partial material | Exact revision membership validation |
| Canonical timestamp mismatch | Normative `canonical_bytes()` and `+00:00` tests |
| Nondeterministic output | Explicit ordering and independent reproduction |
| Ledger split | Existing ModelStore and `mrv_` only |
| Demo overclaim | 34-record default, disposable positive fixtures, disclaimer gate |

## 20. Corrected adversarial acceptance matrix

Every row is normative, executable, and required within its owner-gated
slice. RC1–RC5 are explicitly labeled for traceability.

### 20.1 Identity and fixed decisions

| ID | Acceptance criterion |
|---|---|
| I01 | `trn_` accepts exactly 32 lowercase hex characters; wrong prefix, case, length, and non-hex reject. |
| I02 | `mint_transition_anchor()` is keyword-only, calls UUID4 once, returns the exact frozen anchor, and performs no I/O. |
| I03 | Anchor extras or semantic fields for subject, endpoint, trigger, occurrence, or outcome reject. |
| I04 | Names never match, merge, discover, or select transitions. |
| I05 | Both endpoint SRGs must have the exact TRG subject; cross-entity registration rejects despite hierarchy or evidence. |
| I06 | Self-transition registration rejects. |
| I07 | A second identity for the same ordered same-subject tuple rejects. |
| I08 | Reversed pairs A→B and B→A under distinct anchors coexist as two directed transitions. |
| I09 | Independent TRD roots represent multiple evidence claims about one transition and never create another identity. |

### 20.2 Record, canonical, evidence, and append contracts

| ID | Acceptance criterion |
|---|---|
| R01 | `trg_`, `trd_`, `trw_` exact ID/filename grammars and discriminator mappings are pinned. |
| R02 | Every ID suffix equals SHA-256 of normative kernel canonical bytes excluding `record_id`. |
| R03 | UTC canonical timestamps contain `+00:00`; JSON-mode `Z` bytes are not labeled canonical. |
| R04 | Equal instants under different offsets produce identical IDs; stale IDs after mutation reject. |
| R05 | Evidence and parents canonicalize; valid reversed input order preserves identity. |
| R06 | Endpoint role reversal changes canonical bytes and record ID. |
| R07 | Effective-body bytes contain exactly transition ID, context, and ordered exact pins. |
| R08 | Unknown kinds, wrong prefixes, hidden fields, hostile nested instances, and filename/content mismatch reject. |
| R09 | All existing record/evidence golden vectors, schemas, IDs, and bytes remain unchanged. |
| RC4 | `ModelRecordEvidence` admits `trg_` and `trd_`, rejects `trw_`, preserves every existing evidence arm unchanged, and admits a TRD's mandatory TRG citation through store closure. |
| R11 | Equal-record re-append for each new kind is an idempotent validated no-op. |
| R12 | A contradictory record supplied under an existing same ID rejects typed and writes nothing. |

### 20.3 Registration, pins, evidence closure, and contexts

| ID | Acceptance criterion |
|---|---|
| S01 | Unknown subject, endpoint SRG, TRG, or pinned STD rejects. |
| S02 | TRG uniform model-record evidence closure runs before exact-citation/claim-basis admission. |
| S03 | TRD uniform model-record evidence closure runs before exact-citation/claim-basis admission. |
| S04 | TRG requires exact subject registration and both SRG citations plus claim-bearing evidence. |
| S05 | TRD requires exact TRG, both SRGs, both exact STDs, and claim-bearing evidence. |
| S06 | Endpoint pin role, anchor, kind, and exact context substitutions reject. |
| S07 | Two lifecycle contexts differing only in `view` reject as unequal. |
| S08 | Two endpoint STDs plus TRD with exact `view_independent` context admit. |
| S09 | `view_independent` mixed with any lifecycle context rejects typed. |
| RC1a | A new TRD pinning an already-superseded STD admits; TRD conclusion remains `declared`, activity is `superseded`, alignment is `pinned_declaration_superseded`, and the successor is not substituted. |
| RC1b | A new TRD pinning an already-withdrawn STD admits in the RC1 declared-state fixture; activity is `withdrawn`, alignment is `pinned_declaration_withdrawn`, and no active STD is substituted. |

### 20.4 Lifecycle, merge, conflict, and withdrawal

| ID | Acceptance criterion |
|---|---|
| L01 | Parent must be a present TRD for the same transition and exact context. |
| L02 | Duplicate, unsorted, self, missing, cyclic, cross-transition, and cross-context parents reject. |
| L03 | One root/one tip is healthy and declared. |
| L04 | Same-root fork conflicts even with identical bodies. |
| L05 | Partial same-root convergence remains conflicted. |
| RC3a | A same-root two-parent merge admits, makes both fork tips superseded, leaves one current tip, and restores healthy root state. |
| RC3b | A parent tuple spanning independent roots rejects with the typed transition-lineage error. |
| L08 | Identical independent healthy roots corroborate without merging identity. |
| L09 | Different healthy root bodies conflict without winner selection. |
| L10 | Inactive roots remain visible beside active roots. |
| L11 | All roots inactive yields transition declaration `inactive` while `transition()` remains `registered`. |
| L12 | TRW rejects missing, wrong-kind, superseded, non-tip, already-withdrawn, and duplicate targets. |
| L13 | Successor-plus-withdrawal rejects regardless of record/input order. |
| L14 | Selective withdrawal of one fork tip recomputes root health. |
| L15 | Historical membership omitting successor/withdrawal revives the old tip. |
| L16 | Deep declaration DAG validation is iterative and independent of Python recursion depth. |

### 20.5 Query conclusions and RC2 parity

| ID | Acceptance criterion |
|---|---|
| Q01 | Exactly the four accepted method names/signatures exist; no aliases, assessment, traversal, or occurrence query leaks. |
| Q02 | Exact result fields, literal order, and exports are pinned. |
| Q03 | Lookup independently covers `not_registered` and permanent `registered`. |
| Q04 | Declaration query independently covers all five conclusions and every agreement finding. |
| Q05 | Entity collection uses exact permanent subject and includes not-declared, declared, conflicted, and inactive registrations. |
| Q06 | Assertion lookup accepts only valid TRG/TRD/TRW IDs and separates activity from containing health. |
| Q07 | Roots, lineages, tips, withdrawals, groups, entries, endpoints, and findings use exact deterministic order. |
| RC2a | For every reachable state-conclusion × pin-activity cell in Section 9.6, endpoint state conclusion equals public `state_declaration()` and activity equals public `state_assertion()` on identical material. |
| RC2b | Every structurally unreachable Section 9.6 cell has an executable full-set-rejection proof; no parallel transition-specific ST derivation exists. |
| Q10 | Conflict/inactivity alignment precedence preserves exact activity in the separate field. |
| Q11 | A forged alignment/activity precedence swap rejects under outer revalidation. |
| Q12 | A superseded or withdrawn pin never retargets and never changes TRD lifecycle conclusion by itself. |
| Q13 | Registration lookup remains `registered` when all declaration roots are inactive. |

### 20.6 Authoritative reconstruction and architecture

| ID | Acceptance criterion |
|---|---|
| H01 | Every outer result carries complete `ModelQueryMaterial` exactly once; nested rows use strict indices only. |
| H02 | Missing, duplicate, extra, reordered, mixed-revision, stale-ID, and wrong-arm material reject. |
| H03 | Forged endpoint roles, pins, contexts, roots, tips, bodies, findings, conclusions, activities, and alignments reject. |
| H04 | Bool, float, string, negative, out-of-range, and wrong-record indices reject. |
| H05 | Hidden extras, cyclic containers, and excessive depth reject deterministically. |
| H06 | Plain serialized round-trip reconstructs and rederives exactly. |
| H07 | Validation accesses no store, filesystem, network, environment, clock, cache, or write capability. |
| H08 | AST/import checks enforce System Identity → model kernel direction and same-layer ST derivation reuse only. |

### 20.7 Temporal non-inference

| ID | Acceptance criterion |
|---|---|
| T01 | Model transition queries accept no cutoff, source selector, observation, or classification. |
| T02 | No transition assessment/occurrence public symbol, record, package, store, or result exists. |
| T03 | No pair of ST classifications, regardless of cutoffs or outcomes, produces a transition result. |
| T04 | `change_class`, previous occurrence, receipt/source order, and proximity create no transition. |
| T05 | Multiple matching states do not conflict, rank, or select endpoints. |
| T06 | Recorded-at time never selects a declaration, endpoint, or winner. |
| T07 | No cohort, persistence, continuity, causality, control, safety, health, or recommendation is asserted. |

### 20.8 Authoritative absence, replay, and preservation

| ID | Acceptance criterion |
|---|---|
| RC5a | On the untouched 34-record ledger, `transition(trn_00000000000000000000000000000000)` returns exact `not_registered` structured absence. |
| RC5b | On that ledger, `transition_declaration()` for the same anchor and exact `lifecycle_view/as_operated` context returns `not_registered`, `not_applicable`, and empty lifecycle/group/current rows. |
| RC5c | On that ledger, `transitions_of_entity(ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50, context=lifecycle_view/as_operated)` returns `registered`, entity index 14, and empty entries. |
| RC5d | On that ledger, `transition_assertion()` returns exact `not_found` structured absence for valid all-zero `trg_`, `trd_`, and `trw_` IDs. |
| P05 | Explicit 9/10/11/14/16/18/28/29/32/34 memberships retain exact revisions and structured transition absence. |
| P06 | Existing 34 predecessor bytes, aggregate, and accepted PT/VP/BH/ST artifacts remain unchanged. |
| P07 | Reversed input/copy order and hash seed do not change indexes, results, canonical bytes, or revisions. |
| P08 | Working, base-only, and all-extras columns reproduce authorized outputs exactly. |
| P09 | Complete suite, focused suites, compilation, whitespace, topology, and status checks pass at each implementation gate. |
| P10 | No push, merge, unauthorized history operation, or authoritative append occurs. |

## 21. Exact authoritative 34-record absence behavior

### 21.1 Fixed material

All four query families execute against the complete untouched material:

```text
record_count = 34
revision_id = mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41
transition records = 0
```

The valid-shaped absent sentinel IDs are not allocated identities or model
records:

```text
trn_00000000000000000000000000000000
trg_0000000000000000000000000000000000000000000000000000000000000000
trd_0000000000000000000000000000000000000000000000000000000000000000
trw_0000000000000000000000000000000000000000000000000000000000000000
```

### 21.2 `transition()` exact result

Excluding the shared material field:

```text
transition_anchor_id = trn_00000000000000000000000000000000
status = not_registered
registration_index = None
subject_entity_registration_index = None
from_state_registration_index = None
to_state_registration_index = None
```

### 21.3 `transition_declaration()` exact result

For exact context
`LifecycleViewContext(kind="lifecycle_view", view="as_operated")`, excluding
material:

```text
transition_anchor_id = trn_00000000000000000000000000000000
context = lifecycle_view / as_operated
conclusion = not_registered
lineage_summary = not_applicable
agreement_findings = ()
registration_index = None
roots = ()
effective_body_groups = ()
current_declaration_indices = ()
```

### 21.4 `transitions_of_entity()` exact result

For `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50` and the same context, excluding
material:

```text
entity_anchor_id = ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50
context = lifecycle_view / as_operated
status = registered
entity_registration_index = 14
entries = ()
```

Index 14 is pinned against the exact sorted 34-record membership. The result
must not assume at least one transition entry.

### 21.5 `transition_assertion()` exact results

For each valid all-zero `trg_`, `trd_`, and `trw_` sentinel, excluding
material:

```text
record_id = exact requested sentinel
lookup_status = not_found
record_index = None
activity = None
containing_lineage_health = None
containing_subject_conclusion = None
containing_agreement_findings = None
root_record_index = None
successor_indices = ()
withdrawal_indices = ()
```

These are three calls to the fourth query family. They neither allocate nor
persist the sentinel IDs.

## 22. Disposable positive fixtures and optional demo prerequisite

### 22.1 Default test policy

Transition-positive contract coverage uses disposable synthetic models with
two legitimate same-subject states constructed through public builders and
public `ModelStore`. It covers TRG/TRD/TRW, stale pin admission, context
equality, forks, same-root merge, independent roots, conflict, withdrawal,
alignment precedence, all queries, reconstruction, and replay.

No candidate identity is minted or frozen by this design document.

### 22.2 Why the authoritative ledger stays at 34

The accepted model has one StateAnchor/SRG/STD. V1 rejects self-transitions.
An honest transition-positive append therefore requires a legitimate second
state that does not exist. ST-002 must not:

- infer a second state from a complement, name, observation, or match;
- reuse one STD under another state ID;
- create an engineering-indistinguishable state merely for display;
- weaken same-subject, self-transition, or exact-pin rules; or
- append an occurrence because observations differ.

### 22.3 Slice D prerequisite, not authorization

Slice D is nonexistent unless a separate proposal and owner decision first
accept a legitimate second same-subject StateAnchor, SRG, and exact-context
STD. Only after that prerequisite may an owner separately authorize
transition candidate identity allocation, pre-append rehearsal, an exact
candidate contract, and an authoritative append.

This specification authorizes none of those steps.

### 22.4 Future fixture disclaimer

Any later separately authorized transition fixture must state:

> This is an illustrative synthetic ST-002 transition declaration fixture. A
> `declared` result means only that the selected model revision contains an
> admitted declaration connecting the exact pinned from-state and to-state
> declarations in the stated context. It does not claim that a real system is
> in either state, that either state is exclusive or complete, that the
> transition is enabled, executable, occurring, observed, or completed, or
> that temporal order establishes cause, control, safety, health, diagnosis,
> correctness, or recommended action.

It must also say that names, ownership, hierarchy, CAD, ports, VPA,
PIF/PCN/PCM, BH declarations, semantic compatibility, CN satisfaction, ST
matches, temporal correlation, and observation changes did not create the
transition. Displaying endpoint observations beside a transition does not
persist an occurrence.

## 23. Owner-gated implementation slices

Acceptance of this design authorizes no slice automatically. Each slice begins
only after separate owner authorization and stops for separate owner
acceptance.

### 23.1 Slice A — identity, records, store, lifecycle, and replay

Slice A includes only:

- `TransitionAnchor`, `trn_`, and `mint_transition_anchor()`;
- TRG/TRD/TRW frozen contracts, builders, unions, exports, and exact evidence
  grammar extension;
- canonical prefixes and transition effective-body bytes;
- full-set subject, endpoint, tuple, evidence, pin, context, DAG, merge, and
  withdrawal validation;
- deterministic immutable indexes;
- append idempotency/integrity cases;
- lifecycle and explicit historical replay tests; and
- Slice A portions of the corrected acceptance matrix.

Slice A adds no public transition query, endpoint alignment result, positive
authoritative fixture, candidate identity, assessment, or occurrence.

### 23.2 Slice B — four authoritative read-only queries

Slice B includes only:

- the four methods in Section 12;
- exact result fields, literals, exports, ordering, and carry-once material;
- transition lifecycle query derivation;
- endpoint conclusion/activity reuse from the accepted shared ST derivation;
- complete parity and structural-unreachability matrix;
- hostile outer-result reconstruction;
- authoritative 34-record exact absence query tests; and
- Slice B portions of the corrected acceptance matrix.

Slice B adds no assessment, occurrence, state-classification composition,
source selector, cutoff, or ledger append.

### 23.3 Slice C — integrated hardening and reproduction

Slice C includes only:

- remaining adversarial tests from Section 20;
- disposable two-state positive worlds;
- stale pin, merge, conflict, evidence-arm, context, and forgery integration;
- reversed-order and deterministic reproduction;
- exact historical replay and predecessor/artifact preservation;
- working, base-only, and all-extras verification;
- complete focused and repository suites, compilation, whitespace, topology,
  and status checks; and
- a file-first completion report.

Slice C leaves the authoritative ledger exactly 34 records at the accepted
revision with zero transition records. It adds no authoritative fixture,
candidate identity, assessment, or occurrence.

### 23.4 Slice D — nonexistent without a new gate

Slice D is not an authorized or scheduled ST-002 slice. It may exist only
after the prerequisite and separate owner gates in Section 22.3. No work in
Slices A–C may anticipate a particular Slice D identity, record, revision, or
artifact.

## 24. Explicit exclusions, limitations, and future compatibility

### 24.1 Explicit exclusions

ST-002 v1 contains no:

- transition assessment, occurrence, detector, event history, or persisted
  computed result;
- state or transition family, state space, exclusivity, completeness, winner,
  priority, or aggregate selection;
- self-transition, cross-entity transition, or indistinguishable parallel
  transition registration;
- trigger, event, guard, action, effect, mechanism, dwell, debounce,
  hysteresis, persistence, continuity, interpolation, resampling, or freshness
  policy;
- executable state machine, next-state selection, graph traversal,
  reachability, path finding, command, or control;
- safety, health, fault, diagnosis, correctness, probability, confidence,
  recommendation, or causal conclusion;
- hidden field on any ST-001, CN, BH, temporal, binding, interpretation, port,
  relationship, or evidence record; or
- transition-specific store, ledger, revision, cache, database, projection,
  or artifact store.

### 24.2 Known limitations

- A current TRD may intentionally pin a superseded or withdrawn STD. The
  result discloses transition lifecycle, state conclusion, exact pin activity,
  and alignment separately.
- The model can declare a directed relation but cannot say whether it is
  enabled or physically possible now.
- V1 cannot distinguish multiple mechanisms sharing one endpoint pair.
- Same-subject-only scope defers workflows or transfers between entities.
- Self-transition rejection defers eventful re-entry semantics.
- No adjacency or path query is available; entity collection is the only
  bounded transition collection.
- The authoritative model has no transition-positive fixture.

### 24.3 Compatibility guarantees

No ST-001 record gains a transition field. Existing `sta_`, `srg_`, `std_`,
`stw_`, classification contracts, canonical bytes, query results, and
historical revisions retain their accepted meaning.

Future state families, context mappings, cross-entity transitions,
self-transitions, or mechanism discriminators require additive owner-gated
contracts. They may admit new identities and memberships but must not:

- reinterpret an existing `trn_` identity;
- mutate an existing TRG/TRD/TRW schema or canonical byte meaning;
- turn independent declaration roots into distinct transition mechanisms;
- turn occurrence instances into transition registrations; or
- change historical membership replay.

A future occurrence plane must reference, not replace or reinterpret, exact
transition identity and declaration material.

## 25. Final design status and owner approval gate

This corrected synthesis resolves every architecture decision required before
implementation planning:

- ST-002 is declaration-only;
- transition identity is opaque, directed, same-subject, and non-self;
- one ordered endpoint tuple has at most one permanent identity per selected
  membership;
- exact endpoint STD pins prevent silent meaning drift;
- stale pins admit and disclose without retargeting;
- lifecycle supports correction, same-root merge, independent claims,
  corroboration, conflict, withdrawal, and replay;
- endpoint alignment stays orthogonal to transition lifecycle and reuses the
  accepted ST derivation;
- evidence closure and citable prefixes are exact;
- canonical identity and the existing `mrv_` remain authoritative;
- four carry-once read-only queries have complete decision tables;
- the untouched authoritative 34-record absence behavior is pinned;
- transition assessment and occurrence remain deferred; and
- Slices A, B, and C are bounded, while Slice D is only a future prerequisite
  path and is not authorized.

All five challenger corrections RC1–RC5 are normative executable acceptance
rows. The unresolved implementation-blocking owner-question count is zero.

Final owner design approval of this specification would approve the
architecture only. It would not authorize Slice A or any implementation,
identity allocation, fixture, record, ledger append, artifact, commit, push,
merge, or history operation.

END OF ST-002 CORRECTED FINAL SYNTHESIS
