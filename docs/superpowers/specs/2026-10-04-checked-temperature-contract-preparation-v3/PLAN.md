# Plan v3: gates, test authority and verification (proposed; nothing authorized)

## Counting vocabulary (fixed)

| Term | Meaning | Count |
|---|---|---:|
| Witness | a contract property (`witnesses.json`) | 19 |
| Case | one concrete positive or adverse input | 104 (33 positive, 71 adverse) |
| Invocation | one application CLI command, run as a child process | 179 (SE 62, SV 31, SR 29, RE 31, RV 16, RR 10) |
| Harness mutation | copying and editing a retained bundle; not an application invocation | 10 copies (4 selection, 6 reassessment) |
| Process launch | one top-level process started under a reservation | Gate 2: 2 (L1, L2) |

## Gate 0: owner decisions (documentation only)

The owner resolves D1–D10, O3, O5, A1, G1 and G2 (see `README.md`). All remain pending; recommendations are not approvals. The accepted content is
then frozen as edition files, the frozen digests are recorded, and the frozen
copies no longer carry `status: proposed`.

## Gate 1: implementation with an explicitly scoped test allowance

**Implementation authorization does not imply unlimited execution.** Gate 1
requires two separate grants.

**(a) Implementation scope.** New application modules only:

- `checked_contracts.py`
- `checked_derivation.py`
- `checked_applicability.py`
- `checked_selection.py`
- `checked_reassessment.py`
- `checked_runtime.py`
- `checked_cli.py`
- the dispatch entry

Also in scope: new tests under `tests/checked_temperature/`. Not in scope:
edits to legacy NM/NR modules, the backend, existing tests or assertions.

**(b) TDD test allowance.** Proposed:

- **Launches:** at most 40 pytest launches in total.
- **Selection:** each launch is limited to `tests/checked_temperature/**` and/or
  the five named legacy files below; nothing else is selected.
- **Workspace:** each launch uses a fresh `--basetemp` under a dedicated new
  workspace (`test-workspaces/ct-gate1-tdd/`), on ext4, outside every
  qualification root, corpus and ledger.
- **Cumulative storage:** 536,870,912 logical bytes, 20,000 files and 5,000
  directories, all retained with no cleanup.
- **Recording:** every launch is recorded in a local launch log (argv, exit,
  usage).
- **Prohibited in Gate 1:** CLI runs that write outside `tmp_path`, the Slice 4
  corpus, the full suite, and qualification claims.
- **Exhaustion:** reaching the limit stops for the owner. It does not raise the
  allowance.

**Named legacy regression files.** These are statically screened as having no
hard-coded roots, subprocesses or corpus writes:

| File | Test functions | Why |
|---|---:|---|
| `tests/measurement_profile/test_ranking_slice4.py` | 5 | the ranker is reused |
| `tests/measurement_profile/test_support_qualification_slice3.py` | 4 | legacy qualification is unchanged |
| `tests/measurement_profile/test_contracts_and_closure.py` | 10 | legacy closure and limits are unchanged; reads the committed fixture package |
| `tests/reassessment_profile/test_assessment.py` | 19 | the all-intersecting-branches rule is reused |
| `tests/reassessment_profile/test_admission.py` | 26 | legacy NR admission is unchanged |

`tests/reassessment_profile/test_delivery.py` is excluded: it writes into the
hard-coded historical Slice 4 corpus.

**Gate 1 exit.** Gate 1 ends with a code-review-ready diff, the launch log, and
the claim "unit tests for the witness matrix exist and pass under the TDD
allowance". It is not a qualification result.

## Gate 2: one bounded verification (separate execution authorization)

**Launches:**

- **L1 (witness driver):** one process. It runs the 179 invocations sequentially
  as child processes, in the order FX1 first, then witness order. It also
  performs the ten harness mutations.
- **L2 (legacy regression):** one pytest process selecting exactly the five
  named files.
- No contingency launch.

**Allowances** (re-proposed in v3 because the matrix grew to 179 invocations and 10 copies; v2 proposed 288/320 MiB for L1; pending owner choice G2). See `RESOURCES.md` §4:

| Launch | Logical | Physical | Files | Dirs |
|---|---:|---:|---:|---:|
| L1 | 352 MiB | 384 MiB | 4,500 | 900 |
| L2 | 16 MiB | 20 MiB | 600 | 300 |

The workspace is new (`test-workspaces/ct-gate2-verify/`), on ext4, and outside
all existing roots. Usage is checked before and after every child.

**Frozen expectations.** Before L1 starts, the driver writes the witness
expectations (`witnesses.json` at its frozen digest) and the case-to-invocation
plan, and hashes both. Expectations are never weakened.

**Stop rules.** Any one of these stops L1 immediately:

- an outcome differing from its frozen expectation. The difference is then
  classified as a software defect, a witness error or a contract ambiguity, and
  never re-read as a pass;
- an allowance crossed;
- a write outside the workspace;
- a missing required diagnostic;
- an L2 failure.

**Excluded:**

- full-suite runs and release qualification;
- physical acquisition;
- authenticated or owner-issued authority;
- deployment policy;
- XFS or durability claims;
- performance claims.

**Deliverable.** One report listing, for each case, the expected and actual
outcome and the invocations used; usage against the allowances; every refusal;
and the build identities.

## Later qualification

Any release qualification, a full-suite run, or acceptance stays a separate
owner gate. Nothing in Gates 1–2 requests or implies it.

## Not in scope

The following are not implied by any gate:

- hypothesis discovery;
- uncertainty-aware selection;
- action coupling;
- automatic adoption;
- backend extension;
- IN-001 / CI-001;
- a physical end-to-end producer.

END OF PLAN V3
