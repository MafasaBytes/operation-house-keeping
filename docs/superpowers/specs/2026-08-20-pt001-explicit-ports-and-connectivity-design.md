# PT-001 — Explicit ports and typed interface connectivity

Status: PT-001 Slice A, including the qualified-token repair, is owner accepted.
PT-001 Slice B implemented and adversarially reviewed; awaiting owner acceptance.
Slice C remains owner-gated. No committed PT fixture is permitted before Slice C.

## Mission and boundary

PT-001 adds stable port identities, permanent evidence-bearing ownership,
per-dimension interface declarations, positive evidence-backed topology, and
explicit compatibility claims to the existing model ledger. It records declared
knowledge only. Connectivity is not compatibility; compatibility is not flow,
behavior, influence, causality, safety, health, correctness, or activity.

The kernel continues importing only `system_identity`, stdlib, and Pydantic.
Existing entity relationships, variables, constraints, observations, bindings,
interpretations, evidence, and historical revisions retain their accepted
meaning and bytes. PT-001 creates no separate ledger, store, runtime composition
module, relationship endpoint generalization, or port-as-entity convention.

## Identity and registration

`PortAnchor` belongs to `backend/system_identity`: `prt_` plus 32 lowercase hex
characters minted from UUID4, with `anchor_id`, `namespace`, `display_name`, and
optional `role_name=None`. It is frozen, extra-forbid, fully revalidated, and
uses the accepted anchor string conventions. It contains no owner, kind,
lifecycle, interface, topology, evidence, authority, compatibility, state,
flow, behavior, or causal field.

`PortRegistration` (`prg_`) embeds `anchor: PortAnchor`, names one
`owner_entity_anchor_id`, and carries nonempty canonical `EvidenceRef` evidence,
`AuthorityRef`, `UtcDatetime`, and conventional `note=""`. Registration is
permanent: no context, parents, correction, or withdrawal. The owner entity must
exist in the selected membership and one port may have only one registration.

Continuity is conservative. Preserve an anchor only when accountable authority
and evidence explicitly declare that the same enduring interface locus
continues. Otherwise mint a new anchor. Names, ownership, firmware addresses,
connector types, geometry, CAD paths, and source identifiers never prove
continuity. Replacing the owner always requires new port anchors. The kernel
validates structure and evidence presence, not real-world continuity.

```text
PortRegistration:
  record_kind: "port_registration"
  schema_version: "1"
  record_id: prg_...
  anchor: PortAnchor
  owner_entity_anchor_id: ent_...
  evidence: nonempty canonical tuple[EvidenceRef, ...]
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

## Interface declarations

`PortInterfaceDeclaration` (`pif_`) is a correctable claim keyed by
`(port_anchor_id, exact AssertionContext, dimension)`. The exact dimensions and
normative order are:

1. `interface_domain`
2. `direction_role`
3. `interface_type`

Bodies are a discriminated union of `InterfaceDomainDeclaration`,
`DirectionRoleDeclaration`, and `InterfaceTypeDeclaration`. Domain and type use
distinct qualified tokens:

```text
InterfaceDomainToken: token_kind="interface_domain", system_id,
                      system_edition, code
InterfaceTypeToken:   token_kind="interface_type", system_id,
                      system_edition, code
```

All three identity components use the existing bounded `LocalIdentifier`
contract. `system_id` admits qualified systems such as `project_local`, `iec`,
`iso`, `opc-ua`, and `vendor.example`; it is not a project-local-only literal.
PT-001 compares all four serialized token fields exactly and performs no
vocabulary inference, equivalence, or conversion.

`token_kind` is serialized and participates in equality, canonical bytes, and
record ID. Body dimension must equal token kind. Direction is exactly `input`,
`output`, `bidirectional`, or `non_directional`; it is an endpoint role only.
Corrections may change value, evidence, authority, note, and recorded time, but
not port, context, or dimension. Parents are a canonical unique tuple within the
same multi-parent correction root. Forks remain conflicted; an all-tip successor
converges them; replay currentness depends only on selected membership.

There is at most one parentless PIF root per lineage key.

```text
PortInterfaceDeclaration:
  record_kind: "port_interface_declaration"
  schema_version: "1"
  record_id: pif_...
  port_anchor_id: prt_...
  context: AssertionContext
  declaration: InterfaceDomainDeclaration | DirectionRoleDeclaration |
               InterfaceTypeDeclaration
  evidence: nonempty canonical tuple[EvidenceRef, ...]
  supersedes: canonical unique tuple[pif_..., ...]
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""

InterfaceDomainDeclaration:
  dimension: "interface_domain"
  value: InterfaceDomainToken
DirectionRoleDeclaration:
  dimension: "direction_role"
  value: "input" | "output" | "bidirectional" | "non_directional"
