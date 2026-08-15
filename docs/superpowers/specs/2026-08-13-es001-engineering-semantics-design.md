# ES-001 — Explicit Engineering Semantics and Source-Property Interpretation

Status: accepted by the owner (2026-08-13) as the authoritative design
after a four-specialist design turn (architect synthesis, independent
72-row adversarial acceptance matrix, feasibility inspection, adversarial
review) and an owner correction pass. All earlier drafts and any
conflicting wording are non-governing. ADR:
`docs/adr/0011-engineering-semantics-and-source-property-interpretation.md`.
Plan: `docs/superpowers/plans/2026-08-13-es001-engineering-semantics.md`.
Acceptance matrix:
`docs/superpowers/plans/2026-08-13-es001-acceptance-matrix.md`.

This document is standalone: it incorporates the corrected synthesis and
every retained adjudication (F1–F10, recorded in §14) and does not rely on
any conversation or superseded draft.

## The question ES-001 answers

The accepted stack proves, over the committed demo-printer fixtures
(`tests/observation_compatibility/test_demo_compatibility.py`): what was
observed (`TemporalOccurrence.value_json="60.4"`, `declared_unit=None`);
where the evidence came from (occurrence, raw record, checksum,
provenance chain); which canonical variable the observation attaches to
(`iba_b1b86a4f…`, `binding_kind="property"` →
`var_b7e2d3c4f5a6172839405a6b7c8d9e0f`); what JSON value shape and
model-unit token the model requires (`vsp_c8e5d91d…`: `number`,
`project_local/ohk-units-1/degree_celsius`); and whether the supplied
representation is compatible (ruleset `vs001.1`).

It cannot yet honestly say: what physical quantity the variable
represents; whether the exact source property represents the same
quantity; whether the absent source-unit string has a separate authority
interpretation; whether source-property meaning and model-variable
meaning are compatible.

ES-001 adds exactly those declarations, without altering source evidence
and without collapsing interpretation into identity binding:

- **Part A** — a seventh model-kernel record kind,
  `VariableSemanticDeclaration` (prefix `vsm`), declaring per-dimension
  model-side engineering meaning (quantity kind; observation role), plus
  the `variable_semantics` kernel query.
- **Part B** — a new authoritative sibling append-only ledger,
  `backend/source_interpretation/` (repository root `interpretations/`),
  holding `SourcePropertyInterpretation` records: how an identified
  authority interprets one exact six-dimension source property (quantity
  kind; observation role; unit identity), with applicability, lifecycle,
  multi-parent convergent supersession, revisions (`irv_`), and replay.
- **Part C** — a new read-only composition facade,
  `backend/semantic_compatibility/`, ruleset `es001.1`, composing the
  VS-001 result, the kernel semantics query, and the interpretation
  resolution verbatim, and reporting token-identity compatibility per
  dimension.

**Never in scope**: constraint evaluation. Nothing calls 60.4 safe,
normal, in-range, excessive, or violating. No conversion, no dimensional
algebra, no range, no alarm, no diagnosis, no recommended action.

## Non-negotiable semantic rules

1. **Evidence and interpretation never merge.** `declared_unit=None`
   stays byte-true everywhere. Every public result keeps three separate
   unit facts — source-supplied (`occurrence.declared_unit` via the
   carried VS-001 `source_unit_evidence`), authority-interpreted (the
   carried interpretation resolution), model-required (the carried
   specification result) — and four separate meaning facts: source
   observation / source-property interpretation / model-variable meaning
   / compatibility result. An interpreted or model-required unit is
   never inserted into, copied into, or presented as a source-supplied
   field.
2. **Identity binding is not semantic interpretation.** Interpretation
   records reference the exact six-dimension key — the three
   `SourceSubjectRef` fields plus the three `SourcePropertyRef` fields,
   carried verbatim as `identity_binding` carries them. No interpretation
   record carries an anchor id, mints an anchor, or duplicates
   `BindingAssertion`. The existing binding remains the only authority
   connecting the property to the canonical variable.
3. **Model meaning is a separate correctable record**, never a field on
   an accepted record kind — ADR-0009 D1 measured the id breakage of
   field addition, and D2 deferred quantity/semantic kind to a separate
   future record kind. ES-001 executes that deferral.
4. **Units, quantity kinds, and roles are identity tokens.** Byte-exact
   triple comparison only. A result may say exact identities agree or
   disagree — never convertibility, dimension, scale, offset, or
   physical equivalence. Quantity kind and observation role are
   independent dimensions with independent verdicts: measured
   temperature and a commanded target are never interchangeable because
   they share a unit.
5. **Accepted layers stay intact.** `data_sources`, `temporal_state`,
   `system_identity`, `model_state`, `observation_compatibility`, and
   `structural_evidence` are unchanged. `model_kernel` changes only
   additively (the measured-safe union-arm mechanism) plus the one
   owner-mandated bounded integrity repair (§7). `identity_binding`
   changes only by the owner-authorized promotion of `membership()` to a
   documented supported helper with zero behavior change (§8).
   `VariableRegistration`, `VariableValueSpecification`,
   `TemporalOccurrence`, `SourcePropertyRef`, and every accepted
   identity-binding record keep their shapes.

## Architecture and import diagram

```
system_identity ──→ model_kernel ─────────────────────────────┐
temporal_state.contracts ──→ identity_binding ────────────────┤
temporal_state.contracts ─────────────┐                       │
identity_binding.contracts            │                       │
  (AppliesScope, AuthorityRef,        ├─→ source_interpretation (NEW ledger)
   Membership) + .resolver.membership │        │
model_kernel (token classes only) ────┘        │
model_kernel + identity_binding + temporal_state
        └─→ model_state ─→ observation_compatibility ─┐
              source_interpretation ──────────────────┴─→ semantic_compatibility (NEW facade)
```

