# FM-001 Codex Lead Proposal Challenger Audit

Independent architectural challenge of
`docs/superpowers/proposals/2026-09-07-fm001-codex-lead-proposal.md`.

## 1. Frozen inputs and audit method

The proposal digest was verified before substantive reading:

| Input | Result |
|---|---|
| Proposal lines | 578 |
| Proposal UTF-8 bytes | 30,026 |
| Proposal SHA-256 | `2e8e69b465defe2e9610bb1a34e85b80cc20cdd2a668dc0d01eb119818bf36f2` |
| Numbered top-level sections | 22 |
| Required final line | `END OF FM-001 CODEX LEAD PROPOSAL` |

The audit treated the lead proposal as untrusted design input. It inspected
`CLAUDE.md`, `README.md`, the post-TA reconciliation report, ADR-0008 through
ADR-0020, the accepted VM/VS/ES/PT/VP/FL/EA/TA specifications, model-kernel
contracts, canonicalization, store validation, query/result contracts, and
focused tests. The second proposal digest check is recorded in §18.

This report is the only file created by this audit. No proposal, code, test,
fixture, ledger, identity, artifact, ADR, branch, or history was changed.

## 2. Verified repository facts

The frozen baseline is `main` at
`a069cb664af1638cef2168ced6034eb2d30f2f14`. ADR files are exactly 0001–0020;
ADR-0021 is absent. The reconciliation report is
`docs/superpowers/reports/2026-09-07-post-ta001-architecture-and-adr-reconciliation-report.md`
with SHA-256
`c07bd4311d4dbe0345fd877d41a6b9cc7005396dc2c09fd6e2dca85beb09a2fa`.

