# VP-001 — Explicit variable-to-port association

Status: VP-001 Slices A, B, and C are owner accepted. Slice D is implemented
and adversarially reviewed; awaiting final owner acceptance.
Slice B is owner accepted at
`81179700513bb671cf9955c6a5d7163e3bcc7e1b`. The bounded fixture is exactly one
parentless VPA and no VPW, correction, or additional root.

## Mission and boundary

VP-001 adds an explicit, evidence-backed relationship between an existing
registered variable and an existing registered port without changing either
identity or ownership contract.

The normative meaning is:

> In the stated AssertionContext, an accountable authority declares, with the cited evidence, that this registered variable and this registered port—both owned by the same registered entity—are explicitly associated.

This means only that the selected model membership contains an explicit
positive association claim. It does not assert that an observation occurred
physically at the port; that the port owns the variable; that a value passed
through the port; input, output, sensing, reporting, command, or control;
topology or connectivity; interface compatibility; flow, activity, influence,
causality, or behavior; correctness; or safety.

Shared ownership is an admission constraint. It never creates an association
without an explicit `vpa_` record.

VP-001 adds no anchor, ledger, store, generic relationship endpoint, association
role, negative assertion, or runtime composition module in Slice A. All records
belong to the existing model ledger and participate in the existing `mrv_`.
The model kernel continues importing only `system_identity`, the standard
library, and Pydantic.

## Owner-gated delivery

1. **Slice A — claims and kernel validation.** Add the two record kinds,
   canonical identity, builders, public exports, validating store integration,
   immutable indexes, evidence closure, lifecycle, and historical replay. Add
   no queries, state composition, or fixture records.
2. **Slice B — read-only model queries.** Add the exact association and reverse
   discovery methods plus authoritative result contracts. No state composition
   or fixture mutation.
3. **Slice C — read-only bound-state composition.** Add the accepted composition
   to the existing model-state layer. Slice C is required for VP-001 completion
   but starts only after Slice B owner acceptance.
4. **Slice D — bounded synthetic demonstration.** Append exactly one `vpa_` to
   evolve the demo model from 28 to 29 records and create a deterministic
   disclosure artifact.

Every slice stops for owner validation.

## Record contracts

The sketches below use existing repository contracts and validation
conventions. They do not introduce a new record base class or identifier
framework.

```text
VariablePortAssociation:
  record_kind: "variable_port_association"
  schema_version: "1"
  record_id: vpa_ plus 64 lowercase hexadecimal characters
  variable_anchor_id: str matching existing VARIABLE_ANCHOR_ID_PATTERN
  port_anchor_id: str matching existing PORT_ANCHOR_ID_PATTERN
  context: existing AssertionContext
  evidence: nonempty canonical tuple[EvidenceRef, ...]
  supersedes: canonical tuple[vpa_..., ...]
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

`VariablePortAssociation` is frozen, extra-forbid, and fully revalidated. It
contains no embedded variable or port, owner field, association anchor, role,
arbitrary association label, value, unit, variable semantics, PIF token,
topology, compatibility, temporal cutoff, state, or behavior.

```text
VariablePortAssociationWithdrawal:
  record_kind: "variable_port_association_withdrawal"
  schema_version: "1"
  record_id: vpw_ plus 64 lowercase hexadecimal characters
  withdraws: vpa_ record ID
  recorded_at: UtcDatetime
  authority: AuthorityRef
  note: str = ""
