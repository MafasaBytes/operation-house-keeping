# VP-001 — adversarial acceptance matrix

Status: VP-001 Slices A, B, and C are owner accepted. Slice D is implemented
and adversarially reviewed; awaiting final owner acceptance.
Slice A is owner accepted at
`60b739182e423a05eac7f3c531145d90c65fe9bc`; Slice B is owner accepted at
`81179700513bb671cf9955c6a5d7163e3bcc7e1b`.
Displaying variable state beside a port is not a claim that an observation
occurred at the port.

## A. Public contract and canonical identity

| ID | Attack or assertion | Required result |
|---|---|---|
| A01 | Malformed `vpa_`/`vpw_` prefix, case, hex, or length | Typed contract rejection |
| A02 | Extra association, owner, role, state, or outcome field | Extra-forbid rejection |
| A03 | Empty VPA evidence | Typed rejection |
| A04 | VPW with evidence, context, parents, outcome, or alternate target | Typed rejection |
| A05 | Malformed parent in a later tuple position | Every supplied parent validated; rejection |
| A06 | Duplicate parent IDs | Rejected, never silently deduplicated |
| A07 | Self-supersession | Rejected |
| A08 | Reversed valid parent order | Identical canonical bytes and VPA ID |
| A09 | Forged nested model via `model_construct` or `model_copy` | Full reconstruction rejects |
| A10 | Mutated content with stale ID | Hash mismatch rejection |
| A11 | Filename/content ID mismatch | Typed load failure |
| A12 | Existing accepted record | Canonical bytes and ID unchanged |
| A13 | VPA used as `ModelRecordEvidence` | Accepted structurally, membership closure enforced |
| A14 | VPW used as evidence | Union rejection |
| A15 | Exact public exports | Only Slice A names added; no query/state names |

## B. Endpoint, owner, and evidence closure

| ID | Attack or assertion | Required result |
|---|---|---|
| B01 | Unknown variable registration | Append/load/replay integrity failure |
| B02 | Unknown port registration | Integrity failure |
| B03 | Missing variable-owner entity registration | Integrity failure |
| B04 | Missing port-owner entity registration | Integrity failure |
| B05 | Variable and port have different owner IDs | Integrity failure |
| B06 | Same owner and no VPA | No inferred record or index entry |
| B07 | Forged embedded `VariableAnchor` owner | Full registration reconstruction rejects |
| B08 | Forged embedded `PortAnchor` | Full registration reconstruction rejects |
| B09 | Type owner equals exact type owner | Structurally admitted |
| B10 | Type and instance related but IDs differ | Cross-owner rejection; no propagation |
| B11 | Missing model-record evidence member | Evidence-closure failure |
| B12 | Foreign evidence arm | Preserved as declared reference; no dereference/inference |
| B13 | Names, owners, tokens, PIF/PCN/PCM, CAD, paths, or telemetry align | No VPA fabricated |

## C. Correction roots and multiplicity

| ID | Attack or assertion | Required result |
|---|---|---|
| C01 | Parent absent or wrong kind | Lineage integrity failure |
| C02 | Parent changes variable | Subject-preservation failure |
| C03 | Parent changes port | Subject-preservation failure |
| C04 | Parent changes exact context | Subject-preservation failure |
| C05 | DAG cycle | Iterative cycle validation rejects |
| C06 | One same-root successor | Parent superseded; one healthy tip |
| C07 | Same-root fork | Valid; multiple current tips, root conflicted |
| C08 | Full same-root convergence | Valid; one healthy current tip |
| C09 | Partial convergence | Uncovered tip remains; root conflicted |
| C10 | Correction parents derive from two roots | Cross-root rejection |
| C11 | Two parentless records for one subject | Valid independent corroborating roots |
| C12 | Healthy and conflicted corroborating roots | Both disclosed; conflict not hidden |
| C13 | Same variable, several same-owner ports | Valid distinct subjects |
| C14 | Same port, several same-owner variables | Valid distinct subjects |
| C15 | Identical canonical record resubmitted | Idempotent same ID, not another root |
| C16 | Time, authority, filename, append order, hash seed varied | No winner; deterministic indexes |

## D. Withdrawal and replay

| ID | Attack or assertion | Required result |
|---|---|---|
| D01 | Unknown VPW target | Integrity failure |
| D02 | Non-VPA or VPW target | Integrity failure |
| D03 | Withdrawal of superseded/non-tip VPA | Integrity failure |
| D04 | Duplicate withdrawal of one target | Integrity failure |
| D05 | Target both successor-parent and withdrawn | Integrity failure |
| D06 | Successor of a withdrawn target | Integrity failure |
| D07 | Withdraw one active tip of a fork | Valid; sibling remains and conflicted root may become healthy |
| D08 | Withdraw one corroborating root | Other active root remains current |
| D09 | Withdraw every root tip | All roots inactive; no negative claim |
| D10 | Replay omits later withdrawal | Target becomes current again |
| D11 | Replay omits successor | Earlier tip becomes current |
| D12 | Replay contains VPA but omits endpoint/evidence dependency | Integrity failure |
| D13 | Another context appears later | Earlier exact context unchanged |

