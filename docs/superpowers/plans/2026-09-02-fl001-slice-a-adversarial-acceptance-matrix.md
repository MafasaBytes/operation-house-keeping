# FL-001 Slice A Executable Adversarial Acceptance Matrix

Date: 2026-09-02

Scope: accepted FL-001 final synthesis Section 26 rows applicable to Slice A,
plus the owner's mandatory attack list. Every row below must resolve to one or
more executable pytest cases before Slice A completion.

## 1. Test modules

| Module | Responsibility |
|---|---|
| `tests/identity_binding/test_flow_anchor.py` | `flo_` contract, minter, nested forgery, identity exports |
| `tests/model_kernel/fl001_slice_a_helpers.py` | deterministic disposable port/flow worlds through public APIs |
| `tests/model_kernel/test_flow_records.py` | exact record fields, tuple grammar, evidence, forbidden semantics |
| `tests/model_kernel/test_flow_canonical.py` | canonical bytes, golden IDs/stored files, permutation invariants |
| `tests/model_kernel/test_flow_store.py` | FRG/FLD/FLW admission, lifecycle, RC3, indexes, replay |
| `tests/model_kernel/test_flow_revalidation.py` | hostile instances/on-disk records, atomic refusal, deep DAG |
| `tests/model_kernel/test_flow_architecture.py` | imports, exports, authoritative/historical/artifact preservation |

## 2. Identity, schema, and canonical integrity

| ID | Executable requirement |
|---|---|
| I01 | Reject malformed, uppercase, wrong-length, wrong-prefix, and non-hex `flo_`; accept exact lowercase shape. |
| I02 | Reject anchor/token/pin/record hidden extras, private state, `model_construct`, `model_copy`, and nested forgery. |
| I03 | Prove equal names do not merge and different names do not split/select an anchor. |
| I04 | Reject empty role, union under 2/over 64, within-role duplicate, overlap, and malformed ports. |
| I05 | Prove within-role permutations canonicalize to identical tuples, bytes, and IDs. |
| I06 | Prove role reversal or repartition changes FRG bytes and ID. |
| I07 | Reject second exact signature; admit different token, reverse, and different partition. |
| I08 | Prove all four `FlowKindToken` fields compare exactly and imply no equivalence. |
| I09 | Canonicalize evidence/parents/pins; reject duplicate parents/pins and preserve distinct evidence. |
| I10 | Prove equivalent instants use normative `+00:00`, never `Z`. |
| I11 | For FRG/FLD/FLW, prove canonical SHA-256 equals ID suffix, compute matches, verify true. |
| I12 | Pin literal canonical bytes, stored bytes, byte counts, IDs, and file SHA-256 for all three records. |
| I13 | Prove every pre-FL canonical vector and authoritative stored byte is unchanged. |
| I14 | Equal re-append is validated no-op; same-ID/different-content rejects. |
| I15 | Reject wrong discriminator/prefix/filename and a corrupted sibling before append/load succeeds. |

## 3. Registration, support, context, and evidence

| ID | Executable requirement |
|---|---|
| R01 | Reject missing participant PRG and replay-omitted participant dependency. |
| R02 | Admit same-owner and cross-entity role partitions under identical explicit rules. |
| R03 | Reject FLD missing FRG, PCN, PIF, parent, or evidence member atomically. |
| R04 | Reject PCN subset, superset, different union, overlap-only subject, or wrong context. |
| R05 | Prove a merely containing connection cannot satisfy exact-union FLD admission. |
| R06 | Reject missing, extra, duplicate, wrong-port, wrong-dimension, or wrong-context PIF pins. |
| R07 | Reject source input/non-directional and sink output/non-directional pins. |
| R08 | Admit source output/bidirectional and sink input/bidirectional pins without implying activity. |
| R09 | Admit a structurally exact already-superseded/withdrawn PCN pin without retargeting. |
| R10 | Admit structurally exact already-superseded/withdrawn PIF pins without retargeting. |
| R11 | Prove a current replacement cannot repair an invalid exact stale pin. |
| R12 | Admit exact lifecycle and exact view-independent worlds separately. |
| R13 | Reject context kind/view/union-arm substitution and cross-context parentage. |
| R14 | Require every FRG PRG citation and one claim-specific owner basis independently. |
| R15 | Require FLD FRG/PRG/PCN/PIF citations and claim-specific owner basis independently. |
| R16 | Reject every dangling, wrong-kind, or replay-omitted extra model citation. |
| R17 | Accept `frg_`/`fld_` evidence citations; reject `flw_` and every withdrawal prefix. |
| R18 | Prove PT/VP/BH/ST/ST-002/observation material cannot create FRG/FLD. |
| R19 | Prove PCN/PIF correction/withdrawal never writes or retargets an FLD. |
| R20 | Snapshot disposable bytes and prove every failed prospective append is a no-op. |
| R21 | RC3 twin: admit valid FRG with zero PCN/PIF or inactive support; identity is registered in indexes, no FLD/support/occurrence exists, and FLD still rejects until exact support exists. |

