# Reassessment Slice 1 completion evidence

**Slice 1 — Captured contracts, closure and executable identity** is implemented;
owner acceptance remains pending. Tested implementation:
`822d9f82326f0d960ed334ff275cef69e7de6f66`. Separate approval/authorization commit:
`7a83f1226eae547d3faadbd7c8e8c368271938ab`. The administrative completion HEAD is
the commit containing this report, identified separately in the delivery receipt.
Starting checkpoint was `15bd9dcb1559898944149cab0ec78b962019ab50`, matching the
package authority, on local `main`. No remote operation was performed.

The [approval record](2026-09-23-reassessment-package-approval-slice1-authorization.md)
records all five verified owner commitments. The exact committed package retains
the governing candidate, v2 amendment, policy, plan and transitive authority.
Isolated static recovery verified 2,030 payload members, 72 cases in 12 groups,
32,845,071 payload bytes and all required original material. This is recovery,
not execution of the 180-command proof. No frozen commitment was corrected.

## Implemented boundary

New application modules `reassessment_contracts.py`, `reassessment_build.py` and
`reassessment_capture.py` provide closed v2 parsing, exact typed references,
nomination/identity checks, complete required ancestry, fixed prior reconstruction,
bounded safe capture and actual executable binding. The Python entry point is
`capture(invocation_file, objects_dir, authority_pin, limits=None)`; it has no
caller-supplied build, computation callback or bypass option. Unreferenced files
cannot supply nominations or extend the captured closure.

The producer binds actual clean source, interpreter, dependency artifacts, approved
contract and policy. A prepared witness or merely well-shaped replacement fails.
Historical selection-build bytes remain historical material, not current executable
authority. Capture reserves reconstruction before allocating it, validates the
original manifest and seven required roles, and preserves original bytes exactly.
Sharing does not remove repeated validation charges. Four existing measurement
helpers gained work instrumentation; their contracts and policies did not change.

Observation containment, E0/E1 public admission, permission/baseline decisions and
chronology consistency remain Slice 2; qualification and full-envelope conclusions
remain Slice 3; reassessment commands, publication and semantic replay remain
Slice 4; full qualification/release remains Slice 5. In particular, capturing an
inconsistent uncertainty specimen does not admit it. No result or trace is computed
from prepared expected outputs, and no new reassessment bundle is published here.

## Obligations and executable evidence

All names below refer to `tests/reassessment_profile/test_capture.py`. The retained
logs and patch permit inspection of assertions rather than reliance on counts.

| Obligation | Tests and established boundary |
| --- | --- |
| Exact prior recovery, manifest and role checks | `exact_historical_recovery_and_sharing`, `rehashed_descriptor_attacks`, `original_recorded_work_limit_is_not_erased_by_sharing`; seven original files verified by bytes, size and digest |
| Complete ancestry and limits | `frozen_structural_boundaries`, `nearest_valid_boundaries`, `complete_required_material_fits`: four/five revisions, eight/nine contexts, 128/129 objects, valid large closure |
| Identity and nomination | `ancestor_identity_mismatch_and_coherent_twin`, `owning_nomination_integrity`, `case_sensitive_identity_and_construction_permutation`; exact duplicates, different revisions, semantic substitutions and coherent twins |
| Typed and closed input | `rehashed_closed_shape_attacks`, `typed_reference_rejects_rehashed_cross_profile`, `required_observation_reference_cannot_be_null`, `production_root_dispatch_precedes_typed_closure` |
| Cycles versus sharing | `public_bytes_hash_precedes_cycle_claim` establishes public digest/missing-reference precedence; `internal_actual_traversal_cycles_and_diamond` exercises actual traversal using explicitly synthetic internal graphs. No public SHA-consistent cycle admission is claimed |
| Numerical and JSON guards | `original_decoder_and_rational_guards`, `recovery_valid_large_and_numerical_twins`, `interval_endpoint_digit_boundary_without_observation_admission`, `canonical_and_token_preallocation_guards`; exact parsing, not observation interpretation |
| Reservation and resource refusal | `real_graph_measured_demand_and_one_below` covers twelve dimensions; `internal_unchanged_guard_at_ceiling_and_plus_one` covers 21 counter dimensions internally; `serialization_reserves_before_base64`, `prior_result_limit_precedes_role_parse`, `prior_aggregate_reserved_before_reconstruction`, `required_role_nodes_reserved_before_json_allocation`, `historical_policy_does_not_replace_outer_diagnostic_ceiling` |
| Actual build/policy/authority | `production_capture_actual_build_exact_prior_and_measurements`, `production_build_policy_and_external_pin`; real producer and substituted/prepared/policy/pin adverse twins |
| Safe filesystem capture | `production_file_admission`, `invocation_replacement`, `directory_replacement`, `unreferenced_files_never_supply_or_expand_nomination`, `root_capture_limit_precedes_build_work`: ext4, no-follow regular-file reads, containment, descriptor/path race checks and bounded reads |
| Actual repeated work | `hash_work_includes_repeated_integrity_checks`, `json_work_includes_repeated_role_and_header_parsing`, `production_build_hash_accounting_matches_actual_calls`; independently instrumented call counts cross-check runtime counters |
| Scope boundary | `no_observation_or_support_work_in_slice_one`; UTC grammar twins validate spellings without proving chronology or exposure |

