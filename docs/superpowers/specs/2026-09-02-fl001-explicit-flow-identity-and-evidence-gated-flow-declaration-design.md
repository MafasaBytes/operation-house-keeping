# FL-001 — Explicit Flow Identity and Evidence-Gated Flow Declaration

**Status:** corrected final synthesis; owner design approval pending

**Date:** 2026-09-02

**Milestone boundary:** declaration-only model knowledge and read-only
disclosure; no implementation is authorized by this specification

This specification uses **MUST**, **MUST NOT**, **SHOULD**, and **MAY** in
their ordinary normative senses.

## 1. Status, baseline, authority order, and input digests

### 1.1 Verified baseline

| Item | Verified value |
|---|---|
| Repository | `operation-house-keeping` |
| `HEAD` | `1d53d8adb22aada01bf808adb7dc7454a688543d` |
| local `main` | `1d53d8adb22aada01bf808adb7dc7454a688543d` |
| `origin/main` | `1d53d8adb22aada01bf808adb7dc7454a688543d` |
| Authoritative model | exactly 34 records |
| Authoritative revision | `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41` |
| Transition records | zero TRG, zero TRD, zero TRW |
| FL-001 records | zero FRG, zero FLD, zero FLW |
| Initial untracked files | lead proposal and challenger audit only |

ST-002 is complete and owner accepted. No model, fixture, artifact, or
runtime change was made during synthesis.

### 1.2 Frozen inputs

Both files were read completely after their digests were verified:

| Input | SHA-256 |
|---|---|
| `docs/superpowers/proposals/2026-09-02-fl001-codex-lead-proposal.md` | `4ab663af9e5766bb088353c95878b9115fb96973939778fc0fb42ac195dac092` |
| `docs/superpowers/reports/2026-09-02-fl001-codex-lead-proposal-challenger-audit.md` | `449243118c95eb1296d8d0ffa1373daaa19261d629f8bf16b2383366ba822d3e` |

The audit verdict is **approve with corrections**, with zero blocking
findings, three required corrections, and eight non-blocking observations.

### 1.3 Authority order

Conflicts are resolved in this order:

1. the owner's decisions and explicit rulings in the synthesis request;
2. this corrected final synthesis after owner approval;
3. already accepted repository contracts, specifications, and ADRs;
4. the lead proposal, corrected by the challenger audit; and
5. the challenger audit's recommendations where the owner did not rule more
   specifically.

The lead proposal and audit remain immutable source artifacts. This
specification supersedes their unresolved-question and correction status; it
does not modify them.

### 1.4 Approval effect

Approval of this document fixes architecture only. It does not authorize
code, tests, identity minting, fixture construction, ledger append, artifact
generation, commit, push, merge, or history operation. Each implementation
slice in Section 29 requires separate authorization and later owner
acceptance.

## 2. Change log from the lead proposal

| Change | Final synthesis disposition |
|---|---|
| Proposal status | Replaced “owner questions pending” with a fixed owner-decision register. |
| RC1 | Rewrote PCN/PIF lineage-health × activity reachability precisely; only `(inactive, current)` is impossible. |
| RC2 | Made `flows_involving_port()` exact-context declaration-scoped; other contexts are excluded from entries and every derivation. |
| RC3 | Added normative and executable positive FRG admission with no current—or any—PCN/PIF support. |
| Q5 | Fixed one logical flow per canonical signature and deferred physical parallel-mechanism discrimination. |
| NB1 | Made dynamic arbitration an explicit future owner-gated contract, not a v1 encoding technique. |
| NB2 | Required one shared authoritative PT payload derivation; flow code may not inline a parallel copy. |
| NB3 | Stated that exact-subject topology conclusion never substitutes for pinned-root health. |
| NB4 | Strengthened the permanent parallel same-signature limitation and additive future gate. |
| NB5 | Preserved opaque FlowKindToken semantics and assigned vocabulary honesty to the declaring authority. |
| NB6 | Required identical support rows for corroborating roots grouped under one effective body. |
| NB7 | Reused the accepted carry-once reconstruction discipline without a new validation machine. |
| NB8 | Retained the current demo only as a conditionally eligible later declaration-fixture prerequisite. |
| Slice layout | Kept A and B; found no necessary v1 cross-layer Slice C; retained D only as a separately proposed demo gate. |

No public prefix, core record field, identity signature, PCN/PIF admission
rule, lifecycle vocabulary, or four-query name from the lead architecture is
relaxed.

## 3. Audit reconciliation table

| Audit item | Normative disposition | Final sections |
|---|---|---|
| RC1 | Incorporated: full reachable matrices, precise impossible pair, and admit/reject acceptance row. | 17.4–17.5, 20, 26 Q08 |
| RC2 | Incorporated: exact requested context only; registered/empty when none; hostile context substitution rejects. | 16, 19, 20, 26 Q13/Q23 |
| RC3 | Incorporated: FRG admits independently of PCN/PIF presence or currentness; identity/support/occurrence separated. | 14.3–14.4, 26 R21 |
| NB1 | Incorporated: dynamic bus arbitration deferred to an owner-gated future contract. | 11.4, 30.3 |
| NB2 | Incorporated: call one shared authoritative PT derivation; no flow-specific inline copy. | 17.3, 20.2, 22 |
| NB3 | Incorporated: topology conclusion is not lineage health and must be disclosed beside pin health. | 17.3–17.4, 18.4 |
| NB4 | Incorporated and resolved by owner: no same-signature physical-mechanism discrimination in v1. | 8, 30.2–30.3, 31 D5 |
| NB5 | Lead decision retained: token stays nominal and opaque; authority bears vocabulary-discipline burden. | 12.2–12.4 |
| NB6 | Incorporated: a shared effective-body group requires identical support rows across corroborating roots. | 15.6, 18.4, 26 Q25 |
| NB7 | Lead decision retained and clarified: accepted carry-once machinery is reused, not duplicated. | 20 |
| NB8 | Incorporated: verified PT facts are only conditional support for a later separately gated synthetic declaration. | 28.2–28.4 |

Every observation was reviewed. NB5 and NB7 require no new model scope;
their existing lead decisions are sufficient once the stated implementation
discipline is explicit.

## 4. Objective and exact non-objectives

### 4.1 Objective

FL-001 establishes the smallest explicit vocabulary that can:

1. mint an opaque durable logical flow identity;
2. permanently register its exact source-port set, sink-port set, and
   qualified nominal flow kind;
3. declare an evidence-backed flow capability/pathway under one exact
   assertion context;
4. pin one exact matching PCN and one exact direction-role PIF for every
   participant;
5. correct, corroborate, conflict, withdraw, and replay declarations without
   silent evidence retargeting; and
6. disclose identity, declaration lifecycle, support activity/alignment, and
   incident-port membership through exactly four read-only model queries.

### 4.2 Normative truth boundary

> An admitted FLD means only that an authority explicitly declared one
> kind-qualified directed port-group capability or pathway under the exact
> context and exact cited support records. It does not mean anything was
> commanded, observed, calculated, transferred, conserved, caused, active,
> current in the physical world, correct, healthy, safe, or recommended.

`registered`, `declared`, `healthy`, `current`, `aligned`, and `asserted`
are scoped model/support disclosures. None is a physical-flow conclusion.

### 4.3 Concepts that remain separate

| Concept | Owner-approved FL-001 treatment |
|---|---|
| Positive connection assertion | Existing PCN only; common membership, not adjacency or flow |
| Durable logical flow identity | FlowAnchor plus FRG |
| Declared flow capability/pathway | Exact-context FLD |
| Commanded flow | Deferred |
| Observed flow | Deferred |
| Calculated or inferred flow | Deferred |
| Particular flow occurrence | Deferred to a separate occurrence plane |
| Causal influence | Deferred |
| Conservation or balance | Deferred |

Identity admission, structural/evidence closure, declaration currentness,
support activity, support alignment, and physical occurrence are distinct
axes. No result collapses them into one validity or activity boolean.

### 4.4 Exact non-objectives

FL-001 does not provide:

- flow assessment, occurrence, observation, calculation, rate, amount, unit,
  duration, persistence, history, continuity, loss, efficiency, or capacity;
- command, target, setpoint, controller, guard, action, effect, or state
  machine;
- simulation, estimation, detection, optimization, path finding, traversal,
  routing, addressing, arbitration, reachability, or next selection;
- conservation, balance, causal, diagnostic, safety, health, correctness, or
  recommendation conclusions;
- connection, cable, pipe, conduit, channel, bus, route, or mechanism
  identity; or
- observation/source/cutoff/temporal composition in the model kernel.

No `backend.flow_assessment`, `backend.flow_occurrence`, or equivalent
package is part of FL-001.

## 5. Alternatives considered

### 5.1 Alternative A — FlowAnchor owns the logical directed locus

One permanent registration fixes:

```text
(canonical source port set, canonical sink port set, complete FlowKindToken)
```

PCN/PIF records remain exact contextual support pins in correctable FLDs.
Their correction or withdrawal cannot mutate identity or retarget an older
declaration. This alternative is adopted.

### 5.2 Alternative B — ConnectionAnchor first

Rejected for FL-001. A ConnectionAnchor would be justified only for a
particular physical/logical connection, continuity across endpoint change,
parallel same-endpoint mechanism distinction, connection-owned variables /
behavior/state/metadata, or route/segment identity. PT-001 deliberately
provides none of those meanings.

PCN roots cannot be promoted into connection identities. They are
context-bound evidence lineages; independent roots may corroborate the same
topology subject. Treating each root as a physical object would transform
evidence plurality into invented mechanism plurality.

### 5.3 Alternative C — content-derived flow identity

Rejected. PCN/PIF IDs change on correction, PCN is unordered, PIF is
per-port, and neither is a flow claim. A composite support hash would silently
change identity when evidence changed.

### 5.4 Alternative D — defer flow identity entirely

Rejected as unnecessarily restrictive. Existing stable PortAnchors, exact
model membership, qualified tokens, and accepted registration/declaration
lifecycle support a declaration-only flow plane. Evaluation and occurrence,
not identity, are unsupported.

## 6. Final FlowAnchor and no-ConnectionAnchor decision

### 6.1 Adopted referent

