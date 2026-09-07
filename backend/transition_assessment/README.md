# Transition assessment

`backend.transition_assessment` is the TA-001 pure leaf composition surface.
It determines whether two exact, already-computed state-classification views,
their declared transition, and their complete carried evidence alignments
support the declared endpoint pattern at ordered cutoffs.

## Status

TA-001 Slice A is owner accepted at exact tested implementation
`76738ac0d098eb59b0fec4f6970aa862528647d9`. Slice B adversarial hardening and
final verification are implemented at exact tested implementation
`2ec18f7234273dba98098d268df4568d5cc84d85`; final TA-001 acceptance is pending.
The accepted design is recorded in
[ADR-0020](../../docs/adr/0020-evidence-gated-declared-transition-assessment.md).

## Public boundary

The package exports the exact 28-name contract surface and one operation:

```python
assess_declared_transition_endpoints(request)
```

The request carries one transition-declaration result, ordered from/to
state-classification results, and the exact distinct evidence-alignment
collection required by their governing observed conditions. The result
carries that request once and adds only derived endpoint disclosures, condition
traces, issues, execution state, and a bounded conclusion.

## Admission and evidence gate

Before lower reconstruction or derivation, TA applies one aggregate request
budget: 134,217,728 canonical JSON bytes, 200,000 expanded graph nodes, and
nesting depth 128. It rejects cycles, unsupported or hostile content, hidden
state, boolean indices, invalid cardinalities, non-finite floats, and floats in
non-float schema positions. Exact built-in finite floats inherited from lower
contracts remain numbers and use deterministic `float.__repr__` JSON tokens in
private canonical verification.

Execution requires exact transition, context, revision, endpoint, subject, and
cutoff admission; complete endpoint classifications; complete governing
evidence alignment; and a separately supplied expected fingerprint reported by
the lower alignment as matched. Evidence completeness remains independent of
the fingerprint relation.

The strongest conclusions are only:

- `bounded_evidence_supports_declared_endpoint_pattern`; or
- `bounded_evidence_does_not_support_declared_endpoint_pattern`.

## Purity and non-claims

The operation reconstructs and derives only from carried public results. It
performs no filesystem, store, database, network, connector, environment,
clock, or write operation. It does not reclassify state, select evidence,
revalidate stores, or recompute lower alignment.

TA does not establish a transition occurrence or non-occurrence, event
identity, continuity, temporal cohort, traversed path, causality, physical
truth, correctness, safety, diagnosis, recommendation, or control. It owns no
store, cache, ledger, durable identity, signature, receipt, fixture,
demonstration, or persistent artifact.

## Verification

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/transition_assessment -q
```

The Slice A completion report records its accepted implementation evidence.
The uncommitted Slice B completion report records adversarial T01-T74 closure,
final full-suite and clean-checkout verification, deterministic reproduction,
preservation, compilation, dependency, and whitespace evidence for owner
validation.
