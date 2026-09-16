# Maintained declared admissibility — shared-reference corrected candidate

2026-09-16. Documentation correction; proposed contract, not owner-approved design
or implementation authority. “Final” identifies the corrected design candidate,
not an accepted capability. Focused independent re-review is required.

## Narrow correction provenance

This is a new candidate, not a contract freeze or owner approval. The historical
[corrected design](2026-09-16-maintained-admissibility-enforcement-corrected-final-design.md)
remains unchanged at SHA-256
`e6e9938aac5387c6719c678a2392c48b9539e4f3d7840ea6ab1d5cfaacfbd472`;
the historical [focused re-review](../reports/2026-09-16-maintained-admissibility-enforcement-focused-rereview.md)
remains unchanged at
`9631c4d333272a2379128e0cc438764490de0d32931d0b3528a3d6e9f681457b`.
That review closed original M1/M2 and identified N1 only: sharing was conflated
with cycles. The substantive correction is §3.1 and the replacement of the blanket
refusal sentence. Other contract choices, including all five decisions in §10,
are unchanged. The new candidate's exact SHA-256 is recorded externally in the
focused confirmation and receipt; a document does not include its own future hash.
No historical byte copy is deleted or overwritten. This correction exists to
permit legitimate evidence reuse while preventing inadmissible scenarios from
reaching projection/recommendation, not to extend the architecture.

## 1. Basis, scope and correction disposition

Verified local main/HEAD: `8f0dc6a2bc9990c042301ed6d9df50bf8eeb5574`.
Read the complete frozen [lead proposal](../proposals/2026-09-16-maintained-admissibility-enforcement-lead-proposal.md)
SHA-256 `5a5b26fca9043bb14df44e9f963e880446813a5fcf0d7a9017a41c9f7c43e038`
and [independent review](../reports/2026-09-16-maintained-admissibility-enforcement-independent-adversarial-review.md)
SHA-256 `7c58332df841d526dc73bbaf430ce11acae61985d585dfcd339c358128b57dad`.
Both remain byte-exact. This document replaces their ambiguous proposed commitment
and equality choices, not their historical text. M1 is addressed in §§2–4; M2 in
§§5–7. Closure is for the independent reviewer to adjudicate.

The question remains: under an explicitly selected, owner-attested declaration,
may this complete nominated scenario be evaluated, and which named decisions
require reconsideration after premise, context or authority changes?

Recommend an application-owned finite table gate over singleton worlds. W0 and J1
are the two semantic members of the example declaration; X must be denied before
its projection. The existing Cartesian calculation remains unchanged for admitted
worlds. No generic rules, constrained-joint projection, authentication service,
backend record or ledger mutation is required. Historical legacy X calculations
retain their accepted meaning; they did not enforce the joint constraint.

The [individual acceptance](../reports/2026-09-16-bounded-decision-workflow-evidence-and-assumption-proof-owner-acceptance.md)
and [joint acceptance](../reports/2026-09-16-bounded-decision-workflow-joint-assumption-proof-owner-acceptance.md)
and their recoverable archives remain the evidence basis. Historical 110/63/36 and
66/42/17 counts are not expectations for this new gate. Same-author oracle disclosure
remains. Hypothetical feedback supplies no requirement. C is unresolved/dossier-only;
F remains historical/analytical. IN-001 and CI-001 remain open and unselected.

## 2. Exact commitment primitives and object fields

The names below are proposed application schemas, not milestone identifiers or ADRs.
All objects are closed: every listed field is required, optional values are explicit
null, unknown fields and duplicate keys refuse. No embedded self-hash field exists.
Objects use canonical compact sorted-key UTF-8 JSON, no trailing LF, no NaN/Infinity,
no BOM, and no alternate JSON whitespace/escape/key-order representation. This is
the existing `canonical_json_bytes` rule, not a new cross-language JSON standard.
Bound reads, nesting, integers and strings before parsing/normalization. Do not
normalize incoming bytes to conceal a noncanonical wire or invalid commitment.

`H(O)` is SHA-256 of that object's entire canonical byte sequence. All fields,
including metadata, nulls, ancestry and reference fields, participate. A reference
is exactly `{kind,sha256}`; kind identifies the expected object schema or captured
input role and sha256 is 64 lowercase hexadecimal characters. References never
resolve by name, path search or “latest.” Exact captured bytes must exist and hash
correctly; kind/schema and any separately compared IDs/revisions must agree.

`Q` is the complete existing inner request (`bdw001.1`); `B` is its complete public
snapshot. Both preserve current wire/profile validation and their original bytes.
`Q.snapshot_commitment=H(B)`. Existing premise envelope commitments keep their
existing full-envelope-minus-commitment formula; that formula is NOT changed to
the membership-key formula below. Each envelope is checked before deriving a key.
Existing application semantic version/profile editions inside Q are not revision
counters. The new outer schema and new executable build identify the added gate.

