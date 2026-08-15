# CN-001 Acceptance Matrix

Rows bind to **behavior at the public boundary**, not to names (house style
per the ES-001 matrix). Each row: `ID | Behavior at the public boundary |
Failure killed`. Produced independently of implementation. Slice A rows (A1–
A20) are enforced by Slice A tests; Slice B rows (B*) are specified here and
enforced in Slice B.

## Group A — Constraint identity anchor

| ID | Behavior at the public boundary | Failure killed |
|----|----------------------------------|----------------|
| A1 | `ConstraintAnchor` is public and matches its own `con_` grammar | identity grammar drift |
| A2 | non-canonical anchor ids (bad prefix, uppercase hex, wrong length, `ent_`/`var_`) are rejected | forged/cross-kind anchor |
| A3 | `mint_constraint_anchor` emits real unique RFC-4122 UUID4 ids | non-uuid4 / colliding identity |
| A4 | `namespace`/`role_name` use the accepted `^[a-z0-9-]+$` grammar; `display_name` nonempty | context-as-identity |
| A5 | the anchor is frozen and minimal: `entity_anchor_id`, `variable_anchor_id`, `unit`, `predicate`, `severity` are forbidden extras | anchor-as-claim drift |
| A6 | a `model_construct`-forged anchor re-fails `model_validate` | construction forgery |

## Group B — Canonical decimal + predicate

| ID | Behavior at the public boundary | Failure killed |
|----|----------------------------------|----------------|
| B1 | `CanonicalDecimal` accepts exact canonical strings (`0`,`-1`,`0.5`,`-0.25`, 128-digit) | canonical rejection |
| B2 | `CanonicalDecimal` rejects `-0`,`+1`,`01`,`.5`,`1.`,`1.0`,`0.0`,`1.230`,`1e3`,`NaN`,` 1`, 129-digit, and non-str | alias/hostile/oversize acceptance |
| B3 | `ScalarComparisonPredicate` accepts every one of the six operators | operator gap |
| B4 | the predicate accepts `DeclaredUnit` and `UnitNotDeclared` | unit-shape coupling |
| B5 | the predicate rejects `interval`,`between`,`tolerance`,`lower`,`severity`,`other_variable_anchor_id`, bad variable pattern, `threshold="60.40"`, `unit=None` | non-v1 / implicit-field drift |
| B6 | the predicate is frozen and a `model_construct` forgery re-fails `model_validate` | predicate forgery |

## Group C — ConstraintRegistration record (crg_)

| ID | Behavior at the public boundary | Failure killed |
|----|----------------------------------|----------------|
| C1 | a registration builds with a content-derived `crg_` id | envelope drift |
| C2 | evidence is nonempty and uses the full `EvidenceRef` union, canonicalized | membership-only unsupported fact |
| C3 | the registration carries the synthetic disclaimer in `OwnerDeclarationEvidence.statement` (and may in `note`) | silent owner claim |
| C4 | the registration has no `supersedes`/withdrawal/lifecycle field | permanent-claim mutation |
| C5 | a registration whose target variable is unregistered is refused at append | dangling target |
| C6 | two registrations of the same `con_` anchor are refused (never tie-broken by recency/authority/id) | duplicate identity |
| C7 | a `crg_` whose `model_record` evidence is absent from the collection is refused | dangling evidence |

## Group D — VariableConstraintDeclaration record + DAG (vcn_)

