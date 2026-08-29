# VP-001 Slice D — implementation plan

Status: VP-001 Slices A, B, and C are owner accepted. Slice D is implemented
and adversarially reviewed; awaiting final owner acceptance. Final VP-001 owner
acceptance remains a separate owner gate.

Accepted base: `e50d7cdfdada015230c3f3469c29c8ebc502bac4`.

## Decision being validated

Slice D appends exactly one bounded synthetic `VariablePortAssociation` to the
existing `demo-printer` model and demonstrates the already accepted Slice A–C
contracts. It changes no runtime behavior. The association is a positive,
evidence-backed model claim in one exact context; it is not inferred from
ownership, names, source data, geometry, interface declarations, topology,
compatibility, or observations.

The committed model evolves from the explicit 28-record PT-001 membership to
one explicit 29-record VP-001 membership. Every earlier membership and revision
remains historical, explicit, replayable, and byte-frozen.

## Frozen fixture contract

Construct only through public `build_record()`:

```text
record_kind: variable_port_association
schema_version: 1
variable_anchor_id: var_b7e2d3c4f5a6172839405a6b7c8d9e0f
port_anchor_id: prt_91a3d6db9df440e1a09dbdb185c7b182
context: lifecycle_view / as_designed
supersedes: ()
recorded_at: 2026-08-29T12:00:00+00:00
authority: test_fixture / vp001_demo_fixture / manual_declaration
note: VP-001 bounded synthetic demonstration.
```

Evidence is exactly the canonical tuple containing:

1. model record `vrg_40c8c6b984345af33de6913ca9025d60d22b0e627b110e974c78270eb941dca7`;
2. model record `prg_c06e49bef910d073a6af206d884a1bb68c0b9baa1cdb1d698d0c35c61025e057`;
3. owner declaration `VP-001 fixture authority explicitly declares that the existing synthetic hotend-temperature variable and the existing synthetic extruder-unit interface are associated in the as-designed lifecycle view; illustrative fixture only.`

The public builder must produce:

