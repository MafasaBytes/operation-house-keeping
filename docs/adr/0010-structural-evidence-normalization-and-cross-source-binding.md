# ADR-0010 — Structural evidence normalization and cross-source model binding

Status: accepted (owner, 2026-08-11). Spec:
`docs/superpowers/specs/2026-08-11-sn001-structural-evidence-design.md`.

## Context

The repository can independently ingest CSV BOM evidence (DS-001), STEP
assembly evidence (DS-002), PDF evidence (DS-003), and operational
Moonraker evidence (DS-004). It maintains canonical anchors
(`system_identity`), an explicit identity-binding ledger
(`identity_binding`), a typed model kernel (`model_kernel`), a rebuildable
temporal projection (`temporal_state`), a bound model-state facade
(`model_state`), and observation compatibility
(`observation_compatibility`).

The structural sources do not converge on the model kernel. The committed
`models/demo-printer/` model is hand-authored synthetic model truth; it is
neither derived from nor explicitly reconciled with the committed BOM or
STEP evidence. SN-001 closes that gap without turning extraction into
engineering truth.

Three things must never silently collapse into one another:

1. what the source bytes and extractor actually reported;
2. how an identified authority interpreted and mapped that report;
3. what was separately accepted into a model revision.

## Decisions

1. **Structural source→anchor mappings are ordinary `BindingAssertion`
   records in `identity_binding`.** SN-001 defines no mapping record kind,
   no second identity ledger, no anchor-bearing record, no new revision
   namespace, and no parallel resolution vocabulary; `ResolutionResult` and
   `BindingRevision` are carried verbatim. *Rejected:* a mapping ledger
   inside the new module. ADR-0006 D1 makes `identity_binding` the answer
   to "which canonical entity does this source-native subject represent";
   ADR-0008 D3(c) rejected source locators in the kernel because "it would
   be a second, worse binding ledger"; ADR-0009 D1 rejected a second ledger
   because cross-ledger reference closure cannot be verified, "producing a
   second model-truth ledger and a fourth revision id". A structural
   `BindingAssertion` is constructible today with zero contract change
   (measured).

2. **A new payload-pinned `StructuralAddress` is defined in
   `backend/structural_evidence/`, used only as an evidence address and
   never as an identity.** `SourceSubjectRef` carries no `raw_record_id`
   and no `payload_checksum` and structurally cannot say "row 3 of *these*
   bytes"; `SourcePropertyRef.json_pointer` is an RFC-6901 pointer into a
   JSON document, and a pointer invented for a CSV or Part 21 payload would
   address a derived pydantic serialization rather than the source.
   *Rejected:* overloading either accepted locator.

3. **Subject identity is produced by versioned subject-identity rules whose
   fingerprint is part of the subject namespace.** `CLAUDE.md` assigns this
   decision here verbatim: extraction "must not decide by itself that
   column `Item No.` is the platform's canonical component identity. That
   decision belongs to the later normalization and identity-resolution
   layer." A rule is *adopted* by the authority who writes a
   `BindingAssertion` using its grammar; that adoption record already has
   authority, applicability, supersession, retraction, and a revision id.
   *Rejected:* an SN-001 rule ledger (a fourth revision id).

4. **`sx1` is the version of the complete subject-generation semantics** —
   namespace grammar, `apply_rule`, missing-value behaviour, field
   selection, comparisons, subject-value encoding, percent encoding, and
   the normalization policy, which is *none*. Any behaviour change to those
   mechanics requires `sx2` or later and therefore creates a new identity
   domain requiring explicit new mappings. Rule *data* changes are
   content-addressed and necessarily create a new namespace; changes to the
   shared interpreter or encoder are guarded by a versioned algorithm
   contract, hand-authored behaviour vectors, and implementation-drift
   tests. This is enforced by tests and review, not by construction alone,
   and the design says so. *Rejected:* an embedded expression evaluator.

5. **The runtime module owns no authoritative store, no ledger, and no
   revision id.** Results and proposals are computed and returned, never
   persisted. The milestone nevertheless produces durable committed
   artifacts — frozen showcase sources, their manifest, their frozen
   extraction results, versioned rule definitions, and hand-authored
   binding and model records. Committed showcase derivatives are **test
   artifacts, not engineering truth or runtime authority**. This satisfies
   ADR-0008 D2's read-only composition-facade pattern.

6. **The engineering context is SN-001-local, with a first-class `unknown`
   and no default anywhere.** `AssertionContext` has no `unknown` member,
   and `view_independent` is a positive claim, not absence of knowledge —
   the same distinction `identity_binding` already draws between
   `UnboundedBoundary` and `UnknownBoundary`. A claim whose context is
   unknown can never be materialized. *Rejected:* adding `unknown` to
   `AssertionContext`, which would invalidate
   `RelationshipTypeDefinition.context_requirement`'s two-value `Literal`.

7. **STEP assembly structure materializes only through a new, separately
   hand-authored `assembly_definition_contains` type with
   `type_definition → type_definition` endpoints.** It is a second,
   non-merging containment lineage, queried only by explicit type name, and
   is never presented as "the hierarchy". The committed `contains` type
   excludes `type_definition` from both endpoint kind sets, and
   `ComponentInstance.parent_definition_ref` names a *definition*; the
   escapes — registering CAD definitions as `physical_instance` or
   `logical_instance`, or flattening usages into per-path instances — are
   all hidden inference. STEP extraction never creates the relationship.

