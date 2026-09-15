# Bounded decision-workflow S3 target-and-policy blocker report

Date: 2026-09-15

Status: S2 owner acceptance recorded. S3 stopped before implementation because
four frozen acceptance cases conflict with accepted S1/S2 validation. This is not
an S3 completion or acceptance claim. No frozen expectation was changed.

## 1. Verified checkpoint and completed acceptance

Branch `brc-exp001` began at `bf7954595db73e20ccba4a8f838abd24d26f175c`.
The exact accepted S2 implementation/test commit is
`aa454b53063c1e6a88f4fe398dbd787873241d0e`. Its only subsequent change was the
administrative completion-report update, not implementation or tests.

The unchanged [S2 completion report](2026-09-15-bounded-decision-workflow-s2-raw-projection-completion-report.md)
matches `55d4c2b3587664b074e0b8f14c3552b940d0728498f53b6f8989f5d2d0eacfbc`.
The [S2 acceptance](2026-09-15-bounded-decision-workflow-s2-owner-acceptance.md),
SHA-256 `064e17ec322a24a5c79458f6e6398197c3b74dac699c26f9a6e718b705ae81cd`,
was committed separately at `0a2864c63cc64b8be7b16aa4f19d69e167778daf`.
That is the S3 starting/diagnostic HEAD. There is no S3 implementation/test HEAD.

The recorded S2 result remains 188 passing tests (20 S1, 94 S2, 74 affected).
Acceptance verification reconfirmed the 188-test collection and ran ten focused
frozen-result, Cartesian, false-gate, public-refusal and schema-order tests:
**10 passed, 84 deselected in 4.82s**. The unaffected suites were not rerun.

