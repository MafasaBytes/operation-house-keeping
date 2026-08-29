# model_state

The VM-001 read-only bound model-state query facade. It holds **no state
of its own**: it joins a loaded model revision (a knowledge context,
never a time axis) to identity-bound temporal evidence at a required
receipt-axis cutoff, by composition of injected accepted query objects.

```text
data_sources → temporal_state ─┐
        system_identity ─→ identity_binding ─→ ┌──────────────┐
        system_identity ─→ model_kernel ─────→ │ model_state  │
                           temporal_state ───→ └──────────────┘
```

Spec: `docs/superpowers/specs/2026-08-09-vm001-model-state-design.md`;
decisions: `docs/adr/0008-model-state-composition-facade.md`.

VP-001 Slices A, B, and C are owner accepted. Slice D is authorized and in
progress.
Slice B is owner accepted at
`81179700513bb671cf9955c6a5d7163e3bcc7e1b`. Slice C adds only
`associated_port_variable_state()`: displaying variable state beside a port is
not a claim that an observation occurred at the port. No VP fixture record
exists.

## Composition

`ModelStateQueries(model: LoadedModel, resolver: BindingResolver,
temporal: TemporalQueries)` — public APIs only, no store construction, no
private-field access (AST-enforced). The facade builds one
`BoundTemporalQueries` from the exact injected objects, so ONE binding
revision governs reverse discovery and every candidate resolution — a
mismatch is unconstructible.

`associated_port_variable_state()` composes the exact-context, selected-model
`VariablePortAssociationResult` with the independently computed
`VariableStateResult` at the requested cutoff. Its outer status comes only from
association admission and lifecycle. The state pipeline runs for every valid
request even when endpoints are not admitted or the association is undeclared,
conflicted, or inactive. Lifecycle context never filters temporal evidence;
the cutoff never selects a model revision. Model revision, binding revision,
and temporal cutoff remain separate provenance axes.

## Semantics worth knowing

- **The pipeline always runs**: an unregistered model variable still gets
  reverse discovery, temporal querying, and per-occurrence resolution;
  its evidence returns in identity/model limbo with an honest
  per-candidate `attachment` status. Evidence is never suppressed and
  never described as model state.
- **Observation existence ≠ model attachment**:
  `observation_availability == "observed"` asserts only that source
  evidence exists under a queried locator. Attachment to the requested
  variable is claimed exclusively by a candidate's
  `attachment == "attached"` (deterministic precedence: no observation →
  resolution nonpositive → resolution mismatch → variable unregistered →
  anchor divergent → attached).
- **Latest-per-locator only (accepted limitation)**: each candidate
  reports the locator's most recent observation at or before the cutoff,
  forward-resolved at its own `received_at`. When that occurrence
  resolves elsewhere, the result means **"no latest candidate observation
  attachable to the requested variable"** — never "no observation ever".
  The historical last observation that once resolved to this variable
  belongs to a later, explicitly named history query.
- **Binding resolution happens at each occurrence's own `received_at`** —
  never at `as_of`, never at the execution clock. A far-future cutoff
  yields an older/staler bound observation, not `outside_applicability`.
- **Discovery is revision-relative and time-free**: every locator EVER
  declared for the variable is a candidate, including superseded,
  retracted, and closed declarations — each disclosed via its verbatim
  `DeclaredLocatorEntry` (lifecycle flags and record ids, no
  time-specific "active" claim). Zero candidates means unbound, not
  missing data.
- **Explicit selectors are diagnostic**: executed even when undeclared,
  classified (`ever_declared_for_requested_variable` /
  `ever_declared_for_other_variable` / `undeclared` — "ever declared"
  means declared somewhere in this binding revision, not necessarily
  applicable at the observation time), never creating or implying a
  binding, and `declared_locator_count` always discloses multiplicity.
- **Anchor divergence is inspectable, never reconciled**: the
  binding-declared `VariableAnchor` is carried verbatim next to the
  model-embedded one, with the exact differing field names.
- **No ranking, no aggregation, no conversion, no single current value**:
  multiple candidates are all surfaced in locator order; identical values
  never collapse multiplicity; there is no aggregate value field.
- **Typed failures**: naive cutoffs and malformed inputs are
  `ModelStateError`s; upstream typed errors — including
  `TemporalStoreError("TEMPORAL_STORE_UNAVAILABLE")` for
  missing/corrupted/unreadable temporal storage — propagate unchanged.
  Storage unavailability is never conflated with `none_before_cutoff`.
  This module never imports `sqlite3`.

## Verification

```bash
.venv/bin/python -m pytest tests/model_state/   # focused suite
.venv/bin/python -m pytest                      # full repository suite
```
