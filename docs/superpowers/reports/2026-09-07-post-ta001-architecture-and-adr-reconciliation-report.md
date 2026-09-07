# Post-TA-001 Architecture and ADR Reconciliation Report

Date: 2026-09-07

## 1. Decision and checkpoint

This reconciliation was performed on `main` at baseline
`25b7cacb5aacc456d8d3507d5b76940772d94cda`, whose subject was
`docs: preserve TA-001 Slice B completion report`. `main` and `origin/main`
resolved to the same commit before mutation. The working tree was clean
except for no ordinary changes; ignored owner-local settings were preserved.

TA-001 remains accepted at exact tested implementation
`2ec18f7234273dba98098d268df4568d5cc84d85`, with final administrative
acceptance at the baseline commit above. The final owner-acceptance record is
SHA-256 `138cb9ce44327fc2f0d3826e17462488b6a9ceb51c83e778cdba53700221da5e`.

The corrected synthesis is SHA-256
`3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`; the
Slice B completion report is SHA-256
`3765001e5ebae2bd22211f0108cb7d0bd03e71fad9645ecf4e472d291b1233b3`.

## 2. Files inspected

The complete inspection covered `CLAUDE.md`, `README.md`, every ADR title and
status from ADR-0001 through ADR-0020, ADR-0014 through ADR-0020 in full, the
accepted FL-001, EA-001, and TA-001 specifications, both TA completion/owner
reports, the TA public READMEs and contracts, `backend/model_kernel`,
`backend/model_state`, `models/`, and `models/demo-printer/`.

The inspected public composition surfaces were:

- immutable source evidence and temporal projection;
- `backend/evidence_assurance`;
- `backend/evidence_alignment`;
- `backend/transition_assessment`;
- model-kernel flow declarations and queries;
- model-state and variable-port composition.

Only `README.md` and the current `CLAUDE.md` status/frontier section were
changed, plus this report. No runtime code, tests, fixtures, ledgers,
identities, memberships, canonical bytes, accepted synthesis, ADR content,
or artifacts were changed.

## 3. Contradictions found and corrected

Three stale statements were confirmed:

1. Root README said the accepted implemented sequence ended at EA-001 even
   though TA-001 was complete and owner accepted. It now says the sequence is
   complete through TA-001.
2. The authoritative `CLAUDE.md` owner-accepted sequence ended at EA-001.
   TA-001 is now included, with its adversarial hardening and dual-clean-
   checkout verification stated alongside the preceding milestones.
3. Root README's architectural frontier still narrated TA-001 as the active
   design frontier. It now treats TA-001 as the completed current boundary and
   identifies FM-001 as a distinct, unapproved design candidate.

The mirrored package status, ADR-0020 status, and TA plan status were already
truthful after final acceptance and required no changes in this reconciliation.
Historical status phrases in lower milestone documentation were preserved.

## 4. ADR sequence and disposition

ADR numbering is contiguous and unique from ADR-0001 through ADR-0020. Every
file has one identifiable title and status; links in the root milestone table
resolve to the corresponding ADR. ADR-0020 remains the latest accepted
decision and records the pure, read-only, bounded declared-transition
assessment boundary.

No ADR-0021 was created, reserved, or implied. This reconciliation report is
not an architectural decision record. The next ADR number may be allocated
only after a future design is owner accepted.

No existing ADR contained a contradiction requiring a status or decision-link
edit. ADR-0014 through ADR-0020 continue to state their accepted boundaries:
variable-port association, behavior, state, declaration-only transition,
declaration-only flow, evidence assurance, and bounded transition assessment.

## 5. Accepted current capability boundary

The accepted repository now has the following ordered boundary map:

| Layer | Accepted capability | Strongest supported claim | Next missing fact |
|---|---|---|---|
| Source/temporal | Immutable raw evidence, extraction/provenance, and rebuildable source-native temporal projection | A captured source observation/material and its receipt/effective-time relations | Physical truth, authentication, and cross-store currentness |
| Evidence assurance/alignment | Bounded content selection, fingerprints, and pure alignment to variable-value compatibility | The named evidence content is structurally consistent and aligned with a variable-value result | Flow meaning and measurement relevance |
| Identity/binding | Opaque anchors and explicit source-to-model binding ledgers | A declared identity/binding relation in the selected membership | Real-world identity or authority endorsement |
| Model kernel | Entities, hierarchy, variables, constraints, ports, VPA, behavior, state, transition, and flow records plus read-only queries | Explicit evidence-bearing model declarations and membership-relative lifecycle/query facts | Measurement association for declared flows |
| Model-state/value/semantic/constraint/behavior/state evaluation | Read-only composition over explicit declarations and carried evidence | Bounded compatibility, semantic, constraint, behavior, or state classification result | Flow-specific measurement relevance and assessment |
| Transition assessment | Pure carried-result join of two classified endpoints and aligned evidence | Bounded evidence support or non-support for one declared endpoint pattern | Occurrence, continuity, causality, and accountable history |
| Declaration versus assessment | Declarations remain separate from read-only evaluation/classification | A declaration or bounded assessment result only | Accountable physical occurrence and durable occurrence history |

FL-001's durable `FlowAnchor` and declaration do not mean a flow was observed,
active, continuous, conserved, or occurred. VP-001's variable-to-port claim
does not mean an observation occurred at or travelled through a port. EA and
evidence alignment carry no flow semantics. Fingerprints bind content; they
are not signatures, authentication, trusted time, authority, or truth claims.

