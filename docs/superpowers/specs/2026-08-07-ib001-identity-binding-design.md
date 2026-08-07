# IB-001 — Explicit Identity Binding and Canonical Anchors (final, self-contained)

Status: **Accepted by the project owner** (original design + two correction
passes + five final decisions, 2026-08-07). This document incorporates the
complete accepted design and stands alone: no conversation history or
correction-pass reference is needed to implement or audit it.

## Objective

The smallest trustworthy layer answering: *which canonical system entity
does this source-native subject represent, and which canonical property or
variable does this source-native field refer to?* It is the bridge:

```text
data_sources → temporal_state → identity_binding → future model kernel
```

Moonraker is the validation source, not the architecture. IB-001 is not the
hierarchy, graph kernel, ontology, reasoning engine, or live-state engine.

## Module boundary

```text
backend/
  system_identity/     # NEW — pure anchor value contracts; ZERO project deps
    anchors.py         #   EntityAnchor, VariableAnchor, ID rules
  identity_binding/    # NEW — ledger, resolver, temporal facade
    contracts.py       #   authority, boundaries, ledger records, results, errors
    canonical.py       #   deterministic serialization + content hashing
    store.py           #   write-once record files, validation, revision replay
    resolver.py        #   membership + eight-case resolution algorithm
    facade.py          #   BoundTemporalQueries (join; never copy/mutate)
bindings/
  demo-printer/records/  # NEW — committed synthetic validation binding set
tests/identity_binding/  # NEW
```

Dependency rules (violations are defects):

```text
system_identity   → (nothing in this repository)
identity_binding  → system_identity, temporal_state (read-only)
identity_binding  ✕→ data_sources        (not even provenance helpers)
data_sources      ✕→ identity_binding / system_identity
temporal_state    ✕→ identity_binding / system_identity
```

Zero changes under `backend/data_sources/` and `backend/temporal_state/`.
Identity resolution is a join over existing evidence; it never rewrites
temporal occurrences or raw/extracted evidence. Locator types are reused
from `temporal_state.contracts` (`SourceSubjectRef`, `SourcePropertyRef`),
never duplicated. Subject identity is the three-dimension
`SourceSubjectRef` (source_id, adapter_id, subject_identifier); property
identity is the six-dimension subject+property pair (adding
extraction_route, item_key, json_pointer). A changed extraction route does
not unbind the subject; it produces a new, initially unbound property
locator. Another source or adapter is a different subject locator.

## Contracts

All models: pydantic v2, `frozen=True`, `extra="forbid"`. Every datetime
field is `AwareDatetime` and is normalized to UTC by a field validator at
construction — naive datetimes are rejected at the model boundary.

### `system_identity.anchors` (pure values — no authority, no timestamps)

```text
EntityAnchor
  anchor_id      str    # "ent_" + 32 lowercase hex (uuid4 hex); OPAQUE
  namespace      str    # human-readable system scope, [a-z0-9-]+; NON-identifying
  display_name   str    # human label; NON-identifying
  role_name      str | None    # e.g. "extruder-unit"; a role survives hardware
                               #   replacement — identity does not; NON-identifying
  referent_kind  Literal["physical_instance", "logical_instance",
                         "type_definition", "unknown"]

VariableAnchor
  anchor_id         str        # "var_" + 32 lowercase hex; OPAQUE
  entity_anchor_id  str        # ent_ id of the owning entity (identity, not hierarchy)
  namespace         str        # NON-identifying, as above
  display_name      str
  role_name         str | None
```

