# Bounded decision-workflow S1 owner acceptance

Date: 2026-09-15

The owner accepts S1: strict canonical input parsing, build-owned limits,
authoritative public reconstruction, exact observation joins, distinct admitted
and unavailable results, and subsequent decimal defense-in-depth. This records
the owner's acceptance, not a release or authorization of S3–S7.

## Verified evidence and authority

Branch `brc-exp001`, administrative checkpoint
`682e0ff5907da3dd543b796b83120c5712d9d587`; accepted implementation/test commit
`160bfc597655fc24b97301b8d1d400df86e68887`. The only following change at that
checkpoint is the administrative completion report. All implementation and tests
are recoverable from Git; no deleted disposable driver is required.

The unchanged [S1 completion report](2026-09-15-bounded-decision-workflow-s1-input-public-admission-completion-report.md)
matches SHA-256 `a9c0dea75c17184d7ce00d40b08d3d3ce842ff44481013851fc9cbd13c9d24ab`.
It records 20 focused and 213 affected passing tests. Acceptance verification
reruns this precise selection to check the recovered admission boundary before S2;
it does not rerun the full production suite.

Result at the unchanged implementation: **233 passed in 43.42s** (20 focused plus
213 affected). All current/historical archive objects recovered in those tests.
The provisioner independently reconfirmed ext4, all ten dependency artifacts and
the approved environment identity. Tests used the new dedicated
`test-workspaces/s2-s1-acceptance-20260915a` directory, not runtime inputs/results.

The [corrected package](2026-09-15-bounded-decision-workflow-candidate-package.json)
is `199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4`;
the [manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json) is
`5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a`.
The [fixture correction record](2026-09-15-bounded-decision-workflow-obs3-decimal-fixture-correction.md)
retains the hostile-decimal, wrong-revision, forged-result and nullable-null
recipe corrections. The original
[package](2026-09-15-bounded-decision-workflow-candidate-package-pre-obs3-decimal-correction.json)
and [manifest](2026-09-15-bounded-decision-workflow-candidate-manifest-pre-obs3-decimal-correction.json)
remain historical evidence, with original digests
`0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365`
and `6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959`.

## Accepted admission order and limits

- Stale snapshot/reference pairing → `SNAPSHOT_COMMITMENT_MISMATCH`.
- Matching enclosing commitment on the hostile nested result →
  `PUBLIC_RECONSTRUCTION_REFUSED`.
- Decimal reparsing follows successful public reconstruction. The current public
  equality invariants make serialized decimal disagreement unreachable; the
  internal defensive seam is tested without mislabeling a forged result valid.

Acceptance does not authenticate source bytes or establish empirical accuracy.
There is no command, projection, policy, retention or replay release in S1.
Backend public ownership and the source-agnostic boundary remain unchanged.

## Separate S2 authorization

The owner's current request authorizes only the existing plan's S2 **raw
projection**: rational/profile validation, gates, effects, Cartesian corners and
raw traces. The approved policy and persistent CPython 3.13/ext4 environment are
unchanged. S2 must return for acceptance. S3–S7 remain unauthorized; IN-001 and
CI-001 remain open and unselected.

END OF BOUNDED DECISION WORKFLOW S1 OWNER ACCEPTANCE
