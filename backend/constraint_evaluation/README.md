# constraint_evaluation

CN-001 provides a read-only composition facade over one injected
`SemanticCompatibilityQueries`. It constructs `ModelQueries` over the exact
loaded model already used by that semantic stack. It owns no store, performs
no writes, and never selects a model revision using `as_of`.

The public verdict vocabulary is `satisfied`, `violated`, and
`not_evaluated`. The exact CN refusal vocabulary is:

1. `constraint_not_declared`
2. `constraint_conflicted`
3. `observation_absent`
4. `observation_not_attached`
5. `evidence_not_assessable`
6. `value_shape_not_evaluated`
7. `model_value_shape_not_numeric`
8. `value_shape_not_satisfied`
9. `numeric_value_absent`
10. `declared_semantics_not_compatible`
11. `constraint_quantity_kind_mismatch`
12. `constraint_observation_role_mismatch`
13. `constraint_unit_identity_mismatch`
14. `numeric_value_out_of_bounds`

An unregistered constraint has no semantic result and no candidate rows. A
registered constraint with no active declaration uses
`constraint_not_declared`; competing active declarations use
`constraint_conflicted`. Detailed VS and ES findings remain unchanged in the
single carried lower-layer result and are not copied into CN's vocabulary.

## Observed decimal

`CanonicalObservedDecimal` is a canonical plain-decimal string. The original
`value_json` lexeme remains unchanged only in the carried ES occurrence.
Parsing accepts one JSON number with legal JSON whitespace and uses these
limits:

- stored `value_json`: 512 UTF-8 bytes;
- mantissa coefficient: 256 digits;
- mantissa fraction: 128 digits;
- significant digits: 256;
- exponent field: 4 lexical digits, including leading zeros;
- absolute exponent: 1024;
- expanded output: 384 digits;
- expanded fraction: 384 digits;
- expanded canonical string: 386 UTF-8 bytes.

Source size, exponent field length, exponent magnitude, expanded lengths, and
expanded byte size are preflighted before expansion. No float, ambient Decimal
rounding, fixed-point formatting, or private VS parser is used. Numeric parity
breaches use a fixed value-free message.

## Results and validation

Exact lookup carries one `ConstraintDeclarationResult`, one ES result when the
constraint is registered, and candidate rows indexed by
`semantic_candidate_index`.

Variable discovery carries `constraint_collection` once and the ES result once
when constraints exist. Each lightweight entry contains only
`constraint_index`, `constraint_anchor_id`, and candidate rows. It repeats
neither constraint declarations nor ES results.

Outer validators structurally revalidate carried lower-layer objects and
recompute every candidate row. They reject missing, duplicate, reordered, or
substituted indices; mixed anchors, variables, cutoffs, and revisions; forged
canonical decimals, boundaries, relations, satisfaction flags, verdicts, and
reasons; and nested `model_construct`, `model_copy`, or stale-ID forgeries.
`violated` means predicate falsity only and carries no safety, diagnostic,
normality, severity, or control meaning.

## Demo-printer Slice C fixture

The committed demo model adds exactly one `crg_` registration and one `vcn_`
declaration under `test_fixture/cn001_demo_fixture/manual_declaration`. The
constraint `con_4b768cf843f5474cb5e564e31d239a59` targets
`var_b7e2d3c4f5a6172839405a6b7c8d9e0f` and declares an inclusive numeric upper
boundary of `80`. The frozen stored value `60.4` evaluates `satisfied`; a
separate noncommitted synthetic `85` evaluates `violated`. Both are predicate
outcomes only, never equipment, safety, alarm, recommendation, diagnostic, or
control claims. The deterministic demonstration is generated and checked in
`tests/constraint_evaluation/test_demo_cn001.py` rather than committed as an
authoritative result.
