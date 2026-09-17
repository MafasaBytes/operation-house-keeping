# Maintained admissibility — Slice 3 completion

2026-09-17. **Implemented and verified; owner acceptance pending.** This report
does not grant final milestone acceptance or authorize later work.

## Authority and exact heads

Verified starting administrative HEAD/main
`590a7b76beb43157bec5f0bc59d37649aeb7a798`, corrected allocation commit
`8e905bca9d215b0d1e770470d44acb817c586d5b`, and Slice 2 completion SHA-256
`19dadad30819bf3a6ae2210336359536e8c1d02799ff00a61828045d3b180c39`.
Read the complete governing design, amendment, consolidated plan, allocation
correction and completion report. Verified the recorded 545-test scope, red/fixed
evidence, four archived measurement sets, complete closure recipes, work arithmetic
and three-world comparison; the 105-file authority recovery also passed. No tests
were rerun merely to record acceptance.

[Slice 2 owner acceptance](2026-09-17-admissibility-slice2-owner-acceptance.md) was
committed separately at `5e7278e85dc23acf59b88435598e03a717f32a69`.
Its SHA-256 is `0baffc254160dfd902b18f2e8e592651c7e39a9fda6f3828b815160167eccdb2`.
The prior completion report and evidence remain byte-exact. This acceptance record
also records the owner's separate Slice 3 authorization; historical approval-gate
statements were not rewritten.

| Implementation/test commit | Scope |
| --- | --- |
| `6cc84bc7c56eb5413de291a0f0923545ec6aa7be` | Governed persistence and owning semantic replay |
| `b69ffb8fc33c4dd87c61e8e64cb77c6303934bf2` | Explicit governed CLI, documentation and command harness |
| `e3f56001296971211187e9836a04010c5b2c4cdc` | Retained build-record schema/policy validation |
| `1b8d7ffd7761f6842cf8ced5a3356179c8d9f9bc` | Durable command evidence and hostile replay twins |
| `63e83ead741ab06bef148ce56a77c39f4b9051ed` | Exact maintained semantic-mismatch diagnostic |
| `41f19685786077dbf2c085420c801dbbf38e784d` | Actual scoped cache-reuse counter in physical evidence |
| `250da5e66479ee1dd2e7c24cd81905509ffe5969` | Bounded inventory recheck independent of timestamp resolution; **final tested HEAD** |

The administrative HEAD adding this report is identified in the final receipt and
by `git log -1 --format=%H --` this file. It cannot be embedded in its own bytes.
It is not a newly tested executable: even a documentation-only commit changes the
exact build witness. Historical replay requires the recorded checkout/environment;
the application does not restore, fetch or silently substitute them.

## Implemented responsibilities and exclusions

Slice 3 owns fixed-file persistent capture/recovery, manifest-last exclusive
publication, successful governed CLI composition and end-to-end semantic replay.
It reuses Slice 1 admission/build binding and Slice 2 complete in-memory validation
and 23-row review. It introduces no backend record, dependency, resource amendment,
new numerical policy, authority service, generic rule engine or joint projection.

The explicit `governed-evaluate`, `governed-verify`, and `governed-replay` commands
never fall back to legacy evaluation. Evaluation requires an independently supplied
exact selection pin and complete content-addressed objects. Current, hypothetical,
working and comparison paths use the same owning gate. All required historical
gates are assessed before projection. No supplied validation/permission flag is
accepted by the public operations.

Persistence retains six payloads plus manifest: I, B, complete typed Q/D/S/A/T,
template/basis and prior closure, R/trace, build and physical-work evidence. Prior
containers recover byte-exact through approved recipes, not floating digests.
Replay validates the complete captured target/ancestors, re-admits and recomputes
their results, and requires byte-equal R/trace and closure. It reuses the owner's
validated in-memory material rather than reconstructing ancestors twice or skipping
validation. The current replay root is not misclassified as another prior.

The completed receipt has mandatory permission, disposition and matching result/
manifest commitments. Denial completes with exit 0 but blocks all current numerical
projection. Technical refusal is nonzero, with bounded stderr and no success receipt.
An admitted no-feasible-action result remains distinct from both.

Retained build records have their own closed schema and pinned contract/policy/lock
checks. Byte verification does not assert executable availability, authority
currentness or numerical truth. Replay additionally requires the exact executable.
Historical D1 replay after D2 still denies X and retains
`currentness=relative_to_captured_selection_only`, not new working adoption.

Publication uses existing no-follow regular-file/ext4/XFS primitives, exclusive
directory/file creation and rename, and payload/file/directory/parent fsync ordering.
There is no overwrite, automatic cleanup or resume. Capture checks bounded final
inventories as well as metadata; directory timestamps alone are insufficient.
This is bounded capture stability checking, not continuous filesystem monitoring.

