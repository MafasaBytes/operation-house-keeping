# ADR-0011 — Engineering semantics in the kernel; source-property interpretation as a sibling ledger; compatibility as composition

Status: accepted (owner, 2026-08-13). Spec:
`docs/superpowers/specs/2026-08-13-es001-engineering-semantics-design.md`.

## Context

VS-001 proved what the model *requires* a variable's value representation
to be, and whether an attached observation's supplied representation is
compatible. It deliberately could not say what physical quantity the
variable represents, whether the exact source property represents the
same quantity, whether an absent source-unit string has a separate
authority interpretation, or whether source-property meaning and
model-variable meaning are compatible. ADR-0009 deferred quantity kind
and semantic kind to a future, separate record kind, and pre-decided the
home of a source-property interpretation record as a new sibling ledger.
ES-001 executes both deferrals. The design passed a four-specialist
design turn plus an owner correction pass; ten adversarial findings
(F1–F10) were adjudicated into the accepted spec (its §14).

## Decisions

1. **Model-side engineering meaning is a seventh kernel record kind**,
   `VariableSemanticDeclaration` (prefix `vsm`), with a discriminated
   per-dimension body (quantity kind; observation role) and a
   multi-parent correction lineage keyed by `(variable_anchor_id,
   dimension)`. Field enrichment of an accepted record kind was rejected
   on ADR-0009's measured id breakage; a separate model-semantics ledger
   was rejected because reference closure to `vrg` is enforced
   in-collection only and a second model-truth ledger would add a fourth
   revision id for an existing truth domain. Per-dimension lineage was
   chosen over a monolithic record (correcting the role must not
   re-litigate the quantity, and a conflict on one dimension must not
   conflict the other) and over two record kinds (duplicate machinery).
2. **Source-property interpretation is a new authoritative sibling
   append-only ledger**, `backend/source_interpretation/`, repository
   root `interpretations/`, executing ADR-0009's pre-decision. Records
   are keyed by the exact six-dimension (SourceSubjectRef,
   SourcePropertyRef) pair carried verbatim, carry `AppliesScope`
   applicability on the ingestion-receipt axis, and never reference an
   anchor: identity binding remains the only property-to-variable
   authority. Rejected homes: identity_binding (semantics in the
   identity ledger), the temporal projection (disposable, derived),
   runtime configuration (unauditable, unreplayable).
3. **Interpretation supersession is a multi-parent convergent DAG**
   (owner correction of the earlier single-parent draft): parents must
   share the exact six-dimension pair and semantic dimension; competing
   current tips surface as `conflicted` with every candidate carried;
   a successor superseding every tip converges; partial convergence
   remains conflicted; parent SET is identity; replay is
   membership-relative and may revive an earlier tip; nothing is ever
   selected by recency, authority, record id, or order.
4. **The interpretation store uses VALIDATING append for every record
   kind** (adjudication F1): the prospective collection is validated
   before any write, so duplicate closures and dangling lifecycle
   targets are refused at append time and no reachable on-disk state can
   permanently poison `load()`. Crafted on-disk states still fail load
   all-or-nothing. This is the kernel's append discipline, chosen over
   identity_binding's record-local append because interpretation records
   form a referential lifecycle graph.
5. **The rejection record `InterpretationRejection` (`spj`) is
   diagnostics-only** and never an input to resolution (the accepted
   `BindingRejection` doctrine). It identifies the considered candidate
   completely (six-dimension pair, rejected body, proposed scope,
   authority) and carries no `spi` reference: it cannot reject an
   accepted assertion — retraction handles withdrawal. No `spj` record
   is committed to the demo set.
6. **Vocabulary tokens are project-local identities with editions**
   (`QuantityKindReference`, `ObservationRoleReference`, mirroring the
   accepted `UnitReference` triple; editions `ohk-quantities-1`,
   `ohk-observation-roles-1`). Closed kernel literals rejected (ontology
   slide); vocabulary record kinds rejected as scaffolding until tokens
   acquire validatable semantics. Byte-exact triple comparison only;
   never physical equivalence. "Unknown" is not a token — absence of a
   record is the computed status.
7. **Compatibility is a new read-only package**,
   `backend/semantic_compatibility/` (ruleset `es001.1`), composing the
   VS-001 result whole and verbatim, building `ModelQueries` per call
   from the exact injected `LoadedModel`, and injecting one
   `InterpretationResolver` — so model/meaning and per-candidate
   interpretation revision mismatches are unconstructible. Three
   knowledge contexts (model, binding, interpretation revisions) are
   disclosed per result, never merged.
