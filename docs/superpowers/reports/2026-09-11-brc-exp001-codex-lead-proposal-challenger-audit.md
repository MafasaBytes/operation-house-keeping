# BRC-EXP-001 Codex Lead Proposal — Independent Challenger Audit

Date: 2026-09-11. Scope: adversarial soundness audit of an experimental
design. This report does not authorize implementation or propose a new model
contract.

## 1. Verdict

`approve_with_corrections`

The disposable two-mode spike is the smallest useful category of experiment
for the three stated questions. Mode A can establish that a bounded finite
compatibility algorithm behaves correctly over supplied premises. Mode B can
test whether accepted public contracts supply those premises. A handwritten
table or isolated minimax unit test cannot test that architectural boundary,
while a diagnostic engine, SAT/SMT solver, or probabilistic system would add
machinery without adding missing semantics.

The proposal is not sound enough to execute unchanged. Four corrections are
required: exact semantic aliases can weight survivor counts; the current Mode B
probe cannot isolate prediction semantics from missing hypothesis/measurement
semantics; hidden fixture assumptions need an executable leakage oracle; and
the envelope binds the request but does not bind the completed result. These
are correctable without a new durable contract or a larger inference engine.

| Severity | Count |
| --- | ---: |
| Blocking | 0 |
| Required correction | 4 |
| Non-blocking observation | 4 |

No correction authorizes a backend milestone, an authoritative append, or
ADR-0023.

## 2. Findings

### RC-1 — Different labels can conceal duplicate hypotheses and alter minimax

The proposal rejects duplicate labels and duplicate cells, but it does not
reject exact semantic aliases under different labels. Survivor cardinality
counts list members. Therefore aliases behave like implicit multiplicity
weights even though `prior=none`.

A concrete counterexample uses three deterministic hypotheses A, B, C and two
binary tests. T1 has branches `{A,B}` and `{C}`; T2 has `{A}` and `{B,C}`.
Both scores are 2. Add `A_alias` with byte-identical hypothesis content,
provenance, baseline assertions, and prediction row. T1 becomes 3 while T2
remains 2, changing a tie into a T2 preference without new engineering
knowledge.

Required correction: define the counting unit and canonical semantic content.
Reject hypotheses with the same canonical statement, baseline requirements,
and assumption body under different labels, even when their provenance metadata
differs; provenance does not create a new semantic candidate. Reject or collapse
exact duplicate measurement procedure/decoder definitions, and reject duplicate
or overlapping decoder regions that let one successful raw result map to more
than one outcome. Distinct hypotheses with the same prediction row may remain
distinct only when their hypothesis statements are genuinely different; report
them as observationally indistinguishable within the supplied candidate set and
disclose that scores depend on supplied hypothesis granularity. Stable
identifiers remain presentation keys, not weights.

### RC-2 — Mode B cannot yet identify the principal missing prerequisite

The main Mode B request removes the meanings of H1/H2 and the procedure,
alphabet, and predictive meaning of T1/T2. It can therefore correctly find a
compound absence: hypothesis semantics, measurement semantics, and conditional
prediction semantics are all unavailable. It cannot then identify conditional
prediction semantics as the principal blocker, nor decide whether directed
influence is needed. The single terminal status
`model_semantics_unavailable` does not distinguish those causes.

Required correction: add a labelled diagnostic assumption ladder outside the
public-only Mode B success path:

1. Run B0 with only public roots and opaque query labels. It may report the
   compound missing prerequisites but cannot pass Gate 2 or Gate 3.
2. Run B1 with hypothesis meanings and measurement procedure/outcome vocabulary
   explicitly supplied as assumptions, but with no compatibility cells. This
   is an isolation control, not Mode B success. Attempt public derivation of the
   cells again.
3. Run B2 with every relevant *existing* expressible public contract populated,
   including the valid observed BH pair. An unchanged inability to predict an
   unobserved outcome distinguishes absent contract semantics from sparse
   population.
4. If influence is suspected, add only the exact proposed directed-relation
   premise in a separately labelled control. Gate 2 is eligible only if that
   premise, without a supplied prediction table, enables the blocked derivation.
   If it does not, the result is not evidence for IN-001.
5. Add only an explicit conditional allowed-outcome rule in the final control.
   If that closes the cells, Gate 3 has an identified missing rule. Success in
   any assumption-bearing control is never Mode B success.

Alternatively, narrow the design's result to “the current public model does
not derive the requested matrix; multiple prerequisite categories are absent.”
It must not call prediction semantics the principal gap without the controls.

### RC-3 — The proposed mode boundary needs an executable leakage oracle

A leakage implementation can pass superficial checks by placing
`expected_reference_outcome(h)` in a fixture helper, naming variables
`high_underlying` and `offset`, creating prospective observations per
hypothesis, or hard-coding H1/T1 outcomes in the B driver. The resulting values
can be wrapped in valid-looking setup objects even though no public contract
derives the counterfactual. That is a failed experiment.

Required correction: use distinct mode-specific envelope schemas. Mode B must
not contain Mode A hypothesis descriptions, justifications, procedures,
decoders, costs, compatibility cells, or expected outcomes. Its premise
allowlist may contain only exact public roots, independently retained lower
commitments, opaque local query labels, and the public rule identifier being
attempted. Every non-`unknown` B cell must reconstruct from those premises.