8. **Findings carry a mandatory `basis` validated against a frozen table,
   and every basis gates its own support.** `source_claim` requires
   non-empty supporting claims; `authority_interpretation` requires
   non-empty supporting resolutions; `accepted_model_record` requires model
   disclosures verified against the supplied revision. A result-level
   validator additionally proves every support item *is* one of the
   disclosed input objects, so a finding and its proof cannot be
   constructed independently.

9. **A generic `sources_disagree` finding is rejected.** Disagreement
   without a comparator definition is unfalsifiable. Two explicit
   comparators are defined; absence, a missing mapping, or a one-sided
   claim is never disagreement. Quantity lexemes are never numerically
   normalized, and a STEP usage count is never expressed as a source
   quantity lexeme.

10. **One additive `EvidenceRef` union arm,
    `StructuralSourceLocatorEvidence`, is added to the kernel.**
    Measured: all committed model record ids verify byte-for-byte under the
    extended union and `mrv_25afc0eb…` is unchanged, because
    `canonical_payload` dumps the *instance*, not the schema. ADR-0009 D1's
    measured breakage was about **field** addition and does not transfer.
    *Rejected:* adding an `evidence` field to `EntityRegistration`, which
    breaks all four committed `reg_` ids even when defaulted empty.

    **This does not reverse ADR-0008 D3(c).** That decision rejected
    storing a source locator in a *registration*, as identity or binding
    knowledge. This arm adds an immutable evidence **citation** to a
    relationship assertion. The citation cannot resolve source identity, has
    no lifecycle and no applicability, cannot discover or replace a
    `BindingAssertion`, and remains `verification="declared_reference"`
    unless an explicit supplied context verifies it. Registrations and
    value specifications continue to carry no source-locator or binding
    knowledge at all.

11. **Structural mappings are appended to the existing binding sets, chosen
    by anchor ownership.** `identity_binding` fails a set whose assertion
    targets an anchor declared elsewhere, and validation is all-or-nothing,
    so the set is *forced*, not chosen: both extruder-targeting mappings
    (the BOM row and the STEP extruder definition) go to
    `bindings/demo-printer/`, the set that declares `ent_a3f1c2d4…`; the
    assembly-type mapping goes to `bindings/demo-printer-model/` beside its
    new anchor declaration. No anchor is redeclared to force one set.
    Reconciliation therefore accepts an **ordered collection of
    resolvers**, queries every resolver for every subject, carries every
    participating revision verbatim, canonicalizes its result independently
    of caller order, and never selects a preferred set.

    **Binding a STEP part definition to a physical-instance anchor does not
    reverse decision 7.** Decision 7 forbids *registering* a CAD definition
    as a `physical_instance` or `logical_instance` — a layer-3 act. The
    mapping is a layer-2, hand-authored, unauthenticated authority claim
    that the definition *represents* the already-registered physical
    extruder in the source's vocabulary: it creates no registration,
    changes no referent kind, and is correctable by supersession or
    retraction. The registration form remains forbidden.

12. **Structural model records append to `models/demo-printer/`.** The
    directory name is the `model_id`; a new directory would be a *different
    printer model*, not a later knowledge revision of this one. Every
    historical revision remains provable by `replay()` from an explicit
    record-id list. A prefix filter is never an acceptable membership
    selector, because a later append silently changes what it selects.

13. **The committed structural fixtures are the negative corpus and are
    never joined by names.** Their only overlap is `Bolt M6` ↔ `bolt-m6`,
    a name similarity — exactly the evidence this design forbids as
    identity. A new generated-and-frozen `showcases/demo-printer/` carries
    the positive path, with a frozen `ExtractionResult` so the milestone is
    verifiable in the base-only column.

## Consequences

- No fourth revision id. The reconciliation result carries an
  `inputs_digest` (`sid_`) which is an **input fingerprint**, not a
  revision: it has no membership tuple, no ledger, is structurally excluded
  from both record-id patterns, and is not citable as evidence.
- A model record cannot, by itself, name the ingestion source: `source_id`
  is deliberately absent from the evidence arm, because it is binding
  knowledge. The `iba_` record the assertion also cites carries it. Two
  hops, and neither is kernel-verified.
- An accepted entity registration cannot cite its structural derivation at
  all. The link is one-directional: the relationship assertion cites the
  structural locator; the registration cites nothing, and `note` is never
  used as a pointer.
- STEP-derived identifiers are stable for a fixed extractor build. The OCCT
  toolchain version is not part of `derive_entity_id`'s material, so the
  toolchain fingerprint is carried explicitly in both the subject namespace
  and the evidence citation: a toolchain change produces a *different
  identity domain* rather than a silently re-pointed mapping.
- `assembly_definition_contains` adds a second containment lineage. Every
  hierarchy query is per `(type_name × view)`, so the lineages cannot merge,
  but a reader who asks for the wrong type name gets a different tree.
- SN-001 mints no `ent_`, `var_`, `reg_`, `rel_`, `rtd_`, or `vrg_`/`vsp_`
  identifier. The upstream `definition_id`/`instance_id` values produced by
  `derive_entity_id` are **extractor-local identifiers**, never canonical
  system entity anchors, and are named `upstream_*` throughout.
- One genuinely new canonical identity is introduced: a single
  hand-authored `type_definition` anchor for the printer assembly type,
  declared once, registered by an append-only record, labelled synthetic
  showcase knowledge, and never described as a real printer component.