8. **Dimensional verdicts are the authoritative result; the findings
   tuple is a derivation.** Quantity kind, observation role, and unit
   identity each carry an evaluated verdict XOR a not-evaluated reason
   with its own precedence chain; `semantic_findings` is a
   deterministic, validator-locked, total derivation from those fields
   and carried evidence — never an independent aggregate status.
9. **Semantic verdicts gate on evidence consistency** (adjudication F2,
   aligning with ADR-0009 rule 9): internally contradictory evidence
   yields `evidence_not_assessable` reasons and no verdict, so
   `declared_semantics_compatible` can never co-occur with
   `evidence_inconsistent`. A differing source-supplied unit *lexeme*
   deliberately does NOT withhold `declared_semantics_compatible` — the
   lexeme has not been interpreted as a unit identity, and granting an
   untyped string veto power would manufacture semantics from a lexeme —
   but `interpreted_unit_lexeme_differs_from_source` is then mandatorily
   co-emitted with the VS-001 lexical result carried verbatim.
10. **The vocabulary is honest by construction** (adjudication F3/F4):
    `unit_identities_differ_conversion_not_attempted` (never emitted
    without `unit_identity_mismatch`) replaces any wording implying a
    conversion is required or possible;
    `interpreted_unit_lexeme_differs_from_source` replaces any
    contradiction claim; `model_specification_not_available` and
    `model_specification_conflicted` are first-class findings so a
    missing specification is never conflated with a declared
    `UnitNotDeclared`.
11. **Interpretation resolves at each occurrence's own `received_at`**,
    exactly like identity binding — never at `as_of`, never at an
    execution clock; no observation means no resolution and no fallback.
    Model-side records carry no applicability interval (supersession
    plus explicit revision selection); source-side interpretations do —
    a deliberate, documented asymmetry.
12. **One bounded repair to accepted behavior** (owner-mandated,
    adjudication F6): evidence-reference closure becomes uniform across
    every evidence-bearing model claim (`rel`, `vsp`, `vsm`) — every
    `ModelRecordEvidence.record_id` must belong to the supplied
    collection, typed `MODEL_REFERENCE_INVALID`, demonstrated failing
    for `vsp` before the fix; committed ledgers and ids are provably
    unaffected. Foreign evidence arms remain declared references.
13. **One accepted-surface promotion** (owner-authorized):
    `identity_binding.resolver.membership(scope, at)` becomes a
    documented supported pure helper with zero behavior change, pinned
    by behavior vectors; the interpretation resolver imports it rather
    than copying the algorithm. The surrounding eight-case
    classification is restated (the accepted implementation is private)
    with shared behavior vectors pinning parity.
14. **The `irv_` revision namespace is legitimate and domain-tagged**:
    `sha256("interpretations\n" + set_id + "\n" + join(sorted(ids)))`.
    The earlier "no fourth revision id" rejections targeted duplicate
    ledgers for existing truth domains; this ledger is a pre-approved
    new knowledge domain, and a replayable authoritative ledger owns its
    membership identity.
15. **Aggregate interpretation `superseded` is removed as unreachable**
    (owner-mandated Group-13 correction). Every finite, reference-closed,
    acyclic supersession DAG has at least one current tip. If a declared
    lineage has no active assertion, each tip is retracted: a root/tip-only
    retraction resolves `retracted`, while superseded ancestors plus a
    retracted tip resolve mixed-history `inactive`. Supersession remains
    fully disclosed per assertion (`superseded_by`, `active=False`, lineage
    history, and replay), but is not an aggregate status, semantic reason,
    or finding. The committed ledgers and canonical identities are
    unaffected.

## Consequences

- Every ES-001 result carries three knowledge contexts (model revision,
  binding revision, interpretation revision) plus `as_of` and the
  ruleset id — the full reproducibility tuple.
- The committed demonstration extends the accepted hotend/Moonraker
  chain: models/demo-printer 14→16 (two `vsm` records),
  interpretations/demo-printer 0→3, binding sets unchanged, every
  historical revision still replayable from explicit id lists, every
  pre-existing record byte-identical (freeze maps completed to all
  14 + 11 before the appends).
- `declared_semantics_compatible` asserts declared-token agreement under
  an exact eight-clause condition and nothing else; CN-001 may later use
  it as an admission gate, and everything evaluative (ranges, limits,
  alarms, conversion, diagnosis) remains forbidden and absent.
- `TemporalOccurrence.declared_unit=None` stays byte-true everywhere;
  the authority-interpreted and model-required units are disclosed in
  their own subtrees and never presented as source-supplied.