Add these executable oracles:

- Run B in a process that never loads the Mode A request or its digest.
- Alpha-rename every H/T/outcome label and every non-semantic display/note
  string. B's semantic result must remain unchanged.
- Change or invert the A matrix while keeping B bytes and lower roots fixed.
  B bytes must remain identical.
- Replace fixture/helper names with random neutral tokens. Names cannot affect
  a B cell.
- Reject any B derivation whose dependency closure reaches a fixture expected
  value, prospective synthetic observation, caller compatibility assertion, or
  unlisted rule.

### RC-4 — Canonical request hashing does not protect a retained result

The proposal specifies a mode-specific request digest and complete replay, but
no canonical completed-result digest or independently retained expected result
commitment. A result mutated after its request digest was calculated is not
detected by that digest. Replay can discover the mutation only if replay is
actually invoked and the expected result bytes are independently known.

Required correction: freeze the complete result only after all derivation and
size checks; serialize it canonically once; calculate a result SHA-256 over
those exact bytes; retain the exact request bytes, result bytes, and both
digests in the experiment report; and validate/recompute on every read. The
expected result digest must be retained outside the submitted result. A
self-updated result hash is no more authoritative than the already-rejected
self-updated request hash. This checksum remains reproducibility evidence, not
a signature or durable engineering identity.

### NBO-1 — The base arithmetic and possibilistic minimax rule are correct

The main 2×2×2 example and its ranking recompute exactly. No probability is
needed or authorized. The rule is sound for its stated within-set objective
after the admissibility conditions in section 4 and RC-1.

### NBO-2 — The edge variants are algorithm controls, not architectural proof

The tie, incomplete, one-survivor, zero-survivor, and BH-conflict variants test
important refusal and language behavior. They remain elementary. Architectural
evidence comes only from a non-leaking Mode B and the diagnostic controls in
RC-2.

### NBO-3 — The proposed limits are experimental ceilings

The finite limits are conservative and preflightable. They have not been
measured against the proposed world and are not production capacity or latency
claims. At-limit and one-over measurements remain a mandatory execution gate.

### NBO-4 — The accepted baseline witnesses remain synthetic evidence

The live FC and integrated witnesses reproduce exactly, but they prove public
contract composition in disposable worlds. They do not validate H1/H2, T1/T2,
physical causality, or real printer knowledge.

## 3. Frozen proposal and baseline verification

The proposal checkpoint matched before this report was written.

| Proposal checkpoint | Verified value | Result |
| --- | --- | --- |
| Path | `docs/superpowers/proposals/2026-09-11-brc-exp001-codex-lead-proposal.md` | match |
| Lines | 740 | match |
| Bytes | 64,770 | match |
| SHA-256 | `0c830c433674eac130c2c01cb337a4e474eba5d2fa88fc72269e6de656a2bfeb` | match |
| Numbered sections | 16 | match |
| Ending marker | `END OF BRC-EXP-001 CODEX LEAD PROPOSAL` | match |

The repository baseline was independently checked, not copied from the
proposal.

| Baseline item | Independent result |
| --- | --- |
| Branch | `main` |
| `HEAD` | `debcffec5a77ae270bbf8822f82ef1aa7556c5bd` |
| `origin/main` | `debcffec5a77ae270bbf8822f82ef1aa7556c5bd` |
| FC | Complete and owner accepted; final acceptance digest matches below |
| CS | Closed without implementation as commissioning application policy |
| DI | Closed without implementation as bounded application composition |
| CV | Backend additions cancelled; application delivery deferred pending concrete requirements |
| Authoritative model | 36 records; live `ModelStore.load()` succeeded |
| Accepted revision | `mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee` |
| Replay | Exact current record-ID membership replays to the same revision |
| Model-kernel exports | 236 ordered and 236 unique |
| Ordered export digest | `77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252` |
| FMA/FMW | `0/0` |
| FCD/FCW | `0/0` |
| ADRs | Exactly one filename for each 0001–0022; contiguous and unique |
| ADR-0023 | Absent, unallocated, and unreserved |
| Complete verification accounting | Historical split evidence: 4,073 suite passes plus the separately permitted loopback pass = 4,074; not rerun here |

Protected decision and verification records were hashed from live bytes:

| Protected record | Bytes | SHA-256 |
| --- | ---: | --- |
| DI owner decision | 13,298 | `ca5413a558ec5512c34845715fc1c63a8b403f31f0ccf5e505c8e2eb081bfaa0` |
| CV owner decision | 10,030 | `7960868e4367e112f7d7dcb275d344ec7e95337be67f29ee9d8cb57d2e7a97bb` |
| CS owner decision | 9,153 | `8557f2252c226b43dabc17ae4ffc5b8a529ac3d26999a456495e6b21c2ad33e3` |
| Post-FC reconciliation | 56,663 | `9593532154632d7cabac8e67db3c0a63d22f677858a973bb26cec14b83a06dd5` |
| FC final acceptance | 2,129 | `1436b12aff7ad6b387a58bba0ea7d87386fffd14c151d5ad76b06384a7529ca8` |
| FC final verification | 17,525 | `eb67c0830ac54c3caac9a8763afd0e84484edc8f7f900fd6391f137d5a9eec71` |

