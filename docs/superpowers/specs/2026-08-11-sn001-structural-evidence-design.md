# SN-001 — Structural Evidence Normalization and Cross-Source Model Binding

Accepted by the owner on 2026-08-11 after two design gates, three specialist
studies, an architect synthesis, two adversarial reviews, and a final ruling
set (K1 waiver, D1–D12, K2–K11, O1, O2, toolchain-identity correction). This
document is the implementation contract. ADR:
`docs/adr/0010-structural-evidence-normalization-and-cross-source-binding.md`.

## The question SN-001 answers

> Given committed BOM and STEP evidence that was honestly extracted, which
> explicit, authority-declared identity mappings connect its source-native
> structure to canonical model anchors — and what does an exact, read-only
> reconciliation of those sources against the accepted model actually
> support, without ever turning extraction into engineering truth?

## Non-negotiable semantic rules

- Three layers never collapse: (1) what the source bytes and extractor
  reported; (2) how an identified authority interpreted and mapped that
  report; (3) what was separately accepted into a model revision. Every
  finding names which layer it speaks for, by contract field.
- No fuzzy name matching, no automatic part-number equivalence, no
  LLM-created identity, no silent anchor creation, no silent promotion of
  source structure into model truth. Names, labels, descriptions, part
  numbers, and geometric similarity are never canonical identity and never
  join keys.
- A STEP usage occurrence is not proof of a physical installed component. A
  BOM row with `quantity = 4` is not permission to fabricate four canonical
  entity instances.
- The engineering view is never inferred from filename, source family, or
  extraction format. Unknown stays unknown, and an unknown-context claim can
  never be materialized.
- SN-001 runtime code never writes any ledger and never mints any `ent_`,
  `var_`, `reg_`, `rel_`, `rtd_`, `rwd_`, `vrg_`, `vsp_`, `anc_`, or `iba_`
  identifier.

## Architecture

`backend/structural_evidence/` — a read-only composition module, sibling of
`model_state`, above `data_sources` / `identity_binding` / `model_kernel`.
Submodules: `contracts.py`, `locators.py`, `rules.py`, `claims.py`,
`reconcile.py`, `proposals.py`, `errors.py`, `__init__.py` (curated
`__all__`).

Required module docstring, first paragraph (asserted verbatim by test A5b):

> This module records what a structural source reported and how that report
> is addressed. It accepts nothing into any model, declares no canonical
> identity, mints no anchor, writes no ledger, and nothing here is
> engineering truth. The runtime module owns no authoritative store or
> ledger. Identity decisions live in identity_binding; model truth lives in
> model_kernel.

Published runtime-storage wording (asserted verbatim by test A5c):

> SN-001's runtime module owns no authoritative store, no ledger, and no
> revision id. Reconciliation results and proposals are computed and
> returned, never persisted. SN-001 milestone work nevertheless produces
> durable committed artifacts: the frozen showcase sources, their manifest,
> their frozen extraction results, versioned subject-identity rule
> definitions, and hand-authored binding and model records. Committed
> showcase derivatives are test artifacts, not engineering truth or runtime
> authority. The hand-authored binding and model records are engineering
> knowledge, and they were authored by a person, not by SN-001 code.

May import: `data_sources.contracts` (`ExtractorIdentity`,
`ExtractionResult`, `ExtractionOutcome`, `ExtractedTable`, `ExtractedRow`,
`ExtractedCell`, `StepExtractionManifest`, `PartDefinition`,
`ComponentInstance`, `RawRecord`, `QuarantineRecord`), `data_sources.raw_store`
types only, `system_identity`, the curated `model_kernel` surface,
`identity_binding.contracts` / `.resolver` / `.store` types,
`temporal_state.contracts`. Must never: be imported by any accepted module;
construct `ModelStore`, `BindingStore`, or `FilesystemRawStore`; import
`model_kernel.canonical`, `model_kernel.store.validate_record_collection`,
`identity_binding.canonical`, `backend.model_state`, or
`backend.observation_compatibility`.

## Information flow (every arrow discloses its kind)

```
source bytes                                [verified_in_supplied_context]
  -> RawRecord (raw_record_id, checksum)    [computed_result]
  -> ExtractionResult                       [verified: CSV base-only;
                                             declared-only: STEP base-only]
  -> StructuralAddress + claims             [computed_result]
  -> SubjectIdentityRule.body -> value      [authority_declaration]
  -> SourceSubjectRef (sx1 namespace)       [authority_declaration]
  -> BindingAssertion (iba_) per set        [authority_declaration]
  -> resolve_subject(at=resolution_at)      [computed_result, VERBATIM]
  -> canonical anchor (ent_)                [authority_declaration: anc_]
  -> accepted reg_/rel_ + mrv_              [verified_in_supplied_context]
  -> ModelQueries / ModelStateQueries       [computed_result]
  -> Moonraker occurrence                   [verified_in_supplied_context]
```

## Payload-pinned locators (`locators.py`)

