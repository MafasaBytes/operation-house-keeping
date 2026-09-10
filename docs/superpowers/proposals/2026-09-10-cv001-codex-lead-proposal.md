# CV-001 — Commissioning Verification Workflow

Codex lead architecture proposal — 2026-09-10. Corrected under the
[owner deferral decision](../reports/2026-09-10-cv001-deferral-owner-decision.md);
retained design guidance, not implementation approval.

## 1. Recommendation and necessity decision

**Corrected architectural disposition: CV-001 backend additions are cancelled;
application delivery is deferred pending concrete application requirements.**
This replaces unconditional cancellation, not the public-API sufficiency finding.

1. No backend CV-001 implementation is justified.
2. No kernel, evidence, evaluation, facade, CLI, HTTP, ledger, fixture, or
   durable-record addition is authorized.
3. The commissioning application boundary is deferred until a concrete consumer
   supplies ingress and invocation mode; authentication and authorization;
   commissioning-policy authority; policy schema/version and retention;
   decision-result retention; application/user identity; confidentiality
   requirements; capacity and latency requirements; error presentation;
   deployment and resource ownership; and scope-completeness expectations.
4. The proposal remains guidance for that future application design.
5. Disposable integration worlds are sufficient; no authoritative FMA/FCD append
   is justified.
6. ADR-0023 remains absent, unallocated, and unreserved.

Named consumer: the commissioning/operations verification workflow.

The exact supported question remains:

> For this exact logical flow, participant port, context, governing criterion, and nominated measured-actual sample at an explicit receipt cutoff: is the evidence usable under the caller's explicit policy, which criterion governs the sample, and is that criterion satisfied?

The request also needs the exact variable, orientation, model membership,
candidate/occurrence, evidence scope and independent commitments described below.
Existing public APIs are sufficient for correct in-process composition from
authoritative layers; that answer is not a new engineering fact. No missing
backend integrity property was demonstrated. No stable application entry point
currently exposes the complete answer. The accepted CS protocol is guidance,
not an implemented policy evaluator or workflow operation. Application delivery
is a real unresolved boundary, not evidence for a generic backend wrapper.

This is not a claim that the six-result FC witness is a deployed application,
a complete policy archive, or an outer self-validating workflow result. It is a
constructive proof of the public join. CS already specifies the additional
caller-owned policy and commitments. A stable presentation, fewer calls or a
new aggregate cannot be counted as a new integrity boundary without a concrete
substitution/omission/reconstruction failure in that existing composition.

No `backend.commissioning_verification`, kernel addition, durable identity,
store, ledger, workflow record, authoritative demonstration append or ADR is
justified. The two separately acquired coherent examples in section 10 confirm
that the usable/satisfied twin also needs no lower repair. The original
satisfied-A twin was CN-only; the separately acquired W40 full-path satisfied-A
witness closes test coverage but adds no new architectural or user-facing
capability. Any later application
implementation requires its own explicit owner authorization and actual consumer
boundary; this proposal reserves neither a package nor ADR-0023.

## 2. Verified baseline and protected hashes

The following checkpoints were verified before writing this proposal:

| Checkpoint | Live value |
| --- | --- |
| Branch; initial worktree | `main`; clean, including no untracked files |
| HEAD = origin/main | `1b9b31dc56be7e7d4da120cac0dc1c9ba31f8675` |
| Latest commit | `docs: close DI-001 as application composition` |
| DI / CS / FC | DI closed as bounded application composition; CS closed as commissioning application policy; FC complete and owner accepted |
| Authoritative model | 36 records; `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| FMA/FMW; FCD/FCW | `0/0`; `0/0` |
| Model-kernel exports | 236 unique ordered names; digest below |
| ADRs | ADR-0001 through ADR-0022, 22 unique contiguous accepted files |
| ADR-0023 | Absent, unallocated and unreserved |
| Last complete verification accounting | 4,074 passing tests, historical working/all-extras accounting in the FC final verification report; not a new full-suite run |

The short FC acceptance links to the final verification report containing the
4,074 accounting. An initial assertion looked for the count in the short record;
the corrected source lookup verified the accounting in its linked report. This
was a verification-script source-location error, not a baseline discrepancy.

Full hashes were recomputed, not completed from abbreviated receipts:

| Protected document or public surface | SHA-256 |
| --- | --- |
| [DI owner decision](../reports/2026-09-10-di001-application-composition-owner-decision.md) | `ca5413a558ec5512c34845715fc1c63a8b403f31f0ccf5e505c8e2eb081bfaa0` |
| [Accepted reconciliation](../reports/2026-09-10-post-fc001-architecture-and-adr-reconciliation-report.md) | `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5` |
| [CS owner decision](../reports/2026-09-10-cs001-application-policy-owner-decision.md) | `8557f2252c226b43dabc17ae4ffc5b8a529ac3d26999a456495e6b21c2ad33e3` |
| [CS correction report](../reports/2026-09-10-cs001-proposal-correction-report.md) | `b28c775071c0ef4aaa4af9a4593f8c31d76b756d811a3ce4ab40b3377e8517e5` |
| [CS audit](../reports/2026-09-10-cs001-codex-lead-proposal-challenger-audit.md) | `ebbe452695019d6f83a3a775149c8370125110c58461380f38a39e1092f37859` |
| [Corrected CS protocol](2026-09-10-cs001-codex-lead-proposal.md) | `ab816af9a96aa0578b29cd8209e3e0f1530ac8a02dac455a5538b58d460372c1` |
| [FC acceptance](../reports/2026-09-09-fc001-final-owner-acceptance.md) | `1436b12aff7ad6b387a58bba0ea7d87386fffd14c151d5ad76b06384a7529ca8` |
| [FC final verification](../reports/2026-09-09-fc001-slice-b-final-verification-report.md) | `eb67c0830ac54c3caac9a8763afd0e84484edc8f7f900fd6391f137d5a9eec71` |
| Ordered compact-JSON model-kernel export list | `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |

Protected tree inventories use sorted repository-relative pathname → file SHA-256,
compact sorted-key JSON plus one newline. All were independently recomputed:

| Protected tree | Files | Inventory SHA-256 |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| `var/raw_store` (ignored) | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

The accepted FC-only witness reproduced at 14,677 bytes,
`a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca`.
The integrated witness reproduced at 174,490 bytes,
`1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e`.
Only disposable temporary producer material was used; authoritative fixtures,
ledgers, membership and generated artifacts were not edited. No checkpoint differs.

## 3. What the accepted integrated witness proves, and what it does not

