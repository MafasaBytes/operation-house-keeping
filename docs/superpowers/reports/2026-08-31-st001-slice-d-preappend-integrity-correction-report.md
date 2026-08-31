# ST-001 Slice D Pre-Append Canonical Integrity Correction

Date: 2026-08-31

Status: bounded disclosure correction complete; candidate awaiting renewed
owner approval; authoritative append prohibited

Branch: `st001`

Committed HEAD: `2f51abe7ffbef473cc9265b7bac62488974b3a01`

Accepted Slice C HEAD:
`f2c6e4e12c3004615e3b0a6f321f6c2b3edec7d6`

## 1. Outcome

The demonstrated defect was real and disclosure-only. The rehearsal helper
used `record.model_dump(mode="json", exclude={"record_id"})` and then compact
JSON encoding to populate fields named `canonical_payload`,
`canonical_payload_bytes`, and `canonical_payload_sha256`. Pydantic JSON mode
rendered the only UTC timestamp with `Z`, while the model kernel's normative
identity algorithm renders UTC with `+00:00`.

The helper now derives every field named canonical directly from:

- `backend.model_kernel.canonical.canonical_payload(record)`;
- `backend.model_kernel.canonical.canonical_bytes(record)`.

It also discloses the exact normative canonical byte string and verifies each
record through `compute_record_id(record)` and `verify_record_id(record)`.

No identity was reminted. No semantic input, record ID, stored record byte,
append order, membership, or revision changed. No authoritative append was
performed.

## 2. Failing-before evidence

A new regression test was added before changing generation and run against the
then-current frozen manifest. It failed exactly at the first SRG payload:

```text
assert disclosed["canonical_payload"] == normative_payload
Differing items:
{"recorded_at": "2026-08-31T12:00:00Z"}
!=
{"recorded_at": "2026-08-31T12:00:00+00:00"}
1 failed
```

The prior mislabeled hashes were:

- SRG: 1007 bytes,
  `63ba8cc94e615772925c8a871e320095191998629a74820bc8dc7eebd41c586a`;
- STD: 1164 bytes,
  `f7d78ffcce5a8e37ac1131674c80961c6860893717044ac83681ec8a574ef32e`.

Neither hash equaled its record-ID suffix. The test therefore fails against
the old owner-gate artifact even though the records themselves are valid.

## 3. Exact corrected canonical contract

| Record | Normative bytes | Normative SHA-256 | ID suffix equal | `compute_record_id` | `verify_record_id` |
|---|---:|---|---|---|---|
| `srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a` | 1012 | `ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a` | yes | exact frozen ID | true |
| `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0` | 1169 | `d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0` | yes | exact frozen ID | true |

For each record, the legacy disclosure bytes and normative bytes are directly
unequal. Replacing the sole `recorded_at` terminal `Z` with `+00:00` in the
legacy bytes makes them directly equal to the kernel canonical bytes. The
normative bytes contain `+00:00`, contain no timestamp-terminal `Z`, and are
exactly five bytes longer. This proves timestamp representation was the only
canonical-payload discrepancy.

The corrected manifest and candidate disclosure both carry the normative
payload object, exact UTF-8 byte representation, byte count, SHA-256,
recomputed record ID, and verification result for each candidate record.

## 4. Unchanged candidate identities and semantics

The frozen identity and record invariants are unchanged:

- StateAnchor:
  `sta_ec739d80d5a843d28a91f4cf96de3883`;
- SRG:
  `srg_ebd6195325325e67aaa911f06c27aa3d454908878f6091690cdc38b2041de60a`;
- STD:
  `std_d787ddfec94485f5348fd6a66097a8e26d77973ff157917b8d0f5c06016564a0`;
- proposed revision:
  `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`.

The StateAnchor was reconstructed from the existing manifest. The minter was
not invoked. The helper contains neither a minter import nor a minter call.

Stored candidate files are unchanged:

| Record | Stored bytes | Stored-file SHA-256 |
|---|---:|---|
| SRG | 1278 | `a0056abafdb5ad51496952721bec4d8eb7ff4a8b562f168c693ab8cd2f964781` |
| STD | 1474 | `5dbc8c57e6dd91a987b1fef7373d6864d20786d19751bc6a822a84dec9574ea6` |

The complete semantic inputs, evidence, authority, notes, recorded instants,
append order, explicit 34-record membership, public query results, source
selector, cutoff, and synthetic disclaimer are unchanged.

## 5. Owner-gate artifact changes

