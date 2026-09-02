# FL-001 — Explicit Flow Identity and Evidence-Gated Flow Declaration

**Status:** Codex lead architecture proposal; owner decision required

**Date:** 2026-09-02

**Repository baseline:** `main = origin/main = 1d53d8adb22aada01bf808adb7dc7454a688543d`

**Accepted model baseline:** 34 records at `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`

**Milestone boundary:** design only; no implementation, identity allocation, fixture, ledger append, or history operation

This proposal uses **MUST**, **MUST NOT**, **SHOULD**, and **MAY** in their
ordinary normative senses. It is deliberately more precise than an
implementation plan: owner approval of this document would approve a design
boundary, not any code or model mutation.

## 1. Repository and architecture findings

### 1.1 Verified source state

The architecture reading began from a clean working tree. `HEAD`, local
`main`, and `origin/main` resolve to
`1d53d8adb22aada01bf808adb7dc7454a688543d`. The authoritative demo model
loads as exactly 34 records at
`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`.
It contains zero `trg_`, zero `trd_`, and zero `trw_` records. ST-002 is
complete and owner accepted.

The sources reconciled for this proposal include:

- the accepted PT-001 port and connectivity specification and ADR-0013;
- the accepted VP-001, BH-001, ST-001, and ST-002 designs and their public
  contracts where they constrain flow terminology;
- ADR-0007, ADR-0015, and ADR-0016;
- `backend.system_identity` anchor and minter contracts;
- the public model-kernel record, canonicalization, store, query, port-result,
  state-result, and transition-result contracts;
- the authoritative 34-record demo membership and its accepted preservation
  reports; and
- specialist reviews of repository architecture, model contracts, PT
  topology, temporal evidence, testing, and adversarial boundaries.

No source supports treating connectivity, interface direction, observation,
state, or transition as flow.

### 1.2 Binding lower-layer facts

The following are binding architecture facts rather than conveniences:

1. A `PortAnchor` is opaque. Port ownership is permanently registered by a
   `prg_` record.
2. A `pcn_` record is a positive, exact-context assertion that its unordered
   set of 2–64 distinct ports participates in one common interface
   connection.
3. A PCN is not a stable connection identity. Its roots are evidence
   lineages, not physical cables, channels, conduits, routes, or buses.
4. A PCN hyperedge never expands into pairwise adjacency. Exact lookup and
   containing-set lookup remain different operations.
5. A `pif_` direction declaration says only `input`, `output`,
   `bidirectional`, or `non_directional` for one port, exact context, and
   dimension. It does not say anything flowed.
6. PIF domain and interface-type tokens are qualified nominal tokens with no
   ontology, equivalence, compatibility, or conversion inference.
7. PCM declares compatibility or incompatibility for one unordered pair. It
   does not declare topology, flow, transfer, activity, or occurrence.
8. VPA declares only a same-owner variable-to-port association. It does not
   attach an observation to a port or prove origin, destination, transport,
   or traversal.
9. BH declarations and numeric consistency do not establish influence,
   transfer, execution, or causality.
10. ST classification and ST-002 transition declaration do not establish a
    flow, change event, or occurrence.
11. Model record IDs are content-derived from normative canonical bytes;
    canonical UTC uses `+00:00`, not JSON-mode `Z`.
12. Model revision identity is already expressed by the existing `mrv_`
    algorithm over exact sorted membership.
13. Accepted lifecycle families establish a reusable pattern: permanent
    opaque registration, correctable exact-context declarations, current-tip
    withdrawal, membership-relative replay, and read-only disclosure.
14. Public complex results carry one complete `ModelQueryMaterial`; nested
    rows refer to authoritative records only by strict indices.

### 1.3 Repository conclusion

The existing model ledger is the correct owner for flow identity and
declaration records. FL-001 needs no second ledger, `flv_` revision, flow
database, cache, projection, or persisted query result. The current `mrv_`
contract remains sufficient because the proposed records are model knowledge,
not observations or computed runtime facts.

The model kernel may add flow records and read-only flow disclosures while
remaining dependent only on `backend.system_identity`, Pydantic, and the
standard library. It must not import source, temporal, binding,
interpretation, evaluation, state-classification, or future flow-assessment
packages.

## 2. Revised project objective and capability boundary

### 2.1 Objective

FL-001 should provide the smallest explicit vocabulary that can:

1. mint one opaque flow identity;
2. permanently register the exact directed port-role locus and exact nominal
   flow kind that identity denotes;
3. declare, under one exact assertion context, an evidence-backed capability
   or pathway for that flow;
4. pin the exact topology and direction-role assertions on which that
   declaration relies;
5. correct, corroborate, conflict, withdraw, and replay declarations without
   silently retargeting their evidence; and
6. disclose the registered identity, declaration lifecycle, lower-layer pin
   alignment, port participation, and individual model assertions through
   read-only public queries.

### 2.2 Normative short form

> An admitted FLD means only that an authority explicitly declared one
> kind-qualified, directed port-group flow capability or pathway under an
> exact context, citing one exact matching PCN and one exact direction-role
> PIF for every participant. It does not mean that anything was commanded,
> observed, calculated, transferred, conserved, caused, active, or safe.

`declared` is a model-lifecycle conclusion. It must never be rendered as
`flowing`, `active`, `enabled`, `open`, `running`, `occurred`, `measured`,
`balanced`, `causal`, `correct`, `healthy`, or `recommended`.

### 2.3 Eight concepts that remain separate

| Concept | FL-001 treatment |
|---|---|
| Positive connection assertion | Existing PCN only; unordered common membership, not flow |
| Declared flow capability/pathway | New FRG plus exact-context FLD |
| Commanded flow | Deferred; no command field, record, or query |
| Observed flow | Deferred; no observation composition or current-flow result |
| Calculated or inferred flow | Deferred; no evaluator or solver |
| Particular flow occurrence | Deferred to a separate occurrence plane |
| Causal influence | Deferred; never inferred from flow declaration or timing |
| Conservation or balance result | Deferred; requires a later explicit balance contract |

An FLD is not an occurrence. A PCN plus complementary PIF roles is not an
FLD. An observation associated with a variable that is associated with a port
is not an observed flow. Two different values or classifications at two times
are not evidence that a flow occurred between them.

### 2.4 Included and excluded capability

Included in v1:

- opaque identity;
- permanent directed hyperedge and flow-kind continuity;
- explicit exact-context declaration;
- exact PCN and PIF support pins;
- evidence closure and claim-bearing authority;
- correction DAG, independent roots, merge, conflict, withdrawal, replay;
- orthogonal support-pin alignment; and
- four read-only, carry-once public queries.

Excluded from v1:

- flow activity, magnitude, amount, rate, sign, unit, duration, accumulation,
  latency, persistence, continuity, loss, efficiency, capacity, or quality;
- commands, setpoints, desired flow, control, actions, effects, guards, or
  triggers;
- observation selection, source selection, cutoff, temporal composition, or
  classification comparison;
- occurrence identity, occurrence detection, flow history, and event
  generation;
- path finding, traversal, upstream/downstream closure, routing, addressing,
  arbitration, graph reachability, or automatic next selection;
- causal, diagnostic, safety, health, correctness, or recommendation claims;
  and
- conservation, balance, simulation, estimation, or inference.

No package named `backend.flow_assessment` is part of FL-001 v1.

## 3. Alternatives and the ConnectionAnchor prerequisite question

### 3.1 Alternative A — FlowAnchor owns the logical directed locus

Under this alternative, a `FlowAnchor` names one kind-qualified logical flow
whose permanent registration freezes:

```text
(canonical source port set, canonical sink port set, exact FlowKindToken)
```

The PCN and PIF records are exact, correctable declaration support pins; they
do not own continuity. A supporting PCN or PIF correction therefore cannot
change what the FlowAnchor means. The prior FLD keeps its old exact pins and
discloses them as superseded, withdrawn, conflicted, or inactive. An authority
may create a correcting FLD with new exact pins. Neither action retargets the
old declaration.

This is the recommended v1 architecture.

### 3.2 Alternative B — introduce ConnectionAnchor first

A `ConnectionAnchor` would be justified if FL-001 promised any of the
following:

- identity of a particular cable, pipe, channel, conduit, link, or bus;
- continuity of that connection while endpoint membership changes;
- distinction between parallel physical or logical connections with the
  same endpoint set and context;
- connection-owned variables, behavior, state, metadata, maintenance,
  observations, or occurrences;
- flow *along this particular connection instance*; or
- route, segment, or traversal identity.

PT-001 deliberately supplies none of those semantics. Promoting a PCN root to
a ConnectionAnchor would be unsound: independent roots can corroborate one
topology subject, roots are context-bound content identities, and correction
lineages are evidence histories rather than enduring physical objects.

Adding ConnectionAnchor now would therefore create a second lifecycle and
query surface without satisfying a demonstrated v1 requirement. It would
also invite the false claim that the existing PCN fixture identifies a
particular real connection.

### 3.3 Alternative C — derive flow identity from PCN or PIF content

Rejected. Content-derived PCN/PIF IDs change across corrections; neither is a
flow claim; PCN is unordered; PIF is per-port; and neither records a durable
directed transfer locus. A composite hash would silently redefine identity
when support evidence changed.

### 3.4 Alternative D — defer all flow identity

Safe but unnecessarily restrictive. The existing `PortAnchor` identities,
explicit PCN/PIF claims, exact model revision, and accepted registration /
declaration lifecycle are sufficient for a declaration-only flow layer.
What is not supportable is evaluation or occurrence, not identity.

### 3.5 Lead recommendation

Adopt Alternative A. State the limitation prominently:

> A v1 FlowAnchor identifies one logical, kind-qualified directed port-group
> relation. It does not identify any particular physical connection, path,
> channel, carrier instance, or occurrence.

A future ConnectionAnchor may be added through a separately owner-gated
contract. It must not reinterpret existing `flo_` identities, PCN roots, or
historical revisions.

## 4. Exact identity and continuity policy

### 4.1 Opaque anchor

Propose:

```python
FLOW_ANCHOR_ID_PATTERN = r"^flo_[0-9a-f]{32}$"

class FlowAnchor(...):
    anchor_id: str
    namespace: str
    display_name: str
    role_name: str | None = None
```

It reuses the accepted name grammar, is frozen and extra-forbidden, and sets
`revalidate_instances="always"`. It contains no ports, kind, owner, context,
evidence, declaration, topology, interface, variable, activity, magnitude,
time, command, occurrence, cause, or result.

Add exactly one public keyword-only minter:

```python
def mint_flow_anchor(
    *,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> FlowAnchor:
    ...
```

