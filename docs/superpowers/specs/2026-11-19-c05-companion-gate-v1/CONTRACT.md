# T1 carried-acquisition companion calibration gate, edition 1

Status: implemented source contract; runtime behavior and tests unvalidated. This is the small companion extension authorized by the Product Owner, not the historical broader owning-evaluator proposal.

## Governing boundary

The governing implementation plan is ../../reports/2026-11-19-c05-companion-gate-IMPLEMENTATION-PLAN.md, 100,780 bytes, SHA-256 3e504faa65e96e936c4e3b25e3c3a37d806cd2da4af1ef01121748c4eb673b99. It specifies the ledger and 16 acceptance cases. This contract fixes the implemented names and encoding and inherits its exact restricted scope.

Rule: ct.t1-calibration-primary-gate.v1. Guarantee: producer-checked-primary-calibration-gated-v1. Schema pack: applications/bounded_decision_workflow/t1_calibration_schemas.json, SHA-256 f7f8fce1b85fa6343a2116586039c6f62acb40f35f0babaa9f4c0ef04d0f3b5e (45,030 bytes). Its digest is compiled in the source-hashed gate loader; it is not embedded as a self-hash constant in the pack. Existing checked v4 and companion v3 packs and simulator rule retain their original bytes/semantics.

The guarantee is available only from a complete new companion package and its pinned producer M, handoff H and prior inputs. It applies to the one carried acquisition's exact reference-calibration premise for inherited-plan T1 reassessment. It does not apply to a detached owning B or direct checked command. Correction release is disabled, with no override flag or accepted-correction record. General historical/multiple-source adjudication, physical-source qualification and adoption are outside this edition.

## Encoding and three kinds

All records use UTF-8 canonical JSON: sorted keys, compact separators, no newline, duplicate keys, non-finite numbers or binary floating values. Exact decimals are strings; bounds are reduced rational objects. stdout adds a newline outside record identity. Typed references are {kind,sha256} over full raw canonical record bytes; opaque evidence preserves its original raw-byte identity and opacity.

The pack contains exactly ct.t1-calibration-gate-finding.v1, ct.t1-calibration-gate-outcome.v1 and ct.t1-calibration-gate-check.v1. All shapes are closed. Each carries schema/profile, rule_edition and schemas_sha256; outcome/check also carry the fixed guarantee. Profile is bdw.checked-temperature.v1. Finding cap 16,384 bytes; outcome cap 32,768; check cap 65,536. Ledger is the 16 ordered groups in the plan, at most 32 rows/128 operands. Existing source/ordinary-object/closure/build/applicability/result caps also apply; overflow refuses and never truncates.

Finding subjects bind producer manifest/receipt, J/G/E/X, W/C/O, R/A/H, model/plan/required claim, source captured policy, distinct assessment policy, simulator policy, producer build and actual checker build. Required claim core is independently derived. Source and assessment policy refs have separate ownership: J.captured_policy is not substituted for R.policy. A shared hash is allowed but not required.

Finding includes exact required/source scope and failed/checked instant, comparison operands (subject alias, JSON pointer and tagged normalized value), qualification, reasons/effect, declared and recomputed calibration Booleans and exact operands/bound, review/item refs, unchanged base applicability ref and synthetic/physical limitation constants. Compound values are retained by pointer plus canonical digest; source bodies remain reachable in the coupled packages. Nulls are missing values, not equality. Auxiliary metadata may be null where an independently complete typed target/unit graph establishes the needed link.

Outcome binds exact external M/J/E/G/H/R/A/prior-request/prior-authority pins, source/checker builds, inline finding, fixed member descriptors, actual delegation/result refs, conclusion and bounded deterministic trace. process_completion=completed describes the companion operation, not an owning hypothesis assessment. scope=carried_acquisition; correction_release=disabled. Evaluate has replay_of=null. Replay names the original outcome as a non-edge provenance annotation. This annotation is not recursive proof/authentication.

Check is the completion/verification/replay report: exact outcome subject, checker identity, performed checks, reproduced decision, limitations and published path/hash/length list. A check file is never accepted instead of recomputation of its subject.

