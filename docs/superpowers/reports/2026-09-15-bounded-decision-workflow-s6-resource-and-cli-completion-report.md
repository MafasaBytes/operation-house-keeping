# Bounded decision workflow S6 — resource/CLI status and consolidated discrepancies

## Status: blocked, not complete or accepted

S5 is accepted. S6 has maintained implementation and real subprocess evidence, but
two conflicting presentation requirements need owner adjudication before S6 can
be completed. This is the single consolidated discrepancy/completion-status record,
not a claim of final application delivery. S7 remains unauthorized.

## Verified authority and commits

Started on `brc-exp001` at administrative HEAD
`e38d7d73d6922257b73d62cbb30d89ee8bcfadaa`. S4 acceptance is
`f4f9748f560d878b01e83dc071be781a309099d9`. Verified the S5 tested implementation
`702a4cbd143950e4fc2e6d724760e0a2723301f2`; only report/plan documentation followed it.
The unchanged [S5 completion report](2026-09-15-bounded-decision-workflow-s5-retention-and-recovery-completion-report.md)
has SHA-256 `a2d8307c8d8fcaf9a5a7a313d8534bae6d55684f136d742f42e358d0aa5dcc90`.

The governing [design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md),
complete [plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md),
S5 [correction record](2026-09-15-bounded-decision-workflow-s5-retention-fixture-correction-report.md)
and completion report were read. The design remains
`54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`.

| Commit | Scope |
| --- | --- |
| `0b1d9011f95699910140e5b147060200c724cce0` | Separate documentation-only [S5 acceptance](2026-09-15-bounded-decision-workflow-s5-owner-acceptance.md), separately authorizing S6. |
| `dec65d68afdfb263e69d347dd2d0e33ebd1baef1` | Initial S6 command/resource/build implementation, version lock, red-first tests. |
| `61d216855e4d15d983d42781fb787fcda330fc88` | Ordinary presentation-budget and malformed-prior repairs; exact synthetic examples and invocation documentation. |
| `5814f22411f09f26a26cb6c10fb47bc08f09a315` | Correct resolved-input resource diagnostic and two test recipe/bootstrap defects. |
| `da68c64059b005e16c33374bee8941d548b4ad50` | Bounded prior-bundle reads/file counts; explicit policy-conflict witnesses. Full affected-run implementation HEAD. |

Final focused tested HEAD: `94ec124345a18f07f53503572e5cf98740600634`.
This changes only S1's historical no-entrypoint test assertion relative to the
full-run HEAD; application/backend source is identical. The administrative commit
containing this report/plan status follows it and is not a new tested build. Obtain
its exact ID with `git log -1 --format=%H --` followed by this report's path.

S5 acceptance confirmed the recorded 597-test selection, red/fixed evidence,
archive recovery and real concurrency/interruption coverage. It reran 139 S5/S4
filesystem/correction/recovery tests, passing in 13.31s, against a fresh test root.
Manifest-last completeness remains distinct from whole-directory atomic visibility
and power-loss durability; no accepted limitation was removed.

## Implemented S6 boundary and actual evidence

The plan's S6 scope is immutable resource policy, incremental counters, the
`evaluate`/`verify`/`replay` module command, exact diagnostics and real subprocess
coverage. [Invocation documentation](../../../applications/bounded_decision_workflow/README.md)
and complete canonical [request](../../../applications/bounded_decision_workflow/examples/request.json)/
[public snapshot](../../../applications/bounded_decision_workflow/examples/snapshot.json)
are now maintained. Their digests remain the prepared baseline commitments
`24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125` and
`782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f`.

- `evaluate` captures ext4 input bytes, lexically preflights them before allocating
  their object graphs, calls accepted S1–S4 admission/projection/policy/review, and
  publishes through S5. Current condition, admitted observation, assumed effects,
  raw predictions, target, feasibility, selection and 22 review decisions remain
  separate. Real subprocesses cover baseline, unavailable, uncertainty, ties,
  missing cost, no-feasible, stale/public reconstruction refusal, resource refusal,
  collision, permission failure and prior target/cost comparisons.
- `verify` retains S5 byte-integrity meaning; it does not establish semantic truth.
  Its incomplete-result presentation is one of the unresolved contracts below.
- `replay` checks the actual build witness, reconstructs and recomputes all selected
  and prior worlds, and checks complete semantic bytes before new-path publication.
  Rehashed forged results do not pass replay. Rehashed source/lock/Python build
  substitutions remain byte-verifiable but refuse replay. A stored successful
  hash comparison is never used as the computational oracle.
