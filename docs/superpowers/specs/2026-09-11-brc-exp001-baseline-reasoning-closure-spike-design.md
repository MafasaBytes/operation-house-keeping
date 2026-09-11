# BRC-EXP-001 — Corrected Final Synthesis

Codex lead; 2026-09-11. Design only. The accepted challenger verdict is
`approve_with_corrections`: zero blocking findings, four required corrections,
and four non-blocking observations. This document replaces the proposal as the
prospective experiment specification; neither frozen input is edited.

Current authority: the 2026-09-11 experiment-redesign owner decision accepts
RC-A–RC-C and NB-A–NB-D of the later redesign audit. Section 17 controls the
current independent slice gates, operational population, resource calibration
and preparation authority. Earlier checkpoint/receipt statements describe their
historical tasks, not the current worktree or a renewed execution authorization.

## 1. Decision, scope, and verified baseline

The corrected two-mode disposable spike is the smallest useful experiment.
Mode A tests bounded finite compatibility filtering and minimax discrimination
over supplied premises. Mode B independently attempts to derive those premises
through accepted public contracts. A truth table alone cannot test that boundary.
Enumeration suffices; a solver cannot supply absent meaning.

This design authorizes no execution. It creates no production reasoner, solver
integration, probability framework, influence ontology, diagnostic ledger,
application facade, authoritative fixture append, ADR, or architectural milestone.
No backend export, model revision, evidence source, or durable identity changes.
No Slice C, authoritative demonstration, production migration, IN-001, or CI-001
is authorized. A useful result may conclude that no future milestone is yet authorized.

The owner explicitly permits exactly the two frozen input files to be untracked
baseline exceptions. Initial `git status --short --untracked-files=all` reported
only those files, with no tracked changes. `main`, `HEAD`, and local `origin/main`
match `debcffec5a77ae270bbf8822f82ef1aa7556c5bd`. No fetch or history operation
was used. The expected final ordinary untracked set adds only this synthesis.

| Frozen input | Lines | Bytes | SHA-256 | Exact final line |
| --- | ---: | ---: | --- | --- |
| [Lead proposal](../proposals/2026-09-11-brc-exp001-codex-lead-proposal.md) | 740 | 64,770 | `0c830c433674eac130c2c01cb337a4e474eba5d2fa88fc72269e6de656a2bfeb` | `END OF BRC-EXP-001 CODEX LEAD PROPOSAL` |
| [Challenger audit](../reports/2026-09-11-brc-exp001-codex-lead-proposal-challenger-audit.md) | 659 | 48,126 | `65738e0d45ecdc47f9cdaa17bf5890b6337c9d09769ae478320f988d77ce4791` | `END OF BRC-EXP-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT` |

Both inputs were read in full. Fresh live `ModelStore.load()` and exact-membership
`replay()` agree: 36 records, accepted revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FMA/FMW/FCD/FCW are `0/0/0/0`. The model-kernel public surface contains 236
ordered, unique exports; compact JSON of the ordered list, without newline,
hashes to `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252`.
ADR filenames are exactly 0001–0022, unique and contiguous. README and accepted
owner decisions confirm ADR-0023 absent, unallocated, and unreserved.

FC is complete and owner accepted. CS is closed without implementation as
commissioning application policy. DI is closed without implementation as bounded
application composition. CV backend additions are cancelled; application delivery
is deferred until concrete consumer requirements are supplied. None is reopened.

| Protected report, freshly hashed | Bytes | SHA-256 |
| --- | ---: | --- |
| DI owner decision, 2026-09-10 | 13,298 | `ca5413a558ec5512c34845715fc1c63a8b403f31f0ccf5e505c8e2eb081bfaa0` |
| CV owner decision, 2026-09-10 | 10,030 | `7960868e4367e112f7d7dcb275d344ec7e95337be67f29ee9d8cb57d2e7a97bb` |
| CS owner decision, 2026-09-10 | 9,153 | `8557f2252c226b43dabc17ae4ffc5b8a529ac3d26999a456495e6b21c2ad33e3` |
| Post-FC reconciliation, 2026-09-10 | 56,663 | `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5` |
| FC final owner acceptance, 2026-09-09 | 2,129 | `1436b12aff7ad6b387a58bba0ea7d87386fffd14c151d5ad76b06384a7529ca8` |
| FC final verification, 2026-09-09 | 17,525 | `eb67c0830ac54c3caac9a8763afd0e84484edc8f7f900fd6391f137d5a9eec71` |

The following live inventories match the frozen checkpoints. Encoding is a map
from sorted repository-relative pathname to file SHA-256, serialized as compact
sorted-key JSON with one trailing newline. Only regular files enter the map.

| Protected tree | Files | Inventory SHA-256 |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| `var/raw_store` | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

The FC-only public query witness was freshly reconstructed using existing
`world`, `declaration`, `membership`, public collection validation, model ID `x`,
and `model_dump_json()`: 14,677 bytes, SHA-256
`a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca`.
The integrated six-result witness checkpoint is 174,490 bytes, SHA-256
`1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e`;
its accepted pin was reverified in the unchanged protected reports. Its historical
session-local `/tmp/fc001_consumer_proof.py` harness is absent in this session;
this synthesis does not claim a fresh integrated-byte replay. The frozen audit
records its independent reproduction. The integrated order is FC, EA selection,
alignment, CN A, CN B, CN A satisfied twin. It proves synthetic public composition,
including unchanged FC across the CN twin; it proves no H/T semantics. The older
13,665-byte FC witness remains superseded. Historical test accounting remains
4,073 suite passes plus one separately permitted loopback pass = 4,074, not rerun.

## 2. Numbered reconciliation and owner adjudications

RC1–RC4 below correspond exactly to audit RC-1–RC-4. NB1–NB4 correspond to its
NBO-1–NBO-4. Each entry states the change or retained limitation and its destination.
All prospective proposal corrections are enumerated here; unchanged scope and
public-contract boundaries remain binding through the explicit contracts below.

1. **RC1, proposal §§7/10/12:** count unique canonical semantic hypotheses, not
   labels or provenance records. Reject identical canonical statement, baseline
   requirements, and assumption body even with different provenance. Reject exact
   measurement procedure/decoder aliases and overlapping decoder regions. Distinct
   meanings with equivalent prediction rows remain distinct only with explicit
   semantic-distinctness approval and indistinguishability/granularity disclosure.
   Sections 4–7 and 12 specify identity keys, admission and valid twins.
2. **RC2, proposal §§9/13:** remove “expected principal B gap” as an unconditional
   prediction claim. B0 establishes compound absence only; B1 supplies H/T meaning
   without cells; B2 populates existing expressible contracts, including observed
   BH; a directed-premise-only control and a conditional-rule-only control isolate
   Gates 2/3. Each failure has its own category and attempted path (§§8/10/13).
3. **RC3, proposal §§4/10/SP20:** replace the generic envelope with disjoint A,
   B0, and diagnostic-control schemas. B0 contains no A descriptions, justifications,
   procedures, decoders, costs, compatibility cells, or expected outcomes. Enforce
   independent processes, label/note/helper renaming, A-matrix invariance, and
   closed public premise provenance for every non-unknown cell (§§5/8/12).
4. **RC4, proposal §10:** freeze the completed result only after derivation and
   size checks; canonicalize once, hash its exact bytes, retain request/result
   bytes and both externally retained expected digests, and validate/recompute on
   every read. A self-updated hash is insufficient (§11).
5. **NB1:** retain exact possibilistic minimax and the 1-versus-2 arithmetic,
   subject to structural/semantic admission. No probabilities (§§6/7/9).
6. **NB2:** tie, incomplete, one/zero-survivor and BH-conflict cases are algorithm
   controls, not architecture proof. Architecture evidence requires non-leaking B
   and isolation controls (§§8/12/13).
7. **NB3:** ceilings are experimental, unmeasured capacity limits. Measure base,
   BH, at-limit, one-over and trace reserve; stop on excess (§10).
8. **NB4:** witnesses remain synthetic evidence. They validate neither H1/H2,
   T1/T2, physical causality, nor real printer knowledge (§§1/3/9).
9. **Owner decision: execute spike — endorse with correction.** All RCs are
   incorporated here and must enter the later execution plan. Execution still
   needs separate owner authorization. Stop after each owner-gated slice (§15).
10. **Owner decision: assumption/provenance — endorse with correction.** Every
    H statement, baseline expectation, measurement identity/procedure, total
    decoder, applicability/availability/calibration/hold condition, compatibility
    cell, candidate-scope statement and optional cost has a unique local statement
    ID, exact canonical bytes, `assumed` label, supplier, explicit approver,
    rationale, applicability scope and source/justification references. Approval
    authorizes use, not truth. B0 carries none; controls are separately labelled (§5).
11. **Owner decision: measurement cost — endorse as written.** Base secondary is
    `none`; costs are absent. Only separately authorized
    `minimum_cost_after_minimax`, complete same-unit 0…100 strings, may reduce a
    primary tie. Never trade away better minimax discrimination (§§5/7).
12. **Owner decision: tiny limits — endorse with correction.** Adopt all audit
    §10 ceilings exactly, with explicit citation/step/token refinements within
    those ceilings. No inherited subsystem cap or silent increase (§10).
13. **Owner decision: canonical retention — endorse with correction.** Retain
    exact canonical A, B0 and all control request/result bytes plus external
    SHA-256 commitments in the experiment report. Apply RC4 on every read (§11).
14. **Owner decision: commit artifact or report only — endorse with correction.**
    Only a separately authorized non-authoritative experiment receipt/report may
    be committed as execution output, containing or bundling the canonical bytes
    and digests. Disposable driver/tests are not committed packages (§15).
15. **Owner decision: B population — endorse with correction.** Only B2 may
    populate relevant existing public contracts in a fresh temporary world with
    an exact record delta and new R. No compatibility cells/new semantics enter
    those records; B2 is not public-only B0 success (§8).
16. **Owner decision: later architecture threshold — endorse with correction.**
    Require all arithmetic/integrity/leakage controls, complete public derivation
    or isolation of one exact missing contract, concrete consumer need, exclusion
    of population/application policy, successful exact one-premise necessity
    control, no physical-causality claim and a separate owner gate (§13).
17. **Coverage clarification, proposal §7:** retain its conservative policy:
    missing or unknown predictions anywhere in the supplied matrix block the
    original full-set comparison, including later-refuted rows. This is stronger
    than the audit's minimum of complete viable rows, never weaker. Missing and
    unknown are distinct; both prevent ranking. Zero-support outcomes remain
    admitted unexplained surprises with empty S exactly as audit §4 recommends (§6).
18. **Schema completion, proposal §10:** pin every field/order/type/invariant,
    total decoders, semantic keys, applicability, unknown vocabulary, status axes,
    typed derivation steps, fixed limits and mode-specific result discriminators.
    No experimental name enters production exports (§§4–7/10).
19. **Gate/status correction, proposal §§7/9/13:** retain the original terminal
    status vocabulary, add precise orthogonal gap categories and a seventh gate
    for invalid/inconclusive experiments. Multiple prerequisites may coexist;
    missing prediction is never renamed missing influence (§§7/8/13).
20. **Execution/retention correction, proposal §§15/16:** split the one experiment
    into owner-gated Slice A and Slice B, with no Slice C. Retention, base no-cost
    policy, limits and architectural exclusions are settled; only execution and
    exact assumption-byte approval remain authority-dependent (§15).
21. **Acceptance completion, proposal §§11/12:** retain all SP01–SP22 and
    T01–T24, add RC1/RC4 attacks, B0/B1/B2/directed/rule isolation, import leakage,
    unlisted-rule and result-mutation controls with valid twins (§12).
22. **Objective correction, proposal §14:** freeze bounded objectives 3/4/7,
    keep 5/6 open and forbid using contract/test/serialization counts as closure
    (§14). Inspection expectations are assertions to test, never forced results.

## 3. Live public capability and epistemic ladder

Inspected public sources include `backend/model_kernel/contracts.py`,
`queries.py`, `store.py`, `__init__.py`, `backend/behavior_evaluation/contracts.py`
and `derivation.py`, public alignment derivation, accepted FC helper/query tests,
and the protected decisions. In particular, `BehaviorRegistration` is an unordered
pair; `ExactNumericEqualityRule.kind` is `exact_numeric_equality`;
`BehaviorRuleDeclaration` explicitly has no direction, role, computed outcome,
port, VPA or operational meaning. BH's `computed_relation` is `equal` or
`different` only after both admitted same-cohort observations; otherwise execution
is `not_executed`. A declared equality may be violated; it is not a transfer rule.

| Public family | Available material | Does not supply |
| --- | --- | --- |
| VM/VS/ES | Observation occurrence, value shape, quantity/role/unit, exact attachment/interpretation | Measurement procedure, future value, source truth, diagnostic meaning |
| CN | Predicate evaluation of admitted observation; satisfied/violated/not_evaluated | Fault identity, cause, severity or hypothetical output |
| BH | Unordered equality declaration; evidence-gated equal/different | Input/output transfer, fault conditioning, unobserved participant value |
| ST/TA | All-of state criteria; declared directed transition endpoints and assessment | Exhaustive fault modes, dynamics, action effects, transition occurrence |
| FL/VP/FM | Directed source/sink topology, variable-port link, exact declared measurement relevance | Engineering influence, calibration, method availability, decoder, utility |
| FC | Governing CRG/VCN designation/applicability and exact FM support | Evaluation, hypotheses or test ranking |
| EA/alignment | Bounded attempt coverage, occurrence/cutoff/scope/fingerprint joins | Future evidence, hypothesis coverage, global completeness |
| Public record/result dependencies | Exact pins, support refs, lifecycle links and owning recomputation | Physical influence, causal mechanism, arbitrary decision discovery |

