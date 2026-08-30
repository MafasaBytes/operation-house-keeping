# BH-001 Slice D Pre-Append Rehearsal Plan

Status: owner-authorized remediation and disposable rehearsal; no authoritative append

## 1. Authority and boundary

Owner resolution: add the narrowly scoped public `mint_variable_anchor()` API, commit it green before candidate allocation, then resume only the disposable pre-append rehearsal.

The accepted Slice C HEAD is
`8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`; its administrative acceptance
commit is `a619ed14d36aeb508e4db8602adbbdce4b1b4e2d`. The authoritative demo remains
29 records at `mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652`.
The current owner-amended BH specification SHA-256 is
`520bf74823ab5e206bef8a56de9ba872ef8f3167451ad9c57e02a364532cd873`.

The authoritative append remains prohibited. This plan permits one public
identity-minter repair, one-time candidate allocation after that repair is
committed and green, and two disposable rehearsals only.

## 2. Public minter repair

Implement exactly:

```python
def mint_variable_anchor(
    *,
    entity_anchor_id: str,
    namespace: str,
    display_name: str,
    role_name: str | None = None,
) -> VariableAnchor:
    ...
```

It allocates one UUID4 using standard-library `uuid4().hex`, prefixes it with `var_`, and delegates all field
validation to the unchanged public `VariableAnchor` contract.

Export `mint_variable_anchor` after `mint_port_anchor` in the existing minter
export sequence. Add no entity minter, framework, injected randomness, store,
registration, binding, authority, persistence, or semantic meaning. No existing
anchor, minter, canonical record, or identity vector may change.

Develop exact tests red-first, make the focused and affected identity suites
green, inspect the diff, and commit the bounded addition separately.

No candidate may be minted before the minter commit is green.

## 3. One-time candidate allocation

Before allocation, freeze these exact minter inputs:

```text
variable anchor
  entity_anchor_id: ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50
  namespace: demo-printer
  display_name: Synthetic comparison variable
  role_name: null

behavior anchor
  namespace: demo-printer
  display_name: Synthetic exact numeric equality
  role_name: null
```

After the minter commit, invoke `mint_variable_anchor()` exactly once and then
`mint_behavior_anchor()` exactly once. Immediately serialize their complete
public anchor content into
`docs/superpowers/reports/2026-08-30-bh001-slice-d-candidate-identities.json`.

The manifest contains only:

- `status: "non_authoritative_candidate"`;
- the accepted 29-record model revision;
- the complete variable anchor;
- the complete behavior anchor; and
- the two allocation API names.

It contains no time, machine path, seed, process, environment, or runtime
metadata. Serialize it as UTF-8 canonical JSON with sorted keys, compact
separators, ASCII escaping, and one trailing newline; report its exact byte
count and SHA-256. After the implementation commit, invoke each public minter exactly once, serialize both outputs, and then never invoke either minter again.
Neither frozen identity may be regenerated or altered.

## 4. Frozen record inputs

Before constructing records, freeze the accepted existing variable
`var_b7e2d3c4f5a6172839405a6b7c8d9e0f`, context
`lifecycle_view/as_designed`, authority
`test_fixture / bh001_demo_fixture / manual_declaration`, recorded time
`2026-08-30T12:00:00+00:00`, the three bounded notes, exact evidence text,
semantic locks, and explicit selectors in the rehearsal implementation. These
values are inputs to content-derived identities and the report must disclose
them completely. Shared ownership, names, semantics, VPA, topology, constraints,
or observations must not be described as creating or corroborating behavior.

Build through public `build_record()` only:

1. one `VariableRegistration` for the frozen new variable;
2. one `BehaviorRegistration` for the unordered pair of new and existing
   variables; and
3. one parentless `BehaviorRuleDeclaration` in the accepted exact context.

Build no other record kind.

## 5. Independent disposable ledger rehearsals

Create two independent disposable ledger roots. Copy each predecessor by the explicit
accepted 29-record membership, never by enumeration-derived history. Hash the
29 source and copied files before append. Reconstruct both frozen anchors from
manifest mappings through public contracts.

In each root append VRG, BRG, then BHD using public `ModelStore.append()`. Load
and replay only the explicit prospective membership. Use public Slice B query
and Slice C evaluation facades. Generate the deterministic disclosure artifact
from public serialized results and canonical JSON.

Require direct equality across runs for anchors, three canonical record bytes,
record IDs, stored hashes, membership, model revision, query serializations,
evaluator serialization, artifact bytes, artifact size, artifact SHA-256, and
predecessor before/after hashes.

Each disposable ledger has exactly one parentless BHD and one behavior lineage
root; “two roots” never means two behavior roots.

## 6. Seam and preservation gates

Prove the new variable is the sole prospective binding-declaration exception;
all pre-existing registrations still match accepted binding declarations; a
second missing declaration and a substituted/divergent exception fail. The
candidate variable's direct model-state result must disclose
`binding_declaration_absent`. Do not change any binding file or revision.

Replay the explicit 9/10/11/14/16/18/28/29 histories unchanged. Pin all 29
predecessor bytes, the accepted PT and VP artifact hashes, model revision, and
authoritative Git inventory before and after rehearsal. No authoritative model,
fixture, artifact, evidence, or membership path may be written.

## 7. Query, evaluator, and artifact gates

The prospective 32-record model must disclose one registered behavior, one
healthy exact-context declaration root, reverse discovery from both variables,
and current BHD assertion activity. The accepted 29-record history must disclose
structured absence.

Evaluation uses exactly two explicit selectors. It must be `not_executed`,
preserve independently available evidence for the existing participant, and
honestly disclose the new participant's missing lower-layer admissions. It must
not fabricate binding, VSP, VSM, interpretation, temporal, or source evidence.

The artifact contains the accepted exact disclaimer and states that
`not_executed` is an admission result, not evidence that the declaration is
false. Equal and different outcomes remain confined to existing disposable
Slice C test worlds.

## 8. Owner gate

Persist the candidate manifest and full results report without modifying the
earlier discrepancy report. Report exact anchors, record content and hashes,
membership, revision, disclosures, artifact bytes/hash, predecessor aggregate,
seam attacks, commands, and Git state. Stop for owner approval. Do not append
to `models/demo-printer` and do not begin final Slice D fixture work.

END OF BH-001 SLICE D PRE-APPEND REHEARSAL PLAN