Rules: ID patterns `^ent_[0-9a-f]{32}$` / `^var_[0-9a-f]{32}$` (lowercase
hex — safe on Windows and case-insensitive filesystems). Anchors are
immutable in IB-001: there is no rename or label-correction mechanism (a
future alias/annotation record is deferred work). The resolver never
consults `namespace`, `display_name`, or `role_name` for any matching
decision. A replacement physical component always receives a new entity
anchor, even if its display name and source address are unchanged. IDs are
opaque by decision: curated role-bearing IDs were rejected because they
weld identity to role (see ADR-0006). `referent_kind` classifies only what
kind of referent the ID names; it carries no attributes, taxonomy, or
relations — a CAD definition gets its own `type_definition` anchor, an
installed unit its own `physical_instance` anchor, and the `instance_of`
relation between them is future kernel material with no IB-001
representation.

### `identity_binding.contracts`

```text
AuthorityRef            # a recorded CLAIM of authorship — nothing is
  kind    Literal["human_owner", "test_fixture"]   # authenticated or signed
  agent   str           # claimed name; never a credential
  method  Literal["manual_declaration"]
```

```text
Boundary (discriminated union on "kind")
  DeclaredBoundary   { kind: "declared", at: AwareDatetime }
  UnboundedBoundary  { kind: "unbounded" }     # explicit authority claim
  UnknownBoundary    { kind: "unknown" }       # absence of knowledge — NOT unbounded

AppliesScope
  axis               Literal["ingestion_received_at"]
  start_boundary     Boundary
  end_boundary       Boundary
  interval_semantics Literal["half_open"]      # [start, end)
  # invariant: both declared ⇒ start.at < end.at
```

Ledger records — every record carries `record_kind`, `schema_version`
("1"), and a content-derived `record_id` (see Hashing):

```text
AnchorDeclaration                  # record_id prefix "anc"
  record_kind    "anchor_declaration"
  schema_version "1"
  record_id      str
  anchor_kind    Literal["entity", "variable"]
  anchor         EntityAnchor | VariableAnchor    # must match anchor_kind
  recorded_at    AwareDatetime                    # audit only
  authority      AuthorityRef
  note           str = ""

BindingAssertion                   # prefix "iba"
  record_kind / schema_version / record_id
  binding_kind      Literal["subject", "property"]
  subject           SourceSubjectRef
  property          SourcePropertyRef | None      # None ⇔ binding_kind == "subject"
  target_anchor_id  str            # ent_ for subject-, var_ for property-bindings
  applies           AppliesScope
  recorded_at       AwareDatetime                 # audit only — never picks winners
  authority         AuthorityRef
  supersedes        str | None     # CORRECTION only (the old decision was WRONG);
                                   #   must reference an existing assertion of the
                                   #   SAME binding_kind and EXACT same locator;
                                   #   never used for real-world replacement
  note              str = ""

BindingRetraction                  # prefix "ibr"
  retracts / recorded_at / authority / note

ApplicabilityClosure               # prefix "ibc"
  closes          str              # assertion record_id
  end             AwareDatetime    # converts an unknown/unbounded effective end
                                   #   to declared; NARROWING only
  recorded_at / authority / note

BindingRejection                   # prefix "ibj" — diagnostics only, never resolution input
  subject / property (None ⇔ subject-level) / rejected_anchor_id
  recorded_at / authority / note
```

```text
BindingRevision
  revision_id     str              # "rev_" + FULL 64-hex SHA-256 over:
                                   #   binding_set_id + "\n" + sorted record_ids
                                   #   joined by "\n"
  record_ids      tuple[str, ...]  # unique, lexicographically sorted — never
                                   #   filesystem order, never recorded_at order
  record_count    int              # == len(record_ids)
  binding_set_id  str              # [a-z0-9-]+, e.g. "demo-printer"
  # validated invariants: sorted/unique membership; count matches;
  # revision_id recomputes to match
```