```text
record id: vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49
stored bytes: 1184
stored SHA-256: 95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e
29-record revision: mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

Any mismatch is a blocker; the golden values are never updated to fit an
unexpected result.

## Gate 0 — accepted baseline and administrative status

1. Verify branch `vp001`, exact accepted base, and a clean worktree.
2. Read the accepted VP specification, ADR, plans, matrix, and module guidance.
3. Record Slice C owner acceptance in a separate status-only commit.
4. Freeze the 28-record revision, PT artifact SHA-256, every existing model
   record byte, every historical membership/revision, and the untouched local
   settings file.

## Gate 1 — red-first fixture and artifact tests

Before the authoritative append, add tests that pin:

- the exact one-record VPA contract, ID, canonical file bytes, and SHA-256;
- exactly 29 current records and exactly one `vpa_`, with zero `vpw_`;
- the explicit `PRE_VP001_REVISION`, `VP001_MODEL_RECORDS`,
  `VP001_MEMBERSHIP`, and final current revision;
- byte identity for all 28 predecessors and unchanged non-model fixture trees;
- replay of all explicit 9/10/11/14/16/18/28 memberships;
- not-declared/registered-empty VP results at the 28-record boundary;
- asserted/healthy exact, reverse, and assertion results at 29 records;
- the accepted bound-state demonstration and raw provenance;
- exact disclaimer, warnings, deterministic artifact bytes, size, and hash.

Run the focused tests against the 28-record ledger and retain the expected
missing-VPA, old-revision, and missing-artifact failures.

## Gate 2 — mandatory disposable rehearsal

1. Hash all 28 committed record files.
2. Copy those exact files to a disposable model-ledger directory and compare
   every copied byte to its source.
3. Build the fixed VPA once through `build_record()` and verify its expected ID.
4. Append it through `ModelStore.append()` to the disposable store.
5. Load and replay the explicit 29-member set through public APIs.
6. Verify count, kind distribution, same-owner closure, one parentless healthy
   root, zero conflict/correction/withdrawal, file size/hash, final revision,
   exact/reverse/assertion queries, and all predecessor bytes.
7. Record the disposable path and manifest for independent integrity review.
8. Do not touch the committed ledger until the reviewer approves the rehearsal.

## Gate 3 — authoritative public append

Reload the exact rehearsed typed VPA from the disposable model, then append it
to `models/demo-printer` only through `ModelStore.append()`. Require the real
stored file, ID, canonical bytes, hash, revision, membership, and query outcomes
to equal the approved rehearsal. Never edit an existing JSON record.

## Gate 4 — explicit history and query demonstration

Keep the existing 9-, 10-, 11-, 14-, 16-, 18-, and 28-record membership tuples
unchanged. Add only:

```text
PRE_VP001_REVISION = the accepted 28-record PT-001 revision
VP001_MODEL_RECORDS = the one approved VPA ID
VP001_MEMBERSHIP = tuple(sorted((*PT001_MEMBERSHIP, *VP001_MODEL_RECORDS)))
CURRENT_REVISION = the accepted 29-record VP-001 revision
```

Never derive a historical membership from directory enumeration, prefixes,
timestamps, or append order. The 28-record replay must remain same-owner and
`not_declared`; the 29-record replay must expose one asserted, healthy root.
Both reverse queries and the assertion disclosure must agree with the exact
query, while the other PT port remains registered-empty for VP associations.

## Gate 5 — read-only state demonstration

Compose the committed 29-record model, committed `demo-printer` bindings, and
the accepted complete three-occurrence Moonraker timeline at
`2026-08-07T20:30:00+00:00`. Require the outer result to be `associated`, the
nested association to be asserted/healthy, and the independently computed
variable state to carry one attached candidate whose latest occurrence is the
accepted `60.4` evidence received at `2026-08-07T20:00:18+00:00`.

The nested association, variable state, and temporal occurrence must equal the
corresponding direct public queries. The observation remains attached only to
the variable. The port supplies no temporal selector, locator, value, or
occurrence.

## Gate 6 — deterministic VP disclosure artifact

Use the established test-owned canonical JSON convention: sorted keys, compact
separators, ASCII encoding, and one trailing newline. Carry the exact disclaimer
and warnings; base and final revisions/memberships; 28 predecessor hashes; the
complete VPA and file hash; authority/context/evidence; exact and reverse query
findings; assertion disclosure; 28-record replay; composed state; binding,
model, and temporal provenance; exact occurrence/raw/checksum chain; and a
content checksum. Keep model revision, binding revision, and cutoff explicitly
separate.

Generate twice locally and require byte equality. Regenerate independently in
fresh base-only and all-extras checkouts at the final HEAD, and require the same
byte length and SHA-256 in every column. The accepted PT artifact must continue
to replay `PT001_MEMBERSHIP` and retain SHA-256
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.

The implemented artifact is 17,824 bytes with SHA-256
`a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`.
It includes the exact variable and owner registrations, binding membership,
declaration and resolution citations, applicability, state classifications,
and temporal provenance required to reconstruct the disclosed attachment path.

## Gate 7 — adversarial and preservation review

Fail on any extra/missing VP record, any VPW/correction/root, endpoint/context/
authority/evidence/time/note substitution, prior-byte mutation, inferred
evidence, enumerated history, reversed historical status, PT artifact change,
nondeterministic ordering, disclaimer change, provenance omission, real-world
engineering implication, runtime change, or fixture growth outside the one VPA.

Independent reviewers must confirm fixture/ledger integrity, canonical identity,
history, query semantics, state separation, artifact determinism, import
isolation, and exact scope before final verification.

## Gate 8 — verification

Run focused Slice D and complete VP tests; complete model-kernel and model-state
suites; PT/demo, identity-binding, temporal, and affected downstream suites;
architecture/import-isolation checks; the complete repository suite; fresh
base-only and all-extras clean checkouts; focused OCP/STEP and PDF suites;
backend compilation; `git diff --check`; and branch/worktree topology checks.
Run a sandbox-denied loopback case separately with permission when required.

## Reviewable commits

1. `docs: record VP-001 Slice C acceptance`
2. `docs: add VP-001 Slice D implementation plan`
3. `test: add VP-001 Slice D fixture reds`
4. `data: add bounded VP-001 demonstration`
5. `test: pin VP-001 disclosure artifact`
6. bounded adversarial test/documentation repairs when genuine defects exist
7. `docs: record VP-001 Slice D review status`

## Mandatory disclaimer

> This is an illustrative synthetic VP-001 association fixture. It does not describe or claim any real printer wiring, signal routing, connector, protocol, sensing location, measurement location, data path, flow, command, control, influence, causality, behavior, compatibility, safety, correctness, activity, or operating condition.

Shared ownership, names, Moonraker data, CAD or geometry, PIF tokens, PCN
topology, and existing observations did not create the association. Displaying
variable state beside a port is not a claim that an observation occurred at
the port; it does not mean the value occurred at, originated at, travelled
through, or describes the port.

## Stop condition

Stop when Slice D is implemented, independently adversarially reviewed,
dual-clean-checkout verified, committed, and awaiting final owner acceptance.
Do not declare VP-001 owner accepted, begin behavior evaluation, or broaden the
demonstration beyond the one approved synthetic VPA.