Expected B0 result: observations and narrow computational dependencies are
derivable; candidate hypothesis identity/fault semantics, measurement procedures,
and hypothesis-conditioned outcome predictions are absent. CN/BH own result enums
are not T1/T2 alphabets. Availability, calibration, hold, method/time applicability
and test alphabets require additional assumptions. Cost and global candidate
completeness are outside the accepted model. No generic IN-001 layer is justified.
Gate 4's current capability absence is demonstrated by this contract inspection;
Gate 3 requires isolated controls. Sparse population must be separated by B2.
The implementation must attempt public derivation and accept a contrary validated
result; it must not return these expectations as hard-coded outcomes.

The ladder tracks source and inference distance, not increasing truth. It is
exactly seven levels, with distinct kinds within levels. Every substantive
statement retains its original kind and dependencies; processing does not lower
its assumption level. A calculation based on an assumption retains that assumption
in its transitive premise set even though the calculation itself is level 5.

| Level | Exact kinds | Permitted meaning |
| ---: | --- | --- |
| 1 | `observation`, `evaluated_result` | Accepted synthetic occurrence and evidence-backed public evaluated result, with exact evidence path and validator; no reality authentication |
| 2 | `declared_model_fact`, `computational_dependency` | Accepted exact declarations/pins and publicly reconstructed computational support; no physical influence |
| 3 | `candidate_hypothesis` | Request-carried candidate statement, baseline requirements and declared granularity; non-authoritative |
| 4 | `supplied_assumption`, `predicted_outcome` | Request-carried method/domain/decoder/applicability/availability/calibration/hold/scope/cost or conditional permission/exclusion; publicly derived predictions retain their derivation origin here |
| 5 | `calculated_result` | Exact experimental comparisons, derived compatibility calculation, S sets, cardinality scores and ranking arithmetic |
| 6 | `inferred_compatibility`, `bounded_conclusion` | Conditional candidate consistency, bounded preference and gate interpretation |
| 7 | `unknown` | Missing/unavailable meaning, evidence, rule, prediction or global coverage; never false/excludes/unaffected/impossible |

Mode A consumes levels 1/2 through public validation, levels 3/4 through exact
owner-approved supplied statements, and explicitly marked level 7. It produces
levels 5/6/7 and retained unchanged level 1–4 citations. It never accepts caller
level-5/6 output as an input shortcut. B0 consumes only levels 1/2 public premises
and level-7 opaque query demands. Its protocol constants are experiment policy,
not model knowledge. It may produce level-3/4 contents only if a named public rule
actually derives their meanings from levels 1/2, with origin `public_derived` and
complete closure; that creates no authoritative H/T record. It then calculates
levels 5/6, or reports level 7. B1/B2 and premise controls may consume explicitly
supplied levels 3/4, and are never B0 success. Neither human nor LLM authorship
changes these rules; exact approved proposal bytes remain request-carried unless
a future separately approved contract says otherwise. No live LLM runs here.

## 4. Experimental location, wire discipline, and primitive types

If execution is authorized, use a fresh `mktemp -d` directory with prefix
`/tmp/brc-exp001-`, outside the repository, containing disposable driver, local
contracts and tests. No package installation, editable install, `__init__.py`
package, backend plugin entry point, repository test package, `.pth`, or production
`sys.path` change is allowed. A one-way launcher may import accepted public backend
APIs. Production subprocesses run without this directory on their import path,
cannot resolve any experiment module, and must not open/load its files. An import
oracle checks static imports, dynamic import hooks, file-loading paths and loaded
module origins from production; any production-to-experiment reachability fails
acceptance. Running as a script outside `backend` alone is not sufficient proof.

The following is schema notation, not code to implement in this task. A record
lists fields in declaration/presentation order. JSON wire objects always sort
keys lexicographically (§11); these two orders are explicit and not competing
serialization rules. All fields are required unless `?` is shown; `?` means the
key is absent when unused, never implicit default or null. `X|null` explicitly
allows null. Unknown keys, wrong union arms and null-for-absent are refused at
every experimental object. Arrays are exact JSON lists at ingress and immutable
ordered tuples internally; no arbitrary Python instances are accepted.

| Primitive | Exact definition |
| --- | --- |
| `Label` | ASCII `[A-Za-z0-9_][A-Za-z0-9_.-]{0,31}`, 1–32 bytes; local to one request; no engineering identity |
| `Text` | NFC Unicode, 1–512 UTF-8 bytes, no NUL/control characters except LF; reject noncanonical form rather than normalize submitted bytes |
| `Digest` | Exactly 64 lowercase hexadecimal characters; experimental-byte checksum only |
| `UInt(a,b)` | Exact built-in JSON integer a…b inclusive; Boolean is not integer |
| `DecimalToken` | ASCII canonical finite decimal, at most 32 bytes: optional `-`, integer `0` or nonzero-leading digits, optional fraction ending in a nonzero digit; no `-0`, exponent, leading `+`, whitespace, NaN or Infinity |
| `CostToken` | String `0` or `[1-9][0-9]*`, parsed integer 0…100 inclusive; maximum 3 bytes |
| `LocalRefs(n)` | Unique ASCII-sorted list of 0…n local IDs, all resolved in the same request/result; duplicate references refused |
| `PublicPath` | Ordered list of 1…16 exact field-name strings or strict nonnegative indices 0…11,999; each string 1…128 ASCII bytes; paths are typed selectors, not executable JSONPath |
| `Ref` | `(space: public|statement|step|query|protocol, root: Label, path: PublicPath)`; public root is F/N/E/BH; local scalar refs use a one-element field path; no filesystem path or executable expression |
| `Epi` | `(level: UInt(1,7), kind: exact §3 kind, origin: public_observed|public_evaluated|public_declared|public_derived|assumed|algorithmic|inferred|unavailable, synthetic: true, sources: list[Ref](0…4))` |

Epi pairs are validated: observation→1/public_observed; evaluated_result→1/
public_evaluated; declared_model_fact→2/public_declared; computational_dependency→2/
public_derived; candidate_hypothesis→3/assumed or public_derived; supplied_assumption→4/
assumed; predicted_outcome→4/assumed or public_derived; calculated_result→5/algorithmic;
inferred_compatibility or bounded_conclusion→6/inferred; unknown→7/unavailable.
Non-unknown derived claims require nonempty source refs and a reconstructable
rule. Four direct refs do not prune public lower proof: complete lower roots
remain intact. Transitive closure is through bounded steps. These classifications
describe synthetic experiment material only; they cannot relabel the protected
demo fixture or literal producer provenance.

Public lower schemas retain their exact current owning types, nested field
order, valid numbers, discriminators and validators, pinned to the baseline HEAD.
Experimental text/decimal restrictions do not rewrite lower-schema payloads.
Full-envelope byte/node/depth/token limits still apply to lower payloads (§10).

## 5. Exact requests, statements, and mode-specific schemas

Each table row defines one closed record in field order. Bounds include both
raw and expanded counts. There are no omitted semantic defaults.

| Record | Fields in order, types and invariants |
| --- | --- |
| `Citation` | `citation_id: Label; supplier: Text; approver: Text; rationale: Text; applicability_scope: Text; references: list[Ref](1…4); epistemic: Epi`. Approval identifies the actor authorizing exact bytes for this experiment, not an authentication service or truth claim. |
| `Statement` | `statement_id: Label; body: Text; epistemic: Epi; citation: Citation`. Canonical statement bytes are the canonical encoding of this complete object, not a self-declared hash field. Globally unique statement/citation IDs; each H/prediction and every assumption-bearing object owns its own Statement. Referenced justifications may be shared. Total Statements ≤24. |
| `BaselineCheck` | `check_id: Label; kind: observed_decimal_equals|cn_verdict_equals|bh_relation_equals|record_current_equals; source: Ref; expected: DecimalToken|satisfied|violated|equal|different|true; statement: Statement`. Tagged kind selects exactly the corresponding expected type. Record membership/currentness is checked through public material/query, not name matching. |
| `Hypothesis` | `hypothesis_id: Label; statement: Statement; assumption_body: list[Label](1…4); baseline_requirements: list[BaselineCheck](0…4); model_record_refs: list[Ref](0…4); semantic_distinctness: Statement`. Main H has two checks. Assumption-body refs resolve to exact supplied statements; statement kind candidate_hypothesis. Distinctness statement explicitly approves counting granularity and identifies why this meaning differs from the other H; it is not evidence of truth. |
| `OutcomeToken` | `outcome_id: Label; region: Region; statement: Statement`. IDs unique within a measurement; outcome statements classify the supplied decoder meaning, not an observation. The label `unknown` is legal as an outcome token and never means the cell relation `unknown`. |
| `Region` | Closed union: `(kind: decimal_interval; lower: DecimalToken|null; lower_inclusive: bool; upper: DecimalToken|null; upper_inclusive: bool)` or `(kind: literal_set; values: list[Label](1…3))`. Null bound means unbounded; its inclusive flag must be false. Nonempty intervals only; literals unique. |
| `Procedure` | `method: Text; subject: Ref; quantity: Text; unit: Text; scenario: Text; domain: Domain; statement: Statement`. Explicit subject nomination, never inference from shared name/entity. |
| `Domain` | `(kind: finite_decimal; unit: Text)` or `(kind: literal_codes; values: list[Label](1…3))`. Finite-decimal domain means all canonical finite numeric values in that exact unit, within representation bounds; literal domain lists every successful code. |
| `Condition` | `status: affirmed|denied|unknown; scenario_ref: Ref; statement: Statement; epistemic: Epi`. scenario_ref names the exact owning procedure.scenario. A affirmed/denied condition remains level 4/supplied_assumption/assumed; unknown is level 7/unavailable. Public-derived condition must cite the exact rule/declaration, never infer applicability from names. |
| `MeasurementCandidate` | `measurement_id: Label; identity: Statement; procedure: Procedure; outcomes: list[OutcomeToken](1…3); applicability: Condition; availability: Condition; calibration: Condition; hold: Condition; admitted: true; semantic_distinctness: Statement`. All four statuses must be affirmed for this nominated scenario before matrix admission. `admitted: true` is checked, never trusted alone. Unknown/denied condition prevents original-set comparison; no natural-language execution is used to decide status. |
| `CompatibilityRelation` | `hypothesis_id: Label; measurement_id: Label; outcome_id: Label; relation: permits|excludes|unknown; statement: Statement; justification_refs: list[Label](1…4); unavailable_reason: GapCode?`. One relation for every supplied H×T×O triple. Known cells have level-4 predicted_outcome/assumed Statement in A; unknown cells have level-7/unavailable Statement and required unavailable_reason. |
| `Scope` | `candidate_scope: explicit_supplied_set; hypothesis_scope: explicit_supplied_set; global_hypothesis_completeness: unknown; global_measurement_completeness: unknown; hypothesis_granularity: unique_canonical_semantic_definition; statement: Statement`. No globally-complete arm exists. |
| `NoCostPolicy` | `secondary: none`. No cost, unit or cost-justification field permitted anywhere in this arm. |
| `CostEntry` | `measurement_id: Label; amount: CostToken; statement: Statement`. Exactly one per supplied measurement; sorted by measurement ID. |
| `CostPolicy` | `secondary: minimum_cost_after_minimax; unit: Text; authorization: Statement; entries: list[CostEntry](1…2)`. One common artificial unit; exact explicit authorization and complete costs required. |
| `Policy` | `prior: none; candidate_scope: explicit_supplied_set; missing_cell: refuse_comparison; secondary_policy: NoCostPolicy|CostPolicy`. No probability, likelihood, entropy, utility or hidden selection field. |

The 24-statement bound counts unique owned statements, not repeated references.
To keep the complete base within it, one approved statement may describe several
fields of the same semantic assertion (for example one measurement identity,
method, decoder, applicability/availability/calibration/hold assertion). Repeated
`Statement` slots then carry a local reference instead of another object:
normatively `StatementSlot = Statement | (statement_ref: Label)`, with exactly one
full definition per ID. Every Statement-typed slot in this section accepts this
closed reference arm. Forward references resolve after count preflight; cycles
are forbidden. A reference cannot change the referenced epistemic class, supplier
or canonical bytes. Shared slots must explicitly enumerate each field they cover
in the statement body; they do not exempt any individual claim from provenance.
One semantic assertion may cover all decoder regions of one measurement, but each
compatibility cell has its own unique statement ID. A compact base uses 2 H + 2
distinctness + 4 baseline-expectation + 2 complete method + 8 cell + J1/J2 + 1 scope
= 21 statements; a cost variant may add at most its three remaining statements.
No full statement can occur twice under the same ID, even with identical bytes.

The individual domain slots above remain separately addressable and each has a
unique assertion identity `(statement_id, typed field path)`, even when one
compound approved statement supplies several slots. The exact compound bytes and
all covered paths must be approved together. Unrelated claims cannot borrow that
approval. H and prediction statements are never combined across H/cell identities.

`LowerRoots = (F: FlowOperatingCriterionResult; N: ConstraintEvaluationResult;
E: OperationalEvidenceSelectionResult; BH: BehaviorEvaluationResult?)`.
Use the complete owning public schemas, not generic JSON objects bypassing them.
F carries full ModelQueryMaterial and R; N carries its VS/ES/VM; no detached copies
are substituted. L is derived from E and N's VS, with independent expected
fingerprint. BH carries its full required proof if present. No root is stripped
to meet a cap. Root-field epistemic binding is fixed by the public schema: records
are level 2, occurrences level 1/observation, evaluated fields level 1/evaluated_result,
missing fields level 7. An outer label cannot overwrite these per-field classes.

`LowerCommitments = (lower_sha256: Digest; model_revision: ModelRevision;
context: accepted AssertionContext; cutoff: accepted UTC datetime;
expected_fingerprint: exact public fingerprint value; binding_revision: exact
public revision value; interpretation_revision: exact public revision value)`.
These values are retained independently by the setup receipt; equality is exact,
not latest-wins. The fingerprint/revision values use their owning public types
and validators at baseline HEAD, with no experimental reinterpretation. Model
membership is exact, not selected by temporal cutoff. Their classification is
public-derived commitment metadata; checksums do not authenticate sources.