## E. Store, indexes, and hostile persistence

| ID | Attack or assertion | Required result |
|---|---|---|
| E01 | Missing required index member | Exact index tests fail |
| E02 | Mutable mapping or sequence alias | Mutation attempt rejected |
| E03 | Reversed record/file/input order | Identical canonical index order |
| E04 | Root or ancestry forged by insertion order | Recomputed root/ancestry stable |
| E05 | Malformed JSON or hostile discriminator on disk | Typed all-or-nothing load failure |
| E06 | Unexpected file/symlink/directory in ledger | Typed ledger-integrity failure |
| E07 | Failed append after staging | No promoted record; prior revision unchanged |
| E08 | Existing corrupted sibling plus idempotent append | Full-set validation rejects |
| E09 | Deep or reverse-ordered DAG | Iterative deterministic validation |
| E10 | Duplicate membership input during replay | Typed rejection |

## F. Historical and architecture preservation

| ID | Attack or assertion | Required result |
|---|---|---|
| F01 | Replay explicit 9/10/11/14/16/18/28 memberships | Exact accepted revisions, zero VP artifacts |
| F02 | Any pre-VP model byte changes | Golden byte-freeze failure |
| F03 | PT deterministic artifact changes | Hash regression failure |
| F04 | Demo ledger count changes in Slice A or B | Failure; must remain 28 |
| F05 | VP query/result surface exceeds the exact Slice B contract | Slice-boundary failure |
| F06 | Model-state composition appears | Slice-boundary failure |
| F07 | VP fixture record appears | Slice-boundary failure |
| F08 | New ledger/store/module appears | Architecture failure |
| F09 | Kernel imports temporal, state, binding, evidence implementation, or source module | Import-isolation failure |
| F10 | Accepted PT/variable/relationship/constraint validation weakened | Regression failure |

## G. Slice B authoritative-query attacks

These rows are exercised by the Slice B query and authoritative-result tests.

| ID | Attack or assertion | Required result |
|---|---|---|
| G01 | Endpoint missing | Exact four-way endpoint status; not evaluated |
| G02 | Same-owner registered pair, no roots | `not_declared`, never negative association |
| G03 | Different registered owners | `different_owners`, `not_evaluated` |
| G04 | Conflicted live root | Subject asserted; lineage conflicted |
| G05 | Independent healthy roots | Separate corroborating roots |
| G06 | Missing/duplicate/reordered result row | Outer reconstruction rejects |
| G07 | Forged root/tip/status/revision/context | Outer reconstruction rejects |
| G08 | Nested `model_construct`/`model_copy` | Full reconstruction rejects |
| G09 | Registered endpoint with no reverse associations | Registered-empty collection |
| G10 | Found VPW disclosure | Event with no assertion lifecycle |

## H. Slice C composition and implemented Slice D boundaries

| ID | Attack or assertion | Required result |
|---|---|---|
| H01 | Observation exists but association absent/conflicted/inactive | Observation disclosed independently; no port claim |
| H02 | `as_of` used to select model membership | Rejected boundary |
| H03 | Model/binding/cutoff presented as synchronized | Refused; axes remain separate |
| H04 | Port value or observed-at-port field | Public-surface rejection |
| H05 | Outer association status forged or derived from observation availability | Full reconstruction rejects |
| H06 | Nested association or variable-state `model_construct`/`model_copy` forgery | Serialized reconstruction rejects |
| H07 | Association and variable-state model revisions differ | Outer validation rejects |
| H08 | Variable, port, context, or UTC cutoff echoes differ | Outer validation rejects |
| H09 | Context changes | Association may change; temporal candidate set is unchanged |
| H10 | Cutoff changes | Temporal evidence may change; association and model revision are unchanged |
| H11 | Endpoint not admitted | Variable state still runs and remains fully disclosed |
| H12 | Upstream temporal storage failure | Original typed error propagates; no association status substitute |
| H13 | Store construction, filesystem access, write, or upper-layer import | Architecture failure |
| H14 | Slice D fixture or artifact mutation during Slice C | Preservation failure |
| H15 | Slice D appends more than one VPA or any VPW | Fixture failure |
| H16 | Existing 28 records modified | Byte-freeze failure |
| H17 | Mandatory synthetic disclaimer altered/absent | Artifact failure |
| H18 | Artifact differs across clean checkouts | Determinism failure |

## Verification evidence required

For each genuine defect found after first green, retain the minimal failing
reproduction and the passing result after repair. Final evidence must include
focused VP tests, all model-kernel and PT regressions, the full suite, both clean
checkout columns, OCP/STEP and PDF suites, import audits, `git diff --check`,
branch topology, clean worktree, 29-record current demo count, explicit
28-record historical PT replay, pinned revisions and artifact hashes, and
unchanged `.claude/settings.local.json`.