> A v1 FlowAnchor identifies one logical, kind-qualified directed port-group
> relation. It does not identify any particular physical connection, path,
> channel, carrier instance, mechanism, or occurrence.

The anchor is opaque. FRG gives it permanent model meaning. FLD supplies
correctable exact-context assertion meaning and exact support pins.

### 6.2 Why FlowAnchor safely owns continuity

The permanent role sets and complete FlowKindToken define what the logical
flow is. The exact PCN/PIF support records are not continuity owners. When a
support record is corrected or withdrawn:

- the FlowAnchor and FRG remain unchanged;
- the old FLD retains its original exact pins;
- support activity/alignment changes only in read-only disclosure;
- an authority may append a correcting FLD with new exact pins; and
- no latest record is silently substituted.

This preserves historical meaning without requiring a connection identity.

### 6.3 No ConnectionAnchor in FL-001

FL-001 MUST NOT introduce, reserve, mint, or imply a ConnectionAnchor,
pathway anchor, mechanism anchor, connection registration, connection-owned
state, or connection revision. A future additive milestone may do so only
under Section 8.4 and Section 30.3.

## 7. Identity and continuity policy

### 7.1 Opaque anchor contract

```python
FLOW_ANCHOR_ID_PATTERN = r"^flo_[0-9a-f]{32}$"

class FlowAnchor(...):
    anchor_id: str
    namespace: str
    display_name: str
    role_name: str | None = None
```

It reuses the accepted name grammar, is frozen and extra-forbidden, and uses
`revalidate_instances="always"`. It contains no port, kind, owner, context,
evidence, declaration, topology, interface, variable, time, activity,
occurrence, command, cause, or result field.

### 7.2 Public minter

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
I/O, clock access, environment access, deterministic seeding, authority
claim, or name-derived identity.

### 7.3 Permanent signature

One FRG permanently fixes:

```text
(source_port_anchor_ids, sink_port_anchor_ids, complete FlowKindToken)
```

Each role tuple is nonempty, duplicate-free, and lexicographically sorted.
The two sets are disjoint. Their union contains 2–64 ports. Within-role order
is non-semantic; source versus sink is semantic.

Changing a participant, moving a port between roles, reversing roles, or
changing any token field requires a new FlowAnchor and FRG. Names, evidence,
authority, note, recorded time, or support-pin correction do not.

### 7.4 Ownership and entity scope

FlowRegistration has no single subject entity. Every participant's owner is
already fixed by its PRG. Same-owner and cross-entity flows are admitted only
through exact ports and explicit evidence. Hierarchy and relationships never
create or own the flow. No system/plant/network scope field exists in v1.

### 7.5 Continuity non-inference

Names, source paths, ownership, hierarchy, CAD, geometry, proximity, contact,
matching tokens, PCN/PIF correction, PCM, VPA, BH, ST, transition records,
observations, timestamps, correlations, and value changes never establish
identity continuity. Replacing a physical port requires a new PortAnchor and
therefore a new FlowAnchor.

## 8. Parallel same-signature limitation and future gate

### 8.1 Exact uniqueness rule

Within one selected membership there is at most one FRG for each exact:

```text
(canonical source tuple, canonical sink tuple, complete FlowKindToken)
```

A second FlowAnchor/FRG for that signature rejects typed. Reversed roles,
different partitions, or different complete tokens are distinct signatures
and may coexist.

### 8.2 Supported meaning

The one admitted identity names one declared logical directed flow for the
canonical signature. It does **not** assert that only one physical mechanism
exists. Independent FLD roots are multiple evidence claims about that one
logical flow, not parallel mechanisms or occurrence instances.

### 8.3 Unsupported distinction

FL-001 cannot distinguish two physically distinct parallel pipes, wires,
channels, routes, or mechanisms with the same logical signature. It MUST NOT
mint multiple indistinguishable flow identities merely to suggest that
plurality. PCN independent roots are corroborating topology evidence, not
parallel-connection identities.

This limitation is safer than inventing identity without distinguishing
evidence: fabricated plurality would look authoritative, could not be tied to
one mechanism in queries or replay, and would let correction-lineage roots
masquerade as physical objects.

### 8.4 Future additive gate

If an application requires parallel distinction, a separate owner-gated
milestone must introduce an evidence-backed connection/path/mechanism
identity and its registration, lifecycle, and query contract. It creates new
identities. It must not reinterpret existing `flo_` anchors, alter FRG
meaning, promote PCN roots, or mutate historical `mrv_` revisions.

## 9. Exact anchors, records, prefixes, discriminators, and builders

### 9.1 Prefix and evidence table

| Prefix | Type | Discriminator | Citable by `ModelRecordEvidence` |
|---|---|---|---|
| `flo_` | `FlowAnchor` | n/a | n/a |
| `frg_` | `FlowRegistration` | `flow_registration` | yes |
| `fld_` | `FlowDeclaration` | `flow_declaration` | yes |
| `flw_` | `FlowDeclarationWithdrawal` | `flow_declaration_withdrawal` | no |

`flo_` avoids collision with withdrawal; `frg_` follows the accepted `*rg_`
registration convention. Add FRG/FLD/FLW to record-ID and filename grammars,
the discriminator/prefix map, discriminated adapter, `ModelRecord` union,
store partitions, and public exports. Add only `frg|fld` to the existing
model-record evidence regex.

### 9.2 Qualified token

```text
FlowKindToken
  token_kind: Literal["flow_kind"]
  system_id: LocalIdentifier
  system_edition: LocalIdentifier
  code: LocalIdentifier
```

It is frozen, extra-forbidden, and always revalidated.

### 9.3 Registration record

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

### 9.4 Exact direction pin

```text
FlowDirectionDeclarationPin
  port_anchor_id: prt_[0-9a-f]{32}
  declaration_record_id: pif_[0-9a-f]{64}
```

It is frozen, extra-forbidden, and always revalidated. Its containing field
supplies source/sink role; no duplicate caller-controlled role string exists.

### 9.5 Declaration record

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

Source/sink pin ports equal the corresponding FRG role tuple exactly, with
one pin per participant.

### 9.6 Withdrawal record

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

### 9.7 Builders

The accepted public `backend.model_kernel.build_record(record_cls, **fields)`
constructs FRG, FLD, and FLW and computes their IDs. No flow-specific record
builder is added. `mint_flow_anchor()` is the only new identity builder.
Callers must not hand-build record IDs, derive anchors from names, or bypass
these APIs.

## 10. Immutable versus correctable fields

| Field/fact | Owner | Mutability rule |
|---|---|---|
| FlowAnchor ID | FlowAnchor | Opaque and permanent |
| Anchor human metadata | Embedded in one FRG | Frozen record content; never used for matching |
| Source port tuple | FRG | Permanent; change requires new FlowAnchor |
| Sink port tuple | FRG | Permanent; change requires new FlowAnchor |
| Complete FlowKindToken | FRG | Permanent; any field change requires new FlowAnchor |
| Participant PRG basis | FRG evidence/closure | Exact at admission and replay |
| AssertionContext | FLD lineage key | Exact and fixed within one lineage; another context is independent |
| PCN pin | FLD effective body | Corrected only by a successor FLD; old pin never retargets |
| PIF pins | FLD effective body | Corrected only by a successor FLD; old pins never retarget |
| FLD evidence/authority/time/note | Individual FLD | New record may differ; excluded from effective-body equality |
| FLD parents | Individual FLD | Canonical DAG position; immutable after record creation |
| Withdrawal | Separate FLW | Targets one current tip; never mutates the FLD |
| Support activity/alignment | Query derivation | Membership-relative disclosure; never persisted in FRG/FLD |
| Physical occurrence | Not represented | Deferred |

FRG has no context, parents, PCN/PIF/PCM/VPA pin, activity, magnitude, unit,
command, occurrence, behavior, state, transition, or result field. FLD has no
evaluation basis, latest-pointer instruction, enabled flag, source selector,
cutoff, observation, rate, amount, unit, trigger, action, effect, occurrence,
confidence, validity, diagnosis, safety, or recommendation. FLW has no
evidence, context, replacement, outcome, reason code, or stopped-flow meaning.

## 11. Endpoint roles, hyperedge semantics, and canonicalization

### 11.1 Directed hyperedge

The permanent role signature is one directed hyperedge:

```text
{source ports} -> {sink ports}
```

It is one group relation. It does not expand into a complete bipartite graph,
pairwise adjacency, per-branch flow, broadcast, duplication, mixing,
summation, allocation, arbitration, conservation, path, capacity, or
occurrence. Applications needing separately assertable branches require
separate FlowAnchors with different signatures or a future explicit branch
contract; queries never manufacture branches.

### 11.2 Arity and role rules

- source tuple length: 1–63, subject to total-union bound;
- sink tuple length: 1–63, subject to total-union bound;
- total distinct union: 2–64;
- no duplicate within a role;
- no port in both roles;
- each tuple sorted lexicographically after validation; and
- source and sink fields never exchanged or jointly sorted.

The bounds are enforced on the complete union. A single-port or same-port
self-flow rejects.

### 11.3 Supported shapes

| Shape | Treatment | Mandatory non-claim |
|---|---|---|
| 1 source → 1 sink | Supported | No transfer/occurrence inferred |
| 1 → N fan-out | One group hyperedge | No broadcast, duplication, or N pairwise flows |
| N → 1 fan-in | One group hyperedge | No mixing, summation, or causal contribution |
| N → M | One group-to-group hyperedge | No complete bipartite graph or routing |
| Static bus partition | Supported when every participant has one permanent role | No addressing, arbitration, talker selection, or reachability |
| Reversed direction | Separate signature and FlowAnchor | No reverse inferred |
| Several different signatures sharing ports | Supported | No exclusivity, priority, capacity, or contention inferred |
| Graph cycle across FlowAnchors | Records may coexist | No traversal, circulating-flow, loop, or causal conclusion |

### 11.4 Bidirectional PIF and dynamic arbitration

A PIF value `bidirectional` is eligible support for either one permanent flow
role. It does not create the reverse FlowAnchor and does not choose a runtime
speaker, direction, order, priority, token holder, or controller.

Genuinely dynamic talker selection or bus arbitration is deferred to a
separately owner-gated arbitration contract. It MUST NOT be encoded through
role correction, multiple indistinguishable FlowAnchors, timestamps, or
query-time selection in v1.

