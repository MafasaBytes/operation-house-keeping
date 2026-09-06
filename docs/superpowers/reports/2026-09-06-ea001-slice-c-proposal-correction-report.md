# EA-001 Slice C Proposal Correction Report

Date: 2026-09-06

Status: bounded design correction complete; implementation unauthorized

## 1. Authority, checkpoint, and ownership resolution

The owner confirmed that the existing untracked proposal
`docs/superpowers/proposals/2026-09-06-ea001-slice-c-integration-proposal.md`
was the intended candidate produced by the earlier authorized design turn. Its
reviewed original form was 618 lines and 36,220 UTF-8 bytes at SHA-256
`60024fd3d5532983584a102b841263aa4ff8b827b1d44a856b267da03d7a765c`.
The correction preserved and amended that candidate; it did not regenerate it.

The work remained on branch `ea001` at
`c34fc6868be9a554095b2fb10dae17436c617a71`. The fail-safe checkpoint report
`docs/superpowers/reports/2026-09-06-ea001-slice-c-design-proposal-checkpoint-discrepancy-report.md`
remains unchanged and untracked at SHA-256
`3b4f9e22d8934e3a33088a02f49c421f07fd8a64169d976941f22b934dc9d402`.

## 2. Owner resolutions incorporated

The corrected candidate records all four owner decisions:

1. The proposed package remains `backend.evidence_alignment`.
2. The sole proposed public function remains
   `align_operational_evidence_with_value_compatibility(...)`.
3. `aligned_with_complete_evidence` and
   `aligned_with_incomplete_evidence` remain distinct successes. The latter
   proves exact occurrence alignment only and is never described as complete,
   usable, current, or assured assessment evidence.
4. Store-bound revalidation is deferred from v1. A caller may separately use
   the accepted EA store-bound API and display its later disclosure, but that
   result neither rewrites nor participates in the pure historical alignment.

There are no unresolved owner decisions. The C1 and C2 implementation gates
remain explicitly owner-gated and unauthorized by this correction.

## 3. Exact contract corrections

The request no longer accepts a caller-supplied `snapshot_validation`. The
pure function instead invokes the accepted store-independent EA validator
internally and carries the computed validation result exactly once in the
output. The `supplied_validation_stale` reason, precedence branch, derivation
logic, and acceptance rows were removed. The dead `snapshot_invalid` result
reason was also removed: structural invalidity in an alleged validated
selection is typed `ALIGNMENT_REQUEST_INVALID`, while independent expected-
fingerprint disagreement remains a structured result. The independent
`expected_snapshot_fingerprint` input remains.

The request no longer carries `store_revalidation`. The result no longer
carries `store_revalidation_status` or `store_revalidation_relation`. The
store-only mismatch reason, precedence branch, and acceptance rows were
removed. No substitute currentness or store claim was introduced.

The proof boundary remains full field-for-field equality of the selected
public `TemporalOccurrence` plus validated EA-internal attempt-to-endpoint
closure. Equality of value, timestamp, name, occurrence ID, checksum, or any
other partial projection alone is insufficient. The function performs no I/O,
clock read, reselection, consumer recomputation, or store access.

## 4. Final ordered public contract

The final request fields, in order, are:

1. `schema_version`
2. `selection`
3. `compatibility`
4. `expected_snapshot_fingerprint`

The final result fields, in order, are:

1. `schema_version`
2. `request`
3. `status`
4. `reason`
5. `snapshot_validation`
6. `evidence_selection_status`
7. `evidence_coverage_completeness`
8. `expected_fingerprint_relation`
9. `cutoff_relation`
10. `scope_relation`
11. `endpoint_closure`
12. `selected_occurrence_role`
13. `occurrence_relation`
14. `mismatched_occurrence_fields`
15. `aligned_candidate_index`
16. `candidate_attachment`
17. `variable_anchor_id`
18. `model_revision_id`
19. `binding_revision_id`

The final status vocabulary, in normative order, is:

1. `aligned_with_complete_evidence`
2. `aligned_with_incomplete_evidence`
3. `not_aligned`
4. `not_evaluated`

The final reason vocabulary and precedence, in normative order, is:

1. `selection_refused`
2. `snapshot_fingerprint_mismatched`
3. `no_selected_observation`
4. `cutoff_differs`
5. `scope_differs`
6. `consumer_observation_absent`
7. `occurrence_content_mismatch`
8. `occurrence_absent_from_consumer_result`
9. `multiple_matching_candidates`

The ordered eight-name proposed `__all__` and the exact function name remain
unchanged. No generic or second-consumer surface was added.

## 5. Multiple-match disposition and repository evidence

`multiple_matching_candidates` is retained because it is independently
reachable through an otherwise valid accepted public
`VariableValueCompatibilityResult`.

Repository inspection found that `VariableStateResult` in
`backend/model_state/contracts.py` requires discovery candidates to have the
correct origin, requires `declared_locator_count == len(candidates)`, and
derives `selection="multiple"` from cardinality, but does not impose candidate
or locator uniqueness. `VariableValueCompatibilityResult` in
`backend/observation_compatibility/contracts.py` requires equal tuple lengths
and index-parallel equality to the carried state candidates, but likewise does
not impose uniqueness. A fully reconstructed valid discovery result can
therefore duplicate one valid candidate in both index-parallel tuples, set the
count to two, and reach two exact occurrence matches. The corrected contract
returns `not_aligned / multiple_matching_candidates` and chooses no index. Its
one-copy valid twin aligns normally.

This reachability is a public-contract property even though the accepted
facade's ordinary locator-discovery path does not emit duplicate locators.

## 6. Acceptance-matrix reconciliation

The corrected adversarial matrix contains 40 rows, numbered contiguously
`C01` through `C40`. Removed rows covered only caller-supplied validation or
store-bound revalidation. The retained rows give every status and reason an
independently reachable case and a valid twin, including complete and
incomplete successes, refused and fingerprint-gated non-evaluation, all
non-alignment reasons, strict reconstruction failures, the reachable duplicate
case, import isolation, no-I/O/no-reselection behavior, determinism, public
surface, and preservation.

The implementation plan remains a two-gate, owner-controlled proposal. This
turn does not authorize either C1 or C2.

## 7. Integrity, preservation, and corrected artifact

The corrected proposal is 649 lines and 38,851 UTF-8 bytes at SHA-256
`dd7200df0ab500a6d1366ae77b629ac13e9c7a710c2b0c63a78b733aeed804a4`.
Its numbered sections are contiguous from 1 through 15 and its exact ending
marker is present.

The accepted EA synthesis remains byte-identical at SHA-256
`557b2df9aec5ee784006bfdba771936ae90844ea7cf8913c1e61455fa4a7e08e`.
No accepted specification, implementation file, test, fixture, evidence,
ledger, model record, artifact, or history was changed. No commit, push,
merge, rebase, reset, cherry-pick, amendment, or other history operation was
performed. `.claude/settings.local.json` remains untouched.

END OF EA-001 SLICE C PROPOSAL CORRECTION REPORT
