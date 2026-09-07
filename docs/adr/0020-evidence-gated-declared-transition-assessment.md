# ADR-0020 — Evidence-gated declared transition assessment

Date: 2026-09-07

Status: TA-001 design and Slice A owner accepted; Slice B adversarial hardening
and final verification authorized; final TA-001 acceptance pending

Authoritative design:
[`docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md`](../superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md),
SHA-256
`3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd`.

The pre-correction accepted digest
`99db3b31f5fa94eb119b32529784a64aff08c604f71ee9eb7530225963816062`
remains historical evidence. The bounded finite-float and T43 correction is
recorded in
[`docs/superpowers/reports/2026-09-07-ta001-slice-a-contract-correction-and-owner-resolution.md`](../superpowers/reports/2026-09-07-ta001-slice-a-contract-correction-and-owner-resolution.md).

Owner approval:
[`docs/superpowers/reports/2026-09-07-ta001-final-design-owner-approval.md`](../superpowers/reports/2026-09-07-ta001-final-design-owner-approval.md).

## Context

ST-002 can declare a directed transition possibility, ST-001 can classify one
declared state at one cutoff, and EA-001 can content-bind and align governing
operational evidence. None of those contracts answers whether two exact
endpoint classifications, backed by complete aligned evidence, support the
declared endpoint pattern across an ordered pair of cutoffs.

## Accepted design decisions

1. **TA is a pure leaf composition.** The
   `backend.transition_assessment` package consumes only public
   model-kernel transition-declaration, state-classification, and
   evidence-alignment results, plus Pydantic and the standard library. It will
   own strict reconstruction and pure derivation only. No existing package
   will import TA.

2. **There is no orchestration facade.** Callers remain responsible for
   producing per-condition classifications, EA selections, alignments,
   horizons, cutoffs, and independently retained expected fingerprints. TA
   will perform no store lookup, source reread, temporal query, evidence
   reselection, network access, write, clock read, or environment discovery.

3. **The join is complete and exact.** One request carries one transition
   declaration result, ordered from/to state-classification results, and one
   bounded exact collection of distinct evidence-alignment results. Exact
   anchors, context, subjects, cutoffs, model revisions, condition traces,
   complete value-compatibility objects, alignment candidates, and governing
   occurrences must agree. Semantic and value candidate indices remain
   separate provenance coordinates even where valid lower results make their
   numeric values equal; a forged divergence rejects.

4. **Execution uses a strict evidence gate.** Every governing observed
   condition must have complete EA horizon coverage, complete occurrence
   alignment, structurally self-consistent snapshot validation, an
   independently supplied expected fingerprint, and relation `matched`.
   Positive and negative conclusions use the same gate. Incomplete or absent
   fingerprint evidence prevents execution without being rewritten as a
   transition conclusion.

5. **Temporal views are not a cohort.** The from cutoff must be strictly
   earlier than the to cutoff. Each state retains independent
   latest-per-condition selection; receipt time, source-effective coverage
   time, source-native time, and clock segments retain their accepted separate
   meanings. TA establishes no simultaneity, continuity, dwell, interval, or
   traversed path.

6. **Public conclusions are deliberately bounded.** The strongest conclusions
   are bounded evidence support or bounded evidence non-support for the
   declared endpoint pattern. Neither asserts transition occurrence or
   non-occurrence, event identity, causality, trigger, guard, action, effect,
   physical truth, correctness, safety, diagnosis, recommendation, or control.

7. **Admission limits are fixed and aggregate.** The accepted limits are
   exactly 134,217,728 canonical-request bytes, 200,000 reconstructed graph
   nodes, and nesting depth 128, alongside the design's condition/alignment
   cardinalities. Iterative preflight enforces node, depth, scalar, container,
   and preliminary byte bounds before plain copying, canonical serialization,
   lower reconstruction, equality, fingerprint work, or derivation. Shared
   acyclic content counts once per serialized occurrence.

8. **Reconstruction is authoritative and deterministic.** Every public input
   and result boundary reconstructs the complete nested content, rejects
   cycles, hidden state, hostile scalars, wrong union arms, boolean/invalid
   indices, reordered or substituted collections, stale derived fields, and
   forged result combinations. Result validation recomputes all joins, traces,
   issues, relations, execution state, and conclusion without I/O.

9. **The package has no facade or demonstration.** TA-001 v1 ends with
   contracts, one public pure assessment function, adversarial hardening, and
   verification. Positive worlds remain disposable temporary test data. No
   committed fixture, result artifact, model/ledger append, second consumer,
   or authoritative demonstration is part of the milestone.

## Consequences and implementation gate

The accepted design can distinguish structural/declaration admission,
endpoint classification, evidence completeness, fingerprint relation,
execution, and bounded conclusion without collapsing them into occurrence.
It preserves historical replay because every result derives only from carried
public material; later store or ledger changes do not rewrite it.

Slice A implements the exact contracts, bounded reconstruction, pure
derivation, authoritative revalidation, tests, and package documentation. It
is adversarially reviewed and owner accepted at exact tested implementation
`76738ac0d098eb59b0fec4f6970aa862528647d9`. Slice B adversarial hardening and
final verification are authorized. Any later discrepancy in accepted joins or limit enforcement
must stop for a bounded contract decision rather than read private lower
fields or silently weaken the design.

END OF ADR-0020
