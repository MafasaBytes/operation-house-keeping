# Selection and supplied-result reassessment

For technical users and local evidence reviewers. These maintained workflows
reason over supplied evidence, hypotheses and support; people supply premises,
authorize work and decide what to adopt. They do not acquire measurements or
establish causal or empirical truth.

Reassessment is [owner accepted](../superpowers/reports/2026-09-30-reassessment-slice5-and-final-owner-acceptance.md).
The [accepted reconciliation, retained with this documentation](../superpowers/reports/2026-09-30-post-reassessment-corrected-reconciliation.md)
contains the detailed objective map, exact historical identities and recovery
inventory. [Delivery status](delivery-status.md) records acceptance for local
retention and the deferred work. Publication readiness is not established.

## What the workflows answer

| Original objective | Available answer and its boundary |
|---|---|
| 1. What exists and how is it connected? | Backend model/hierarchy/port/connection queries and profile-specific context validation. Entities, topology and bindings are supplied; no automatic discovery or general model browser. |
| 2. What is the current state? | Admission of a supplied public snapshot at an exact receipt cutoff, or explicit unavailability. An old valid observation is not necessarily fresh; no monitoring or automatic state update. |
| 3. Why might it behave this way? | Compatibility, conditional incompatibility or unresolved assessment of nominated hypotheses against supplied scalar results. Compatibility is not causal diagnosis; hypotheses are not generated. |
| 4. What measurement should come next? | Prior-free minimax selection over nominated procedures using qualified supplied support, with ties and withholding reasons. This is finite-set selection, not global optimality or acquisition authority. |
| 5. What would a change affect? | The separate thermal/governed workflow reviews 22/23 named decision slots; reassessment exposes changed references and dependencies. No general impact discovery or automatic propagation. |
| 6. What is the smallest valid change? | The separate thermal/governed workflow projects two supplied hypotheses and four supplied actions, selecting least cost among nominated robust-feasible actions. No global minimum, multistep plan or actuation. |
| 7. What is observed, calculated, assumed or unknown? | Typed provenance, support reasons, uncertainty, authority/exposure declarations and recomputing replay. Local attestation is not authenticated truth; results are not automatically adopted. |

The [thermal/governed guide](../../applications/bounded_decision_workflow/README.md)
describes the separate action route. There is **no implemented reassessment-to-action
adapter**. Historical synthetic experiments are evidence within their own scope,
not additional maintained commands or empirical validation.

## Platform and identity prerequisites

| Boundary | What commands accept | What was tested |
|---|---|---|
| Selection and thermal/governed retained I/O | Local ext4 or XFS, with safe path/regular-file checks. | Linux/WSL ext4. XFS acceptance is not XFS qualification. |
| Reassessment inputs, retained bundles and outputs | **ext4 only**; XFS is refused. | The approved local ext4 environment. |
| NM/NR executable identity | CPython 3.13 family, exact locked dependency versions, clean application/backend source scope; actual patch version, installed artifacts, source and checkpoint enter the build identity. | CPython **3.13.11**, the approved dependency identities and recorded environment. Other identities are not qualified by that evidence. |

