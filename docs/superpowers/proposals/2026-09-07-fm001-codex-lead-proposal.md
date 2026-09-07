# FM-001 — Explicit Flow-to-Measurement Association

Lead architecture proposal — design only

## 1. Repository findings and exact baseline

This proposal is based on `main` at
`a069cb664af1638cef2168ced6034eb2d30f2f14`, the accepted post-TA-001
architecture/ADR reconciliation. `origin/main` remained at the preceding
accepted checkpoint `25b7cacb5aacc456d8d3507d5b76940772d94cda` when inspected;
no fetch or push was performed. The working tree was clean apart from ignored
owner-local state.

The reconciliation report is
`docs/superpowers/reports/2026-09-07-post-ta001-architecture-and-adr-reconciliation-report.md`,
SHA-256 `c07bd4311d4dbe0345fd877d41a6b9cc7005396dc2c09fd6e2dca85beb09a2fa`.
ADRs are exactly 0001–0020, contiguous and unique; ADR-0020 is the latest
accepted decision and ADR-0021 does not exist.

The accepted current model remains 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`,
with FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, and ledger aggregate
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The protected FL disclosure is 660,516 bytes with SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
TA-001 is accepted at tested implementation
`2ec18f7234273dba98098d268df4568d5cc84d85`; its deterministic result is
195,429 bytes with SHA-256
`1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`.

No code, test, fixture, ledger, identity, record, branch, ADR, or artifact is
created by this proposal.

## 2. Problem statement and missing-bridge proof

FM-001 asks for the smallest explicit, evidence-bearing, replayable contract
that can state:

> This existing model variable is declared to represent a specified
> measurement or measurement-related role for this existing logical flow at
> this exact declared locus and context.

The accepted repository contains each endpoint of this desired bridge, but no
accepted object contains the complete relation:

- FL-001 `FlowAnchor` and FRG/FLD records identify a logical directed
  port-group relation, nominal flow kind, exact context, and pinned PCN/PIF
  support. They do not name a variable or a measurement role.
- VM/VS/ES records identify variables and their value-shape, semantic,
  quantity, role, and unit declarations. They do not identify a flow or
  participant locus.
- VP-001 `VariablePortAssociation` relates one variable to one same-owner
  port in a context. Its accepted contract explicitly says nothing about
  observation location, transport, flow, or measurement.
- EA-001 and evidence alignment bind selected evidence to a variable-value
  compatibility result. They carry no flow meaning and do not materialize
  model declarations.
- PT/PIF/PCN/PCM records identify ports, interfaces, and topology claims. They
  do not identify measurement relevance.

Search of model records, canonical union, store indexes, queries, exports,
fixtures, and read-only result contracts found no record or result jointly
carrying exact flow identity, exact variable identity, participant locus,
flow-relative role, value relationship, orientation/sign semantics, quantity or
unit expectation, context, lifecycle, evidence closure, replay, and
provenance. Names, shared owners, matching units, topology, port direction,
observation correlation, and value changes are explicitly not substitutes.

Therefore the bridge is genuinely absent. An FA-001 evaluator without FM-001
would have to infer measurement relevance from exactly those forbidden clues.

## 3. Strongest permitted claim and non-claims

The proposed FM-001 declaration would establish only that a selected model
membership contains an evidence-bearing declaration relating an existing flow
to an existing variable at an explicitly declared locus and context, under an
explicit role/orientation/value-semantics vocabulary.

It would not establish:

- an observation at the port or flow boundary;
- a physical sensor, device, channel, connection, path, or control volume;
- a value, rate, amount, command effect, or measurement result;
- that anything flowed, occurred, persisted, was continuous, or was current;
- conservation, balance, causality, influence, correctness, safety, health,
  diagnosis, recommendation, or control;
- semantic convertibility or dimensional algebra merely because tokens match;
- an accountable occurrence history or an FA-001 assessment.

The declaration is model knowledge. Any later assessment is a separate,
read-only upper composition over carried FM facts and independently supplied
evidence.

## 4. Alternatives and recommendation

### A — Model-ledger association record, no new anchor

Add an evidence-bearing, correctable relation over existing FlowAnchor,
VariableAnchor, exact participant locus, context, and bounded body dimensions.
The record lineage is the identity of the assertion; no durable association
anchor is introduced. This is the smallest additive option and follows the
kernel's existing declaration/correction/replay machinery.

### B — Durable association anchor plus registration/declaration

Introduce an opaque association identity with permanent registration and
contextual declarations. This gives an explicit identity for a channel or
measurement installation, but FM-001 does not need to identify a physical
installation. It adds identity, lifecycle, binding, and migration questions
before the missing declared relevance is understood.

### C — Extend VPA

Add flow meaning to VariablePortAssociation. This violates VP-001's narrow
same-owner variable-to-port truth boundary, conflates port locus with flow
relevance, and would make existing VPA records semantically ambiguous.

### D — Extend FRG or FLD

Embed variables or measurement roles in flow registration/declaration. This
couples reusable flow identity or contextual flow support to measurement
concerns, prevents clean fan-out/many-role declarations, and changes accepted
FL-001 semantics.

### E — Upper-layer composition only

Infer an association from VPA, FLD, semantics, and evidence. This has no
authoritative declaration to replay or cite and would necessarily infer the
missing bridge from names, topology, units, or correlation. It is rejected.

### F — Defer until physical boundary identity

Require a sensor, device, channel, connection, or control-volume identity
first. That is a legitimate later product choice, but it makes a logical
declared relevance relation depend on physical identity and is larger than the
current gap.

### Recommendation

Recommend Alternative A: an atomic model-ledger association assertion with no
new opaque anchor. It preserves existing identities, makes the missing claim
explicit and replayable, supports future FA-001, and introduces the least
truth-boundary and migration risk. This remains a design recommendation, not
an owner-approved contract.

## 5. Identity and referent decision

The enduring referent is a **logical association assertion**, not a sensor
installation, physical channel, flow event, or measurement value. A canonical
subject is proposed as:

```text
(FlowAnchor, VariableAnchor, declared participant locus, exact assertion context)
```

The locus is either one declared participant PortAnchor or an explicitly
declared whole-flow/boundary locus if the owner approves that vocabulary. The
subject key must not contain mutable role, sign, unit, value, evidence, note,
authority, timestamp, or append-order fields.

Changing flow, variable, participant locus, or assertion context creates a
new subject lineage. Correcting role, value relationship, orientation,
quantity/unit expectation, support pins, or evidence body remains a new body
within the same subject lineage only when the owner defines those fields as
corrections rather than identity. A correction must never silently retarget a
different flow, variable, port, or context.

No association anchor is proposed. A future physical sensor/channel identity
would be a separate milestone and cannot be smuggled into this subject key.

## 6. Atomic contract sketch

The candidate record is intentionally described without freezing a final record
name, prefix, or public class. It would contain:

1. schema discriminator and content-derived record ID;
2. existing `flow_anchor_id`;
3. existing `variable_anchor_id`;
4. one explicit locus descriptor: participant port or approved aggregate
   boundary locus;
5. exact assertion context;
6. one bounded relationship-to-value dimension;
7. one bounded boundary/participant-role dimension;
8. one bounded orientation/sign dimension;
9. optional exact pins to existing quantity/unit/value/semantic declarations;
10. exact flow/variable/locus support pins and evidence references;
11. optional correction-parent IDs within the same subject lineage;
12. recorded-at, authority, and bounded note fields following kernel precedent.

The record must be atomic: one flow, one variable, one locus, one context, and
one semantic body. A grouped multi-variable record would make partial
correction, fan-in/fan-out reasoning, and result indices ambiguous. Grouping
can be revisited only with evidence that atomic records cannot preserve an
integrity invariant.

The record is a declaration, not an observation. It must not carry a sampled
value, timestamped reading, interval, rate, amount, or derived arithmetic.

## 7. Lifecycle, lineage, and conflict model

The model-kernel precedent should govern lifecycle:

- one subject key may have multiple independent roots;
- identical effective bodies on independent roots may be disclosed as
  corroborating roots, never collapsed by rank;
- same-root forks remain visible as conflict;
- cross-root effective-body disagreement remains disagreement;
- a root's current tips are derived from explicit supersedes edges, not
  timestamps, authority rank, filenames, or append order;
- a withdrawal retracts one current association tip and is itself an evidence-
  bearing, citable record if withdrawal is approved;
- self-supersession, cycles, foreign parents, duplicate parents, and invalid
  withdrawal targets reject structurally;
- historical replay uses an explicit membership list and can revive an earlier
  tip relative to that membership;
- no winner is selected for conflicted roots or cross-root disagreement.

Changing flow, variable, locus, or context starts a new subject lineage. A
mistaken role, orientation, quantity/unit pin, or support citation may be
corrected within the lineage only if its invariant subject remains exact.

If a cited FLD, VPA, semantic, value-specification, port, or flow record is
later superseded, withdrawn, conflicted, or absent from a selected revision,
the association record remains historically immutable. Query results disclose
the support relation as stale, conflicted, inactive, absent, or not applicable;
they do not retarget the pin or retroactively rewrite the record.

## 8. Locus and cardinality semantics

The minimum useful locus is a declared participant PortAnchor plus the exact
flow role to which that port belongs. The association must cite the exact
FLD/PIF support that places the port in the declared source or sink set for
the context. The pin is a model declaration, not proof of sensor placement.

One variable may associate with multiple participant ports and roles through
separate atomic assertions. One flow may fan out to many variables and one
variable may relate to multiple flows; each relation is independently
declared, cited, and queryable. A single assertion may not span several
variables or several unrelated ports.

Whole-flow or aggregate measurements require an explicit abstract boundary
locus. They must not be represented by omitting a port and must not imply a
closed control volume, conservation, or balance. Whether that locus is in v1
is an owner decision.

Fan-in and fan-out are represented as multiple declarations. They do not create
pairwise physical branches, conservation equations, equal values, or flow
balance. A directed hyperedge remains a hyperedge; no pairwise branch is
manufactured from its participant sets.

## 9. Relationship-to-value dimension

FM-001 should not clone ES-001 quantity, role, unit, or semantic declarations.
It should either pin exact existing declarations or state that those
declarations are not required for a purely structural association. The body
needs a bounded relationship-to-value dimension so later assessment can tell
what the association means without guessing.

Candidate meanings for owner selection are direct measurement, command/target,
estimate/inference, calculated/derived quantity, cumulative amount, and
instantaneous rate. These are analysis candidates, not frozen literals. A
small v1 could admit only direct measurement and command/target, with estimate,
derived, amount, and rate deferred until their evidence and arithmetic
contracts exist.

If a role pins a quantity/unit/value specification, the pin must be exact and
the existing declaration retains authority. FM-001 must not infer quantity,
unit conversion, dimensional compatibility, or semantic role from a matching
string or token.

Direct and derived values must remain separate. A derived rate or amount
requires explicit interval endpoints, decimal arithmetic, dimensional rules,
gap/interpolation policy, and temporal coverage; those belong to FA-001 or a
later evaluator, not to this association.

## 10. Boundary role and orientation/sign

Boundary-role candidates include source-side, sink-side, participant-local,
whole-flow/aggregate, storage-related, and other explicitly bounded roles.
Role labels must not imply a control volume or conservation law. The exact v1
vocabulary remains an owner decision.

Orientation/sign candidates are aligned with the FlowAnchor source-to-sink
direction, opposite to it, unsigned magnitude-only, and not-applicable or
unknown. PIF direction must never silently determine sign. The association
must state orientation explicitly when sign has meaning.

Zero is a valid value in any later evaluator but carries no activity meaning.
Negative values require the declared signed orientation; they do not reverse a
logical flow. A bidirectional physical system, reversed logical flow, or unit
conversion requires an explicit later contract. FM-001 does not calculate or
normalize signs.

## 11. Evidence and support closure

Acceptance-time structural closure should require:

- registered FlowAnchor via its exact FRG record;
- exact-context FLD support when a contextual flow claim is asserted;
- registered VariableAnchor;
- registered participant PortAnchor and exact flow-role membership support;
- exact VPA pin when the declaration relies on the variable-to-port relation;
- exact value specification, semantic, quantity, unit, or source-interpretation
  pins only when the selected relationship-to-value dimension requires them;
- evidence-reference closure for every cited model record and the association
  body itself.

An association with no operational observation may still be valid. Observations
never auto-create or amend it. Acceptance is about model declaration closure,
not current source data.

The record stores exact historical IDs and evidence references. A query may
separately disclose whether each support record is current, superseded,
withdrawn, conflicted, inactive, absent from the selected revision, or
unaligned. Staleness does not silently retarget a pin. Whether stale support
means a structured `stale` status or an invalid association conclusion should
follow existing query precedent and remain separate from record validity.

## 12. Model-ledger, canonical, and revision impact

The existing model ledger is the preferred owner: FM-001 is an explicit
engineering declaration between existing model anchors, and the kernel already
provides content IDs, evidence closure, append validation, replay, immutable
indexes, and carry-once query materials. A new ledger would create a
cross-ledger snapshot/revision problem with no demonstrated need.

An implementation would need to extend, without changing existing meanings:

- the canonical `ModelRecord` union with one future candidate record kind and,
  if approved, one withdrawal kind;
- record-kind dispatch and a new collision-free prefix chosen only after
  comparing every accepted prefix;
- content-derived record IDs, file bucket grammar, evidence-reference
  validation, append/load/replay order, and immutable loaded-model indexes;
- exact revision membership and historical byte preservation;
- public builders and `__all__`, with no aliases or accidental exports;
- hostile nested reconstruction, strict indices, deterministic ordering, and
  carry-once read-only query results.

No prefix, record class, field order, hash input, bucket, index, or export is
allocated by this proposal. Existing 36-record bytes, IDs, revision, ledger,
disclosures, and historical replay remain untouched until a separately
authorized implementation slice.

## 13. Query and result surface

The smallest likely read-only query family, subject to owner review, is:

1. exact association lookup by flow, variable, locus, and context;
2. associations for one flow in one context;
3. associations for one variable in one context;
4. associations at one participant port/locus in one context;
5. individual assertion disclosure by record ID.

These are candidate query responsibilities, not frozen names. They would use
injected `LoadedModel` material, own no store, perform no writes, and carry one
complete revision/material object. Nested rows would contain strict indices
only. Result reconstruction would authoritatively recompute endpoint
registration, exact pins, lineage roots/tips, withdrawal activity, support
status, ordering, and all derived relations without I/O.

Candidate literal families should distinguish at least:

- endpoint not registered;
- no association declared;
- one healthy/current declared association;
- corroborating healthy roots;
- same-root conflict or cross-root disagreement;
- inactive/withdrawn lineage;
- stale, conflicted, absent, or unaligned support;
- unknown or not applicable for a dimension not claimed.

The final vocabulary must say “declared association” or equivalent. It must
never use `measured`, `observed_flow`, `flowing`, `active_flow`, or similar
words for a model association result. No query returns a flow value, rate,
current observation, temporal selection, or assessment conclusion.

## 14. Import direction and future composition

The proposed dependency graph is:

```text
system_identity
      ^
