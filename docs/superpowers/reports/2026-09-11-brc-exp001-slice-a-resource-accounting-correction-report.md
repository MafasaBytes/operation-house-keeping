# BRC-EXP-001 Slice A resource-accounting correction

## 1. Owner decision and checkpoint

The owner accepts additive resource accounting and authorizes documentation
correction followed by corpus calibration only. No Slice A minimax execution,
result freezing, numerical-cap amendment or Slice B work is authorized.
Branch: brc-exp001. Starting HEAD:
`be4ddb572926959063d6550deda4e6ec0db96e42`.

The immutable [stop report](2026-09-11-brc-exp001-slice-a-completion-report.md)
remains SHA-256
`7ac7a4aed2a930ea4fa225ecd73b082fb71d714720fca9f323209f4896beec80`.
The original [calibration report](2026-09-11-brc-exp001-slice-a-resource-calibration-report.md)
is committed unchanged, SHA-256
`9c3b4b97dc6a80b84f644bfa36bf507fd90d11fc18fe1e58c67d3750e800679c`.

## 2. Exact correction and document hashes

Replacement expansion subtracted each already-counted three-node reference
object when adding its 67-node resolved Statement. That conflicts with charging
canonical wire material and additional resolution work. Replacement accounting
is rejected. The old measurement remains historical evidence, not a rewritten
receipt: BH wire 11343 plus resolution charge 1072 equals **12415**; primary wire
6058 plus resolution charge 1072 equals **7130**.

| Corrected document | Old SHA-256 | New SHA-256 |
| --- | --- | --- |
| [Synthesis](../specs/2026-09-11-brc-exp001-baseline-reasoning-closure-spike-design.md) | `827381a8280ad89d3d3a506e0f9dd331c82bea169514359f3f3b12125a68a3b2` | `55dd689a75c17f4675df4ad1806925868b1892eeff1aa91494c07dd5fa94f33f` |
| [Slice A plan](../plans/2026-09-11-brc-exp001-slice-a-execution-plan.md) | `16dd72fd7b3d755cbdd8977f2fb81084cf33af8703aa70ab8f79fdd4da85899c` | `d72c878939996c96411075eb650d5f2fae6dd7fcbc347ca77e1b3f3b4f4fe09b` |

## 3. Three-part formula and multiplicity

`wire_node_count` counts every canonical serialized object, array, scalar and
object key once per serialized occurrence. Reference objects remain present.
Repeated required cross-root public proof remains charged at each occurrence.
Python object identity and private/validator reconstruction copies do not count.

`resolution_charge_node_count` is the sum of the complete canonical body-node
counts resolved at each typed StatementSlot reference occurrence. Owned full
Statements already enter wire count. Ordinary provenance Ref selectors, public
indices and model-record references do not recursively expand arbitrary proof.

`charged_validation_node_count = wire_node_count + resolution_charge_node_count`.

The existing max_expanded_nodes field bounds this additive total. Any legacy
expanded_node_count name is an alias for the additive value, not a second metric.
Multiplicity is per occurrence, not unique ID. Caching a body count by exact
identity and canonical bytes is permitted; reducing its occurrence charge is not.
No memoization discount is authorized. Malformed, duplicate, unresolved or cyclic
definitions/references are rejected before full reconstruction.

## 4. Frozen preflight and error mapping

1. Raw byte-length limit.
2. Shallow scalar/container cardinalities, exact types, lexical/depth limits,
   duplicate keys, schema arms and actual H/T/O/cell product bounds.
3. Canonical wire-node count, canonical bytes and independent commitments.
4. Reference-count and identifier/path-shape bounds.
5. Only the bounded carried Statement lookup needed for resolution accounting.
6. Deterministic resolution charge without nested-model reconstruction.
7. Total charged-node ceiling and unchanged output/trace reserve proof.
8. Full owning lower-result and experimental-model reconstruction.
9. Semantic admission and, only with separate execution authority, algorithm.

The wire and resolution gates each use the same existing node ceiling; the total
gate remains mandatory even when both individual quantities are below it.
No new numerical resource field is added.

| Error | Existing code | Fixed protocol/preflight target | Fixed presentation text |
| --- | --- | --- | --- |
| Wire overflow | nodes_exceeded | wire_node_count | Wire node limit exceeded. |
| Resolution overflow | nodes_exceeded | resolution_charge_node_count | Resolution charge limit exceeded. |
| Total overflow | nodes_exceeded | charged_validation_node_count | Charged validation node limit exceeded. |
| Malformed reference | schema_invalid | reference_shape | Malformed reference. |
| Unresolved/cyclic reference | schema_invalid | reference_resolution | Unresolved reference. |

Each existing Refusal has phase preflight, epistemic level 7/unknown/unavailable,
synthetic true, no source refs, and no lower_reason. Target is an existing Ref
with space protocol, root preflight and the one-element fixed field path above.
Messages are presentation constants, not new wire fields. No count value,
identifier, submitted path, exception or payload fragment is interpolated.
Hostile envelopes retain existing bounded RejectedEnvelopeResult framing.

## 5. Unchanged contracts and calibration authority

The literal node limit remains **12000**; neither 12367 nor 12415 is a new cap.
No assumption byte, manifest, hypothesis/test/outcome/prediction semantics,
compatibility relation, cost policy, algorithm finite_compatibility_minimax/v1,
epistemic ladder, byte ceiling, other resource bound or public contract changes.
No accepted proposal/audit, immutable report, production artifact or authoritative
ledger is amended. The candidate assumptions and manifest remain respectively
`4c5e48452ee81a5c65cef2a51dcae8de56262684e7056be429dd6166788241dc` and
`296f0c8d78e6a248b7b647867f5a69a0de69190a5ee02198349c1c1269769c4d`.
They and the pre-execution rehearsal remain untracked.

The correction commit includes only the unchanged original calibration report,
corrected synthesis, corrected plan and this report. No status edit is needed.
After that commit, disposable tools may measure the valid corpus under this
formula. The operational numeric cap remains unchanged until separate owner
approval. M_valid must not be inferred from hostile inputs. If the measured valid
maximum exceeds the owner safety ceiling 16384, recommend carriage redesign,
not a larger cap. Slice A remains incomplete throughout calibration.

END OF BRC-EXP-001 SLICE A RESOURCE ACCOUNTING CORRECTION REPORT