| Envelope | Exact fields in order |
| --- | --- |
| `ModeARequest` | `schema: brc-exp001.mode-a.request/v1; mode: A; algorithm: finite_compatibility_minimax/v1; limits: Limits; lower: LowerRoots; lower_commitments: LowerCommitments; hypotheses: list[Hypothesis](1…2); measurements: list[MeasurementCandidate](1…2); compatibility: list[CompatibilityRelation](0…12); justifications: list[Statement](0…24); scope: Scope; policy: Policy`. Count zero cells is representable incomplete input, never admitted. Empty H/T requests are input_refused; zero surviving H is a result of filtering. |
| `OpaqueQuery` | `hypothesis_labels: list[Label](1…2); measurement_labels: list[Label](1…2); outcome_labels: list[(measurement_id: Label; labels: list[Label](1…3))](1…2); public_rule_id: PublicRuleId; epistemic: Epi(7,unknown,unavailable)`. Labels specify requested slots only; no semantics, expected value or permission follows from them. |
| `ModeBRequest` | `schema: brc-exp001.mode-b.request/v1; mode: B0; algorithm: finite_compatibility_minimax/v1; limits: Limits; lower: LowerRoots; lower_commitments: LowerCommitments; query: OpaqueQuery`. No A request, A digest, hypothesis description, justification, procedure, decoder, cost, compatibility, expected-outcome or arbitrary policy field exists. Protocol constants are fixed: prior none, secondary none, explicit supplied query scope, unknown global completeness. |
| `ControlRequest` | `schema: brc-exp001.control.request/v1; mode: control; control: B1|B2|directed_premise|conditional_rule; base: ModeBRequest; meanings: ControlMeanings; population_delta: PopulationDelta?; added_premise: DirectedPremise|ConditionalRule?`. This is a separate top-level union arm, never an optional extension of ModeBRequest. |
| `ControlMeanings` | `hypotheses: list[Hypothesis](1…2); measurements: list[MeasurementCandidate](1…2); justifications: list[Statement](0…24); scope: Scope`. It contains no cells or costs. Labels exactly match the opaque query. |
| `PopulationDelta` | `before_revision: ModelRevision; after_revision: ModelRevision; added_record_ids: list[exact public record ID](1…32); populated_contracts: list[PublicRuleId](1…8); declaration_authority_refs: list[Ref](1…4); epistemic: Epi(2,declared_model_fact,public_declared)`. Exact added canonical records reside in the after material, not an unexplained ID list. All after roots use after R. The separately retained before request is independently committed outside this object. |
| `DirectedPremise` | `kind: directed_relation; source: Ref; target: Ref; condition: Statement; consequence: Statement; statement: Statement`. No allowed-outcome cells, prospective observed values, embedded executable text or table are permitted. It can close a step only through an explicitly named existing public rule that accepts that meaning; otherwise unknown. |
| `ConditionalRule` | `kind: conditional_allowed_outcomes; rows: list[(hypothesis_id: Label; measurement_id: Label; allowed_outcomes: list[Label](1…3); statement: Statement)](1…4); applicability: Statement`. Exactly one row per H×T, finite allowed sets; exclusions are the explicit complement within the admitted total vocabulary. This is a supplied prediction rule in a labelled control, never public B material. |

`PublicRuleId` is one of the exact public operation names in §8; strings are
identifiers for a fixed dispatcher, never imports or callable expressions. A B
request selects one attempted rule; the bounded derivation inventory may try each
of the fixed rules and disclose the exact failed path. No hypothetical predictor
name is registered merely to make a control succeed.

B1 forbids both optional fields. B2 requires population_delta and forbids
added_premise. Directed and conditional controls use the B2-populated base and
require only their matching added_premise, with no population_delta in that
request; the paired B2 reference is external. Conditional control is paired with
the same B2 bytes without the directed premise: its sole delta is the conditional
rule. All control counts are aggregate, including nested base. A B2 world may
share approved H/T meanings with B1, but cannot count them as public success.

## 6. Semantic admission and complete coverage

The counting unit is one unique canonical semantic hypothesis. Its comparison
key is canonical JSON of `(statement.body, baseline_requirements semantic bodies,
resolved assumption_body bodies)`. Baseline semantic bodies include kind, exact
public subject/path and expected value, not check ID or provenance metadata.
Sort baseline bodies and assumption bodies by canonical bytes for this key only;
reject duplicate baseline bodies and duplicate assumption-body references first.
Exclude hypothesis ID, citation IDs, supplier, approver, rationale/source metadata,
display text and prediction row from the key. Provenance cannot manufacture a new
semantic candidate; changing prediction under an identical H definition creates
conflicting premises, not two candidates. Canonical text is exact NFC, with no
unapproved paraphrase normalization. Semantically equivalent paraphrases must be
rejected at owner semantic admission; lack of a decidable natural-language theorem
prover is disclosed. Exact-byte keys are an executable floor, not a claim to solve
all semantic equivalence. No automatic ranking is valid without this explicit
semantic-distinctness approval for H and T meanings.

The audit's alias counterexample remains an explicit mathematical warning outside
the executable two-H ceiling: for A/B/C, T1 branches {A,B}/{C}, T2 branches
{A}/{B,C}, both scores are 2. Add A_alias with the same canonical meaning,
baseline assertions and prediction row: T1 becomes 3, T2 remains 2, and the tie
changes without new engineering knowledge. The executable within-limit attack
uses two aliased rows and must fail semantic admission. The four-row illustrative
request separately fails count_exceeded before any scoring.

A measurement semantic key includes exact subject, procedure method, quantity,
unit, scenario/domain, resolved applicability/availability/calibration/hold bodies,
and decoder regions. Ignore measurement/outcome labels and provenance metadata;
compare regions in canonical region order. Reject exact duplicate procedure/decoder
definitions; v1 does not collapse candidates silently. Relabelling low/high or
code_a/code_b changes no procedure semantics. The semantic-distinctness approval
must flag same-method aliases even when note text or provenance differs.

Each decoder is a total deterministic map over every successful raw result in its
declared domain. Decimal intervals must be pairwise disjoint and cover the entire
finite-decimal domain, including each boundary exactly once; literal sets must be
pairwise disjoint with union exactly the declared literal domain. Reject duplicate
regions, overlap, gap, inconsistent unit/quantity, empty outcome vocabulary, or
unestablished procedure/application conditions. Unknown/other successful outcomes
must be explicit regions/tokens, not missing cells. Malformed values, absent
observations and acquisition failure are unavailable inputs, outside successful
outcomes. A successful raw value outside the declared domain invalidates outcome
abstraction applicability; it is never automatically `excludes` or impossible.

Identical prediction rows under genuinely distinct approved H meanings are valid
and disclosed as observationally indistinguishable within this exact set. Scores
depend on the supplied hypothesis granularity. Equivalent measurement partitions
under genuinely distinct procedures are valid tied candidates, recorded as
equivalent discrimination; duplicate procedure identities remain refused. For
nondeterministic rows the relation is a cover, not necessarily a partition.
Partition equivalence compares the multiset of survivor sets with outcome labels
removed, retaining multiplicity and empty branches; it is disclosure only, not
permission to delete a candidate or choose a winner.

Structural completeness requires exactly one `permits`, `excludes`, or `unknown`
cell for every member of the actual supplied H×T×O product. Extraneous labels,
duplicate triples and cells outside a decoder vocabulary are input_refused.
Missing triples yield insufficient_information in A (explicit missing-cell list),
not fabricated unknown/excludes cells. An explicit unknown has a required reason;
it also blocks full comparison. B emits a derived or unavailable CellResult for
every requested triple; opaque outcome labels alone do not admit a vocabulary.

Full ranking requires all supplied rows known, including rows later refuted by
baseline checks. Every fully known h,t row must permit at least one outcome;
an all-excluded row is input_refused, never a shortcut for eliminating h. When
unknowns prevent proof of this property, matrix admission is incomplete, not an
assertion of all-excluded invalidity. For admitted viable H and every t:
`union(S(t,o) for o in O(t)) = H`. Each candidate identity, decoder, applicability,
availability and exact supplied candidate list is retained. No silent removal
of an unusable T permits comparison over the original set; a smaller set requires
a separately approved request/commitment. Global H/T completeness remains unknown.

The audit's exact zero-support rule is retained: keep `S(t,o)` empty and disclose
an unexplained outcome under supplied hypotheses. It participates in the formal
maximum but is numerically inert because row coverage guarantees another nonempty
S. It remains an admitted surprise outcome; it does not itself refuse ranking or
assert global completeness/incompleteness as a proven fact. If later observed,
no supplied hypothesis remains; report inadequacy of supplied hypotheses/premises,
not physical impossibility or actual cause. Global coverage was already unknown.
If every H permits an explicit unknown/other branch, its score contribution is
`|H|`; a perfect binary split plus that branch has worst score 2 for two H.

## 7. Final algorithm, results, statuses, and deterministic refusal order

`finite_compatibility_minimax/v1` is prior-free possibilistic enumeration. With
viable H, admitted measurements T and outcome vocabulary O(t), define exactly:

`S(t,o) = {h in H | compatible(h,t,o) = permits}`

`score(t) = worst(t) = max(|S(t,o)| for o in O(t))`

`reduction(t) = |H| - score(t)`

`primary_best = {t in T | score(t) = min(score(u) for u in T)}`

With secondary none, `final_best = primary_best`. With authorized complete cost,
`final_best = {t in primary_best | cost(t) = min(cost(u) for u in primary_best)}`.
Probability, prior, likelihood, entropy and information gain are excluded from v1.
A stable ID may order output, never select a winner.

Ordered execution and admission:

1. Preflight raw bytes, token/depth/node/type/count limits, discriminators, product
   and output reserve (§10) before cells or nested public-result reconstruction.
   Check independent expected request bytes/digest and lower commitments.
2. Reconstruct complete owning lower roots and exact independent joins: R and
   record membership, context, variable/owner, flow/port/orientation, governing
   CRG/VCN, candidate 0 occurrence, binding/interpretation revisions, cutoff and
   fingerprint. Derive L from E and N's actual carried VS. Never repair lower
   array order or substitute satisfied ungoverned B for governing A.
3. Admit applicable FC, complete bounded EA and matched attached alignment, and
   evaluated governing CN. A valid lower refusal/ambiguity is baseline_unavailable.
   Valid satisfied governing A is baseline_not_violated. The synthetic receipt
   policy, when explicitly supplied, uses inclusive age ≤3,600 seconds and the
   complete two-hour horizon; 3,594 seconds passes, without claiming freshness.
4. Resolve typed experimental statements/provenance. Check semantic identity,
   total decoder, candidate conditions, full triple domain, row coverage and
   cost-policy consistency. Structural invalidity refuses; unknown/missing
   material remains incomplete. In B derive meanings/cells through §8 first;
   never infer meaning from the query labels. Retain axes independently.
5. Compare every baseline requirement using only observed_decimal_equals,
   cn_verdict_equals, bh_relation_equals, record_current_equals and public typed
   paths. Exact contradiction gives inconsistent_with_supplied_facts even if
   another check is unavailable; retain both lists. No contradiction plus any
   required unavailable check gives unresolved. Otherwise compatible_with_supplied_facts.
   H is the compatible set. A required unknown in any candidate blocks the full
   comparison in this conservative spike, even where another check contradicts it.
6. Full matrix coverage remains mandatory even for refuted rows. Missing/unknown
   cells prevent ranking before handling zero/one survivor terminal outcomes.
   Once required information is complete: zero H → no_viable_hypotheses; one H →
   no_discrimination_needed. Both have no S scores, best set or recommendation;
   retain complete input cells and consistency trace. Empty initial H is malformed.
7. For at least two H, construct all S sets in measurement/outcome ASCII order,
   each H set in ASCII order; retain contributing cells, including exclusions.
   Compute exact integer scores/reductions and full primary/final best sets.
8. If best reduction is zero, report no_discriminating_measurement, retain scores
   and arithmetic best sets as ties-only disclosure, recommendation null, even
   with unequal costs. Otherwise one final member gives preferred_within_supplied_set;
   two give tied_best_within_supplied_set with no selected member.
9. Validate every derived field, classification, dependency closure and gate;
   check actual result size, freeze canonical bytes and external commitments (§11).