It calls standard-library `uuid4()` exactly once, uses `.hex`, prefixes
`flo_`, and constructs the validated anchor. It performs no storage, lookup,
I/O, timestamp capture, environment access, deterministic seeding, authority
claim, or name-derived identity.

### 4.2 Permanent identity signature

One FRG permanently fixes:

```text
(source_port_anchor_ids, sink_port_anchor_ids, FlowKindToken)
```

The source tuple and sink tuple are each nonempty, duplicate-free, and
lexicographically sorted. Their sets are disjoint. Their combined union has
between 2 and 64 ports. Tuple order *within* a role is not semantic; the
ordered distinction between source and sink roles is semantic.

Changing any participant, moving any port between roles, reversing all roles,
or changing any FlowKindToken field requires a new FlowAnchor and FRG.
Changing names, note, authority, evidence, or support pins does not change the
flow identity.

### 4.3 Semantic-tuple uniqueness and genuinely distinct flows

Within one selected membership, permit at most one FRG for each exact
`(source tuple, sink tuple, FlowKindToken)` signature. A second anchor with the
same signature rejects typed. The reverse signature is different and may
coexist.

This deliberately means:

- independent FLD roots are multiple evidence claims about one flow, not new
  flows;
- different qualified flow kinds over the same ports may use different flow
  identities;
- genuinely distinct same-kind mechanisms sharing exactly the same role sets
  are not representable as distinct v1 flow identities; and
- such mechanisms require a separately owner-gated additive identity
  discriminator or a ConnectionAnchor contract.

Future relaxation must not reinterpret existing `flo_` identities or
historical revisions.

### 4.4 Ownership and system scope

FlowRegistration has no single subject entity or owner. Every port's owner is
already fixed by its PRG. One flow may explicitly span ports owned by one or
several entities. Cross-entity participation is admitted by exact port
identity and claim evidence, never inferred from hierarchy or relationships.

There is no separate system-scope field in v1. The exact port set already
bounds the locus. A separate system, plant, network, or subsystem field would
either duplicate port ownership/hierarchy or introduce an unvalidated scope
ontology.

### 4.5 Continuity non-inference

Names, matching source paths, shared entity ownership, hierarchy, CAD,
geometry, proximity, equal qualified tokens, PCN correction, PIF correction,
PCM, VPA, BH, ST, transition records, observations, timestamps, and value
changes never establish flow identity continuity.

Replacement of a physical port requires a new PortAnchor and therefore a new
FlowAnchor. The v1 flow identity cannot survive endpoint replacement by
claiming that the cable or conceptual route stayed the same.

## 5. Proposed anchors, records, prefixes, builders, and canonicalization

### 5.1 Record family and prefixes

| Prefix | Contract | Meaning | Citable as model evidence |
|---|---|---|---|
| `flo_` | `FlowAnchor` | Opaque identity only | n/a |
| `frg_` | `FlowRegistration` | Permanent identity signature | yes |
| `fld_` | `FlowDeclaration` | Correctable exact-context declared pathway/capability | yes |
| `flw_` | `FlowDeclarationWithdrawal` | Retraction of one current FLD tip | no |

`flo_` avoids collision with the conventional `flw_` withdrawal prefix.
`frg_` follows the repository's `*rg_` registration convention. Add the
three record prefixes to the record-ID and filename grammars,
discriminator-to-prefix map, discriminated adapter, `ModelRecord` union,
store partitions, and public model-kernel exports. Add only `frg_` and `fld_`
to `ModelRecordEvidence`.

### 5.2 Qualified flow-kind token

```text
FlowKindToken
  token_kind: Literal["flow_kind"]
  system_id: LocalIdentifier
  system_edition: LocalIdentifier
  code: LocalIdentifier
```

All four fields participate in equality, canonical bytes, tuple uniqueness,
and record identity. Comparison is exact. The kernel performs no ontology
lookup, hierarchy, aliasing, synonym expansion, compatibility, unit
conversion, commodity inference, or carrier inference.

Flow kind is mandatory because two directed claims over the same ports may
refer to fundamentally different nominal transfer kinds, and PIF domain/type
equality cannot supply that meaning. It is not a physical property assertion.
The claim-bearing authority remains responsible for its chosen vocabulary.

Commodity, carrier, phase, protocol, signal type, material species, energy
form, and payload are not separate v1 identity dimensions. If a later
requirement needs one to be independently queried or corrected, it requires
an additive owner-gated contract. Changing the v1 FlowKindToken itself always
requires a new FlowAnchor.

### 5.3 FlowRegistration

```text
FlowRegistration
  record_kind: Literal["flow_registration"]
  schema_version: Literal["1"]
  record_id: frg_[0-9a-f]{64}
  anchor: FlowAnchor
  source_port_anchor_ids: CanonicalNonEmptyFlowPortTuple
  sink_port_anchor_ids: CanonicalNonEmptyFlowPortTuple
  flow_kind: FlowKindToken
  evidence: NonEmptyCanonicalEvidenceTuple
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

FRG has no context, parents, PCN/PIF/PCM/VPA pin, connection identity,
variable, magnitude, unit, occurrence, activity, command, behavior, state,
transition, cause, safety, or result field.

### 5.4 Direction support pin

```text
FlowDirectionDeclarationPin
  port_anchor_id: prt_[0-9a-f]{32}
  declaration_record_id: pif_[0-9a-f]{64}
```

It is frozen, extra-forbidden, and always revalidates nested instances. Role
comes from the containing `source_direction_pins` or `sink_direction_pins`
field; there is no caller-controlled duplicate role string. Each tuple is
unique and sorted by `port_anchor_id`.

### 5.5 FlowDeclaration

```text
FlowDeclaration
  record_kind: Literal["flow_declaration"]
  schema_version: Literal["1"]
  record_id: fld_[0-9a-f]{64}
  flow_anchor_id: flo_[0-9a-f]{32}
  context: AssertionContext
  connection_assertion_record_id: pcn_[0-9a-f]{64}
  source_direction_pins: CanonicalFlowDirectionPinTuple
  sink_direction_pins: CanonicalFlowDirectionPinTuple
  evidence: NonEmptyCanonicalEvidenceTuple
  supersedes: CanonicalFlowDeclarationIdTuple = ()
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

The source pin ports must equal the FRG source tuple exactly; the sink pin
ports must equal the FRG sink tuple exactly. There is exactly one pin per
participant. FLD has no evaluation basis, latest-pointer instruction,
enabled/activity flag, rate, amount, unit, trigger, event, guard, action,
effect, occurrence, observation, source selector, cutoff, confidence,
probability, priority, validity, diagnosis, or recommendation.

### 5.6 FlowDeclarationWithdrawal