| Object | Exact top-level fields participating in H; nested meanings |
| --- | --- |
| D, declaration | `schema="finite-declaration.v1"`, `declaration_id`, `revision`, `predecessor` (D ref or null), `membership_profile="singleton-gamma-beta.v1"`, `template_request` (Q ref), `template_snapshot` (B ref), `pairs` (array of objects with exactly `gamma` and `beta`, each reduced rational), `provenance` (exactly `kind="owner_declared_synthetic"`, `basis` string, `basis_artifacts` array of captured-byte refs). |
| S, scenario revision | `schema="governed-scenario.v1"`, `scenario_id`, `revision`, `predecessor` (S ref or null), `change_kind` (`initial`, `premise`, `policy`, `context`, `evidence`, `declaration`, `presentation`, or `mixed`), `request` (Q ref), `snapshot` (B ref), `declaration` (D ref). |
| A, authority selection | `schema="local-authority-selection.v1"`, `declaration` (D ref), `scenario` (S ref), `purpose` (`hypothetical_evaluation` or `accepted_working_evaluation`), `attestation` (exactly `issuer_label` string, `authenticated=false`, `declaration_approved=true`, `purpose_approved=true`, `basis` string). |
| T, working adoption | `schema="local-working-adoption.v1"`, `declaration` (D ref), `scenario` (S ref), `selection` (A ref), `attestation` (exactly `issuer_label` string, `authenticated=false`, `adopted_as_working=true`, `basis` string). |
| I, invocation content | `schema="governed-invocation.v1"`, `scenario` (S ref), `selection` (A ref), `adoption` (T ref or null), `comparison` (complete prior bundle manifest ref or null), `build_identity` (exact executable/build-policy witness digest). This is semantic invocation input, not filesystem command text. |
| R, result | `schema="governed-result.v1"`, `invocation` (I ref), `build_identity`, `authority_statement`, `admissibility`, `current_condition`, `observed_value_admission`, `raw_projections`, `target_relations`, `feasibility`, `selection`, `decision_review`, `resource_accounting`. All result data, including blocked statuses and counters, are hashed. R contains neither its own digest nor the future manifest/receipt digest. |

The nested R fields retain existing value contracts where computed, augmented only
by explicit `not_computed_gate_blocked` states and the gate/review contract in §9.
The authority statement records `owner_attested_not_authenticated`, selected D/A/T
references and `currentness="relative_to_captured_selection_only"`. Unknown nested
keys are not an extensibility mechanism. Exact serializer layouts for expanded
diagnostics/counters remain bounded-preparation work; no hash field is excluded
from R because of that layout work. No future output is an input authority.

IDs are existing LocalId-form opaque strings, revision is a strict positive integer.
References use content, not ID equality as authority. Basis artifacts are inert
captured evidence bytes, never interpreted for rules or followed for further refs.
No URI/network fetch. Their refs must resolve to retained bytes but do not confer
approval. D's template is Q/B, NEVER an S, A, T, I or R. Template Q cannot contain
an outer declaration/authority reference because its closed schema forbids it.

## 3. Acyclic construction, validation and example

Construction order (arrows mean “may commit an already constructed object”):

```text
captured Q/B/basis -> D -> S -> A -> T (working only) -> I -> R/trace -> manifest -> receipt
                      S also commits Q/B
                      T commits S,D,A; I commits S,A,T and a past comparison manifest
```

More precisely, D depends only on captured Q/B/basis and an older D; S only on
Q/B, D and an older S; A only on D/S; T only on D/S/A; I only on S/A/T, build and
an already existing comparison manifest. R and trace depend on I and computed
data. The new manifest lists payload hashes, not its own hash; the stdout receipt
may cite manifest/R hashes only after publication. No backward amendment occurs.
An adoption attests acceptance of a scenario as a working premise, NOT acceptance
of its as-yet uncomputed result. Later human result acceptance is outside these
inputs. If a human wants to inspect a hypothetical result first, adopt afterwards
and issue a new working invocation; do not amend the historical hypothetical one.

For D/S revisions, predecessor must have the same ID and revision exactly one lower;
revision 1 requires null. Retain and validate the immediate predecessor's bytes.
Earlier history remains separately retained; deeper closure is not automatically
walked or claimed complete. Active-path cycles refuse; completed validated objects
may be shared under the role, context and accounting rules in §3.1. The
same-type revision order strictly decreases on a parent edge; cross-type edges
follow the order above. Past comparison bundles are immutable and cannot reference
the new invocation. A newly supplied comparison graph cycle refuses, not a reason
to skip reconstruction. This proves no permitted object needs its future digest,
directly or transitively, without relying on finding a cryptographic fixed point.

### 3.1. Shared-reference graph semantics and independent accounting

This section replaces N1's global repeated-digest prohibition. It changes neither
object fields/hash formulas nor allowed role edges, world equality, D/S lineage,
authority pins, replay build rules, gate dispatch or the 23 proposed decision slots.

**Node and edge identity.** A node is captured immutable content identified by its
SHA-256, with the actual bytes retained and compared if multiple definitions claim
that digest. Conflicting bytes for one digest refuse; do not silently select one.
A reference occurrence is a particular schema-defined field/array position in a
particular containing object occurrence. Its required type and semantic role come
from that field's closed schema, not from the target digest or caller-supplied name.
Matching bytes do not turn a request into a snapshot, an inert basis into approval,
or one scenario's adoption into another's. Opaque basis bytes have no traversable
internal reference edges; do not reinterpret arbitrary JSON as another graph.

