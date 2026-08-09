# observation_compatibility

The VS-001 read-only assessment layer: given an observation honestly
attached to a registered model variable, what has the model explicitly
declared about that variable's value type and unit, and is this particular
observation compatible with those declarations?

```text
system_identity ─→ model_kernel ──────┐
identity_binding ─→ model_state ──────┼─→ observation_compatibility
temporal_state (contract types) ──────┘        read-only, holds no state
```

Spec: `docs/superpowers/specs/2026-08-09-vs001-variable-value-specification-design.md`;
decisions: `docs/adr/0009-variable-value-specification-and-observation-compatibility.md`.

## Composition

`ObservationCompatibilityQueries(state: ModelStateQueries)` — one injected
accepted query object. The kernel query is constructed from
`state.model`, the exact public loaded model the state facade uses, so a
membership/specification revision mismatch is unconstructible. The VM-001
`VariableStateResult`, each of its candidates, and the kernel's
`VariableSpecificationResult` are carried **verbatim**; nothing is
recomputed or re-expressed here.

## Semantics worth knowing

- **A specification is a model claim, not a source claim.** It states what
  the model requires. It is never evidence that an observed value carries
  the specified unit, and the model unit is never inserted into the
  observation, the bound result, the occurrence, or provenance.
- **Shape and unit are independently gated.** Evidence consistency gates
  only the shape verdict: a malformed or self-contradictory `value_json`
  never erases an explicitly supplied source-unit string, and source-unit
  evidence is disclosed whenever an observation exists — including for
  unattached candidates, where the comparison is withheld.
- **Contradictory evidence is not incompatibility.** `json_type` and
  `value_json` are cross-checked by strict parse; a disagreement is
  reported as inconsistent evidence, neither field is repaired, neither is
  preferred, and no verdict is computed.
- **A conflicted specification suppresses verdicts without overriding
  earlier precedence.** The recorded reason is still the first applicable
  clause: `no_observation`, then `observation_not_attached`, then
  `specification_conflicted`.
- **Units yield only a lexical relation.** `declared_lexeme_identical`
  means only that the source's unit string is byte-identical to the
  model's unit code — never that the source uses the specified unit
  system, edition, dimension, or scale. A unit is read only from
  `occurrence.declared_unit`: never from the clock's unit, display names,
  role names, JSON pointers, adapter ids, or subject identifiers. No
  conversion, folding, trimming, or normalization.
- **Value shapes are `boolean`, `number`, and `string`.** `integer` is
  deliberately absent: the accepted pipeline classifies integers and
  decimals alike as JSON `number` and canonicalization erases the
  distinction, so a lexical integer verdict would describe the normalized
  representation rather than the source's numeric category. Mathematical
  integrality is never inferred.
- **Nothing is aggregated, ranked, converted, filled, or selected.**
  Compatibility is per candidate; there is no aggregate, normalized,
  winning, current, or usable value field.
- **Real-data limitation**: no producer in this repository ever sets a
  non-`None` `declared_unit`, so on real committed evidence the lexical
  relation is always `not_evaluated` with reason `source_unit_absent`.
  Every lexical-relation outcome is exercised by synthetic fixtures.

## Verification

```bash
.venv/bin/python -m pytest tests/observation_compatibility/   # focused
.venv/bin/python -m pytest                                    # full suite
```
