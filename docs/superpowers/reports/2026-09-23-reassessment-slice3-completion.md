# Reassessment Slice 3 completion evidence

**Slice 3 — Full-envelope qualification and derived reporting** is implemented;
owner acceptance remains pending. Tested implementation:
`433077d717719921d89fe5f882c83bf93f55c18e`. The administrative completion HEAD is
the commit containing this report, identified separately in the delivery receipt.

Slice 2 was accepted separately in
`eeeda1e1dd05fe5eda4500558de9309a05f15b55`, at implementation
`dfb34f30cca10c2d90eb69e92bf3e529d580bbd0`. Starting administrative HEAD was
`e58c5ddaa65a2ee10faab3d62f3d9a572b9bd509`, on local main. Slice 1 acceptance
`75666d0fd5c44c9c3996654743c3876d28eca0f4` remains in the authority chain.

The complete [Slice 2 report](2026-09-23-reassessment-slice2-completion.md) was read
and remains unchanged at SHA-256
`29d0235d16890071b59d26af96f2c4194a9870977efa6e4dff1d997a78403be8`.
Its retained manifest, exact 278-pass command/log and standalone recovery/admission
were verified without rerunning tests merely for acceptance. Exact joins,
containment, independent permission and frozen baseline are accepted behavior;
chronology remains declared and unverified, not authenticated custody. The separate
[acceptance record](2026-09-23-reassessment-slice2-owner-acceptance.md) preserves that
boundary. Governing plan, contracts, candidate reasoning/output clauses, resource
policy and frozen oracle/checker were read. Approved package SHA remains
`454736288217a5c66e8cf6875069aba3a60dee04005c5644d95135adbc8110fb`.

## Implemented scope and exclusions

New application module `reassessment_compute.py` accepts the captured graph and
always recomputes owning public admission through Slice 2. It has no validation
flag, expected-output input, support-discovery path, bypass or callback computation.
It derives canonical result/trace data, without filesystem publication.

Every decoder branch is intersected with the closed uncertainty envelope using
bounded exact rationals. Endpoint-only intersections count only in the declared
finite-decimal domain: 1/2 is representable, 1/3 is not. Empty original branches
remain in the immutable decoder and all-outcome qualification; they are not
rewritten or treated as observed values. A defensive coverage check refuses holes,
overlaps or empty represented coverage. Owning Slice 1 decoder validation still
rejects invalid partitions, including gaps outside the envelope, before assessment.

For each baseline-eligible original H and the one selected P, the maintained
supplied-support qualifier evaluates every outcome for row validity. A completely
excluded row refuses. Only then do all intersecting cells determine the conclusion:
all permits means compatible under the declared model; all justified exclusions
means conditionally incompatible; any missing/conflicting/unavailable/mixed support
leaves unresolved. Positive-only support never supplies complement exclusions.
Missing unrelated cells outside the represented envelope do not invalidate this
local assessment or change the original ranking's meaning.

All original H rows remain visible. Baseline-ineligible rows have no new outcome
cells and are neither resurrected nor newly eliminated by E1. Permission and other
gates retain distinct completed withholding. Multiple fits, model/prediction
mismatch and incomplete assessment remain distinct; no nearest-H selection occurs.
Original references, reasons and dependencies are retained. Changed original
I/Q/E/H/P/O/S references are disclosed against the retained predecessor, including
added/removed entries rather than silently dropping an unmatched array tail.

Results state `derived_not_adopted` and `ranking=not_reassessed`. There is no ranker
call, adoption, state mutation, acquisition or next-request generation. Local
chronology uses the accepted unverified wording; it is not predictive validation.
The two earlier modules changed only to record actual JSON high-water measurements
for nr capture. Legacy Work reporting is unchanged unless nr capture opts in; this
is metering, not a validation bypass or changed limit.

Commands, publication, seven-file delivery, semantic replay and delivery fault
qualification remain Slice 4. Full 180-command qualification/release remains Slice 5.
Phase 8 in the generated trace records bounded semantic output construction only;
it does not claim a published manifest or durability. No reassessment command was
added and no reassessment bundle was published.

## Scope-to-test mapping and oracle provenance

Tests are in `tests/reassessment_profile/test_assessment.py`. Frozen hand-authored
expectations and the separately written static arithmetic checker are by the same
lead author: independent of runtime computation, not independent-reviewer or
empirical evidence. Runtime code never reads either. Frozen bytes were not edited.