### 11.5 Cross-entity semantics

One hyperedge may span ports owned by several entities. The owner set is
derived for disclosure only from exact PRGs. It is not shared ownership, a
system boundary, or evidence of an entity relationship. Same-owner and
cross-entity cases use identical flow admission rules.

### 11.6 Normative record canonicalization

Flow records use only `backend.model_kernel.canonical`:

1. reconstruct and revalidate the complete record;
2. `model_dump(mode="python", exclude={"record_id"})`;
3. recursively normalize datetimes to UTC `.isoformat()` using `+00:00`;
4. preserve source/sink field roles and already-canonical tuple order;
5. encode JSON with sorted keys, compact separators, UTF-8, and
   `ensure_ascii=False`; and
6. SHA-256 the exact bytes and prepend the record-kind prefix.

Every suffix equals `sha256(canonical_bytes(record))`.
`compute_record_id(record)` equals the stored ID and
`verify_record_id(record)` is true. JSON-mode `Z` rendering is never
normative canonical content.

Canonical collection rules are:

- source ports: unique lexicographic tuple;
- sink ports: unique lexicographic tuple;
- direction pins: unique and sorted by port ID within their role field;
- evidence: existing complete canonical evidence key;
- parents: unique lexicographic FLD-ID tuple;
- effective bodies/groups: canonical private body bytes; and
- stored JSON: accepted pretty-file format over validated content plus ID.

Equivalent UTC instants and caller permutations of non-semantic sets produce
equal bytes/IDs. Reversing or repartitioning roles produces different FRG
bytes/IDs. Existing record vectors remain byte-identical.

## 12. Qualified flow kind and commodity semantics

### 12.1 Identity purpose

Flow kind is permanent because identical ports can carry logically different
declared flow kinds and PIF domain/type cannot supply that meaning. Every
FlowKindToken field participates in the semantic signature.

### 12.2 Exact nominal comparison

The kernel compares exactly:

```text
(token_kind, system_id, system_edition, code)
```

It performs no registry lookup, ontology reasoning, hierarchy, aliasing,
synonym expansion, compatibility, conversion, or edition migration.

Even an apparently descriptive code such as `water` is one indivisible
nominal token. The kernel infers no commodity, carrier, phase, material
species, quantity, unit, rate, conservation rule, interface compatibility,
behavior, or physical truth from it.

### 12.3 Authority discipline

The declaring authority is responsible for selecting and documenting the
token vocabulary. The kernel can enforce qualified exactness and evidence
closure; it cannot enforce whether a human-readable code is scientifically or
operationally appropriate.

### 12.4 Deferred semantic dimensions

Commodity, carrier, payload, phase, protocol, material species, energy form,
quantity kind, unit, and mechanism are not separate v1 fields. A future
additive design must decide whether any new dimension is identity-defining or
correctable. It must not extract one from PIF, VPA, variables, names, or an
existing token, and must not reinterpret existing FRG schema-v1 content.

## 13. Evidence, citation closure, and non-citability

### 13.1 Uniform closure first

For every evidence-bearing FRG or FLD, every `ModelRecordEvidence` reference
must identify a present, correctly typed record in the exact selected
membership. Malformed, wrong-kind, dangling, wrong-revision, and
replay-omitted references reject before role-specific claim-basis checks.

Mandatory citations add to uniform closure. Extra admitted evidence is
allowed, but every extra model citation remains closed and cannot replace a
structural pin or owner declaration.

### 13.2 FRG mandatory evidence

Every FRG requires:

1. a direct model-record citation to every exact participant PRG;
2. at least one claim-specific `OwnerDeclarationEvidence` stating that the
   opaque anchor denotes the exact role partition and FlowKindToken;
3. nonempty canonical evidence; and
4. closure for every additional reference.

It requires no PCN, PIF, PCM, VPA, variable, behavior, state, transition, or
observation citation.

### 13.3 FLD mandatory evidence

Every FLD requires:

1. a direct citation to the exact FRG;
2. a direct citation to every participant PRG;
3. a direct citation to the exact pinned PCN;
4. a direct citation to every exact pinned direction-role PIF;
5. at least one claim-specific owner declaration of the exact capability /
   pathway, context, and support-pin set;
6. declaration-parent closure; and
7. closure for every additional reference.

Direct PRG citations are intentionally redundant with FRG closure so the
participant basis remains locally auditable.

### 13.4 Meaning of evidence

The owner declaration makes the flow claim explicit. PCN/PIF citations show
exact lower-layer support and alignment; they do not create flow. PCM, VPA,
BH, state, transition, source, temporal, and structural evidence may be cited
only when honestly relevant and have no implicit flow semantics.

Internal closure does not authenticate external bytes, prove a physical
connection, or prove transfer/occurrence.

### 13.5 Evidence grammar

Add `frg` and `fld` only to `ModelRecordEvidence.record_id`. `flw_` and every
existing withdrawal prefix remain uncitable. No existing evidence union arm,
ordering rule, discriminator, or record-ID alternative changes.

## 14. Registration admission rules

### 14.1 Structural and identity admission

An FRG admits only when:

1. the record and every nested value reconstruct strictly;
2. its canonical record ID verifies;
3. its embedded FlowAnchor is valid and has no other FRG;
4. both role tuples satisfy Section 11.2;
5. every participant PRG exists and names the exact port;
6. no other FRG owns the exact semantic signature;
7. FlowKindToken is complete and valid;
8. uniform evidence closure succeeds;
9. every PRG is directly cited; and
10. claim-specific owner basis exists.

Same-owner and cross-entity signatures are both eligible. Names, hierarchy,
relationships, CAD, topology, PIF, PCM, VPA, behavior, state, transition, and
observations cannot substitute for any gate.

### 14.2 Rejections

Reject a missing/malformed port, missing PRG, empty role, duplicate,
overlap, union outside 2–64, duplicate anchor registration, duplicate exact
signature, malformed token, missing citation, missing owner basis, dangling
extra evidence, hidden semantic field, or wrong canonical ID.

Reversed roles, a different partition, or any exact token-field difference
is a different signature and may coexist under another anchor. No alternative
is inferred or synthesized.

### 14.3 RC3 — positive admission without contextual support

An otherwise valid FRG **MUST admit** when the selected membership contains:

- all exact participant PRGs;
- complete direct PRG citations;
- a claim-specific owner basis; and
- complete uniform evidence closure;

even if it contains no PCN and no PIF for any participant or union. FRG
admission performs no topology or interface lookup.

The same rule holds when matching PCN/PIF lineages exist but have no active
tips, are conflicted, or are in another context. Those facts are not FRG
admission inputs.

### 14.4 RC3 — separation of outcomes

For the admitted no-support case:

- identity lookup is `registered`;
- `flow_declaration(anchor, context=C)` is `not_declared` for every context
  without FLD roots;
- no effective-body or support row exists, so support/alignment is not
  evaluated and no support literal is fabricated;
- `flows_involving_port(port, context=C)` is `registered` with empty entries
  under Section 19 when no exact-context FLD exists; and
- nothing says possible-now, active, occurred, observed, valid, or invalid.

An FLD attempt still rejects atomically until its exact-union, exact-context
PCN and every exact role-compatible, exact-context PIF are present, valid,
cited, and reference-closed.

Unknown, malformed, wrong-kind, wrong-revision, replay-omitted, or
structurally incoherent PRG/evidence references always reject. Optional
extra PCN/PIF evidence, if supplied, is also subject to uniform closure; its
absence is not.

## 15. Declaration correction, withdrawal, corroboration, and conflict

### 15.1 FLD support admission

The exact pinned PCN must:

1. exist and verify as a `PortConnectionAssertion`;
2. have context exactly equal to the FLD context; and
3. have endpoint tuple exactly equal to the sorted FRG participant union.

A subset, proper superset, overlap-only subject, or result from
`connections_containing()` rejects. Exact-union equality prevents a larger
hyperedge from becoming invented pairwise/sub-bus topology.

Every participant has exactly one pinned PIF. It must exist and verify, name
the exact port, use the exact FLD context, declare exactly `direction_role`,
and pass:

| Flow role | Exact pinned value | Admission |
|---|---|---|
| source | `output` | admit |
| source | `bidirectional` | admit |
| source | `input` | reject |
| source | `non_directional` | reject |
| sink | `input` | admit |
| sink | `bidirectional` | admit |
| sink | `output` | reject |
| sink | `non_directional` | reject |

This strict table bounds v1 and does not infer actual flow. Domain/type PIF,
PCM, and VPA are not mandatory pins.

### 15.2 Stale support admission

A structurally valid exact PCN/PIF pin may already be superseded, withdrawn,
or in a conflicted/inactive containing lineage when a new FLD is appended.
Existence, kind, exact subject/port/context/dimension/value, integrity, and
closure are admission facts; currentness is disclosure. A current successor
never repairs or replaces an invalid exact pin.

### 15.3 Lineage key and parent rules

The exact key is:

```text
(flow_anchor_id, exact AssertionContext)
```

- `supersedes=()` creates an independent root;
- one parent is ordinary correction;
- multiple parents merge only within one derived root and exact key;
- parent order is canonical and has no priority; and
- malformed, duplicate, self, missing, cross-flow, cross-context, cyclic, or
  cross-root parentage rejects.

DAG derivation is iterative and membership-bounded.

### 15.4 Effective body

The private, non-persisted FLD effective body is exactly:

```text
flow_anchor_id
exact AssertionContext
connection_assertion_record_id
source_direction_pins
sink_direction_pins
```

It excludes record ID, evidence, authority, time, note, parents, filename,
append order, alignment, and current lower values. Different exact pins are
different bodies even when humans consider their content equivalent.

### 15.5 Root health, merge, and aggregate conclusion

| Current tips in one root | Root health |
|---:|---|
| 0 | `inactive` |
| 1 | `healthy` |
| 2+ | `conflicted` |

A same-root fork conflicts even when bodies match. A successor naming every
current fork tip in that root may converge it; partial convergence stays
conflicted. Timestamps, authority, evidence count, filenames, IDs, and append
order never choose a winner.

Across roots:

| Shape | Conclusion/finding |
|---|---|
| One healthy root/body | `declared`; `one_healthy_root` |
| Two+ healthy roots, one exact body | `declared`; `corroborating_healthy_roots` |
| Healthy roots, different bodies | `conflicted`; `cross_root_effective_body_disagreement` |
| Any same-root fork | `conflicted`; `same_root_conflict` |
| Inactive roots beside otherwise declared body | Preserve result; add `inactive_roots_present` |
| All roots inactive | `inactive` |

### 15.6 NB6 — corroborating-group support identity

Two independent healthy roots with the exact same effective body form one
effective-body group with multiple root indices, one canonical
representative, and one support-row set derived from the shared exact pins and
authoritative membership. Support rows MUST be identical across those roots.
Root-specific lineage/audit data remains in root rows.

Flow code must not derive group support from representative evidence,
authority, timestamp, or note. A different PCN/PIF pin creates another body
group and aggregate disagreement. A supplied per-root support substitution
rejects during outer reconstruction.

### 15.7 Withdrawal

FLW targets exactly one current unsuperseded FLD tip. Unknown, wrong-kind,
superseded, non-tip, already-withdrawn, and duplicate targets reject. A
successor and withdrawal of the same tip in one membership reject independent
of append order. Selective fork-tip withdrawal is allowed and recomputes root
health.

Withdrawal means only that the positive FLD is no longer asserted in the
selected membership. It does not mean flow stopped or topology disappeared.
FRG remains registered after every declaration becomes inactive.

## 16. Context isolation

### 16.1 Exact equality

FLD, pinned PCN, and every pinned PIF have exactly equal
`AssertionContext`. Context kind, lifecycle view, and union arm all matter.

- a lifecycle view matches only the identical lifecycle view;
- `view_independent` matches only `view_independent`;
- `view_independent` is never a wildcard or fallback; and
- no mapping, inheritance, default, union, or conversion exists.

Mixed arms/views reject at FLD admission. Parentage cannot cross contexts.
Roots from different contexts never corroborate, conflict, merge, or alter
one another.

### 16.2 Direct query isolation

`flow_declaration(anchor, context=C)` derives only the lineage key with exact
`C`. Other-context records may remain in carried material because material is
the complete revision, but they contribute no root, group, current index,
finding, conclusion, support row, count, or fallback.

### 16.3 Port-collection isolation (RC2)

`flows_involving_port(port, context=C)` selects entries only for incident
FRGs having at least one FLD root under exact `C`. It derives every included
entry solely from exact-`C` roots. An incident FRG with declarations only in
another context contributes no entry. If no exact-`C` declaration matches,
the registered port result has empty entries.

Declarations under every other context arm or lifecycle view are excluded
from entry membership, lifecycle computation, corroboration, conflict,
ordering, counts, findings, current indices, effective groups, support rows,
and aggregate conclusions.

V1 exposes no alternative-context summary. A future separately named summary
would require an additive query/result contract and could never be treated as
matches for `C`.

### 16.4 Context forgery rejection

Authoritative result reconstruction rejects a substituted outer context,
other-context root/group/index, appended other-context entry, lifecycle-to-
view-independent fallback, or material-derived conclusion that used another
context. Wrong discriminators, extra/private context fields, and
`model_copy`/`model_construct` context laundering reject.

## 17. Currentness, support, alignment, and staleness decision tables

### 17.1 Orthogonal axes

The public disclosure keeps separate:

1. FRG identity admission/lookup;
2. FLD lifecycle conclusion;
3. exact pinned-record activity;
4. exact pinned containing-lineage health;
5. exact-subject PCN topology conclusion;
6. current PIF direction-dimension status/relation;
7. derived pin alignment and aggregate support summary; and
8. physical occurrence, which is absent.

A `declared` FLD may have stale, conflicted, or inactive support. A conflicted
FLD remains conflicted even with current support. No axis changes another.

### 17.2 Accepted activity and health vocabulary

Reuse exactly:

```python
AssertionActivity = Literal["current", "superseded", "withdrawn"]
ContainingLineageHealth = Literal["healthy", "conflicted", "inactive"]
```

Activity derivation uses successor precedence, then withdrawal, then current.
Containing health uses 0/1/2+ current tips as inactive/healthy/conflicted.

### 17.3 One authoritative PT derivation (NB2/NB3)

PCN/PIF support facts MUST come from one shared authoritative PT payload
derivation also used by public `port_assertion()`, `connections_exact()`, and
`port_interface()` results. A private helper may be refactored to preserve
carry-once material, but flow code MUST NOT inline or maintain a parallel PT
truth table.

The exact-subject `TopologyConclusion` aggregates roots and may be `asserted`
while the pinned root is conflicted or inactive. It is not a health summary.
Every connection support row therefore discloses topology conclusion beside,
never instead of, exact pin activity and pinned containing-root health.

### 17.4 Connection alignment and RC1 reachability

```python
FlowConnectionAlignment = Literal[
    "exact_current",
    "pinned_connection_superseded",
    "pinned_connection_withdrawn",
    "connection_lineage_conflicted",
    "connection_lineage_inactive",
]
```

| Pinned lineage health | Activity | Reachable | Alignment |
|---|---|---|---|
| `healthy` | `current` | yes | `exact_current` |
| `healthy` | `superseded` | yes | `pinned_connection_superseded` |
| `healthy` | `withdrawn` | yes | `pinned_connection_withdrawn` |
| `conflicted` | `current` | yes | `connection_lineage_conflicted` |
| `conflicted` | `superseded` | yes | `connection_lineage_conflicted` |
| `conflicted` | `withdrawn` | yes | `connection_lineage_conflicted` |
| `inactive` | `current` | **no** | reject forged result |
| `inactive` | `superseded` | yes | `connection_lineage_inactive` |
| `inactive` | `withdrawn` | yes | `connection_lineage_inactive` |

Only the exact `(inactive, current)` pair is structurally unreachable: an
inactive lineage has zero active tips, while a current pin is itself an active
tip. Inactive lineage is not itself unreachable. The inactive/superseded and
inactive/withdrawn rows are mandatory positive cases.

### 17.5 Direction alignment and RC1 reachability

```python
FlowDirectionAlignment = Literal[
    "exact_current",
    "pinned_direction_superseded",
    "pinned_direction_withdrawn",
    "direction_lineage_conflicted",
    "direction_lineage_inactive",
]
```

| Pinned lineage health | Activity | Reachable | Alignment |
|---|---|---|---|
| `healthy` | `current` | yes | `exact_current` |
| `healthy` | `superseded` | yes | `pinned_direction_superseded` |
| `healthy` | `withdrawn` | yes | `pinned_direction_withdrawn` |
| `conflicted` | `current` | yes | `direction_lineage_conflicted` |
| `conflicted` | `superseded` | yes | `direction_lineage_conflicted` |
| `conflicted` | `withdrawn` | yes | `direction_lineage_conflicted` |
| `inactive` | `current` | **no** | reject forged result |
| `inactive` | `superseded` | yes | `direction_lineage_inactive` |
| `inactive` | `withdrawn` | yes | `direction_lineage_inactive` |

The same precise reachability rule applies. Outer validation rejects only the
impossible pair, never inactive health by itself.

### 17.6 Current direction relation

```python
FlowCurrentDirectionRelation = Literal[
    "consistent", "inconsistent", "indeterminate", "not_evaluated"
]
```

| Permanent flow role | Unique current PIF value/status | Relation |
|---|---|---|
| source | `output` or `bidirectional` | `consistent` |
| source | `input` | `inconsistent` |
| sink | `input` or `bidirectional` | `consistent` |
| sink | `output` | `inconsistent` |
| either | `non_directional` | `indeterminate` |
| either | no unique current direction declaration | `not_evaluated` |

This is a comparison, not flow activity. A later current PIF can make the
relation inconsistent while the FLD retains its exact older compatible pin.

### 17.7 Exact-subject topology and direction status

| Exact-subject PCN roots | Active tips | `TopologyConclusion` |
|---:|---:|---|
| 0 | 0 | `unknown` |
| 1+ | 1+ anywhere | `asserted` |
| 1+ | 0 everywhere | `inactive` |

| Port | Direction roots | Current tips | Dimension status |
|---|---:|---:|---|
| Not registered | any | any | `port_not_registered` |
| Registered | 0 | 0 | `not_declared` |
| Registered | 1+ | 1 | `declared` |
| Registered | 1+ | 2+ | `conflicted` |
| Registered | 1+ | 0 | `inactive` |

The missing-port and no-direction-root rows are impossible for an admitted
FLD support pin but remain hostile result-revalidation cases.

### 17.8 Aggregate support summary

```python
FlowSupportAlignmentSummary = Literal[
    "aligned", "stale", "conflicted", "inactive"
]
```

| Any conflict alignment | Any inactive alignment | Any stale alignment | Summary |
|---|---|---|---|
| yes | any | any | `conflicted` |
| no | yes | any | `inactive` |
| no | no | yes | `stale` |
| no | no | no | `aligned` |

Precedence is conflict, inactive, stale, aligned. Exact activities, health,
topology status, direction status, and current relation remain separately
visible. The summary is not validity, occurrence, or physical activity.

## 18. Read-only query APIs and exact result vocabularies

### 18.1 Exactly four methods

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

Queries operate over one injected immutable `LoadedModel`, own no store,
perform no write, and carry one complete `ModelQueryMaterial`. They accept no
name, entity selector, variable, source selector, cutoff, observation, rate,
current-value request, path, traversal, direction discovery, or implicit
context.

No alias or method named `current_flow`, `observed_flow`, `commanded_flow`,
`assess_flow`, `detect_flow`, `flow_history`, `flow_occurrence`, `upstream`,
`downstream`, `flow_path`, `flow_rate`, `balance`, or `conservation` exists.

### 18.2 Exact literal vocabulary

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

Reuse accepted `AssertionActivity`, `ContainingLineageHealth`, PT
`TopologyConclusion`, and interface-dimension statuses exactly. `healthy`
means one active tip in a correction lineage; it is not an asset or physical-
system health claim. No result label makes a physical flow, safety, diagnosis,
correctness, or recommendation claim.

### 18.3 FlowLookupResult field order

```text
FlowLookupResult
  material
  flow_anchor_id
  status
  registration_index
  source_port_registration_indices
  sink_port_registration_indices
```