```text
FlowDeclarationWithdrawal
  record_kind: Literal["flow_declaration_withdrawal"]
  schema_version: Literal["1"]
  record_id: flw_[0-9a-f]{64}
  withdraws: fld_[0-9a-f]{64}
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

FLW has no evidence, context, anchor copy, replacement, outcome, reason code,
negative-flow assertion, or stopped-flow meaning.

### 5.7 Builders

FL-001 adds no flow-specific record builder. The accepted public
`backend.model_kernel.build_record(record_cls, **fields)` constructs FRG,
FLD, and FLW and computes their IDs. `mint_flow_anchor()` is the only new
identity builder. Public implementation and tests must not hand-assemble a
record ID, derive an anchor from names, or bypass these APIs.

### 5.8 Normative canonicalization

Flow records use only `backend.model_kernel.canonical`:

1. revalidate the complete record from field data;
2. dump in Python mode excluding `record_id`;
3. recursively normalize datetimes to UTC `.isoformat()` with `+00:00`;
4. preserve source versus sink field roles;
5. preserve already-canonical tuple order;
6. JSON-encode with sorted keys, compact separators, UTF-8, and
   `ensure_ascii=False`; and
7. SHA-256 the exact bytes and prepend the record-kind prefix.

Every record suffix equals `sha256(canonical_bytes(record))`.
`compute_record_id(record)` must equal the stored ID and
`verify_record_id(record)` must be true. JSON-mode `Z` output must never be
labeled canonical. Existing record bytes and golden vectors remain unchanged.

Canonical input rules are:

- source ports: unique, sorted lexicographically;
- sink ports: unique, sorted lexicographically;
- source/sink roles: never exchanged or jointly sorted;
- direction pins: unique and sorted by `port_anchor_id` within their role;
- evidence: existing full canonical evidence key;
- parents: unique lexicographic record-ID order; and
- effective-body groups: canonical private body bytes.

## 6. Evidence requirements and exact reference closure

### 6.1 Uniform closure

For every evidence-bearing FRG or FLD, the store first applies the existing
uniform model-record evidence closure rule. Every `ModelRecordEvidence`
reference must identify a present, correctly typed record in the exact
selected membership. A malformed, wrong-kind, dangling, or replay-omitted
reference rejects.

Role-specific mandatory citations are additional to uniform closure. Extra
admitted evidence is permitted, but every extra model-record citation remains
reference-closed and none can replace the mandatory structural pins or
claim-bearing owner declaration.

### 6.2 FRG evidence checklist

Every FRG requires:

1. a direct `ModelRecordEvidence` citation to every exact participant PRG;
2. at least one claim-specific `OwnerDeclarationEvidence` stating that this
   opaque identity denotes the exact role partition and exact FlowKindToken;
3. nonempty canonical evidence; and
4. closure for every additional model-record citation.

The FRG does not cite a PCN or PIF as a mandatory registration dependency.
Its purpose is to preserve identity even when contextual support is absent,
corrected, conflicted, or withdrawn. A registration alone is not a declared
flow capability.

### 6.3 FLD evidence checklist

Every FLD requires:

1. a direct citation to the exact FRG;
2. a direct citation to every exact participant PRG;
3. a direct citation to the exact pinned PCN;
4. a direct citation to every exact pinned direction-role PIF;
5. at least one claim-specific `OwnerDeclarationEvidence` explicitly
   declaring the exact flow capability/pathway under the exact context and
   support-pin set;
6. declaration-parent closure; and
7. closure for every additional model-record citation.

The direct PRG citations are intentionally redundant with FRG closure. They
make the complete participant basis locally auditable and prevent a future
change to transitive evidence treatment from weakening the declaration gate.

### 6.4 Evidence meaning and authenticity limit

The owner-declaration arm is what makes the positive flow claim explicit.
PCN and PIF pins establish exact lower-layer support and alignment, not flow.
PCM, VPA, BH, state, transition, temporal occurrence, source raw record, and
structural evidence arms may be additional evidence only when honestly
relevant; their presence has no implicit flow semantics.

Model-kernel validation proves internal reference closure and canonical
coherence. It does not authenticate external raw bytes, prove physical
transfer, or convert a citation into observation or occurrence evidence.

### 6.5 Evidence grammar compatibility

Extend the `ModelRecordEvidence.record_id` alternatives by `frg` and `fld`
only. `flw_` remains uncitable because a withdrawal is not a positive claim.
Every existing evidence arm, discriminator, ordering rule, and accepted
record ID remains byte-for-byte unchanged.

### 6.6 Relationship to existing model families

| Existing concept | Exact relationship to FL-001 |
|---|---|
| FlowAnchor | Owns opaque continuity only; FRG supplies permanent role/kind meaning |
| PRG / PortAnchor | Supplies each exact participant identity and owner; never creates flow |
| PCN | Mandatory exact-union contextual support pin in FLD; common membership only |
| PIF direction | Mandatory exact per-participant support pin; role comparison only |
| PIF domain/type | Not a flow-kind source and not a mandatory pin |
| PCM | Optional additional evidence only; compatibility never creates or validates flow |
| VPA | Optional additional evidence only; never attaches an observation to the flow or port |
| Variables / semantics | No v1 flow payload, rate, quantity, unit, or measurement meaning |
| BH | Independent model/evaluation claim; no transfer, influence, or conservation inference |
| State / ST classification | Independent model/evaluation claim; no flow activity inference |
| ST-002 transition | Declared transition possibility only; no flow event or causal link |
| Observations / temporal occurrences | Never composed by model-kernel flow queries |

No existing record receives a hidden FlowAnchor, flow role, flow flag, or
flow-result field.

## 7. Port-role and hyperedge semantics without false pairwise claims

### 7.1 Directed hyperedge meaning

The permanent role signature is one directed hyperedge:

```text
{source ports} -> {sink ports}
```

It means only that the registered flow identity has that explicit group
partition. It never expands into a complete bipartite graph, pairwise
adjacency, per-branch flow, broadcast, duplication, mixing, summation,
allocation, arbitration, conservation, capacity, or occurrence.

If an application needs separately assertable branch semantics, it must use
separate explicit FlowAnchors or a later owner-gated branch contract. Query
code must not manufacture branch records or pairwise conclusions.

### 7.2 Supported shapes

| Shape | v1 treatment | Explicit non-claim |
|---|---|---|
| 1 source, 1 sink | Supported | No transfer or occurrence inferred |
| 1 source, N sinks | One explicit fan-out hyperedge | No broadcast, duplication, or N pairwise flows |
| N sources, 1 sink | One explicit fan-in hyperedge | No mixing, summation, or causal contribution |
| N sources, M sinks | One explicit group-to-group hyperedge | No complete bipartite graph or routing |
| Static bus partition | Supported only when every participant is explicitly assigned one role | No addressing, arbitration, dynamic talker, or reachability |
| Dynamic bus roles | Separate identities for each stable role signature or defer | PIF `bidirectional` does not choose a speaker |
| Reversed direction | Separate FlowAnchor and FRG | No reverse flow inferred |
| Same port in both roles | Rejected | No one-record loop |
| One-port flow | Rejected | PCN already requires distinct endpoints |
| Several flows sharing ports | Allowed when signatures differ | No exclusivity, priority, capacity, or contention inferred |
| Graph cycle across flows | Records may coexist | No traversal, loop, or causal conclusion |

### 7.3 Cross-entity flows

One flow may span several entities. The participant entity set is derived for
disclosure only from the exact PRGs. It does not become a single owner, shared
ownership claim, system boundary, or relationship. A cross-entity flow must
still have explicit FRG and FLD evidence; hierarchy and entity relationships
never create one.

### 7.4 Bidirectionality

A bidirectional engineering relationship requires two explicit flow
identities with reversed source/sink partitions. A PIF value of
`bidirectional` is consistent with either endpoint role but creates neither
FlowAnchor and never causes an implicit reverse declaration.

### 7.5 Loops and role overlap

Source and sink sets are disjoint. FL-001 does not represent a closed route or
circulating loop as one flow. Separate explicitly registered directed legs
may form a graph cycle, but v1 exposes no graph traversal or cycle semantics.

## 8. Qualified flow-kind, commodity, and carrier policy

### 8.1 Why PIF domain/type is insufficient

PIF interface-domain and interface-type tokens classify interfaces, not what
is declared to flow. Equal tokens establish only exact nominal equality;
different tokens do not necessarily establish incompatibility; neither case
declares a commodity, signal, carrier, payload, or transfer.

Inferring a flow kind from PIF equality would make a correction to an
interface claim silently change permanent flow meaning. It would also fail
for a common interface that supports several flow kinds.

### 8.2 Required nominal token

The qualified `FlowKindToken` is therefore permanent identity material. It
can name a project-local or externally governed vocabulary through exact
`system_id`, `system_edition`, and `code`. The kernel compares the serialized
token only and never reasons about it.

### 8.3 Deferred dimensions

V1 does not separately encode commodity, carrier, payload, phase, protocol,
quantity kind, unit, or transport mechanism. A token code may be humanly
chosen to denote a useful nominal kind, but the kernel does not decompose it.

If future measured-flow or conservation work needs independent semantic
dimensions, the later architecture must decide which are identity-defining
and which are correctable declaration content. It must not mine those facts
from names, PIF tokens, VPA, or variables, and it must not reinterpret an
existing FlowKindToken.

## 9. Context, lifecycle, correction, corroboration, conflict, withdrawal, and replay

### 9.1 Exact context equality

The FLD, its pinned PCN, and every pinned PIF must have exactly equal
`AssertionContext` values.

- `LifecycleViewContext(kind="lifecycle_view", view="as_designed")` matches
  only that exact context.
- Every other lifecycle view matches only itself.
- `ViewIndependentContext(kind="view_independent")` matches only the exact
  view-independent arm.
- Context kind, lifecycle view, field content, and union arm are all
  significant.

No conversion, inheritance, default, fallback, union, or cross-context
mapping is available. A disposable positive test must cover a completely
view-independent FLD; mixed view-independent/lifecycle inputs reject.

### 9.2 Lineage key

The declaration lineage key is:

```text
(flow_anchor_id, exact AssertionContext)
```

Different contexts have independent declaration sets and cannot be connected
by parentage. Context is not part of permanent flow identity.

### 9.3 Roots and correction

- `supersedes=()` creates an independent FLD root.
- One parent creates an ordinary correction within that root.
- Two or more parents create a merge only when every parent belongs to the
  same derived root and exact lineage key.
- Parent order is canonical and has no priority.
- Duplicate, self, malformed, missing, cross-flow, cross-context, cyclic, and
  cross-root parentage rejects typed.
- DAG derivation is iterative, membership-bounded, and independent of Python
  recursion depth.

A correction may change PCN/PIF pins, evidence, authority, `recorded_at`, and
note. It may not change the registered flow signature or exact context within
one lineage.

### 9.4 Same-root forks and merges

A root with two or more current tips is `conflicted`, even when all tips have
identical effective bodies. No timestamp, ID, evidence count, authority,
filename, or append order chooses a winner.

A successor that names all current fork tips from that one root may converge
the fork. After a complete merge, the parents are superseded, the successor
is the sole current tip, and root health becomes `healthy`. Partial
convergence that leaves multiple tips remains `conflicted`.

### 9.5 Effective declaration body

The private, non-persisted FLD effective body contains exactly:

```text
flow_anchor_id
exact AssertionContext
connection_assertion_record_id
source_direction_pins
sink_direction_pins
```

It excludes record ID, evidence, authority, `recorded_at`, note, parents,
filename, append order, derived alignment, and current lower-layer values.

Different exact PCN or PIF pins are different effective bodies even when the
pinned records have humanly similar content. This prevents independent roots
from silently claiming corroboration across different support contracts.

### 9.6 Root health and independent roots

| Current tips in one root | Root health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2 or more | `conflicted` |

Across independent roots:

| Active shape | Aggregate behavior |
|---|---|
| One healthy root/body | `declared`; `one_healthy_root` |
| Two or more healthy roots with one exact body | `declared`; `corroborating_healthy_roots` |
| Healthy roots with different effective bodies | `conflicted`; `cross_root_effective_body_disagreement` |
| Any same-root fork | `conflicted`; `same_root_conflict` |
| Inactive roots beside an otherwise declared body | Preserve declared result and add `inactive_roots_present` |
| All roots inactive | `inactive` |

Independent roots remain separate evidence claims. Corroboration never merges
records, roots, or identities.

### 9.7 Withdrawal

FLW targets exactly one current unsuperseded FLD tip. Unknown, wrong-kind,
superseded, non-tip, already-withdrawn, and duplicate targets reject. A
membership containing both a successor and withdrawal of the same tip rejects
regardless of append order.

Selective withdrawal of one fork tip is allowed and recomputes root health.
Withdrawal means only that the targeted positive declaration is no longer
asserted in the selected membership. It does not say flow stopped, the
connection disappeared, a direction reversed, or a negative-flow claim is
true.

FRG remains permanently `registered` when there are no declarations, all
roots are inactive, or declarations conflict.

### 9.8 Historical replay

Every lifecycle, activity, and support-alignment conclusion is relative to
the explicitly selected, reference-closed membership. Replaying a membership
that omits a successor or withdrawal makes an older FLD or support assertion
current again. Replay never ranks by timestamps, filenames, directory order,
record IDs, or append order.

An FLD may replay only when its exact FRG, PCN, PIF, parent, and evidence
dependencies are present. Later lower-layer corrections never mutate the
canonical bytes or admission of an older reference-closed FLD.

## 10. Exact PCN/PIF pinning and flow-alignment disclosure

### 10.1 Exact PCN pin

The pinned PCN itself must:

1. be present and verify as a `PortConnectionAssertion`;
2. have context exactly equal to the FLD context; and
3. have `endpoint_port_anchor_ids` exactly equal to the sorted union of the
   FRG source and sink sets.

A subset, proper superset, overlap-only PCN, or result from
`connections_containing()` cannot satisfy admission. Exact-union equality is
the defense against laundering one larger hyperedge into invented pairwise or
sub-bus topology.

The PCN may already be superseded, withdrawn, or contained in a conflicted or
inactive root when a new FLD is appended. Existence, exact subject, exact
context, evidence closure, and record integrity are admission facts;
currentness is disclosure. No current successor is substituted.

### 10.2 Exact direction-role pins

Every participant has exactly one pinned PIF. Each pinned PIF itself must:

1. be present and verify as a `PortInterfaceDeclaration`;
2. name the exact participant port;
3. have context exactly equal to the FLD context;
4. have dimension exactly `direction_role`; and
5. carry an allowed value for the participant's permanent flow role.

The v1 admission table is:

| Flow role | Pinned PIF value | Admission |
|---|---|---|
| source | `output` | admit |
| source | `bidirectional` | admit |
| source | `input` | reject |
| source | `non_directional` | reject |
| sink | `input` | admit |
| sink | `bidirectional` | admit |
| sink | `output` | reject |
| sink | `non_directional` | reject |

This is a deliberately bounded v1 rule. It does not infer actual flow from
the admitted values. A directed flow kind whose lower-layer interface is
honestly non-directional is outside this contract until the owner relaxes or
replaces mandatory direction pinning.

A structurally valid and role-compatible PIF may already be superseded or
withdrawn when a new FLD is appended. A current replacement never repairs an
invalid exact pin. No domain, interface-type, PCM, or VPA pin is mandatory.

### 10.3 Orthogonality rule

Flow declaration lifecycle and support alignment are independent:

- a healthy current FLD can be `declared` while a support pin is stale,
  conflicted, or inactive;
- an FLD conflict remains `conflicted` even when every support pin is current;
- correction or withdrawal of PCN/PIF support never automatically withdraws
  or corrects an FLD; and
- an FLD correction never mutates or withdraws PT records.

Public wording must never collapse these axes into one `valid` or `active`
boolean.

### 10.4 Shared authoritative PT derivation

Flow results must derive lower-layer facts through the accepted PT
derivations, not a parallel implementation:

- exact assertion activity and containing-root health from the authoritative
  `port_assertion()` derivation;
- exact-subject topology conclusion from `connections_exact()` over the
  registered union and FLD context; and
- current direction-dimension conclusion and current declaration from
  `port_interface()` for each participant/context.

Implementation may refactor private reusable payload helpers within the model
kernel, but public results and decision parity must remain exact. Another
healthy PCN root must not hide that the *pinned* PCN root is conflicted or
inactive.

### 10.5 Connection pin alignment

`FlowConnectionAlignment` is exactly:

```python
Literal[
    "exact_current",
    "pinned_connection_superseded",
    "pinned_connection_withdrawn",
    "connection_lineage_conflicted",
    "connection_lineage_inactive",
]
```

Precedence is containing-root health before individual activity:

| Pinned root health | Pinned activity | Alignment |
|---|---|---|
| `conflicted` | any | `connection_lineage_conflicted` |
| `inactive` | `superseded` or `withdrawn` | `connection_lineage_inactive` |
| `healthy` | `current` | `exact_current` |
| `healthy` | `superseded` | `pinned_connection_superseded` |
| `healthy` | `withdrawn` | `pinned_connection_withdrawn` |

`inactive` plus `current` is structurally unreachable and must be rejected by
outer-result validation if forged.

### 10.6 Direction pin alignment and current-role relation

`FlowDirectionAlignment` is exactly:

```python
Literal[
    "exact_current",
    "pinned_direction_superseded",
    "pinned_direction_withdrawn",
    "direction_lineage_conflicted",
    "direction_lineage_inactive",
]
```

| Direction lineage health | Pinned activity | Alignment |
|---|---|---|
| `conflicted` | any | `direction_lineage_conflicted` |
| `inactive` | `superseded` or `withdrawn` | `direction_lineage_inactive` |
| `healthy` | `current` | `exact_current` |
| `healthy` | `superseded` | `pinned_direction_superseded` |
| `healthy` | `withdrawn` | `pinned_direction_withdrawn` |

`FlowCurrentDirectionRelation` is
`consistent | inconsistent | indeterminate | not_evaluated`:

- source plus current `output`/`bidirectional` is `consistent`;
- source plus current `input` is `inconsistent`;
- sink plus current `input`/`bidirectional` is `consistent`;
- sink plus current `output` is `inconsistent`;
- a current `non_directional` declaration is `indeterminate`; and
- no unique current direction declaration is `not_evaluated`.

This comparison is disclosure only. It does not change FLD lifecycle and does
not say anything flowed.

### 10.7 Aggregate support summary

`FlowSupportAlignmentSummary` is exactly:

```python
Literal["aligned", "stale", "conflicted", "inactive"]
```

It is derived across the PCN and every PIF alignment in this precedence:

1. any lineage-conflicted alignment -> `conflicted`;
2. otherwise any lineage-inactive alignment -> `inactive`;
3. otherwise any superseded/withdrawn alignment -> `stale`;
4. otherwise -> `aligned`.

The individual rows, exact activities, root health, topology conclusion,
direction conclusions, and current-role relations remain visible. The summary
is never a flow validity or activity result.

## 11. Exact read-only query and public result vocabulary

### 11.1 Four-query public surface

FL-001 should add exactly:

```python
flow(flow_anchor_id) -> FlowLookupResult

