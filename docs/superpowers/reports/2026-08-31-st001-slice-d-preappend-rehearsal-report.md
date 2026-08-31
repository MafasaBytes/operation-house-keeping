# ST-001 Slice D Pre-Append Rehearsal Report

Date: 2026-08-31

Status: rehearsal complete; exact candidate awaiting owner approval; authoritative append prohibited

Branch: `st001`

Accepted Slice C HEAD:
`f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6`

Current committed HEAD:
`2f51abe7ffbef473cc9265b7bac62488974b3a01`

Original milestone base:
`0ed77df7ea4870faec1eae9b89668add97aa855d`

## 1. Outcome and stop boundary

The bounded Slice D pre-append rehearsal is complete. One frozen synthetic
`StateAnchor`, one candidate state registration (SRG), and one parentless
candidate state declaration (STD) were reconstructed and appended only in
disposable ledgers. Public kernel, CN, and ST queries produced the required
results. Two independent disposable roots and fresh base-only and all-extras
clean checkouts reproduced the same complete deterministic contract and the
same candidate disclosure bytes.

No authoritative append was performed. The authoritative demo model remains
exactly 32 records at
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`.
It contains zero committed SRG, STD, or STW records. This report, the results
report, the frozen manifest, the candidate disclosure, and the focused
rehearsal support remain untracked owner-gate material.

Work stops here. Authoritative Slice D append remains unauthorized.

### Canonical disclosure integrity correction

This report incorporates the bounded owner-requested correction performed
after the initial rehearsal. The original manifest mislabeled a compact
`record.model_dump(mode="json")` serialization as canonical; that rendered
the sole UTC `recorded_at` field with `Z`. Corrected generation now obtains
every canonical field directly from
`backend.model_kernel.canonical.canonical_payload(record)` and
`canonical_bytes(record)`, which render that same instant with `+00:00`.
The corrected hashes equal the unchanged record-ID suffixes. A dedicated
integrity-correction report records red-before/fixed-after evidence and all
owner-gate hash changes.

## 2. Administrative acceptance record

The repository was inspected before continuing the rehearsal. Two existing
documentation-boundary commits follow the accepted Slice C HEAD:

1. `70d35981b7552d3c2af14dddee34c9fb6eeb0752` —
   `docs: record ST-001 Slice C acceptance`
2. `2f51abe7ffbef473cc9265b7bac62488974b3a01` —
   `docs: clarify ST-001 Slice D authorization boundary`

Together their committed snapshot records Slice C owner acceptance at the
exact accepted HEAD, authorizes pre-append rehearsal only, explicitly keeps
the authoritative append unauthorized, and changes no Slice A-C runtime
behavior. The first commit changes documentation and one documentation
assertion test; the second is documentation-only. Because the owner forbade
amendment, reset, rebase, or history rewrite, this already-existing topology
was preserved rather than consolidated or rewritten.

Both whitespace gates pass:

- working tree: `git diff --check` — passed;
- full milestone range:
  `git diff --check 0ed77df7ea4870faec1eae9b89668add97aa855d..HEAD`
  — passed.

## 3. Existing-manifest recovery and no-remint rule

At the beginning of this execution the candidate manifest already existed at:

`docs/superpowers/reports/2026-08-31-st001-slice-d-candidate-identities.json`

The no-remint rule was applied immediately: allocation stopped, the existing
file was inspected, its canonical JSON and embedded content checksum were
recomputed, and every later rehearsal reconstructed its `StateAnchor` from
that frozen content. The minter was not called during this execution. The
rehearsal helper has neither a `mint_state_anchor` import nor a minter call,
and a focused AST check enforces that boundary.

The frozen manifest records this exact allocation statement:

> The public UUID4 minter was invoked exactly once. UUID4 allocation is intentionally nondeterministic; this manifest freezes the returned opaque identity for all reproductions.

Manifest contract:

- schema version: `1`;
- status: `non_authoritative_candidate`;
- bytes: `31834`;
- file SHA-256:
  `990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7`;
- embedded canonical-content SHA-256:
  `4a3e6826637d932e5c0234eb9b5c2a3c7397f475bad0de0e88524def50782c3c`.

## 4. Frozen candidate contract

The complete frozen anchor is:

```json
{"anchor_id":"sta_ec739d80d5a843d28a91f4cf96de3883","display_name":"Synthetic Region Alpha","namespace":"demo-printer","role_name":null}
```

It is a neutral RFC-4122 UUID version 4 `StateAnchor`. Its name, evidence,
notes, and human-facing metadata contain none of the prohibited state,
equipment, diagnostic, or action vocabulary.

The SRG is exactly:

- record ID:
  `srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a`;
- subject:
  `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`;
- permanent singleton condition:
  `con_4b768cf843f5474cb5e564e31d239a59`;
- condition family: `all_of_constraints`;
- authority: `test_fixture / st001_demo_fixture / manual_declaration`;
- recorded at: `2026-08-31T12:00:00+00:00`;
- normative canonical payload: 1012 bytes, SHA-256
  `ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a`;
- stored file: 1278 bytes, SHA-256
  `a0056abafdb5ad51496952721bec4d8eb7ff4a8b562f168c693ab8cd2f964781`.

The STD is exactly:

- record ID:
  `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0`;
- state anchor:
  `sta_ec739d80d5a843d28a91f4cf96de3883`;
- context: `lifecycle_view / as_operated`;
- exact VCN pin:
  `vcn_2fcac4a3c7b1ce656bddac5348fce9f82d4e3b66907209603fe58eb0b5ba37ec`;
- evaluation basis: `independent_latest_at_or_before_cutoff`;
- parents/supersedes: none;
- authority: `test_fixture / st001_demo_fixture / manual_declaration`;
- recorded at: `2026-08-31T12:01:00+00:00`;
- normative canonical payload: 1169 bytes, SHA-256
  `d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0`;
- stored file: 1474 bytes, SHA-256
  `5dbc8c57e6dd91a987b1fef7373d6864d20786d19751bc6a822a84dec9574ea6`.

Both records contain nonempty, claim-specific synthetic evidence, a neutral
note, a deterministic aware UTC timestamp, and the accepted synthetic
authority. The manifest freezes the complete semantic inputs, full serialized
records, reversible stored JSON, canonical payloads, byte counts, hashes,
append order, memberships, revisions, selector, cutoff, expected results,
artifact contract, predecessor hashes, and accepted artifact hashes.

## 5. Disposable rehearsal architecture

Every rehearsal followed the same public-only sequence:

1. Resolve a safe disposable root and reject any root that could contain the
   authoritative ledger.
2. Inventory all 32 authoritative predecessor files.
3. Copy the explicit accepted 32-record membership byte-for-byte into a newly
   initialized disposable `ModelStore` root.
4. Replay the explicit membership and verify its count and revision.
5. Reconstruct the frozen `StateAnchor` from the manifest.
6. Construct SRG and STD through public `build_record()`.
7. Append SRG through public `ModelStore.append()`, then load and verify the
   33-record state immediately.
8. Append STD through public `ModelStore.append()`, then load and verify the
   34-record state immediately.
9. Replay the explicit proposed 34-record membership.
10. Run public kernel, CN, and ST facades.
11. Generate the disclosure artifact in memory.
12. Reinventory predecessor, protected, and runtime-evidence bytes.

No candidate record file was copied from one root to another. The second root
copied the predecessor files in reverse order and still generated identical
candidate bytes. Candidate record files existed only inside disposable roots.

## 6. Public demonstrations

The public kernel disclosed:

- `state()` — `registered`;
- `state_declaration()` — `declared`, lineage `healthy`, exactly one healthy
  root, agreement finding `one_healthy_root`;
- `states_of_entity()` — exactly one entry for the candidate state and exact
  subject;
- `state_assertion(SRG)` — `found`, permanent/event-shaped registration
  disclosure;
- `state_assertion(STD)` — `found`, `current`, containing lineage `healthy`.

The direct public CN query disclosed:

- current declaration is the exact pinned VCN;
- canonical observed decimal is `60.4`;
- predicate is upper bound `80`, inclusive;
- upper boundary assessment is satisfied;
- verdict is `satisfied`.

The complete public ST classification disclosed:

- state conclusion `declared` and lineage `healthy`;
- declaration alignment `exact_current`;
- condition outcome `satisfied`;
- condition coverage `complete`;
- temporal alignment `not_asserted`;
- execution `executed`;
- computed match `matches`;
- refusals: none.

The exact selector is `moonraker / printer-1 / extruder` with extraction route
`api:moonraker:v1`, item key `printer_objects`, and JSON pointer
`/result/status/extruder/temperature`. The exact cutoff is
`2026-08-07T20:30:00+00:00`.

The selected occurrence was received at `2026-08-07T20:00:18Z`. The STD was
recorded later at `2026-08-31T12:01:00+00:00`. The later model declaration is
applied relative to evidence at the cutoff. The rehearsal does not claim that
the declaration existed at the cutoff or that the observation persisted.

## 7. Deterministic disclosure and reproduction columns

The candidate disclosure is:

- path:
  `docs/superpowers/reports/2026-08-31-st001-slice-d-candidate-disclosure.json`;
- bytes: `510943`;
- SHA-256:
  `23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9`.

The following four columns independently consumed the frozen manifest without
calling the minter:

- implementation-worktree disposable root one;
- implementation-worktree disposable root two, with reverse predecessor-copy
  order;
- fresh base-only detached clean checkout;
- fresh all-extras detached clean checkout.

All four columns were equal for anchor serialization; complete canonical SRG
and STD payloads; record IDs; stored JSON bytes and hashes; append order;
34-record membership; model revision; all kernel disclosures; direct CN
serialization; complete ST classification serialization; artifact bytes,
count, and hash; 32-record predecessor aggregate; and accepted PT/VP/BH
artifact hashes.

The canonical complete reproduction summary is 485765 bytes with SHA-256:

`7b2dcbe05108824b0a940ddd65984f49cb44ab599c9a47c0b75b8faed71d2296`

The proposed 34-record revision is:

`mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`

## 8. Preservation results

The authoritative 32-record predecessor aggregate is unchanged:

`eb0b50157837ff33d0f1d67c595ab96c29cd45c61254566da07493622fa69c58`

The protected model/binding/interpretation/showcase aggregate frozen in the
manifest is unchanged:

`c39c52cb251d593d8201acaf61bc6bac36839c79dae22466b1bb7e22fc571e08`

Accepted artifacts reproduced unchanged:

- PT: 33855 bytes,
  `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`;
- VP: 17824 bytes,
  `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`;
- BH: 122406 bytes,
  `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.