Absent: registration is `None`; both port tuples are empty. Registered: every
index resolves to the exact FRG/PRG, preserving canonical role order.

### 18.4 Support and lifecycle row field order

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

Rows carry derived scalar labels and strict indices, never copied model
records or another material snapshot. Support is derived once from the exact
effective body, not independently per corroborating root.

### 18.5 FlowDeclarationResult field order

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

Support rows exist only in active body groups. Historical roots remain in an
inactive result. Not-registered/not-declared results have no roots/groups /
current indices as dictated by the tables below.

### 18.6 FlowAssertionDisclosureResult field order

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

Only a found FLD has activity and containing lifecycle fields. Found FRG/FLW
have those fields null/empty. Conflict is a root or flow/context conclusion,
not an individual activity.

### 18.7 Registration and declaration tables

| Exact FRG | Lookup status | Indices |
|---|---|---|
| Absent | `not_registered` | registration `None`; role tuples empty |
| Present | `registered` | exact FRG and every participant PRG |

FRG lookup is unaffected by FLD/support state.

| FRG | Exact-context roots | Active shape | Declaration conclusion |
|---|---:|---|---|
| absent | any | not evaluated | `not_registered` |
| present | 0 | not applicable | `not_declared` |
| present | 1+ | no active tips | `inactive` |
| present | 1+ | any same-root fork | `conflicted` |
| present | 2+ healthy | different bodies | `conflicted` |
| present | 1+ healthy | one active body group | `declared` |

| Conclusion | Lineage summary |
|---|---|
| `not_registered` | `not_applicable` |
| `not_declared` | `not_applicable` |
| `declared` | `healthy` |
| `conflicted` | `conflicted` |
| `inactive` | `inactive` |

### 18.8 Finding order

Findings are independently derived and emitted in this exact order:

| Condition | Finding |
|---|---|
| Exactly one healthy root | `one_healthy_root` |
| Two+ healthy roots share one body | `corroborating_healthy_roots` |
| Any same-root fork | `same_root_conflict` |
| Healthy roots contain multiple bodies | `cross_root_effective_body_disagreement` |
| Any inactive root | `inactive_roots_present` |

### 18.9 Assertion lookup/activity tables

| Valid-shaped ID | Exact record | Lookup |
|---|---|---|
| `frg_`, `fld_`, or `flw_` | absent | `not_found` |
| exact kind/ID | present | `found` |

Malformed or non-flow IDs fail typed before record-index access.

| FLD direct successors | Withdrawal | Activity |
|---:|---:|---|
| 1+ | any defensive input | `superseded` |
| 0 | 1 | `withdrawn` |
| 0 | 0 | `current` |

Successor precedence is defensive; validated membership rejects successor
plus withdrawal. Containing health is inactive/healthy/conflicted for 0/1/2+
current root tips.

### 18.10 Deterministic ordering

- material: exact lexicographic revision membership;
- source/sink PRGs and PIF rows: registered role tuple order;
- port entries: FlowAnchor ID then FRG ID defensively;
- roots: root FLD ID;
- lineage, tips, withdrawals, successors: record ID;
- body groups: canonical effective-body bytes;
- current declaration indices: body-group order then record ID; and
- findings: Section 18.8 order.

No timestamp, authority, note, append order, filesystem order, locale, or
hash iteration changes public ordering.

## 19. Complete flows_involving_port() behavior

### 19.1 Result field order

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

### 19.2 Selection algorithm

For exact requested port `P` and exact context `C`:

1. validate `P` and reconstruct `C` strictly;
2. if `P` has no PRG, return `port_not_registered`, no PRG index, and empty
   entries;
3. discover FRGs only through the immutable direct participant-port index;
4. retain only FRGs that have at least one FLD root keyed by exact `C`;
5. derive one entry per retained FRG from the same exact-`C` lifecycle helper
   as direct `flow_declaration()`;
6. assign role from the permanent disjoint FRG partition; and
7. sort entries by Section 18.10.

It performs no PCN traversal, adjacency expansion, hierarchy lookup, entity
inference, or other-context discovery.

### 19.3 Exact context-arm exclusion (RC2)

Only exact-`C` FLD roots may contribute to entry selection or contents.
Declarations under another lifecycle view or `view_independent` contribute no
entry, root, group, current index, count, finding, support row, ordering key,
corroboration, conflict, or aggregate conclusion.

If an incident FRG has only other-context FLDs, it is omitted. The query does
not emit a `not_declared` incident entry. The direct
`flow_declaration(flow_anchor_id, context=C)` query remains the way to obtain
`not_declared` for a known registered FlowAnchor.

### 19.4 Structured outcomes

| Requested port | Exact-context matching FLD roots | Status | Entries |
|---|---:|---|---|
| no PRG | any | `port_not_registered` | empty |
| registered | 0 | `registered` | empty |
| registered | 1+ across incident FRGs | `registered` | one entry per matching incident FRG |

An included entry can be `declared`, `conflicted`, or `inactive`. It cannot
be `not_registered` or `not_declared` under the selection algorithm; forged
such entries reject.

### 19.5 Direct/collection parity

For each included flow, its entry equals the direct exact-context declaration
derivation field-for-field apart from the documented wrapper, omitted outer
material/context/anchor fields, role, and entry index. Other-context records
may exist in carried complete material but are unreachable from the entry.

### 19.6 Hostile cases

Reject a result that:

- substitutes another outer context;
- adds an incident FRG whose only roots are another context;
- appends any other-context root/group/tip/finding/support row;
- lets another context change conclusion or ordering;
- treats `view_independent` as fallback/wildcard;
- discovers a nonincident flow through PCN membership; or
- returns an entry when exact-context matching-root count is zero.

No optional alternative-context summary is part of v1.

## 20. Authoritative carry-once result reconstruction

### 20.1 Material exactly once

Every outer result carries exactly one complete `ModelQueryMaterial`:

- exact `ModelRevision`;
- every selected record exactly once in lexicographic ID order;
- IDs exactly equal revision membership; and
- no second snapshot in nested rows.

Every index is `StrictInt >= 0`, non-boolean, in range, and names the required
record kind. Nested rows may carry derived scalars but refer to authoritative
records only by index.

### 20.2 Reconstruction sequence

The accepted carry-once machine is reused. Each outer result MUST:

1. inspect the supplied object graph before serialization and reject hidden
   `model_copy`/`model_construct` extras;
2. traverse iteratively under deterministic depth/node bounds and reject
   hostile cycles;
3. rebuild `ModelRevision` and every record from plain field data;
4. require strict indices and exact union arms;
5. require unique lexicographically ordered records exactly equal membership;
6. call authoritative `validate_record_collection()` over the complete set;
7. recompute and compare the revision;
8. rebuild exact contexts and rows from plain content;
9. derive the expected flow payload from the rebuilt `LoadedModel`;
10. call the shared authoritative PT support derivations from Section 17.3;
11. compare every field, index, order, lifecycle/support fact, relation, and
    alignment exactly;
12. bind private material access only after equality; and
13. perform no `ModelStore`, filesystem, database, network, environment,
    clock, cache, or write access.

No new validation machine, cached `LoadedModel` trust, partial membership, or
inline PT lifecycle implementation is permitted.

### 20.3 Mandatory forgery rejection

Reject:

- missing, duplicate, extra, reordered, mixed-revision, stale-ID, wrong-hash,
  filename/content, or wrong-union material;
- forged anchor, signature, role, context, PCN/PIF pin, topology subject,
  ownership, root, ancestry, tip, successor, withdrawal, body group,
  conclusion, finding, or support summary;
- forged activity, lower health, topology conclusion, direction status,
  current relation, or alignment precedence;
- exact `(inactive, current)` for PCN or PIF support;
- boolean, float, string, negative, out-of-range, or wrong-kind indices;
- cross-material private bindings or per-root support substitutions;
- other-context entry material and context fallback;
- hidden fields such as `flowing`, `observed`, `rate`, `occurred`, `cause`,
  `safe`, `mechanism`, `parallel_index`, or `recommended_action`; and
- hostile object cycles, excessive depth, or excessive node count.

### 20.4 Authenticity limitation

Reconstruction proves coherence of selected model material and exact result
derivation. It does not authenticate external evidence, identify a physical
connection/mechanism, count physical mechanisms, or prove flow occurred.

## 21. Store validation and immutable indexes

### 21.1 Public append sequence

`ModelStore.append(record)` retains this order:

1. reconstruct and revalidate supplied/nested field data;
2. verify ID against normative canonical bytes;
3. load and validate complete current membership;
4. return exact equal-record re-append as a validated idempotent no-op;
5. reject same ID with different content as typed integrity failure;
6. form prospective membership;
7. run complete prospective `validate_record_collection()`;
8. serialize accepted stored JSON from validated content plus ID; and
9. atomically promote one file.

Every failure leaves no durable partial file.

### 21.2 Full-set validation order

After existing entity/PT families are authoritatively rebuilt:

1. partition exact FRG/FLD/FLW discriminators;
2. validate FRG anchor/signature uniqueness, role sets/bounds, PRGs, token,
   uniform closure, mandatory citations, and owner basis without PCN/PIF
   lookup;
3. validate FLD FRG, exact context, exact-union PCN, complete exact PIF pins,
   role table, closure, citations, owner basis, and parent shapes;
4. build exact-key DAGs and reject cycles/cross-root convergence;
5. validate FLW against one current unsuperseded tip and reject duplicates;
6. reject successor/withdrawal race independent of append order;
7. derive immutable deterministic indexes and effective bodies; and
8. compute existing `mrv_` over exact sorted membership.

Earlier structural/hash/union/closure failures remain typed and are not
masked by flow semantics.

### 21.3 Immutable indexes

At minimum:

- FRG by FlowAnchor ID;
- FlowAnchor ID by exact semantic signature;
- FlowAnchor IDs by participant PortAnchor ID;
- FLD IDs by `(FlowAnchor ID, exact context)`;
- FLD parents, successors, roots, ancestry, current tips;
- FLW IDs by target;
- effective bodies/groups; and
- role by `(FlowAnchor ID, PortAnchor ID)`.

Every mapping/nested collection is immutable and sorted. Reversed input,
copy, append, and hash iteration order yield identical indexes and revision.