| Obligation | Evidence |
| --- | --- |
| P1–P9 semantics and refusals | `frozen_mathematical_and_epistemic_expectations`: 49 cases, 36 completed and 13 adverse; exact statuses, branches, disposition, original rows and zero ranking work |
| Complete semantic output | `complete_frozen_semantic_result_excluding_runtime_accounting`: all 36 completed P1–P9 results match after mechanical invocation binding; only actual runtime accounting is excluded from static equality |
| Independent arithmetic challenge | `separate_frozen_arithmetic_checker_agrees` applies the retained separate checker to each assessed envelope; `exact_endpoint_domain` contrasts 1/3 and 1/2 |
| Complete branches and exclusions | `all_outcomes_qualified_but_only_envelope_concludes`, `missing_complement_and_justified_twin`, `empty_nondecimal_branch_is_retained_not_interpreted`; missing/conflict/unavailable/positive-only/mixed/no-fit/multiple-fit frozen twins |
| Invalid coverage | Frozen P4 gap/overlap/remote-gap versus partition twins use real capture validation; `defensive_envelope_coverage_rejects_gap_and_overlap` separately labels an internal coverage-algorithm probe |
| Baseline and lifecycle | `baseline_ineligible_source_cannot_force_row_refusal`, P7 revised-baseline twins, `revision_discloses_before_and_after_without_changing_history`; no outcome qualification for ineligible H, predecessor bytes unchanged |
| No implicit later action | `construction_order_and_no_ranking` forbids ranking dispatch; `withholding_has_no_qualification_or_intersection` forbids both functions after gates; results retain all H and manual-adoption status |
| Reasons, dependencies and trace | `complete_withholding_result_matches_frozen_template`: nine gate templates; `complete_trace_matches_bound_frozen_template`: four complete traces; dependency refs resolve exclusively inside captured material |
| Closed output and resource boundaries | Six closed result/trace shape checks, actual high-water counters, exact output demand/demand-minus-one, bounded chunk serialization and zero writes on refusal |
| Real executable-bound composition | Five `real_captured_semantic_path` cases: supported, missing-support, no-fit, multiple-fit and denied; actual Slice 1 safe capture/build before owning admission and assessment |

Most semantic cases intentionally use the internal shaped-build graph while still
performing real public reconstruction and qualification. They do not assert
production build admission. The five production twins and twelve measured public
capture/computation probes establish that boundary separately. No synthetic build
or traversal seam is exposed through a production command. Support bypass controls
were not introduced. Reused prior cycle evidence retains its public/internal split.

## Red/fixed evidence and exact-head verification

`initial-red.log` records missing `reassessment_compute` before implementation.
The first 60 semantic tests passed after implementation. The expanded 101-test
selection passed mathematical, epistemic and full-result comparisons. Further
schema tests failed because the first result copied unrestricted Work fields and
omitted required accounting fields; the fix projects the closed 14-field layout,
retains zeros for unreached operations and records actual input high-water values.
`shape-red.log` and `shape-fixed.log` retain that repair. `trace-red.log` / `trace-fixed.log`
record restoration of the frozen observation dependency role order, without editing
the template. Output guards reuse the maintained bounded serializer.

Fresh clean implementation `433077d717719921d89fe5f882c83bf93f55c18e`:
**333 passed, zero skips/failures, 258.16 seconds**. Exact argv, HEAD, exit and output
are in `tested-command.json` / `tested.log`. Selection: 129 Slice 3 tests, all
181 Slice 1–2 tests, and 23 affected selector contract/admission/qualification/ranking
tests. Earlier working-tree logs are red/fixed evidence, not exact-HEAD verification.
The accepted earlier thermal/governed and selector-delivery evidence remains
historical; those command tests were not freshly rerun or claimed as such here.
No full repository suite or 180-command proof ran.

Existing provisioned CPython 3.13.11/dependencies were used without acquisition.
Runtime checks used isolated ext4 directories. The pytest driver's aggregate
duration is not a single application operation's wall-time measurement.

## Measurements, capacity and recovery

Actual build witness: **27,139 bytes**, SHA-256
`2b0b5474f2e0afd3ac28d85fce1a259394948c8dafa187c69c5b03c690cd85e5`.
Producer: 47,713,072 bytes read, 2,209 read operations, 47,823,207 hash-input bytes,
26,986 JSON-decoding bytes. Previous witness sizes are historical, not constants.
The independent 65,536-byte component ceiling still does not guarantee aggregate fit.

Static mechanical rebinding of all **51 completed prepared cases** fits unchanged
limits. Largest closure: **479,208 / 524,288 bytes**; largest captured raw total:
**354,175 bytes**. Conservative complete seven-file reserve, including full allowed
result/trace/manifest ceilings: **720,790 / 1,048,576 bytes**. This is static carriage
feasibility, not runtime execution of all 51 cases or a promise about all maximum
dimensions simultaneously.

