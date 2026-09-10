# CV-001 Codex Lead Proposal — Independent Challenger Audit

One independent adversarial audit of the frozen CV-001 lead proposal —
2026-09-10.

## 1. Verdict and findings

Verdict: `approve_with_corrections`.

The backend conclusion survives: no kernel, ledger, authoritative fixture,
reusable commissioning package, CLI, HTTP endpoint, or speculative application
schema is justified by the current evidence. Existing public lower contracts can
be composed to answer the bounded commissioning question, and this audit did so.
Cancellation needs one scope correction, however. The repository does not expose
that complete answer through an application entry point. It supplies the lower
results and enough public validation to let a correctly implemented application
compute it. The final CS policy evaluation, gate order, cross-result admission,
disposition, and user-facing carriage exist only as application guidance and
ad-hoc audit code.

Finding counts:

| Classification | Count |
| --- | ---: |
| Blocking | 0 |
| Required correction | 1 |
| Non-blocking observation | 3 |

### RC-1 — Existing composability is not an exposed application capability

The proposal must describe the current state as **architecture capable of the
answer and tests demonstrating its lower composition**, not as a repository
application already exposing the answer. There is no public operation accepting
the complete `F/N/E/P/X` input, no public CS policy evaluator, no application
result contract, and no CLI, report generator, or HTTP ingress. The accepted
integrated witness stops after FC, EA, alignment, and CN; it does not execute the
CS policy or emit the final workflow disposition. This is a concrete application
capability gap and the documentation-only component required by the mandate.

This correction does not justify implementing a wrapper now. A correct direct
application composition was reproduced without private fields or duplicated
lower algorithms. The repository has no specified application consumer from
which to obtain ingress, caller identity, authorization, policy ownership,
retention, error presentation, audit destination, capacity, latency, or
deployment requirements. CV should therefore be cancelled as a backend
architecture milestone while application delivery is **deferred pending concrete
ingress and authority**. Objectives 2 and 7 receive architecture/test support,
not current user-facing delivery; objective 4 still receives no next-best-test
selection.

### NBO-1 — The accepted satisfied-A twin is deliberately narrower than W40

The accepted 174,490-byte witness uses `craft_value` to add value 40 to its
temporal store and requeries CN. It proves satisfied governing A with unchanged
FC, but it does not reacquire and realign an EA snapshot for value 40. The
separately acquired W40 world does that and closes witness coverage. It adds no
new public field, decision, or algorithm. The proposal states this limitation
accurately.

### NBO-2 — A future direct application owns omission and refusal preservation

Lower validators reject forged roots, but they cannot force application code to
invoke FC, carry the independent fingerprint, compare the governing VCN, retain
an unfavorable CN row, or preserve an EA refusal. The direct composition is
sufficient only when the application implements every admitted join. This is a
real responsibility at the future application boundary, not a defect in the
lower contracts and not evidence for a consumer-independent wrapper today.

### NBO-3 — Security, retention, and presentation remain consumer prerequisites

The lower proof cannot establish caller authentication, policy authority,
decision-receipt retention, confidentiality admission of carried values, safe
error translation, audit destination, or resource ownership. The proposal
mostly identifies these limits, including SP24. Their absence prevents a claim
of deployed application completeness. It does not require backend expansion
before a real consumer is named.

## 2. Frozen proposal verification

The proposal was read without modification. Every frozen control matched before
any audit output was written.

| Control | Expected | Independently observed | Result |
| --- | --- | --- | --- |
| Path | `docs/superpowers/proposals/2026-09-10-cv001-codex-lead-proposal.md` | Exact path | PASS |
| Lines | 661 | 661 | PASS |
| Bytes | 69,441 | 69,441 | PASS |
| SHA-256 | `7d1714076204bdff1169c6215370ae7207ed80beeb6b0aeb1ff8ba8993cbc6a2` | Same | PASS |
| Numbered sections | 14 | 14, numbered 1 through 14 | PASS |
| Ending marker | `END OF CV-001 CODEX LEAD PROPOSAL` | Exact final line | PASS |

No discrepancy-stop condition was reached.

## 3. Baseline and preservation verification