The protected sorted pathname-to-file-digest inventories also match:

| Tree | Files | SHA-256 |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| `var/raw_store` | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

The FC-only witness reproduced from current public code at exactly 14,677
bytes and SHA-256
`a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca`.
The six-result integrated witness reproduced at exactly 174,490 bytes and
SHA-256
`1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e`.
It again showed applicable governing A, A violated, ungoverned B satisfied,
complete evidence, attached matched alignment, a satisfied-A CN twin, and
unchanged FC across that twin.

## 4. Mathematical audit

For H = `{H1,H2}` the supplied matrix has two tests, two outcomes per test,
and eight explicit compatibility cells:

| Test/outcome | Survivor set | Count |
| --- | --- | ---: |
| T1/low | `{H2}` | 1 |
| T1/high | `{H1}` | 1 |
| T2/code_a | `{H1,H2}` | 2 |
| T2/code_b | `{H1,H2}` | 2 |

Therefore `score(T1)=max(1,1)=1` and `score(T2)=max(2,2)=2`. T1
has guaranteed reduction 1 and T2 reduction 0. The stated result is exact.

The algorithm

`S(t,o) = {h in H | compatible(h,t,o)}`

and

`score(t) = max(|S(t,o)| for o in O(t))`

is sufficient for pure worst-case survivor-count discrimination only after all
of these admissibility conditions hold:

1. H contains unique canonical hypothesis definitions under an explicit
   counting/granularity policy; see RC-1.
2. Each admitted measurement has a nonempty, unique, finite outcome vocabulary
   and a total, deterministic decoder over every successful raw result in its
   declared domain. Decoder regions are disjoint. `unknown` or `other`, when a
   possible successful result, is an explicit outcome rather than a missing
   cell.
3. There is exactly one `permits`, `excludes`, or `unknown` cell per H×T×O
   member. Full ranking requires no `unknown` cell in the scored viable rows.
4. Every h,t row permits at least one outcome. Equivalently, for each admitted
   t, the union of S(t,o) over its outcomes covers H. An all-excluded row is an
   invalid predictive relation.
5. The candidate measurement identity, procedure, decoder, applicability, and
   availability are supplied or publicly derived, and the exact candidate set
   being ranked is retained. Global completeness remains unknown.

With those conditions:

| Challenge | Conclusion |
| --- | --- |
| Deterministic hypotheses | Exactly one outcome per h,t; survivor sets partition H when the decoder is exhaustive. Main T1 has this form. |
| Multiple permitted outcomes | Valid possibilistic predictions; S sets may overlap and need not partition H. Cardinality minimax remains defined without probabilities. |
| Incomplete cells | `unknown` is not exclusion. Refuse the affected full-set comparison. |
| Duplicate hypotheses/tests/outcomes | Duplicate labels/cells are already refused; RC-1 additionally requires exact semantic-alias and decoder-region controls. |
| Outcome supported by no hypothesis | Keep S empty and disclose an unexplained outcome. It participates in the formal maximum but is numerically inert because row coverage guarantees another nonempty S. If later observed, no supplied hypothesis remains. It is not “physically impossible.” |
| One viable hypothesis | No discrimination score or test recommendation; report conditional survival. |
| Zero viable hypotheses | No score, fallback, or cause. Report exact contradictions and inadequacy of the supplied set/premises. |
| Test producing no partition | Valid for nondeterministic hypotheses. If every branch retains H, reduction is zero and the test is not discriminating. Main T2 demonstrates this. |
| Equal scores | Preserve the whole primary best set. No identifier-based winner. |
| Optional cost | Only an explicitly authorized, complete, same-unit secondary policy may reduce the primary tie. It may never trade away a better minimax score. |
| Different outcome counts | The maximum does not reward extra branches by itself. Outcome granularity still must be justified by the decoder and cannot be manufactured to alter hypothesis definitions. |
| `unknown`/`other` branch | If all hypotheses permit it, it raises the worst case to `|H|`; a constructed example changes a binary perfect split from score 1 to score 2. If none permit it and it occurs, the supplied space is inadequate. |
| Impossible outcomes in maximum | Retain them for trace completeness. Empty sets cannot increase the maximum and therefore do not change the score. |
| Open-world surprise | An out-of-vocabulary successful raw result invalidates the declared outcome abstraction and ranking applicability. Acquisition failure is a separate unavailable state. Neither becomes a false compatibility cell. |
| Candidate-set incompleteness | Ranking is conditional on the exact supplied set only. No global optimum follows. |
| Stable identifier order | Presentation and canonicalization only. Marking the first tied identifier as selected would be an illicit policy and must fail. |

No prior, likelihood, entropy, expected information gain, or probability is
authorized by the matrix. None is recommended.

## 5. Epistemic audit and strongest honest language

The proposed seven-way accounting is necessary and substantially correct:

| Kind | What it may contain here | What it may not become |
| --- | --- | --- |
| Observation | Exact admitted synthetic occurrence and its evidence path | A prediction, cause, current physical truth, or real printer fact |
| Declared model fact | Exact records, pins, semantics, predicates, contexts, and lifecycle findings | Proof that reality obeys the declaration |
| Calculated result | CN/BH/EA/alignment results, baseline comparisons, S sets, and scores | A supplied fact or causal claim |
| Supplied assumption | H/T meanings, calibration/hold/availability, decoder, compatibility, cost | Observed or authoritative model knowledge |
| Inferred compatibility | Consistency under admitted facts and explicit assumptions | Truth, cause, probability, or completeness |
| Candidate hypothesis | A request-scoped conjecture under an explicit counting policy | A fault fact or generated diagnosis |
| Predicted outcome | A supplied or derived allowed-outcome relation under h,t and stated conditions | An observation or authenticated forecast |
| Unknown | Missing fact, rule, prediction, candidate, or global coverage | False, excluded, unaffected, or impossible |

Mode A proves only: “Given this supplied diagnostic matrix and admitted
baseline, `finite_compatibility_minimax/v1` produces these survivor sets and
this within-set ranking.” It does not prove that a hypothesis is real, a
prediction is correct, either hypothesis is causal, the hypothesis/candidate
sets are complete, or T1 is globally best.

Use these exact strengths of wording:

| Result | Strongest honest wording |
| --- | --- |
| Surviving hypotheses | “These supplied candidate hypotheses are not contradicted by the admitted finite facts and supplied compatibility assumptions.” |
| Rejected hypothesis | “This supplied candidate hypothesis is inconsistent with the named admitted fact/rule at the exact path.” Do not say it is false in reality. |
| Preferred measurement | “Within this exact admitted candidate set and complete supplied prediction relation, T1 minimizes worst-case surviving candidate count under `finite_compatibility_minimax/v1`.” |
| Tie | “These candidates tie on the primary minimax criterion; no unique preferred measurement exists under the stated policy.” |
| Incomplete prediction | “The comparison is not determined because the named required prediction cell is unknown; no ranking follows.” |
| No viable hypothesis | “Every supplied candidate is contradicted under the admitted finite checks; the supplied hypothesis/prediction space is inadequate for this result.” |

“Why” means a trace of bounded consistency or rejection, not mechanism or
cause. “Explanation” must be qualified as a supplied candidate account.
“Prediction” means conditional allowed outcomes, with source and applicability,
not a forecast merely implied by a name. “Best” always carries the supplied-set,
algorithm, policy, and completeness qualifiers.

## 6. Mode A/Mode B separation

Mode A may carry a complete, explicitly non-authoritative diagnostic matrix.
It tests admission, consistency, set construction, minimax, ties, refusals, and
epistemic output language. A successful Mode A says nothing about whether the
accepted engineering model can supply H, T, O, or compatibility.

Mode B must derive every non-unknown matrix element solely from accepted public
repository contracts and the exact lower roots. It must not copy or infer Mode
A cells, execute notes/names, fabricate future observations, or use caller
assumptions hidden in setup. Failure must retain the exact missing premise and
attempted public path.

The proposal states that separation correctly, but its generic envelope
description says a request retains hypothesis assertions, procedures, outcomes,
and every compatibility cell without making the A/B schema difference explicit.
RC-3 resolves that ambiguity and supplies the missing executable leakage
controls.

The constructed leakage case is decisive: a helper can generate an H-specific
future value, pass it through a valid synthetic observation pipeline, and call
the resulting CN/BH output a model prediction. The public validators can prove
that the synthetic observation was processed correctly; they cannot prove that
the helper was entitled to generate that counterfactual under h. Mode B success
based on that setup is a failed experiment.

Conclusion: Mode A and Mode B test genuinely different things only after RC-3.
Mode A algorithm success can coexist with an honest B0 compound-semantic
failure. Neither result may be relabelled as success of the other.

## 7. Existing-model derivation audit

The live contracts support the proposal's negative expectation.

| Family | Publicly available | Diagnostic limit |
| --- | --- | --- |
| BH | Unordered two-variable registration; exact numeric equality declaration; `equal`/`different` only after two admitted same-cohort observations | No input/output roles, transfer function, intervention, fault condition, or unobserved output computation. The declaration explicitly has no direction or computed outcome. |
| CN | Numeric predicate and `satisfied`/`violated`/`not_evaluated` for admitted observations | A predicate is not a predictor, severity, abnormality model, or cause. |
| ST | Registered all-of constraint region and evidence-gated match/non-match | States need not be exclusive or exhaustive; no fault-mode family or hypothesis generation. |
| FL | Logical source/sink port-group topology with explicit direction pins | Direction is declared topology, not physical influence, response magnitude, transfer, or causality. |
| FM | Exact flow/variable/participant/context/orientation relevance with support pins | No measurement acquisition procedure, availability, calibration, decoder, or diagnostic utility. |
| FC | Exact governing CRG/VCN designation and selected-model applicability | No criterion evaluation, hypothesis, future outcome, or test selection. |
| VP | Exact variable-port association | No observation relocation, sensing mechanism, influence, or prediction. |
| VS | Value shape, nullability, unit identity, observation attachment and compatibility | No quantity dynamics, measurement method, conditional outcome, or test inventory. |
| ES | Quantity/role/unit declarations and source-interpretation compatibility | Token comparison only; no ontology, conversion, fault semantics, or predictor. |
| EA and alignment | Bounded evidence selection, coverage, content assurance, and exact occurrence/cutoff/scope alignment | No future evidence, source truth, hypothesis coverage, conditional result, or candidate completeness. |
| Evidence/provenance dependencies | Exact carried record/result references and public reconstruction | Computational/support dependency is not engineering influence or causality. |