**Traversal states.** Maintain the distinction between unresolved, active on the
current dependency path, and completed under a specified validation scope:

1. Bound and charge the edge attempt, validate reference shape and its permitted
   type/role, resolve captured bytes and check the claimed digest. Existing earlier
   wire/integrity/resource guards keep precedence.
2. A target node already on the current active path is a cycle: refuse closure,
   with no numerical dispatch. This check uses content identity, so changing a
   role label cannot hide a back edge. An invalid role may already have refused
   at step 1; cycle detection does not promise to override an earlier defect.
3. A target previously completed and validated may be shared if its bytes, intrinsic
   type validation and required closure scope match this use. Repeat this edge's
   role, lineage, authority, binding, effective-limit and applicability checks.
   A completed-object record is not a cached permission or universal-context verdict.
4. Otherwise validate the required target scope, mark it active while following its
   permitted dependencies, then mark that scope completed only after those checks
   succeed. An error cannot publish a completed validation marker or positive gate.

“Active” is per dependency path, not “seen anywhere.” A completed object in a
sibling branch is not active merely because another branch used it previously.
Structural validation may reuse completed immutable bytes; per-use contextual
obligations cannot be skipped. Scope includes the required role/profile, build
and applicable limits. A weaker-limit check cannot satisfy a stricter use without
rechecking it. Immediate-predecessor inspection is not full ancestry validation;
a completed limited-scope node cannot stand in for complete comparison replay
closure. Expand only the closure required by the existing design, with no new
unbounded history discovery. Duplicate identical captured copies are not cycles;
retain or represent them according to the bounded layout and charge their actual
copies. Conflicting definitions or incompatible roles refuse.

**Counting is separate from cycle state.** The prepared build policy must supply
finite caps for every new dimension below before a governed run can be authorized.
Symbols here describe counting rules, NOT chosen capacities or amendments to the
accepted application's limits. Count/guard before allocating, expanding or executing
the next charged unit; exceeding a bound refuses with the applicable resource
diagnostic/exit 4. A valid acyclic graph is not exempt from resource refusal.

| Dimension | Count and bound |
| --- | --- |
| Unique objects U | Count each distinct captured content node once, after hash/byte identity checks, regardless of incoming edges. Bound U, each object's bytes/nodes/depth and total distinct bytes; type/scope validations remain separately charged. Shared references cannot manufacture additional free object definitions. |
| Supplied references E | Count every schema-defined reference occurrence in every captured input occurrence, including agreeing repeated edges and repeated serialized copies. This includes basis refs and required metadata refs even if their targets are opaque or not recursively expanded. Bound E before traversal. Do not deduplicate this count by target digest. Existing lower input-reference counting is additionally retained unchanged. |
| Traversal/validation work W | Charge every attempted edge visit (including completed-object reuse and the back edge that triggers refusal), every structural node expansion for a required validation scope, and every required per-use contextual check. Track these as separate monotonically increasing counters with finite caps. Each context check accounts for the bounded fields/entries it inspects, not an unbounded task disguised as one unit. Re-entering a completed node can avoid redundant intrinsic expansion only, never its incoming edge/context charge. Count additional visits/expansions actually performed too. |
| Required reconstruction C | Charge every world/ancestor reconstruction required by existing review/replay contracts at its full accepted lower-layer cost, even when Q/B bytes are shared. No content cache erases existing per-world charges, validator rows, lookups, reference/node accounting, corner work or required recomputation. Extra reconstructions also count; never substitute U for C. Blocked worlds perform zero projection, but all earlier capture/gate/check work still counts. |
| Physical retention and capture | Count every actual captured/serialized copy toward its applicable bytes/files/nodes budget, including templates, priors, diagnostics and witnesses. A single retained immutable object may serve several refs if the approved layout supports it; E/W/context and required C charges still apply. A hash alone never supplies recoverable content. |
| Active depth and closure scope | Bound the active path independently of U and E. Immediate parent versus complete comparison closure remains explicit; missing required closure refuses, not truncates into apparent validation. |

Accounting is invocation-local and cumulative across current and historical worlds;
starting a new branch does not reset budgets. Report logical required counts
independently of optional optimization diagnostics. In particular, charge required
per-use checks/reconstructions even if an implementation caches their result; such
caching cannot change a refusal into admission by making mandated work appear free.
A future optimization that changes accepted lower-layer reconstruction semantics
requires separate approval, not this correction. Byte capture caches are local to
the captured invocation, not persistent sources of authority.

**Determinism.** Use the same schema-defined root/phase order as §8 (D,S,A,T,I;
Q/B retain their existing earlier guard precedence), and canonical field order
within an object, with array edges in their specified numeric index order. Within
a required closure, process dependencies in that stable order. Filesystem discovery,
map insertion, parallel completion or cache warmness cannot select a different
first error, applicable role, logical charge total or permission. Normalize only
the previously permitted representation rules; do not reorder semantically ordered
arrays to obtain a favorable result. Use fresh logical accounting for replay.
A bounded implementation may do extra physical work, but must charge it and may
not present an optimized run as authority for a smaller logical resource demand.

**Nearest twins and future obligations, not tests run here:**

