# FM-001 Slice B Completion Report

Date: 2026-09-09

Status: Slice B implementation verified; uncommitted report for owner review;
final FM-001 owner acceptance pending.

## 1. Exact checkpoint and authorization

Branch: `fm001`.

Exact tested implementation:
`4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`.

The corrected Slice B contract was accepted at
`7bb7db8ec27af74bdd887d763222757c1f1fc821`. Its administrative authorization
is recorded in commit `a7fe841` and
`docs/superpowers/reports/2026-09-09-fm001-slice-b-contract-owner-acceptance.md`.
Repaired Slice A remains accepted at
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`.

This continuation resumed a clean tree with the implementation and hardening
already committed. It inspected that implementation, ran fresh verification,
and wrote this report. It made no production or test changes and created no
new implementation commit. Historical failing-test counts are not inferred
from commit history.

The accepted synthesis, plan, and matrix still have their frozen SHA-256
digests:

| Authority | SHA-256 |
| --- | --- |
| FM synthesis, `2026-09-07-fm001-explicit-flow-to-measurement-association-design.md` | `6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7` |
| Slice B implementation plan | `1bf6c8835d799186795478c337e12df9446e0b16d494d412604d07d6717922f2` |
| Slice B adversarial acceptance matrix | `6f4d6927b41bb97089c4b4277c064b9cc6371ffa68375b36af36954d617c8200` |

## 2. Implemented behavior and boundaries

The existing `ModelQueries` class adds the accepted exact-subject lookup,
three independently indexed reverse lookups, and FMA/FMW assertion lookup.
The public surface appends exactly 20 names to the accepted 205-name prefix:
11 aliases, four nested rows, and five outer results, for 225 total exports.

Every outer result carries one complete, authoritatively reconstructed
`ModelQueryMaterial`. Nested rows disclose indices and derived fields.
Required null and empty fields remain explicit. Exact and reverse queries
share private subject derivation, while each reverse query selects through
its own flow/context, variable/context, or port/context index.

The results retain every root and current effective-body group, including
mixed healthy, conflicted, and inactive roots. Findings retain their accepted
order and coexist without selecting a winner. Each positive body or selected
positive assertion discloses exactly six pinned support rows in
FRG/VRG/PRG/FLD/VPA/VSM order. Historical support activity, lineage health,
and current alignment remain separate axes. Withdrawal and absent assertion
results retain their exact null/empty shapes.

The committed hardening validates standalone nested-row invariants, hostile
scalar/container/model/timezone inputs, stored dictionaries and fields-set
metadata, material reconstruction order, and bounded shared-object traversal.
The shared `result_revalidation.py` helper also rejects caller-defined
mappings and avoids repeatedly expanding already visited containers.
The full suites below exercise its existing consumers as well as FM.

Bounded local inspection during this continuation covered public contracts,
support reachability, root/body grouping, reverse sorting and index selection,
assertion disclosure, and reconstruction. No additional defect was found.
No separate reviewer-agent result is claimed by this report.

The implementation adds no authoritative FM records, fixture, demonstration,
store, identity, facade, upper composition, or occurrence claim. Model
declarations do not establish measured flow, physical activity, correctness,
safety, diagnosis, or recommended action.

## 3. Acceptance coverage

The executable Slice B evidence is in
`tests/model_kernel/test_flow_measurement_slice_b.py` and
`tests/model_kernel/test_flow_measurement_slice_b_adversarial.py`.

| Matrix obligations | Exercised behavior |
| --- | --- |
| FM-B01–B08 | Exact public additions, aliases, fields, signatures, scope, and typed malformed-input refusal |
| FM-B09–B15 | Endpoint registration, structured absence, exact context, participant locus, and orientation subjects |
| FM-B16–B27 | Same-root and cross-root conflicts, corroboration, inactive mixtures, body groups, reciprocal references, and finding order |
| FM-B28–B37 | Six mandatory pins, valid support lifecycle worlds, unreachable products, and forged/substituted support rejection |
| FM-B38–B45 | Three reverse axes, semantic sorting, context isolation, distinct orientations, and shared subject payloads |
| FM-B46–B49 | Absent, positive, and withdrawal assertion shapes and parity with exact/reverse results |
| FM-B50–B55 | Authoritative reconstruction, hostile instances and indices, carry-once material, bounded graphs, and no-I/O behavior |
| FM-B56–B58 | Five hash seeds, reversed construction, exact 36-record absence, and preservation evidence |

The standalone Slice B gate passed **43 tests in 27.58 seconds**. The complete
FM, model-kernel, identity, affected lower/upper consumers, architecture,
isolation, and preservation tests were also exercised by each full suite.
No separate per-package counts are claimed for those aggregate runs.

## 4. Full working-tree verification

Command:

`PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q`

Result: **3,896 passed in 2,084.21 seconds (34:44)**, exit zero, with no skips
or errors. The real loopback test passed inside this uninterrupted aggregate.

## 5. Fresh base-only verification

A new detached checkout at `/tmp/fm001-slice-b-base-i14a9F` used its own newly
created `venv`, installed from `requirements.txt` and `requirements-dev.txt`.
Its exact HEAD was the implementation in Section 1.

From that checkout:

`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q`

Sandbox aggregate: **3,860 passed, 35 expected optional-dependency skips,
1 setup error in 1,587.01 seconds (26:27)**, exit one.

The sole error was the real loopback fixture attempting to create a socket
for `127.0.0.1`: `PermissionError: [Errno 1] Operation not permitted`.
The exact targeted test passed separately under the permitted invocation:
**1 passed in 0.79 seconds**.

Target:
`tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation`.

The reconciled accounting is **3,861 runnable tests passed plus 35 expected
skips**. This is split evidence, not an uninterrupted full-suite pass.

## 6. Fresh all-extras verification

A separate new detached checkout at `/tmp/fm001-slice-b-extras-SQT1fb` used
its own newly created `venv`, with base/dev dependencies followed by
`pip install --require-hashes -r requirements-cad.txt -r requirements-pdf.txt`.
It tested the same exact HEAD.

The same full-suite command, run from this checkout, recorded
**3,895 passed, 1 setup error in 1,588.85 seconds (26:28)**, exit one, with
no skips. The sole error was the same sandbox socket restriction. The exact
targeted loopback test passed separately: **1 passed in 0.79 seconds**.

The reconciled accounting is **all 3,896 runnable tests passed**, with the
same explicit split-evidence limitation as the base run.

The separate CAD/STEP/PDF gate passed **120 tests in 48.36 seconds**, exit
zero. It covered STEP ingestion/extraction and structural claims, plus PDF
ingestion, contracts, coordinates, availability/detection, and extraction.

## 7. Determinism and accepted reproductions

The permanent Slice B determinism test compares forward and reverse
construction and subprocesses with hash seeds `0`, `1`, `7`, `41`, and
`random`. It passed in the focused gate and all three full suites.

Additional direct reproductions in the working, fresh base, and fresh extras
environments produced identical bytes and hashes:

| Reproduction | Bytes | SHA-256 |
| --- | ---: | --- |
| FM Slice B witness, forward and reverse | 245,676 | `b65567aae97c7dc3c6913a12ab52c78e329a99fedcb40bfa1b9bc36f69a40839` |
| Accepted in-horizon source plus temporal material | 24,766 | `ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7` |
| Accepted TA private canonical result | 195,429 | `1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97` |

The FM witness uses
`tests/model_kernel/fm001_slice_b_reproduction.py:witness_bytes`. Lower
material uses the existing `_captured_lower_material` test helper and its
source/newline/temporal serialization. TA uses the existing disposable
`build_world` helper, public assessment, and private canonical serialization.
These operations use disposable material and do not append to authoritative
stores.

## 8. Protected state and repository hygiene

The dedicated authoritative-ledger preservation test passed separately:
**1 passed in 3.50 seconds**. Full-suite preservation tests also passed.

The authoritative model remains:

- 36 records at
  `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- accepted ledger inventory aggregate
  `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, and FMA/FMW `0/0`;
- FL disclosure SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- local-settings SHA-256
  `abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

Comparison with accepted Slice A found no changes to its kernel contracts,
canonicalization, store, system identity, lower evidence/temporal packages,
EA/TA production packages, authoritative data, or fixtures. Frozen artifact,
historical membership, disclosure, and documentation checks passed within
the full suites.

All three Python environments report Python 3.13.11. All three `pip check`
runs returned `No broken requirements found`. Backend compilation exited
zero in all three environments, with bytecode directed into disposable
`/tmp` prefixes. Working and clean-checkout whitespace checks passed for the
full FM range `a069cb6..HEAD`.

Both detached checkouts remained clean after their full runs and retained
the exact tested HEAD. This report is intentionally uncommitted. No push,
merge, owner-acceptance edit, or authoritative append was performed during
this continuation.

## 9. Owner gate

Slice B implementation and verification are complete at the exact tested
commit. Final FM-001 acceptance remains a separate owner decision on this
implementation and report. There is no Slice C or demonstration, and this
report authorizes no FA-001 or other frontier work.

END OF FM-001 SLICE B COMPLETION REPORT
