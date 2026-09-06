# EA-001 Slice C1 Expected-Fingerprint Integrity Repair Report

Date: 2026-09-07

Status: bounded C1 integrity repair implemented and verified; owner acceptance
pending; Slice C2 unauthorized

## 1. Authority and verified starting checkpoint

The owner authorized only the bounded expected-fingerprint integrity repair in
`2026-09-07-ea001-slice-c1-integrity-repair.md`. Work ran on branch `ea001`
from exact C1 HEAD
`c94b5629bea928e976779be6cb4cf035264dc88d`; the accepted pre-C1 base remains
`c34fc6868be9a554095b2fb10dae17436c617a71`.

Before editing, `git status --short` was empty for tracked and untracked
repository content. The owner-local `.claude/settings.local.json` appeared only
with `--ignored`, remained untracked and untouched, and had SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.
The original C1 completion report was 13,898 bytes at the required SHA-256
`5c728116fbc458352d9ce7967d3286ce96ce82991e678d1a3469306fb52310e6`.
The corrected proposal matched its pre-repair SHA-256
`dd7200df0ab500a6d1366ae77b629ac13e9c7a710c2b0c63a78b733aeed804a4`.

## 2. Exact reproduction and root cause

The owner reproduction was preserved as a permanent focused regression. At
the exact starting HEAD, a refused selection with an independently supplied
expected fingerprint produced:

```text
not_evaluated selection_refused None mismatched
```

