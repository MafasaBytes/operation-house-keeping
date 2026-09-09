# FC-001 Slice A Implementation Plan

**Status:** FC-001 is complete and owner accepted at exact tested implementation
`9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`; this plan remains the historical
Slice A execution record. FA-001 is cancelled under the accepted direct-join
proof and may be reconsidered only by a new owner-approved proposal
demonstrating an integrity attack existing public-result validation cannot prevent.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Persist an explicit authority-designated governing criterion for one exact FM meaning, preserving historical support without evaluating applicability or a sample.

**Architecture:** Two additive records in the existing model kernel ledger. A private bounded structural-input helper protects new record paths; canonical/store integration derives exact witness-based bodies and immutable lifecycle indexes. No Slice B contracts or upper dependencies.

**Tech Stack:** Existing Python, Pydantic v2, standard library, pytest; no new dependency.

## Global Constraints

- Frozen specification: `docs/superpowers/specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md`, SHA-256 `7aa5007058c1733720fc624839c19efd98258c800c67461d1afc5ade674a3453`.
- All 27 owner decisions, C1 and N1–N5 remain normative; no design amendment.
- Reject stale content-derived IDs, support substitution, missing support and invalid structural closure; preserve valid retained historical support.
- Currentness-based applicability/staleness conclusions and all FC query/result contracts belong to unauthorized Slice B.
- VSM remains context-independent. Only accepted FLD/VPA relations require exact FMA context.
- Branch `fc001`; accepted base `c0e1c8fe930e10243fec16a4950a3d34d4c85df4`; no push, merge or history rewrite.
- Exactly 227 unique ordered exports; preserve accepted 225-name serialized prefix byte-for-byte and append only `FlowOperatingCriterionDeclaration`, `FlowOperatingCriterionWithdrawal`.
- Preserve authoritative 36-record membership/revision and all existing identity, ledger, fixture, artifact and local settings bytes. No authoritative FMA/FCD/FCW append.
- No anchor, minter, registration, evaluator, facade, sibling ledger/store or upper import.
- Initial consumer: commissioning/operations verification. Slice A establishes designation, not a completed sample check or physical truth.
- Post-green architecture, backend, test and adversarial reviews must cover contract and original objectives. Review judgments are not fabricated test counts.
- FA remains deferred; successful separately accepted FC/CN/evidence direct-join proof mandates cancellation. Reopening requires an owner-approved unpreventable public-result integrity attack, not convenience.

## File ownership

Modify `backend/model_kernel/contracts.py` for the exact two records and union/
positive-only evidence patterns; `canonical.py` for prefixes, safe builders and
membership-dependent effective body; `store.py` for bounded dispatch, closure,
lifecycle and twelve indexes; `__init__.py` for the two appended exports.
Create `backend/model_kernel/flow_operating_criterion_validation.py` only for
private structural preflight/JSON reconstruction helpers. Do not create
`flow_operating_criterion_results.py`, methods in `queries.py`, or identity code.

Create disposable test helpers and three focused modules under
`tests/model_kernel/`: `fc001_slice_a_helpers.py`,
`test_flow_operating_criterion_records.py`,
`test_flow_operating_criterion_store.py`, and
`test_flow_operating_criterion_preservation.py`. Reconcile existing FM surface
assertions only to retain exact historical prefixes and append the new suffix.
No accepted fixture or golden artifact is regenerated.

### Task 1: Exact record and bounded-input foundation

**Interfaces:** Consume existing `EvidenceRef`, `AuthorityRef`, `UtcDatetime`,
`build_record(record_cls, **fields)` and the plain `ModelRecord` union. Produce
exact synthesis §§5–8/16 record classes and canonical dispatch; no public helper.

- [ ] Read the complete frozen synthesis and specialized backend/test instructions.
- [ ] Add executable red tests using module attribute lookup inside tests, not
  imports that prevent collection. Pin exact field order, defaults, discriminators,
  nonempty evidence, parent validation, FCW non-citability and export suffix.