flow_declaration(
    flow_anchor_id,
    *,
    context,
) -> FlowDeclarationResult

flows_involving_port(
    port_anchor_id,
    *,
    context,
) -> PortFlowsResult

flow_assertion(
    record_id,
) -> FlowAssertionDisclosureResult
```

The queries operate over one injected immutable `LoadedModel`, own no store,
perform no write, and carry one `ModelQueryMaterial`. They accept no name,
entity, variable, source selector, cutoff, observation, rate, current-value,
path, traversal, direction discovery, or automatic context.

There are no aliases or methods named `current_flow`, `observed_flow`,
`commanded_flow`, `assess_flow`, `detect_flow`, `flow_history`,
`flow_occurrence`, `upstream`, `downstream`, `flow_path`, `flow_rate`,
`balance`, or `conservation`.

### 11.2 Exact literals

```python
FlowLookupStatus = Literal[
    "not_registered",
    "registered",
]

FlowDeclarationConclusion = Literal[
    "not_registered",
    "not_declared",
    "declared",
    "conflicted",
    "inactive",
]

FlowDeclarationLineageSummary = Literal[
    "not_applicable",
    "healthy",
    "conflicted",
    "inactive",
]

FlowAgreementFinding = Literal[
    "one_healthy_root",
    "corroborating_healthy_roots",
    "same_root_conflict",
    "cross_root_effective_body_disagreement",
    "inactive_roots_present",
]

FlowPortRole = Literal["source", "sink"]

PortFlowsStatus = Literal[
    "port_not_registered",
    "registered",
]

FlowAssertionLookupStatus = Literal[
    "not_found",
    "found",
]
```

Reuse accepted `AssertionActivity`, `ContainingLineageHealth`, PT topology and
interface-dimension statuses, plus the alignment literals in Section 10.
No result literal implies physical activity, possibility-now, execution,
occurrence, causality, correctness, health, safety, or action.

### 11.3 FlowLookupResult

```text
FlowLookupResult
  material
  flow_anchor_id
  status
  registration_index
  source_port_registration_indices
  sink_port_registration_indices
```

When absent, the registration index is `None` and both port-index tuples are
empty. When registered, every index resolves to the exact FRG/PRG in carried
material. Source and sink tuples preserve role and canonical port order.

### 11.4 Lightweight support and lifecycle rows

```text
FlowConnectionSupportResult
  connection_assertion_index
  exact_topology_conclusion
  pinned_assertion_activity
  pinned_lineage_health
  alignment

FlowDirectionSupportResult
  role
  port_anchor_id
  port_registration_index
  direction_declaration_index
  direction_dimension_status
  pinned_assertion_activity
  pinned_lineage_health
  current_direction_relation
  alignment

FlowEffectiveBodyGroupResult
  group_index
  representative_declaration_index
  current_tip_indices
  root_record_indices
  connection_support
  source_direction_supports
  sink_direction_supports
  support_alignment_summary

FlowDeclarationRootResult
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health
  effective_body_group_indices
```

Rows contain derived scalar labels and strict indices, never duplicated
authoritative records or a second material snapshot. Convenience properties
resolve indices only through private binding to the one outer material.

### 11.5 FlowDeclarationResult

```text
FlowDeclarationResult
  material
  flow_anchor_id
  context
  conclusion
  lineage_summary
  agreement_findings
  registration_index
  roots
  effective_body_groups
  current_declaration_indices
```

Support rows appear only inside active effective-body groups. Historical roots
remain visible when the conclusion is inactive. Absence and not-declared
results have no body groups.

### 11.6 PortFlowsResult

```text
PortFlowEntry
  entry_index
  flow_anchor_id
  flow_registration_index
  role
  conclusion
  lineage_summary
  agreement_findings
  roots
  effective_body_groups
  current_declaration_indices

PortFlowsResult
  material
  port_anchor_id
  context
  status
  port_registration_index
  entries
```

The collection returns every FRG whose permanent source or sink set contains
the exact port, including `not_declared`, `declared`, `conflicted`, and
`inactive` entries for the requested context. Disjoint role sets make each
entry's role unique. It performs no traversal and does not include flows merely
because another participant shares a PCN.

### 11.7 FlowAssertionDisclosureResult

```text
FlowAssertionDisclosureResult
  material
  record_id
  lookup_status
  record_index
  activity
  containing_lineage_health
  containing_flow_conclusion
  containing_agreement_findings
  root_record_index
  successor_indices
  withdrawal_indices
