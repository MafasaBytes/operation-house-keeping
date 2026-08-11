# operation-house-keeping

Backend foundation for a living, constraint-aware representation of an
engineered system. Model-centric, not LLM-centric: deterministic code,
explicit models, evidence, and provenance are authoritative; an LLM is
never the source of engineering truth. `CLAUDE.md` is the authoritative
project specification.

## Architecture

```
Source systems
  -> backend/data_sources            evidence acquisition + format extraction
        (CSV/BOM, STEP, PDF, Moonraker; raw store; provenance; quarantine)
  -> backend/temporal_state          rebuildable temporal evidence projection
  -> backend/system_identity         canonical anchors (opaque identity)
  -> backend/identity_binding        explicit identity-binding ledger
  -> backend/model_kernel            typed entity/relationship model ledger
  -> backend/structural_evidence     structural claims + reconciliation (SN-001)
  -> backend/model_state             bound model-state query facade
  -> backend/observation_compatibility  value-specification compatibility
```

Committed knowledge lives beside the code: `models/` (model-kernel
ledgers), `bindings/` (identity-binding ledgers), `showcases/` (frozen
synthetic demonstration sources — test artifacts, never engineering
truth).

## Milestones

Accepted: DS-001 (CSV/BOM), DS-002 (STEP), DS-003 (PDF), DS-004
(operational API), TS-001 (temporal projection), IB-001 (identity
binding), MK-001 (model kernel), VM-001 (variable membership +
`model_state`), VS-001 (value specification + `observation_compatibility`)
— each with owner-mandated validation and repair slices. Current: SN-001
(structural evidence normalization and cross-source model binding), in
three gated slices. Designs in `docs/superpowers/specs/`; decisions in
`docs/adr/`.

## Verification

```
.venv/bin/python -m pytest        # base-only: cad/pdf-marked tests skip
# all-extras: install requirements-cad.txt + requirements-pdf.txt first
```
