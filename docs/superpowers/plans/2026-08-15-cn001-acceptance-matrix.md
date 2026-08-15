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
| B1 | `CanonicalDecimal` accepts canonical positive/negative integers and fractions including `0.25` and `-0.25`, through contract, builder, canonical bytes, append and load | negative sub-unit rejection |
| B2 | direct contracts/load reject `-0`,`-0.0`,`+1`,`01`,`.5`,`1.`,`1.0`,`60.40`, exponent, whitespace, nonfinite, over-limit and non-string values | alias/hostile acceptance |
| B3 | `canonical_constraint_decimal` normalizes string aliases (`60.40→60.4`, `-0→0`, `0e99→0`) before construction and refuses non-string/nonfinite/over-limit input | post-hash repair |
| B4 | lower and upper predicates accept inclusive and exclusive `NumericBoundary` values | boundary-kind gap |
| B5 | intervals accept `lower<upper` and inclusive singleton `lower==upper` | singleton rejection |
| B6 | reversed intervals and equal intervals with either exclusive endpoint are rejected | empty predicate |
| B7 | discriminated union rejects wrong arms, arbitrary operators, tolerance, severity, extra variables and unit/conversion fields | non-v1 drift |
| B8 | boundaries/predicates are frozen and `model_construct` forgeries fail public revalidation | predicate forgery |

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
| D3 | the registration, not the declaration or predicate, is the sole target-variable authority | duplicate target drift |
| D4 | expected quantity-kind, observation-role and unit locks are complete exact token types but are not cross-validated against VSM/VSP at append | append-time semantic inference |
| D5 | only a parent with a different constraint anchor is refused; predicate form, bounds, inclusivity, and expected tokens may change under the same anchor | over-constrained correction |
| D6 | a supersession cycle is refused (`MODEL_CONSTRAINT_LINEAGE_INVALID`) | cyclic correction |
| D7 | a self-supersede is rejected | self-correction |
| D8 | competing current tips on one `con_` are surfaced as `conflicted`, never resolved by recency/authority/id | false winner |
| D9 | a successor superseding every tip converges; partial convergence stays conflicted | premature convergence |
| D10 | superseded-but-historical declarations remain disclosed (superseded ids carried) | history erasure |
| D11 | an explicit replay subset is membership-relative and may revive an earlier tip | non-replayable correction |
| D12 | a `vcn_` whose `model_record` evidence is absent from the collection is refused | dangling evidence |
| D13 | identical reappend is idempotent; any immutable declaration-content edit changes its canonical id | identity drift |

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
| E9 | exact lookup of a valid unknown `con_` returns `not_registered`; malformed/wrong-type ids fail before I/O | absent/misuse conflation |

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