| Result record | Fields in order, types and invariants |
| --- | --- |
| `Gap` | `category: GapCode; target: Ref; attempted_rule: PublicRuleId|null; missing_property: Text; evidence_refs: list[Ref](0…4); epistemic: Epi(7,unknown,unavailable)`. Multiple categories may attach to one cell. No executable exception text. |
| `GapCode` | `missing_semantics`, `hypothesis_generation`, `fault_mode_representation`, `measurement_candidate_representation`, `measurement_procedure`, `outcome_vocabulary`, `test_applicability`, `engineering_influence_semantics`, `behavior_input_output_semantics`, `executable_prediction`, `model_population`, `unsupported_record_family`, `unavailable_public_field`, `invalid_model_material`, `application_policy`, `algorithm_failure`. This is a local finite enum, not a kernel contract. |
| `Refusal` | `phase: preflight|commitment|lower_validation|baseline|semantics|coverage|derivation|ranking|retention; code: RefusalCode; target: Ref|null; lower_reason: Text?; epistemic: Epi`. Text is the exact bounded public reason code, not a truncated arbitrary exception. |
| `RefusalCode` | `bytes_exceeded`, `token_exceeded`, `depth_exceeded`, `nodes_exceeded`, `type_invalid`, `schema_invalid`, `count_exceeded`, `product_exceeded`, `trace_bound_unproven`, `commitment_mismatch`, `lower_invalid`, `join_mismatch`, `baseline_unusable`, `semantic_alias`, `decoder_invalid`, `candidate_unavailable`, `scope_invalid`, `cell_duplicate`, `cell_outside_domain`, `row_all_excluded`, `cell_missing`, `cell_unknown`, `cost_invalid`, `epistemic_invalid`, `mode_leakage`, `rule_unlisted`, `derivation_unavailable`, `algorithm_mismatch`, `result_mutated`, `output_exceeded`, `nondeterministic`, `production_import`. |
| `CheckResult` | `check_id: Label; status: matches|contradicts|unavailable; expected: exact check expected type; actual: same type|null; source: Ref; gap: Gap?; epistemic: Epi(5,calculated_result,algorithmic)`. Unknown actual requires gap, never false. |
| `HypothesisConsistencyResult` | `hypothesis_id: Label; status: compatible_with_supplied_facts|inconsistent_with_supplied_facts|unresolved; checks: list[CheckResult](0…4); conflict_ids: LocalRefs(4); unknown_ids: LocalRefs(4); epistemic: Epi(6,inferred_compatibility,inferred)`. Recompute status from checks, retaining conflicts and unknowns together. |
| `CellResult` | `hypothesis_id: Label; measurement_id: Label; outcome_id: Label; relation: permits|excludes|unknown; origin: supplied|public_derived|control_derived|unavailable; statement_ref: Label?; step_id: Label?; gaps: list[Gap](0…16); epistemic: Epi`. A known supplied cell requires statement_ref; a known derived cell requires step_id. Unknown requires unavailable origin, no fabricated statement_ref, and nonempty gaps. Public B known cells forbid supplied/control origins. |
| `AdmittedMatrix` | `supplied_hypothesis_ids: LocalRefs(2); viable_hypothesis_ids: LocalRefs(2); measurement_ids: LocalRefs(2); outcomes: list[(measurement_id: Label; outcome_ids: LocalRefs(3))](1…2); cells: list[CellResult](1…12); completeness: complete; row_coverage: every_h_t_permits; hypothesis_aliases: rejected; measurement_aliases: rejected; indistinguishable_hypothesis_groups: list[LocalRefs(2)](0…1); equivalent_measurement_groups: list[LocalRefs(2)](0…1); scope: explicit_supplied_set; global_completeness: unknown; epistemic: Epi(5,calculated_result,algorithmic)`. No unknown/missing cells. Empty viable list is allowed after complete checks. Each equivalence group has exactly two distinct IDs. |
| `SurvivingSet` | `measurement_id: Label; outcome_id: Label; hypothesis_ids: LocalRefs(2); contributing_cell_refs: list[Ref](1…2); unexplained: bool; epistemic: Epi(5,calculated_result,algorithmic)`. Include all viable cells for this branch, not only permissions; unexplained iff survivor set empty. |
| `MeasurementScore` | `measurement_id: Label; surviving_sets: list[SurvivingSet](1…3); worst_case_survivors: UInt(0,2); guaranteed_reduction: UInt(0,2); cost: CostToken?; epistemic: Epi(5,calculated_result,algorithmic)`. Only present for ≥2 viable H and complete admitted matrix. |
| `TiedBestResult` | `primary_best: LocalRefs(2); final_best: LocalRefs(2); policy: none|minimum_cost_after_minimax; recommendation: Label|null; discriminating: bool; epistemic: Epi(6,bounded_conclusion,inferred)`. Nonempty arithmetic sets only when scores exist. recommendation is present as a value only for positive reduction and exactly one final_best; otherwise null. No selected/first/preferred Boolean on tied rows. |
| `DerivationStep` | `step_id: Label; rule: StepRule; dependencies: list[Ref](1…4); output_ref: Ref; depth: UInt(1,4); epistemic: Epi`. Output value resides once in its typed result slot, never arbitrary nested JSON. Steps are acyclic, topologically ordered; dependency depth is recomputed, not trusted. All source premises remain reachable. |
| `StepRule` | Exact PublicRuleId or `baseline_compare/v1`, `supplied_cell/v1`, `conditional_rule_control/v1`, `surviving_set/v1`, `worst_count/v1`, `best_set/v1`, `cost_secondary/v1`, `bounded_conclusion/v1`. Supplied/control rules are forbidden in B0 premise closure. |
| `GateResult` | `gate: UInt(1,7); name: exact §13 name; status: met|not_met|inconclusive; evidence_refs: list[Ref](0…4); recommendation: exact §13 recommendation token; epistemic: Epi(6,bounded_conclusion,inferred)`. Seven rows, fixed gate order; no milestone-authorized flag may be true. |
| `ResultBody` | `status: TerminalStatus; admission: admitted|refused|unavailable; baseline: unavailable|not_violated|violated; matrix_state: complete|incomplete|unavailable; derivation_availability: supplied|public_complete|public_incomplete|control_only|unavailable; hypothesis_results: list[HypothesisConsistencyResult](0…2); cell_results: list[CellResult](0…12); admitted_matrix: AdmittedMatrix|null; scores: list[MeasurementScore](0…2); best: TiedBestResult|null; refusals: list[Refusal](0…32); gaps: list[Gap](0…32); steps: list[DerivationStep](0…64); gates: list[GateResult](7); limitations: list[Text](1…16); epistemic: Epi(6,bounded_conclusion,inferred)`. Matrix cells are local references to once-carried cell_results on wire, using `(cell_index: UInt(0,11))`; never duplicate full cells. |
| `ModeAResult` | `schema: brc-exp001.mode-a.result/v1; mode: A; algorithm: finite_compatibility_minimax/v1; request: ModeARequest; result: ResultBody`. |
| `ModeBResult` | `schema: brc-exp001.mode-b.result/v1; mode: B0; algorithm: finite_compatibility_minimax/v1; request: ModeBRequest; derived_hypotheses: list[Hypothesis](0…2); derived_measurements: list[MeasurementCandidate](0…2); result: ResultBody`. Derived H/T statements must have public-derived origin and closure; no invented approver of supplied semantics. Public provenance occupies citation supplier/approver as exact declaration authority reference text, not experiment approval. Missing meanings leave lists empty, with per-query gaps. |
| `ControlResult` | `schema: brc-exp001.control.result/v1; mode: control; control: matching request control; algorithm: finite_compatibility_minimax/v1; request: ControlRequest; result: ResultBody`. Any complete result has derivation_availability control_only. |
| `OverallExperimentResult` | Closed union ModeAResult|ModeBResult|ControlResult. All requests/results carry their discriminator. Request present exactly once; its complete bytes are embedded structurally in successful parsed results. |
| `RejectedEnvelopeResult` | `schema: brc-exp001.rejected/v1; mode: rejected; status: input_refused; refusal: Refusal; input_sha256: Digest; epistemic: Epi(7,unknown,unavailable)`. For hostile/unparseable input only: no echo of unbounded input, no nested request/results reconstruction. The report retains bounded forensic metadata; oversized hostile bytes are not bundled as frozen admitted requests. |

Two exact result-schema refinements complete the table. `Triple` has fields
`hypothesis_id: Label; measurement_id: Label; outcome_id: Label` in that order.
ResultBody has `missing_cells: list[Triple](0…12)` immediately after cell_results,
sorted by (H,T,O), with no duplicates. It is exactly the supplied product minus
present cell triples in A. It is empty when B emitted an explicit unknown for
every requested triple. It never silently completes the admitted matrix.
CellResult.gaps uses `(gap_index: UInt(0,31))` references to the once-carried
ResultBody.gaps, and the table's per-cell bound of 16 applies to these references.
Cell epistemic classification is exact: supplied→level 4/predicted_outcome/assumed;
public_derived→level 4/predicted_outcome/public_derived; control_derived→level 5/
calculated_result/algorithmic with the level-4 control rule retained in closure;
unavailable→level 7/unknown/unavailable. A step calculating a public prediction
is separately level 5 and preserves the original prediction/declaration premises.
For record_current_equals, expected is literal true but actual may be either
Boolean or null; false is a contradiction, null an unavailable finding.

The A requirement that method/provenance premises be assumed applies to A and
the supplied portions of controls. In B-derived H/T objects, exact model method
declarations, if any are actually found, retain level 2/public_declared, and their
computed semantic-distinctness/decoder-coverage proofs retain level 5/algorithmic.
Public-derived candidate/prediction meanings retain levels 3/4 with public_derived
origin. They do not need, and must not fabricate, a supplied-assumption approver.
Citation authority comes from the actual public declaration. This distinction
allows a genuine complete public derivation to succeed; B is not designed to
refuse every possible result by requiring an A-only assumption field.

TerminalStatus order is exact: `input_refused`, `baseline_unavailable`,
`baseline_not_violated`, `model_semantics_unavailable`, `insufficient_information`,
`no_viable_hypotheses`, `no_discrimination_needed`, `no_discriminating_measurement`,
`preferred_within_supplied_set`, `tied_best_within_supplied_set`. First applicable
status wins, with independently retained axes/reasons. model_semantics_unavailable
applies to B/control public-semantic inability; insufficient_information to A
missing/unknown premises and controls still lacking supplied necessary information.
Algorithm failure, corruption or leakage triggers Gate 7, not a semantic milestone.

Refusals sort by the phase order above, then RefusalCode declaration order, then
canonical target bytes; duplicate identical refusal rows are rejected on read.
Gaps sort by GapCode declaration order, target and attempted rule. Experimental
H/T/outcomes and sets sort by ASCII label; checks sort by check_id; cells sort by
(H,T,O); topological steps sort by depth then step_id. Public lower arrays retain
owning canonical order unchanged. Preserve exact lower reasons on valid refusals.
Do not continue expensive derivation after an earlier admission stop solely to
fill later arrays; empty later arrays disclose not attempted.

## 8. Mode B isolation, population twins, and leakage oracles

B's fixed public operation inventory is `ModelQueries.behavior_declaration`,
`ModelQueries.flow_declaration`, `ModelQueries.flow_measurement_association`,
`ModelQueries.flow_operating_criterion`, `ModelQueries.transition_declaration`,
`BehaviorEvaluationQueries.behavior_evaluation`,
`ConstraintEvaluationQueries.constraint_evaluation`, and
`align_operational_evidence_with_value_compatibility`. Each dispatcher entry uses
the existing operation/owning validator and exact carried arguments; no new
public predictor is invented. Full exact record material and public support
fields may be inspected as premises through typed Ref paths. An unavailable
field is distinct from a public contract's lack of the requested semantics.

| Control | Exact delta and evidence | Expected result, not forced |
| --- | --- | --- |
| B0 public-only | Byte-identical base lower roots shared with A through independent setup, opaque H/T/O labels, no A request/digest in the process | Baseline/computational dependencies derivable; H/fault, procedures/alphabets and prediction premises unavailable. model_semantics_unavailable, unknown cells, no ranking. Compound gap only; Gates 2/3 cannot fire. |
| B1 meaning isolation | Supply approved H meanings and method/procedure/domain/outcome vocabulary and conditions as assumptions, no compatibility cells | Reattempt cells; if still unavailable, expose exact remaining rule. This is control_only, never B0 success. |
| B2 population twin | Fresh temporary world; populate every relevant existing expressible contract, including valid observed BH pair/semantic locks/same cohort; exact delta and new R; retain B1 meanings unchanged | Public BH observed comparison becomes available. If unobserved conditional prediction remains unavailable, sparsity did not close that step. No new semantic contract/prediction entered population. |
| Directed-premise control | Starting from the same B2 roots/meanings, add only source, target, condition, consequence, with no conditional table and no synthetic future observation | Gate 2 eligible only if this premise alone enables a named previously blocked derivation through an identified rule. A topology edge with no outcome consequence does not. Failure is no evidence for IN-001. |
| Conditional-rule control | Independently paired with B2, add only the explicit h,t→allowed-outcome rule and its applicability; keep other bytes unchanged | If it closes the cells, Gate 3 identifies that missing conditional rule under the supplied H/T meanings. It remains assumed/control_only. No simultaneous directed-premise addition may confound this claim. |

At least one positive population-only step must be demonstrated: before, the
existing BH declaration/locks or second observed participant needed for observed
comparison is missing; after, accepted constructors produce the complete pair,
public BH executes `equal` (or the explicitly nominated `different` twin). The
same operation, cohort, rule family and semantic unit are used. Freeze record
delta and legitimate baseline observation-production delta independently of H.
Rebuild all model-bearing roots at the after R, never mix revisions. The before
unavailable BH cannot refute a hypothesis; the after evaluated result can support
an exact current-relation check. Repeat the unobserved prediction attempt: valid
observed equality does not license a hypothetical second observation. This is
the positive existing-contract population twin and negative prediction twin.

For FM/FC sparsity, accepted constructors can populate declared relevance and
governing designation in a disposable world. Zero authoritative FMA/FCD says
nothing about contract expressiveness. Extra measured-variable registration fixes
identity availability only, not measurement method semantics. B2 records every
relevant expressible family considered, populated record IDs, attempted field and
before/after disposition. Unsupported record family, missing public field, invalid
material, population absence, semantic absence, application-only policy and actual
algorithm failure remain separate GapCodes; absence is never guessed from a name.

Executable leakage acceptance controls, all required in Slice B:

1. Run B0 in a fresh process that never loads A bytes, A digest, A fixture module,
   A expected-result fixture or A code-generation closure. Its filesystem access
   during replay is denied; input delivery is complete plain bytes before replay.
2. Freeze independent immutable setup bytes before either mode. No shared mutable
   dictionaries, caches, module globals, model instances or monkey-patched helpers
   cross A/B. Mutate A after B setup; B bytes/results remain identical.
3. Alpha-rename every H/T/outcome label and every non-semantic display/note string.
   For public records, rebuild valid IDs/revisions and lower results with public
   constructors; never edit content-bound fields in place. After inverse label
   and public-ID mapping, B semantic findings and cell relations are unchanged.
   Literal raw decoder codes in controls are semantic values, not display labels.
4. Change/invert A's compatibility matrix while keeping B request bytes and lower
   roots fixed. Require byte-identical B results/digests; B never sees A's digest.