### 21.4 Ledger ownership

FRG/FLD/FLW join the existing model record union, `ModelStore`, replay, and
`mrv_`. No flow ledger, database, cache, projection, persisted result, or
second revision is introduced. Slices A/B keep the authoritative model at 34
records.

## 22. Import-direction and ownership rules

### 22.1 Ownership

| Concern | Owner |
|---|---|
| FlowAnchor/pattern/minter | `backend.system_identity` |
| FlowKindToken, pins, FRG/FLD/FLW | `backend.model_kernel` |
| Generic builder/canonical identity | `backend.model_kernel` |
| Admission/lifecycle/indexes/replay | `backend.model_kernel.store` |
| Flow query/results | `backend.model_kernel` |
| Shared PCN/PIF derivation | existing model-kernel PT helpers |
| Observations/temporal projection | existing packages, unchanged |
| BH/ST evaluation | existing upper packages, unchanged |
| Future assessment/occurrence | later upper layer, absent |

### 22.2 Permitted direction

```text
backend.system_identity
          ^
backend.model_kernel  (PT and FL records/results are peers)
          ^
future separately approved flow composition/assessment/occurrence
```

The layer above may depend on the layer below. Reusing one same-kernel PT
helper does not reverse the dependency.

### 22.3 Prohibitions

- system identity never imports model kernel;
- model kernel never imports model state, semantic compatibility, constraint /
  behavior/state evaluation, binding/interpretation/temporal/source/ingestion,
  structural/CAD/PDF, sockets, environment, filesystem paths, or clocks for
  flow derivation;
- `ModelQueries` owns no store and persists nothing;
- no lower layer imports a future flow layer; and
- result validation obtains no ambient repository, cache, database, network,
  clock, or write authority.

Architecture tests pin imports and absence of evaluation/occurrence APIs.

## 23. Historical replay and pre-FL structured absence

### 23.1 Replay semantics

All lifecycle, activity, and alignment is relative to exact selected,
reference-closed membership. Omitting a successor or withdrawal can revive an
older declaration/support assertion. Replay never ranks by timestamp,
filename, ID, directory order, or append order.

An FLD replays only with exact FRG, PCN, every PIF, parent, and evidence
dependency. Omitting any rejects. Later support corrections never mutate old
canonical bytes.

### 23.2 Historical obligations

Replay exact accepted 9, 10, 11, 14, 16, 18, 28, 29, 32, and 34 record
memberships. Prove exact historical revisions/membership, predecessor bytes,
reference closure, immutable empty flow indexes, and—after Slice B—structured
flow absence.

### 23.3 Authoritative 34-record absence

Against the untouched accepted 34-record model:

| Query | Exact structured behavior |
|---|---|
| `flow(valid-shaped absent flo ID)` | `not_registered`; no indices |
| `flow_declaration(absent flo ID, context=C)` | `not_registered`; `not_applicable`; no roots/groups/current indices |
| `flows_involving_port(existing PRG port, context=C)` | `registered`; exact PRG index; empty entries |
| `flows_involving_port(valid absent port, context=C)` | `port_not_registered`; no PRG index; empty entries |
| `flow_assertion(valid-shaped absent frg/fld/flw ID)` | `not_found`; no record/lifecycle indices |

Valid-shaped absent sentinels are test inputs, not minted/frozen identities.
Each result carries the exact 34-record material once. Existing PCN/PIF/PCM,
VPA, BH, ST, or other facts never fabricate an FL result.

### 23.4 Preservation

Before/after every slice, preserve:

- exact 34 records and accepted revision;
- zero transition and zero flow records;
- every authoritative record byte;
- every binding, interpretation, temporal, source, structural, PT, VP, BH,
  and ST fixture; and
- every accepted PT/VP/BH/ST artifact byte and hash.

Use an exact inventory and aggregate hash, not a count alone.

## 24. Temporal, observed-flow, and occurrence boundary

### 24.1 Why declaration-only is mandatory

Current contracts cannot support flow evaluation or occurrence:

1. `TemporalOccurrence` is a point observation occurrence, not flow, and
   proves no persistence.
2. Temporal `changed` is exact reported-value difference in acquisition
   order, not start/stop/rate/cause.
3. Receipt and source-native times provide no shared physical time axis.
4. Model-state selection creates no validity interval or sensor fusion.
5. VPA does not relocate an observation to a port or prove origin,
   destination, or travel.
6. BH cohort/equality provides no direction, signed sum, storage term,
   uncertainty, boundary completeness, transfer, or conservation.
7. ST selects conditions independently and asserts no temporal alignment.
8. ST-002 declares transition possibility, not an occurrence.
9. Gaps, failures, omissions, repeated points, and close timestamps prove no
   continuity.
10. Carry-once reconstruction proves coherence, not physical authenticity.

### 24.2 Strongest permitted statements

| Facts | Strongest permitted statement |
|---|---|
| FRG only | Registered logical identity |
| FRG + admitted FLD | Explicit revision/context-relative declared capability/pathway |
| PCN + PIF | Common membership and interface-role claims only |
| VPA + observation | Separate association and variable observation; not value-at-port |
| PCM compatible | Compatibility claim only |
| rate-like numeric point | Reported value for one variable/locator, not FlowAnchor measurement |
| `changed`/`unchanged` | Sampled value comparison only |
| BH same-cohort/equal | Same acquisition envelope and exact equality only |
| ordered ST matches | Evidence-relative classifications only |
| no/failed/empty/stale evidence | Coverage/absence/staleness only, never zero/current flow |

### 24.3 Later assessment prerequisites

Any later assessment requires a separately approved:

- flow-to-measurement/boundary attachment with exact variables, locus, roles,
  FLD/VPA pins, lifecycle, and evidence;
- quantity kind, unit, sign/orientation, polarity, and direct/derived-rate
  semantics;
- authoritative time axis/window, source alignment, skew/cohort, gap,
  freshness, coverage, persistence, interpolation, and late-evidence rules;
- immutable temporal selection/snapshot digest;
- explicit evaluation family and deterministic refusal/coverage vocabulary;
  and
- upper-layer carry-once composition over public lower facades.

Derived rates additionally need interval endpoints, arithmetic, decimals,
dimensional algebra, and zero/missing rules.

### 24.4 Conservation, occurrence, and causality prerequisites

Conservation additionally requires a control-volume/boundary identity,
boundary completeness, signed aggregation, compatible units/conversion,
storage term, integration window, tolerance/uncertainty, missing-branch
policy, and co-temporal measurements.

Occurrence requires a separate accountable occurrence identity/record,
exact FlowAnchor/FLD/source-occurrence pins, time/window basis, provenance,
evidence, lifecycle, replay, and authenticity boundary. Evaluators never
auto-append occurrences. Detection further requires thresholds, dwell,
debounce, hysteresis, persistence, gaps, late evidence, and bounded history.

Causality requires an explicit causal/mechanism/intervention model and its
assumptions. Topology, direction, equality, state, flow declaration, temporal
order, correlation, change, or cohort never proves cause.

## 25. Threat model

### 25.1 Protected properties

Protect opaque identity, exact semantic-signature uniqueness, source/sink
partition, nominal token identity, exact non-retargeted support pins, evidence
closure, canonical IDs, `mrv_`, lifecycle/replay, exact context isolation,
carry-once disclosure, and the declaration/physical-truth boundary.

### 25.2 Adversary capabilities

Assume hostile callers can supply malformed or fabricated IDs; nested/private
Pydantic forgeries; reordered/omitted/mixed membership; corrupted JSON;
dangling/wrong-revision evidence; PCN subsets/supersets; wrong PIF
ports/contexts/dimensions/roles; current records intended to retarget old
pins; PCN roots intended as physical connections; timestamps/names intended
as winner selectors; other-context declarations intended to leak into a
collection; forged indices/status/alignment/private bindings; deep/cyclic
objects; and PT/VP/BH/ST/temporal facts intended to launder flow/occurrence /
conservation/causality.

### 25.3 Principal attacks and defenses

| Attack | Mandatory defense |
|---|---|
| Name-derived anchor | UUID4 opaque minter; names never match |
| Partition swap hidden by sorting | Sort each role separately; preserve role fields |
| Duplicate same signature | Exact FRG signature uniqueness |
| Duplicate anchor implies parallel mechanism | Reject; v1 asserts no mechanism count |
| PCN root treated as connection | Roots remain evidence lineages only |
| PCN superset creates sub-flow | Exact participant-union equality; no containing lookup |
| PCN/PIF creates flow | Explicit FRG, FLD, and claim-specific owner evidence |
| Wrong/non-directional PIF supports role | Exact role table rejects |
| Latest support silently substitutes | Exact pins plus activity/health/alignment; no retarget |
| Active PCN root hides pinned failure | Topology conclusion and pin health shown separately |
| Support state changes FLD lifecycle | Orthogonal state machines and parity tests |
| Other context widens port query | Exact-context entry selection and forged-result rejection |
| Hyperedge becomes pairwise graph | One group result; no branch/traversal APIs |
| Bidirectional PIF creates reverse | Separate FlowAnchor required |
| Dynamic bus chooses speaker | Explicit future arbitration contract only |
| VPA + observation becomes observed flow | No flow-measurement attachment/evaluator |
| BH equality becomes conservation | No balance evaluator; prerequisites explicit |
| Change/order becomes occurrence/cause | No detection/occurrence/causal APIs |
| `recorded_at` becomes event time | Audit metadata only; no cutoff query |
| Timestamp/authority ranks tips | Membership DAG only |
| Forged carry-once result | Rebuild complete membership and expected payload |
| Deep/cyclic payload exhausts validator | Bounded iterative inspection |
| Failed append leaves record | Prospective validation and atomic one-file promotion |

### 25.4 Residual boundary

The kernel does not authenticate human authority, digital signatures, source
systems, external raw bytes, or physical assets. It prevents semantic
escalation within selected model material; it does not prove external claims
true.

## 26. Corrected adversarial acceptance matrix

Every row becomes executable only in its separately authorized slice.
“Reject” means deterministic typed failure before any durable partial write or
trusted result.

### 26.1 Identity, schema, and canonical integrity

