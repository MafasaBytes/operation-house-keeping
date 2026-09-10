# CS-001 — Commissioning Evidence Sufficiency Policy

Codex lead design proposal — 2026-09-10. Unapproved, design-only.

## 1. Recommended outcome and exact decision

**Recommend outcome 1: no new milestone—existing APIs suffice.** Close this
investigation with an application-consumer policy protocol, subject to owner
review, rather than authorize a CS backend implementation. No new durable
contract, record, identity, ledger, package, public API, or ADR is justified.
The decision protocol below specifies what an explicit caller policy would
mean; it is not an implemented API or an approved operational policy.

The exact question is:

> For this exact governing criterion and nominated measured-actual sample at
> an explicit receipt cutoff, may the commissioning workflow use the evidence
> under an explicit age-and-coverage policy, or is that evidence not usable
> under policy because its receipt age exceeds the bound?

The named initial consumer is the commissioning/operations verification
workflow. With the stated preconditions, every engineering/evidence fact needed
for this question is already disclosed and publicly reconstructible. The only
new decision is permission to use this nominated evidence under a caller's
rule. This is not a new fact about the engineered system. Otherwise admissible evidence whose receipt age exceeds the bound has disposition
`evidence_not_usable_under_policy`, reason `receipt_age_exceeded`. The workflow
may request a new acquisition or evidence refresh; this is not a requirement
for a new physical measurement. Other failures retain distinct withheld/refused
outcomes, not automatic refresh.

There is no demonstrated attack which requires a new integrity boundary.
Moving the accepted FC/CN/EA checks into another backend wrapper would not
establish a missing property. The policy-specific arithmetic is deterministic
application policy, not evidence-backed model declaration. This conclusion
does not claim that the repository already contains a named sufficiency API.

## 2. Verified accepted baseline and scope