model_kernel  (flow, variable, port, and future FM declarations)
      ^
future pure flow-assessment composition
```

`model_kernel` remains independent of data sources, temporal stores,
identity-binding stores, evidence assurance/alignment, model state, semantic,
constraint, behavior, state, and transition evaluation, CAD/PDF adapters, and
FA-001. FM-001 is not allowed to import an upper composition package.

After FM-001, a future FA-001 evaluator might consume a validated FM result,
FL declaration/support result, selected variable value/semantic/constraint
results, and separately supplied EA/evidence-alignment results. It would still
need an explicit policy for time, direct versus derived value, sign, coverage,
and any aggregation. Those inputs and its public surface are not designed
here.

## 15. Historical replay and current 36-record membership

For every pre-FM membership, FM queries return structured absence rather than
scanning directory contents or inferring a relation. The existing 36-record
revision must remain unchanged and return no FM association records.

A later membership containing FM records must include complete dependency
closure and an explicit revision record list. Revisions are membership-relative:
currentness, conflict, withdrawal, and support staleness are derived from the
selected material, not filesystem enumeration, timestamps, or append order.

No demonstration is needed to establish the design. A future synthetic
append, if useful, requires a separate rehearsal and owner gate and must not be
assumed by FM-001 or this proposal.

## 16. Threat model

The implementation proposal must reject or disclose all of the following:

- inference from VPA, PIF direction, names, units, topology, hierarchy, CAD,
  ownership, state, behavior, transition, or observation correlation;
- substitution of a variable, flow, locus, role, context, revision, FLD, VPA,
  semantic, value-specification, or support record;
- a non-participant port, wrong source/sink role, or unsupported aggregate locus;
- role, orientation, quantity, and unit conflation;
- signed values read backward, cumulative amount treated as rate, command
  target treated as direct measurement, or derived value treated as observed;
- fan-in/fan-out converted to pairwise branches, conservation, equality, or
  balance;
- duplicate roots, forks, partial convergence, cross-root supersession,
  cycles, self-supersession, and invalid withdrawal;
- timestamps, authority, filenames, or append order selecting a winner;
- forged anchors, IDs, nested results, indices, ordering, statuses, lineage,
  support, and revision material;
- hostile deep/cyclic/oversized content, boolean indices, and scalar subclasses;
- unclosed evidence references or uncitable withdrawal records;
- result validation that accesses a store or observation source;
- observations or evidence automatically appending model truth; and
- any result presented as physical flow, occurrence, conservation, correctness,
  or safety.

## 17. Adversarial acceptance matrix

The future owner-gated implementation plan should retain these stable rows:

| ID | Acceptance witness |
|---|---|
| FM-A01 | Exact record identity, schema, content hash, and candidate prefix are deterministic; existing prefixes remain collision-free. |
| FM-A02 | Flow, variable, locus, and context subject key is exact; changing any subject starts a new lineage. |
| FM-A03 | Valid FRG/FLD/variable/port/VPA support closure succeeds; missing closure returns typed structured refusal. |
| FM-A04 | VPA alone cannot create FM association; names, units, ownership, topology, and PIF direction cannot create it. |
| FM-A05 | Non-participant port, wrong source/sink role, or wrong FLD pin refuses without path/secret leakage. |
| FM-A06 | Direct, command, estimate, derived, amount, and rate candidates remain explicitly separated; unapproved literals are not silently admitted. |
| FM-A07 | Quantity, unit, semantic, and value-specification pins are exact references, never cloned or inferred. |
| FM-A08 | Orientation/sign is explicit; zero, negative, unsigned, and reversed-flow cases do not change logical flow identity. |
| FM-A09 | Fan-in/fan-out and aggregate-locus cases do not manufacture pairwise or conservation claims. |
| FM-A10 | Same-root correction, fork, convergence, cross-root disagreement, and duplicate-root disclosure match kernel precedent. |
| FM-A11 | Withdrawal is citable, target-limited, cycle-free, and membership-relative. |
| FM-A12 | Historical replay can revive an earlier tip and never uses timestamps, authority, filenames, or enumeration to select a winner. |
| FM-A13 | Later FLD/VPA/semantic/value correction or withdrawal produces disclosed stale/conflicted/inactive support without retargeting. |
| FM-A14 | A 36-record pre-FM revision returns structured absence and byte-identical historical material. |
| FM-A15 | Exact lookup, flow lookup, variable lookup, locus lookup, and assertion disclosure use exact context and deterministic ordering. |
| FM-A16 | Results distinguish unregistered, absent, healthy/current, conflicted, inactive, stale, unaligned, unknown, and not applicable. |
| FM-A17 | Every result carries one complete validated revision/material object; nested rows are strict indices. |
| FM-A18 | Forged nested records, wrong union arms, hidden state, stale derived fields, duplicate/reordered indices, cycles, and substitutions reject before I/O. |
| FM-A19 | Query validation performs no filesystem, store, network, clock, environment, connector, or write operation. |
| FM-A20 | Canonical bytes and result ordering are stable across mapping order and hash seeds. |
| FM-A21 | Import isolation proves model kernel has no dependency on upper evaluation or evidence packages. |
| FM-A22 | Public fields, literals, exports, refusal reasons, and carry-once rules are exact and fully tested. |
| FM-A23 | No result uses occurrence, measured, flowing, active-flow, conservation, causality, correctness, or safety language. |
| FM-A24 | No observation, EA selection, or evidence alignment can auto-append or mutate an FM record. |
| FM-A25 | Existing 36-record ledger, IDs, revisions, protected disclosures, and lower canonical bytes remain unchanged. |
| FM-A26 | Any fixture or append is separately owner-gated; no demo is required by the association contract. |
| FM-A27 | FA-001 input boundary consumes explicit FM facts and never infers relevance from topology, names, units, or correlation. |
| FM-A28 | Physical occurrence/history remains absent unless a later contract explicitly supplies time-window, continuity, and authenticity facts. |

Every final literal and refusal reason must either be reached by a valid
disposable world or be documented as structurally impossible. Subset-only
assertions are insufficient.

## 18. Owner-gated implementation slices

If the owner accepts the design direction, the smallest likely sequence is:

### Slice A — declaration and ledger integrity

Only the approved model-ledger record(s), canonicalization, evidence closure,
store bucket/dispatch, append/load/replay validation, immutable indexes,
identity-preserving corrections/withdrawal, exact exports, and hostile tests.
No query facade, fixture append, assessment, or observation integration.

### Slice B — read-only query disclosure

Only exact FM queries, structured statuses, authoritative result
reconstruction, deterministic indices/order, conflict/staleness disclosure,
import isolation, and result-forgery tests. No upper evaluator or source/EA
lookup.

### Optional Slice C — pure upper composition

Only if the approved objective cannot be met by kernel queries, a separately
gated pure composition may combine carried FM, FL, semantic, and value facts.
It must not select evidence, calculate rates, assess flow, or create an
occurrence claim.

### Optional final rehearsal

Any synthetic demonstration or ledger append requires a separate rehearsal,
owner authorization, preservation proof, and explicit stop. It is not part of
this proposal.

Every slice must stop for owner validation and preserve all lower layers.

## 19. Explicit exclusions and limitations

FM-001 excludes flow evaluation, rate calculation, aggregation, balance,
conservation, accountable occurrence/history, temporal cohorts, continuity,
interpolation, sensor/device/channel identity, physical path or connection
identity, control-volume identity, command/control/action planes, causality,
diagnosis, impact, safety, goals, planning, recommendation, configuration
identity/versioning, UI/facades, orchestration, new connectors, native CAD
interpretation, and all changes to TA-001.

It also excludes automatic relevance from names, topology, ownership,
hierarchy, port direction, units, observation correlation, or changed values.
The association is not a flow value and does not prove that a sensor exists at
the declared locus.

## 20. Consequences for future FA-001

FM-001 supplies a replayable declared relevance relation. FA-001 could then
require an explicit FM association before assessing a flow-related proposition,
alongside carried FL declaration/support, variable semantic/value facts, and
independently selected and aligned evidence.

FA-001 would still need owner-approved semantics for direct versus derived
values, quantity/unit conversion, sign/orientation, source/sink aggregation,
time windows, coverage, and refusal. It could not turn an association into an
observation, occurrence, continuity, conservation, causal, or safety claim.

If those prerequisites cannot be specified without physical boundary identity
or authenticated history, FA-001 must stop rather than infer them.

## 21. Genuine owner decisions still required

The lead proposal intentionally leaves these decisions open:

1. Approve Alternative A and the model-ledger ownership boundary, or choose a
   different alternative.
2. Confirm the invariant subject key: flow, variable, participant locus, and
   exact context, including whether an aggregate/whole-flow locus is in v1.
3. Select the bounded relationship-to-value and boundary-role vocabularies.
4. Select orientation/sign semantics and decide whether unsigned/unknown is a
   valid v1 state.
5. Decide which existing quantity/unit/semantic/value-specification pins are
   mandatory versus optional for each role.
6. Decide whether withdrawal is required in v1 and confirm stale-support
   disclosure versus invalidation behavior.
7. Decide exact query/result breadth and whether optional pure composition is
   needed after kernel queries.
8. Approve owner-gated slice boundaries and whether any rehearsal is useful;
   no append or demo is presumed.

These are design choices, not implementation details. No record name, prefix,
field order, public export, fixture, or ADR number is frozen by this proposal.

## 22. Lead recommendation

Recommend owner authorization for a challenger review of FM-001 Alternative A:
an atomic, evidence-bearing, replayable model-ledger association over existing
FlowAnchor and VariableAnchor identities, an explicit declared locus and
context, and owner-approved bounded role/orientation/value semantics, with no
new durable association anchor. It is the smallest missing bridge and the only
safe prerequisite for a later FA-001 design; it establishes declared
measurement relevance only, never observed flow or physical occurrence.

END OF FM-001 CODEX LEAD PROPOSAL