```

The withdrawal is frozen, extra-forbid, and fully revalidated. It contains no
evidence, context, parents, outcome, reason code, alternate target, or negative
association claim. Context and subject are inherited from its target.

A withdrawal means only:

> This positive association claim is no longer asserted in this selected revision.

It does not mean the association was false, impossible, or physically removed.

## Canonical identity

`vpa_` and `vpw_` use the existing content-derived record identity:

```text
<prefix>_<sha256(canonical record content excluding record_id)>
```

Both prefixes extend the model-record ID grammar, filename grammar,
discriminated `ModelRecord` union, record adapter, prefix mapping, canonical
serialization, builder path, store dispatch, and exact public exports.

Parent handling is normative:

1. validate every supplied parent ID;
2. reject duplicate parents rather than silently deduplicating;
3. reject self-supersession;
4. sort valid parents lexicographically;
5. use the canonical tuple for equality and record identity.

Caller parent permutations therefore produce identical canonical bytes and IDs.
`vpa_` becomes an accepted `ModelRecordEvidence` target. `vpw_` is uncitable.
No accepted record kind changes fields, canonical bytes, schema, or hash.

## Endpoint and owner closure

A selected membership containing a VPA is valid only when:

1. its variable registration exists;
2. its port registration exists;
3. the embedded variable identity fully verifies;
4. the embedded port identity fully verifies;
5. the variable-owner entity registration exists;
6. the port-owner entity registration exists;
7. the two owner anchor IDs are exactly equal; and
8. every model-record evidence dependency exists in the membership.

Normative equality:

```text
VariableRegistration.anchor.entity_anchor_id
==
PortRegistration.owner_entity_anchor_id
```

Cross-owner VPA records are invalid at append, load, and replay. A registered
different-owner pair is outside VP-001 admission; it is not a negative
association. Shared ownership without VPA is not declared.

No referent kind is privileged. A variable and port owned by the exact same type
entity are structurally admissible, as are ones owned by the exact same logical
or physical instance. Type associations do not propagate to instances, instance
associations do not propagate to types, and no entity-kind equivalence is
inferred.

## Subject, roots, and correction lifecycle

The exact subject is:

```text
(variable_anchor_id, port_anchor_id, exact AssertionContext)
```

A parentless VPA starts an independent root. Multiple roots over the same exact
subject are allowed and are disclosed as corroborating positive claims, not as
a correction-lineage conflict.

Every correction parent must be a membership-present VPA with the same exact
subject. A correction may cite one or more parents only when all parents derive
from the same root. Same-root multi-parent convergence is allowed. Cross-root
convergence and DAG cycles are invalid.

Changing variable, port, or context is not correction. It requires a new
parentless association root and, where appropriate, withdrawal of the old claim.

Within one root:

- zero active current tips: `inactive`;
- one active current tip: `healthy`;
- more than one active current tip: `conflicted`.

At subject level:

- no root: `not_declared`;
- at least one active tip in any root: `asserted`, including a conflicted root;
- roots exist but none has an active tip: `inactive`.

Independent healthy roots remain separately visible corroboration. A healthy
root never hides a conflicted root. No time, authority, record ID, filename,
directory order, or append order selects a winner.

## Withdrawal lifecycle

A VPW target must exist in the selected membership, be a VPA, be an
unsuperseded current tip, and not already be withdrawn. Reject unknown,
out-of-membership, wrong-kind, VPW, already superseded, and already withdrawn
targets. A selected revision may not both supersede and withdraw the same target,
and a later correction may not supersede a withdrawn target.

A VPW may target any unsuperseded, unwithdrawn current tip even when sibling
current tips exist in the same fork. Sibling tips do not block the withdrawal.
Withdrawing one fork tip may therefore change that root from `conflicted` to
`healthy` when exactly one active current tip remains. VP-001 does not impose a
sole-tip prerequisite.

Withdrawal of one corroborating root does not suppress another active root.
Replay that omits a later withdrawal makes the target current again relative to
that selected historical membership. Withdrawal never revives a superseded
ancestor.

## Multiplicity

The model permits one variable with multiple same-owner ports, one port with
multiple same-owner variables, multiple independent corroborating roots for one
subject, correction forks and complete convergence within one root, and
separate lineages for different exact contexts.

It imposes no uniqueness, exclusivity, or cardinality inference. Identical
canonical content is idempotent and does not form another root.

## Evidence semantics

Every VPA carries nonempty canonical evidence. Existing evidence arms may
support the accountable authority's claim, including variable or port
registration citations, explicit owner declarations, identity-binding records,
raw source records, temporal occurrences, and structural source locators through
the existing `EvidenceRef` union. Source-interpretation ledger records are not a
direct `EvidenceRef` arm and are not made citable by VP-001.

Evidence remains evidence. No name, namespace, owner, token, unit, observation
role, PIF, PCN, PCM, CAD location, geometry, proximity, Moonraker identifier,
telemetry path, source path, or observation automatically materializes a VPA.
Model-record evidence closes against the exact selected membership. Existing
foreign evidence arms retain their declared-reference semantics.

## Slice A store and index contract

The existing validating store gains these immutable indexes:

```text
variable_port_associations
variable_port_association_withdrawals
variable_port_association_root_by_id
variable_port_association_ancestry_by_id
variable_port_association_ids_by_subject
variable_port_association_ids_by_variable_context
variable_port_association_ids_by_port_context
variable_port_association_superseded_by
current_variable_port_association_tips_by_root
variable_port_association_withdrawn_by
variable_port_association_withdrawals_by_target
```

Keys use the accepted exact context representation and canonical scalar
identifiers. Every map is immutable and every sequence is deterministically
ordered. Validation fully reconstructs every record and checks filename/content
agreement, registrations, exact owner equality, evidence closure, parent kind
and subject, root preservation, acyclicity, forks, convergence, cross-root
refusal, withdrawal discipline, and all-or-nothing append/load/replay.

No accepted PT, variable, relationship, semantic, constraint, or store rule may
be weakened to accommodate VP.

## Historical replay

All existing model bytes and explicit 9-, 10-, 11-, 14-, 16-, 18-, and
28-record memberships remain frozen. They replay to their exact accepted
revision IDs and expose no fabricated VP records or indexes.

A membership containing VPA without either endpoint or its registered owner is
invalid. Omitting a later successor revives the earlier correction tip. Omitting
a later withdrawal revives its target. Records in another exact context do not
affect the requested context. Historical membership is never reconstructed by
directory enumeration.

Slice A appended no fixture records. The explicit historical PT membership
remains exactly 28 records at revision
`mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`,
and the accepted PT artifact remains SHA-256
`53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.

