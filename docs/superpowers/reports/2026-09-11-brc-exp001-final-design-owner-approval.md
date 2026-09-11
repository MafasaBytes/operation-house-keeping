# BRC-EXP-001 Final Design Owner Approval

## 1. Owner decision and frozen authority

The requesting owner accepts the corrected BRC-EXP-001 design. This record
implements the owner's 2026-09-11 instruction to record design acceptance and
prepare exact Slice A assumption bytes for a later approval gate.

| Frozen design document | SHA-256 |
| --- | --- |
| [Lead proposal](../proposals/2026-09-11-brc-exp001-codex-lead-proposal.md) | `0c830c433674eac130c2c01cb337a4e474eba5d2fa88fc72269e6de656a2bfeb` |
| [Challenger audit](2026-09-11-brc-exp001-codex-lead-proposal-challenger-audit.md) | `65738e0d45ecdc47f9cdaa17bf5890b6337c9d09769ae478320f988d77ce4791` |
| [Accepted synthesis](../specs/2026-09-11-brc-exp001-baseline-reasoning-closure-spike-design.md) | `827381a8280ad89d3d3a506e0f9dd331c82bea169514359f3f3b12125a68a3b2` |

All three are committed byte-for-byte unchanged. The accepted verdict is
`approve_with_corrections`, with zero blockers. The synthesis's 22-entry change
log, all eight owner adjudications, and RC1–RC4/NB1–NB4 dispositions are accepted.

## 2. Accepted corrections and limitations

| Item | Accepted disposition |
| --- | --- |
| RC1 | Canonical semantic hypothesis counting; reject H/T aliases and decoder overlap; preserve genuine distinct meanings with equivalent predictions and granularity disclosure. |
| RC2 | B0 compound gap; separate B1 meanings, B2 population and one-premise controls before attributing prediction/influence gaps. |
| RC3 | Distinct A/B/control schemas and executable public-premise closure, isolated processes, renaming and A-matrix invariance controls. |
| RC4 | Independently retained exact request/result bytes and expected digests; completed-result freezing and validation/recomputation on every read. |
| NB1 | Exact possibilistic minimax arithmetic remains valid only after admission. |
| NB2 | Edge-case arithmetic is not architectural evidence. |
| NB3 | Tiny ceilings require later base/BH/at-limit/one-over measurement and trace-bound proof. |
| NB4 | Protected witnesses establish synthetic public composition, not real-device knowledge or H/T predictions. |

The selected algorithm remains `finite_compatibility_minimax/v1`, with no
probabilities and secondary policy `none` for the primary request. Full supplied
matrix coverage, semantic identity, total decoders and epistemic classification
remain mandatory. Empty-support outcomes retain their exact surprise disclosure.

## 3. Present authorization and hard stop

Authorization is limited to pre-execution premise freezing, documentation/status
checks, a local branch named `brc-exp001`, and the specifically requested design
documentation commit. Slice A execution is not authorized. Exact assumption bytes
are candidates until the owner explicitly approves their digest and authorizes
execution. An `approver` field names the intended requesting experiment owner;
it does not represent an approval already granted to those bytes.

No experiment driver, implementation, tests, result bytes, disposable BRC model
world, production package, solver, durable engineering identity, ledger record,
authoritative fixture, or ADR is authorized in this preparation task. Slice B
remains unauthorized. Nothing is pushed or merged.

The owner explicitly authorizes committing the execution-plan document now,
superseding only the synthesis's earlier default temporary-plan retention and
no-documentation-commit instructions. No algorithm, schema, ceiling, premise,
future execution-report retention rule, or architecture boundary is changed.

## 4. Repository and preservation checkpoint

Before branching, tracked `main` was clean and the only ordinary untracked
files were the three frozen BRC design documents. `HEAD = origin/main =
debcffec5a77ae270bbf8822f82ef1aa7556c5bd`. The local branch was newly created
from that checkpoint; origin/main remains unchanged.

Live model load and exact-membership replay agree: 36 records at
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
The 236 unique ordered model-kernel exports retain digest
`77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252`.
FMA/FMW/FCD/FCW remain 0/0/0/0. Protected report and six tree inventory digests
match synthesis section 1. FC remains accepted; CS/DI remain closed application
policy/composition; CV backend additions remain cancelled and delivery deferred.

The existing FC-only witness is rechecked at 14,677 bytes and
`a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca`.
The integrated witness retains the accepted 174,490-byte pin
`1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e`
in unchanged reports. As already disclosed in the accepted synthesis, its
historical temporary harness is unavailable; no fresh integrated replay is
claimed. Historical full-suite evidence is not rerun or relabelled.

ADR-0001 through ADR-0022 are unique and contiguous. ADR-0023 remains absent,
unallocated and unreserved. No authoritative revision or protected artifact changes.

## 5. Checkpoint artifacts and subsequent gate

The [Slice A execution plan](../plans/2026-09-11-brc-exp001-slice-a-execution-plan.md)
distinguishes this five-document design commit, the three subsequent untracked
candidate artifacts, later disposable driver/tests, and the separately authorized
final execution report. No additional status-file edit is necessary: this record
and the plan supply the exact current status without changing accepted decisions.

The candidate assumption JSON will use only the assumption-bearing field
projection of the accepted ModeARequest schema, with its exact Mode A
discriminator and algorithm. It will not fabricate the required lower roots or
lower commitments, and is not an executable ModeARequest. Its manifest discloses
that boundary, candidate status, mathematical expectations and pending lower
admission/resource checks. There is no alternate executable schema.

Stop after preparing and checking the three untracked artifacts. The next owner
gate is approval of the exact assumption bytes plus explicit Slice A execution
authorization. Slice A acceptance and a separate later authorization are required
before any Slice B work.

END OF BRC-EXP-001 FINAL DESIGN OWNER APPROVAL