```python
class StructuralSourceRef(_Frozen):
    source_id:        str = Field(min_length=1)
    raw_record_id:    str = Field(pattern=r"^[0-9a-f]{32}$")
    payload_checksum: str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    extractor:        ExtractorIdentity            # EMBEDDED verbatim

class CsvRowLocator(_Frozen):
    kind: Literal["csv_row"]
    physical_row_index: int = Field(ge=0)

class CsvCellLocator(_Frozen):
    kind: Literal["csv_cell"]
    physical_row_index: int = Field(ge=0)
    column_index:       int = Field(ge=0)          # IDENTITY
    column_name_as_extracted: str                  # disclosure only

class StepDefinitionLocator(_Frozen):
    kind: Literal["step_part_definition"]
    extractor_path_id:      str = Field(min_length=1)   # IDENTITY
    upstream_definition_id: str = Field(pattern=r"^[0-9a-f]{32}$")  # cross-check

class StepUsageLocator(_Frozen):
    kind: Literal["step_nauo_usage"]
    extractor_path_id:         str = Field(min_length=1)
    upstream_instance_id:      str = Field(pattern=r"^[0-9a-f]{32}$")
    definition_path_id:        str = Field(min_length=1)
    parent_definition_path_id: str | None = Field(default=None, min_length=1)
    # None means "the synthesized root usage has no parent" — a distinct
    # state; an empty string is rejected (K3), so None and "" can never
    # serialize to the same canonical locator value.

StructuralLocator = Annotated[Union[...4 kinds...], Field(discriminator="kind")]

class StructuralAddress(_Frozen):
    source:  StructuralSourceRef
    locator: StructuralLocator
```

- `column_index`, never `column_name`, is identity: the accepted extractor
  *warns* on duplicate headers and synthesizes `__column_{n}__` names.
- `upstream_definition_id`/`upstream_instance_id` are **extractor-local
  identifiers** (`derive_entity_id(raw_record_id, version, path)`), never
  canonical system entity anchors. They are carried as recorded cross-checks
  verified on read; a mismatch is a loud typed finding, never a silent
  re-pointing.
- The canonical locator value grammar (used in the kernel evidence arm) is
  total and injective per scheme, with explicit prefixes (K7):
  - `csv_row`: `r=<int>`
  - `csv_cell`: `r=<int>;c=<int>`
  - `step_part_definition`: `p=<quote(path)>;d=<32hex>`
  - `step_nauo_usage`: `p=<quote(path)>;i=<32hex>;dp=<quote(defpath)>;pp=<quote(parentpath)>`
    where `parent_definition_path_id is None` is encoded as the **empty
    tail** `;pp=` — unambiguous because `min_length=1` guarantees a quoted
    parent path is non-empty. (A sentinel character cannot be used:
    `quote("-", safe="")` returns `-`, so `-` IS a valid quoted path and
    would collide. The adversarial value `-` is in the R8 value set and the
    R12 pinned literals.)
  Integers have no leading zeros and no sign. `quote(v, safe="")` escapes
  everything non-unreserved. A bare 32-hex string satisfies no scheme.
  The three path fields (`extractor_path_id`, `definition_path_id`,
  `parent_definition_path_id`) carry `max_length=1024` as a cheap early
  guard, but the load-bearing bound is on the **canonical value**:
  `canonical_locator_value` raises the typed `SN_LOCATOR_TOO_LONG`
  whenever its output would exceed 510 characters (percent-encoding
  expands up to 3×, so path-field caps alone cannot bound it — the
  fully-escaped worst-case budget is ~51 raw chars per path). A raw
  pydantic `ValidationError` is never the failure mode at the kernel
  boundary; L3 covers both the 1024 early guard and a legal-length path
  whose canonical value overruns.

## Subject-identity rules (`rules.py`) — K1 waiver incorporated

A rule splits into a fingerprinted **body** — the complete generation
program — and non-fingerprinted disclosure:

```python
class CsvColumnLexemeRuleBody(_Frozen):
    rule_kind:            Literal["csv_column_lexeme"]
    semantics_version:    Literal["v1"]
    column_name_as_extracted: str = Field(min_length=1, max_length=128)
    name_match:           Literal["exact_as_extracted"]
    empty_lexeme_outcome: Literal["no_subject_identity"]

class CsvPhysicalRowRuleBody(_Frozen):
    rule_kind:         Literal["csv_physical_row"]
    semantics_version: Literal["v1"]
    include_payload_checksum: Literal[True]

class StepPathRuleBody(_Frozen):
    rule_kind:         Literal["step_extractor_path"]
    semantics_version: Literal["v1"]
    path_source:       Literal["extractor_path_id"]

SubjectIdentityRuleBody = Annotated[Union[...], Field(discriminator="rule_kind")]

class SubjectIdentityRule(_Frozen):
    rule_id:    str = Field(pattern=r"^[a-z][a-z0-9-]{0,47}$")
    applies_to: tuple[StructuralClaimKind, ...] = Field(min_length=1)
    body:       SubjectIdentityRuleBody
    statement:  str = Field(min_length=1, max_length=1024)   # NOT fingerprinted
    stability:  Literal["source_native_key", "payload_pinned",
                        "toolchain_relative"]                # NOT fingerprinted

def rule_fingerprint(body) -> str:
    """sha256 over sort_keys/compact/utf-8 canonical dump of the body,
    first 16 hex — restating model_kernel's canonicalization, not importing
    it."""

def apply_rule(body, claim) -> str | None:
    """Total. None means 'no subject identity under this rule' — a
    first-class outcome, never a fallback, never an empty string."""
```

**The K1 contract, published verbatim and asserted by test A5h:**

> Changes to rule data are content-addressed and necessarily create a new
> subject namespace. Changes to the shared rule interpreter or subject
> encoder are guarded by a versioned algorithm contract, hand-authored
> behavior vectors, and implementation-drift tests; this is enforced by
> tests and review, not by construction alone.

`sx1` is the version of the **complete subject-generation semantics**:
namespace grammar, `apply_rule`, missing-value behaviour, field selection,
comparisons, subject-value encoding, percent encoding, and the
normalization policy — which is none. Any behaviour change to those
mechanics requires `sx2` or later and creates a new identity domain
requiring explicit new mappings. Guards: R4 (AST: `apply_rule` reads exactly
the body's `model_fields`), R5 (hand-authored behaviour vectors, including
case-differing and encoding-adversarial rows, authored from the `statement`
prose), R12 (encoder drift: the exact `quote(value, safe="")` output for an
adversarial value set is pinned as literals). The phrase "structurally
impossible" is never used of interpreter changes.