- S4 exposes already recomputed ancestor views to S6, avoiding a second uncharged
  evaluation of every prior. S5's public signatures/default ceilings remain intact;
  application-local adapters enforce tighter aggregate prior/file and retained-bundle
  limits, including manifest bytes, before successful publication.
- Build identity records committed application material, public-module hashes,
  CPython/dependency/lock identities and policy commitment. It is a witness, not
  executable authentication. The version-only lock exactly matches the approved
  raw lock digest `7c87f0d7a3f12c271311cc0c33e59025e0161c37f16336901a0764b4330c0817`;
  installation remains tied to separately retained hash-verified artifacts.

The frozen candidate expectations remain independent mathematical/policy evidence.
Prepared output hashes are not misreported as emitted runtime hashes: the actual
result adds the design-required build/count/admission detail; actual trace rows
retain the effect operands and corner derivation. Nine result sections and the three
trace top-level fields remain as designed. Exact runtime identity and replay tests
compare retained actual bytes, not those preparation-only anticipated digests.

## Consolidated blocking findings

### S6-P1 — refusal envelope versus caller-tightened budgets

Design §§3.1/10.2 and the accepted request contract allow every limit dimension to
be tightened. `RequestedLimits` accepts positive integer 1 for both
`output_stdout_stderr_bytes` and `output_diagnostic_bytes`; actual public application
parsing confirms this, with unchanged valid model/evidence premises. Design §11.2
simultaneously requires a complete JSON diagnostic line on every nonzero exit.

Independent canonical arithmetic: the existing `OUTPUT_LIMIT_EXCEEDED` diagnostic
is **200 bytes**, or **201 bytes including its required newline**. Even the smallest
frozen catalogue diagnostic is 157 bytes before newline. No complete required
diagnostic can fit an admitted one-byte budget. The current error path emits the
complete diagnostic under the immutable build envelope, exceeding the caller's
one-byte limit. That is a disclosed provisional behavior, not an approved exception.
The first witness reaches output-budget refusal; the second uses the existing stale
snapshot control after accepting a one-byte diagnostic budget.

**Owner decision required:** explicitly define whether failure diagnostics use a
non-tightenable build-owned control envelope, or define minimum admissible
presentation/diagnostic budgets and the envelope used to reject smaller requests.
Silently truncating JSON, suppressing the required line, or claiming the one-byte
budget was honored would violate the other commitments. No cap was raised and no
schema minimum/exception was invented here.

### S6-P2 — incomplete inspection versus the frozen failure shape/channel

Design §9.3 requires `verify --bundle` to report recognized fixed files and safely
bounded digests for incomplete bundles. Section 11.2 requires empty stdout on
failure and one fixed diagnostic on stderr. The frozen seven-field diagnostic
shape has no inspection field; the shared stdout/stderr ceiling is 512 bytes.

The retained witness removes only the manifest from an isolated six-payload bundle.
The S5 API captures all six files without changing them. The actual command returns
only `BUNDLE_INCOMPLETE` (212 bytes including newline). Adding a straightforward
complete filename-to-SHA-256 inventory produces **728 bytes**, exceeding 512 and
changing the frozen diagnostic shape. The current command therefore does not deliver
the required incomplete inventory, even though it correctly refuses promotion.

**Owner decision required:** define an approved bounded inspection representation
and channel (including any partial/aggregate summary rule), or explicitly narrow
CLI incomplete reporting and leave detailed inspection to the S5 API. Any altered
diagnostic shape, channel rule or ceiling requires approval; none is selected here.
No service, backend extension or new dependency is needed to answer this decision.

These are the complete independently confirmed semantic/policy conflicts from this
sweep. [Three executable witnesses](../../../tests/applications/bounded_decision_workflow/test_s6_policy_conflicts.py)
retain both sides of the contradictions. Their passing assertions demonstrate the
conflicts; they are **not passing S6 acceptance tests**.

## Ordinary repairs and preparation drift (not architectural gaps)

The two initial subprocess tests failed because `__main__` did not exist (6.18s),
then passed after implementation (16.79s). Twenty command-branch tests passed in
163.57s. Fourteen independent lexical/census tests passed in 4.19s, including all
68 recovered candidate objects and hostile/escaped Unicode and resource twins.