```text
AssertionSummary                   # structured evidence in every result
  record_id         str
  target_anchor_id  str
  authority         AuthorityRef
  declared_applies  AppliesScope   # exactly as written in the assertion
  effective_applies AppliesScope   # after a valid closure; == declared when none
  closure_records   tuple[str, ...]   # 0 or 1 in a valid set
  superseded_by     tuple[str, ...]   # iba_ ids citing this via supersedes
  retracted_by      tuple[str, ...]   # ibr_ ids targeting this assertion
  active            bool           # superseded_by == () and retracted_by == ()
  membership_at     Literal["in", "out", "unknown"]  # computed on EFFECTIVE applies
  recorded_at       AwareDatetime

SubjectResolutionContext           # non-recursive property-result context
  status              (ResolutionStatus)
  resolved_entity     EntityAnchor | None            # only when subject "bound"
  candidate_entities  tuple[EntityAnchor, ...]
  via_assertion_ids   tuple[str, ...]                # ids only — no nesting

ResolutionResult
  status            Literal["bound", "applicability_unknown",
                            "outside_applicability", "unbound", "ambiguous",
                            "conflicted", "superseded", "retracted", "inactive"]
  locator_subject   SourceSubjectRef
  locator_property  SourcePropertyRef | None
  resolved_target   EntityAnchor | VariableAnchor | None  # non-None ⇔ "bound"
  candidate_targets tuple[EntityAnchor | VariableAnchor, ...]  # anchor_id order
  via_assertions    tuple[AssertionSummary, ...]     # record_id order; ALL matching
                                                     #   assertions incl. OUT/inactive
  applicability_basis Literal["declared_interval",
                              "includes_unbounded_claim"] | None  # bound only
  revision          BindingRevision
  subject_context   SubjectResolutionContext | None  # present ⇔ property resolution
  detail            str = ""       # human note; never sole carrier of data
```

Errors: `IdentityBindingError(error_code, message)` base;
`BindingIntegrityError` (invalid set — all-or-nothing);
`BindingResolutionError` (e.g. `BINDING_NAIVE_AT`);
`BindingConfigurationError` (bad set root / set id).

## Applicability algorithm (three-valued, exact)

For effective scope `s` (half-open `[start, end)` on the
`ingestion_received_at` axis) and aware, UTC-normalized query time `t`:

```text
started(t):   start declared  → YES if t >= start.at else NO
              start unbounded → YES
              start unknown   → UNKNOWN

not_ended(t): end declared    → YES if t < end.at else NO   # t == end.at is OUT
              end unbounded   → YES
              end unknown     → UNKNOWN

membership(t) = IN       if started == YES and not_ended == YES
              = OUT      if started == NO  or  not_ended == NO
              = UNKNOWN  otherwise
```

All nine boundary combinations:

| start \ end | declared `e` | unbounded | unknown |
|---|---|---|---|
| **declared `s`** | IN on `[s,e)`, OUT outside | IN for `t≥s`, OUT before | OUT for `t<s`; UNKNOWN for `t≥s` |
| **unbounded** | IN for `t<e`, OUT at/after | IN always | UNKNOWN always |
| **unknown** | OUT for `t≥e`; UNKNOWN before | UNKNOWN always | UNKNOWN always |

A declared timestamp proves exclusion on its side even when the opposite
side is unknown; an unknown opposite boundary blocks every positive claim;
`unbounded` is an explicit claim, never conflated with `unknown`; the
boundary instant belongs to the successor.

## Resolution algorithm (eight non-overlapping cases)

Deterministic total function of `(revision, locator, at)`. `at` is a
required timezone-aware datetime; missing, `None`, non-datetime, and
naive values all fail through the same typed
`BindingResolutionError("BINDING_NAIVE_AT")` (the parameter defaults to
`None` solely so missing input reaches the typed contract); there is no
implicit `datetime.now()` anywhere in the resolver. The public result
contracts themselves reject impossible states — targets/basis exactly
when bound, candidate-bearing statuses only, entity-vs-variable anchor
kinds by resolution level, subject context exactly on property results,
lifecycle links consistent with `active`, unique canonically ordered
collections — rather than relying on the resolver to avoid constructing
them.