**CSV header wording (K5).** The accepted CSV extractor strips header
lexemes before exposing them (`columns = [name.strip() ...]`). Rule prose
and golden vectors therefore say: *"the column name as exposed by the
accepted CSV extractor after its documented header processing"* — never
"the header as read". Column index remains identity; the processed name is
disclosure only. The `bom-item-no-v1` rule matches
`column_name_as_extracted == "item_no"` under `exact_as_extracted`.

Rules shipped: `bom-item-no-v1` (`source_native_key`),
`bom-physical-row-v1` (`payload_pinned`; its subject value includes the
payload checksum **and** the extractor `config_fingerprint`, since
delimiter/encoding change row segmentation over the same bytes),
`step-ocaf-entry-v1` (`toolchain_relative`; the namespace carries the
extractor and toolchain identity, so the value is the OCAF entry alone).

## The structural subject namespace — eight components (owner correction)

The value of `SourceSubjectRef.adapter_id`:

```
structural-namespace := "sx1" ":" family ":" extractor-name ":" extractor-version
                        ":" config-fp ":" toolchain-fp ":" rule-id ":" rule-fp

family            := "csv" | "step"
extractor-name    := [a-z][a-z0-9_]{0,63}
extractor-version := [0-9A-Za-z][0-9A-Za-z._+-]{0,31}
config-fp         := [0-9a-f]{16,64}
toolchain-fp      := [0-9a-f]{16}
rule-id           := [a-z][a-z0-9-]{0,47}
rule-fp           := [0-9a-f]{16}
```

- `toolchain-fp = sha256(ExtractorIdentity.toolchain lexeme, utf-8)[:16]`.
  STEP OCAF paths are toolchain-relative; a toolchain change may alter their
  meaning with no change to name, version, or config fingerprint. Changing
  only the toolchain therefore produces a **different `SourceSubjectRef`**:
  an old structural binding never silently applies to a new toolchain
  identity domain. The fingerprint participates in `ResolvedSubject`,
  `inputs_digest`, and fixture goldens.
- Escaping: none and none permitted. Every component alphabet excludes
  `:`, so injectivity is a property of the alphabets, not of a decoder.
  Parsing is `split(":")` into exactly 8 parts; anything else is
  `SN_NAMESPACE_INVALID`.
- Length cap 256 (worst case 254: 3+4+64+32+64+16+48+16 + 7 separators).
- `subject_identifier = quote(source-native value, safe="")`,
  `max_length=512`. A rule returning `None` produces **no**
  `SourceSubjectRef` at all.
- **`SourceSubjectRef.source_id` carries `StructuralSourceRef.source_id`
  verbatim and participates in identity**: `BindingResolver` matches the
  whole three-field `SourceSubjectRef`, so a structural mapping is scoped
  to one `source_id`. The same bytes re-ingested under a different
  `source_id` are a different subject and resolve `source_subject_unmapped`
  — recorded as limitation 16, and R9's perturbation covers `source_id` as
  a ninth dimension.
- The 256-char namespace cap and the 512-char identifier cap are enforced
  by SN-001's builder and result validators; the accepted
  `SourceSubjectRef` contract itself carries only `min_length=1` and is not
  modified.
- `sx1 -> sx2` on any grammar or semantics change: a different identity
  domain by construction, never a silent reinterpretation.

## Claims (`contracts.py`, `claims.py`)

```python
StructuralClaimKind = Literal["bom_row", "step_part_definition", "step_nauo_usage"]

class SourceNativeField(_Frozen):
    """One field EXACTLY as the extractor reported it. `lexeme` is never
    parsed, coerced, normalized, trimmed, or unit-interpreted. None means
    the extractor reported an absent/empty cell."""
    field_name_as_extracted: str = Field(min_length=1)
    lexeme:  str | None
    address: StructuralAddress            # cell-level for CSV

class SourceStructuralClaim(_Frozen):
    claim_kind: StructuralClaimKind
    address:    StructuralAddress
    fields:     tuple[SourceNativeField, ...] = ()
    # canonical order by (field_name_as_extracted, column_index)

class SourceContainmentClaim(_Frozen):
    """Containment in the SOURCE'S OWN vocabulary. Never an MK-001 edge,
    never functional/causal/electrical/fluid/physical containment. For STEP
    both endpoints are DEFINITIONS."""
    claim_kind: Literal["bom_parent_column", "step_nauo_usage_edge"]
    child:  StructuralAddress
    parent: StructuralAddress

class DerivedUsagePath(_Frozen):
    """SN-001's OWN derivation, explicitly labelled."""
    derivation: Literal["nauo_parent_definition_chain_v1"]
    steps:      tuple[StepUsageLocator, ...]      # root-first; () unless unique
    ambiguity:  Literal["unique", "multiple_parent_uses", "unresolved"]

class QuantityFieldRef(_Frozen):
    """K4: the exact extracted column carrying the quantity lexeme,
    identified by column index — never by a display/header name."""
    column_index: int = Field(ge=0)
    column_name_as_extracted: str                 # disclosure only

class SourceStructuralClaimSet(_Frozen):
    source_ref:          StructuralSourceRef
    engineering_context: EngineeringContext       # NO DEFAULT
    subject_claims:      tuple[SourceStructuralClaim, ...]
    containment_claims:  tuple[SourceContainmentClaim, ...] = ()
    derived_paths:       tuple[DerivedUsagePath, ...] = ()
    quantity_field:      QuantityFieldRef | None = None   # None = this source
                                                          # declares no quantity column
    extraction_outcome:  ExtractionOutcome        # carried verbatim
    extraction_warnings: tuple[str, ...] = ()     # carried verbatim
```

