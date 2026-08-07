# ADR-0006: shared identity contracts, opaque anchors, and an append-only JSON binding ledger

Date: 2026-08-07
Status: Accepted (project owner; original design + two correction passes)

## Context

`data_sources` (immutable evidence) and `temporal_state` (rebuildable
source-native timeline) are accepted; `SourceSubjectRef` and
`SourcePropertyRef` deliberately remain unresolved. IB-001 must answer
which canonical entity a source-native subject represents and which
canonical variable a source-native field refers to — without hierarchy,
inference, fuzzy matching, or rewriting evidence. Identity decisions are
durable human knowledge, not a disposable projection.

## Decisions

1. **Shared `system_identity` contracts package.** Canonical anchors
   (`EntityAnchor`, `VariableAnchor`) live in a tiny, contracts-only,
   zero-dependency package that both `identity_binding` and the future
   model kernel import. Rejected: anchors owned inside `identity_binding`
   (forces the kernel to depend on binding machinery or re-own IDs — a
   dependency reversal); references to an external registry (does not
   exist; a dummy dependency). Ledger concerns (authority, recorded_at,
   notes) live in `identity_binding.AnchorDeclaration`, keeping anchors
   pure values.

2. **Opaque UUID-backed anchor IDs** (`ent_`/`var_` + 32 lowercase hex),
   with `namespace`, `display_name`, and optional `role_name` as separate
   NON-identifying fields, and a minimal four-value `referent_kind`
   (physical_instance | logical_instance | type_definition | unknown).
   Rejected: curated role-bearing IDs (`…/extruder-unit`) — they weld
   identity to role, so replacement hardware must either inherit the ID
   (falsifying identity) or take a history-leaking suffix. Rejected:
   name-hash IDs (couple identity to names while adding nothing). A
   replacement physical component always receives a new anchor. Committed
   fixtures use fixed UUID constants for determinism.

3. **Append-only JSON authority + derived in-memory index.** One
   write-once, pretty-printed JSON file per ledger record
   (`records/<record_id>.json`), atomic temp+rename, single-writer
   assumption stated honestly, all-or-nothing binding-set validation, no
   locks pretended, no SQLite in IB-001 (a derived index would follow the
   TS-001 rebuildable pattern if scale ever demands it). Rejected: SQLite
   as authority (binary in git — hostile to review, hand recovery, and
   clean checkout); git-edited declarative documents (in-place edits
   destroy the runtime-visible audit trail). The demo binding set is
   committed to the repository; runtime sets live outside it in the same
   format.

4. **Content-derived record IDs at full checksum strength.**
   `<prefix>_<full 64-hex SHA-256>` over the validated model's canonical
   serialization: sorted keys, compact separators, `record_id` excluded,
   timestamps UTC-normalized at validation and serialized with Python's
   `+00:00` ISO form (equal instants under different offsets hash
   identically), enums as strings, discriminated unions carrying their
   discriminator. IDs are schema-versioned (the hash covers
   `schema_version`), tamper-evident, idempotent, and Windows-path-safe.

5. **Revision replay over exact membership.** `BindingRevision` carries
   the canonically sorted `record_ids`, `record_count`, and
   `binding_set_id`; `revision_id` = `rev_` + full SHA-256 over the set id
   plus sorted membership. The store validates and reloads an explicitly
   supplied membership from the still-present append-only records, making
   earlier resolutions explainable after later appends. `recorded_at` is
   audit-only and never selects winners. Knowledge-time queries ("the
   revision as of date X") are explicitly not provided in IB-001.

6. **Strict applicability and conflict semantics.** Discriminated
   boundaries (declared | unbounded | unknown), half-open `[start, end)`
   intervals on the `ingestion_received_at` axis, and a three-valued
   membership algorithm (IN/OUT/UNKNOWN) feeding an eight-case, non-overlapping
   resolution algorithm. `bound` requires positive establishment;
   unknown applicability yields the structurally distinct
   `applicability_unknown` with candidates outside the authoritative
   field; a differing-target UNKNOWN prevents `bound`; OUT assertions
   never block or compete; conflicts and ambiguity are never resolved by
   recency, timestamp, or authority rank; there is no present-day
   interpretation mode. Correction is supersession; real-world
   replacement is applicability closure plus a new anchor — never
   rebinding in place. Two closures on one assertion invalidate the set.

## Consequences

- The future kernel gets a stable identity namespace to key typed nodes
  by, with no IB-001 decision to reverse; hierarchy and relationships
  will be edges between existing anchors.
- Every resolution is fully explainable from its own structured result
  (assertions, authorities, lifecycle links, closure causes, revision
  membership) without searching the ledger.
- Historical observations can never be silently claimed by a later
  binding; the address-vs-occupant problem is handled by disjoint
  declared intervals.
- The full spec is
  `docs/superpowers/specs/2026-08-07-ib001-identity-binding-design.md`.
