# Post-reassessment reconciliation — corrected successor

2026-09-30. Documentation-only lead correction following independent review.
**Assessment, not owner approval or authorization to execute the proposed delivery.**
The frozen lead and review remain unchanged. No application, test, recovery helper,
qualification driver or provisioning verifier was executed for this correction.

## 1. Verified checkpoint and answer

| Frozen input | SHA-256, verified over retained bytes |
|---|---|
| [Lead reconciliation](2026-09-30-post-reassessment-lead-reconciliation.md) | `842e6a0bd3a5e8d60f3b1cea7d2e1ef682f05307c6fb0affed933cbaf71fc9cb` |
| [Complete independent review](2026-09-30-post-reassessment-lead-reconciliation-adversarial-review.md) | `3336db0f6e2dd6a01c58171a4351a246ef1c03c5522bd3e430be1d17290f5d16` |
| [Slice 5 and milestone acceptance](2026-09-30-reassessment-slice5-and-final-owner-acceptance.md) | `a98286666e9de0e24db10e6c6dda5fd7719510442151ce3e9b76b03d4cee7a9c` |

HEAD remains `239d9eada4fbf65ad539919161df9bc62d149684`; no intervening
commit changes the assessment. Accepted application source is
`c321f2e096a71a43bf65787f6f1605c4031266e7`, FINAL execution revision is
`f28de9e900c700d910eb5edf2b0e6f8c336472fe`, and verified harness commit is
`509a43b1f71a3ed83bdcff7055512c28535b2b37`.
Their common application tree is `5a46b1fc064b15331ad185b2bb245bbcec9eeeec`;
backend tree is `652b9a21cac36c18a6181f2676d4a7b36fb47637`.
Administrative HEAD is not a newly tested executable.

**What a user can accomplish:** a technically equipped user can separately run
bounded selection and reassessment on explicitly supplied, authorized artifacts,
retain reasons and uncertainty, and verify or independently recompute a retained
result at its matching executable identity. Connecting a fresh selection to a
new reassessment requires manual artifact composition and a newly authorized
reassessment request. There is no maintained end-to-end authoring command.
The accepted historical examples are recoverable demonstrations of those
contracts; they do not confer permission for a fresh workflow.

**Smallest useful next delivery:** documentation-only consolidation for technical
users and evidence reviewers: a maintained reassessment guide, two distinct
example/recovery descriptions, corrected preparation and test-suite instructions,
and a classified evidence index. This advances usability of objectives 3, 4 and 7
without selecting a new capability. A helper, portable delivery-test setup,
diagnostic change and evidence export are separate options (§7).

## 2. Seven objectives, with the accepted bounds retained

| Objective | Shipped backend contracts | Maintained application | Supplied premises / human decisions | Experimental evidence only | Remaining gap / exclusion |
|---|---|---|---|---|---|
| 1. What exists and how is it connected? | Model revisions, hierarchy/relationship queries, ports, connections, interfaces and variable/flow associations. | Captures and validates the model, subject, variable and binding used by the selected profile. | Entities, topology, lifecycle views and meanings. | Synthetic topology demonstrates declarations. | No discovery, general model browser or physical completeness claim. |
| 2. What is the current state? | Receipt-axis temporal queries, model state, value/semantic/constraint evaluation, public state classification, evidence assurance/alignment and endpoint assessment. | Admits a supplied public snapshot at an exact cutoff; keeps original baseline and supplied result distinct. | Source/cutoff/model selection, units, tokens, acquisition and conditions. | Synthetic snapshots and transition witnesses. | No global freshness, live acquisition, monitoring or automatic state mutation. |
| 3. Why might it behave this way? | Declared behavior and evidence-gated transition evaluation. | Model-relative compatibility, conditional incompatibility, unresolved and baseline-ineligible results for nominated hypotheses; separate fixed thermal projections. | Hypotheses, laws, prediction/support warrants, decoder, uncertainty, conditions and permission. | BRC, conditional-prediction and model-derived-prediction finite proofs remain historical. | No causal diagnosis, generated hypotheses, arbitrary-law inference or empirical accuracy guarantee. |
| 4. What is the next best measurement? | Evidence admission and provenance contracts; ranking is application-owned. | Prior-free minimax over nominated procedures; ties retained, unsupported whole-set ranking withheld, unique positive-reduction winner may be recommended. | Nominations, decoder, qualified support/exclusions, D/A/T authority and policy; human acquisition decision. | Earlier experimental selectors are not maintained entry points. | No global optimum, generated procedures, acquisition or automatic post-result reranking. |
| 5. What would a change affect? | Explicit relationships/dependencies, alignment and endpoint assessment. | Fixed thermal/governed review of 22/23 decision slots; required review, performed work and comparable changes distinguished. Reassessment carries changed references and dependency traces. | Prior material, nominated changes and human review. | Broader influence dossiers are analytical where not implemented. | No general dependency discovery, cross-profile propagation or CI-001 implementation. |
| 6. What is the smallest valid change? | Constraints, behavior, state, flow criteria and transition declarations support evaluation. | Separate fixed two-hypothesis/four-action, one-step rational projection; least-cost selection among nominated robust-feasible actions. | Effects, bounds, target, costs, authority, nominations and human execution/adoption. | Historical one-step proof has its own scope; maintained delivery has separate acceptance. | Finite-set least cost is not globally smallest change. No generated actions, multistep planning, actuation or NR-to-action adapter. |
| 7. What is observed, calculated, inferred, assumed or unknown? | Typed evidence, immutable revisions, provenance and explicit unavailability. | Support reasons, uncertainty, authority/exposure disclosures, traces, bundles and recomputing replay; derived, not adopted. | Local attestations, bases, declared chronology, pins and human decisions outside the application. | Same-author synthetic oracles establish scoped consistency, not empirical truth. | No authenticated truth, universal epistemic ontology, automatic adoption or general robustness. |

Evidence: [model queries](../../../backend/model_kernel/queries.py),
[state-classification contracts](../../../backend/state_classification/contracts.py),
[application guide](../../../applications/bounded_decision_workflow/README.md),
[selection coverage](../../next-measurement/coverage.md),
[ranking](../../../applications/bounded_decision_workflow/measurement_ranking.py),
[support qualification](../../../applications/bounded_decision_workflow/support_qualification.py),
[reassessment computation](../../../applications/bounded_decision_workflow/reassessment_compute.py).
No backend frontier expansion follows from this correction. Physical validation
remains deferred; IN-001 and CI-001 remain open and unselected.

## 3. Platform acceptance, qualification and the diagnostic

| Surface | Actual source acceptance | Retained platform evidence / limit |
|---|---|---|
| Selection and thermal/governed retained I/O | Shared retention accepts ext4 or XFS. | Qualified local Linux/WSL ext4 environment. XFS acceptance in code is not empirical XFS qualification. |
| Reassessment invocation/objects, retained bundle and output | ext4-only checks in capture and runtime; XFS is refused. | Accepted ext4 runs. No XFS, Windows/DrvFS, network-filesystem or general portability claim. |
| Delivery-root adapter | Its setup check accepts ext4 or XFS. | This does not broaden NR's ext4-only application boundary. A corpus intended to exercise NR must be on ext4. |

See [capture](../../../applications/bounded_decision_workflow/reassessment_capture.py)
(`capture`, input-parent and objects-directory checks),
[runtime](../../../applications/bounded_decision_workflow/reassessment_runtime.py)
(`_filesystem`), and [shared retention](../../../applications/bounded_decision_workflow/retention.py)
(`_filesystem`, `_fail`). The committed NR package's `CONTRACTS.md` also
specifies ext4 (§6 locators). Recognition by command code, filesystem setup
acceptance, and observed qualification are three different statements.

**M1 diagnostic qualification:** shared `FILESYSTEM_UNSUPPORTED` constructs the
misleading retry hint `choose_supported_ext4_xfs` when invoked from NR.
However, [reassessment CLI](../../../applications/bounded_decision_workflow/reassessment_cli.py)
lines 53–65 copies code/target/status and emits its own generic
`retry: correct_input`; it does not forward that shared hint. Thus the review's
specific claim that the NR CLI prints the ext4/XFS hint is not supported by this
source path. The shared diagnostic remains misleading for an NR caller, and the
CLI gives no useful ext4-specific remedy. A profile-appropriate diagnostic is a
possible, separately scoped code correction (§7 C2). This report changes neither
diagnostic nor filesystem semantics. Changing the shared hint globally to ext4
would incorrectly narrow the selection/thermal description.

## 4. Handoffs, identity propagation and authority

### 4.1 Actual manual journey

| Step | Contracts and implemented handoff | Required human / owner-authorized act |
|---|---|---|
| Admitted evidence | Caller supplies `nm.evidence.v1` carrying a public `StateClassificationResult`, context, token roles and bindings; public validators check owning subject/variable/cutoff/unit joins. | Construct the public result through backend composition and select evidence/context. There is no raw-ingestion or result-wrapper authoring command here. |
| Nominated hypotheses and procedures | `nm.request.v1` names hypotheses, measurements, decoders, support and policy. D/A/T declarations, permission and any required working adoption are distinct from predictive support. | Supply and attest actual premises and authority. Putting an object in a directory is not nomination or permission. |
| Next-measurement selection | `measurement-evaluate` admits the invocation and pin, qualifies support, ranks the nominated set, and writes seven retained files. | Decide whether to acquire a measurement. The recommendation grants no acquisition authority. |
| Selection-to-NR material | Reuse original typed objects, or decode and hash-check the base64 closure into `<sha256>.<kind>` files. Carry original invocation/selection and, if declared, the exact retained bundle via `nr.retained-bundle.v2`. | Manually construct the descriptor and references; preserve original bytes and their historical identity. No maintained converter performs this handoff. |
| Supplied result | `nr.observation.v2` references evidence, nominated procedure and decoder. `nr.execution.v2` carries original/result contexts, acquisition interval and availability/applicability/calibration/fidelity/hold declarations. | Supply actual result evidence, uncertainty, provenance and truthful conditions. No instrument integration or default truth is supplied. |
| Reassessment permission | `nr.exposure.v2` declares original invocation, observation, optional prior bundle, relation and learning/commitment chronology. `nr.request.v2` binds these plus procedure, decoder, execution, interpretation and policy. `nr.authority.v2` binds that exact request. | An authorized owner/attestor must make the new permission-bearing declaration and approve its exact pin. Hashing or copying fields cannot issue permission. This task issues none. |
| Reassessment | `reassessment-evaluate` computes compatibility and reasons while retaining original nominations. The chosen procedure must be in the original request, not necessarily its recommendation. | Review withheld/unresolved support and uncertainty. Successful command completion may represent denial or withholding. |
| Human decision (outside the application) | `summary.disposition` is a computed classification such as `one_compatible`; `ranking=not_reassessed`, `adoption=derived_not_adopted`, policy `adoption=manual_only`. | A person may, for example, retain, reject or defer a conclusion. These are illustrative actions, not an implemented human-disposition protocol. No command adopts or mutates the original model/request. |

