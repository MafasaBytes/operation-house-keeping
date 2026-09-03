# FL-001 Slice D Pre-Append Rehearsal Plan

Date: 2026-09-03

Status: owner-authorized pre-append rehearsal only; authoritative append
unauthorized

## 1. Authority and stop condition

Rehearse exactly one synthetic `FlowAnchor`, one FRG, and one parentless FLD
over two independent disposable copies of the accepted 34-record model. Add no
FLW, correction, second root, second anchor, fixture, runtime behavior, or
authoritative record. Stop with the exact frozen candidate contract and ask
the owner both to approve it and, separately, to authorize the 34-to-36
authoritative append.

Slice C is absent from FL-001 v1. Rehearsal authorization is not append
authorization.

## 2. Accepted source and preflight

Before minting:

1. require the documentation-only Slice B acceptance commit as clean HEAD;
2. fail closed if any candidate manifest already exists;
3. load and revalidate exactly 34 authoritative records at
   `mrv_67fb4be22bd50683cc427d3d4e4abf97c0ffe6b800f764b156f671cd18bb5b41`;
4. require zero FRG, FLD, and FLW records;
5. freeze every predecessor filename, stored byte count, and SHA-256 plus the
   aggregate;
6. freeze explicit historical memberships and accepted PT/VP/BH/ST artifacts;
7. verify all predecessor record IDs from normative canonical bytes; and
8. verify the authoritative and protected fixture trees contain no unexpected
   change.

## 3. Frozen permanent identity semantics

Invoke public `mint_flow_anchor()` exactly once with:

```text
namespace    = demo-printer
display_name = Synthetic Logical Flow Alpha
role_name    = null
```

Immediately persist the complete returned anchor in the candidate manifest.
Every later construction reconstructs that anchor from the manifest; the
rehearsal helper does not import or invoke the minter.

Freeze the complete nominal `FlowKindToken`:

```text
token_kind     = flow_kind
system_id      = project_local
system_edition = fl001-demo-1
code           = synthetic_fixture_kind
```

This indivisible token is synthetic nominal identity content. It is not a
commodity, carrier, protocol, physical mechanism, rate, or occurrence claim.

## 4. Exact accepted PT support

Freeze this one-source/one-sink directed signature:

| Role | PortAnchor | PRG | exact direction PIF |
|---|---|---|---|
| source | `prt_c1d68d104a73405a950556b55f6a4d34` | `prg_c37057871b41bf873e317abde29dbba764be4974e195e21261d26942e5833af9` | `pif_258ca8416b648b6d1fa4e89f9b482ebc23ac761d275992cd82f0a89062213242` (`output`) |
| sink | `prt_91a3d6db9df440e1a09dbdb185c7b182` | `prg_c06e49bef910d073a6af206d884a1bb68c0b9baa1cdb1d698d0c35c61025e057` | `pif_80ce1f623bcec03fa2de7d6a40828a779d9005198b6629bb1839f3cf41e63e84` (`input`) |

Exact-union PCN:

`pcn_4861ecf058add8a45686c9b9c4f2e28085f60575705d6d06f1890b8ef11f1726`

Exact context: `lifecycle_view / as_designed`.

These accepted PT records support only structural admission and model-relative
alignment. They do not create the FlowAnchor or prove physical flow.

## 5. Frozen FRG and FLD semantic inputs

Use for both records:

```text
authority.kind   = test_fixture
authority.agent  = fl001_demo_fixture
authority.method = manual_declaration
```

FRG:

- exact anchor reconstructed from the manifest;
- exact source and sink tuples from Section 4;
- exact token from Section 3;
- `recorded_at = 2026-09-03T12:00:00+00:00`;
- note `FL-001 bounded synthetic logical-flow registration.`;
- exact model-record citations to both participant PRGs; and
- owner statement: `FL-001 fixture authority explicitly registers this opaque synthetic logical-flow identity for the exact cited source-port set, sink-port set, and complete nominal flow-kind token; illustrative fixture only.`

FLD:

- exact frozen FlowAnchor ID;
- exact context, PCN, and source/sink direction pins from Section 4;
- `supersedes = ()`;
- `recorded_at = 2026-09-03T12:01:00+00:00`;
- note `FL-001 bounded synthetic logical-flow declaration.`;
- exact model-record citations to FRG, both PRGs, PCN, and both pinned PIFs;
  and
- owner statement: `FL-001 fixture authority explicitly declares this exact synthetic logical-flow capability/pathway in the as-designed lifecycle view with the cited exact-union topology assertion and exact source/sink direction declarations; illustrative fixture only.`

Append order is exactly FRG then FLD. Proposed membership is the canonical
sorted 34-record predecessor union plus those two IDs.

## 6. Canonical and stored integrity

Build FRG and FLD only through public `build_record`. Derive every field named
canonical directly from `backend.model_kernel.canonical.canonical_payload()`
and `canonical_bytes()`. Prove `+00:00` timestamp representation, canonical
SHA-256 equality with each record-ID suffix, exact `compute_record_id()`, and
true `verify_record_id()`.

Capture stored bytes only from public `ModelStore` output. Freeze canonical
payload/bytes, byte counts, hashes, complete record serialization, stored JSON
bytes, stored byte counts, file hashes, append order, proposed membership, and
proposed revision in the manifest.

## 7. Independent disposable rehearsal

Resolve two safe temporary roots and prove neither can alias the authoritative
model. Independently copy the exact 34 predecessor files into each root; use
reverse copy order in the second root. In each root:

1. replay and verify the exact predecessor membership/revision;
2. reconstruct the frozen anchor and semantic inputs from the manifest;
3. build FRG and FLD through public builders;
4. append FRG then FLD through public `ModelStore`, verifying 35 then 36;
5. replay the explicit proposed 36-record membership;
6. run every required public flow and PT support query;
7. independently generate the deterministic disclosure bytes; and
8. prove every copied predecessor byte remains unchanged.

Candidate record files and disclosure bytes are never copied between roots.

## 8. Required query and non-inference checks

Pin:

- registered flow lookup with exact FRG and PRG indices;
- declared/healthy/`one_healthy_root` exact-context declaration;
- asserted/current/healthy/exact-current PCN support;
- declared/current/healthy/exact-current and consistent source/sink PIF
  support;
- aligned aggregate support;
- one source entry and one sink entry with direct-query parity;
- found FRG with no lifecycle fields;
- found current FLD in one healthy containing lineage;
- other-context direct `not_declared` and registered-empty port collection;
  and
- structured absence at the untouched 34-record revision.

No output may claim adjacency, traversal, physical activity, occurrence,
command, observation, rate, quantity, conservation, behavior, influence,
causality, control, safety, health, diagnosis, correctness, or recommendation.
The word `healthy` is restricted to one-current-tip model-lineage health.

## 9. Deterministic artifact and preservation

Generate one canonical compact UTF-8 JSON disclosure independently in each
root. Require direct byte equality and freeze its path, size, and SHA-256 in
the manifest. Include exact predecessor/proposed memberships and revisions,
anchor and records, evidence, public flow/PT query disclosures, canonical and
stored contracts, predecessor hashes, accepted artifact hashes, authenticity
limitation, mandatory disclaimer, and semantic warnings.

Replay exact historical 9/10/11/14/16/18/28/29/32/34 memberships. Preserve
the authoritative 34-record bytes/aggregate, Slice A golden contracts, and
accepted PT/VP/BH/ST artifacts before and after rehearsal.

## 10. Verification and owner gate

Run candidate/canonical/replay/query/non-inference checks, two-root byte
reproduction, focused FL-001 tests, the complete repository where practical,
backend compilation, working and milestone whitespace checks, Git
status/topology, and an authoritative before/after sweep. Isolate and rerun
only an environment-denied loopback test through the established procedure.

Leave the plan, candidate manifest, deterministic disclosure, and rehearsal
report uncommitted. If a contract defect appears, stop with a discrepancy
report. Otherwise ask exactly whether the owner approves the frozen candidate
and separately authorizes the authoritative 34-to-36 append.