The requested derivability classification is:

| Required item | Classification | Reason |
| --- | --- | --- |
| Candidate hypotheses | Not derivable | No hypothesis-generation or candidate-diagnosis contract exists. |
| Hypothesis identity | Not derivable | H1/H2 are local request labels, not accepted anchors or records. |
| Fault or abnormality semantics | Not derivable | A violated VCN is not a fault mode, and ST/BH do not create abnormality semantics. |
| Directed computational dependencies | Publicly derivable, narrowly | Exact record/result support and calculation dependencies are public; FL/TR direction is also declared. Neither is physical influence. DI may compose only an explicitly supplied decision inventory. |
| Conditional outcome predictions | Not derivable | No public operation computes allowed T outcomes conditioned on H. |
| Measurement procedures | Not derivable | FM relevance and variable/port identity do not define a procedure. |
| Outcome vocabularies | Derivable only under explicit additional assumptions | CN/BH expose their own result enums, but T1/T2 outcome alphabets and total decoders are request-carried. |
| Applicability conditions | Derivable only under explicit additional assumptions | Public lifecycle/FC applicability is narrower than hypothesis-conditioned method availability, calibration, hold, domain, and time conditions. |
| Candidate costs | Conceptually outside the accepted model | The experiment may carry an explicit policy value; the model has no cost authority for diagnostic actions. |
| Candidate-set completeness | Conceptually outside the accepted model | No public contract claims all hypotheses or all diagnostic procedures. Global completeness remains unknown. |

Behavior declarations do not currently establish input/output computational
dependency at all; BH is unordered equality. Even a future input/output
declaration would establish only a directed computational relation unless it
also supplied an executable, total-enough rule with hypothesis, context,
domain, time, and applicability semantics. Shared entity, variable, port,
flow, context, identity, or naming supplies none of those missing premises.

## 8. Experimental-identifiability audit

| Probe | What changes is learned | Sound conclusion |
| --- | --- | --- |
| Main T1 | Low leaves H2; high leaves H1 | T1 distinguishes the two supplied rows under J1. This does not validate J1. |
| Main T2 | Either code leaves both | T2 has zero guaranteed reduction under J2. It is not generally useless outside J2. |
| Tie variant | T2 changes from overlapping permissions to a deterministic split | It nontrivially tests full tie retention and optional secondary policy, but not architecture readiness. |
| Incomplete variant | One required cell becomes unknown | It tests refusal and unknown preservation, not an ordinary probabilistic uncertainty calculation. |
| One-survivor variant | Baseline contradiction removes H2 | No next-test discrimination is needed; H1 is not proven causal. |
| Zero-survivor variant | All supplied candidates contradict the baseline | It detects inadequacy/inconsistency of the supplied finite space. It does not establish model incompleteness as the cause. |
| BH conflict | A supplied expected current relation conflicts with an admitted BH result | The candidate can be rejected on an observed-rule check. This still does not make BH a counterfactual predictor. |
| B0 public-only failure | Several meanings are absent together | Compound semantic insufficiency only; no unique architecture gate. |
| Population control | Existing expressible contracts are fully populated | Distinguishes sparse population from absent expressiveness for those contracts. |
| Assumption ladder | One missing category is supplied at a time | Distinguishes missing H/T meaning, prediction, and a genuinely necessary directed relation without calling an assumption B success. |

As written, two architectural deficiencies can produce the same Mode B status.
RC-2 is therefore required. With that correction, the experiment can expose a
precise conditional-prediction prerequisite or honestly stop at a compound
missing-semantics result. It cannot establish a need for general influence or
causal semantics unless the one-premise control proves that narrower claim.

## 9. Minimality audit

| Alternative | What it answers | Audit disposition |
| --- | --- | --- |
| Handwritten truth table | Recomputes the four S sets and 1/2 scores | Too weak: no executable admission, refusal, integrity, determinism, or model-boundary evidence. |
| Pure minimax function test | Tests finite arithmetic and most edge cases | Necessary core of Mode A, but still cannot ask whether public contracts derive the matrix. |
| Public-result integration test | Proves FC/CN/EA/alignment admission and joins | Necessary baseline, but contains no hypothesis-conditioned predictions or test ranking. |
| Corrected two-mode spike | Tests algorithm over explicit assumptions and independently probes derivability/leakage | Smallest logically useful experiment for all three questions. |
| Full model-based diagnostic engine | Adds durable vocabulary, generation, execution, and packaging before semantics are known | Premature and not minimal. |
| SAT/SMT or probabilistic inference | Adds a solver or unauthorized prior/likelihood model | Reject. Enumeration is exact at 12 cells and a solver cannot create missing meaning. |

Two hypotheses, two binary measurements, and eight main cells are enough to
show perfect versus zero guaranteed discrimination. The variants are necessary
to expose nondeterministic permissions, no partition, ties, unknown cells,
zero/one survivors, and model-rule conflict. They do not demonstrate scale,
realism, production readiness, hypothesis generation, or acquisition.

The corrected two-mode spike is therefore minimal. Without Mode B isolation
and RC-2 controls, it collapses into an elementary minimax demonstration and
does not provide useful architectural evidence.

