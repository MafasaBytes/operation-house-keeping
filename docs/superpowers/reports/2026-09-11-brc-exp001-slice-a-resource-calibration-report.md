# BRC-EXP-001 Slice A resource-calibration report

## 1. Disposition: counting-contract clarification required first

**No corrected cap is recommended. M_valid has not been established.**
This is a bounded first-gate investigation, not a completed valid-corpus
calibration and not permission to resume Slice A.

The retained 12,367-node measurement is reproducible under **replacement
expansion**. However, the accepted synthesis section 10 says: “Repeated statement
references count as their wire objects; resolved-body expansion is additionally
charged”. The accepted plan section 5 likewise says to count resolved
StatementSlot expansion “as well as serialized nodes”.

The stopped implementation instead subtracted each three-node reference object
when adding its 67-node resolved body. These are different accounting contracts:

- Replacement-tree count: wire + sum(resolved-body nodes − reference nodes).
- Additive charge: wire + sum(resolved-body nodes), retaining the wire references.

For the BH candidate those give **12,367** and **12,415**, respectively. The
difference is exactly 48 nodes, not floating-point error or nondeterminism.
The accepted rehearsal and stopped report use the former; the quoted normative
wording supports the latter. Choosing between them silently would change the
meaning of the quantity against which the corpus maximum is calibrated.

This is a **counting-contract ambiguity/undercharge finding**, not evidence of
overcount that removes the resource excess. Neither interpretation admits the
BH candidate under 12,000. No avoidable duplication or traversal error was found
that explains away the excess. The report does not claim that correcting the
48-node discrepancy solves the resource-cap problem.

The corrected-limit rule requires correct, settled counting semantics before
a numeric recommendation. That prerequisite is not closed. I therefore stop
at this first gate and recommend the explicit counting clarification in section
8, rather than select a cap or silently interpret away the frozen wording.
The lower-world minimality proof and complete valid-corpus measurement remain
unperformed. Their absence is disclosed in the complete work-item register in
section 6; the two inspected candidates are not called the complete corpus.

**Slice A remains incomplete.** There was no minimax execution, experimental
result calculation/acceptance/freezing, Mode B work, documentation amendment,
commit, push or merge in this investigation.

## 2. Verified checkpoint and frozen bytes

Branch: `brc-exp001`.
HEAD unchanged: `be4ddb572926959063d6550deda4e6ec0db96e42`.
Starting design/implementation checkpoint:
`53e4c3122bccacef0fb63712c28196584b286664`.
The authoritative production baseline remains
`debcffec5a77ae270bbf8822f82ef1aa7556c5bd`.

The tracked tree was clean. Initially the only ordinary untracked files were
the three frozen owner-gate artifacts. This report is the only repository file
created by this investigation and remains untracked.

| Frozen input | Bytes | Verified SHA-256 |
| --- | ---: | --- |
| [Immutable resource-stop report](2026-09-11-brc-exp001-slice-a-completion-report.md) | 423274 | `7ac7a4aed2a930ea4fa225ecd73b082fb71d714720fca9f323209f4896beec80` |
| [Approved assumptions](2026-09-11-brc-exp001-slice-a-candidate-assumptions.json) | 29153 | `4c5e48452ee81a5c65cef2a51dcae8de56262684e7056be429dd6166788241dc` |
| [Manifest](2026-09-11-brc-exp001-slice-a-candidate-assumptions-manifest.json) | 23490 | `296f0c8d78e6a248b7b647867f5a69a0de69190a5ee02198349c1c1269769c4d` |
| [Rehearsal](2026-09-11-brc-exp001-slice-a-preexecution-rehearsal-report.md) | 17708 | `8e34bbc84ae404c0789e62801abe025c6a6820f33747b3c5a38dfbc56cf193f1` |
| [Accepted synthesis](../specs/2026-09-11-brc-exp001-baseline-reasoning-closure-spike-design.md) | 99525 | `827381a8280ad89d3d3a506e0f9dd331c82bea169514359f3f3b12125a68a3b2` |
| [Accepted plan](../plans/2026-09-11-brc-exp001-slice-a-execution-plan.md) | 10573 | `16dd72fd7b3d755cbdd8977f2fb81084cf33af8703aa70ab8f79fdd4da85899c` |

The proposal digest
`0c830c433674eac130c2c01cb337a4e474eba5d2fa88fc72269e6de656a2bfeb`
and audit digest
`65738e0d45ecdc47f9cdaa17bf5890b6337c9d09769ae478320f988d77ce4791`
also match. No frozen document or JSON input was edited or normalized.

The two exact requests were decoded independently in temporary material from
the resource-stop report's two `base64` blocks in section 10, not regenerated
from new model or observation data. The report's `base64-log` blocks are not
requests. The canonical requests remain compact sorted-key UTF-8 with no
trailing newline.

| Inspected candidate | Canonical bytes | SHA-256 |
| --- | ---: | --- |
| Primary, F/N/E, 17 records | 94819 | `67fe5d164251fdc6d8ba577e90660b0c486ea626af0a1faccac5362481f188c1` |
| BH-bearing, F/N/E/BH, 23 records | 189522 | `bace2e4bec513e920b8afdd11d5562971cb213e7dec2ea08878b136b71192a9b` |

For both requests, extracting exactly schema, mode, algorithm, limits, hypotheses,
measurements, compatibility, justifications, scope and policy, then canonically
encoding, yields the exact approved 29,153 bytes, not merely equivalent JSON.
Both projection digests equal
`4c5e48452ee81a5c65cef2a51dcae8de56262684e7056be429dd6166788241dc`.

Important identity clarification: **12,367 is the BH-bearing candidate's
replacement-expanded count, not the 94,819-byte primary's count**. The primary
replacement-expanded count is 7,082. The immutable stop record is left unchanged.

## 3. Complete decomposition of the inspected requests

Every object, array, scalar value and object key counts once per serialized
occurrence. Keys are counted separately from their values. Root depth is one.
The following top-level table assigns each field its one key node plus the
complete value subtree. Add the single outer request object to the sum.

| Top-level field | Primary wire nodes | BH-bearing wire nodes |
| --- | ---: | ---: |
| algorithm | 2 | 2 |
| compatibility | 778 | 778 |
| hypotheses | 638 | 638 |
| justifications | 136 | 136 |
| limits | 42 | 42 |
| lower | 3714 | 8988 |
| lower_commitments | 67 | 78 |
| measurements | 584 | 584 |
| mode | 2 | 2 |
| policy | 12 | 12 |
| schema | 2 | 2 |
| scope | 80 | 80 |
| Outer object itself | 1 | 1 |
| Total | 6058 | 11343 |

Equivalent concise decomposition:

- Primary: assumption projection 2,277 + lower field/subtree 3,714 +
  lower_commitments field/subtree 67 = **6,058 wire nodes**.
- BH: assumption projection 2,277 + lower field/subtree 8,988 +
  lower_commitments field/subtree 78 = **11,343 wire nodes**.

The projection's outer root is already the request root in this equation; it
is not counted twice. The lower aggregates include the lower field key,
its object, and its root-name keys. Individual lower-root values are:

| Complete owning lower result | Primary nodes | BH-bearing nodes |
| --- | ---: | ---: |
| F | 994 | 1320 |
| N | 1913 | 1951 |
| E | 802 | 802 |
| BH | absent | 4909 |

The following **disjoint** classification assigns every node to exactly one
bucket. It is a reporting taxonomy, not another admission policy. Classification
priority is: epistemic subtree; Citation subtree excluding epistemic; public
fields literally named evidence; record object content; ModelQueryMaterial shell;
other lower proof; supplied Statement content; H structure; T/outcome structure;
cell structure; outer fields/commitments/limits/scope/policy. A field key follows
its owning subtree's bucket. Other lower proof includes evidence-bearing public
fields not literally named evidence, query findings, public selectors, occurrence
proof, and membership disclosures. Consequently the public-evidence bucket is
not asserted to be all evidence-bearing lower material.

| Disjoint node category | Primary wire | Primary replacement-expanded | BH wire | BH replacement-expanded |
| --- | ---: | ---: | ---: | ---: |
| assumption_statement_content | 126 | 222 | 126 | 222 |
| compatibility_structure | 106 | 106 | 106 | 106 |
| epistemic_classifications | 1064 | 1704 | 1064 | 1704 |
| hypothesis_structure | 94 | 94 | 94 | 94 |
| measurement_structure | 218 | 170 | 218 | 170 |
| model_query_material_shell | 31 | 31 | 74 | 74 |
| model_records | 887 | 887 | 2462 | 2462 |
| other_carried_lower_results | 2616 | 2616 | 5985 | 5985 |
| outcome_structure | 70 | 54 | 70 | 54 |
| outer_fields_commitments_limits_scope_policy | 140 | 140 | 151 | 151 |
| provenance | 526 | 878 | 526 | 878 |
| public_evidence_citations | 180 | 180 | 467 | 467 |
| Total | 6058 | 7082 | 11343 | 12367 |

Hypotheses, measurements, outcomes and cells include their Statements through
the separate assumption/epistemic/provenance buckets. The disjoint structural
buckets alone are not full-object sizes. The top-level table supplies those
complete rollups; do not add rollups to the disjoint table.

| Node kind | Primary wire | Primary replacement-expanded | BH wire | BH replacement-expanded |
| --- | ---: | ---: | ---: | ---: |
| Object | 618 | 714 | 1178 | 1274 |
| Array | 372 | 468 | 609 | 705 |
| Object key | 2770 | 3234 | 5194 | 5658 |
| Scalar value | 2298 | 2666 | 4362 | 4730 |
| Total | 6058 | 7082 | 11343 | 12367 |

Both requests contain 21 owned Statements and 16 StatementSlot references.
Each referenced full method Statement is 67 nodes; each closed reference object
is three nodes. The same approved method Statement is referenced at multiple
typed slots; occurrence count, not unique-ID count, controls expansion.

Replacement expansion adds exactly:

- 96 object nodes;
- 96 array nodes;
- 464 key nodes;
- 368 scalar nodes;
- total **1,024** = 16 × (67 − 3).

Retaining reference nodes as well adds another 16 objects, 16 keys and 16 scalar
values: **48** nodes. The additive expansion charge is **1,072** = 16 × 67.

Thus:

| Accounting interpretation | Primary | BH-bearing |
| --- | ---: | ---: |
| Canonical serialized wire tree | 6058 | 11343 |
| Replacement-expanded tree | 7082 | 12367 |
| Wire plus additionally charged resolved bodies | 7130 | 12415 |

Virtual StatementSlot charging must be distinguished from actual lower-result
reconstruction. It accounts for explicitly referenced logical bodies; it is not
permission for a public validator to add missing serialized fields.

## 4. Carry-once and reconstruction audit

**Within each owning public root, carry-once integrity passes for these bytes.
Global physical deduplication across public roots is not true and is not claimed.**