A STEP usage count is **computed**, never a source quantity lexeme. It is
derivable only by counting disclosed `step_nauo_usage` claims; no contract
carries a manufactured count field, and it never enters the source-lexeme
comparator (K4). Because C1 requires a declared `quantity_field` on **both**
claim sets and STEP declares none, the showcase's "quantity `4` against 2
usages" yields `claims_not_comparable` — deliberately: only an authority can
reconcile a lexeme with a usage count. Because that case requires the
quantity-bearing row to positively join (it is EXT-100 itself), the
quantity-vs-model check necessarily also fires on it (`"4"` ≠ `"1"`), so
the demonstration's golden finding set for that anchor is exactly
{`corroborated_by_all_mapped_sources`, `claims_not_comparable`,
`quantity_not_reconcilable_with_registered_instances`} — three honest,
consistent findings, pinned together.

**BOM `parent` column containment (claim derivation, not a join).** The
`parent` cell holds an `item_no` lexeme. Building
`SourceContainmentClaim(claim_kind="bom_parent_column")` requires a
**within-source** lookup of that lexeme against the same claim set's
subject column — a source-native structural reading, never a cross-source
join key. If the lexeme matches exactly one row, the claim is emitted with
both addresses. If it matches zero or multiple rows, **no containment claim
is emitted**; the claim set discloses it verbatim:

```python
class UnresolvedParentReference(_Frozen):
    child:  StructuralAddress
    parent_lexeme: str
    reason: Literal["no_matching_row", "multiple_matching_rows"]
```

carried as `SourceStructuralClaimSet.unresolved_parent_references:
tuple[UnresolvedParentReference, ...] = ()`.

## Engineering context — three arms, no default (D12/9)

```python
class DeclaredEngineeringContext(_Frozen):
    kind: Literal["declared_lifecycle_view"]
    view: LifecycleView                    # model_kernel Literal, reused verbatim
    declared_by: AuthorityRef
    statement:   str = Field(min_length=1)

class ViewIndependentEngineeringContext(_Frozen):
    """A POSITIVE claim that the structure holds regardless of view."""
    kind: Literal["view_independent"]
    declared_by: AuthorityRef
    statement:   str = Field(min_length=1)

class UnknownEngineeringContext(_Frozen):
    """Absence of knowledge. Never equivalent to view_independent."""
    kind:   Literal["unknown"]
    reason: Literal["source_declares_no_view", "authority_has_not_declared"]

EngineeringContext = Annotated[Union[...], Field(discriminator="kind")]
```

Compatibility: `declared_lifecycle_view(v)` is compatible only with
`LifecycleViewContext(view=v)`; `view_independent` only with
`ViewIndependentContext`; `unknown` with nothing (finding `context_unknown`).

## Mapping and authority model

Structural mappings are hand-authored `BindingAssertion` records with
`binding_kind="subject"`, `unbounded`/`unbounded` applicability (resolves
`bound` with `applicability_basis="includes_unbounded_claim"`), and the note
that applicability is asserted on the ingestion-receipt axis only and
carries no lifecycle-view validity. Lifecycle, supersession, retraction,
rejection, conflict behaviour, and revision identity are inherited unchanged
from `identity_binding`; SN-001 re-expresses none of it.

**Set selection is forced by anchor ownership** (the store fails an
assertion targeting an anchor declared elsewhere, all-or-nothing). Both
mappings that target the extruder physical instance `ent_a3f1c2d4…` — the
BOM row **and** the STEP extruder definition — must live in
`bindings/demo-printer/`, the set that declares that anchor. The mapping
that targets the new assembly-type anchor lives in
`bindings/demo-printer-model/`, beside its declaration. No anchor is
redeclared to force one set.

**Why binding a STEP part definition to a physical-instance anchor is not
the escape ADR-0010 decision 7 forbids.** Decision 7 forbids *registering*
a CAD definition as a `physical_instance` (or `logical_instance`) — a
layer-3 act that would make source structure model truth. The mapping here
is a layer-2 act: a hand-authored, unauthenticated authority **claim** that
this STEP part definition *represents* the already-registered physical
extruder in the source's vocabulary. It creates no registration, changes no
referent kind, and is correctable by supersession or retraction like any
binding. The registration form remains forbidden; ADR-0010 states this
distinction alongside its D3/ADR-0008 statement.

## Resolved subjects and the join rule

```python
class BindingSetResolution(_Frozen):
    binding_set_id: str
    resolution:     ResolutionResult              # identity_binding, VERBATIM

class ResolvedSubject(_Frozen):
    claim_address: StructuralAddress
    rule_id:       str
    rule_fingerprint: str
    toolchain_fingerprint: str
    subject:       SourceSubjectRef | None        # None = rule yielded no identity
    no_subject_reason: Literal["rule_yielded_none"] | None
    resolutions:   tuple[BindingSetResolution, ...]   # every participating set
    join_anchor_id: str | None
    # validator: join_anchor_id is non-None IFF the set of anchor ids from
    # resolutions with status=="bound" has exactly one member, and equals it.

class ClaimSetDisclosure(_Frozen):
    claim_set:         SourceStructuralClaimSet
    resolved_subjects: tuple[ResolvedSubject, ...]
    # validator (O1, corrected): complete one-to-one coverage over the pair
    # (claim_address, rule_id) — every (subject-bearing claim × applicable
    # rule) has exactly one ResolvedSubject and vice versa. Two rules
    # applying to the same claim (e.g. bom-item-no-v1 AND
    # bom-physical-row-v1 over one bom_row) yield two ResolvedSubjects,
    # deliberately. The locally-checkable completeness form: within one
    # claim set, all claims sharing a claim_kind carry an IDENTICAL rule_id
    # set — guaranteed because a None-yielding rule still emits a
    # ResolvedSubject with no_subject_reason="rule_yielded_none". Whether
    # that rule set equals the reconciler's full applicable-rule list is
    # checked by the reconciler at construction, not by this validator.
```