Forbidden reverse edges (AST-enforced by isolation tests): no accepted
module imports `source_interpretation` or `semantic_compatibility`;
`source_interpretation` never imports `data_sources`, `model_state`,
`observation_compatibility`, `structural_evidence`,
`semantic_compatibility`, or `sqlite3`; `semantic_compatibility` never
imports `data_sources`, `identity_binding` (its types travel inside
carried objects), `structural_evidence`, or `sqlite3`, constructs no
store (`ModelStore`/`BindingStore`/`TemporalStore`/
`InterpretationStore`), holds no path literals, and never touches private
attributes of injected objects. Constructing `ModelQueries` from the
injected stack's exact public `LoadedModel` is explicitly permitted (the
accepted VS-001 seam).

## Part A — model-side engineering meaning (`model_kernel`, additive)

### Token value classes

Placed with `UnitReference`, reusing `LocalIdentifier`:

```python
class QuantityKindReference(_Frozen):
    """An identity TOKEN for a quantity kind, never a physical
    definition. It asserts no dimension, no dimensional algebra, no SI
    traceability, and no equivalence to any external ontology. Identity
    is the exact triple (system_id, system_edition, code), compared
    byte-for-byte."""
    system_id: Literal["project_local"]
    system_edition: LocalIdentifier
    code: LocalIdentifier

class ObservationRoleReference(_Frozen):
    """An identity TOKEN for an observation role (how a value relates to
    the physical quantity: measured actual, commanded target, …), never
    a behavioural definition. Same triple identity, byte-for-byte."""
    system_id: Literal["project_local"]
    system_edition: LocalIdentifier
    code: LocalIdentifier
```

Two classes rather than one shared token class: identical shape, but
distinct types make a role token unassignable where a quantity token is
expected at construction time.

Approved project editions (declared in the records that use them; no
central registry exists or is pretended): `ohk-quantities-1` with
`temperature`; `ohk-observation-roles-1` with `measured_actual`,
`commanded_target`, `setpoint`, `calculated_estimate`,
`status_configuration`. "Unknown / not declared" is **not** a token:
absence of a declaration record is the computed `not_declared` status.

### The record

```python
class QuantityKindDeclaration(_Frozen):
    dimension: Literal["quantity_kind"]
    quantity_kind: QuantityKindReference

class ObservationRoleDeclaration(_Frozen):
    dimension: Literal["observation_role"]
    observation_role: ObservationRoleReference

SemanticDimensionDeclaration = Annotated[
    Union[QuantityKindDeclaration, ObservationRoleDeclaration],
    Field(discriminator="dimension")]

class VariableSemanticDeclaration(_Frozen):
    """What the MODEL declares this variable to REPRESENT, one semantic
    dimension per record. An unauthenticated authority CLAIM about the
    model — never a claim about any source, adapter, observation, or
    supplied value; never a constraint, limit, range, behaviour, or
    equation; and never evidence that any observed value actually is the
    declared quantity. Tokens are identity strings, not an ontology."""
    record_kind: Literal["variable_semantic_declaration"] = (
        "variable_semantic_declaration")
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^vsm_[0-9a-f]{64}$")
    variable_anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    declaration: SemanticDimensionDeclaration
    evidence: tuple[EvidenceRef, ...]      # min 1, _canonical_evidence
    supersedes: tuple[str, ...] = ()       # multi-parent, _canonical_parents
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
    # validator mirrors VariableValueSpecification: parents are vsm_ ids,
    # no self-reference
```

The variable anchor is REFERENCED, never embedded (the `vrg` embeds it
verbatim; a copy would create an in-revision divergence class).

### Registration ripple (all additive; measured hash-safe)

`ModelRecord` union; `MODEL_RECORD_ID_PATTERN` and store `_FILENAME`
widen to `(reg|rtd|rel|rwd|vrg|vsp|vsm)`; `canonical._PREFIX_BY_KIND`
gains `"variable_semantic_declaration": "vsm"`;
`ModelRecordEvidence.record_id` widens to `(reg|rtd|rel|vrg|vsp|vsm)`
(`rwd` stays uncitable); the store bucket dispatch gains an arm;
`LoadedModel` gains three defaulted read-only mappings
(`semantic_declarations`,
`current_semantic_tips_by_variable_dimension` keyed by
`(variable_anchor_id, dimension)`, `semantic_superseded_by`);
`__all__` grows by eight names (54 → 62). No committed record hash
changes: `canonical_payload` dumps instances, not schemas — pinned by
regression.

### Validation pass (per-dimension lineage)

Slots after the `vsp` pass; all-or-nothing over load, prospective
append, and explicit replay subsets:

- `variable_anchor_id` must key `variable_registrations_by_anchor`
  (`MODEL_REFERENCE_INVALID`).
- Every parent must exist in the collection, be a `vsm` record,
  reference the same `variable_anchor_id`, **and carry the same
  `declaration.dimension`** — a cross-variable or cross-dimension
  supersession raises `MODEL_SEMANTIC_LINEAGE_INVALID`.
- Acyclicity by the iterative three-colour walk;
  `semantic_superseded_by` reverse index; current tips computed per
  `(variable_anchor_id, dimension)`; zero-tip defence in depth.
- **Evidence-reference closure** per the uniform rule of §7.
- Competing tips surface as `conflicted`, never invalidate the
  revision (the ADR-0009 D3 doctrine); a record superseding every
  current tip of its `(variable, dimension)` lineage converges it;
  partial convergence remains conflicted; repeated contention converges
  again (multi-parent DAG, ADR-0009 D4 semantics).
- Replay is membership-relative: an ancestor-only subset revives it as
  the governing tip; a successor without full ancestry is a
  reference-closure failure; `vsm` without its `vrg` is a
  reference-closure failure.

### Kernel query

