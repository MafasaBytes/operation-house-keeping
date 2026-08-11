# backend/structural_evidence

This module records what a structural source reported and how that report
is addressed. It accepts nothing into any model, declares no canonical
identity, mints no anchor, writes no ledger, and nothing here is
engineering truth. The runtime module owns no authoritative store or
ledger. Identity decisions live in identity_binding; model truth lives in
model_kernel.

## Runtime storage

SN-001's runtime module owns no authoritative store, no ledger, and no
revision id. Reconciliation results and proposals are computed and
returned, never persisted. SN-001 milestone work nevertheless produces
durable committed artifacts: the frozen showcase sources, their manifest,
their frozen extraction results, versioned subject-identity rule
definitions, and hand-authored binding and model records. Committed
showcase derivatives are test artifacts, not engineering truth or runtime
authority. The hand-authored binding and model records are engineering
knowledge, and they were authored by a person, not by SN-001 code.

## Rule durability (the K1 contract)

Changes to rule data are content-addressed and necessarily create a new
subject namespace. Changes to the shared rule interpreter or subject
encoder are guarded by a versioned algorithm contract, hand-authored
behavior vectors, and implementation-drift tests; this is enforced by
tests and review, not by construction alone.

`sx1` is the version of the complete subject-generation semantics:
namespace grammar, `apply_rule`, missing-value behaviour, field selection,
comparisons, subject-value encoding, percent encoding, and the
normalization policy — which is none. Any behaviour change to those
mechanics requires `sx2` or later and therefore creates a new identity
domain requiring explicit new mappings.

## Limitations

1. A recorded mapping is an unauthenticated authority claim, never
   evidence that the mapping is correct.
6. Structural mapping applicability is asserted on the ingestion-receipt
   axis only and carries no lifecycle-view validity.
7. A claim whose engineering context is unknown can never be materialized.
10. Anchor ids are uuid4 hex by accepted decision; SN-001 generates none.
12. The raw store is not committed; a committed record citing a raw
    record is a dangling reference from a clean checkout until the
    demonstration regenerates it against pinned golden constants.
14. Changes to the shared rule interpreter or subject encoder under a
    fixed `sx1`/`semantics_version` are guarded by tests and review, not
    by construction.
15. The runtime module owns no store; the milestone's durable artifacts
    are test artifacts and hand-authored records, as published above.
16. A structural mapping is scoped to one `source_id`: the same bytes
    re-ingested under a different source id are a different subject and
    resolve `source_subject_unmapped`.

(Numbering follows the SN-001 spec's limitation list; the remaining
entries land with the slices that introduce their subjects.)

## `resolution_at`

`resolution_at` is a required, timezone-aware instant on the
ingestion-receipt axis — the same axis
`AppliesScope.axis == "ingestion_received_at"` names. It is the instant at
which binding applicability is evaluated, and nothing else. It is not a
model-knowledge cutoff: the supplied model revision alone decides
membership. It is not an observation cutoff. It is not a wall clock:
SN-001 never reads the clock, and the caller must supply the instant. Two
reconciliations differing only in `resolution_at` are different results
with different `inputs_digest` values, even when every finding is
identical.