| Check | Independently observed | Result |
| --- | --- | --- |
| Branch | `main` | PASS |
| `HEAD` | `1b9b31dc56be7e7d4da120cac0dc1c9ba31f8675` | PASS |
| `origin/main` | `1b9b31dc56be7e7d4da120cac0dc1c9ba31f8675` | PASS |
| Head subject | `docs: close DI-001 as application composition` | PASS |
| FC-001 | Final owner acceptance says complete, owner accepted, adversarially hardened, and verified | PASS |
| CS-001 | Owner decision closes it without implementation as commissioning application policy | PASS |
| DI-001 | Owner decision cancels it as a backend milestone and retains bounded application-composition guidance | PASS |
| Authoritative records | 36 loaded records | PASS |
| Accepted revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` | PASS |
| Exact replay | Replaying the accepted record-ID tuple produced the same revision | PASS |
| Model-kernel exports | 236 ordered names, 236 unique | PASS |
| Export digest | `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` | PASS |
| FMA/FMW | `0/0` | PASS |
| FCD/FCW | `0/0` | PASS |
| ADRs | 22 accepted files, unique and contiguous from ADR-0001 through ADR-0022 | PASS |
| ADR-0023 | Absent, unallocated, and unreserved | PASS |

Protected records were unchanged:

| Protected material | Files | Recomputed SHA-256 |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| `var/raw_store` | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

Protected decision/report hashes also matched: FC acceptance
`1436b12aff7ad6b387a58bba0ea7d87386fffd14c151d5ad76b06384a7529ca8`,
FC final verification
`eb67c0830ac54c3caac9a8763afd0e84484edc8f7f900fd6391f137d5a9eec71`,
CS decision
`8557f2252c226b43dabc17ae4ffc5b8a529ac3d26999a456495e6b21c2ad33e3`,
DI decision
`ca5413a558ec5512c34845715fc1c63a8b403f31f0ccf5e505c8e2eb081bfaa0`,
and post-FC reconciliation
`9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5`.

## 4. Exact commissioning answer and sufficiency verdict

The exact question is answerable by a correctly implemented application using
existing public contracts:

> For this exact logical flow, participant port, context, governing criterion,
> and nominated measured-actual sample at an explicit receipt cutoff: is the
> evidence usable under the caller's explicit policy, which criterion governs
> the sample, and is that criterion satisfied?

This audit constructed that direct application join and obtained:

| World/policy | Evidence | Governing criterion | CN verdict | Final application result |
| --- | --- | --- | --- | --- |
| W60/P1 | Complete, attached, independently fingerprint-matched; receipt age 3,594 s within inclusive 3,600 s | A, upper bound 50 | `violated` | `policy_permits_use`; governing A violated |
| W40/P1 | Complete, attached, independently fingerprint-matched; receipt age 3,594 s within inclusive 3,600 s | A, upper bound 50 | `satisfied` | `policy_permits_use`; governing A satisfied |
| W60/P2 | Same valid lower evidence; 3,594 s exceeds 3,000 s | A | `violated` retained | `evidence_not_usable_under_policy` / `receipt_age_exceeded` |
| W40/P2 | Same valid lower evidence; 3,594 s exceeds 3,000 s | A | `satisfied` retained | `evidence_not_usable_under_policy` / `receipt_age_exceeded` |

Public-join sufficiency is therefore **yes for in-process application
composition** and **no for an already exposed application capability**. The
application code needed equality checks, exact integer-microsecond arithmetic,
policy gate ordering, and disposition mapping. It did not need private fields,
private derivation functions, raw payload access, direct ledger reads, or copies
of FM, FC, EA, alignment, VM, VS, ES, or CN algorithms.

## 5. Complete public entry-point map

The relevant supported entry points divide into production and replay. A caller
that already possesses complete roots needs only the replay/application rows.
Fresh production necessarily uses the explicitly injected stores/readers that
own acquisition; that I/O is not part of result validation.

| Layer | Public entry point | Required role |
| --- | --- | --- |
| Model acquisition | `ModelStore.load()` / `ModelStore.replay(record_ids)` | Load or replay one explicit reference-closed model membership. |
| Model material | `ModelQueryMaterial.loaded()` / `.record_at(index)` | Purely reconstruct carried model material and resolve exact indexed records. |
| Flow | `ModelQueries.flow(flow_anchor_id)` | Disclose exact flow registration. |
| Port | `ModelQueries.port(port_anchor_id)` | Disclose exact participant port registration and owner. |
| Flow declaration | `ModelQueries.flow_declaration(flow_anchor_id, context=...)` | Disclose the exact logical declaration and direction pins. |
| FM direct query | `ModelQueries.flow_measurement_association(flow, variable, port, context, orientation)` | Disclose FM declaration, effective-body groups, support, and refusals. |
| FM assertion | `ModelQueries.flow_measurement_assertion(record_id)` | Disclose the retained FMA witness and its lifecycle/body relation. |
| FC query | `ModelQueries.flow_operating_criterion(flow, variable, port, context, orientation)` | Select or refuse the governing criterion for the exact FM body. |
| Variable state | `ModelStateQueries.variable_state(variable, as_of=C, entity_anchor_id=..., source=...)` | Join loaded model, binding resolver, and temporal evidence at C. |
| Value compatibility | `ObservationCompatibilityQueries.variable_value_compatibility(...)` | Preserve value shape, attachment, and exact observation candidate. |
| Semantics | `SemanticCompatibilityQueries.variable_semantic_compatibility(...)` | Join model meaning, source-property interpretation, and value compatibility. |
| CN | `ConstraintEvaluationQueries.constraint_evaluation(constraint, as_of=C, entity_anchor_id=..., source=...)` | Evaluate each admitted semantic candidate against the exact declared predicate. |
| EA production | `EvidenceAssuranceQueries.select_operational_evidence(request)` | Select and close bounded source/temporal evidence, coverage, assurance, and provenance. |
| EA replay validation | `OperationalEvidenceSelectionResult.model_validate(...)` and `validate_operational_evidence_snapshot(snapshot, expected_fingerprint=...)` | Reconstruct the carried snapshot and compare an independent fingerprint without I/O. |
| Alignment | `align_operational_evidence_with_value_compatibility(OperationalEvidenceAlignmentRequest(...))` | Purely align E with N's carried VS result. |
| Owning result boundaries | `FlowMeasurement*Result.model_validate`, `FlowOperatingCriterionResult.model_validate`, `VariableStateResult.model_validate`, `VariableValueCompatibilityResult.model_validate`, `VariableSemanticCompatibilityResult.model_validate`, `ConstraintEvaluationResult.model_validate`, `OperationalEvidenceAlignmentResult.model_validate` | Rebuild and reject stale or forged derived lower content within each authority boundary. |

Fresh production additionally injects public `BindingStore`/`BindingResolver`,
`TemporalStore`/`TemporalQueries`, `InterpretationStore`/
`InterpretationResolver`, and a `Ds004OperationalEvidenceReader` such as
`FilesystemDs004OperationalEvidenceReader`. The accepted synthetic producer
uses test helpers to create its disposable worlds. Those helpers are not needed
to validate or compose already produced public results, and they are not a
production application API.

No `backend.commissioning_verification`, CS policy evaluator, commissioning CLI,
report generator, or HTTP route exists.

## 6. Join keys, required inputs, and authority boundaries

### Join keys

| Boundary | Exact key that must agree |
| --- | --- |
| Request to FC | Flow anchor, variable anchor, participant-port anchor, full typed context, and orientation. |
| F to FM | Retained FMA record and the exact FM effective body: five subject fields plus the six pinned FRG/VRG/PRG/FLD/VPA/VSM records; healthy current equal-body support may preserve a historical witness. |
| F to flow/port | Whole FRG, PRG, FLD, PCN, and PIF records selected by carried indices; names are not keys. |
| F to N | Whole CRG and VCN records, exact constraint anchor, target variable, semantic signature, predicate, and model revision. Same anchor with another VCN is not equal. |
| F/N to variable state | Exact variable registration and entity owner in F's complete material equal N's nested VM registrations and model revision. |
| N to candidate | Strict semantic-candidate index/path, exact candidate order, variable anchor, explicit source selector when used, and full carried occurrence. |
| All temporal results | N, ES, VS, VM, and E `as_of` equal the independent receipt cutoff C. |
| E to N/VS | Six-field consumer locator (`source_id`, `adapter_id`, `subject_identifier`, `extraction_route`, `item_key`, `json_pointer`), snapshot-bound endpoint closure, and the full occurrence including IDs, receipt/source times, run/attempt/provenance, value/type/unit, clock segment, change class, predecessor, and quality flags. |
| E to independent context | Exact scope, horizon, cutoff, selected occurrence, and independently retained snapshot fingerprint. An embedded replacement fingerprint is insufficient. |
| P to request | Full policy content, profile/version/authority, exact FM body and CRG/VCN target, age unit/limit/boundary, exact coverage window/rule, receipt cutoff, reuse semantics, and source-time rule. |
| Replay | Complete original F/N/E/P/X roots and revisions; no ambient latest membership, latest policy, current clock, or current store. |

### Required inputs

One complete F, one complete exact-criterion N, one complete E, and one
independently expected request/policy context are required. X must bind the
model revision and membership, exact subject tuple, retained FMA witness/body,
CRG/VCN, entity owner, nominated candidate index/path and full occurrence,
cutoff C, source scope/endpoint, expected EA fingerprint, carried binding and
interpretation revisions where relevant, and synthetic/real classification.

P must explicitly carry its schema/profile, label, version, authority reference,
target, maximum receipt age as canonical integer microseconds, inclusive or
exclusive boundary, required coverage window and exact EA completeness rule,
receipt cutoff, reuse rule, and `source_time_use=disclosure_only`. Authority is
established outside the pure comparison; possession of an authority token is
not proof. An optional decision timestamp never substitutes for C.

### Authoritative validation boundaries

Model material owns canonical records, closure, selected membership, lifecycle,
and FM/FC derivation. VM owns model/binding/temporal composition but does not
authenticate a ledger absent from its carried result. VS owns value-shape and
attachment comparison. ES owns declared model/source semantic compatibility.
CN owns numeric parsing, predicate boundaries, and satisfied/violated/
not-evaluated derivation. EA owns bounded selection, content fingerprint,
source/temporal parity, assurance, provenance, and attempt coverage. Alignment
owns only E-to-VS cutoff/scope/occurrence/fingerprint relations.

The application owns cross-root equality, independent expected commitments,
policy authority/applicability, integer receipt-age comparison, required-horizon
comparison, final gate order, disposition, retention, confidentiality admission,
and presentation. It must not recompute any lower semantic, lifecycle, evidence,
or predicate algorithm.

## 7. Refusal and indeterminate outcomes

The public join retains the following lower outcomes rather than collapsing them
into falsehood, staleness, or a green/red Boolean.

| Layer | Exact relevant outcomes |
| --- | --- |
| FM | Endpoint registration: `all_registered`, `flow_not_registered`, `variable_not_registered`, `port_not_registered`, `multiple_not_registered`; presence `not_declared`/`declared`; conclusion `not_evaluated`, `declared_direct_measurement_relevance`, `conflicted`, `inactive`; agreement includes one/corroborating healthy roots, same-root conflict, inactive roots, and cross-root effective-body disagreement. |
| FC | `not_declared`, `inactive`, `conflicted`, `disagreed`, `inapplicable`, `applicable`; reasons: `fc_not_declared`, `fc_inactive`, `fc_same_root_conflict`, `fc_cross_root_disagreement`, `fm_inactive`, `fm_same_root_conflict`, `fm_cross_root_disagreement`, `fm_body_not_current`, `vcn_conflicted`, `vcn_not_current`, `typed_support_not_current`, `typed_support_conflicted`, `typed_support_inactive`, `typed_support_unaligned`. |
| VM | Registered/unregistered model and requested entity; owner match/difference/unavailable; binding candidate absence/unknown/explicit selector; no observation before cutoff; zero/single/multiple/explicit selection; attachment `attached`, variable unregistered, anchor divergent, resolution mismatch/nonpositive, or `not_evaluated`. |
| VS/ES | Observation absent/unattached, evidence inconsistent, value shape unavailable/conflicted/not satisfied, model meaning or unit absent/conflicted, source interpretation absent/inapplicable/unknown/ambiguous/conflicted/retracted/inactive, quantity/role/unit mismatch, and explicit unit-lexeme disclosures. |
| CN | `satisfied`, `violated`, or `not_evaluated`; exact not-evaluated reasons: constraint absent/conflicted, observation absent/unattached, evidence not assessable, value-shape unavailable/non-numeric/not satisfied, numeric value absent/out of bounds, declared semantics incompatible, or constraint quantity/role/unit mismatch. |
| EA | `complete_within_declared_horizon`, `incomplete_within_declared_horizon`, or `refused`; refusal/incomplete issues retain unsupported/invalid/excessive material, source/temporal unavailable or changed, checksum/provenance/content/parity failure, extraction incomplete, occurrence absent/inconsistent, no observation, and incomplete coverage. Snapshot validation is self-consistent, fingerprint mismatch, or invalid. |
| Alignment | `aligned_with_complete_evidence`, `aligned_with_incomplete_evidence`, `not_aligned`, or `not_evaluated`; reasons: selection refused, fingerprint mismatch, no selected observation, cutoff/scope difference, consumer absence, occurrence mismatch/absence, or multiple matching candidates. |
| Application | `policy_permits_use`, `criterion_evaluation_unavailable`, `evidence_not_usable_under_policy`, `coverage_insufficient`, `evidence_selection_refused`, `applicability_unavailable`, `evidence_absent`, `input_or_revision_incoherent`, or `policy_inapplicable`, always with the reached lower axes retained. |

Structural misuse remains a typed exception rather than an engineering outcome,
including model query invalidity/result invalidity or limit exhaustion, EA
dependency/request/policy invalidity, and `ALIGNMENT_REQUEST_INVALID`. Lower
value-free errors are not automatically an application presentation contract.

## 8. Integrated-witness challenge

The accepted FC-only witness reproduced at exactly 14,677 bytes and SHA-256
`a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca`.
The accepted integrated witness reproduced at exactly 174,490 bytes and SHA-256
`1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e`.
The inspected producer remained 6,287 bytes and SHA-256
`b5a93888b468ede89da6ae9f9c72655e07de994f732fcb320e31ad1fd08ae18c`.

The accepted witness executable proves:

- exact flow `flo_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`, participant port
  `prt_11111111111111111111111111111111`, variable
  `var_11111111111111111111111111111111`, `lifecycle_view/as_designed`, and
  `aligned` orientation;
- retained FMA
  `fma_cd234041b6e1a98b65a33c61b7b742c463a348fcb92f1de912e88de2555cb2cb`;
- governing A VCN
  `vcn_70b5e146d682db6ca696a9165d0d4521c36ba4324b3d52f96c8a13bae13912cd`
  with inclusive upper bound 50;
- ungoverned B VCN
  `vcn_3caad214041adad24a48bac3f13767078022329de34e2f46161a745c11c0273e`
  with bound 80;
- exact cutoff `2026-08-07T21:00:00+00:00`, occurrence
  `79bcec2f4de12d6e67f657f2e1153637`, receipt
  `2026-08-07T20:00:06+00:00`, and value `60.1`;
- governing A `violated`, ungoverned B `satisfied`, and whole-record B
  substitution rejection;
- EA `complete_within_declared_horizon`, 3,594-second receipt age, exact
  provenance closure and evidence assurance;
- independently expected snapshot fingerprint
  `sha256:36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`
  matched by public snapshot validation/alignment;
- complete alignment, exact nominated candidate 0, and attachment;
- CN-only value-40 governing-A twin `satisfied` with unchanged FC; and
- no conclusion about physical flow, port observation, source authenticity,
  safety, health, or permission to operate.

It is a disposable test artifact, not a deployed application. After its temporary
producer builds the world, the protected consumer checks use public result
validation and public alignment. The temporary script and test helpers are
reproducibility aids, not required runtime dependencies.

The separately acquired W60 and W40 worlds were independently reproduced from
new response bytes through the source/projector/query stack. W60 had fingerprint
`sha256:37259b04c6b2d92794ec03b2054558accfed07894a4e9c3dfb0eaa328186cf80`
and serialized F/N/E sizes `17,634/33,263/19,803`. W40 had fingerprint
`sha256:e2b00eaf6d4e70421c3ca16b96a8093205bc18329cd33a96810c283e52ab468e`
and sizes `17,634/33,255/19,797`. Both were complete, attached, matched the
independent fingerprint, and retained the same applicable A designation. W60
violated A; W40 satisfied A. W40 closes the full-path satisfied witness gap; it
does not add capability.

The policy/disposition step remains documentation plus caller code. That is
RC-1, not an unreported property of the accepted witness.

## 9. Application-boundary alternatives

| Alternative | Concrete integrity or usability property it can provide | Audit decision |
| --- | --- | --- |
| 1. Direct application use of existing APIs | Actual answer in a concrete application; application-local independent commitments, authority, gate order, omission checks, retention, and presentation. It can be correct, as reproduced here, but each application owns the full composition. | Sufficient for one specified application; no backend change. |
| 2. Documentation-only orchestration guidance | Reviewable checklist for joins, gate order, refusal mapping, provenance, limits, and overclaim prevention. It cannot execute, enforce, authenticate, or retain a decision. | Retain this proposal as useful guidance; no separate milestone needed. |
| 3. Pure application request/result contract | One executable omission-resistant cross-root validator, deterministic gate order, stable disposition vocabulary, bounded carriage, and replay format. It does not authenticate users, choose policy authority, store receipts, or define deployment. | Defer until a concrete consumer and input/output compatibility need exist. |
| 4. Thin deterministic CLI/report generator | A runnable operator ingress, stable arguments/artifact/exit behavior, and human error presentation. | Defer until operator, delivery, classification, and retention needs are known. |
| 5. Reusable commissioning package | Shared semantics/versioning across multiple concrete consumers and one place to preserve refusal behavior. | No second consumer or cross-application drift has been shown; defer. |
| 6. HTTP API | Remote transport, authentication/authorization hook, request sizing, concurrency, latency, status mapping, and network audit integration. | Premature; no network consumer or security/deployment contract exists. |
| 7. Kernel or ledger additions | Durable engineering identity or authoritative model fact. The workflow needs neither; storing caller policy/disposition there would misclassify application judgment as model truth. | Reject. |

No wrapper is required for call-count convenience. A pure application contract
becomes justified when a concrete application needs one of the stated integrity
properties, particularly enforced omission resistance and stable replay, and its
requirements can be tested. The current absence of such a contract is a real
application exposure gap but premature backend packaging.

## 10. Unknown application requirements

| Requirement | Known now? | Consequence |
| --- | --- | --- |
| Ingress | No | No stable wire, file, command, or in-process request shape can be chosen. |
| Authentication/authorization | No | Authority-token presence cannot establish who may commission or see evidence. |
| Policy authority | Profile semantics are documented; actual authority and thresholds are not | No operational P may be selected or defaulted. |
| Policy version and retention | Required conceptually; repository/system of record unknown | Historical replay cannot be assigned to an application store. |
| Decision-receipt retention | Required if an application claims replay/audit; location and period unknown | No durable result identity or retention schema is justified. |
| Latency and capacity | Only exploratory lower/example sizes are known | No application admission budget or service objective can be frozen. |
| Error presentation | Lower reasons exist; audience/channel unknown | No final localization, redaction, status code, or remediation format can be selected. |
| User identity | No | No accountable human/service actor can be bound to P or a decision receipt. |
| Audit destination | No | No event, report, log, or external system is authorized. |
| Deployment boundary | No | CLI, library, local service, and HTTP service have materially different threat models. |

A stable application API designed now would encode assumptions about these
unknowns or remain so abstract that it adds only packaging. Defer it. Direct
application implementation is appropriate once the consumer supplies them.

## 11. Independent spill audit

All 26 proposal entries were inspected against live package ownership and
validation. “Prevented” means the existing lower architecture or the selected
no-runtime decision makes the spill impossible at present. “Application guard”
means a future consumer must enforce it; the repository does not currently
provide that application boundary.

| ID | Independent result | Existing prevention or missing boundary |
| --- | --- | --- |
| SP01 | Evidence usability must not become observation truth. | Lower EA/CN contracts separate evidence and evaluation; future display requires an application guard. |
| SP02 | Criterion satisfaction must not become system health. | CN is candidate/predicate bounded; health authority is absent and display must say so. |
| SP03 | Declared logical flow must not become physical occurrence. | FL/FM/FC carry declaration only and expose no occurrence result. Prevented. |
| SP04 | FMA port relevance must not become “observed at port.” | VM/EA preserve the source locator; port association remains model relevance. Future display guard required. |
| SP05 | Orientation must not become causality. | Orientation is a fixed FM literal with no causal semantics. Prevented. |
| SP06 | Disposition must not become safety/operate approval. | No safety, command, or operate field/authority exists. Future display and authorization guard required. |
| SP07 | CS policy must not enter `model_kernel`. | No code/import/record was added; caller owns P. Prevented. |
| SP08 | Commissioning policy must not enter EA/CN/FC/FM/temporal. | Live dependency direction remains unchanged. Prevented. |
| SP09 | Lower packages must not import the workflow or expose private workflow state. | No workflow package exists; direct composition imports public lower surfaces. Prevented. |
| SP10 | Application must not copy canonicalization/lifecycle/body derivation. | Public material/results rederive these. Direct audit code used equality and public lookups only. Prevented. |
| SP11 | Nested/cached green results must not be trusted. | Complete public root validation plus independent commitments rejects them; application must invoke all validators. |
| SP12 | Revision/identity/candidate/cutoff/witness must not weaken. | Lower roots expose exact fields; application must compare them all. Missing aggregate enforcement is RC-1/NBO-2. |
| SP13 | Conflicts/multiple matches must not be favorably selected. | FC and alignment expose exact unavailable/multiple outcomes. Application must preserve them. |
| SP14 | Derived workflow disposition must not become model truth. | No store/ledger/result identity exists. Prevented; application retention remains separate. |
| SP15 | Validation must not write source/temporal/model ledgers. | Owning validators/alignment are pure; disposable acquisition is separate. Prevented. |
| SP16 | Policy fingerprint must not become engineering identity/authority. | No such identity exists; full P and external authority remain necessary. Prevented. |
| SP17 | One nominated candidate must not become best-measurement selection. | All APIs require or preserve explicit candidate selection and perform no ranking. Prevented. |
| SP18 | The workflow must not expand into diagnosis/impact/planning. | No such result or algorithm exists. Prevented. |
| SP19 | Withholding must not become a maintenance/safety command. | No adapter command or recommendation result exists. Future presentation guard required. |
| SP20 | Synthetic examples must not become real printer knowledge. | Authoritative model remains without FM/FC records; classification/disclaimer is application-owned and unauthenticated. |
| SP21 | Visibility must not force an FMA/FCD demo append. | Counts remain zero; disposable worlds establish contract feasibility. Prevented. |
| SP22 | Predecessors/wiring/flow/condition must not be inferred or edited. | Protected inventories and memberships are unchanged. Prevented. |
| SP23 | Raw payloads must not be unnecessarily carried. | F/N/E proof roots carry accepted bounded metadata, not a second raw cache. Required `value_json` cannot be redacted while claiming the same proof. |
| SP24 | Paths, secrets, or confidential values must not leak. | Lower error text has safety checks, but lower validation does not certify all carried content for disclosure. A concrete application confidentiality/error boundary is missing. |
| SP25 | Hostile input must not cause unbounded replay. | FC/lower limits and hostile-object tests exist; aggregate application limits remain unknown and must be chosen by the consumer. |
| SP26 | Captured fingerprints must not become live authentication. | EA explicitly reports source bytes/store membership not rechecked; no signature/authority claim exists. Prevented by semantics and display guard. |

The 26 rows cover the named categories but do not create executable application
ownership. The following concrete application spills remain outside the live
architecture:

| Omitted/implicit spill | Present state | Required future boundary |
| --- | --- | --- |
| Application authentication | No ingress or user identity | Authenticate the actor and bind authorization to the exact request; do not treat a string token as proof. |
| Policy authority and retention | P is caller guidance only | Name the authority/system of record, immutable policy content/version, retention period, and historical lookup rules. |
| Result carriage/decision receipt | No aggregate result | If replay/audit is required, retain exact F/N/E/P/X and derived disposition without turning it into model truth. |
| Error translation | Lower reasons are typed; final presentation is not | Preserve lower codes, redact safely, distinguish structural refusal, evidence denial, and CN falsehood. |
| Resource ownership | No application store/service | Assign storage, lifecycle, capacity, concurrency, and cleanup to the concrete deployment. |
| Scope completeness | No commissioned application scope | Declare supported scope and report everything else unknown; never present a partial implementation as complete. |

These are real application-boundary requirements. Existing architecture prevents
kernel/lower-layer spill, while the lack of a consumer prevents honest claims
that these application risks have been solved.

## 12. Required adversarial cases and valid twins

| Case | Adversarial result | Valid twin |
| --- | --- | --- |
| 1. Governing A violated; ungoverned B satisfied | W60 yields A `violated` and B `satisfied`; whole CRG/VCN comparison rejects B as the governing result. | Original W60 A with complete matched evidence is usable under P1. A separately designated B in a new admitted model/request would be a different valid request. |
| 2. Governing A satisfied | Separately acquired W40 yields A `satisfied`, with its own occurrence, fingerprint, E, and alignment. | W60 under the same model/P1 is the valid violated twin. Mixing W60 E with W40 N is rejected. |
| 3. Receipt-age failure | W40/P2 retains satisfied A but yields `evidence_not_usable_under_policy` / `receipt_age_exceeded`. | The same coherent W40/P1 passes its independently authorized 3,600-second bound. |
| 4. Insufficient attempt coverage | Failed, quarantined, omitted, empty, or nonobserving in-horizon routes keep EA incomplete and final `coverage_insufficient`; a selected value alone cannot rescue it. | Fresh W60 with every captured required-horizon attempt observing the property is complete. |
| 5. Evidence-selection refusal | EA refusal has no snapshot; alignment is `not_evaluated/selection_refused`; age and coverage are unreached. | Valid W60 E carries one reconstructed snapshot and reaches alignment/policy. |
| 6. Multiple matching candidates | Public alignment returns `multiple_matching_candidates`, `multiple_matches`, and no index; the application withholds CN availability. | The explicit unique-selector candidate aligns at index 0. |
| 7. Absent or conflicted governing criterion | FC returns `not_declared/fc_not_declared`, same-root `conflicted`, or cross-root `disagreed`; no criterion verdict may be selected. | One admitted FCD, or corroborating independent equal-body roots, yields applicable A. |
| 8. Stale VCN or FM support | VCN successor yields `vcn_not_current`; changed FM/support can yield `fm_body_not_current` or typed-support reasons. | Explicitly renewed, reference-closed FMA/FCD and independently committed revision; a healthy equal-body current FMA can preserve an old witness only under FC's accepted rules. |
| 9. Source-effective time rescues receipt-age failure | Rejected: policy age is C minus `selected_received_at`; source wall/monotonic/unavailable markers remain disclosure only. | Same receipt proof with any admitted source-time form has the same age result; a genuinely later valid receipt is the valid recency twin. |
| 10. Byte-identical rereceipt | Dropping origin/run/seed closure or editing only `received_at` refuses. A valid rereceipt creates a distinct attempt/occurrence while payload/observation bytes may be reused. | Fully recaptured later receipt with complete closure and horizon can pass a two-second age limit without claiming a new physical measurement. |
| 11. Candidate/cutoff/policy/witness/VCN/flow/port/context/revision substitution | Any changed key against fixed X is structurally invalid, fingerprint-mismatched, not aligned, policy-inapplicable, or `input_or_revision_incoherent`; it cannot silently succeed. | Independently nominate/authorize the changed request and rederive all affected roots and commitments. |
| 12. Mixed lower-result revisions | N's model revision must equal F and its nested ES/VS/VM revision; E must align at the same C/occurrence. W60 E plus W40 N and historical/current mixtures reject. | F/N from one exact model and E/VS from one exact occurrence/cutoff with matching X. |
| 13. Policy failure presented as observation falsehood | Rejected: P2 denies usability while preserving the same observation and CN satisfied/violated result. | P1 may permit use of exactly that evidence; neither result authenticates physical truth. |
| 14. Declared flow presented as physical occurrence | Rejected: FRG/FLD/FM/FC carry declaration/relevance only. | “Declared logical flow and governing A for the nominated sample” with explicit occurrence exclusion. |
| 15. Synthetic evidence presented as real equipment knowledge | Rejected: W60/W40 have no realism authenticator and authoritative demo has no FMA/FCD. | Correctly labelled synthetic contract demonstration; real claims require separately authenticated evidence and authority. |
| 16. Direct application omits one required lower result | Nothing in one lower root detects that the application skipped another root. A claimed answer without F, N, E, P, or X is incomplete. | The reproduced direct application admitted all five inputs, revalidated every root, rederived L, and preserved the policy/CN axes. |
| 17. Wrapper weakens a lower refusal | Reject any wrapper that maps EA refusal, FC conflict, CN not-evaluated, or multiple matches to a Boolean, “stale,” or criterion violation. | A future wrapper that carries the exact lower code/reason and marks unreached gates not evaluated. |
| 18. Unknown application scope presented as complete | Rejected: no ingress, identity, policy authority, audit destination, deployment, or capacity is specified. | A concrete consumer declares its exact admitted scope and reports unsupported/omitted scope as unknown. |

Cases 1–3 and 16 were exercised through the full direct composition. The
accepted witness and new W60/W40 acquisition were reproduced. The 71-test focused
suite exercised FC reconstruction/conflict, EA complete/incomplete/refusal,
fingerprint integrity, alignment cutoff/scope/occurrence/multiplicity, hostile
input, and value-free error cases. Byte-identical rereceipt, mixed CN inputs, and
lower source/temporal cases were also inspected in their owning tests. Presentation,
authority, and unknown-scope cases are application obligations because no
application implementation exists; they are not falsely reported as executed CV
runtime tests.

## 13. Authoritative-fixture challenge

No authoritative append is necessary. Disposable worlds establish the relevant
integrity properties: canonical model closure, FM/FC lifecycle and governing
selection, exact CRG/VCN pinning, VM/VS/ES/CN composition, evidence acquisition,
EA assurance/coverage, independent fingerprint alignment, and valid
satisfied/violated twins. None of those properties depends on the demo model
being the authoritative subject of an invented commissioning declaration.

The authoritative demo's zero FMA/FMW and FCD/FCW counts mean only that the demo
model cannot currently answer the commissioning question for itself. Appending
synthetic declarations would make one example visible but would not authenticate
real equipment, choose operational policy, establish an application ingress, or
strengthen the public join. It could instead encourage SP20–SP22 overclaim.

An authoritative append would be necessary only for an owner-approved real model
decision whose integrity depends on preserving an actual FMA/FCD declaration and
authority in that ledger. No such decision is supplied. Endorse maximum append:
zero records.

## 14. Original-objective audit

| Objective | Architecture capable? | Tests demonstrate? | Application exposes? | CV disposition |
| --- | --- | --- | --- | --- |
| 1. What exists and how connected? | Yes for exact declared flow, port, variable, FM, and governing VCN. | Yes in disposable FC/W60/W40 worlds. | No commissioning application exists. | No new CV backend contribution. |
| 2. Current state of this system? | Partially: one nominated evidence sample and exact CN verdict can be disclosed as usable/withheld at C; not present physical state, continuity, or health. | Yes for W60/W40 and P1/P2 direct audit code. | No. RC-1 prevents calling this user-delivered capability. | Backend cancellation honest; application delivery deferred. |
| 3. Why might it behave this way? | No causal explanation; only refusal/policy explanation. | Lower reason paths are tested. | No. | No contribution. |
| 4. Next best measurement or test? | No. It can withhold one nominated path and an application may choose to refresh it. It does not rank or select another test. | Receipt/coverage cases demonstrate withholding only. | No. | No contribution; do not inflate. |
| 5. What changes would affect it? | Exact revision/pin comparisons disclose invalidation, but no physical impact propagation. | FC stale/conflict and mixed-revision cases are tested. | No. | No new CV capability. |
| 6. Smallest valid desired-state change? | No goals, actions, optimization, or control. | No. | No. | No contribution. |
| 7. Observed/calculated/inferred/assumed/unknown? | Partially: lower roots and documented application axes can keep these separate. | Yes for lower result/refusal separation; policy display is audit code/guidance. | No stable result/presentation exists. | Backend cancellation honest with RC-1; application result deferred. |

Cancellation is honest only with this three-way distinction. The architecture
knows how to compute the bounded answer, and tests/audit code demonstrate it. The
product repository does not currently present that answer to a user. This is
acceptable at the current backend frontier because no application consumer has
been specified; it is not evidence that user-facing delivery already exists.

## 15. Owner-decision adjudication

| Owner decision | Adjudication | Reason |
| --- | --- | --- |
| Cancel CV-001 | **Endorse with correction** | Cancel it as a backend/kernel/ledger/runtime-package milestone. Do not describe the absent application operation as already delivered. |
| Retain documentation-only orchestration guidance | **Endorse as written** | The proposal is useful safety guidance and is the only complete cross-layer join/policy/spill recipe. Retention need not become another milestone. |
| Stable application request/result | **Defer until a real application consumer is specified** | It could provide executable omission resistance, gate order, replay, and carriage, but its actual input/output and security requirements are unknown. |
| Authoritative fixture append | **Endorse as written** | Disposable integration proves the contracts; zero append. |
| Concrete application ingress prerequisite | **Endorse as written** | Required before selecting library/CLI/report/HTTP form or calling the result user-visible. |
| Policy authority and retention prerequisite | **Endorse as written** | Required before operational use; token presence and example thresholds are not authority. |
| Capacity and deployment prerequisite | **Endorse as written** | Exploratory limits/sizes do not define a production SLO or trust boundary. |
| Final CV-001 disposition | **Endorse with correction** | Backend work cancelled; application delivery deferred pending concrete ingress and authority; proposal retained as guidance. |

Final CV-001 disposition: **deferred pending concrete ingress and authority**,
with the proposed backend additions cancelled and the frozen proposal retained
as documentation-only application guidance. This is not a narrower implementation
milestone and allocates no successor package or ADR.

## 16. Verification, Git state, and audit-only boundary

Fresh focused verification ran the proposal's existing lower-test command:

```text
71 passed in 25.30s
```

The accepted witnesses and separate W60/W40 worlds used disposable temporary
directories only. The direct application-composition probe used public lower
validation and alignment plus caller-owned comparisons/arithmetic. It wrote no
repository code, test, fixture, ledger, model record, binding, interpretation,
source artifact, or generated demonstration.

ADR-0023 remains absent, unallocated, and unreserved. The branch and both refs
remain at the verified baseline. Before this report, Git status contained only
the frozen untracked proposal. After this report, the intended allowlist is
exactly the frozen proposal and this challenger audit, both untracked. The
proposal and every pre-existing file remain unchanged.

Whitespace is clean for this report and the working-tree diff. No branch,
implementation, test, authoritative append, ADR, commit, push, merge, rebase,
reset, checkout, cherry-pick, amend, or history operation was performed.

END OF CV-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