5. Replace fixture/helper names with random neutral tokens. No B cell changes.
   Instrument dependency closure: a fixture expected value, prospective synthetic
   observation, caller compatibility assertion, unlisted rule, or name-based
   branch anywhere in a known B cell's closure is mode_leakage/input_refused.
6. Submit wrong union arms and A-only fields to B, including cost, descriptions,
   procedures, decoders and expected outcomes hidden in nested objects. Refuse
   schema_invalid before lower reconstruction; no permissive extra-field stripping.
7. Submit forged `public_derived` classification or copied A result/cell wrapped
   in otherwise valid lower objects. Recompute exact public closure; epistemic_invalid
   or mode_leakage refuses. Public validation of a synthetic observation does not
   validate a helper's right to invent its H-conditioned counterfactual value.
8. Every requested B triple has a CellResult: known cells name public premises and
   step; otherwise relation unknown, unavailable origin, exact attempted rule/path
   and missing-property category. No fallback to A; no forced expected failure.

## 9. Frozen disposable micro-world and mathematical twins

Device-neutral synthetic scalar case: one entity, two logical participant ports,
a declared logical flow, measured-actual Y, governing A with Y ≤50 inclusive,
observed Y=60.1, and admitted CN A=`violated`. Quantity/unit identities agree
across VSP/VSM/VCN/interpretation; use one explicit scalar unit, with no assertion
of installed equipment. Construct through accepted builders and temporary stores,
scripted source/binding/interpretation/temporal production and public FC/CN/EA/L.
No protected fixture is edited or used as real engineering knowledge.

Freeze actual complete disposable revision R and membership before producing
roots. R is computed from the temporary model, never the authoritative 36-record
revision or a fabricated digest. Context is exactly
`LifecycleViewContext(kind='lifecycle_view', view='as_designed')`.
Cutoff C=`2026-08-07T21:00:00+00:00`; receipt=`2026-08-07T20:00:06+00:00`;
EA horizon is `[2026-08-07T19:00:00+00:00,2026-08-07T21:00:00+00:00]`.
Source-effective time is separately disclosed. Evidence admission nominates
candidate 0 with exact occurrence, governing CRG/VCN and independent fingerprint.
No BH is used in the base; say so explicitly. No candidate measurement is run.

H1 statement: “high underlying-level / faithful baseline-channel explanation.”
H2 statement: “low underlying-level / positive baseline-channel-offset explanation.”
Toy rationale is respectively 60.1+0 and 40+20.1. Both require exact observed
Y=60.1 and CN A violated. These are level-3 supplied conjectures with level-4
assumptions, not transfer equations, exhaustive fault modes or actual causes.
Their genuinely different meanings remain even in an observationally equivalent
prediction twin. A new label alone does not create a different hypothesis.

T1 is the assumed reference-channel scalar procedure for the nominated case,
with an explicit same-unit finite-decimal domain, calibrated/available reference
method, hypothetical sampling scenario and hold assumption. Decoder: low is
(-∞,50], high is (50,+∞); each boundary and all successful values map once.
T2 is the assumed nonspecific two-code procedure; domain `{code_a,code_b}` and
literal identity decoder, with explicit applicability/availability. J1 supplies
the reference/hold conditional rule; J2 supplies the nonspecific either-code rule.
Every H, baseline expectation, method/domain/decoder/condition, cell, J and scope
has the StatementSlot/Epi/citation treatment of §5. Synthetic observation is level
1; declarations level 2; scores level 5; conditional conclusions level 6; absent
real cause, equipment availability and global completeness level 7.

| Primary cell | T1/low | T1/high | T2/code_a | T2/code_b |
| --- | --- | --- | --- | --- |
| H1 | excludes | permits | permits | permits |
| H2 | permits | excludes | permits | permits |

Exactly two hypotheses, two measurements, two outcomes each, eight explicit
primary cells. Each T1 cell cites its H and J1; each T2 cell cites its H and J2.
Both H baseline checks pass. S(T1,low)={H2}; S(T1,high)={H1}; both T2 S sets are
{H1,H2}. T1 score=1/reduction=1; T2 score=2/reduction=0. Primary/final best={T1},
secondary none, status preferred_within_supplied_set. No outcome was observed.

| Separately frozen variant | Exact input delta | Exact expected result |
| --- | --- | --- |
| Valid tied-best | T2 H1 permits only code_a, H2 only code_b; same distinct procedure | Scores 1/1; primary/final={T1,T2}, recommendation null, tied_best_within_supplied_set. Equivalent partitions disclosed, not alias-refused. |
| Incomplete | (H2,T1,low) explicitly unknown with missing justification; separate missing-triple variant removes it | insufficient_information; named unknown or missing cell; no scores or silent T2 selection. Fully justified new cell/new independent commitment is valid twin. |
| H semantic alias attack | Replace H2 semantic statement/baseline/assumption bodies with H1's, retain a different H ID and different supplier/source metadata | input_refused/semantic_alias, before minimax; valid twin restores genuinely distinct H2. Audit three-H-plus-alias example is retained as a hand counterexample (§2 RC1); four H is separately input_refused/count_exceeded under the two-H ceiling. |
| Measurement alias attack | Replace T2 with exact T1 procedure/domain/decoder/conditions under new IDs/provenance | input_refused/semantic_alias; valid twin is genuinely different code procedure with the tied partition above. |
| Indistinguishable H twin | Keep genuine H1/H2 meanings, both permit both T1 outcomes and both T2 outcomes | Scores 2/2, reduction 0, no_discriminating_measurement; disclose indistinguishable H and granularity. |
| Zero-support surprise | Add T2 raw code_c to domain and explicit outcome, excluded under both H; preserve its other four permissions | 10 cells, S(T2,code_c)=empty, scores 1/2, T1 preferred; unexplained outcome retained. If separately admitted as later observed, zero supplied survivors, no cause claim. |
| All-support other | Extend T1 abstraction with explicit successful other code in a separately declared literal-domain decoder twin {low,high,other}; both H permit other | Other branch retains two; T1 score rises from 1 to 2, no positive discrimination with unchanged T2. Domain change is explicit new approved request, not a fake decimal interval overlap. |
| One survivor | H2's CN expected verdict becomes satisfied under new exact hypothesis bytes | H2 contradicted, H1 survives; no_discrimination_needed, no score/recommendation, H1 not proven causal. |
| Zero survivors | Both require CN A satisfied while admitted A is violated | no_viable_hypotheses; both exact contradictions, no fallback, score, cause or recommendation. |
| No partition | Separately approved singleton-candidate T2 request, four cells | Each branch retains both H; score 2/reduction 0; no_discriminating_measurement. Original set is not silently reduced. |
| All-excluded row | Exclude both outcomes for one H,T | input_refused/row_all_excluded, never H elimination; valid twin permits one or both. |
| BH conflict/valid twin | In populated temporary R, valid same-cohort BH computes equal; H requirement says different / equal | Inconsistent / compatible respectively. Missing/cohort-invalid observation gives unavailable, never a fabricated contradiction. |
| Population/anti-leakage | Exact B0/B1/B2 and premise controls from §8 | Observed BH step can be closed by population; conditional prediction absence remains separately tested. Copied/hidden A premise refuses; clean B0 unknown cells are valid. |
| Hash-seed reproduction | Independent frozen runs at PYTHONHASHSEED=1,7,313 | Exact canonical request and completed-result bytes/digests identical, not merely the winning label. |

## 10. Exact tiny resource limits and preflight

Limits is a closed record with the following required fields in this order and
literal integer values. Values are experimental ceilings endorsed by audit §10,
not production capacity/latency promises. They are not copied from another subsystem.

| Field | Literal maximum |
| --- | ---: |
| max_hypotheses | 2 |
| max_measurements | 2 |
| max_outcomes_per_measurement | 3 |
| max_compatibility_cells | 12 |
| max_baseline_checks_per_hypothesis | 4 |
| max_model_record_refs_per_hypothesis | 4 |
| max_model_records | 32 |
| max_base_lower_roots | 3 |
| max_optional_bh_roots | 1 |
| max_statements | 24 |
| max_text_utf8_bytes | 512 |
| max_label_ascii_bytes | 32 |
| max_derivation_depth | 4 |
| max_json_depth | 48 |
| max_expanded_nodes | 12000 |
| max_request_bytes | 524288 |
| max_result_bytes | 786432 |
| max_generated_trace_bytes | 131072 |
| envelope_reserve_bytes | 1024 |
| max_cost | 100 |

The schema fixes these additional within-ceiling refinements: at most four direct
citations/justification refs per hypothesis/prediction/step; at most 64 derivation
steps total, depth at most four; at most 32 global Gap rows and 32 Refusal rows;
at most 16 per-cell gaps; at most 16 limitation texts; at most 16 public path
segments; experimental decimal token ≤32 bytes, cost token ≤3, label/outcome
token ≤32, field-name/path token ≤128; full-envelope decoded string token ≤16,384
UTF-8 bytes and numeric lexical token ≤128 bytes before any lower parsing. Public
schemas may be stricter. Experimental Text remains ≤512 even when the general
parser permits a larger lower token. No public proof is truncated to meet these
refinements. At-limit and one-over component checks must measure these too;
full-request node boundary evidence uses the natural witnesses in section 17.

Node accounting is additive, with three distinct measured values:

- `wire_node_count`: every object, array, scalar and object key in the canonical
  serialized request, counted once per serialized occurrence. Reference objects
  remain charged. Required cross-root public material is charged for every
  physical occurrence. Python identity, validator copies and private aliases do
  not define this tree. Root depth is 1; each container/value child adds 1.
- `resolution_charge_node_count`: for each typed `StatementSlot` reference
  occurrence, charge the complete canonically serialized resolved Statement body.
  Full owned Statements already contribute to wire count. Ordinary provenance
  `Ref`, model indices, model-record references and scalar IDs do not recursively
  expand into additional copied proof. No validator-created reconstruction copy
  is charged. A reference cannot change its body's bytes or epistemic class.
- `charged_validation_node_count = wire_node_count + resolution_charge_node_count`.

The existing `max_expanded_nodes` field bounds `charged_validation_node_count`.
If a tool uses `expanded_node_count`, that name is an exact alias for this
additive value, never replacement-expanded-tree size. Replacement accounting
is rejected: never subtract the already-counted reference object. The numerical
limit remains 12,000. The owner rejects a numerical increase. Section 17 separates
the diagnostic calibration population from the operational witness cohort;
neither 12,367, 12,415 nor the 22,845 diagnostic maximum is an authorized limit.

Multiplicity is per typed reference occurrence, not per unique Statement ID.
Bounded lookup/count caching by exact ID plus exact canonical body bytes is
allowed, but each occurrence still adds its full charge. No memoization discount
is authorized. Reject duplicate definitions, malformed/unresolved refs and
cycles before full reconstruction. Resolving a local reference never calls a
store, filesystem, network, device, clock or arbitrary expression.

Frozen preflight order, before semantic execution:

1. Enforce raw byte length.
2. Enforce shallow scalar/container cardinalities, literal Limits, mode/schema
   arms, exact built-in types, lexical token/depth bounds and duplicate keys.
   Bound actual H/T/O/cell dimensions and their product before allocating cells.
3. Count the canonical wire tree; enforce its node ceiling. Check canonical
   bytes and independent byte commitments without owning-model reconstruction.
4. Enforce reference counts, exact identifier/path shapes and unique definitions.
5. Build only the bounded carried Statement lookup needed for resolution charges
   (at most 24 definitions); do not reconstruct nested lower models here.
6. Compute deterministic resolution charges; reject malformed/unresolved refs
   and enforce the resolution-charge ceiling. No copied body expansion is needed.
7. Enforce the total charged-validation-node ceiling; prove the unchanged
   generated-trace bound and output reserve before reconstruction.
8. Only then reconstruct complete owning lower results and experimental models,
   including all exact public joins and the baseline checks in section 7.
9. Continue semantic admission and, only when separately authorized, algorithm
   execution. A failed accounting gate never enters full reconstruction.

All three node ceilings in these gates use the same existing `max_expanded_nodes`
value; there is no new independently adjustable numerical limit. Wire <= limit
and resolution charge <= limit are necessary but not sufficient: total <= limit
is mandatory. No `model_construct`, `model_copy`, serializer hook, custom mapping,
subclass, cycle, executable note or coerced Boolean bypasses this order.

Fixed typed accounting refusals retain the existing Refusal schema. Each has
phase `preflight`, epistemic `(7,unknown,unavailable,true,[])`, no `lower_reason`,
and target `Ref(protocol,preflight,[fixed field below])`. Presentation messages
are fixed strings outside the wire record, never new schema fields or payloads.

| Condition | Refusal code | Fixed target field | Fixed presentation message |
| --- | --- | --- | --- |
| Wire nodes exceed limit | nodes_exceeded | wire_node_count | Wire node limit exceeded. |
| Resolution charge exceeds limit | nodes_exceeded | resolution_charge_node_count | Resolution charge limit exceeded. |
| Total charged nodes exceed limit | nodes_exceeded | charged_validation_node_count | Charged validation node limit exceeded. |
| Malformed reference/definition | schema_invalid | reference_shape | Malformed reference. |
| Unresolved reference or cycle | schema_invalid | reference_resolution | Unresolved reference. |

These fixed targets distinguish typed errors without adding new RefusalCode
members. Never interpolate a hostile identifier, node value, exception, path or
payload fragment into an error. Hostile envelopes retain the bounded existing
RejectedEnvelopeResult framing and no echoed request.

Compute `n_H * sum(n_O(t) for t in T) ≤12` and each dimension's ceiling before
allocating cells or surviving sets; declarations of counts are not trusted.
At most eight baseline checks and four H×T predictive rows exist. B/control query
dimensions and added rule rows obey the same aggregate product. No nested base
request multiplies budgets; its records/roots/statements count once in the whole
request, and repeated lower schema proof counts every serialized occurrence.