## 10. Reproducibility and resource audit

The proposed disposable envelope carries the essential request material:
lower roots and revisions, observation and criterion paths, candidate
hypotheses and measurements, outcome vocabulary/decoder, compatibility cells,
assumptions/provenance, algorithm version, policy, limits, and scope. The result
carries checks, conflicts/unknowns, per-cell derivations, all S sets/scores,
best sets, status, epistemic labels, and limitations.

| Challenge | Audit result |
| --- | --- |
| Canonical ordering | Sorted object keys plus explicit array orders are sufficient; lower authoritative arrays must never be repaired by sorting. |
| Request digest | Complete mode-specific canonical request digest plus an external expected commitment is correct. |
| Result digest/mutation | Missing; RC-4 required. |
| Hash-seed independence | Seeds 1, 7, and 313 are appropriate deterministic checks; include exact output bytes, not only the winner. |
| Boolean coercion | Exact built-in JSON types and strict indices/cost strings refuse Booleans correctly. |
| Non-finite/negative/fractional cost | Correctly refused; cost absent under `secondary=none`. |
| Missing/duplicate cells | Exact cross-product and one-cell rule refuse them. RC-1 adds semantic alias controls. |
| Excessive matrices | Count/byte/node/depth preflight and whole-request refusal are sound. |
| Reconstruction before preflight | Outer bytes, token/depth/node/type/count checks must occur first as stated. |
| Forged nested results | Complete owning public validators and independent joins are required and sufficient for carried-result integrity, not external truth. |
| Mixed revision/context/cutoff | Exact equality across all relevant roots and independently retained commitments correctly refuses mixing. |
| Result immutability | Pydantic freezing alone is not a retention commitment; RC-4 binds final bytes. |
| Filesystem/store/network/device access | Replay is pure. Explicit setup may use temporary stores and scripted acquisition only and must be separated from reasoning. |

The exact proposed ceilings are endorsed for the spike, subject to measured
at-limit and one-over confirmation:

- 2 hypotheses; 2 candidate tests; at most 3 outcomes per test; at most 12
  compatibility cells;
- at most 4 baseline checks and 4 explicit model-record references per
  hypothesis;
- at most 32 disposable model records; 3 base lower roots plus 1 optional BH
  result;
- at most 24 assumption/justification statements, 512 UTF-8 bytes per text,
  and ASCII local labels of 1–32 bytes;
- experimental derivation depth 4; serialized JSON depth 48 and 12,000
  expanded nodes;
- request 524,288 bytes; result 786,432 bytes; generated-trace reserve 131,072
  bytes and envelope reserve 1,024 bytes;
- optional artificial cost is a complete same-unit canonical integer string
  from 0 through 100.

If the measured valid base or BH world exceeds a ceiling, the experiment stops
and reports the exact dimension. It does not silently raise a cap or prune
proof. No durable identity or authoritative record is needed for reproducible
canonical bytes and digests.

## 11. Spill audit

The classifications below assess the proposed design. Because the spike is not
implemented, “structurally prevented” and “runtime-refused” are requirements
for the future disposable driver, not claims about controls already running.

| ID | Spill | Classification | Audit |
| --- | --- | --- | --- |
| SP01 | Hypothesis promoted to fact | Runtime-refused | Per-statement labels and exact provenance must reject authoritative/observed relabelling. |
| SP02 | Prediction promoted to observation | Structurally prevented | Matrix namespace never enters evidence producers; prospective observations in B are additionally forbidden by RC-3. |
| SP03 | Computational dependency promoted to influence | Runtime-refused | Typed premise origin and bounded wording reject the promotion. |
| SP04 | Influence promoted to causality | Disclosed | No intervention semantics exist; the report must state that even a directed relation is not cause. |
| SP05 | Within-set best promoted to globally best | Runtime-refused | Exact candidate scope and unknown global completeness are mandatory. |
| SP06 | Hidden uniform prior | Structurally prevented | No probability/entropy fields or likelihood arithmetic exist in v1. |
| SP07 | Silent tie-breaking | Runtime-refused | Full primary/final sets are reconstructed; identifier order is presentation only. |
| SP08 | Unknown treated as false/incompatible | Runtime-refused | Unknown blocks affected ranking and never becomes exclusion. |
| SP09 | Incomplete hypothesis space treated as complete | Runtime-refused | Global-completeness assertions are inadmissible; supplied scope is retained. |
| SP10 | Assumptions persisted as model truth | Structurally prevented | No ledger append or kernel record for H/T/predictions is allowed. |
| SP11 | Experimental/application policy enters production/lower packages | Structurally prevented | Driver remains outside `backend`; add an import-isolation check before accepting execution. |
| SP12 | Solver output presented as safety/health | Structurally prevented | There is no solver or safety/health/permission result. |
| SP13 | Synthetic scenario presented as real printer knowledge | Runtime-refused | Neutral identifiers, exact producer provenance, and compulsory synthetic classification are required. |
| SP14 | Lower validation duplicated incorrectly | Structurally prevented | The spike invokes owning public validators and only owns the finite experimental checks. |
| SP15 | Hidden filesystem/store/network/device access | Structurally prevented | Replay accepts complete plain inputs; setup is separate, temporary, and scripted. |
| SP16 | Unbounded search/resource exhaustion | Runtime-refused | Exact preflight caps and whole-request refusal apply; no solver/graph recursion. |
| SP17 | Nondeterministic ordering | Runtime-refused | Canonical bytes across fixed hash seeds and no set-iteration selection are acceptance oracles. |
| SP18 | LLM hypothesis accepted without authority | Runtime-refused | Exact bytes require explicit experiment-owner supply/approval and remain assumed. No live LLM is used. |
| SP19 | Equality declaration treated as transfer equation | Runtime-refused | BH can compare two observations only; it cannot fill an unobserved conditional cell. |
| SP20 | Mode A assumption leaked into Mode B | Unresolved | The prose allowlist is directionally correct, but hidden helper/hard-coded leakage remains until RC-3. |
| SP21 | Confidential data/absolute paths in proof | Disclosed | Synthetic bounded input avoids the current spill. This is not a production confidentiality boundary. |
| SP22 | Refusal/zero survivors presented as evidence falsehood | Runtime-refused | Separate axes and bounded status language preserve unknown reality. |

