# ADR-0009 — Variable value specification in the kernel; compatibility as a composition facade

Status: accepted (owner, 2026-08-09). Spec:
`docs/superpowers/specs/2026-08-09-vs001-variable-value-specification-design.md`.

## Context

VM-001 can attach an observation to a registered canonical variable and
report its identity resolution and provenance honestly, but it deliberately
preserves the observed value and any supplied unit without assigning
engineering meaning. A result of `value_json="60.4"`,
`declared_unit=None`, `attachment="attached"` proves identity and evidence
attachment; it does not prove the variable represents temperature, that the
value is numeric rather than numeric-looking, that the unit is degrees
Celsius, or that the value may safely enter an equation. Something had to
state what the model *requires*, separately from what a source *supplied*.

## Decisions

1. **Variable value specifications are a sixth kernel record kind**,
   `VariableValueSpecification` (prefix `vsp`), referencing a registered
   `VariableAnchor` by id. Enriching `VariableRegistration` was rejected on
   evidence: adding a field to an accepted record kind changes its
   canonical payload, so the committed `vrg` record's content-derived id
   stops verifying (measured: `40c8c6b9…` → `d61e0fc6…`) and the ledger
   fails to load. It was independently rejected on semantics — registrations
   are deliberately lifecycle-free and irrevocable, while a specification
   must be correctable. A separate semantics ledger was rejected because
   reference closure to `vrg` is enforced in-collection only and could not
   be verified across ledgers, producing a second model-truth ledger and a
   fourth revision id.
2. **The record specifies value representation only**: accepted value
   shape, optional model-unit identity, nullability, authority, evidence,
   lineage. Quantity kind and semantic kind are deferred to a future,
   separate record kind rather than a field, because field addition after
   the first append is impossible. The class is named
   `VariableValueSpecification` rather than `VariableSpecification` so it
   cannot be read as specifying the variable's meaning.
3. **Competing current specification tips surface as `conflicted`; they do
   not invalidate the revision.** Mirroring the accepted single-parent
   type-lineage rule was rejected after demonstration: once two tips exist
   on disk, `load()`, every query, and full replay all fail, and no append
   can repair it because a single-parent `supersedes` cannot supersede both
   tips. Surfacing matches the accepted doctrine (contention is surfaced,
   malformation invalidates) and costs nothing, since nothing else in the
   kernel cites specifications.
4. **The lineage is a multi-parent DAG from its first committed version.**
   `supersedes: tuple[str, ...]` is sorted and deduplicated by a validator
   that runs before the digest, so parent order is not part of identity but
   the parent *set* is. A record superseding every current tip converges a
   conflict; a record superseding only some remains a competing tip. This
   makes conflicts convergent under repeated contention, which a
   single-parent field cannot be.
5. **`integer` is not a value shape in VS-001.** The accepted pipeline
   classifies integers and decimals alike as JSON `number` and
   canonicalization erases the distinction (`1e0` → `1`, `6e2` → `6E+2`),
   so a lexical integer verdict would describe the normalized
   representation rather than the source's numeric category.
6. **Units are project-local identity tokens with a required edition**,
   compared byte-exactly, and only ever yielding a *lexical* relation.
   UCUM was not adopted: its grant is revocable and forbids derivative
   works, which is a poor fit for identifiers written into an append-only
   ledger correctable only by supersession. QUDT (CC-BY 4.0, IRIs) remains
   the better licensed option if an external system is ever needed;
   `system_id` is a widenable `Literal` so either can be added later
   together with its edition semantics.
7. **Compatibility is a new read-only package**,
   `backend/observation_compatibility/`, composing the kernel specification
   query and the VM-001 result **verbatim** rather than re-expressing
   either. It constructs `ModelQueries(state.model)` from the exact public
   `LoadedModel` the injected `ModelStateQueries` uses, so a
   model/specification revision mismatch is unconstructible, and it never
   implements a second specification-status vocabulary.
8. **Shape and unit are independently gated.** Evidence consistency gates
   only the shape verdict; a malformed `value_json` never erases an
   explicitly supplied source-unit string, and source-unit evidence is
   disclosed whenever an observation exists, including for unattached
   candidates. Each dimension carries its own not-evaluated reason with its
   own precedence chain.
9. **Evidence that is internally contradictory is not incompatibility.**
   `json_type` and `value_json` are cross-checked by strict parse; a
   disagreement is reported as inconsistent evidence, neither field is
   repaired, neither is preferred, and no verdict is computed.

## Consequences

- One `mrv_` revision covers membership and specification, so
  reproducibility does not gain a fourth revision id.
- "Which specification is current" becomes a computed graph property over
  the selected record collection: a reference-closed replay subset that
  omits a successor revives an older specification as the tip. This is
  coherent under "a revision is a knowledge context" and is pinned by test.
- The kernel gains a `unit.code` string. It names what the model requires
  and never what a source supplied; no source locator or observed value
  enters the kernel, and the committed-ledger vocabulary sweep continues to
  enforce that.
- Every unit-comparison outcome is unreachable on real committed data,
  because no producer in the repository sets a non-`None` `declared_unit`.
  The real demonstration therefore reports a declared model unit, absent
  source-unit evidence, and no lexical relation — which is the honest
  answer.
- The accepted `RelationshipTypeDefinition` single-parent lineage remains
  non-convergent. VS-001 does not touch it; it is recorded as a separate
  pre-existing concern.
- A future authority-backed source-property interpretation record remains
  out of scope, with its home pre-decided as a new sibling ledger.