## 4. Lifecycle, withdrawal, and replay

| ID | Executable requirement |
|---|---|
| L01 | Reject parent wrong-prefix, missing, self, duplicate, cross-anchor, cross-context, and cycle. |
| L02 | Reject a parent tuple crossing independent roots. |
| L03 | Derive one root/one tip as one current immutable tip. |
| L04 | Preserve two current tips for a same-root fork even when bodies match. |
| L05 | Preserve conflict shape after partial convergence. |
| L06 | Admit a same-root all-tip merge and leave one current tip. |
| L07 | Keep identical independent healthy roots independent while effective bodies match. |
| L08 | Prove a changed exact PCN or PIF pin changes effective-body bytes. |
| L09 | Selectively withdraw a current fork tip and recompute current tips. |
| L10 | Reject unknown, superseded, non-tip, wrong-kind, already-withdrawn, and duplicate withdrawal. |
| L11 | Reject successor plus withdrawal of one tip independent of record/input order. |
| L12 | All withdrawn roots have zero current tips while FRG registration persists. |
| L13 | Replay omission of successor/withdrawal revives the older membership-relative tip. |
| L14 | Replay retaining FLD while omitting FRG/PCN/PIF/parent/evidence dependency rejects. |
| L15 | Validate a deep legal DAG iteratively without Python recursion dependence. |
| L16 | Prove timestamp, authority, ID, filename, input, and append order never selects a winner. |

## 5. Hyperedge and semantic non-inference

| ID | Executable requirement |
|---|---|
| N01 | Many-to-many remains one ordered role partition; no pairwise record/index is created. |
| N03 | Reversed endpoint direction is a distinct signature and is never synthesized from bidirectional PIF. |
| N04 | Shared ports or cycles add no path, exclusivity, capacity, priority, activity, or causal field/index. |
| N17 | Dynamic arbitration/speaker selection cannot be encoded by bidirectional PIF or corrections. |
| N18 | Reject a second exact-signature FRG regardless of a claimed parallel physical mechanism. |
| N19 | Independent FLD/PCN roots remain evidence lineages, not mechanism identities. |
| N20 | `FlowKindToken` remains one opaque nominal token with no decomposed physical semantics. |

## 6. Preservation, determinism, and architecture

| ID | Executable requirement |
|---|---|
| P01 | Authoritative ledger stays exactly 34 records at the accepted revision with zero FRG/FLD/FLW. |
| P02 | Replay exact 9/10/11/14/16/18/28/29/32/34 memberships and require empty immutable flow indexes. |
| P03 | Preserve all 34 record bytes, accepted aggregate, and pinned PT/VP/BH/ST artifacts. |
| P04 | Prove no hidden flow field appears in any existing contract or fixture. |
| P05 | Reversed record input/copy/append order and multiple hash seeds preserve bytes, indexes, and revisions. |
| P08 | Focused/affected/full/compilation/OCP/STEP/PDF/loopback verification follows the completion gate. |
| P09 | Working/range whitespace, topology, status, and no-push/no-merge checks pass. |
| P10 | No authoritative identity mint, record append, fixture, or candidate contract exists. |

## 7. Owner-mandated attack traceability

| Owner attack | Matrix coverage |
|---|---|
| malformed/forged/nested flow anchor | I01–I02 |
| stale record IDs and hostile disk content | I11, I14–I15 |
| duplicate registration/conflicting permanent signature | I07, N18 |
| endpoint/role shape and ordering attacks | I04–I06, R01–R02 |
| wrong/incoherent/inactive PCN/PIF support | R03–R13, R21 |
| cross-signature/context/root supersession | L01–L02, R13 |
| forks, convergence, withdrawal, successor race | L03–L13 |
| evidence closure and uncitable withdrawal | R14–R17 |
| missing replay dependency/mixed membership | L14, P02 |
| file/hash nondeterminism and hostile records | I15, P05 |
| import-direction violation | P04, P08 |
| inferred occurrence/activity/compatibility/behavior/causality | R18–R19, N01–N20 |

Completion requires every row to be executable and green, with red-before
evidence retained in the Slice A completion report.