## Red/fixed evidence and verification scope

[Recoverable evidence](2026-09-17-admissibility-slice3-evidence.json), SHA-256
`e69a2a3e19907de8c52f00bfb56a634b53047c0284fc08f5e2255da698c4693d`, retains commands,
red/fixed records, exact test heads, baseline file commitments and four command
archives. Red development runs are not mislabeled as release-HEAD runs.

Corrections include missing persistence/CLI integration, current-root versus prior
charging, retained publication reservation checks, build-record validation, the
`investigate_integrity` replay retry class, actual cache-counter propagation, and
the directory-inventory race. The latter first failed on real ext4; deterministic
twins then demonstrated failure when directory metadata values alias. Both bundle
and object-directory capture now perform bounded final inventory checks.

A tighter-limit fixture initially expected publication to be reached, but its full
legacy limit map correctly refused earlier at result construction. The assertion
was corrected to accept that specified earlier refusal, not to loosen a limit.
Persistence unit build providers were mechanically given the required record shape;
they remain explicitly synthetic providers, never executable witnesses. Actual
command tests use the unpatched executable builder. Historical fixture bytes and
intermediate runs remain retained. Intermediate zero cache-hit placeholders are
explicitly superseded evidence defects, not measurements accepted by this report.

| Exact tested HEAD | Verification |
| --- | --- |
| `250da5e66479ee1dd2e7c24cd81905509ffe5969` | **163 passed** in 155.66s: all governed Slice 1–3 tests plus focused legacy CLI baseline/replay and usage |
| `250da5e66479ee1dd2e7c24cd81905509ffe5969` | **60 real subprocess commands**, all expected outcomes, on approved ext4 |
| `63e83ead741ab06bef148ce56a77c39f4b9051ed` | Broader governed and legacy S1–S6 scope: **765 passed, 1 skipped**, 685.90s; before the final cache/inventory repairs |
| `b69ffb8fc33c4dd87c61e8e64cb77c6303934bf2` | Earlier broad run: 764 passed, 1 skipped |

The optional unsupported-output-parent probe was not nominated. S7 release and a
full repository suite were not run. The earlier broad result is not represented
as a final-HEAD broad run. Final-head verification covers the changed governed
paths and legacy commands; final release acceptance remains a separate gate.

Final commands include twelve primary evaluate/verify/replay sets, historical
W0/D1-X replay after D2, legacy evaluate/verify/replay, wrong/missing authority,
oversized raw-wire refusal, usage/collision controls, a mismatching historical
build, a rehashed false recommendation, bounded observation, two concurrent
publishers, abrupt pre-manifest exit and capture-race injection. Exit counts are
47 zero, one 2, seven 3, one 4, three 5, and one deliberate process exit 91.
The last is interruption evidence, not an application diagnostic.

The false recommendation passes byte integrity but fails semantic replay with the
exact maintained diagnostic. Two competing publishers yield one success and one
collision. Abrupt exit preserves `.manifest.json.tmp` and payloads, yields no
success, refuses verification as incomplete and refuses overwrite on retry.
Unit faults also cover write/fsync/manifest failures and visible durability-unknown
states. Denied and authority-refused instrumented subprocesses have no projection
planner or policy entries. D2's observer records exactly two permitted policy
entries: W0 and D2-X, never denied D1-X.

Twelve primary evaluations contain **276 slots, 234 performed assessments, 42
blocked slots, 89 required reviews, 25 typed-value changes and 9 comparable numeric
pairs**. Five historical world reconstructions add 115 row slots to that primary
sequence; they are not extra primary cases. W0/J1 select aH; D1-X denies before
current projection; D2-X admits and has no feasible supplied action. The three-world
chain retains 11,847 lower charges, 2,073 references, 304,321 Q/B bytes and 8+0+8
corners. All four finite-table nominations, unavailable evidence, working adoption
and applicability-unknown completion are covered. Unavailable numeric comparisons
remain null changes, never proof of unchanged numbers.

Across duplicate observation/lifecycle runs and replays there are 29 newly published
governed bundles containing 667 current row slots, plus two legacy bundles with
22 rows each. These are not 29 independent proof cases. Technical refusals publish
no semantic rows, even when permitted computation occurred before a later collision,
semantic mismatch or publication interruption. Oracle authorship and shared frozen
law/target/cost assumptions remain same-author; outputs did not generate their own
expected numerical answers.

## Actual resource and retained-byte measurements

The final 6,224-byte executable witness has SHA-256
`6d25dea1635567f4a6838b5252f25d448f1a4194657cb54ba30bbc705f8afafb`.
One identity probe records 210 source read/hash operations / 2,237,942 bytes and
seven contract reads / 160,643 bytes. Repeated startup and retained-record checks
are distinct from Q/B reconstruction; whole-command timings include startup.