| Case | Adverse input / valid twin and required contract result |
| --- | --- |
| Valid diamond | S0 references D1 and Q0; D1.template_request also references that identical Q0. Traversing either branch first completes Q0, and the other shares it after its own role/context check. One unique Q0, two incoming occurrences/edge checks; normal gate still decides membership. Duplicate identical retained Q0 copies add capture/retention charges, not a cycle. Compare with distinct valid Q1 used under an explicitly renewed matching declaration: two unique objects, same two edge occurrences. |
| Direct active-path cycle | S predecessor points back to the active S, or an abstract closure edge returns immediately to its source. Refuse: invalid same-type revision/role/hash may precede cycle diagnosis. Twin references a distinct retained S with the same ID and revision exactly one lower, with valid renewed commitments. |
| Indirect active-path cycle | A required dependency path returns to an active ancestor through another node. Refuse; do not label the back edge completed sharing. Twin removes the back edge in favor of a legitimate earlier dependency shared from two completed branches. Legal content-addressed schema/order already prevents constructible valid cyclic authority; these are hostile closure contracts, not a demand to forge a SHA fixed point. |
| Invalid role for shared content | Q0 is already validated as a request; another field claims the same bytes as S.snapshot or as working adoption. Refuse type/role/integrity mismatch, regardless of completion/cache state. Twin uses the actual B0/T bound to the required role and exact S/D/A. A valid T for another S likewise fails contextual reference agreement; sharing cannot transfer adoption. |
| Many repeated references | A schema-permitted family of captured/reference occurrences repeatedly names the same target. U may stay small while E/W/C or copied-byte bounds exceed their applicable finite cap; refuse resource overrun before further work. Twin uses one fewer occurrence at the exact prepared boundary, with valid shape/commitments and every other bound satisfied. If profile/cardinality is violated first, that earlier diagnostic wins. The actual boundary is to be measured/prepared, not invented here. |
| Reference-order changes | Alternate discovery/insertion/scheduling order over identical captured graph bytes yields the same canonical logical traversal, membership, logical counters and first refusal. Twin with actual reordered semantically ordered arrays is not automatically equivalent: follow existing canonical/profile/equality rules and renew hashes/authority if supported. The W0 diamond passes regardless of which implementation branch happened to fetch Q0 first; fetch order never supplies permission. |

Commitments still bind original reference positions and bytes; deduplicating logical
validation does not rewrite objects or hash formulas. Historical replay reconstructs
the captured graph and authority, performs the same role/context checks and charges,
and recomputes only permitted worlds. A replay encountering repeated evidence must
not reject it as a cycle or treat previous success as present authority. This section
does not authorize a new graph engine, backend record, cache service or wider domain.

Byte-construction recipe for W0 (notation below is documentation, not an approval
artifact or an executable package): capture Q0 at
`24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125`
and B0 at `782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f`.
The exact canonical `pairs` member bytes for example D1, ordered by increasing gamma:

```json
[{"beta":{"denominator":10,"numerator":3},"gamma":{"denominator":1,"numerator":2}},{"beta":{"denominator":5,"numerator":1},"gamma":{"denominator":1,"numerator":4}}]
```

Construct D1's complete closed body using those domain bytes, template refs Q0/B0,
revision 1/predecessor null and explicitly supplied synthetic provenance. Only then
compute d=H(D1). Construct S0 with declaration ref d and request/snapshot refs
Q0/B0, revision 1/predecessor null/change_kind initial; compute s=H(S0). A0 can now
contain refs d,s and an explicit hypothetical attestation; compute a=H(A0). I0 then
contains refs s,a, adoption null, comparison null and the actual build witness;
compute i=H(I0). None of d,s,a,i is a field of the body being hashed. The literal
reference serialization is `{"kind":"finite-declaration.v1","sha256":"<d>"}`
after replacing `<d>` with the 64 computed hex digits; angle-bracket placeholders
are never accepted wire input. No example attestation is granted by this document.

For working use, construct a fresh Awork with the working purpose and the same
d,s; then Twork refs d,s,H(Awork); then Iwork refs s,H(Awork),H(Twork). Neither S0
nor Awork references Twork. Any change to Q, even an allowed alias or presentation
change, requires a new S and newly bound A/T; equal membership is NOT transferable
approval. A may approve an already constructed S; S's sole governing reference is
to D, never to A or T. This explicitly resolves the phrase “scenario's reference”
in the lead proposal.

Reference validation is equality of complete captured commitments: S.snapshot must
match Q.snapshot_commitment; A.scenario=I.scenario; A.declaration=S.declaration;
T, when present, must match all three D/S/A refs. Hypothetical purpose requires
T=null; working purpose requires a matching T. Neither purpose permits draft or
missing approval. Invocation capture requires the local operator's independently
supplied expected A digest to match I.selection and captured A. This pin is retained
with command evidence; it cannot be inferred from whatever A happens to be supplied.
No scenario field supplies the expected pin. All other refs and the actual build
must match before a substantive gate decision. Missing or mismatched pins refuse.

## 4. Authority, stale use and immutable history

