# IB-001 Identity Binding Implementation Plan

**Spec:** `docs/superpowers/specs/2026-08-07-ib001-identity-binding-design.md`
(self-contained, authoritative). **ADR:** `docs/adr/0006-identity-binding-ledger.md`.

**Goal:** the accepted vertical slice — pure anchor contracts, append-only
ledger with full-SHA-256 canonical record IDs, write-once JSON store with
all-or-nothing validation and revision replay, three-valued applicability,
the eight-case resolver with structured lifecycle explanations and
non-recursive subject context, the bound temporal facade, and the
committed synthetic Moonraker binding set proving the complete provenance
chain.

**Hard boundaries:** zero changes under `backend/data_sources/` and
`backend/temporal_state/` (stop and request approval if one appears
unavoidable). `identity_binding` imports only `system_identity` and
`temporal_state`. No new dependencies. TDD throughout: write the failing
test, watch it fail for the right reason, implement minimally, watch it
pass, commit per task.

**Verification commands:**

```bash
.venv/bin/python -m pytest tests/identity_binding/ -q     # focused
.venv/bin/python -m pytest tests/ -q                      # full repository
```

## Task 1 — Anchor and ledger contracts (`system_identity` + `identity_binding.contracts` + `canonical`)

Files: `backend/system_identity/{__init__,anchors}.py`,
`backend/identity_binding/{__init__,contracts,canonical}.py`,
`tests/identity_binding/{__init__,test_anchors,test_contracts}.py`.

1. Failing tests — anchors: `ent_`/`var_` 32-hex pattern enforcement;
   namespace/role `[a-z0-9-]+`; frozen/extra-forbid; variable requires
   `ent_` owner id; `referent_kind` values; `system_identity` imports
   nothing from `backend.*` (assert on module imports).
2. Failing tests — ledger contracts: every record kind validates;
   binding_kind/property pairing; target prefix vs binding_kind;
   naive datetimes rejected; non-UTC aware datetimes normalized to UTC at
   validation; AppliesScope declared-interval invariant; AuthorityRef
   literals.
3. Failing tests — canonical hashing: `record_id` = prefix + full 64-hex;
   recomputation matches; `record_id` excluded from its own hash; sorted
   keys/compact separators; **equal instants with different offsets hash
   identically** (mandatory regression); `+00:00` serialization; hash
   covers `schema_version` (changing it changes the id).
4. Run tests, watch them fail. Implement `anchors.py`, `contracts.py`
   (records, results, errors), `canonical.py` (canonical payload walk +
   sha256 + `make_record_id`/`verify_record_id`). Watch tests pass.
5. Commit: `feat: system_identity anchors and identity_binding ledger contracts`.

## Task 2 — Write-once store, all-or-nothing validation, revision replay

Files: `backend/identity_binding/store.py`,
`tests/identity_binding/test_store.py`.

1. Failing tests: append writes `<record_id>.json` atomically; identical
   re-append is a no-op; load verifies content hashes; every integrity
   invariant from the spec's numbered list rejects the complete set
   (parametrized: hash mismatch, duplicate anchor_id across declarations
   — mandatory regression —, cross-kind identifier, prefix/kind
   contradiction, dangling target/entity/supersedes/retracts/closes/
   rejected_anchor_id, wrong-kind or wrong-locator supersedes, closure on
   declared end, closure ≤ declared start, **two closures on one
   assertion**, retraction of non-assertion); valid set loads with
   lifecycle links (superseded_by/retracted_by/closure_records) computed;
   revision membership sorted lexicographically regardless of file
   creation order; **revision_id changes when membership or
   binding_set_id changes** (mandatory regression); `load_revision`
   replays a supplied subset, rejects missing ids and non-reference-closed
   subsets; deterministic reload (same files ⇒ same revision, same
   loaded state).
2. Watch fail → implement `BindingStore` (append/load/load_revision,
   whole-set validation, `LoadedBindingSet` with anchors-by-id and
   lifecycle index) → watch pass.
3. Commit: `feat: write-once identity ledger store with all-or-nothing
   validation and revision replay`.

## Task 3 — Resolver: applicability, eight cases, lifecycle summaries, subject context