| Checkpoint | Verified value |
| --- | --- |
| Branch; initial working tree | `main`; clean |
| Local accepted HEAD | `4ad1a5812e01490bf40aaa8079936f038488e6f9` |
| HEAD subject | `docs: reconcile architecture and ADRs through FC-001` |
| Local origin/main ref | `7693f1acf763f652947dff28b5dbb8a8dfee2505`; no fetch or remote mutation |
| Frozen reconciliation | [Post-FC reconciliation report](../reports/2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md) |
| Reconciliation SHA-256 | `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5` |
| Reconciliation size | 645 lines; 56,663 bytes |
| Model ledger | 36 records; exact-membership load/replay agrees |
| Model revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| Model-kernel public exports | Exactly 236, unique and ordered |
| Ordered export digest | `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |
| FCD/FCW; FMA/FMW | `0/0`; `0/0` |
| ADR sequence | 22 unique, contiguous accepted ADRs, ADR-0001 through ADR-0022 |
| ADR-0023 | Absent and unallocated; this proposal does not reserve it |
| Last full verification | Historical accepted coverage of 4,074 passing tests, not rerun here |

The [final FC verification report](../reports/2026-09-09-fc001-slice-b-final-verification-report.md)
records 4,073 working/all-extras passes plus the separately permitted passing
loopback test, covering 4,074; this is not an uninterrupted new full run.
The [final FC owner acceptance](../reports/2026-09-09-fc001-final-owner-acceptance.md)
and its verification report retain respectively SHA-256
`1436b12aff7ad6b387a58bba0ea7d87386fffd14c151d5ad76b06384a7529ca8` and
`eb67c0830ac54c3caac9a8763afd0e84484edc8f7f900fd6391f137d5a9eec71`.
All baseline checks passed before writing this file.

This proposal creates no implementation, test, fixture, disposable model
record, authoritative append, generated artifact, branch, or commit. Examples
are design inputs and expected decisions, not newly captured evidence. The
authoritative zero-FMA/zero-FCD model cannot produce a positive FC commissioning
answer merely because this proposal exists.

## 3. Necessity test against live public results

### 3.1 Existing facts and exact supporting surfaces

The dependency test starts with the existing accepted join, not a proposed
schema. The normative join is section 20 of the
[FC design](../specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md).
The frozen reconciliation records its successful disposable A/B proof and
the independent expected-fingerprint check. This investigation also inspected
the live implementations below, not just that proof summary.

| Required fact | Existing public API/result and authoritative material | Sufficiency for this question |
| --- | --- | --- |
| Which criterion governs? | `backend.model_kernel.ModelQueries.flow_operating_criterion(...)`; reconstruct full `FlowOperatingCriterionResult` using its public `model_validate`. `material` carries exact membership/records; `subject` carries roots, governing group, applicability and typed support rows. | Applicable group identifies exact CRG/VCN, variable, FM body and retained witnesses. No inferred designation. |
| Which FM body and why is its witness relevant? | FC material contains the referenced `FlowMeasurementAssociation` and its six pins. Public `ModelQueries.flow_measurement_association(...)` and `flow_measurement_assertion(record_id)` expose FM agreement/currentness and historical witness detail if separately requested. | FC already reconstructs its FM dependence. A second carried FM result is not needed for this decision. Historical witness activity must not be confused with current same-body support. |
| What was evaluated? | `backend.constraint_evaluation.ConstraintEvaluationQueries.constraint_evaluation(...)`; full `ConstraintEvaluationResult.model_validate(...)`; exact `constraint.registration`, `constraint.declaration`, revision, candidate indices and verdict. | Full CRG/VCN equality to FC, not just an anchor or predicate string, defeats B-for-A substitution. |
| Which nominated value and interpretation? | CN's single `semantic_compatibility`, its `value_compatibility` (`VariableValueCompatibilityResult`), model-state/binding disclosures and candidate's complete `TemporalOccurrence`. Public producers: `SemanticCompatibilityQueries.variable_semantic_compatibility(...)` and `ObservationCompatibilityQueries.variable_value_compatibility(...)`. | Exact variable, candidate path, six-field locator, occurrence content, model/binding/interpretation revisions and receipt cutoff are available. No new observation identity. |
| Selected evidence and attempt membership | `backend.evidence_assurance.EvidenceAssuranceQueries.select_operational_evidence(request)`; full `OperationalEvidenceSelectionResult`; snapshot request, source/temporal material, routes, capture fences, issues, `selected`, `coverage`, assurance and fingerprint. | Exact one-source scope, inclusive horizon/cutoff, receipt age, ordered captured attempts, reused-payload closure and seed membership are already present. |
| Integrity without stores | `validate_operational_evidence_snapshot(snapshot, expected_fingerprint=...)`. | Reconstructs canonical snapshot and all derived coverage/selection. Independent expected fingerprint detects coherent replacement; no new source-byte or current-store check. |
| Does that evidence belong to the CN candidate? | `backend.evidence_alignment.align_operational_evidence_with_value_compatibility(OperationalEvidenceAlignmentRequest(...))`. | Compares exact cutoff, six-field locator, full occurrence and endpoint closure; uniquely matching candidate, fingerprint relation, attachment and incomplete/refused distinctions are explicit. |
| Receipt-side elapsed age | `snapshot.selected.selected_received_at`, `.observation_age_seconds`, `.age_basis`; `snapshot.request.as_of`. | EA already computes exact nonnegative age from receipt timestamps. The caller compares it to its explicit threshold. |
| Coverage admissibility | `OperationalCoverageSummary` plus reconstructed routes and exact request interval/scope. | Caller can require the precise nonempty/all-attempts-observed condition below. No additional coverage declaration is necessary. |

Relevant live source: [FC results](../../../backend/model_kernel/flow_operating_criterion_results.py),
[FM records](../../../backend/model_kernel/contracts.py),
[CN contracts](../../../backend/constraint_evaluation/contracts.py),
[EA contracts](../../../backend/evidence_assurance/contracts.py),
[EA derivation and queries](../../../backend/evidence_assurance/queries.py),
[alignment derivation](../../../backend/evidence_alignment/derivation.py),
and [source time contracts](../../../backend/data_sources/contracts/api.py).
The accepted boundaries remain [ADR-0019](../../adr/0019-content-bound-operational-evidence-selection-and-assurance.md)
and [ADR-0022](../../adr/0022-explicit-flow-operating-criterion.md).

### 3.2 Constructive sufficiency argument

Let E be the fully validated, independently bound FC/CN/EA join. Let P be a
caller-authorized exact policy value. The workflow can already derive:

1. designation/applicability and the exact nominated CN verdict from E;
2. whether E covers precisely P's required receipt-side interval and scope;
3. whether every captured attempt in that interval observed the property;
4. whether the selected occurrence's disclosed receipt age meets P's bound.

After the refusal and coherence gates in section 7, the conjunction of 2–4
decides policy permission. Both `satisfied` and `violated` CN verdicts pass
the *availability* gate; neither dictates policy permission. No unknown model
fact is queried, inferred, or fabricated in this construction. Section 8 gives
deterministic counterexamples and boundary twins.

The accepted integration disclosure is already a decision-relevant witness:
at `2026-08-07T21:00:00+00:00`, nominated `60.1` violates governing A (upper
bound 50), while ungoverned B (upper bound 80) is satisfied; aligned EA coverage
is complete, and selected receipt time `20:00:06+00:00` yields exactly 3,594
seconds. An explicit inclusive 3,600-second policy permits using A's violation;
an explicit inclusive 3,000-second policy yields
`evidence_not_usable_under_policy`, reason `receipt_age_exceeded`. No ledger or lower
result changes between those two policy evaluations. Those illustrative
thresholds are not recommendations or accepted commissioning limits.

### 3.3 Four distinct categories

| Category | Finding |
| --- | --- |
| Already disclosed accepted information | All exact designation, candidate, cutoff, membership, provenance, alignment, age and bounded attempt-coverage facts above. |
| Deterministic policy evaluation not implemented as a repository API | Exact threshold comparison, selecting the explicit coverage requirement, and mapping receipt-age failure to `evidence_not_usable_under_policy` with reason `receipt_age_exceeded`. These operations need no additional backend evidence contract. |
| Durable policy facts genuinely requiring model representation | None demonstrated. A future regulation, calibration certificate or engineering authority's durable requirement would need its own concrete authority/lifecycle question; it cannot be presumed from this workflow preference. |
| Application workflow choices | Who may approve P, its age/window values, its retention/version labels, when to ask a human for refresh, display of withheld decisions, and whether any refresh request is subsequently executed. |

If “coverage” instead means physical continuity, required polling cadence,
all independent sources, authenticated time, or agreement between sensors,
the construction does not answer that stronger question. Section 4 names the
missing prerequisite explicitly. That is a scope change, not a reason to invent
a coverage Boolean or to introduce a durable CS declaration now.

## 4. Exact semantic policy profile for the caller

This is a proposed bounded **application protocol**, not a new backend schema.
Its values are explicit request-carried data retained by the caller if replay
is required. It uses existing engineering IDs; the local label/version are
not minted identities, model anchors, signatures, or globally unique records.

### 4.1 Mandatory inputs; no silent defaults

| Input | Meaning and rule |
| --- | --- |
| Protocol tag | Exact literal `commissioning.receipt_age_and_attempt_coverage.v1`; selects only the semantics in this document, not a pluggable policy engine. |
| Policy label and version | Nonempty application-local ASCII tokens, 1–64 bytes each, alphabet `[A-Za-z0-9._-]`. No automatic latest-version resolution. |
| Authorization/provenance reference | Mandatory nonempty opaque caller-local token, same bounds. Caller supplies authorization out of band; this token is a disclosure, not cryptographic proof. No URI fetching. |
| Expected policy | Independently retained full policy value, including label, version, authorization reference, target and every rule. Compare exact validated values. A label alone cannot bind content; no new content-derived policy ID is needed. |
| Policy target | Exact FM effective body and exact CRG/VCN record IDs. The body is the five subject fields (flow, variable, participant port, context, orientation) plus six FMA support pins. Context is the full typed value, not a display label. |
| Maximum receipt age | `max_receipt_age_us`, canonical decimal integer string, explicit; unit is microseconds. |
| Age boundary | Exact `inclusive` or `exclusive`, mandatory; never inherited from the CN predicate's boundary. |
| Required coverage window | `coverage_window_us`, same duration representation. Required interval is exactly `[C - window, C]` in EA's receipt-side wall-time domain, both ends inclusive. Overflow is invalid input. |
| Coverage requirement | Exact literal `nonempty_all_captured_attempts_observed_exact_property`; no optional weaker mode. |
| Reuse treatment | Exact literal `receipt_occurrence_with_complete_payload_and_seed_closure`; repeated payloads are permitted only with their accepted full closure. This explicitly does not demand newly changed content. |
| Source-time use | Exact literal `disclosure_only`; required even when source time is unavailable. |
| Expected evidence request | Exact seven-field EA scope (source, adapter, subject identifier, endpoint, extraction route, item, JSON Pointer), supported EA selection-policy kind/version/axes, explicit cutoff C and required interval. No wildcards or alternative-source lists. |
| Independent engineering/evidence commitments | Selected model revision, binding and interpretation revisions when carried; exact FC subject/body/CRG/VCN; nominated strict candidate path; full occurrence and locator when a sample exists; expected EA snapshot fingerprint for every non-refused selection. These are caller context, not copied from an untrusted result. |

All fields above are mandatory for a usable-sample request. A non-refused
absence snapshot still requires an independently retained expected fingerprint,
but has no nominated full occurrence to bind; the caller explicitly requests
an absence disposition for the same variable/locator/cutoff, never substitutes
absence for a supplied sample. Refusal has no snapshot/fingerprint comparison;
the intended request must still match. Structural missing fields are invalid,
not inferred defaults. A wholly absent policy or unrecognized semantic profile
means policy applicability is unavailable, never permissive fallback.

There are no optional rule fields in this profile. Descriptive notes can remain
outside it in application records; they have no evaluation effect and cannot
be silently accepted as extra protocol fields. Authorizing a policy does not
authorize a measurement command. No real age/window/authority values are chosen
by this proposal.

### 4.2 Coverage definition and its exact limits

For the independently expected scope and interval, admit the reconstructed EA
snapshot, not a caller-supplied summary flag. Let T be
`coverage.attempt_route_indices` and O be
`coverage.property_observed_route_indices`. Coverage passes precisely when:

- the snapshot's request equals the expected scope, cutoff and interval;
- all accepted source/temporal membership, provenance and fence checks pass;
- T is nonempty, O equals T, and the omitted-property, empty-snapshot, failed,
  quarantined and extraction-incomplete index sets are empty;
- a selected source observation exists, and the resulting accepted EA status
  is `complete_within_declared_horizon`.

This restates the live EA derivation: nonempty routes, selected occurrence,
and every route having disposition `property_observed`. It covers the captured
attempt population within an explicitly declared interval, not every instant
of that interval. Ten minutes with one observed attempt can satisfy this rule;
it proves no ten-minute cadence. No attempts is incomplete, not vacuous success.

The interval membership axis is EA's `effective_wall_time`: attempt receipt
time, or `finished_at_no_response` for an attempt with no response. That is
accepted receipt-side bookkeeping, **not source-effective time**. Membership
and ordering remain lower-layer responsibilities; do not sort by source time
or invent overlap semantics for an attempt whose start precedes the interval.
Requiring the entire lifetime of every started/unfinished attempt would need
an explicit alternative acquisition-window contract and treatment of unfinished
attempts; this profile does not establish it.

The full seven-field scope is exact. EA's selected consumer locator has six
fields; endpoint closure comes only from validated snapshot material. This is
coverage for that one scope, not mixed inventory totals. Required material is
the existing mechanical closure, not a new list of arbitrary named documents.
An independently specified finite document/source checklist could be compared
as application data, but deciding its completeness/authority is outside this
profile. No requirement is inferred from other configured sources.

Failure anywhere in the whole required horizon makes this policy's coverage
insufficient, including a failed attempt before or after the selected sample.
This is deliberately stronger than “no failures since the selected sample”
and must be explicitly accepted by the workflow owner. A shorter supplied
horizon is not silently upgraded. For a well-formed same-cutoff/same-scope
selection with a different horizon, report `coverage_insufficient` with
`required_interval_not_established`; neither reselect nor crop a larger
snapshot into a new proof. A cutoff/scope substitution is incoherence instead.
Here the independent snapshot commitment binds what was actually captured;
the policy window specifies what was required. A correctly committed capture
can fail that requirement without being forged. The interval comparison is
therefore a coverage gate, not a generic expected-context equality check.
Changing the capture while keeping its independently expected fingerprint is
still incoherence, including when that change alters its horizon.

A pre-horizon seed may establish the latest selected observation and its age,
but never enters T or proves continuity before the horizon. Preserve its exact
independently discovered seed, source inventory token and all dependencies.
Do not drop historical envelope/run dependencies when several attempts reuse
one raw payload. Distinct receipt occurrences can share one observation/raw
record; a fresh receipt is not proof that the physical measurement was renewed.

Exact missing prerequisites for stronger meanings are: a required sampling
schedule and missed-attempt semantics for cadence; an approved required-source
inventory and per-scope evidence for cross-source coverage; a named-material
authority/completeness rule for arbitrary documents; and physical event/time
authentication and continuity semantics for occurrence history. They are not
provided by EA's complete status and are not designed here.

### 4.3 Age, clock domains, versioning and renewal

Use only receipt-side timestamps already made comparable by EA selection:
`age_us = C - selected_received_at`, computed exactly as integer microseconds.
Check equality with EA's canonical `observation_age_seconds` after exact decimal
conversion. Never call an ambient clock, use binary floating-point seconds,
or compute an age from `source_time`, envelope time, HTTP Date, or a policy's
recording time. UTC normalization does not prove that two independent source
clocks are comparable or authentic.

Source-effective disclosure remains the complete `SourceTimeMarker` (wall
clock with basis, monotonic with clock identity/unknown origin, or unavailable),
its carried segment/context and original occurrence. No source wall clock is
compared with receipt time, and no cross-segment monotonic ordering is added.
A source's apparently recent timestamp cannot rescue stale receipt evidence.
If an owner requires authenticated elapsed physical time or a different
receipt clock domain, that comparability/authority prerequisite is missing;
this protocol must be policy-inapplicable rather than assert a new ordering.

Both duration strings admit exactly `0` or a nonzero ASCII digit followed by
ASCII digits, no sign, whitespace, exponent, decimal point or leading zero.
Proposed application admission range: 0 through 31,536,000,000,000 microseconds
(365 days), inclusive; maximum lexical length 14. This is a bounded protocol
capacity, not an engineering freshness constant. The actual threshold/window
must always be supplied. Different capacity requires a separately reviewed
profile, not silent clamping. Date arithmetic must remain within the accepted
aware-datetime range; reject overflow and sub-microsecond timestamps.

Inclusive means `age_us <= max_receipt_age_us`; exclusive means `<`. With zero
maximum age, inclusive permits only an exact receipt/cutoff match, and exclusive
permits no nonnegative age. A zero coverage window is `[C,C]`; it still requires
at least one qualifying captured attempt at C. No observations or timestamps
are synthesized to make zero pass. Negative age in claimed admitted material
is incoherence. Missing receipt time in a claimed selected EA observation is
invalid lower content, not `age_unavailable`: accepted EA selected observations
always carry receipt time and age. A valid no-observation snapshot has no age
and receives the distinct absence handling below.

Version changes require a new explicit caller value and separate authorization.
Never mutate the meaning of an already retained label/version. Compare the full
policy, so even same-version/different-threshold substitution is rejected.
Historical replay supplies the older policy and the older independent expected
commitments; no filesystem lookup of “latest,” auto-renewal, automatic VCN
repinning or model-revision selection from C occurs. A coherent policy targeted
at another FM body/VCN is `policy_inapplicable`, not implicit renewal. Replaying
an older authorized decision does not authorize use under today's policy.

## 5. Composition boundary, authoritative joins and carriage

Ownership follows semantics: this is workflow use-permission above FC/CN/EA,
not model truth and not evidence selection. Existing application code may
evaluate the protocol with downward imports from public package surfaces.
`backend.model_kernel` must not import EA, CN or policy; EA must not acquire
model semantics or policy thresholds. Alignment must remain its accepted sole
VS-occurrence alignment operation. No new package name or shared policy engine
is selected.

The minimal replay input consists of complete FC, complete exact-lookup CN,
complete EA selection, the caller policy and independent expected commitments.
Retain each root once. Do not carry a second standalone VS/ES/state/observation
result: use CN's existing nested material. Do not carry a second FM snapshot:
FC material already retains all records and witnesses needed for its proof.
Reconstruct the existing alignment **during** composition from EA and CN's
carried VS with the independent expected fingerprint. It is not another
authoritative archived input. The workflow decision can reference that derived
alignment and the three retained roots, without embedding copies of them.

This does not edit, flatten or deduplicate inside accepted lower schemas;
their mandated internal repeated request fields remain exactly as defined.
Transient alignment necessarily references EA and VS as its accepted request
requires. No new aggregate serializes both that request and extra copies of
its lower roots. If a caller separately retains the full alignment for display,
that is an optional application artifact with inherited duplication, not a new
canonical CS proof or a claim of globally deduplicated lower fields.

Required joins, using reconstructed complete outer results:

1. Verify independent expected model membership/revision and exact FC subject.
   Require `subject.conclusion == 'applicable'` before reading a governing
   group. Preserve all roots/groups, not a favorable root subset.
2. From the group's typed `support_rows`, resolve full CRG and VCN records
   through `material.records[record_index]`. Compare their full content and
   IDs with CN's `constraint.registration` and `constraint.declaration` and
   compare exact revisions. Require the nominated variable throughout.
3. Resolve FCD declarations and retained FMA witnesses using the group's
   declared indices. Compare the full effective body (section 4.1) and VCN
   to the caller target. Retain every competing/current/historical disclosure.
   Do not require the originally cited FMA witness itself to remain current
   when FC validly finds a healthy same-body current assertion. No newly
   nominated “best” FCD is selected among corroborating equal-body roots.
4. Resolve the independently nominated strict CN candidate path, its
   `semantic_candidate_index`, ES value candidate, VS/state/bound observation,
   exact six-field locator and complete `TemporalOccurrence`. Compare all
   independently expected content and revision commitments, not merely value,
   checksum, occurrence ID or timestamp. Preserve the CN/ES/VS findings.
5. Require CN, VS and EA normalized receipt cutoffs to equal intended C. For
   non-refused EA, require independent expected fingerprint matched. Compute
   existing alignment once with CN's exact VS; its aligned index must identify
   the nominated candidate, with `candidate_attachment == 'attached'`.
   Honest `multiple_matching_candidates` with otherwise valid inputs maps to
   `criterion_evaluation_unavailable`, retaining that exact lower reason and
   `multiple_matches` disclosure; never “pick first.” Actual candidate or
   carried-result inconsistencies still map to `input_or_revision_incoherent`.
6. Apply the explicit age/coverage rule only after the appropriate availability
   gates. Report policy permission separately from the exact CN verdict.

`FlowOperatingCriterionResult.model_validate`,
`ConstraintEvaluationResult.model_validate`, and the public alignment operation
are the existing reconstruction boundary; do not import private derivation
helpers, build replacement green objects, or trust `model_construct` output.
Alignment performs its public pure snapshot validation once for a non-refused
selection and zero times for refusal. Do not separately carry a caller-authored
green snapshot-validation result. Additional internal reconstruction calls made
by accepted lower validators are unchanged, not a new CS guarantee about total
runtime invocation counts.

Independent expected commitments must come from the caller's accepted request
context. Replacing all input results **and** that external context coherently
is outside this proof boundary. A digest is not a signature, source authority,
trusted time or truth. Store-bound EA revalidation, if separately requested by
the application, remains an explicit lower operation and separate disclosure;
it neither participates secretly in policy evaluation nor rewrites historical
captured evidence.

## 6. Input safety, bounds and deterministic evaluation order

No new parser/validator is implemented or claimed verified here. If the consumer
receives untrusted serialized input, its existing request-admission boundary
must enforce the following profile before attempting this protocol. This is a
bounded application obligation, not justification for a new engineering ledger.

Proposed limits are one FC root, one CN root, one EA selection, one policy,
one expected context and one nominated candidate path; at most 128 MiB total
UTF-8 input, 200,000 parsed nodes and depth 128. Count repeated occurrences of
shared objects against work budgets; reject cycles. Policy alone: 16 KiB,
512 nodes and depth 8, with the exact field set above. These are admission
ceilings, not a promise to admit every simultaneously maximal lower result.
All stricter accepted lower limits remain in force: notably FC's 4 MiB
normalized public result boundary and EA's 4,096 in-horizon attempts, 16,384
occurrence members, 16,384 retained artifacts and 64 MiB retained metadata.
Do not truncate a large proof or select a smaller favorable subset to fit.

For serialized input, preflight size/nesting before full recursive parsing;
reject duplicate object keys and non-finite constants. Use exact built-in
scalar/container types, reject exotic mappings, scalar subclasses and objects
with access/conversion hooks. Reconstruct only the exact expected public model
classes if handling in-process results; reject extras/hidden attributes before
dumping. Never invoke arbitrary object's `model_dump`, `__int__`, `__str__`,
iteration or filesystem methods. Reject Boolean-to-integer coercion for every
index, position and duration; a valid Boolean is allowed only in an actual
lower Boolean field. Reject NaN, infinity and numeric durations of any type:
duration inputs are canonical strings, not floats, Decimal objects or integers.
Lower fields retain their own accepted type rules, including finite floats
only where those lower contracts genuinely allow them.

Reject missing, duplicate, extra or reordered carried array material at the
existing public reconstruction boundary. Mapping insertion order is not
semantic; a reordered mapping with identical unique keys is a valid twin.
Do not silently sort authoritative arrays to repair an attack. Recompute all
derived outcomes; never accept a supplied policy permission flag as evidence.
Output diagnostic labels are bounded/value-free, not exception traces exposing
paths, secrets, payloads or policy authorization details.

Deterministic gate order is: structural admission and independent commitment
checks; accepted lower reconstruction and cross-input coherence; EA refusal;
FC applicability; policy applicability/authorization; nominated observation
availability; exact candidate alignment and CN evaluation availability;
required coverage; age availability; age comparison. Selection refusal is
checked before applicability so it cannot be relabelled as stale. Structural
coherence is always first, including incoherent CN material even if EA refused.
Availability-dependent comparisons are not attempted when their lower material
is legitimately absent. Section 7 defines the single primary outcome; lower
facts and reasons remain available even when a later gate is not evaluated.

No filesystem, network, database, connector, store, environment, configuration
lookup or ambient clock access is part of reconstruction or policy evaluation.
Historical policy retrieval and lower query production are explicit caller
work performed before this boundary. Resource exhaustion is rejected input,
never a partial success or an excuse to consult stores.

## 7. Exact decision vocabulary and separation of meanings

These are application decision labels proposed for review, not new exported
backend literals. Apply rows in order after section 6 admission. Earlier rows
exclude later ones, making the primary outcome non-overlapping. Where several
lower problems exist, preserve them in the original lower results and mark
unreached policy checks `not_evaluated`, rather than discard or rewrite them.

| Primary outcome | Exact trigger after earlier gates pass | Policy evaluation; workflow disposition |
| --- | --- | --- |
| `input_or_revision_incoherent` | Malformed/bounded input, unsupported object/scalar, failed public reconstruction, mismatch against independent expected commitments, mixed revision/scope/cutoff, full-record/candidate substitution, fingerprint mismatch or forged carriage. | Not evaluated; refuse this request. Re-querying may be appropriate externally; never call this predicate violation or stale evidence. |
| `evidence_selection_refused` | Valid matching EA selection has `status == 'refused'`. | Not evaluated; withhold and retain exact EA refusal issues. No age or coverage verdict is invented. |
| `applicability_unavailable` | Valid coherent FC is not applicable: not declared, inactive, conflicted, disagreed or inapplicable, with original FC reasons. | Not evaluated; resolve declaration/applicability outside this protocol. Refreshing cannot repair it. |
| `policy_inapplicable` | No policy/authorization supplied, well-formed unsupported policy profile, authorization not established by caller, or coherent authorized policy target differs from the nominated body/VCN. This is distinct from tampering with independently expected policy content. | Not evaluated; request policy/authority clarification. No defaults. |
| `evidence_absent` | Valid matching non-refused EA snapshot selects `no_observation_at_or_before_as_of`, and the corresponding lower observation result coherently discloses absence. | Not evaluated; withhold, report absence, and let workflow decide whether/how to obtain evidence. It is not a stale measured sample. |
| `criterion_evaluation_unavailable` | Honest alignment `multiple_matching_candidates` with otherwise valid inputs prevents unique attachment, or the exact nominated observation is identified but attachment/semantic/value gates or CN prevent an exact `satisfied`/`violated` verdict. Preserve the exact lower `multiple_matching_candidates` reason and `multiple_matches` disclosure, CN `not_evaluated` and its reason, or valid lower non-attachment/unavailability finding. | Not evaluated; withhold. No automatic measurement request is inferred from every CN reason. |
| `coverage_insufficient` | Exact required interval not established or the section 4.2 nonempty/all-attempt condition fails on a valid matching snapshot. | Denied by coverage; withhold usable verdict. Display exact missing interval or failed/omitted/empty/quarantined route disclosures. A new measurement alone may not repair a historical failed window. |
| `age_unavailable` | Earlier gates pass, but an admitted lower contract cannot disclose receipt age under the requested supported age basis. | Indeterminate; withhold. Reserved distinction, currently unreachable for selected EA v1 evidence: legitimate absence is `evidence_absent`, forged missing age is incoherent, unsupported clock policy is inapplicable. Do not invent a v1 example that violates EA to reach it. |
| `evidence_not_usable_under_policy` | Fully admissible applicable nominated evidence and sufficient coverage, but exact receipt age fails explicit inclusive/exclusive bound; reason `receipt_age_exceeded`. | Denied by receipt age; the workflow may request a new acquisition or evidence refresh. No claim that the physical measurement is stale, a new physical measurement is necessary, byte-identical rereceipt is insufficient, or the observation is false. CN verdict retained historically but not currently usable under this policy. No command is issued. |
| `policy_permits_use` | Every gate passes and receipt age meets the explicit bound. CN may be satisfied **or violated**. | Permitted under this policy at C; workflow may report exact nominated CN verdict with applicability, policy and evidence disclosures. |

For legitimate absence or refused selection, a nominal candidate path need not
resolve to an occurrence. A request that independently committed to a different
existing occurrence cannot instead submit absence and pass the coherence gate.
For a present observation, cutoff/scope/content differences are incoherence;
do not misclassify them as CN unavailability. A valid matching candidate with
`not_evaluated` is not an input forgery.

Keep four separate views: lower-layer evidence facts, policy evaluation,
constraint result, and workflow disposition. The exact CN result is retained
even when stale; do not overwrite `satisfied` with `not_evaluated`, and do not
display that historical satisfaction as currently usable. The receipt should
say, for example, “use permitted under policy P at C; governing A violated,”
not “commissioning passed.” Policy permission never means observation truth,
general source trust, criterion satisfaction, physical flow, health, safety,
source agreement, acceptable uncertainty, optimal test choice or hardware
command permission.

## 8. Executable-quality worked design examples

### 8.1 Common admitted-world preconditions

These examples use disposable symbolic material only. `E_A` denotes a complete
publicly reconstructed FC/CN/EA join satisfying section 5, not a hand-built
positive result. Its preconditions can be reproduced under separate future
test authorization using the accepted public producers; no fixture or record
is created by this proposal. All variants must reconstruct their changed lower
results and independently expected commitments; mutating an embedded status,
timestamp, value or digest in place is an attack, not a valid twin.

The reference admitted-world values below are corroborated by the frozen
reconciliation and the accepted FC final verification report, not the
authoritative demo ledger. No disposable-model revision is cited: the accepted
disposable 19-record world existed only in temporary storage and no revision
for it is preserved in any accepted artifact. Examples therefore bind exact
content through full public-result reconstruction and independently retained
expected commitments, never through a quoted disposable revision.
- Governing A VCN `vcn_70b5e146d682db6ca696a9165d0d4521c36ba4324b3d52f96c8a13bae13912cd`;
  B VCN `vcn_3caad214041adad24a48bac3f13767078022329de34e2f46161a745c11c0273e`.
- FMA witness `fma_cd234041b6e1a98b65a33c61b7b742c463a348fcb92f1de912e88de2555cb2cb`.
- Candidate path 0, full occurrence ID `79bcec2f4de12d6e67f657f2e1153637`,
  value `60.1`, receipt `2026-08-07T20:00:06+00:00`, C `21:00:00+00:00`.
- Exact expected EA fingerprint
  `sha256:36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`;
  horizon `19:00:00+00:00`, complete aligned evidence, age 3,594 seconds.

An ID alone never meets these preconditions: full occurrence, FC/CN contents,
scope and all independently bound results must also agree. The accepted
historical satisfied-A twin changed the nominated observed value in a
disposable occurrence; it is not
claimed here to have a separately captured matching EA snapshot. Examples
requiring satisfied A stipulate a newly coherent hypothetical evidence world
with its own full public results, rather than splice that old twin into E_A.

P1 is an illustrative caller policy `commissioning.demo`, version `v1`,
authorization reference `owner.example.v1`, exact A/FM target, inclusive
`max_receipt_age_us = '3600000000'`, `coverage_window_us = '7200000000'`,
and every mandatory literal from section 4. These values are explicit examples,
not silently applicable policy. P2 is a separately authorized example version
`v2` with maximum `'3000000000'`; all unchanged fields remain explicit.

### 8.2 Eight required scenarios and precise expectations

| Example | Exact change to admitted preconditions | Expected primary outcome and retained meaning |
| --- | --- | --- |
| 1. Violated A, receipt-age admissible, covered | E_A with P1. `3,594,000,000 <= 3,600,000,000`; required interval/scope exact; A is violated. | `policy_permits_use`; report **governing A violated**. Never replace it with B's satisfied result. |
| 2. Satisfied A, receipt-age bound exceeded | Coherent separate E_A40 has selected value `40`, A satisfied, same illustrative receipt age/complete interval, independently matching snapshot/occurrence; use P2. | `evidence_not_usable_under_policy`, reason `receipt_age_exceeded`; preserve historical A satisfied but mark it not usable under P2 at C. |
| 3. Receipt-age admissible, incomplete | Coherent E_A includes an additional failed attempt in the required horizon with effective wall time after its selected receipt; no later observation. Age still 3,594 seconds; P1. | `coverage_insufficient`, exact failed route retained. Age cannot upgrade incomplete coverage. Omitting the failure and reusing the old expected fingerprint is incoherent, not this valid scenario. |
| 4. Ungoverned B substituted | E_A's FC, expected A target and EA remain fixed; substitute B's full satisfied CN result. | `input_or_revision_incoherent` at full CRG/VCN join. Valid twin is original violated A, permitted by P1; alternatively an independently approved newly designated B world with its own revision/target/results is a different request. |
| 5. Apparently recent source time | Coherent hypothetical E_A40 discloses source wall-clock `20:59:59+00:00` with its source basis, while selected receipt stays `20:00:06+00:00`; C remains `21:00:00+00:00`, P2. All changed content is independently rebound. | `evidence_not_usable_under_policy`, reason `receipt_age_exceeded`. No subtraction of source time from C, no comparison of clock domains and no one-second rescue. Unavailable or monotonic source time gives the same receipt-age policy result. |
| 6. Selection refusal | Valid matching EA refusal with no snapshot and original integrity/unavailability issue; structurally coherent other inputs, intended scope/C unchanged. | `evidence_selection_refused`; no “stale” finding and no snapshot validation comparison. Valid non-refused P1 twin is example 1. |
| 7. Threshold twins | With E_A fixed, inclusive max `'3594000000'` permits; inclusive max `'3593999999'` fails. At max `'3594000000'`, exclusive fails; exclusive max `'3594000001'` permits. | Respectively permit/not-usable and not-usable/permit (not-usable reason `receipt_age_exceeded`); all differ by one microsecond or the explicit boundary token, not rounding. At age zero, inclusive zero permits and exclusive zero fails, provided zero-age lower selection/coverage are genuinely valid. |
| 8. Historical policy replay | Replay E_A and the independently retained P1 value/version and accepted historical commitments after P2 has been adopted elsewhere. Do not fetch P2 or change C. | `policy_permits_use` **under historical P1 at C**. Same E_A explicitly evaluated under P2 yields `evidence_not_usable_under_policy`, reason `receipt_age_exceeded`. Submitting P2 while the replay context expects P1 is incoherent. No claim about current store membership or today's permission. |

RC-1 valid reused-payload/rereceipt twin: retain the same raw payload and
observation content, including unchanged source time, but obtain a distinct
valid receipt occurrence at `2026-08-07T21:00:05+00:00`. Evaluate its coherently
reconstructed CN/VS/EA/alignment results at C' `21:00:06+00:00`, with independently
bound new occurrence, cutoff and snapshot, and the exact P2-required two-hour
horizon ending at C'. If every captured attempt observed the property and all
other gates pass, receipt age is 1,000,000 microseconds, within P2's explicit
3,000,000,000-microsecond inclusive bound: `policy_permits_use`. Retain every
reused-payload origin/run and seed dependency. No new physical measurement,
changed source observation or observation falsity is established. Keeping the
old occurrence/fingerprint while merely editing its receipt time is instead
incoherent. This valid twin proves why receipt-age failure has disposition
`evidence_not_usable_under_policy`, reason `receipt_age_exceeded`, not a physical
measurement-freshness requirement.

RC-2 valid ambiguity twin: two honest candidate paths carry the same complete
occurrence and all inputs independently match the expected identities,
revisions, cutoff and carried material. Existing alignment honestly reports
`not_aligned`, reason `multiple_matching_candidates`, occurrence relation
`multiple_matches`. The policy outcome is `criterion_evaluation_unavailable`
with those exact lower disclosures retained, not incoherence. Its unique-match
twin aligns and proceeds through the remaining policy gates. Duplicating or
editing a carried candidate in violation of public reconstruction is still
`input_or_revision_incoherent`; the honest ambiguity does not relax validation.

### 8.3 Exact arithmetic oracle, not a new public API

The following standalone design example is deliberately only an arithmetic
oracle **after** all public-result and policy-admission gates. It cannot admit
evidence, validate coverage or defeat substitutions by itself. Its Python
assertions can run in memory without stores, records, fixtures or test files.

```python
from datetime import datetime

