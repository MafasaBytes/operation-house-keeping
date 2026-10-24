# Rebinding regression correction and Codex validation

Date: 2026-10-23 (Europe/Amsterdam). Authorized by the owner's request that Codex finish the reported rebinding test scope.

## Change

Only `tests/tools/test_t1_rebind.py` changed. The failing provenance regression previously selected a record that was the sole typed referrer to opaque plain-text evidence. Rehashing that record disconnected the opaque payload from the role roots, causing input parsing to refuse before the intended assertions.

The regression now selects a provenance-bearing record without opaque references, using an independent typed-reference traversal. It still checks literal historical digests in copied provenance, rendered-authority lineage, and refusal of a structured stale reference. Assertions were not removed or weakened.

This is a fixture correction, not a parser repair. The reported limitation concerning disconnected opaque objects remains outside this change. No new disposition on producer-written provenance was enacted.

- Test before: `b2ad744af3aa16d1de9ee086869fea81a6a986441cc1a2c23b97693e478ce92e`
- Test after: `88147043aec497792ad6efa10d6dc5a875509c160eaf488014101e92ca6aeda7` (73,374 bytes)
- Tool unchanged: `180858b016b9f6c9459425a10acdb73c06250bc01713d492646b665684172831`

## Validation

One pytest invocation completed: **108 passed in 195.14 seconds**, exit 0. No failed, error or skipped tests were reported.

Selected modules:

- `tests/tools/test_t1_rebind.py` (80)
- `tests/t1_simulation/test_maintained_increment.py` (13)
- `tests/t1_simulation/test_command_integration.py` (15)

Used the existing `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python`, with `-I -B`, plugin autoload disabled, `-c /dev/null`, explicit repository pythonpath, cache provider disabled, fresh basetemp and JUnit capture. Tests generated only temporary synthetic application fixtures. No standalone tool execution or historical workflow run was performed.

The run was bounded by a 300-second TERM timeout with KILL after 3 seconds, a 2 GiB address-space limit, disabled core dumps and an 8 MiB per-file limit. No timeout fired. This was focused development validation, not a repetition of the former admission/preservation harness or an independently qualified environment audit.

Evidence workspace:

`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/t1-rebind-codex-validation-20261023-1`

- `junit.xml`: `f5a0acf82a27464cb01171d4db0f49e2c6b52a27bc710e93911e9f2f70261b38`
- `pytest.stdout`: `5125735abf16e5f09a0fd3e90e2c03d9dea607a4032c24c2c6ebb9485bee7ab0`
- `pytest.stderr`: empty, `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `pytest.rc`: 0
- `time.txt`: resource observations from the run

Two Windows-to-WSL launch setup attempts failed before tests or workspace creation. A quoting-safe encoded stdin launch then started the single pytest invocation. Initial sandbox WSL access was denied; escalated WSL access was subsequently approved. No test retry occurred.

## Preservation and attribution

Claude's earlier 107/108 result remains unchanged in `2026-10-23-t1-rebind-correction-and-validation-RECEIPT.md`, hash `db6dbf8ba59b74bb49eba7e8f8d3f83758e3ef4ad974818b607b8ea5ec2e3f64`, independently rechecked after this run.

Both frozen L2 documents were independently hashed and still match `74a39d87586b50e91fb5862579f28c02f86c498a6fa69e02bfb97e487d059a1b` and `6bca403bf936cf47da0eea373af8b587578a4b995d2b6ffdd7cb48fb1b77425e`.

No application/backend code, authority input, frozen document or existing evidence record was edited. Historical runtime workspaces were not rescanned; no broad preservation claim is made. No Git command, checkout, K, commit or merge occurred. R1/L1 and historical end-to-end attribution remain unchanged; D-P remains open. L2 remains frozen.

Only the test edit, this receipt and the fresh runtime evidence were written. Runtime storage, aggregate process counts and session overhead were not independently accounted; they are unknown, not zero. No held capacity was deliberately repurposed.

END RECEIPT