Before reconstruction require canonical-request-size +131,072+1,024 ≤786,432.
Reserve all generated data, including B-derived meanings, trace, cells, statuses,
gates and escaping within 131,072, without copied lower roots or repeated full
assumptions. A fixed-step trace may use at most 64 steps with four bounded refs;
output refs point to once-carried typed values. The later implementation must
derive a schema-based worst-case encoded bound (including JSON escaping, indices,
gaps and rejected-envelope framing) at or below that reserve, then measure actual
output bytes before freezing. Merely citing 64 steps or a passing base size is not
a proof of the trace bound. If this cannot be proven within these exact schemas
and caps, stop as trace_bound_unproven; do not silently relax, prune or truncate.

Measure bytes/nodes/depth/steps and reconstruction time for base, BH, each legal
at-limit shape and one-over hostile counterpart. Legal at-limit input must pass
that dimension's gate while still satisfying every other semantic/aggregate bound;
over-limit inputs fail before lower/cell reconstruction. The audit's base/BH size
expectation is not a measured fact for this not-yet-built world. Any valid world
excess stops execution and reports the exact dimension; it authorizes no cap
increase, model mutation, omitted proof or architecture change.

## 11. Canonical replay, RC4 integrity, and retention mechanics

Canonical experimental JSON is UTF-8, NFC experimental text, sorted object keys,
compact separators, no trailing newline, no NaN/Infinity and fixed explicit array
orders (§7). Exact finite numbers required by lower schemas retain owning public
serialization; no custom rounding/canonicalization of lower content. Reject
duplicate keys before a JSON parser/dumper loses them. Ingress canonicalization
may ignore object insertion order only; it cannot repair lower array order,
unapproved semantics, unknown fields or lexical noncanonical scalar tokens.

Independent setup retains expected exact request bytes/digest and lower commitments
outside the submitted request. Verify them before reasoning. A substituted H
with a recomputed self-hash fails; a new approved request needs a new externally
retained commitment. B's commitment contains no A digest. These digests identify
experimental bytes only, not durable engineering identities, signatures, authority
or evidence-source authentication. Do not mint anchors for H/T, cells or steps.

RC4 sequence is mandatory: fully calculate and validate all result fields and
derivation/classification closures → verify final size → freeze immutable complete
result → serialize canonically once → SHA-256 those exact bytes → retain bytes
and expected result digest outside the submitted result. No result self-hash
field creates authority. Store canonical request and canonical result bytes and
both digests in the non-authoritative receipt/report. Exact byte bundles may be
base64 inside that report with decoded lengths/digests and a named encoding; do
not let Markdown/newlines change the canonical payload. Report framing is separate
from the per-result byte budget, but no extra execution package is implied.

On every read, preflight retained bytes, compare both independent expected
commitments, validate owning lower objects, recompute the complete experimental
result and compare exact canonical result bytes/digest. An edited result with a
new self-hash still fails the external commitment. An edited report plus its own
new hashes is not authenticated by this checksum: the reviewer must independently
retain the accepted report/commitments. Pydantic freezing alone does not establish
retention integrity. Refuse mutated cells, scores, status, classification, traces,
scope or best sets even when the request digest is unchanged.

Pure replay opens no filesystem/store/network/device, reads no clock/environment,
uses no LLM/solver and issues no acquisition. Hash-seed is an externally varied
test process setting, not result data. Setup is a separately identified temporary
scripted observation-production phase, independent of H and A truth tables.
Request/result bytes for A, B0, B1, B2 and each executed control/twin are retained;
all successful controls and bounded refusal receipts identify their source and
classification. No prediction or hypothesis is appended to model, evidence,
temporal, binding, interpretation or source ledgers, including temporary setup
ledgers as a workaround for B leakage.

## 12. Threat and acceptance matrix, including all original twins

These are future acceptance oracles, not tests implemented or executed here.
An attack that fails an earlier bounded admission gate need not exercise a later
gate; construct an independently valid within-bounds twin to exercise the later
rule. A valid twin does not obtain approval by updating its own digest.

| Case | Attack/challenge → exact expected outcome | Valid twin / retained interpretation |
| --- | --- | --- |
| T01 | Forged T1 score 0 → algorithm_mismatch/input_refused on result read | Both S rows, score 1, reduction 1, T1 unique within set |
| T02 | Call nondeterministic T2 informative → algorithm_mismatch | Overlapping S sets, score 2/reduction 0; T1 preferred |
| T03 | Select first tied ID → algorithm_mismatch | Full tied set, recommendation null; explicitly authorized complete cost may reduce only primary tie |
| T04 | Missing/unknown cell → insufficient_information, no ranking | Complete newly approved justified cell; unknown never exclusion |
| T05 | Duplicate H/T/O labels or triple → schema_invalid/cell_duplicate | Unique labels and exact cross-product |
| T06 | Forged observation/CN nested proof → lower_invalid or join_mismatch/input_refused | Complete owning F/N/E reconstruction with attached exact violated governing A |
| T07 | Mixed R/context/cutoff/occurrence → join_mismatch | Exact one-R historical request with exact binding/interpretation and cutoff is valid |
| T08 | Substitute H meaning/table and self-update digest → commitment_mismatch | New exact owner-approved bytes and independent expected commitment |
| T09 | Boolean index or non-string cost → type_invalid | Candidate integer 0; cost string 0 under authorized cost arm |
| T10 | NaN/Infinity/negative/fractional/over-100/missing/mixed-unit costs → cost_invalid or earlier lexical/type refusal | Same-unit strings 0/100, zero valid; equal costs preserve tie; no base costs |
| T11 | Hidden prior, outcome averaging or entropy → schema_invalid/algorithm_mismatch | Exact cardinality minimax, no likelihood or prior fields |
| T12 | Undeclared outcome or mismatched decoder/unit → cell_outside_domain/decoder_invalid | Exhaustive coherent low/high or literal decoder; acquisition failure is unavailable |
| T13 | Empty-support outcome claimed impossible/cause proof → epistemic_invalid | Retained empty S, unexplained flag; subsequent observation leaves no supplied H |
| T14 | One survivor called proven cause or next-test optimum → epistemic_invalid/algorithm_mismatch | no_discrimination_needed; scores/best absent |
| T15 | Zero survivor fallback H/T → algorithm_mismatch | no_viable_hypotheses with exact conflict traces; restore one H as twin |
| T16 | Global completeness or silently reduced candidate set → scope_invalid | Exact supplied set, unknown global H/T coverage; separately approved smaller set allowed |
| T17 | Hash seed/key-order affects bytes/winner → nondeterministic, Gate 7 | Exact bytes at seeds 1/7/313; lower arrays never repaired |
| T18 | Excess bytes/nodes/depth/dimensions/refs/steps, cycles/hooks → first ordered preflight refusal | Legal at-limit input, one-over rejected before reconstruction; no truncation |
| T19 | Required different contradicts admitted BH equal → H inconsistent | Required equal compatible; absent/cohort-refused BH is unknown, never fabricated future observation |
| T20 | Assumption/H/prediction relabelled observed or public → epistemic_invalid | Exact origin and citations; observed only for actual admitted occurrence |
| T21 | All-excluded h,t row → row_all_excluded/input_refused | At least one permission, including valid nondeterministic cover |
| T22 | A table/helper output/cost/description copied into B → schema_invalid or mode_leakage | B0 public closure or honest unknown; independent A success |
| T23 | Satisfied ungoverned B substitutes for governing A → join_mismatch | Exact CRG/VCN designation; separate real designation change needs complete new R/request |
| T24 | EA refusal, BH not_executed or receipt denial used as H contradiction → epistemic_invalid | baseline_unavailable with exact lower reason; valid evidence permits finite checking |
| RC1-H | Same canonical H under two IDs/different provenance → semantic_alias | Genuinely different approved H meaning; same prediction row permitted with disclosure |
| RC1-T | Same procedure/decoder with renamed labels/metadata → semantic_alias | Distinct method with equivalent prediction partition stays in full tie |
| RC1-D | Overlap/duplicate decoder regions or successful-domain gap → decoder_invalid | Disjoint exhaustive regions, each boundary mapped exactly once |
| RC2-P | Sparse fixture used to justify IN-001 → Gate 2 not_met | B2 existing-contract delta closes observed BH step; record exact new R and continuing missing prediction |
| RC2-S | B0 compound absence labelled principal prediction gap → Gate 3 inconclusive | B1/B2 H/T meanings isolated, conditional-rule-only closure proves exact missing rule |
| RC2-I | Direction/topology alone called predictor → Gate 2 not_met | Only actual enabling one-premise control with source/target/condition/consequence makes investigation eligible |
| RC3-U | Wrong request/result union arm, hidden A fields, shared mutable setup → schema_invalid/mode_leakage | Separate closed schemas, immutable independent setup and isolated B process |
| RC3-N | H/T/outcome/display/helper name controls a B prediction → mode_leakage | Alpha-renamed semantic invariance; A inversion leaves exact B bytes unchanged |
| RC3-F | Prospective synthetic observation/expected helper value/unlisted rule in B closure → mode_leakage/rule_unlisted | Genuine admitted baseline observations independent of H; every known cell public-derived |
| RC3-E | Forged derivation classification or copied result with valid-looking wrappers → epistemic_invalid/mode_leakage | Full typed public closure and output recomputation, or explicit unavailable cell |
| RC4 | Mutate completed result and update embedded/self hash → result_mutated or commitment_mismatch | External expected request/result digests plus exact bytes and recomputation on every read |
| R-IO | Replay opens file/store/network/device or runs clock/LLM → Gate 7 invalid | Complete pure carried inputs; setup separately temporary/scripted |
| R-IMPORT | Production imports/loads experiment code directly or indirectly → production_import, Gate 7 | Isolated external directory, one-way public imports, production process cannot resolve/load it |
| R-FAIL | Algorithm exception or unsupported implementation arm called missing contract → algorithm_failure, Gate 7 | Distinguish unavailable public field/family, valid model sparsity and absent semantic rule |

All original spill classifications are retained as requirements. SP01 hypothesis
to fact (runtime refusal); SP02 prediction to observation (structural separation);
SP03 computational dependency to influence (runtime origin check); SP04 influence
to causality (explicit disclosed absence of intervention semantics); SP05 within-set
to global best (runtime scope check); SP06 hidden prior (structural absence of
probability fields); SP07 silent tie-break (runtime recomputation); SP08 unknown
to false (runtime refusal); SP09 incomplete H space to complete (runtime scope);
SP10 assumptions to ledger truth (structural no-append); SP11 experimental policy
to backend (structural/import oracle); SP12 solver result to safety/health
(structural absence of solver/permission output); SP13 synthetic to real knowledge
(runtime provenance/disclosure); SP14 duplicated lower validation (owning public
validators); SP15 hidden I/O (pure replay); SP16 resource exhaustion (preflight);
SP17 nondeterminism (byte oracle); SP18 LLM proposal to accepted fact (explicit
assumed approval, no live LLM); SP19 equality to transfer (runtime rule check);
SP20 A leakage to B (RC3 executable closure, no longer merely prose); SP21 confidential
data/absolute paths (synthetic bounded content and value-free errors, disclosed
non-production confidentiality limit); SP22 refusal/zero H to evidence falsehood
(separate axes and bounded language). RC1 closes multiplicity weighting; RC4
closes result mutation after request hashing. These are design guards, not claims
that unimplemented controls already pass.

## 13. Decision gates, required evidence, and permitted recommendations

Gate names/tokens are exact. Report all seven in order. Multiple missing
prerequisites may coexist; do not force a winner unless controls exclude the
alternatives. Each met gate cites exact result/step and paired independent
request commitments in the report. A missing category is not itself an allocated
milestone. No gate authorizes implementation or changes accepted architecture.

| Gate / exact name | Required evidence before met | Permitted recommendation token and meaning |
| --- | --- | --- |
| 1 — Existing model sufficient | B0 derives H meanings, method/domain/decoder/applicability and every cell solely from public premises; complete admitted matrix, correct full reasoning answer and all integrity/leakage/refusal twins pass. Assumption controls cannot count. | `consider_bounded_reasoning_proposal`: separately owner-gated pure finite reasoning proposal for a concrete consumer; IN-001 unnecessary for this proven question. |
| 2 — Directed influence missing | After H/T semantic isolation and population exclusion, name exact absent source/target/condition/consequence. Adding only that directed premise, with no prediction table, must enable the exact blocked step through a named rule. Other missing prerequisites cannot be hidden. | `consider_exact_IN001_investigation`: investigate only that relation with separate approval; no generic influence ontology, no physical causality. |
| 3 — Conditional prediction missing | B1 supplies or publicly derives H/T meaning without cells; B2 rules out sparse existing population; exact remaining failure is h,t→allowed outcomes under explicit domain/time/applicability. Conditional-rule-only paired control closes it. B0 alone is ineligible. | `name_conditional_prediction_prerequisite`: name exact missing diagnostic/prediction rule and fault/normal-mode conditions; no relabelling as directed influence, DI or change impact. |
| 4 — Candidate-hypothesis semantics missing | Public material lacks representation/generation/validation of candidate/fault meanings; exact inspected contract inventory and B0 attempted paths disclose absence. Violated VCN, state name or opaque H ID cannot supply it. | `keep_hypotheses_request_carried`: retain assumed H; any later representation proposal needs independent justification. No causal model fact. |
| 5 — Model population missing | A named accepted contract is demonstrably expressive for the exact failed step; only valid disposable population/observation delta, no new rule, closes the identical operation in B2. Record before/after roots/R and actual successful public finding. | `use_disposable_existing_population`: temporary existing-contract population only, no authoritative append or architecture. Applies to that step, not automatically the whole reasoning question. |
| 6 — Application packaging only | Full equivalent survival/ranking answer already reproducible through existing operations, all semantic prerequisites present; missing item solely concrete invocation/policy/presentation. FC/CS/DI/CV baseline composition alone is not equivalent. | `defer_to_concrete_application_requirements`: stop redundant reasoning work; retain CV consumer prerequisites; no new wrapper/delivered-capability claim. |
| 7 — Experiment invalid or inconclusive | Any arithmetic/admission/integrity/leakage/import/determinism failure, unproven bound, invalid material, unisolated compound gap or unavailable prerequisite prevents a supported conclusion. Name exact failed oracle or missing evidence. | `stop_no_milestone_authorized`: repair only through authorized experiment scope or request exact missing authority/evidence; no architecture conclusion from implementation failure. |

