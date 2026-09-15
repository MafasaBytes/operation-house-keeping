# S3 policy fixture correction

## Authority and preservation

Started on `brc-exp001` at `7270dacf5567209923530b64c5f75b89832ae07f`.
The owner explicitly authorized the four corrections and S3 resumption, not S4–S7.
The [blocker report](2026-09-15-bounded-decision-workflow-s3-target-and-policy-blocker-report.md)
remains `5fbae38608d6a04d3967d6f4bdb86eaa1842bf72e20f324a9b6e57691a0c8d66`.
The [governing design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
remains `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.

Byte-identical historical copies, made before corrections:

- [Package before S3 correction](2026-09-15-bounded-decision-workflow-candidate-package-pre-s3-policy-correction.json): `199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4`.
- [Manifest before S3 correction](2026-09-15-bounded-decision-workflow-candidate-manifest-pre-s3-policy-correction.json): `5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a`.

Corrected [package](2026-09-15-bounded-decision-workflow-candidate-package.json):
`df9766b51dea3339b9b2096ab3a96ea75ff01b130b6eb913da86d337c5d7cb1e`;
[manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json):
`9b9effe6809bb49ad2f0a7cd1096eeef688ef17dee1a87f44b0832af1e478de9`.
Both remain compact sorted-key UTF-8 JSON without a trailing newline.

## Exact changes and mechanically dependent commitments

POL-2-missing-effect still removes `/premises/effects/E-aH`. Only its expected
diagnostic changes from `EDITION_MISMATCH` to the catalogue's exact
`REQUEST_SCHEMA_INVALID`, stage `lexical_schema`, target `request`, exit 3.
[WorkflowRequest's exact inventory](../../../applications/bounded_decision_workflow/contracts.py)
rejects the omission before public reconstruction or policy. An explicit missing
envelope body is instead unavailable; a stale envelope is `STALE_REFERENCE` and
edition 2 is `EDITION_MISMATCH` after admission. Design §§4–6 and the accepted
[profile validation](../../../applications/bounded_decision_workflow/projection_profile.py)
remain authoritative. No lower validation is bypassed.

For the other three cases the only changed request field is
`/target_policy/costs/canonical_commitment`. The old value was
`285896709e23fc37d2b375311dc93fe41120f95b6be9cc495952f13f71636efd` in all three.

| Case | Corrected cost-premise commitment | Old request → corrected request |
| --- | --- | --- |
| POL-3 | `716bb58544063ea78898909d4dce8633259b1eac815f22015f451837185e7a6a` | `0148633af3c9f8b9aefd25de0ebf79fd4bf161fe0d65429e5fa7e4deb63aec45` → `df05d1e3c01133ec644a0c7b18548111b600cdfe28492b1beda86b789372db63` |
| POL-5-tie | `13b4d6663393a496b7c735e846b24ae51070a813c19ce7cd8bbb4a2d156c09eb` | `6119f55f38ce721660d3e445edebb8d996741b3e94f11876c20a58df4cbf3d2a` → `bfaa5286050c981c30ff03dc0ef51e11a3c849444c4e2f08f6079f24abf466e8` |
| POL-5-missing-cost | `9623eb6a4f1ddb91c6e7ea0803d02ef636a9a2eb01dc014b762f384dfe481e57` | `4f34efe5e1cf8c9304fe52670d509aaa207c82aa433a58745358a11d3529922f` → `2143d8f81410824058bb7891332e4bbccd391e81727ca71e4e003cde95fb5969` |

Only `/commitments_and_limits/request_sha256` changes in the three expected result
objects. The complete object remapping is:

- `1ba217a6adf2643fb2ae38b6938eb4e68c178e06b34450e3b3a60b74310485e8` → `750254e5ec702d105205d3664296cbace8bcab08687939e0adcaddf175eb64de`.
- `820533f297d485f5de8566dccf760b39c304ed4384d1cc2b125a38c37b96ae50` → `9117ba98078763367da0bc9c7ab18fc0fcc1f61f3150fbaa833f96b863af3ba4`.
- `a96d7f0f7062bbbaa287e9326734b559dd51cf7fd4f3abc074fce77e92d372f8` → `d7ce87232546c73546cd892aef0054760b259d4e9fed5f7ce541d4a704c60f69`.

Dependent acceptance request/result references and stdout result commitments are
remapped; traces are unchanged. Manifest package bytes/hash and object count are
recomputed. All 38 old objects remain byte-identical; six corrected objects bring
the total to 44. The original 27 acceptance cases/69 variants remain; three named
stale-admission controls are separately recorded in `s3_fixture_correction` and
are explicitly not policy coverage. No costs, targets, effects or bounds changed.

## Reachability, independent expectations and sweep

[Correction regressions](../../../tests/applications/bounded_decision_workflow/test_s3_fixture_correction.py)
recover every object and both historical files, check exact field diffs, sweep
every active request's nested commitments, and run accepted S1/S2 independently
of the future policy implementation. All three stale originals refuse with
`REQUEST_SCHEMA_INVALID` at lexical admission; all three repaired twins and the
untouched baseline admit observation 40 and produce eight ready raw rows. The
omitted-effect twin reproduces the corrected lexical diagnostic.

Independent policy reasoning from these ready rows: retained H_H predicts 32 for
aH/aHF, inside target [31,33], versus 42 for a0/aF, outside. POL-3 therefore ties
aH/aHF at cost 5; POL-5-tie ties them at cost 2; POL-5-missing-cost must remain
unknown because eligible aH has no cost. This is expected reasoning, not yet a
claim of implemented S3 policy coverage; the S3 completion report must record the
actual integrated branch checks separately.

The complete S3 fixture sweep found no further content/commitment repairs or
semantic contradictions. The existing POL-1 mixed-unknown example makes both
hypotheses unknown and cannot alone cover unknown-plus-incompatible precedence;
S3 must additionally test that total-function table directly. Likewise prior-world
reevaluation remains S4, not a claimed result of these fresh computations.

The independent expectations share the approved equations and synthetic policy,
not runtime prediction helpers; same-author provenance remains disclosed.
No production backend, authoritative ledger, dependency or frozen design changed.
Correction tests and their exact results are recorded in the correction commit's
verification and subsequent S3 completion report. S3 remains subject to acceptance.

END OF BOUNDED DECISION WORKFLOW S3 POLICY FIXTURE CORRECTION REPORT