```text
matching   = assertions whose locator equals the query locator EXACTLY
active     = matching with superseded_by == () and retracted_by == ()
membership = per active assertion, on EFFECTIVE applies

IN_targets      = distinct targets of active assertions with membership IN
UNKNOWN_targets = distinct targets of active assertions with membership UNKNOWN
# OUT assertions are proven not applicable at t: they never compete for and
# never block the target; they remain in via_assertions diagnostics.

1  matching == ∅                                       → unbound
2  active == ∅                                         → inactive-status rules
3  active ≠ ∅, IN_targets == ∅, UNKNOWN_targets == ∅   → outside_applicability
4  |IN_targets| ≥ 2                                    → conflicted
5  |IN_targets| == 1 and UNKNOWN_targets ⊄ IN_targets  → ambiguous
6  |IN_targets| == 1 and UNKNOWN_targets ⊆ IN_targets  → bound
7  IN_targets == ∅ and |UNKNOWN_targets| == 1          → applicability_unknown
8  IN_targets == ∅ and |UNKNOWN_targets| ≥ 2           → ambiguous
```

Inactive-status rules (case 2): every inactive assertion superseded-only →
`superseded`; every one retracted-only → `retracted`; any assertion
carrying both facts, or a mixture of kinds → `inactive`. No precedence is
invented between independent lifecycle facts.

`bound` details: `resolved_target` is set; `candidate_targets` is empty;
`applicability_basis` is `"declared_interval"` when every IN assertion's
effective scope has declared start and end, else
`"includes_unbounded_claim"`. Same-target corroboration lists every IN
assertion without vote counting. An unknown-only candidate appears ONLY in
`candidate_targets`, never in `resolved_target`. Conflicts and ambiguity
are never resolved by recency, `recorded_at`, or authority rank. There is
no present-day interpretation mode in IB-001.

## Subject/property independence

- A property assertion that is positively IN binds its exact six-dimension
  locator on its own authority — it is itself an explicit identity
  decision. It creates no subject binding for any other property.
- Resolving a subject resolves nothing beneath it: every property needs
  its own assertion.
- Every property result carries `subject_context` (non-recursive).
- An unbound subject is not a contradiction: the property result stays
  `bound`; the context shows `unbound`.
- Cross-level consistency: if the subject resolves `bound` to entity E₁ at
  the same `at` and an IN property assertion targets a variable whose
  `entity_anchor_id` ≠ E₁, the property result is `conflicted` — the IN
  variable anchor(s) in `candidate_targets`, the conflicting entity in
  `subject_context`. The check fires only when both sides are positively
  established: an `applicability_unknown` or `ambiguous` subject cannot
  prove an inconsistency and remains visible in context.
- A binding establishes identity only. It never establishes a unit,
  conversion, tolerance, validity interval, or engineering meaning the
  source did not supply.

## Lifecycle and closure semantics

The ledger is append-only; nothing is edited or deleted. Lifecycle events
are new records:

- **Assert** — new `BindingAssertion`.
- **Correct** — new assertion with `supersedes`: "the old decision was
  wrong." The old record remains; superseded_by links both ways in
  summaries.
- **Real-world change** (hardware replaced) — applicability closure on the
  old assertion (only if its effective end is unknown/unbounded) plus a
  new assertion with a new anchor and a declared start. Never supersession.
- **Retract** — withdraw without replacement; the original is never
  deleted.
- **Reject** — record a refused candidate; diagnostics only.

Supersession and retraction are independent facts: an assertion may carry
both, and summaries disclose both without loss. Multiple competing
successors remain active and flow through the resolution algorithm; no
successor wins by timestamp. `membership_at` is always computed on
`effective_applies`; a summary alone explains a resolution: "declared end
was unknown; closure `ibc_…` (in `closure_records`) established the end
used here." `superseded_by`/`retracted_by` name the exact deactivating
records — no blind revision search is ever needed.

## Storage and revision rules

Write-once JSON files, one binding set per directory
(`<root>/<binding_set_id>/records/<record_id>.json`), single-writer
assumption, no locks pretended:

