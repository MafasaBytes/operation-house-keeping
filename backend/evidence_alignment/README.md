# Evidence alignment

`backend.evidence_alignment` is the bounded EA-001 read-only composition
surface. It relates one already-computed operational-evidence selection to one
already-computed observation-compatibility result. It owns no evidence,
model, store, identity, revision, or persistent result.

## Public boundary

The single public operation is:

```python
align_operational_evidence_with_value_compatibility(request)
```

Its request carries exactly one
`OperationalEvidenceSelectionResult`, one independently computed
`VariableValueCompatibilityResult`, and an optional independently retained
expected snapshot fingerprint. Its result carries that request once, one
internally computed store-independent snapshot-validation result when a
snapshot exists, and only derived scalar disclosures.

The sole v1 consumer is
`backend.observation_compatibility.VariableValueCompatibilityResult`. There is
no consumer registry, generic adapter, second consumer, convenience facade,
or store wrapper.

## Alignment rule

Alignment requires all of the following from carried material:

1. a non-refused EA selection with a structurally self-consistent snapshot;
2. equal normalized UTC `as_of` values;
3. equal source, adapter, subject, extraction route, item, and JSON Pointer;
4. exactly one consumer candidate whose complete public
   `TemporalOccurrence` is field-for-field equal to the EA-selected
   occurrence; and
5. EA-internal closure from that occurrence's attempt to the snapshot scope's
   endpoint.

The consumer does not carry `endpoint_id`. Endpoint closure is derived only
inside the validated EA snapshot; it is never inferred from a URL, item key,
adapter name, or consumer value. Equal values, units, checksums, timestamps,
or occurrence IDs alone do not establish alignment.

## Result meanings

`aligned_with_complete_evidence` means the exact occurrence aligns and the EA
selection is complete within its declared horizon.

`aligned_with_incomplete_evidence` means the exact occurrence aligns while EA
reports incomplete evidence within its declared horizon. It does not upgrade
the evidence to complete, usable, current, or assured assessment evidence.

`not_aligned` reports a derived relational difference or absence such as a
different cutoff, different six-field locator, absent observation, changed
occurrence content, absent occurrence, or multiple exact candidates.

`not_evaluated` reports an earlier validity/integrity gate: either EA refused
selection or an independently supplied expected snapshot fingerprint did not
match. A refused selection has no snapshot validation and is never treated as
a relational mismatch.

Consumer attachment, specification, shape, and unit findings are disclosed
through the carried consumer result. They do not gate or upgrade occurrence
identity alignment.

## Expected-fingerprint relation

The alignment-local relation has four states:

- `not_supplied`: the caller supplied no independent expected fingerprint;
- `not_evaluated`: one was supplied, but a refused selection left no snapshot
  comparison to perform;
- `matched`: a non-refused snapshot comparison was performed and matched;
- `mismatched`: a non-refused snapshot comparison was performed and differed.

This does not change or re-export the lower EA fingerprint vocabulary. A
snapshot and embedded fingerprint can be coherently replaced together; an
independently retained expected fingerprint is required to detect that
replacement without stores. A fingerprint is not a signature, identity,
authority endorsement, trusted time, or truth claim.

## Purity and revalidation boundary

The public function reconstructs nested public content, calls the public pure
`validate_operational_evidence_snapshot(...)` exactly once for a non-refused
selection and zero times for a refused selection, and derives the result from
the carried values. It performs no filesystem, database, network, connector,
environment, configuration, store, or clock access. It does not reselect
source or temporal evidence and does not recompute observation compatibility.

Store-bound EA revalidation is deliberately absent from v1 alignment. A
caller may obtain a separate EA store-revalidation result and display it
beside an alignment, but that later disclosure neither rewrites nor
participates in the historical alignment result.

## Explicit non-claims

Evidence alignment does not establish or evaluate:

- source, adapter, extractor, sensor, payload, clock, or signer authority;
- global atomicity, currentness, freshness, staleness, continuity, cadence,
  completeness outside the declared EA horizon, or later store immutability;
- binding, interpretation, semantic suitability, engineering compatibility,
  constraints, behavior, state, state classification, transitions, or flows;
- physical occurrence, activity, measurement, command, configuration truth,
  causality, influence, conservation, or balance;
- correctness, safety, health, normality, diagnosis, impact, goals, actions,
  recommendations, planning, optimization, or control; or
- evidence aggregation, ranking, interpolation, gap filling, inference, or a
  current-value selection.

The package adds no store, cache, database, ledger, durable receipt, signature,
anchor, minter, model record, revision, connector, writer, UI, or artifact.

## Verification

Focused verification:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/evidence_alignment -q
```

Dependency and compilation checks:

```bash
.venv/bin/pip check
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m compileall -q backend
```

The EA-001 Slice C2 completion report records the complete lower/consumer,
architecture/no-I/O, working full-suite, clean base-only, clean all-extras,
CAD/STEP/PDF, determinism, preservation, and whitespace verification matrix.