Frozen `P10-rational129` places the large number in public observation material;
its numerical admission belongs to Slice 2. Slice 1 endpoint tests independently
exercise the applicable 128/129-digit boundary. Internal counter probes are not
evidence that all public maximum-sized inputs fit simultaneously. Test/oracle
derivation and cross-checks are same-author, not independent-reviewer evidence.

## Red/fixed history and verification

The first preimplementation test failed collection with the missing
`reassessment_capture` module (exit 2); its tool output is transcribed in evidence
notes, not misrepresented as a retained raw log. Subsequent raw red/fixed logs
are archived. Initial implementation was `f61c9685acaabcb63fdb1a4f1fce83be04ba3708`.

| Repair | Evidence and resolution |
| --- | --- |
| `620e275c0d88e990ac10a4841986151f3834f968` | `precedence-red.log`: phase-2 prior integrity checks now precede phase-3 nomination checks |
| `eee239e4679aec229c8640b459123f46228190e2` | `null-reference-red.log`, `utc-red.log`: required reference and permitted UTC grammar |
| `90e93bd879fa90fec149af714d91f6c378c8d51b` | `hash-accounting-red.log`, `reservation-red.log`: repeated actual hashing counted and role size reserved before parsing |
| `11dc614a050150497217016760ca9ca7fd00a026` | `actual-accounting.log`: corrected test expectation for maintained cap-plus-one read probe (two physical bytes at cap one), without changing policy |
| `822d9f82326f0d960ed334ff275cef69e7de6f66` | `aggregate-context-red.log`, `role-nodes-red.log`, `root-dispatch-red.log`: preallocation aggregate/node reservation, original outer diagnostic ceiling preserved, profile dispatch precedence |

Final clean tested HEAD `822d9f8`: **119 passed**, zero skips/failures, 83.61 seconds:
108 capture tests, two selector delivery/build-substitution checks, thermal exact
replay, governed CLI checks and the exact unsupported-output-parent test. Exact
argv, HEAD and output are in `release-command.json` and `release-tests.log`.

At `11dc614`: **217 passed**, zero skips/failures, 532.19 seconds: then-current
capture tests, the entire measurement-profile regression selection and those
legacy gates. The subsequent changes touched only reassessment modules/tests;
the shared measurement instrumentation was unchanged. This is reused earlier-HEAD
evidence, not a claim that 217 tests ran at the final HEAD.

At `620e275`: **968 passed, one skipped**, 1,160.13 seconds: then-current capture,
measurement profile and complete bounded-workflow application tests, including
clean-root/archive delivery. The skip was precisely
`test_s5_retention_recovery.py::test_symlink_parent_and_unsupported_output_parent`,
reason “nominate an isolated BDW_UNSUPPORTED_OUTPUT_PARENT”. That same test passed
in later selections including final 119, using a newly nominated isolated 9p
parent. This does not establish support for publication on 9p. No full repository
suite or reassessment full proof ran.

Verification used the existing provisioned CPython 3.13.11 environment; no
dependency acquisition occurred. New runtime data used isolated ext4 `/tmp`
locations, with the adverse unsupported-parent check separately identified.

## Measured capacity and recovery

