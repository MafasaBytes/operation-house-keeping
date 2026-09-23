# Slice 5 delivery-contract resolution and repair evidence

The approved artifacts already specify the command carriage. **This was an implementation omission, not a missing semantic contract. No amendment or additional CLI arguments are needed.** This report supersedes the remaining-contract-gap diagnosis in the historical final repair report; that report and the original completion/review bytes remain unchanged. Slice 5 acceptance remains withheld pending owner review of this repair.

Starting administrative HEAD was `bc022e61fb7cdf7f726a96c5c078eb826e47e44e`; the previously reported tested implementation resolves to `671f4f2b542f1f8d300dcfbd9e82e32e3783b62c`. The historical final report still hashes to `b966667978a3020a4e7fada61f6717f8e3bc0375f595c32a37e7719aab41636d`. The initial inventory contains **2,429** nonignored regular files, recorded individually in the evidence directory; its exact inventory SHA-256 is `b875a536e36b0afa987dda9cc4a6ac4254a94f3e3de64ffa16ca641c7e114bc7`.

The package, manifest and recovery commitments remain respectively `a6e48ea447444e4f7c12993d9567905978c2a0c8972414e0ac421df47cd2217f`, `18ed716ab327944f700b8e00b30235512a9ea6d5b41f49e87ab88b343680e2ea`, and `ecfe3f62d796a21edc5509419206aebb68d46d8d3f10736d6708c412110a8dac`. The full command/invocation/closure contracts were read. The local `CONTRACTS.md`, semantic candidate, catalog, policy and implementation plan were also compared byte-for-byte with their approved ZIP members. They match. `CONTRACTS.md` hashes to `2e802d1a04f570378c83963d21f7979415b061bc7f68794024a2c9fc9231fa24`.

## Existing normative field mapping

References below are to [the frozen candidate](2026-09-19-next-measurement-preparation/frozen/semantic-candidate.md) and [the packaged contracts](2026-09-19-next-measurement-preparation/CONTRACTS.md).

| Input / destination | Existing clause and exact carriage |
| --- | --- |
| `--invocation FILE` | Candidate §4 I: `request, selection, adoption, build_identity, resource_policy`, plus the common header. Q/A/T are typed references; the last two fields pin fixed-role witness bytes. |
| Nominated candidates | Candidate §3 Q: `hypotheses` and `measurements` are the entire nominated sets. `support` explicitly nominates S objects; `evidence, context, policy, predecessor` establish their shared scenario and lineage. Directory contents never nominate candidates. |
| Public material | Candidate §3 E: `snapshot` is the complete public `StateClassificationResult`; `question` carries `state_anchor_id, assertion_context, as_of, declared_state_label`; `binding` carries the three indices, three anchors and three expected token references. `token_roles` carries `quantity, observation_role, unit, basis`. The paragraph immediately after the object table expressly reuses admission semantics, **not a thermal request wrapper**. There is no extra public-request file to discover. |
| Prediction support | Candidate §3 S: exact `hypothesis, procedure, decoder, evidence, context`; declared `origin, coverage, permits, excludes, uncertainty, qualification, basis, exclusion_basis, provenance`. S membership comes only from Q. P pins `decoder, method, method_edition, conditions` and its context/E. |
| Authorities | Candidate §4: A/D/T permission joins are separate from S qualification and K ranking policy. Packaged command clause requires an external `--authority-pin` equal to `I.selection.sha256`. Q absence from D is assessed denial, not implicit pruning. |
| Object files / closure | Packaged delivery clause: `<sha256>.<kind>`, required filenames only, no directory enumeration/fallback. Candidate §4A follows all required typed references, every D member, every Q ancestor through revision 1 and all basis bytes. Opaque basis/public custody strings do not generate edges. |
| Retention / replay | Packaged delivery clause: seven fixed files; `closure.json` contains `invocation, authority_pin, limits_override, members`, with sorted typed references and exact base64 bytes. Build/policy external copies equal their closure copies. Replay reconstructs and recomputes from this closure in the matching executable/environment. |