| ID | Slice | Acceptance row |
|---|---|---|
| I01 | A | Malformed, uppercase, wrong-length/prefix, non-hex `flo_` rejects. |
| I02 | A | Anchor/token/record hidden extras and nested private-state forgeries reject. |
| I03 | A | Equal names do not merge; different names do not split/select. |
| I04 | A | Empty role, union <2/>64, duplicate, overlap, malformed port rejects. |
| I05 | A | Within-role permutations yield identical tuples/bytes/IDs. |
| I06 | A | Role reversal/repartition changes FRG bytes/ID. |
| I07 | A | Second exact signature rejects; different token/reverse/partition coexists. |
| I08 | A | All four token fields compare exactly; no equivalence inferred. |
| I09 | A | Evidence/parent/pin permutations canonicalize; duplicates reject. |
| I10 | A | Equivalent instants canonicalize with `+00:00`, never normative `Z`. |
| I11 | A | ID suffix, canonical SHA-256, compute, and verify agree for each flow record. |
| I12 | A | Literal golden canonical/stored bytes, counts, IDs, hashes pin FRG/FLD/FLW. |
| I13 | A | Every existing canonical vector and stored byte remains unchanged. |
| I14 | A | Equal re-append is validated no-op; same-ID/different-content rejects. |
| I15 | A | Wrong discriminator/prefix/filename and corrupted sibling reject. |

### 26.2 Registration, support, context, and evidence

| ID | Slice | Acceptance row |
|---|---|---|
| R01 | A | Missing participant PRG or replay-omitted dependency rejects. |
| R02 | A | Same-owner/cross-entity signatures follow identical explicit rules. |
| R03 | A | FLD missing FRG/PCN/PIF/parent/evidence member rejects atomically. |
| R04 | A | PCN subset/superset/different union/overlap/wrong context rejects. |
| R05 | A | `connections_containing()` cannot satisfy exact PCN admission. |
| R06 | A | PIF missing/extra/duplicate/wrong port/dimension/context rejects. |
| R07 | A | Source input/non-directional and sink output/non-directional pins reject. |
| R08 | A | Source output/bidirectional and sink input/bidirectional pins admit. |
| R09 | A | Valid already-superseded/withdrawn PCN pin admits without retargeting. |
| R10 | A | Valid already-superseded/withdrawn PIF pin admits without retargeting. |
| R11 | A | Current replacement never repairs an invalid exact stale pin. |
| R12 | A | All-lifecycle and all-view-independent positive cases admit exactly. |
| R13 | A | Context kind/view/union-arm substitution rejects. |
| R14 | A | FRG PRG citations and owner basis are independently mandatory. |
| R15 | A | FLD FRG/PRG/PCN/PIF citations and owner basis are independently mandatory. |
| R16 | A | Every extra model citation remains uniformly reference-closed. |
| R17 | A | FRG/FLD citable; FLW/all withdrawals uncitable. |
| R18 | A/B | Existing PT/VP/BH/ST/transition/observation facts cannot create FRG/FLD. |
| R19 | A/B | PCN/PIF correction/withdrawal never auto-writes or retargets FLD. |
| R20 | A | Every failed prospective append leaves bytes unchanged. |
| R21 | A | Valid FRG with all PRGs/citations/owner basis/closure admits with zero PCN/PIF; lookup registered, declaration not-declared, no support rows/occurrence. |

### 26.3 Lifecycle, withdrawal, and replay

| ID | Slice | Acceptance row |
|---|---|---|
| L01 | A | Parent wrong-prefix/missing/self/duplicate/cross-anchor/context/cycle rejects. |
| L02 | A | Parent tuple crossing independent roots rejects. |
| L03 | A | One root/one tip is healthy. |
| L04 | A | Same-root fork conflicts even with equal bodies. |
| L05 | A | Partial convergence remains conflicted. |
| L06 | A | Complete same-root all-tip merge restores one healthy tip. |
| L07 | A | Identical healthy independent bodies corroborate without root merge. |
| L08 | A | Any different exact PCN/PIF pin yields body disagreement. |
| L09 | A | Selective current fork-tip withdrawal recomputes health. |
| L10 | A | Unknown/superseded/non-tip/wrong-kind/duplicate withdrawal rejects. |
| L11 | A | Successor plus withdrawal of same tip rejects independent of order. |
| L12 | A | All roots withdrawn gives inactive; FRG stays registered. |
| L13 | A | Replay omission of successor/withdrawal revives older state. |
| L14 | A | Replay keeping FLD but omitting any dependency rejects. |
| L15 | A | Deep valid DAG loads iteratively without recursion dependence. |
| L16 | A/B | Time/authority/ID/filename/input/append order never selects winner. |

### 26.4 Queries, RC1, RC2, and authoritative reconstruction

| ID | Slice | Acceptance row |
|---|---|---|
| Q01 | B | Exactly four signatures/exports exist; forbidden aliases absent. |
| Q02 | B | Malformed IDs/context fail typed; valid absence is structured. |
| Q03 | B | FRG lookup stays registered across every declaration/support state. |
| Q04 | B | Every conclusion/summary/finding follows Sections 18–19. |
| Q05 | B | Merge/corroboration/disagreement/withdrawal/revival disclose exactly. |
| Q06 | B | PCN activity/health/topology equals shared authoritative PT derivation. |
| Q07 | B | PIF activity/health/dimension equals shared authoritative PT derivation. |
| Q08 | B | For PCN and PIF independently, all eight reachable health×activity pairs admit with exact alignment; inactive/superseded and inactive/withdrawn are positive; forged inactive/current rejects. |
| Q09 | B | Current PIF correction yields exact relation without changing FLD conclusion. |
| Q10 | B | Active other PCN root cannot hide pinned conflict/inactivity/staleness. |
| Q11 | B | Summary precedence conflict>inactive>stale>aligned never changes lifecycle. |
| Q12 | B | Every included port entry equals direct exact-context derivation. |
| Q13 | B | Port collection selects exact-context matching roots only; other contexts contribute nothing. |
| Q14 | B | Assertion disclosure covers FRG/FLD/FLW/absence and activity precedence. |
| Q15 | B | One complete material carried once; nested record references strict indices. |
| Q16 | B | Missing/duplicate/extra/reordered/mixed/stale/wrong-union material rejects. |
| Q17 | B | Forged lifecycle/body/support/relation/index/order/context/precedence rejects. |
| Q18 | B | Bool/float/string/negative/out-of-range/wrong-record indices reject. |
| Q19 | B | Hidden/private/model-copy/construct/cross-material laundering rejects. |
| Q20 | B | Hostile cycles/depth/node count reject deterministically. |
| Q21 | B | Plain round-trip reconstructs without store/filesystem/network/env/clock. |
| Q22 | B | No result/API claims physical activity/rate/occurrence/conservation/cause/action. |
| Q23 | B | Incident FRG with FLDs only in another context is omitted; registered port returns empty entries; forged other-context entry/root/group/finding rejects. |
| Q24 | B | Lifecycle and view-independent arms each return only their own roots; changing requested/result context rejects rather than widening. |
| Q25 | B | Corroborating roots with one body have one identical support-row set; per-root substitution rejects; changed pin splits groups/disagrees. |

### 26.5 Hyperedge, parallel mechanism, and non-inference

| ID | Slice | Acceptance row |
|---|---|---|
| N01 | A/B | Many-to-many FRG remains one group and yields no pairwise result. |
| N02 | B | Incident query never traverses PCN/another FlowAnchor. |
| N03 | A/B | Reversed signature coexists and is never synthesized by bidirectional PIF. |
| N04 | A/B | Overlap/cycles imply no path/exclusivity/capacity/priority/cause. |
| N05 | B | VPA plus observation cannot become value-at-port/observed flow. |
| N06 | B | PIF plus PCN cannot create identity/declaration. |
| N07 | B | PCM compatibility cannot create possible/current/observed flow. |
| N08 | B | BH same-cohort equal cannot become transfer/conservation. |
| N09 | B | BH same-cohort different cannot become leak/fault/loss. |
| N10 | B | Changed/zero-to-positive/ordered ST matches cannot create occurrence. |
| N11 | B | Repeated unchanged cannot create continuity/dwell/persistence. |
| N12 | B | Source/receipt proximity cannot create simultaneity/causality. |
| N13 | B | Empty/failed/quarantined/omitted/stale cannot become zero/current flow. |
| N14 | B | Rate-like variable cannot attach without future measurement contract. |
| N15 | B | PCN hyperedge cannot become closed control volume/complete boundary. |
| N16 | B | `recorded_at` is not event time; `mrv_` is not temporal cutoff. |
| N17 | A/B | Dynamic arbitration/speaker selection cannot be encoded by bidirectional PIF or corrections. |
| N18 | A | Second FRG for identical signature rejects regardless of claimed physical mechanism; no mechanism-count field exists. |
| N19 | A/B | Independent FLD/PCN roots remain evidence claims, never parallel mechanisms. |
| N20 | A/B | Human-readable FlowKindToken never yields decomposed physical semantics. |

### 26.6 Preservation and deterministic reproduction

| ID | Slice | Acceptance row |
|---|---|---|
| P01 | A/B | Authoritative model stays exact 34/revision with zero flow records. |
| P02 | A/B | Historical 9/10/11/14/16/18/28/29/32/34 replay unchanged. |
| P03 | A/B | Every predecessor byte and accepted PT/VP/BH/ST artifact hash unchanged. |
| P04 | A/B | No hidden flow fields added to existing contracts/fixtures. |
| P05 | A/B | Reversed input/copy/append and hash seeds preserve bytes/indexes/results. |
| P06 | B | Two independent disposable roots reproduce without copying generated records. |
| P07 | B | Working/base-only/all-extras columns yield byte-identical reproduction. |
| P08 | A/B | Full repository, compilation, OCP/STEP, PDF, permitted loopback remain green. |
| P09 | A/B | Working/milestone whitespace and exact status/topology checks pass. |
| P10 | A/B | No authoritative identity mint/record append without separate D gates. |

## 27. Deterministic ordering and canonical integrity

### 27.1 Red-first obligation

Each authorized implementation slice begins with focused failures for the
absent contract, then the narrow implementation and fixed-after proof. Every
genuine hardening defect records failing-before/fixed-after evidence.

### 27.2 Reproduction columns