```python
class SemanticDimensionResult(_Frozen):
    dimension: Literal["quantity_kind", "observation_role"]
    status: Literal["declared", "not_declared", "conflicted",
                    "not_registered"]
    declaration: VariableSemanticDeclaration | None = None
    conflicting_declarations: tuple[VariableSemanticDeclaration, ...] = ()
    superseded_declaration_ids: tuple[str, ...] = ()
    # validator: declaration iff declared; tips iff conflicted (>= 2,
    # canonically ordered by record id); superseded ids unique/sorted;
    # not_registered carries no history

class VariableSemanticsResult(_Frozen):
    anchor_id: str = Field(pattern=VARIABLE_ANCHOR_ID_PATTERN)
    quantity_kind: SemanticDimensionResult
    observation_role: SemanticDimensionResult
    revision: ModelRevision
    # validator: each dimension result carries its own dimension literal;
    # both are not_registered exactly together
```

`ModelQueries.variable_semantics(anchor_id) -> VariableSemanticsResult`,
beside `variable_value_specification`: `MODEL_ANCHOR_ID_INVALID` for
malformed input; `not_registered` for an unregistered anchor; tips read
from the loaded mappings; never ordered or chosen by `recorded_at`,
authority, record id, file order, or append order. This query is the
single source of model-meaning status; the facade never recomputes tips.

## Part B — the source-property interpretation ledger

### Ownership

`backend/source_interpretation/` (submodules `errors.py`, `canonical.py`,
`contracts.py`, `store.py`, `resolver.py`, `__init__.py`, `README.md`),
ledger root `interpretations/<set_id>/records/<record_id>.json`, set id
pattern `^[a-z0-9-]+$` (directory name is the set id). Demo set:
`interpretations/demo-printer/`. This home was pre-decided by ADR-0009's
closing consequence; records inside `identity_binding` (semantics in the
identity ledger), the temporal projection (disposable, derived), and
runtime configuration (unauditable, unreplayable) were all rejected.

Required module docstring, first paragraph (asserted verbatim by test):

> This ledger records how an identified authority interprets an exact
> source-native property. An interpretation is a claim ABOUT a source
> property, never evidence FROM the source: it is never inserted into,
> copied into, or presented as a source-supplied field, and a source
> that supplied no unit still supplied no unit. It declares no canonical
> identity, mints no anchor, and never maps a source property to a model
> variable — that decision lives exclusively in identity_binding.

### Record kinds

```python
class QuantityKindInterpretation(_Frozen):
    dimension: Literal["quantity_kind"]
    quantity_kind: QuantityKindReference        # model_kernel token class
class ObservationRoleInterpretation(_Frozen):
    dimension: Literal["observation_role"]
    observation_role: ObservationRoleReference
class UnitInterpretation(_Frozen):
    dimension: Literal["unit"]
    unit: UnitReference                          # model_kernel token class

InterpretationBody = Annotated[
    Union[QuantityKindInterpretation, ObservationRoleInterpretation,
          UnitInterpretation],
    Field(discriminator="dimension")]

class SourcePropertyInterpretation(_Frozen):     # prefix spi_
    """One authority's interpretation of ONE exact six-dimension source
    property, one semantic dimension per record."""
    record_kind: Literal["source_property_interpretation"] = ...
    schema_version: Literal["1"] = "1"
    record_id: str = Field(pattern=r"^spi_[0-9a-f]{64}$")
    subject: SourceSubjectRef            # temporal_state, VERBATIM (3 dims)
    property: SourcePropertyRef          # temporal_state, VERBATIM (3 dims)
    interpretation: InterpretationBody
    applies: AppliesScope                # identity_binding, VERBATIM
    supersedes: tuple[str, ...] = ()     # MULTI-PARENT, canonical sort,
                                         # duplicate rejection; parent SET
                                         # is identity, order is not
    recorded_at: UtcDatetime
    authority: AuthorityRef              # identity_binding, VERBATIM
    note: str = ""

class InterpretationRetraction(_Frozen):   # spr_: "no longer asserted"
    retracts: str                          # spi_ id
class InterpretationClosure(_Frozen):      # spc_: narrowing-only end,
    closes: str                            # at most one per spi_
    end: UtcDatetime

class InterpretationRejection(_Frozen):    # spj_ — DIAGNOSTICS ONLY
    """A considered-and-refused interpretation. NEVER an input to
    resolution. It identifies the considered candidate completely and
    carries no spi_ reference: it cannot reject an accepted assertion —
    withdrawal of accepted assertions is InterpretationRetraction."""
    subject: SourceSubjectRef
    property: SourcePropertyRef
    rejected_interpretation: InterpretationBody
    proposed_applies: AppliesScope
    recorded_at: UtcDatetime
    authority: AuthorityRef
    note: str = ""
```

Matching is exact equality on the whole six-dimension pair — the same
predicate the accepted resolver uses. No pattern, no wildcard, no
vendor-wide rule: a future authoring convenience must expand to exact
records, never to a broadened match.

### Multi-parent supersession lineage

Per exact `(subject, property, dimension)` key:

1. Every parent must exist in the supplied collection, be an `spi_`,
   and carry the **exact same six-dimension pair and the same
   `interpretation.dimension`** — `INTERPRETATION_SUPERSEDES_INVALID`.
2. The supersession graph per key is a multi-parent acyclic DAG
   (three-colour walk; cycles typed-refused).
3. Current tips = records with no successor in the supplied collection.
   A successor superseding every current tip converges the lineage;
   superseding only some leaves the remainder in contention; repeated
   contention converges again.
4. Parent order is never identity; the parent set is (canonical sort
   and duplicate rejection before the digest).
5. Replay is membership-relative and may revive an earlier tip; a
   successor without its full ancestry in the subset is a
   reference-closure failure.
6. `recorded_at`, authority, filesystem order, and record id never
   select a winner.

### Store (VALIDATING append; all-or-nothing load and replay)

