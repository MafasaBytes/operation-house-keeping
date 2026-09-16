# Governed workflow integration — slice-allocation discrepancy

2026-09-16. **Not an implementation completion report.** First-slice owner
acceptance is recorded separately. No implementation or tests were performed in
this turn; no unchanged first-slice test results are offered as new verification.

## Verified starting evidence

- Starting administrative HEAD: `db402a6766ed889a74da1771c46ae6dea2c748c3`.
- Accepted executable HEAD: `949e96e5ff27c6eed041e1f25352c3a94d40714e`.
- Unchanged completion report SHA-256:
  `8d1a18713b10f4ca78044851f2e784267482cf6389b4b57b875be9384552c3ce`.
- Consolidated manifest and readiness commitments are respectively
  `56b53c7bdc02c6687e1eb50942e5ecc3080407758872b1bc0c56d6b1743ae075`
  and `d3a920f45b43af6e53629c51b27c84fb7749133ec15d8e10b3463d12feb47521`.

No first-slice owner-acceptance record was found in the current records or history
of its intended path. The new record reuses the existing authority/evidence chain
and does not modify the completion report. Only that record was staged for its
separate commit. The current owner instruction supersedes the old authorization
gate for slice 2; the discrepancy below is not reliance on that obsolete gate.

## Named next slice and concrete boundary conflict

The governing [plan](2026-09-16-maintained-admissibility-consolidation/CONTRACT-AND-PLAN.md)
lines 276–279 defines slice 2 as **“integrate all governed paths and 23-row review”**
and assigns **“bounded retention/replay and actual build-bound acceptance
preparation”** to slice 3. Only the first slice has detailed independent exit
criteria there. The global contract is substantially specified; allocation of the
following indispensable integration prerequisites between slices 2 and 3 is not.

| Slice-2 path under the global contract | Required dependency | Existing implementation |
| --- | --- | --- |
| Completed governed evaluate, including denial | Complete governed bundle; no success receipt before publication | Legacy publisher emits `schema_version=bdw001.1`, with legacy limits and shape |
| Comparison/current and historical gate review | Complete matching-build prior closure, exact manifest references, reconstruction and work-evidence checks; no omitted ancestor | Pure admission refuses comparison-bearing I; legacy comparison adapter understands only legacy retained nodes |
| Governed replay, included in “every supported governed entry point” | Historical version selection, complete original closure, semantic replay and independent physical evidence; new publication | Explicitly assigned to slice 3; no governed adapter exists |

These requirements are explicit in the plan's completed-output table, comparison
rule and instrumentation/retained-bundle sections, and design sections 8–9. The
maintained implementation confirms the dependency: `governed_admission.assess`
rejects non-null comparison; `cli._recover_valid_shape` expects the legacy
request/snapshot/prior container; `retention._publish_bundle` and `_verify_bundle`
produce/check the legacy manifest. This is not a demonstrated backend gap and
does not justify any backend extension.

It would be possible to implement a **partial internal review kernel** now, but
that is not completion of the literal all-paths slice. Conversely, making all
listed operations complete would implement work expressly left to the
unauthorized third slice. Merely wiring refusal stubs is not semantic coverage
of W0 → D1-X → D2-X. Returning success without publication, silently deleting I's
comparison, trusting an `already_admitted` flag, or reusing a legacy bundle under
governed labels would contradict approved contracts.

The missing authority is therefore an explicit **slice-2/slice-3 interface and
acceptance boundary**, not approval of numerical semantics or resource limits.
No numerical, equality, authority, limit or dependency amendment is proposed.

## Minimum recommended clarification

Authorize slice 2 as the internal governed workflow/review kernel, including
bounded **in-memory reconstruction and validation of complete captured governed
prior closures** as its necessary prerequisite. Require admission of every
current/ancestor before numerical dispatch, 23 slots with exact blocked/unavailable
semantics, all numerical comparison transitions, deterministic aggregate review
accounting and separately observed physical work. Keep W0/D1-X/D2-X and the four-pair
and unavailable twins as mandatory kernel acceptance obligations, not substitutes
for later retained end-to-end proof.

Specify that this slice exposes only a non-published internal assessment API;
production CLI activation, filesystem capture/publication, verify/replay command
completion and actual retained build-bound proof remain slice 3. All supported
internal nomination/working/hypothetical/comparison routes must gate; no governed
CLI success or end-to-end enforcement claim is made before slice 3. This is a
proposed allocation, **not recorded owner approval**. The alternative is to
authorize the required retention/replay integration now, which would expand the
currently authorized slice and is not assumed.

## Preservation, verification and next gate

Read-only inspection covered the complete consolidated plan and approved amendment,
readiness, relevant governing design clauses and admission/build/resource,
decision-review, policy, CLI and retention source contracts. No runtime evidence
was generated, no numerical command executed, and no dependency acquired.

The exact 242-entry untracked status matched the accepted status receipt after the
acceptance commit. Application/backend sources, frozen report and preparation
bytes, persistent environment, runtime inputs/results, provisioning, dependencies
and ledger were not written. Changes in this turn are documentation only.

No newly tested executable HEAD exists. The previously accepted executable HEAD
remains as above; this report's administrative commit is identified in the receipt,
not circularly embedded in its own bytes. There are no new runtime measurements
or red/green results to claim. One consolidated scope-allocation finding remains.

**Owner gate:** approve the explicit kernel/closure boundary above (or explicitly
authorize the necessary slice-3 dependencies). Then implement and verify that
bounded slice red-first. Acceptance of a newly completed slice is not requested
because slice 2 has not been implemented. IN-001 and CI-001 remain open/unselected.