The focused red command was:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/evidence_alignment/test_expected_fingerprint_integrity.py -q
```

It produced `2 failed, 4 passed in 4.58s`. The first failure proved the false
`mismatched` disclosure; the second proved that the required local four-state
alias did not exist. The four passing twins already proved refused-without-an-
expectation, both non-refused comparisons, and the validator-call boundary.

Root cause: `_base_disclosures()` mapped every supplied expected fingerprint
to `mismatched` before checking whether a snapshot comparison could occur. A
refused selection correctly skipped snapshot validation, so that provisional
value survived despite no comparison. The accepted lower
`ExpectedFingerprintRelation` lacks an evaluated/not-evaluated distinction and
could not truthfully represent this upper result.

## 3. Narrow contract and derivation repair

`backend.evidence_alignment.contracts` now defines exactly:

```python
OperationalEvidenceAlignmentExpectedFingerprintRelation = Literal[
    "matched",
    "mismatched",
    "not_supplied",
    "not_evaluated",
]
```

Only `OperationalEvidenceAlignmentResult.expected_fingerprint_relation` uses
this new local alias. The lower EA alias and every lower contract remain
unchanged. `_base_disclosures()` now derives `not_supplied` when the expectation
is absent and `not_evaluated` when it is present but no comparison has yet
occurred. A non-refused selection's one pure snapshot validation overwrites
that field with its actually computed `matched`, `mismatched`, or
`not_supplied` relation.

The repaired exact reproduction prints:

```text
not_evaluated selection_refused None not_evaluated
```

`selection_refused` remains the higher-precedence reason, and refused input
still carries no snapshot validation. The planned C2 root `__all__` is now the
exact ordered nine-name surface from the amended proposal, including the local
relation alias between reason and request. Root exports remain absent; this
repair does not implement Slice C2.

## 4. Red-first repair evidence and valid twins

The test-only red checkpoint is
`78e0de4b15cf585ec02fb0c43ea4297039d8aa01` (`test: reproduce C1 fingerprint
relation defect`). The repair checkpoint is
`867cfb9c4c374f0603ad7db1827ba09d6a511308` (`fix: distinguish unevaluated
alignment fingerprints`).

After repair, the same focused regression file produced `6 passed in 2.95s`.
It proves all four exact relations:

1. refused plus supplied expected fingerprint: `not_evaluated`;
2. refused plus absent expected fingerprint: `not_supplied`;
3. non-refused plus exact expected fingerprint: `matched`;
4. non-refused plus different expected fingerprint: `mismatched`.

Each result reconstructs from plain serialized content with the same relation,
and substitution of a different relation is rejected. The test pins the exact
four-literal order and planned nine C2 names while proving the package still
has no `__all__` and no root-exported C2 names.

## 5. Bounded sibling-field review

The mandatory compact result fields were inspected for the same false-evidence
category. No sibling defect was reproduced. A refused selection leaves cutoff,
scope, and endpoint relations `not_evaluated`; occurrence and seed role are
`not_applicable`; candidate attachment is `not_applicable`; and no selected
index or mismatch list is claimed. An independent expected-fingerprint
mismatch leaves later comparison fields unevaluated or inapplicable. Later
reasons retain only relations actually computed before their precedence gate.

The permanent count test proves that the public store-independent snapshot
validator is called zero times for a refused selection and exactly once for a
non-refused selection. No test or implementation invokes a store query,
reselection, facade, clock, filesystem, or network path.

## 6. Proposal amendment and exact changed files

The corrected proposal was amended only at its result-field type, four-state
vocabulary, derivation event table, C19/C22 acceptance rows, planned C2 exports,
and current owner-gate wording. Its historical pre-repair digest is preserved
above. The amended proposal is 40,385 UTF-8 bytes at SHA-256
`829435ba1f6bff6a27daf1aeb6f1c654257fd20afc4e831c13a7f90478436812`.
The earlier proposal-correction report was not changed.

The bounded repair changes only:

- `backend/evidence_alignment/contracts.py`;
- `backend/evidence_alignment/derivation.py`;
- `tests/evidence_alignment/helpers.py`;
- `tests/evidence_alignment/test_expected_fingerprint_integrity.py`;
- `docs/superpowers/proposals/2026-09-06-ea001-slice-c-integration-proposal.md`;
- the narrow pending-status wording in `CLAUDE.md` and the original C1 report;
- this integrity-repair report.

There is no change to `backend/evidence_alignment/__init__.py`, any lower
production package, accepted synthesis, fixture, evidence, ledger, membership,
or artifact-generation path.

## 7. Focused and relevant verification

All final runtime/test verification ran at exact repair checkpoint
`867cfb9c4c374f0603ad7db1827ba09d6a511308`:

1. Complete `tests/evidence_alignment`: `54 passed in 15.17s`.
2. Accepted EA/lower gate — complete `tests/evidence_assurance`, both focused
   DS-004 repair files, Slice A reproduction/architecture, and temporal
   selection material: `137 passed in 36.56s`.
3. Architecture/no-I/O/import-isolation — alignment isolation, Slice A
   architecture, and EA adversarial contracts: `20 passed in 21.02s`.
4. Relevant observation-compatibility and model-state suites:
   `219 passed in 87.66s`.
5. Immutable committed-ledger, authoritative aggregate, FL reproduction, and
   accepted lower reproduction checks: `18 passed in 167.05s`.
6. `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m compileall -q backend`:
   exit 0 with no output.
7. `.venv/bin/pip check`: `No broken requirements found`; the disabled pip
   cache warning is sandbox-informational only.
8. Applicable documentation/status gate: `26 passed in 3.05s`.

No authorized test column required loopback setup, and no loopback failure
occurred. The full repository and dual clean-checkout matrix were not run or
claimed because they remain in the unauthorized C2 gate.

## 8. Determinism and preservation

The focused hash-seed proof still passes for seeds 1, 7, and 12345. The valid
EA canonical snapshot remains 19,235 bytes at SHA-256
`36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`.
The accepted original lower material remains 24,766 bytes at SHA-256
`ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`,
and the seed-aware lower material remains 11,528 bytes at SHA-256
`494801a6aaed53f49768f9fe143fc7bb80f327fb6a332da3b1a2b0354a12272f`.

The authoritative ledger remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remain `1/1/0`; the record-file aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The FL disclosure remains 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
No historical membership, fixture, evidence, ledger record, or authoritative
artifact changed.

## 9. Git integrity, limitations, and owner gate

Before the documentation/status commit, `git diff --check` and
`git diff --check c94b5629bea928e976779be6cb4cf035264dc88d..HEAD` passed.
The same working and full-repair-range whitespace checks, report line/byte/hash
checks, contiguous-section check, exact ending marker, post-commit focused
gate, and final `git status --short` are recorded in the terminal receipt.

This repair distinguishes only whether the independent expected fingerprint
was absent, compared equal, compared different, or supplied without a possible
comparison. It adds no fingerprint, authentication, store state, selection,
freshness, currentness, physical occurrence, semantic suitability, state,
transition, flow, correctness, or truth claim.

Repaired Slice C1 awaits owner acceptance. Slice C2 exports, final full-suite
and dual-clean verification, upper integration, demonstrations, and ledger
appends remain unauthorized. Nothing was pushed, merged, rebased, reset,
amended, cherry-picked, forced, or history-rewritten.

END OF EA-001 SLICE C1 INTEGRITY REPAIR REPORT