The production entry point is `python -m applications.bounded_decision_workflow`, with exactly the three approved measurement operations: evaluate with the four required arguments and optional `--limits`; verify with `--bundle`; replay with `--bundle`, `--output-dir` and optional `--limits`. Repeated/abbreviated/unknown flags and caller matrix/result/trace arguments refuse. The earlier short-form storage CLI and caller-matrix delivery API are retired.

## Implemented boundary and evidence

The maintained application now captures exact required files through the existing descriptor-relative, no-follow, regular-file, supported-filesystem primitives. It checks stable capture metadata, uses captured bytes thereafter, validates closed typed joins and complete ancestry, reconstructs public evidence through the owning validator and maintained observed-value checks, applies permission/applicability gates, qualifies all nominated support, and constructs the minimax input itself. The supplied-support mapper and minimax helper are reused; complete-envelope complement support and lexicographic survivor ordering were repaired. Positive-only support does not gain exclusions.

A real `nm.build.v1` is generated from the clean executable checkpoint, tracked maintained Python source/lock manifest, actual interpreter/platform and installed distribution artifact digests. The supplied witness must equal this generated witness, not merely assert an executable status. The fixed approved policy digest is enforced. Prepared witnesses refuse. This establishes local executable compatibility, not authentication or empirical validity.

Publication reserves bounded output, refuses collisions, uses the maintained exclusive writer and writes the manifest last. Failed publication leaves an incomplete directory. Verify checks commitments, profiles, complete recoverable closure and build/policy compatibility without selecting a measurement. Replay independently reconstructs public inputs, re-admits authority, requalifies support and recomputes minimax/result/trace; fresh physical evidence goes in the new manifest. No caller-supplied computation participates.

| Obligation | Concrete evidence in `tests/measurement_profile/test_delivery_contract_mapping.py` and retained logs |
| --- | --- |
| Real semantic delivery | P carries the real 60.1 public snapshot and all H/P/O/S/K/Q/D/A/I/basis bytes. CLI result matches the frozen P semantic fields after invocation rebinding; scores are 1/2 and T2's repeated two-survivor branches remain repeated. |
| Whole-set withholding / admission separation | U, X-conflict-missing, G-denied and A-false complete with their distinct dispositions, null ranking and both procedure identities. Every resulting bundle replays. Denial has no downstream assessment/mapping/ranking work. |
| Independent replay | A rehashed forged score passes stored-byte verification but fails semantic replay. Original input paths are moved before replay. Separately, the retained P evidence copy was recovered to `/tmp/nm-slice5-recovery-Bk8qc5`; verify/replay ran from that isolated working directory with no objects-directory argument, and result/trace bytes match. |
| Exact joins / closure / witnesses | Rehashed stale procedure support, missing historical basis, wrong external pin, substituted executable checkpoint and policy, nonexecutable prepared witness and forbidden harness fields refuse. |
| Filesystem / publication | Symlink input/parent, FIFO, replacement after capture, collision and incomplete bundle controls; unreferenced hostile object-directory material is ignored. A trusted test-only manifest-write fault leaves six payload files without a manifest, verifies as incomplete and cannot be resumed/overwritten. A fresh valid twin succeeds. No fault callback or bypass is exposed by the production command. |
| Resource/history | Complete four-revision shared ancestry and standalone replay; fifth revision refuses. Public-input exact unique-object limit versus one less, history 4 versus tightened 3, and actual contextual edge work exceeding 62 at attempted 63. Limits were not increased. |
| Compatibility | Fresh Slice 1–5 tests, clean thermal replay and governed command regressions; broader thermal/governed/retention regression evidence also retained. No backend, dependency, thermal/governed schema or ledger changes. |

Red evidence covers the missing command path, unbound caller-matrix interface, rehashed foreign-result verification, missing contextual edge-budget charge, incomplete-bundle exit classification and malformed field-type exceptions. A test import defect was also corrected. These are ordinary implementation/test repairs, not semantic amendments. Historical source/tests remain recoverable from Git; historical reports remain byte-identical. Raw red pytest logs deliberately preserve their trailing spaces, so the aggregate documentation whitespace check reports those log lines; implementation, report and structured evidence checks are clean.