```python
def test_positive_field_order():
    cls = getattr(mk, "FlowOperatingCriterionDeclaration", None)
    assert cls is not None
    assert tuple(cls.model_fields) == (
        "record_kind", "schema_version", "record_id",
        "flow_measurement_association_record_id",
        "constraint_registration_record_id", "constraint_declaration_record_id",
        "evidence", "supersedes", "recorded_at", "authority", "note",
    )
```

- [ ] Author literal compact JSON golden input for FCD/FCW independently of
  production canonical helpers; calculate expected SHA-256 using stdlib. Test
  witness-sensitive IDs, evidence/parent permutations and UTC normalization.
- [ ] Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/model_kernel/test_flow_operating_criterion_records.py -q`.
  Record real failed test counts and causes before production edits.
- [ ] Implement exactly the synthesis's 11/7-field frozen extra-forbid classes,
  strict strings, parent sorting after duplicate/self rejection, canonical
  evidence after pre-normalization limits, and fixed value-free outer errors.
- [ ] Implement private callback-free plain reconstruction with exact trusted
  classes/scalars/containers, active-path cycle detection and per-edge expanded
  accounting. Check all inclusive budgets from §16 before expansion/dump.
  Do not reuse legacy visited-once traversal as an expanded-size defense.

```text
new record: canonical bytes <=131072; nodes <=8192; containers <=2048;
depth <=32; evidence <=64; parents <=64; string/key UTF8 <=16384;
authority.agent <=1024; note <=8192; other container cardinality <=256.
raw JSON <=1048576; integer bits <=4096; JSON integer digits <=1234.
```

- [ ] Override JSON and alternate validation entry points so depth scanning and
  duplicate-key rejection precede parsing/union adaptation. Reject unsupported
  `model_validate_strings` with the fixed invalid-input outcome. No coercion bypass.
- [ ] Add fcd/fcw canonical prefixes and record-ID patterns, fcd-only citability,
  append union arms and the exact two exports. Preserve old union semantics.
- [ ] Keep new builder dispatch safe before class callbacks and return a fully
  validated final instance rather than an unchecked `model_copy`.
- [ ] Run the same focused tests green and existing canonical/FM tests. Record
  actual red/fixed evidence and commit the verified bounded foundation.

### Task 2: Exact closure, lifecycle, immutable indexes and store integration

**Interfaces:** Consume Task 1 contracts and existing full collection validator,
FM six-pin admission, `_flow_measurement_effective_body_bytes` and iterative DAG
machinery. Produce the twelve exact `LoadedModel` mappings in synthesis §17.

- [ ] Build a labelled disposable FM foundation plus CRG/VCN using public builders.
  Override the test helper's old `measured` role with exact
  `project_local/ohk-observation-roles-1/measured_actual`.
- [ ] Add red tests for missing/wrong-kind/forged witnesses, each support pin,
  CRG target and VCN anchor/role mismatch, cross-subject parents, all orientations,
  witness retention and no silent substitution. Use exact expected error codes.
- [ ] Add paired history tests: retain a superseded VCN or withdrawn witness and
  load/replay successfully; omit that exact witness despite equal replacement
  and reject. Assert old FC references remain unchanged, not floating to current.

```python
# In a dependency-closed disposable world after exact VCN correction:
loaded = validate_record_collection("fc001-disposable", records)
assert loaded.flow_operating_criterion_declarations[d.record_id].constraint_declaration_record_id == old_vcn.record_id
# No applicability/currentness field or FC query is introduced by this assertion.
```

- [ ] Run `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/model_kernel/test_flow_operating_criterion_store.py -q` and record genuine red counts.
- [ ] Implement collection passes in synthesis §8 order: revalidation/hash;
  all existing lower invariants; exact witness/CRG/VCN membership; S/B and role
  coherence; evidence closure; parents/root/cycle; withdrawals; immutable indexes.
  Preserve historical support irrespective of currentness.
- [ ] Compute effective body only from the retained membership witness:

```python
body = {
    "flow_measurement_body": json.loads(fm_body_bytes),
    "constraint_registration_record_id": declaration.constraint_registration_record_id,
    "constraint_declaration_record_id": declaration.constraint_declaration_record_id,
}
body_bytes = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
```

- [ ] Derive S from the witness, enforce same-S/same-root parents, iterative
  acyclicity and exact withdrawal eligibility. Zero/one/multiple tip IDs remain
  indexed facts, not new public statuses. FC current-tip tuples contain IDs.
- [ ] Publish all twelve copied mapping proxies with deterministic tuple ordering.
  Preserve separate body groups and inactive roots without selecting a winner.
- [ ] Add bounded new-prefix file reads (cap+one byte), safe JSON before union
  adaptation, kind/filename/hash checks, and existing prospective atomic append.
  Revalidate corrupted siblings even on idempotent append; no staging on validation failure.
- [ ] Run both FC modules and complete model-kernel tests green. Commit verified
  kernel integration. No test fixture/model append is part of the commit.

### Task 3: Post-green adversarial review and preservation hardening

**Interfaces:** Consume exact implemented records, indexes and public store APIs.
Produce reviewed code, regression tests and file-based review evidence only.

- [ ] Run the [acceptance matrix](2026-09-09-fc001-slice-a-adversarial-acceptance-matrix.md)
  through architecture/backend/test/adversarial reviewers after the first green
  implementation. Test invalid closure rejection, retained-history loading and
  absence of Slice B conclusions independently.
- [ ] For every genuine defect, write a failing regression, capture red output,
  fix only authorized behavior and rerun covering tests; request scoped re-review.
- [ ] Pin exact ordered surface with literal suffix and accepted-prefix digest:

```python
assert len(mk.__all__) == len(set(mk.__all__)) == 227
assert mk.__all__[225:] == ["FlowOperatingCriterionDeclaration", "FlowOperatingCriterionWithdrawal"]
assert hashlib.sha256(json.dumps(mk.__all__[:225], separators=(",", ":"), ensure_ascii=True).encode("ascii")).hexdigest() == "097fe647d38bfd0947d1cac94583a1fd50bda5c15b5386ac3137c781097e414a"
```

- [ ] Verify authoritative 36-record inventory/revision, zero FMA/FMW/FCD/FCW,
  all accepted historical memberships, protected artifacts and unchanged settings.
- [ ] Run deterministic public-builder/store witnesses with five seeds
  `0,1,7,42,12345` and reversed input order. Record canonical/stored/index bytes
  and hashes; never substitute copied generated records for independent construction.
- [ ] Commit reviewed implementation and tests. Record this exact tested commit.

### Task 4: Complete verification and owner handoff

**Interfaces:** Consume exact tested implementation commit. Produce only evidence,
status reconciliation and the final completion report, then stop for the owner.

- [ ] Run focused FC, complete model-kernel and affected FM/FL/CN/VP/VS/ES/ST/BH/TA,
  model-state, observation/semantic compatibility, identity, architecture/isolation suites.
- [ ] Run full `tests/` with `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' -p no:cacheprovider tests/ -q`.
- [ ] Create fresh detached base-only and all-extras checkouts of the exact tested
  commit under unique `/tmp` directories, each with its own fresh venv. Install
  repository base/dev dependencies; extras additionally use hash-pinned CAD/PDF
  requirements. Run complete suites in both; do not count warmed environments.
- [ ] Run applicable CAD/STEP/PDF gates, `pip check`, and backend compilation.
  If sandbox denies loopback, retain the failing evidence and rerun the exact
  isolated test with approved permissions; report the split honestly.
- [ ] Run link/marker checks, frozen digests, protected inventory and
  `git diff --check` for working tree and `c0e1c8fe930e10243fec16a4950a3d34d4c85df4..HEAD`.
- [ ] Write `docs/superpowers/reports/2026-09-09-fc001-slice-a-completion-report.md`
  with exact commands/counts, commits, red/fixed evidence, reviews, deterministic
  witnesses, preservation, limits and goal assessment. End exactly
  `END OF FC-001 SLICE A COMPLETION REPORT`.
- [ ] Commit report only after required verification succeeds; preserve frozen
  inputs/settings. Return compact receipt and ask for Slice A acceptance and
  separate Slice B authorization. Do not begin Slice B or push/merge.

END OF FC-001 SLICE A IMPLEMENTATION PLAN