Two further red-first checks failed in 19.18s: a caller-tightened successful-receipt
limit was checked too late, and a malformed rehashed prior became `INTERNAL_ERROR`.
They were repaired and both passed in 18.06s. This repaired successful-receipt
publication timing, but did not resolve S6-P1's failure-envelope policy.

An expanded run found five ordinary failures (11 passed): two test recipes had not
applied their declared context/129-digit mutations, a resolved-input serializer
reported an output-stage resource error, and two fault bootstraps failed to accept
the entrypoint's keyword argument. All were repaired without altering model,
admission, numerical, policy or dependency semantics. The subsequent full run also
exposed S1's historical assertion that no command entrypoint exists; S6 authorization
uniquely supersedes that assertion while retaining the exact S1 public input/export
checks. Original red code and results remain recoverable from preceding commits.

There is nonblocking preparation drift: RES-2-raise's frozen recipe calls the error
`REQUEST_LIMIT_RELAXATION`, whereas accepted S1 emits `REQUESTED_LIMIT_RELAXATION`
with its existing dimension-specific target and profile-stage precedence. S6 keeps
S1 authoritative. Candidate/oracle bytes were not silently rewritten; this spelling/
envelope reconciliation is mechanical follow-up, not permission to reorder validation.
The broad RES-1 recipe is not proof that every hard cap admits a complete semantic
world; lexical/counter twins and successful tightened-limit command cases are
reported separately from complete workflow acceptance.

The complete affected selection at `da68c64059b005e16c33374bee8941d548b4ad50`
returned **653 passed, one failed in 517.25s**. The only failure was the obsolete
S1 no-entrypoint assertion; 650 functional tests and three conflict witnesses
passed. The assertion correction preserves all S1 admission/export requirements.
At `94ec124345a18f07f53503572e5cf98740600634`, the focused recheck passed all
five tests in 29.33s: the corrected assertion, baseline evaluate/verify/replay,
and the three conflict witnesses. There was no second full-suite run; unchanged
application source and the exact test-only delta are recorded rather than claiming
a full green run that did not occur. All observed ordinary failures have fixed
checks; the two owner-policy conflicts remain unresolved.

The full selection was the application test directory plus
`tests/constraint_evaluation/test_decimal_parser.py`,
`tests/state_classification/test_architecture.py` and
`tests/semantic_compatibility/test_isolation.py`, using
`PYTHONDONTWRITEBYTECODE=1`, the approved interpreter, `-o addopts=''`,
`-p no:cacheprovider`, and a fresh `--basetemp` beneath the test root below.
Final focused verification selects S1's public-surface test, S6's real baseline/
replay test and the three conflict witnesses. No unrelated full production suite
or S7 clean-checkout reproduction was run.

A read-only census of 39 integrity-consistent S6 test bundles (including controlled
rehashed adversarial examples, not all semantically accepted evidence) found byte
maxima: request 17,227; snapshot 84,979; resolved input 224,672; result 13,688;
trace 12,652; build 3,751; complete bundle 356,300. Those remain within the unchanged
build ceilings. These are execution-corpus measurements, not a final release/resource
acceptance claim and not evidence that caller-tightened refusal budgets are honored.
Complete final policy conformance must be rechecked after the owner decisions.

## Environment, preservation and gates

All command inputs/results/corruption/interruption fixtures were confined to fresh
children of `/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/s6-cli-NJ312t`.
The approved interpreter is CPython 3.13.11 in `environments/cp313-bdw001`.
`findmnt` outside the sandbox confirmed `/dev/sdc`, ext4, rw. Provisioning verified
environment `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`
and all ten artifacts, set commitment
`26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`.
No installation, mount change, repository relocation, WSL restart or power-loss test.

The 899-file starting digest inventory preserves all 63 unrelated untracked
artifacts. Existing runtime inputs/results and dependencies were not test
destinations. Candidate package/manifest, historical copies, design/review,
accepted reports, backend contracts and authoritative ledgers remain unchanged.
Only scoped application/test and status/report paths were staged. Local links,
digests, example canonicalization, whitespace and exact commit scope were checked.

The owner gate is **resolve S6-P1 and S6-P2, then resume/complete S6 verification**,
not accept S6 now. S7 clean-checkout reproduction, full release measurements and
final application acceptance remain unauthorized. No empirical accuracy, physical
execution, causal truth, generated alternatives or global planning is claimed.

END OF BOUNDED DECISION WORKFLOW S6 RESOURCE AND CLI COMPLETION REPORT