Published join rule (asserted verbatim by test A5d):

> Two source subjects participate in a cross-source identity join if and
> only if, at the required resolution instant, accepted binding resolutions
> positively bind both subjects to the same canonical anchor. Names, labels,
> part numbers, quantities, geometry, and display text are never join keys.

"Positively bind" ⇒ `status == "bound"` exactly; "same anchor" ⇒ byte
equality. `_join_index` is the only function building a claim-keyed mapping
(AST test J1). **No fallback join exists.**

## Comparators (replacing `sources_disagree`, which stays removed)

| # | `comparable` | Precondition | Operands | Contradiction iff |
|---|---|---|---|---|
| C1 | `quantity_lexeme` | both subjects `join_anchor_id == A`; both claim sets declare a `quantity_field` | the verbatim lexeme of the field at the declared `column_index` | both present, non-empty, not byte-equal |
| C2 | `containment_parent_anchor` | both containment claims' child subjects `join_anchor_id == A` | the parent subjects' `join_anchor_id` values | both present and different |

Guardrails: compare only claims whose subjects positively join to the same
anchor; require both operands; carry both supporting claims verbatim; an
absent operand is `not_comparable` (validator-enforced), never a
contradiction; quantity lexemes are never numerically normalized (`"8"` vs
`"8.0"` vs `"08"` are contradictory); a STEP usage count is never
manufactured into a quantity lexeme; parent comparison uses positively
resolved parent **anchors**, never parent names. If no comparator applies:
`claims_not_comparable` — agreement is never inferred.

**The quantity-vs-model check (not a comparator).** The finding
`quantity_not_reconcilable_with_registered_instances`
(basis `accepted_model_record`) is produced by a claim-vs-model rule, never
by C1/C2 and never against a STEP usage count: for every positively-joined
subject whose claim set declares a `quantity_field` and whose row carries a
non-empty quantity lexeme, the lexeme is compared **lexically** against the
exact decimal representation of the number of distinct registered canonical
entity anchors the join binds — which is by the join rule always `1`. A
lexeme of exactly `"1"` is reconciled (no finding); any other lexeme —
`"4"`, `"8"`, and equally `"1.0"` or `"01"`, since nothing is numerically
normalized — yields the finding, disclosing the lexeme and the registered
count. The model has no instance-multiplicity representation, and this rule
says so honestly instead of comparing two source-native counts to each
other. An absent or empty lexeme on a declared quantity field is
`evidence_incomplete`. **The rule applies only when the joined anchor is
registered in the supplied revision**; an unregistered joined anchor falls
to `anchor_not_registered` instead.

## Findings — the complete frozen vocabulary (25 literals)

`basis = source_claim` (11): `supported_by_bom_only`,
`supported_by_step_only`, `claims_mutually_contradictory`,
`claims_not_comparable`, `duplicate_source_label_not_identity`,
`absence_is_not_evidence_of_absence`, `evidence_incomplete`,
`evidence_unavailable`, `cited_payload_checksum_differs`,
`extractor_identity_changed`, `derived_usage_path_ambiguous`.

`basis = authority_interpretation` (11): `source_subject_unmapped`,
`mapping_ambiguous`, `mapping_conflicted`, `mappings_jointly_incoherent`,
`context_unknown`, `context_incompatible`,
`subject_bound_in_multiple_sets_consistently`,
`mapping_conflicted_across_sets`, `anchor_declared_in_multiple_sets`,
`required_binding_set_missing`, `cited_extraction_not_found` —
`cited_extraction_not_found` speaks for the MAPPING that cites absent
evidence (no claim exists to support a `source_claim` basis); this is an
implementation-documented correction to the earlier 12/10/3 split.

`basis = accepted_model_record` (3): `anchor_not_registered`,
`quantity_not_reconcilable_with_registered_instances`,
`corroborated_by_all_mapped_sources`.

`BASIS_BY_FINDING` freezes exactly this 25-row table; A12′'s
"other statuses absent" assertions and the per-literal basis test are
reviewable against it.

`ReconciliationFinding` enforces at construction: `basis` matches the frozen
`BASIS_BY_FINDING` table; `source_claim` ⇒ non-empty `supporting_claims`;
`authority_interpretation` ⇒ non-empty `supporting_resolutions`;
`accepted_model_record` ⇒ non-empty `model_disclosures`
(`verified: Literal["verified_in_supplied_revision"]`, every cited record id
present in the supplied `ModelRevision`) and a named anchor; a
`mutually_contradictory` comparison appears iff the finding is
`claims_mutually_contradictory`. **Absence-form exemption:**
`anchor_not_registered` is the one `accepted_model_record` finding with, by
definition, no registration record to cite; it gates instead on the named
`anchor_id` plus a `ModelDisclosure` carrying only the searched
`model_revision_id` and no record ids — disclosing what was searched and
not found, never fabricating support. The converse is enforced in the
frozen-table validator: for the other two `accepted_model_record` findings
(`quantity_not_reconcilable_with_registered_instances`,
`corroborated_by_all_mapped_sources`) every `ModelDisclosure` must cite at
least one record id, so the record-free form is constructible only for the
absence finding.

