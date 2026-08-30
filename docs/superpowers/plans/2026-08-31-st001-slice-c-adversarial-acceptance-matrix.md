# ST-001 Slice C — Adversarial Acceptance Matrix

Status: Slices A and B are owner accepted. Slice C is implemented and adversarially reviewed; awaiting owner acceptance. Slice D remains unstarted and unauthorized.

Date: 2026-08-31

## 1. Public surface

| ID | Acceptance criterion |
|---|---|
| C01 | Package exports exactly the ordered 15-name surface. |
| C02 | Error inheritance and exact two error codes are pinned. |
| C03 | Facade accepts only public `ConstraintEvaluationQueries`. |
| C04 | Exactly one public method exists with the exact keyword-only signature. |
| C05 | Exact source/refusal/condition/result field order is pinned. |
| C06 | Exact literals and refusal order are pinned; no aliases leak. |
| C07 | Contracts are frozen, extra-forbidden, and full-instance revalidated. |

## 2. Input and scheduling

| ID | Acceptance criterion |
|---|---|
| C08 | Malformed state/context/cutoff/source requests fail through typed ST input error. |
| C09 | Naive and offset-less cutoffs reject; aware cutoffs normalize to UTC. |
| C10 | Unregistered state admits only empty sources and invokes no CN branch. |
| C11 | Registered state source IDs equal the permanent condition set exactly. |
| C12 | Missing, extra, duplicate, malformed, substituted, and retargeted sources reject. |
| C13 | Valid reversed sources canonicalize by constraint ID. |
| C14 | Every permanent condition is invoked once in canonical order. |
| C15 | Permanent subject entity and one normalized cutoff reach every CN branch unchanged. |
| C16 | Not-declared/inactive/conflicted lifecycle does not suppress registered CN branches. |
| C17 | All scheduled branches run before first canonical typed lower failure propagates unchanged. |
| C18 | No discovery, fallback, ranking, permutation, or cross-product exists. |

## 3. Pin alignment and truth

| ID | Acceptance criterion |
|---|---|
| C19 | State lifecycle refusals map exactly and keep coverage not evaluated. |
| C20 | One/corroborating healthy effective body is admitted without winner selection. |
| C21 | Absent constraint maps to `not_registered` / `condition_not_registered` and contributes nothing. Valid public SRG material makes this branch defensive-unreachable through reference closure; closure and fail-closed derivation are pinned without forging a private model. |
| C22 | No current VCN maps to `not_declared` / `condition_declaration_not_declared` and contributes nothing. Valid public STD material makes this branch defensive-unreachable through pin closure; closure and fail-closed derivation are pinned without forging a private model. |
| C23 | Two current VCN tips map to `conflicted` / `condition_declaration_conflicted` and contribute nothing regardless of body equality. |
| C24 | A unique current VCN differing from pin maps to `superseded` / `condition_declaration_superseded` and contributes nothing. |
| C25 | Only `exact_current` uses the authoritative CN candidate verdict; a CN `not_evaluated` outcome maps to `condition_evaluation_not_evaluated`. |
| C26 | Alignment-to-refusal mapping is exact and independently tested. |
| C27 | All satisfied yields complete/executed/matches. |
| C28 | Known violation with evaluated siblings yields complete/executed/does_not_match. |
| C29 | Violation plus unknown yields incomplete/executed/does_not_match. |
| C30 | No violation plus unknown yields incomplete/not_executed/None. |
| C31 | Unknown rows/refusals remain visible; nonmatch selects no alternative state. |
| C32 | Two independent calls may both match; no aggregate exists. |

## 4. Temporal and lower-result integrity

| ID | Acceptance criterion |
|---|---|
| C33 | Model membership is explicit and never selected by cutoff. |
| C34 | Registered branches disclose temporal alignment not asserted. |
| C35 | Lower receipt/source/clock/staleness/provenance remain unchanged. |
| C36 | No cohort, skew, freshness threshold, interpolation, persistence, or clock-equivalence rule exists. |
| C37 | Every complete CN result is carried once; detailed CN refusals are not duplicated. |
| C38 | Model, binding, interpretation revision and cutoff coherence are exact. |
| C39 | Selector, entity, constraint, candidate, occurrence, and pin coherence are exact. |

## 5. Hostile public reconstruction

| ID | Acceptance criterion |
|---|---|
| C40 | Missing, duplicate, extra, reordered, and substituted source/CN/condition/refusal rows reject. |
| C41 | Mixed model/binding/interpretation revisions and cutoffs reject. |
| C42 | Wrong-arm, out-of-range, negative, boolean, float, string, and coercible indices reject. |
| C43 | Forged lifecycle, pin, outcome, coverage, temporal status, execution, and match reject. |
| C44 | Nested `model_construct`, `model_copy`, hidden extra, and stale-ID attacks reject. |
| C45 | Validation remains store/filesystem/network/environment/clock/write independent. |
| C46 | ST-specific coherent mutation test states the inherited authentication limitation exactly. |
| C47 | Typed CN parity and lower errors remain the exact same class object. |
| C48 | Ambient decimal context cannot affect the carried CN result or ST derivation. |

## 6. Architecture, replay, and preservation

| ID | Acceptance criterion |
|---|---|
| C49 | Exact public chain is `constraints.semantic.compatibility.state.model`. |
| C50 | No private lower helper, parser, predicate, store, path, socket, database, cache, or write exists. |
| C51 | Lower layers do not import `state_classification`; kernel import boundary remains exact. |
| C52 | Existing 9/10/11/14/16/18/28/29/32 histories and revisions remain exact. |
| C53 | Authoritative ledger remains 32 records with zero SRG/STD/STW. |
| C54 | PT/VP/BH artifact hashes and every predecessor byte remain exact. |
| C55 | Hash seed, source input order, and physical record order do not change output. |
| C56 | Focused, affected, architecture, compile, full, and dual-clean-checkout columns pass. |
| C57 | Slice D creates no candidate, rehearsal, ledger, fixture, membership, or artifact change. |

## 7. Completion gate

Every applicable row must be green and every confirmed specialist finding must
remain as a regression. The completion report asks only: accept Slice C and
separately authorize Slice D pre-append rehearsal?

All rows are implemented and adversarially reviewed. C21 and C22 are pinned as
defensive-unreachable consequences of accepted public reference closure, not
as fabricated private worlds. Slice D remains unstarted and unauthorized.

END OF ST-001 SLICE C ADVERSARIAL ACCEPTANCE MATRIX