For not_met/inconclusive gates 1–6, recommendation is `none`; Gate 7 uses
stop_no_milestone_authorized when met, otherwise none. Current inspection supports
Gate 4; Gates 1/2/6 are not met, Gate 3 requires isolation, Gate 5 is per-step
population-dependent. This is an inspection disposition, not invented future
execution rows. Compound insufficiency may support Gate 4 while Gate 7 records
inconclusive principal-gap attribution. A negative B0 can be an informative valid
experiment result without proving a unique successor contract.

Before any later milestone proposal, all algorithm/integrity/leakage cases must
pass; B either derives complete semantics or the ladder isolates one exact missing
contract; a concrete consumer requires the capability; population and application
policy are ruled out; an exact one-premise necessity control succeeds; physical
causality remains excluded; and a separate owner gate approves the bounded
milestone. Mode A success alone is insufficient. No future milestone is yet authorized.

## 14. Objective contribution and exact permitted conclusions

Objective 3 experiment-level success: demonstrate bounded compatibility filtering
over supplied candidate explanations without claiming actual cause. Both primary
H survive; contradiction twins reject only against named admitted finite facts;
unavailable premises remain unknown. No hypothesis generator or causal discovery
is implemented or claimed.

Objective 4 experiment-level success: demonstrate best worst-case discrimination
within a supplied candidate set without claiming global best-test selection.
Required evidence is all four primary S sets, scores 1/2, reductions 1/0, full
valid tied-best set, no-partition outcome and incomplete-prediction refusal.
No method acquisition, global utility, real availability or installed sensor follows.

Objective 7 experiment-level success: preserve exact epistemic classification
through every input, derivation and result. Unknown never becomes exclusion;
supplied hypotheses/predictions never become observations/declarations; calculated
dependencies never become engineering influence. Provenance survives mixed-level
steps and both modes/controls, with executable relabelling and leakage refusals.
This tests carried origin integrity, not source authentication or completeness.

Objectives 1/2 reuse accepted identities/topology and one admitted synthetic
governed violation, adding no topology completeness or delivered current-state
application. Objectives 5 and 6 remain open: there are no actions, physical
counterfactual/change effects, feasibility model, goals or minimum-change planner.
Contract counts, test counts and successful serialization do not close objectives.

Use the audit's exact strongest honest wording:

| Finding | Permitted sentence |
| --- | --- |
| Survivors | “These supplied candidate hypotheses are not contradicted by the admitted finite facts and supplied compatibility assumptions.” |
| Rejected H | “This supplied candidate hypothesis is inconsistent with the named admitted fact/rule at the exact path.” |
| Preferred T1 | “Within this exact admitted candidate set and complete supplied prediction relation, T1 minimizes worst-case surviving candidate count under `finite_compatibility_minimax/v1`.” |
| Tie | “These candidates tie on the primary minimax criterion; no unique preferred measurement exists under the stated policy.” |
| Incomplete | “The comparison is not determined because the named required prediction cell is unknown; no ranking follows.” |
| Zero H | “Every supplied candidate is contradicted under the admitted finite checks; the supplied hypothesis/prediction space is inadequate for this result.” |

Why means a trace of bounded consistency/rejection; explanation means a supplied
candidate account; prediction means conditional allowed outcomes with source and
applicability; best always names set, algorithm, policy and completeness. None
means actual cause, physical truth, safety, health or operating permission.

## 15. Owner-gated slices, artifact retention, and unresolved authority

The audit preserves one two-mode experiment and requires stopping after a report;
it does not mandate a conflicting slice split. The owner's requested A/B split
adds an early validation stop without adding an architectural milestone.

Experimental Slice A, only after separate owner execution authorization:

1. Prepare the exact local implementation plan and approved canonical assumptions,
   independent commitments and temporary neutral setup; verify base bounds.
2. Implement only experimental contracts, Mode A admission/filter/minimax and
   mathematical/integrity/semantic-alias tests in the temporary external directory.
3. Run all applicable mathematical/admission/hostile-bound/retention/import and
   hash-seed controls; prove trace reserve and measure base/at-limit/one-over.
4. Freeze deterministic Mode A requests/results and bounded refusal receipts,
   report objective 3/4/7 evidence and limitations. Stop for owner validation.

Experimental Slice B is eligible only after explicit Slice A acceptance:

1. Run isolated B0 derivation with no A bytes/digest in its process; implement
   executable leakage/renaming/invariance/closure controls and honest cell gaps.
2. Run B1 and B2 population-control twin, measure BH bounds and record exact R
   delta; run directed-premise control only if influence is actually suspected,
   and conditional-rule-only isolation control with exact approved assumptions.
3. Reproduce deterministic canonical B/control bytes, validate external retained
   request/result digests on every read, and compile final objective/gate evidence.
4. Stop with the execution receipt/report. Do not promote temporary code/tests into
   production, fixtures, a public package, ADR or a third slice.

The challenger-corrected retention policy is exact:

| Artifact | Retain / would commit if execution later authorized? |
| --- | --- |
| Final synthesis | Create and retain this design document now. No add/commit now. Execution authorization alone does not authorize committing this or the frozen inputs; any documentation commit needs its own authority. |
| Implementation plan | Prepare as non-authoritative temporary execution planning material when execution is authorized; summarize exact version/digest in report. No standalone committed implementation-plan package implied. |
| Experiment implementation | Disposable external driver only; do not commit, package, export or promote. The report records its experimental-byte digest and execution environment, not the driver source as a committed artifact. |
| Tests | Disposable local tests only; no repository test implementation/commit. Report exact cases, outcomes and experimental code-byte digest as reproduction evidence, not test source as a committed artifact. |
| Frozen request | Retain exact canonical A/B0/control bytes and independent expected digests inside or bundled with the non-authoritative receipt/report; no standalone authoritative fixture or ledger record. |
| Frozen result | Same report-contained/bundled exact bytes, external expected digest and every-read validation; not a durable engineering identity/result ledger. |
| Execution report | Sole execution-output commit candidate, only if separately authorized. It contains or bundles exact canonical requests/results and both digests, measurements, control evidence, limitations, gates, objectives and preservation receipt. No commit is implicit in execution approval. |

“Containing or bundling” means report data payloads, not an installed driver,
backend API, production/test package, model fixture, ledger or new contract. The
report does not bundle driver/test source as an alternative way to commit it.
Its canonical byte bundles are frozen requests/results, with external commitments.
Temporary directories stay outside authoritative model/evidence/temporal/binding/
interpretation/source stores. No authoritative model revision may change.

Only genuinely authority-dependent blockers to execution remain: explicit owner
authorization of Slice A execution, including approval of the exact canonical
H/T/method/calibration/hold/scope/prediction statements and named supplier/approver;
then separate Slice A acceptance and authorization of Slice B and its exact
additional assumption-control bytes. These are later execution gates, not reasons
to leave this design unfinished. A cost variant is excluded by default and needs
separate authorization if requested; it does not block the base. Caps, base cost
none, report-only retention and architectural non-authorizations are settled.
Separate commit permission is needed only if committing the execution report is
later requested; this task explicitly forbids all add/commit operations.

CV application requirements remain deferred application questions, not blockers
to this synthetic experiment and not reopened choices: ingress/invocation,
authentication/authorization, policy authority/version/retention, decision retention,
actor identity, confidentiality, capacity/latency, error presentation, deployment/
resource ownership and scope completeness. No value is invented for that future app.

## 16. Design-only verification and terminal boundary

Only this synthesis is written. Frozen input digests/lengths/markers, exact main
refs, no tracked changes, two authorized input exceptions, accepted load/replay,
36 records/revision, 236 exports/digest, zero FMA/FMW/FCD/FCW, protected reports/
inventories, contiguous unique ADRs and the FC-only witness have been checked.
Integrated witness and full-suite evidence retain the explicitly historical
qualification in §1. No experiment implementation, new test, model population
control or hypothetical measurement was executed during this design task.

Final acceptance of this document requires numbered sections 1–16, all 22 change
log entries, RC1–RC4 and NB1–NB4 dispositions, all eight owner adjudications, exact
marker, whitespace check including the new untracked file, and Git status containing
only the two frozen inputs plus this synthesis. No branch, add, commit, ADR-0023
allocation, fixture/ledger mutation, push, merge or history operation occurs.
ADR-0023 remains absent, unallocated and unreserved. Stop after the terminal receipt.

## 17. Accepted experiment redesign and exact preexecution gates

This normative amendment implements the owner-accepted
[redesign audit](../reports/2026-09-11-brc-exp001-slice-a-experiment-redesign-proposal-challenger-audit.md),
SHA-256 `e4d7b6b2aea52e949eb322067d4c6660c3268afb415501e9585761725dfb93ea`.
The [frozen redesign proposal](../proposals/2026-09-11-brc-exp001-slice-a-experiment-redesign-proposal.md)
remains unchanged at `ec4f818c42ce8e67c10c0d2564ac54fdf4e66fd7ebdc8ec01e30306f18119012`.
The [correction report](../reports/2026-09-11-brc-exp001-slice-a-experiment-redesign-correction-report.md)
records old/new document commitments and the exact reconciliation.
This section supersedes the proposal's unconditional full-universe barrier and
prospective cap-amendment rule. It changes neither public contracts nor the
Mode A algorithm, assumption ladder, primary bytes, cost policy or numerical caps.

### 17.1 Independent proof boundaries, not a smaller truth claim by omission

The following partition is exhaustive and unique over E01–E32:

| Class | IDs | Count | Required boundary |
| --- | --- | ---: | --- |
| slice_a_required | E01–E17, E26–E28, E30–E32 | 23 | Slice A acceptance, with every applicable guard below |
| slice_b_required | E18–E21, E23–E25 | 7 | Separately approved and executed Slice B |
| cross_slice_closeout_required | E22 | 1 | Combined A/B closeout only |
| resource_refusal_only | E29 | 1 | Separate Slice A resource guard, never semantic-success evidence |

Missing B0/B1/B2/conditional-rule premises and unproved E22 cannot block Slice A
acceptance. They do block corresponding B and combined claims. A-side wrong-arm,
field-leakage, import and epistemic guards remain immediate under E27/E32;
stage separation does not excuse them. Slice B remains unproved, unapproved,
and dependent on separately versioned complete premises and its own owner gates.
No successor milestone follows from Slice A, and no Slice C is authorized.

Successful A is bounded compatibility/minimax correctness over explicitly supplied
H/T/outcome/prediction premises, not derivation or accuracy of those premises.
Objective 3 receives conditional finite-account filtering, not actual cause;
objective 4 receives within-supplied-set worst-case discrimination, not global
best-test selection; objective 7 receives exact carried assumption/computation
classification, not source authentication. Objectives 1/2 only reuse existing
synthetic public evidence; 5/6 remain open. All seven dispositions in section 14
and audit section 11 remain binding. The supplied-versus-publicly-derived premise
question remains open after A. None of IN-001, CI-001, diagnosis, prediction,
influence, change impact, planning, control or an application is preselected.

### 17.2 Three preserved corpus roles and exact selection

`diagnostic_calibration_corpus` is the unchanged 250 structurally complete typed
requests retained in the continuation archive and proposal matrix. It is not
the population of operationally admissible Slice A requests. All 250 costs,
contents and commitments remain evidence, including the 22,845 maximum and the
22,821 complete-known maximum. The archived missing-cell control stays outside
those maxima but remains an A negative control.

`resource_refusal_corpus` includes all 218 archived requests above 12,000,
with their identities/costs and intended preflight refusal retained. Refusal
does not prove a semantic model gap or operational algorithm success.
`operational_witness_cohort` is the minimal input-support basis selected below,
plus a separately identified acceptance register: the seven basis requests
are not a replacement for all applicable A positive/negative oracles. These
corpus roles overlap; choosing a witness neither deletes the omitted 243 rows
nor calls every omitted sublimit row invalid. No cost-based cherry-picking of
unique semantic obligations is allowed.

For the frozen support matrix, seven disjoint necessary groups are E01, E02,
E04, E05, E07, E08 and E09, with 10/1/2/114/1/1/1 candidate rows. Enumerate all
2,280 seven-way combinations without filtering by cost. Recompute coverage
from the exact projection/check/relation predicates in proposal section 4.
An independent bit-mask set-union dynamic program must reproduce the minimum;
at the forced 7,680 threshold it minimizes (cardinality, aggregate charge).
No six-request cover exists. The optimum is seven, maximum 7,680, sum 50,738.
This establishes input support for 15 columns, not execution of 23 obligations.

All six minimum cohorts remain disclosed. Let
K={all_other,one_viable,tied,unknown_single,zero_viable}:

| Historical tie | Add to K | Continuity disposition |
| --- | --- | --- |
| C1 | closure_base_000000, different_outcomes | Does not nominate the approved primary role or isolated surprise role |
| C2 | closure_base_000000, surprise | Same selected complete bytes; retain the archival primary alias |
| C3 | nondeterministic, different_outcomes | Does not nominate the approved primary role or isolated surprise role |
| C4 | nondeterministic, surprise | Same selected complete bytes; retain the archival primary alias |
| C5 | primary, different_outcomes | Distinct provenance bytes for the extension, not the isolated surprise role |
| C6 | primary, surprise | Present the approved primary role explicitly; exact bytes equal C2/C4 |