Omission search found two real unresolved spills and two covered concerns:

| Additional spill | Classification | Disposition |
| --- | --- | --- |
| Exact semantic aliases create hidden multiplicity weighting | Unresolved | RC-1. |
| Result mutated after request digest/final calculation | Unresolved | RC-4. |
| Experiment code imported by production | Structurally prevented | Already excluded by the driver-outside-`backend` boundary; verify imports during execution. |
| Out-of-vocabulary open-world result | Runtime-refused | Refuse abstraction applicability; do not invent an `excludes` cell or call reality impossible. |

No other requested spill is omitted. Resource-limit and deterministic-ordering
failures are covered by SP16/SP17; candidate incompleteness by SP05/SP09;
fixture/naming/caller leakage by corrected SP20; and prediction/observation,
dependency/influence, influence/cause, hidden priors, synthetic truth, I/O, LLM,
and safety/health promotions by the entries above.

## 12. Decision-gate audit

| Gate | Current evidence and counterexample | Correct adjudication |
| --- | --- | --- |
| 1. Existing model sufficient | Current public contracts cannot derive H/T meanings or cells. Lower FC/CN composition is not an equivalent reasoning answer. | Not met. Require complete B derivation with RC-3 leakage oracles and no assumption-bearing control counted as success. |
| 2. Directed influence missing | A flow source/sink declaration is directed, but adding it does not yield H-conditioned T outcomes. BH direction absence alone also proves nothing. | Not met. IN-001 is justified only by the one-premise enabling control in RC-2 naming source, target, condition, and consequence. |
| 3. Conditional prediction missing | No public predictor exists, but in B0 the H/T semantic identities are also absent. Calling prediction the principal gap would skip prerequisites. | Ambiguous as written. Eligible only after B1 supplies/derives H/T meaning without cells and the remaining exact failure is the conditional allowed-outcome rule. |
| 4. Hypothesis semantics missing | The repository has no hypothesis/fault-mode representation or generator. | Met as a missing capability, but the spike may keep H request-carried. It does not authorize causal model facts. |
| 5. Model population missing | The authoritative fixture has zero FMA/FCD, but a disposable public join works. Adding BH observations can exercise equality, not prediction. | Use only where an existing contract is demonstrably expressive and a population-only delta closes the step. Sparse fixtures never authorize architecture. |
| 6. Only application packaging missing | Existing operations do not produce hypothesis survival and measurement ranking. FC/CS/DI/CV composition is not that answer. | Not met. Packaging is the answer only if a full equivalent reasoning result already exists through current operations. |

Wrong-milestone counterexamples are therefore blocked as follows:

- Missing predictions are not relabelled as missing influence. An influence
  edge that does not generate allowed outcomes fails the Gate 2 control.
- Missing hypotheses remain request assumptions or a separately justified
  representation question; they are not automatically solved with causal facts.
- Disposable population is an isolation probe, never an authoritative append
  or architecture trigger.
- Mode A success authorizes no production reasoning engine.
- Mode B success would prove only computational derivation under accepted
  declarations. It would not prove physical influence or causality.

The exact gate correction is to make B0/B1/B2 and the one-premise controls part
of the evidence table, give each missing category its own status/reason, and
prohibit Gate 2/3 conclusions when their prerequisites are absent.

## 13. Original-objective audit

| Objective | Actual contribution |
| --- | --- |
| 1. What exists/how connected? | Reuses exact public identities and declared relations; no new topology or completeness. |
| 2. Current state? | Starts from one admitted synthetic governed violation; no new physical-currentness or application delivery. |
| 3. Candidate explanations | Genuine bounded progress: retains or rejects supplied candidate accounts against admitted facts and exposes unknown premises. It does not generate explanations or determine cause. |
| 4. Next best measurement/test | Genuine bounded progress: computes best worst-case discrimination within an exact supplied set and complete relation. It does not establish global best, availability, acquisition, or real utility. |
| 5. Change impact | No closure. No action/change propagation or physical counterfactual exists. |
| 6. Minimum-change planning | No closure. No goals, actions, effects, feasibility, or optimization model exists. |
| 7. Epistemic classification | Genuine bounded progress if per-statement origin survives validation and output. It tests observation/declaration/calculation/assumption/inference/prediction/unknown separation, not source authentication. |