The [design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
remains `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.
The current [package](2026-09-15-bounded-decision-workflow-candidate-package.json)
and [manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json) remain
`199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4`
and `5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a`.
Historical package/manifest and previous fixture corrections remain intact.

## 2. Actual S3 scope and investigation

The [plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md)
defines S3 as target relations, robust feasibility and supplied-action cost
selection total functions, with no filesystem code. Applicable cases are POL-1–5,
plus target/uncertainty boundaries left by NUM-1 and UNC-1/2. S4 owns named-decision
reevaluation; S3 can compare freshly computed layers for target/cost changes but
cannot claim S4's dependency inventory or prior-world review.

Before writing S3 code, the investigation recovered all 38 package objects and
verified their byte counts and outer SHA-256 identities. It recursively audited
the premise commitments in all 13 complete request objects, ran all seven
materialized POL success inputs through the accepted S1/S2 public application
entry point, and independently checked both POL-2 refusal recipes and their
nearest valid/missing/stale/edition twins. This exposed two classes of conflict
affecting four frozen case entries, detailed below.

## 3. B1 — missing-effect fixture conflates omission, unavailable support and edition mismatch

Package path: `acceptance_cases[acceptance_id=POL-2].variants[variant_id=POL-2-missing-effect]`.
The recipe says `remove referenced E-aH` but expects `EDITION_MISMATCH` at
`profile_cardinality_edition`, target `premise_edition`.

Actual deletion of `/premises/effects/E-aH` is rejected by the accepted exact
inventory in [WorkflowRequest](../../../applications/bounded_decision_workflow/contracts.py).
Its diagnostic is:

```json
{"bundle_state":"optional_refusal","code":"REQUEST_SCHEMA_INVALID","exit_code":3,"message_key":"request_schema_invalid","retry_class":"correct_input","stage":"lexical_schema","target":"request"}
```

The unchanged [S2 regression](../../../tests/applications/bounded_decision_workflow/test_s2_raw_projection.py)
already distinguishes an omitted declaration from a present envelope with missing
support. The accepted [profile validator](../../../applications/bounded_decision_workflow/projection_profile.py)
distinguishes stale references and edition conflicts. No public reconstruction or
policy evaluation is reached when the required declaration is omitted.

All following twins use the same valid baseline snapshot, SHA-256
`782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f`.
Only the described field changes are made; changed envelopes are recommitted.

| Mutation | Canonical request SHA-256 | Reproduced outcome |
| --- | --- | --- |
| Untouched baseline | `24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125` | All eight raw rows ready. |
| Delete E-aH envelope | `3fc9a34eeef34d429458c23b78e9991cad160241da12b57f9c1cd86053de9789` | `REQUEST_SCHEMA_INVALID`, lexical stage. |
| E-aH availability missing, value null | `165ca128ece7ccb4d82224972362e9b1248e9fca336b050436d1a70949809556` | Four aH/aHF rows unknown; a0/aF ready. |
| E-aH availability unknown, value null | `9829f3841adb4bb9421379245215b85c90e4d9086fbd67ad3317dc3b6e23eb91` | Same raw dispositions as missing support. |
| E-aH availability stale_reference | `7907c7407433260dc0dc5da74d6edf8006a10f41285ce8edb97ae4cd9e625dab` | `STALE_REFERENCE`, profile stage, target premise_reference. |
| E-aH edition 2 | `0ed4d6f8c6a3a7c1700d571c8b127f6915c8e8720a2619d2b5542f95a0003294` | `EDITION_MISMATCH`, profile stage, target premise_edition. |
| E-aH body replaced by dependency | `05891921a70637df63017556679fe7392132cb58e996404d1343ad2bbb366ce0` | `PROFILE_UNSUPPORTED`; agrees with POL-2-dependency-as-effect. |

The dependency body was exactly
`{"kind":"dependency","from":"heater","to":"temperature"}`.
These cases cannot be conflated merely to reach the frozen expected diagnostic.
Recommended correction: retain omission as schema refusal, explicit missing
support as unavailable prediction, and an edition mutation as the edition-refusal
control. No change to S1/S2 admission, effect semantics or backend is justified.

## 4. B2 — three cost-policy mutations retain the baseline premise commitment

All three requests have valid outer object-store hashes but the wrong nested
`/target_policy/costs/canonical_commitment`. They retain the baseline P-cost hash
`285896709e23fc37d2b375311dc93fe41120f95b6be9cc495952f13f71636efd`
after changing its body. [PremiseEnvelope](../../../applications/bounded_decision_workflow/contracts.py)
correctly rejects each as `REQUEST_SCHEMA_INVALID`, lexical stage, target request.
An outer object hash does not repair the nested premise commitment.

| Case | Changed cost body versus baseline | Correct P-cost commitment |
| --- | --- | --- |
| POL-3 | aH cost 2 → 5 | `716bb58544063ea78898909d4dce8633259b1eac815f22015f451837185e7a6a` |
| POL-5-tie | aHF cost 5 → 2 | `13b4d6663393a496b7c735e846b24ae51070a813c19ce7cd8bbb4a2d156c09eb` |
| POL-5-missing-cost | aH availability missing, cost null | `9623eb6a4f1ddb91c6e7ea0803d02ef636a9a2eb01dc014b762f384dfe481e57` |

For diagnosis only, replacing that one hash in memory produced the following
valid twins. Nothing was written back to the package or oracle.

| Case | Frozen request SHA-256 | Prospective corrected request SHA-256 |
| --- | --- | --- |
| POL-3 | `0148633af3c9f8b9aefd25de0ebf79fd4bf161fe0d65429e5fa7e4deb63aec45` | `df05d1e3c01133ec644a0c7b18548111b600cdfe28492b1beda86b789372db63` |
| POL-5-tie | `6119f55f38ce721660d3e445edebb8d996741b3e94f11876c20a58df4cbf3d2a` | `bfaa5286050c981c30ff03dc0ef51e11a3c849444c4e2f08f6079f24abf466e8` |
| POL-5-missing-cost | `4f34efe5e1cf8c9304fe52670d509aaa207c82aa433a58745358a11d3529922f` | `2143d8f81410824058bb7891332e4bbccd391e81727ca71e4e003cde95fb5969` |

All three twins passed S1/S2 admission. Independent one-off rational/set checks
of design §§7–8 agreed with the frozen raw/target/feasibility/selection values:
POL-3 selects `{aH,aHF}` at 5; POL-5-tie selects both at 2; POL-5-missing-cost
is unknown. POL-4's unchanged target-only request also agrees and requires no
commitment repair. Each affected expected result embeds its original request
reference, so a correction must update mechanically dependent input/result/trace
references, counts and manifest commitments, not just its request-object key.

These checks are disposable diagnostic calculations, not maintained S3 code or
S3 acceptance tests. They share the design's assumptions and same-author
provenance; they establish no empirical accuracy.

## 5. Remaining sweep findings and reproduction

No other premise-commitment defect was found among the 13 recovered requests.
The four unmodified valid POL inputs (POL-1-false, POL-1-mixed,
POL-2-unknown-precondition and POL-4) reach their expected raw dispositions.
NUM-1-endpoint and UNC-1/2 also agree with independent raw/target/policy checks.

Non-blocking coverage observation: POL-1-mixed reuses missing beta support and
therefore makes both hypotheses unknown. It does not itself exercise a mixed
unknown/incompatible pair. That explicit total-function decision-table test is
still required for S3; it must not be claimed passed by this fixture. Likewise,
POL-3/4 prior-bundle reevaluation remains S4/S6 work, not S3 authorization.

Minimal reproduction from the unchanged checkout and approved interpreter:

```python
import base64, copy, hashlib, json, zlib
from pathlib import Path
from applications.bounded_decision_workflow import (
    project_request_and_snapshot, WorkflowInputError,
)
p = json.loads(Path("docs/superpowers/reports/2026-09-15-bounded-decision-workflow-candidate-package.json").read_bytes())
def wire(key):
    return zlib.decompress(base64.b64decode(p["objects"][key]["payload"]))
def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
snapshot = wire("782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f")
baseline = json.loads(wire("24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125"))
request = copy.deepcopy(baseline)
del request["premises"]["effects"]["E-aH"]
try:
    project_request_and_snapshot(canonical(request), snapshot)
except WorkflowInputError as error:
    print(error.diagnostic)  # REQUEST_SCHEMA_INVALID, not EDITION_MISMATCH
for key in (
    "0148633af3c9f8b9aefd25de0ebf79fd4bf161fe0d65429e5fa7e4deb63aec45",
    "6119f55f38ce721660d3e445edebb8d996741b3e94f11876c20a58df4cbf3d2a",
    "4f34efe5e1cf8c9304fe52670d509aaa207c82aa433a58745358a11d3529922f",
):
    request = json.loads(wire(key))
    cost = request["target_policy"]["costs"]
    correct = hashlib.sha256(canonical({k: v for k, v in cost.items()
                                       if k != "canonical_commitment"})).hexdigest()
    assert correct != cost["canonical_commitment"]
    try:
        project_request_and_snapshot(wire(key), snapshot)
    except WorkflowInputError as error:
        print(key, error.diagnostic)
    cost["canonical_commitment"] = correct  # in-memory valid twin only
    project_request_and_snapshot(canonical(request), snapshot)
    print("valid twin", hashlib.sha256(canonical(request)).hexdigest())
```

## 6. Preservation and exact decision required

The persistent CPython 3.13 environment verifier returned `verified`, ext4 and
the unchanged approved environment/artifact identities. These checks used
in-memory application calls; they created no runtime inputs, result bundles,
devices, dependencies or temporary tooling files. Source, tests, frozen evidence,
historical packages, authoritative ledgers and unrelated untracked files remain
unchanged. Documentation links, commitments, preservation and whitespace were
checked. No S3 implementation was committed and no completion is claimed.

Requested owner resolution: authorize a narrowly scoped fixture correction that
preserves today's package/manifest as historical evidence, corrects the B1
expectation without bypassing S1/S2, repairs the three B2 premise commitments and
their mechanically dependent references, and retains the invalid originals as
regression controls with valid twins. Then resume S3 under its existing
implementation authorization. This requires no new equation, policy, backend
capability or relaxed limit.

S3 acceptance is not yet available. S4–S7 remain unauthorized; IN-001 and CI-001
remain open and unselected. No physical accuracy, causal identification, action
generation, multi-step planning or global-minimality claim is made.

END OF BOUNDED DECISION WORKFLOW S3 TARGET-AND-POLICY BLOCKER REPORT