InterfaceTypeDeclaration:
  dimension: "interface_type"
  value: InterfaceTypeToken
```

## Positive topology

`PortConnectionAssertion` (`pcn_`) carries a canonical endpoint tuple, exact
context, nonempty evidence, correction parents, authority, recorded time, and
optional note. Endpoint processing is normative: validate every supplied ID;
reject every duplicate; require 2–64 distinct endpoints; sort the already-unique
IDs lexicographically; hash and compare the sorted tuple. Canonicalization never
changes cardinality.

The claim means only that all endpoints are asserted to participate in one
common interface connection under the exact context. It carries no direction,
flow, magnitude, activity, state, compatibility, behavior, health, safety,
cause, command, or control. A parentless record begins an independent root.
Independent roots over the same endpoint set/context corroborate. Correction
parents must have one derived root and preserve endpoints/context; cross-root
supersession is invalid. Changing subject requires withdrawal and a new root.

There are no negative topology claims. In Slice B queries: no lineage
means `unknown`; any current tip means aggregate `asserted`, including a forked
root; lineages but no current tips means `inactive`. Lineage health is separately
`healthy`, `conflicted`, or `inactive`. Nothing means disconnected.

```text
PortConnectionAssertion:
  record_kind: "port_connection_assertion"
  schema_version: "1"
  record_id: pcn_...
  endpoint_port_anchor_ids: canonical tuple[prt_..., ...]  # 2..64
  context: AssertionContext
  evidence: nonempty canonical tuple[EvidenceRef, ...]
  supersedes: canonical unique tuple[pcn_..., ...]
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

PCN alone permits multiple parentless roots per subject. Each successor's
parents must all derive to exactly one root. Multi-parent convergence within
that root is valid; cross-root convergence is invalid.

## Explicit compatibility declaration

`PortCompatibilityDeclaration` (`pcm_`) addresses one canonical unordered pair
under one exact context and declares `declared_compatible` or
`declared_incompatible`. It carries nonempty evidence, authority, recorded time,
optional note, correction parents, and a nonempty structured basis.

The basis selects a nonempty subset of the three dimensions. Dimensions
serialize in the normative order above. For each selected dimension, citations
serialize lower endpoint then higher endpoint. Caller permutations canonicalize
identically; duplicate dimensions or citations are rejected. A nonempty
explanatory statement accompanies the structural citations.

```text
PortInterfaceCitation:
  port_anchor_id: prt_...
  declaration_record_id: pif_...

CompatibilityDimensionBasis:
  dimension: "interface_domain" | "direction_role" | "interface_type"
  citations: exactly two PortInterfaceCitation values

PortCompatibilityBasis:
  statement: nonempty str
  dimensions: nonempty tuple[CompatibilityDimensionBasis, ...]

PortCompatibilityDeclaration:
  record_kind: "port_compatibility_declaration"
  schema_version: "1"
  record_id: pcm_...
  endpoint_port_anchor_ids: canonical tuple[prt_..., prt_...]
  context: AssertionContext
  outcome: "declared_compatible" | "declared_incompatible"
  basis: PortCompatibilityBasis
  evidence: nonempty canonical tuple[EvidenceRef, ...]
  supersedes: canonical unique tuple[pcm_..., ...]
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

The accepted public shape places ordered `CompatibilityDimensionBasis`
entries inside `PortCompatibilityBasis`; each entry structurally owns its two
endpoint citations. There is no detached parallel citation collection.

A citation is structurally valid when the cited PIF exists in selected
membership, verifies its content ID, belongs to the cited endpoint and dimension,
uses the exact PCM context, belongs to the carried revision, and occurs once.
Append, load, and replay do not require it to be current. A structurally valid
stale PCM remains loadable. Slice B exposes the unique PCM outcome only when
every citation is the unique active current PIF; otherwise it reports `stale`.
No time, append order, file order, directory state, or hidden history participates.

“Belongs to the carried revision” means the cited record ID occurs in the
explicitly selected membership from which that revision is computed; model
records do not carry a revision field.

PCM lineage is `(canonical pair, exact context)`, with one root and the accepted
multi-parent correction/conflict discipline. Token identity/difference never
produces compatibility or incompatibility.

## Withdrawal

`PortClaimWithdrawal` (`ptw_`) targets exactly one `pif_`, `pcn_`, or `pcm_`.
Its target field is `withdraws`, consistently with the accepted
`RelationshipWithdrawal` contract.
It carries authority, recorded time, and optional note but no evidence. It is
excluded from citable model-record evidence. Unknown, non-PT, `prg_`, `ptw_`,
already superseded, or already withdrawn targets are invalid. A selected
membership may not both withdraw and supersede one target, and successors may
not resurrect withdrawn parents. Withdrawal means only no longer asserted in
that revision, never false, disconnected, or stopped at a time.

There is at most one parentless PCM root per pair/context lineage. A PTW target
must be an unsuperseded current tip and may have only one withdrawal in the
selected membership. Replay that omits the PTW revives the target according to
the remaining supersession graph.

```text
PortClaimWithdrawal:
  record_kind: "port_claim_withdrawal"
  schema_version: "1"
  record_id: ptw_...
  withdraws: pif_... | pcn_... | pcm_...
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

