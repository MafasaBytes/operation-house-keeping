# TA-001 Slice A Owner Acceptance

Date: 2026-09-07

Status: corrected TA-001 Slice A owner accepted; Slice B adversarial hardening
authorized; TA-001 final acceptance pending

## 1. Accepted implementation and contract

The owner accepts corrected TA-001 Slice A at the exact tested implementation
commit `76738ac0d098eb59b0fec4f6970aa862528647d9`. The accepted implementation
is the pure `backend.transition_assessment` leaf with the exact ordered
28-name public surface, bounded reconstruction, exact carried-result joins,
strict evidence and expected-fingerprint gate, authoritative result
reconstruction, and bounded endpoint-pattern conclusions.

The governing corrected synthesis remains
`docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md`
at SHA-256
`3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`.
The documentation-only descendant at the time of acceptance was
`b9e506fe918fee860707cd57e08502e62194c3dc`; it changed package and project
status documentation only and is not substituted for the exact tested
implementation checkpoint.

## 2. Frozen completion evidence

The accepted completion report is
`docs/superpowers/reports/2026-09-07-ta001-slice-a-completion-report.md`.
Before this acceptance commit it was verified as exactly 453 lines and 24,820
UTF-8 bytes at SHA-256
`f0fadaeefff2614f270a3be1343b92dfe6f754d90837cfae2c0b602f82e55c82`.
Its 20 numbered sections are contiguous and its required ending marker is
present. The report is committed without changing its reviewed bytes.

The bounded contract-correction and owner-resolution report remains 163 lines
and 7,884 UTF-8 bytes at SHA-256
`10605da5dd2a104db2daf883f1bb19d5276ede996af6a6e225ce1934848cb5ff`.

## 3. Accepted R1 and R2 decisions

R1 is accepted exactly as implemented: structural preflight admits only exact
built-in finite floats, nominal lower reconstruction remains authoritative for
legal field positions, and deterministic private canonical bytes preserve the
built-in `float.__repr__` JSON-number token. Float subclasses, NaN, both
infinities, and floats in non-float positions reject through the sole typed
input error.

R2 is accepted exactly as implemented: corrected T43 treats an alternate
evidence-alignment candidate index as malformed lower content and raises
`TRANSITION_ASSESSMENT_INPUT_INVALID` before TA derivation. Candidate zero is
the accepted valid twin. No multi-candidate lower behavior is invented.

## 4. Verification accepted by the owner

The owner accepts the completion report's exact implementation verification:
57 focused TA tests; 1,905 affected lower and integration tests; 39 dedicated
architecture and isolation tests; and a working all-extras repository run of
3,737 passed. The separate fresh base-only column recorded 3,701 passed, 35
expected optional skips, and one sandbox-denied loopback setup error, followed
by the separately permitted exact loopback rerun passing 1 test. The separate
fresh all-extras column recorded 3,736 passed and the same one sandbox-denied
loopback setup error, followed by its separately permitted exact rerun passing
1 test. Explicit CAD, STEP, and PDF coverage passed 120 tests.

The five deterministic environments and required hash seeds reproduced the
same private TA result at 195,429 bytes and SHA-256
`1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`.
Compilation and dependency checks passed in working, base-only, and all-extras
environments. This acceptance preserves the report's split accounting: a
sandbox setup error is not relabelled as an uninterrupted aggregate pass.

Immediately before this administrative acceptance, the accepted Slice A
focused gate passed 57 tests in 146.24 seconds and the six-file
documentation/status gate passed 26 tests in 1.98 seconds.

## 5. Preservation receipt

The authoritative model remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remains `1/1/0`, TRG/TRD/TRW remains `0/0/0`, the ledger aggregate
remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`,
and the FL disclosure remains 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
The accepted lower reproductions remain 24,766 bytes at
`ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`
and 11,528 bytes at
`494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f`.

## 6. Slice B authorization and limits

The owner separately authorizes TA-001 Slice B adversarial hardening and final
verification only. Slice B must close every corrected T01-T74 row, preserve
the exact ordered 28-name public surface and meanings, repair genuine defects
red-first only inside `backend.transition_assessment`, and complete the
working plus dual-clean verification matrix. Any required lower production or
public-contract change is a discrepancy stop.

This authorization adds no facade, second consumer, demonstration, fixture,
artifact, occurrence model, store, persistent identity, ledger append, or
lower migration. Positive worlds remain disposable and uncommitted.

## 7. Acceptance boundary

This record accepts Slice A, not final TA-001 completion. Final TA-001
acceptance remains owner-gated after Slice B's completion report and exact
tested implementation are reviewed. TA-001 has no Slice C or demonstration
slice.

No acceptance here turns a bounded positive or negative endpoint-pattern
assessment into transition occurrence or non-occurrence, temporal cohort,
continuity, causality, flow, correctness, safety, diagnosis, recommendation,
control, authentication, or physical truth.

END OF TA-001 SLICE A OWNER ACCEPTANCE