received = datetime.fromisoformat('2026-08-07T20:00:06+00:00')
cutoff = datetime.fromisoformat('2026-08-07T21:00:00+00:00')
delta = cutoff - received
age_us = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
assert age_us == 3594000000

# Each limit string below is already strictly admitted under section 4.
assert age_us <= int('3600000000')       # E_A / P1: may use A's violation
assert not age_us <= int('3000000000')   # E_A / P2: not usable; receipt_age_exceeded
assert age_us <= int('3594000000')       # inclusive exact boundary
assert not age_us <= int('3593999999')   # one microsecond over limit
assert not age_us < int('3594000000')    # exclusive exact boundary
assert age_us < int('3594000001')        # one microsecond inside limit
assert 0 <= int('0')                    # zero, inclusive
assert not 0 < int('0')                 # zero, exclusive

# Only after reconstructed EA supplies T and O, never from an untrusted flag:
complete_T, complete_O = (0,), (0,)
failed_T, failed_O = (0, 1), (0,)
assert bool(complete_T) and complete_O == complete_T
assert not (bool(failed_T) and failed_O == failed_T)
assert not (bool(()) and () == ())      # empty population is not complete
```

These assertions illustrate policy arithmetic and the non-vacuous coverage
condition; they do not claim a new end-to-end runtime proof for examples 2–6.
The implementation facts supporting their admitted-world preconditions were
inspected in the existing [EA selection tests](../../../tests/evidence_assurance/test_selection.py),
[EA validation tests](../../../tests/evidence_assurance/test_validation.py),
[EA parity tests](../../../tests/evidence_assurance/test_parity.py) and accepted
FC integration/reconciliation evidence. In particular the live tests distinguish
reused payloads from occurrences, pre-horizon seeds from coverage, failed
attempts from source observations, and exact inclusive receipt cutoffs.

## 9. Alternatives compared and ownership derived

| Alternative | Decision value and authority | Cost/risk; disposition |
| --- | --- | --- |
| No new milestone; consumer composes existing APIs | All exact evidence/engineering inputs and integrity checks already exist. Caller owns its explicit policy and can make the bounded use/not-usable decision; an evidence refresh is a workflow option. | **Recommended outcome 1.** No additional backend architecture is necessary. The policy protocol and review evidence are this design's deliverable. |
| Pure request-carried policy in a new read-only backend composition | Could centralize section 7 labels and arithmetic, with downward dependencies on FC/CN/EA/alignment. No durable identity required. | Rejected for this milestone: no missing integrity property or new consumer capability beyond the same caller computation was demonstrated. Calling it CS instead of FA does not justify a wrapper. An application may use a local pure helper; this proposal does not authorize one or allocate a backend API. |
| Versioned non-ledger policy artifact/configuration plus pure composition | Useful if a real application needs managed distribution/retention and stable historical references across consumers. | Unnecessary now: the caller can retain the full request value/version in its own workflow context. File loading, discovery, latest resolution, signatures, revocation and distribution would add unasked semantics. Version-labelled request data is not a new artifact system. |
| Durable evidence-bearing policy declaration in an existing ledger plus pure composition | Would be appropriate only for a demonstrated durable engineering requirement with an identified issuer, evidence, scope, conflict/supersession/withdrawal semantics and consumers querying that fact. | Rejected: no such new model fact is established. A policy threshold is not automatically VCN semantics, an FCD designation, SPI interpretation or identity binding. No record kind can honestly be overloaded to store workflow permissions. |
| Defer for a lower prerequisite | Necessary if the owner actually requires cadence, authenticated elapsed physical time, multi-source completeness, newly measured rather than re-received content, or physical continuity. | Not the selected outcome for the explicit bounded profile: its required facts are present. Those stronger questions would require a new separately scoped investigation with the exact prerequisites in section 4, not a fabricated Boolean here. |

No package owner is assumed. The semantics belong to the application because
the decision governs *this workflow's use* of evidence. A backend composition
would be a downward leaf if later independently justified; kernel or EA
ownership would invert or pollute accepted responsibilities. Nothing here
requires an authoritative policy record, policy store, durable CS result,
receipt minter, new revision, evidence adapter, registry or generic rule engine.

FA-001 remains cancelled. Its accepted reconsideration rule requires a new
owner-approved proposal demonstrating a concrete integrity attack that existing
public-result validation cannot prevent. Convenience, aggregation, fewer
objects or a consumer omitting a required check are insufficient. None of this
proposal's attacks establishes that missing property.

## 10. Contribution to the seven original objectives

| Original objective | Exact contribution if the caller adopts this explicit protocol | Confidence and remaining gap |
| --- | --- | --- |
| 1. What exists, and how is it connected? | None beyond existing FC/FM/model declarations; exact target is reused, not newly discovered. | Existing strong declared-model answer unchanged; no new physical connectivity evidence. |
| 2. What is the current state of this particular system? | Distinguishes “this nominated criterion verdict is usable at C under P” from historical but too-old or insufficient evidence. | Partial. Policy-conditioned use is decision-relevant but not present physical state, source authenticity, continuity or freshness outside receipt semantics. |
| 3. Why might the system be behaving this way? | Can explain why the workflow withheld evidence (age, coverage, refusal); not why the physical system behaves that way. | Foundational only, unchanged for causal diagnosis. Hypotheses, mechanisms, counterfactual/intervention evidence and uncertainty are missing. |
| 4. What is the next best measurement or test? | Only “this nominated evidence is not usable under policy because its receipt age exceeds P's bound”; the workflow may refresh that evidence path. | Foundational only for the original objective, with one narrow workflow decision. No selection among alternatives and no ranking by information gain, cost, risk, accessibility or diagnostic value. |
| 5. What would be affected by a component, parameter or software change? | Policy/body/VCN mismatch withholds this exact decision; historical policy versions can be compared explicitly. | Existing partial exact-dependency visibility unchanged; no impact traversal, physical propagation or software effect model. |
| 6. What is the smallest valid change set to reach a desired state? | None. Asking for a refresh is neither a state-changing plan nor an optimized action set. | Absent; goals, admissible actions, effects, feasibility and cost/order semantics still missing. |
| 7. Which conclusions are observed, calculated, inferred, assumed or unknown? | Keeps source observations and calculated CN/age separate from caller-authorized policy, missing evidence and withheld permission. | Partial overall; strong traceability within the nominated existing result families. Does not add general epistemic classification, trust, calibration or uncertainty evaluation. |

For genuine next-best-test selection the initial consumer must additionally
name a finite eligible test set, scope/feasibility and accessibility, hypotheses
or target uncertainty, possible outcomes and their evidence-backed likelihoods,
an explicit decision utility/information-gain measure, costs and risks, resource
constraints, ranking/tie/refusal semantics and an external evaluation oracle.
None is supplied by an age threshold, failed-attempt list, graph traversal or
alphabetical sort. This proposal does not claim progress toward “best” merely
by naming a policy contract; indeed it recommends no new backend contract.

## 11. Threat model and acceptance matrix with valid twins

The attacker can submit hostile or coherently substituted carried values but
does not control the caller's independently retained expected context. Loss of
that context is explicitly outside the content-binding proof. A valid twin
means valid input with the stated honest outcome, not necessarily permission.
Rows are review/acceptance obligations for an application adopting the protocol,
not claims that a new CS test suite was run or that new validators exist.

| ID | Attack or false claim | Required rejection/disclosure | Valid twin |
| --- | --- | --- | --- |
| CS-A01 | Substitute criterion anchor, CRG or same-anchor/different-edition VCN, including equal predicate text. | Incoherent full FC/CN record join or stale ID; no predicate verdict from the substitute. | Exact governing full CRG/VCN and independent expected revision, including a violated verdict, remain usable if policy passes. |
| CS-A02 | Substitute same-valued candidate or occurrence, or choose a favorable candidate index. | Incoherent strict path, full occurrence or alignment index; never automatic selection. | Independently nominated candidate and complete matching occurrence, even when another candidate has the same value. |
| CS-A03 | Move cutoff to make the sample younger or use differing CN/VS/EA cutoffs. | Incoherent against independent C and normalized lower cutoffs. | All cutoffs denote the same aware UTC instant, including equivalent legal timezone offsets before normalization. |
| CS-A04 | Replace policy version, authorization reference or threshold, even under the same label/version. | Incoherent against independently retained complete expected policy. | Separately authorized explicit P2 request; P1 historical replay still uses P1 unchanged. |
| CS-A05 | Use a recent source-effective timestamp, HTTP Date or monotonic marker as receipt age; compare clock domains. | Reject asserted receipt-age derivation; disclose original source marker without ordering it against C. | Exact EA receipt age with recent, old, monotonic or unavailable source time has identical age-policy outcome. |
| CS-A06 | Forge a coverage Boolean, route classification or completeness index set. | Existing EA reconstruction/fingerprint and explicit T/O check reject incoherence. | Complete reconstructed nonempty T=O passes; valid incomplete material reports coverage insufficient, not invalid. |
| CS-A07 | Submit only a shorter favorable attempt window or crop a broader snapshot. | Valid wrong horizon: coverage insufficient; edited material with stale commitment: incoherent. No unseen interval completeness. | Exact required interval with every captured attempt retained; a real empty interval reports insufficient. |
| CS-A08 | Drop intervening failed, empty, omitted-property or quarantined attempt while retaining selected observation. | Source/temporal membership, route derivation and expected fingerprint reject omission. | Retain every such route and report coverage insufficient; valid all-property-observed twin passes. |
| CS-A09 | Deduplicate reused payload attempts into one occurrence or omit envelope/run dependencies. | Reject broken occurrence membership/provenance closure; equal payload does not identify receipt occurrence. | Multiple exact attempts referencing one retained payload/observation with complete dependency closure remain valid. |
| CS-A10 | Omit pre-horizon seed or independent source seed fence; count seed as horizon coverage. | Reject closure/membership mismatch or forged coverage; seed cannot fill T. | Exact seed and closure retained outside horizon attempt population; empty horizon is honestly insufficient. |
| CS-A11 | Mix inventories from different source, adapter, subject, endpoint, item or property. | Incoherent seven-field scope or source/temporal parity; no aggregate totals. | One exact scope, six-field consumer locator and EA-derived endpoint closure, with all its captured members. |
| CS-A12 | Edit content but retain old record/observation/fingerprint/content-derived ID. | Accepted canonical/reconstruction checks and independent expected commitments reject. | Genuine correctly derived lower content with its independently nominated new request commitments, not an unauthorized replacement of the old request. |
| CS-A13 | Splice model, binding or interpretation revisions, or infer model membership from C. | Incoherent lower/expected revision comparisons; no automatic revision selection. | Explicit historical memberships used coherently across FC/CN/ES/VS with the same independent context. |
| CS-A14 | Duplicate, omit, add or reorder records, routes, artifacts, candidates, support roots or indices. | Existing outer reconstruction and admission reject noncanonical/incomplete carriage; no silent repair. | Accepted complete canonical array order; mapping key insertion order alone may differ without changing meaning. |
| CS-A15 | Use `True` as candidate index, sweep position or integer duration; numeric-looking scalar subclass. | Reject exact-type violation before coercion/access hooks. | Built-in integer zero in an actual index and canonical string `'0'` in a duration; real lower Boolean fields stay Boolean. |
| CS-A16 | Negative, non-finite, huge, exponent, whitespace, fractional, leading-zero or hostile numeric durations. | Reject lexical/type/bound violations before numeric expansion; value-free diagnostic. | `'0'` and `'31536000000000'` at inclusive bounds; one above maximum rejected; actual finite float fields in lower schemas remain governed by their own contracts. |
| CS-A17 | Off-by-one, rounding, or CN boundary token reused as age boundary. | Derive exact microsecond comparison using explicit policy token only. | All four exact-threshold twins and inclusive/exclusive zero in section 8. |
| CS-A18 | Forge nested public results with `model_construct`, `model_copy`, wrong union, extras, hidden fields, stale derived verdict or a green validation object. | Strict admission and full existing outer reconstruction; policy result must be rederived. | Full correctly reconstructed outer FC/CN/EA and internally recomputed alignment, with all legitimate lower refusals preserved. |
| CS-A19 | Inject cycles, deeply nested/oversized material, custom mappings/accessors or repeated-object amplification. | Bounded preflight before deep parsing/dumping; count work and reject without partial result. | Exact built-in bounded containers and supported model classes at each applicable inclusive limit; one-over twin rejected. |
| CS-A20 | Validation secretly opens a policy file, store, database, network or clock, or reselects newer evidence. | Adopting consumer must show zero I/O/clock calls in this boundary; do not claim captured evidence current. | Carried historical inputs and explicit C produce the same decision with such accesses forbidden; any separate revalidation is explicitly external. |
| CS-A21 | Omit mandatory policy rule, silently assume a threshold/window or fetch “latest.” | Missing policy is inapplicable; malformed supplied policy is incoherent; no permissive default. | Complete explicit policy, including zero values and all fixed semantic literals. |
| CS-A22 | Present satisfied ungoverned B in place of violated governing A and call commissioning passed. | Full FC-to-CN comparison rejects B; display must retain A's violated verdict separately from permission. | Example 1: receipt-age-admissible/covered governing A is usable and violated. A truly newly designated B requires its own complete independently approved context. |
| CS-A23 | Present policy permission as observation truth, source trust, safety/health, physical occurrence, uncertainty acceptance, global optimality or command authority. | Reject interpretation/display claim; policy permission has only section 7 meaning. | “P permits use at C; exact governing A violated; receipt age and bounded attempt coverage disclosed; physical truth/safety not assessed.” |
| CS-A24 | Convert selection refusal, legitimate absence, missing age, inapplicability or unevaluated CN into generic “stale; measure again.” | Preserve distinct ordered outcomes and original reasons; no invented age. | Honest refusal/absence/inapplicability/unavailable outcomes remain valid, while admitted excessive receipt age yields `evidence_not_usable_under_policy`, reason `receipt_age_exceeded`; a new physical measurement is not mandated. |
| CS-A25 | Strip or duplicate lower results to create an apparently self-contained green aggregate without enough reconstruction material. | No CS aggregate accepted as evidence; retain FC/CN/EA roots once and derive alignment from their exact material. | Complete three-root replay with nested lower material unchanged and policy outcome referencing it; no independent green summaries. |

The matrix must not be used to argue that a consumer forgetting these already
expressible checks proves a missing backend contract. Nor does it prove
source authentication when the attacker can replace the expected commitments.
New operational security requirements, if any, need an identified trust root,
not another content-derived CS identity.

## 12. Owner gates, rejected scope and unresolved decisions

No implementation slices are recommended because outcome 1 is selected.
Do not translate this design into a coding plan, reserve an ADR, publish new
exports or commit a demonstration. The next step is only the separately
authorized independent challenger audit and owner disposition of this proposal.
Neither occurs in this turn.

If the owner later wants an application implementation, that requires separate
authorization identifying the actual application consumer code and its existing
request boundary. A reusable backend milestone still requires affirmative
evidence of a missing capability beyond this protocol; convenience alone does
not reopen FA. Any alternative requiring stronger coverage must first resolve
the exact lower prerequisite in section 4. No slice here authorizes a fixture,
ledger append, policy artifact, new record or production default.

Unresolved owner decisions are concrete:

1. Accept or reject the finding that CS needs no new backend milestone, after
   the separately authorized challenger audit.
2. Whether this workflow actually accepts receipt-occurrence age (including
   byte-identical rereceipts), rather than physical measurement age or trusted
   elapsed time that the current contracts do not establish.
3. Supply defensible maximum age, inclusive/exclusive boundary and required
   interval; decide whether nonempty/all-captured-attempts-observed coverage
   for one exact source scope is sufficient. No numerical value is approved here.
4. Identify who authorizes the caller policy, where the caller retains full
   historical values/expected commitments, and whether actual distribution or
   revocation requirements create a separate application configuration task.
5. Confirm the distinct refusal/withheld dispositions and user-facing wording.
   Especially: a past failed coverage window is not automatically repaired by
   a single fresh reading, and a refresh request is not permission to command.

Explicitly not recommended: general next-best measurement/test selection,
ranking, information-gain optimization, causal diagnosis, impact traversal,
goals/actions/desired-state planning, control, multi-criterion aggregation,
alternative-source substitution, physical flow/transition occurrence history,
calibration/uncertainty acceptance, source trust scoring or safety/health verdicts.
FC still determines which explicit VCN governs one exact FM effective body and
whether that designation is applicable under the selected model revision; it
does not acquire any of those excluded meanings through this caller policy.

## 13. Verification, preservation and bounded handoff

Verification for this design consists of fresh baseline/preservation assertions,
live public-surface inspection, the in-document arithmetic assertions, local-link
resolution, numbered-section/ending-marker checks, an exact changed-file
allowlist and whitespace checks. It does not consist of an implemented CS
validator, end-to-end example fixtures, a complete repository test run or a
clean-checkout matrix. Historical 4,074-pass coverage remains historical.

The pre-existing read-only reconciliation checker was run with
`PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 .venv/bin/python /tmp/post_fc001_reconciliation_checks.py`.
It passed before this proposal was written: 22 unique contiguous accepted ADRs,
73 reconciliation-document links, 31 qualified public API references,
36-record load/replay, exact family counts/export digest, six protected tree
inventories covering 65 files, ignored settings and accepted FC report digests.
An initial invocation without `PYTHONPATH=.` could not import `backend`; that
invocation established no result and was corrected without repository changes.
The frozen reconciliation SHA-256 was independently checked with `sha256sum`.

Protected areas are `models/demo-printer`, both demo binding trees,
`interpretations/demo-printer`, `showcases/demo-printer`, ignored `var/raw_store`
and `.claude/settings.local.json`. No original README, guidance, ADR,
specification, acceptance/report, source, test or authoritative/generated
artifact is edited. The only deliverable is this proposal file. Post-write
checks and its exact final size/digest are reported in the terminal receipt;
the file does not try to embed its own hash.

Repository brainstorming informed the alternatives, explicit semantics and
owner gate; verification-before-completion informed fresh evidence and the
limited verification claims. The user's one-file/design-only/no-commit/stop
instructions override the skills' default spec path, commit and implementation
handoffs. Codex worked alone, without delegation or external challenger.
ADR-0023 stays absent and unallocated. No branch, commit, push, merge, rebase,
reset, amend, cherry-pick or history rewrite is part of this task.

END OF CS-001 CODEX LEAD PROPOSAL