## Canonical/store impact

Add exactly `prg_`, `pif_`, `pcn_`, `pcm_`, and `ptw_` to the model record
grammar, filename rules, discriminated union, adapters, canonical builder,
verification, exports, validating store, and `LoadedModel`. `prt_` is an anchor,
not a model record. `ModelRecordEvidence` may cite the four claim/registration
prefixes but never `ptw_`. Existing record definitions and hashes do not change.

Slice A's public construction surface is the existing semantic
`build_record(record_cls, **fields)` extended to the five new record classes;
there are no additional per-kind builder functions. Public exports add exactly
`PortRegistration`, `InterfaceDomainToken`, `InterfaceTypeToken`,
`InterfaceDomainDeclaration`, `DirectionRoleDeclaration`,
`InterfaceTypeDeclaration`, `PortInterfaceDeclaration`,
`PortConnectionAssertion`, `PortInterfaceCitation`,
`CompatibilityDimensionBasis`, `PortCompatibilityBasis`,
`PortCompatibilityDeclaration`, and `PortClaimWithdrawal`. `system_identity`
adds exactly `PORT_ANCHOR_ID_PATTERN`, `PortAnchor`, and `mint_port_anchor`.

Immutable deterministic indexes cover registration by port; ports by owner; PIF
keys, successors, tips, and withdrawals; PCN roots, ancestry, subjects, incident
ports, successors, tips, and withdrawals; PCM keys, successors, tips,
withdrawals, citations and reverse citations; and withdrawals by target.

## Read-only query semantics

Slice B adds exact port/interface disclosure, exact endpoint-set, incident,
shared-superset, assertion disclosure, and multidimensional compatibility
queries directly to `ModelQueries`. It adds no traversal, store, or write path.
Direction comparison and cross-finding behavior is:

- exact-set lookup matches only the identical canonical hyperedge;
- incident lookup returns every hyperedge containing one requested port;
- shared lookup returns every hyperedge containing the complete requested set,
  including exact equality, without inventing pairwise connectivity;
- no topology root means aggregate `unknown`, any current tip in any healthy or
  conflicted root means `asserted`, and roots with no current tip mean
  `inactive`; root health remains separately `healthy`, `conflicted`, or
  `inactive`;
- domain and interface-type comparisons disclose only `token_identical`,
  `token_different`, `not_declared`, `conflicted`, or `inactive`;
- direction pairing is symmetric: input/output and bidirectional paired with
  input, output, or bidirectional are `admissible`; input/input and output/output
  are `inadmissible`; non-directional/non-directional is `not_applicable`; mixed
  non-directional or unavailable declarations are `indeterminate`;
- explicit compatibility status is `not_declared`, the unique declared outcome,
  `conflicted`, `inactive`, or `stale`;
- cross-finding consistency is `consistent` for declared-compatible plus
  admissible and declared-incompatible plus inadmissible; it is `inconsistent`
  for declared-compatible plus inadmissible and declared-incompatible plus
  admissible; it is `indeterminate` without a unique outcome or a
  determinate/applicable direction result.

These deterministic findings never prove mateability, correctness, activity,
flow, safety, or causality. Slice B results carry the complete selected model
membership once, one revision, and one exact context. Their validators rebuild
the authoritative PT state without store access and reject mixed, reordered,
substituted, stale-ID, `model_construct`, and `model_copy` forgeries.

## Historical replay and exclusions

Every pre-PT explicit membership must reproduce its exact revision and expose no
fabricated port artifacts. Store validation uses selected membership only; never
directory enumeration or chronology. Slice A appends no fixture. Slice C, only
after two owner gates, may rehearse then append exactly 2 `prg_`, 6 `pif_`, 1
`pcn_`, and 1 `pcm_`, evolving the demo model 18→28 while freezing every prior
byte.

PT-001 excludes connection absence, observed state, flow, equations, behavior,
causality, diagnosis, impact, traversal, planning, safety, control, variable-port
association, connection identity, parallel identical-connection distinction,
native-CAD interpretation, ingestion connectors, UI, and new CN predicates.

BH-001 may not implement behavior evaluation until an owner-approved,
evidence-backed association can relate existing entity-owned variables to
registered ports without changing variable identity or fabricating state.