Final actual build witness: **26,809 bytes**, SHA-256
`03b920e96c72074fb412879f7ad402ae9e4a8d1be2e89d944f2bce59c2d5a99e`.
It binds 167 source/lock entries, ten distributions and 652 artifacts. Producer
work: 47,685,128 bytes read in 2,205 operations, 47,794,933 hash-input bytes and
26,656 JSON-decoding bytes. This is current evidence, not a future fixed size.
The independent 65,536-byte component ceiling does not guarantee aggregate fit.

| Final public capture | P8-before | P7-newbaseline |
| --- | ---: | ---: |
| Unique objects / contexts / maximum revision | 32 / 2 / 1 | 45 / 4 / 2 |
| Captured payload bytes | 281,098 | 353,845 |
| Serialized closure bytes | 379,820 | 478,768 |
| Reference occurrences / traversal edges | 451 / 859 | 221 / 749 |
| Scoped expansions / context-scan bytes | 114 / 3,503,409 | 154 / 3,590,546 |
| JSON nodes / decoded input bytes | 8,912 / 868,570 | 11,115 / 698,303 |
| Hash input bytes, excluding build producer | 725,543 | 407,871 |
| Payload read operations / writes | 93 / 0 | 126 / 0 |
| Elapsed seconds / process peak RSS bytes | 1.681 / 97,570,816 | 1.701 / 99,463,168 |

P8 recovers all seven historical files, **232,849 bytes**; original reconstructed
input is 129,617 bytes. Base64 encoding charges 410,715 input and 547,660 output
bytes. P7-newbaseline has no supplied prior descriptor; it is not claimed as a
second recovery of that prior bundle. Build work above is separately charged.

Static rebinding of all 51 prepared completed cases to the actual executable
found maximum closure **478,768 / 524,288 bytes**. Conservative complete seven-file
reserve is **720,020 bytes**, including actual invocation, closure, build, policy
and full result/trace/manifest allowances (65,536 + 131,072 + 16,384). All 51 fit.
This is static carriage/reserve arithmetic, not produced reassessment results or
general runtime capacity. No limit was increased; overflow refuses without
truncation, and complete ancestry beyond revision four remains unsupported.

Standalone structural recovery from captured P8 closure into a fresh ext4
directory succeeded through public capture with the actual executable, reproduced
the identical closure and seven exact original files, without supplying the
original directory. It establishes structural recapture, not later semantic replay.

Retained regular files under 277 test manifest directories across five isolated
run roots total **64,965,220 bytes**, including malformed controls, below 67,108,864.
This conservative inventory excludes source/dependency checkout copies and prepared
archives, which are not result bundles; it is not a filesystem-wide usage claim.
No reassessment result bundle was published.

## Recoverable evidence, preservation and remaining gate

The [evidence archive](2026-09-23-reassessment-slice1-evidence.zip), SHA-256
`728867a684e5292ab5d891197551b7431338c767a99ae75a0d3766aa0519e531`,
contains an entry manifest, raw logs, exact commands/HEADs, implementation patch,
actual build and captured closure bytes, measurements, standalone recovery receipt,
starting inventory and preservation checks. Its manifest covers each other entry.
This accompanies the exact committed approved package; neither hashes alone nor
temporary locations are the only recovery source.

Starting inventory was **4,756 regular tracked/untracked files**, including **3,502
untracked paths**. All original untracked bytes remain. Four existing application
source files changed intentionally for metering; all other 4,752 starting files
remain byte-identical, with none missing. Three original untracked authority files
became tracked in the explicit approval commit, leaving **3,499** unrelated untracked
paths. Historical reports, original failures, frozen oracle/package bytes, backend,
dependencies, ledger and existing maintained runtime results were not changed.
This inventory covers Git-enumerated regular files, not every ignored/system file.

Fresh sandbox Git metadata access returned read-only; ordinary product-approved
Git access succeeded. No permission, ownership, security, mount or lock workaround
was used. Only explicit authorized files were staged. No cleanup, remote operation,
history rewrite, ADR allocation or successor work occurred.

No known Slice 1 implementation defect remains. Later admission and interpretation
must retain exact containment, model-relative conclusions, exposure limitations and
manual adoption. Neither byte integrity nor retained relationships prove prior
knowledge. The unresolved historical review-digest discrepancy is unchanged; C
remains unresolved and IN-001/CI-001 remain open and unselected. Broader filesystem,
durability, complete command/replay and 180-command proof obligations remain with
their planned slices. Owner acceptance of this slice is the next gate.

END OF REASSESSMENT SLICE 1 COMPLETION REPORT.