`InterpretationStore(set_dir)`: `append` structurally revalidates the
record, verifies its content-derived id, loads the current set, and
validates the prospective collection before the atomic
stage-outside/promote write — so duplicate closures, dangling
supersession/retraction/closure targets, cross-property or
cross-dimension parents, and cycles are refused typed at append time and
no reachable on-disk state can poison `load()`. Crafted on-disk
violations still fail `load()` all-or-nothing with the same codes.
`load_revision(record_ids)` replays from an explicit id list with
pattern-check-before-path, duplicate rejection, and reference-closed
subsets. Collection validation also enforces: retraction targets exist;
closures are narrowing-only (an unknown or unbounded end to a declared
end; a declared end is corrected only by supersession), at most one per
assertion, with `effective_applies` rewritten to the declared end;
rejections are standalone diagnostics validated for shape only.

Canonical identity: content-derived ids through a module-local hardened
`build_record` (the kernel variant: typed failures, placeholder id,
validate-then-finalize), `_PREFIX_BY_KIND = {…: "spi", …: "spr",
…: "spc", …: "spj"}`; byte-parity with the accepted canonicalization
rules held by shared golden test vectors, never shared code.
`canonical.py` imports nothing from `contracts.py`.

`InterpretationRevision`: `revision_id` = `irv_` + sha256 over the
**domain-tagged** material

```
"interpretations\n" + set_id + "\n" + "\n".join(sorted(record_ids))
```

plus `record_ids` (unique, sorted), `record_count`,
`interpretation_set_id` — the `BindingRevision` shape with a distinct
prefix and deliberately distinct hash material (pinned in golden
vectors). This is a legitimate new revision namespace: the ledger is a
pre-approved new knowledge domain, and a replayable authoritative ledger
owns its membership identity.

Errors: `SourceInterpretationError` tree
(`InterpretationConfigurationError`, `InterpretationIntegrityError`,
`InterpretationResolutionError`) with codes
`INTERPRETATION_SET_ID_INVALID`, `INTERPRETATION_RECORD_INVALID`,
`INTERPRETATION_RECORD_KEY_MISMATCH`,
`INTERPRETATION_RECORD_HASH_MISMATCH`,
`INTERPRETATION_SUPERSEDES_INVALID`, `INTERPRETATION_RETRACTS_INVALID`,
`INTERPRETATION_CLOSURE_INVALID`, `INTERPRETATION_MULTIPLE_CLOSURES`,
`INTERPRETATION_REVISION_INVALID`, `INTERPRETATION_STORAGE_FAILURE`,
`INTERPRETATION_NAIVE_AT`, `INTERPRETATION_LOCATOR_INVALID`. Messages
carry ids only, never absolute paths.

### Resolution

`InterpretationResolver(loaded: LoadedInterpretationSet)` with

```python
def resolve_property_interpretations(
        self, subject: SourceSubjectRef, prop: SourcePropertyRef,
        at: datetime | None = None) -> PropertyInterpretationResult
```

`at` defaults to `None` solely so missing input fails through the typed
contract (`INTERPRETATION_NAIVE_AT`); there is no implicit clock.

Per dimension (`quantity_kind`, `observation_role`, `unit`):

1. Candidate set = current tips for the exact key that are not
   retracted (**active** = current tip and no `retracted_by`).
   Superseded and retracted records are disclosed in `via_assertions`
   summaries with lifecycle links but never resolvable. `spj_` records
   never enter this set (whole-object result equality with and without
   a rejection record, pinned by test).
2. No record ever declared for the key → `not_declared`. Records exist
   but none active → `retracted` when the governing tips are retracted
   without supersession history, or `inactive` when superseded and
   retracted lifecycle history is mixed. Aggregate `superseded` is
   impossible: every finite valid DAG has a current tip. Supersession
   remains fully disclosed per assertion through `superseded_by` and
   `active=False`.
3. Otherwise classify each active tip's `effective_applies` at `at`
   with the imported `identity_binding.resolver.membership(scope, at)`
   (§8) and apply the accepted eight-case classification with the
   interpretation body's canonical bytes as the target key: one
   positive body (possibly corroborated by same-body tips) →
   `interpreted` with `applicability_basis`; two or more positively-in
   differing bodies → `conflicted`, all candidates carried verbatim,
   canonically ordered; a differing unknown-membership candidate
   prevents a positive result (`ambiguous`); only unknowns →
   `applicability_unknown` / `ambiguous`; all out →
   `outside_applicability`.
4. Nothing is ranked by recency, `recorded_at`, authority, record id,
   file order, or append order — pinned by permutation tests. The
   surrounding classification is restated (the accepted `_Assessment`
   is private) with hand-authored behaviour vectors pinning parity with
   the identity-binding semantics; `membership` itself is imported, one
   implementation for every consumer.

Result contracts (every one `revalidate_instances="always"`):

```python
InterpretationStatus = Literal[
    "interpreted", "applicability_unknown", "outside_applicability",
    "not_declared", "ambiguous", "conflicted", "retracted", "inactive"]
# the corrected eight-status shape with bound→interpreted,
# unbound→not_declared renamed so an interpretation is never described
# with binding vocabulary

class InterpretationAssertionSummary(_Frozen):
    record_id, dimension, interpretation (VERBATIM), authority,
    declared_applies, effective_applies, closure_records (max 1),
    superseded_by, retracted_by, active, membership_at (Membership,
    VERBATIM), recorded_at
    # lifecycle validator mirrors the accepted AssertionSummary

class DimensionInterpretationResolution(_Frozen):
    dimension: Literal["quantity_kind", "observation_role", "unit"]
    status: InterpretationStatus
    interpretation: InterpretationBody | None = None   # iff interpreted
    candidate_interpretations: tuple[InterpretationBody, ...] = ()
    via_assertions: tuple[InterpretationAssertionSummary, ...] = ()
    applicability_basis: Literal["declared_interval",
                                 "includes_unbounded_claim"] | None = None
    # validator: interpretation iff interpreted; basis iff interpreted;
    # candidates only under applicability_unknown/ambiguous/conflicted;
    # candidates canonically ordered by canonical bytes

class PropertyInterpretationResult(_Frozen):
    subject: SourceSubjectRef                   # echo, VERBATIM
    property: SourcePropertyRef                 # echo, VERBATIM
    at: UtcDatetime
    quantity_kind: DimensionInterpretationResolution
    observation_role: DimensionInterpretationResolution
    unit: DimensionInterpretationResolution
    revision: InterpretationRevision
```