| Measured maximum across completed governed operations | Actual | Approved ceiling |
| --- | ---: | ---: |
| Complete seven-file bundle | 355025 | 393216 |
| Build / manifest / physical report bytes | 6224 / 2216 / 1101 | 8192 / 16384 / 8192 |
| Result bytes / nodes | 22372 / 1077 | 32768 / 2048 |
| Trace bytes | 21258 | 32768 |
| Resolved container bytes / nodes | 233679 / 8088 | 262144 / 16384 |
| Lower charges / references / Q/B bytes | 11847 / 2073 / 304321 | 12288 / 2304 / 393216 |
| Prior capture / reconstruction bytes | 304273 / 908056 | 393216 / 1048576 |
| Capture bytes | 659295 | 786432 |
| Charged context nodes / bytes | 126178 / 3646827 | 131072 / 4194304 |
| Graph references / edge visits / expansions | 80 / 80 / 27 | 128 / 128 / 64 |

The existing 128/129-reference twins are covered by final-head tests; historical
64/65 fixtures are not substituted. Extra publication checks and replay-root work
are positively charged; cache savings do not cancel excess. Existing lower/backend
limits and caller-tightened applicable limits remain unchanged. Four pairs is still
a functional scope cap, not a guarantee that every maximal request completes.

Replay preserves deterministic R/trace accounting while retaining independently
checked fresh physical reports. Actual scoped-validation cache hits range 3–15 in
the primary cases (W0 4, D1-X 8, D2-X 15), not a constant placeholder. These count
completed intrinsic-validation-scope reuse, not machine/cache instructions. Full
required reconstruction and contextual checks remain charged. Manifest publication
is prepaid; the report cannot attest its own future fsync. Completion is withheld
until publication returns.

Bounded test observation uses at most 4096 events of at most 512 bytes each per
probe, outside ordinary runtime bundles. The D2 probe records 879 events, maximum
261 bytes; denial/refusal prefixes are separately retained. Directory scans are
independently bounded by their owning fixed file/object counts. No eighth ordinary
bundle file, new operational ceiling or cache-work exemption was added.

The longest timed serial command was 19.79s. The harness's cumulative child usage
records 92.50 user seconds, 21.67 system seconds and maximum RSS 105692 KiB; this is
not isolated per-command RSS or a CPU/RSS capacity guarantee. Fixed request-work
units are not total machine instructions. No throughput, simultaneous-maxima,
power-loss, reboot or XFS durability guarantee is inferred.

## Recovery, preservation and remaining gate

Final execution evidence recovers **467 files from 198 distinct byte objects**,
including inputs, outputs, command journals, instrumentation and deliberate hostile
fixtures. Its raw evidence SHA-256 is
`6a54c36b2d057830c176558b9c8dda9c8896c87a2267c62e674c64aebefec268`.
The report evidence embeds lossless XZ chunks with compressed/raw commitments and
file maps, using existing standard-library compression, not a dependency change.
Decode/verify those bytes; command strings are evidence, not permission to rerun.
Archive recovery is not a claim that intentionally invalid fixtures are admissible.

All earlier runtime directories remain intact, including the early dirty-build
refusal and the run whose oversized tool response was truncated. That truncated
response is not final acceptance evidence; later durable command journals and
archives provide complete recovery. No earlier result was overwritten.

The isolated approved ext4 root is
`/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/governed-slice3-bmXH44`.
Existing environment, provisioning, dependencies, inputs/results and backend
contracts were not modified. Of 1186 pre-existing repository files, 1182 are
byte-identical; only README.md, cli.py, governed_closure.py and governed_review.py
in the application changed as authorized. All 242 original untracked entries are
preserved byte-exact. No ledger mutation, ADR, remote operation, push, merge or
history rewrite occurred.

The final documentation commit contains only this report and its evidence file,
with explicitly inspected staging. Committed bytes, recovery, local links, markers,
whitespace and the original [exact Git-status receipt](2026-09-16-admissibility-first-slice-git-status.txt)
are verified. Tracked worktree/index are clean after that commit.

No known failing final-head in-scope test or unresolved semantic/resource discrepancy
remains. **Owner gate: accept Slice 3.** Any later slice/work and final milestone
acceptance remain separately gated, including any separately requested independent
release review or fresh-checkout release qualification. No automatic historical
environment restoration, physical acquisition or actuation is provided. Local
attestation is not authenticated identity or empirical truth. C remains unresolved/
dossier-only; F historical/analytical; IN-001 and CI-001 remain open and unselected.
No statistical correlation, continuum robustness, physical validity or causality
is established; existing platform/durability exclusions remain.

END OF MAINTAINED ADMISSIBILITY SLICE 3 COMPLETION