Transport precision for the review's M2 list: retained `manifest.json`,
`result.json` and `trace.json` are carried as opaque **`nm.basis` references**;
their decoded inner schemas must respectively be `nm.bundle.v1`,
`nm.result.v1` and `nm.trace.v1`. Those inner schema names are not new
transport object kinds. The descriptor has seven sorted file rows: invocation,
closure, result, trace, build, policy and manifest. The closure row uses the
`original_closure` recipe with original header and typed members; it is not
a renamed opaque file. Other roles use their required typed references.
[Capture's prior-bundle reconstruction](../../../applications/bounded_decision_workflow/reassessment_capture.py)
checks lengths, digests, roles, build/policy linkage, manifest members and
selection/request linkage. [Contracts](../../../applications/bounded_decision_workflow/reassessment_contracts.py)
and [admission](../../../applications/bounded_decision_workflow/reassessment_admission.py)
define the joins. Integrity does not prove exposure chronology or recompute the
original selection.

### 4.2 Exactly which changes propagate

1. A new actual NM build changes `nm.invocation.v1.build_identity`; therefore
   invocation bytes and digest change. The selection pin need not change solely
   for this rebinding if the original request and selection authority remain
   byte-identical and applicable. Changed nominations/premises require their own
   valid revised NM references and authority.
2. An actual new selection run produces its own bundle, including invocation,
   build and manifest observations. Carrying that bundle requires a corresponding
   retained-bundle descriptor and exact file commitments. It is not legitimate to
   relabel the old witness as the new run.
   If the original selection authority changes, NR's `original_selection_pin`
   must also change to match that invocation. A ranking/result/trace-byte change
   changes the prior-bundle descriptor when carried, and consequently exposure
   and request references; the recommendation itself never issues NR permission.
3. Referring to the new original invocation changes
   `nr.request.v2.original_invocation` and
   `nr.exposure.v2.original_invocation`. If a prior bundle is declared,
   `exposure.prior_bundle` must name the matching descriptor. These changes
   produce a new exposure digest and then a new request digest.
4. New result/evidence/provenance/conditions change observation and/or execution
   bytes and their references as applicable. They are **not necessarily changed
   by an NM build-only rebind**. Their existing values cannot be reused to make
   false declarations about a newly acquired result.
5. Since `nr.authority.v2.request` binds the exact NR request, its permission
   declaration must be newly attested for that new request. Its digest becomes
   the new `--authority-pin`, and the NR invocation's request/authority
   references change. NR build binding independently changes its build reference.
   Revision/predecessor rules remain enforced; there is no permission-generating
   mechanical conversion.

No new authority, request, exposure, result or invocation was authored here.

### 4.3 Two examples, not one fresh authorized chain

**Selection P:** [existing recovery helper](../../next-measurement/recover.py)
reads frozen input premises, binds the actual `nm.build.v1`, rewrites the NM
invocation and preserves the selection pin. The committed helper does not mint
permission. A newly bound run is a new invocation; it is not the historical
selection embedded in P8-before.

**NR P8-before:** use its committed original historical selection and retained
bundle as immutable evidence. Only the prepared NR build and NR invocation can
be replaced for an actual-build example binding; request, authority, exposure and
all other input premises must remain byte-identical. Existing binding logic is
test code in [`actual_case`](../../../tests/reassessment_profile/test_capture.py);
it is not a maintained user helper. Replaying the original selection itself
requires its matching historical checkout/environment; NR carrying that selection
does not rerun its ranking. A helper for this second example would be new
executable fixture code and is excluded from the minimum (§7 B).

Committed witness locators are under
`D/2026-09-23-reassessment-preparation/package.zip::objects/` (D defined in §6):

| Object filename / identity | Meaning |
|---|---|
| `1369a8df87e823e55ea436461f64d594450ad08e0f51d779cf15efb66e963567.nm.invocation.v1` | Historical original selection invocation. |
| `7e94de3a64c6dbcf303406d39d4c63be415aaa82599ce268478c5831cda9ff80.nm.selection.v1` | Original selection permission pin. |
| `870ad9750fbef990a54180c2e10a7d4884b723d2c82dd9f2f9e188cec637ac7a.nm.build.v1` | Original build at `23b60a42c2279fc228168967d47491b8983658fb`. |
| `03be226fecbb1ae952f50fae001ccbd2633655d15327f28c539ef1b49f36e262.nr.request.v2` | Frozen reassessment request. |
| `d9075ed1e7ab334cc425f2981f510968b2e2fa9cad09c84febf8c6d2944448e0.nr.authority.v2` | Its fixture permission, attestor `local-static-fixture-author`; not a fresh grant. |

The chosen P8-before fixture is one of the package's cases, not its only committed
NR case. Original selection scores T1/T2 as 1/2 worst survivors and recommends
T1 within that supplied set. The supplied point 60 produces `one_compatible`
under the example's premises; neither result establishes empirical validity.

**Runtime-only historical execution:** NR invocation
`b63b164431070454c1fd4fa0874cb80f03cf3c92bd0208a16daa60df3ed4a03d`
and `R/outputs/m180-e-p8-before/manifest.json` SHA-256
`b0487f75feb727e254cf825181cedab6f66a9cd9e7650ffcfbbec261c5662748`
belong to the c321 run, not FINAL. The committed original witness does not need
those runtime files for its static recovery; exact recovery of this execution does.

### 4.4 Command contracts and stale inputs

The following is command grammar, not a launch instruction. PY is an absolute,
approved interpreter; inputs must be valid and authorized, output directories
new, and the relevant filesystem/resource constraints satisfied.

```text
PY -m applications.bounded_decision_workflow measurement-evaluate --invocation I --objects-dir O --authority-pin NM_PIN --output-dir M [--limits L]
PY -m applications.bounded_decision_workflow measurement-verify --bundle M
PY -m applications.bounded_decision_workflow measurement-replay --bundle M --output-dir MR [--limits L]
PY -m applications.bounded_decision_workflow reassessment-evaluate --invocation NI --objects-dir NO --authority-pin NR_PIN --output-dir N [--limits L]
PY -m applications.bounded_decision_workflow reassessment-verify --bundle N
PY -m applications.bounded_decision_workflow reassessment-replay --bundle N --output-dir NR [--limits L]
```

N1: NM argparse permits omission of `--authority-pin`, but
[measurement runtime](../../../applications/bounded_decision_workflow/measurement_runtime.py)
refuses a v1 invocation without it (`AUTHORITY_PIN_REQUIRED`). It is effectively
mandatory. NR verify re-admits and checks integrity; replay recomputes
result/trace. Build equality includes checkpoint and environment; a documentation
commit does not make an old bundle replayable under an arbitrary new HEAD.

A further stale-identity gate is `ORIGINAL_CONTRACT_UNSUPPORTED`:
[NR capture](../../../applications/bounded_decision_workflow/reassessment_capture.py)
rejects an original NM build whose `contract_sha256` differs from current
`measurement_build.CONTRACT_SHA`. [NR build](../../../applications/bounded_decision_workflow/reassessment_build.py)
commits `supported_nm_contract_sha256`. Current NM contract is
`2e802d1a04f570378c83963d21f7979415b061bc7f68794024a2c9fc9231fa24`.
A future change to that contract prevents reassessing these old selections under
that new build unless compatibility is separately designed. It does not erase
replay using a preserved matching historical executable.

Exact context/cutoff joins and immutable references reject substitution; they do
not discover newer evidence. Reassessment evaluates eligibility against the frozen
original baseline. Missing/conflicting warrants, mixed permit/exclude cells,
unknown acquisition or conditions, and inadequate uncertainty remain unresolved
or withheld. Confidence-only uncertainty is not converted into a hard interval.
Chronology is declared, not authenticated custody. Manual C remains unresolved.
No invented feedback-ingestion requirement is needed: supplied public result
evidence already has an implemented admission route.

**Action boundary:** the separate `evaluate --request --snapshot --output-dir`
and `governed-evaluate --invocation --objects-dir --authority-pin --output-dir`
routes (optional `--compare-to`) retain bounded projection/selection.
No implemented adapter turns an `nr.result.v2` into their thermal premises,
action nominations or adoption. Any such next request is separately supplied
and authorized; it is not part of this journey or proposed minimum.

## 5. Host portability and stale user instructions

### 5.1 Application portability versus test-suite portability

The application accepts caller-supplied paths within its Linux/local-filesystem,
environment and build-identity restrictions. That does not make the test suite
host-portable. [Delivery budget](../../../tests/reassessment_profile/delivery_budget.py)
line 11 hard-codes
`W/nr-slice4-qualification-r1`; [delivery tests](../../../tests/reassessment_profile/test_delivery.py)
import `ROOT` by value before their fixture writes.
`pyproject.toml` collects `tests/`; the normal conftest optional CAD/PDF skips
do not exclude these 19 delivery nodes.

Consequently, the guide's generic full-suite instruction at HEAD is incomplete:
on a host without that root these tests cannot use their expected corpus; where
it exists, an unadapted launch can write into historical evidence. This is a
source-established portability defect, not a new observed test run. Changing
pytest's basetemp or setting TMPDIR does not repair this separate ROOT reference.

The documentary correction must offer these explicitly distinct paths:

- **Full delivery coverage:** separately authorized preparation of a fresh private
  ext4 corpus with all seven categories (`outputs, repairs, inputs, logs,
  recovery, indexes, exports`), valid genesis and no prior test outputs; explicit
  `REL5_CORPUS_ROOT`, module search path for the test plugin, and
  `-p slice5_delivery_root_adapter` loaded **before collection**. The
  [existing adapter](../../../tests/reassessment_profile/slice5_delivery_root_adapter.py)
  substitutes `delivery_budget.ROOT` before the test's import and retains caps
  and assertions. Environment-variable setting alone is insufficient. The
  adapter checks for an index JSON, not the complete authorized genesis/accounting
  history: that preparation must be specified and verified separately.
- **Explicit reduced coverage:** `--ignore=tests/reassessment_profile/test_delivery.py`
  omits those 19 nodes. Such a run is not the accepted 5,304-node qualification.
  This is disclosure of an option, not permission to run it now.

No instruction may use a historical corpus. The smallest code correction, if
selected later, is explicit fresh-root configuration/fixture setup with a
fail-closed missing-configuration path, preserving the existing shape, genesis,
CAPS, assertions, isolation and accounting, with no historical fallback.
It needs its own scoped verification (§7 C1). Documentation alone cannot remove
the defect or promise an unmodified portable full suite.

### 5.2 Commit-precise preparation correction

The preparation directory
`D/2026-09-19-next-measurement-preparation` was absent at
`23b60a42c2279fc228168967d47491b8983658fb` and c321.
Commit `b085e0ee65cefd770bb2cba82e834aebb82c50e4` added it before FINAL f28.
The [selection guide](../../next-measurement/README.md)'s “absent initially”
instruction is stale from b085 onward, including HEAD; it was accurate at the
older candidates.

Read-only archive comparison here found **all 1,194 files byte-identical**:
1,191 manifest payloads plus `package.zip`, `MANIFEST.json`, `recovery.json`.
Running `recover.py --package-dir` against the already present destination
would raise an uncaught `FileExistsError` at `mkdir(exist_ok=False)`,
not a structured refusal. The minimal guide correction is to recognize already
present verified material, and reserve recovery for an absent, separately chosen
destination. No fixture replacement or cleanup is needed.

## 6. Recovery inventory and publication readiness

### 6.1 Locator and purpose conventions

- D = `docs/superpowers/reports`; T = `tests/reassessment_profile`;
  A = `applications/bounded_decision_workflow`, relative to this repository.
- B = `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow`.
- W = `B/test-workspaces`; R = `W/nr-slice5-qualification-r1`.
- P = `D/2026-09-23-reassessment-preparation/package.zip`.
- `archive::member::nested-member` is an exact ZIP locator, not a filesystem path.
- **C** = committed file; **Z** = byte-identical committed archive member;
  **U** = untracked local file; **R** = runtime-only (including provisioning
  outside R itself). A loose U copy may also have a Z recovery location.
- Purpose **A** = required authority/design; **E** = executable reproduction;
  **Q** = qualification/audit evidence; **H** = optional historical navigation.
  Historical failures and corrections are Q when auditing acceptance, not
  disposable H. Requiredness depends on whether the claim is source use, example
  recovery or complete qualification recovery.

Appendix A inventories every unique 64-hex commitment in the acceptance and
completion reports: **33 total, 27 raw-file hashes and six structured identities**.
Appendix B supplies the expanded file inventory: all 46 v9 artifact entries,
static local driver dependencies, reviewer additions and provisioning prerequisites.
The v6/v7/v8 artifact path sets add no paths beyond v9. Full retained populations
are indexed by their authoritative manifests/ledger families below rather than
flattening the runtime tree into this report. This is a dependency inventory,
not a portable evidence export or a claim that every historical byte was freshly
revalidated here.

### 6.2 Transitive dependencies, including those outside the receipts

| Dependency closure | Availability and purpose | Concrete recovery boundary |
|---|---|---|
| Accepted source and tests | C; E/Q. Exact commits in §1; source manifests inside retained build files. | NR build enumerates 172 source entries. Historical NM, S6 and governed replay need their own recorded commits/builds; current source equality does not replace them. |
| NM preparation/example | C/Z; A/E/Q. `D/2026-09-23-next-measurement-slice6-correction-evidence/frozen-authority.zip::{package.zip,MANIFEST.json,recovery.json}`, current committed preparation directory, and `docs/next-measurement/{README.md,recover.py,coverage.md}`. | Inner package SHA `a6e48ea447444e4f7c12993d9567905978c2a0c8972414e0ac421df47cd2217f`; manifest `18ed716ab327944f700b8e00b30235512a9ea6d5b41f49e87ab88b343680e2ea`; recovery `ecfe3f62d796a21edc5509419206aebb68d46d8d3f10736d6708c412110a8dac`. |
| NR preparation/contracts/input closure | C/Z; A/E/Q. P, `P::MANIFEST.json`, `CONTRACTS.md`, `wire-catalog.json`, `objects/`, `cases/`, `README.md`, `recover_static.py`. | P: 33,618,258 bytes, SHA `454736288217a5c66e8cf6875069aba3a60dee04005c5644d95135adbc8110fb`; 2,030 manifest members. Manifest/NR contract SHA `3a7c1d176c2231e8b9b938e404b2500e32eb87bfd12cdf046f144d0953edf0cf`. Static recovery instructions/helper are only inside ZIP; no maintained external NR guide/helper exists. |
| NR design authority | Z; A. `P::authority/` contains the 09-23 lead proposal, corrected candidate, focused review, independent adversarial review, preparation discrepancy and prior-bundle carriage amendment, each with its full dated filename. | `P::authority/commitments.json` and package manifest bind them. Amendment SHA `d7136af5c4a086361e92be159d9aadc3c9d552d315dc2b2a3ecbf7df952a1676`. Loose amendment is U, but its required authority bytes are recoverable from P. |
| NR embedded prior context | Z; A/E/Q. `P::authority/accepted-source-context.zip` (164 members), `next-measurement-frozen-authority.zip`, `recovery.zip`, `expected-files.json`, `reconstruct.py`, witness/snapshot/schema files. | Nested manifests and expected-files index bind original seven-file NM bundle and public-result material. Decode/extract instructions must preserve originals. No runtime corpus is necessary merely to inspect this historical witness. |
| Carriage evidence | Nine loose files U+Z; one U only; E/Q. Exact mappings in Appendix C. | `recovery-receipt.json` has no equal member in the eleven searched committed reassessment ZIPs/nested ZIPs. Do not call the entire loose folder committed, or the entire folder missing. |
| Earlier slice acceptance and qualification | C/Z; A/Q, eleven committed reassessment ZIPs under D. Slice 1–4 acceptance reports point to their respective evidence. | Those archives do not contain the complete latest Slice 5 environment-corrected chain. Original synthetic oracles remain comparison evidence, never production inputs. |
| Release authority and schedule | U; A/Q. 09-25 consolidated plan/owner approval, architecture/readiness review, fresh M180 schedule; 09-26 campaign report and 09-29 correction. | Appendix B exact locators/digests. Required for qualification provenance; old campaign completion claim remains withdrawn. General earlier drafts outside this chain are optional H. |
| Corrected launch chain | Mixed C/U; E/Q. v9 artifact map and Appendix B. | Actual static chain: v13 → v11 → v9 → fetch-verification v8 → fetch-comparison v7 → resume v6 → repairs v2 → budget v3. v13 installs launcher v4, environment helper, controller v5, routing v2; launcher/reporters/adapters and their local imports are transitive dependencies. Old launcher v2 referenced by repairs v2 remains historical support; overridden for final launches. Preserve versions/diffs, do not execute the historical campaign drivers as user examples. |
| Approved external environment | R outside R corpus; E/Q. `B/provisioning/`, `B/dependency-artifacts/`, `B/environments/cp313-bdw001/`. | Provisioning verifier reads artifact/environment/lock manifests, hashed lock, persistence probe and its evidence; wheel manifest lists ten exact artifacts. Installed trees, base CPython 3.13.11 binary, venv configuration, SOABI and pip 25.3 bootstrap are separate prerequisites. Linux x86_64/ext4, resource controls and system utilities are not supplied by Git. No installation or executable probe was done here. |
| Accepted control/V2/V3/FINAL | R; Q. `R/regressions/rel5-{control-env-replacement-1-accounting,V2-env-replacement-1-boundary,V3-skips-bytecode,FINAL-full-release}/`; corresponding specs, results, streams, environment identities, samples, diagnostics, gate/closeout records and frozen skip manifest. | FINAL runtime-only streams record 5,304 nodes, 5,269 passes, 35 expected skips, all 19 delivery nodes; this remains the accepted retained finding, not a rerun. Stream hashes and stop recovered in this read-only inventory. A repository-only reader cannot verify those stream contents. |
| Matrix, controls, clean delivery and recovery | R; Q/E. Fresh schedule → `R/inputs/`, `logs/`, `outputs/m180-*/`, C6/G-clean outputs and ledger comparisons; `R/repairs/g-app-r2/`; `R/recovery/campaign-copy-{1,2,3,4}/` and associated H4 outputs. | Ledger event paths/stream commitments and each bundle manifest/closure enumerate their members, not receipts alone. Matching c321 build and original cases needed. `W/s7-release-Gvdefi/historical-w0/` plus its `environment/` is separate historical H-v1 dependency. |
| Accounting and external destinations | R; A/Q. `R/indexes/*-record.json`, ordered-file reconciliation 0282, funding/reservation/claim/closeout records through 3595; registration paths; baseline inventories; preserved checkouts/repairs/logs. | Do not substitute only a final tip for the ledger or claim an unbroken chain before the disclosed reconciliation. External export entries require their exact destination bytes. Separate `W/nr-slice5-delivery-final/`, negative destination and additive Git inventory are charged once, not subsumed invisibly into R. External paths are recorded in FINAL spec/storage observations and ledger. |
| Adverse history | Mixed U/R; Q. Both V1s, wrong-environment control/V2, abandoned repairs, original/revised campaign reports, unauthorized probe 3440 and correction 3442. | Required to preserve acceptance limitations and consumed accounting. Functional V1 exception does not qualify either failed attempt. No retrospective compliance, refund or replacement evidence is created. |

Environment raw manifests and their field commitments are deliberately distinct.
The base interpreter commitment is
`47f615b1be25c94e9304ccd9339f9a8ef21d2194fca32643c441fb2dad290264`;
the environment manifest records ten installed-tree commitments, while the artifact
manifest records ten wheel-byte commitments. Neither installs an environment or
provides the OS. An offline portable reproduction package is therefore not
established by a dependency lock and acceptance receipt alone.

Historical execution identities remain separate: M180/C6/G-clean/H4 and G-app
current delivery at c321; G-app S6 recovery at
`c37c24ee50667121d6b2dc4739aa3b7d12825c96`; H-v1 governed replay at
`250da5e66479ee1dd2e7c24cd81905509ffe5969`; FINAL at f28.
Their exact build hashes/IDs appear in Appendix A. H-v1 used its own retained
historical environment, not a relabelled cp313-bdw001 launch.
The acceptance/completion records also name administrative matrix harness revision
`8d0f09f4449fe3c3eaa21460c75f4d41a9446c69` and harness-commit parent
`29fa81648a35e66525a8172775d5954dfc92390b`. These local Git recovery references
are not alternative application execution identities.

### 6.3 Environment-stop investigation

**Located, not recreated:** `R/regressions/rel5-V2-boundary/continuation-stop.json`,
6,064 bytes, SHA-256
`41161b77f57862e06eda2c0148228759fc665b83ee1fe1807c0eee4d716f5df9`.
Its bytes match the commitment in acceptance/completion, v9 and
`R/indexes/3519-record.json`; replacement funding record 3520 preserves it.
The JSON retains the administrative-.venv mismatch, consumed control/V2 with
qualification withdrawn and unlaunched later slots at that stop.

I searched the eleven committed reassessment ZIPs recursively through nested ZIPs
for matching-size/hash members; none contained this report. The review's
repository-only gap is confirmed, but the report is recoverable locally under R.
No gap was filled by reconstructing prose or regenerating a stop. Exporting those
bytes would be a new, separately authorized operation.

### 6.4 Local publication blockers and disclosures

A repository-only reader can recover source, preparation packages, original
example premises and earlier slice evidence. They cannot recover all of the
latest qualification chain from Git. Acceptance → completion is an untracked
target; further completion links are absolute administrative/runtime paths.
The inventory makes these dependencies visible, but does not publish them.

Installation still needs the specified interpreter, dependency artifacts and
supported storage; optional PDF/CAD absence explains the accepted 35 skips
(23 PDF, 12 CAD). The test portability defect and both stale instructions (§5)
remain present in their original files because only this successor is authorized.

The prior local comparison recorded `origin/main=15bd9dc`, HEAD 57 ahead and
0 behind, adding 1,013 blobs / 111,079,804 bytes. That is local remote-reference
information, not a fresh remote/publication check. No remote operation occurred.

Any future export from R must be explicitly authorized and ledger-accounted,
including destination category, physical allocation, entries, directories,
indexes and external bytes exactly once. A documentation index grants no draw.
If historical untracked launch helpers are retained, preserve them as
manifest-bound archive members under D, with their imports/environment references;
do not quietly stage loose `tests/` modules as maintained user code.

Host-path disclosure is an owner publication decision for **existing as well as
new** material: delivery/qualification modules, root adapter, interpreter paths,
recovery receipts, acceptance/completion links and this report include local
paths. Approved presentation redaction may use a separate derivative with an
original commitment; it must not rewrite frozen historical bytes or pretend a
redacted copy retains the original hash. No export/redaction is performed here.

## 7. Consolidation options — distinct scope and gates

### A. Documentation-only minimum — recommended

- **Audience:** technical application users and local evidence reviewers.
- **Deliverables:** maintained NR guide/navigation; exact command/input/identity
  and filesystem table; selection P and historical NR P8-before as two separate
  recovery descriptions; manual fresh-handoff/authority explanation; correct
  preparation and full-suite instructions; classified acceptance/transitive
  evidence index with package and runtime locators.
- **Acceptance criteria:** every claim links to maintained code/contract or a
  correctly classified retained artifact; all 33 root commitments classified;
  both stale instructions corrected; archived inputs clearly distinguish authority
  from expected outputs; unknown support/manual decisions disclosed. Application
  and backend trees remain byte-identical to §1. No new executable, schema,
  command, policy, helper, permission or capability.
- **Authority/disclosure:** owner selects this document scope and audience.
  It may disclose the present recovery gap and existing local paths; public
  disclosure is a separate owner decision.
- **New code/execution:** none. Static link, hash and source review suffice.
- **Remaining limitations:** manual handoff, no fresh authority authoring tool,
  no maintained NR build-binding helper, host-coupled tests, misleading shared
  diagnostic and runtime-only qualification remain. This minimum does **not**
  promise that a clean clone can execute both walkthroughs unaided.

This replaces the lead's bundled recommendation. The review's proposed
“clean clone plus approved environment reaches both walkthroughs” execution
criterion belongs to option B if selected, not to this non-executing minimum.

### B. Optional maintained walkthrough / fixture helper

- **Audience:** developers who need a reproducible synthetic NR example.
- **Deliverables:** a documentation/fixture helper outside production, plus a
  bounded walkthrough that locates the committed archive and binds the actual NR
  build/invocation. Reuse the existing NM helper for its separate selection example.
- **Acceptance criteria:** no imports from tests; no expected output supplied to
  production; only `nr.build.v2` and `nr.invocation.v2` rewritten. Assert
  byte-identical authority, request, exposure and other premises. New private
  outputs; no hidden untracked/runtime inputs for the documented examples.
  Preserve exact historical selection identities. Verify recovery, binding,
  authority preservation and refusal behavior under explicitly approved limits.
- **Authority/disclosure:** separate code and verification authorization, frozen
  diff, environment, write paths and accounting. A helper is not a production
  command or trust boundary. Fresh NM→NR permission issuance remains outside it.
- **New code/execution:** yes, both. Not a prerequisite for A or currently approved.

### C1. Optional delivery-test portability correction

- **Audience:** maintainers and users attempting the repository suite on another host.
- **Deliverables:** smallest explicit fresh-corpus configuration/fixture correction
  described in §5; no historical fallback; documented environment and accounting.
- **Acceptance criteria:** retain all 19 assertions and original caps; isolated
  authorized fresh corpus, exact genesis/shape and complete child/path accounting;
  reject absent/unsafe configuration and historical destinations; run the selected
  portability/delivery verification only under a separately approved scope.
  Preserve historical tests/results as evidence, and label new results with their
  actual source/environment.
- **Authority/disclosure:** separate test-code and execution approval and bounded
  resource reservations. Existing acceptance does not grant another FINAL.
- **New code/execution:** yes. Application semantics unchanged. Optional for A;
  necessary before claiming an ordinary portable full suite.

### C2. Optional profile-correct filesystem diagnostic

- **Audience:** command/library users encountering unsupported storage.
- **Deliverables:** narrowly scoped NR-appropriate diagnostic and explicit useful
  CLI guidance, preserving selection's ext4/XFS acceptance and NR's ext4-only rule.
- **Acceptance criteria:** emitted diagnostics truthfully describe each route,
  including the CLI's translation path; no assertion weakening, filesystem
  admission expansion or semantic change. Retain the historical diagnostic evidence.
- **Authority/disclosure:** separate application-code correction and focused
  verification approval. This option changes application source identity and
  therefore cannot hide inside A's byte-identical application-tree criterion.
- **New code/execution:** yes. Not authorized by this documentation task.

### D. Optional evidence-retention / export delivery

- **Audience:** independent offline qualification reviewers and prospective publishers.
- **Deliverables:** selected manifest-bound archives of missing authority,
  corrected launcher dependency closure, schedule/skip manifest, correction and
  completion reports, environment-stop, selected ledger/stream/bundle evidence,
  and an explicit external-environment inventory. Appendix A–C defines the
  dependencies; any exclusions must bound the advertised recovery claim.
- **Acceptance criteria:** each selected commitment resolves to exact bytes;
  authority, reproduction and qualification members remain distinguishable;
  transitive imported helpers and external registrations are accounted for;
  source/build revisions remain historical; all adverse evidence needed for the
  claimed acceptance audit is retained. No “complete offline reproduction” claim
  without the corresponding environment and runtime closure.
- **Authority/disclosure:** owner selects archive contents, audience, host metadata
  and permitted destinations; separately approve ledger-accounted preparation,
  exports and any recovery verification. Preflight exact logical/physical/count
  envelope and backing headroom before writing. The inventory is not a reservation.
- **New code/execution:** archive construction and hash/recovery validation are new
  operations; a new application feature is unnecessary. Whether an executable
  recovery check is included must be separately selected. No export now.

**Coherent minimum:** A alone. B, C1, C2 and D solve different additional needs and
are not prerequisites bundled into it. None selects new semantics, IN-001, CI-001,
an ADR, a backend milestone or a successor capability.

## 8. Individual correction dispositions and owner decisions

| Review §5 correction | Findings/notes | Disposition with evidence |
|---|---|---|
| 1 | M1 | Corrected in §3: NR ext4-only; NM/shared routes accept XFS without XFS qualification. Qualified the review's claimed CLI hint using `reassessment_cli.py`; proposed diagnostic code correction separately. |
| 2 | M2 | Corrected in §4.1–4.3: manual transformations, exact digest propagation, owner-attested new request authority, and two separate examples. Refined transport kinds to `nm.basis` with checked inner schemas; no invented permission. |
| 3 | M3 | Corrected in §6 and Appendices A–C: all 33 root commitments, 46 v9 entries, reviewer additions, transitive source/environment/runtime families and exact archive locators. Stop found hash-equal under R; repository-only gap retained. |
| 4 | M4 | Corrected in §5.1: host-coupled collected tests and stale full-suite advice; explicit plugin-before-collection fresh-root route or disclosed 19-node deselection. Separate C1 code gate. |
| 5 | m1 | Corrected in §4.1: human decision outside application; computed `summary.disposition` is not an adoption act or retain/reject/defer protocol. |
| 6 | m2 | Corrected in §5.2: b085 boundary, prior absence, all 1,194 files byte-equal, and uncaught `FileExistsError`. |
| 7 | m3, N3 | Corrected in §4.3 and §6: committed original witness/design locators; ZIP-only recovery entry points; execution invocation/manifest, FINAL streams and ledger explicitly runtime-only. |
| 8 | m4 | Corrected in §4.4: original NM contract gate and NR supported-contract commitment; future-build refusal distinguished from historical matching replay. |
| 9 | m5 | Corrected in §6.4 and option D: separately authorized/accounted export; archive-bound historical helpers, not loose maintained tests; existing/new host metadata disclosure decision. |
| 10 | m6 | Corrected in option B: helper removed from minimum, no test imports, no oracle outputs, build/invocation only, unchanged authority/request/exposure, separate verification approval. |

**All remaining notes:** N1's effective mandatory NM pin is confirmed in §4.4.
N2 is corrected by naming the preserved modified file exactly:
`tests/reassessment_profile/bounded_pytest_runner.py`. N3 is covered above.
The review's accurate objective, replay, seven-file bundle and bounded acceptance
observations are retained. Its recovery verdict is refined by the newly inspected
runtime stop and nine recoverable carriage members; this does not erase its
repository-only publication concern. No critical or new semantic defect is
asserted.

**Exact owner decisions needed next:**

1. Accept or reject this corrected reconciliation as the scope basis.
2. Select A alone (recommended), and confirm its audience: technical users/local
   evidence reviewers. This is a documentation delivery decision, not a new
   capability or acceptance exception.
3. If more is wanted, select B, C1, C2 and/or D explicitly and separately approve
   their changes, verification/execution and accounting. No option is selected by
   listing it here. In particular, fresh workflow authority remains an owner/
   authorized-attestor act, not a helper feature.
4. Before publication/export, decide which evidence and existing/new host metadata
   may be disclosed and whether a separately labelled presentation derivative is
   wanted. No remote state or permission is inferred.

No additional adversarial review, implementation or execution is undertaken.
The next gate is the owner's bounded scope decision.

## 9. Preservation and method receipt

Only this new report is added. Both frozen inputs, tracked changes, runtime
results and historical evidence are preserved. Baseline: HEAD as §1, empty index
diff, 2,428 untracked files, and the sole tracked modification named in §8.
Its complete tracked diff SHA-256 is
`fb31b6888f8b684b1053a9171a6c449e6dcd6622b5edd7643d365d40e833257e`.
Runtime ledger tip remains record 3595, SHA-256
`f56d8fea6ebbabe7a156799ed30dd696ad3e7f0387f1aec290a6603d92512204`.

Checks used read-only Git/source inspection, raw hashing, JSON parsing and ZIP
reads in memory. This did not run an application, test campaign, recovery helper,
provisioning verifier or historical driver. No permission issuance, evidence
export, ledger mutation, dependency operation, ADR allocation, staging, commit,
remote operation or cleanup occurred. The accepted failed/noncompliant attempts,
withdrawn claims, unauthorized-probe disclosure and evidence corrections retain
their original status. Final acceptance remains the bounded historical owner
decision, not a new qualification conferred by this report.

## Appendix A. Every acceptance/completion commitment

The 40-hex source/execution revisions are distinguished in §§1 and 6; they are
Git identities, not SHA-256 file commitments. The following raw hashes were
recomputed over the listed retained files. No root hash was left without a locator.

| Raw SHA-256 | Locator | State; purpose | Bytes |
|---|---|---|---:|
| `07bb65962db717fd761e4aba2beec13d603621cdaea35021189e273bbec25ffc` | `R/indexes/3589-record.json` | R; Q | 473 |
| `12db9d01d1d9ac81b2389e3f6916fcce324b26f62305bec8d17086b1a6d9f7d0` | `T/slice5_storage_routing_v2.py` | U; E/Q | 8071 |
| `219e6f89f545ea5df09e6ff549658c64980de039ab918aea6ecd0cdd427d6255` | `D/2026-09-29-reassessment-slice5-targeted-verification-successor-v9.diff` | U; Q | 33901 |
| `24e8051f61c751e259a095d408dc8269ff615d9b6d5fb41516a71b5a9ea3d808` | `R/regressions/rel5-FINAL-full-release/run/storage-observations.json` | R; Q | 3895 |
| `2a15e8118d8212c5a54a7db918a85e8704b935a7b15acd4c8e614a94f2c3c93d` | `R/regressions/rel5-FINAL-full-release/run/collection.jsonl` | R; Q | 1566051 |
| `2ed7cdf000d26937e5b2ba6f36c18561c15c2642231be1e739a64ae0ea7fb918` | `R/outputs/m180-e-p1-point60/build.json` | R; Q | 27632 |
| `3a4d021f1f8d35e4ae53d5b06a9faabbdc8b17e7558fc071250889b6e3f0c289` | `W/nr-slice5-delivery-final/outputs/rel5final-3569-profile/build.json` | R; Q | 27632 |
| `41161b77f57862e06eda2c0148228759fc665b83ee1fe1807c0eee4d716f5df9` | `R/regressions/rel5-V2-boundary/continuation-stop.json` | R; Q | 6064 |
| `447fccef3a26fad37965bc6c28278bd446866238e3bd4bd984d1d66f0412d95d` | `D/2026-09-29-reassessment-slice5-approved-environment-continuation-result.md` | U; Q | 12789 |
| `488b8e96a92ab92be56e4cd6c55318ff0de4879cdb76515dbe6744d90f32dcf6` | `T/slice5_environment_identity_v1.py` | U; E/Q | 4507 |
| `536bbd792d0556dd0e65737c5e4d0fb0392f995e38377f643931ff81d3748f0a` | `D/2026-09-29-reassessment-slice5-release-repair-pytest-launcher-v4.py` | U; E/Q | 2211 |
| `6a945fb2726d75efc2380434c37c31f67570793144a0193aabbf9dab295a9430` | `D/2026-09-25-reassessment-slice5-fresh-m180-schedule.json` | U; Q | 54329 |
| `6bd19b4bda84da2469df4efbe4ffc816c104ba4cb99cec7851d18939a4bd70a4` | `R/regressions/rel5-FINAL-full-release/run/results.jsonl` | R; Q | 5123155 |
| `6d25dea1635567f4a6838b5252f25d448f1a4194657cb54ba30bbc705f8afafb` | `W/s7-release-Gvdefi/historical-w0/build.json` | R; Q | 6224 |
| `6f5c6af9ca273d956934b79de6f95f454e3810fc823a134bb4bca7f18f870f6d` | `D/2026-09-29-reassessment-slice5-targeted-verification-stage-v13.py` | U; E/Q | 29354 |
| `7bd8cb7906f82f16b18ca28a5356b815f365cbe97c760a222eca56818786126d` | `R/repairs/g-app-r2/tmp/test_accepted_s6_archive_recov0/recovered/build.json` | R; Q | 3871 |
| `7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817` | `A/requirements.lock` | C; A/E/Q | 191 |
| `7cca2236b585685c890c97726668b2ec2c1088e46d4650d626e43e9843958eb7` | `R/regressions/rel5-control-env-replacement-1-accounting/control-result.json` | R; Q | 1315 |
| `b0378b3094b6930379c2984bd196b14e226635c723cdb84cf88823f6c439cee8` | `R/regressions/rel5-FINAL-full-release/substitution.json` | R; Q | 710 |
| `ba9c6badf0ace3744bcd4c40eae972c929ab4964112f66d91dd54aba6c3757f0` | `D/2026-09-29-reassessment-slice5-targeted-verification-manifest-v9.json` | U; A/E/Q | 10184 |
| `bb46dad43992be630704459ef3ba0d2b404d58c0556b43eadf19ef7b52a06ef4` | `R/regressions/rel5-FINAL-full-release/corpus-final-after.json` | R; Q | 78281 |
| `bd7e94e1a883415b4c747ad3422de701388afa14637f1ef576fd7e2ff01b201e` | `R/indexes/3581-record.json` | R; Q | 3116 |
| `c1e280203f0db4bdc37055431ea5e0190ab3070b087e4c093036bc9b50e9bd09` | `D/2026-09-29-reassessment-slice5-targeted-verification-manifest-v8.json` | U; A/E/Q | 7462 |
| `c44101dc2b7abe9e3afba207383ac111e2fc266a6b5daa740cd3679e368f876e` | `R/indexes/3583-record.json` | R; Q | 459 |
| `d1ebb41d0c547dbe663dbc5455f3ef2b3f7fcbfebf5cb8069f46269b6af20980` | `R/repairs/g-app-r2/tmp/test_two_clean_roots_twelve_co0/run-0-1-0/result/build.json` | R; Q | 7394 |
| `da87127a571195b4129e6fefd393da39d57819667ecba4f1f8a37d5f1984bc34` | `B/provisioning/environment-manifest.json` | R; A/E/Q | 2255 |
| `f8845787925b1bd6769a51201cfab9bc675b9d07b2d559bb6aa836612b058acf` | `D/2026-09-29-reassessment-slice5-targeted-verification-successor-v8.diff` | U; Q | 47735 |

These six commitments are structured identities, not raw-file hashes. All are
runtime-only (R). Environment, wheel-set, lock-text and both build IDs were
recomputed by read-only canonical JSON hashing; the Git inventory commitment is
located in its historical records and is not relabelled as today's inventory.

| Structured SHA-256 | Locator / field and meaning | Purpose |
|---|---|---|
| `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a` | `B/provisioning/environment-manifest.json`: environment_identity_commitment; canonical JSON of manifest excluding that field | A/E/Q |
| `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1` | `B/provisioning/artifact-manifest.json`: artifact_set_commitment; canonical JSON of artifacts rows | E/Q |
| `aca75138681ef473898adf84559e155c6e1a2a7968f67071103e51dce161201e` | `B/provisioning/lock-specification.json`: original_lock_text_commitment; canonical JSON string of runtime_lock_text + test_lock_text | E/Q |
| `08fbcdd783743a64d306d07f45195cc8db8b3570fceaaf04a73788be35792d50` | `R/outputs/m180-e-p1-point60/build.json`: id; canonical NR build body excluding schema/profile/id/revision/predecessor | E/Q |
| `67a1f1265ffc04f0a89b5419f612b2bea3e613072ba76a04579ee32ae9ce9b60` | `W/nr-slice5-delivery-final/outputs/rel5final-3569-profile/build.json`: id; same build-body rule | E/Q |
| `c0206a35f106300ade6c159681e7b509b99e1ea26474b6ff56bb677f97ab03dd` | `R/indexes/3591-record.json; R/indexes/3568-record.json`: git_metadata_sha256 / after_listing_sha256; retained Git metadata inventory, not current Git tree hash | Q |

## Appendix B. Expanded local file inventory

Appendix A and this table together cover 128 inspected files: 45 tracked paths,
54 untracked paths and 29 runtime paths, totaling 9,223,933 logical bytes.
This is the indexed selection of control files/evidence, **not the size of the full
runtime dependency closure or an export reservation**. Large source/package,
installed-environment and runtime bundle populations are separately indexed in
§6.2. A future D export must size its selected closure and ledger overhead before
writing; summing this table cannot fund it.

Rows already in Appendix A are not duplicated below. `v9` marks membership in the
frozen v9 artifact map (46 total across both tables; all hashes matched).
The other rows are reviewer additions or source-inspected dependencies.
C* means committed path with a pre-existing working modification; its hash is
only a preservation identity for today's bytes, never a relabelled historical
execution commitment. Other C rows name the retained committed working files.
Archive duplicates of U rows are given in Appendix C.

| Locator | State; purpose | Bytes | SHA-256 | v9 |
|---|---|---:|---|---|
| `B/provisioning/artifact-manifest.json` | R; A/E/Q | 3565 | `17eb5aa4013994732909e1dae9b16263e2c4d9261d4f1b9d890cf3935aed17ad` | — |
| `B/provisioning/lock-specification.json` | R; A/E/Q | 888 | `33ed2b74c4599432e0585642f3e52c44c412af521222df36c3d30e180f57a2b8` | — |
| `B/provisioning/persistence-probe-evidence.json` | R; A/E/Q | 504 | `85c747ad3b9bb5787e1ed979c095e8a2bfe783df6651509b03dedecb1ccc9e0f` | — |
| `B/provisioning/requirements-hashed.txt` | R; A/E/Q | 981 | `6bcc7bd80022ce38d984ada0b4e4d4986272befea760ae895c76a8c6f3937fcf` | — |
| `B/provisioning/verify-provisioning.py` | R; A/E/Q | 4912 | `697d90efcb62ab8124e01cf6680164857a63376f3849ee802f3610014359ad92` | — |
| `B/provisioning/workspace-persistence-probe.json` | R; A/E/Q | 217 | `f369e1b85d873829f7e789ebe8ca778691fadfc088c12f14ae1764bf89893364` | — |
| `R/indexes/3463-record.json` | R; Q | 2246 | `a12ab4d42f38c043f09efdd9b40c05f70c72eaebc8cf5a286e47672a492a8b1c` | yes |
| `R/indexes/3519-record.json` | R; Q | 771 | `f602ee513f0ecb535ab21eb66d3cee85a56c19545e9e9c1a9769b3c0a798b078` | — |
| `R/indexes/3520-record.json` | R; Q | 2405 | `4cc022b9aa47241114022e26c35dc0b001e67e23b2be3cc10a3d991a27957e50` | yes |
| `R/indexes/3568-record.json` | R; Q | 5027 | `b019eb5f821e94e5dc7120fa9656fb7919982eca2b0421846166f1fa101ad727` | — |
| `R/indexes/3591-record.json` | R; Q | 567416 | `def277a2a3f999588c997bdb175eb7abe19f9739c42aa839c82adfdf7ecb2438` | — |
| `R/indexes/3595-record.json` | R; Q | 700 | `f56d8fea6ebbabe7a156799ed30dd696ad3e7f0387f1aec290a6603d92512204` | — |
| `R/outputs/m180-e-p8-before/manifest.json` | R; Q | 970 | `b0487f75feb727e254cf825181cedab6f66a9cd9e7650ffcfbbec261c5662748` | — |
| `A/__main__.py` | C; E/Q | 144 | `8a9577bd418fc214881592dd7290d3dd64c3bc75d9c9c3f47c36c2ff67f956b5` | — |
| `A/cli.py` | C; E/Q | 15633 | `67279635b0e5786be4d6fdab44af2e274c7331993c8ebafc5410039885c5167c` | — |
| `A/errors.py` | C; E/Q | 947 | `7829278c93e60c0ee3321e3bc124926cc8dddb2ee05c07641f52a95373dbda72` | — |
| `A/measurement_cli.py` | C; E/Q | 3759 | `c46d9a46b675f91c3dd2c91ee1141535d7ee5ef5aab50ae09a7ee73e89227c59` | — |
| `A/measurement_contracts.py` | C; E/Q | 19701 | `146b529a6f9524a80407b431f7eff8ec89bd93c39de23652bb066cfd913ed587` | — |
| `A/measurement_wire.py` | C; E/Q | 32861 | `9e50628d3362efe8f7be230312a1d62c3a1a148b06a8f85cd9025758c6098f47` | — |
| `A/reassessment_cli.py` | C; E/Q | 3836 | `4fee03f8002b2eeff543b5ddc4906537765e2eddcff27861c0d0ca44e6bcfe07` | — |
| `D/2026-09-23-reassessment-carriage-evidence/MANIFEST.json` | U; E/Q | 2003 | `9904a5a12662984ce8cc1eb978d1188fa800d0accde5f044a55f9134c21bccca` | — |
| `D/2026-09-23-reassessment-carriage-evidence/alternatives.json` | U; E/Q | 459 | `05ae7e1183b18fcdb2e34a6d97736e71dc0c4e7204f5b953874ce3bbb73e5ac0` | — |
| `D/2026-09-23-reassessment-carriage-evidence/expected-files.json` | U; E/Q | 792 | `c5693d82724bd540cafc4319ed278610ec8f7089f2f046752f51b1e2627b3f4d` | — |
| `D/2026-09-23-reassessment-carriage-evidence/measurements.json` | U; E/Q | 2494 | `736f8dc7547a76d9f9839513c77545174e6df32f1b83bf1b808fdb0915e2269b` | — |
| `D/2026-09-23-reassessment-carriage-evidence/reconstruct.py` | U; E/Q | 11127 | `e5418505f94e10bc60db2a39fd035708d5dee861e97e53a2dbc222f92558e7e9` | — |
| `D/2026-09-23-reassessment-carriage-evidence/recovery-receipt.json` | U; E/Q | 343 | `b81c88c1f06080a928b9ee909b1844aa4beefa1a17cc3b87f6a4fe33d6d2b701` | — |
| `D/2026-09-23-reassessment-carriage-evidence/recovery.zip` | U; E/Q | 475291 | `cd07349f8b639e57f92ad38e073a8953e54d6506e4695354595a405e8d05a674` | — |
| `D/2026-09-23-reassessment-carriage-evidence/standalone-recovery.json` | U; E/Q | 1682 | `e2b623b4a4080bbc151680b5af6dde95fe7d9034bd4f00d3d9c50b0426b20042` | — |
| `D/2026-09-23-reassessment-carriage-evidence/static-controls.json` | U; E/Q | 704 | `6f442832f57598f7c5bd4701b4dd17069c78f0e55a880cc16e3299e31e8e071a` | — |
| `D/2026-09-23-reassessment-carriage-evidence/witness.json` | U; E/Q | 219976 | `d91332ea6f277c9415125b5e4273e83986a2b2a936718801e0a2a161a0a1efb4` | — |
| `D/2026-09-23-reassessment-prior-bundle-carriage-amendment.md` | U; A/Q | 19619 | `d7136af5c4a086361e92be159d9aadc3c9d552d315dc2b2a3ecbf7df952a1676` | — |
| `D/2026-09-25-reassessment-independent-architecture-and-release-readiness-review.md` | U; Q | 20134 | `985e3724bdcbe45b92ae5d1b5520eb12337032c3ccf6354330307109215e6edc` | — |
| `D/2026-09-25-reassessment-slice5-campaign-budget-v3.py` | U; E/Q | 13321 | `959d9ef5ed3ea242287714f88d0e69b5d51722d517c9d781fc7e303367c2ed11` | yes |
| `D/2026-09-25-reassessment-slice5-campaign-pytest-launcher.py` | U; E/Q | 2036 | `52536931efedcbf7f7d8e672c74d5514a0e4ac8ba7f073d62802491bc9c7ebd8` | — |
| `D/2026-09-25-reassessment-slice5-campaign-stage-a.py` | U; E/Q | 14548 | `9dd828cda87188f170f7ce9881db87096253ab55da8aa71c2cc4b777df61e7d4` | — |
| `D/2026-09-25-reassessment-slice5-campaign-stage-b.py` | U; E/Q | 7260 | `27e9de92e602c36eb685872ddf2888a543e6251e46b7dacf0b63104b27b0c9a2` | — |
| `D/2026-09-25-reassessment-slice5-campaign-stage-b2.py` | U; E/Q | 3661 | `39a73e1b1babe4f2d4d15dd8f9969ac33f78c86e80635801b52baaa4c2f1ac73` | — |
| `D/2026-09-25-reassessment-slice5-campaign-stage-f.py` | U; E/Q | 7618 | `a2e8840d14c12c42710b3ae164521e054c8a2fb8b6a934ccef4d96116898b3de` | — |
| `D/2026-09-25-reassessment-slice5-campaign-stage-g.py` | U; E/Q | 24837 | `d5b874a49a3d1eba2f89c272d07a17a0f46c6bf831ea8730769f1e25aac6cead` | — |
| `D/2026-09-25-reassessment-slice5-campaign-stage-m.py` | U; E/Q | 24198 | `f839a8356820d79de7c931c3fb0e41d5a00525cb1acd69e088e376cc57d3796d` | — |
| `D/2026-09-25-reassessment-slice5-consolidated-release-plan-owner-approval.md` | U; A/Q | 5475 | `318529d0a58620f1cc8219c8f3309c836dc7cf2a066503325e4b2d6b38544f6a` | — |
| `D/2026-09-25-reassessment-slice5-consolidated-release-plan.md` | U; A/Q | 17447 | `51519fefad1b386c88124e3e95dc54d15e9942c2e4ff3fec5efafe60afd3f9b4` | — |
| `D/2026-09-26-reassessment-slice5-campaign-execution-report.md` | U; Q | 13038 | `62c11404761784b67f1e0c66aa5969a0934de270ddc722e6142fa7b43a158ec6` | — |
| `D/2026-09-29-reassessment-slice5-campaign-report-correction.md` | U; Q | 4335 | `b1ddb97813508aebfd512e282d44bfdeb75a5428054e587dd1b25330175c0e0d` | — |
| `D/2026-09-29-reassessment-slice5-client-fetch-comparison-stage-v7.py` | U; E/Q | 13599 | `c537cc14f6725135268982adb1ff6b6c49c7323567be0d9b03ba00893a6494ed` | yes |
| `D/2026-09-29-reassessment-slice5-client-fetch-verification-stage-v8.py` | U; E/Q | 13135 | `21fee67b851ed2412c2a4383abf10cc37c2b1bef764d91517f17fc62330a7388` | yes |
| `D/2026-09-29-reassessment-slice5-expected-optional-extra-skips.json` | U; Q | 17222 | `a6d898b11e44376ceb9b5aea5b7583f4a73242f154e3daf6691536b248e3a242` | yes |
| `D/2026-09-29-reassessment-slice5-full-suite-retry-result.md` | U; Q | 7225 | `32f9594b1aab2594f00c69e833f8c06bf4d6f9c351795a647deb097b81b5e2bd` | yes |
| `D/2026-09-29-reassessment-slice5-release-repair-pytest-launcher-v2.py` | U; E/Q | 2836 | `84ff4a5af2614b14ead214842890b14865a380d9397b27589d8ec8a2ce38621d` | — |
| `D/2026-09-29-reassessment-slice5-release-repair-pytest-launcher-v3.py` | U; E/Q | 3052 | `34a9d1fc41fd1b3d3af0bb80fa21601f5ad7579b76a02d507e37741e7ea5b3fe` | yes |
| `D/2026-09-29-reassessment-slice5-release-repairs-stage-v2.py` | U; E/Q | 32966 | `51c7efcc4f7b73003e26c25b94c0473f6e8b6351043bbef30cda289cebc47359` | yes |
| `D/2026-09-29-reassessment-slice5-resume-stage-v6.py` | U; E/Q | 10198 | `730f9bad18edf4b685d96605556fb91aeda57de4b7c63319387a08d53546e2bc` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-correction-audit-v8.md` | U; Q | 6654 | `c27c15587560918603ab2f043911827dca992ea0de1fd988560e2045408bfc8c` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-environment-audit-v9.md` | U; Q | 3738 | `44b9b110f046a2bd5459988ce276d9e5c662f56281c8c6ba36258f0ccd77a323` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-manifest-v6.json` | U; A/E/Q | 4519 | `be2bbfc42b706de8a65d14bc8dba2d23b899f1013786a414b7875c8579faaf49` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-manifest-v7.json` | U; A/E/Q | 4891 | `21492aeed81fda360c8e76d369c7f6b3a8ed4b5f6364576a17c9a423bb5721dd` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-replacement-preflight.md` | U; Q | 4263 | `797d8aa7fc91aa4e4d3f8866c5f5d08d92edbc9998bb5c32db64f68c91ae0d0a` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-replacement-stop.md` | U; Q | 3662 | `d1c12f01451a68dfa53e6094ace2ba84880065d9df658600e2a18a426c171e4c` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-stage-v10.py` | U; E/Q | 15197 | `a5148ee13f429b16003027e34e1fc7bfb5b6ba3b58634cc8912a4a0dff1cc166` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-stage-v11.py` | U; E/Q | 20932 | `00b931220df350a7e7aaba975adba49184a0a67f56fa3183e7eacf17300d9303` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-stage-v12.py` | U; E/Q | 21523 | `f8bb09e663bb6392037435ae4e17583c6c9e7454e1c5f1b6d23bc1eda2973e3c` | yes |
| `D/2026-09-29-reassessment-slice5-targeted-verification-stage-v9.py` | U; E/Q | 16376 | `6701999f7bcd5ef4ac50f05a64328d5cdac14604506ab3a24acf859bb2ab6a12` | yes |
| `D/2026-09-30-reassessment-slice5-and-final-owner-acceptance.md` | C; A/Q | 16848 | `a98286666e9de0e24db10e6c6dda5fd7719510442151ce3e9b76b03d4cee7a9c` | — |
| `tests/A/governed_fixtures.py` | C; E/Q | 4330 | `6404234a5455b07e52ddbe538df0b522a3639020a3c9a71ff5cb098f38de40dd` | — |
| `tests/A/test_governed_build.py` | C; E/Q | 5593 | `668fc3a0f2c45e358b1e2a6f2744c4ffcf6761caa7f187105cf28bcfd0aefea9` | — |
| `tests/A/test_governed_persistence.py` | C; E/Q | 10580 | `aebf22c6d5a5096b485e966ea039d2003c2cb875ea0851ee87d3c7ab4bc0e094` | — |
| `tests/A/test_s7_release.py` | C; E/Q | 9607 | `319beac5cbbccf42c862556e6b8a94c3d530ad580a39ca91a8d40239aea6bc35` | — |
| `tests/conftest.py` | C; E/Q | 787 | `83bb50ff8f4bb01dc39cab03c51cb16ae378e9a8456a24e7e3a2fd08e667520f` | yes |
| `tests/data_sources/test_ingestion_runner_pdf.py` | C; E/Q | 8463 | `f773daa382445a08f7da1802b828b95977cd33af8c4d31c5b1d201ee18613c22` | — |
| `tests/data_sources/test_ingestion_runner_step.py` | C; E/Q | 9662 | `4bcd2e4601ee4af4d0e95d5f1903b1757247d0e987f5aa1cfcde539d39fc6e91` | — |
| `tests/data_sources/test_pdf_detection_availability.py` | C; E/Q | 3652 | `7fe57009424022358ffe6c6dadfe7c9c1c5d3274c006f35c58d92fc6cebf75ec` | — |
| `tests/data_sources/test_pdf_extractor.py` | C; E/Q | 30778 | `2b3738e1b211ef2d6301bdc307a89b68377c2ae2d5897d7d0782a23cc8a9c634` | — |
| `tests/data_sources/test_step_extractor.py` | C; E/Q | 11208 | `3e5a93ee7d19098a8144882234acb8aa97bbf2ca4b6eb6f93d1de1be97158396` | — |
| `tests/data_sources/test_worker_harness.py` | C; E/Q | 6148 | `a89df1ad9523466a57b99c2e213a79fbe8d4fac360e91b9c29d8583a516f74aa` | — |
| `tests/model_kernel/test_fl001_slice_d_reproduction.py` | C; E/Q | 8803 | `2343c7a0c1ccfa11283dd6dd4694d47d1649c798749f27a6fb8dbb4f7c616a82` | — |
| `T/bounded_pytest_runner.py` | C*; E/Q | 6065 | `97999fadaeb87c9107f9d927a622a207a3bded71a8e4f08101846c53f180de78` | — |
| `T/bounded_pytest_runner_v2.py` | C; E/Q | 7952 | `040c3211f87ed1c6d4652c91285fb8aa496d8bdcd259193da945df5eea421d10` | yes |
| `T/bounded_pytest_runner_v3.py` | C; E/Q | 20455 | `a39d30410147ecba7f96100dd9071a1f31e97c016e2973824f548e91328e4d47` | yes |
| `T/bounded_pytest_runner_v4.py` | C; E/Q | 26494 | `727dd1a4ce0d2a287b92cba22b9430fa15a82ede821dae92018858303c22f137` | yes |
| `T/delivery_budget.py` | C; E/Q | 4112 | `4cf93dc421b078e916ef44181c749a1a0634d14facd2d098edc2dd20b0186650` | yes |
| `T/qualification.py` | C; E/Q | 13277 | `72149f8e134da0e33a38095d01fad146236744ec1f73d2afd5ee86510bf8a0fb` | — |
| `T/qualification_remaining.py` | C; E/Q | 6808 | `4cc3153522c0763e84277b53c0dd401d238ae7f43f8766b600850dd0883d3139` | — |
| `T/slice5_delivery_root_adapter.py` | C; E/Q | 3950 | `fe041ebc58d7e9055c43ac943c3607c9f1fa89a5640f5ff4f57c1b171432de24` | yes |
| `T/slice5_external_controller_v3.py` | C; E/Q | 7225 | `e6dc1df121942d31c4682be2d6a2c1cfad6472c21912ab662b41d4d550815069` | yes |
| `T/slice5_external_controller_v4.py` | C; E/Q | 8226 | `898be00e44bef029227c69e4793e7b1da15a3aecdc5e4b75aa1a9139d7d9739b` | yes |
| `T/slice5_external_controller_v5.py` | U; E/Q | 9637 | `09d7398542f04a39bd78020817b2b275f95345d491aa6be6f3ecb857fb4d8bb7` | yes |
| `T/slice5_f2_session_ballast_check.py` | C; E/Q | 1618 | `1d717cb2e57e7443865f01d85c77475742aef5f7952aaa73fb565c9f039059fb` | yes |
| `T/slice5_g_app_root_adapter.py` | C; E/Q | 3453 | `b0fd35b45c8323e4915d1fa249cc0d4afe704f7b37e24274b99c6eadabfc9bb6` | — |
| `T/slice5_node_address_space_adapter.py` | C; E/Q | 4226 | `5c33142f869b3f470b77eb558412af5d91967813c042b0470d8bc7552692c5e8` | yes |
| `T/slice5_pinned_fetch_adapter.py` | C; E/Q | 4901 | `8e82f251c929a50a8072e8db7d7149dc952903448b9f4c449a4198ff8fa5a365` | yes |
| `T/slice5_pinned_fetch_adapter_v2.py` | C; E/Q | 5844 | `00e935e858d598e6e2301f597b46a5375652bf9f550b4e4153fc90a24a045285` | yes |
| `T/slice5_pinned_fetch_adapter_v3.py` | C; E/Q | 10110 | `cd741d2a5a8771dc59074e820c5776878fd3bfad50c7051d78ff0feee02dfe9b` | yes |
| `T/slice5_reporter_v3_checks.py` | C; E/Q | 5720 | `c74403168ef8eb6c26cd7f87da04ea407132e242226d860a3d59c8469e82b475` | yes |
| `T/slice5_reporter_v4_checks.py` | C; E/Q | 5857 | `457a123522410b7acc8dac819b1f2fec3f9593d65b18637faf51bb9cf2a90a09` | yes |
| `T/slice5_storage_routing_v1.py` | U; E/Q | 7648 | `8038fc53b74f2033091bc6e12d50b96cb04f85a4ff5f45983323e760dc688617` | yes |
| `T/test_bounded_pytest_runner.py` | C; E/Q | 1109 | `434b3dcf674d1a56a9bfd2261ea700288b04d6acfecad84897662bf41abe585c` | — |
| `T/test_capture.py` | C; E/Q | 25641 | `4f42e1b09de55204a2128ec4ca71b71eef734622ed355be5b46f088fe778b4af` | — |
| `T/test_delivery.py` | C; E/Q | 12223 | `8938b4e815f0ee16dff4ec686ac90c41d5db779dcdc2046b7aa16a2fd5391b50` | yes |
| `tests/structural_evidence/test_reconcile.py` | C; E/Q | 42627 | `27f6959c0f0b4be795f63337b268041344a4e5869809d272e8f8aa8f2bac5780` | — |
| `tests/structural_evidence/test_step_claims.py` | C; E/Q | 10625 | `8bd92eede5d03468e37a159ca7caad2de68f0a279c1e5f530b2487baceac3c4f` | — |
| `tests/transition_assessment/test_preflight.py` | C; E/Q | 10541 | `053e30b3da7e64aa4a26092be5c9ec4e5c1761744413ff30aa627f3d6e9582e4` | — |

## Appendix C. Exact committed archive alternatives

Every row below was hash-matched by reading ZIP bytes in memory. All ten loose
carriage files are untracked. Nine have committed archive copies; the local
receipt does not. Purpose is E/Q unless specified. A Z locator removes the need
for a loose copy for that recovery purpose; it does not make a new execution.

| Loose file under D/2026-09-23-reassessment-carriage-evidence/ | Committed locator | SHA-256 |
|---|---|---|
| `alternatives.json` | `P::authority/recovery.zip::alternatives.json` | `05ae7e1183b18fcdb2e34a6d97736e71dc0c4e7204f5b953874ce3bbb73e5ac0` |
| `expected-files.json` | `P::authority/expected-files.json`; `P::authority/recovery.zip::expected-files.json` | `c5693d82724bd540cafc4319ed278610ec8f7089f2f046752f51b1e2627b3f4d` |
| `MANIFEST.json` | `P::authority/recovery.zip::MANIFEST.json` | `9904a5a12662984ce8cc1eb978d1188fa800d0accde5f044a55f9134c21bccca` |
| `measurements.json` | `P::authority/recovery.zip::measurements.json` | `736f8dc7547a76d9f9839513c77545174e6df32f1b83bf1b808fdb0915e2269b` |
| `reconstruct.py` | `P::authority/reconstruct.py`; `P::authority/recovery.zip::reconstruct.py` | `e5418505f94e10bc60db2a39fd035708d5dee861e97e53a2dbc222f92558e7e9` |
| `recovery-receipt.json` | No matching member in the eleven committed reassessment ZIPs or their nested ZIPs; U only | `b81c88c1f06080a928b9ee909b1844aa4beefa1a17cc3b87f6a4fe33d6d2b701` |
| `recovery.zip` | `P::authority/recovery.zip` | `cd07349f8b639e57f92ad38e073a8953e54d6506e4695354595a405e8d05a674` |
| `standalone-recovery.json` | `P::authority/recovery.zip::standalone-recovery.json` | `e2b623b4a4080bbc151680b5af6dde95fe7d9034bd4f00d3d9c50b0426b20042` |
| `static-controls.json` | `P::authority/recovery.zip::static-controls.json` | `6f442832f57598f7c5bd4701b4dd17069c78f0e55a880cc16e3299e31e8e071a` |
| `witness.json` | `P::authority/recovery.zip::witness.json`; `P::authority/witness.json`; `P::carriage-controls/shared_valid.json` | `d91332ea6f277c9415125b5e4273e83986a2b2a936718801e0a2a161a0a1efb4` |

The untracked amendment is additionally recoverable at
`P::authority/2026-09-23-reassessment-prior-bundle-carriage-amendment.md`
(A), SHA-256 `d7136af5c4a086361e92be159d9aadc3c9d552d315dc2b2a3ecbf7df952a1676`.
The full names of the other governing design/review members are:

- `P::authority/2026-09-23-measurement-result-reassessment-lead-proposal.md`
- `P::authority/2026-09-23-measurement-result-reassessment-corrected-candidate.md`
- `P::authority/2026-09-23-measurement-result-reassessment-focused-review.md`
- `P::authority/2026-09-23-measurement-result-reassessment-independent-adversarial-review.md`
- `P::authority/2026-09-23-measurement-result-reassessment-preparation-discrepancy.md`

The environment-stop report has no matching archived member in that search;
its verified runtime locator and digest are in §6.3 and Appendix A.

## Appendix D. Archive and environment leaf indexes

These are additional dependency containers, outside Appendix B's 128-file subtotal.
All eleven ZIPs are committed (C), and were searched through nested ZIPs for the
stop report and carriage files. Their raw hashes were recomputed. Package/design
members are A/E/Q; qualification archives, including failed-suite evidence, are Q.

| Committed locator | Bytes | SHA-256 |
|---|---:|---|
| `D/2026-09-23-reassessment-preparation/package.zip` | 33618258 | `454736288217a5c66e8cf6875069aba3a60dee04005c5644d95135adbc8110fb` |
| `D/2026-09-23-reassessment-slice1-evidence.zip` | 733472 | `728867a684e5292ab5d891197551b7431338c767a99ae75a0d3766aa0519e531` |
| `D/2026-09-23-reassessment-slice2-evidence.zip` | 667396 | `29f857dbcc03d99a0b002fffec13c509a1eebc56f406745cb3ee6ffa36a79993` |
| `D/2026-09-23-reassessment-slice3-evidence.zip` | 1063061 | `768dbf9e913458055c8a278903a0eed81dbf3e88dc373fb45fd2f41f7c78c7a6` |
| `D/2026-09-23-reassessment-slice4-evidence.zip` | 1825025 | `c078f207b122e520119baffd1594daf09c08e0a87a6697b9a212a651e75804dd` |
| `D/2026-09-23-reassessment-slice4-retention-evidence.zip` | 298472 | `ee2982a7fae7bc4e4fe379f1d2f94dc0776be532cacf6d3169bf87f15c25a1a8` |
| `D/2026-09-24-reassessment-slice5-build-carriage-decision/decision-package.zip` | 1170742 | `ca49082eb39973ca8b93d0036ec6bfe22ca7786a4c97980611b8b5c3d8293111` |
| `D/2026-09-24-reassessment-slice5-build-carriage-decision/evidence/failed-suite-evidence.zip` | 983906 | `ce7a710bd6de4a5a06eb0c24d49a7ace74b2fbbd7320032d55772dade2bd3d7e` |
| `D/2026-09-24-reassessment-slice5-core-correction-evidence.zip` | 43575847 | `646cf92d296d87ba1f661f7c295aee0f27eeedca6f86e0982d2659c7bcf7c7a4` |
| `D/2026-09-24-reassessment-slice5-resumed-evidence.zip` | 5252640 | `2a45ea044ed99c7fa127daab581f6045721e1dd977a9071579f041445d2ac913` |
| `D/2026-09-24-reassessment-slice5-retry19-evidence.zip` | 1397026 | `c1fc61dd08b247b01eb4eae2e92139dc20389dc9633a32d83abd87e6be220c11` |

The ten wheel leaves below are runtime-only E prerequisites under
`B/dependency-artifacts/`; bytes matched the recorded artifact manifest. The
manifest and installed-tree commitments are separate dependencies (§6.2).

| Wheel filename | Bytes | SHA-256 |
|---|---:|---|
| `annotated_types-0.8.0-py3-none-any.whl` | 13427 | `f072f4d804ea359e4eaf198b1af7a8b0943881a87f31bb764f8bf219bb9419e0` |
| `iniconfig-2.3.0-py3-none-any.whl` | 7484 | `f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12` |
| `packaging-26.3-py3-none-any.whl` | 129956 | `d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c` |
| `pluggy-1.6.0-py3-none-any.whl` | 20538 | `e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746` |
| `pydantic-2.13.4-py3-none-any.whl` | 472262 | `45a282cde31d808236fd7ea9d919b128653c8b38b393d1c4ab335c62924d9aba` |
| `pydantic_core-2.46.4-cp313-cp313-manylinux_2_17_x86_64.manylinux2014_x86_64.whl` | 2094467 | `9551187363ffc0de2a00b2e47c25aeaeb1020b69b668762966df15fc5659dd5a` |
| `pygments-2.20.0-py3-none-any.whl` | 1231151 | `81a9e26dd42fd28a23a2d169d86d7ac03b46e2f8b59ed4698fb4785f946d0176` |
| `pytest-9.1.1-py3-none-any.whl` | 386536 | `37a86b45efb9a47a61a36449063e8e18d0cab3161329fc099eb21783169c4f0c` |
| `typing_extensions-4.16.0-py3-none-any.whl` | 45571 | `481caa481374e813c1b176ada14e97f1f67a4539ce9cfeb3f350d78d6370c2e8` |
| `typing_inspection-0.4.2-py3-none-any.whl` | 14611 | `4ed1cacbdc298c220f1bd249ed5287caa16f34d44ef4e9c3d0cbad5b521545e7` |

`B/environments/cp313-bdw001/pyvenv.cfg` is runtime-only, raw SHA-256
`e957ced4bc47ecba78a9d904e72d22c2e81307a1867267923afe6d1dc1a20600`.
It records the base executable `/home/mafasa/miniconda3/bin/python3.13` and disabled
system-site packages. That binary, the venv's installed distribution files
(indexed by their `.dist-info/RECORD` and retained installed-tree commitments),
its bootstrap tooling and the compatible OS remain executable-reproduction
prerequisites. No verifier was executed and no environment was constructed here.

For precise FINAL navigation, the spec is
`R/regressions/rel5-FINAL-full-release/run/spec.json`; the same `run/` contains
`env/`, `collection.jsonl`, `results.jsonl`, `storage-observations.json`,
`routing.jsonl` and `detail-v4.json`. Sibling `fetch-evidence/`, `node-as-evidence/`,
`substitution.json` and `corpus-final-after.json` complete those observation
families. Ledger registration/baseline records and controller observations name
the external destinations. These retained execution files are Q, not optional
history when claiming complete recovery of FINAL. This index does not replace
their manifest commitments or grant permission to replay them.

END OF CORRECTED RECONCILIATION
