# ADR-0012 — Explicit variable constraints and evidence-gated evaluation

Status: accepted (owner, 2026-08-15, Slice A). Spec:
`docs/superpowers/specs/2026-08-15-cn001-explicit-variable-constraints-and-evidence-gated-evaluation-design.md`.

## Context

ES-001 (ADR-0011) unlocked CN-001: a constraint record can name its subject
by declared meaning; a constraint evaluator gains a semantic admission gate
(attached + satisfies_value_shape + declared_semantics_compatible, every
prerequisite traceable to records); and an honest refusal vocabulary.
Everything evaluative (ranges-as-safety, alarms, conversion, diagnosis)
remained forbidden. CN-001 executes that unlock as two owner-gated slices:
Slice A (the model-kernel foundation) and Slice B (the read-only evaluator
facade). A prior provisional synthesis deferred an opaque constraint anchor
and validated the lock at append; the owner correction pass and the
`ConstraintRegistration`-evidence amendment reversed both.

## Decisions

1. **A constraint identity is a canonical `ConstraintAnchor`** in
   `backend/system_identity/` (prefix `con_`, uuid4 hex), a pure identity
   value with no target, unit, predicate, or severity — mirroring
   `EntityAnchor`/`VariableAnchor`. It is minted through the **first public
   UUID4 minter** in `system_identity` (`mint_constraint_anchor`) and first
   persisted by `ConstraintRegistration`. The provisional "lineage-key-as-
   identity, no opaque anchor" option (RE1) is overridden: the anchor is the
   identity; the target variable lives on the registration, not the anchor.
2. **`ConstraintRegistration` (prefix `crg_`) is a permanent, evidence-bearing
   membership claim** (the amendment, overriding the membership-only-envelope
   precedent of entity/variable registrations): one constraint identity
   targets one variable, with nonempty `EvidenceRef` evidence, canonicalized
   and closed by the uniform rules. It has no `supersedes`, withdrawal, or
   lifecycle field — the association must not become an unsupported model fact
   when a declaration is later superseded.
3. **`VariableConstraintDeclaration` (prefix `vcn_`) is the correctable numeric
   claim.** Its lineage key is the `con_` anchor; lineage invariants are the
   anchor, the target variable, the semantic lock (quantity kind, observation
   role), and the predicate's unit and operator — only the `threshold` may
   change across a supersession. The DAG is the accepted multi-parent
   three-colour form; competing tips are `conflicted`, never resolved.
4. **The lock is not validated against `vsm`/`vsp` at append** (the accepted
   "kernel does not cross-validate" discipline, confirmed structurally for
   `vsp` vs `vsm`). The kernel validates intra-collection consistency
   (declaration↔registration target, declaration lineage invariants) but not
   the lock against declared semantics; a lock mismatch surfaces at
   evaluation (Slice B) as `not_evaluated`, never as an append-time rejection.
   The provisional "validate the lock at append" option (RE2) is overridden.
5. **The v1 predicate is a single `ScalarComparisonPredicate`** with six
   operators against one `CanonicalDecimal` threshold. A two-sided range is
   two independent constraints (two anchors), never an interval predicate;
   `interval`, `between`, `tolerance`, and `severity` are forbidden in v1.
6. **`CanonicalDecimal` is a strict, bounded plain-number grammar** (128
   digits each side; accepts negative fractions; rejects negative zero,
   exponents, whitespace, aliases, and trailing fractional zero). Any accepted
   string is already canonical, so the content-derived record id is
   deterministic and the `Decimal.normalize()` exponent trap never arises.
7. **Both CN record kinds use the accepted kernel envelope** (`record_kind`
   Literal+default, `schema_version: Literal["1"]="1"`, `recorded_at:
   UtcDatetime`, `note: str=""`, the global kernel `_Frozen` with no
   `revalidate_instances` override). `record_kind` is part of the content
   hash. The committed CN fixture carries the full synthetic disclaimer in
   `OwnerDeclarationEvidence.statement` and may repeat it in its `note`.
8. **Both CN evidence-bearing record kinds receive uniform evidence closure**
   (`_check_model_record_evidence`): each `model_record` evidence arm must
   name a member of the supplied collection, at prospective append, complete
   load, and explicit replay alike. Foreign evidence arms remain declared
   references.
9. **Constraint discovery is a `status`-bearing structured result**, never an
   exception for absence: `registered` vs `not_registered` (of the variable),
   with an empty `constraints` tuple in both empty cases (unregistered, and
   registered-with-no-constraints) — the accepted structured-absence pattern.
   Both `ConstraintDeclarationResult` and `VariableConstraintCollectionResult`
   carry the **complete `ModelRevision`**; validators prove every carried id
   belongs to `revision.record_ids`.
10. **The evaluator (Slice B) carries the accepted ES result exactly once**
    (CM3): it adds no second `CandidateSemanticCompatibility` or
    `CandidateValueCompatibility` copy; the ES contract's internal verbatim
    carriage of the VS result is outside CN-001's scope. CN reads
    `es_result.value_compatibility` and `es_result.candidates[i].value_candidate`.
11. **The admission precedence is single, reachable, and non-duplicative**
    (Slice B): CN relies on the complete carried VS/ES result for detailed
    lower-layer refusal causes; it never dereferences model tokens until
    `declared_semantics_compatible` proves the necessary declarations are
    positive. `numeric_value_malformed` is removed (impossible after VS reports
    consistent number-shaped JSON); `numeric_value_out_of_bounds` is retained
    (CN adds narrower resource limits than VS). `CanonicalObservedDecimal`
    preflight-checks exponent expansion before allocation; never `float` or
    ambient `Decimal` context; the VS strict parse helper and standard-JSON
    whitespace handling are reused; the original evidence is preserved.
12. **The vocabulary is honest by construction**: `satisfied` / `violated` /
    `not_evaluated` only. None connotes safety, normality, fault, alarm,
    diagnosis, recommended action, or control. No `severity`/`grade`/`normality`
    /`alarm`/`recommendation`/`cause` field exists, ever.

## Consequences

- The model kernel gains two record kinds, two buckets, five immutable
  indexes, one query, and three result contracts; the accepted `mrv_`
  revision admits `crg_`/`vcn_` with no new revision id; no accepted module
  outside `system_identity` / `model_kernel` changes.
- `identity_binding` is unchanged — CN-001 adds no binding declaration, no
  ledger change, no behavior extension.
- The committed demonstration grows 16 → 17 records (one `crg_`, one `vcn_`),
  all 16 pre-CN-001 records byte-frozen; the demonstration records are not
  appended in Slice A.
- Slice B composes the accepted VS + ES results plus the Slice A
  `variable_constraints` query to produce `satisfied` / `violated` /
  `not_evaluated` per (constraint, candidate), with no aggregation, ranking,
  conversion, or LLM judgment.