The experiment contributes directly only to objectives 3, 4, and 7, and even
there only at supplied-candidate spike scope. It confirms no closure for
objectives 5 or 6.

With the four corrections, this is a useful pivot from contract accumulation
to an objective-driven reasoning experiment: it asks a decision question,
keeps missing semantics visible, and can stop without allocating a contract.
It becomes contract theatre if the envelope is promoted into a durable API, if
Mode A arithmetic is advertised as architecture readiness, or if a compound
Mode B failure is used to name the next ontology without the isolation controls.

## 14. Owner-decision adjudication

| Owner decision | Adjudication | Exact disposition |
| --- | --- | --- |
| Execute the disposable spike | Endorse with correction | Execute only after RC-1 through RC-4 are incorporated in the execution plan. Stop after the receipt/report. |
| Assumption/provenance requirements | Endorse with correction | Every H statement, baseline expectation, measurement identity/procedure, total decoder, applicability/availability/calibration/hold condition, compatibility cell, candidate-scope statement, and optional cost carries a unique local statement ID, exact canonical bytes, `assumed` label, supplier, explicit approver, rationale, applicability scope, and source/justification references. Approval authorizes use, not truth. Mode B contains none of these except in separately labelled controls. |
| Measurement cost | Endorse as written | Exclude cost from the base proof. Permit only a separately authorized `minimum_cost_after_minimax` variant as a complete same-unit secondary tie policy. Never use cost outside the primary best set. |
| Tiny resource limits | Endorse with correction | Use exactly the ceilings in section 10. Acceptance requires measured base/BH/at-limit/one-over results and proof of trace reserve. Any excess stops the spike. |
| Canonical request/result retention | Endorse with correction | Retain exact canonical A, B0, and control request/result bytes plus external SHA-256 commitments in the experiment report; apply RC-4. No durable engineering identity is created. |
| Commit artifact or report only | Endorse with correction | Commit, if separately authorized, only the non-authoritative experiment receipt/report containing or bundling the exact canonical bytes and digests. Do not commit the disposable driver as a production/test package, a backend API, fixtures, ledgers, or new contracts. |
| Mode B disposable population | Endorse with correction | Permit only the B2 population control in a fresh temporary world with an exact record delta and new R. It may populate existing contracts, never compatibility cells or new semantics, and cannot count as public-only B success. |
| Success threshold for later architecture | Endorse with correction | No later milestone is authorized by this proposal or by Mode A alone. A later proposal is eligible only after all algorithm/integrity/leakage cases pass; B derives a complete matrix solely from public contracts or the assumption ladder isolates one exact missing contract; a concrete consumer requires that capability; population/application policy are ruled out; an exact one-premise necessity control succeeds; physical causality remains excluded; and a separate owner gate approves the bounded milestone. |

## 15. Final conclusions

Mathematical conclusion: the 1-versus-2 Mode A oracle is correct and finite
minimax survivor count is adequate after explicit coverage/admissibility and
semantic-alias controls. It needs no solver or probabilities.

Epistemic conclusion: Mode A ranks supplied possibilistic premises only. The
proposal mostly preserves epistemic kinds, but every “why,” “prediction,” and
“best” claim must use the bounded language in section 5.

Mode-separation conclusion: the conceptual split is right; execution is sound
only with mode-specific schemas, public-premise closure, alpha-renaming, A-matrix
invariance, and no prospective-observation/helper leakage.

Existing-model conclusion: public contracts admit the observed governed
violation and exact computational provenance, but do not derive hypothesis
identity/fault meaning, measurement procedures, or hypothesis-conditioned
outcomes. BH equality is observed comparison, not counterfactual prediction.

Experimental-identifiability conclusion: T1/T2 and the variants identify the
algorithm's behavior. B0 alone identifies only compound insufficiency. RC-2 is
required to distinguish prediction, influence, hypothesis, and population
gaps.

Minimality conclusion: the corrected two-mode spike is the smallest experiment
that can test both finite reasoning and the accepted-model boundary. A smaller
test loses the architectural question; a larger solver/engine is unjustified.

Decision-gate conclusion: Gates 1, 2, and 6 are not met; Gate 4 identifies a
real current absence; Gate 3 requires the assumption-ladder precondition; Gate
5 is allowed only as a controlled existing-contract population probe. No gate
currently justifies IN-001, CI-001, a production reasoner, or application
packaging.

Objective-contribution verdict: bounded useful progress on objectives 3, 4,
and 7; no closure of objectives 5 or 6. With corrections it is an
objective-driven pivot, not contract theatre.

## 16. Scope preservation and audit-only confirmation

ADR-0001 through ADR-0022 remain unique and contiguous. ADR-0023 is absent,
unallocated, unreserved, and not recommended for allocation by this audit.

Only this challenger-audit report was written. The frozen proposal was read
without modification. No experiment, production code, test, branch, ADR,
fixture, ledger, authoritative record, commit, push, merge, or history operation
was created or modified. Read-only verification used current public code and
disposable temporary witness worlds; no authoritative store was changed.

END OF BRC-EXP-001 CODEX LEAD PROPOSAL CHALLENGER AUDIT