The recommendation remains local owner attestation, not authenticated identity.
Names/true flags/hashes establish no issuer identity. The application enforces
consistency relative to the operator's explicit pin, cannot stop that operator
from fabricating an internally coherent approval, and cannot discover newer or
omitted authority. Output must not say “authenticated/authorized owner.” Private
filesystem control and correct pin selection are owner responsibilities. A stronger
threat model needs another design, not an implicit service in this milestone.

Stale selection means supplied S/D/A/T differs from the exact pinned selection or
its references. Same ID/revision with altered bytes is not equivalent authority.
Given the selected A, no “latest revision” substitution occurs. A deliberately pinned
historical selection remains historical, not certified current. New D revisions
do not retroactively revoke the ability to replay old input snapshots of authority.

Replay captures the historical I and closure, requires the historical exact build,
rechecks all references and recomputes gate/results under that recorded selection.
The original expected A pin is recovered from its retained invocation evidence,
not fetched from current files. Replay emits a new operation manifest identifying
historical recomputation, not a new working adoption or current-authority finding.
Changed build/profile priors refuse; rebaseline explicitly into new bundles if
later authorized. No old result or snapshot is rewritten. A missing historical
declaration/approval cannot be repaired by a same-named current one.

## 5. Exact admissible-world equality

Three identities are intentionally different:

1. **Artifact/scenario identity:** exact H(Q), H(B), H(S), etc. It binds every
   captured byte, actor/purpose/request ID, limits, ancestry and authority refs.
2. **World equality:** equality of the complete canonical membership key W below.
   It quotients only the explicitly allowed aliases/presentation exclusions.
3. **Authority identity:** exact D/A/T/I references. Equal W never permits swapping
   approval, adoption, declaration edition or build.

To derive W, first successfully validate Q/B's canonical wire, closed schemas,
existing premise commitments, numeric shapes, profile versions and public integrity.
Use a deep copy of Q's parsed JSON, NOT an unconstrained model dump that may omit,
coerce or normalize unspecified fields. Delete exactly these three top-level fields:
`actor_assertion`, `request_id`, `requested_limits`. Normalize only
`current_condition_question.as_of` according to §6. Leave every other field and
array element untouched. Wrap that copy as exactly
`{"membership_schema":"singleton-world-key.v1","request":<copy>}`.
Canonical bytes of that object are W; its SHA-256 is an index/witness, not a
substitute for comparing complete W bytes. SHA collision resistance is an integrity
assumption, not a theorem that distinct worlds cannot hash-collide.

The closed Q inventory makes the inclusion rule exhaustive:

| Included in W | Equality rule |
| --- | --- |
| `schema_version`, `workflow_profile`, entire `application_identity` | Exact supported literals and field values. No version aliases or ignoring build-policy meaning. Outer membership schema is also exact. |
| Entire `current_condition_question` | Exact anchor, assertion-context structure and all its fields, label, and normalized instant. Labels inside this question are retained even if two happen to describe the same condition. |
| Entire `observed_input_binding` | Exact indexes, IDs, quantity/unit/observation role refs, token-role premises and their commitments. No ID/name/unit conversion or reordered index interpretation. |
| Entire `premises` | All actions, commands, coordinate envelopes, effects, global applicability, hypotheses, invariances, law, preconditions, support semantics and timing; every envelope field and commitment is included. |
| Entire `target_policy` | Target, costs, feasibility, retained hypotheses, selection rule: every field/order/envelope/commitment. No cost/target changes hidden as presentation. |
| `snapshot_commitment` | Exact H(B); validate against complete retained B. No snapshot normalization, field omission or claim that distinct evidence bytes mean the same world. |

Excluded actor assertion is still validated (including authenticated=false) and
retained. Inner actor `purpose` is free-text provenance, NOT the operative purpose
in A; A's purpose and working adoption remain enforced. Request IDs are provenance.
Caller limits are enforced before membership and cannot loosen hard ceilings;
therefore equivalent worlds may have different technical resource refusals, never
different membership once all guards succeed. No notes field is added to Q.
Provenance basis/issuer text inside premises stays fixed and committed: it is not
parsed for calculations, but changing the support declaration requires renewal.
D provenance likewise changes D authority even when W is unchanged.

D's template must itself be complete, applicable (present/true), canonical and a
singleton world. Derive Wtemplate using the same rules. For membership, derive a
fixed-part key F from W by replacing exactly the following six fields with typed
markers defined by this schema, not caller input:

- gamma.value.lower and gamma.value.upper: marker `{"var":"gamma"}`;
- beta.value.lower and beta.value.upper: marker `{"var":"beta"}`;
- gamma.canonical_commitment and beta.canonical_commitment: marker
  `{"derived":"coordinate_envelope_commitment"}` for each.

These paths are under `request.premises.coordinates`. No other envelope fields
are removed: unit_role, availability, scope, issuer, basis, edition, epistemic kind,
endpoint semantics and premise ID all remain exact. The two replaced commitment
strings were already validated against their actual original bodies. A marker in
an actual request or declaration coordinate is malformed, not a wildcard.