Twelve public capture/computation probes ran at the tested HEAD. Representative
actual values (complete details and output bytes are retained):

| Case | Disposition | Intersections / qualified cells / source contributions | Result / trace bytes | Seconds |
| --- | --- | ---: | ---: | ---: |
| P8-before | one_compatible | 2 / 4 / 4 | 5,045 / 5,242 | 2.433 |
| P7-newbaseline | one_compatible | 3 / 3 / 3 | 7,333 / 6,589 | 3.055 |
| P10-no-observation | observation_unavailable | 0 / 0 / 0 | 4,841 / 5,073 | 2.187 |
| P10-shared_four | one_compatible | 2 / 4 / 4 | 4,993 / 5,545 | 3.221 |
| P5-mismatch | model_prediction_mismatch | 3 / 6 / 6 | 4,967 / 4,845 | 2.294 |
| P5-positive | incomplete_assessment | 3 / 6 / 6 | 5,459 / 5,015 | 2.272 |
| P6-multiple | multiple_compatible | 3 / 6 / 6 | 5,450 / 4,845 | 2.228 |
| P10-context8 | one_compatible | 3 / 6 / 6 | 4,959 / 5,451 | 4.101 |
| P10-objects128 | one_compatible | 3 / 6 / 6 | 4,960 / 14,445 | 2.427 |

Additional measured probes cover P3b-third, P3b-half and P5-conflict. Max observed
process RSS across probes: **105,840,640 bytes**, below 512 MiB; it is a process
high-water value, not isolated per-case allocation. Longest measured operation:
**4.101 seconds**, below 30 seconds. Four-revision capture/assessment used 545 reference
occurrences, 1,289 edge visits and 5,173,811 context-scan bytes; all unchanged guards
passed. Eight contexts and 128 objects also passed actual computation, not only
static fit. No broader platform or durability guarantee follows.

For P7-newbaseline, actual semantic result/trace plus exact captured input/build/
policy and the full manifest allowance reserve **538,104 bytes**. This is an
in-memory complete-delivery fit calculation; no seven-file nr bundle or actual
manifest was produced. Application writes remain zero. Harness evidence writes
are separately retained. Actual repeated backend-validator hashes remain measured
by the pass-through test observer, separate from application logical hashing;
they are not represented as free or included in a counter that excludes them.

All seven original files totaling **232,849 bytes** recover exactly in the fresh
capture tests and measured prior-bearing cases. Captured closure and build bytes
are retained for recovery; no original directory or digest-only ancestor shortcut
is introduced. Full standalone semantic replay is still a Slice 4 obligation.
No new manifest directories were created by this run, so the previously scoped
retained-bundle inventory remains **65,433,988 / 67,108,864 bytes**. Input captures,
source copies and proof/evidence archives are separate; this is not total workspace
disk usage. No earlier runtime evidence was deleted. Later delivery testing must
address remaining corpus headroom within the unchanged policy.

## Evidence, preservation and owner gate

[Evidence archive](2026-09-23-reassessment-slice3-evidence.zip): **1,063,061 bytes**,
SHA-256 `768dbf9e913458055c8a278903a0eed81dbf3e88dc373fb45fd2f41f7c78c7a6`.
All 34 payload members were verified against its manifest. It includes raw red/fixed
and final logs, commands, build/closure/output material, measurement scripts,
runtime/static accounting, source patch, inventory and preservation. The exact
approved self-contained package remains committed separately.

Starting inventory: **4,768** Git-enumerated regular files and **3,499** untracked
paths. None is missing. Only two pre-existing application source files changed for
nr-specific measurement; the other 4,766 are byte-identical. All original untracked
paths/bytes remain. Historical reports, frozen package/oracle commitments, runtime
results, dependencies, provisioning, backend contracts and ledger were preserved.
Only explicit authorized source/tests and documentation/evidence were staged.
No cleanup, permission/security change, dependency acquisition, remote operation,
ADR allocation or history rewrite occurred.

No known Slice 3 defect remains. Commands, publication, independently recomputing
replay, fault qualification, full proof and release verification remain deferred as
the plan assigns. No empirical validity, causal truth, authenticated identity,
pre-exposure custody or autonomous action is claimed. C remains unresolved;
IN-001 and CI-001 remain open and unselected; the historical review-digest discrepancy
remains disclosed and unresolved.

Owner gate: accept Slice 3. Subsequent slices and the full proof remain unauthorized.

END OF REASSESSMENT SLICE 3 COMPLETION REPORT.