Every resolution is fully explainable from its own structured result
without searching the ledger.

## Part C — the semantic compatibility facade

Package `backend/semantic_compatibility/` (`contracts.py`, `facade.py`,
`__init__.py`, `README.md`). Read-only; owns no store; writes nothing.

### Constructor and query

```python
class SemanticCompatibilityQueries:
    def __init__(self, compatibility: ObservationCompatibilityQueries,
                 interpretations: InterpretationResolver) -> None:
        # isinstance-checked; wrong types raise
        # SemanticCompatibilityConfigurationError(
        #     "SEMANTIC_COMPATIBILITY_INPUT_INVALID")

    def variable_semantic_compatibility(
        self, variable_anchor_id: str, *, as_of: datetime,
        entity_anchor_id: str | None = None,
        source: SourceSelector | None = None,
    ) -> VariableSemanticCompatibilityResult: ...
```

- The VS-001 facade is injected and composed whole: its
  `VariableValueCompatibilityResult` (which itself carries the VM-001
  `VariableStateResult` and the kernel `VariableSpecificationResult`
  verbatim) is carried verbatim. ES-001 never re-expresses a lower-layer
  fact and holds no second vocabulary for one.
- `ModelQueries` is constructed per call from `compatibility.state.model`
  — the exact public `LoadedModel` the injected stack uses — so a
  membership/meaning revision mismatch is unconstructible.
- The `InterpretationResolver` is injected once; one resolver governs
  every candidate's interpretation resolution, so an
  interpretation-revision mismatch across candidates is unconstructible.
- Request validation is delegated to the accepted boundaries; upstream
  typed errors propagate unchanged. The module adds exactly one own
  error code (`SEMANTIC_COMPATIBILITY_INPUT_INVALID`).

### Result contracts

```python
class VariableSemanticCompatibilityResult(_Frozen):
    variable_anchor_id: str
    as_of: UtcDatetime
    ruleset_version: Literal["es001.1"]
    value_compatibility: VariableValueCompatibilityResult  # VS-001 VERBATIM
    semantics_result: VariableSemanticsResult              # kernel VERBATIM
    interpretation_revision: InterpretationRevision        # knowledge context
    candidates: tuple[CandidateSemanticCompatibility, ...] = ()
    # invariants: semantics_result.anchor_id == variable_anchor_id;
    # semantics_result.revision == value_compatibility.state.model_revision;
    # len(candidates) == len(value_compatibility.candidates), index-parallel
    # and verbatim; every candidate interpretation.revision ==
    # interpretation_revision. Three knowledge contexts (model, binding,
    # interpretation revisions) all disclosed, never merged.
```

Per candidate — the **authoritative dimensional fields**:

```python
class CandidateSemanticCompatibility(_Frozen):
    value_candidate: CandidateValueCompatibility           # VS-001 VERBATIM
    interpretation: PropertyInterpretationResult | None = None
    # None IFF the candidate has no observation: the lock predicate is
    # `value_candidate.state_candidate.bound is None` — OBSERVATION
    # EXISTENCE, never attachment and never a binding status. When
    # present: subject/property echo the candidate's exact locator and
    # at == occurrence.received_at (validator-locked). A limbo candidate
    # (observed, unattached) therefore CARRIES its interpretation
    # resolution while receiving no semantic verdict.

    quantity_kind_compatibility: Literal[
        "token_identical", "token_differs", "not_evaluated"]
    quantity_kind_not_evaluated_reason: _MeaningReason | None = None
    observation_role_compatibility: Literal[
        "token_identical", "token_differs", "not_evaluated"]
    observation_role_not_evaluated_reason: _MeaningReason | None = None
    unit_identity_compatibility: Literal[
        "unit_identity_exact", "unit_identity_mismatch", "not_evaluated"]
    unit_identity_not_evaluated_reason: _UnitReason | None = None

    interpreted_unit_source_lexeme_relation: Literal[
        "lexeme_identical", "lexeme_differs", "not_evaluated"]
    interpreted_unit_source_lexeme_not_evaluated_reason: \
        _LexemeReason | None = None

    semantic_findings: tuple[_SemanticFinding, ...] = ()
    # sorted, unique, derived one-to-one from the fields above by a
    # validator — a deterministic disclosure vocabulary WITHOUT an
    # independent aggregate status; it can never contradict the
    # dimensional fields because it is locked to them
```

Each verdict/reason pair is validator-locked: a reason exists exactly
when the verdict is `not_evaluated`; the dimensional fields are the
authoritative result.

### Reason vocabularies

```python
_MeaningReason = Literal[
    "no_observation", "observation_not_attached",
    "evidence_not_assessable",           # the F2 gate (ADR-0009 rule 9)
    "model_meaning_not_declared",        # covers not_declared AND
                                         # not_registered (unreachable
                                         # after the attachment clause,
                                         # because attachment implies
                                         # registration in the same
                                         # revision — a VM-001 invariant)
    "model_meaning_conflicted",
    "source_interpretation_not_declared",
    "source_interpretation_inapplicable",         # outside_applicability
    "source_interpretation_applicability_unknown",
    "source_interpretation_ambiguous",
    "source_interpretation_conflicted",
    "source_interpretation_retracted",            # root/tips retracted
    "source_interpretation_inactive"]

_UnitReason = Literal[
    "no_observation", "observation_not_attached",
    "evidence_not_assessable",
    "model_specification_not_available", "model_specification_conflicted",
    "model_unit_not_declared",
    "source_interpretation_not_declared",
    "source_interpretation_inapplicable",
    "source_interpretation_applicability_unknown",
    "source_interpretation_ambiguous",
    "source_interpretation_conflicted",
    "source_interpretation_retracted",
    "source_interpretation_inactive"]

_LexemeReason = Literal[
    "no_observation", "observation_not_attached",
    "source_unit_absent",                # the demo's honest outcome
    "unit_interpretation_not_positive"]  # any non-interpreted unit dim
```