Require F=Ftemplate byte-for-byte AND the actual reduced singleton (gamma,beta)
pair equal to one D.pairs entry. Fixed-part mismatch is declaration-not-applicable;
matching fixed part with nonmember pair is inadmissible. Before F comparison,
handle explicit unknown/missing/global-false statuses as §8 specifies; do not
construct an artificial complete key by filling defaults. W for complete worlds
includes actual gamma/beta values: distinct admitted members have different W.
F is NOT a world identity and cannot justify equality of their projected outputs.

Finite-domain completeness is thus exact over semantic W classes, not over all raw
request byte strings. D1 has precisely two W classes despite differing valid actor
labels/request IDs, tightened limits or timestamp spellings. Every fixed semantic
field comes from the one complete template and every allowed pair is enumerated.
No other world can enter by an omitted mask or a nonmatching fixed field. The
proposed maximum of four rows is a scope cap only; D1 has exactly two. Reject empty
tables, duplicate pairs and rows not sorted by increasing exact gamma then beta.
Rational comparison must be bounded before arithmetic. A larger domain requires
another explicit declaration, not inference from marginal ranges or an invariant.

## 6. Permitted normalization and rejected aliases

Only request `as_of` has a semantic spelling normalization. Accept a valid Gregorian
date/time `YYYY-MM-DDTHH:MM:SS`, optional decimal fraction of 1–6 digits, and uppercase
`Z` or explicit `+HH:MM`/`-HH:MM` offset (hours 00–23, minutes 00–59), except `-00:00`.
Require seconds 00–59 and hour 00–23; reject leap seconds, 24:00, impossible dates,
naive/local dates, lowercase t/z, whitespace separators, more than six fractional
digits and UTC conversions outside years 0001–9999. Normalize by exact offset
subtraction to UTC with six fractional digits and Z, e.g.
`2026-08-07T20:30:00.000000Z`. No truncation, rounding or implicit timezone. Keep
original Q bytes and hash. This is a deliberately specified subset of the existing
typed datetime acceptance, applicable only to the new governed profile.

All numerical operands/table entries require existing strict exact rational objects:
exactly `numerator` and `denominator`, integer JSON tokens (not booleans/floats),
positive denominator, gcd=1 and existing bounded integer size. Zero is only 0/1;
negative numerators remain numbers subject to existing profile constraints, not
silently rejected as physically impossible. There is no physical range inference.
No fraction reduction, float conversion, epsilon equality, percent/unit conversion,
or string-number coercion. Singleton lower equals upper exactly; intervals refuse.
Inclusive singleton endpoints retain the existing endpoint semantics.

All other strings/IDs are exact decoded Unicode code-point sequences, with existing
lexical constraints. No case folding, trim, Unicode normalization, URI aliasing,
renaming or authenticated identity matching. Canonical JSON spelling is required;
equivalent escape or key-order wire spellings are rejected at the canonical guard.
Object key order is fixed by canonical encoding, arrays retain their exact order.
No arbitrary sorting of actions, hypotheses, binding indexes or context arrays.
Supported profile order is enforced as today; otherwise an array-order change is
a different W, not an alias. Unknown/omitted fields fail closed; no default values.

## 7. Hostile examples and nearest twins (not executions)

Every allowed Q byte change below creates a newly committed S and requires fresh
exact A (and T if working). “Same membership” never means reusing the old approval.

| Pair or hostile input | Exact consequence and nearest valid twin |
| --- | --- |
| W0 cutoff `2026-08-07T20:30:00Z` versus `2026-08-07T22:30:00+02:00` | Both normalize to the same W with the same B; identical membership under D1. Their Q/S/A hashes differ. Canonical JSON is still required. |
| Fractionless instant versus `.000000Z`; `.100Z` versus `.100000Z` | Same instant/W in each pair, no discarded precision. Original byte hashes remain different. |
| `22:31:00+02:00` versus W0's `20:30:00Z` | Different normalized instant. If Q/B public integrity mismatches, technical refusal first; with coherently supplied public evidence, fixed-world mismatch under old D. Twin restores original instant/evidence or obtains a new approved D. |
| Changed request ID/actor label/actor free-text purpose, or valid tighter limits | Same W after successful guards; updated artifact authority required. Cannot change A purpose to working without T. Too-tight limits still produce resource refusal. |
| Beta `2/10`, float `0.2`, boolean numerator, decimal string, denominator -5, or negative-zero JSON | Noncanonical rational/schema/wire refusal, never normalized to 1/5. Twin is exact 1/5 with valid commitments. No duplicate pair can enter by reducible fraction. |
| X=(4,3/10), aliases in cutoff or actor fields | F still matches D1 but actual pair is not enumerated; inadmissible, no numerical dispatch. X→W0 changes beta only; X→J1 changes gamma only. |
| Remove beta key; use null with `availability=present`; put a marker in beta; omit snapshot commitment | Schema refusal. Twin is complete canonical beta/snapshot input. A well-formed explicit missing beta envelope instead produces unknown membership, never default beta. |
| Change unit_role, premise ID, retained hypothesis, target, applicability context, snapshot or support edition | No normalization erases it. Existing profile/integrity violation wins if applicable; otherwise fixed-world mismatch requires renewed D. Twin restores the fixed field or renews exact D/S/A. |
| `-00:00`, excess fractional precision, naive date or impossible date | `WORLD_REPRESENTATION_UNSUPPORTED`; twin is a supported exact instant, with no guessed timezone/rounding. |
| Pretty JSON, duplicate keys or reordered canonical keys | Existing canonical/JSON refusal; twin supplies canonical bytes, never silently repairs a signed/attested input. |
| Reorder pair table, duplicate row, fourth-plus-one row, empty list | Declaration shape/canonical-domain refusal; twin is distinct canonical sorted rows within the proposed cap. A new declaration must explicitly authorize any additional pair. |
| Same D name/revision with new bytes; substitute A2 under expected A1 pin | `AUTHORITY_REFERENCE_MISMATCH` before membership/projection. Twin has explicit owner-selected fresh D/S/A pins; no implicit same-name approval. |
| A for S1 applied to alias-equivalent S2; working adoption for S1 reused at S2 | Exact reference mismatch despite equal W. Twin is a fresh correctly bound attestation/adoption, or an authorized hypothetical invocation with null T. |
| Replay old D1 denial after approved D2 adds X | Captured D1 still denies X. Current evaluation under newly selected D2 may admit it and obtain no feasible supplied action. D2 is only a hypothetical future authority choice here, not approved by this design. |

