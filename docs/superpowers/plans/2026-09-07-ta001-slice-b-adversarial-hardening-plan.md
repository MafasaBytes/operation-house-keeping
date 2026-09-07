# TA-001 Slice B Adversarial-Hardening Plan

Date: 2026-09-07

Status: Slice A owner accepted; Slice B adversarial hardening and final
verification authorized; final TA-001 acceptance pending

## 1. Authority, checkpoint, and immutable boundaries

This plan executes only Slice B from the owner-corrected synthesis
`docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md`
at SHA-256
`3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`.
Slice A is owner accepted at exact tested implementation
`76738ac0d098eb59b0fec4f6970aa862528647d9`; the documentation-only Slice A
acceptance commit immediately preceding this plan is its administrative gate.

Slice B adds adversarial proof and repairs genuine defects red-first only
inside `backend.transition_assessment`. It preserves the exact ordered 28-name
public surface, public models, literals, exception vocabulary, limits, join,
fingerprint gate, carry-once rules, and bounded conclusions. Lower production
packages, fixtures, evidence, memberships, ledgers, deterministic lower bytes,
and the corrected synthesis are immutable. Any need to change one is a
discrepancy stop.

No facade, second consumer, demonstration, result artifact, occurrence model,
store, registry, cache, durable identity, connector, ambient input, write path,
or authoritative append is authorized. Every positive world is disposable.

## 2. Red-first and independent-review method

The accepted 57-test Slice A suite is the clean baseline. Architecture/join,
hostile-preflight, and test-coverage reviews run independently and read-only
before production mutation. For each genuine defect, the smallest permanent
failing test and a valid twin are committed first; the narrow production
repair is committed separately; focused and affected gates run after each
repair. Missing proof of correct behavior receives a green adversarial test
without manufacturing a defect.

Direct TA witnesses use compact disposable public lower-result worlds and
minimal validated mutations. Accepted lower tests may establish lower
lifecycle behavior, but a direct TA test must still prove the TA mapping,
gate, join, or disclosure. Private injected limits keep combinatorial tests
small; separate safe production-number probes pin every public constant.

## 3. Coverage map T01-T25

| ID | Governing clause | Current direct evidence | Required public outcome / path | Slice B red-first action |
|---|---|---|---|---|
| T01 | Sections 3, 8, 14.4 | `test_complete_matched_endpoints_execute_bounded_support` | executed bounded support via full derivation gate | retain and add full-chain assertions |
| T02 | Sections 3, 14.4 | existing negative test changes both endpoints, so from-only witness is missing | executed bounded non-support; no occurrence wording | add from-only non-match twin |
| T03 | Sections 3, 14.4 | missing direct to-only witness | executed bounded non-support | add to-only non-match twin |
| T04 | Sections 10, 14.2 | accepted lower lifecycle tests only | structured `transition_not_registered`, not admitted/executed | add direct TA mapping world |
| T05 | Sections 10, 14.2 | registered-not-declared helper reaches adjacent subject disclosure only | structured `transition_not_declared` | add exact issue/result assertion |
| T06 | Sections 3, 10 | accepted lower same-root fork tests only | structured conflict, no winner | add direct TA mapping world |
| T07 | Sections 3, 10 | accepted lower cross-root disagreement tests only | structured conflict, no winner | add direct TA mapping world |
| T08 | Sections 10, 14.2 | accepted lower withdrawn-lineage tests only | structured inactive, not executed | add direct TA mapping world |
| T09 | Sections 10, 14.2 | accepted lower superseded-pin tests only | from pin issue, not executed | add direct TA mapping world |
| T10 | Sections 10, 14.2 | accepted lower withdrawn-pin tests only | to pin issue, not executed | add direct TA mapping world |
| T11 | Sections 10, 14.3 | generic incomplete-classification test only | lower conflicted/inactive endpoint retained, not executed | add direct valid lower mapping twin |
| T12 | Sections 6, 10 | authoritative reconstruction exists; no structured anchor-world witness | `transition_anchor_mismatch`, not executed | add valid distinct request-anchor world |
| T13 | Sections 6, 10, 15 | missing direct from-state substitution witness | from-anchor plus independently applicable subject issues | add public wrong-state world and order assertion |
| T14 | Sections 6, 10, 15 | missing direct to-state substitution witness | to-anchor plus independently applicable subject issues | add symmetric public world |
| T15 | Sections 6, 10 | no direct wrong-subject-only world | distinct subject issue | add valid same-anchor/different-subject lower world |
| T16 | Sections 6, 10 | missing direct transition-context witness | context mismatch, not executed | add valid other-context result |
| T17 | Sections 6, 10 | missing direct endpoint-context witness | endpoint/global context mismatch | add from and to parametrized worlds |
| T18 | Sections 3, 6 | hostile substitution coverage is generic | valid other transition result gives anchor issue only | add exact valid substituted-result world |
| T19 | Sections 7, 14.2 | `test_equal_cutoffs_are_structured_nonexecution` | equal cutoff and exact issues | retain; assert independent admission |
| T20 | Sections 7, 14.2 | literal pinned; reversed branch has no direct test | reversed cutoff, not executed | add direct reversed world |
| T21 | Sections 7, 13 | equivalent-offset deterministic test | UTC normalization and byte equality | retain; assert normalized stored cutoffs |
| T22 | Sections 7, 9, 12 | generic non-float/schema attacks; no datetime-subclass spy | sole typed error before lower access | add naive and hostile datetime twins with access spy |
| T23 | Sections 6, 10 | equal-cutoff test incidentally yields one endpoint mismatch | exact endpoint cutoff issue | add isolated from/to cutoff substitution worlds |
| T24 | Sections 6, 10 | complete equality exists; differing valid revision world missing | model revision mismatch, not executed | add public valid divergent-revision result world |
| T25 | Sections 10, 14.3 | incomplete world covers a from non-execution incidentally | from classification-not-executed issue | add isolated direct assertion |