## Slice B API

Slice B implements exactly these read-only `ModelQueries` contracts over one
injected `LoadedModel`. They own no store, perform no writes, and do not infer
associations.

```python
variable_port_association(variable_anchor_id, port_anchor_id, *, context)
    -> VariablePortAssociationResult
ports_associated_with_variable(variable_anchor_id, *, context)
    -> VariablePortsResult
variables_associated_with_port(port_anchor_id, *, context)
    -> PortVariablesResult
variable_port_assertion(record_id)
    -> VariablePortAssertionDisclosureResult
```

Public literal vocabularies:

```text
VariablePortEndpointStatus:
  both_registered | variable_not_registered | port_not_registered |
  both_not_registered
VariablePortOwnerAlignment:
  not_evaluated | same_owner | different_owners
VariablePortAssociationConclusion:
  not_evaluated | not_declared | asserted | inactive
VariablePortLineageSummary:
  not_applicable | healthy | conflicted | inactive
VariablePortsStatus:
  variable_not_registered | registered
PortVariablesStatus:
  port_not_registered | registered
VariablePortAssertionLookupStatus:
  not_found | found
```

The accepted `AssertionActivity` and `ContainingLineageHealth` are reused.

```text
VariablePortAssociationRootResult:
  root_record_index
  lineage_record_indices
  current_tip_indices
  withdrawal_indices
  lineage_health

VariablePortAssociationResult:
  material
  variable_anchor_id
  port_anchor_id
  context
  endpoint_status
  owner_alignment
  variable_registration_index
  variable_owner_registration_index
  port_registration_index
  port_owner_registration_index
  conclusion
  lineage_summary
  roots

VariablePortAssociationEntry:
  entry_index
  variable_anchor_id
  port_anchor_id
  variable_registration_index
  variable_owner_registration_index
  port_registration_index
  port_owner_registration_index
  conclusion
  lineage_summary
  roots

VariablePortsResult:
  material
  variable_anchor_id
  context
  status
  variable_registration_index
  owner_registration_index
  entries

PortVariablesResult:
  material
  port_anchor_id
  context
  status
  port_registration_index
  owner_registration_index
  entries

VariablePortAssertionDisclosureResult:
  material
  record_id
  lookup_status
  record_index: optional
  activity: optional
  containing_lineage_health: optional
  root_record_index: optional
  successor_indices
  withdrawal_indices
```

