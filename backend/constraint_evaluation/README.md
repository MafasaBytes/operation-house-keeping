# constraint_evaluation

A read-only CN-001 Slice B composition facade. It evaluates declared numeric
constraints against the evidence attached to their target variable, building
directly over one injected accepted ES-001 `SemanticCompatibilityQueries`
instance and the Slice A `ModelQueries` constructed from its exact public
loaded model. The facade owns no store, performs no writes, selects no model
revision by `as_of`, and propagates lower-layer typed errors unchanged.

The evaluator emits exactly three verdicts (`satisfied`, `violated`,
`not_evaluated`) and refuses for exactly the reasons enumerated in
`NotEvaluatedReason`. It emits no severity, grade, normality, alarm,
recommendation, cause, diagnosis, or safety field, ever. `violated` asserts
only that the admitted observed value does not satisfy the declared numeric
predicate.

## Composition boundary

The facade is constructed over one injected `SemanticCompatibilityQueries`.
The Slice A `ModelQueries` is built over the SAME public loaded model the
injected ES facade uses, so a constraint-declaration / membership /
specification / semantics revision mismatch is structurally impossible rather
than merely detected.

The complete ES result for the variable is queried once and carried once
across every evaluation in a collection. Each candidate evaluation refers to
its ES candidate by contiguous zero-based index. No duplicate semantic or value
candidate objects are constructed.

## Reachable precedence (15 steps)

`derive_candidate_evaluation` is the single authoritative per-candidate
derivation, shared by both the facade and the outer result validators. The
refusal precedence is:

1. `not_declared` — the constraint anchor has no registration or no
   declaration (conflicted declarations also land here).
2. `conflicted` — multiple active declarations cite the same anchor.
3. `no_observation` — the variable has no temporal occurrence.
4. `observation_not_attached` — the occurrence is not bound to the
   registered variable.
5. `evidence_not_assessable` — VS reports a non-admitted reason (verbatim):
   `json_type_unrecognized`, `shape_disagreement`,
   `value_json_malformed`, `value_not_representable`,
   `specification_conflicted`, `specification_not_available`.
6. `model_value_shape_not_numeric` — the governing model VSP declares a
   non-`number` value shape.
7. `does_not_satisfy_value_shape` — VS reports `consistent` but the observed
   shape is not `number`.
8. `numeric_value_absent` — the admitted value is null (nullable null) or
   otherwise not a parseable decimal.
9. `declared_semantics_not_compatible` — ES reports
   `declared_semantics_compatible` is false.
10. `constraint_quantity_kind_lock_mismatch` — the constraint's expected
    quantity-kind does not match the model's declared quantity-kind.
11. `constraint_observation_role_lock_mismatch` — the constraint's expected
    observation-role does not match the model's declared observation-role.
12. `constraint_unit_identity_lock_mismatch` — the constraint's expected
    unit does not match the model's specified unit.
13. `numeric_value_out_of_bounds` — the admitted decimal exceeds the CN
    parser's observation-specific limits.
14. Otherwise: predicate comparison → `satisfied` or `violated`.

Authoritative model semantic tokens are not dereferenced until
candidate-local `declared_semantics_compatible` has passed (step 9).

## Observed-decimal contract

`CanonicalObservedDecimal` carries the original source `lexeme` (the exact
`value_json` text) and a `canonical` plain-number string. The parser accepts
exactly one JSON number, permits legal JSON whitespace, enforces a byte limit
on the full lexeme, preserves the source lexeme unchanged, accepts bounded
exponent notation, preflights expansion before allocation, normalizes
mathematical zero to `"0"`, never uses float or ambient Decimal rounding, and
treats disagreement with the VS numeric classification as a typed
parity-breach integrity error (`NumericParityBreachError`). The parser does
not import or copy any private VS parsing code; it uses the standard
library's `json.loads(parse_float=Decimal, parse_int=int,
parse_constant=reject)` call shape.

## Authoritative outer validation

The result contracts (`ConstraintEvaluationResult`,
`VariableConstraintEvaluationCollectionResult`) have validators that
re-derive every candidate from the carried ES result and reject divergence.
This detects: wrong counts or indices, candidate substitution or reordering,
mixed anchors / variables / revisions / cutoffs, forged decimals, boundary
relations, satisfaction, verdicts, or reasons, evaluated rows under failed
admission, refusal rows when all gates pass, and forged nested objects via
`model_construct` / `model_copy` / stale IDs.