## 6. Candidate comparison

| Candidate | Prerequisites today | Additive size | Truth-boundary risk | Disposition |
|---|---|---|---|---|
| FM-001 explicit flow-to-measurement association | FlowAnchor, VariableAnchor, VPA/port context, evidence-bearing kernel seams exist | Smallest new declared relation; no evaluator required | Correctable declared relevance if explicit role/context/lifecycle are required | Recommended design investigation |
| FA-001 flow assessment without association | Flow declaration and evidence exist, but no flow-to-variable measurement relation exists | Appears small but requires an ungrounded join | Would infer relevance from names, ports, units, topology, or correlation | Do not precede FM-001 |
| Accountable transition occurrence/history | TA provides bounded endpoint support only | Large new time-window, continuity, authenticity, and durable-history boundary | High risk of turning classifications into occurrence claims | Deferred |
| Configuration identity/versioning | Identity/binding seams exist | Potentially additive and mission-relevant | Durable identity and revision semantics require separate design | Legitimate alternative priority |
| Causal/diagnostic reasoning | No explicit causal/diagnostic model or evidence contract | Large and cross-cutting | Highest risk of inference from correlation, timing, or names | Premature |

## 7. Recommendation: FM-001

Recommend only a future **FM-001 — Explicit Flow-to-Measurement Association**
design investigation. FL-001 already provides durable logical flow identity and
declaration-only support. VP-001 relates variables to ports but expressly does
not say an observation occurred at or travelled through a port. EA and evidence
alignment bind selected evidence to a variable-value compatibility result but
carry no flow meaning. No accepted record relates a flow to the variable or
variables intended to measure its source, sink, boundary, rate, amount,
command, or other role.

An FA-001 evaluator today would therefore have to infer measurement relevance
from port ownership, VPA, names, units, topology, timing, or correlation. That
inference is forbidden by the accepted truth boundaries. FM-001 is the
smallest additive capability that can make the relevance relation explicit,
evidence-bearing, replayable, and correctable without claiming an observation
or physical flow.

The investigation should explore an explicit relation between existing
`FlowAnchor` and `VariableAnchor` records, with declared measurement/boundary
role, orientation/sign semantics, quantity/unit expectations, exact context
and lifecycle, and explicit FLD/VPA support pins where justified. It must not
pre-decide record names or prefixes, role vocabulary, registration versus
declaration placement of sign/orientation, correction/withdrawal structure,
cardinality, ledger ownership, fixture size, public query/result names, or
implementation slices.

## 8. Unapproved roadmap

The only recommended ordering is an unapproved roadmap:

```text
FM-001  explicit flow-to-measurement association
  -> FA-001  evidence-gated bounded flow assessment
  -> optional accountable flow occurrence/history, only after explicit
     time-window/continuity/authenticity contracts
```

Configuration identity/versioning remains a legitimate alternative priority if
the owner changes product focus. Causal, diagnostic, impact, goal, action,
planning, and control layers remain deferred until their explicit model and
evidence prerequisites exist. Nothing in this reconciliation authorizes any
of those milestones or allocates their ADR number.

## 9. Truth boundaries

An FM-001 association could establish declared measurement relevance only. It
could not establish observed flow, flow occurrence, continuity, conservation,
balance, causality, correctness, safety, or current physical activity. FA-001,
if later designed, would remain bounded and evidence-gated. Accountable flow
occurrence/history would require separate explicit contracts for time windows,
continuity, authenticity, and durable history.

The 36-record model remains declaration/evaluation evidence, not a physical
system ledger. No current-state or “why” answer may be inferred from names,
topology, VPA, values, timing, correlation, or a fingerprint alone.

## 10. Verification and preservation

Before mutation, the checkpoint branch, commit, remote ref, settings hash, TA
digests, model revision, ledger aggregate, family counts, and protected FL/TA
deterministic values matched the owner baseline. The ADR scan found exactly 20
numbered ADRs with no duplicate or missing number.

After mutation, local Markdown links in every changed file were checked: 24
links were examined and none was missing. Status phrase checks passed in the
root and package guidance. Ending markers and section continuity were checked
for the new report and the frozen TA reports. Working and staged
`git diff --check` passed.

The preserved values are:

- 36 model records;
- revision `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`;
- FRG/FLD/FLW `1/1/0` and TRG/TRD/TRW `0/0/0`;
- ledger aggregate `bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`;
- FL disclosure 660,516 bytes, SHA-256
  `096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`;
- TA result 195,429 bytes, SHA-256
  `1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`;
- final TA acceptance record SHA-256
  `138cb9ce44327fc2f0d3826e17462488b6a9ceb51c83e778cdba53700221da5e`;
- corrected synthesis SHA-256
  `3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`;
- Slice B report SHA-256
  `3765001e5ebae2bd22211f0108cb7d0bd03e71fad9645ecf4e472d291b1233b3`.

The owner-local settings file remains ignored and byte-identical at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 11. Scope and owner gate

This was documentation-only architecture/status reconciliation. No full
repository or dual-clean-checkout matrix was rerun because no binding test
required it and no runtime or behavioral file changed. No proposal was
written, no implementation was started, no fixture or ledger was appended,
and nothing was pushed or merged.

Owner gate: accept this reconciliation and separately authorize an FM-001
design-only Codex lead proposal?

END OF POST-TA-001 ARCHITECTURE AND ADR RECONCILIATION REPORT
