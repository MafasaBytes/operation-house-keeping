# semantic_compatibility

A read-only ES-001 composition facade. It combines the complete VS-001 value
compatibility result, the model kernel's per-dimension variable semantics, and
source-property interpretation resolved at each occurrence's own
`received_at`. All lower-layer objects are carried verbatim.

The authoritative outputs are independent quantity-kind, observation-role,
unit-identity, and interpreted-unit/source-lexeme verdicts. Each verdict has a
validator-locked not-evaluated reason. `semantic_findings` is a sorted,
unique, total derivation from those fields, never a second aggregate truth.

`declared_semantics_compatible` exists only when all eight governing clauses
hold: observation present; attached to the requested registered variable;
evidence consistent; one model quantity declaration; one model role
declaration; positive quantity, role, and unit interpretations; exact identity
in all three dimensions; and a specified model value representation with a
declared unit. It says nothing about the observed value's quality or safety.

This package owns no store, performs no conversion, dimensional algebra,
range/constraint evaluation, normalization, filling, ranking, diagnosis, or
recommended action. A differing source unit lexeme remains a separate lexical
disclosure and does not manufacture a unit identity.

## Governing ES-001 limitations

1. An interpretation is an unauthenticated authority claim — never
   evidence that the source actually reports that quantity, role, or
   unit. `interpreted_unit_lexeme_differs_from_source` is the only
   in-band staleness signal.
2. Token identity is not a physical ontology: byte equality of
   project-local identity triples only; two editions' `temperature`
   tokens differ and are reported as differing. No dimensional
   equivalence, convertibility, scale, or SI traceability is asserted
   anywhere.
3. `unit_identities_differ_conversion_not_attempted` asserts difference
   and non-attempt only — convertibility is never established in either
   direction.
4. An interpretation is scoped to one exact six-dimension locator; the
   same bytes re-ingested under a different source_id, adapter, or
   pointer resolve `source_interpretation_not_declared`. No vendor-wide
   or pattern-scoped interpretation exists.
5. The eight-case resolution classification is restated in
   `source_interpretation.resolver`; parity with identity binding is
   guarded by the imported `membership()` helper, shared behaviour
   vectors, and review — not by construction.
6. `declared_unit=None` remains true in every occurrence; the
   demonstration's `degree_celsius` never appears in source evidence,
   asserted by path-scoped sweeps.
7. There is no explicit "declared unknown" semantic arm: absence of a
   record is the only not-declared state on both sides.
8. Interpretation resolution requires an observation instant; a
   candidate with no observation gets no interpretation resolution (no
   `as_of` fallback, no execution clock).
9. Model-side semantic declarations carry no applicability interval;
   meaning change over wall time is supersession plus explicit revision
   selection. The asymmetry with interpretation applicability is
   deliberate.
10. The committed interpretation records assert a declared interval
    scoped to the fixture scenario and make no claim about a real
    printer.
11. `declared_semantics_compatible` asserts declared-meaning token
    agreement under the eight-clause condition only — never value
    validity, calibration, correctness, safety, or constraint
    satisfaction, and never that the authority claim is true.
12. `spj_` rejection records are diagnostics only and are not committed
    to the demo set in ES-001.
13. Single-writer stores, no fsync-grade durability, no knowledge-time
    revision queries — inherited verbatim from the accepted ledgers.
14. Interpretation and binding sets are independent knowledge domains;
    both revisions are disclosed, never cross-checked.
15. The `projector_version` gap in `TemporalOccurrence` (VS-001's
    honest gap) remains and is restated, not repaired.

## Verification

```bash
.venv/bin/python -m pytest tests/semantic_compatibility/
```
