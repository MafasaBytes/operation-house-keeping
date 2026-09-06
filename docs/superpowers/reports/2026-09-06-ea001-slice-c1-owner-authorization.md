# EA-001 Slice C1 Owner Authorization

Date: 2026-09-06

Status: corrected Slice C design owner approved; Slice C1 implementation only
authorized; Slice C2 unauthorized

## 1. Accepted design

The owner approves the corrected bounded EA-001 Slice C design in:

`docs/superpowers/proposals/2026-09-06-ea001-slice-c-integration-proposal.md`

Its verified SHA-256 is:

`dd7200df0ab500a6d1366ae77b629ac13e9c7a710c2b0c63a78b733aeed804a4`

The correction report is:

`docs/superpowers/reports/2026-09-06-ea001-slice-c-proposal-correction-report.md`

Its verified SHA-256 is:

`eac53c09eacaa6b47a29f6248a313540a56061e88761cb6ccf848835ab4fec56`

The checkpoint-discrepancy report remains a valid, unchanged audit record at
SHA-256
`3b4f9e22d8934e3a33088a02f49c421f07fd8a64169d976941f22b934dc9d402`.

## 2. Authorized implementation boundary

This decision authorizes Slice C1 only: the exact contracts, pure derivation,
and red-first adversarial tests described by the corrected proposal. It permits
only the new `backend.evidence_alignment` leaf implementation needed for those
definitions, focused tests, a concise plan, and a completion report.

Slice C2 root-package public exports, final full-repository and dual-clean-
checkout verification, authoritative demonstrations, fixtures, ledgers,
artifacts, and every other upper-layer integration remain unauthorized. No
accepted lower contract or implementation may change.

## 3. History and preservation boundary

The accepted implementation base is branch `ea001` at
`c34fc6868be9a554095b2fb10dae17436c617a71`. Local forward commits are
authorized. Push, merge, rebase, reset, amend, cherry-pick, force operations,
and history rewrites are not authorized. `.claude/settings.local.json` remains
owner-local, ignored, untouched, and outside the milestone.

END OF EA-001 SLICE C1 OWNER AUTHORIZATION
