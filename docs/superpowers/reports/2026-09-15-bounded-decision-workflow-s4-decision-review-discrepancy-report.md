# Bounded decision workflow S4 — consolidated decision-review discrepancies

Date: 2026-09-15. **S3 accepted; S4 blocked before implementation.** This is not an
S4 completion report and supplies no S4 tested implementation ID.

## 1. Verified checkpoint and completed S3 acceptance

Started on `brc-exp001` at administrative HEAD
`4380d2ce3821a51f9f233ee4fa0d486efbcd7f08`. Accepted S3 implementation:
`17095402b4aea11f526d430c6ee8e568ce180f48`. Its subsequent changes were only the
completion report, plan status and fixture-report wording; source/tests were equal.
The untouched [S3 completion report](2026-09-15-bounded-decision-workflow-s3-target-and-policy-completion-report.md)
matches `c4fe6effeb3649a7cf2aa399e60a3f279c24de9f53cec981dade0a69a8338eca`.

[S3 owner acceptance](2026-09-15-bounded-decision-workflow-s3-owner-acceptance.md)
was committed separately at `ba967d6cab8195442c5b5090f0417cb2913a8185`, which is also
the S4 investigation HEAD. Acceptance-record SHA-256:
`ed567d369b373d1afccdae1d96946ac6eaeda0a01d220f19dfc3add90fefdd05`.
The later discrepancy/status commit is administrative, not implementation.