| File | Before bytes | Before SHA-256 | Corrected bytes | Corrected SHA-256 |
|---|---:|---|---:|---|
| candidate identities manifest | 29015 | `85dd1b820df991c2b450996d0747c7edcfa896b36b26160c24cb429c2276fcda` | 31834 | `990807c2b81ad4a8ec256869bdb5271bf54b360132ca3ab063d5e837bcde43f7` |
| candidate disclosure | 505799 | `b9a6663ca1d4a88060a290990e4c025ba0e0d59d2311978e047d302532aab2a4` | 510943 | `23baf7961570aa1eca4c3a7b08e19673c69cfbc53a61e912d86a887f775ef7b9` |
| pre-append rehearsal report | 13081 | `828809ceeadc77486981efed3ea47ced0b97852d1f29ba9912f6897e3332a228` | 13791 | `ac1c6b9922019051d281a5a8cc8bbbd849dfa044d283cc5ea4ff80e3d9b5e7a3` |
| pre-append rehearsal results | 13521 | `c7ca2ac16eacf92aa23705b47e1f51c9c0741af2c13bf9b22572588d43d4e61e` | 13956 | `431137b61d5cbb12d00a6fb15676607834bdec1c3c2c10f66062d2396feb5fa5` |

The corrected manifest's embedded canonical-content SHA-256 is:

`4a3e6826637d932e5c0234eb9b5c2a3c7397f475bad0de0e88524def50782c3c`

The corrected complete reproduction serialization is 485765 bytes with
SHA-256:

`7b2dcbe05108824b0a940ddd65984f49cb44ab599c9a47c0b75b8faed71d2296`

## 6. Fixed-after and deterministic reproduction evidence

The corrected focused suite passed 12 tests. It includes explicit assertions
that, for both records:

- disclosed bytes equal the kernel's normative `canonical_bytes(record)`;
- disclosed payload equals normative `canonical_payload(record)`;
- disclosed SHA-256 equals the record-ID suffix;
- `compute_record_id(record)` equals the frozen record ID;
- `verify_record_id(record)` is true;
- the only legacy/normative byte difference is `Z` versus `+00:00` in
  `recorded_at`.

Two independently initialized disposable roots reconstructed the frozen
anchor and records. The second copied the exact 32 predecessors in reverse
order. Both produced identical canonical payloads, record IDs, stored bytes,
append order, membership, revision, kernel disclosures, CN result, ST result,
artifact bytes, predecessor aggregate, and accepted artifact hashes.

Fresh base-only and all-extras detached clean checkouts independently consumed
the corrected frozen manifest and external minter-free helper. Both produced
the same 485765-byte reproduction serialization and the same corrected
510943-byte disclosure.

## 7. Verification results

| Verification | Result |
|---|---:|
| red-before canonical regression | 1 failed exactly on `Z` vs `+00:00` |
| corrected focused rehearsal | 12 passed |
| corrected implementation-worktree full suite | 3076 passed |
| fresh base-only aggregate | 3028 passed, 35 expected skips, 1 sandbox-denied loopback setup |
| fresh base-only permitted loopback rerun | 1 passed |
| fresh base-only distinct verified total | 3029 passed, 35 expected skips |
| fresh all-extras aggregate | 3063 passed, 1 sandbox-denied loopback setup |
| fresh all-extras permitted loopback rerun | 1 passed |
| fresh all-extras distinct verified total | 3064 passed |
| focused OCP/STEP/PDF paths | 79 passed |
| backend compilation | passed |
| working-tree whitespace | passed |
| full milestone-range whitespace | passed |

The two aggregate errors were only the expected sandbox refusal when opening
the real loopback server. The exact test passed separately in each clean
checkout with local-socket permission.

## 8. Preservation and authoritative boundary

The authoritative demo ledger remains exactly 32 records at:

`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`

It contains zero committed `srg_`, `std_`, or `stw_` records. Its predecessor
file-map aggregate remains:

`eb0b50157837ff33d0f1d67c595ab96c29cd45c61254566da07493622fa69c58`

The protected-tree aggregate remains:

`c39c52cb251d593d8201acaf61bc6bac36839c79dae22466b1bb7e22fc571e08`

Accepted artifacts remain unchanged:

- PT: `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`;
- VP: `a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`;
- BH: `4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.

No authoritative model, binding, interpretation, source, temporal,
structural, PT, VP, or BH fixture changed. No candidate record file was
committed or copied into the authoritative ledger.

## 9. Git and owner gate

No commit, push, merge, rebase, reset, cherry-pick, amend, or history rewrite
was performed. The committed HEAD remains
`2f51abe7ffbef473cc9265b7bac62488974b3a01`.

The candidate manifest, disclosure, corrected reports, helper, and tests
remain untracked owner-gate material. Authoritative append remains prohibited.

Owner approval is required again for the exact corrected owner-gate contract,
followed by separate explicit authorization before any authoritative append.