These twins expose representational equality, not a claim that materially different
worlds mathematically cannot share a SHA-256 digest. Compare full key bytes for
membership; use retained hashes for reference integrity under the existing trust
assumption. No outside-domain X becomes W0/J1 through normalization.

## 8. Gate, diagnostics, dispatch and retention

Recommend the following versioned disposition contract, subject to owner choice:

| Stage in precedence order | Result; dispatch/retention |
| --- | --- |
| Existing usage/path/build/resource/wire/schema/public-integrity guards | Existing bounded technical diagnostic/exit; no partial semantic bundle. Preserve existing relative order. Validate all present malformed material before interpreting epistemic missing values. |
| Governed representation and declaration shape | `WORLD_REPRESENTATION_UNSUPPORTED` (unsupported timestamp spelling), `DECLARATION_SCHEMA_INVALID` (including noncanonical rational/table), or `GOVERNED_PROFILE_UNSUPPORTED` (non-singleton/unsupported version); exit 3, no semantic result. Existing numeric-size errors remain exit 4. |
| Authority/pin/closure | `AUTHORITY_UNAVAILABLE`, `AUTHORITY_REFERENCE_MISMATCH`, `AUTHORITY_AMBIGUOUS`, `WORKING_ADOPTION_REQUIRED`, or `HISTORY_INCOMPATIBLE`; exit 3, no numerical work. Wrong present adoption refs use reference-mismatch; absent required T uses adoption-required. |
| Applicability | Known false or known differing fixed context: `declaration_not_applicable`; well-formed missing/unknown global applicability: `applicability_unknown`. No inferred false from absence. |
| Complete operands and membership | Missing/unknown coordinates: `admissibility_unknown` with reason `missing_or_unknown_premise`. Complete matching F but nonmember pair: `inadmissible`. Complete matching F and pair: `admissible`. Other known fixed-field mismatch: `declaration_not_applicable`. |
| Numerical calculation, only if admissible | Existing raw/target/feasibility/selection outcomes. Admissible with unavailable observed evidence is distinct from complete computed no-feasible-action. |

Schema-absent required fields are not unknown applicability. Supported stale_reference
markers remain technical refusals as today. Known public question/binding mismatches
cannot be hidden by an applicability-unknown marker. If multiple errors at the same
new stage coexist, inspect objects D,S,A,T,I in that order, fields in canonical key
order; existing error precedence inside Q/B stays unchanged. For applicability,
well-formed explicit missing/unknown status wins before fixed-part comparison;
no affirmative membership is inferred. Draft/unapproved attestations do not pass
the authority schema. New diagnostic names/fields fit the existing bounded terminal
shape; exact byte envelopes must be checked in bounded preparation, not assumed fit.

Completed semantic gates publish a complete result with exit 0 and an unavoidable
`evaluation_permitted` boolean in receipt and result. False permits assessment
retention only, NEVER projection/selection. Technical refusal is nonzero with empty
stdout; it does not promise a retained refusal bundle. Output-resource/path/retention
failure cannot produce a completed gate receipt. A no-feasible-action outcome has
true permission and a completed numerical/policy assessment, not a gate refusal.

Every supported governed entry point—evaluate, hypothetical/working, replay,
compare-to and any public callable workflow—must use the same validating gate.
No caller-supplied `already_admitted` flag or CLI-only bypass. First validate all
captured integrity/authority inputs and compute each needed world's gate; only
then dispatch numerical work for that world's admitted node. Reconstructed priors
also use their own captured historical gate. A blocked X can never enter
`_prepare_projection` or `_assess_admitted` via current, ancestor or replay paths.
Historical admitted priors may be recomputed for comparison, explicitly charged
as historical work, not represented as permission for the current blocked world.
Byte-only verify never grants permission and does not execute projections.

New governed profile absence is not fallback permission. Legacy profiles/builds
can still compute historical X and remain clearly legacy/non-governed; this is not
universal control over an owner's ability to run other software. Cross-build replay
and prior substitution remain refused. No old semantic result is relabeled.

