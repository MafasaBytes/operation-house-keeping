# S4 complete-recipe sweep correction

This is a further correction under the owner's existing authorization to replace
no-prior expectations when a valid prior is supplied. It changes no input, policy,
effect, observation, diagnostic precedence or resource ceiling. S4 is not accepted;
S5–S7 remain unauthorized.

## Discovery and preserved authority

The [first correction](2026-09-15-bounded-decision-workflow-s4-review-fixture-correction-report.md)
was committed at `3b2f8cdbe0bcbc5370f9bb9d537d6921402275fa`. Its sweep missed two
prior recipes outside the named POL/REV cases. The first implementation at
`4d7508cf25ad220d1f2f0b8aed43f2911a68f34c` passed 471 tests, but those two tests
incorrectly invoked the valid unavailable inputs without their specified prior.
That result is not final complete-recipe S4 acceptance evidence.

`CMD-2-unavailable` and `OBS-2-absent` already supply `--compare-to PRIOR_BUNDLE`
and the same complete baseline prior. Their no-prior expectations were therefore
wrong for the same reason as the original B1 finding. Governing design §§4 and
11.3 require comparison of the actual supplied worlds, including unavailable
answers. The unchanged public snapshots have equal `state` material but different
carried evaluation results: full snapshot dependency is necessary.

The immediately preceding package/manifest are preserved byte-for-byte as
[historical package](2026-09-15-bounded-decision-workflow-candidate-package-pre-s4-complete-sweep.json)
and [historical manifest](2026-09-15-bounded-decision-workflow-candidate-manifest-pre-s4-complete-sweep.json):

- Package: `6af90f315b7f1c407a30e57d526d609c650dfbd10bb2489c87087a6f596a8a63`.
- Manifest: `75382b7098b9ab98382f104da7cb201dacb357cee67cfb9c9ca81f8f2202c460`.

The original pre-S4, pre-S3 and pre-OBS histories remain untouched.

## Exact repair and independent reasoning

Only result `/reevaluation` and trace `/decision_rows` change. Both variants share:

| Object | Before SHA-256 | After SHA-256 |
| --- | --- | --- |
| Result | `59290c74fda0ca283149646b4ceeda116eaf4e6c1af5ecee7853b39c5f14e596` | `e271ea9f35bcac91685e9ca599026f018958710cf7e4b442d48a979bc54b1279` |
| Trace | `2d15f96d4f44517975fd7928da3fb4aff4e9ba5c8b2e6d5dc937a590f1f1e924` | `cbbedde6c930a64e4c6ee87a6b2caa4f38ca530b2a5bc8b9f9fdefcf64a14b31` |

Disposition becomes `compared`. The changed public snapshot changes classification
and admitted-observation support; eight raw decisions, eight target assessments,
four feasibility decisions and selection must consequently be reviewed. All 22
values change; none is equal after reevaluation. The unavailable classification
match remains **null**, not a substituted string; its separate admitted disposition
explains unavailability. All S1–S3 result fields remain byte-equivalent canonical
values. The test-only manual oracle specifies this dependency propagation; it does
not call the runtime review builder or use output equality to select dependencies.

The same two active result/trace references and stdout result commitments are
updated. Two objects are added; all 66 preceding objects remain unchanged, for 68
objects, 72 variants and the same 27 acceptance IDs. Complete per-variant remapping
is retained in `s4_complete_sweep_correction.object_changes`.

- Corrected [package](2026-09-15-bounded-decision-workflow-candidate-package.json):
  `89ba39623a72326d876740d624af501b467179c608ae89ce9e40f66806ec0d4e`.
- Corrected [manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json):
  `e0a94c429d69dff69d7b00351dac52ba125e858683f41c0f585c0aafbabd10fc`.

## Runtime repair versus fixture correction

The first implementation expanded a public snapshot into leaf-level changed paths,
exceeding the 64-path cap on these cases. This was an implementation granularity
choice, not a design requirement. The corrected application diff treats the public
snapshot as one opaque `/snapshot` change, consistent with its declared dependency;
it still retains and revalidates the entire before/proposed serialization. Request
fields retain exact leaf/frontier paths. It neither raises the cap nor omits a
changed dependency. This implementation repair is committed separately from these
expectations. Generic 64/65-path refusal controls remain required.

The complete fixture check now examines **every** successful recipe's prior
argument, not only named REV/POL cases; the two repaired service tests must actually
pass their specified prior. The genuine omitted-prior control remains. Command
recipes are not claimed executed: S4 tests use captured bytes, while command and
filesystem acceptance remain later slices. Runtime branch results are recorded
in the S4 completion report after verification, not inferred from expected objects.

END OF BOUNDED DECISION WORKFLOW S4 COMPLETE SWEEP CORRECTION REPORT