```

Only a found FLD has activity and containing lifecycle fields. Found FRG and
FLW records have those fields null/empty. Conflict is a root or flow-context
conclusion, never an individual assertion activity.

### 11.8 Deterministic public ordering

- material records: exact lexicographic revision membership;
- source/sink registrations and direction rows: registered role tuple order;
- incident flow entries: ascending FlowAnchor ID, then FRG ID defensively;
- roots: ascending root FLD ID;
- lineage, tips, withdrawals, successors: ascending record ID;
- effective-body groups: canonical body bytes;
- current declaration indices: body-group order then record ID;
- findings: fixed vocabulary order shown in Section 12; and
- no timestamp, authority, note, append order, filesystem order, locale, or
  hash iteration affects output.

## 12. Complete decision tables for public conclusions

### 12.1 Registration lookup

| Exact FRG | `FlowLookupStatus` | Indices |
|---|---|---|
| Absent | `not_registered` | Registration `None`; port tuples empty |
| Present and admitted | `registered` | Exact FRG and every exact PRG index |

Declaration absence, conflict, support staleness, or inactivity never changes
a present FRG's lookup status.

### 12.2 Declaration conclusion

| FRG | Exact-context roots | Active shape | Conclusion |
|---|---:|---|---|
| Absent | any | not evaluated | `not_registered` |
| Present | 0 | not applicable | `not_declared` |
| Present | 1+ | no active tips anywhere | `inactive` |
| Present | 1+ | any same-root fork | `conflicted` |
| Present | 2+ healthy | different effective bodies | `conflicted` |
| Present | 1+ healthy | one exact active body group | `declared` |

Support alignment does not participate in this table.

### 12.3 Lineage summary

| Conclusion | Lineage summary |
|---|---|
| `not_registered` | `not_applicable` |
| `not_declared` | `not_applicable` |
| `declared` | `healthy` |
| `conflicted` | `conflicted` |
| `inactive` | `inactive` |

### 12.4 Agreement findings

Findings are independently derived and emitted in this exact order:

| Condition | Finding |
|---|---|
| Exactly one healthy root | `one_healthy_root` |
| At least two healthy roots share one body | `corroborating_healthy_roots` |
| At least one same-root fork | `same_root_conflict` |
| Healthy roots contain more than one body | `cross_root_effective_body_disagreement` |
| At least one inactive root | `inactive_roots_present` |

### 12.5 Root health

| Current tips after withdrawals | Health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2+ | `conflicted` |

### 12.6 Exact-subject topology conclusion

Reuse the accepted PT conclusion exactly for the registered participant union
and exact FLD context:

| Exact-subject PCN roots | Active tips | Conclusion |
|---:|---:|---|
| 0 | 0 | `unknown` |
| 1+ | 1+ anywhere | `asserted` |
| 1+ | 0 everywhere | `inactive` |

An admitted active FLD has at least its pinned PCN record, but another root
may make the exact subject `asserted` while the pinned root is inactive. Both
facts are disclosed.

### 12.7 Direction dimension conclusion

Reuse the accepted PIF direction-dimension derivation for each exact port and
context:

| Port | Direction roots | Current tips | Status |
|---|---:|---:|---|
| Not registered | any | any | `port_not_registered` |
| Registered | 0 | 0 | `not_declared` |
| Registered | 1+ | 1 | `declared` |
| Registered | 1+ | 2+ | `conflicted` |
| Registered | 1+ | 0 | `inactive` |

The first two rows are structurally unreachable for an admitted FLD pin but
must be rejected if forged into a result.

### 12.8 Pin alignment

The complete individual PCN/PIF alignment matrices and unreachable states are
Sections 10.5 and 10.6. Alignment precedence is lineage conflict, lineage
inactivity, then exact activity. A forged activity/alignment precedence swap
rejects.

### 12.9 Aggregate support summary

| Any conflict | Any inactive support | Any stale support | Summary |
|---|---|---|---|
| yes | any | any | `conflicted` |
| no | yes | any | `inactive` |
| no | no | yes | `stale` |
| no | no | no | `aligned` |

### 12.10 Port collection

| Requested port | Status | Entries |
|---|---|---|
| No PRG | `port_not_registered` | Empty |
| Registered | `registered` | Every exact incident FRG, possibly empty |

Each entry reuses the direct flow-declaration derivation for the same flow and
context. Direct and collection payloads must agree field-for-field apart from
their documented outer wrappers and entry index.

### 12.11 Assertion lookup and activity

| Valid-shaped ID | Selected exact record | Lookup |
|---|---|---|
| `frg_`, `fld_`, or `flw_` | absent | `not_found` |
| Exact kind and ID | present | `found` |

Malformed and non-flow IDs fail typed before model index access.

Only a found FLD has activity:

| Direct successors | Withdrawal | Activity |
|---:|---:|---|
| 1+ | any defensively supplied state | `superseded` |
| 0 | 1 | `withdrawn` |
| 0 | 0 | `current` |

Successor precedence matches the accepted defensive kernel rule even though
full-set validation rejects successor-plus-withdrawal.

### 12.12 Containing lineage health

| Current tips in containing root | Health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2+ | `conflicted` |

The containing flow conclusion and findings are exactly those for the found
FLD's flow/context key.

## 13. Carry-once authoritative outer-result reconstruction

### 13.1 Material rule

Every outer flow result carries exactly one complete `ModelQueryMaterial`:

- exact `ModelRevision`;
- every selected record exactly once in lexicographic ID order;
- record IDs exactly equal revision membership; and
- no duplicate snapshot in a nested result.

Every record index is a strict non-boolean integer greater than or equal to
zero and within bounds. Nested rows may carry derived scalar values but may
refer to authoritative model records only by index.

### 13.2 Trust boundary and validation sequence

No supplied result, nested Pydantic instance, private attribute, cached
object, conclusion, alignment, or index is trusted. Each outer result must:

1. inspect the supplied object graph before serialization and reject hidden
   `model_copy`/`model_construct` extras;
2. traverse iteratively with deterministic depth and node bounds, rejecting
   hostile cycles;
3. reconstruct `ModelRevision` and every record from plain serialized fields;
4. enforce strict indices and exact union arms;
5. require unique lexicographically ordered records exactly matching revision
   membership;
6. call authoritative `validate_record_collection()` over the complete set;
7. recompute and compare the model revision;
8. reconstruct the exact assertion context and all nested rows from plain
   content;
9. derive the expected flow payload from the rebuilt `LoadedModel`;
10. derive PCN/PIF facts through the accepted shared PT derivations;
11. compare every supplied field, index, order, lifecycle fact, support fact,
    activity, relation, and alignment exactly;
12. bind private material access only after exact equality succeeds; and
13. perform no store, filesystem, database, network, environment, clock,
    cache, or write access.

### 13.3 Mandatory forgery rejection

Reject:

- missing, duplicate, extra, reordered, or mixed-revision material;
- stale IDs, wrong hashes, filename/content substitutions, or wrong record
  union arms;
- forged anchor, flow kind, source/sink partition, role, context, PCN/PIF pin,
  topology subject, or port ownership;
- forged roots, ancestry, tips, successors, withdrawals, body groups,
  findings, corroboration, conflict, conclusion, or support summary;
- forged assertion activity, lower lineage health, PT conclusion, direction
  status, current-role relation, or alignment precedence;
- boolean, float, string, negative, out-of-range, or wrong-record indices;
- nested rows privately bound to another material snapshot;
- hidden implication-bearing fields such as `flowing`, `observed`, `rate`,
  `occurred`, `cause`, `safe`, or `recommended_action`; and
- hostile object cycles, excessive depth, or excessive node count.

### 13.4 Authenticity limitation

Authoritative reconstruction proves internal coherence of the selected model
membership and exact derivation of the disclosure. It does not authenticate
foreign evidence bytes, identify a physical connection, or prove that any
flow occurred.

## 14. Store ownership, admission, indexes, and validation order

### 14.1 Public append sequence

`ModelStore.append(record)` retains the accepted sequence:

1. structurally reconstruct and revalidate supplied field data, including all
   nested models and private-state defenses;
2. verify record ID against normative canonical bytes;
3. load and fully validate the complete current membership;
4. if the same ID and exactly equal content exists, return the ID as an
   idempotent no-op;
5. if the same ID exists with different content, reject typed as a
   contradictory same-ID/hash-integrity failure;
6. form the prospective membership;
7. run complete prospective `validate_record_collection()`;
8. serialize stored JSON from normative validated content plus exact ID; and
9. atomically promote exactly one record file.

Any failure leaves no final file and no partial model change.

### 14.2 Full-set validation order

After existing entity, port, PCN, and PIF families are authoritatively rebuilt
and indexed, validate flow records in this order:

1. partition exact FRG, FLD, and FLW records by discriminator;
2. validate FRG anchor uniqueness, semantic-signature uniqueness, canonical
   role sets, disjointness, union bounds, every PRG, full evidence closure,
   mandatory citations, qualified token, and claim basis;
3. validate each FLD's FRG, exact context, exact-union PCN, complete exact PIF
   pins, direction admission table, full evidence closure, mandatory
   citations, claim basis, and parent shapes;
4. build the FLD DAG by exact lineage key and reject cycles or cross-root
   convergence;
5. validate each FLW against a present current unsuperseded tip and reject
   duplicate withdrawals;
6. reject successor-plus-withdrawal races independent of append order;
7. derive immutable roots, ancestry, successors, tips, withdrawals,
   effective-body groups, anchor indexes, semantic-signature indexes, and
   incident-port indexes deterministically; and
8. compute the existing `mrv_` from exact sorted membership.

General record structure, ID/hash, discriminated-union, and evidence closure
errors must remain typed and deterministic. Flow-specific checks must not
mask earlier integrity failures.

### 14.3 Required immutable indexes

At minimum the loaded model needs immutable, sorted indexes for:

- FRG by FlowAnchor ID;
- FlowAnchor IDs by exact semantic signature;
- FlowAnchor IDs by participant PortAnchor ID;
- FLD IDs by `(FlowAnchor ID, exact context)`;
- parents, successors, derived roots, ancestry, and current tips;
- FLW IDs by target FLD;
- effective bodies/groups; and
- source/sink role membership by `(FlowAnchor ID, PortAnchor ID)`.

Every map and nested collection is immutable. Reversed input, copy, and append
orders must yield identical index serialization and revision.

### 14.4 Existing ledger and revision

FRG/FLD/FLW join the existing model record union, store, replay, and `mrv_`
algorithm. No flow-owned ledger or revision is introduced. The authoritative
ledger remains 34 records by default throughout design and implementation
Slices A–C.

## 15. Import direction and package ownership

### 15.1 Ownership table

| Concern | Owner |
|---|---|
| FlowAnchor, pattern, minter | `backend.system_identity` |
| FlowKindToken and FRG/FLD/FLW contracts | `backend.model_kernel` |
| Public generic `build_record` and canonical identity | `backend.model_kernel` |
| Admission, lifecycle, indexes, replay | `backend.model_kernel.store` |
| Flow query/result derivation | `backend.model_kernel` |
| PCN/PIF lifecycle derivation reused by flow results | existing model-kernel PT result helpers |
| Observations and temporal projections | existing lower packages, unchanged |
| BH/ST evaluation | existing upper packages, unchanged and not imported by kernel |
| Future flow assessment/occurrence | later upper layer, absent in FL-001 |

### 15.2 Permitted direction

```text
backend.system_identity
          ^
backend.model_kernel  (PT and flow records/results are peers)
          ^