- **Append**: validate record → canonical hash → unique temp file staged
  in `.staging/` OUTSIDE the scanned `records/` directory → one atomic
  rename (cleaned up on handled failure), so a reader sees the old
  complete set or the new complete record, never a partial ledger
  member, and crash residue in staging can never invalidate `load()`.
  When the final file already exists it is READ AND VALIDATED first:
  identical validated content is an idempotent no-op; malformed,
  tampered, or inconsistent existing content raises
  `BindingIntegrityError` and is never silently overwritten.
- **Load (current revision)**: read every `records/*.json`; verify each
  `record_id` against the recomputed content hash; run whole-set
  validation; membership = all records; `record_ids` sorted
  lexicographically; `revision_id` per the formula above. Filesystem
  enumeration order never matters.
- **Load (explicit revision)**: caller supplies `record_ids`; every
  supplied id is validated against the ledger-record ID pattern BEFORE
  any filesystem path is constructed (traversal-shaped or malformed
  members fail with the typed revision error) and duplicate membership
  is rejected; the store then
  verifies every id exists as a still-present file with matching content,
  requires the subset to be reference-closed (an assertion's anchor
  declaration, a closure's assertion, a supersession's predecessor, a
  rejection's anchor must be inside the membership), runs the same
  validation on the subset, and resolves over exactly that membership.
  This makes an earlier resolution explainable after later appends.
- `recorded_at` is audit information only: it never orders winners, breaks
  conflicts, or substitutes for explicit supersession.
- IB-001 does **not** provide knowledge-time queries ("the revision as of
  date X"); it provides revision replay only when the caller supplies the
  membership.
- Files are pretty-printed for review; the hash is computed over the
  canonical serialization of the validated model, not raw file bytes.
- A **loaded revision is genuinely immutable**: `LoadedBindingSet`
  exposes copied read-only mappings, so neither mutation of the caller's
  input mapping after validation nor attempted mutation of any exposed
  mapping can alter a validated revision — the same revision, locator,
  and time always produce the same result. Validation also binds every
  collection key to its record's own identity
  (`BINDING_RECORD_KEY_MISMATCH`): a forged key can never become
  revision membership, and `BindingRevision` itself rejects members that
  do not match the ledger-record ID pattern.
- The demo binding set is committed to the repository; runtime sets for
  real deployments live under a configured non-repo root in the same
  format. Derived indexes are in-memory only (no SQLite in IB-001).

## Hashing rules

`record_id` = `<prefix>_<full 64-lowercase-hex SHA-256>` where prefix ∈
{anc, iba, ibr, ibc, ibj} by record kind. The digest input is the
**validated model** serialized deterministically:

- `record_id` excluded from its own hash;
- keys sorted; compact separators (no insignificant whitespace);
- every timestamp normalized to UTC at model validation and serialized as
  Python's `datetime.astimezone(UTC).isoformat()` — offset `+00:00`;
- enums as their string values; discriminated unions as plain objects
  carrying their discriminator field.

Consequence (by decision): semantically identical timestamps expressed
with different offsets produce the **same** `record_id`.
`revision_id` = `rev_` + full 64-hex SHA-256 over
`binding_set_id + "\n" + "\n".join(sorted(record_ids))` — revision
identity changes when either the membership or the set id changes.

## Integrity invariants (all-or-nothing)

Any violation invalidates the complete binding set
(`BindingIntegrityError`); an invalid set resolves nothing:

1. unknown `record_kind` or `schema_version`;
2. content hash mismatch (file name/id vs recomputed canonical hash);
3. duplicate `record_id` with different content;
4. two declarations with the same `anchor_id`, even under different
   `record_id`s — exactly one declaration owns each canonical anchor ID;
5. one identifier used by both anchor kinds;
6. an anchor ID whose prefix contradicts its declaration's `anchor_kind`;
7. a variable anchor referencing an undeclared entity anchor;
8. an assertion whose `target_anchor_id` is undeclared or whose prefix
   contradicts its `binding_kind` (subject→ent_, property→var_);
9. `binding_kind`/`property` mismatch (subject with property, property
   without);
10. `supersedes` referencing a missing record, a non-assertion, a
    different `binding_kind`, or a different exact locator;
11. any cycle in the supersession graph (content-derived ids make cycles
    cryptographically implausible; validated regardless);
12. a retraction referencing a missing or non-assertion record;
13. a closure referencing a missing assertion, targeting an effective end
    already declared, or violating `end > declared start`;
14. two or more closures for one assertion (contradictory administrative
    amendments — no silent winner);
15. a rejection whose `rejected_anchor_id` is undeclared;
16. a naive datetime anywhere (rejected at model validation);
17. declared-interval violation (`start.at >= end.at`).

## Facade behavior

```python
BindingResolver(loaded_set)
    .resolve_subject(subject: SourceSubjectRef, at: AwareDatetime)  -> ResolutionResult
    .resolve_property(subject, prop: SourcePropertyRef, at)         -> ResolutionResult

BoundTemporalQueries(resolver, temporal_queries)
    .latest_observed(subject, prop, as_of) -> BoundLatestObserved | None
    .history(subject, prop)               -> list[BoundOccurrence]

BoundLatestObserved:  observed: LatestObservedState    # TS-001 object, VERBATIM
                      resolution: ResolutionResult
BoundOccurrence:      occurrence: TemporalOccurrence   # VERBATIM
                      resolution: ResolutionResult
```

The facade delegates to the existing `TemporalQueries` unchanged
(inheriting its contracts — a naive `as_of` already raises
`TemporalQueryError`), then attaches a resolution. `latest_observed`
resolves at the returned observation's `received_at` — never the query
execution clock and never `as_of`. `history` resolves each occurrence at
its own `received_at`, so one history can honestly span a replacement
boundary. Every status returns the underlying observation — identity limbo
never hides evidence. No temporal or evidence row is copied or mutated.

## Fixture definition (committed demo binding set)

`bindings/demo-printer/records/` — four records, all with
`authority = {kind: "test_fixture", agent: "ib001_demo_fixture",
method: "manual_declaration"}` (never `human_owner`: the committed
Moonraker evidence is deterministic validation data, not authenticated
real-world knowledge):

1. `AnchorDeclaration` (entity): anchor_id
   `ent_a3f1c2d4e5b6478899aa0b1c2d3e4f50` (fixed constant), namespace
   `demo-printer`, display_name "Extruder unit (demo printer)", role_name
   `extruder-unit`, referent_kind `physical_instance`. Note describes it
   as a synthetic physical-instance anchor in the demo model.
2. `AnchorDeclaration` (variable): anchor_id
   `var_b7e2d3c4f5a6172839405a6b7c8d9e0f` (fixed constant),
   entity_anchor_id = the entity above, role_name `hotend-temperature`.
3. `BindingAssertion` (subject): locator {source_id `printer-1`,
   adapter_id `moonraker`, subject_identifier `extruder`} → the entity
   anchor.
4. `BindingAssertion` (property): the same subject plus
   {extraction_route `api:moonraker:v1`, item_key `printer_objects`,
   json_pointer `/result/status/extruder/temperature`} → the variable
   anchor.

Both assertions declare the owner-approved applicability interval on the
ingestion-receipt axis:

```text
[2026-08-07T20:00:00Z, 2026-08-07T21:00:00Z)   half-open
```

chosen from inspected evidence: the API-path deterministic test clock
starts at 2026-08-07T20:00:00Z and ticks one second per call, so all
fixture observations are received minutes after that instant; the hour is
the smallest clear covering interval with an explicit deterministic
margin. Both assertion notes state: "This interval is asserted solely for
the committed validation scenario and makes no claim about a real printer
outside the fixture." A future real deployment creates a separate runtime
binding set with `human_owner` authority and a genuinely known interval.

## Exclusions

IB-001 does not include: hierarchy or parent-child relationships; typed
graph edges; automatic entity discovery or merging; fuzzy/name-based
matching; LLM-generated bindings; CAD-to-BOM reconciliation; PDF semantic
interpretation; canonical unit conversion; inferred state;
validity-interval inference; causality or diagnosis; constraints, goals,
actions, or desired-state planning; physical commands; Excel ingestion;
public API or UI; present-day interpretation mode; knowledge-time queries;
anchor renaming/aliasing; authentication or signing of authorities;
derived SQLite indexes.

## Threat and failure model

- **Wrong binding recorded** → supersession with full audit; every result
  cites assertion ids and authorities.
- **Name-collision temptation** (`extruder` everywhere) → structurally
  impossible to exploit: no matching logic exists; only exact locators
  resolve; anchor names are non-identifying by contract.
- **Silent history rewriting** → per-occurrence resolution at
  `received_at`; positive claims require declared/unbounded boundaries;
  unknown applicability yields `applicability_unknown` with candidates
  outside the authoritative field.
- **Contradictory ledger** → `conflicted`/`ambiguous` with all
  competitors; never auto-resolved.
- **Tampered record file** → content-derived id mismatch at load; set
  invalid.
- **Revision drift** → every result carries the full revision membership;
  results are comparable only with equal revisions; earlier revisions
  replay from supplied membership.
- **Route/adapter drift** → a changed extraction route leaves the subject
  binding intact and yields a new unbound property locator; a different
  adapter is a different subject locator.
- **Address vs occupant** → the stable source address maps to different
  entity anchors over disjoint declared intervals; replacement is closure
  + new anchor, never rebinding in place.
- **Secrets/paths** → records hold identities and notes only; authority is
  a claimed name, never a credential; validated patterns keep ids
  path-safe; no absolute paths in committed records.
- **Evidence corruption** → this layer opens the temporal store read-only
  and the evidence store not at all; byte-for-byte hash sweeps prove both
  unchanged.

## Acceptance criteria

- All new `tests/identity_binding/` tests pass, including the named
  mandatory regression cases: different-target OUT never blocks a valid
  binding; different-target UNKNOWN prevents `bound`; an unknown-only
  candidate never occupies `resolved_target`; simultaneous supersession
  and retraction loses neither fact; summaries cite exact closure/
  supersession/retraction records; duplicate canonical anchor declarations
  invalidate the set; equal instants with different offsets hash
  identically; revision identity changes with membership or set id; a
  property may bind while its subject is unbound; positively inconsistent
  subject/entity ownership → `conflicted`; property binding never creates
  a subject binding; fixture authority is `test_fixture`, never
  `human_owner`; fixture results outside the declared hour are
  `outside_applicability`; evidence and temporal stores remain
  byte-for-byte unchanged.
- The end-to-end slice proves the complete chain: canonical anchor ←
  assertion + revision ← six-dimension locator ← TemporalOccurrence ←
  attempt ← extraction ← raw record + checksum; and proves the same word
  from another adapter stays unbound, conflict surfacing, and correction
  without destroying the prior assertion.
- The 389-test baseline is preserved; base-only and all-extras clean
  checkouts pass (no new dependencies, so base-only grows by the full new
  count); zero diffs under `backend/data_sources/` and
  `backend/temporal_state/`; no secrets or absolute paths in committed
  records; module READMEs document verification commands; known
  limitations recorded.

## Known limitations (accepted)

No label-correction path (anchors immutable; alias records deferred); no
interpretation convenience (unknown applicability answers
`applicability_unknown`, full stop); no implicit "now" (explicit `at`
everywhere); no knowledge-time reconstruction (revision replay requires
the caller to retain membership); a mistaken closure cannot be amended by
a second closure (supersede the underlying assertion instead); full
configuration-aware rebinding (config generations, serial tracking) is
deferred beyond IB-001.
