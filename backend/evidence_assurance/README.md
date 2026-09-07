# Evidence assurance

`backend.evidence_assurance` is the owner-accepted EA-001 read-only composition
surface for bounded DS-004 operational evidence. It coordinates injected
public source-reader and temporal-query dependencies, produces a captured
evidence snapshot and content fingerprint, and owns no store or authoritative
state.

## Status and lineage

EA-001 is complete and owner accepted. The exact accepted implementation
lineage includes the seed-aware Slice A integrity repair at
`ceee1446f18ae9b7134005089046a5a4d69e10ae`, repaired Slice B at
`932514a456bcafe690a94d2d774b61913c352fbf`, repaired Slice C1 at
`64c0a8ba7678c7567c2b596947167535cf8fbab3`, and the exact tested Slice C2
public surface at `96d0dfec1a73c6250159dae0df498880ac5e26b0`.

The accepted architecture and proof boundary are recorded in
[ADR-0019](../../docs/adr/0019-content-bound-operational-evidence-selection-and-assurance.md).

## Public operations

The stateful query object exposes exactly:

```python
EvidenceAssuranceQueries.select_operational_evidence(request)
EvidenceAssuranceQueries.revalidate_operational_evidence(
    snapshot,
    *,
    membership_mode,
)
```

The package also exposes the pure function:

```python
validate_operational_evidence_snapshot(
    snapshot,
    *,
    expected_fingerprint=None,
)
```

The package root has the accepted ordered 33-name `__all__`; it adds no
convenience aliases or alternate public vocabulary. Lower source and temporal
contracts remain owned and exported by their defining packages.

## Selection boundary

One request names one exact operational API source/property scope and an
inclusive aware-UTC interval from `horizon_started_at` through `as_of`.
Selection uses `received_at` and the complete `AttemptOrderKey`. Attempt
coverage separately uses effective wall time, including
`finished_at_no_response`. Source-native time and calculated observation age
are disclosure only.

The source inventory fence independently discovers the latest eligible
source-side observation at or before `as_of`. If it predates the horizon, the
token binds exactly one pre-horizon seed and its full mechanical closure. The
temporal-selected seed must agree with that independent source selection. A
seed does not enter horizon attempt coverage or establish continuity before
the horizon.

Selection captures source and temporal inventory tokens before and after its
material reads. Temporal material is read in one transaction; source material
is read from the exact named files with same-read metadata hashing/parsing and
payload-checksum checks. The result can claim only captured-view consistency
at those observed fences. It is not a distributed transaction, a global
atomic snapshot, or a claim about changes after the final fences.

## Snapshots, fingerprints, and statuses

A canonical snapshot carries complete source and temporal material once,
strict provenance indices, the selected observation, horizon coverage,
fences, assurance disclosures, ordered issues, and a `sha256:` content
fingerprint. It does not embed raw payload bytes.

Selection status is exactly one of:

- `complete_within_declared_horizon`;
- `incomplete_within_declared_horizon`; or
- `refused`.

Integrity, parity, unsupported-family, mutation, and bound conditions refuse
without a snapshot. Absence at or before the cutoff and incomplete horizon
coverage produce a canonical incomplete snapshot. Every applicable issue is
retained in normative order and carried exactly once.

The fingerprint binds the canonical snapshot content. It is not a signature,
durable identity, authority endorsement, trusted timestamp, authentication,
or truth claim. Replacing both snapshot and embedded fingerprint can remain
structurally self-consistent; detecting that replacement without stores
requires an independently retained expected fingerprint.

## Validation and store-bound revalidation

`validate_operational_evidence_snapshot(...)` is store independent and
performs no I/O. It reconstructs all nested public content, rejects forged
instances, hidden extras, wrong unions, cycles, hostile scalars, boolean or
invalid indices, reordered collections, stale derivations, and substituted
results, then recomputes routes, selection, coverage, issues, assurance,
canonical bytes, and fingerprint. Its source-byte and temporal-membership
fields always report `not_rechecked`.

Store-bound revalidation supports exactly:

- `require_equal_final_observed_membership`; and
- `named_captured_artifacts`.

The first requires stable current observed memberships equal to the
snapshot's final fence tokens. The second rereads exactly the captured named
source material and separately discloses current source/temporal membership
relations. A successful named reread does not call historical material current
or latest, even when current membership differs or cannot be fully observed.
Neither mode silently reselects evidence.

## Dependencies and non-claims

The package imports only public DS-004 operational evidence contracts and the
reader seam from `backend.data_sources`, public temporal contracts and query
seam from `backend.temporal_state`, Pydantic, and the standard library. It does
not import identity binding, source interpretation, model/model-state,
compatibility, constraint/behavior evaluation, state classification,
transition, flow, connectors, vendor clients, UI, planning, control, or
private store implementations.

EA owns no store, cache, database, ledger, revision, receipt, signature,
anchor, minter, connector, writer, ambient clock, or environment discovery.
It makes no freshness, suitability, semantic, state, transition, flow,
correctness, source-authority, or physical-occurrence judgment.

`backend.evidence_alignment` is a downward consumer of EA's public carried
results; EA never imports it. That pure package remains the sole alignment
consumer and adds no store-bound claim.

## Verification

Focused package verification:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider tests/evidence_assurance -q
```

The final EA owner-acceptance and Slice C2 completion reports record the full
lower, consumer, isolation, full-suite, clean-checkout, optional-format,
determinism, preservation, and whitespace evidence.