The primary has one ModelQueryMaterial, at `lower.F.material): 17 records,
794 nodes, 14,129 bytes, SHA-256
`213d2929b5cf213b5fb8ac38ef2158b9ae2dbf00b81fe612a19e05977285613b`.

The BH candidate has two byte-identical complete ModelQueryMaterial occurrences:

- `lower.F.material`;
- `lower.BH.behavior.material`.

Each has 23 records, 1,120 nodes, 19,476 bytes, SHA-256
`7bd2c4110dd77b58d9d6ab8e9a6f1a78819686696b96b406e75587d0c584fb71`.
Both occurrences are mandatory under the current owning public types. Public
field metadata confirms F.material, BH.behavior, BH.behavior.material and BH's
participant_semantic_results are required. Synthesis section 5 explicitly
requires the complete owning F and BH proofs and forbids stripping a root to
meet a cap. Counting both wire occurrences is therefore correct under the
current contract, not an accidental second visit to the same serialized node.

Nested FC/BH structural rows retain indices into their owning material; private
bound-material aliases do not serialize as additional ModelQueryMaterial
objects. Complete membership lists also occur in the owning N/VS/ES/VM and BH
public revision disclosures and in the independently retained commitments.
Those serialized occurrences must each be counted. The evidence inventory
records every such path, membership count and subtree digest. They are not
expanded into more model records by the counter.

No complete ModelQueryMaterial or model membership appears inside the hypotheses,
measurements, outcomes, predictions or supplied justifications. There are no
derivation rows in these Mode A requests. A request field named steps or a
caller-supplied result/derivation would be a wrong closed schema arm, not a
valid large request.

The BH participant proof is not interchangeable with N's semantic result:
N uses declared-binding discovery; BH uses explicit selectors and explicit owner
nomination. Their source/selection and requested-entity disclosures differ.
Identical numerical values do not authorize collapsing those public proofs.

Full public reconstruction used only these accepted constructors:

| Owning public type | Primary before/after nodes | BH-bearing before/after nodes |
| --- | ---: | ---: |
| FlowOperatingCriterionResult | 994 / 994 | 1320 / 1320 |
| ConstraintEvaluationResult | 1913 / 1913 | 1951 / 1951 |
| OperationalEvidenceSelectionResult | 802 / 802 | 802 / 802 |
| BehaviorEvaluationResult | absent | 4909 / 4909 |

Each complete public `model_validate` followed by `model_dump(mode='json')`
reproduced exactly the original canonical bytes. No serializer defaults,
validation copies, aliases or private attributes added nodes. No public result
was changed. Exact R/context/cutoff coherence and lower_sha256 were also checked
against the carried independently bound commitments. Public reconstruction here
is a calibration integrity check, **not Mode A admission, execution or result
acceptance**.

The 12,367 value is therefore accurate for replacement expansion of the retained
BH bytes. This proves reproducibility of that count, not world minimality and
not that 12,367 is an irreducible operational budget for the complete valid corpus.

## 5. Independent counting and lower-world comparison

Counter 1 recursively counts exact JSON-built-in objects: an object contributes
one plus its key count plus its value-subtree counts; an array contributes one
plus its element counts; a scalar contributes one. It additionally materializes
a diagnostic replacement-expanded tree to measure that interpretation.

Counter 2 scans independent canonical UTF-8 JSON token streams, counting opening
containers, quoted key/value tokens, numeric tokens and literal values. It does
not call Counter 1, its traversal, or its expansion function. It counts the
wire request, each closed reference stream and each referenced full Statement
stream independently, then applies each named accounting equation. No Python
object identity or shared-pointer discount enters either counter.

For each **fixed equation**, the counters agree exactly. This is not a claim
that two implementations disagree on one unambiguous mathematical function:
the unresolved defect is the frozen contract's **choice of equation**.
Both formulas were retained rather than quietly selecting the smaller count.
The old implementation's replacement measurement cannot be cited as proof of
compliance with an additive interpretation.

Sanity controls passed: an object with one scalar member has three nodes;
an empty array has one; an array with one null has two; two identical one-member
objects in an array have seven. Making those two entries the same Python object
still counts seven, just like independent serialized copies. This distinguishes
serialized-tree occurrence counting from Python-identity counting.

| Lower-world comparison | Actual evidence and verdict |
| --- | --- |
| Current BH world | Complete owning public types revalidated; 23 records; 11343 wire / 12367 replacement / 12415 additive. No proof truncation or counting inflation found. |
| Smaller honest public world | Not constructed after the counting-contract gate remained unresolved. Minimality is **unproven**, not “no smaller world exists.” No reduction is credited. |
| Potential redundant nomination | BH explicitly carries owner nomination absent from N's declared-binding route. This is a different public disclosure, not an accidentally repeated Python object. Whether an alternative nomination preserves every required boundary requires a separately constructed valid comparison; none is claimed here. |
| Shared-material/stripped-root shortcut | Rejected as a recommendation under the frozen schema: required owning public fields cannot silently become cross-root refs or disappear. A future carriage redesign would require explicit owner review. |
| Mock/stub/private/trusted-instance shortcut | Not constructed or used; cannot establish the required public reconstruction boundary. |

No new model, binding, evidence or temporal world was created. Only frozen request
bytes and temporary counting/reconstruction code were used. Neither a smaller
world nor a maximal world is asserted valid on the basis of an edited trusted
instance.

## 6. Valid-corpus register and M_valid

This table is the **complete register of requested work items**, not a claim
that a complete valid corpus has been admitted. “Unmeasured” is not zero and
must not enter a maximum calculation. No hostile case enters M_valid.
All unmeasured fields—bytes, nodes, decomposition, projection digest and full
admission—remain unavailable rather than inferred from a nearby case.

| Normative request/twin | Bytes / wire / replacement / additive nodes | Projection digest / validity / membership rationale |
| --- | --- | --- |
| Primary T1=1, T2=2 | 94819 / 6058 / 7082 / 7130 | Approved projection digest from section 2; public roots valid; original two-H/two-T/eight-cell base. No minimax run. |
| Retained BH-bearing size control | 189522 / 11343 / 12367 / 12415 | Same exact approved projection; complete public BH proof valid; optional-BH carriage measurement. This is not the not-yet-constructed BH hypothesis twin. |
| Valid tied-best | Unmeasured | Required by synthesis section 9; deferred at first gate. |
| Zero-support surprise outcome | Unmeasured | Required explicit successful code_c, ten-cell twin; deferred. |
| One-viable-hypothesis twin | Unmeasured | Required H2 baseline contradiction; not an empty/one-row shortcut. |
| Zero-viable-hypothesis setup | Unmeasured | Required both baseline contradictions; distinct from malformed zero supplied H. |
| No-partition singleton-T2 | Unmeasured | Required separately nominated candidate-set variant. |
| Nondeterministic-hypothesis twin | Unmeasured as a separate twin | Overlapping permissions already occur in the primary; that does not replace a separate corpus entry's admission. |
| Different outcome counts | Unmeasured | Required within-bounds vocabulary variation. |
| Secondary-cost-policy twin | Excluded, not admitted | Accepted plan leaves costs absent and requires separate authority for a cost variant; this investigation must not change cost policy. |
| Maximum H/T/O/cell dimensions | Unmeasured | Required valid 2 × 2 × 3 and 12-cell shape, also satisfying ≤24 Statements and all other bounds. |
| Maximum citation/provenance | Unmeasured | Required four-reference and exact text/token bounds; no arbitrary padding is counted as a valid request. |
| Maximum derivation-bearing request | Not a Mode A request arm | Derivation steps are result material, not a permitted request field. Maximum baseline-check/model-ref request shapes still require measurement. |
| Maximum baseline checks/model refs | Unmeasured | Required up to four of each per H, with resolved public selectors and approved shared Statements. |
| BH equal/different hypothesis twins | Unmeasured | Required actual BH baseline requirements and provenance, absent from the retained size-control request. |
| All-support other outcome | Unmeasured | Required explicit domain-change variant, not a decimal gap/overlap. |
| Observationally indistinguishable H | Unmeasured | Required genuinely different semantic H with equal prediction rows. |
| Complete repair twin for missing/unknown cells | Unmeasured separately | Primary byte completeness alone is not the separately committed repair. |
| Other legal at-limit shapes and cross-combinations | Unmeasured | Must include simultaneous record, Statement, citation/path and actual-product bounds; independently padding one field is not a complete maximum. |

**M_valid = not established.** The maximum of the two inspected candidates is
12,367 under replacement or 12,415 under additive charging; neither is M_valid.
No recommended cap may be inferred from those two numbers, rounded to a power
of two, or supplied with percentage headroom. No result, ranking, probability,
prior, cost preference or future milestone is produced by this register.

## 7. Determinism and reproducible evidence

Two independently created temporary roots were used:

- /tmp/brc-exp001-calibration-a-z59ZIZ
- /tmp/brc-exp001-calibration-b-BwxHBe

Each ran at PYTHONHASHSEED 1, 7 and 313. Root A preserved permissible object
construction order; root B reversed object insertion order recursively while
preserving all semantic array orders. Canonical serialization reproduced the
original request bytes before counting. Both roots independently decoded the
immutable report and reconstructed the owning public types.

All six runs returned exit 0 and produced byte-identical measurement JSON:
**33689 bytes**, SHA-256
`379dc4c44fbc7014ed0bec7ac7d5d49627772f79339e77bf67735228bc34c1f2`.
This measurement artifact is sorted compact UTF-8 JSON with **one LF** after
the JSON value. It is audit data, not a Mode A result or a new canonical request.
No root path, hash seed, current time or random identifier enters it.

Agreement covers both frozen request digests/projections, category totals, node
kinds, material/membership paths, reference/body charges and exact public
roundtrips. It does not cover an unbuilt valid corpus or a nonexistent experiment
result. Reversed object construction is not misreported as a newly produced
observation world.

Both disposable scripts had SHA-256
`d077f42ff7a4d39c897bbf10a1dba6cbc98c8657213b404f0483a8ae1407832c`.
No script source is retained in the repository. The complete audit measurement
bytes are bound below; decoded requests remain recoverable from the unchanged
resource-stop report at its independently pinned digest. Reproduction requires
only decoding those two request blocks, canonical projection comparison, the
explicit equations, and the documented independent token/tree counting rules;
no minimax implementation is needed.

Decode standard base64 after removing only displayed ASCII line breaks:

```base64-audit
eyJiaCI6eyJhZGRpdGl2ZWx5X2NoYXJnZWRfbm9kZXMiOjEyNDE1LCJhc3N1bXB0aW9uX3Byb2pl
Y3Rpb25fYnl0ZXMiOjI5MTUzLCJhc3N1bXB0aW9uX3Byb2plY3Rpb25fc2hhMjU2IjoiNGM1ZTQ4
NDUyZWU4MWE1YzY1Y2VmMmE1MWRjYWU4ZGU1NjI2MjY4NGU3MDU2YmU0MjlkZDYxNjY3ODgyNDFk
YyIsImJ5dGVzIjoxODk1MjIsImZ1bGxfbWVtYmVyc2hpcHMiOlt7Im1lbWJlcnMiOjIzLCJub2Rl
cyI6MzIsInBhdGgiOiJsb3dlci5CSC5iZWhhdmlvci5tYXRlcmlhbC5yZXZpc2lvbiIsInNoYTI1
NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1NDAwYzg5MmUzNjVlZjgzZGVm
MzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjYsIm5vZGVzIjoxNSwicGF0aCI6Imxvd2VyLkJILnBh
cnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMuMC5jYW5kaWRhdGVzLjAuaW50ZXJwcmV0YXRpb24u
cmV2aXNpb24iLCJzaGEyNTYiOiI1ZmQ2N2FhZDA0YzExMTVjNjkxNjQwNWU0MTRmODJhMTg0YjFm
Y2M1YTY3OGJiOWFmMzVlOWQ2MzQxMzViNTBkIn0seyJtZW1iZXJzIjo1LCJub2RlcyI6MTQsInBh
dGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjAuY2FuZGlkYXRlcy4w
LnZhbHVlX2NhbmRpZGF0ZS5zdGF0ZV9jYW5kaWRhdGUuYm91bmQucmVzb2x1dGlvbi5yZXZpc2lv
biIsInNoYTI1NiI6IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmExY2ZiMjVlMzMyZjIyMzUwZWM1
NjE4NjQ3NmQ5ZGM2ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjYsIm5vZGVzIjoxNSwicGF0aCI6Imxv
d2VyLkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMuMC5pbnRlcnByZXRhdGlvbl9yZXZp
c2lvbiIsInNoYTI1NiI6IjVmZDY3YWFkMDRjMTExNWM2OTE2NDA1ZTQxNGY4MmExODRiMWZjYzVh
Njc4YmI5YWYzNWU5ZDYzNDEzNWI1MGQifSx7Im1lbWJlcnMiOjIzLCJub2RlcyI6MzIsInBhdGgi
OiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjAuc2VtYW50aWNzX3Jlc3Vs
dC5yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1
NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjUsIm5vZGVzIjoxNCwi
cGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMuMC52YWx1ZV9jb21w
YXRpYmlsaXR5LmNhbmRpZGF0ZXMuMC5zdGF0ZV9jYW5kaWRhdGUuYm91bmQucmVzb2x1dGlvbi5y
ZXZpc2lvbiIsInNoYTI1NiI6IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmExY2ZiMjVlMzMyZjIy
MzUwZWM1NjE4NjQ3NmQ5ZGM2ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjIzLCJub2RlcyI6MzIsInBh
dGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjAudmFsdWVfY29tcGF0
aWJpbGl0eS5zcGVjaWZpY2F0aW9uX3Jlc3VsdC5yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEz
MGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMi
fSx7Im1lbWJlcnMiOjUsIm5vZGVzIjoxNCwicGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3Nl
bWFudGljX3Jlc3VsdHMuMC52YWx1ZV9jb21wYXRpYmlsaXR5LnN0YXRlLmJpbmRpbmdfcmV2aXNp
b24iLCJzaGEyNTYiOiI3Zjc5YjNhYzM5YTAzZDU4ZWZmZGNlOGZhMWNmYjI1ZTMzMmYyMjM1MGVj
NTYxODY0NzZkOWRjNmQ1MjhmNGY2In0seyJtZW1iZXJzIjo1LCJub2RlcyI6MTQsInBhdGgiOiJs
b3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjAudmFsdWVfY29tcGF0aWJpbGl0
eS5zdGF0ZS5jYW5kaWRhdGVzLjAuYm91bmQucmVzb2x1dGlvbi5yZXZpc2lvbiIsInNoYTI1NiI6
IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmExY2ZiMjVlMzMyZjIyMzUwZWM1NjE4NjQ3NmQ5ZGM2
ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjIzLCJub2RlcyI6MzIsInBhdGgiOiJsb3dlci5CSC5wYXJ0
aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjAudmFsdWVfY29tcGF0aWJpbGl0eS5zdGF0ZS5tb2Rl
bF9yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1
NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjYsIm5vZGVzIjoxNSwi
cGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMuMS5jYW5kaWRhdGVz
LjAuaW50ZXJwcmV0YXRpb24ucmV2aXNpb24iLCJzaGEyNTYiOiI1ZmQ2N2FhZDA0YzExMTVjNjkx
NjQwNWU0MTRmODJhMTg0YjFmY2M1YTY3OGJiOWFmMzVlOWQ2MzQxMzViNTBkIn0seyJtZW1iZXJz
Ijo1LCJub2RlcyI6MTQsInBhdGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1
bHRzLjEuY2FuZGlkYXRlcy4wLnZhbHVlX2NhbmRpZGF0ZS5zdGF0ZV9jYW5kaWRhdGUuYm91bmQu
cmVzb2x1dGlvbi5yZXZpc2lvbiIsInNoYTI1NiI6IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmEx
Y2ZiMjVlMzMyZjIyMzUwZWM1NjE4NjQ3NmQ5ZGM2ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjYsIm5v
ZGVzIjoxNSwicGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMuMS5p
bnRlcnByZXRhdGlvbl9yZXZpc2lvbiIsInNoYTI1NiI6IjVmZDY3YWFkMDRjMTExNWM2OTE2NDA1
ZTQxNGY4MmExODRiMWZjYzVhNjc4YmI5YWYzNWU5ZDYzNDEzNWI1MGQifSx7Im1lbWJlcnMiOjIz
LCJub2RlcyI6MzIsInBhdGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRz
LjEuc2VtYW50aWNzX3Jlc3VsdC5yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZl
NzRlYWI2NTBmNDgyMzAxYTM1NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJl
cnMiOjUsIm5vZGVzIjoxNCwicGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jl
c3VsdHMuMS52YWx1ZV9jb21wYXRpYmlsaXR5LmNhbmRpZGF0ZXMuMC5zdGF0ZV9jYW5kaWRhdGUu
Ym91bmQucmVzb2x1dGlvbi5yZXZpc2lvbiIsInNoYTI1NiI6IjdmNzliM2FjMzlhMDNkNThlZmZk
Y2U4ZmExY2ZiMjVlMzMyZjIyMzUwZWM1NjE4NjQ3NmQ5ZGM2ZDUyOGY0ZjYifSx7Im1lbWJlcnMi
OjIzLCJub2RlcyI6MzIsInBhdGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1
bHRzLjEudmFsdWVfY29tcGF0aWJpbGl0eS5zcGVjaWZpY2F0aW9uX3Jlc3VsdC5yZXZpc2lvbiIs
InNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1NDAwYzg5MmUzNjVl
ZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjUsIm5vZGVzIjoxNCwicGF0aCI6Imxvd2Vy
LkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMuMS52YWx1ZV9jb21wYXRpYmlsaXR5LnN0
YXRlLmJpbmRpbmdfcmV2aXNpb24iLCJzaGEyNTYiOiI3Zjc5YjNhYzM5YTAzZDU4ZWZmZGNlOGZh
MWNmYjI1ZTMzMmYyMjM1MGVjNTYxODY0NzZkOWRjNmQ1MjhmNGY2In0seyJtZW1iZXJzIjo1LCJu
b2RlcyI6MTQsInBhdGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjEu
dmFsdWVfY29tcGF0aWJpbGl0eS5zdGF0ZS5jYW5kaWRhdGVzLjAuYm91bmQucmVzb2x1dGlvbi5y
ZXZpc2lvbiIsInNoYTI1NiI6IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmExY2ZiMjVlMzMyZjIy
MzUwZWM1NjE4NjQ3NmQ5ZGM2ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjIzLCJub2RlcyI6MzIsInBh
dGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjEudmFsdWVfY29tcGF0
aWJpbGl0eS5zdGF0ZS5tb2RlbF9yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZl
NzRlYWI2NTBmNDgyMzAxYTM1NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJl
cnMiOjIzLCJub2RlcyI6MzIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJldmlzaW9uIiwic2hh
MjU2IjoiMjE0Yzk5YTMwYmVmZmNlNmU3NGVhYjY1MGY0ODIzMDFhMzU0MDBjODkyZTM2NWVmODNk
ZWYzMGM4ZDZjNjRhMyJ9LHsibWVtYmVycyI6MjMsIm5vZGVzIjozMiwicGF0aCI6Imxvd2VyLk4u
Y29uc3RyYWludC5yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBm
NDgyMzAxYTM1NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjYsIm5v
ZGVzIjoxNSwicGF0aCI6Imxvd2VyLk4uc2VtYW50aWNfY29tcGF0aWJpbGl0eS5jYW5kaWRhdGVz
LjAuaW50ZXJwcmV0YXRpb24ucmV2aXNpb24iLCJzaGEyNTYiOiI1ZmQ2N2FhZDA0YzExMTVjNjkx
NjQwNWU0MTRmODJhMTg0YjFmY2M1YTY3OGJiOWFmMzVlOWQ2MzQxMzViNTBkIn0seyJtZW1iZXJz
Ijo1LCJub2RlcyI6MTQsInBhdGgiOiJsb3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkuY2Fu
ZGlkYXRlcy4wLnZhbHVlX2NhbmRpZGF0ZS5zdGF0ZV9jYW5kaWRhdGUuYm91bmQucmVzb2x1dGlv
bi5yZXZpc2lvbiIsInNoYTI1NiI6IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmExY2ZiMjVlMzMy
ZjIyMzUwZWM1NjE4NjQ3NmQ5ZGM2ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjYsIm5vZGVzIjoxNSwi
cGF0aCI6Imxvd2VyLk4uc2VtYW50aWNfY29tcGF0aWJpbGl0eS5pbnRlcnByZXRhdGlvbl9yZXZp
c2lvbiIsInNoYTI1NiI6IjVmZDY3YWFkMDRjMTExNWM2OTE2NDA1ZTQxNGY4MmExODRiMWZjYzVh
Njc4YmI5YWYzNWU5ZDYzNDEzNWI1MGQifSx7Im1lbWJlcnMiOjIzLCJub2RlcyI6MzIsInBhdGgi
OiJsb3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkuc2VtYW50aWNzX3Jlc3VsdC5yZXZpc2lv
biIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1NDAwYzg5MmUz
NjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjUsIm5vZGVzIjoxNCwicGF0aCI6Imxv
d2VyLk4uc2VtYW50aWNfY29tcGF0aWJpbGl0eS52YWx1ZV9jb21wYXRpYmlsaXR5LmNhbmRpZGF0
ZXMuMC5zdGF0ZV9jYW5kaWRhdGUuYm91bmQucmVzb2x1dGlvbi5yZXZpc2lvbiIsInNoYTI1NiI6
IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmExY2ZiMjVlMzMyZjIyMzUwZWM1NjE4NjQ3NmQ5ZGM2
ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjIzLCJub2RlcyI6MzIsInBhdGgiOiJsb3dlci5OLnNlbWFu
dGljX2NvbXBhdGliaWxpdHkudmFsdWVfY29tcGF0aWJpbGl0eS5zcGVjaWZpY2F0aW9uX3Jlc3Vs
dC5yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1
NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjUsIm5vZGVzIjoxNCwi
cGF0aCI6Imxvd2VyLk4uc2VtYW50aWNfY29tcGF0aWJpbGl0eS52YWx1ZV9jb21wYXRpYmlsaXR5
LnN0YXRlLmJpbmRpbmdfcmV2aXNpb24iLCJzaGEyNTYiOiI3Zjc5YjNhYzM5YTAzZDU4ZWZmZGNl
OGZhMWNmYjI1ZTMzMmYyMjM1MGVjNTYxODY0NzZkOWRjNmQ1MjhmNGY2In0seyJtZW1iZXJzIjo1
LCJub2RlcyI6MTQsInBhdGgiOiJsb3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkudmFsdWVf
Y29tcGF0aWJpbGl0eS5zdGF0ZS5jYW5kaWRhdGVzLjAuYm91bmQucmVzb2x1dGlvbi5yZXZpc2lv
biIsInNoYTI1NiI6IjdmNzliM2FjMzlhMDNkNThlZmZkY2U4ZmExY2ZiMjVlMzMyZjIyMzUwZWM1
NjE4NjQ3NmQ5ZGM2ZDUyOGY0ZjYifSx7Im1lbWJlcnMiOjIzLCJub2RlcyI6MzIsInBhdGgiOiJs
b3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkudmFsdWVfY29tcGF0aWJpbGl0eS5zdGF0ZS5t
b2RlbF9yZXZpc2lvbiIsInNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAx
YTM1NDAwYzg5MmUzNjVlZjgzZGVmMzBjOGQ2YzY0YTMifSx7Im1lbWJlcnMiOjUsIm5vZGVzIjox
NCwicGF0aCI6Imxvd2VyX2NvbW1pdG1lbnRzLmJpbmRpbmdfcmV2aXNpb24iLCJzaGEyNTYiOiI3
Zjc5YjNhYzM5YTAzZDU4ZWZmZGNlOGZhMWNmYjI1ZTMzMmYyMjM1MGVjNTYxODY0NzZkOWRjNmQ1
MjhmNGY2In0seyJtZW1iZXJzIjo2LCJub2RlcyI6MTUsInBhdGgiOiJsb3dlcl9jb21taXRtZW50
cy5pbnRlcnByZXRhdGlvbl9yZXZpc2lvbiIsInNoYTI1NiI6IjVmZDY3YWFkMDRjMTExNWM2OTE2
NDA1ZTQxNGY4MmExODRiMWZjYzVhNjc4YmI5YWYzNWU5ZDYzNDEzNWI1MGQifSx7Im1lbWJlcnMi
OjIzLCJub2RlcyI6MzIsInBhdGgiOiJsb3dlcl9jb21taXRtZW50cy5tb2RlbF9yZXZpc2lvbiIs
InNoYTI1NiI6IjIxNGM5OWEzMGJlZmZjZTZlNzRlYWI2NTBmNDgyMzAxYTM1NDAwYzg5MmUzNjVl
ZjgzZGVmMzBjOGQ2YzY0YTMifV0sImluZGVwZW5kZW50X29yYWNsZV9hZ3JlZXMiOnRydWUsImxv
d2VyX3Jvb3RzIjp7IkJIIjo0OTA5LCJFIjo4MDIsIkYiOjEzMjAsIk4iOjE5NTF9LCJtYXRlcmlh
bHMiOlt7ImJ5dGVzIjoxOTQ3Niwibm9kZXMiOjExMjAsInBhdGgiOiJsb3dlci5CSC5iZWhhdmlv
ci5tYXRlcmlhbCIsInJlY29yZHMiOjIzLCJzaGEyNTYiOiI3YmQyYzQxMTBkZDc3YjU4ZDlkNmFi
OGU5YTZmMWE3ODgxOTY4NjY5NmI5NmI0MDZlNzU1ODdkMGM1ODRmYjcxIn0seyJieXRlcyI6MTk0
NzYsIm5vZGVzIjoxMTIwLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbCIsInJlY29yZHMiOjIzLCJz
aGEyNTYiOiI3YmQyYzQxMTBkZDc3YjU4ZDlkNmFiOGU5YTZmMWE3ODgxOTY4NjY5NmI5NmI0MDZl
NzU1ODdkMGM1ODRmYjcxIn1dLCJtb2RlbF9yZWNvcmRfb2NjdXJyZW5jZXMiOlt7ImlkIjoiYmhk
X2FkNGUwZGRmN2E2NGNjZTZhMzE4ZjdkNTQ5ZTllMzUwZWE1MmIzMDZjODc4Y2U4NzQzYjExMWMw
MGI4ZmYwNWUiLCJraW5kIjoiYmVoYXZpb3JfcnVsZV9kZWNsYXJhdGlvbiIsInBhdGgiOiJsb3dl
ci5CSC5iZWhhdmlvci5tYXRlcmlhbC5yZWNvcmRzLjAifSx7ImlkIjoiYnJnX2ZjZmFhYjJkZjA3
ODBhMGI4MzEwNjFjNjNiNGVmMjMxMmFmZTI1NTc4NzM4NzYyMjM4NDhkZDlmZmY0NzY3N2YiLCJr
aW5kIjoiYmVoYXZpb3JfcmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2VyLkJILmJlaGF2aW9yLm1h
dGVyaWFsLnJlY29yZHMuMSJ9LHsiaWQiOiJjcmdfYmVkMjAxMTUyMGY2NjEyYzI0NzY2M2E0MGZl
MTc4NjY4OTU0MDkzMmM2MGZlYjJmNDcyZjlkNmMxOTUyMDU4ZiIsImtpbmQiOiJjb25zdHJhaW50
X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dlci5CSC5iZWhhdmlvci5tYXRlcmlhbC5yZWNvcmRz
LjIifSx7ImlkIjoiZmNkXzk3MTgyMGQzZTQwYWVlNDBlMjlkMjA3Njg2M2M5ZTk1YjE5Y2M5YTNm
M2RkZTJlYzIzZTZhMjMxYTkyMDgwNjkiLCJraW5kIjoiZmxvd19vcGVyYXRpbmdfY3JpdGVyaW9u
X2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkJILmJlaGF2aW9yLm1hdGVyaWFsLnJlY29yZHMu
MyJ9LHsiaWQiOiJmbGRfODhiY2Y1NmZmZjAzMTBiNTI0YTdmM2RlYmU5NDViNWJkMDEzODk0MjY5
N2JkMGFjMjUyMjhiYzQ5NGU4OTA1ZiIsImtpbmQiOiJmbG93X2RlY2xhcmF0aW9uIiwicGF0aCI6
Imxvd2VyLkJILmJlaGF2aW9yLm1hdGVyaWFsLnJlY29yZHMuNCJ9LHsiaWQiOiJmbWFfZjI4NjAz
NGVmZDU2NGIxY2MxNWI4MmY2MWUyMmQ4NDUyZmU2OWU3MWIzZGVmMmQwMGExM2QyYjE0ZDMzZGJk
ZSIsImtpbmQiOiJmbG93X21lYXN1cmVtZW50X2Fzc29jaWF0aW9uIiwicGF0aCI6Imxvd2VyLkJI
LmJlaGF2aW9yLm1hdGVyaWFsLnJlY29yZHMuNSJ9LHsiaWQiOiJmcmdfNDJkNzk5NGExOWQ2MjQ2
OTI3ZjI0NTM4NTk4ZWE4ZTE2YmQ2YTY1YWU4N2E0OTNlNjNkYTY5NjdhMDcwY2NhMCIsImtpbmQi
OiJmbG93X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dlci5CSC5iZWhhdmlvci5tYXRlcmlhbC5y
ZWNvcmRzLjYifSx7ImlkIjoicGNuXzdkNzE3N2FiZmFmYTg1ZmUxNzI0OGJiYjVkZTU5MmE1OTM3
ODlmNjY0MGUwZDgxZGM3NjAwOWQ0MDY3M2U5ZTkiLCJraW5kIjoicG9ydF9jb25uZWN0aW9uX2Fz
c2VydGlvbiIsInBhdGgiOiJsb3dlci5CSC5iZWhhdmlvci5tYXRlcmlhbC5yZWNvcmRzLjcifSx7
ImlkIjoicGlmXzBkMjYyZjQ3OTM3MzJiZTI0NTI5NjBhNzgwZjI1MzI2NGI2ODE1MDBhZDg0NTBk
MDVlNWUzNWZmZjg3N2JiNzIiLCJraW5kIjoicG9ydF9pbnRlcmZhY2VfZGVjbGFyYXRpb24iLCJw
YXRoIjoibG93ZXIuQkguYmVoYXZpb3IubWF0ZXJpYWwucmVjb3Jkcy44In0seyJpZCI6InBpZl9k
OGE0MmYyNWNlOTMxYjA0YzRjMjAwNDgyZjEyYjhhMjYxNTMyZDhiMDU2ZTU3NTViZmE1NDRjZDYz
MGQxZTZkIiwia2luZCI6InBvcnRfaW50ZXJmYWNlX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2Vy
LkJILmJlaGF2aW9yLm1hdGVyaWFsLnJlY29yZHMuOSJ9LHsiaWQiOiJwcmdfMTcyYjBjZjIxMDM2
Mzc4N2U0YjBlMGVjYTdkYjVlNzUzNGE0MGVmNjM4NzQ2ZmYzNDBiMzA5MDYyNTIyZWE4OSIsImtp
bmQiOiJwb3J0X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dlci5CSC5iZWhhdmlvci5tYXRlcmlh
bC5yZWNvcmRzLjEwIn0seyJpZCI6InByZ18zNzU5NDA2ZDkwMjU5YTU4ZmRiMjRmNjZkZWRlYWYz
NjZlYTdiYjNmZDRjNDM4OGI2YWY1YTVjZTAwMGQ5MjExIiwia2luZCI6InBvcnRfcmVnaXN0cmF0
aW9uIiwicGF0aCI6Imxvd2VyLkJILmJlaGF2aW9yLm1hdGVyaWFsLnJlY29yZHMuMTEifSx7Imlk
IjoicmVnXzI3YzM2ZTY3MWUwMTQ3YzllMjM1YmRhYzkyNDFlZjcyZDRmY2RkMzg0MzZkMzViNzI3
ZTY2MTA5ZGQ2Yzc4MTkiLCJraW5kIjoiZW50aXR5X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dl
ci5CSC5iZWhhdmlvci5tYXRlcmlhbC5yZWNvcmRzLjEyIn0seyJpZCI6InZjbl9hNjNkNGYzZWQy
MzYwNDI3YTdjOTBmMjM2NzgxODE0YWEyYTZhNTYwYTcyZTlkODE5MWJjNWQ4NWY3ZmUyYTEyIiwi
a2luZCI6InZhcmlhYmxlX2NvbnN0cmFpbnRfZGVjbGFyYXRpb24iLCJwYXRoIjoibG93ZXIuQkgu
YmVoYXZpb3IubWF0ZXJpYWwucmVjb3Jkcy4xMyJ9LHsiaWQiOiJ2cGFfZTA1MDEwNGRkOGFkNmMx
MGYxODRkYTY3ZTRiNDdlYmRlMmJiYjAwODA5ZDhmZDAwMzc0MWZmYzFiYzc5MjYyNyIsImtpbmQi
OiJ2YXJpYWJsZV9wb3J0X2Fzc29jaWF0aW9uIiwicGF0aCI6Imxvd2VyLkJILmJlaGF2aW9yLm1h
dGVyaWFsLnJlY29yZHMuMTQifSx7ImlkIjoidnJnXzU0M2Y4NzU1MjA1OGQyMmFmN2QzMTE1NGZk
MGNhZmExZmMzZGM0NWQ4YzhiODNjMWYwY2Q2ODRlYzUwOGYwYmQiLCJraW5kIjoidmFyaWFibGVf
cmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2VyLkJILmJlaGF2aW9yLm1hdGVyaWFsLnJlY29yZHMu
MTUifSx7ImlkIjoidnJnX2MyNTU2Y2QwOTVhNmVlMzEwOTg2OGQ5MWI1NDkwODNiMTM4NzY3ZmI2
N2JjYzY2MThiNTUzODcwMDE4NDcyMzUiLCJraW5kIjoidmFyaWFibGVfcmVnaXN0cmF0aW9uIiwi
cGF0aCI6Imxvd2VyLkJILmJlaGF2aW9yLm1hdGVyaWFsLnJlY29yZHMuMTYifSx7ImlkIjoidnNt
XzUxMGMyMGJjMzkyZDc5YjhjODQ5MDE5MDY3ODQ3NTk3MWY5MzFmODUzZDE4OGI5MDYzMTM2YWU1
YmE1MzkwOWIiLCJraW5kIjoidmFyaWFibGVfc2VtYW50aWNfZGVjbGFyYXRpb24iLCJwYXRoIjoi
bG93ZXIuQkguYmVoYXZpb3IubWF0ZXJpYWwucmVjb3Jkcy4xNyJ9LHsiaWQiOiJ2c21fYWI2Yjg2
NDljY2IxMTI0ZWE2MTZkNjY2NzEzZWIzYTQxOGRiZDhiYjM1ODkyNjBlMzY5ZmYzNjUzZDBkMzdm
ZSIsImtpbmQiOiJ2YXJpYWJsZV9zZW1hbnRpY19kZWNsYXJhdGlvbiIsInBhdGgiOiJsb3dlci5C
SC5iZWhhdmlvci5tYXRlcmlhbC5yZWNvcmRzLjE4In0seyJpZCI6InZzbV9lYzdjNzU5YTY5ZmFm
NmQ3MWQ0NDRhMTJjYjA3YWYzNGI0NjA4MGQyN2I5YTljY2FiNzBhN2UzNDJkNmIzNGY4Iiwia2lu
ZCI6InZhcmlhYmxlX3NlbWFudGljX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkJILmJlaGF2
aW9yLm1hdGVyaWFsLnJlY29yZHMuMTkifSx7ImlkIjoidnNtX2Y3YzA5NTQyMWIwNjllMTIyZDI2
NDBhOTc0NDUzNzI5MDQ5NGNiOGY1ZTA5YjNhNzBkNjliODg0MzRjNTI3YjgiLCJraW5kIjoidmFy
aWFibGVfc2VtYW50aWNfZGVjbGFyYXRpb24iLCJwYXRoIjoibG93ZXIuQkguYmVoYXZpb3IubWF0
ZXJpYWwucmVjb3Jkcy4yMCJ9LHsiaWQiOiJ2c3BfNmUzOGJiODZhZTg5N2MwYTAxOGRkYzkxZTQx
NmRjNDMzZDM5YTI3YmRjYTExYjA3ZWRkNmRkMmE4MGZkZTYyYSIsImtpbmQiOiJ2YXJpYWJsZV92
YWx1ZV9zcGVjaWZpY2F0aW9uIiwicGF0aCI6Imxvd2VyLkJILmJlaGF2aW9yLm1hdGVyaWFsLnJl
Y29yZHMuMjEifSx7ImlkIjoidnNwX2I4ZTA0MGY5YmEyZDZmNjJlMGQ4MTBkMjFlODAwYjVhZTJm
NDRmMzdhMWQwY2I4OTY5OWU1ZTFiOTY3YjIxMTkiLCJraW5kIjoidmFyaWFibGVfdmFsdWVfc3Bl
Y2lmaWNhdGlvbiIsInBhdGgiOiJsb3dlci5CSC5iZWhhdmlvci5tYXRlcmlhbC5yZWNvcmRzLjIy
In0seyJpZCI6InZzbV9hYjZiODY0OWNjYjExMjRlYTYxNmQ2NjY3MTNlYjNhNDE4ZGJkOGJiMzU4
OTI2MGUzNjlmZjM2NTNkMGQzN2ZlIiwia2luZCI6InZhcmlhYmxlX3NlbWFudGljX2RlY2xhcmF0
aW9uIiwicGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMuMC5zZW1h
bnRpY3NfcmVzdWx0Lm9ic2VydmF0aW9uX3JvbGUuZGVjbGFyYXRpb24ifSx7ImlkIjoidnNtX2Y3
YzA5NTQyMWIwNjllMTIyZDI2NDBhOTc0NDUzNzI5MDQ5NGNiOGY1ZTA5YjNhNzBkNjliODg0MzRj
NTI3YjgiLCJraW5kIjoidmFyaWFibGVfc2VtYW50aWNfZGVjbGFyYXRpb24iLCJwYXRoIjoibG93
ZXIuQkgucGFydGljaXBhbnRfc2VtYW50aWNfcmVzdWx0cy4wLnNlbWFudGljc19yZXN1bHQucXVh
bnRpdHlfa2luZC5kZWNsYXJhdGlvbiJ9LHsiaWQiOiJ2c3BfNmUzOGJiODZhZTg5N2MwYTAxOGRk
YzkxZTQxNmRjNDMzZDM5YTI3YmRjYTExYjA3ZWRkNmRkMmE4MGZkZTYyYSIsImtpbmQiOiJ2YXJp
YWJsZV92YWx1ZV9zcGVjaWZpY2F0aW9uIiwicGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3Nl
bWFudGljX3Jlc3VsdHMuMC52YWx1ZV9jb21wYXRpYmlsaXR5LnNwZWNpZmljYXRpb25fcmVzdWx0
LnNwZWNpZmljYXRpb24ifSx7ImlkIjoicmVnXzI3YzM2ZTY3MWUwMTQ3YzllMjM1YmRhYzkyNDFl
ZjcyZDRmY2RkMzg0MzZkMzViNzI3ZTY2MTA5ZGQ2Yzc4MTkiLCJraW5kIjoiZW50aXR5X3JlZ2lz
dHJhdGlvbiIsInBhdGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjAu
dmFsdWVfY29tcGF0aWJpbGl0eS5zdGF0ZS5vd25lcl9yZWdpc3RyYXRpb24ifSx7ImlkIjoicmVn
XzI3YzM2ZTY3MWUwMTQ3YzllMjM1YmRhYzkyNDFlZjcyZDRmY2RkMzg0MzZkMzViNzI3ZTY2MTA5
ZGQ2Yzc4MTkiLCJraW5kIjoiZW50aXR5X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dlci5CSC5w
YXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjAudmFsdWVfY29tcGF0aWJpbGl0eS5zdGF0ZS5y
ZXF1ZXN0ZWRfZW50aXR5X3JlZ2lzdHJhdGlvbiJ9LHsiaWQiOiJ2cmdfNTQzZjg3NTUyMDU4ZDIy
YWY3ZDMxMTU0ZmQwY2FmYTFmYzNkYzQ1ZDhjOGI4M2MxZjBjZDY4NGVjNTA4ZjBiZCIsImtpbmQi
OiJ2YXJpYWJsZV9yZWdpc3RyYXRpb24iLCJwYXRoIjoibG93ZXIuQkgucGFydGljaXBhbnRfc2Vt
YW50aWNfcmVzdWx0cy4wLnZhbHVlX2NvbXBhdGliaWxpdHkuc3RhdGUudmFyaWFibGVfcmVnaXN0
cmF0aW9uIn0seyJpZCI6InZzbV9lYzdjNzU5YTY5ZmFmNmQ3MWQ0NDRhMTJjYjA3YWYzNGI0NjA4
MGQyN2I5YTljY2FiNzBhN2UzNDJkNmIzNGY4Iiwia2luZCI6InZhcmlhYmxlX3NlbWFudGljX2Rl
Y2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkJILnBhcnRpY2lwYW50X3NlbWFudGljX3Jlc3VsdHMu
MS5zZW1hbnRpY3NfcmVzdWx0Lm9ic2VydmF0aW9uX3JvbGUuZGVjbGFyYXRpb24ifSx7ImlkIjoi
dnNtXzUxMGMyMGJjMzkyZDc5YjhjODQ5MDE5MDY3ODQ3NTk3MWY5MzFmODUzZDE4OGI5MDYzMTM2
YWU1YmE1MzkwOWIiLCJraW5kIjoidmFyaWFibGVfc2VtYW50aWNfZGVjbGFyYXRpb24iLCJwYXRo
IjoibG93ZXIuQkgucGFydGljaXBhbnRfc2VtYW50aWNfcmVzdWx0cy4xLnNlbWFudGljc19yZXN1
bHQucXVhbnRpdHlfa2luZC5kZWNsYXJhdGlvbiJ9LHsiaWQiOiJ2c3BfYjhlMDQwZjliYTJkNmY2
MmUwZDgxMGQyMWU4MDBiNWFlMmY0NGYzN2ExZDBjYjg5Njk5ZTVlMWI5NjdiMjExOSIsImtpbmQi
OiJ2YXJpYWJsZV92YWx1ZV9zcGVjaWZpY2F0aW9uIiwicGF0aCI6Imxvd2VyLkJILnBhcnRpY2lw
YW50X3NlbWFudGljX3Jlc3VsdHMuMS52YWx1ZV9jb21wYXRpYmlsaXR5LnNwZWNpZmljYXRpb25f
cmVzdWx0LnNwZWNpZmljYXRpb24ifSx7ImlkIjoicmVnXzI3YzM2ZTY3MWUwMTQ3YzllMjM1YmRh
YzkyNDFlZjcyZDRmY2RkMzg0MzZkMzViNzI3ZTY2MTA5ZGQ2Yzc4MTkiLCJraW5kIjoiZW50aXR5
X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dlci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1
bHRzLjEudmFsdWVfY29tcGF0aWJpbGl0eS5zdGF0ZS5vd25lcl9yZWdpc3RyYXRpb24ifSx7Imlk
IjoicmVnXzI3YzM2ZTY3MWUwMTQ3YzllMjM1YmRhYzkyNDFlZjcyZDRmY2RkMzg0MzZkMzViNzI3
ZTY2MTA5ZGQ2Yzc4MTkiLCJraW5kIjoiZW50aXR5X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dl
ci5CSC5wYXJ0aWNpcGFudF9zZW1hbnRpY19yZXN1bHRzLjEudmFsdWVfY29tcGF0aWJpbGl0eS5z
dGF0ZS5yZXF1ZXN0ZWRfZW50aXR5X3JlZ2lzdHJhdGlvbiJ9LHsiaWQiOiJ2cmdfYzI1NTZjZDA5
NWE2ZWUzMTA5ODY4ZDkxYjU0OTA4M2IxMzg3NjdmYjY3YmNjNjYxOGI1NTM4NzAwMTg0NzIzNSIs
ImtpbmQiOiJ2YXJpYWJsZV9yZWdpc3RyYXRpb24iLCJwYXRoIjoibG93ZXIuQkgucGFydGljaXBh
bnRfc2VtYW50aWNfcmVzdWx0cy4xLnZhbHVlX2NvbXBhdGliaWxpdHkuc3RhdGUudmFyaWFibGVf
cmVnaXN0cmF0aW9uIn0seyJpZCI6ImJoZF9hZDRlMGRkZjdhNjRjY2U2YTMxOGY3ZDU0OWU5ZTM1
MGVhNTJiMzA2Yzg3OGNlODc0M2IxMTFjMDBiOGZmMDVlIiwia2luZCI6ImJlaGF2aW9yX3J1bGVf
ZGVjbGFyYXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjAifSx7ImlkIjoi
YnJnX2ZjZmFhYjJkZjA3ODBhMGI4MzEwNjFjNjNiNGVmMjMxMmFmZTI1NTc4NzM4NzYyMjM4NDhk
ZDlmZmY0NzY3N2YiLCJraW5kIjoiYmVoYXZpb3JfcmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2Vy
LkYubWF0ZXJpYWwucmVjb3Jkcy4xIn0seyJpZCI6ImNyZ19iZWQyMDExNTIwZjY2MTJjMjQ3NjYz
YTQwZmUxNzg2Njg5NTQwOTMyYzYwZmViMmY0NzJmOWQ2YzE5NTIwNThmIiwia2luZCI6ImNvbnN0
cmFpbnRfcmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJpYWwucmVjb3Jkcy4yIn0s
eyJpZCI6ImZjZF85NzE4MjBkM2U0MGFlZTQwZTI5ZDIwNzY4NjNjOWU5NWIxOWNjOWEzZjNkZGUy
ZWMyM2U2YTIzMWE5MjA4MDY5Iiwia2luZCI6ImZsb3dfb3BlcmF0aW5nX2NyaXRlcmlvbl9kZWNs
YXJhdGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuMyJ9LHsiaWQiOiJmbGRf
ODhiY2Y1NmZmZjAzMTBiNTI0YTdmM2RlYmU5NDViNWJkMDEzODk0MjY5N2JkMGFjMjUyMjhiYzQ5
NGU4OTA1ZiIsImtpbmQiOiJmbG93X2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJp
YWwucmVjb3Jkcy40In0seyJpZCI6ImZtYV9mMjg2MDM0ZWZkNTY0YjFjYzE1YjgyZjYxZTIyZDg0
NTJmZTY5ZTcxYjNkZWYyZDAwYTEzZDJiMTRkMzNkYmRlIiwia2luZCI6ImZsb3dfbWVhc3VyZW1l
bnRfYXNzb2NpYXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjUifSx7Imlk
IjoiZnJnXzQyZDc5OTRhMTlkNjI0NjkyN2YyNDUzODU5OGVhOGUxNmJkNmE2NWFlODdhNDkzZTYz
ZGE2OTY3YTA3MGNjYTAiLCJraW5kIjoiZmxvd19yZWdpc3RyYXRpb24iLCJwYXRoIjoibG93ZXIu
Ri5tYXRlcmlhbC5yZWNvcmRzLjYifSx7ImlkIjoicGNuXzdkNzE3N2FiZmFmYTg1ZmUxNzI0OGJi
YjVkZTU5MmE1OTM3ODlmNjY0MGUwZDgxZGM3NjAwOWQ0MDY3M2U5ZTkiLCJraW5kIjoicG9ydF9j
b25uZWN0aW9uX2Fzc2VydGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuNyJ9
LHsiaWQiOiJwaWZfMGQyNjJmNDc5MzczMmJlMjQ1Mjk2MGE3ODBmMjUzMjY0YjY4MTUwMGFkODQ1
MGQwNWU1ZTM1ZmZmODc3YmI3MiIsImtpbmQiOiJwb3J0X2ludGVyZmFjZV9kZWNsYXJhdGlvbiIs
InBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuOCJ9LHsiaWQiOiJwaWZfZDhhNDJmMjVj
ZTkzMWIwNGM0YzIwMDQ4MmYxMmI4YTI2MTUzMmQ4YjA1NmU1NzU1YmZhNTQ0Y2Q2MzBkMWU2ZCIs
ImtpbmQiOiJwb3J0X2ludGVyZmFjZV9kZWNsYXJhdGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVy
aWFsLnJlY29yZHMuOSJ9LHsiaWQiOiJwcmdfMTcyYjBjZjIxMDM2Mzc4N2U0YjBlMGVjYTdkYjVl
NzUzNGE0MGVmNjM4NzQ2ZmYzNDBiMzA5MDYyNTIyZWE4OSIsImtpbmQiOiJwb3J0X3JlZ2lzdHJh
dGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuMTAifSx7ImlkIjoicHJnXzM3
NTk0MDZkOTAyNTlhNThmZGIyNGY2NmRlZGVhZjM2NmVhN2JiM2ZkNGM0Mzg4YjZhZjVhNWNlMDAw
ZDkyMTEiLCJraW5kIjoicG9ydF9yZWdpc3RyYXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlh
bC5yZWNvcmRzLjExIn0seyJpZCI6InJlZ18yN2MzNmU2NzFlMDE0N2M5ZTIzNWJkYWM5MjQxZWY3
MmQ0ZmNkZDM4NDM2ZDM1YjcyN2U2NjEwOWRkNmM3ODE5Iiwia2luZCI6ImVudGl0eV9yZWdpc3Ry
YXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjEyIn0seyJpZCI6InZjbl9h
NjNkNGYzZWQyMzYwNDI3YTdjOTBmMjM2NzgxODE0YWEyYTZhNTYwYTcyZTlkODE5MWJjNWQ4NWY3
ZmUyYTEyIiwia2luZCI6InZhcmlhYmxlX2NvbnN0cmFpbnRfZGVjbGFyYXRpb24iLCJwYXRoIjoi
bG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjEzIn0seyJpZCI6InZwYV9lMDUwMTA0ZGQ4YWQ2YzEw
ZjE4NGRhNjdlNGI0N2ViZGUyYmJiMDA4MDlkOGZkMDAzNzQxZmZjMWJjNzkyNjI3Iiwia2luZCI6
InZhcmlhYmxlX3BvcnRfYXNzb2NpYXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZWNv
cmRzLjE0In0seyJpZCI6InZyZ181NDNmODc1NTIwNThkMjJhZjdkMzExNTRmZDBjYWZhMWZjM2Rj
NDVkOGM4YjgzYzFmMGNkNjg0ZWM1MDhmMGJkIiwia2luZCI6InZhcmlhYmxlX3JlZ2lzdHJhdGlv
biIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuMTUifSx7ImlkIjoidnJnX2MyNTU2
Y2QwOTVhNmVlMzEwOTg2OGQ5MWI1NDkwODNiMTM4NzY3ZmI2N2JjYzY2MThiNTUzODcwMDE4NDcy
MzUiLCJraW5kIjoidmFyaWFibGVfcmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJp
YWwucmVjb3Jkcy4xNiJ9LHsiaWQiOiJ2c21fNTEwYzIwYmMzOTJkNzliOGM4NDkwMTkwNjc4NDc1
OTcxZjkzMWY4NTNkMTg4YjkwNjMxMzZhZTViYTUzOTA5YiIsImtpbmQiOiJ2YXJpYWJsZV9zZW1h
bnRpY19kZWNsYXJhdGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuMTcifSx7
ImlkIjoidnNtX2FiNmI4NjQ5Y2NiMTEyNGVhNjE2ZDY2NjcxM2ViM2E0MThkYmQ4YmIzNTg5MjYw
ZTM2OWZmMzY1M2QwZDM3ZmUiLCJraW5kIjoidmFyaWFibGVfc2VtYW50aWNfZGVjbGFyYXRpb24i
LCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjE4In0seyJpZCI6InZzbV9lYzdjNzU5
YTY5ZmFmNmQ3MWQ0NDRhMTJjYjA3YWYzNGI0NjA4MGQyN2I5YTljY2FiNzBhN2UzNDJkNmIzNGY4
Iiwia2luZCI6InZhcmlhYmxlX3NlbWFudGljX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkYu
bWF0ZXJpYWwucmVjb3Jkcy4xOSJ9LHsiaWQiOiJ2c21fZjdjMDk1NDIxYjA2OWUxMjJkMjY0MGE5
NzQ0NTM3MjkwNDk0Y2I4ZjVlMDliM2E3MGQ2OWI4ODQzNGM1MjdiOCIsImtpbmQiOiJ2YXJpYWJs
ZV9zZW1hbnRpY19kZWNsYXJhdGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMu
MjAifSx7ImlkIjoidnNwXzZlMzhiYjg2YWU4OTdjMGEwMThkZGM5MWU0MTZkYzQzM2QzOWEyN2Jk
Y2ExMWIwN2VkZDZkZDJhODBmZGU2MmEiLCJraW5kIjoidmFyaWFibGVfdmFsdWVfc3BlY2lmaWNh
dGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuMjEifSx7ImlkIjoidnNwX2I4
ZTA0MGY5YmEyZDZmNjJlMGQ4MTBkMjFlODAwYjVhZTJmNDRmMzdhMWQwY2I4OTY5OWU1ZTFiOTY3
YjIxMTkiLCJraW5kIjoidmFyaWFibGVfdmFsdWVfc3BlY2lmaWNhdGlvbiIsInBhdGgiOiJsb3dl
ci5GLm1hdGVyaWFsLnJlY29yZHMuMjIifSx7ImlkIjoidmNuX2E2M2Q0ZjNlZDIzNjA0MjdhN2M5
MGYyMzY3ODE4MTRhYTJhNmE1NjBhNzJlOWQ4MTkxYmM1ZDg1ZjdmZTJhMTIiLCJraW5kIjoidmFy
aWFibGVfY29uc3RyYWludF9kZWNsYXJhdGlvbiIsInBhdGgiOiJsb3dlci5OLmNvbnN0cmFpbnQu
ZGVjbGFyYXRpb24ifSx7ImlkIjoiY3JnX2JlZDIwMTE1MjBmNjYxMmMyNDc2NjNhNDBmZTE3ODY2
ODk1NDA5MzJjNjBmZWIyZjQ3MmY5ZDZjMTk1MjA1OGYiLCJraW5kIjoiY29uc3RyYWludF9yZWdp
c3RyYXRpb24iLCJwYXRoIjoibG93ZXIuTi5jb25zdHJhaW50LnJlZ2lzdHJhdGlvbiJ9LHsiaWQi
OiJ2c21fYWI2Yjg2NDljY2IxMTI0ZWE2MTZkNjY2NzEzZWIzYTQxOGRiZDhiYjM1ODkyNjBlMzY5
ZmYzNjUzZDBkMzdmZSIsImtpbmQiOiJ2YXJpYWJsZV9zZW1hbnRpY19kZWNsYXJhdGlvbiIsInBh
dGgiOiJsb3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkuc2VtYW50aWNzX3Jlc3VsdC5vYnNl
cnZhdGlvbl9yb2xlLmRlY2xhcmF0aW9uIn0seyJpZCI6InZzbV9mN2MwOTU0MjFiMDY5ZTEyMmQy
NjQwYTk3NDQ1MzcyOTA0OTRjYjhmNWUwOWIzYTcwZDY5Yjg4NDM0YzUyN2I4Iiwia2luZCI6InZh
cmlhYmxlX3NlbWFudGljX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLk4uc2VtYW50aWNfY29t
cGF0aWJpbGl0eS5zZW1hbnRpY3NfcmVzdWx0LnF1YW50aXR5X2tpbmQuZGVjbGFyYXRpb24ifSx7
ImlkIjoidnNwXzZlMzhiYjg2YWU4OTdjMGEwMThkZGM5MWU0MTZkYzQzM2QzOWEyN2JkY2ExMWIw
N2VkZDZkZDJhODBmZGU2MmEiLCJraW5kIjoidmFyaWFibGVfdmFsdWVfc3BlY2lmaWNhdGlvbiIs
InBhdGgiOiJsb3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkudmFsdWVfY29tcGF0aWJpbGl0
eS5zcGVjaWZpY2F0aW9uX3Jlc3VsdC5zcGVjaWZpY2F0aW9uIn0seyJpZCI6InJlZ18yN2MzNmU2
NzFlMDE0N2M5ZTIzNWJkYWM5MjQxZWY3MmQ0ZmNkZDM4NDM2ZDM1YjcyN2U2NjEwOWRkNmM3ODE5
Iiwia2luZCI6ImVudGl0eV9yZWdpc3RyYXRpb24iLCJwYXRoIjoibG93ZXIuTi5zZW1hbnRpY19j
b21wYXRpYmlsaXR5LnZhbHVlX2NvbXBhdGliaWxpdHkuc3RhdGUub3duZXJfcmVnaXN0cmF0aW9u
In0seyJpZCI6InZyZ181NDNmODc1NTIwNThkMjJhZjdkMzExNTRmZDBjYWZhMWZjM2RjNDVkOGM4
YjgzYzFmMGNkNjg0ZWM1MDhmMGJkIiwia2luZCI6InZhcmlhYmxlX3JlZ2lzdHJhdGlvbiIsInBh
dGgiOiJsb3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkudmFsdWVfY29tcGF0aWJpbGl0eS5z
dGF0ZS52YXJpYWJsZV9yZWdpc3RyYXRpb24ifV0sInB1YmxpY19yZWNvbnN0cnVjdGlvbiI6eyJC
SCI6eyJjYW5vbmljYWxfcm91bmR0cmlwX2lkZW50aWNhbCI6dHJ1ZSwidHlwZSI6IkJlaGF2aW9y
RXZhbHVhdGlvblJlc3VsdCIsIndpcmVfbm9kZXNfYWZ0ZXIiOjQ5MDksIndpcmVfbm9kZXNfYmVm
b3JlIjo0OTA5fSwiRSI6eyJjYW5vbmljYWxfcm91bmR0cmlwX2lkZW50aWNhbCI6dHJ1ZSwidHlw
ZSI6Ik9wZXJhdGlvbmFsRXZpZGVuY2VTZWxlY3Rpb25SZXN1bHQiLCJ3aXJlX25vZGVzX2FmdGVy
Ijo4MDIsIndpcmVfbm9kZXNfYmVmb3JlIjo4MDJ9LCJGIjp7ImNhbm9uaWNhbF9yb3VuZHRyaXBf
aWRlbnRpY2FsIjp0cnVlLCJ0eXBlIjoiRmxvd09wZXJhdGluZ0NyaXRlcmlvblJlc3VsdCIsIndp
cmVfbm9kZXNfYWZ0ZXIiOjEzMjAsIndpcmVfbm9kZXNfYmVmb3JlIjoxMzIwfSwiTiI6eyJjYW5v
bmljYWxfcm91bmR0cmlwX2lkZW50aWNhbCI6dHJ1ZSwidHlwZSI6IkNvbnN0cmFpbnRFdmFsdWF0
aW9uUmVzdWx0Iiwid2lyZV9ub2Rlc19hZnRlciI6MTk1MSwid2lyZV9ub2Rlc19iZWZvcmUiOjE5
NTF9fSwicmVmZXJlbmNlX29jY3VycmVuY2VzIjoxNiwicmVwbGFjZW1lbnRfY2F0ZWdvcmllcyI6
eyJhc3N1bXB0aW9uX3N0YXRlbWVudF9jb250ZW50IjoyMjIsImNvbXBhdGliaWxpdHlfc3RydWN0
dXJlIjoxMDYsImVwaXN0ZW1pY19jbGFzc2lmaWNhdGlvbnMiOjE3MDQsImh5cG90aGVzaXNfc3Ry
dWN0dXJlIjo5NCwibWVhc3VyZW1lbnRfc3RydWN0dXJlIjoxNzAsIm1vZGVsX3F1ZXJ5X21hdGVy
aWFsX3NoZWxsIjo3NCwibW9kZWxfcmVjb3JkcyI6MjQ2Miwib3RoZXJfY2FycmllZF9sb3dlcl9y
ZXN1bHRzIjo1OTg1LCJvdXRjb21lX3N0cnVjdHVyZSI6NTQsIm91dGVyX2ZpZWxkc19jb21taXRt
ZW50c19saW1pdHNfc2NvcGVfcG9saWN5IjoxNTEsInByb3ZlbmFuY2UiOjg3OCwicHVibGljX2V2
aWRlbmNlX2NpdGF0aW9ucyI6NDY3fSwicmVwbGFjZW1lbnRfZXhwYW5kZWRfbm9kZXMiOjEyMzY3
LCJyZXBsYWNlbWVudF9ub2RlX2tpbmRzIjp7ImFycmF5Ijo3MDUsImtleSI6NTY1OCwib2JqZWN0
IjoxMjc0LCJzY2FsYXIiOjQ3MzB9LCJyb290X25vZGUiOjEsInNoYTI1NiI6ImJhY2UyZTRiZWM1
MTNlOTIwYjhhZmRkMTFkNTU2Mjk3MWNiMjEzZTdkZWMyZWEwODg3OGIxMzZiNzExOTJhOWIiLCJz
bG90cyI6W3siYm9keV9ub2RlcyI6NjcsImJvZHlfc2hhMjU2IjoiNjAyNGQ5ZmE5M2IyMWFhNGE3
YmMzYmVlZWYyN2RmN2RlMzdlYWU4MzEwMjgxNDZhMmRkZDE4Y2Y2OGM4ZjRiNiIsInBhdGgiOiJt
ZWFzdXJlbWVudHMuMC5hcHBsaWNhYmlsaXR5LnN0YXRlbWVudCIsInN0YXRlbWVudCI6IlQxX00i
LCJ3aXJlX25vZGVzIjozfSx7ImJvZHlfbm9kZXMiOjY3LCJib2R5X3NoYTI1NiI6IjYwMjRkOWZh
OTNiMjFhYTRhN2JjM2JlZWVmMjdkZjdkZTM3ZWFlODMxMDI4MTQ2YTJkZGQxOGNmNjhjOGY0YjYi
LCJwYXRoIjoibWVhc3VyZW1lbnRzLjAuYXZhaWxhYmlsaXR5LnN0YXRlbWVudCIsInN0YXRlbWVu
dCI6IlQxX00iLCJ3aXJlX25vZGVzIjozfSx7ImJvZHlfbm9kZXMiOjY3LCJib2R5X3NoYTI1NiI6
IjYwMjRkOWZhOTNiMjFhYTRhN2JjM2JlZWVmMjdkZjdkZTM3ZWFlODMxMDI4MTQ2YTJkZGQxOGNm
NjhjOGY0YjYiLCJwYXRoIjoibWVhc3VyZW1lbnRzLjAuY2FsaWJyYXRpb24uc3RhdGVtZW50Iiwi
c3RhdGVtZW50IjoiVDFfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9keV9ub2RlcyI6NjcsImJvZHlf
c2hhMjU2IjoiNjAyNGQ5ZmE5M2IyMWFhNGE3YmMzYmVlZWYyN2RmN2RlMzdlYWU4MzEwMjgxNDZh
MmRkZDE4Y2Y2OGM4ZjRiNiIsInBhdGgiOiJtZWFzdXJlbWVudHMuMC5ob2xkLnN0YXRlbWVudCIs
InN0YXRlbWVudCI6IlQxX00iLCJ3aXJlX25vZGVzIjozfSx7ImJvZHlfbm9kZXMiOjY3LCJib2R5
X3NoYTI1NiI6IjYwMjRkOWZhOTNiMjFhYTRhN2JjM2JlZWVmMjdkZjdkZTM3ZWFlODMxMDI4MTQ2
YTJkZGQxOGNmNjhjOGY0YjYiLCJwYXRoIjoibWVhc3VyZW1lbnRzLjAub3V0Y29tZXMuMC5zdGF0
ZW1lbnQiLCJzdGF0ZW1lbnQiOiJUMV9NIiwid2lyZV9ub2RlcyI6M30seyJib2R5X25vZGVzIjo2
NywiYm9keV9zaGEyNTYiOiI2MDI0ZDlmYTkzYjIxYWE0YTdiYzNiZWVlZjI3ZGY3ZGUzN2VhZTgz
MTAyODE0NmEyZGRkMThjZjY4YzhmNGI2IiwicGF0aCI6Im1lYXN1cmVtZW50cy4wLm91dGNvbWVz
LjEuc3RhdGVtZW50Iiwic3RhdGVtZW50IjoiVDFfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9keV9u
b2RlcyI6NjcsImJvZHlfc2hhMjU2IjoiNjAyNGQ5ZmE5M2IyMWFhNGE3YmMzYmVlZWYyN2RmN2Rl
MzdlYWU4MzEwMjgxNDZhMmRkZDE4Y2Y2OGM4ZjRiNiIsInBhdGgiOiJtZWFzdXJlbWVudHMuMC5w
cm9jZWR1cmUuc3RhdGVtZW50Iiwic3RhdGVtZW50IjoiVDFfTSIsIndpcmVfbm9kZXMiOjN9LHsi
Ym9keV9ub2RlcyI6NjcsImJvZHlfc2hhMjU2IjoiNjAyNGQ5ZmE5M2IyMWFhNGE3YmMzYmVlZWYy
N2RmN2RlMzdlYWU4MzEwMjgxNDZhMmRkZDE4Y2Y2OGM4ZjRiNiIsInBhdGgiOiJtZWFzdXJlbWVu
dHMuMC5zZW1hbnRpY19kaXN0aW5jdG5lc3MiLCJzdGF0ZW1lbnQiOiJUMV9NIiwid2lyZV9ub2Rl
cyI6M30seyJib2R5X25vZGVzIjo2NywiYm9keV9zaGEyNTYiOiJhN2Q4ZTY4ZDI4OTE4MzBlYTk1
ZjgwN2IwMjBlMWExYThmMmUyOTI2Yjk1ZmUyOGI4MjRhOTQ3ZDE3ZGFmOTdkIiwicGF0aCI6Im1l
YXN1cmVtZW50cy4xLmFwcGxpY2FiaWxpdHkuc3RhdGVtZW50Iiwic3RhdGVtZW50IjoiVDJfTSIs
IndpcmVfbm9kZXMiOjN9LHsiYm9keV9ub2RlcyI6NjcsImJvZHlfc2hhMjU2IjoiYTdkOGU2OGQy
ODkxODMwZWE5NWY4MDdiMDIwZTFhMWE4ZjJlMjkyNmI5NWZlMjhiODI0YTk0N2QxN2RhZjk3ZCIs
InBhdGgiOiJtZWFzdXJlbWVudHMuMS5hdmFpbGFiaWxpdHkuc3RhdGVtZW50Iiwic3RhdGVtZW50
IjoiVDJfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9keV9ub2RlcyI6NjcsImJvZHlfc2hhMjU2Ijoi
YTdkOGU2OGQyODkxODMwZWE5NWY4MDdiMDIwZTFhMWE4ZjJlMjkyNmI5NWZlMjhiODI0YTk0N2Qx
N2RhZjk3ZCIsInBhdGgiOiJtZWFzdXJlbWVudHMuMS5jYWxpYnJhdGlvbi5zdGF0ZW1lbnQiLCJz
dGF0ZW1lbnQiOiJUMl9NIiwid2lyZV9ub2RlcyI6M30seyJib2R5X25vZGVzIjo2NywiYm9keV9z
aGEyNTYiOiJhN2Q4ZTY4ZDI4OTE4MzBlYTk1ZjgwN2IwMjBlMWExYThmMmUyOTI2Yjk1ZmUyOGI4
MjRhOTQ3ZDE3ZGFmOTdkIiwicGF0aCI6Im1lYXN1cmVtZW50cy4xLmhvbGQuc3RhdGVtZW50Iiwi
c3RhdGVtZW50IjoiVDJfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9keV9ub2RlcyI6NjcsImJvZHlf
c2hhMjU2IjoiYTdkOGU2OGQyODkxODMwZWE5NWY4MDdiMDIwZTFhMWE4ZjJlMjkyNmI5NWZlMjhi
ODI0YTk0N2QxN2RhZjk3ZCIsInBhdGgiOiJtZWFzdXJlbWVudHMuMS5vdXRjb21lcy4wLnN0YXRl
bWVudCIsInN0YXRlbWVudCI6IlQyX00iLCJ3aXJlX25vZGVzIjozfSx7ImJvZHlfbm9kZXMiOjY3
LCJib2R5X3NoYTI1NiI6ImE3ZDhlNjhkMjg5MTgzMGVhOTVmODA3YjAyMGUxYTFhOGYyZTI5MjZi
OTVmZTI4YjgyNGE5NDdkMTdkYWY5N2QiLCJwYXRoIjoibWVhc3VyZW1lbnRzLjEub3V0Y29tZXMu
MS5zdGF0ZW1lbnQiLCJzdGF0ZW1lbnQiOiJUMl9NIiwid2lyZV9ub2RlcyI6M30seyJib2R5X25v
ZGVzIjo2NywiYm9keV9zaGEyNTYiOiJhN2Q4ZTY4ZDI4OTE4MzBlYTk1ZjgwN2IwMjBlMWExYThm
MmUyOTI2Yjk1ZmUyOGI4MjRhOTQ3ZDE3ZGFmOTdkIiwicGF0aCI6Im1lYXN1cmVtZW50cy4xLnBy
b2NlZHVyZS5zdGF0ZW1lbnQiLCJzdGF0ZW1lbnQiOiJUMl9NIiwid2lyZV9ub2RlcyI6M30seyJi
b2R5X25vZGVzIjo2NywiYm9keV9zaGEyNTYiOiJhN2Q4ZTY4ZDI4OTE4MzBlYTk1ZjgwN2IwMjBl
MWExYThmMmUyOTI2Yjk1ZmUyOGI4MjRhOTQ3ZDE3ZGFmOTdkIiwicGF0aCI6Im1lYXN1cmVtZW50
cy4xLnNlbWFudGljX2Rpc3RpbmN0bmVzcyIsInN0YXRlbWVudCI6IlQyX00iLCJ3aXJlX25vZGVz
IjozfV0sInRvcF9maWVsZHMiOnsiYWxnb3JpdGhtIjoyLCJjb21wYXRpYmlsaXR5Ijo3NzgsImh5
cG90aGVzZXMiOjYzOCwianVzdGlmaWNhdGlvbnMiOjEzNiwibGltaXRzIjo0MiwibG93ZXIiOjg5
ODgsImxvd2VyX2NvbW1pdG1lbnRzIjo3OCwibWVhc3VyZW1lbnRzIjo1ODQsIm1vZGUiOjIsInBv
bGljeSI6MTIsInNjaGVtYSI6Miwic2NvcGUiOjgwfSwid2lyZV9jYXRlZ29yaWVzIjp7ImFzc3Vt
cHRpb25fc3RhdGVtZW50X2NvbnRlbnQiOjEyNiwiY29tcGF0aWJpbGl0eV9zdHJ1Y3R1cmUiOjEw
NiwiZXBpc3RlbWljX2NsYXNzaWZpY2F0aW9ucyI6MTA2NCwiaHlwb3RoZXNpc19zdHJ1Y3R1cmUi
Ojk0LCJtZWFzdXJlbWVudF9zdHJ1Y3R1cmUiOjIxOCwibW9kZWxfcXVlcnlfbWF0ZXJpYWxfc2hl
bGwiOjc0LCJtb2RlbF9yZWNvcmRzIjoyNDYyLCJvdGhlcl9jYXJyaWVkX2xvd2VyX3Jlc3VsdHMi
OjU5ODUsIm91dGNvbWVfc3RydWN0dXJlIjo3MCwib3V0ZXJfZmllbGRzX2NvbW1pdG1lbnRzX2xp
bWl0c19zY29wZV9wb2xpY3kiOjE1MSwicHJvdmVuYW5jZSI6NTI2LCJwdWJsaWNfZXZpZGVuY2Vf
Y2l0YXRpb25zIjo0Njd9LCJ3aXJlX25vZGVfa2luZHMiOnsiYXJyYXkiOjYwOSwia2V5Ijo1MTk0
LCJvYmplY3QiOjExNzgsInNjYWxhciI6NDM2Mn0sIndpcmVfbm9kZXMiOjExMzQzfSwicHJpbWFy
eSI6eyJhZGRpdGl2ZWx5X2NoYXJnZWRfbm9kZXMiOjcxMzAsImFzc3VtcHRpb25fcHJvamVjdGlv
bl9ieXRlcyI6MjkxNTMsImFzc3VtcHRpb25fcHJvamVjdGlvbl9zaGEyNTYiOiI0YzVlNDg0NTJl
ZTgxYTVjNjVjZWYyYTUxZGNhZThkZTU2MjYyNjg0ZTcwNTZiZTQyOWRkNjE2Njc4ODI0MWRjIiwi
Ynl0ZXMiOjk0ODE5LCJmdWxsX21lbWJlcnNoaXBzIjpbeyJtZW1iZXJzIjoxNywibm9kZXMiOjI2
LCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZXZpc2lvbiIsInNoYTI1NiI6ImYwZjMzZjVkYzMy
MDI3ZmY0ZWQ0MjRkYTY2MDZhZmFkMzI1NWJiYzdlYTZhMDkzNjRiODkzMDc5ODNiZTJlMjYifSx7
Im1lbWJlcnMiOjE3LCJub2RlcyI6MjYsInBhdGgiOiJsb3dlci5OLmNvbnN0cmFpbnQucmV2aXNp
b24iLCJzaGEyNTYiOiJmMGYzM2Y1ZGMzMjAyN2ZmNGVkNDI0ZGE2NjA2YWZhZDMyNTViYmM3ZWE2
YTA5MzY0Yjg5MzA3OTgzYmUyZTI2In0seyJtZW1iZXJzIjozLCJub2RlcyI6MTIsInBhdGgiOiJs
b3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkuY2FuZGlkYXRlcy4wLmludGVycHJldGF0aW9u
LnJldmlzaW9uIiwic2hhMjU2IjoiMjExOTQyOTllMmM4YThhNDhkODA4OGRhY2JmZTI0ODkwOWFk
YmMyOTVhNTY5MDk1MmQxOGVlYWE3NmIyZTI1MSJ9LHsibWVtYmVycyI6Mywibm9kZXMiOjEyLCJw
YXRoIjoibG93ZXIuTi5zZW1hbnRpY19jb21wYXRpYmlsaXR5LmNhbmRpZGF0ZXMuMC52YWx1ZV9j
YW5kaWRhdGUuc3RhdGVfY2FuZGlkYXRlLmJvdW5kLnJlc29sdXRpb24ucmV2aXNpb24iLCJzaGEy
NTYiOiIwZGQwZjhkMWFhMTc1NmZmNzBiZGNlMGFiZjJiYWE1ZDI5YTY3MzgzMjViYTI3MDUzNjY3
MmQxOGUyODg4ODBkIn0seyJtZW1iZXJzIjozLCJub2RlcyI6MTIsInBhdGgiOiJsb3dlci5OLnNl
bWFudGljX2NvbXBhdGliaWxpdHkuaW50ZXJwcmV0YXRpb25fcmV2aXNpb24iLCJzaGEyNTYiOiIy
MTE5NDI5OWUyYzhhOGE0OGQ4MDg4ZGFjYmZlMjQ4OTA5YWRiYzI5NWE1NjkwOTUyZDE4ZWVhYTc2
YjJlMjUxIn0seyJtZW1iZXJzIjoxNywibm9kZXMiOjI2LCJwYXRoIjoibG93ZXIuTi5zZW1hbnRp
Y19jb21wYXRpYmlsaXR5LnNlbWFudGljc19yZXN1bHQucmV2aXNpb24iLCJzaGEyNTYiOiJmMGYz
M2Y1ZGMzMjAyN2ZmNGVkNDI0ZGE2NjA2YWZhZDMyNTViYmM3ZWE2YTA5MzY0Yjg5MzA3OTgzYmUy
ZTI2In0seyJtZW1iZXJzIjozLCJub2RlcyI6MTIsInBhdGgiOiJsb3dlci5OLnNlbWFudGljX2Nv
bXBhdGliaWxpdHkudmFsdWVfY29tcGF0aWJpbGl0eS5jYW5kaWRhdGVzLjAuc3RhdGVfY2FuZGlk
YXRlLmJvdW5kLnJlc29sdXRpb24ucmV2aXNpb24iLCJzaGEyNTYiOiIwZGQwZjhkMWFhMTc1NmZm
NzBiZGNlMGFiZjJiYWE1ZDI5YTY3MzgzMjViYTI3MDUzNjY3MmQxOGUyODg4ODBkIn0seyJtZW1i
ZXJzIjoxNywibm9kZXMiOjI2LCJwYXRoIjoibG93ZXIuTi5zZW1hbnRpY19jb21wYXRpYmlsaXR5
LnZhbHVlX2NvbXBhdGliaWxpdHkuc3BlY2lmaWNhdGlvbl9yZXN1bHQucmV2aXNpb24iLCJzaGEy
NTYiOiJmMGYzM2Y1ZGMzMjAyN2ZmNGVkNDI0ZGE2NjA2YWZhZDMyNTViYmM3ZWE2YTA5MzY0Yjg5
MzA3OTgzYmUyZTI2In0seyJtZW1iZXJzIjozLCJub2RlcyI6MTIsInBhdGgiOiJsb3dlci5OLnNl
bWFudGljX2NvbXBhdGliaWxpdHkudmFsdWVfY29tcGF0aWJpbGl0eS5zdGF0ZS5iaW5kaW5nX3Jl
dmlzaW9uIiwic2hhMjU2IjoiMGRkMGY4ZDFhYTE3NTZmZjcwYmRjZTBhYmYyYmFhNWQyOWE2NzM4
MzI1YmEyNzA1MzY2NzJkMThlMjg4ODgwZCJ9LHsibWVtYmVycyI6Mywibm9kZXMiOjEyLCJwYXRo
IjoibG93ZXIuTi5zZW1hbnRpY19jb21wYXRpYmlsaXR5LnZhbHVlX2NvbXBhdGliaWxpdHkuc3Rh
dGUuY2FuZGlkYXRlcy4wLmJvdW5kLnJlc29sdXRpb24ucmV2aXNpb24iLCJzaGEyNTYiOiIwZGQw
ZjhkMWFhMTc1NmZmNzBiZGNlMGFiZjJiYWE1ZDI5YTY3MzgzMjViYTI3MDUzNjY3MmQxOGUyODg4
ODBkIn0seyJtZW1iZXJzIjoxNywibm9kZXMiOjI2LCJwYXRoIjoibG93ZXIuTi5zZW1hbnRpY19j
b21wYXRpYmlsaXR5LnZhbHVlX2NvbXBhdGliaWxpdHkuc3RhdGUubW9kZWxfcmV2aXNpb24iLCJz
aGEyNTYiOiJmMGYzM2Y1ZGMzMjAyN2ZmNGVkNDI0ZGE2NjA2YWZhZDMyNTViYmM3ZWE2YTA5MzY0
Yjg5MzA3OTgzYmUyZTI2In0seyJtZW1iZXJzIjozLCJub2RlcyI6MTIsInBhdGgiOiJsb3dlcl9j
b21taXRtZW50cy5iaW5kaW5nX3JldmlzaW9uIiwic2hhMjU2IjoiMGRkMGY4ZDFhYTE3NTZmZjcw
YmRjZTBhYmYyYmFhNWQyOWE2NzM4MzI1YmEyNzA1MzY2NzJkMThlMjg4ODgwZCJ9LHsibWVtYmVy
cyI6Mywibm9kZXMiOjEyLCJwYXRoIjoibG93ZXJfY29tbWl0bWVudHMuaW50ZXJwcmV0YXRpb25f
cmV2aXNpb24iLCJzaGEyNTYiOiIyMTE5NDI5OWUyYzhhOGE0OGQ4MDg4ZGFjYmZlMjQ4OTA5YWRi
YzI5NWE1NjkwOTUyZDE4ZWVhYTc2YjJlMjUxIn0seyJtZW1iZXJzIjoxNywibm9kZXMiOjI2LCJw
YXRoIjoibG93ZXJfY29tbWl0bWVudHMubW9kZWxfcmV2aXNpb24iLCJzaGEyNTYiOiJmMGYzM2Y1
ZGMzMjAyN2ZmNGVkNDI0ZGE2NjA2YWZhZDMyNTViYmM3ZWE2YTA5MzY0Yjg5MzA3OTgzYmUyZTI2
In1dLCJpbmRlcGVuZGVudF9vcmFjbGVfYWdyZWVzIjp0cnVlLCJsb3dlcl9yb290cyI6eyJFIjo4
MDIsIkYiOjk5NCwiTiI6MTkxM30sIm1hdGVyaWFscyI6W3siYnl0ZXMiOjE0MTI5LCJub2RlcyI6
Nzk0LCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbCIsInJlY29yZHMiOjE3LCJzaGEyNTYiOiIyMTNk
MjkyOWI1Y2YyMTNiNWZiOGFjMzhlZjIxNThiOWFlMmRiZjAwYjgxZmU2MTJhMTllMDU5NzcyODU2
MTNiIn1dLCJtb2RlbF9yZWNvcmRfb2NjdXJyZW5jZXMiOlt7ImlkIjoiY3JnX2JlZDIwMTE1MjBm
NjYxMmMyNDc2NjNhNDBmZTE3ODY2ODk1NDA5MzJjNjBmZWIyZjQ3MmY5ZDZjMTk1MjA1OGYiLCJr
aW5kIjoiY29uc3RyYWludF9yZWdpc3RyYXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5y
ZWNvcmRzLjAifSx7ImlkIjoiZmNkXzk3MTgyMGQzZTQwYWVlNDBlMjlkMjA3Njg2M2M5ZTk1YjE5
Y2M5YTNmM2RkZTJlYzIzZTZhMjMxYTkyMDgwNjkiLCJraW5kIjoiZmxvd19vcGVyYXRpbmdfY3Jp
dGVyaW9uX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJpYWwucmVjb3Jkcy4xIn0s
eyJpZCI6ImZsZF84OGJjZjU2ZmZmMDMxMGI1MjRhN2YzZGViZTk0NWI1YmQwMTM4OTQyNjk3YmQw
YWMyNTIyOGJjNDk0ZTg5MDVmIiwia2luZCI6ImZsb3dfZGVjbGFyYXRpb24iLCJwYXRoIjoibG93
ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjIifSx7ImlkIjoiZm1hX2YyODYwMzRlZmQ1NjRiMWNjMTVi
ODJmNjFlMjJkODQ1MmZlNjllNzFiM2RlZjJkMDBhMTNkMmIxNGQzM2RiZGUiLCJraW5kIjoiZmxv
d19tZWFzdXJlbWVudF9hc3NvY2lhdGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29y
ZHMuMyJ9LHsiaWQiOiJmcmdfNDJkNzk5NGExOWQ2MjQ2OTI3ZjI0NTM4NTk4ZWE4ZTE2YmQ2YTY1
YWU4N2E0OTNlNjNkYTY5NjdhMDcwY2NhMCIsImtpbmQiOiJmbG93X3JlZ2lzdHJhdGlvbiIsInBh
dGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuNCJ9LHsiaWQiOiJwY25fN2Q3MTc3YWJmYWZh
ODVmZTE3MjQ4YmJiNWRlNTkyYTU5Mzc4OWY2NjQwZTBkODFkYzc2MDA5ZDQwNjczZTllOSIsImtp
bmQiOiJwb3J0X2Nvbm5lY3Rpb25fYXNzZXJ0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJpYWwu
cmVjb3Jkcy41In0seyJpZCI6InBpZl8wZDI2MmY0NzkzNzMyYmUyNDUyOTYwYTc4MGYyNTMyNjRi
NjgxNTAwYWQ4NDUwZDA1ZTVlMzVmZmY4NzdiYjcyIiwia2luZCI6InBvcnRfaW50ZXJmYWNlX2Rl
Y2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJpYWwucmVjb3Jkcy42In0seyJpZCI6InBp
Zl9kOGE0MmYyNWNlOTMxYjA0YzRjMjAwNDgyZjEyYjhhMjYxNTMyZDhiMDU2ZTU3NTViZmE1NDRj
ZDYzMGQxZTZkIiwia2luZCI6InBvcnRfaW50ZXJmYWNlX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxv
d2VyLkYubWF0ZXJpYWwucmVjb3Jkcy43In0seyJpZCI6InByZ18xNzJiMGNmMjEwMzYzNzg3ZTRi
MGUwZWNhN2RiNWU3NTM0YTQwZWY2Mzg3NDZmZjM0MGIzMDkwNjI1MjJlYTg5Iiwia2luZCI6InBv
cnRfcmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJpYWwucmVjb3Jkcy44In0seyJp
ZCI6InByZ18zNzU5NDA2ZDkwMjU5YTU4ZmRiMjRmNjZkZWRlYWYzNjZlYTdiYjNmZDRjNDM4OGI2
YWY1YTVjZTAwMGQ5MjExIiwia2luZCI6InBvcnRfcmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2Vy
LkYubWF0ZXJpYWwucmVjb3Jkcy45In0seyJpZCI6InJlZ18yN2MzNmU2NzFlMDE0N2M5ZTIzNWJk
YWM5MjQxZWY3MmQ0ZmNkZDM4NDM2ZDM1YjcyN2U2NjEwOWRkNmM3ODE5Iiwia2luZCI6ImVudGl0
eV9yZWdpc3RyYXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjEwIn0seyJp
ZCI6InZjbl9hNjNkNGYzZWQyMzYwNDI3YTdjOTBmMjM2NzgxODE0YWEyYTZhNTYwYTcyZTlkODE5
MWJjNWQ4NWY3ZmUyYTEyIiwia2luZCI6InZhcmlhYmxlX2NvbnN0cmFpbnRfZGVjbGFyYXRpb24i
LCJwYXRoIjoibG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjExIn0seyJpZCI6InZwYV9lMDUwMTA0
ZGQ4YWQ2YzEwZjE4NGRhNjdlNGI0N2ViZGUyYmJiMDA4MDlkOGZkMDAzNzQxZmZjMWJjNzkyNjI3
Iiwia2luZCI6InZhcmlhYmxlX3BvcnRfYXNzb2NpYXRpb24iLCJwYXRoIjoibG93ZXIuRi5tYXRl
cmlhbC5yZWNvcmRzLjEyIn0seyJpZCI6InZyZ181NDNmODc1NTIwNThkMjJhZjdkMzExNTRmZDBj
YWZhMWZjM2RjNDVkOGM4YjgzYzFmMGNkNjg0ZWM1MDhmMGJkIiwia2luZCI6InZhcmlhYmxlX3Jl
Z2lzdHJhdGlvbiIsInBhdGgiOiJsb3dlci5GLm1hdGVyaWFsLnJlY29yZHMuMTMifSx7ImlkIjoi
dnNtX2FiNmI4NjQ5Y2NiMTEyNGVhNjE2ZDY2NjcxM2ViM2E0MThkYmQ4YmIzNTg5MjYwZTM2OWZm
MzY1M2QwZDM3ZmUiLCJraW5kIjoidmFyaWFibGVfc2VtYW50aWNfZGVjbGFyYXRpb24iLCJwYXRo
IjoibG93ZXIuRi5tYXRlcmlhbC5yZWNvcmRzLjE0In0seyJpZCI6InZzbV9mN2MwOTU0MjFiMDY5
ZTEyMmQyNjQwYTk3NDQ1MzcyOTA0OTRjYjhmNWUwOWIzYTcwZDY5Yjg4NDM0YzUyN2I4Iiwia2lu
ZCI6InZhcmlhYmxlX3NlbWFudGljX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJp
YWwucmVjb3Jkcy4xNSJ9LHsiaWQiOiJ2c3BfNmUzOGJiODZhZTg5N2MwYTAxOGRkYzkxZTQxNmRj
NDMzZDM5YTI3YmRjYTExYjA3ZWRkNmRkMmE4MGZkZTYyYSIsImtpbmQiOiJ2YXJpYWJsZV92YWx1
ZV9zcGVjaWZpY2F0aW9uIiwicGF0aCI6Imxvd2VyLkYubWF0ZXJpYWwucmVjb3Jkcy4xNiJ9LHsi
aWQiOiJ2Y25fYTYzZDRmM2VkMjM2MDQyN2E3YzkwZjIzNjc4MTgxNGFhMmE2YTU2MGE3MmU5ZDgx
OTFiYzVkODVmN2ZlMmExMiIsImtpbmQiOiJ2YXJpYWJsZV9jb25zdHJhaW50X2RlY2xhcmF0aW9u
IiwicGF0aCI6Imxvd2VyLk4uY29uc3RyYWludC5kZWNsYXJhdGlvbiJ9LHsiaWQiOiJjcmdfYmVk
MjAxMTUyMGY2NjEyYzI0NzY2M2E0MGZlMTc4NjY4OTU0MDkzMmM2MGZlYjJmNDcyZjlkNmMxOTUy
MDU4ZiIsImtpbmQiOiJjb25zdHJhaW50X3JlZ2lzdHJhdGlvbiIsInBhdGgiOiJsb3dlci5OLmNv
bnN0cmFpbnQucmVnaXN0cmF0aW9uIn0seyJpZCI6InZzbV9hYjZiODY0OWNjYjExMjRlYTYxNmQ2
NjY3MTNlYjNhNDE4ZGJkOGJiMzU4OTI2MGUzNjlmZjM2NTNkMGQzN2ZlIiwia2luZCI6InZhcmlh
YmxlX3NlbWFudGljX2RlY2xhcmF0aW9uIiwicGF0aCI6Imxvd2VyLk4uc2VtYW50aWNfY29tcGF0
aWJpbGl0eS5zZW1hbnRpY3NfcmVzdWx0Lm9ic2VydmF0aW9uX3JvbGUuZGVjbGFyYXRpb24ifSx7
ImlkIjoidnNtX2Y3YzA5NTQyMWIwNjllMTIyZDI2NDBhOTc0NDUzNzI5MDQ5NGNiOGY1ZTA5YjNh
NzBkNjliODg0MzRjNTI3YjgiLCJraW5kIjoidmFyaWFibGVfc2VtYW50aWNfZGVjbGFyYXRpb24i
LCJwYXRoIjoibG93ZXIuTi5zZW1hbnRpY19jb21wYXRpYmlsaXR5LnNlbWFudGljc19yZXN1bHQu
cXVhbnRpdHlfa2luZC5kZWNsYXJhdGlvbiJ9LHsiaWQiOiJ2c3BfNmUzOGJiODZhZTg5N2MwYTAx
OGRkYzkxZTQxNmRjNDMzZDM5YTI3YmRjYTExYjA3ZWRkNmRkMmE4MGZkZTYyYSIsImtpbmQiOiJ2
YXJpYWJsZV92YWx1ZV9zcGVjaWZpY2F0aW9uIiwicGF0aCI6Imxvd2VyLk4uc2VtYW50aWNfY29t
cGF0aWJpbGl0eS52YWx1ZV9jb21wYXRpYmlsaXR5LnNwZWNpZmljYXRpb25fcmVzdWx0LnNwZWNp
ZmljYXRpb24ifSx7ImlkIjoicmVnXzI3YzM2ZTY3MWUwMTQ3YzllMjM1YmRhYzkyNDFlZjcyZDRm
Y2RkMzg0MzZkMzViNzI3ZTY2MTA5ZGQ2Yzc4MTkiLCJraW5kIjoiZW50aXR5X3JlZ2lzdHJhdGlv
biIsInBhdGgiOiJsb3dlci5OLnNlbWFudGljX2NvbXBhdGliaWxpdHkudmFsdWVfY29tcGF0aWJp
bGl0eS5zdGF0ZS5vd25lcl9yZWdpc3RyYXRpb24ifSx7ImlkIjoidnJnXzU0M2Y4NzU1MjA1OGQy
MmFmN2QzMTE1NGZkMGNhZmExZmMzZGM0NWQ4YzhiODNjMWYwY2Q2ODRlYzUwOGYwYmQiLCJraW5k
IjoidmFyaWFibGVfcmVnaXN0cmF0aW9uIiwicGF0aCI6Imxvd2VyLk4uc2VtYW50aWNfY29tcGF0
aWJpbGl0eS52YWx1ZV9jb21wYXRpYmlsaXR5LnN0YXRlLnZhcmlhYmxlX3JlZ2lzdHJhdGlvbiJ9
XSwicHVibGljX3JlY29uc3RydWN0aW9uIjp7IkUiOnsiY2Fub25pY2FsX3JvdW5kdHJpcF9pZGVu
dGljYWwiOnRydWUsInR5cGUiOiJPcGVyYXRpb25hbEV2aWRlbmNlU2VsZWN0aW9uUmVzdWx0Iiwi
d2lyZV9ub2Rlc19hZnRlciI6ODAyLCJ3aXJlX25vZGVzX2JlZm9yZSI6ODAyfSwiRiI6eyJjYW5v
bmljYWxfcm91bmR0cmlwX2lkZW50aWNhbCI6dHJ1ZSwidHlwZSI6IkZsb3dPcGVyYXRpbmdDcml0
ZXJpb25SZXN1bHQiLCJ3aXJlX25vZGVzX2FmdGVyIjo5OTQsIndpcmVfbm9kZXNfYmVmb3JlIjo5
OTR9LCJOIjp7ImNhbm9uaWNhbF9yb3VuZHRyaXBfaWRlbnRpY2FsIjp0cnVlLCJ0eXBlIjoiQ29u
c3RyYWludEV2YWx1YXRpb25SZXN1bHQiLCJ3aXJlX25vZGVzX2FmdGVyIjoxOTEzLCJ3aXJlX25v
ZGVzX2JlZm9yZSI6MTkxM319LCJyZWZlcmVuY2Vfb2NjdXJyZW5jZXMiOjE2LCJyZXBsYWNlbWVu
dF9jYXRlZ29yaWVzIjp7ImFzc3VtcHRpb25fc3RhdGVtZW50X2NvbnRlbnQiOjIyMiwiY29tcGF0
aWJpbGl0eV9zdHJ1Y3R1cmUiOjEwNiwiZXBpc3RlbWljX2NsYXNzaWZpY2F0aW9ucyI6MTcwNCwi
aHlwb3RoZXNpc19zdHJ1Y3R1cmUiOjk0LCJtZWFzdXJlbWVudF9zdHJ1Y3R1cmUiOjE3MCwibW9k
ZWxfcXVlcnlfbWF0ZXJpYWxfc2hlbGwiOjMxLCJtb2RlbF9yZWNvcmRzIjo4ODcsIm90aGVyX2Nh
cnJpZWRfbG93ZXJfcmVzdWx0cyI6MjYxNiwib3V0Y29tZV9zdHJ1Y3R1cmUiOjU0LCJvdXRlcl9m
aWVsZHNfY29tbWl0bWVudHNfbGltaXRzX3Njb3BlX3BvbGljeSI6MTQwLCJwcm92ZW5hbmNlIjo4
NzgsInB1YmxpY19ldmlkZW5jZV9jaXRhdGlvbnMiOjE4MH0sInJlcGxhY2VtZW50X2V4cGFuZGVk
X25vZGVzIjo3MDgyLCJyZXBsYWNlbWVudF9ub2RlX2tpbmRzIjp7ImFycmF5Ijo0NjgsImtleSI6
MzIzNCwib2JqZWN0Ijo3MTQsInNjYWxhciI6MjY2Nn0sInJvb3Rfbm9kZSI6MSwic2hhMjU2Ijoi
NjdmZTVkMTY0MjUxZmRjNmQ4YmE1NzdlOTA2NjBiMGM0ODZlYTYyNmFmMGExZmFjY2FjNTM2MjQ4
MWYxODhjMSIsInNsb3RzIjpbeyJib2R5X25vZGVzIjo2NywiYm9keV9zaGEyNTYiOiI2MDI0ZDlm
YTkzYjIxYWE0YTdiYzNiZWVlZjI3ZGY3ZGUzN2VhZTgzMTAyODE0NmEyZGRkMThjZjY4YzhmNGI2
IiwicGF0aCI6Im1lYXN1cmVtZW50cy4wLmFwcGxpY2FiaWxpdHkuc3RhdGVtZW50Iiwic3RhdGVt
ZW50IjoiVDFfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9keV9ub2RlcyI6NjcsImJvZHlfc2hhMjU2
IjoiNjAyNGQ5ZmE5M2IyMWFhNGE3YmMzYmVlZWYyN2RmN2RlMzdlYWU4MzEwMjgxNDZhMmRkZDE4
Y2Y2OGM4ZjRiNiIsInBhdGgiOiJtZWFzdXJlbWVudHMuMC5hdmFpbGFiaWxpdHkuc3RhdGVtZW50
Iiwic3RhdGVtZW50IjoiVDFfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9keV9ub2RlcyI6NjcsImJv
ZHlfc2hhMjU2IjoiNjAyNGQ5ZmE5M2IyMWFhNGE3YmMzYmVlZWYyN2RmN2RlMzdlYWU4MzEwMjgx
NDZhMmRkZDE4Y2Y2OGM4ZjRiNiIsInBhdGgiOiJtZWFzdXJlbWVudHMuMC5jYWxpYnJhdGlvbi5z
dGF0ZW1lbnQiLCJzdGF0ZW1lbnQiOiJUMV9NIiwid2lyZV9ub2RlcyI6M30seyJib2R5X25vZGVz
Ijo2NywiYm9keV9zaGEyNTYiOiI2MDI0ZDlmYTkzYjIxYWE0YTdiYzNiZWVlZjI3ZGY3ZGUzN2Vh
ZTgzMTAyODE0NmEyZGRkMThjZjY4YzhmNGI2IiwicGF0aCI6Im1lYXN1cmVtZW50cy4wLmhvbGQu
c3RhdGVtZW50Iiwic3RhdGVtZW50IjoiVDFfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9keV9ub2Rl
cyI6NjcsImJvZHlfc2hhMjU2IjoiNjAyNGQ5ZmE5M2IyMWFhNGE3YmMzYmVlZWYyN2RmN2RlMzdl
YWU4MzEwMjgxNDZhMmRkZDE4Y2Y2OGM4ZjRiNiIsInBhdGgiOiJtZWFzdXJlbWVudHMuMC5vdXRj
b21lcy4wLnN0YXRlbWVudCIsInN0YXRlbWVudCI6IlQxX00iLCJ3aXJlX25vZGVzIjozfSx7ImJv
ZHlfbm9kZXMiOjY3LCJib2R5X3NoYTI1NiI6IjYwMjRkOWZhOTNiMjFhYTRhN2JjM2JlZWVmMjdk
ZjdkZTM3ZWFlODMxMDI4MTQ2YTJkZGQxOGNmNjhjOGY0YjYiLCJwYXRoIjoibWVhc3VyZW1lbnRz
LjAub3V0Y29tZXMuMS5zdGF0ZW1lbnQiLCJzdGF0ZW1lbnQiOiJUMV9NIiwid2lyZV9ub2RlcyI6
M30seyJib2R5X25vZGVzIjo2NywiYm9keV9zaGEyNTYiOiI2MDI0ZDlmYTkzYjIxYWE0YTdiYzNi
ZWVlZjI3ZGY3ZGUzN2VhZTgzMTAyODE0NmEyZGRkMThjZjY4YzhmNGI2IiwicGF0aCI6Im1lYXN1
cmVtZW50cy4wLnByb2NlZHVyZS5zdGF0ZW1lbnQiLCJzdGF0ZW1lbnQiOiJUMV9NIiwid2lyZV9u
b2RlcyI6M30seyJib2R5X25vZGVzIjo2NywiYm9keV9zaGEyNTYiOiI2MDI0ZDlmYTkzYjIxYWE0
YTdiYzNiZWVlZjI3ZGY3ZGUzN2VhZTgzMTAyODE0NmEyZGRkMThjZjY4YzhmNGI2IiwicGF0aCI6
Im1lYXN1cmVtZW50cy4wLnNlbWFudGljX2Rpc3RpbmN0bmVzcyIsInN0YXRlbWVudCI6IlQxX00i
LCJ3aXJlX25vZGVzIjozfSx7ImJvZHlfbm9kZXMiOjY3LCJib2R5X3NoYTI1NiI6ImE3ZDhlNjhk
Mjg5MTgzMGVhOTVmODA3YjAyMGUxYTFhOGYyZTI5MjZiOTVmZTI4YjgyNGE5NDdkMTdkYWY5N2Qi
LCJwYXRoIjoibWVhc3VyZW1lbnRzLjEuYXBwbGljYWJpbGl0eS5zdGF0ZW1lbnQiLCJzdGF0ZW1l
bnQiOiJUMl9NIiwid2lyZV9ub2RlcyI6M30seyJib2R5X25vZGVzIjo2NywiYm9keV9zaGEyNTYi
OiJhN2Q4ZTY4ZDI4OTE4MzBlYTk1ZjgwN2IwMjBlMWExYThmMmUyOTI2Yjk1ZmUyOGI4MjRhOTQ3
ZDE3ZGFmOTdkIiwicGF0aCI6Im1lYXN1cmVtZW50cy4xLmF2YWlsYWJpbGl0eS5zdGF0ZW1lbnQi
LCJzdGF0ZW1lbnQiOiJUMl9NIiwid2lyZV9ub2RlcyI6M30seyJib2R5X25vZGVzIjo2NywiYm9k
eV9zaGEyNTYiOiJhN2Q4ZTY4ZDI4OTE4MzBlYTk1ZjgwN2IwMjBlMWExYThmMmUyOTI2Yjk1ZmUy
OGI4MjRhOTQ3ZDE3ZGFmOTdkIiwicGF0aCI6Im1lYXN1cmVtZW50cy4xLmNhbGlicmF0aW9uLnN0
YXRlbWVudCIsInN0YXRlbWVudCI6IlQyX00iLCJ3aXJlX25vZGVzIjozfSx7ImJvZHlfbm9kZXMi
OjY3LCJib2R5X3NoYTI1NiI6ImE3ZDhlNjhkMjg5MTgzMGVhOTVmODA3YjAyMGUxYTFhOGYyZTI5
MjZiOTVmZTI4YjgyNGE5NDdkMTdkYWY5N2QiLCJwYXRoIjoibWVhc3VyZW1lbnRzLjEuaG9sZC5z
dGF0ZW1lbnQiLCJzdGF0ZW1lbnQiOiJUMl9NIiwid2lyZV9ub2RlcyI6M30seyJib2R5X25vZGVz
Ijo2NywiYm9keV9zaGEyNTYiOiJhN2Q4ZTY4ZDI4OTE4MzBlYTk1ZjgwN2IwMjBlMWExYThmMmUy
OTI2Yjk1ZmUyOGI4MjRhOTQ3ZDE3ZGFmOTdkIiwicGF0aCI6Im1lYXN1cmVtZW50cy4xLm91dGNv
bWVzLjAuc3RhdGVtZW50Iiwic3RhdGVtZW50IjoiVDJfTSIsIndpcmVfbm9kZXMiOjN9LHsiYm9k
eV9ub2RlcyI6NjcsImJvZHlfc2hhMjU2IjoiYTdkOGU2OGQyODkxODMwZWE5NWY4MDdiMDIwZTFh
MWE4ZjJlMjkyNmI5NWZlMjhiODI0YTk0N2QxN2RhZjk3ZCIsInBhdGgiOiJtZWFzdXJlbWVudHMu
MS5vdXRjb21lcy4xLnN0YXRlbWVudCIsInN0YXRlbWVudCI6IlQyX00iLCJ3aXJlX25vZGVzIjoz
fSx7ImJvZHlfbm9kZXMiOjY3LCJib2R5X3NoYTI1NiI6ImE3ZDhlNjhkMjg5MTgzMGVhOTVmODA3
YjAyMGUxYTFhOGYyZTI5MjZiOTVmZTI4YjgyNGE5NDdkMTdkYWY5N2QiLCJwYXRoIjoibWVhc3Vy
ZW1lbnRzLjEucHJvY2VkdXJlLnN0YXRlbWVudCIsInN0YXRlbWVudCI6IlQyX00iLCJ3aXJlX25v
ZGVzIjozfSx7ImJvZHlfbm9kZXMiOjY3LCJib2R5X3NoYTI1NiI6ImE3ZDhlNjhkMjg5MTgzMGVh
OTVmODA3YjAyMGUxYTFhOGYyZTI5MjZiOTVmZTI4YjgyNGE5NDdkMTdkYWY5N2QiLCJwYXRoIjoi
bWVhc3VyZW1lbnRzLjEuc2VtYW50aWNfZGlzdGluY3RuZXNzIiwic3RhdGVtZW50IjoiVDJfTSIs
IndpcmVfbm9kZXMiOjN9XSwidG9wX2ZpZWxkcyI6eyJhbGdvcml0aG0iOjIsImNvbXBhdGliaWxp
dHkiOjc3OCwiaHlwb3RoZXNlcyI6NjM4LCJqdXN0aWZpY2F0aW9ucyI6MTM2LCJsaW1pdHMiOjQy
LCJsb3dlciI6MzcxNCwibG93ZXJfY29tbWl0bWVudHMiOjY3LCJtZWFzdXJlbWVudHMiOjU4NCwi
bW9kZSI6MiwicG9saWN5IjoxMiwic2NoZW1hIjoyLCJzY29wZSI6ODB9LCJ3aXJlX2NhdGVnb3Jp
ZXMiOnsiYXNzdW1wdGlvbl9zdGF0ZW1lbnRfY29udGVudCI6MTI2LCJjb21wYXRpYmlsaXR5X3N0
cnVjdHVyZSI6MTA2LCJlcGlzdGVtaWNfY2xhc3NpZmljYXRpb25zIjoxMDY0LCJoeXBvdGhlc2lz
X3N0cnVjdHVyZSI6OTQsIm1lYXN1cmVtZW50X3N0cnVjdHVyZSI6MjE4LCJtb2RlbF9xdWVyeV9t
YXRlcmlhbF9zaGVsbCI6MzEsIm1vZGVsX3JlY29yZHMiOjg4Nywib3RoZXJfY2FycmllZF9sb3dl
cl9yZXN1bHRzIjoyNjE2LCJvdXRjb21lX3N0cnVjdHVyZSI6NzAsIm91dGVyX2ZpZWxkc19jb21t
aXRtZW50c19saW1pdHNfc2NvcGVfcG9saWN5IjoxNDAsInByb3ZlbmFuY2UiOjUyNiwicHVibGlj
X2V2aWRlbmNlX2NpdGF0aW9ucyI6MTgwfSwid2lyZV9ub2RlX2tpbmRzIjp7ImFycmF5IjozNzIs
ImtleSI6Mjc3MCwib2JqZWN0Ijo2MTgsInNjYWxhciI6MjI5OH0sIndpcmVfbm9kZXMiOjYwNTh9
fQo=
```

## 8. Recommended counting correction, boundaries and safety ceiling

Recommend an owner-approved clarification of the counting contract **before**
selecting a new cap. To preserve the synthesis's explicit “additionally charged”
wording, the proposed precise rule is:

- N_wire counts every canonical serialized key, container and scalar occurrence,
  including all closed StatementSlot reference objects and every required
  serialized lower-proof occurrence.
- Resolve only typed StatementSlot references; ordinary public/statement/step
  provenance Ref values do not cause arbitrary recursive proof expansion.
- For every StatementSlot reference occurrence, additionally charge the node
  count of its complete resolved Statement body. Charge each occurrence, not
  each unique ID. Do not subtract the already-counted reference object.
- Therefore `expanded_node_charge = N_wire + sum(N_resolved_statement_at_slot)`.
- Compute the charge on canonical input and the bounded Statement graph before
  owning lower reconstruction. Do not count validator copies/private aliases.
  A cached per-definition count is allowed only if multiplied by every actual
  reference occurrence; it is not a deduplication exemption.
- Preserve independent wire/depth/type/byte and all other frozen guards.
  Explicitly distinguish wire nodes, replacement-tree nodes and additive
  resource charge in later receipts. Do not edit the immutable old report.

This is a **recommendation for documentation clarification**, not an amendment
made here. If the owner instead intends replacement-expanded-tree semantics,
that choice needs explicit wording saying the wire and expanded views are
separate checks, not an additive charge. The historical 12,367 measurement then
retains that precise label. Neither choice establishes a numeric cap without
the later complete valid corpus and honest lower-world comparison.

Exact-limit/plus-one design is pinned but **not instantiated or claimed passed**:

1. After the counting contract is settled and all valid requests are admitted
   for calibration, let K=M_valid. The exact-limit positive must be an actual
   corpus member with measured charge K, valid owning roots, complete coverage
   and all remaining bounds satisfied. A raw K-node array is not a valid twin.
2. Its paired hostile request can append one JSON null to its compatibility
   array, adding exactly one scalar node and no Statement expansion. Verify
   byte headroom first. Both counters must measure K+1. This is intentionally
   malformed and never enters M_valid.
3. The node gate must refuse that K+1 input before cell-object or nested lower
   reconstruction, regardless of its later null-cell/count defects. Instrument
   those constructors to prove they were not entered.
4. Pin the existing Refusal fields: phase preflight; code nodes_exceeded;
   target null; epistemic level 7 / unknown / unavailable, synthetic true,
   sources empty. Omit lower_reason. Use the existing rejected-envelope schema
   for hostile input; no new error field or experimental result arm is proposed.
   Any presentation message is the fixed literal “Expanded node limit exceeded.”
   Never interpolate counts, values, paths, exception text or submitted payload.
5. Independently retain `n_H * sum(n_O(t)) <= 12`, H<=2, T<=2, O(t)<=3,
   and actual cell count<=12 before cell/lower reconstruction. No declared
   dimension or nested reconstruction may bypass that product gate.

K and K+1 are unavailable now. Neither 12,367/12,368 nor 12,415/12,416 is frozen
as the required corpus boundary pair.

The owner safety ceiling is **16,384**, not a suggested operational limit.
The two measured alternatives are below it by 4,017 and 3,969 nodes respectively.
This says nothing about unmeasured maximum-valid citation, Statement, record or
combined shapes. No assertion `M_valid <= 16384` is justified.
If a later complete valid corpus exceeds 16,384, recommend reviewed request-
carriage redesign, not an automatic increase. This report does not choose a
carriage redesign, truncate public proof or approve a convenient numerical cap.

## 9. Preservation, verification and scope

Fresh digest checks passed for the eight frozen BRC inputs listed/pinned above
and six protected DI/CV/CS/reconciliation/FC reports. All six protected
model/binding/interpretation/showcase/raw-store inventories match the accepted
synthesis and immutable stop report. Existing FC and integrated witness pins
remain in unchanged protected artifacts; no fresh integrated replay is claimed.

Public ModelStore load and reversed-membership replay agree on **36** records
and unchanged accepted revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
The model-kernel surface remains **236** ordered unique exports, digest
`77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252`.
FMA/FMW/FCD/FCW remain **0/0/0/0**.

ADRs 0001–0022 remain contiguous and unique. ADR-0023 is absent, unallocated
and unreserved, as asserted in the unchanged README. FC/CS/DI/CV accepted
dispositions are unchanged. No production contract, source, test, fixture,
ledger, identity, membership or authoritative revision was modified.

Report structure, links, terminal marker, exact embedded measurement bytes,
frozen projection/digest checks, counter/oracle arithmetic, six-run determinism,
documentation/preservation assertions, working-tree whitespace and current
milestone range whitespace were checked. No full repository or clean-checkout
matrix was rerun. The previous 4,073 suite passes plus the permitted loopback
pass remain historical evidence in the immutable report, not new tests here.

No algorithm, assumption bytes, manifest, H/T/outcome/prediction semantics,
compatibility relation, cost policy, epistemic ladder, byte ceiling or other
resource cap was changed. No accepted design/proposal/audit/plan was amended.
No model world was shrunk, result truncated or lower owning boundary mocked.
No minimax scorer, driver, accepted result, solver or Mode B surface was built.

## 10. Retention and owner gate

After checking the embedded measurement bundle against all six on-disk runs,
both exact task-created temporary roots named in section 7 were recursively
removed and checked absent. They contained only the disposable audit scripts
and measurement JSON copies. No temporary code or standalone measurement file
is retained. Exact measurement bytes remain recoverable from this report; the
script source is not recoverable from its digest. The frozen requests remain
recoverable from the unchanged resource-stop report. No owner-gate file was
removed or rewritten.

Only this calibration report is newly retained and is **untracked** for owner
review. The three original owner-gate artifacts remain untracked and unchanged.
The accepted resource-stop report stays committed at its exact pinned digest.
HEAD remains be4ddb572926959063d6550deda4e6ec0db96e42.

Owner question: approve the recommended explicit counting clarification and
authorize a documentation amendment before Slice A resumes? Numeric-cap
approval and Slice A resumption still require the honest lower-world comparison,
complete valid-corpus calibration, exact-limit/plus-one evidence and a separate
owner approval; this first-gate report grants none of them.

END OF BRC-EXP-001 SLICE A RESOURCE CALIBRATION REPORT