The exact final tested implementation/test HEAD is **`d9350f87a918dc31466b31a682afb3f27ff7fe56`**: **58 passed** in the final bounded selection. At `bfa224716851991e5aa6f322d155135a742ddc0f`, the broader selection passed **211**, with **1 skipped** because no isolated unsupported output parent was nominated. Intermediate 54- and 55-test green runs and all red logs are retained. The documentation-only successor containing this report is the administrative reporting HEAD, not a newly tested executable or an acceptance commit; its exact hash is returned in the receipt.

## Actual measurements and limits

Final tests ran with the provisioned CPython 3.13.11 environment, keeping inputs/results on ext4 at `/tmp/nm-slice5-final-Nj7rj9`. [Measurements and per-bundle provenance](2026-09-23-next-measurement-slice5-delivery-contract-resolution-evidence/measurements.json) distinguish deterministic graph requirements from observed I/O. Three complete exact-byte example bundles (P, U, four-revision history) are retained in the evidence directory for recovery; repository copies must be recovered onto a supported runtime filesystem before replay.

| Measured corpus quantity | Maximum | Unchanged approved ceiling |
| --- | ---: | ---: |
| Required unique objects / contexts / complete chain | 22 / 4 / 4 | 128 / 8 / 4 |
| Captured exact object bytes | 134,403 | 1,048,576 |
| Closure / build / result / trace bytes | 182,766 / 26,165 / 11,671 / 26,068 | 524,288 / 65,536 / 65,536 / 131,072 |
| Complete seven-file bundle bytes | 248,061 | 1,048,576 |
| Observed active depth / scoped expansions | 7 / 56 | 32 / 1,024 |
| Observed edge visits / contextual scan bytes / public reconstruction nodes | 315 / 1,782,464 / 10,716 | 4,096 / 16,777,216 / 131,072 |

The last two rows come from [read-only observations of actual Work objects](2026-09-23-next-measurement-slice5-delivery-contract-resolution-evidence/observed-work.json), not preparation estimates. P performs 62 captured reference occurrences plus 55 contextual edge checks, one public reconstruction, ten condition assessments, four hypothesis checks, eight cell mappings and four ranking branches. Four-revision history performs four public reconstructions but only the current request's eight cell mappings. Denial performs its required public reconstructions and zero condition/hypothesis/support/ranking assessments. The observer is retained test-only profiling code; it changes no input, function, digest or computed result and is not independent-review evidence.

Unprofiled/fault-harness corpus manifests record at most 47,886,308 explicitly instrumented read bytes (including executable/dependency hashing), 2,258 read calls, 2.636 seconds elapsed before manifest publication and 104,116,224 bytes process peak RSS. RSS includes process baseline/harness overhead. Manifest counters expressly stop **before the manifest write**: six payload write calls, up to 247,087 bytes. Complete seven-file retained bytes are separately measured, including the manifest. These counters are not a claim to measure all kernel/interpreter metadata I/O, crash durability, cold-cache capacity or all supported-filesystem fault paths. Corpus maxima are not general capacity guarantees. Slice 6 qualification remains unexecuted.

Expected ranking is the frozen hand-derived semantics, checked against frozen P fields and separate assertions; production imports no frozen expected output. The preparation oracle, tests and resource observer share authorship/assumptions. None is independent adversarial reviewer endorsement or empirical prediction validation.

## Preservation and owner gate

The initial inventory comparison found no missing files and only authorized application/test changes. Original completion and delivery-review report hashes remain `2d0e90a4592c4845d107fbfad22a0f155e60b3cd72d7871c28662614acab84ae` and `24eef24c8c704a60006e18308a1c1372fbddc0b6a7846add35fa2ac7496f2996`. Frozen package/oracle bytes and existing approved runtime locations were not modified. Default executor Git metadata access was freshly read-only; a unique probe succeeded and was removed through the normal product approval boundary. No permissions, ownership, mounts, security settings, locks or history were altered to obtain access.

No new owner semantic decision is required for carriage. The owner gate is review and acceptance of this repaired Slice 5 implementation and its exact executable-bound evidence; the old completion claim remains superseded and unaccepted. Supplied conditional predictions, local-attestation limits, manual unresolved C and whole-nominated-set withholding remain in force. Independent adversarial review, Slice 6 qualification and the full 142-command proof remain separately gated. IN-001 and CI-001 remain open and unselected.
