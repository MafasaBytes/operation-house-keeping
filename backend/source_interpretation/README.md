# source_interpretation

An authoritative append-only ledger of claims about what one exact
source-native property means. Each `spi_` record is scoped to the complete
three-field subject plus three-field property locator and declares one
dimension: quantity kind, observation role, or unit identity.

Interpretation is neither source evidence nor identity binding. Records never
carry an anchor, never attach a property to a model variable, and never fill an
absent `TemporalOccurrence.declared_unit`. Applicability is evaluated on the
ingestion-receipt axis at an explicit observation instant.

## Ledger and resolution

- `InterpretationStore` validates both the current and prospective complete
  collection before atomic append. Load and explicit-membership replay are
  all-or-nothing.
- Supersession is a same-locator, same-dimension, canonically ordered
  multi-parent DAG. Current tips are membership-relative; partial convergence
  remains contention and full convergence restores one tip.
- Retractions withdraw claims. Closures only narrow an unknown or unbounded
  end. `spj_` rejection records are standalone diagnostics and never enter
  resolution.
- `InterpretationResolver` imports the supported pure
  `identity_binding.membership()` helper and returns each dimension
  independently. Nothing is selected by time, authority, record id, append
  order, or filesystem order.
- Revision `irv_` identity is the interpretation-set id plus exact sorted
  membership under the `interpretations\n` domain tag.

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
.venv/bin/python -m pytest tests/source_interpretation/
```
