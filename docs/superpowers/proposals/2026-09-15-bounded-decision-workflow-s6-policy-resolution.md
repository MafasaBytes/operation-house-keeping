# Bounded decision workflow S6 — two policy resolutions

## Status and verified checkpoint

Proposed for owner approval only. S6 remains incomplete and unaccepted; S7 remains
unauthorized. This pass changes no implementation, limit, frozen expectation or
retained evidence. Approval of these corrections would permit resuming the existing
S6 scope, not accepting S6 or starting S7.

Verified `brc-exp001` at administrative HEAD
`3f2f698154dc31469fff3abd12bd2b4bb747fd68`, with focused tested HEAD
`94ec124345a18f07f53503572e5cf98740600634`. The intervening commit changes only
the plan's blocked-status paragraph and the S6 report. Tracked/staged state was
clean; all 63 unrelated untracked artifacts were present.

The complete [S6 checkpoint report](../reports/2026-09-15-bounded-decision-workflow-s6-resource-and-cli-completion-report.md)
was read and verified as
`50b80f1d793c7a2bc182c6f24a8b0fe9a13e833f5fdebcee0ebe2b7fe1003f6f`.
Its filename does not imply completion. The [governing design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md)
remains `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.
The current [plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md),
[candidate package](../reports/2026-09-15-bounded-decision-workflow-candidate-package.json)
(`355b169df2805fa09eaba8865eea1a89e02071cc56c302a078677789fad616bf`), and
[manifest](../reports/2026-09-15-bounded-decision-workflow-candidate-manifest.json)
(`6f1c6103cbc834e089c839f6e3a4503e0a6d91408dccb70972f40a628784fb57`)
were checked for the relevant normative clauses and fixed diagnostic forms.

## Decision P1 — non-tightenable failure-control envelope

### Current clauses and contradiction

Design §§3.1 and 10.2 allow every requested limit to equal or tighten its build
ceiling; §11.2 requires one complete compact JSON diagnostic on nonzero exit.
Plan §§5–6 freeze the seven-field diagnostic, 1,024-byte diagnostic-body ceiling
and 512-byte shared stdout/stderr ceiling. The approved numerical ceilings do
**not** already authorize an exemption from caller-tightened limits. The plan's
current gate explicitly says no such exception has been authorized.

[RequestedLimits](../../../applications/bounded_decision_workflow/contracts.py)
admits 1 for both presentation dimensions; [input admission](../../../applications/bounded_decision_workflow/input.py)
does not impose a larger minimum. [CLI main](../../../applications/bounded_decision_workflow/cli.py)
currently writes its failure diagnostic without checking those tightened values.
That provisional implementation is not normative authority.

Independent standard-library canonical encoding of all 42 frozen diagnostics gives
157–248 body bytes (158–249 including LF). `OUTPUT_LIMIT_EXCEEDED` takes 200/201;
`SNAPSHOT_COMMITMENT_MISMATCH` takes 247/248. Thus a one-byte budget cannot contain
the required line. Replacing the original error with another budget error cannot
solve this and would obscure admission precedence.

### Smallest recommended correction

Amend the interpretation of design §§10.2/11.2 and plan §§5–6 as follows, through
an explicit approved addendum rather than rewriting frozen design evidence:

1. Reserve one build-owned **512-byte failure-control envelope per invocation**,
   including its single trailing LF. Diagnostic JSON excluding LF must also be
   within the existing 1,024-byte diagnostic ceiling. This is the existing shared
   presentation ceiling, not 512 additional bytes alongside success output.
2. The envelope cannot be tightened by request data. Request values remain exactly
   as admitted and retained. They still constrain successful receipts, result/trace
   generation, work and any retained refusal bundle. In particular, a one-byte
   successful-receipt budget still refuses before output-directory creation.
   `output_diagnostic_bytes` continues to constrain any retained diagnostic body;
   the terminal failure line alone has the explicit emergency exemption. There
   is no new request field, minimum, default or silently increased caller budget.
3. On failure, stdout is empty and stderr receives exactly one canonical seven-field
   diagnostic plus LF. Preserve the original typed error, exit code, stage and
   precedence even when its body or line exceeds the corresponding caller budget.
   Do not replace a prior admission error merely because its diagnostic needs the
   emergency envelope. Usage/path failures and `verify`, which have no admitted
   request policy, use the same fixed envelope. `replay` uses it even if the retained
   request tightened presentation limits. No partial successful result is emitted.
4. Select/validate bounded diagnostic fields before serialization; do not stringify
   arbitrary exceptions, paths, source contents or cause chains into the line.
   Bound encoding before buffer growth beyond the hard envelope. Do not retry
   semantic computation, publish a refusal bundle, raise another resource exception
   or recursively serialize an error while handling failure-line overflow.
5. If the diagnostic itself is malformed, cannot be encoded, or exceeds the hard
   envelope, emit the pre-encoded constant below once, exit 7. This is an internal
   diagnostic-emission defect, not the expected response to a small caller budget.
   The **proposed** `bundle_state="unknown"` variant of existing `INTERNAL_ERROR`
   avoids falsely asserting absence when publication may already have occurred.
   It adds no field or code; it is a new, explicitly approval-gated state value for
   this fallback only. It performs no filesystem inspection, repair or cleanup.
6. A failed stderr write/flush cannot guarantee a received complete line. Stop with
   exit 7 without another write attempt, traceback or stdout fallback. Any partially
   delivered diagnostic bytes are not a success or bundle-completeness assertion.
   The one-line delivery guarantee assumes a writable channel; no power-loss or
   uncatchable-termination guarantee is introduced.

Exact ordinary resource refusal (201 wire bytes, exit 4):

```json
{"bundle_state":"optional_refusal","code":"OUTPUT_LIMIT_EXCEEDED","exit_code":4,"message_key":"output_limit_exceeded","retry_class":"reduce_input","stage":"output_resource","target":"result_or_trace"}
```

Exact proposed defensive fallback (174 wire bytes, exit 7):

```json
{"bundle_state":"unknown","code":"INTERNAL_ERROR","exit_code":7,"message_key":"internal_error","retry_class":"investigate","stage":"internal_failure","target":"application"}
```

Both lines retain the fixed fields `bundle_state`, `code`, `exit_code`, `message_key`,
`retry_class`, `stage`, `target`. Normal retention failures keep their existing exit 6
and exact state, including `complete_visible_durability_unknown`; they do not use
the fallback merely because the request budget is small. No allowance authorizes
retaining oversized material: if a refusal bundle cannot fit its effective limits,
omit that optional bundle and emit only the bounded terminal refusal.

Compatibility: successful mathematics, policy, admission order and limits are
unchanged. Callers must accept up to 512 failure bytes regardless of their requested
presentation limits; consumers of the defensive fallback must accept `unknown` as
not certifying bundle state. These are new policy permissions, not a claim that the
old contract was satisfied. The eventual implementation/source identity changes;
exact-build replay compatibility is not relaxed and old bundles are not rewritten.

## Decision P2 — honest incomplete-bundle presentation

### Current clauses and contradiction

Design §9.3 says `verify --bundle` reports recognized fixed files and safe bounded
digests for incomplete bundles. Section 11.2 and plan §5 require empty failure
stdout and the fixed seven-field stderr diagnostic. Those fields describe an error,
not an inventory: overloading `target` or `message_key` would change their meanings.
There is no existing field that can honestly carry the promised inventory.

The report's six-payload/no-manifest witness retains a 212-byte failure line; its
straightforward complete filename/digest extension would be 728 bytes and add a
field. Compression or omitting filenames would also create an unapproved format.
Neither truncation presented as complete nor a second line/channel is acceptable.

### Smallest recommended correction

Narrow the CLI reporting promise in design §9.3: `verify --bundle` is read-only and
returns the fixed rejection for incomplete material; it does **not** print a file
inventory. Missing manifest yields exit 3, empty stdout and this 212-byte line:

```json
{"bundle_state":"absent","code":"BUNDLE_INCOMPLETE","exit_code":3,"message_key":"bundle_incomplete","retry_class":"inspect_or_resubmit_to_new_output","stage":"commitment_public_reconstruction","target":"bundle"}
```

An invalid existing manifest yields the existing 208-byte line, exit 3:

```json
{"bundle_state":"absent","code":"MANIFEST_INVALID","exit_code":3,"message_key":"manifest_invalid","retry_class":"restore_authentic_bundle","stage":"commitment_public_reconstruction","target":"manifest.json"}
```

Here `bundle_state="absent"` means **no new output bundle**, not that the inspected
directory disappeared. Both mean rejected input, not verified incomplete content.
Path, file-type and resource errors retain their earlier diagnostic precedence.

Detailed bounded inspection remains available through existing public
[`verify_bundle` / `BundleInspection`](../../../applications/bounded_decision_workflow/retention.py).
When inspection returns, `integrity_state="incomplete_bundle"`, no accepted bundle
kind, and the diagnostic remain explicit. Its `captured` mapping contains only
recognized fixed files successfully captured within the existing limits; a local
caller can compute `len(bytes)` and SHA-256 over those captured bytes. That is an
inventory of captured recognized material, **not** all directory entries, a trusted
manifest, semantic validation or source authentication. A vanished entry may not be
captured; an unsafe/oversized entry can refuse inspection altogether. No partial
inventory is promised after that refusal. Unknown files are not read for contents.

The directory and its recoverable bytes remain in place for owner inspection and
manual resubmission to a new destination. No new field, command, output file,
inventory serialization, capacity increase or automatic cleanup is proposed.
This preserves S5 behavior and narrows only the unimplementable CLI presentation
promise. Manifest-last completeness is still neither whole-directory atomic
visibility nor power-loss durability. Byte integrity remains distinct from replay
reconstruction and recomputation.

## Exact acceptance obligations after approval

These are specifications, not tests executed in this pass. Retain the three
[original conflict witnesses](../../../tests/applications/bounded_decision_workflow/test_s6_policy_conflicts.py)
and checkpoint commits as red evidence; add approval-traceable conformance assertions.
Real command checks use isolated directories on the approved persistent ext4
workspace, never existing inputs/results. All refusal checks require empty stdout,
exact diagnostic fields/exit, at most 512 stderr bytes including LF, no partial
success, and unchanged input/collision targets.

| Case / existing coverage | Adverse input and exact expected disposition | Nearest valid twin / independent check |
| --- | --- | --- |
| P1-a / RES-2, CMD-2 | Baseline with only `output_stdout_stderr_bytes=1`: exit 4, exact 201-byte `OUTPUT_LIMIT_EXCEEDED`, output absent. | Same request with sufficient receipt allowance: exit 0, empty stderr, valid bundle; admitted limit remains unchanged in each case. |
| P1-b / OBS-3, RES-2 | Baseline with only `output_diagnostic_bytes=1` and stale snapshot commitment: exit 3, exact 248-byte `SNAPSHOT_COMMITMENT_MISMATCH`; no public-reconstruction bypass or output bundle. Repeat with both presentation limits 1: same admission error wins. | Repair only snapshot reference while keeping diagnostic limit 1 and sufficient receipt budget: successful baseline. Restore only diagnostic budget in the hostile case: identical refusal bytes. |
| P1-c / RES-1 | Receipt budget measured line length minus 1 refuses before publication; exact length permits success. Diagnostic budgets one byte below/exactly the ordinary diagnostic body length yield the same original error, with emergency use only needed below. | Compare canonical bytes and independently count UTF-8 body versus LF-inclusive wire bytes. Enumerate catalogue and all bounded target/state variants; all ordinary lines must fit 512. |
| P1-d / CMD-2 | Trusted fault seam supplies malformed/over-hard-envelope diagnostic or encoder failure: one exact 174-byte fallback, exit 7, no recursion or arbitrary contents. Failed stderr sink: exit 7, no second write. | Same seam supplies a valid ordinary diagnostic: preserve its exact code/exit. Normal writable sink receives one line. Exercise a post-publication fault: fallback says unknown, never absent or successful; existing files remain untouched. |
| P1-e / RET-4, REP-1 | Tight-budget replay uses the same refusal policy after normal build/reconstruction checks. Normal directory/parent-fsync faults retain exit 6 and `complete_visible_durability_unknown`, not fallback. | Matching successful replay to a fresh destination and no-fault publication retain existing semantics. Re-run exits 2–7 for exact fields/channel behavior; tight limits do not reorder errors. |
| P2-a / RET-5 | Remove only manifest from isolated valid six-payload bundle: API returns incomplete with six captured files; CLI exact `BUNDLE_INCOMPLETE`, exit 3, no inventory. Empty directory gives same CLI refusal and empty API capture. | Original manifest-valid bundle: exit 0 byte-verification receipt. Compare every captured byte and independently calculated hash; no file is changed by either inspection. |
| P2-b / RET-5 | Replace manifest with canonical `{}`: exact `MANIFEST_INVALID`, exit 3; API remains incomplete. | Restore original manifest bytes: verification succeeds. Corrupt manifest is not trusted merely because its own digest is available. |
| P2-c / PATH-1, RES-1 | Recognized fixed file replaced by symlink: exit 5 `PATH_FINAL_SYMLINK`; same file oversized: exit 4 `INPUT_WIRE_LIMIT_EXCEEDED`. No inventory or file contents leak. An unknown file in a no-manifest directory is not captured or opened for content. | Regular bounded file twin returns incomplete inspection; recognized-file captures agree byte-for-byte. A complete bundle with extra entries remains invalid under existing S5 rules. |

For P1-c, hard-envelope 512/513-byte guards use bounded serializer unit tests, not
invented valid catalogue entries. Malformed diagnostics are trusted fault injection,
not newly accepted caller input. Test both equal and tightened successful budgets;
retain rejection of budget relaxation. Any optional refusal retention must be tested
separately against caller limits, not counted as covered by terminal emission.

## Inspection, preservation and owner gate

This pass read the full checkpoint and relevant design/plan/resource/CLI/retention
contracts, inspected current implementation and conflict tests, checked Git scope
and digests, and independently counted canonical diagnostic bytes with Python's
standard library. It did not invoke the workflow, rerun tests, touch the runtime
workspace, install dependencies or modify any frozen input. Existing tests remain
reported evidence, not new verification. Preservation checks matched all 912
pre-existing tracked/untracked file commitments. HEAD and the index are unchanged;
the 64 untracked files are the original 63 plus this proposal. Local links, marker
and whitespace checks passed. No backend work or broader investigation follows.

Two approval questions:

1. Approve P1's fixed, non-tightenable 512-byte terminal failure envelope, preserving
   typed diagnostics and caller success/retention limits, including the specified
   bounded `INTERNAL_ERROR`/`unknown` fallback and nonrecursive sink-failure behavior?
2. Approve P2's explicit narrowing of incomplete CLI verification to its existing
   fixed exit-3 diagnostic, with detailed bounded captured-file inspection available
   only through the existing S5 API and no new CLI field, channel or limit?

After approval, record the policy addendum and resume S6 implementation and focused/
affected verification under its existing authorization. Neither this proposal nor
its approval substitutes for a completed S6 acceptance report. S7 stays unauthorized.

END OF BOUNDED DECISION WORKFLOW S6 POLICY RESOLUTION
