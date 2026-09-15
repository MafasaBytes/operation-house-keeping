# S5 retention fixture correction

Under the owner's preauthorization for uniquely determined fixture/reference
corrections, three preparation recipes are corrected. No semantic input, S1–S4
expectation, diagnostic catalogue, resource limit or dependency changes.

The governing design §§9–11 and the plan's frozen diagnostic catalogue name a
distinct diagnostic for each failure stage. RET-3 previously used the write-failure
diagnostic for all six nominated stages; RET-4 used directory-fsync failure for both
directory and parent fsync. The `/expected` object now contains
`by_fault_boundary`, mapping each already-nominated boundary to its exact existing
catalogue diagnostic, exit, stdout and bundle state:

| Boundary | Diagnostic |
| --- | --- |
| create (file inside owned directory) | RETENTION_CREATE_FAILED |
| write | RETENTION_WRITE_FAILED |
| flush | RETENTION_FLUSH_FAILED |
| file_fsync | RETENTION_FILE_FSYNC_FAILED |
| rename | RETENTION_RENAME_FAILED |
| manifest_before_rename | RETENTION_MANIFEST_FAILED |
| directory_fsync | RETENTION_DIR_FSYNC_FAILED |
| parent_fsync | RETENTION_PARENT_FSYNC_FAILED |

PATH-1-manifest-extra previously invoked evaluate without any prior/bundle input,
so its manifest attack was not reachable. `/input/argv` now specifies `verify
--bundle CORRUPT_BUNDLE`. A baseline request/snapshot/result/trace `bundle_recipe`
replaces unused evaluate arguments; the existing manifest-extra mutation remains.
Verification is the governing read-only operation for this attack. The valid bundle
twin is unchanged. These are command recipes for later integration, not S5 command
acceptance claims.

The complete package's `s5_fixture_correction.changes` retains exact before/after
objects and paths for all three recipes. All 68 content-addressed objects remain
byte-identical; there are still 72 variants and 27 acceptance IDs. RET-5-replay's
actual evaluate recipe is left intact: in S5 it is fresh-path republication/manual
resubmission support, not the separately gated S6 replay computation.

| Artifact | SHA-256 |
| --- | --- |
| [Historical package](2026-09-15-bounded-decision-workflow-candidate-package-pre-s5-retention-correction.json) | `89ba39623a72326d876740d624af501b467179c608ae89ce9e40f66806ec0d4e` |
| [Historical manifest](2026-09-15-bounded-decision-workflow-candidate-manifest-pre-s5-retention-correction.json) | `e0a94c429d69dff69d7b00351dac52ba125e858683f41c0f585c0aafbabd10fc` |
| [Corrected package](2026-09-15-bounded-decision-workflow-candidate-package.json) | `355b169df2805fa09eaba8865eea1a89e02071cc56c302a078677789fad616bf` |
| [Corrected manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json) | `6f1c6103cbc834e089c839f6e3a4503e0a6d91408dccb70972f40a628784fb57` |

Only outer package byte/hash commitments change; object identities do not.
Historical originals were preserved before mutation. Correction tests prove this
scope and compare every per-boundary expected diagnostic with the unchanged
catalogue. Real S5 tests independently raise storage errors at each file boundary,
inspect incomplete/complete-visible files, and reject extra/traversal/duplicate
manifest names with valid twins. The first such run passed 104 tests; final exact
tested-commit evidence belongs in the S5 completion report.

No additional semantic contradiction was found in the S5 recipe sweep. S4 remains
accepted; S5 implementation is not accepted; S6–S7 remain unauthorized.

END OF BOUNDED DECISION WORKFLOW S5 RETENTION FIXTURE CORRECTION REPORT