The three primary-role aliases are literally identical bytes, not inferior
semantic candidates. The two extension variants differ in 14 Statement bodies,
not mathematics. There are six case-level ties and two byte-level choices.
Continuity selects experimental roles fixed by prior approval and the isolated
surprise control, never filenames, spelling, enumeration, IDs, time or hashes.
Require equality to the approved primary bytes, not an archival filename match.
C2/C4/C6 are one exact seven-request byte cohort under this condition, with
three archival aliases preserved, not three different semantic choices. Naming
its unchanged approved request primary is display/traceability, not an ID-based
winner. Do not quotient distinct bytes merely because their scores might agree.
Within cohorts containing both exact roles and covering the A acceptance register,
minimize maximum charge, aggregate charge, then new assumption variants. Preserve
any remaining tie and stop for owner direction. Do not execute all six.
Canonical case-ID ordering is presentation only.

Primary complete request SHA-256 remains
`67fe5d164251fdc6d8ba577e90660b0c486ea626af0a1faccac5362481f188c1`
(94,819 bytes); its exact projection remains
`4c5e48452ee81a5c65cef2a51dcae8de56262684e7056be429dd6166788241dc`
(29,153 bytes). Historical approval metadata is not rewritten. Every other
projection is a candidate version requiring independent exact-byte owner approval.
Owner approval never promotes levels 3/4 to observed or declared engineering truth.

### 17.3 Complete A acceptance register, including missing controls

The cohort manifest must contain one ordered entry for each of the following
23 obligations. For each guard record its exact complete parent commitment,
mutation/construction and independent expected commitment, expected phase/code,
resource treatment, owner authority and later actual result. Candidate preparation
may mark an execution-only oracle not_run; it may never mark it passed from a
positive parent, byte counting or public-only reconstruction. A missing exact
input or proof remains an explicit gate, not an omitted case.

| ID | Frozen input support and mandatory acceptance oracle |
| --- | --- |
| E01 | Exact approved primary; independent all-branch mathematical oracle and forged score/step refusal; retain later exact result externally |
| E02 | tied; both distinct procedures remain in the full best set; select-first mutation refused |
| E03 | Primary overlapping permits; no probability, exclusive-partition or outcome-average substitution |
| E04 | Isolated surprise; explicit unsupported successful branch is unexplained, never impossible/cause proof |
| E05 | unknown_single at H1/T1/high; unknown remains level 7; also unknown in a contradicted H and required-baseline-unknown precedence |
| E06 | Archived missing_cell plus exact primary restoration; cell_missing differs from cell_unknown; no imputation |
| E07 | all_other; explicit successful other is not unavailable input and must retain both H permissions |
| E08 | one_viable; no_discrimination_needed with absent scores/best, never proven cause |
| E09 | zero_viable; no_viable_hypotheses with conflicts, no invented fallback or evidence-falsehood claim |
| E10 | all_other plus no_partition; no positive recommendation when reduction is zero; do not confuse singleton T with a useful discriminator |
| E11 | tied positive; exact aliased procedure/decoder with renamed IDs/provenance refused semantic_alias; owner paraphrase/granularity admission retained |
| E12 | Primary unique product; duplicated identical and conflicting triples refused cell_duplicate before reconstruction of a comparison |
| E13 | indistinguishable positive retained at 7,130; distinct meanings with identical rows disclosed; same canonical H meaning under new ID/provenance refused semantic_alias |
| E14 | Complete primary and outcome-extension decoders; overlap, gap, duplicate region, unit mismatch, empty vocabulary and outside-domain success refused decoder_invalid/cell_outside_domain |
| E15 | one_supplied and unique primary positive; empty H/T and duplicate H/T/O identities refused; strict Boolean/integer distinction retained |
| E16 | Full F/N/E owning reconstruction, exact governed CN/observation and alignment; satisfied governing baseline is baseline_not_violated, not a changed expected H verdict |
| E17 | Forged nested roots, mixed R/context/cutoff/occurrence/fingerprint and ungoverned substitution refused lower_invalid/join_mismatch; BH/current-record integration below remains required |
| E26 | Every premise and later calculation/conclusion preserves the seven-level ladder and transitive supplied dependency closure |
| E27 | A closed arm, no B fields; prior/cost insertion, cause/global-best, unknown-as-false and assumed-as-observed/public relabelling refused at the exact first applicable gate |
| E28 | Every stage preserves complete lower contents/joins and original provenance/citation IDs; external request substitution refused even after self-hash update |
| E30 | Seeds 1/7/313, two independent roots and reversed permissible construction order; compare canonical complete requests and later results/steps/classifications, not just scores |
| E31 | Full RC4: actual validated result/size then freeze; external independent expected request/result commitments; mutate every result class and recompute on every read |
| E32 | Disposable one-way public imports, production reachability rejection, pure no-I/O/store/network/device/clock/LLM validation; exceptions stay algorithm_failure, never missing semantics |

Additional applicable guards attach to these entries rather than disappearing
outside the seven basis inputs: all-excluded h/t row → row_all_excluded; denied
or unknown applicability/availability/calibration/hold → candidate_unavailable;
valid required lower refusal or absent BH → unavailable, never H contradiction;
hostile duplicate-locator carriage → input_refused under section 18, never unavailable;
strict fields/unions/indices/numerics/unauthorized costs; trace/step/depth/output
reserves and fixed non-echo error ordering; scope and granularity disclosure.
Input attacks need independent intended-attack commitments so stale hashes or
earlier resource failures cannot masquerade as the targeted semantic rejection.
Positive cost-ranking variants remain separately unauthorized and nonblocking.

T19 BH/current-record integration is an A obligation, not B2 or mere resource
stress. Its proposed bounded witness retains both H, four checks/H and the
entire 23-record F/N/E/BH proof, but nominates only T2 in a separately versioned
full request. Equal/different expectations and unavailable BH handling need
their own exact candidate bytes and rehearsal. Deleting unused T1 predictions
and justification in this separately scoped request is not a runtime projection
of the approved primary; that primary never changes. No lower field, evidence
boundary or owning validator may be removed. If this cannot be fully prepared
under 12,000, stop the corresponding A acceptance claim for an explicit owner
scope decision. No unmeasured symbolic 11,567 estimate is execution evidence.

### 17.4 Operational capacity and natural boundary evidence

`M_A_support = 7680` is established for the seven-request support cohort.
`M_A_complete` is the maximum charged count among all complete, operationally
admitted input parents in the finally frozen A cohort/acceptance-guard register,
including a successful under-limit resource guard and complete BH integration
parents. Expected resource-refused inputs do not enter that maximum. It remains
pending until all required input parents and guards are frozen and counted;
neither a seven-input maximum nor future trace/result bytes alone establish it.
Unprepared valid lower-refusal/satisfied-baseline or integration arms must be
identified explicitly, with no premature full-acceptance bound claim.

Before any future capacity claim, test coverage/coherence feasibility at 12,000
independently of request count. A minimum-cardinality cover requiring a larger
individual request is not proof that a larger sublimit cover cannot suffice.
Only after feasibility may economical execution be optimized. The owner retains
12,000 operational and 16,384 safety limits, rejecting an increase. Existing
carrier failure or speculative future controls justify no amendment.

Replace the artificial exact-12,000 full-request requirement by the greatest
naturally reachable complete semantically admissible request at or below 12,000,
and the least naturally reachable structurally complete request above it, in
the explicitly committed boundary-search population. Distinguish a finite-corpus
extremum from a schema-wide attainability theorem. Preserve all tied natural
counts, their contents and any semantic criterion used to nominate a guard.
Do not add padding, irrelevant fields, strings or meaningless structure to hit
a target. The historical 7,783 complete-typed requests have unknown predictions;
they cannot be described as semantically admitted matrices. Record them unchanged
as diagnostic/unavailability evidence, not silently substituted under-limit success.

The over-limit guard must refuse before any owning reconstruction: raw bytes,
shallow types/cardinalities/aggregate product, W, reference shape, bounded lookup,
R, total C=W+R, then reconstruction only if every resource gate passes. Preserve
section 10's exact fixed typed error and value-free presentation. Record W, R,
C and zero owning calls. A separate inclusive comparator component guard uses
12,000 and 12,001 as integer inputs, never padded requests. Retain aggregate
product, token/byte/depth/reference/trace boundaries and all refusal ordering.
Natural request witnesses do not replace this numerical comparator proof.

### 17.5 Complete stage commitments, retention and current stop

Each A semantic/guard, resource-refusal and later B/control stage receives its
entire canonical input and exact public proofs, and reconstructs all owning
results. A digest or projected scalar cannot replace the proof. An outer report
binds independently retained request/result commitments, obligation/register
version, invariant full subobjects and allowed differences. Check exact R,
membership, context, cutoff, occurrence, governing declaration, fingerprint,
binding/interpretation and any separately approved population delta. No
simultaneously necessary evidence may be omitted by splitting stages. B0 must
never load A bytes, digest or helper; its later gate stays separate.

The current authority permits one documentation-only commit containing the frozen
redesign proposal, frozen redesign audit, amended synthesis, amended Slice A plan
and redesign correction report. Subject:
`docs: redesign BRC-EXP-001 Slice A experiment`. Preserve all older owner-gate
artifacts. Newly prepared operational-cohort JSON/manifest, resource-guards
JSON/manifest and redesigned-preexecution rehearsal report stay untracked for
exact owner approval. Canonical JSON is compact sorted-key UTF-8 with no trailing
newline. These are non-authoritative experiment review data, not production
fixtures, executable packages, durable identities or accepted results.

Preparation may use disposable public-reconstruction/counting/commitment tools,
then remove them. It must not filter H, calculate minimax rankings/preferences,
produce an accepted result, implement Mode B or begin a successor milestone.
Input support, structural/semantic inspection and lower-owning reconstruction
are reported separately from future algorithm, trace/output and result-read
oracles. No earlier incomplete execution report is amended or relabelled complete.
The next owner gate is exact cohort/guard/new-assumption approval and explicit
release of the A execution stop, subject to every outstanding A admission and
acceptance condition. After eventual A acceptance, B requires separate premise
preparation and execution approval. No push, merge or history rewrite is authorized.

## 18. Owner-corrected baseline-specific multiple-match gate

This section supersedes any earlier requirement for an honest producer-generated
multiple-match parent on the selected baseline path. It does not remove the
public `multiple_matching_candidates` vocabulary or declare it universally
unreachable. No Mode B conclusion follows. A future accepted producer path
making honest multiple matching reachable needs new evidence and its own owner gate.

On baseline `af16e925a2df80f84d5cdf5c1c6e97cf3172fea0`, public
BindingResolver.declared_property_locators groups assertions by the exact tuple
`(source_id, adapter_id, subject_identifier, extraction_route, item_key, json_pointer)`.
It emits one locator per key. ModelStateQueries.variable_state emits one candidate
per locator (or one explicit-selector candidate); the value-compatibility producer
preserves that cardinality. Alignment filters by exactly the same six fields.
Thus at most one producer-generated candidate can exactly match the selected scope.
Reproduce this invariant independently through public production and a separate
key-set oracle; do not infer it merely from a test helper or fabricate discovery.

The replacement is an adversarial carried-input control: duplicate a complete
consumer candidate and its corresponding state row, with internally adjusted
declared count/selection and fresh lower commitment, so stale-digest detection
does not mask the intended integrity distinction. Preserve complete hostile input
bytes and original provenance as hostile content; never call this a produced
observation or accept its `not_aligned / multiple_matching_candidates /
multiple_matches` disclosure as an engineering conclusion. Do not modify a
producer or its deduplication. The nearest valid twin has one exact match from
the selected producer and passes complete public reconstruction and exact joins.

After all bounded preflight and commitment checks, reconstruct the complete
owning lower results, then enforce selected-path input coherence before baseline
assessment or minimax. Require distinct six-field keys in the carried N
semantic_compatibility.value_compatibility.state.candidates and exact paired
state_candidate correspondence in value_compatibility.candidates. Check matching
declared counts/selection under the selected producer path; compare complete
occurrence, R, cutoff, context, binding/interpretation and governing identities.
No filesystem/store lookup is allowed in this final validation. Public model
round-trip alone is insufficient: existing lower validators can represent the
defensive duplicated shape. The experimental coherence gate supplies the required
rejection without changing lower contracts or globally banning valid public arms.

For the isolated duplicate with otherwise valid complete lower material, the
ordered issue list is exactly one refusal: phase `lower_validation`, code
`join_mismatch`, target `Ref(space=public,root=N,path=[semantic_compatibility,
value_compatibility,state,candidates])`, lower_reason absent, epistemic level 7 /
unknown / unavailable. Fixed presentation: `Carried input violates the selected
producer invariant.` No hostile value is interpolated. Earlier malformed/schema,
resource, commitment or owning-lower failures retain section 7's ordering and
codes and must be tested independently, not relabelled as this isolated case.
Terminal status is `input_refused`, not criterion/baseline unavailable; no
successful scores, preference or successful trace conclusions may accompany it.
Raw hostile lower status/reason is retained only in bounded forensic metadata.

E16/E17 retain the lower admission/integrity obligation; E28 retains complete
provenance/coherence. All 23 A obligations remain, and all 40 frozen negative
recipes remain unchanged. Register this additional hostile control and its
positive twin separately; it does not overwrite or silently renumber the 40.
The remaining honest parents are a complete satisfied governing baseline and
a complete EA refusal with its exact retained reason and supporting inputs.
Any new assumptions for these parents require separately versioned candidate
bytes and owner approval before inclusion. M_A_complete remains pending until
all admitted parents/twins and the admitted natural guard are counted. Expected
reconstruction refusals are excluded from that maximum, not from resource tests.

The owner authorizes a documentation-only checkpoint for this correction,
followed by final preexecution preparation only. Preserve the not-ready report
byte-for-byte as the multiple-match-discrepancy report. Commit only this synthesis,
the amended plan, that discrepancy report and the gate-correction report under
`docs: correct BRC-EXP-001 multiple-match control`. Candidate parents, oracles,
manifests and the replacement final closure report remain untracked. Neither
minimax nor Mode B is authorized; 12,000/16,384 caps and all other contracts remain.

END OF BRC-EXP-001 CORRECTED FINAL SYNTHESIS