## Admission and qualification

Order: safe bounded intake -> producer policy/build/prior verification and independent reconstruction/oracle -> exact H/R carriage -> complete ordinary owning request/authority/prior/execution/observation/review admission -> unchanged base applicability -> typed qualification/comparison -> restrictive gate -> either companion block or existing owning delegation -> final companion publication.

The shared preflight performs ordinary owning admission without hypothesis derivation or B publication. The old owner keeps derivation-before-applicability ordering on its own path. Invalid authority/review/closure/reconstruction refuses before a completed scientific block, even when beta is already false.

Qualify against full typed model/claim/bound/instrument/entity/variable/occurrence/raw/context/configuration/effective binding/interpretation/time joins. Existing fresh producer reconstruction re-runs the owning backend resolution; selected effective scopes are additionally checked against C's revalidated collections. O's indices select one occurrence; D's admitted fields and raw payload checksum must match it. No O ID/display name/prose-only join is sufficient. Independent receipt_values recomputes from J-pinned W/X/model/plan; a retained Boolean is not an oracle.

Required closed interval is [model.context.as_of,R.result.acquisition.ended]. Source support is closed J.window. The witness is D.admitted.received_at for the same admitted occurrence, whose finished_at is also contained. Identity/interpretation scopes use ingestion_received_at, half-open, covering the whole source window; unknown is distinct from known unbounded. Publication age, mtime or a monotonic source clock with unknown origin never selects a winner. A qualified failed point defeats the premise; a positive point supplies no interval continuity proof.

Classifications:
- qualified_match requires every necessary link established. False beta_in_closed_b_ref -> block_counterexample; true -> permission_to_delegate only.
- established_mismatch retains exact exclusion facts and all other unknowns. As the mandatory carried source, it leaves required_primary_match_missing -> block_required_correspondence.
- insufficient_information has no conclusive exclusion but at least one unresolved link -> block_required_correspondence.
- malformed, unavailable, corrupted or unreconstructible evidence is a native refusal, not a scientific contradiction.

Existing unrelated/stale ordinary items/reviews follow unchanged applicability exclusion/coverage rules. There is no optional second producer API. Substituted unrelated primary evidence normally refuses upstream; classifier controls do not claim native reachability. C05 item-local null metadata does not erase the complete independent producer graph.

Owning via_assertions arrays disclose history as well as their selected positive basis. The gate checks scopes against the revalidated collections, then requires an active, definitely in-scope assertion supporting the unique resolved target/body and covering the whole source window. Inactive/outside rows are retained but do not add a veto; a redundant same-target unknown does not defeat an independently complete positive basis. Without such a basis correspondence stays unresolved. Existing source admission, including its conservative scope rules, is unchanged.

Base declarations/reviews/opposition/conflict/uncertainty remain unchanged and retained. A qualified negative with support does not fabricate opposition. A positive producer never clears a base block. Ordinary request predecessors remain reachable; a same-primary revision with the same false predicate stays blocked. Proposed corrective prose/content has no release effect; unsupported structured corrective/history inputs refuse rather than being dropped.

## Packages and publication

Gate block exact member set:
- receipt/admission-closure.json: existing ct.closure.v1, full ordinary R/A/predecessor/prior/model/policy/item/review closure.
- receipt/base-applicability.json: unchanged ct.applicability.v1.
- receipt/build.json: actual ct.build.v1.
- workflow-receipt.json: new outcome; delegation not_run; null owning manifest/result; no fabricated hypotheses/B.

Delegation exact member set: ordinary nine-file B under bundle/ plus new workflow-receipt.json. The owner retains invocation/closure/derivation/applicability/result/trace/build/policy/manifest v1 semantics. The companion binds exact B manifest/result and compares closure/build/base applicability with preflight. B alone cannot prove this companion gate.

Members are ordered closure, base_applicability, checker_build and owning_manifest when delegated. Typed subjects and member hashes/lengths resolve to exact retained bytes. Unexpected/missing files, PARTIAL and no-B/B branch inconsistencies refuse.

