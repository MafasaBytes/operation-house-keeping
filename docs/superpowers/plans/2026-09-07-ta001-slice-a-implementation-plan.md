# TA-001 Slice A Implementation Plan

Date: 2026-09-07

Status: executable plan for owner-authorized Slice A; Slice B unauthorized

## 1. Authority and starting point

Implement only Slice A from
`docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md`
at accepted SHA-256
`99db3b31f5fa94eb119b32529784a64aff08c604f71ee9eb7530225963816062`.
The accepted slice base is
`a4754d8659c08af8fb86bf18bd3c5aac4ea355fe`; the administrative authorization
commit is the documentation-only descendant recorded immediately before this
plan.

The implementation creates only `backend.transition_assessment`, focused
tests, its README, necessary current-status wording, and an uncommitted
completion report. No lower contract, authoritative record, fixture, evidence,
membership, artifact, facade, demonstration, persistence, or occurrence model
may change.

## 2. Red-first test layout

Create the following focused test modules before their corresponding
production behavior:

1. `tests/transition_assessment/test_public_contracts.py` — exact Section 11
   errors, literals in normative order, model field order/types, frozen/extra
   behavior, strict indices, and exact ordered 28-name root `__all__`.
2. `tests/transition_assessment/test_preflight.py` — iterative aggregate
   graph admission, cycles, active-path sharing, strict scalar admission,
   hidden Pydantic state, node/depth/byte/cardinality limits, exact-limit and
   limit-plus-one private-walker twins, and rejection before lower work.
3. `tests/transition_assessment/test_derivation.py` — disposable public lower
   worlds for the exact transition/classification/alignment join, positive and
   negative executed conclusions, ordered cutoffs, exact declaration and
   endpoint admission, strict fingerprint gate, complete/incomplete/refused
   evidence, absent observations, traces, issues, and carry-once behavior.
4. `tests/transition_assessment/test_revalidation.py` — full nested
   reconstruction from plain serialized values and rejection of constructed,
   copied, hidden, substituted, stale, reordered, duplicated, boolean,
   out-of-range, wrong-union, and divergent semantic/value-index results.
5. `tests/transition_assessment/test_isolation.py` — root purity, exact public
   imports, no reverse consumer, no private lower import, no filesystem/store/
   database/network/connector/environment/clock/write access, and absence of
   facade, identity, persistence, fixture, artifact, or demo paths.
6. `tests/transition_assessment/test_determinism.py` — accepted construction
   permutations, normative tuple rejection, independent disposable roots, UTC
   normalization, and byte-identical private canonical result serialization
   under `PYTHONHASHSEED` 1, 7, and 12345.

Programmatic positive worlds may live only in
`tests/transition_assessment/helpers.py`. They construct valid lower results in
memory or temporary directories during each test and never add committed
model/evidence/result fixtures.

## 3. Contract and public-surface task

Write failing tests for the complete Section 11 surface before creating
production files. Implement:

- the exact exception tree and sole input error code;
- all 18 status/relation aliases and the 22-code issue vocabulary in the
  accepted literal order;
- `TransitionAssessmentPolicy` and `TransitionAssessmentLimits` with exact
  fixed fields and literals;
- the request, issue, condition trace, endpoint disclosure, and result models
  with exact field order, strict types, frozen instances, forbidden extras,
  and always-revalidated instances; and
- the exact ordered 28-name package export surface with no alternate names.

Commit the red test state separately from the first implementation green.

## 4. Bounded reconstruction and preflight task

Implement a private iterative preflight before model dumping, plain copying,
canonical encoding, lower reconstruction, equality, fingerprint access, or
derivation. It must:

- accept only ordinary mappings/sequences/scalars and expected public models;
- reject hostile scalar subclasses, non-string keys, unsupported containers,
  hidden/extra/private model state, and boolean index/count values;
- track active-path identity for cycles while counting a shared acyclic
  subtree once per serialized occurrence;
- count root depth as zero and refuse at depth 129;
- use one aggregate request budget and refuse at node 200,001;
- incrementally count canonical JSON contributions and refuse at byte
  134,217,729 without retaining an oversized full copy; and
- enforce two endpoint classifications, at most 64 conditions per endpoint,
  at most 128 traces, and at most 128 distinct alignments.

Expose no public limit override. Focused tests use injected private limits for
precise inexpensive boundaries while separately pinning production constants.

After admission, build one ordinary graph, reconstruct every lower object
through its nominal public model, publish working state only after all nested
objects succeed, and require serialized-shape equality except accepted UTC
normalization.

## 5. Exact carried-result join task

Derive traces in from-then-to condition order. For each condition:

1. resolve `constraint_evaluation_index` inside the endpoint classification;
2. resolve the classification candidate inside that exact CN result;
3. derive `semantic_candidate_index` from the CN candidate;
4. independently derive `value_candidate_index` from the validated semantic
   result's positional correspondence with its complete carried
   `VariableValueCompatibilityResult`;
5. obtain the complete compatibility object and governing bound occurrence;
6. require the exact alignment collection entry whose request carries that
   complete compatibility;
7. require the alignment candidate index to equal the derived value
   coordinate only after complete-object equality; and
8. disclose the lower selection, coverage, occurrence role, alignment, and
   expected-fingerprint relations without reselecting evidence.

Build the distinct alignment collection in first-governing-trace order; equal
complete compatibilities are carried once and may be cited by multiple traces.
An observation-absent trace has no alignment and uses exact `not_applicable`
arms. Missing, duplicate, extra, reordered, or substituted alignment
collections are typed malformed input.

## 6. Admission, issue, and conclusion task

Independently derive:

- transition anchor, lifecycle conclusion, healthy single effective-body
  admission, exact context, complete model revision equality, endpoint pins,
  declared state anchors, subjects, and classification cutoffs;
- cutoff relation and strictly earlier-to-later execution order;
- endpoint classification execution, coverage, and match values;
- evidence completeness without allowing fingerprint state to rewrite it;
- every applicable issue in the exact Section 11 precedence, endpoint,
  condition, and alignment-index order;
- fixed source-time, non-cohort, and continuity disclosures; and
- execution and the bounded support/non-support conclusion table.

Both positive and negative execution require every governing observed
condition to be aligned with complete evidence and an independently supplied
expected fingerprint whose relation is `matched`. No incomplete, refused,
absent, mismatched, or ambiguous support is silently dropped.

## 7. Authoritative result reconstruction task

`DeclaredTransitionAssessmentResult.model_validate(...)` must run the bounded
request reconstruction once, derive the complete expected compact result
without I/O, and compare every supplied scalar, relation, endpoint row, trace,
issue, execution state, and conclusion. It must reject stale, forged,
duplicated, missing, reordered, substituted, boolean, out-of-range, and
semantic/value-coordinate-divergent content.

The public function accepts only the reconstructed request, calls the pure
derivation once, and returns the exact result. Any malformed input maps to
`TransitionAssessmentInputError` with fixed safe text; valid lifecycle and
relational failures remain structured results.

## 8. Architecture and determinism task

Production imports are limited to the public roots of `backend.model_kernel`,
`backend.state_classification`, and `backend.evidence_alignment`, plus
Pydantic and the standard library. No existing package may import TA. Root
import and every public boundary must remain deterministic, synchronous,
offline, and side-effect free.

Private canonical test bytes use the accepted result JSON graph, sorted keys,
compact separators, UTF-8, no NaN, normalized UTC `Z`, shortest exact
fractions, and no final newline. They create no public fingerprint, identity,
receipt, or persisted artifact.

## 9. Commit sequence and review

Use small forward commits in this order:

1. administrative Slice A authorization;
2. this executable plan;
3. failing exact-contract/public-surface tests;
4. contract/public-surface implementation;
5. failing preflight/limit and disposable join tests;
6. preflight and pure derivation implementation;
7. failing result-reconstruction and isolation/determinism tests;
8. authoritative reconstruction, architecture, and deterministic-byte
   implementation;
9. red-first repairs for any genuine independent-review defect; and
10. durable package/status documentation, leaving the completion report
    uncommitted.

After first green, obtain bounded independent architecture, test, and hostile-
input reviews. Reproduce each genuine defect as a failing permanent test before
repair. Do not restart design or expand into Slice B.

## 10. Verification and stop conditions

Run the complete `tests/transition_assessment` suite plus exact public,
preflight, derivation, reconstruction, isolation, and determinism subsets.
Then run affected state-classification, evidence-alignment,
evidence-assurance, model-kernel, and architecture suites; compilation and
dependency checks; the working full suite; separate fresh base-only and all-
extras full suites; explicit CAD/STEP/PDF tests; hash-seed reproductions;
immutable ledger/lower-artifact preservation; settings digest; and working and
full-Slice-A `git diff --check`.

Record sandbox loopback setup failures separately from permitted exact reruns.
Do not claim any column not actually run.

Stop and write a discrepancy report instead of continuing if the accepted
join requires a private or missing lower fact, a lower contract change, a
public signature/literal/field/export change, reset of aggregate limits per
child, unsafe allocation, a new dependency direction, or any authorized-scope
expansion.

On success, update the package README and only necessary current status to say
`TA-001 Slice A implemented and adversarially reviewed; awaiting owner
acceptance.` Write the complete uncommitted Slice A completion report and stop
for the owner. Slice B remains unauthorized.

END OF TA-001 SLICE A IMPLEMENTATION PLAN