## 4. Coverage map T26-T49

| ID | Governing clause | Current direct evidence | Required public outcome / path | Slice B red-first action |
|---|---|---|---|---|
| T26 | Sections 10, 14.3 | missing direct to-side witness | to classification-not-executed issue | add symmetric direct world |
| T27 | Sections 10, 14.3 | no two-condition violation-plus-unknown TA world | incomplete; partial negative not reused | add disposable two-condition world |
| T28 | Sections 10, 14.3 | from-only incomplete direct test | to incomplete, no conclusion | add symmetric world |
| T29 | Sections 6, 14.1 | missing alignment test covers one-alignment truncation | sole typed error | retain and add two-condition omission witness |
| T30 | Sections 6, 14.1 | missing | duplicate alignment typed error | add duplicate-row attack |
| T31 | Sections 6, 14.1 | missing | extra unmatched alignment typed error | add foreign extra row attack |
| T32 | Sections 6, 13 | reversed collection direct test | typed error; no remap | retain; add stable error assertion |
| T33 | Sections 6, 16 | missing direct full-object substitution | typed error despite scalar resemblance | add foreign compatibility/alignment attack |
| T34 | Sections 6, 12 | missing direct shared compatibility carry-once witness | two traces cite one row; duplicate row rejects | build minimal shared public world and attack |
| T35 | Sections 8, 14.3 | lower EA refusal tests only | selection refusal retained; not executed | add direct TA refusal world |
| T36 | Sections 8, 14.5 | direct missing-fingerprint test | completeness unchanged, not executed | retain and strengthen trace/issue assertions |
| T37 | Sections 8, 14.5, 15 | missing direct multi-issue refusal world | refusal plus fingerprint-not-evaluated in order | add valid lower refusal world |
| T38 | Sections 8, 14.5 | lower mismatch only | mismatch blocks without changing completeness | add direct TA mapping world |
| T39 | Sections 8, 16 | lower coherent-replacement detection only | original expected fingerprint mismatches | add direct TA mapping world |
| T40 | Sections 8, 16 | documented limitation only | coherent replacement may validate; no authentication claim | add disposable coherent-replacement valid twin |
| T41 | Sections 8, 14.3 | lower incomplete-alignment tests only | incomplete retained; not executed | add direct TA mapping world |
| T42 | Sections 8, 14.3 | lower not-aligned tests only | exact reason path retained; not executed | add direct TA mapping world |
| T43 | Sections 15, 18 | direct candidate-zero/candidate-one test with derivation spy | candidate zero accepted; alternate typed malformed before derivation | retain and extend to substituted lower instance |
| T44 | Sections 6, 16 | lower occurrence-content mismatch only | not aligned/content mismatch; not executed | add direct TA occurrence-content attack |
| T45 | Sections 7, 13 | fixed cohort literal only | valid different receipt times; independent latest | add two-condition public world |
| T46 | Sections 7, 13 | fixed source-time literal only | source time disclosure has no result effect | add source-time-only divergence twin |
| T47 | Sections 7, 13 | no direct noncomparable-clock twin | disclosure only; no cross-clock issue | add distinct clock-segment world |
| T48 | Sections 7, 8 | lower seed-role tests only | pre-horizon seed role retained; coverage governs | add direct TA seed alignment world |
| T49 | Sections 7, 16, 17 | purity implies no reread; no mutation witness | historical result byte-identical after post-fence source change | add disposable post-fence mutation proof |

