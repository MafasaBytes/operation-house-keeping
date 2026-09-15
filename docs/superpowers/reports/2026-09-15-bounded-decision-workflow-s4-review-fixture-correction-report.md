# S4 decision-review expectation and dependency correction

## Authority, baseline and commitments

Owner-authorized bounded correction and S4 resumption, not S4 acceptance or S5–S7.
Verified `brc-exp001` at `99d6f6693945c392bd9fe5eb3b602ac3943a9dc2`;
S3 acceptance is `ba967d6cab8195442c5b5090f0417cb2913a8185`.
The [discrepancy report](2026-09-15-bounded-decision-workflow-s4-decision-review-discrepancy-report.md)
remains `8dc27ca1f691b58e45bc6ed3bacce9d3415931deea845b173260c0a1e0244f1a`.
The [approved design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
and its numerical/effect/policy meanings are unchanged.

| Artifact | SHA-256 |
| --- | --- |
| [Historical package](2026-09-15-bounded-decision-workflow-candidate-package-pre-s4-review-correction.json) | `df9766b51dea3339b9b2096ab3a96ea75ff01b130b6eb913da86d337c5d7cb1e` |
| [Historical manifest](2026-09-15-bounded-decision-workflow-candidate-manifest-pre-s4-review-correction.json) | `9b9effe6809bb49ad2f0a7cd1096eeef688ef17dee1a87f44b0832af1e478de9` |
| [Corrected package](2026-09-15-bounded-decision-workflow-candidate-package.json) | `6af90f315b7f1c407a30e57d526d609c650dfbd10bb2489c87087a6f596a8a63` |
| [Corrected manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json) | `75382b7098b9ab98382f104da7cb201dacb357cee67cfb9c9ca81f8f2202c460` |

Historical files were copied exclusively before mutation. All 44 original objects
remain identical; 22 new expected result/trace objects bring the count to 66.
The package's `s4_fixture_correction.object_changes` records **every** affected
variant's exact old/new result and trace SHA-256, including shared-object cases.
It is the recoverable complete remapping, not a lossy old-hash-only dictionary:
the old target result splits into genuine no-prior and comparison expectations.
No complete request, snapshot, application premise or S1–S3 result layer changed.

## Exact field corrections

Only `/reevaluation` changes inside expected results; only `/decision_rows` changes
inside expected traces. Outer object byte lengths/hashes, variant result/trace and
stdout-result references, prior recipe references, manifest package length/hash
and object count are mechanically updated. Historical preparation measurements
remain historical, not rebranded as new execution maxima.

POL-3, POL-4 and REV-1-target now have `disposition=compared`. Each of the 22 rows
retains its computed `value`, has explicit `depends_on`, and reports:

- `reevaluation`: `required`, `not_required`, or `not_applicable_no_prior`;
- `value_changed`: comparison of independently recomputed values, or null without prior;
- `equal_after_reevaluation`: value equality only for required rows, otherwise null.

Design §§4, 7–8, 11.3 and POL-3/4 require propagation of changed **support**, not
propagation only when the upstream value changes. Cost-only POL-3 requires one
selection review and changes one value. Target-only POL-4/REV-1-target requires
13 downstream reviews: seven changed values, six equal results; all eight raw
values remain unchanged and their review is not required. Genuine no-prior
expectations retain no-prior dispositions, with null comparison flags.

REV-1-incompatible now explicitly supplies `--compare-to PRIOR_BUNDLE`, a complete
baseline request/snapshot/result/trace recipe and exact `build_identity` mutation.
Separate `REV-1-profile` and `REV-1-retained-result` twins isolate profile and
retained-result-with-matching-digest attacks. All expect the unchanged catalogue
`PRIOR_INCOMPATIBLE`, commitment/public-reconstruction stage, prior_bundle, exit 3.
REV-1-target remains the valid-prior twin. Added REV-1-omitted-prior uses baseline
inputs with no prior argument and a successful genuine no-prior result. These
three distinct added variants bring 69 to 72; the 27 acceptance IDs are unchanged.
Command recipes are corrected preparation evidence, not executed CLI acceptance.

## Complete dependency interpretation

The independent [expected specification](../../../tests/applications/bounded_decision_workflow/s4_expected_reasoning.py)
uses explicit action-support tables; it does not call a runtime review builder.
There are still exactly 22 decisions. `premise:<id>` means the **whole exact
application envelope**, including availability, edition, identity and provenance,
not an assertion that the premise is physically true. IDs are resolved only inside
each complete admitted world. The `snapshot` support is the entire selected public
serialization, not merely its `state` field; `question` is the complete supplied
current-condition question. `observed:T0` denotes exact selected snapshot identity
plus the complete observed-input binding, whose value must first pass S1 admission.
It cannot be supplied as a number or forged public object.

| Decision | Required support and why |
| --- | --- |
| Current condition | Full snapshot and question: public classification also consumes carried evaluations, not only state declarations. |
| Each raw row | Admitted T0 support; actions, commands, hypotheses, global applicability, law, Cartesian support and all four coordinate envelopes required by S2; only that action's explicit effect, precondition, timing and invariance envelopes. These determine availability/applicability as well as arithmetic. |
| Each target row | Its raw decision and target envelope; costs cannot affect it. |
| Each feasibility row | Retained target decisions, retained-set and feasibility-rule envelopes, global and that action's gate envelopes. When retained membership is unavailable, both nominated target rows remain conservatively reviewable, never silently unaffected. Explicit false gates still apply with missing membership. |
| Selection | All four feasibility decisions, nominated-action envelope, global applicability and selection rule; relevant guaranteed/unknown action costs and shared cost-policy support. Complete noneligible cost entries cannot affect selection. |

`cost:<action>` denotes only that action's entry. `cost_policy` denotes the cost
envelope header without derived canonical_commitment/value, plus its cost token;
overall availability and policy provenance matter, but another entry's changed
content/hash does not create a spurious dependency. The full cost envelope is
still admitted and retained; malformed/stale noneligible entries still refuse.
Relevant cost and retained-target dependencies are taken from **both** before and
proposed worlds; dropping a dependency cannot hide its change. Direct dependencies
and upstream required reviews propagate in inventory order regardless of equality.

Whole-envelope provenance changes require review of their consumers even when the
answer stays equal. Receipt ID, actor label and requested resource limits are not
decision-value dependencies: they remain retained inputs and changed-field evidence.
Limits still control whether a call can complete. Current-condition value never
selects hypotheses or gates raw projection. No dependency declaration supplies an
effect. All support interpretation comes from the governing S1–S3 semantics.

## Sweep, independent controls and implementation handoff

The sweep covered all 23 old expected result/trace objects and all active variants.
It corrected shared inventories consistently rather than only the three named
comparisons. An ordinary preparation defect initially assumed every success
variant carried request_ref directly; replay recipes instead identify it through
the result's committed request. The script stopped before writing current JSON;
historical copies were verified identical before resuming. No semantics changed.

[Correction tests](../../../tests/applications/bounded_decision_workflow/test_s4_fixture_correction.py)
retain all 11 old failing conditions as historical reds and assert their corrected
twins; check exact changed sections and recovery; verify 1/1/0 and 13/7/6 review/
changed/equal counts; and retain the omitted-prior success. Existing S3 tests prove
the relevant requests admit and reach the intended physical/policy branches.
Production S4 prior refusal/recomputation and missing/unnecessary-dependency checks
must run after this correction commit; expected fixtures are not execution evidence.

S4's public application-service seam will consume captured current/prior bytes,
recompute both through S1–S3, compare retained prior decisions/traces, and require
matching explicitly supplied application-build commitments. It will not open a
bundle, authenticate an executable or implement a filesystem verifier. The future
S5/S6 caller must verify the manifest and supply its own build identity and exact
captured material; application-level equality does not establish source authenticity.
Complete prior ancestry, when supplied, must be retained/recomputed under aggregate
limits, never replaced by a trusted success flag or unbounded references.

No additional semantic contradiction was found. Remaining work is implementation
and its bounded integrity/resource verification. No backend, dependency, resource
policy, fixture ledger or S5–S7 capability is changed. Original untracked evidence
and the persistent environment remain protected; S4 is not yet accepted.

END OF BOUNDED DECISION WORKFLOW S4 REVIEW FIXTURE CORRECTION REPORT
