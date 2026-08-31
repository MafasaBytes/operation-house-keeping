# ST-001 Slice C — Evidence-Gated State Classification Plan

Status: ST-001 complete, owner accepted, adversarially reviewed, full-suite verified, and dual-clean-checkout verified.

The preceding implementation gate was recorded exactly as: ST-001 Slices A-D are implemented and verified; Slice D final owner acceptance is pending.

Date: 2026-08-31

## 1. Scope

Implement only the read-only `backend/state_classification` package and one
`StateClassificationQueries.state_classification()` method. Compose the public
`ConstraintEvaluationQueries` facade over its exact loaded-model membership.
Do not change accepted kernel, CN, model-state, semantic, temporal, binding,
fixture, ledger, or artifact behavior.

## 2. Public-contract red phase

Add failing tests that pin:

- exact three-error tree and two codes;
- exact 15-name ordered `__all__`;
- exact facade constructor and single method signature;
- exact six literal contracts and nine refusal reasons in order;
- exact field order for source, refusal, condition, and outer result;
- frozen, extra-forbidden, full-instance reconstruction;
- absence of aliases, lower exports, transition vocabulary, and later APIs.

Record the red count before adding production code.

## 3. Request boundary and scheduling

Implement typed validation for canonical `sta_` identity, exact
`AssertionContext`, aware UTC-normalized cutoff, and source rows. Rebuild source
rows from field content and reject hidden Pydantic extras. Canonicalize valid
rows by constraint ID.

Reach the model only through
`constraints.semantic.compatibility.state.model`, construct public
`ModelQueries`, and obtain state lookup/declaration for exact context. An
unregistered state admits only an empty source tuple and schedules no CN call.
A registered state requires exact equality with the permanent SRG constraint
set.

Schedule each condition exactly once in canonical order, with the permanent
subject entity and identical normalized cutoff. Attempt all branches, retain
typed failures by index, then propagate the first failure in canonical order
unchanged.

## 4. Store-independent authoritative derivation

Implement one private deterministic derivation shared by facade construction
and public result validation. It must:

- revalidate the carried `StateDeclarationResult`;
- rebuild its model in memory and rerun public `ModelQueries`;
- reconstruct every public `ConstraintEvaluationResult`;
- verify model/binding/interpretation/cutoff/selector/candidate coherence;
- derive one admitted active STD effective-body group without choosing a
  declaration winner;
- derive strict VCN-pin alignment without comparing CN bodies;
- map CN candidate verdict to condition outcome;
- derive coverage, temporal alignment, refusals, execution, and optional
  all-of match exactly;
- carry lower results once and use strict indices in condition rows;
- perform no store, filesystem, network, clock, environment, or write action.

## 5. Lifecycle, pin, and truth tests

Use disposable evidence worlds to independently prove:

- unregistered, not-declared, inactive, conflicted, and declared states;
- corroborating independent STD roots execute from one effective body;
- condition absent, CN not-declared, strict CN conflict, superseded pin, and
  exact-current alignment;
- all-satisfied, all-known-with-violation, violation-plus-unknown, and
  no-violation-plus-unknown rows of the three-valued all-of table;
- multiple state calls may both match without aggregation;
- independent evidence remains carried for lifecycle-refused states.

The strict CN-conflict fixture must use two parentless current
engineering-identical VCNs, a state pin naming either, and satisfying evidence;
the result remains conflicted/incomplete/not-executed with no match.

## 6. Hostile reconstruction and authenticity

Attack every outer and nested field using serialized substitutions,
`model_construct`, `model_copy`, hidden extras, booleans/coercible indices,
wrong union arms, mixed revisions/cutoffs/selectors/candidates/occurrences,
missing/duplicate/extra/reordered rows, forged pins/outcomes/refusals/coverage/
execution/match, and disabled store/filesystem/network capabilities.

Create a new ST-specific coherent lower-evidence mutation test. Demonstrate
that ST detects inconsistencies derivable from carried public material, but
does not claim authentication of uncaptured raw payload content accepted by
lower public contracts.

## 7. Bounded internal review

After the first green implementation, request three read-only reviews:

1. architecture and public-facade dependency review;
2. backend derivation/scheduling/truth-table review;
3. adversarial reconstruction and coverage review.

Reproduce every confirmed finding red-first, repair it, and retain the
regression. Do not broaden into Slice D.

## 8. Documentation

Document the classifier in its package README and update applicable ST status
documentation to: Slice C implemented and adversarially reviewed; awaiting
owner acceptance. Retain explicit non-claims, independent temporal policy,
authenticity limitation, and Slice D prohibition.

## 9. Verification

Run focused Slice C, all ST, kernel, CN and affected downstream, architecture,
replay/artifact, compile, full repository, base-only clean checkout,
all-extras clean checkout, PDF/STEP/OCP, loopback permission reruns when needed,
both diff checks, and branch/status/topology checks.

## 10. Stop gate

Commit in reviewable groups. Write and separately commit the file-first Slice C
completion report. Stop for owner acceptance and separate authorization of
Slice D pre-append rehearsal only.

Implementation completed through the exact public CN facade chain. Internal
reviews identified and closed stale lower-model projections, hidden nested
extras, forged context extras, coercible cutoffs, deep/cyclic hostile payloads,
and obsolete import-isolation expectations. Every repair is retained as a
regression. The public closure rules make condition-level `not_registered` and
`not_declared` branches defensive-unreachable in valid SRG/STD material; the
implementation keeps them fail-closed without constructing invalid private
models for coverage.

Slice C is owner accepted at
`f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6`. This acceptance authorizes only
the separately bounded Slice D pre-append rehearsal and does not authorize an
authoritative ledger append.

Subsequent status: the owner approved the corrected frozen Slice D contract
and separately authorized the exact SRG-then-STD append. It produced the
34-record revision
`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
final Slice D owner acceptance was pending at that gate.

## 12. Final ST-001 owner acceptance

The owner grants final acceptance at implementation HEAD
`0f05903af4f11fd94d6e6987247ceb9795faebd6`. The exact 34-record revision and
SRG-then-STD append are accepted with no STW or additional record. The accepted
completion-report SHA-256 is
`2ccc501a4ff7c930518e75adc6f991cbb585637e04dbd768bca713cfbcce24b3`.
This later status does not alter the historical Slice C scope or stop gate.

END OF ST-001 SLICE C IMPLEMENTATION PLAN