## 5. Coverage map T50-T74

| ID | Governing clause | Current direct evidence | Required public outcome / path | Slice B red-first action |
|---|---|---|---|---|
| T50 | Sections 9, 12, 16 | constructed hidden request and one cycle; nesting-level matrix missing | typed rejection before derivation | attack every public model level, copy/construct/private/cache/cycle/wrong arm |
| T51 | Sections 9, 11, 12 | issue and trace boolean examples only | every integer index/count rejects booleans | enumerate all TA and carried lower integer coordinates |
| T52 | Sections 9, 12 | one strict issue-string test and spoofed model subclass | hostile scalar subclasses reject before equality/hash/conversion | add equality/hash/iteration/length/repr/serialization classes |
| T53 | Section 12 | missing/duplicate/reordered traces tested; issue/index matrix incomplete | authoritative result rejection | add all row/index/order/substitution attacks |
| T54 | Section 12 | seven top-level partitions and one endpoint field tested | every result partition authoritative | mutate each fixed/derived endpoint/trace/disclosure field |
| T55 | Section 13 | recursive mapping reversal direct test | identical private bytes | retain and add independently constructed nested dicts |
| T56 | Section 13 | seeds 1, 7, 12345 | identical private bytes across at least five seeds | add two seeds and receipt assertion |
| T57 | Sections 6, 13 | reversed tuple typed rejection in-process | deterministic rejection, never normalization | add subprocess seed matrix |
| T58 | Sections 5, 12 | filesystem/socket/SQLite spies and AST `ImportFrom` scan | no I/O, ambient input, orchestration, private import, reverse consumer | expand AST/runtime spies for environment, clock, stores, selectors, connectors, writes |
| T59 | Section 17 | accepted lower replay suites/report only | before/after lower results and revisions identical | add direct disposable TA replay/preservation witness |
| T60 | Section 17 | Slice A report and lower preservation suites | exact inventory and hashes | rerun immutable suites and direct receipt script |
| T61 | Sections 3, 21 | names/literals partly pinned; wording scan missing | positive surface says bounded support only | scan public API, exceptions, README, serialized result |
| T62 | Sections 3, 21 | negative literal pinned; wording scan missing | no non-occurrence language | scan negative result and documentation |
| T63 | Sections 6, 12 | semantic-coordinate forgery direct; separate value mutation missing | divergent coordinates reject; neither wins | independently forge both coordinates and cross-request row |
| T64 | Sections 9, 18 | historical manual probe only; no permanent production-number test | exact 134,217,728-byte private graph admitted | add safe generated production-number proof |
| T65 | Sections 9, 18 | historical manual probe only | byte 134,217,729 rejects before copy/lower/equality | add plus-one instrumentation twin |
| T66 | Sections 9, 18 | injected 3-node twin only | exact 200,000 expanded nodes admitted | add safe generated production-number proof |
| T67 | Sections 9, 18 | injected limit+1 only | node 200,001 rejects before lower work | add production-number plus-one twin |
| T68 | Sections 9, 18 | depth-two injected and root-zero tests only | root-relative depth 128 admitted | add iterative generated production proof |
| T69 | Sections 9, 18 | small depth plus-one only | depth 129 rejects before lower work | add production-number plus-one twin |
| T70 | Sections 9, 18 | small shared-DAG and cycle direct tests | per-reference expanded counting and active-path cycle refusal | strengthen with exact injected aggregate edge |
| T71 | Sections 9, 12 | one request copy/canonical pass and result request-once spies | one aggregate budget; no reset/rebudget/repeated subtree | add distributed near-limit and lower-call instrumentation |
| T72 | Sections 9, 18 | huge string/mapping early-refusal tests | scalar/mapping/sequence incremental refusal before allocation/lower work | add huge sequence, keys, bytes/unsupported container, stack-depth metrics |
| T73 | Sections 11, 15 | literals enumerated; all 22 issues not independently reached | every status arm/fixed arm/issue reachable; exact order/multi-retention | build compact exhaustive truth/reachability table test |
| T74 | Sections 9, 13, 18 | finite tokens and hostile floats; carried-value round-trip incomplete | admitted lower floats retained deterministically; hostile/schema-invalid reject before derivation | add all representatives in real lower world and five-seed receipt |

