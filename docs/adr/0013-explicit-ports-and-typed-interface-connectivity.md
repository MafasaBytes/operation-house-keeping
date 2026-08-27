# ADR-0013 — Explicit ports and typed interface connectivity

Status: PT-001 Slice A, including the qualified-token repair, is owner accepted.
PT-001 Slice B, including the public-contract repair, is owner accepted at
`ec9ea7d8c20016e267fae16a2554d5e7f1a0ebce`. Slice C is implemented and
adversarially reviewed; awaiting owner acceptance.

## Context

The accepted kernel represents entities, variables, constraints, relationships,
semantic declarations, and revision-bound model knowledge, but it cannot name an
interface independently from its owning entity or distinguish topology from
ordinary entity relationships. PT-001 must add those facts without changing any
accepted record kind or implying flow, behavior, compatibility, or causality.

## Decisions

1. `PortAnchor` is a pure `system_identity` value (`prt_` plus UUID4 hex) with
   `anchor_id`, `namespace`, `display_name`, and optional `role_name`. It embeds
   no owner or engineering claim.
2. `PortRegistration` (`prg_`) permanently binds the complete anchor to exactly
   one registered owner entity with nonempty evidence. Ownership has no context,
   correction, or withdrawal. A different owner requires a new port identity.
3. All PT records extend the existing model ledger and `mrv_`. Existing `rel_`
   endpoints remain entity-only. There is no PT store or composition module.
4. `PortInterfaceDeclaration` (`pif_`) independently declares exactly one of
   `interface_domain`, `direction_role`, or `interface_type` under an exact
   `AssertionContext`. Domain and type tokens have distinct serialized
   `token_kind` discriminators; their `system_id`, `system_edition`, and `code`
   fields are bounded `LocalIdentifier` values. Comparison is exact across all
   four serialized fields, with no vocabulary inference, equivalence, or
   conversion. Direction is one of `input`, `output`,
   `bidirectional`, or `non_directional` and implies no flow.
5. `PortConnectionAssertion` (`pcn_`) is a positive unordered hyperedge over
   2–64 distinct registered ports. Duplicate endpoints are rejected before the
   already-unique tuple is sorted. It means only common-interface participation.
   Independent roots may corroborate; corrections preserve endpoints and context
   and remain within one derived root.
6. `PortCompatibilityDeclaration` (`pcm_`) records only an explicit
   `declared_compatible` or `declared_incompatible` claim for one unordered pair
   and exact context. Its nonempty basis cites one PIF per endpoint for every
   selected dimension in the normative dimension/endpoint order. Citation
   validity is membership-structural, never chronological. Slice B computes
   citation staleness for its selected immutable revision.
7. `PortClaimWithdrawal` (`ptw_`) may withdraw only `pif_`, `pcn_`, or `pcm_`.
   Its target field is `withdraws`, matching `RelationshipWithdrawal`. It is
   uncitable and means only “no longer asserted in this revision.”
8. Registration, lineage, endpoint, evidence, citation, withdrawal, and
   content-ID closure are validated for append, load, and explicit replay. All
   currentness is membership-relative; timestamps and file order never rank.
9. PT-001 has no negative topology, traversal, flow, behavior, variable-port
   association, diagnosis, safety judgment, control, or committed fixture.
   Slice B adds read-only queries directly to `ModelQueries`; it adds no store,
   composition module, or writes. Slice C may append exactly ten synthetic demo
   records only after its owner gate.
10. Slice B's normative results are `PortLookupResult`, `EntityPortsResult`,
    `PortInterfaceResult`, `ExactConnectionSetResult`, `PortConnectionsResult`,
    `SharedConnectionsResult`, `PortAssertionDisclosureResult`, and
    `InterfaceCompatibilityResult`. Exact/shared topology disclose endpoint
    admission independently from `unknown | asserted | inactive`; incident
    topology discloses port registration independently from that conclusion.
    Entity ownership absence is `owner_not_registered`. Compatibility endpoint
    admission is one requested-order aggregate (`both_registered`,
    `left_not_registered`, `right_not_registered`, or `both_not_registered`).
    Assertion lookup, assertion activity, and containing-lineage health remain
    separate. Implementation-oriented pre-acceptance result names are not
    public aliases.
11. Slice C appends exactly two `prg_`, six `pif_`, one positive two-port
    `pcn_`, and one `pcm_` to the synthetic demo model after a public-API-only
    disposable rehearsal. It freezes all prior bytes and the explicit
    eighteen-record historical membership. Its deterministic disclosure is a
    test-owned documentation artifact, not a runtime renderer or new model
    record.

## Consequences

Pre-PT records and revisions replay unchanged. The kernel gains five additive
record kinds and immutable indexes but keeps its dependency boundary of
`system_identity`, stdlib, and Pydantic. A port persists only when accountable
evidence declares the same enduring interface locus; names, ownership, firmware
addresses, connector types, geometry, CAD paths, and source identifiers never
prove continuity. Replacing the owning entity always requires new port anchors.

The Slice C fixture is governed by this mandatory disclaimer:

> This is an illustrative synthetic PT-001 fixture. It does not describe or claim any real printer wiring, connector, protocol, pinout, electrical design, behavior, operating activity, flow, influence, causality, safety property, correctness, or operating condition.

Geometry does not create its ports; CAD and Moonraker do not establish its
connection; token equality does not establish compatibility; direction
admissibility does not establish flow; and explicit compatibility remains a
declared synthetic claim.