The [design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
remains `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.
The unchanged [package](2026-09-15-bounded-decision-workflow-candidate-package.json)
and [manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json) remain
`df9766b51dea3339b9b2096ab3a96ea75ff01b130b6eb913da86d337c5d7cb1e` /
`9b9effe6809bb49ad2f0a7cd1096eeef688ef17dee1a87f44b0832af1e478de9`.
Original pre-S3 and pre-OBS correction evidence remains retained and unchanged.

S3 acceptance checks: **46 passed, 153 deselected in 25.39s**, covering archived
object recovery, stale controls, valid twins, frozen semantic layers and hostile
policy cases. Plural ties and unknown selection for missing eligible cost remain
green. The previous 387-test result is retained evidence, not claimed rerun here.

## 2. Exact S4 scope and stop boundary

The [plan §9](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md)
assigns S4 fixed 22-decision dependencies, prior recomputation and distinguishing
changed/equal-after-reevaluation results. Design §§4, 11.3 and 13 require complete
prior/proposed comparison; POL-3/4 and REV-1 exercise it. S5 owns filesystem
publication/verifier/fault handling; S6 owns command/replay integration. Those are
not silently implemented to satisfy S4, nor declared tested by in-memory checks.

The owner permits mechanically recomputing stale commitments without changing
intended semantics, but requires stopping for semantic changes. The problems below
are not stale hashes. All recovered objects have correct canonical outer hashes;
the implicated request premises already pass accepted S1–S3. Changing expected
reevaluation meanings or defining missing dependency closure is more than a digest
repair. No expectation, design, resource ceiling or runtime code was amended.

## 3. B1 — prior comparisons have no-prior expected results and traces

All three variants below supply `--compare-to PRIOR_BUNDLE` and a baseline prior
recipe. Yet their result `/reevaluation/disposition` and all 22 decision-row
`reevaluation` fields are `not_applicable_no_prior`. The corresponding trace rows
are identical. Equality-after-reevaluation and changed-value flags are absent.

| Variant | Expected result object | Expected trace object | Required by design, independently checked |
| --- | --- | --- | --- |
| POL-3 | `750254e5ec702d105205d3664296cbace8bcab08687939e0adcaddf175eb64de` | `3b3105ae8d6fc6dcf5c9eafcfbabde4340f3f2d16bd5b4159b66e628582b484d` | Selection alone requires reevaluation and changes from aH at 2 to aH/aHF tied at 5. |
| POL-4 / REV-1-target | `f9a1395690da45c41c65b91f0bc9dc3e736e4bf5260b9306bdd7369823f51ffc` | `51d8076e61c79cf912a0fd41147d9bf26e3cee20ead67fd2eda958a4f7045189` | Eight target, four feasibility and selection decisions require reevaluation; seven values change and six stay equal. Raw values are unchanged. |

The prior request is
`24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125`.
Fresh S1–S3 recomputation confirmed all physical/policy values; no S4 runtime was
used. For target [31,33] → [25,27], the changed values are four target rows
(H_F/aF, H_F/aHF, H_H/aH, H_H/aHF), feasibility aH/aHF and selection. The other
four target rows and feasibility a0/aF remain incompatible but require review
because their target premise changed. Output equality cannot replace that rule.

Needed correction: independently specify complete comparison expectations and
their exact fields, preserve untouched no-prior twins, and mechanically update the
dependent commitments afterward. Do not weaken the design to return no-prior.

## 4. B2 — frozen dependency inventory lacks a complete field/closure meaning

All 23 retained expected-result/trace objects (including historical S3 objects)
contain the same dependency inventory and only no-prior row dispositions.

The current-condition row lists only `snapshot.state` and
`request.current_condition_question`. Two existing publicly produced fixtures
disprove sufficiency if those names mean the literal fields:

- Baseline request/snapshot: `24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125` /
  `782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f` → `matches`.
- Unavailable request/snapshot: `20839102e285d056bc486bcfeef1bd3597e18cbe317736b12f7bbeb9335b9d14` /
  `72c057d8707f4904cf2dfb658937a4610c56b364217ec073239530756f128ea6` → `unavailable`.

Their `snapshot.state` and `current_condition_question` values compare exactly
equal. The full public classification depends on additional carried evaluations,
as the accepted [admission](../../../applications/bounded_decision_workflow/admission.py)
and public reconstruction establish. This is not an empirical or backend gap.

Each raw row lists `observed.T0`, law, coordinates, commands, one hypothesis and
one action. It does not explicitly list global applicability, support semantics,
effects, preconditions, timing or invariance. The accepted
[S2 projection](../../../applications/bounded_decision_workflow/projection.py)
requires these, independently of dependency edges. Six valid in-memory mutations
set one envelope to `availability=unknown,value=null` and recommit that envelope:

| Mutated support | Canonical request commitment | Actual changed results through S1–S3 |
| --- | --- | --- |
| global_applicability | `06b65cef72792681def350bfe5d8a9424b2ee34834190ebbdc45e1771d2068da` | All eight raw, eight target, four feasibility and selection values. |
| support_semantics | `4d1a75095fc10f3943dcb5cc3c324bc122750ba47ded1413e8196b6376d41d36` | Same 21 decisions. |
| effects/E-aH | `9829f3841adb4bb9421379245215b85c90e4d9086fbd67ad3317dc3b6e23eb91` | Four aH/aHF raw, four target, two feasibility and selection values. |
| preconditions/PC-isolation | `297ae7bd7a66bc1ae87d39f722c343165fea11b1e0d5fadbb9606e245a9de097` | Same 11 decisions. |
| timing/T-aH | `813a4f09f900ca480d5edd01c9e33e4f66ff624b0932abc90144a983f7573ca5` | Same 11 decisions. |
| invariances/I-aH | `b22a4167405d186bb58057af3edcfb1a9a82e469b6728e182d700932fb704aaf` | Same 11 decisions. |

The untouched baseline is each mutation's valid twin. No mutation changed costs,
targets, equations, observed values or backend records. All direct fields named in
the raw map remain unchanged; changes are in omitted support groups.

These dependency labels might instead be intended as aliases for larger resolved
closures (for example action plus effect/gate support). That could be an appropriate
implementation, but the frozen package does not define that expansion. This audit
does not prove all such aliases impossible; it rejects silently treating a literal
field list as complete. Define exact closure, provenance and before/proposed
membership, or amend the dependency list and expectations. Preserve the narrower
promises that target changes exclude raw decisions and cost changes affect only
selection. A whole-world dependency everywhere would not satisfy those promises.

## 5. C1 — incompatible-prior refusal recipe does not supply a prior

`REV-1-incompatible` expects `PRIOR_INCOMPATIBLE`, stage
`commitment_public_reconstruction`, target `prior_bundle`, exit 3. Its argv has
neither `--compare-to` nor a prior path, and it has no `prior_bundle_recipe`.
The only extra data is `prior_mutation=build_profile_or_retained_result` under a
fixture setup object. That is not CLI authority to load an unspecified bundle.

Required future correction: explicitly nominate a valid prior twin and separately
instantiate build/profile/retained-result attacks, retaining independent expected
diagnostics. This is a related command-fixture defect, **not permission to implement
S5/S6 now**. In-memory S4 compatibility/recomputation tests can be written once
the prior/result comparison contract is consistent; filesystem and real command
claims remain gated to their owning slices.

## 6. Checks run, recovery and consolidated decision

Read-only Python checks recovered all 44 objects, audited every expected decision
inventory, inspected all three comparison variants and the prior refusal recipe,
and invoked accepted S1–S3 on the baseline, changed-target/cost inputs, unavailable
public twin and six support mutants above. Independent expected review reasoning
came from design dependency obligations, not output equality alone.

A red-first frozen-contract audit ran four unittest methods with **11 failing
assertions/subtests**: three prior/no-prior expectations, one equal-listed-inputs/
changed-classification witness, six missing raw-support groups, and one missing
prior command argument. These are specification reds, not failures of an S4
implementation or command run. No production test file was added and no failing
suite was presented as green. Reproduce the central checks from the package by
decoding an object as `json.loads(zlib.decompress(base64.b64decode(entry['payload'])))`,
checking its SHA-256/length, then examining the variant references and fields named
above. Support witnesses are reproducible by the stated two-field mutation and
SHA-256 recomputation over the envelope excluding `canonical_commitment`.

The persistent CPython 3.13 environment verifier returned `verified`, filesystem
ext4, unchanged environment identity
`693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`
and artifact set
`26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`.
All checks were in memory/read-only; no new runtime files or filesystem acceptance
probes were needed. The sandbox's read-only mount view is not a new platform
failure or a claim to have rerun writable filesystem guarantees.

Only acceptance/status/discrepancy documentation changed. The S3 report, frozen
design/review, package/manifest, historical evidence, backend, ledgers, retained
inputs/results/dependencies and all 63 unrelated untracked files remain unchanged.
Digests, object recovery, links, markers, scoped staging and whitespace were checked.
There was no S4 production implementation, new dependency, resource-policy change,
physical acquisition, push, merge or history rewrite.

Owner decision required: authorize correction of B1's comparison expectations and
B2's explicit dependency/closure specification, with preserved originals and
independent twins; also resolve C1's prior-invocation recipe before its later
command acceptance. Mechanical hashes alone cannot resolve these meanings. No new
backend or effect/policy semantics is requested. Resume S4 after that correction;
S4 is not ready for acceptance. S5–S7 remain unauthorized.

END OF BOUNDED DECISION WORKFLOW S4 DECISION-REVIEW DISCREPANCY REPORT
