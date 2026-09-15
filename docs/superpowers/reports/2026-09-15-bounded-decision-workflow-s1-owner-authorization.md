# Bounded decision-workflow S1 owner authorization

Date: 2026-09-15

Status: prepared policy, dependency lock and persistent environment approved; S1 implementation only authorized; S2–S7 unauthorized

## Accepted authority

The owner authorizes the first slice of the seven-slice bounded decision-workflow implementation plan on branch `brc-exp001` from checkpoint `ec027add0cb2dae5434c42f67454752eb93f7228`.

Frozen commitments are:

- corrected design: `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`;
- implementation plan: `6686c8add03d2b8e9aae10b51d12553a9af81d7c56f83866d37fbb5ec26e18d5`;
- candidate package: `0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365`;
- candidate manifest: `6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959`;
- readiness report: `3792d9ade000b83c9226d50217b4b35154e8abfc780c39d6d9c3ce797f568d93`;
- persistent-environment report: `4e83517a4ee3ec360ed681c336c71cd94dbf58b76bc98bddc541f5f70c3935e2`;
- environment identity: `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`; and
- retained artifact set: `26e6a7b92ba5167a660a5227d128e4649387d862db7bb73496ad540492a7fba1`.

## Authorized implementation boundary

S1 is limited to maintained code in `applications/bounded_decision_workflow/` and focused tests in `tests/applications/bounded_decision_workflow/` for strict wire/JSON preflight, complete request contracts, authoritative public `StateClassificationResult` reconstruction, exact observed-`T0` admission joins, public decimal reparsing, and complete canonical S1 examples. The approved build-owned limits and counting meanings are immutable and cannot be relaxed by input.

The implementation must use public backend exports and the approved persistent CPython 3.13 environment. It may add narrow documentation and this authorization/completion record. It may not import a deleted experiment driver or alter a backend contract, authoritative fixture, ledger, dependency lock, mount, or system environment.

Raw projection, target/feasibility/selection, decision review, retention/recovery, CLI evaluate/verify/replay, command-level acceptance, release work, IN-001, CI-001, backend extensions and S2–S7 remain unauthorized. Local commits are permitted; push, merge and history rewrite are not.

END OF BOUNDED DECISION WORKFLOW S1 OWNER AUTHORIZATION