Git does not supply the interpreter, installed environment or wheelhouse.
The retained I/O implementation uses Linux mount metadata and POSIX path checks;
these instructions do not establish general Windows or network-filesystem support.
[Installation prerequisites](../../applications/bounded_decision_workflow/README.md#release-verification-and-recovery)
describe the external material. Its ext4/XFS guidance is for the original routes:
use ext4 for reassessment. Exact historical replay needs the matching recorded
checkpoint and environment; reinstalling the same versions at another prefix can
change installed script hashes. Source equality alone does not establish replay
identity. Qualification's optional PDF/CAD absence and expected skips are recorded
in the acceptance report, not a blanket promise about every environment.

The shared filesystem diagnostic contains `choose_supported_ext4_xfs`, which is
misleading for NR; the NR CLI translates it to the generic `correct_input`.
Neither expands NR's ext4-only boundary. The diagnostic correction is deferred.
See [capture](../../applications/bounded_decision_workflow/reassessment_capture.py),
[retention](../../applications/bounded_decision_workflow/retention.py) and
[CLI translation](../../applications/bounded_decision_workflow/reassessment_cli.py).

## Handoff: supplied evidence to a human decision

NM means next-measurement selection; NR means result reassessment.
Objects use canonical bytes and `<sha256>.<kind>` filenames. Directory contents
do not nominate hypotheses, grant permission or supply missing references.

| Stage | Required artifacts / implemented handoff | Human responsibility |
|---|---|---|
| Admit evidence | `nm.evidence.v1` carries a public `StateClassificationResult`, owning context and bindings. | Supply the public result through backend composition. There is no command here that builds it from raw measurements. |
| Nominate and select | `nm.request.v1` names hypotheses, procedures, decoders, support and policy. `nm.invocation.v1` binds request, selection authority, build and resource policy. | Supply premises and applicable declaration/attestation/adoption references. Decide whether to perform a recommended procedure. |
| Carry original selection | Preserve its invocation, selection pin and required typed closure. If carrying the prior result bundle, describe its exact seven files in `nr.retained-bundle.v2`. | Manually assemble the handoff; no maintained converter does this. The NR procedure must be nominated in the original request, but need not be its winner. |
| Supply result | `nr.observation.v2`: evidence, procedure, decoder, provenance. `nr.execution.v2`: observation, original/result contexts, acquisition and conditions. | Supply the scalar result, uncertainty, acquisition interval and applicability/calibration/fidelity/hold declarations. No instrument integration is implied. |
| Declare exposure and authorize | `nr.exposure.v2`: original invocation, observation, optional prior bundle, relation, prediction-commitment/first-learned times and basis. `nr.request.v2` binds these plus original selection pin, procedure, decoder, execution, interpretation and policy. `nr.authority.v2` binds the exact request. | An owner or authorized attestor must issue the applicable permission declaration. Declared chronology is not independently established custody. |
| Reassess and decide | `nr.invocation.v2` binds request, authority, actual NR build and resource policy. The command returns hypotheses, reasons, uncertainty and provenance. | Inspect the result and decide outside the application. `summary.disposition` is computed; it is not a human adoption record. |

Result admission currently supports a reference scalar in degrees Celsius with a
declared point or hard interval. Confidence-only uncertainty does not become a
hard envelope. Missing/conflicting support and unknown conditions can withhold
assessment. Original hypotheses remain nominated; `ranking=not_reassessed` and
`adoption=derived_not_adopted`. There is no automatic reranking or adoption command.

**Manual bundle composition:** reuse original objects, or decode and hash-check
the original base64 closure into typed files. A completed bundle contains
`invocation.json, closure.json, result.json, trace.json, build.json, policy.json,
manifest.json`. The retained-bundle descriptor has seven sorted file rows and
an `original_closure` reconstruction recipe. Result/trace/manifest bytes travel
as **`nm.basis` references**; their inner schemas must be `nm.result.v1`,
`nm.trace.v1` and `nm.bundle.v1`. Invocation/build/policy use their respective
typed references. Do not rename the inner schemas into transport kinds.
[Contracts](../../applications/bounded_decision_workflow/reassessment_contracts.py)
and [capture](../../applications/bounded_decision_workflow/reassessment_capture.py)
define the exact shapes and checks; the package below retains the wire catalog.

### Mechanical work versus authority

Hashing, decoding a closure and binding an actual build are mechanical operations.
They are not permission issuance:

- A new NM build changes its invocation digest. NR must reference that new
  invocation in both request and exposure; carrying a new bundle also changes
  its descriptor. Those changes produce a new NR request digest.
- A changed original selection authority also changes NR's
  `original_selection_pin`. New result evidence or conditions change observation/
  execution references as applicable; a build-only rebind does not itself require
  inventing a new observation.
- Because NR authority binds the exact request, a fresh request requires a newly
  attested authority and new `--authority-pin`, then an updated NR invocation.
  Documentation, a recommendation or an example's existing permission cannot
  supply that grant.

Exact context/cutoff checks reject substitutions; they do not discover newer
evidence. Changed premises require explicit revised references and applicable
authority. `ORIGINAL_CONTRACT_UNSUPPORTED` rejects an original NM build with a
different contract commitment; NR's build records `supported_nm_contract_sha256`.
A future contract change may block old selections under a new build without
erasing their matching historical replay route. No separate feedback-ingestion
capability is required for already supported public result evidence.

## Command interfaces

Here `PY` means the absolute path to the intended interpreter, not shell
activation. Inputs must already be valid and authorized; output directories must
be new. These signatures document interfaces, not a prepared runnable workflow.

```text
PY -m applications.bounded_decision_workflow measurement-evaluate --invocation I --objects-dir O --authority-pin NM_PIN --output-dir M [--limits L]
PY -m applications.bounded_decision_workflow measurement-verify --bundle M
PY -m applications.bounded_decision_workflow measurement-replay --bundle M --output-dir MR [--limits L]
PY -m applications.bounded_decision_workflow reassessment-evaluate --invocation NI --objects-dir NO --authority-pin NR_PIN --output-dir N [--limits L]
PY -m applications.bounded_decision_workflow reassessment-verify --bundle N
PY -m applications.bounded_decision_workflow reassessment-replay --bundle N --output-dir NR [--limits L]
```

The NM pin must equal the invocation's selection digest; the NR pin must equal its
authority digest. NM's parser permits omission, but runtime refuses a v1 invocation
without the pin. `--limits` may only tighten approved ceilings. Exit 0 can mean
completed withholding or denial: read the result, not just the exit status.

Verify checks retained integrity/build/policy (and NR admission); replay
independently recomputes and compares result/trace under the matching identity.
Neither grants present adoption. See the [selection guide](../next-measurement/README.md)
for selection-specific result and refusal interpretation.

## Examples and recovery routes

**Accepted examples are separate from a fresh authorized workflow.** Selection P
and NR P8-before are two recovery descriptions, not one fresh continuous run.

| Route | Available material | Prerequisites and limits |
|---|---|---|
| Selection P | Committed [guide and existing fixture helper](../next-measurement/README.md#recoverable-synthetic-example-from-committed-material); frozen package input premises. | Approved external environment and new private supported destinations. The helper binds the actual NM build/invocation while preserving fixture authority. It never supplies expected outputs to production. This creates a new invocation, not P8-before's historical selection. |
| NR P8-before: static inspection/recovery | Committed [preparation package](../superpowers/reports/2026-09-23-reassessment-preparation/package.zip). Inside: `README.md`, `READINESS.md`, `MANIFEST.json`, `CONTRACTS.md`, `wire-catalog.json`, `recover_static.py`, `cases/P8-before/input.json`, `objects/` and `authority/`. | Archive instructions/helper become accessible after extracting them to a new destination. Static recovery needs an external standard-library Python; it is not an application run. Prepared NR builds are deliberately nonexecutable. No maintained NR example-binding helper is provided. |
| Historical NR execution/replay | The [local evidence supplement and exact Git history](evidence/v1/README.md) retain manifest-selected bundle bytes, including the c321 P8-before bundle historically at R's `outputs/m180-e-p8-before/`. | Static recovery is separate from execution. Verify/replay still require matching historical source/build and external environment, fresh supported destinations and authority/accounting. No clean-clone execution recipe is implied. |
| Qualification evidence audit | The [recovery index](evidence/v1/README.md) identifies committed acceptance/completion records, launch chain, manifests, ledger, streams, provisioning records and selected external-destination evidence. | The supplement plus required Git providers support manifest-selected static recovery; receipts alone or a shallow/source-only export are insufficient. Missing raw probe output and V1 peak evidence remain disclosed gaps. |

For P8-before, `input.json.members` selects the required objects; do not use every
object in the pool or repair a negative case. Its original selection is at
`23b60a42c2279fc228168967d47491b8983658fb`. Its request, exposure and fixture
authority remain immutable. Any future example binder may change only the NR
build and invocation; it must not mint authority. Recomputing that original
selection requires its own matching historical environment/build. Its expected
T1 recommendation and point-60 `one_compatible` result are synthetic checks,
not evidence of empirical accuracy.

The [accepted recovery inventory, §§6 and Appendices A–D](../superpowers/reports/2026-09-30-post-reassessment-corrected-reconciliation.md)
provides exact digests, archive-member locators and the absolute retained R root.
That inventory is retained with this documentation. Its historical “untracked”
observations describe its recorded checkpoint, not the report's current status.
It distinguishes authority/source, archived recovery and material that was then
untracked or runtime-only. The [retention supplement](evidence/v1/README.md) now
supplies the selected additional bytes, including launch/FINAL evidence and the
recovered environment-stop report, while referencing sufficient existing Git
and archive providers. Its canonical manifest defines the precise closure;
historical inventories are not rewritten to describe the later retention.
[Acceptance](../superpowers/reports/2026-09-30-reassessment-slice5-and-final-owner-acceptance.md)
retains exact source/execution identities, failures, exceptions and accounting.
Do not relabel older runs as FINAL or turn preserved failed attempts compliant.

## Application paths versus existing test requirements

Caller-selected application paths do not make the full test suite portable.
[Delivery accounting](../../tests/reassessment_profile/delivery_budget.py) hard-codes
the historical `nr-slice4-qualification-r1` corpus; its 19 delivery tests are
collected by default. An absent path breaks their setup, and an existing path can
receive writes. **Never run them against historical evidence.**

For a separately authorized test run, the current choices are:

- **Retain delivery coverage:** prepare a fresh private ext4 corpus with exactly
  `outputs, repairs, inputs, logs, recovery, indexes, exports`, a valid genesis
  and no prior outputs, under approved accounting. Make
  `tests/reassessment_profile` importable, set the absolute
  `REL5_CORPUS_ROOT`, and explicitly load
  `-p slice5_delivery_root_adapter` before collection. The
  [adapter](../../tests/reassessment_profile/slice5_delivery_root_adapter.py)
  substitutes ROOT without changing caps/assertions; it does not prepare or fund
  the corpus. Merely setting the variable, TMPDIR or `--basetemp` is insufficient.
  Its XFS setup allowance does not override NR's ext4 requirement.
- **Disclose reduced coverage:** explicitly use
  `--ignore=tests/reassessment_profile/test_delivery.py`. This excludes 19 nodes
  and is not equivalent to the accepted full qualification.

Other release tests require the nominated unsupported-mount paths, exact
environment, historical source/archive inputs and isolated temporary destinations
described in the linked guides. The choices above address the delivery ROOT
defect only; they are not a clean-clone full-suite recipe. No test is authorized
or executed by this documentation delivery.

A maintained helper, test-portability implementation, diagnostic correction and
publication remain [distinct deferred delivery items](delivery-status.md).
Local evidence retention supplies the manifest-selected static recovery route;
execution still requires the disclosed external environment and owner decisions.
Publication and external disclosure remain unauthorized; publication readiness
is not established.