Recommend a versioned six-payload-plus-manifest bundle retaining complete Q/B,
I/D/S/A/T/template/basis closure, expected pin, needed immediate predecessors,
comparison material, R/trace and build witness. A digest alone is not retention.
Retain captured originals and derived W/F witnesses distinctly; replay checks
derived witnesses from captured inputs, not from an untrusted cached gate flag.
All embedded copies and historical nodes count toward limits. If this cannot fit,
stop for explicit policy/scope decision; do not invent external floating dependencies.
Only new exclusive paths, bounded capture, no network, symlink traversal, overwrite
or cleanup. Manifest-last publication and existing durability exclusions remain.

## 9. Decision accounting and revision effects

Propose exactly 23 named decision slots: gate `admissibility`, independently
supported `current_condition`, eight raw, eight target, four feasibility and one
selection. The gate is not free metadata. Current condition is classified from
the intact public snapshot/question after integrity validation even when the
scenario gate blocks; it is not a projected state. Blocked worlds have all 21
numerical/policy slots explicitly `not_computed_gate_blocked`, with no numeric
values or copied historical recommendations. Zero projected corner work for X.

Gate dependencies include exact D/S/A/T selection semantics, complete W/F operands
and applicability. The governing A changes for each exact new S, so conservative
gate-driven reevaluation of all 21 descendants is expected even for an alias-only
or presentation-only scenario revision. Equal world membership/values does not
mean authority review is irrelevant. Do not claim legacy minimal-review counts.
Gate value is its permission/disposition/reason, not its provenance hashes; changing
authority may require review while leaving that value equal. No dependency on its
own future result or on its own gate row occurs.

Reuse old/current support unions and existing dependency edges, not an automatic
impact-discovery engine. Current condition changes/reviews only under its existing
snapshot/question supports; raw/policy descendants additionally depend on gate.
Add/remove/revise declaration, adoption, context or premises explicitly; removed
supports cannot vanish from comparison. For blocked slots, distinguish required
review from work performed. `value_changed` and equal-after-review are null when
either side lacks a computed comparable value; never compare null as a calculated
number. First-world/no-prior is explicit, not evidence of unaffectedness. A blocked
predecessor becoming admitted requires fresh numerical computation before any
new recommendation; no value-change claim against an uncomputed old value.

One D/S predecessor validates local lineage; comparison results additionally need
their complete matching-build replay closure under bounded policy. If a requested
comparison's closure is unavailable/too large, refuse that comparison invocation,
not silently drop the prior. A separate explicit no-comparison invocation can retain
`no_prior_supplied`; it cannot claim complete history or no affected decisions.
No automatic latest-head, adoption, evidence acquisition or observed-state mutation.

## 10. Remaining owner choices, resource preparation and gate

Recommend these explicit choices; none is approved by this document:

1. **Scope/equality:** select this closed singleton gamma/beta table, exact W/F rules,
   permitted timestamp aliases, conservative fixed-world renewal and proposed maximum
   four pairs. D1 itself enumerates only W0/J1. No general expressions or regions.
2. **Trust/deployment:** accept unauthenticated local owner attestation and explicit
   external selection pin, with no rollback/global-currentness guarantee. Name the
   runtime/storage owner and private evidence-retention responsibility. Reject this
   minimum if adversarial operator authentication is required; do not silently add it.
3. **Revision/adoption:** approve the acyclic D→S→A→T→I order, exact-byte renewals even
   for equal-W aliases, separate hypothetical and working purposes, explicit T and
   historical replay that makes no current-authority claim. Approvals do not grant
   physical truth, C resolution, permission to actuate or permission to execute now.
4. **Presentation:** approve completed gate exit 0 with explicit false permission,
   retained blocked slots and independently disclosed current condition; nonzero
   technical/authority refusal, no promised refusal bundle and no false success
   after retention failure. Consumers must check disposition, not only process exit.
5. **Accounting/preparation:** approve the proposed 23-slot review semantics in
   principle and authorize only bounded static package/resource preparation next.
   Today's 22-row limit is unchanged. The existing 7,898/8,192 charges and other
   historical margins are not measured capacity for new envelopes. Prepare exact
   candidate bytes, closed witnesses, prior copies, diagnostics, denial bundles,
   counters, trace/manifest/receipt accounting and recoverability before proposing
   any exact new resource policy. Do not invent unmeasured ceiling increases.

No milestone name or ADR is allocated. After focused review, the next gate is
owner design approval and separately bounded preparation only. Implementation
requires another explicit authorization after exact schema/resource approval;
experiments/commands require a separately frozen plan and execution authorization.
The earlier contract/workflow/acceptance slices remain independently gated, not
permission granted by this correction. Accepted coverage can inform arithmetic,
integrity, dependency and retention expectations, but cannot prove new gate behavior.

This correction creates only this new candidate and its focused independent confirmation.
All existing frozen documents, application semantics, runtime results, dependencies,
provisioning, ledger and unrelated artifacts are preserved. No tests, application
execution, implementation, acquisition, commit or remote operation is authorized.

END OF MAINTAINED ADMISSIBILITY ENFORCEMENT SHARED REFERENCE CORRECTED CANDIDATE