### Precedence chains (first matching clause wins; independence
enforced; no clause hides evidence — every underlying status is carried
verbatim)

Quantity kind (observation role identical in form over its own
dimension results):

1. no observation → `no_observation`
2. `attachment != "attached"` → `observation_not_attached`
3. `value_candidate.evidence_consistency ∉ {consistent, not_evaluated}`
   → `evidence_not_assessable` (aligned with ADR-0009 rule 9: evidence
   that is internally contradictory receives no verdict)
4. semantics dimension status ∈ {not_declared, not_registered} →
   `model_meaning_not_declared`
5. status conflicted → `model_meaning_conflicted`
6. interpretation dimension status mapped to its distinct reason
7. otherwise → verdict: byte-exact triple equality of the model token
   and the interpreted token → `token_identical` / `token_differs`

Unit identity: clauses 1–3 as above; 4. specification status
`not_specified`/`not_registered` → `model_specification_not_available`;
5. `conflicted` → `model_specification_conflicted`; 6. governing tip
carries `UnitNotDeclared` → `model_unit_not_declared`; 7. interpretation
`unit` status mapped as clause 6 above; 8. verdict: byte-exact triple
equality of `specification.unit.unit` and the interpreted unit →
`unit_identity_exact` / `unit_identity_mismatch`. (This compares two
full triples — stronger than VS-001's bare-lexeme relation, which is
untouched inside the carried `value_candidate`.)

Interpreted-unit-vs-source-lexeme (disclosure of tension between what
the source wrote and what the authority claims it means; deliberately
NOT gated on evidence consistency — a malformed `value_json` never
erases a supplied unit string, the accepted VS-001 doctrine): 1–2 as
above; 3. `source_unit_evidence != "present"` → `source_unit_absent`;
4. unit interpretation not positively `interpreted` →
`unit_interpretation_not_positive`; 5. verdict: byte comparison of
`occurrence.declared_unit` against the interpreted unit's `code` →
`lexeme_identical` / `lexeme_differs`. A `lexeme_differs` is loud
evidence the interpretation may be stale — disclosed, never
auto-resolved, and never a semantic verdict.

Model-side clauses precede interpretation-side clauses deliberately:
when neither side declares, the model-side absence governs.

### `declared_semantics_compatible` — the exact eight-clause condition

Present exactly when ALL hold:

1. an observation exists;
2. it is attached to the requested registered variable;
3. evidence is assessable and consistent
   (`evidence_consistency == "consistent"`);
4. model quantity meaning has exactly one current declaration;
5. model role meaning has exactly one current declaration;
6. applicable source interpretations resolve positively
   (`interpreted`) for quantity kind, observation role, and unit;
7. model and interpretation tokens are byte-exactly equal in all three
   dimensions;
8. the model value specification is `specified` with a declared unit.

Contract docstring: *asserts that the model declarations and the
applicable authority interpretation tokens agree for quantity kind,
observation role, and unit identity — nothing about safety, normality,
physical correctness, calibration, constraint satisfaction, or whether
the authority claim is true.* A differing source-supplied unit lexeme
does not withhold it (the lexeme has not been interpreted as a unit
identity), but then `interpreted_unit_lexeme_differs_from_source` is
mandatorily co-emitted and the VS-001 lexical result rides verbatim.

### The total findings derivation (validator-locked; sorted; unique)

```python
_SemanticFinding = Literal[
    "declared_semantics_compatible",
    "observation_absent", "observation_not_attached",
    "evidence_inconsistent",
    "model_meaning_not_declared", "model_meaning_conflicted",
    "model_specification_not_available",
    "model_specification_conflicted", "model_unit_not_declared",
    "source_interpretation_not_declared",
    "source_interpretation_inapplicable",
    "source_interpretation_applicability_unknown",
    "source_interpretation_ambiguous",
    "source_interpretation_conflicted",
    "source_interpretation_retracted",
    "source_interpretation_inactive",
    "quantity_kind_mismatch", "observation_role_mismatch",
    "unit_identity_exact", "unit_identity_mismatch",
    "unit_identities_differ_conversion_not_attempted",
    "source_unit_absent_but_interpreted",
    "interpreted_unit_lexeme_differs_from_source"]
```

Derivation, published as a total function:

- `observation_absent` iff no observation; `observation_not_attached`
  iff observed and unattached (one finding each, subsuming every
  dimension's clause-1/2 reasons).
- `evidence_inconsistent` iff
  `evidence_consistency ∉ {consistent, not_evaluated}` — and then no
  semantic verdict exists (the gate), so it can never co-occur with
  `declared_semantics_compatible`.
- Per meaning dimension: `token_differs` → `quantity_kind_mismatch` /
  `observation_role_mismatch`; every clause-4/5/6 reason → its
  identically named finding (deduplicated by the sorted-unique tuple).
- Unit dimension: `unit_identity_exact` → `unit_identity_exact`;
  `unit_identity_mismatch` → `unit_identity_mismatch` AND
  `unit_identities_differ_conversion_not_attempted` (always co-emitted,
  never alone; asserts ONLY that the two identity tokens differ, that
  no conversion is performed, and that no convertibility, dimension,
  scale, offset, or required conversion has been established); reasons
  → their identically named findings
  (`model_specification_not_available`,
  `model_specification_conflicted`, `model_unit_not_declared`, and the
  interpretation reasons — never conflated: a missing specification is
  not a declared-no-unit).
- `source_unit_absent_but_interpreted` iff
  `source_unit_evidence == "absent"` and the unit dimension resolved
  `interpreted` — the demo's headline disclosure: an absent source unit
  has a separate authority interpretation which is NOT filled into the
  evidence.
- `interpreted_unit_lexeme_differs_from_source` iff the lexeme relation
  is `lexeme_differs`.
- `declared_semantics_compatible` iff the eight-clause condition.

No field named `value`, `current_value`, `normalized_value`,
`unit_filled_value`, `winner`, `current`, or `usable` exists anywhere.
All contracts owned by the two new modules use
`revalidate_instances="always"`; carried lower-layer objects are trusted
only when produced by accepted modules.

## Time and revision semantics

| Instant / context | Role |
|---|---|
| `occurrence.received_at` | The only resolution instant: binding resolution already runs here; interpretation resolution runs at the same instant, per candidate. |
| `as_of` | Receipt-axis candidate cutoff, delegated to VM-001 unchanged. Never a resolution instant. |
| Binding applicability | Evaluated at `received_at` (accepted, untouched). |
| Interpretation applicability | Evaluated at `received_at`. |
| Model revision (`mrv_`) | Knowledge context; tips membership-relative; replay revives. |
| Interpretation revision (`irv_`) | Knowledge context; `load()` vs `load_revision()`. |
| `recorded_at` | Audit only; never selects winners. |

Why `received_at`: an interpretation is a claim about what the source's
report meant over an ingestion-receipt interval. A firmware change at T
is closure-plus-new-record, and per-occurrence resolution lets one
timeline honestly span it. Resolving at `as_of` would let a later query
silently change what an old observation meant — the failure mode the
accepted stack already refuses for identity. No observation ⇒ no
resolution instant ⇒ `interpretation is None`; no `as_of` fallback, no
execution-clock default anywhere.

Asymmetry, deliberate and documented: model-side records (`vsp`, `vsm`)
carry no applicability interval — meaning change over wall time is
supersession plus explicit revision selection. Source-side
interpretations carry applicability because the source itself can change
behaviour at a wall instant.

## §7 The uniform evidence-reference closure rule (owner-mandated bounded repair)

> For every evidence-bearing model claim record —
> `RelationshipAssertion`, `VariableValueSpecification`, and
> `VariableSemanticDeclaration` — each `EvidenceRef` of kind
> `model_record` must satisfy `record_id ∈ the supplied collection's
> record ids`, else the collection fails with the accepted typed
> `MODEL_REFERENCE_INVALID`. The rule is uniform and all-or-nothing
> across `load()`, prospective-append validation, and every explicit
> replay subset. Foreign evidence arms (`owner_declaration`,
> `identity_binding_record`, `source_raw_record`,
> `temporal_occurrence`, `structural_source_locator`) remain declared
> references: never dereferenced, never validated against foreign
> ledgers. `vsm_` becomes citable in `ModelRecordEvidence`; `rwd_`
> remains uncitable.

Sequencing: before the ES-001 append — (a) failing-before reproduction
that a `vsp_` citing `ModelRecordEvidence` for an absent record
currently loads; (b) the uniform rule lands; (c) regression proving
every committed ledger and record id loads and verifies unchanged; (d)
replay-subset tests proving omission of cited model evidence invalidates
the replay.

## §8 The `membership()` promotion (the only accepted identity-binding surface change)

`identity_binding.resolver.membership(scope, at)` is promoted to a
documented, supported, pure helper of the identity-binding public
surface: docstring promotion naming it supported, a README note, and a
behaviour-vector contract test pinning all nine start/end boundary-kind
combinations. **Zero behaviour change**; existing identity-binding
behaviour vectors remain byte- and result-identical. The interpretation
resolver imports this helper and never copies the algorithm.

## Vocabulary identity (decision record)

Closed kernel literals rejected (welds physics vocabulary into the
kernel — the ADR-0007 D3 ontology slide). Independent vocabulary record
kinds rejected as scaffolding (the tokens carry no validatable
semantics; recorded as the natural future home if they ever do).
Project-local identity tokens with editions chosen — the accepted
`UnitReference` shape; `system_id` is a widenable literal so an external
ontology (QUDT was identified as licence-compatible in ADR-0009 D6) can
arrive later with its own edition semantics.

## Demo-printer evolution (fixed by owner decision)

```
models/demo-printer/             14 -> 16
  + vsm_A: quantity_kind = project_local/ohk-quantities-1/temperature
           for var_b7e2d3c4f5a6172839405a6b7c8d9e0f
  + vsm_B: observation_role = project_local/ohk-observation-roles-1/
           measured_actual, same variable
interpretations/demo-printer/     0 -> 3    (NEW ledger set)
  + spi_1: quantity_kind = temperature      } all for the exact pair
  + spi_2: observation_role = measured_actual } subject (printer-1,
  + spi_3: unit = ohk-units-1/degree_celsius } moonraker, extruder) x
           property (api:moonraker:v1, printer_objects,
                     /result/status/extruder/temperature)
bindings/demo-printer/            6 -> 6    (UNCHANGED)
bindings/demo-printer-model/      5 -> 5    (UNCHANGED)
```

No committed `spj_` record: rejection behaviour is exercised only in
synthetic tests. Record content: `recorded_at = 2026-08-13T12:00:00Z`
(fixed constant), authority `{test_fixture, es001_demo_fixture,
manual_declaration}`, `supersedes = ()`, `note = ""`; `vsm` evidence is
one `OwnerDeclarationEvidence` in the committed model-only statement
style (no source vocabulary — the model-ledger vocabulary sweep
continues to enforce this, extended to `vsm`); `spi` records carry the
committed demo binding's exact subject/property, the same declared
fixture interval `[2026-08-07T20:00Z, 2026-08-07T21:00Z)` on
`ingestion_received_at`, and an honesty note stating the interpretation
is authority knowledge, never source-supplied evidence. Every id is
computed through the canonical builders at implementation time — no
fabricated hashes; the spec names ids only after they exist on disk.

Revisions: the current `mrv_702c840f…` (14) becomes the pinned
pre-semantics revision; all historical revisions (9, 10, 11, 14 records)
keep replaying from explicit full record-id lists; prefix filters are
never membership selectors. The interpretation set's first revision
(`irv_…` over 3 sorted ids) is pinned as a golden constant with an
explicit-membership replay test. Every previously committed record stays
byte-identical, mechanically checkable: the byte-freeze maps are
completed (all 14 model + all 11 binding records) BEFORE the ES-001
appends land.

### The demonstration chain (per-arrow disclosure kind)

```
Moonraker source bytes                                  [source evidence]
  -> RawRecord 698aa72a…, sha256:6771710d…              [computed result]
  -> TemporalOccurrence cd2579c5…: value_json="60.4",
     declared_unit=None, received_at=2026-08-07T20:00:18Z [source evidence]
  -> SourceSubjectRef + SourcePropertyRef               [source-native
                                                         identity, unresolved]
  -> existing BindingAssertion iba_b1b86a4f…            [authority declaration]
  -> resolve_property at received_at -> bound           [computed result]
  -> canonical VariableAnchor var_b7e2d3c4…             [authority declaration]
  -> VariableRegistration vrg_40c8c6b9…                 [verified in supplied revision]
  -> VariableValueSpecification vsp_c8e5d91d…           [verified in supplied revision]
  -> NEW VariableSemanticDeclaration vsm_A / vsm_B      [verified in supplied revision]
  -> NEW SourcePropertyInterpretation spi_1..3,
     resolved at received_at -> interpreted             [authority declaration
                                                         + computed resolution]
  -> semantic compatibility: token_identical /
     token_identical / unit_identity_exact;
     source unit absent; findings exactly
     {declared_semantics_compatible, unit_identity_exact,
      source_unit_absent_but_interpreted}               [computed result]
```

The committed demonstration
(`tests/semantic_compatibility/test_demo_semantics.py`) asserts the six
separate disclosures (observed value as the verbatim string "60.4";
source-supplied unit absent — still and forever; model-required
representation verbatim; model-declared meaning verbatim; authority
interpretation verbatim; per-dimension compatibility plus the findings
tuple), plus the negative guards: serialized evidence subtree free of
interpretation vocabulary; pre-`vsm` replay reports
`model_meaning_not_declared` with VS-001 verdicts unchanged; an empty
interpretation set reports `source_interpretation_not_declared`; a
cutoff before first receipt reports `observation_absent`; the whole
VS-001 result whole-object-equal to a directly computed one. It runs
offline from frozen fixtures.

## What ES-001 unlocks for CN-001, and what stays forbidden

Unlocked (later, owner-gated): a constraint record can name its subject
by declared meaning; a constraint evaluator gains a semantic admission
gate (attached + satisfies_value_shape + declared_semantics_compatible,
every prerequisite traceable to records); honest refusal vocabulary.
Still forbidden, in ES-001 and unchanged by it: ranges, bands, limits,
thresholds, alarms, envelopes, equations, behaviours, unit conversion,
dimensional algebra, interpolation, aggregation, fusion, causality,
diagnosis, recommended actions, and any wording that grades an observed
value. The ES-001 result contracts contain no numeric comparison of
`value_json` against anything.

## Exclusions

No LLM in any path. No network in any test. No writes from any facade.
No canonical-id minting outside the canonical builders. No vendor or
device vocabulary in kernel contracts beyond identity tokens. No
pattern- or vendor-scoped interpretation matching.

## Limitations (verbatim in the module READMEs, asserted by test)

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

## §14 Adjudication record (F1–F10, all incorporated)

- **F1** — the interpretation ledger uses VALIDATING append for every
  record kind, so no append-only poisoned state is reachable; crafted
  on-disk states still fail load typed.
- **F2** — semantic verdicts gate on evidence consistency
  (`evidence_not_assessable` reason); `declared_semantics_compatible`
  can never co-occur with `evidence_inconsistent`. The lexeme
  co-occurrence is deliberate, mandatory-disclosed, and pinned.
- **F3** — `interpreted_unit_lexeme_differs_from_source` (a lexical
  disclosure, not a contradiction claim);
  `unit_identities_differ_conversion_not_attempted` (owner-corrected
  name; never emitted without `unit_identity_mismatch`).
- **F4** — the findings derivation is a published total function;
  `model_specification_not_available` / `model_specification_conflicted`
  are first-class findings, never conflated with
  `model_unit_not_declared`.
- **F5** — every result contract in both new modules carries
  `revalidate_instances="always"`; carried-object trust extends only to
  accepted-module products.
- **F6** — evidence-reference closure is uniform across `rel`, `vsp`,
  `vsm` (§7, owner-mandated repair).
- **F7 (Group-13 correction)** — aggregate `superseded` is unreachable
  for a finite valid interpretation DAG and is not a public status,
  reason, or finding. `retracted` and mixed-history `inactive` remain
  distinct; supersession is disclosed per assertion through lifecycle
  links and history, never collapsed or discarded.
- **F8** — `InterpretationRejection` (`spj_`) exists, diagnostics-only,
  with the exact shape of §Part B; not committed to the demo set.
- **F9** — the `irv_` hash material is domain-tagged and pinned in
  golden vectors.
- **F10** — the interpretation-presence lock predicate is observation
  existence (`state_candidate.bound is None`), spelled out; `at=None` is
  a typed-refusal path; the attachment-implies-registration dependency
  is stated where relied upon.

## Verification

Two clean-checkout columns, green at every commit: base-only
(`requirements.txt` + `requirements-dev.txt`; ES-001 imports no extras
anywhere) and all-extras (adds cad + pdf; results byte-identical across
columns). Baseline to preserve: 1435 passed / 0 failed / 0 skipped
(all-extras) at `8cb5f1e`. Focused suites: `tests/model_kernel`,
`tests/source_interpretation`, `tests/semantic_compatibility`, plus the
accepted suites unchanged except the enumerated extend-only migrations.
The next open question (CN-001 candidate): how does a constraint declare
its subject by meaning, and what admission gate does evaluation require?