`StructuralReconciliationResult` enforces: canonical claim-set order;
participations unique and sorted by `binding_set_id` (there is **no
`position` field** — K8/2); `_no_subject_silently_dropped` (every
`ResolvedSubject` appears in ≥1 finding); canonical finding order;
`_support_is_disclosed` (every support item **is** a disclosed input object
— a fabricated claim, resolution, or model disclosure is unconstructible);
`_digest_recomputes`.

## `inputs_digest` (K10)

```python
lines = [
  "sn001-inputs-v1",
  resolution_at (UTC isoformat),
  model_revision.revision_id,
  *sorted(f"required={sid}" for sid in required_binding_set_ids),
  *(f"{p.binding_set_id}={p.revision.revision_id}" for p in participations),  # sorted
  *(f"{rule_id}={rule_fp}" for (rule_id, rule_fp) in rules_used),             # sorted
  *sorted(f"toolchain={tfp}" for tfp in toolchain_fingerprints_used),
  *sorted(f"payload={rid}:{sha256hex}" for supplied payloads),                # ids+checksums, never bytes
  *(canonical(d.claim_set) for d in claim_sets),                              # sorted
  *(canonical(s) for d in claim_sets for s in d.resolved_subjects),
]
inputs_digest = "sid_" + sha256("\n".join(lines))
```

Recomputable from disclosed result fields only (`required_binding_set_ids`
and the payload id/checksum pairs become disclosed fields of the result).
Changing any input capable of changing findings changes the digest. It
remains an **input fingerprint** — not a result, not a revision id, no
membership tuple, structurally excluded from both record-id patterns, not
citable as evidence. Findings are a deterministic function of the fully
disclosed inputs and are not digested.

## `resolution_at`

Required, timezone-aware, on the ingestion-receipt axis — not a
model-knowledge cutoff, not an observation cutoff, not a wall clock. Naive
or missing ⇒ `SN_NAIVE_RESOLUTION_AT`. In the digest.

## The multi-resolver facade

```python
StructuralReconciler(*, resolvers: Sequence[BindingResolver],
                     rules: Sequence[SubjectIdentityRule],
                     model: LoadedModel,
                     required_binding_set_ids: frozenset[str] = frozenset(),
                     payloads: Mapping[str, bytes] | None = None)
  .reconcile(claim_sets, *, resolution_at) -> StructuralReconciliationResult
  .propose(reconciliation) -> ModelProposalResult
```

`rules` supplies the subject-identity rules applied during resolution.
`StructuralReconciliationResult.rules_used` is defined as exactly the
distinct `(rule_id, rule_fingerprint)` pairs appearing in the disclosed
`ResolvedSubject`s, sorted — so K10's "recomputable from disclosed result
fields only" stays true by construction.

Every resolver is queried for every subject — no short-circuit, no
first-match, no priority, never a preferred set. The result is canonicalized
independently of caller order; forward and reversed resolver input produce
equal logical results and equal digests. Errors: `SN_NO_BINDING_RESOLVER`,
`SN_DUPLICATE_BINDING_SET`, `SN_REVISION_MISMATCH` (on `propose` with
mismatched participations/model revision — recomputing revisions inside
`propose` is forbidden). Cross-set behaviours surface as the four findings
above; duplicate anchor declarations are reported, never deduped. When
`payloads` supplies bytes, each is checked against the claim set's
`payload_checksum` (mismatch ⇒ `cited_payload_checksum_differs`); when it
does not, the result's disclosed payload list is empty and no
verified-in-context claim is made for those bytes. There is no orphan
verification type: verification status is carried per disclosed payload pair
in the result (K9 resolved by connecting, minimally, not by a free-floating
enum).

## Proposals — inert by construction

`sxp_`-prefixed (structurally excluded from `MODEL_RECORD_ID_PATTERN`),
carrying no constructed record and no `reg_`/`rel_` id.
`EntityRegistrationProposal(anchor_id, supporting, caller_must_supply)`;
`RelationshipAssertionProposal(type_name — never type_id —, endpoints,
evidence_inputs, supporting, caller_must_supply)`. `caller_must_supply` is
validated against a frozen `REQUIRED_BY_PROPOSAL_KIND` table:
`("authority", "recorded_at")` for registrations;
`("authority", "context", "recorded_at", "type_id")` for assertions — the
values SN-001 structurally cannot know. Acceptance is a separate, manual,
committed act; SN-001's public API contains no function that writes to any
store.

## The kernel evidence arm (D3, with toolchain correction)

Inserted immediately before the `EvidenceRef` alias in
`backend/model_kernel/contracts.py` (the alias currently sits at `:118`;
K11 — the final insertion point is determined by the code, and the docs then
cite the resulting location). It cannot use `LocalIdentifier`, which is
defined later in the file.