A not-found result has no record or lifecycle indices and empty successor and
withdrawal tuples. A found VPW is an event with a record index but no assertion
lifecycle/root and empty successor/withdrawal tuples. Registered endpoints with
no declaration return registered-empty or `not_declared`, never an
evidence-backed negative. Results follow the accepted `ModelQueryMaterial`
carry-once pattern and fully recompute all derived fields without store access.

## Implemented Slice C composition

Slice C is owner accepted over the owner-accepted Slice B boundary. It remains
limited to the following read-only model-state composition. Slice D is
implemented and adversarially reviewed; awaiting final owner acceptance.

```python
ModelStateQueries.associated_port_variable_state(
    variable_anchor_id,
    port_anchor_id,
    *,
    context,
    as_of,
    entity_anchor_id=None,
    source=None,
) -> AssociatedPortVariableStateResult
```

```text
AssociatedPortVariableStateStatus:
  endpoint_not_admitted | association_not_declared |
  association_conflicted | association_inactive | associated

AssociatedPortVariableStateResult:
  variable_anchor_id
  port_anchor_id
  context
  as_of
  status
  association: VariablePortAssociationResult
  variable_state: VariableStateResult
```

State remains independently disclosed for valid input. Association failure does
not suppress temporal evidence. Observations remain attached to variables,
never ports. Displaying variable state beside a port is not a claim that an
observation occurred at the port. Context does not filter temporal data;
`as_of` does not select a
model revision; model revision, binding revision, and temporal cutoff remain
separate provenance axes; no temporal revision or clock synchronization is
invented. The kernel never imports state, temporal, binding, or compatibility
modules.

## Implemented Slice D demonstration

After A–C were separately accepted, Slice D appended exactly one VPA and no
VPW:

```text
variable: var_b7e2d3c4f5a6172839405a6b7c8d9e0f
port:     prt_91a3d6db9df440e1a09dbdb185c7b182
owner:    ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50
context:  lifecycle_view / as_designed
authority: test_fixture / vp001_demo_fixture / manual_declaration
evidence: exact variable registration, exact port registration, and one
          claim-specific synthetic owner declaration
```

The model evolves from 28 to exactly 29 records. No correction, second root,
cross-owner claim, role, variable, port, or state record is added.

The approved record is
`vpa_f6443787fc9665e24cae80a5ba0650d0bda8abefe87cb60427c8b39068932e49`;
its 1,184-byte stored file has SHA-256
`95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e`.
The explicit 29-record revision is
`mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`.
The deterministic VP disclosure artifact is 17,824 bytes with SHA-256
`a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3`.
It carries the exact binding membership, declaration, resolution,
applicability, model registrations, and temporal provenance while keeping the
model revision, binding revision, and cutoff separate.

Mandatory disclaimer:

> This is an illustrative synthetic VP-001 association fixture. It does not describe or claim any real printer wiring, signal routing, connector, protocol, sensing location, measurement location, data path, flow, command, control, influence, causality, behavior, compatibility, safety, correctness, activity, or operating condition.

The demonstration also states that shared ownership, names, Moonraker data, CAD,
geometry, PIF tokens, PCN topology, and existing observations did not create the
association, and displaying state beside a port does not mean a value occurred
at or travelled through it.

## Explicit exclusions and limitations

VP-001 has no association roles, cross-owner semantics, negative assertions,
exclusivity, inferred cardinality, traversal, topology, compatibility, state at
a port, signal routing, flow, control, causality, behavior evaluation, safety
judgment, new store, new ledger, or new runtime module. Later engineering
meanings require separately defined evidence-bearing contracts and cannot
reinterpret `vpa_`.