The live [FC design's direct join](../specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md)
and final verification sections 9–10 were inspected alongside the actual producer
and preservation checker available in the workspace. The temporary producer
`/tmp/fc001_consumer_proof.py` has SHA-256
`b5a93888b468ede89da6ae9f9c72655e07de994f732fcb320e31ad1fd08ae18c`.
It is an inspected reproducibility aid, not a repository API, production entry
point or dependency that a future application may require to remain in `/tmp`.

Its 19-record disposable model and source/binding/interpretation worlds use:

- Flow `flo_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, participant port
  `prt_11111111111111111111111111111111`, variable
  `var_11111111111111111111111111111111`, full `lifecycle_view/as_designed`
  context, orientation `aligned`.
- Retained FMA `fma_cd234041b6e1a98b65a33c61b7b742c463a348fcb92f1de912e88de2555cb2cb`.
- Governing A VCN `vcn_70b5e146d682db6ca696a9165d0d4521c36ba4324b3d52f96c8a13bae13912cd`,
  inclusive upper bound 50; ungoverned B VCN
  `vcn_3caad214041adad24a48bac3f13767078022329de34e2f46161a745c11c0273e`, bound 80.
- Receipt cutoff `2026-08-07T21:00:00+00:00`; occurrence
  `79bcec2f4de12d6e67f657f2e1153637`, received at `20:00:06+00:00`, value `60.1`.
- Complete EA coverage, attached alignment, and reconstructed snapshot fingerprint
  `sha256:36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`.

FC reports applicable A; CN evaluates A as `violated` and B as `satisfied`.
Full CRG/VCN equality, exact candidate/occurrence/cutoff and independently expected
fingerprint defeat B substitution. Receipt age is exactly 3,594 seconds. Under
CS's illustrative inclusive 3,600-second policy with the exact complete two-hour
horizon, the application can use A's violation. Under an explicitly authorized
3,000-second policy, evidence is not usable because receipt age exceeded.

Three important limits of the proof are not new architecture gaps:

1. The six-result payload is `(FC, EA selection, alignment, CN A, CN B, CN A twin)`;
   it is a deterministic comparison witness, not a canonical carry-once workflow
   envelope. B is an adversarial control, not a second operating criterion.
2. The original producer passes `expected_snapshot_fingerprint=None` to alignment.
   The separate preservation/consumer checks rederive alignment with an independent
   expected fingerprint and obtain `matched`. A self-reported embedded hash alone
   is not enough. The accepted FC and CS protocols already require the independent
   commitment; CV does not invent that protection.
3. The value-40 twin uses `craft_value` to insert a crafted temporal occurrence
   for CN evaluation. It proves satisfied A with unchanged FC; it is not a fresh
   full EA/alignment proof for 40. Reusing the earlier 60.1 selection/alignment
   with that twin would be wrong. This proposal separately exercised genuinely
   acquired 40 evidence through the existing source/projector/query stack and
   obtained complete, matched, attached alignment and satisfied A (section 10).

The original proof also uses test helpers and temporary stores to **produce**
lower results. Production and store-independent **validation** are different
phases. Its fixed support-row index is backed by the accepted ordering, but a
consumer should resolve typed `crg`/`vcn` rows and validate the outer FC result;
no private row, builder or temporary script is needed for the actual public join.

| Candidate missing property | Existing support / actual remaining work | Necessity finding |
| --- | --- | --- |
| Stable application request | FC/CS already enumerate exact target, cutoff, candidate, policy and independent commitments. No deployed consumer input format was placed in scope. | Application integration choice, not missing engineering authority. |
| Deterministic orchestration | Lower producers and pure validators exist; CS fixes gate order. Acquisition remains outside replay validation. | No need to copy lower algorithms or introduce a new selector. |
| Single reproducible result | Complete roots plus caller policy/context can be retained and replayed; six-result witness proves deterministic lower serialization. | A single object is packaging unless an actual consumer cannot enforce exact joins. |
| Policy retention/fingerprint | CS mandates full policy, version and authority retention; exact bytes can be hashed by the caller. | Digest adds content comparison convenience, not authority or a new durable fact. |
| Bounded carriage and consistent refusals | CS specifies carry-once roots, preflight and distinct outcomes; lower validators preserve exact reasons. | Application obligation already identified; no demonstrated missing public field. |
| Cross-result coherence | Full FC material and CN/VS/EA/alignment public comparisons supply all keys; independent commitments reject coherent replacement. | Existing public joins suffice. |
| User-consumable trace | Public lower paths/reasons and documented policy axes support a future display, but no stable application entry point exposes the complete answer. | Application delivery is deferred pending concrete requirements; lower composability is not delivered capability. |

## 4. Candidate architecture comparison and ownership

| Candidate | Honest capability / potential integrity contribution | Decision |
| --- | --- | --- |
| 1. Direct existing public APIs in application code | Produces and validates exact lower results, applies explicit CS policy, retains a bounded trace. | Sufficient; no new implementation recommended by this proposal. |
| 2. Documented application recipe, no runtime package | Makes the same obligations easier to review; this proposal supplies analysis without changing accepted contracts. | Retain guidance for deferred application design; no separate milestone or delivered workflow is implied. |
| 3. Pure `backend.commissioning_verification` | Could enforce aggregate coherence/disposition once, with downward imports. | No attack requiring a new aggregate was demonstrated; rejected for now. Replacing correct joins with a shared function is not automatically a new capability. |
| 4. Thin stable request/result contract over lower results | Could make a real application ingress fail closed and stabilize transport. | No actual ingress, caller compatibility problem or required artifact contract is demonstrated. A type alone does not authenticate caller expectations. |
| 5. CLI or deterministic report generator | Could give an operator a runnable named command and stable output. | Requires actual operator input, artifact-retention and delivery requirements; not supplied. Do not manufacture those requirements from the use-case name. |
| 6. HTTP/application API | Introduces transport, authorization, concurrency, request sizing and deployment concerns. | Unnecessary and premature; no network consumer or security contract in scope. |
| 7. New kernel records or queries | Would store workflow policy/disposition or duplicate already public FM/FC support. | No missing model fact; violates ownership if application policy becomes kernel truth. |
| 8. Authoritative FMA/FCD demonstration append | Would make one synthetic declared association/designation present in the demo. | Does not add join integrity or workflow capability; disposable integration suffices. No append. |

Owner remains the commissioning application above public lower contracts.
Its potential imports are public `model_kernel`, `constraint_evaluation`,
`evidence_assurance`, `evidence_alignment`, and public producer packages when
it explicitly acquires results. No lower package imports the application.
`model_kernel` continues to import only its accepted identity/stdlib/Pydantic
dependencies, never EA, temporal, binding, adapters or application policy.
EA does not gain model or commissioning semantics; CN does not gain use policy;
FM/FC do not evaluate observations. No sibling package is selected or reserved.

## 5. Exact fourteen-step public composition map

Notation: **F** is one complete `FlowOperatingCriterionResult`; **N** one exact-
lookup `ConstraintEvaluationResult`; **E** one `OperationalEvidenceSelectionResult`;
**L** is alignment derived from E and N's carried VS; **P** is the full explicit
caller policy; **X** the independent expected request context. These are names
for existing material, not proposed classes or durable IDs.

Self-validation means the stated public outer boundary, not an isolated row or
arbitrary `model_construct` instance. Older summary-only model/VM/VS facts need
comparison against F's complete material; source/binding ledgers absent from a
result are not authenticated by locally valid shape. No row is granted stronger
authority than its accepted lower contract.

| Step | Public API/result and exact join | Validation, carriage, refusal and I/O boundary |
| --- | --- | --- |
| 1. Model revision/material | `ModelQueryMaterial.revision`, `.records`, `.loaded()`; `ModelQueries`; X's exact `ModelRevision`/membership. | Public material revalidates canonical IDs, sorted exact membership and closure. F carries it once. Invalid closure refuses; no file/store read in `.loaded()`. An explicit `ModelStore.load/replay` is an optional producer operation, never validation. |
| 2. Logical flow/participant/context | F.`subject.flow_anchor_id`, `.variable_anchor_id`, `.participant_port_anchor_id`, `.context`, `.orientation`; complete FRG/PRG/FLD support via F.`material.record_at(index)`. Public `ModelQueries.flow`, `.port`, `.flow_declaration` can independently disclose these. | Validate exact typed context, identity and orientation against X, not display names. Registration/participant/owner closure is kernel-owned. Additional lookup results are derived, not retained duplicates; no physical-flow or port-observation claim. |
| 3. FM body and retained witness | F governing group's `witness_record_indices`, `matching_fm_current_indices`; exact FMA records; `.loaded().flow_measurement_effective_body_by_id`; optional `ModelQueries.flow_measurement_assertion` → `FlowMeasurementAssertionResult`. | Public outer FM/FC reconstruction owns activity, lineage health and body equivalence. Body is five subject fields plus six exact pins; evidence/authority/note are not body fields. A healthy current equal-body FMA may support a retained historical witness; keep the old witness, do not demand it itself be current or substitute its bytes. No separately archived FM root required. |
| 4. Governing applicability | `ModelQueries.flow_operating_criterion(flow, variable, port, context, orientation)` → F; `subject.conclusion`, `reasons`, `roots`, `fm_roots`, `body_groups`, `governing_body_group_index`. | Full F `.model_validate` rederives all groups/reasons from carried material. Only `applicable` authorizes a current governing check; absent/inactive/conflicted/disagreed/inapplicable are preserved. Do not pick a favorable group or create a `stale` FC enum. |
| 5. Exact CRG/VCN | Governing `support_rows` with `support_kind='crg'/'vcn'` → F material records; N.`constraint.registration`, `.declaration`, `.revision`. Also requery `ModelQueries.constraint_declaration` on F material. | Compare whole records including anchors, target, signature, predicate and ID; exact revision. B-for-A, same-anchor old VCN and forged summary refuse. One supplied CN A root only; B belongs solely to adversarial examples. |
| 6. Entity-owned variable | CRG.`variable_anchor_id`; FMA's exact VRG pin; VRG.`anchor.entity_anchor_id`; N.`semantic_compatibility.value_compatibility.state.variable_registration`, `.owner_registration`, `.requested_entity_registration` and request owner when specified. Producer `ModelStateQueries.variable_state`. | Compare full registrations against F's loaded maps. Entity ownership is not hierarchy/name matching. Binding attachment and divergence disclosures remain separate. Missing/unaligned model identity withholds the workflow; no foreign registration is silently promoted. No separate VM root. |
| 7. Nominated semantic candidate | N.`candidates[i].semantic_candidate_index` → N.`semantic_compatibility.candidates[i]`, `.value_candidate` → N's VS candidate; exact variable and X's strict index/path. Producer `SemanticCompatibilityQueries.variable_semantic_compatibility`. | Revalidate full N/ES/VS; match all retained candidate content and order. Measured-actual model VSM pin and source interpretation's observation role are different checks. Retain quantity/role/unit compatibility findings and interpretation revision; never choose another satisfied candidate. Honest multiple matches withhold, not incoherence. |
| 8. Selected sample/value and cutoff | VS candidate's `state_candidate.bound.observed.occurrence`; full subject/property locator, occurrence/value/type/receipt/source-time fields; N/ES/VS/VM `.as_of` = X.C. Producer `ObservationCompatibilityQueries.variable_value_compatibility`. | N already carries nested VS/state/occurrence. Do not retain standalone duplicates. An absent bound value is absence, not zero; malformed nominal indices refuse. Match full occurrence, not value/checksum/ID alone. Producer may read explicit temporal/binding material; replay validation cannot. |
| 9. EA selection/assurance | `EvidenceAssuranceQueries.select_operational_evidence` → E; `request.scope`, `horizon_started_at`, `as_of`, policy; snapshot `selected`, `coverage`, `provenance_routes`, `source_material`, `temporal_material`, `capture_fence`, `assurance`, `content_fingerprint`. | E/snapshot public reconstruction validates carried coverage/provenance. `validate_operational_evidence_snapshot` supplies pure validation against X's independent fingerprint. Production reads explicit source/temporal readers; replay does not. E has no model revision. Refusal has issues and no snapshot; incomplete is not refusal. |
| 10. Alignment | `align_operational_evidence_with_value_compatibility(OperationalEvidenceAlignmentRequest(selection=E, compatibility=N.semantic_compatibility.value_compatibility, expected_snapshot_fingerprint=X.expected_fingerprint, schema_version='1'))` → L. | Pure public operation; L outer `.model_validate` rederives its fields. Matches C, six-field consumer locator and full occurrence; seventh EA endpoint field is bound by snapshot closure. Require `matched`, correct nominated `aligned_candidate_index` and `attached` for use. Exact lower ambiguity/refusal/mismatch reasons survive. Derive L rather than archive a fourth duplicated root. |
| 11. Caller policy | Accepted CS full P and independently expected P; exact FM body/CRG/VCN target; explicit age, boundary, coverage window, authorization and source-time/reuse semantics. | Application-only arithmetic and policy applicability; no repository public policy evaluator/ledger exists or is needed. Canonical representation/fingerprint is caller retention, not engineering identity. Unsupported/missing authority cannot become a permissive default. |
| 12. CN evaluation | `ConstraintEvaluationQueries.constraint_evaluation(exact_constraint_anchor, as_of=C, source=explicit_SourceSelector_when_used)` → N; `candidates[i].verdict`, `not_evaluated_reason`, `observed_decimal`, `boundary_assessments`. | Complete N `.model_validate` recomputes indexed verdicts from its carried ES/constraint, but model-selection facts must also match F queries. Verdict is `satisfied`, `violated` or `not_evaluated`; policy never recalculates predicate or changes verdict. No extra CN row copy becomes authority. |
| 13. Disposition | Caller derives the separate axes in section 7 from admitted F/N/E/L/P/X. | No new lower result or exported workflow enum. Policy denial withholds usability, not historical CN disclosure. All reasons remain available; no command, commissioning-complete certificate or operating permission. |
| 14. Provenance/limitations | Preserve full F/N/E roots; P/X; derived L trace; exact record/index/candidate paths, revisions, cutoffs, authority claims, source-time markers, coverage/seed/reuse/fence disclosures and synthetic classification. | No lossy replacement by a green summary. Reconstruct from those inputs without private imports or I/O. Witness hashes do not authenticate uncarried payload/store bytes; claimed authority is not a signature. Presentation references are non-authoritative, not a second truth store. |

The live support inspected includes [kernel material](../../../backend/model_kernel/port_results.py),
[FM results](../../../backend/model_kernel/flow_measurement_results.py),
[FC results](../../../backend/model_kernel/flow_operating_criterion_results.py),
[kernel queries](../../../backend/model_kernel/queries.py),
[CN reconstruction](../../../backend/constraint_evaluation/contracts.py),
[EA contracts](../../../backend/evidence_assurance/contracts.py), and
[alignment derivation](../../../backend/evidence_alignment/derivation.py).
Private derivation was read to verify claims, never selected as a consumer API.

## 6. Explicit caller policy and replay context

This is an application retention recipe using the accepted CS semantic profile,
not a CV public schema. No operational threshold or authority is chosen here.
Policy values must be supplied explicitly; descriptive defaults are forbidden.

| Retained input | Exact rule |
| --- | --- |
| Schema/profile, label, version | CS profile `commissioning.receipt_age_and_attempt_coverage.v1`; explicit application-local label/version, ASCII `[A-Za-z0-9._-]`, 1–64 bytes. No ambient latest-policy lookup or meaning changes under an old version. |
| Authority | Full explicit caller authorization reference, same token bounds, retained with P; authorization established outside the pure comparison. Token presence is not proof of authority. No fetching a URI or secret. |
| Target | Exact public FM effective body and CRG/VCN IDs; independent X also binds complete model revision, exact subject, retained witness requirement, candidate and occurrence. Policy for another coherent target is inapplicable; substitution against expected P is incoherent. |
| Maximum receipt age and unit | `max_receipt_age_us`, canonical ASCII integer string; explicit unit `microseconds`. Same syntax for `coverage_window_us`: `0` or `[1-9][0-9]*`, no signs, whitespace, exponent, fraction or leading zero. Retain CS's proposed application capacity 0…31,536,000,000,000 inclusive (14 characters); not an engineering threshold. |
| Threshold boundary | Exact `inclusive` means `age_us <= limit`; `exclusive` means `<`. Independent of CN boundary inclusion. Inclusive zero permits only genuine zero age; exclusive zero permits no nonnegative age. |
| Required attempt coverage | Exact EA outcome `complete_within_declared_horizon`; CS condition `nonempty_all_captured_attempts_observed_exact_property`. Required horizon is explicitly `[C - coverage_window_us, C]`, inclusive. No Boolean-only replacement or weaker optional rule. |
| Receipt cutoff | Explicit aware receipt-side C, normalized UTC; N/ES/VS/VM and E cutoffs equal C. C is not a model-revision selector. Date overflow/sub-microsecond unsupported inputs refuse. |
| Decision timestamp | May be separately retained as application metadata, explicitly null when absent. If supplied, normalize an aware value; it never replaces C, computes age, picks a revision or changes replay. No ambient `now()` and no assumed clock relation beyond accepted contracts. |
| Reuse/source-time rules | Explicit `receipt_occurrence_with_complete_payload_and_seed_closure` and `disclosure_only`. Rereceipt of identical bytes is allowed when the new lower proof is valid. Source-effective/observed time cannot rescue receipt-age failure. |
| Expected context | Independently retained model/binding/interpretation revisions where carried, exact source scope/endpoint, candidate path, full occurrence, expected snapshot fingerprint, policy content and fixture/application classification. Never derive expected values solely from attacker-controlled results. |

Coverage is precisely EA's disclosed captured-attempt property, not cadence,
continuous physical observation, all-source agreement or a polling SLA. Preserve
`attempt_route_indices`, `property_observed_route_indices` and each omitted,
empty, failed, quarantined and extraction-incomplete set. EA reconstructs these;
the application compares the exact completeness outcome and required horizon.
Empty T never passes. One attempt over two hours can pass without proving
two-hour continuity. Failed attempts anywhere in the required horizon matter,
including after the selected sample. No shorter-window crop rescues failure.
A well-formed independently committed different horizon gives
`coverage_insufficient` / `required_interval_not_established`; a forged capture
under an unchanged expected fingerprint is instead incoherent.

EA's `effective_wall_time` is receipt-side attempt membership (receipt time or
finished-without-response time), not source-effective time. A selected pre-horizon
seed does not count as an in-horizon observed attempt. Retain payload origin,
run, reused-envelope, occurrence and seed dependencies and the captured fences.
Do not rederive these lower algorithms in the workflow.

Receipt age uses only EA-established comparable timestamps:
`C - snapshot.selected.selected_received_at`, exactly in integer microseconds;
compare to the exact decimal `observation_age_seconds` disclosure. No binary
floating-point `total_seconds()` comparison. Preserve the full source-time
marker, basis and clock segment separately; UTC normalization does not establish
cross-clock authenticity or comparability. A selected EA v1 observation must
have receipt time/age: forging them absent is invalid, not an honest age-unknown
example. Legitimate absence and unsupported age bases retain their distinct gates.

For a caller that wants a policy fingerprint, retain the **whole** validated
policy as an exact-key JSON object, including profile, label, version, authority,
target, duration strings, explicit unit/boundary, coverage and reuse/source-time
rules. A documented application encoding may use UTF-8, sorted object keys,
compact separators, `ensure_ascii=False`, `allow_nan=False`, no trailing newline;
fingerprint is `sha256:` plus SHA-256 of those exact bytes. Reject duplicate keys,
unknown fields and noncanonical scalars before encoding. Obtain the FM body from
public reconstructed material/indexes; do not copy lower canonicalization logic.
This is an optional application checksum convention, not a new required backend
policy identity. Exact expected full-policy equality remains mandatory whether
or not a checksum is displayed. Same-version/different-content substitution
fails; hashing a substituted policy and its own hash is not authorization.

Keep C, optional decision timestamp, exact expected context and resulting
disposition beside the full policy; they are not silently inserted into its
rule hash. Historical replay supplies the old P, X, F, N and E, not today's
configuration. It asserts usability under that historical P at C only.

## 7. Separate decision axes and refusal-preserving display

No workflow Boolean, exported enum or new result class is proposed. A caller
must preserve these nine axes, even if a primary CS disposition stops later gates:

| Axis | Values/authority and interpretation |
| --- | --- |
| Request admission | Admitted, `input_or_revision_incoherent`, or supported-policy applicability unavailable. Structural/budget failures are not criterion violations. |
| Governing applicability | Exact FC `not_declared`, `inactive`, `conflicted`, `disagreed`, `inapplicable`, `applicable`, with full reasons. Staleness appears as reasons such as `vcn_not_current`/`typed_support_not_current`, not a fabricated FC `stale` status. |
| Nominated-candidate selection | Exact strict candidate/occurrence identified; legitimate absence; `multiple_matching_candidates`; mismatch. Ambiguity is not incoherence unless carried material is actually inconsistent. No pick-first behavior. |
| Evidence selection | Exact EA `refused`, `incomplete_within_declared_horizon`, `complete_within_declared_horizon`, with issues/snapshot as allowed. |
| Evidence alignment | Exact L status/reason, candidate attachment/index, fingerprint/cutoff/scope/occurrence relations. Complete alignment is not model or semantic admission by itself. |
| Receipt-age policy | Within explicit bound, `receipt_age_exceeded`, unavailable/not reached. The latter two are not interchangeable; selected v1 missing age is malformed. |
| Attempt-coverage policy | Exact required complete horizon satisfied, `coverage_insufficient`, or not evaluated; preserve actual EA completeness and interval relation. |
| Constraint verdict | N's exact `satisfied`, `violated`, `not_evaluated` plus existing reason, or no admissible nominated evaluation. Never recomputed from policy or a lower failure. |
| Final workflow disposition | CS-compatible use/withhold/refusal mapping below; no operational command or engineering verdict. |

| Situation | Final disposition and user-visible answer |
| --- | --- |
| All joins and policy gates pass; A satisfied | `policy_permits_use`: “Evidence usable under P at C; governing A satisfied.” |
| Same gates; A violated | `policy_permits_use`: “Evidence usable under P at C; governing A violated.” Violation does not invalidate evidence. |
| Age/coverage are sufficient but N is `not_evaluated` | `criterion_evaluation_unavailable`, retaining CN's exact reason. Display “Evidence meets the stated age/attempt-coverage tests; governing A was not evaluated.” This distinguishes evidence usability from evaluation availability, but does **not** redefine CS's final use-permission gate or advertise a usable satisfied/violated verdict. |
| Otherwise admitted evidence fails age | `evidence_not_usable_under_policy`, reason `receipt_age_exceeded`; retain A's CN finding as not currently usable under P. Never physical-measurement staleness or falsity. |
| Exact required coverage fails | `coverage_insufficient`; withhold usable verdict; retain incomplete/failed routes or `required_interval_not_established`. A new reading alone may not repair a historically failed horizon. |
| EA refused | `evidence_selection_refused`; preserve EA issue(s) and L `selection_refused`; age/coverage not evaluated. |
| Honest multiple exact matches | `criterion_evaluation_unavailable`; retain L `multiple_matching_candidates` and `multiple_matches`. Do not classify as incoherence or select a winner. |
| FC absent/inactive/conflicted/disagreed/inapplicable | `applicability_unavailable`; preserve exact FC conclusion/reasons and all roots/body groups; no governing satisfied/violated assertion. |
| Valid absence | `evidence_absent`; preserve `no_selected_observation`, consumer absence or no observation at/before C as applicable. No false or zero value. |
| Wrong full record/revision/candidate/cutoff/witness/policy commitment or invalid nested result | `input_or_revision_incoherent`; refuse; do not call it stale, unknown source truth or criterion violation. |
| Missing/unsupported policy semantics or unestablished authority | `policy_inapplicable`; explicit unknown/withheld policy use, never fallback defaults. Other unsupported/unavailable scope is disclosed as unknown, not a fabricated success. |

Follow accepted CS primary-gate order: structural admission/independent commitments;
lower reconstruction and coherence; EA refusal; FC applicability; policy
applicability/authority; nominated-observation availability; candidate alignment
and CN availability; required coverage; age availability/comparison. Legitimately
absent material does not force an impossible positive join. Do not skip admission
of a forged supplied CN merely because EA refused. Preserve valid earlier lower
findings and mark unreached policy checks not evaluated.

If a diagnostic display separately evaluates age/coverage facts for an identified
candidate whose CN is not evaluated, label those as separate evidence tests,
not a different primary CS disposition. No new permission semantics is introduced.
An apparently stale and incomplete sample retains both lower facts; deterministic
primary refusal follows the gate order, not a hidden severity ranking. The display
must distinguish “A evaluated satisfied but withheld” from “A usable and satisfied.”

## 8. Integrity, carry-once material and bounded reconstruction

No new request/result contract is recommended, so there is no CV validator to
implement or claim tested. The existing application recipe has a precise trust
boundary nevertheless:

1. Retain F, N and E exactly once as complete accepted roots, plus P/X. Derive L
   from E and N's existing VS; do not archive L's duplicated request alongside
   another copy of E/VS in a supposedly carry-once canonical aggregate. Keep FM,
   CRG/VCN, ES, VS, VM and occurrence in their existing nested locations.
2. Existing schemas themselves repeat some request/member material. Do not strip,
   flatten or deduplicate inside them. A separately retained full L is an optional
   artifact with inherited duplication, not a new deduplicated authoritative proof.
3. Revalidate complete F, N and E through public boundaries; rederive L; compare
   exact model-derived N/VS/VM facts to `ModelQueries(F.material.loaded())` and
   registrations. Validate X independently; public result self-consistency alone
   cannot prove the caller intended that model, source, candidate or policy.
4. Recompute the policy checksum, age/coverage decisions and display disposition
   from full retained inputs. Never accept an independently supplied green flag
   or cached CN/FC summary as authority. Do not mutate records or splice a new
   revision into an old result. Historical material is valid only for its exact
   request; mixed before/after revisions refuse.
5. Exact lower indices and array order are authoritative: missing, duplicate,
   extra, reordered, substituted or noncontiguous material refuses through the
   owning validators. Strictly reject Boolean-as-index and hostile scalar types
   before lookup. Preserve alternate valid candidates; do not confuse honest
   lower multiple-match material with unauthorized duplicated rows.
6. Before serializing in-process objects, reject unsupported subclasses, hidden
   fields/private state, cycles and access/conversion hooks. A `model_copy` or
   `model_construct` object is untrusted input. Do not invoke arbitrary methods
   or silently lose hidden extras by dumping first. Legacy summary-only results
   do not acquire full-model authority because a local validator accepts them.
7. For JSON, preflight bytes/depth, reject duplicate keys and non-finite constants,
   then enforce exact supported types and bounded expanded nodes. Retain finite
   lower scalars only where their actual contracts permit them. Duration values
   are canonical strings, not float/Decimal/int/Boolean coercions.
8. No filesystem/store/network, source query, environment configuration, clock,
   LLM or latest-policy lookup occurs during reconstruction. Lower production and
   optional explicit store-bound EA revalidation are separate caller operations.
   Hashes and captured metadata authenticate no source bytes or current ledgers
   that the result does not carry.

The accepted CS exploratory input ceilings remain guidance, not new CV limits:
one F/N/E root each, one P/X and one nomination; aggregate 128 MiB, 200,000
expanded nodes, depth 128; policy 16 KiB/512 nodes/depth 8; stricter accepted
lower limits remain in force (including FC 4 MiB). Repeated shared-object
appearances count against reconstruction work. These do not promise admission
of simultaneously maximal lower results or production latency. The separately
acquired examples measured three-root sizes 17,634 + 33,263 + 19,803 bytes for
60.1, and 17,634 + 33,255 + 19,797 for 40; they are observations, not frozen
workflow artifact contracts. An actual consumer must explicitly set and measure
its capacity rather than silently inherit a number from TA or this document.

Crossing a chosen cap refuses the whole input; never truncate the proof, crop
coverage or omit unfavorable roots to fit. Canonical application JSON must retain
accepted lower array order, normalize policy/context explicitly, use fixed root
ordering, and contain no ambient timestamps or hash iteration order. Across-hash-
seed determinism is a verification obligation of any future application artifact,
not a claim that a new CV artifact exists. This proposal's arithmetic/hash example
is checked independently of any such artifact.

## 9. Spill register

Guard classes: **S** structural boundary (for the no-runtime recommendation or
existing package direction); **V** existing validation or explicit caller check;
**D** documented limitation requiring honest presentation. **B** means a stronger
claim is blocked pending an exact prerequisite, not silently weakened. No unavoidable
spill is required for correct in-process composition. Existing lower boundaries
prevent backend spill; they do not implement the application guards. Authentication
and authorization, policy authority, result retention, error translation,
confidentiality, resource ownership, deployment, and scope completeness remain
application-design prerequisites. None may be guessed or hidden inside a generic
backend wrapper. A future boundary unable to enforce these guards must stop and
identify its missing prerequisite. All 26 register entries below are preserved.

| ID / category | Spill | Guard and enforcement |
| --- | --- | --- |
| SP01 Semantic | Evidence usability → observation truth | D/V: retain separate policy/evidence axes; never emit a truth assertion. Accepted results bind disclosures, not reality. |
| SP02 Semantic | Criterion satisfied → system healthy | D: say exact A satisfied for candidate at C, not system health. B for health: domain verdict/authority absent. |
| SP03 Semantic | Declared logical flow → physical occurrence | S/D: no occurrence record/output; FRG/FLD/FM/FC preserve declaration-only meaning. |
| SP04 Semantic | VPA/FMA port association → observed at port | D/V: exact owner/port relevance only; observation provenance remains its source locator. |
| SP05 Semantic | Orientation/direction → causality | D: `aligned` is a declared mapping, not causal influence or transport. |
| SP06 Semantic | Workflow disposition → safety approval | S/D: no safety/operate/command field or permission to energize hardware; safety prerequisites absent. |
| SP07 Layer | CS policy in model_kernel | S: no new kernel code/record/query or imports; caller retains P. |
| SP08 Layer | Commissioning policy in EA/CN/FC/FM/temporal | S: no lower modifications; each retains its accepted semantics. |
| SP09 Layer | Lower layers import workflow / private workflow access | S/V: application imports public lower surfaces only; no workflow package created. Private code was inspected, not used as a consumer seam. |
| SP10 Validation | Copying canonicalization/lifecycle/body derivation | V: public material/queries own those algorithms; policy JSON hashing is not lower record canonicalization. |
| SP11 Validation | Trust nested/cached green results | V: complete public root validation plus model-fact and independent commitment joins; reject hidden state before dumping. |
| SP12 Validation | Weaken exact revision/identity/candidate/cutoff/witness | V: full fields and exact paths from section 5; no value-only or same-anchor shortcut. |
| SP13 Validation | Choose favorable conflict or multiple match | V/D: preserve all roots/candidates and exact unavailable/refused reason, no tie breaking. |
| SP14 State/persistence | Workflow store or derived disposition as model truth | S: no store/ledger/record or persistence implementation. Application retention, if separately authorized, retains a derived historical trace only. |
| SP15 State/persistence | Writes to source/temporal/model ledgers | S: validation is pure; no authoritative append. Disposable source production for design verification does not grant runtime write authority. |
| SP16 State/persistence | Policy fingerprint becomes engineering identity | D/V: optional checksum of retained caller policy; full content and external authorization required, no minted anchor or ledger lifecycle. |
| SP17 Scope | Select/rank measurements or best test | S/D: one independently nominated candidate; no candidates optimization, acquisition plan, cost/risk/information-gain utility. |
| SP18 Scope | Diagnosis, causal reasoning, impact, planning/optimization | S/D: no engine or output for these; DI remains bounded composition, not physical impact. |
| SP19 Scope | Commands, maintenance or safety recommendation | S/D: no device adapter invocation in composition; optional human response to evidence withholding is outside the result. |
| SP20 Fixture | Synthetic data presented as real printer knowledge | D/V: independently supplied synthetic classification and mandatory disclaimer in any displayed example; no new authenticated-real flag inferred from source names. |
| SP21 Fixture | FMA/FCD append merely to make demo complete | S: zero authoritative append; current 36-record model honestly lacks these declarations. |
| SP22 Fixture | Edit predecessors or infer wiring/flow/condition | S/D: preserve all predecessor bytes and memberships; disposable fixtures prove contract behavior only. |
| SP23 Data/security | Unnecessary raw payload carriage | S/V: retain accepted metadata/proof roots, not raw payload blobs or a second extraction cache. Do not erase lower value_json fields required for validation. |
| SP24 Data/security | Secrets/absolute paths in outputs | V/D/B: caller uses bounded opaque policy references and value-free errors; no exception trace or temporary filesystem path in a workflow result. Lower validation does not certify that carried values/metadata contain no secrets or paths. Before disclosure, the application must admit the complete required material under its confidentiality rules; it must refuse public output or require separately authorized restricted retention when those rules fail, not redact canonical proof fields and claim unchanged validation. The disposable examples contain no operational credentials. This proposal's temporary-script path is reproducibility metadata, not result content. |
| SP25 Data/security | Unbounded material/replay of hostile objects | V: preflight bytes/depth/work and exact types before public reconstruction; whole-input refusal, never partial success. No executing acquired content. |
| SP26 Data/security | Captured proof represented as live authentication | D: report historical fingerprints/fences and stated assurances only; no uncarried byte, ledger, time or authority authentication. |

## 10. Executable-quality disposable worked cases

### 10.1 Common worlds and reproduction boundary

**W60** and **W40** below are separately acquired disposable worlds, not edited
green result objects. Each uses the inspected FC producer up to, but excluding,
its `craft_value` mutation. For each, obtain `happy_script()` from the existing
DS test helper, decode only the scripted `/printer/objects/query` response body
in memory, set `result.status.extruder.temperature` to 60.1 or 40, and supply a
new `ok_json` response with the explicit original Date header. Use the existing
`_captured_world(temp_directory, script=responses)` to acquire/project it and the
existing FC producer's public model/binding/interpretation/VS/ES/CN operations.
This changes no fixture file. Capture independent expected context from the
trusted disposable producer before testing replacement inputs.

Recompute alignment using N's **carried** VS and the producer-established expected
fingerprint, not the original producer's optional no-expectation alignment.
Both executions passed: FC applicable; attached, complete alignment; fingerprint
matched; age 3,594 seconds; exact A join; A violated in W60 and satisfied in W40;
B satisfied in both but not governed. Three-root sizes are in section 8. These
response bytes differ from the frozen FC proof, so their new snapshot fingerprints
are not substituted for the accepted 174,490-byte witness:

- W60: `sha256:37259b04c6b2d92794ec03b2054558accfed07894a4e9c3dfb0eaa328186cf80`.
- W40: `sha256:e2b00eaf6d4e70421c3ca16b96a8093205bc18329cd33a96810c283e52ab468e`.

Only these two coherent full-path examples and the existing focused lower tests
were executed for CV. The remaining rows specify executable-quality construction
and oracle conditions using accepted helpers/public builders; they are not claims
that a CV engine or every hypothetical combined workflow was implemented/run.
No authoritative fixture, record ID, ledger append or committed demonstration
is introduced. Use a fresh temporary world for each variant and retain every
new independent commitment rather than patching the old snapshot green.

Common illustrative P1 is the complete CS profile, label `commissioning.demo`,
version `v1`, authorization `owner.example.v1`, exact A/FM target, inclusive
maximum `3600000000` microseconds and window `7200000000`. P2 explicitly changes
version/authorization and maximum to `3000000000`. All other mandatory rules
remain explicit. These are examples, not operational configuration defaults.

### 10.2 Fifteen required cases

| Case | Construction and exact expected result | Valid twin / guard |
| --- | --- | --- |
| 1. A violated; B satisfied | W60 + P1: `policy_permits_use`, governing A `violated`. Replace N with the same world's B result while keeping X/F fixed: full CRG/VCN join refuses as incoherent. | Original W60 A is valid; independently approving another governing world is a different request, never silent B substitution. Executed exact A/B pin comparison. |
| 2. A satisfied, usable | W40 + P1: `policy_permits_use`, governing A `satisfied`; matched E/L refer to the separately acquired value 40. | W60 is the violated twin with the same model/policy. Old W60 E plus W40 N must not pass. Coherent W40 path executed. |
| 3. Satisfied but receipt-age failure | W40 + P2: 3,594,000,000 > 3,000,000,000; `evidence_not_usable_under_policy` / `receipt_age_exceeded`. Keep satisfied verdict as withheld under P2. | W40 + independently authorized P1 permits. Same-version/unchanged-expected-policy tampering is incoherent instead. |
| 4. Violated but insufficient coverage | In a fresh W60 acquisition world, include an accepted failed attempt in the required horizon with no later observation; capture E anew and requery N at C. Exact attachment can remain while E/L report incomplete coverage. Final `coverage_insufficient`; no usable violation. | Fresh complete W60 + P1. Existing EA failed/quarantined route and pre-horizon incomplete tests supply the lower construction patterns. A declared shorter required horizon is a new policy/request, not cropping old material. |
| 5. Selection refusal | Build the accepted refusal form: same E request, `status='refused'`, snapshot null, issue `invalid_bounded_material` with explicit safe detail and null route; use otherwise coherent F/N. L reports `not_evaluated` / `selection_refused`; final `evidence_selection_refused`. | Valid non-refused W60 E aligns. Do not demand a nonexistent snapshot fingerprint for refusal or infer stale evidence. Existing alignment refusal test verifies the form. |
| 6. Multiple matching candidates | Use the existing `duplicate_consumer` admitted VS test construction, preserving both exact matching candidate paths and the expected multiplicity; public alignment gives `multiple_matching_candidates` / `multiple_matches`, null aligned index. A complete CN composition must carry matching ES/VS rows under its public validator. Final `criterion_evaluation_unavailable`. | Existing `explicit_consumer` unique-selector twin aligns. This is lower-admitted ambiguity, not permission to inject duplicate rows into a fixed independently expected result. The VS/alignment lower case is tested; no fabricated full CN ambiguity execution is claimed. |
| 7. Missing governing declaration | Use `world()` without adding `declaration(witness, crg, vcn)` and public complete material/FC query. FC `not_declared` / `fc_not_declared`; final `applicability_unavailable`. | Add one valid disposable FCD and independently bind the new membership; applicable twin. The authoritative demo remains absent, not an excuse for implicit designation. |
| 8. Conflicted FC lineage | In the helper world, append two distinct same-root FCD successors using `replace`/`declaration`, each superseding the root, with different notes. Requery complete membership: `conflicted` / `fc_same_root_conflict`. | Two independent equal-body roots corroborate; or a valid same-root merge explicitly supersedes both tips. No authority/time/ID winner. |
| 9. Stale VCN or FM support | Add `replace(vcn, supersedes=(vcn.record_id,))` even with identical semantics: FC inapplicable / `vcn_not_current`. Alternatively correct VPA then FMA's exact VPA pin; retained old FCD gets `fm_body_not_current` and/or typed-support reasons. | Explicitly renew the required exact FMA/FCD chain, preserving all history and binding the new revision. An independent healthy same-body FMA may preserve old witness applicability only when FC's other gates agree. |
| 10. Recent source time, old receipt | Use a lower-admitted occurrence with recent source wall-clock marker or advanced monotonic marker and old receipt, with all changed raw/extraction/temporal content coherently recaptured. P2 still fails on receipt age only. | Source time unavailable or unchanged gives the same age result. W60's actual monotonic source time is never cross-compared; do not edit a source marker in place to fake this full-world twin. |
| 11. Exact threshold / one unit over | W60 age 3,594,000,000 us: inclusive max `3594000000` passes; max `3593999999` fails. Exclusive exact max fails; `3594000001` passes. | Genuine zero-receipt-age selection passes inclusive zero and fails exclusive zero; zero-window coverage still requires a captured attempt at C. Exact arithmetic below; accepted EA fractional/zero-age tests supply lower twins. |
| 12. Byte-identical rereceipt | Existing EA `_world` → run twice with unchanged `happy_script`, project both, capture selection: two attempts/occurrences, one envelope/observation, selected second occurrence. Set explicit C to second receipt plus one second and recapture/requery every affected lower result. Under a two-second maximum and complete required horizon, receipt age passes even if old receipt would fail. | Same valid old receipt under a larger explicit threshold passes; editing only received_at or dropping payload-origin/seed dependencies refuses. Existing reuse test confirms distinct occurrences and one reused payload/observation; no new physical measurement inferred. |
| 13. Forged key/policy/witness | Keep X independently fixed; substitute cutoff, policy content/hash, candidate path, VCN, FMA witness or model revision in otherwise plausible data. Public reconstruction or exact expected joins refuse as `input_or_revision_incoherent`. | Fully reconstruct and independently authorize a genuinely different request; do not call changed expectations a successful attack. Wrong policy target with genuinely different authorized P is policy-inapplicable, not implicit renewal. |
| 14. Historical replay | Retain complete F/N/E/P1/X at C. After adopting P2 elsewhere or adding a VCN successor, replay the original membership and original roots/policy, with no latest lookup. Historical P1 disposition unchanged; no claim about current membership or today's use. | Same evidence evaluated under explicitly supplied P2 gives receipt-age denial; blending current FC with historical N refuses mixed revision. |
| 15. Synthetic disclaimer | Label W60/W40 and their independent expected context as disposable/synthetic. A displayed example must say “Synthetic contract demonstration; not evidence of real wiring, physical flow, operating condition, health or safety.” | A correctly labelled synthetic report is valid. Omitting/changing that label fails the caller's presentation/context rule; lower packages do not cryptographically certify realism. A real-world claim is blocked pending real accepted evidence/authority, not permitted by renaming the source. |

### 10.3 Executable arithmetic and fingerprint illustration

This runs only after public-result and exact-policy admission. It is neither a
CV API nor an evidence validator; no source query or ledger write occurs.

```python
from datetime import datetime
from hashlib import sha256
import json

received = datetime.fromisoformat('2026-08-07T20:00:06+00:00')
cutoff = datetime.fromisoformat('2026-08-07T21:00:00+00:00')
delta = cutoff - received
age_us = (delta.days * 86400 + delta.seconds) * 1000000 + delta.microseconds
assert age_us == 3594000000
assert age_us <= int('3600000000')
assert not age_us <= int('3000000000')
assert age_us <= int('3594000000')
assert not age_us <= int('3593999999')
assert not age_us < int('3594000000')
assert age_us < int('3594000001')
assert 0 <= int('0') and not 0 < int('0')

# Illustration of an application checksum, NOT a complete admitted policy:
fragment = {'age_unit': 'microseconds', 'max_receipt_age_us': '3600000000',
            'boundary': 'inclusive', 'version': 'v1'}
other_order = dict(reversed(tuple(fragment.items())))
encode = lambda value: json.dumps(value, sort_keys=True, separators=(',', ':'),
                                 ensure_ascii=False, allow_nan=False).encode('utf-8')
assert encode(fragment) == encode(other_order)
assert sha256(encode(fragment)).digest() == sha256(encode(other_order)).digest()
changed = {**fragment, 'max_receipt_age_us': '3000000000'}
assert sha256(encode(fragment)).digest() != sha256(encode(changed)).digest()
```

## 11. Threat model and valid twins

Attacker controls supplied content, not independently retained caller commitments.
If all results and the expected context/authority are replaced together, neither
hashing nor a new wrapper authenticates them. The following are checks an actual
caller must enforce, not a claim that an unimplemented CV validator already does.

| Attack | Fail-closed rule | Valid twin |
| --- | --- | --- |
| CV-T01 A versus satisfied B | Exact full CRG/VCN equality to applicable F group and X; reject B. | Original violated A with complete evidence remains usable. |
| CV-T02 Candidate substitution | Strict nominated index/path, full occurrence/locator and N/VS/L index agreement. | Independently nominated different sample with complete new context/roots. |
| CV-T03 Policy substitution | Full expected-policy equality, recomputed optional checksum, explicit authority/version. | Separately authorized P2; changed policy may legitimately deny use. |
| CV-T04 Cutoff substitution | Exact N/ES/VS/VM/E receipt cutoff = X.C; decision timestamp cannot replace it. | Equivalent UTC instant representation; or separately authorized new C with rederived results. |
| CV-T05 Revision substitution | Exact complete F material and model-bearing N facts; historical versus current context explicit. | Reference-closed historical replay with its original N/P/X. |
| CV-T06 Flow/port/context substitution | Full five-part FC subject, variable owner, participant role and orientation; no name/token equality. | Different explicitly nominated subject with matching model/results is a separate request. |
| CV-T07 FMA witness substitution | Preserve exact retained witness and public body match; compare X's witness/body commitment. | Old witness retained while another healthy current equal-body FMA supports it. |
| CV-T08 Corrected VCN substituted by same anchor | Exact current VCN and whole F/N equality; retain `vcn_not_current`/conflict. | Explicit accepted renewal chain and new independently committed revision. |
| CV-T09 Mixed lower roots | N-carried VS is L's consumer; E/occurrence/fingerprint exact; reject W60 evidence with W40 N. | Coherently acquired W40 F/N/E and rederived matched L. |
| CV-T10 Stale/forged nested results and IDs | Public complete revalidation, canonical record checks and model-fact joins; reject hidden extras before dumping. | Canonical `build_record` content plus full admitted membership and recomputed results. |
| CV-T11 Receipt/effective-time confusion | Receipt age only; preserve source markers without cross-clock subtraction. | Same receipt proof with unavailable/monotonic source time gives same policy age. |
| CV-T12 Coverage reduction | Compare required horizon and reconstructed exact EA completeness; no crop/favorable route omission. | Complete explicitly captured required horizon; honestly committed incomplete horizon is coverage denial, not forgery. |
| CV-T13 Refusal collapsed into staleness | EA refusal and exact issues precede age policy; no snapshot invented. | Valid non-refused snapshot reaches age evaluation. |
| CV-T14 Multiple matches resolved silently | Preserve `multiple_matching_candidates` / `multiple_matches`; no tie break. | Existing explicit unique-selector twin aligns. |
| CV-T15 Lower failure → criterion violated | Only N's exact evaluated row can report violation; preserve `not_evaluated` and reason. | Actual violated A from numeric CN evaluation with admitted inputs. |
| CV-T16 Policy failure → measurement falsehood | Age/coverage deny workflow usability only, retain original observation and CN verdict. | Byte-identical valid rereceipt can satisfy receipt-age policy without changing physical measurement. |
| CV-T17 Physical-flow/safety overclaim | No physical occurrence/health/safety/operate field; mandatory bounded-language limitation. | “Governing A satisfied for nominated sample at C under P” with explicit exclusions. |
| CV-T18 Hidden I/O | Pure reconstruction/derivation only; reject objects/hooks/config lookups and ambient clocks. | Explicit producer acquisition outside replay; stored complete roots validate with I/O forbidden. |
| CV-T19 Duplicated or missing authoritative material | Exactly one retained F/N/E root and P/X; derive L; retain mandatory nested fields/order. | Existing unavoidable lower-schema repetition is preserved, not stripped to satisfy an invented global dedup claim. |
| CV-T20 Unbounded reconstruction | Explicit byte/depth/expanded-node and scalar preflight; whole-input refusal, no favorable truncation. | At-limit supported request admitted if all lower limits pass; one-over refused without partial answer. |
| CV-T21 Synthetic presented as real | Independently retained synthetic classification and required disclaimer; no rename-to-real inference. | Correctly labelled disposable demonstration. Real application authority/evidence is a separate prerequisite, not supplied by this witness. |
| CV-T22 Reordered/duplicate/extra/noncontiguous rows or Boolean index | Reject through owning result reconstruction and strict caller index admission; do not sort malformed arrays into validity. | Different object insertion order with unchanged canonical arrays; ordinary integer zero at a real index. |
| CV-T23 Coherent snapshot plus new self-reported fingerprint | Match independent expected fingerprint; embedded self-consistency is insufficient. | New trusted producer capture separately bound by X, not copied from an adversarial replacement. |
| CV-T24 Silent defaults/unsupported authority | Missing or unsupported policy/authorization withholds; no implicit threshold or latest version. | Complete explicitly authorized CS-profile policy with all required values retained. |

No attack identifies a missing lower public field or requires a new durable
engineering fact. The existing public joins plus caller admission/retention
prevent the bounded substitutions. If a future actual application cannot enforce
them safely, its concrete failed boundary—not this hypothetical list—would be
the evidence for revisiting a typed application contract.

## 12. Authoritative fixture question

Recommend **no authoritative append**. The live model's zero FMA/FMW and FCD/FCW
counts are honest: it does not declare an applicable commissioning criterion for
an invented demo association. The disposable integration already proves join and
policy feasibility; increasing record counts adds no integrity property.

An optional deterministic application artifact over disposable material could be
useful only if an owner names its recipient, retention needs, exact input format,
output contract and synthetic classification. It is not recommended or created
here merely to offer a prettier witness. Its original roots/policy/context would
remain the authority for reproduction, not a new model disposition record.

A future exact FMA-then-FCD append is neither necessary nor proposed. Maximum
authorized records in this task: **zero**. There is therefore no fictional
two-record allocation, evidence/authority plan or reserved rehearsal gate to
approve. If a concrete engineering declaration is later needed, a separate
owner-approved task must establish its evidence and authority, exact records,
dependency order, disposable rehearsal, predecessor byte preservation, explicit
historical replay, synthetic/real boundary and deterministic artifact contract.
None of that can be inferred from “commissioning workflow.”

## 13. Original-objective contribution and exact user-visible delta

| Original objective | Existing answer relevant to this question | CV-specific delta / exclusion |
| --- | --- | --- |
| 1. What exists and how connected? | Exact logical flow, participant, variable and explicit governing designation. | No new declaration or connectivity capability; dependencies are already public. |
| 2. Current state of this particular system? | Architecture/test support for a bounded nominated sample/criterion answer at C under exact revision and caller policy; usable satisfied/violated versus withheld/unavailable. | Not delivered application capability: no stable entry point exposes the complete answer. Not current physical system state, occurrence, continuity or health. |
| 3. Why might it behave this way? | Can explain a lower refusal or policy withholding. | No causal diagnosis, mechanism or behavioral explanation. Causal diagnosis remains premature. |
| 4. Next best measurement or test? | May tell the application that this nominated evidence is unusable under P and could be refreshed outside the result. | No choice among alternatives, information-gain/cost/risk/accessibility ranking, acquisition command or assertion that a new physical measurement is necessary. |
| 5. What changes would affect it? | Existing exact pin/revision checks disclose whether this join still applies; DI guidance can mark supplied decisions for reevaluation. | No new dependency traversal, physical impact, behavioral prediction, risk or cost/schedule analysis. |
| 6. Smallest changes to desired state? | No such answer. | No goals/actions, planning, optimization or control. |
| 7. Observed/calculated/inferred/assumed/unknown? | Architecture/test support for separating observed evidence, declared criterion, calculated CN verdict, explicit caller policy, disposition and unknown/refused states. | Not delivered application capability: no stable application result/presentation exists. No new epistemic fact or source authentication. |

The sentence “Evidence usable under P at C; governing A violated” is supported
by correct in-process public composition plus explicit caller policy. The accepted
FC integrated witness proves the lower public join, not a stable application
operation. Its original satisfied-A twin was CN-only; separately acquired W40
closes full-path test coverage, not an architectural or user-facing capability
gap. Objectives 2 and 7 have architecture/test support, not delivered application
capability. Objective 4 still lacks next-best-measurement or test selection.
The backend must not be credited with a user-facing workflow that has not been
built. Backend additions are cancelled; application delivery is deferred until
the concrete consumer requirements in sections 1 and 14 are supplied.

## 14. Owner gates, verification and stopping boundary

No implementation slices are authorized. The owner accepts the challenger's
scope correction: no backend additions, with application delivery deferred.
Before further application work, a concrete consumer must supply all eleven
requirements in section 1: ingress/invocation; authentication/authorization;
commissioning-policy authority; policy schema/version/retention; decision-result
retention; application/user identity; confidentiality; capacity/latency; error
presentation; deployment/resource ownership; scope completeness. Independently
trusted context and synthetic/real classification must be resolved within those
requirements. They are application prerequisites, not missing kernel facts.
Further backend abstraction requires a demonstrated integrity gap. Causal
diagnosis, next-test ranking, impact prediction, and planning remain unauthorized.

Reject now: workflow runtime package, shared policy engine, typed aggregate
without an actual application boundary, CLI/report milestone without a recipient,
HTTP API, kernel extensions, authoritative FMA/FCD demonstration append, durable
workflow/policy identity, recommendation/diagnosis/impact/planning/control.
No successor implementation is approved; ADR-0023 remains absent, unallocated
and unreserved. The separately completed challenger audit remains unchanged;
no additional challenger is run for this correction.

The original authoring verification below is retained as historical evidence;
fresh closeout checks are recorded in the
[correction report](../reports/2026-09-10-cv001-proposal-correction-report.md).
Original verification includes baseline/DI hash, protected document/tree/export
digests, model load/count/revision/family counts, accepted ADR sequence and
historical verification accounting; both accepted witnesses reproduced through
the existing preservation checker; separately acquired W60/W40 public-join
checks; and existing focused lower tests. Final checks cover this file's numbered
sections, fourteen join steps, fifteen worked cases, spill/threat row counts,
local links, arithmetic/checksum illustration across hash seeds, exact ending
marker, whitespace and one-file worktree allowlist. No CV implementation/test
file, new test suite or committed demonstration is produced.

The focused command uses the existing test files only:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/evidence_alignment/test_derivation.py tests/evidence_alignment/test_expected_fingerprint_integrity.py tests/evidence_alignment/test_isolation.py tests/evidence_assurance/test_selection.py tests/model_kernel/test_flow_operating_criterion_slice_b.py -q
```

Original authoring result: **71 passed in 26.50 seconds**. This is focused existing-test
verification, not a new complete-repository verification count.

A full repository/clean-checkout matrix is unnecessary and was not run for this
design-only task. No production performance, exhaustive CV scenario execution,
new outer-result validator or canonical workflow artifact is claimed. Existing
authoritative files/ledgers/fixtures/identities/memberships/artifacts are unchanged;
disposable acquisition checks are not authoritative appends.

Repository brainstorming informed necessity and alternative comparison;
verification-before-completion informed fresh checks and bounded claims. The
user's exact proposal path, no-commit/design-only/stop instructions override
the skills' default spec path, commit, review-dialogue and implementation handoffs.
Only the proposal was written in that original authoring task, without a commit.
The subsequent owner-authorized documentation closeout corrects this proposal,
preserves the audit, and records the deferral; it authorizes no implementation.

END OF CV-001 CODEX LEAD PROPOSAL