Roots must be fresh, safe and disjoint from retained inputs and from other outputs/scratch. Publication uses exclusive immutable writes, PARTIAL, file/directory fsync, final temporary record and atomic rename, then marker removal and a final containing-directory fsync. Failure conservatively retains/restores PARTIAL and emitted bytes. A final record with PARTIAL is incomplete. A B surviving later companion failure has its original checked guarantee only. The protocol is not a cross-package atomic transaction; no retry repairs an existing root. stdout failure may coexist with an already durable package and must not erase it.

A completed contradiction/correspondence block exits 0 with blocked status and owning not_run. Integrity/admission/usage/resource/filesystem/internal failures retain native nonzero diagnostics and no invented completion. New comparison consistency codes are CALIBRATION_FINDING_MISMATCH, CALIBRATION_OUTCOME_MISMATCH and CALIBRATION_PACKAGE_MISMATCH, companion order 9/exit 3.

## Commands and conclusion projection

t1-reassessment-evaluate keeps its existing inputs and always applies this gate; it emits the new outcome/check schema. No opt-out or legacy-evaluate mode exists in the active route.

t1-workflow-verify accepts mutually exclusive --workflow-package (new no-B or delegated outcome) or --bundle (legacy F/B only). New failures never downgrade to old success. Legacy interpretation and guarantee remain unchanged.

t1-workflow-replay requires --workflow-package for a new outcome, the same ten full external pins and retained producer/handoff/prior inputs, and fresh output/scratch. It needs no new authority input because ordinary A is retained; no authority is issued.

New check forms require pins for workflow receipt, producer manifest, J/E/G, prior R/A, H and current R/A; paths for workflow/producer/handoff/prior plus output/scratch; optional diagnostic dir. Existing evaluate separately receives A/objects. Duplicate flags, malformed pins and unsupported flags refuse.

Conclusion projection preserves the exact owning disposition: applicability_blocked -> blocked; incomplete_assessment -> unresolved; model_prediction_mismatch -> no_compatible_conclusion; one_compatible/multiple_compatible -> conditional for conditional_use_with_unresolved_conditions, or permitted_under_declared_conditions for use_permitted. Base blocked must agree with owning applicability_blocked. Unknown/inconsistent combinations refuse. No status is physical truth or adoption. The explanation exposes exact claim/bias/bound/witness/source pointers, retained reviews and whether owning assessment ran.

## Verification/replay

New verification checks canonical edition/pack/pin/branch/member integrity, recovers the complete ordinary closure/A, and reruns source reconstruction, H joins and owning preflight. It independently regenerates base applicability, claim/scope, finding, gate, conclusion and trace. It compares all committed outcome/member data, never a saved report flag. A no-B block verifies successfully as a completed block with owning not_run.

Delegated verification also uses unchanged owning verify plus full owning replay computation to compare complete result/trace. Old verify's weaker downstream promise remains explicitly unchanged. The prospective replay B remains call-local/in-memory during verification and is not published as an assessment.

Replay first verifies original, then publishes a fresh no-B block or the existing owning replay B plus companion root. Reuse only immutable call-local computation. Scientific finding/base/closure/result/trace/reasons remain equal; invocation/manifest metadata, operation/replay_of and new paths may change. No acquisition, correction selection, authority issuance or general historical traversal occurs.

Actual build equality, source/checker policy lists and prior identity constraints are unchanged. Changed code must use its real new build, not saved B-old bytes. Native fixtures need fresh coherent checked prior/policies/J/E/G/M/D/O/R/A/H bindings after source freeze. Historical evidence remains under its original semantics; old executable feasibility is required only for an operation actually needing it. No historical dispatch/new provider is introduced.

## Acceptance attribution

The implementation receipt maps C01–C16 to tests and records static review/preservation. All tests, imports, syntax and runtime behavior remain unvalidated until separately authorized execution. Injected component providers are not native evidence. Native tests are opt-in, consume separately prepared real-current-build inputs and retain finite command evidence. Historical C05, session 70642, failed attempts/authorities, accepted temperature trial and R1/L1 keep their original attribution. L2/VM/COOMET remain frozen/parked.

END C05 COMPANION GATE CONTRACT
