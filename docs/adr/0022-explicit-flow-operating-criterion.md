# ADR-0022 — Explicit flow operating criterion

Date: 2026-09-09

Status: complete; owner accepted; adversarially hardened; dual-clean-checkout verified

Exact tested implementation: `9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`.

Authoritative [corrected synthesis](../superpowers/specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md)
SHA-256 `7aa5007058c1733720fc624839c19efd98258c800c67461d1afc5ade674a3453`.
The [owner approval](../superpowers/reports/2026-09-09-fc001-final-design-owner-approval.md)
also records the execution clarification preserving historical support.

## Context

FM declares measured-actual relevance, and CN evaluates a variable predicate.
Neither designates which constraint governs an exact flow-measurement meaning.
The commissioning/operations workflow needs a durable, replayable authority
choice so a satisfied ungoverned criterion cannot substitute for a violated
governing one. This missing relation, not a vacancy in the roadmap, justifies FC.

## Decision

1. Keep FC in `backend.model_kernel`, extending its existing ledger/revision.
   Add only `FlowOperatingCriterionDeclaration` (`fcd_`) and
   `FlowOperatingCriterionWithdrawal` (`fcw_`); no anchor, minter, registration,
   sibling store, evaluated state or upper-layer import.
2. Govern exact FM effective body B through the explicitly stored, retained,
   membership-present FMA witness. Body equality excludes witness identity,
   evidence, authority and ancestry, but record identity retains them. Never
   silently select or substitute a witness. Another healthy active equal-body
   assertion can supply endorsement after the witness becomes non-current.
3. Use exact immutable FM subject S as correction key, with one governing slot.
   Same-root forks conflict even for equal bodies; independent equal bodies
   corroborate; active disagreement blocks later applicability; inactive roots
   remain disclosed without veto. Multiple real requirements are unsupported,
   not contradictory, and cannot be hidden in artificial contexts/orientations.
4. Pin exact CRG and VCN editions. No predicate equivalence, floating to latest
   or automatic migration. An identical-looking VCN correction still requires
   explicit renewal for present applicability.
5. Structural admission validates exact support/evidence/parent closure and
   canonical IDs but retains valid historical support. Present eligibility
   requires current, healthy, aligned exact FLD/VPA/VSM and selected PCN/PIF
   editions only in Slice B. This is local selected-model policy, not global
   FL agreement, physical connectivity or truth. VSM stays context-independent.
6. Positive records carry nonempty evidence and authority. Withdrawal is
   evidence-free, uncitable, targets one eligible positive tip and does not
   assert falsity. Parents preserve S and one root; withdrawn parents cannot
   acquire successors. Closed historical replay may revive a withdrawn tip
   when its withdrawal is omitted, but may never omit a retained witness.
7. Slice A adds records, bounded canonical/store reconstruction, DAG/replay and
   twelve immutable indexes only. Its ordered exports are exactly 227: the
   accepted 225-name prefix followed by the two records. Slice B queries,
   result contracts, applicability vocabulary and direct-join proof require
   separate owner acceptance and authorization.
8. The eventual result proof boundary remains public carried-result coherence,
   not source authentication. Disposable software worlds suffice; no append to
   the zero-FMA authoritative 36-record model is authorized.

## Alternatives and consequences

Existing generic relationships have entity endpoints and cannot express exact
FMA/VCN closure. Extending VCN or FMA changes accepted record meaning and bytes.
A sibling ledger adds duplicate model authority; presentation selection or an
external procedure is legitimate but does not supply the selected model-centric
replay contract. Exact-record dependence would privilege ongoing witness
endorsement contrary to the approved body policy. A new anchor is unnecessary.

FC supplies designation, never evaluation, observed physical flow, state,
occurrence, continuity, conservation, causality, correctness, safety, diagnosis,
planning, recommendation or permission. It directly advances explicit model
relations and provenance distinction; it does not provide causal explanation,
next-best-test optimization, impact propagation or control.

FA stays deferred during FC and must be cancelled after a successful accepted
FC/CN/evidence direct-join proof. Reconsideration requires a new owner-approved
proposal demonstrating an attack existing explicit public-result checks cannot
prevent. No identified attack currently qualifies; API convenience, one status
or smaller carriage is insufficient. No successor milestone is authorized.

END OF ADR-0022