## 6. Exhaustive gate, result-boundary, and language work

Build one compact disposable truth-table harness that varies declaration,
context, complete revision, endpoints, subjects, pins, cutoffs, endpoint
execution and coverage, observation presence, alignment and EA completeness,
all expected-fingerprint relations, and positive/negative endpoint match. It
must prove the strict conjunction for execution, preserve completeness
independently of fingerprints, retain every independently applicable issue in
normative order, and make each of the 22 issue codes reachable through a valid
lower world.

Attack request and result reconstruction at every public nesting level using
ordinary serialized content, exact trusted instances, `model_construct`,
`model_copy`, hidden/private state, subclasses, hostile scalars, cycles,
wrong union arms, stale derived data, index/cardinality attacks, and
cross-request substitution. Instrument the authoritative result boundary to
prove the carried request is reconstructed exactly once under one aggregate
budget and every compact partition is independently rederived without I/O.

Expand purity and AST gates to cover both import forms, every forbidden lower
or orchestration call family, environment and clock access, writes, and reverse
dependencies. Scan the exact public names and literals, exceptions, README,
and serialized positive/negative results for forbidden occurrence,
continuity/cohort, causality, flow, diagnosis, recommendation, safety,
probability, and confidence claims, while allowing only the exact accepted
negative vocabulary.

## 7. Commit and verification sequence

Use forward-only commits:

1. documentation-only Slice A acceptance;
2. this Slice B plan;
3. red adversarial tests for each confirmed defect, with valid twins;
4. the narrowest production repair inside `backend.transition_assessment`;
5. green proof-only T01-T74, reachability, limit, determinism, purity, and
   preservation tests;
6. any further red-first repair found by independent review; and
7. truthful package/status documentation at the exact tested implementation.

After the last runtime or behavioral-test commit, run: the exact T01-T74 gate;
complete TA tests; affected model-kernel, state-classification,
evidence-alignment, evidence-assurance, temporal/model-state, and
architecture/isolation suites; backend compilation and dependency checks;
the complete working repository; separate detached base-only and all-extras
checkouts with fresh environments; explicit CAD/STEP/PDF tests; permitted
loopback reconciliation only when the sandbox blocks that exact setup; at
least five hash seeds across working and clean environments; both accepted
lower deterministic reproductions; the private TA canonical receipt; and
complete preservation inventory.

Run `git diff --check` for the working tree, Slice B implementation range, and
the complete TA milestone range. Record failures and separately permitted
reruns without collapsing columns. Leave
`docs/superpowers/reports/2026-09-07-ta001-slice-b-completion-report.md`
uncommitted with contiguous sections and exact marker. Stop for final owner
acceptance; TA-001 has no Slice C or demonstration slice.

END OF TA-001 SLICE B ADVERSARIAL-HARDENING PLAN