```python
class StructuralSourceLocatorEvidence(_Frozen):
    """An EXACT structural position inside one immutable source payload,
    declared by the authoring authority. SELF-CONTAINED: every field is a
    canonical scalar; the kernel imports nothing to interpret it, resolves
    nothing, and verifies nothing about it — disclosure is always
    verification="declared_reference". This is a CITATION, never a locator
    ledger and never an identity: it names where a claim was read, not what
    the claim is about. It has no lifecycle and no applicability, cannot
    resolve source identity, and cannot discover or replace a
    BindingAssertion (ADR-0010 decision 10)."""
    kind: Literal["structural_source_locator"]
    raw_record_id:                str = Field(pattern=r"^[0-9a-f]{32}$")
    payload_checksum:             str = Field(pattern=r"^sha256:[0-9a-f]{64}$")
    extractor_name:               str = Field(pattern=r"^[a-z][a-z0-9_]{0,63}$")
    extractor_version:            str = Field(pattern=r"^[0-9A-Za-z][0-9A-Za-z._+-]{0,31}$")
    extractor_config_fingerprint: str = Field(pattern=r"^[0-9a-f]{16,64}$")
    extractor_toolchain_fingerprint: str = Field(pattern=r"^[0-9a-f]{16}$")
    locator_scheme: Literal["csv_row", "csv_cell",
                            "step_part_definition", "step_nauo_usage"]
    locator_value:  str = Field(
        pattern=r"^(?:r=|p=)[0-9A-Za-z._~:@!$&*+,;=%/-]{1,510}$")
```

The toolchain fingerprint makes a STEP locator exact: an OCAF path exists
only relative to a toolchain. The conversion
`to_kernel_evidence(StructuralAddress) -> (evidence, dropped)` is an exact
bijection on the locator half and a documented projection on the source
half. Exactly two fields are dropped, named by the exact keyword names of
`from_kernel_evidence(ref, *, source_id: str, extractor_toolchain: str)`:
`dropped == ("extractor_toolchain", "source_id")` (sorted literal).
`source_id` is binding knowledge and forbidden in a model record; the
toolchain **prose** is dropped while its fingerprint is carried. Both are
required keyword arguments of the inverse, so the loss is a typed
obligation, never a silent default. A locator whose quoted canonical value
exceeds the arm's 510-character bound raises the typed
`SN_LOCATOR_TOO_LONG` from `to_kernel_evidence` — never a raw pydantic
`ValidationError` at the kernel boundary (test X6). The arm inherits `verification="declared_reference"`; making it
`verified_in_revision` would require cross-ledger closure, rejected by
ADR-0009 D1.

**Vocabulary sweeps become semantic (owner ruling).** The accepted
isolation sweeps in `tests/model_state/test_isolation.py` and
`tests/observation_compatibility/test_isolation.py` are refined from blanket
substring bans to semantic assertions: registrations and value
specifications contain no source-locator or binding vocabulary at all;
relationship evidence may contain exactly the approved immutable structural
citation (whose field names are enumerated); no model query treats the
citation as a binding or source-discovery mechanism. `step_nauo_usage` is
the name because it is the precise STEP concept.

## The one coherent demonstration

`showcases/demo-printer/`: `README.md` (first line: synthetic showcase
evidence, represents no real machine), `SOURCES.md` (the designed structure
in prose — the oracle input), `sources/printer_bom.csv`,
`sources/printer_assembly.step`, `MANIFEST.json` (source sha256s, pinned
`source_id`/`raw_record_id`/`payload_checksum`, extractor identity + config
fingerprint + toolchain fingerprint, frozen-extraction checksum,
`regeneration_command`, and the honesty sentence including "NOT an
authoritative ledger record"), `extractions/<raw_record_id>.json` (frozen
canonical `ExtractionResult`), `tools/generate.py` (cad-marked, run once,
never imported by a test).

Designed content: a BOM-only item; a STEP-only usage; two BOM rows with the
same name and different `item_no`; quantity `"4"` against 2 usages; one
deliberately unmapped subject; one sub-assembly used twice (the only path to
`derived_usage_path_ambiguous`, tied to a golden path count in
`SOURCES.md`); a view-less STEP export. The positive path: BOM row
`EXT-100` and the STEP extruder definition, mapped by two separate
hand-authored `BindingAssertion`s to the committed extruder anchor
`ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50`, corroborated, then
`variables_of` → `var_b7e2…` → the existing Moonraker observation via the
accepted facades, with every arrow disclosing its kind.

The committed incoherent fixtures (`bom_valid.csv` × `step_assembly.step`)
are the negative corpus: with both committed resolvers and zero structural
mappings the finding multiset is exactly `{source_subject_unmapped: N}`, the
other statuses are asserted absent, and nothing is proposable (A12′).

## O2 — the one new canonical anchor

Exactly one new hand-authored `type_definition` anchor (the printer assembly
type): declared once in `bindings/demo-printer-model/`; registered by an
append-only record in `models/demo-printer/`;
`authority.kind="test_fixture"`, agent `sn001_showcase_fixture`; explicitly
labelled synthetic showcase knowledge; never minted by runtime code; never
described as a real printer component. The `assembly_definition_contains`
type (`type_definition → type_definition`, containment,
`context_requirement="lifecycle_view"`) and the definition-level assertion
remain separately hand-authored. **`rel_S7`'s endpoints are `anc_S3` (the
new printer-assembly-type anchor) →
`ent_2b3c4d5e6f70819a2b3c4d5e6f708192` ("Extruder unit type (synthetic)")**
— the only committed pair that type-checks: containment forbids
self-relation, O2 authorizes exactly one new anchor, and the extruder-unit
type is the only other committed `type_definition`. D6-2's anchor
disjointness from the `contains` projection holds for exactly this pair.
D6 separation is proven by comparing the
**replayed pre-SN-001 `contains` projection** with the current projection's
semantic content (nodes, edges, conflicts, lineage — the embedded revision
necessarily differs and is excluded; K8/1), plus endpoint-kind rejection in
both directions and a wording sweep.

## Ledger and revision evolution