| ID | Behavior at the public boundary | Failure killed |
|----|----------------------------------|----------------|
| D1 | a declaration builds with a content-derived `vcn_` id | envelope drift |
| D2 | a declaration whose `con_` anchor is unregistered is refused at append | dangling identity |
| D3 | a declaration whose `variable_anchor_id` ≠ its registration's target is refused | identity/target drift |
| D4 | a declaration whose `predicate.variable_anchor_id` ≠ its own `variable_anchor_id` is rejected | predicate/target inconsistency |
| D5 | a parent with a different anchor/lock/unit/operator/variable is refused (different identity) | cross-lineage supersession |
| D6 | a supersession cycle is refused (`MODEL_CONSTRAINT_LINEAGE_INVALID`) | cyclic correction |
| D7 | a self-supersede is rejected | self-correction |
| D8 | competing current tips on one `con_` are surfaced as `conflicted`, never resolved by recency/authority/id | false winner |
| D9 | a successor superseding every tip converges; partial convergence stays conflicted | premature convergence |
| D10 | superseded-but-historical declarations remain disclosed (superseded ids carried) | history erasure |
| D11 | an explicit replay subset is membership-relative and may revive an earlier tip | non-replayable correction |
| D12 | a `vcn_` whose `model_record` evidence is absent from the collection is refused | dangling evidence |
| D13 | only the `threshold` may differ across a same-lineage correction (idempotent id for unchanged content) | uncontrolled duplicate |

## Group E — Structured discovery (query)

| ID | Behavior at the public boundary | Failure killed |
|----|----------------------------------|----------------|
| E1 | an unregistered variable → `status="not_registered"`, `constraints=()` | exception-on-absence |
| E2 | a registered variable with no constraints → `status="registered"`, `constraints=()` | empty-conflated-with-absent |
| E3 | a malformed variable anchor id raises `MODEL_ANCHOR_ID_INVALID` before I/O | silent bad-format |
| E4 | a registered variable with one declared tip → one `ConstraintDeclarationResult` with `status="declared"` | missing declaration |
| E5 | competing tips → `status="conflicted"` carrying every tip verbatim in canonical order | conflict resolution |
| E6 | every result carries the complete `ModelRevision` (not a bare id) | revision-id-only carriage |
| E7 | validators prove every carried registration/declaration/conflict/superseded id ∈ `revision.record_ids` | unprovable invariant |
| E8 | the collection result's constraints are ordered by `constraint_anchor_id` | nondeterministic order |

## Group F — Structural revalidation + ledger preservation

| ID | Behavior at the public boundary | Failure killed |
|----|----------------------------------|----------------|
| F1 | a `model_construct`-forged `crg_`/`vcn_` re-fails `model_validate` / `revalidate` | construction forgery |
| F2 | a `model_copy`-mutated record re-fails hash verification | copy-mutation forgery |
| F3 | a forged nested `ConstraintAnchor` inside a registration is rejected | nested forgery |
| F4 | a forged predicate / evidence / superseded id is rejected | field forgery |
| F5 | every existing record id, byte, revision, and authority is unchanged after Slice A | ledger regression |
| F6 | no accepted module outside `system_identity`/`model_kernel` is modified | boundary violation |
| F7 | the full accepted suite stays green after every Slice A commit | broken neighbor |

## Group G — Slice B (specified; enforced in Slice B)

| ID | Behavior at the public boundary | Failure killed |
|----|----------------------------------|----------------|
| G1 | the ES result is carried exactly once; no second VS/ES candidate copy | CM3 duplication |
| G2 | the admission precedence is reachable and non-duplicative (14 steps) | overlapping/unreachable reasons |
| G3 | model tokens are never dereferenced before `declared_semantics_compatible` | None-dereference crash |
| G4 | a unit lock mismatch → `not_evaluated`, never a converted comparison | silent conversion |
| G5 | `numeric_value_out_of_bounds` fires for CN-narrower resource limits; `numeric_value_malformed` is not a normal candidate outcome | dishonest malformed reason |
| G6 | `CanonicalObservedDecimal` preflight-checks exponent expansion before allocation | resource exhaustion |
| G7 | the evaluation emits no `severity`/`grade`/`alarm`/`recommendation`/`cause` | grading drift |
| G8 | the evaluation-discovery wrapper preserves `registered`/`not_registered` through evaluation | ambiguous empty tuple |