The authoritative synthetic model remains exactly 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`:

* FRG/FLD/FLW are `1/1/0`;
* TRG/TRD/TRW are `0/0/0`;
* the ledger aggregate is
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
* the FL disclosure SHA-256 is
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
* the TA deterministic result SHA-256 is
  `1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`.

The inspected production precedents are concrete, not merely documentary:

* `backend/model_kernel/contracts.py` owns model record unions, evidence
  arms, `AssertionContext`, registrations, declarations, and withdrawals.
* `backend/model_kernel/store.py` performs validating append/load/replay and
  derives immutable indexes and membership-relative DAG state.
* `backend/model_kernel/queries.py` is the authoritative read-only query home.
* `backend/model_kernel/port_results.py` and `flow_results.py` implement
  carry-once material, strict indices, and reconstructed result contracts.
* `backend/model_kernel/result_revalidation.py` rejects cycles, hidden state,
  hostile scalars, and invalid graph sizes without I/O.
* ADR-0014 establishes role-free VPA semantics and uncitable `vpw_`.
* ADR-0018 establishes declaration-only FlowAnchor/FRG/FLD semantics and
  uncitable `flw_`.
* ADR-0011 establishes model-side VSM/VSP ownership and a separate
  `source_interpretation` ledger. Source interpretation is not model-record
  evidence.
* ADR-0019 and ADR-0020 establish carried, bounded, pure composition with no
  store reread, reselection, or physical truth claim.

## 3. Missing bridge and strongest admissible claim

The proposal correctly proves that the bridge is absent. Existing FL-001
records identify a logical directed port-group relation; VS/ES identify model
value shape and model semantic declarations; VP-001 identifies an explicit
same-owner variable-to-port relation; EA/TA carry bounded evidence results.
None declares flow-to-variable relevance.

The strongest admissible FM claim is:

> In a selected model revision, an accountable authority declared an
> evidence-bearing relevance relation between one existing logical
> `FlowAnchor` and one existing `VariableAnchor`, at one exact declared
> participant locus and context, with explicit bounded semantics and pinned
> historical support.

That claim is not a sampled value, sensor installation, physical boundary,
observed flow, activity, transfer, rate, amount, conservation, continuity,
causality, correctness, safety, or current physical state. The proposal mostly
preserves this boundary and correctly rejects inference from names, VPA,
topology, units, CAD, correlation, state, behavior, transition, and EA.

## 4. Alternatives A–F and refined A

| Alternative | Benefits | Permanent costs / migration | Replay and truth risk | Verdict |
|---|---|---|---|---|
| A: existing model ledger, no new anchor | Smallest bridge; one `mrv_`; existing canonical IDs, evidence closure, DAGs, indexes, replay, and query material | Adds union arms and kernel indexes; no independent association identity | Lowest risk if immutable semantic dimensions and support pins are exact | **Best, with corrections** |
| Refined A: neutral flow-variable association, participant-port-only v1 | Keeps A's size while separating direct measurement relevance from later command/derived/amount/rate contracts | Requires a later additive role/aggregation contract; no migration if v1 is narrow | Lowest semantic drift; historical support remains explicit | **Recommended** |
| B: new durable association anchor | Names a reusable channel/installation if that is truly needed | New registration, lifecycle, identity, revision, migration, and physical-identity obligations | Risks converting declared relevance into installation truth | Reject for FM-001 |
| C: extend VPA | Reuses existing variable/port relation | Breaks VP-001's role-free boundary and changes old meaning | Makes VPA look like flow or measurement truth | Reject |
| D: extend FRG/FLD | One flow-side home | Couples flow identity/declaration to variable and measurement semantics; damages fan-out and reuse | Flow declarations become accidental measurement claims | Reject |
| E: upper composition only | No ledger mutation | No authoritative relation; necessarily infers from forbidden clues | Highest truth risk and no replayable bridge | Reject |
| F: defer until physical boundary identity | Avoids abstract locus ambiguity | Blocks a logical declaration on a future physical identity not yet designed | May force sensor/channel/control-volume claims into FM | Defer only as a product-priority alternative |

Alternative A is sound only as the refined A: a narrow, atomic, model-ledger
relation with participant-port locus, existing semantic tokens where required,
uncitable withdrawal, exact support pins, and orthogonal result statuses.

## 5. Blocking findings

These findings block implementation authorization for the proposal as written;
they are repairable without rejecting the refined A direction.

### B1 — Broad “measurement” vocabulary collapses unlike dimensions

FM-A06 leaves direct measurement, command/target, estimate/inference,
calculated/derived, cumulative amount, and instantaneous rate as candidates.
This is not one role dimension. ES-001 already distinguishes model
`ObservationRoleReference` values such as `measured_actual`,
`commanded_target`, `calculated_estimate`, and `status_configuration`
(`docs/superpowers/specs/2026-08-13-es001-engineering-semantics-design.md`,
Part A). Amount/rate additionally concern quantity form and temporal
arithmetic. Calling all of these “measurement” permits a command or a
calculated result to enter FM-001 without an observation or evaluator.

**Required correction:** FM-001 v1 must admit only declared direct
measurement relevance, represented with the accepted ES role token, or rename
the milestone to a neutral flow-variable association and explicitly defer
non-measurement roles. Do not create a second role/unit/quantity vocabulary.

### B2 — The proposed subject permits semantic identity drift

The proposed key
`(FlowAnchor, VariableAnchor, locus, AssertionContext)` excludes relationship
to value, boundary role, and orientation/sign while allowing them to change
inside one correction lineage. A lineage could therefore change measured
actual to commanded target, direct to derived, rate to amount, or aligned to
opposite sign while retaining the same subject. Those are not ordinary
corrections to one referent; they identify different propositions.

**Required correction:** either put every meaning-defining dimension in the
immutable subject/lineage key, or prohibit those changes within a lineage and
require a new parentless root. Support pins and notes remain correctable body
fields; flow, variable, locus, context, relationship-to-value, aggregation
form, and sign/orientation must not silently drift.

### B3 — Aggregate/whole-flow locus is not implementation-ready

The proposal permits an “explicit abstract boundary locus” but no durable
boundary/control-volume anchor or exact sentinel exists in the accepted
repository. Omitting a port is explicitly forbidden, correctly, but the
alternative is left unresolved. A FlowAnchor is a logical hyperedge, not a
physical boundary or control volume (ADR-0018).

**Required correction:** make participant-port-only the v1 locus. Defer
whole-flow/aggregate loci until a separately accepted stable boundary
referent exists. No sentinel, empty port, or “aggregate” label may imply a
control volume.

### B4 — Citable withdrawal contradicts every accepted model withdrawal

The proposal says an FM withdrawal may be evidence-bearing and citable.
`ModelRecordEvidence` explicitly excludes withdrawal prefixes; ADR-0014 says
`vpw_` has no evidence and is uncitable; ADR-0018 says `flw_` is uncitable;
PT withdrawals are also uncitable. A withdrawal carries authority, time, and
note only; it is not a claim supporting the withdrawn positive record.

**Required correction:** FM withdrawal must be uncitable, target exactly one
eligible current positive tip, be non-duplicable, and mean only inactive in
the selected membership—not false, impossible, or non-measurement.

### B5 — Optional support pins and sibling-ledger references invert ownership

“Optional exact pins to existing quantity/unit/value/semantic declarations”
and “source-interpretation” pins are not enough to define an admission
contract. `VariableValueSpecification` and `VariableSemanticDeclaration` are
model-kernel records; source-property interpretations live in the sibling
`source_interpretation` ledger and cannot be model-record members. ES-001
forbids model kernel imports of that sibling and keeps interpretation
resolution outside model-record closure.

**Required correction:** pin only existing model records in FM. Never cite
source-interpretation records, semantic-compatibility results, EA results, or
TA results as FM membership. State a role-specific support matrix instead of
“optional” pins. Support currentness is query-time disclosure and never
retargets a historical pin.

## 6. Required corrections and non-blocking observations

### Required corrections

* **RC1 — Derive boundary role:** for participant loci, `source` or `sink` is
  derived from immutable FRG membership; it must not be an independently
  asserted body field that can disagree with FRG. `participant_local` is not
  a third role when the locus is a flow participant.
* **RC2 — Fix support closure:** require FRG, variable registration,
  participant port registration, exact-context FLD support, and exact-context
  VPA support for participant-port v1. FLD is the sole contextual route to
  its exact PCN/PIF pins; FM must not duplicate PCN/PIF fields. Historical
  support may be stale but is never retargeted.
* **RC3 — Fix model semantic/value policy:** direct-measurement v1 requires
  an exact model-side observation-role declaration with the accepted
  `measured_actual` token. VSP, quantity-kind VSM, and model unit are
  independently disclosed prerequisites for later assessment, not source
  interpretation and not cloned FM meaning. If the owner chooses to require
  them for admission, that must be a role-specific explicit rule, not an
  optional bag.
* **RC4 — Make sign/orientation explicit:** use a bounded declaration such as
  `aligned`, `opposite`, `unsigned_magnitude`, or `not_applicable`. Absence is
  not an implicit whole-flow or unknown measurement. Do not use orientation to
  reverse FRG direction; do not calculate, convert, or normalize negative
  values. “Unknown” is a result/status, not a positive semantic token.
* **RC5 — Separate result axes:** results must independently report endpoint
  registration/admission, declaration presence, root health/conflict,
  withdrawal activity, support pin activity/currentness/alignment, and
  semantic dimension disclosure. Do not collapse these into “healthy/current”
  or “valid/measured.”
* **RC6 — Complete lineage rules:** every correction parent must be a
  membership-present positive FM record with the same immutable subject and
  same root; all parents must be same-root. Cross-root convergence, foreign
  parents, cycles, self-supersession, duplicate parents, and invalid
  supersession must reject.
* **RC7 — Define exact-body identity:** effective-body grouping must compare a
  canonical semantic body including all identity-defining dimensions. Evidence,
  support pins, authority, note, and time must not be silently ignored when
  they are intended to be correctable. Independent equal roots corroborate;
  different bodies remain visible disagreement.
* **RC8 — Preserve accepted withdrawal behavior:** sibling fork tips do not
  block withdrawal; a withdrawal may make one root healthy while another root
  remains conflicted or corroborating. Historical replay may revive an earlier
  tip relative to explicit membership.
* **RC9 — Tighten query contract:** exact lookup must either include every
  immutable identity dimension or return all matching lineages without
  pretending to select one. Flow, variable, and participant-locus reverse
  queries are non-overlapping only when their exact context and deterministic
  ordering are explicit. Assertion disclosure remains record-id based.
* **RC10 — Add missing hostile twins:** add cross-lineage correction,
  exact-body identity, evidence closure, prefix/citability, duplicates,
  invalid supersession, role/sign identity drift, cross-context leakage, and
  no-I/O result validation to the acceptance matrix and executable tests.

### Non-blocking observations

* **NB1:** “healthy” is a lineage-health term; “current” is pin activity.
  The proposal should avoid compound prose that makes them one conclusion.
* **NB2:** The proposal correctly excludes conversion, arithmetic, and
  evaluation; its FA section should say these remain separate inputs, not
  promise that FM alone is sufficient.
* **NB3:** The proposal's five candidate queries are defensible, but locus
  lookup is useful only as an exact-context participant-port reverse index;
  otherwise it duplicates variable/flow scans.
* **NB4:** A future FM prefix, record class, and evidence-union arm must be
  selected only after collision comparison; the proposal correctly does not
  allocate one.
* **NB5:** “No demo needed” is consistent with TA-001 and should remain the
  default. A disposable positive world proves behavior; it does not justify
  an authoritative append.

## 7. Identity, lineage, and cardinality

The proposal is correct to use existing `FlowAnchor` and `VariableAnchor`
rather than minting an association anchor. It is also correct that one record
must be atomic: one flow, one variable, one participant port, one context, and
one semantic body. Fan-in/fan-out must be represented by multiple records, not
one grouped multi-variable record.

The permanent decisions are:

1. A new opaque association anchor is not required for a declaration of
   relevance. A physical sensor/channel/boundary identity is a later
   milestone.
2. Participant port is part of the referent in v1. Changing it starts a new
   subject.
3. Exact assertion context is part of the referent. Context never wildcard
   matches or leaks into another view.
4. Direct-measurement role and orientation are identity-defining. A change
   from measured actual to command/estimate/derived, or aligned to opposite,
   is a new root or later role-specific contract, not a silent correction.
5. Support pins are historical evidence of the declaration, not identity
   selectors and never latest-successor pointers.

One variable may associate with many ports and one flow with many variables.
No uniqueness, exclusivity, equality, conservation, or branch semantics
follow. Identical canonical content is idempotent; it does not create a
second root.

## 8. Locus and whole-flow boundary

For v1 the locus is exactly one registered participant `PortAnchor` that is
in the FRG source or sink set. The derived boundary role is therefore:

* `source` if the port is in `FlowRegistration.source_port_anchor_ids`;
* `sink` if it is in `sink_port_anchor_ids`.

The association does not assert a physical sensor at that port. VPA is a
declared model association only, as ADR-0014 makes explicit. A PIF direction
does not determine FM orientation or sign; it remains FLD support.

Whole-flow, aggregate, storage, control-volume, and unspecified-port loci are
deferred. “No port,” an empty tuple, a null sentinel, or a label such as
`aggregate` must not enter v1. This is the smallest policy that is exact,
replayable, and does not invent a durable boundary.

## 9. Semantic, sign, and unit model

FM-001 should not clone ES-001's quantity, observation-role, or unit types.
The direct-measurement v1 body should reuse exact model-side declarations and
carry only the minimum association dimensions:

* relationship-to-value: one explicit direct measurement relevance;
* orientation: aligned, opposite, unsigned magnitude, or not applicable;
* no independently asserted source/sink role;
* no amount/rate/aggregation arithmetic;
* no unit conversion, dimensional equivalence, or sign normalization.

The accepted ES role token `measured_actual` is the model-side semantic
declaration that prevents “measurement” from silently meaning command,
setpoint, estimate, or configuration. `calculated_estimate`, `commanded_target`,
and similar roles belong to a later neutral association or assessment
contract. Cumulative amount and instantaneous rate are not observation roles
and require temporal/quantity contracts absent from FM-001.

Signed zero remains a value-level fact for a future evaluator; it does not
mean no flow. A negative value is interpreted only under the declared
orientation by a later evaluator. FM performs none of that work. Reversed
logical flow requires a different FlowAnchor/FRG; bidirectional physical
behavior is not inferred from FLD or PIF.

## 10. Support closure and import direction

### Admission-time closure

Participant-port v1 should require:

1. registered `FlowAnchor` through exact `frg_`;
2. registered `VariableAnchor` through exact `vrg_`;
3. registered participant `PortAnchor` through exact `prg_`;
4. exact-context `fld_` that includes the participant and whose source/sink
   membership agrees with FRG;
5. exact-context `vpa_` for the same variable and participant port;
6. the exact model-side `vsm_` observation-role declaration required by the
   direct-measurement rule; and
7. ordinary model-record evidence closure for the FM positive record and its
   citable model dependencies.

The exact `pcn_` and `pif_` records remain FLD's closure. FM may disclose
their indices through FLD, but duplicating them in FM creates two support
truths and duplicate currentness axes. A missing or nonmatching FLD/VPA
refuses structural admission; a superseded/withdrawn/conflicted support pin
remains historical and is disclosed as stale or conflicted at query time.

VSP, quantity-kind VSM, model unit, source interpretation, EA, semantic
compatibility, observation, behavior, state, transition, and temporal results
are not FM model-record members. They are later carried inputs or separately
disclosed facts. In particular, model kernel must not import
`backend.source_interpretation` or an upper evaluation package.

### Query-time support behavior

Support records never retarget. The result must distinguish:

* exact current support;
* structurally present but superseded support;
* withdrawn support;
* conflicted support lineage;
* absent support in the selected revision; and
* unaligned support where the exact context/body no longer matches.

This is support disclosure, not invalidation of historical model bytes and not
physical truth.

## 11. Lifecycle and withdrawal

The positive FM record should follow the accepted multi-parent correction DAG:
parent sets are canonical and duplicate-free; corrections preserve immutable
subject dimensions; independent parentless roots may corroborate; same-root
forks are conflict; complete convergence is permitted; partial convergence
remains conflict; no winner is chosen by time, authority, record ID, file
order, or append order.

The withdrawal record must follow VPA/FL/PT convention:

* no evidence field and no `ModelRecordEvidence` arm;
* authority, recorded time, and bounded note only;
* target exactly one existing, unsuperseded, unwithdrawn current positive tip;
* duplicate withdrawal, withdrawal of a successor, foreign target, and
  supersede-plus-withdraw of one target are invalid;
* sibling fork tips do not block withdrawal;
* the meaning is “inactive in this selected revision,” never “false.”

The proposal's “citable withdrawal” is therefore a required correction, not
an owner-selectable variation. FM-A11 must be rewritten accordingly.

## 12. Query and result minimality

The query family can follow accepted kernel conventions:

1. exact association(s) for flow, variable, participant port, and context;
2. all associations for one flow and exact context;
3. all associations for one variable and exact context;
4. all associations at one participant port and exact context; and
5. assertion disclosure by FM positive or withdrawal record ID.

The fifth query is a disclosure primitive, not an assessment query. Locus
lookup is not inherently redundant because it is the reverse index needed to
find all variables associated at one declared participant port; it is
redundant only if implemented as an unbounded scan or as an alias with
different ordering.

Every outer result carries one complete `ModelQueryMaterial`. Nested rows
carry strict indices only. Public validation reconstructs the material and
recomputes registration, lifecycle, roots, tips, exact support, ordering, and
statuses without store, filesystem, network, clock, environment, cache, or
write access. It must use the accepted `ModelQueryMaterial` and
`result_revalidation` discipline, not a second validation machine.

Statuses are orthogonal:

* endpoint admission: registered/not registered;
* declaration conclusion: not declared/asserted/inactive;
* root health: healthy/conflicted/inactive;
* assertion activity: current/superseded/withdrawn;
* support relation: exact current/stale/conflicted/inactive/absent/unaligned;
* semantic dimensions: declared/not declared/conflicted/not applicable.

No result literal may say `measured`, `observed_flow`, `flowing`,
`active_flow`, `rate`, `occurrence`, `conserved`, `correct`, or `safe`.

## 13. FA-001 sufficiency and truth boundary

FM can supply FA-001 with exact:

* flow anchor and FRG signature;
* variable anchor and registration;
* participant port locus and derived source/sink role;
* exact assertion context;
* direct-measurement relation;
* explicit orientation;
* model declaration/body IDs;
* exact historical FLD/VPA/VSM support pins;
* revision membership, lineage roots/tips, and support currentness.

FA-001 still needs carried results outside FM for:

* selected operational evidence and independent expected fingerprints;
* time window, cutoff, cohort, coverage, and continuity policy;
* observation attachment and value-shape compatibility;
* quantity/unit/source interpretation and semantic compatibility;
* numeric policy, conversion policy, aggregation, and refusal;
* derived-rate or cumulative arithmetic, gap/interpolation rules;
* source/sink fan-in/fan-out handling; and
* any physical occurrence or authenticity boundary.

FM-A27 is therefore a boundary statement, not a promise that FA-001 will
exist or that FM output is sufficient by itself. Any attempt to calculate,
select evidence, assess a value, infer occurrence, or report conservation is
later-milestone scope.

## 14. Acceptance matrix FM-A01–FM-A28

| ID | Classification | Challenger disposition |
|---|---|---|
| FM-A01 | needs correction | Keep deterministic content identity and collision checks, but add the exact future prefix/evidence-union/canonical comparison gate without allocating them now. |
| FM-A02 | needs correction | Exact flow/variable/locus/context is necessary but insufficient if role/orientation remain mutable; immutable semantic dimensions must be included or root-changing. |
| FM-A03 | needs correction | Store admission and query refusal must be distinct, and the support matrix must require exact FLD/VPA rather than generic “valid closure.” |
| FM-A04 | sound | VPA, names, units, ownership, topology, and PIF direction cannot create FM truth. |
| FM-A05 | sound | Non-participant and wrong-role ports must refuse without path/secret leakage. |
| FM-A06 | needs correction | Candidate vocabulary mixes observation role, command, derivation, amount, and rate; restrict v1 or split orthogonal dimensions. |
| FM-A07 | needs correction | Exact pins are sound, but optional semantic/value pins need a role-specific support matrix and no sibling-ledger citations. |
| FM-A08 | needs correction | Explicit orientation is sound; sign vocabulary must be fixed and must not leave orientation identity mutable or imply evaluation. |
| FM-A09 | sound | Fan-in/fan-out and aggregate non-inference are correct once aggregate loci are removed from v1. |
| FM-A10 | needs correction | Kernel DAG precedent is correct, but exact-body identity, same-root parent restriction, and partial-convergence twins must be normative. |
| FM-A11 | needs correction | Withdrawal must be uncitable under VP/FL/PT precedent, target one eligible current tip, and mean inactive only. |
| FM-A12 | sound | Explicit membership replay and no winner selection are correct. |
| FM-A13 | sound | Historical pins must disclose stale/conflicted/inactive/absent support without retargeting. |
| FM-A14 | sound | Structured absence and unchanged pre-FM replay are required and correctly scoped. |
| FM-A15 | needs correction | Query breadth is acceptable only with exact context, immutable identity dimensions, deterministic indexes, and non-overlapping locus reverse lookup. |
| FM-A16 | needs correction | The listed statuses are not enough unless registration, lifecycle, support, and semantic axes are separate fields. |
| FM-A17 | sound | Carry-once complete material and strict nested indices match accepted results. |
| FM-A18 | needs correction | Hostile reconstruction is correct, but the listed twins must include cross-lineage, exact-body, duplicate, citability, and role/sign identity drift. |
| FM-A19 | sound | No-I/O result validation is mandatory and matches TA/EA precedent. |
| FM-A20 | sound | Canonical bytes and ordering must be independent of mapping order and hash seed. |
| FM-A21 | needs correction | Isolation must explicitly forbid `model_kernel` imports of `source_interpretation`, semantic compatibility, EA, and TA. |
| FM-A22 | needs correction | Public literals and exports cannot be frozen until role, support, withdrawal, and prefix decisions are resolved; the exactness requirement itself is sound. |
| FM-A23 | sound | Wording exclusion is essential and aligned with FL/VP/TA truth boundaries. |
| FM-A24 | sound | Observations and EA cannot append or mutate FM declarations. |
| FM-A25 | sound | Existing 36-record bytes, IDs, revisions, and protected disclosures must remain unchanged. |
| FM-A26 | sound | Fixture/append owner gate and no-demo default are correct. |
| FM-A27 | later-milestone scope | It is a useful FA boundary, but it cannot be an FM acceptance promise or import dependency. |
| FM-A28 | sound | Occurrence/history remains absent until explicit time-window, continuity, and authenticity contracts exist. |

## 15. Threat, replay, and hostile-world audit

The implementation must reject or disclose all of the following without
best-effort repair:

* flow, variable, port, context, role, orientation, support, and revision
  substitution;
* cross-lineage correction, cross-root convergence, partial convergence,
  cycles, self-supersession, duplicate parents, duplicate records, and
  invalid supersession;
* exact-body disagreement hidden by a shared subject or selected by authority,
  timestamp, record ID, path, or append order;
* FLD/VPA support copied from another context, participant, or root;
* source/sink role asserted contrary to immutable FRG membership;
* VPA-only, PIF-only, PCN-only, name-only, unit-only, CAD-only, observation-
  only, EA-only, or TA-only false admission;
* citable withdrawal or withdrawal of a superseded/non-current tip;
* source-interpretation or upper-result objects smuggled into model-record
  evidence;
* role/sign identity drift, command/measurement collapse, amount/rate
  conflation, negative-value reversal, and unsigned-value evaluation;
* missing/unknown/invalid/not-applicable support being collapsed into zero,
  false, current, or measured;
* cross-context lookup leakage and aggregate-locus omission;
* forged nested records, wrong union arms, hidden state, boolean indices,
  scalar subclasses, cycles, reordered/substituted rows, stale derived
  fields, and invalid material membership;
* query/result validation performing any I/O or clock/environment access; and
* historical replay that silently retargets support or chooses a winner.

The accepted 36-record revision must return structured FM absence. A future
FM membership must be explicit, reference-closed, and replayable from a
record-id list. Replaying an ancestor-only membership may revive an earlier
tip; a successor without its ancestry is invalid. No directory enumeration,
filesystem order, or current store state may alter a historical answer.

## 16. Owner decisions

The following are the challenger’s concrete dispositions. These are owner
decisions still requiring acceptance, not implementation authorization.

| Decision | Disposition | Concrete recommendation |
|---|---|---|
| D1. Model-ledger A versus alternatives | `endorse_with_correction` | Adopt refined A in the existing model ledger; do not create an association anchor, new ledger, VPA extension, or FL extension. |
| D2. Invariant subject/locus and aggregate policy | `endorse_with_correction` | Subject is flow, variable, participant port, exact context, and immutable role/orientation dimensions; participant-port-only v1; defer aggregate/boundary loci. |
| D3. Relationship-to-value and boundary-role vocabulary | `endorse_with_correction` | Restrict v1 to direct measurement relevance; reuse ES `measured_actual`; derive source/sink from FRG; defer command, estimate, derived, amount, rate, storage, and aggregate roles. |
| D4. Orientation/sign vocabulary | `endorse_with_correction` | Require explicit aligned/opposite/unsigned magnitude/not applicable; no unknown positive token, sign conversion, reversal, or evaluation. |
| D5. Mandatory semantic/value/support pins | `endorse_with_correction` | Require FRG, VRG, PRG, exact FLD, exact VPA, and exact model-side measured-actual VSM pin; do not cite source interpretation, EA, ES result, or TA result; keep VSP/quantity/unit as separately disclosed prerequisites unless owner makes a role-specific admission rule. |
| D6. Withdrawal and stale-support behavior | `endorse_with_correction` | Use uncitable VP/FL withdrawal convention; one eligible current positive tip; inactive only; historical pins disclose stale/conflicted/absent/unaligned without retargeting. |
| D7. Query breadth and no optional composition | `endorse_with_correction` | Keep exact, flow, variable, locus, and assertion-disclosure queries with orthogonal statuses; no optional Slice C composition and no evidence/value query. |
| D8. Slices and rehearsal/demo boundary | `endorse_as_written` | Slice A ledger integrity, Slice B pure queries, stop for owner validation; no authoritative append; any positive demo requires separate rehearsal, identity freeze, preservation proof, and owner gate. |

Permanent identity decisions are the use of the existing model ledger, no
association anchor, participant-port-only locus, exact context, immutable
measurement/orientation dimensions, and uncitable withdrawal. Permanent
contract decisions are no inferred role, no source-interpretation import, no
aggregate sentinel, no physical occurrence claim, and no winner selection.

## 17. Corrections required before owner authorization

The lead proposal can become implementation-ready without changing its
architectural direction if it is replaced by a corrected contract that:

1. narrows the v1 claim to direct measurement relevance;
2. freezes participant-port-only locus;
3. promotes relationship-to-value and orientation/sign to immutable identity
   dimensions or requires new roots when they change;
4. derives source/sink boundary role from FRG;
5. makes exact FRG/VRG/PRG/FLD/VPA/VSM support closure normative;
6. prohibits source-interpretation and upper-result evidence references;
7. changes FM withdrawal to uncitable inactive retraction;
8. defines orthogonal result statuses and exact query inputs;
9. adds every hostile twin listed in §15 and RC10; and
10. keeps all implementation, fixture, identity, ADR, and append work behind
    separate owner gates.

No new ADR number, record prefix, field order, identity, fixture, artifact,
or public implementation name should be allocated by this audit.

## 18. Preservation and final verification

After the audit, the frozen proposal was rehashed and remained:

`lines=578 bytes=30026 sha256=2e8e69b465defe2e9610bb1a34e85b80cc20cdd2a668dc0d01eb119818bf36f2`

Protected values verified unchanged during the audit:

* `.claude/settings.local.json` SHA-256
  `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`;
* post-TA reconciliation SHA-256
  `c07bd4311d4dbe0345fd877d41a6b9cc7005396dc2c09fd6e2dca85beb09a2fa`;
* ADR count 20, contiguous 0001–0020, ADR-0021 absent;
* model/revision/family counts and protected FL/TA/ledger digests in §2.

`git diff --check` produced no whitespace diagnostics. Because both inputs are
ordinary untracked files, `git diff --no-index --check` returned its normal
comparison exit code without any whitespace error; the repository-wide
`git diff --check` was also empty. The targeted pytest command was not
available: `.venv` is absent and the system Python has no `pytest`; no
dependency or test tooling was installed for this audit.
The final working tree contains only:

```text
?? .claude/settings.local.json
?? docs/superpowers/proposals/2026-09-07-fm001-codex-lead-proposal.md
?? docs/superpowers/reports/2026-09-07-fm001-codex-lead-proposal-challenger-audit.md
```

No history operation was performed. No existing file was modified. The
working-tree preservation, settings preservation, frozen-baseline
preservation, and audit-only scope are confirmed.

## 19. Findings summary and verdict

| Class | Count | IDs |
|---|---:|---|
| Blocking against implementation authorization | 5 | B1–B5 |
| Required correction | 10 | RC1–RC10 |
| Non-blocking observation | 5 | NB1–NB5 |
| Total findings | 20 | — |

**Overall verdict: `approve_with_corrections`.**

Alternative A is the smallest sound architectural bridge only after the
refinements in this report. The proposal is not implementation-ready as
written because its broad “measurement” vocabulary, mutable semantic
lineage, unresolved aggregate locus, citable withdrawal, and optional
cross-ledger support language create identity, dependency-direction, and
truth-boundary defects. Those defects are concrete and blocking for
implementation authorization, but they are repairable within refined A.

The resulting FM declaration must remain only a declared relevance relation.
It must never be reported as a measured value, observed flow, active flow,
physical occurrence, rate, amount, conservation, causality, correctness,
safety, diagnosis, or recommendation.

END OF FM-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