```
bindings/demo-printer/        4 -> 6    (+ iba_S1: BOM EXT-100 -> extruder;
                                         + iba_S2: STEP extruder definition -> extruder)
bindings/demo-printer-model/  3 -> 5    (+ anc_S3: assembly-type anchor;
                                         + iba_S4: STEP assembly definition -> anc_S3)
models/demo-printer/         11 -> 14   (+ rtd_S5, + reg_S6, + rel_S7)
```

Both extruder-targeting mappings live in `bindings/demo-printer/` because
only that set declares `ent_a3f1c2d4…` and `identity_binding` validation is
same-set, all-or-nothing.

No existing record edited or deleted; all historical revisions replay from
explicit full record-id lists (`mrv_c28b6301…` from 9, `mrv_10565807…` from
10, `mrv_25afc0eb…` from 11, `rev_8605f52c…` from 4, `rev_b4878a69…` from
3 — all measured); no prefix-filter membership reconstruction anywhere;
current membership via `load()`, historical membership via explicit
`replay(...)`; existing bytes frozen by an extended sha256 map (18 files);
the Moonraker subject and hotend variable resolve and attach identically
before and after.

## Determinism

CSV: logical and byte-level. STEP: stable for a fixed extractor build; the
toolchain fingerprint is now **in the subject namespace and the evidence
arm**, so a toolchain change produces a different identity domain and the
typed finding `extractor_identity_changed` — never a silent re-pointing and
never `source_subject_unmapped`'s misleading reading. Golden literal
upstream-id pins (A11) make an OCCT shift fail loudly. No byte-identical
database file is claimed anywhere, because SN-001 has no database.

## Failure and threat model

Missing extraction ⇒ `evidence_unavailable`, present in the result, never a
silent skip — scoped to **cited** sources: the finding (basis
`source_claim`) gates on non-empty `supporting_claims`, so it is reachable
exactly when a claim set citing the missing evidence was supplied; SN-001
cannot report the absence of evidence nothing cites. Quarantined record ⇒ zero claims; a `QuarantineRecord` is never
read as a partial result. `outcome=="partial"` ⇒ `evidence_incomplete` even
when the partial result would otherwise corroborate. Changed checksum ⇒
`cited_payload_checksum_differs` disclosing both. Toolchain change ⇒
`extractor_identity_changed`. Ambiguous derived path ⇒ reported with
`steps=()`, never picked. Multi-record acceptance failure ⇒ a typed error
naming the partially-applied ids (the kernel has no bulk append and SN-001
must not create one). Concurrent writers: undefined and documented, inherited
verbatim. Secrets/absolute paths: every result field derived from source
text passes the accepted sanitizers; sweeps carry anti-vacuity guards. No
network, no wall clock.

## Exclusions

Excel; SQL; native CAD; OCR; additional APIs; behaviours; constraints;
diagnosis; planning; UI; source-unit interpretation; semantic PDF
interpretation; any redesign of operational telemetry; the ADR-0009
source-property interpretation ledger; any suggestion or matching engine.

## Limitations — verbatim in `backend/structural_evidence/README.md`, asserted by test A5i

1. A recorded mapping is an unauthenticated authority claim, never evidence
   that the mapping is correct.
2. Usage-path identity is derived by SN-001 and is not guaranteed stable
   across re-exports of the same CAD model.
3. STEP-derived identifiers are stable for a fixed extractor build; the
   toolchain fingerprint makes a build change a new identity domain, and the
   golden id pins make it loud.
4. `assembly_definition_contains` is a second, non-merging containment
   lineage and is never "the hierarchy".
5. An accepted entity registration cannot cite its structural derivation;
   the link is one-directional via the relationship assertion.
   5b. A model record cannot, by itself, name the ingestion source; the
   cited `iba_` record does. Two hops, neither kernel-verified.
6. Structural mapping applicability is asserted on the ingestion-receipt
   axis only and carries no lifecycle-view validity.
7. A claim whose engineering context is unknown can never be materialized.
8. In the base-only verification the frozen STEP extraction is trusted; its
   agreement with the live extractor is verified only in the all-extras
   column.
9. Enumeration-order independence is asserted for reversed and
   adversarially-named orderings, not proven exhaustively.
10. Anchor ids are uuid4 hex by accepted decision; SN-001 generates none.
11. The showcase does not resemble a real printer and is not intended to.
12. The raw store is not committed; a committed record citing a raw record
    is a dangling reference from a clean checkout until the demonstration
    regenerates it against pinned golden constants.
13. Atomic multi-record acceptance is not provided.
14. Changes to the shared rule interpreter or subject encoder under a fixed
    `sx1`/`semantics_version` are guarded by tests and review, not by
    construction. (K1 waiver, honest form.)
15. The runtime module owns no store; the milestone's durable artifacts are
    test artifacts and hand-authored records, as published in §2.
16. A structural mapping is scoped to one `source_id`: the same bytes
    re-ingested under a different source id are a different subject and
    resolve `source_subject_unmapped`.

## Verification

Two columns, green at every commit: base-only
(`requirements.txt` + `requirements-dev.txt`; the entire SN-001 suite
including the demonstration runs off frozen extractions; only `cad`/`pdf`
corroboration skips) and all-extras (adds the live STEP drift guard, the
Tier-1 CAD halves, and the generator round-trip). Baseline to preserve:
1159 collected; base-only 1126 passed / 33 skipped. Expected SN-001c red
baseline before the ledger appends land: 11 named failures at the staging
run (enumerated in the plan, commit 10) plus a 12th
(`test_variable_registration.py`, `__all__` 53→54) that fires at commit 11
— with the two prefix-filter replays (`test_demo_join.py:162-164`,
`test_demo_compatibility.py:122`) passing silently while selecting 12 and
13 records: the honesty defect the RP2/HD1 migration kills.