Explicit 9/10/11/14/16/18/28/29/32 memberships replayed at their accepted
revisions and returned structured absence for the candidate state. No model,
binding, interpretation, temporal, source, structural, PT, VP, or BH fixture
was modified.

## 9. Verification summary

- focused candidate rehearsal: 12 passed;
- implementation-worktree complete suite: 3076 passed;
- fresh base-only aggregate: 3028 passed, 35 expected optional skips, one
  sandbox-denied loopback setup;
- fresh base-only permitted isolated loopback rerun: 1 passed;
- fresh all-extras aggregate: 3063 passed, one sandbox-denied loopback setup;
- fresh all-extras permitted isolated loopback rerun: 1 passed;
- focused OCP/STEP/PDF paths: 79 passed;
- backend compilation: passed;
- working-tree whitespace: passed;
- full milestone-range whitespace: passed;
- both detached clean-checkout Git statuses: clean.

The aggregate socket errors were the known sandbox refusal at
`ThreadingHTTPServer(("127.0.0.1", 0), Handler)`. Each exact test passed when
run separately with local-loopback permission. A denied setup is not counted
as a pass.

## 10. Truth boundary and mandatory disclaimer

Names, shared ownership, hierarchy, CAD, ports, VPA, PIF/PCN/PCM, BH
declarations, semantic compatibility, CN satisfaction alone, temporal
correlation, and observation changes did not create the state. Displaying an
observation beside a state does not persist it as state truth.

The disclosure also states the raw-authenticity boundary: ST proves the
internal coherence of carried public results and does not independently
authenticate uncaptured raw payload bytes.

> This is an illustrative synthetic ST-001 state declaration and evidence classification fixture. `matches` means only that the explicitly selected admitted observation satisfied the referenced synthetic constraint under the stated context, cutoff, and revisions. It does not claim that a real printer is currently in this state, that the state is exclusive or complete, that any transition occurred, or that temporal order establishes cause, control, safety, health, diagnosis, correctness, or recommended action.

## 11. Owner gate

The exact candidate contract is fully enumerated in the frozen manifest,
candidate disclosure, and companion results report. None is committed. No
push, merge, rebase, reset, cherry-pick, amend, or history rewrite occurred.

The next action requires two inseparable owner decisions stated explicitly:
approval of this exact candidate contract, and separate authorization to
perform the authoritative 32-to-34 append. Until both are given, no
authoritative append may begin.