Disposable positive worlds use at least two independently initialized roots
from byte-identical explicit predecessor membership; one reverses predecessor
copy/input order. Each independently constructs through public identity,
`build_record`, and `ModelStore`; candidate files are never copied between
roots.

Compare anchor serialization, canonical/stored bytes, IDs/hashes, semantic
append order, membership/revision, immutable indexes, all query bytes,
predecessor aggregate, and protected artifact hashes.

Repeat at accepted implementation HEAD in working, fresh base-only, and fresh
all-extras checkouts under multiple hash seeds. Locale, timezone spelling,
clock, directory order, and hash iteration have no effect.

### 27.3 Verification tiers

Focused suites separate anchor/minter, record/canonical contracts, store /
lifecycle, hostile record reconstruction, evidence/architecture preservation,
query conclusions/PT parity, result revalidation, context isolation, RC1
reachability, and deterministic reproduction.

Affected suites include identity, complete model kernel, model state,
constraint/behavior/state classification, and all serialization paths for
`ModelRecord`/`ModelQueryMaterial`. Then run the full repository, backend
compilation, base-only/all-extras suites, focused OCP/STEP and PDF paths, and
the loopback test separately if sandbox-denied.

Working-tree and full milestone-range `git diff --check`, exact status,
topology, and no-push/no-merge checks are mandatory.

## 28. Demonstration policy and pre-append owner gate

### 28.1 Default authoritative policy

The authoritative demo ledger remains 34 records throughout Slices A/B and
any later separately proposed non-demo Slice C. Positive tests use disposable
synthetic worlds. Design approval and implementation approval do not authorize
minting/freezing an authoritative FlowAnchor or changing
`models/demo-printer`.

### 28.2 Conditional eligibility of current PT material (NB8)

The current synthetic demo's two PRGs, exact-union PCN, and complementary
same-context direction PIFs are eligible lower-layer support for a *possible*
future declaration candidate. They do not supply:

- a FlowAnchor or FlowKindToken;
- a flow owner claim, FRG, or FLD;
- observation, calculation, occurrence, or physical-flow evidence;
- candidate identity, append authorization, or final acceptance.

Their bytes/hashes remain protected. PT facts support future admission only
when a separately authorized synthetic owner claim and all final gates exist.

### 28.3 Mandatory pre-append rehearsal gate

Slice D does not exist until separately proposed. Its first possible
authorization is **pre-append rehearsal only**, requiring:

1. no pre-existing candidate manifest;
2. exact freeze of authoritative predecessor membership/bytes and protected
   artifact hashes;
3. one public minter invocation, immediately persisted and never repeated for
   that candidate;
4. independent reconstruction from frozen semantic content in at least two
   disposable roots;
5. public `build_record` and `ModelStore` only;
6. canonical bytes/ID suffix/stored bytes/revision/query equality;
7. directly byte-identical artifacts across reproduction columns;
8. unchanged authoritative ledger during rehearsal; and
9. an owner question approving the exact frozen contract and separately
   requesting authoritative append authority.

Rehearsal approval is not append approval. A second explicit authorization is
required for exact authoritative append, followed by another final owner
acceptance gate. This specification invents no candidate anchor, record ID,
timestamp, membership, revision, artifact byte count, or hash.

### 28.4 Mandatory synthetic disclaimer

Any later candidate/accepted artifact must include at least:

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

It must also state that names, ownership, hierarchy, geometry, contact, CAD,
proximity, PCN, PIF, PCM, VPA, BH, ST, transition declarations,
observations, correlations, cohorts, and value changes did not create the
flow. Displaying an observation beside a flow does not attach or persist it as
flow truth.

## 29. Owner-gated implementation slices

Every slice requires separate authorization and later owner acceptance. This
section is a plan, not authority.

### 29.1 Slice A — identity, records, canonicalization, store, replay, indexes

Scope if separately authorized:

- FlowAnchor pattern/export and pure minter;
- FlowKindToken, direction pin, FRG/FLD/FLW contracts;
- generic builder/union/prefix/filename/evidence/canonical integration;
- literal golden vectors and existing-vector preservation;
- FRG/FLD/FLW store admission, including RC3;
- exact support/context rules, lifecycle DAG, withdrawals, replay, immutable
  indexes, and `mrv_` integration;
- applicable I/R/L/N/P acceptance rows; and
- focused, affected, full, compilation, preservation, and clean-checkout
  verification.

Not included: public flow queries/results, cross-layer composition, fixture,
authoritative identity/record, assessment, occurrence, or ConnectionAnchor.
It ends at an owner validation gate with a filesystem completion report.

### 29.2 Slice B — read-only queries, disclosure, carry-once, hardening

Scope if separately authorized after Slice A acceptance:

- exactly four public queries and result contracts;
- lifecycle/support/alignment disclosure and shared PT derivation;
- complete RC1 reachability and RC2 context isolation;
- carry-once authoritative reconstruction;
- complete query/adversarial/non-inference matrix;
- disposable positive hyperedge/lifecycle worlds;
- deterministic independent-root and clean-checkout reproduction;
- authoritative 34-record structured absence; and
- full historical/artifact preservation and repository verification.

Not included: cross-layer value composition, source/cutoff, assessment,
occurrence, traversal, fixture, or ledger append. It ends at an owner gate.

### 29.3 Slice C — no v1 slice proposed

No permitted cross-layer read-only composition is necessary to meet FL-001's
declaration-only objective. The kernel already discloses every approved fact.
Therefore Slice C is absent, not implicitly authorized or reserved work.

If a later design demonstrates a necessary read-only composition, it must be
separately proposed and owner-gated as an upper layer, preserve kernel import
independence, compose only public lower facades, add no occurrence/evaluation
claim without its missing contracts, and receive its own acceptance matrix.

### 29.4 Slice D — optional bounded synthetic demonstration

Slice D is nonexistent unless separately proposed after A/B acceptance (and
any later C, if one is ever approved). It begins only with Section 28.3
rehearsal authorization, stops for exact candidate approval, then requires
separate append authorization and final acceptance. It may demonstrate
identity/declaration/read-only disclosure only.

## 30. Explicit exclusions and future milestones

### 30.1 V1 exclusions

FL-001 provides no:

- connection/path/channel/conduit/bus/mechanism identity;
- parallel same-signature mechanism distinction or mechanism cardinality;
- endpoint-changing continuity;
- inferred flow from PCN/PIF/PCM/VPA/BH/ST/transition/observation;
- dynamic roles/arbitration, neutral participants, same-port flows, route or
  path composition;
- payload/variable/measurement attachment, observation-at-port, rate,
  quantity, unit, duration, persistence, continuity, or history;
- command/control/target/action/effect/state-machine behavior;
- simulator/evaluator/detector/estimator/optimizer;
- conservation/balance/completeness/capacity/contention/loss/efficiency;
- transition or flow occurrence generation; or
- cause/influence/safety/health/diagnosis/correctness/validity/recommendation.

### 30.2 Accepted limitations

- identity is an abstract kind-qualified role partition, not a physical
  mechanism;
- one exact signature has one logical identity and says nothing about number
  of physical mechanisms;
- parallel/replaced same-signature mechanisms cannot be distinguished;
- non-directional/opposite PIF roles cannot support a v1 directed FLD;
- containing-bus PCN cannot support a subset flow without an exact-union PCN;
- dynamic arbitration cannot be represented;
- FlowKindToken is nominal/opaque;
- different exact support-pin bodies disagree even if humanly equivalent;
- contexts cannot map/widen/fallback;
- declaration currentness is model-membership-relative, not physical; and
- result coherence does not authenticate evidence or physical truth.

### 30.3 Future owner-gated milestones

Additive future work may introduce:

- evidence-backed connection/path/mechanism identity for parallel/replaced
  physical mechanisms;
- explicit arbitration/dynamic-role declarations;
- separately queryable commodity/carrier/payload/protocol dimensions;
- flow-to-measurement/boundary associations;
- temporal cohort/continuity/window contracts;
- rate/amount/occurrence assertion planes;
- control-volume/conservation declaration/evaluation;
- command/control planes; or
- causal-model claims.

Each needs its own design, evidence/lifecycle, import boundary, result truth
boundary, adversarial matrix, and owner gates. It creates new identities /
records where required and MUST NOT reinterpret `flo_`, change FRG schema-v1
meaning, retarget FLD pins, promote PCN roots, alter historical revisions, or
add hidden flow fields to PT/VP/BH/ST/ST-002 records.

## 31. Final owner-decision register

All nine lead-proposal questions are resolved. None remains implementation-
blocking or open.

| ID | Final owner decision | Consequence |
|---|---|---|
| D1 | Adopt durable logical, kind-qualified directed FlowAnchor; no ConnectionAnchor. | Cannot name a physical connection/mechanism. |
| D2 | Permanent identity is exact canonical source set, sink set, and complete FlowKindToken. | Any role/participant/token change requires new anchor. |
| D3 | Support 1→1, fan-out, fan-in, and many-to-many as one non-pairwise hyperedge. | No pairwise, routing, mixing, broadcast, or conservation inference. |
| D4 | Require one exact-union PCN and one exact compatible direction PIF per participant. | Non-directional/opposite support is refused in v1. |
| D5 | Permit at most one FRG per exact signature; do not represent parallel same-signature mechanisms. | No claim that only one physical mechanism exists; future distinction is additive and owner-gated. |
| D6 | Permit same-owner and cross-entity port sets; no single subject entity. | Ownership is disclosed from PRGs only; hierarchy never creates flow. |
| D7 | Accept both exact context arms, stale exact pins, no retargeting, orthogonal support/lifecycle. | RC1 matrices and RC2 collection isolation are binding. |
| D8 | Accept `flo_`/`frg_`/`fld_`/`flw_` and exactly four query names/result vocabulary. | No aliases or assessment/occurrence APIs. |
| D9 | Keep authoritative ledger at 34 through A/B; demo PT material is only a later candidate prerequisite. | No identity mint, fixture, or append without Section 28 gates. |

**Unresolved owner-question count: 0.**

This final synthesis preserves the existing model ledger and `mrv_`, keeps
FL-001 declaration-only, separates every lower-layer concept from flow, and
does not authorize implementation.

END OF FL-001 FINAL SYNTHESIS