future flow_assessment / flow_occurrence, if separately designed
```

The arrow means “may be depended on by the layer above.” Same-package reuse of
accepted PT payload derivation does not reverse dependency direction.

### 15.3 Forbidden dependencies

- `backend.system_identity` must not import model-kernel code.
- Model kernel must not import model state, semantic compatibility, constraint
  evaluation, behavior evaluation, state classification, binding or
  interpretation stores, temporal stores, source connectors, ingestion,
  structural/CAD/PDF evidence, sockets, environment, filesystem paths, or
  wall clocks to derive flow results.
- `ModelQueries` owns no `ModelStore` and persists nothing.
- No lower layer imports a future assessment or occurrence package.
- No result validator obtains ambient authority from a repository, cache,
  database, network, or write capability.

Architecture tests must pin allowed import edges and explicitly prove the
absence of `backend.flow_assessment`, source/cutoff parameters, and flow
evaluation APIs.

## 16. Temporal, observed-flow, occurrence, conservation, and causal boundary

### 16.1 Why no evaluation is supportable now

The current stack lacks the contracts needed to say that flow was observed or
occurred:

1. `TemporalOccurrence` is a point observation occurrence, not a flow
   occurrence, and never proves persistence until a later poll.
2. Temporal `changed` compares exact source values in acquisition order; it
   does not mean flow began, stopped, increased, or caused anything.
3. Receipt order and source-native time do not provide a shared physical time
   axis across sources.
4. Model-state selection is per locator and creates no validity interval,
   aggregate value, or sensor fusion.
5. VPA does not relocate an observation to a port or establish origin,
   destination, traversal, or direction.
6. BH same-cohort equality proves at most exact numeric equality within one
   accepted acquisition envelope; it supplies no direction, sum, sign,
   storage term, uncertainty, completeness, or conservation boundary.
7. ST independently selects latest evidence for each condition and explicitly
   reports temporal alignment as not asserted.
8. An ST-002 transition declaration is only model possibility, not an event.
9. Point values, repeated values, gaps, failures, omissions, and close
   timestamps establish no continuity or occurrence.
10. Carry-once reconstruction proves model/result coherence, not raw physical
    authenticity.

Consequently FL-001 must not add a point evaluator merely because a variable
name or semantic token resembles “flow rate.”

### 16.2 Strongest permitted conclusions from current facts

| Available facts | Strongest permitted statement |
|---|---|
| PCN + PIFs + admitted FLD | One explicit revision/context-relative declared flow capability/pathway |
| VPA + variable observation | Association and observation may be displayed separately; not value-at-port or observed flow |
| PIF output/input | Interface-role declaration only |
| PCM compatible | Compatibility declaration only |
| Source-reported numeric rate-like value | One reported point for one variable/locator, not a FlowAnchor measurement |
| `changed` between points | Exact reported-value difference in acquisition order |
| repeated `unchanged` | Equal reported values at sampled points, not continuity |
| BH same-cohort/equal | Same acquisition envelope and exact admitted equality, not conservation |
| ST matches at ordered cutoffs | Two evidence-relative classifications, not a flow event |
| no observation / failed / empty / omitted | Coverage or absence finding, never zero flow |
| close or ordered timestamps | Timestamp relation only, never cause or physical simultaneity |

### 16.3 Prerequisites for any later assessment

A separately designed assessment would require, at minimum:

- an evidence-bearing flow-to-measurement attachment that pins FlowAnchor/FLD,
  exact variable identities, VPA support if relevant, endpoint/boundary role,
  and measurement locus;
- exact quantity-kind, unit, orientation/sign, source/sink polarity, and
  direct-versus-derived-rate semantics;
- an authoritative time axis, assessment instant/window, source alignment,
  skew/cohort, gap, coverage, freshness, persistence, interpolation, and
  late-evidence policy;
- immutable temporal selection material or an accepted snapshot/digest
  revision contract;
- an explicit evaluation family with deterministic refusals, coverage, and
  truth-boundary language; and
- separate result reconstruction that composes only public lower facades.

A derived rate additionally needs interval endpoints, subtraction/division,
decimal behavior, dimensional algebra, and zero/missing rules.

### 16.4 Additional prerequisites for conservation

Conservation needs substantially more than BH equality:

- explicit control-volume or boundary identity;
- proof of relevant boundary-port completeness, which positive PCN topology
  does not provide;
- signed source/sink convention and multi-participant aggregation;
- exact compatible dimensions/units or approved conversion algebra;
- storage/accumulation term and integration window;
- tolerance, uncertainty, and missing-branch policies; and
- co-temporal or explicitly aligned measurements over the same interval.

Without those contracts, equal values do not prove conservation and unequal
values do not prove leakage, fault, loss, or error.

### 16.5 Separate occurrence and causality planes

A later flow occurrence needs its own accountable identity/record or explicit
occurrence contract, exact FlowAnchor and FLD pin, exact admitted source
occurrences, time/window basis, provenance, evidence, lifecycle, replay, and
raw-authenticity boundary. An evaluator must never auto-append an occurrence.

Detection would separately require start/stop thresholds, dwell, debounce,
hysteresis, persistence, gap handling, late evidence behavior, and bounded
historical windows.

Causality requires an explicit causal model or mechanism/intervention
contract and assumptions about confounding and alternative paths. Temporal
order, topology, declared direction, numeric equality, state matches, and a
declared flow never prove causality.

## 17. Threat model

### 17.1 Protected properties

FL-001 must protect:

- opaque flow identity and permanent semantic-signature continuity;
- exact source/sink role partition and qualified flow-kind identity;
- exact, non-retargeted PCN/PIF support pins;
- explicit evidence closure and claim basis;
- content-derived record identity and existing model revision semantics;
- membership-relative lifecycle and replay;
- separation between lifecycle and lower support alignment;
- deterministic, carry-once public disclosure; and
- the boundary between a declared pathway and any physical or temporal claim.

### 17.2 Adversary capabilities

Assume a caller can supply:

- malformed, wrong-prefix, uppercase, truncated, or fabricated IDs;
- Pydantic objects produced by `model_construct`, `model_copy`, nested private
  state, or hostile subclassing;
- duplicate, reordered, omitted, mixed-revision, or wrong-union material;
- corrupted stored JSON, filename/content substitutions, or contradictory
  same-ID payloads;
- dangling, wrong-kind, or replay-omitted evidence references;
- PCN subsets/supersets intended to manufacture pairwise topology;
- PIFs for the wrong port, context, dimension, or role;
- current lower-layer successors intended to retarget an old FLD;
- independent PCN roots intended to masquerade as parallel connections;
- timestamps, names, authority, or append order intended to choose winners;
- forged query conclusions, indices, activities, alignments, private material
  bindings, object cycles, or excessive graphs; and
- observations, VPA, PCM, BH, ST, or transition results intended to launder a
  flow, occurrence, conservation, or causal claim.

### 17.3 Principal attacks and defenses

| Attack | Required defense |
|---|---|
| Name-derived or deterministic anchor | UUID4 opaque minter; names never match |
| Repartition/swap hidden by sorting | Canonicalize role sets separately; preserve role fields |
| Duplicate same semantic flow | Exact signature uniqueness across FRGs |
| Parallel PCN roots treated as connection instances | State explicitly that roots are evidence claims only |
| PCN `(A,B,C)` laundered into `(A)->(B)` | Exact participant-union equality; never containing lookup |
| PIF direction creates flow | Require explicit FRG, FLD, and claim-specific owner evidence |
| Opposite/non-directional PIF used as role support | Exact role admission table rejects |
| Latest PCN/PIF silently replaces pin | Exact record IDs; activity/alignment disclosure; no retarget |
| Another active PCN root hides pinned-root failure | Disclose exact-subject conclusion and pinned-root health separately |
| Support staleness changes FLD lifecycle | Orthogonal derivations and hostile precedence tests |
| Hyperedge expanded into pairwise branches | Group-result contract and explicit non-pairwise assertions |
| Bidirectional PIF creates reverse flow | Separate reverse FlowAnchor required |
| VPA plus observation becomes observed flow | No observation composition; explicit future attachment required |
| BH equality becomes conservation | No flow evaluator; conservation prerequisites explicit |
| Changed value becomes occurrence | No occurrence/detection API; temporal non-inference tests |
| Model `recorded_at` becomes event time | Audit metadata only; queries accept no cutoff |
| Timestamp/authority selects lifecycle winner | Membership/DAG only; deterministic ordering tests |
| Forged nested result or material | Rebuild full membership and expected payload independently |
| Deep/cyclic hostile graph causes resource failure | Bounded iterative traversal and deterministic typed rejection |
| Failed append leaves partial record | Prospective validation and atomic one-file promotion |

### 17.4 Out-of-scope threats

The model kernel does not authenticate human authority, signatures, source
systems, foreign raw bytes, or physical assets. Filesystem and process
security remain outside FL-001. The proposal prevents semantic escalation
within admitted model material; it does not prove that an external claim is
true in the physical world.

## 18. Adversarial acceptance matrix

Every row below is intended to become executable in the owner-gated slice
shown. “Reject” means a deterministic typed failure before any durable
partial write or trusted public result.

### 18.1 Identity, contract, and canonical rows

| ID | Slice | Executable acceptance row |
|---|---|---|
| I01 | A | Malformed, uppercase, wrong-length, wrong-prefix, and non-hex `flo_` IDs reject. |
| I02 | A | Anchor/token/record hidden extras and nested private-state forgeries reject after reconstruction. |
| I03 | A | Equal human names do not merge anchors; different names do not split or select them. |
| I04 | A | Empty source or sink, union below 2 or above 64, duplicate port, overlap, and malformed port reject. |
| I05 | A | Within-role input permutations yield identical tuples, canonical bytes, and IDs. |
| I06 | A | Source/sink reversal or repartitioning changes canonical bytes and the FRG ID. |
| I07 | A | A second anchor for one exact semantic signature rejects; different token, reverse, or partition coexists. |
| I08 | A | All four FlowKindToken fields compare exactly; no vocabulary equivalence is inferred. |
| I09 | A | Evidence, parent, and direction-pin permutations canonicalize; duplicates reject. |
| I10 | A | Equivalent UTC instants canonicalize identically with `+00:00`, never normative `Z`. |
| I11 | A | Every flow record ID suffix equals normative canonical SHA-256; compute and verify APIs agree. |
| I12 | A | Literal golden vectors pin canonical payload, canonical bytes, byte count, ID, stored bytes, and stored hash for FRG/FLD/FLW. |
| I13 | A | Existing record canonical vectors and bytes remain unchanged. |
| I14 | A | Exact equal-record re-append is a validated no-op; contradictory same-ID content rejects. |
| I15 | A | Wrong discriminator/prefix/filename combinations and corrupted sibling files reject. |

### 18.2 Registration, topology, interface, context, and evidence rows

| ID | Slice | Executable acceptance row |
|---|---|---|
| R01 | A | Missing participant PRG or replay-omitted dependency rejects. |
| R02 | A | Same-owner and cross-owner participant sets follow the accepted explicit policy without hierarchy inference. |
| R03 | A | Missing FRG, PCN, PIF, parent, or model-evidence member rejects. |
| R04 | A | PCN subset, proper superset, different union, overlap-only subject, or wrong context rejects. |
| R05 | A | `connections_containing()` output cannot satisfy exact-PCN admission. |
| R06 | A | Missing, extra, duplicate, wrong-participant, wrong-dimension, or wrong-context PIF pin rejects. |
| R07 | A | Source `input`/`non_directional` and sink `output`/`non_directional` exact pins reject. |
| R08 | A | Source `output`/`bidirectional` and sink `input`/`bidirectional` exact pins admit. |
| R09 | A | A valid already-superseded or withdrawn PCN pin admits without retargeting. |
| R10 | A | A valid already-superseded or withdrawn PIF pin admits without retargeting. |
| R11 | A | A current replacement cannot repair an invalid exact stale pin. |
| R12 | A | Lifecycle-view and view-independent positive cases admit only under exact context equality. |
| R13 | A | Context kind, lifecycle view, or union-arm substitution rejects. |
| R14 | A | FRG requires every PRG citation and claim-specific owner basis independently. |
| R15 | A | FLD requires exact FRG, every participant PRG, PCN, every PIF citation, and claim-specific owner basis independently. |
| R16 | A | Every additional model-record evidence reference remains uniformly reference-closed. |
| R17 | A | FRG/FLD are citable; FLW and every existing withdrawal remain uncitable. |
| R18 | A/C | PCN/PIF/PCM/VPA/BH/ST/transition/observation facts cannot create FRG or FLD. |
| R19 | A/C | A PCN/PIF correction or withdrawal never automatically appends, corrects, or withdraws an FLD. |
| R20 | A | Every failed prospective append leaves the model byte-for-byte unchanged. |

### 18.3 Lifecycle, conflict, withdrawal, and replay rows

| ID | Slice | Executable acceptance row |
|---|---|---|
| L01 | A | Parent wrong prefix, missing, self, duplicate, cross-anchor, cross-context, or cycle rejects. |
| L02 | A | A parent tuple crossing independent roots rejects. |
| L03 | A | One-root/one-tip is healthy. |
| L04 | A | Same-root fork conflicts even when exact bodies are equal. |
| L05 | A | Partial convergence remains conflicted. |
| L06 | A | A complete same-root all-tip merge admits and restores one healthy tip. |
| L07 | A | Identical independent healthy bodies corroborate without merging roots. |
| L08 | A | One different exact PCN or PIF pin across healthy roots creates body disagreement. |
| L09 | A | Selective withdrawal of one current fork tip recomputes root health. |
| L10 | A | Unknown, superseded, non-tip, wrong-kind, and duplicate withdrawal targets reject. |
| L11 | A | Successor plus withdrawal of the same tip rejects independent of append order. |
| L12 | A | All roots withdrawn yields inactive; FRG remains registered. |
| L13 | A | Replay omission of successor/withdrawal revives the older membership-relative conclusion. |
| L14 | A | Replay retaining FLD while omitting any pinned or evidence dependency rejects. |
| L15 | A | Deep valid DAGs load iteratively without recursion dependence. |
| L16 | A/C | Timestamps, authority, IDs, filenames, input order, and append order never choose a winner. |

### 18.4 Public query and alignment rows

| ID | Slice | Executable acceptance row |
|---|---|---|
| Q01 | B | Exactly four approved query methods/signatures and exports exist; forbidden aliases are absent. |
| Q02 | B | Malformed IDs/context fail typed; valid-shaped absence returns exact structured absence. |
| Q03 | B | Registration lookup remains registered with no, conflicted, stale-supported, or inactive declarations. |
| Q04 | B | Every declaration conclusion, lineage summary, and finding combination follows Section 12. |
| Q05 | B | Same-root merge, corroboration, disagreement, withdrawal, and historical revival disclose exactly. |
| Q06 | B | PCN activity/root health/topology conclusion are in parity with accepted public PT derivation. |
| Q07 | B | PIF activity/root health/dimension conclusion are in parity with accepted public PT derivation. |
| Q08 | B/C | Complete reachable PCN health × activity and PIF health × activity matrices match alignment precedence; unreachable combinations reject. |
| Q09 | B/C | Current PIF role correction yields exact consistent/inconsistent/indeterminate/not-evaluated relation without changing FLD conclusion. |
| Q10 | B | Another active PCN root cannot hide pinned-root conflict, inactivity, supersession, or withdrawal. |
| Q11 | B | Aggregate support summary follows conflict > inactive > stale > aligned and never changes lifecycle. |
| Q12 | B | Direct declaration and port collection entries agree over identical material and context. |
| Q13 | B | Port collection assigns exact unique source/sink role and canonical entry order without traversal. |
| Q14 | B | Assertion disclosure covers FRG, FLD, FLW, and valid absence with exact activity precedence. |
| Q15 | B | One complete ModelQueryMaterial is carried once; nested authoritative references are strict indices only. |
| Q16 | B/C | Missing, duplicate, extra, reordered, mixed-revision, stale-hash, or wrong-union material rejects. |
| Q17 | B/C | Forged lifecycle, body group, support, relation, index, ordering, context, and precedence fields reject. |
| Q18 | B/C | Bool/float/string/negative/out-of-range/wrong-record indices reject. |
| Q19 | B/C | Hidden extras/private state/model-copy/model-construct laundering and cross-material bindings reject. |
| Q20 | B/C | Hostile cycles, excessive depth, and excessive node counts reject deterministically. |
| Q21 | B | Serialized round-trip reconstructs exactly with no store/filesystem/network/environment/clock access. |
| Q22 | B/C | No result field or method states flow activity, rate, occurrence, continuity, conservation, causality, control, safety, health, or action. |

### 18.5 Hyperedge, temporal, and semantic non-inference rows

| ID | Slice | Executable acceptance row |
|---|---|---|
| N01 | A/C | A many-to-many FRG remains one group relation and produces no pairwise record or conclusion. |
| N02 | B/C | Incident queries never traverse through PCN or another FlowAnchor. |
| N03 | A/C | Reversed role signature coexists as a distinct flow and is never synthesized from `bidirectional`. |
| N04 | A/C | Overlapping flows and graph cycles imply no path, exclusivity, capacity, priority, or cause. |
| N05 | C | VPA plus observation cannot become value-at-port or observed flow. |
| N06 | C | PIF direction plus PCN cannot create a flow identity or declaration. |
| N07 | C | PCM compatibility cannot create possible, current, or observed flow. |
| N08 | C | BH same-cohort equal cannot become transfer or conservation. |
| N09 | C | BH same-cohort different cannot become leak, fault, or loss. |
| N10 | C | `changed`, zero-to-positive, or ordered ST classifications cannot create start, stop, or occurrence. |
| N11 | C | Repeated `unchanged` cannot create continuity, dwell, or persistence. |
| N12 | C | Source/receipt proximity cannot create simultaneity or causality. |
| N13 | C | Empty, failed, quarantined, omitted, or stale evidence cannot become zero/current flow. |
| N14 | C | A rate-like variable cannot attach to FlowAnchor without a future explicit measurement contract. |
| N15 | C | PCN hyperedge cannot become a closed control volume or complete boundary. |
| N16 | C | Model `recorded_at` never becomes occurrence time; `mrv_` never becomes temporal cutoff. |

### 18.6 Preservation and reproduction rows

| ID | Slice | Executable acceptance row |
|---|---|---|
| P01 | A–C | Authoritative model remains exact accepted 34 records/revision with zero FRG/FLD/FLW. |
| P02 | A–C | Historical 9/10/11/14/16/18/28/29/32/34 memberships and revisions replay unchanged. |
| P03 | A–C | Every authoritative predecessor record byte and accepted PT/VP/BH/ST artifact hash is unchanged. |
| P04 | A–C | No hidden flow fields are added to PT, VP, BH, ST, transition, observation, binding, or interpretation contracts. |
| P05 | A–C | Reversed predecessor/input/append order and multiple hash seeds produce identical records, indexes, revision, and query bytes. |
| P06 | C | Two independent disposable roots reproduce the same positive world without copying generated records. |
| P07 | C | Working, fresh base-only, and fresh all-extras columns produce byte-identical reproduction hashes. |
| P08 | A–C | Full repository, compilation, OCP/STEP, PDF, and separately permitted loopback paths remain green. |
| P09 | A–C | Working-tree and full milestone-range whitespace checks pass; exact status/topology is reported. |
| P10 | A–C | No identity is minted or record appended to the authoritative model without a later separate owner gate. |

## 19. Determinism and historical-preservation obligations

### 19.1 Red-first evidence

Every implementation slice begins with focused tests that fail for the
specific absent or defective contract, followed by the narrow implementation
and passing-after evidence. A genuine repair discovered during hardening must
record the exact failing-before and fixed-after case. Tests must not encode
an unapproved owner decision before that decision is fixed.

### 19.2 Historical memberships

Replay the accepted explicit 9, 10, 11, 14, 16, 18, 28, 29, 32, and 34
record memberships. For each, prove the exact historical revision, exact
membership, reference closure, immutable empty flow indexes where applicable,
and—after query authorization—structured flow absence. Existing histories
must not be recomputed from directory enumeration or present-day tips.

### 19.3 Authoritative preservation

Before and after every slice:

- the authoritative ledger remains exactly 34 records at the accepted
  revision;
- it contains zero `frg_`, `fld_`, and `flw_` files;
- it still contains zero transition records;
- every authoritative record byte is unchanged;
- every binding, interpretation, temporal, source, structural, PT, VP, BH,
  and ST fixture is unchanged; and
- accepted PT/VP/BH/ST artifact bytes and SHA-256 values are unchanged.

Freeze and compare an exact authoritative record inventory and aggregate hash.
Do not use a count alone as preservation evidence.

### 19.4 Deterministic disposable reproduction

Positive coverage uses at least two independently initialized disposable
model roots built from byte-identical explicit predecessor membership. One
column reverses predecessor copy/input order. Each independently constructs
records through public identity, `build_record`, and `ModelStore` APIs; it
must not copy generated flow record files from another root.

Compare directly across roots:

- anchor serialization supplied by the disposable test fixture;
- canonical FRG/FLD/FLW bytes and IDs;
- stored bytes and file hashes;
- semantic append sequence;
- exact membership and `mrv_`;
- immutable index serialization;
- all four query serializations;
- predecessor aggregate; and
- all protected artifact hashes.

Repeat at the accepted implementation HEAD in the working checkout, a fresh
base-only checkout, and a fresh all-extras checkout under multiple hash seeds.
Locale, timezone spelling, wall clock, and filesystem enumeration must not
affect results.

### 19.5 Verification tiers for future slices

Focused suites are separated by identity/minter, record/canonical contracts,
store admission/lifecycle, hostile record reconstruction, architecture and
preservation, query contracts/conclusions, PT-parity, result revalidation,
and deterministic reproduction.

Affected suites include the complete model kernel plus identity, model-state,
constraint, behavior, state-classification, and semantic/observation paths
that serialize `ModelRecord` or `ModelQueryMaterial`. Then run the complete
repository, backend compilation, fresh base-only and all-extras suites,
focused OCP/STEP and PDF paths, and the loopback test separately if the
sandbox denies it.

For this design-only phase, executable verification is limited to proposal
file integrity, exact ending marker, whitespace checks, and Git status. No
unimplemented runtime test is manufactured.

## 20. Bounded synthetic-demo policy and mandatory pre-append owner gate

### 20.1 Default policy

The authoritative demo ledger remains 34 records throughout FL-001 Slices
A–C. Positive tests use disposable synthetic worlds. No design approval or
implementation-slice approval authorizes minting or freezing an authoritative
FlowAnchor, changing `models/demo-printer`, or appending FRG/FLD/FLW.

### 20.2 Current demo evidence assessment

The current synthetic demo contains two registered ports, an exact common
PCN, and complementary direction-role PIF declarations. Those lower-layer
facts are sufficient to support *admission evidence* for a later bounded
synthetic flow declaration if:

- the owner accepts the FL-001 design and implementation first;
- the exact PCN union and PIF contexts/roles satisfy the final contract;
- a claim-specific synthetic owner declaration supplies the flow claim and
  qualified FlowKindToken;
- the artifact says only `registered`/`declared` and exact pin alignment; and
- no observation, VPA, BH, state match, transition, or temperature value is
  represented as flow evidence.

They do not create a flow automatically and do not justify an evaluation or
occurrence fixture.

### 20.3 Required gate before any append

A future demo append is nonexistent unless separately proposed. Its first
authorization must be **pre-append rehearsal only** and must require:

1. proof that no candidate manifest already exists;
2. exact freeze of authoritative predecessor membership, record bytes, and
   protected artifact hashes;
3. one-time public minter allocation, persisted immediately and never
   repeated for that candidate;
4. deterministic reconstruction from the frozen manifest in independent
   disposable roots;
5. public builder and `ModelStore` use only;
6. canonical bytes/ID suffix/stored bytes/revision/query parity;
7. direct byte-identical candidate disclosure artifacts across reproduction
   columns;
8. unchanged authoritative ledger throughout rehearsal; and
9. an owner question approving the exact frozen contract and separately
   requesting authority to append.

Even after rehearsal approval, authoritative append requires a second,
explicit authorization. The append must be exact and must stop again for
final owner acceptance. No candidate ID, record ID, revision, artifact hash,
or timestamp is invented by this proposal.

### 20.4 Mandatory synthetic disclaimer

Any later candidate and accepted demo artifact must include, at minimum:

> This is an illustrative synthetic FL-001 flow identity and declaration
> fixture. `declared` means only that the selected model membership contains
> an admitted evidence-bearing declaration over the stated exact port-role,
> topology, interface, context, and flow-kind claims. It does not claim that a
> real printer carries material, signal, energy, or data; that flow is active,
> observed, commanded, current, continuous, or occurred; that any rate,
> quantity, or observation occurred at or travelled through a port; that
> source and sink observations are simultaneous or persistent; that anything
> is conserved; or that topology, compatibility, values, state, transition,
> timing, or order establishes transport, influence, cause, control, safety,
> health, diagnosis, correctness, or recommended action.

It must also state that names, ownership, hierarchy, CAD, proximity, PCN,
PIF, PCM, VPA, BH, ST, transition declarations, observations, temporal
correlation, and value changes did not create the flow. Displaying an
observation beside a flow does not attach or persist it as flow truth.

## 21. Owner-gated implementation slices

No slice begins without separate owner authorization against an accepted
architecture hash.

### 21.1 Slice A — identity, records, store, lifecycle, and replay

Authorized only after owner approval:

- FlowAnchor pattern/export and pure minter;
- FlowKindToken, direction pin, FRG/FLD/FLW contracts;
- generic builder integration, record union, evidence grammar, prefixes,
  filenames, canonical vectors, and effective-body projection;
- full store admission, exact PCN/PIF rules, lifecycle DAG, withdrawals,
  indexes, revision, and historical replay;
- identity/record/store/forgery/architecture tests for applicable I, R, L, N,
  and P rows; and
- focused, affected, full, compilation, preservation, and clean-checkout
  verification.

Slice A includes no public flow query, result contract, authoritative flow
fixture, assessment, occurrence, or ConnectionAnchor. It ends with a full
filesystem completion report and owner validation gate.

### 21.2 Slice B — exactly four read-only queries

Authorized separately after Slice A acceptance:

- exactly the four methods in Section 11.1;
- exact result contracts, field order, literal vocabulary, exports, and
  deterministic ordering;
- one carry-once material and strict-index nested rows;
- shared authoritative PT support derivation;
- complete conclusion/alignment/current-role matrices;
- hostile outer-result reconstruction and import isolation;
- exact structured absence on the untouched authoritative 34-record ledger;
  and
- applicable Q, N, and P rows plus full verification.

Slice B adds no flow evaluation, occurrence, traversal, fixture, or ledger
record. It ends at a separate owner gate.

### 21.3 Slice C — integrated hardening and deterministic reproduction

Authorized separately after Slice B acceptance:

- all remaining adversarial acceptance rows;
- disposable same-owner and cross-entity 1→1, fan-out, fan-in, and many-to-many
  worlds built only through public APIs;
- strict exact-union topology and direction-pin attacks;
- stale support, context, same-root merge, independent-root corroboration /
  disagreement, withdrawal, historical revival, and alignment precedence;
- direct versus port-collection parity;
- reversed signatures and overlapping-flow non-inference;
- deterministic dual-root and working/base-only/all-extras reproduction; and
- full historical and artifact preservation.

Slice C repairs only demonstrated defects within the accepted contract. It
does not expand vocabulary or create an authoritative candidate.

### 21.4 Optional Slice D — nonexistent without a new gate

Slice D is not part of the authorized v1 implementation plan. It exists only
if, after Slice C acceptance, the owner separately requests a bounded
synthetic-demo proposal and then authorizes the pre-append process in Section
20. No flow evaluation or occurrence can be smuggled into that fixture.

## 22. Explicit exclusions, limitations, and future compatibility

### 22.1 Explicit exclusions

FL-001 v1 provides no:

- stable connection, cable, pipe, channel, bus, conduit, route, or segment
  identity;
- distinction between parallel same-signature physical mechanisms;
- endpoint-changing connection or flow continuity;
- inferred flow from PCN, PIF, PCM, VPA, BH, ST, transition, observations,
  names, hierarchy, geometry, proximity, or CAD;
- dynamic port roles, neutral participants, same-port flows, single-record
  loops, route identity, or path composition;
- payload/variable attachment, observation-at-port, measured flow, rate,
  quantity, unit, amount, duration, persistence, or history;
- command, target, setpoint, controller, guard, action, effect, or state
  machine;
- simulator, estimator, detector, evaluator, optimizer, or automatic
  next-flow selection;
- conservation, balance, completeness, capacity, contention, efficiency,
  loss, or leakage result;
- transition/occurrence generation or temporal inference; or
- cause, influence, safety, health, diagnosis, correctness, validity, or
  recommendation.

### 22.2 Known limitations

- Flow identity is an abstract kind-qualified role partition, not a physical
  mechanism.
- Exact semantic-signature uniqueness means parallel same-kind mechanisms
  with identical participants cannot be distinguished.
- Mandatory PIF roles exclude a directed declaration supported only by a
  `non_directional` or opposite-role interface claim.
- Exact-union PCN pinning rejects a containing bus assertion unless an exact
  PCN for the declared participant union also exists.
- Static source/sink partitions cannot model dynamic bus arbitration.
- FlowKindToken is nominal and opaque to the kernel.
- Different exact support-pin bodies conflict even if humans consider the
  underlying lower claims equivalent.
- Contexts compare exactly and cannot map across lifecycle views.
- Declaration currentness is model-membership-relative, not physical
  currentness.
- Internal result coherence does not authenticate external evidence or the
  physical world.

### 22.3 Future compatibility guarantees

Future work may add, through separate owner-gated contracts:

- ConnectionAnchor and connection-owned records;
- an additive mechanism discriminator for parallel same-signature flows;
- separately queryable commodity, carrier, payload, or protocol dimensions;
- explicit flow-to-measurement and boundary associations;
- temporal cohort/continuity/window contracts;
- rate/amount/occurrence assertions;
- control-volume and conservation declarations/evaluations;
- command and control planes; and
- causal-model claims.

Such work must be additive. It must not reinterpret an existing `flo_`
anchor, change FRG permanent meaning, retarget an FLD pin, reclassify a PCN
root as a connection identity, mutate historical `mrv_` revisions, or add
hidden flow fields to PT/VP/BH/ST/transition records.

## 23. Genuine unresolved owner decisions and approval gate

The lead recommendation is coherent, but these nine decisions are genuinely
implementation-blocking and require owner resolution:

1. **Durable locus:** approve a logical, kind-qualified directed FlowAnchor
   and defer ConnectionAnchor, accepting that v1 cannot name parallel or
   replaced physical connections?
2. **Identity signature:** approve permanent
   `(source set, sink set, complete FlowKindToken)` identity, with every token
   field exact and a new anchor required for any role or token change?
3. **Hyperedge scope:** approve full 1→1, fan-out, fan-in, and many-to-many
   directed hyperedges as non-pairwise group relations, rather than limiting
   v1 to 1→1?
4. **Support contract:** approve one exact-union PCN plus one exact
   direction-role PIF per participant, and the strict role table that admits
   source output/bidirectional and sink input/bidirectional only?
5. **Duplicate signature:** approve at most one FRG per exact semantic
   signature, deferring parallel same-kind mechanisms until an additive
   discriminator or ConnectionAnchor exists?
6. **Entity boundary:** approve flows spanning several exact port owners,
   with no single subject entity and no inference from hierarchy?
7. **Context and stale pins:** approve both exact AssertionContext arms,
   already-superseded/withdrawn support-pin admission, no automatic
   retargeting, and support alignment orthogonal to FLD lifecycle?
8. **Public surface:** approve prefixes `flo_`, `frg_`, `fld_`, `flw_` and
   exactly `flow()`, `flow_declaration()`, `flows_involving_port()`, and
   `flow_assertion()` with the proposed result vocabulary?
9. **Demo boundary:** approve keeping the authoritative ledger at 34 through
   Slices A–C and treating the existing synthetic PT material only as a
   possible later, separately proposed declaration-fixture prerequisite—not
   authorization for an append, assessment, or occurrence?

Until these questions and the proposal as a whole are accepted, no FL-001
implementation slice, identity allocation, fixture, record, ledger append,
artifact, commit, push, merge, or history operation is authorized.

END OF FL-001 CODEX LEAD PROPOSAL