Files: `backend/identity_binding/resolver.py`,
`tests/identity_binding/test_resolver.py`.

1. Failing tests — applicability: all nine boundary combinations at
   representative times; half-open boundary instant is OUT; membership on
   EFFECTIVE scope after closure.
2. Failing tests — algorithm (one per case + regressions): unbound;
   inactive rules (superseded-only / retracted-only / mixture→inactive;
   **simultaneous supersession and retraction loses neither fact**);
   outside_applicability; conflicted (two IN targets); ambiguous (one IN
   + different-target UNKNOWN — **different-target UNKNOWN prevents
   bound**); bound (**different-target OUT never blocks**; same-target
   UNKNOWN corroborates); applicability_unknown (**unknown-only candidate
   never occupies resolved_target**); ambiguous (two UNKNOWN targets);
   competing successors resolved by the matrix, never timestamp;
   `applicability_basis` declared vs includes_unbounded_claim; naive `at`
   → `BINDING_NAIVE_AT`; candidate/summary canonical ordering;
   **summaries cite exact closure/supersession/retraction records**.
3. Failing tests — property independence: **property binds while subject
   unbound**; **property binding creates no subject binding**;
   cross-entity ownership → **conflicted**; unknown/ambiguous subject
   visible in context; context is non-recursive (ids only).
4. Watch fail → implement membership + `BindingResolver` → watch pass.
5. Commit: `feat: deterministic identity resolver with three-valued
   applicability and structured lifecycle`.

## Task 4 — Bound temporal facade

Files: `backend/identity_binding/facade.py`,
`tests/identity_binding/test_facade.py` (reuses the DS-004 fixture runner
helpers from `tests/data_sources/test_ingestion_runner_api.py` as the
TS-001 repair tests do).

1. Failing tests: `latest_observed` returns the TS-001 object **verbatim**
   (equality against a direct `TemporalQueries` call) with resolution
   computed at the observation's `received_at` (not `as_of`, not now);
   `history` resolves per occurrence at each `received_at`, spanning an
   applicability boundary to different anchors; unresolved/ambiguous
   results still carry the observation; no writes to either store.
2. Watch fail → implement `BoundTemporalQueries`, `BoundLatestObserved`,
   `BoundOccurrence` → watch pass.
3. Commit: `feat: bound temporal query facade`.

## Task 5 — Committed demo binding set + end-to-end validation slice

Files: `bindings/demo-printer/records/*.json` (4 records, generated
through `BindingStore.append` with the spec's fixed constants),
`bindings/README.md`, `backend/system_identity/README.md` (short),
`backend/identity_binding/README.md`,
`tests/identity_binding/test_demo_binding_set.py`.

1. Failing tests: committed set loads valid; **fixture authority is
   test_fixture, never human_owner** (asserted over every committed
   record); end-to-end bound resolution inside
   `[2026-08-07T20:00:00Z, 2026-08-07T21:00:00Z)` with
   `applicability_basis="declared_interval"`; **an occurrence outside the
   hour → outside_applicability**; complete provenance chain (anchor ←
   assertion ids + revision ← locator ← occurrence ← attempt ←
   raw_record_id ← payload checksum verified against stored bytes); the
   same word from another adapter/source unbound; conflict surfaced in a
   tmp_path set, never guessed; supersession preserves the prior
   assertion; **SHA-256 hash sweep proves evidence and temporal stores
   byte-for-byte unchanged** across all IB-001 operations.
2. Generate the four committed records via the store (deterministic ids),
   commit them, watch tests pass.
3. Commit: `feat: committed demo-printer binding set and IB-001
   validation slice`.

## Task 6 — Verification and handoff

1. Focused suite; full repository suite (baseline 389 must be preserved).
2. `git diff --stat` proof of zero upstream changes; grep committed
   records for secrets/absolute paths (none).
3. Base-only and all-extras clean-checkout verification (fresh clones,
   fresh venvs).
4. Update project memory (milestone + decisions checkpoint).
5. Report: commit list, exact test counts, clean-checkout results, live
   provenance demonstration, upstream-unchanged evidence, known
   limitations, and the next architectural question for MK-001. Stop for
   owner validation.
