# L1 implementation receipt: COMPLETE (one attempt)

Date 2026-10-22. Authority: owner ID-1, OD-K2, and the revised L1 implementation only.
Governing addendum `2957475768335f09685ac910c493b78c8dac9eb9c87825b63eaecd13a5d67e5e`;
patch block `7bf112ec71a285bc1037eca0a90f86653e1c9ab05ecabbf63b177031a8ca4d07` (22,043 B).

## Outcome

| Target | Before | After |
|---|---|---|
| `applications/bounded_decision_workflow/measurement_build.py` | `172efff4…5d25`, 4,627 B | `5c3619e4e9435bbc9ced21898bbb9806161dbab03a265f8221376ed574520267`, 4,987 B |
| `applications/bounded_decision_workflow/release_identity.py` | absent | `2dfb4fca907ebd8dfc3c36dc22b27c93dfa0f98b5ddddffed65a69ddc2d28092`, 6,458 B |
| `tools/release/release_identity_record.py` | absent | `b30a2cd8341fae2544e0f8ded48a90ab35cbe2ebf25cea73f3d08dfd9cfe6bf6`, 2,460 B |
| `tests/applications/bounded_decision_workflow/test_release_identity.py` | absent | `807b08edf51d4edad978623619337268ef933d89e5e7929cedf1613f4904825c`, 10,414 B |

- **Order:** preserved copy, `tools/release/` (the only directory created), the three new files, then
  `measurement_build.py` via temp file, fsync, rename and directory fsync.
- **Temporary file:** none remains.
- **fsync:** every fsync returned without error. Durability on drvfs is unverified, and the four-file
  set is not atomic.
- **Pre-image preserved:** `2026-10-22-t1-linux-ext4-l1-implementation-preserved-measurement_build.py`
  (`172efff4…5d25`, 4,627 B).

## Preservation (read-only)

- **Passed:**
  - the four exact post-images;
  - no temporary file;
  - no unexplained change among the 1,616 baseline files in applications/backend/tests/tools outside the
    targets;
  - accepted checkpoint unchanged (`record.py` `b790cf22`, test `f60636f5`, launcher `228509f4`);
  - sealed packages and records unchanged: vertical slice 3/3, K amendment 8/8, route-b 6/6,
    correction 10/10, R1 16/16, regression 14/14, plus the addendum, disposition and PARTIAL application
    records;
  - protected Git identities unchanged (HEAD, index `43dca87c`, packed-refs, repair-branch ref and main
    `07055c63`);
  - demonstration gates closed.
- **Limits:**
  - Protected Git identities are only the named items; no all-ref check was made.
  - The /proc view was WSL-only.
  - The K source manifest and Route B `current_sources` now describe historical `measurement_build.py`
    bytes, intentionally. They were not edited.

## Records

- **STATUS:** `2026-10-22-t1-linux-ext4-l1-implementation-STATUS.json`
  `b04e72447ab88907d14845f4fdebebbeeab39ee12a965c8f9a6de196a59523be`, 2,952 B, outcome COMPLETE.
- **ACCOUNTING:** `2026-10-22-t1-linux-ext4-l1-implementation-ACCOUNTING.json`
  `647f64a72540b4a97696521729ca45b04cb30854b50a7953c84c32c7379cf6fb`, 7,864 B / 8,192 allocated. It records
  ID-1 and OD-K2.
- **This RECEIPT:** measured outside itself.

## Capacity

- **Grant:** 7 files, 1 conditional temporary file and up to 3 directories, with up to 131,072 logical /
  262,144 allocated bytes partitioned from the remaining byte allowance. That leaves
  13,276,326 / 27,975,680 outside the partition.
- **Used before this receipt:** 6 files and 1 directory, 35,135 logical / 49,152 allocated. The directory
  is charged at 4,096; drvfs reports 0.
- **Unused and still reserved:** 2 directories, the conditional temporary file (terms retained) and the
  rest of the partition.
- **Untouched:** the held K-amendment application reservation and its conditional capacity.
- **Not measured:** process, thread and time use is unknown, and host/session records are a separate
  scope.

## Confirmations

- **Not done:** no tests, collection, imports, syntax checks, candidate or release-tool execution, release
  generation, installation, builds, application/provider execution, K, controls, signals, Git, staging,
  commits or merge. No `RELEASE-IDENTITY.json` was created.
- **Tests:** the twenty L1 tests remain unexecuted.
- **Still ungranted:** validation, commit, authoring, packaging and deployment implementation.
- **Attribution:** R1's 141 results keep their tested-byte attribution, and no acceptance migrates to
  L1. D-COV stays unenacted and handoff deferred.

END RECEIPT
