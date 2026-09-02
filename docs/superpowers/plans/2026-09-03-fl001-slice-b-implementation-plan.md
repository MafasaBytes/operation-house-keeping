# FL-001 Slice B Implementation Plan

Date: 2026-09-03

Status: owner-authorized Slice B plan; implementation in progress

## 1. Authority and boundary

Implement only Sections 18–20 and 29.2 of the accepted FL-001 final
synthesis, from the owner-accepted Slice A commit
`0071b5599f7d3a52f74573a37163ecc50f51dff8` and its documentation-only
acceptance successor. The work adds exactly four read-only `ModelQueries`
methods and their exact carry-once public results. It adds no assessment,
occurrence, observed/commanded/calculated flow, traversal, fixture, identity,
or authoritative ledger record. Slice C remains absent and Slice D remains
unauthorized.

## 2. Baseline and preservation capture

Before production edits, preserve the accepted Slice A report digest, flow
golden IDs/canonical bytes, authoritative 34-record membership and revision,
explicit historical memberships, and accepted PT/VP/BH/ST artifact hashes.
Run the focused Slice A architecture/canonical/store preservation suite and
both working-tree and milestone whitespace checks.

## 3. Red-first public contract

Add exact-equality tests for the four method signatures; seven status/literal
aliases and their declared order; nine result contracts and field order; and
the exact package exports. Prove the four forbidden aliases and all other
forbidden flow-evaluation/traversal names are absent. Capture the failing
collection before production changes.

## 4. Shared authoritative derivation

Refactor only the minimum private PT payload seams needed for PCN/PIF support
so existing PT query results and flow support rows use one lifecycle truth.
Implement one flow payload derivation for registration, exact-context
declaration, participant-port collection, and assertion disclosure. Support
pins remain exact record identities and never retarget to a successor.

## 5. Carry-once result contracts

Add immutable strict models whose outer result carries one
`ModelQueryMaterial`. Nested rows carry strict indices and derived scalars
only. At validation, inspect the supplied graph, rebuild all nested content,
validate exact membership and revision through the accepted kernel, derive
the complete expected payload from the rebuilt `LoadedModel`, compare every
field, then bind private material access. Perform no ambient or store access.

## 6. Lifecycle, support, and context tests

Build disposable public-API worlds covering every declaration conclusion,
lineage summary, ordered finding, same-root fork/convergence, independent-root
corroboration/disagreement, selective withdrawal, historical revival, every
reachable RC1 activity/health combination, and rejection of the unreachable
`inactive/current` pair. Cover exact PCN topology and all PIF role relations,
alignment precedence, stale pins, exact-context isolation, `view_independent`
non-wildcard behavior, registered-empty port results, and direct/collection
parity.

## 7. Hostile and deterministic hardening

Exercise missing/extra/duplicate/reordered/substituted/wrong-kind/boolean
indices; forged material, revisions, records, anchors, contexts, roots,
groups, findings, support rows, activities, alignments and conclusions;
hidden extras/private state, hostile object graphs, stale IDs, and
store-independent validation. Reproduce exact serializations across reversed
record order and multiple hash seeds. Repair only reproduced Slice B defects
within the accepted vocabulary.

## 8. Commits and independent review

Use bounded commits for (1) plan plus red-first public contract,
(2) result/query implementation plus focused semantic tests, and (3)
adversarial/deterministic repairs. Obtain independent architecture,
backend-contract, and adversarial reviews; Codex owns synthesis and repairs.

## 9. Verification and report gate

Run focused FL-001 A–B, model-kernel, affected downstream,
architecture/import-isolation, full repository, compilation, historical
replay, artifact preservation, and fresh base-only/all-extras columns. Rerun
only an environment-denied loopback test under the established permission
procedure. Write the completion report, keep it as the sole final untracked
file, and stop for exact Slice B owner acceptance.

