# ES-001 adversarial acceptance matrix (final)

Produced independently by the test-engineer specialist BEFORE
implementation planning, at main @ 8cb5f1e, and adopted by the accepted
design as the test plan. The independent matrix follows verbatim below
the amendment section; rows bind to behavior, not names.

## Final-design amendments (owner correction pass; governing)

Naming placeholders in the matrix map to the accepted names:
"meaning record" = `VariableSemanticDeclaration` (`vsm_`);
"interpretation record" = `SourcePropertyInterpretation` (`spi_`) in
`backend/source_interpretation/` (root `interpretations/`); "semantic
result" = `VariableSemanticCompatibilityResult` (ruleset `es001.1`).
Verdict tokens: the unit dimension uses `unit_identity_exact` /
`unit_identity_mismatch`; the aggregate finding is
`declared_semantics_compatible`; the mismatch co-finding is
`unit_identities_differ_conversion_not_attempted` (never emitted
without `unit_identity_mismatch`); the lexeme finding is
`interpreted_unit_lexeme_differs_from_source`.

Contradiction resolutions (owner-adjudicated):

- FC4/F7 are corrected by the owner at Group 13: aggregate
  `superseded` is unreachable in a finite valid interpretation DAG and
  is removed from the public status, reason, and finding vocabularies.
  `retracted` remains distinct from mixed-history `inactive`;
  supersession remains fully disclosed per assertion through
  `superseded_by`, `active=False`, lineage history, and replay.
- IL5 stands: `InterpretationRejection` (`spj_`) exists with the exact
  shape in the spec — diagnostics-only, never an input to resolution,
  carries no `spi_` reference, and is NOT committed to the demo set
  (synthetic tests only).
- HD6 stands: semantic dimensions gate on evidence consistency with the
  `evidence_not_assessable` reason; `declared_semantics_compatible`
  never co-occurs with `evidence_inconsistent`.
- IL6 is resolved to "closure adopted": narrowing-only, at most one per
  assertion.

Added row groups (final design):

### IN — interpretation supersession lineage (multi-parent, convergent)

| ID | Behavior at the public boundary | Failure killed |
|----|----|----|
| IN1 | Two root `spi_` records for one exact (pair, dimension) with overlapping in-scope applicability and differing bodies → `conflicted`, both candidates carried verbatim, canonically ordered by canonical bytes. | Silent winner among branches. |
| IN2 | A successor superseding only one of three current tips leaves `conflicted` with the honest remaining-tip set. | Partial convergence miscounted as resolution. |
| IN3 | A successor superseding EVERY current tip restores a single `interpreted` resolution; repeated contention after convergence conflicts again and converges again. | Non-convergent contention. |
| IN4 | Permuted `supersedes` parent order produces ONE identical record id (parent SET is identity; canonical sort + duplicate rejection before digest). | Order-sensitive identity. |
| IN5 | Supersession cycles are refused typed at validating append AND at crafted on-disk load. | Cycle acceptance. |
| IN6 | A parent id absent from the collection is refused typed (append and load and replay subset). | Dangling lineage. |
| IN7 | A parent with a different six-dimension pair is refused typed (`INTERPRETATION_SUPERSEDES_INVALID`). | Cross-property correction. |
| IN8 | A parent with a different `interpretation.dimension` is refused typed. | Cross-dimension correction. |
| IN9 | Explicit-id replay of an ancestor-only subset revives the ancestor as governing tip; a successor without full ancestry in the subset fails reference closure. | Unreplayable lineage history. |
| IN10 | The full EM6-style permutation grid over competing tips (recorded_at, authority kind/agent, append order, record id) yields the identical conflicted candidate set every time. | Hidden arbitration. |
| IN11 | Validating append refuses a second closure for one `spi_`, a retraction of a missing target, and a closure of a missing target BEFORE any write; the same states crafted on disk fail `load()` typed. No reachable append sequence can make `load()` permanently fail. | The append-only poisoned-ledger trap (adjudication F1). |

### EC — uniform model-record evidence closure (owner-mandated repair)

| ID | Behavior at the public boundary | Failure killed |
|----|----|----|
| EC1 | FAILING-BEFORE (Group 2 evidence): a `vsp_` citing `ModelRecordEvidence` for an absent record loads at 8cb5f1e; after Group 3 the same collection fails typed `MODEL_REFERENCE_INVALID`. | The inherited unchecked-evidence surface. |
| EC2 | The rule is uniform: `rel_`, `vsp_`, and `vsm_` records citing absent model-record evidence all fail with the same accepted code, at load, at prospective append, and at explicit replay subsets. | Per-kind divergence. |
| EC3 | A replay subset omitting a record cited as model-record evidence by a member is invalid. | Evidence-dangling replays. |
| EC4 | The committed ledgers load unchanged and every committed record id verifies after the repair (no committed record trips the rule); the byte-freeze maps now pin ALL 14 model + ALL 11 binding records. | Accepted-history breakage or unpinned mutation. |
| EC5 | Foreign evidence arms (owner_declaration, identity_binding_record, source_raw_record, temporal_occurrence, structural_source_locator) remain declared references: never dereferenced, never validated against foreign ledgers (a syntactically valid foreign id that matches nothing still loads). | Scope creep into cross-ledger validation. |
| EC6 | `rwd_` remains uncitable in `ModelRecordEvidence`; `vsm_` is citable. | Withdrawals cited as claims. |

### MH — membership helper promotion

| ID | Behavior at the public boundary | Failure killed |
|----|----|----|
| MH1 | `identity_binding.resolver.membership` is importable, pure, and total over (AppliesScope, aware datetime); all nine start/end boundary-kind combinations pinned by behavior vectors; results identical to the pre-promotion accepted behavior (the IB suite passes byte-unchanged). | Behavior drift smuggled in with the promotion. |
| MH2 | The interpretation resolver IMPORTS the helper (AST assertion: no local membership reimplementation); the surrounding eight-case classification's parity with IB semantics is pinned by shared hand-authored vectors. | A drifting second applicability algorithm. |

### DC — declared_semantics_compatible conjunction (each clause independently falsified)

| ID | Falsified clause | Expected instead |
|----|----|----|
| DC1 | no observation | `observation_absent`; no verdicts |
| DC2 | observed, unattached | `observation_not_attached`; interpretation still carried (F10 lock: observation existence, not attachment) |
| DC3 | evidence inconsistent | `evidence_inconsistent`; `evidence_not_assessable` reasons; no verdict |
| DC4 | quantity meaning absent / conflicted | `model_meaning_not_declared` / `model_meaning_conflicted` |
| DC5 | role meaning absent / conflicted | same, via the role dimension |
| DC6 | any interpretation dimension not positively `interpreted` | the specific `source_interpretation_*` reason and finding |
| DC7 | any token pair differs | the dimension mismatch finding; no aggregate |
| DC8 | specification not specified / unit not declared | `model_specification_not_available` / `model_unit_not_declared` |

Everything below is the independent matrix, verbatim.

---

# ES-001 Adversarial Acceptance Matrix

Independent test-engineer constraint set, written BEFORE implementation
planning, at main @ 8cb5f1e. Every row asserts behavior at a PUBLIC
boundary (module contract, facade query, committed fixture, or clean
checkout) — never a private implementation detail. Any design that
cannot go green on these rows without weakening an accepted test is
rejected.

Conventions assumed from the repo (verified in the current tree):

- Six-dimension property identity = `SourceSubjectRef(source_id,
  adapter_id, subject_identifier)` + `SourcePropertyRef(extraction_route,
  item_key, json_pointer)` (`backend/temporal_state/contracts.py:49-64`).
- Applicability = `AppliesScope` on the `ingestion_received_at` axis,
  half-open, with declared/unbounded/unknown boundaries
  (`backend/identity_binding/contracts.py:80-119`). Resolution is at the
  occurrence's own `received_at`, never at `as_of`
  (`tests/model_state/test_model_state.py:87`).
- Correctable-record lineage = the `vsp_` pattern: content-derived ids,
  supersedes-tuple, tips, conflict carried verbatim, convergence records
  (`tests/model_kernel/test_specification_lineage.py`).
- Unit identity = exact triple `(system_id, system_edition, code)` byte
  equality; a `UnitReference` is an identity token, never a definition
  (`backend/model_kernel/contracts.py:366-374`). Same rule for any new
  quantity-kind or role token: identity comparison only, no semantics.
- Fixture builders reused: `tests/model_state/helpers.py` (`SUBJECT`,
  `PROP_TEMP`, `PROP_TARGET`, `full_timeline_stack`, `model_with`,
  `resolver_with`, `state_queries`), `tests/model_kernel/builders.py`,
  `tests/identity_binding/test_facade.temporal_stack`.
- Naming placeholders (the design may rename; rows bind to behavior, not
  names): "meaning record" = the model-kernel record for variable
  engineering meaning (quantity kind + observation role); "interpretation
  record" = the authority-declared source-property interpretation ledger
  entry; "semantic result" = the composed read-only facade output.

Flags: **[PINS-BYTES]** = row pins committed bytes or sha256 digests.
**[PINS-REVISION]** = row pins a computed revision id or explicit
membership list. **[EXTENDS-ACCEPTED]** = row modifies an existing
accepted test file (the exact extension discipline is stated inline).

---

## A. Model meaning record (kernel ledger) — EM rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| EM1 | A well-formed meaning record for a registered variable appends, round-trips through store load, and the kernel query returns status `specified`-equivalent ("meaning declared") carrying the record verbatim: quantity kind token, role token, evidence, authority. | `model_with(tmp_path)` + `build_record` for the new meaning kind; load; query by `V1`. | Meaning silently dropped, re-expressed, or paraphrased by the query layer. |
| EM2 | Meaning ABSENT for a registered variable is a structured status ("no meaning declared"), distinct from `not_registered`, with no record payload and no fabricated default quantity kind or role. | Registered `V1`, no meaning record; query. | "Unknown" manufactured into a default (e.g. dimensionless / measured) — CLAUDE.md "Unknown is a valid result". |
| EM3 | Meaning for an UNREGISTERED variable id: query answers `not_registered` (with the revision), and APPENDING a meaning record without the variable registration is refused with a typed kernel error — reference closure exactly as `vsp_` (`test_specification_lineage.py::TestReferenceClosure`). Crafted on-disk load and replay-subset without the registration also fail typed. | Store without `vrg_` for the target; append/load/replay. | Meaning floating free of model membership; untyped crash on crafted ledgers. |
| EM4 | SUPERSEDED: a successor citing its parent makes the parent non-tip; the query carries exactly one tip and discloses the superseded ids per-variable (never another variable's lineage — mirror `TestSupersededHistoryIsPerVariable`). Self-reference, unknown parent, cross-variable parent, and cycles are refused typed at append AND at crafted load. | Chain of two meaning records; then forged `model_construct` cyclic pair written to disk. | Correction destroying history; lineage leakage between variables; cycle acceptance. |
| EM5 | CONFLICTED: two independent tips for one variable yield a conflicted status carrying EVERY tip verbatim, canonically ordered by record id, with `meaning is None`. The set stays loadable — conflict is a disclosed state, not an integrity failure. | Two root meaning records for `V1`. | Conflict hidden, or one tip silently promoted. |
| EM6 | Conflict is NEVER resolved by recency, file order, authority label, or record id: permute `recorded_at` (later vs earlier), append order, `human_owner` vs `test_fixture` authority, and lexically smaller/larger record ids across the tips — the status stays conflicted and the carried tip SET is identical in every permutation. | Parametrized permutations of the EM5 pair. | Any hidden arbitration rule (the exact bug class `test_tips_are_never_chosen_by_recency_or_authority` kills for `vsp_`). |
| EM7 | CONFLICT-CONVERGED: a converging successor superseding BOTH tips restores a single tip; PARTIAL convergence (superseding only one of three tips) remains conflicted with the honest remaining-tip set; repeated contention after convergence conflicts again and converges again. | Mirror `test_partial_convergence_remains_conflicted` / `test_full_convergence_restores_one_tip` / `test_repeated_contention_converges_again` for the meaning kind. | Partial convergence miscounted as resolution. |
| EM8 | Quantity kind and observation role are IDENTITY TOKENS with a closed grammar (project-local identifier discipline like `LocalIdentifier`): the record asserts no dimension, no convertibility, no physical semantics; measured-vs-commanded is exactly the CLAUDE.md commanded/measured distinction and role vocabulary must distinguish them as distinct enumerated identities, not free prose. Malformed tokens (uppercase, whitespace, empty, regex metacharacters, trailing newline via the `$`-anchor trick) are refused by the behavioral grammar guard, not only the pydantic `pattern=`. | Direct contract construction with adversarial token strings incl. `"temperature\n"`. | Grammar resting on a regex-engine default (`_identifier` precedent, `backend/model_kernel/contracts.py:345-357`); prose smuggled into identity. |
| EM9 | A meaning record makes NO claim about any source: constructing one that embeds source vocabulary is impossible because the contract has no such fields (`extra="forbid"`), and the committed demo meaning record's evidence statement contains none of `moonraker, klipper, printer, extruder, hotend, json_pointer, declared_unit, adapter_id, source_id` (mirror `test_permanent_evidence_is_model_only`). | Contract introspection + committed fixture sweep. | Source knowledge in the model ledger. |
| EM10 | Meaning is a record kind DISTINCT from `vsp_`: it never enters the specification bucket, never alters `VariableSpecificationResult`, and the accepted VS-001 result contract is byte-unchanged (its module file hash / public field set is not edited by ES-001). | Load a set with registration + vsp + meaning; assert `variable_value_specification` result identical with and without the meaning record. | Meaning grafted onto the accepted specification contract, changing accepted behavior. |
| EM11 | Tampered meaning record (content edited on disk, id kept) is detected at load — content-derived id verification (`verify_record_id` discipline); identical re-append is a validated no-op producing no duplicate file and the same revision. | Byte-edit a committed-format record in `tmp_path`; re-append the same record. | Write-once violation; silent duplicate membership. |

## B. Interpretation ledger (authority-declared source-property interpretation) — IL rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| IL1 | An interpretation record is keyed by the EXACT six-dimension pair (full `SourceSubjectRef` + `SourcePropertyRef`), carries `AppliesScope`, quantity-kind token, optional interpreted-unit token, `recorded_at`, `AuthorityRef`; it appends, loads, and round-trips verbatim. It is an authority CLAIM about interpretation — never source evidence and never an identity binding: it cannot target an anchor and cannot substitute for a `BindingAssertion`. | New ledger store in `tmp_path` with `SUBJECT`+`PROP_TEMP`. | Interpretation half-keyed (subject-only or pointer-only); interpretation doubling as identity resolution. |
| IL2 | Ledger validation is ALL-OR-NOTHING: one malformed record file (bad JSON, wrong id digest, unknown field, naive datetime) fails the whole set load with a typed integrity/configuration error naming the offending record — an invalid set resolves nothing (mirror `BindingIntegrityError` discipline). | Valid set + one corrupted file. | Partial loads interpreting from a half-valid ledger. |
| IL3 | SUPERSEDED: correction-only supersession (mirror `BindingAssertion.supersedes` note: correction ≠ real-world replacement, which is closure + a new record). The prior record remains on disk, remains disclosed in resolution summaries with `superseded_by`, `active=False` (mirror `test_correction_preserves_the_prior_assertion`). | Append successor with `supersedes=` original. | History rewritten; correction deleting the audit trail. |
| IL4 | RETRACTED: a retraction record makes the target inactive; resolution over retracted roots/tips without supersession history reports `retracted`, while mixed superseded/retracted lifecycle history reports `inactive`, never `unbound`-as-if-never-declared. The retraction id is cited; simultaneous supersession + retraction loses neither link. Aggregate `superseded` is impossible, while per-assertion supersession remains disclosed (mirror `TestLifecycleStatuses::test_retracted_only`, `test_summary_cites_exact_closure_record`). | Interpretation + retraction; then + competing successor. | Retraction conflated with absence; lifecycle links dropped; dead aggregate status exposed. |
| IL5 | REJECTED: a considered-and-refused interpretation is a diagnostics-only record — it NEVER participates in resolution (present alongside an active interpretation the result is identical whole-object to the run without the rejection; present alone the status is still "no interpretation", with the rejection disclosed only in the diagnostic surface). Mirror `BindingRejection` ("never an input to resolution"). | Parametrize: rejection alone / rejection + active record. | Rejection records leaking into winner selection or blocking resolution. |
| IL6 | Applicability CLOSURE (if the design adopts IB's amendment): converting an unknown/unbounded end to a declared end narrows; changing a declared end requires supersession and is refused as a closure. If the design omits closure, the contract must have NO closure kind at all — not a half-working one. | Closure against declared-end record. | A mutation path disguised as amendment. |
| IL7 | The ledger holds NO values, NO occurrences, NO checksums of payloads-as-claims: contract has no `value_json`, `received_at`-of-observation, or occurrence fields (`extra="forbid"` + field-set introspection). Interpreting is not observing. | Contract introspection. | Evidence duplication into the interpretation ledger. |
| IL8 | Committed ES-001 interpretation fixtures live OUTSIDE `models/` (their own root, like `bindings/`), because interpretation records necessarily carry `source_id`/`adapter_id`/`json_pointer` vocabulary that the model-ledger sweep (`tests/model_state/test_isolation.py::TestLedgerVocabulary`) permanently bans from `models/demo-printer/records`. The sweep still passes over the post-ES-001 model ledger with its count guard updated. **[EXTENDS-ACCEPTED]**: extend the count `assert len(records) == 14` to the new total; do NOT remove any needle — removing `moonraker`/`json_pointer` from `LEDGER_VOCABULARY_NEEDLES` to make room for a wrongly-placed record is the weakening this row exists to kill. | Repo sweep. | Source vocabulary entering the model ledger through the new record kind. |
| IL9 | Identical re-append of an interpretation record is a validated no-op; tampering (edited content, kept id) is detected at load; record ids are content-derived over canonical serialization so the parent SET and key fields are identity while file order is not. | Same as EM11 for the new store. | Uncontrolled duplicates; undetected tampering. |

## C. Resolution semantics — RS rows

Resolution = "given a six-dimension pair and an instant on the
ingestion-receipt axis, what interpretation (if any) governs?" The
statuses below may be named differently, but each STATE must be a
distinct, non-conflatable public status (unknown / missing / invalid /
not-applicable are different states).

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| RS1 | ABSENT: no interpretation ever declared for the pair → "uninterpreted" status; result carries the ledger revision; no candidate, no default quantity kind, no unit guessed from the pointer text (`/temperature` in the JSON pointer must NOT produce "temperature" — mirror `test_no_unit_is_inferred_from_names_or_pointers`). | Empty ledger; `SUBJECT`+`PROP_TEMP`. | Semantic inference from field names — CLAUDE.md rule 7. |
| RS2 | SINGULAR: exactly one active record whose scope contains the instant → resolved, carrying the record verbatim, the applicability basis (declared interval vs includes-unbounded-claim, mirror `applicability_basis`), and the exact via-record id. | One record, `hour()` scope, instant inside. | Resolution without disclosure of basis. |
| RS3 | OUTSIDE APPLICABILITY: instant at/after declared end (half-open: the boundary instant belongs to the successor) or before declared start → `outside_applicability`, never `unbound`, never a fallback to a neighboring interval. Boundary-exact instants tested on both edges. | `hour(20,21)`; probe 19:59:59.999999, 20:00:00, 20:59:59.999999, 21:00:00. | Off-by-one on the half-open boundary; outside conflated with absent. |
| RS4 | APPLICABILITY UNKNOWN: unknown start or end boundary and the instant falls where membership cannot be decided → `applicability_unknown` carrying the candidate WITHOUT resolving it (mirror `test_applicability_unknown_candidate_never_resolved`); an unknown boundary is never treated as unbounded (`UnknownBoundary` docstring is the spec). All nine start/end boundary-kind combinations behave per the IB membership table (mirror `test_all_nine_boundary_combinations`). | `UNKNOWN_START`-style scopes, parametrized. | Unknown promoted to unbounded — manufactured completeness. |
| RS5 | CONFLICTED: two active records for the SAME pair with overlapping applicability and differing interpretation content → conflicted, all candidates carried verbatim, canonically ordered; a same-content corroborating record does NOT conflict (design must state and test which — corroboration vs conflict — but never pick a winner). | Two records, overlapping `hour()` scopes, different unit tokens. | Silent winner among competing authorities. |
| RS6 | Competing interpretations are never resolved by recency, file order, authority label, or record id: full permutation grid as EM6 over the RS5 pair — identical conflicted candidate set every time. | Parametrized permutations. | Hidden arbitration. |
| RS7 | Resolution is at the OCCURRENCE'S OWN `received_at`, not the query `as_of`: an occurrence received inside the interpretation's scope stays interpreted when queried with a much later `as_of`; an occurrence received outside stays uninterpreted even when `as_of` is inside. (Mirror `test_resolution_at_received_at_not_as_of`.) | `full_timeline_stack` occurrences at 20:00:06/12/18 + scope `hour(20,21)`; `as_of` 23:00. | The wrong time axis — the single most likely subtle bug. |
| RS8 | Superseded and retracted records are disclosed in the resolution result (summaries with lifecycle links) but never resolvable; a superseded-then-scope-matching record does not shadow its successor and vice versa; `recorded_at` is audit information and never picks winners. | Chains from IL3/IL4. | Lifecycle leakage into applicability. |
| RS9 | Naive `at`/`received_at` instants are rejected with the module's typed error BEFORE any ledger access; tzinfo-present-but-`utcoffset()->None` datetimes are also rejected (mirror `test_naive_as_of_utcoffset_none_clause`). | `datetime(2026,8,7,20,30)` naive + crafted tzinfo subclass. | Naive-datetime acceptance on one of the two guard clauses. |
| RS10 | Input-order independence: the same record SET loaded in permuted file-append orders yields byte-identical resolution results and the SAME computed revision id (canonical order = sorted record ids, never filesystem enumeration — mirror `BindingRevision` docstring). | Write the same records in three different append orders in three `tmp_path` stores. | Filesystem-enumeration-dependent behavior (breaks on other OSes and under replay). |

## D. Six-dimension identity sensitivity — SI rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| SI1 | Perturb EACH of the six dimensions independently — `source_id` (`printer-1`→`bench-2`), `adapter_id` (`moonraker`→`other_adapter`), `subject_identifier` (`extruder`→`heater_bed`), `extraction_route` (`api:moonraker:v1`→`api:moonraker:v2`), `item_key` (`printer_objects`→`server_info`), `json_pointer` (`/result/status/extruder/temperature`→`/result/status/extruder/target`) — while an interpretation is declared for the unperturbed pair: EVERY perturbed lookup is "uninterpreted"; the unperturbed lookup stays resolved. Six parametrized cases, one per dimension, each asserted individually (never a single combined case). | One declared interpretation; six one-field-off probes (extend the `test_exact_six_dimension_locator_required` pattern). | Partial-key matching (五-of-six matching) — the exact bug the six-dimension rule exists to prevent. |
| SI2 | Two source properties with IDENTICAL `json_pointer`, `item_key`, and `extraction_route` but different `source_id` or `adapter_id` never contaminate each other: declare interpretation A ("temperature, degree_celsius") for printer-1/moonraker and interpretation B ("temperature, kelvin-token") for bench-2/moonraker (and printer-1/other-adapter) — each pair resolves ONLY its own record; retracting A leaves B resolved; conflicting A leaves B singular. | Three subjects sharing `PROP_TEMP`'s property triple. | Pointer-shaped global interpretation ("everything ending /temperature is Celsius"). |
| SI3 | A changed `json_pointer` under the SAME bound subject inherits nothing: subject printer-1 stays bound/interpretable for `/temperature` while `/target` (identical in five dimensions) is independently uninterpreted until its own record exists (mirror `test_same_word_elsewhere_stays_unbound`'s route case). | `PROP_TEMP` interpreted, `PROP_TARGET` not. | Subject-level inheritance of property semantics. |
| SI4 | Case and whitespace are identity: `Extruder` vs `extruder`, trailing-space `json_pointer`, differ. No normalization, trimming, or case-folding anywhere in the key path. | Perturbed-by-case probes. | "Helpful" normalization corrupting identity. |

## E. Facade composition (semantic-compatibility result) — FC rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| FC1 | For a canonical variable anchor + `as_of`, the facade composes and carries VERBATIM (whole-object equality against independently-produced results): `VariableStateResult` (VM-001), `VariableSpecificationResult` (kernel), the meaning result, and the per-candidate interpretation resolution. `result.state == state.variable_state(...)`, `result.specification_result == ModelQueries(model).variable_value_specification(...)`, and equivalents for the two new results (mirror `test_lower_layer_results_are_whole_object_equal`). | `state_queries(...)` + new meaning/interpretation builders. | Re-expression / paraphrase of lower-layer facts — the "no second vocabulary" rule. |
| FC2 | One MODEL revision governs membership, specification, AND meaning: constructing a result whose specification-result revision, meaning-result revision, or `state.model_revision` differ is a `ValidationError` (contract validator, mirror "one model revision governs membership and specification"); likewise the interpretation resolutions all carry ONE interpretation-ledger revision and a mismatch is unconstructible. | Forge results from two different loaded revisions; attempt construction. | Frankenstein results mixing revisions — the revision-mismatch attack. |
| FC3 | Per-dimension verdict discipline (VS-001 pattern): every semantic dimension (quantity-kind agreement, role agreement, unit-identity agreement) is `evaluated`-with-finding XOR `not_evaluated`-with-reason; a reason exists exactly when not evaluated; a finding exists exactly when evaluated; the finding always agrees with the verdict (contract validators + facade behavior both tested). | Direct contract construction of every inconsistent combination → `ValidationError`. | Assertions that can't fail; verdicts without accountable reasons. |
| FC4 | Gating: NO semantic verdict without a governing meaning (absent/conflicted meaning → all semantic dimensions `not_evaluated` with the honest reason); no verdict without a resolved interpretation (uninterpreted / outside / unknown / conflicted / retracted / inactive interpretation → unit- and quantity-comparison dimensions `not_evaluated` with the specific reachable reason — never one lump). Aggregate `superseded` is rejected at contract construction; supersession remains assertion-history disclosure. The pipeline still runs: state and specification results are complete in every gated case (mirror `TestConflictDoesNotOverridePrecedence`). | Parametrize meaning × reachable interpretation statuses plus forged aggregate `superseded`. | Gates collapsing distinct absences into one reason; gated cases suppressing unrelated evidence; dead status exposed. |
| FC5 | Unattached observations get NO semantic verdict (attachment precedence, mirror "no verdict for an unattached observation") but their interpretation resolution and source-unit evidence are still DISCLOSED per-candidate. | Unregistered-variable limbo case from `TestEvidenceInLimbo`. | Verdicts on evidence that isn't attached; or disclosure suppressed for limbo evidence. |
| FC6 | Candidates are index-parallel and carried in VM-001 order; reordering or substituting a candidate in the result is unconstructible (mirror `test_candidate_reordering_is_rejected`); multiple candidates (temperature + target) get INDEPENDENT semantic verdicts (mirror `test_verdicts_are_independent_per_candidate`). | Two-locator binding set (`PROP_TEMP`, `PROP_TARGET`). | Cross-candidate verdict bleed. |
| FC7 | The facade constructor validates injected types (typed configuration error on wrong types, mirror `MODEL_STATE_INPUT_INVALID` / `test_constructor_type_is_validated`); queries validate the anchor-id grammar and `as_of` before any store access; upstream typed errors (ModelKernelError, IdentityBindingError, TemporalError incl. storage-unavailable) propagate UNCHANGED. | Bad constructor args; malformed ids; deleted temporal.db (`test_temporal_store_unavailable_propagates_unchanged`). | Error-code laundering; late validation after partial reads. |
| FC8 | No aggregate/normalized/filled/winning/current/usable value ANYWHERE: serialized result JSON contains none of `normalized, converted, canonical_value, best, winner, current_value, usable, effective_value` and no float re-encoding of `value_json` (stays the exact string `"60.4"`, mirror `test_nothing_is_normalized_converted_filled_or_selected` + `test_no_aggregate_or_selected_value_fields_exist`). | Serialize the full result; sweep. | Value selection sneaking in under a new name. |
| FC9 | Mutating the injected model/resolver/ledger objects after construction cannot desynchronize an already-returned result, and a fresh query reflects a coherent single revision (mirror `test_mutating_the_injected_model_cannot_desynchronize_the_result`). | Mutate `loaded` dicts post-hoc. | Aliasing bugs producing mixed-revision answers. |

## F. Semantic verdict cells (quantity, role, unit) — SV rows

All cells run with: model meaning declared (quantity `temperature`, role
`measured_actual`), model unit declared (`project_local/ohk-units-1/
degree_celsius` — the committed `vsp_c8e5d9…` content), over
`full_timeline_stack` evidence unless stated.

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| SV1 | QUANTITY MATCH + ROLE MISMATCH: interpretation says quantity `temperature`, role facts differ (model role `measured_actual` vs a target-property interpretation whose role claim is `commanded_target`): quantity dimension = match, role dimension = mismatch, EACH reported independently; the overall result never averages dimensions into one "compatible" boolean without the per-dimension findings. | Meaning `measured_actual` on the variable, interpretation for `PROP_TARGET` declaring `commanded_target`. | Role collapsed into quantity; single-boolean compatibility. |
| SV2 | ROLE MATCH + QUANTITY MISMATCH: interpretation `pressure`/`measured_actual` vs model `temperature`/`measured_actual`: quantity = mismatch, role = match, unit dimension still independently evaluated (or independently reasoned not-evaluated) — quantity mismatch must NOT suppress the unit comparison silently; whichever gating the design chooses must be an explicit reason, tested. | Interpretation with a different quantity token. | Cross-dimension suppression without a disclosed reason. |
| SV3 | MEASURED vs TARGET remain distinct despite IDENTICAL quantity kind AND identical unit token: two variables (hotend temperature `measured_actual`, hotend target `commanded_target`), both quantity `temperature`, both unit `degree_celsius`, bound to `PROP_TEMP` and `PROP_TARGET` respectively — each variable's result attaches only its own property's evidence, the role dimensions differ per variable, and swapping the two interpretations flips the role verdicts symmetrically. | Second registered variable + `PROP_TARGET` binding (helpers already define `PROP_TARGET`). | The commanded/measured conflation CLAUDE.md forbids — identical (quantity, unit) treated as identical meaning. |
| SV4 | UNIT MATCH: interpretation's unit token exactly equals the model's declared triple → unit-identity dimension = match, and the match is TOKEN identity: results disclose both tokens' provenance (authority-interpreted vs model-required) as separate fields, never a merged "the unit". | Interpretation `degree_celsius` triple. | Provenance merge on agreement. |
| SV5 | UNIT MISMATCH: interpretation `degree_fahrenheit`-token vs model `degree_celsius` → mismatch, both tokens carried, NO conversion, NO numeric transformation of `value_json` anywhere in the result. | Interpretation with a different `code`. | Helpful conversion. |
| SV6 | UNIT TRIPLE SENSITIVITY: same `code`, different `system_edition` (`ohk-units-1` vs `ohk-units-2`) → mismatch; same for `system_id` if a second literal ever exists. Exact triple equality only. | Perturb each triple member. | Code-only comparison. |
| SV7 | SOURCE-UNIT ABSENT + AUTHORITY INTERPRETATION PRESENT: the accepted VS-001 fact stands — `source_unit_evidence == "absent"`, `declared_unit_lexeme_relation == "not_evaluated"` with reason `source_unit_absent` — while the NEW result additionally reports the authority-interpreted unit vs model unit identity comparison. The authority's interpretation NEVER changes `source_unit_evidence` from `absent`: an interpreted unit is not source evidence. | The committed demo chain (model declares Celsius, Moonraker supplied nothing). | The milestone's central conflation: interpretation back-filling source evidence. |
| SV8 | SOURCE-SUPPLIED UNIT + INTERPRETATION BOTH PRESENT: when an occurrence carries `declared_unit="degC"` (synthetic temporal fixture), the result discloses THREE independent facts — source lexeme (verbatim string), authority-interpreted token, model-required token — and at most pairwise comparisons with distinct field names; no transitive equivalence is fabricated (source "degC" matching neither token is three disclosures, zero merges). | Synthetic occurrence with a `declared_unit`. | Lexeme/token conflation; transitive unit equivalence. |
| SV9 | UNSUPPORTED CONVERSION IS NOT A CONCEPT: no public API accepts a target unit, no result field names a conversion outcome, and the serialized result of SV5 contains no numerically-converted value (e.g. `140` for `60.4` never appears; sweep the JSON for any numeral other than the verbatim lexemes). API surface introspection + serialization sweep. | SV5 setup. | A convert-on-request backdoor. |
| SV10 | Meaning declared but model unit NOT declared (`UnitNotDeclared`) while interpretation declares a unit: unit-identity dimension = not-evaluated with reason "model unit not declared" (distinct from interpretation-absent), quantity/role dimensions still evaluated. The model's explicit not-declared claim is never overwritten by the interpretation. | `vsp` with `kind="not_declared"` + interpreting record. | Interpretation "completing" the model. |

## G. Evidence separation — ES rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| ES1 | `declared_unit=None` BYTE-IDENTICAL before and after composition: `occurrence.declared_unit is None`; the occurrence object inside the composed result `==` the occurrence from a direct `temporal.latest_observed(SUBJECT, PROP_TEMP, AS_OF)` (whole-object); the serialized candidate JSON contains `"declared_unit":null` and none of `degree_celsius, ohk-units-1, project_local, celsius, Celsius, kelvin, fahrenheit, temperature_unit` (extend the `test_celsius_is_never_manufactured` token list with the ES-001 vocabulary: quantity/role tokens must ALSO not appear inside `state_candidate`). | Committed demo chain. | Interpretation tokens leaking into carried source evidence. |
| ES2 | Interpreted unit NEVER serialized into temporal evidence: run the full ES-001 demonstration, then (a) `temporal.ordered_logical_dump()` equals the pre-composition dump, (b) a sweep of the temporal store bytes + raw-store files finds no interpretation vocabulary (unit tokens, quantity tokens, role tokens, interpretation record ids), (c) the data_sources store is byte-identical (`sweep()` before/after, mirror `TestUpstreamImmutability`). | `temporal_stack` + demo run + `sweep(ds_store.base_dir, tmp_path)`. | Composition writing semantics back into evidence stores. |
| ES3 | Model-required unit never presented as SOURCE evidence: the result field carrying the model unit is reachable ONLY under the specification/model side of the result tree (assert by walking the serialized structure: every occurrence of the model unit token has a JSON path prefixed by the specification/meaning result, never by `state`/`state_candidate`/occurrence paths). | Serialize; walk paths. | Structural leak the flat token sweep can't see (token present legitimately in spec AND illegitimately in evidence would pass a naive "token exists" check — path-scoped sweep kills it). |
| ES4 | Authority-interpreted unit never presented as source evidence: same path-scoped sweep for the interpretation token; additionally the `CandidateObservation`/`BoundObservation` accepted contracts are UNCHANGED (no new fields added to accepted VM-001/TS-001 types — field-set introspection against the accepted list). | Field-set snapshot of accepted contracts. | "Just one convenience field" on an accepted evidence contract. |
| ES5 | The interpretation ledger fixture files contain no observation values: sweep committed ES-001 fixture records for `60.1`, `60.4`, `value_json`, `occurrence`, checksums of the Moonraker payloads. | Fixture sweep. | Evidence copied into interpretation fixtures "for context". |

## H. Hardening — HD rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| HD1 | FORGED instances via `model_construct` at EVERY operational public boundary: (a) forged interpretation/meaning records passed to store `append` are structurally revalidated or refused typed (kernel `test_mk_repairs` forge pattern); (b) forged records written directly to disk fail `load` typed; (c) a forged selector/locator passed to the facade fails as the module's INPUT_INVALID without leaking a raw `ValidationError` (mirror `test_forged_selector_never_leaks_a_raw_validation_error`); (d) the new result contracts carry `revalidate_instances="always"` so forging THIS module's nested contracts is rejected on revalidation (mirror `test_this_modules_own_contracts_reject_forged_instances`); (e) carried lower-layer objects remain trusted-by-producer and that boundary is documented+tested (mirror `test_carried_lower_layer_objects_are_trusted_by_their_producer`). | `model_construct` forgeries per boundary, incl. broken nested anchors and out-of-grammar tokens. | Validation-bypass acceptance anywhere on the operational surface. |
| HD2 | NAIVE DATETIMES rejected everywhere they can enter: record `recorded_at` (AwareDatetime at contract level), scope boundaries, facade `as_of`, resolution `at` — each independently, both truly-naive and `utcoffset()->None` tzinfo. Every accepted instant is normalized to UTC on the result (`UtcDatetime` discipline). | Parametrized per entry point. | One forgotten entry point. |
| HD3 | Non-string / wrong-type inputs at facade queries (int anchor id, bytes as_of, dict selector) → typed error with the module's own code, before any store access (assert no store file was opened: run against a store path that does not exist and expect the INPUT error, not a storage error). | Bad-input grid (mirror `test_malformed_inputs_typed`). | Input validation happening after I/O. |
| HD4 | ORDER INDEPENDENCE, full grid: (a) record FILE order on disk (write orders permuted) — same revision id, same results; (b) resolver/facade construction order of injected objects irrelevant; (c) ledger append order across interleaved kinds (meaning, interpretation, retraction) — same statuses. Assert whole-object result equality across permutations, not just statuses. | Three permuted `tmp_path` stores per case. | Order-dependent tie-breaking hiding under passing single-order tests. |
| HD5 | The new stores refuse absolute-path escape and honor the write-once discipline: appending a record whose id already exists with DIFFERENT content is a typed integrity error (never an overwrite); store roots under `tmp_path` only in tests. | Append-conflict attempt. | Silent overwrite of a ledger record. |
| HD6 | Deep/adversarial payload robustness at the semantic layer: an occurrence with pathological `value_json` (deep nesting, huge integers, non-finite constants) reaches ES-001 composition as the accepted VS-001 OUTCOMES (`value_json_malformed`, `value_not_representable`) and the semantic dimensions gate on evidence-consistency with a disclosed reason — no recursion error, no float inf (mirror `TestGateRepairs`). | Reuse VS-001 adversarial lexeme fixtures. | Semantic layer crashing on evidence VS-001 already survives. |

## I. Replay, revisions, and byte-freeze — RP rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| RP1 | **[PINS-REVISION]** REPLAYED MODEL REVISIONS: after the ES-001 meaning append, (a) the current pre-ES-001 revision `mrv_702c840f…` (14 records) replays by EXPLICIT id list and answers "no meaning declared"; (b) the VS-001 `mrv_25afc0eb…` (11) and pre-specification `mrv_10565807…` (10) replays still hold their accepted answers; (c) NEVER a prefix filter for membership selection (the RP2 lesson: a kind-prefix filter silently selects the wrong set after later appends — replays must subtract explicit id constants). | Extend the explicit-membership constants in new ES-001 tests (import, don't copy, the accepted lists). | History-loss; prefix-filter membership. |
| RP2 | **[PINS-REVISION]** REPLAYED INTERPRETATION REVISIONS: the interpretation ledger supports explicit-membership replay (`load_revision` discipline); the initial committed ES-001 interpretation revision id is pinned as a constant; replaying it after appending a later correction still resolves the ORIGINAL interpretation for in-scope instants. | Pin `rev_…`-style constant. | Unreplayable interpretation history. |
| RP3 | REVISION MISMATCH BETWEEN COMPOSED INPUTS is unconstructible (FC2's contract half) AND unproducible: drive the facade with a model replayed at `mrv_10565807…` and confirm every model-side result in the output carries THAT revision consistently; there is no code path mixing the current store's revision into a replayed query. | `committed(tmp_path, model=replayed)` pattern from `test_pre_specification_replay_is_attached_but_unspecified`. | Mixed-revision composition. |
| RP4 | HISTORICAL QUERY CLOSURE UNDER LATER APPENDS: capture a full semantic result; append a superseding meaning + a superseding interpretation; re-run at the same `as_of` against the OLD replayed revisions → whole-object-equal result; against the NEW revisions → changed result that discloses the supersessions. Later ingestion also cannot rewrite an earlier `as_of` (mirror `test_later_ingestion_cannot_rewrite_an_earlier_cutoff`). | Before/after append comparison. | Append-visibility bleeding into historical answers. |
| RP5 | **[PINS-BYTES]** BYTE-FREEZE, COMPLETE: sha256 of ALL 14 committed model records and ALL 11 committed binding records (6 in `bindings/demo-printer`, 5 in `bindings/demo-printer-model`) pinned. NOTE the current gap this row closes: `FROZEN_MK001_RECORDS`+`FROZEN_VS001_RECORD`+`FROZEN_VM001_RECORD` freeze only 11/14 model records (the three SN-001 records `reg_c17de…`, `rel_29785…`, `rtd_04b8d…` are authority-checked but NOT hash-pinned) and `FROZEN_PRE_SN001_BINDING_RECORDS` freezes only 7/11 binding records (`iba_2061…`, `iba_22a8…` in demo-printer; `iba_162f…` and `anc_4a576f…` in demo-printer-model are unpinned). ES-001 tests must pin the missing 3+4 digests BEFORE the milestone's own appends land, so "ES-001 touched an accepted byte" is mechanically detectable. **[EXTENDS-ACCEPTED]**: add digests to the freeze maps in `tests/model_kernel/test_demo_model.py`; never alter an existing digest. | `hashlib.sha256` over committed files. | Accepted-fixture mutation smuggled in with the ES-001 commit. |
| RP6 | **[PINS-BYTES]** NO MUTATION OF EXISTING LEDGERS/EVIDENCE: ES-001 changes to `models/demo-printer` are ADD-ONLY (new record files; every pre-existing file byte-identical per RP5); `bindings/demo-printer` and `bindings/demo-printer-model` gain NO files unless the design explicitly needs a binding (if it does, the new files carry an `es001_*` fixture agent and the per-record authority maps are extended); `var/raw_store` and all temporal fixtures untouched (git-status + digest check in the acceptance evidence). | Digest sweep + `git diff --stat` discipline in the verification report. | "Small fixups" to accepted history. |
| RP7 | `test_no_accepted_record_hash_changed` (content-derived id verification over every loaded record) still passes over the post-ES-001 ledger including the new record kinds. **[EXTENDS-ACCEPTED]**: the count assertion `record_count == 14` in that test and in `test_golden_revision_and_membership` moves to the new total with the NEW current-revision constant pinned; the old constant remains pinned via RP1's replay. | Run the accepted test extended. | Reviving records that no longer verify. |

## J. Architectural isolation — AI rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| AI1 | NO WRITES FROM THE FACADE: AST sweep of the new facade package — no store construction (`ModelStore`, `BindingStore`, `TemporalStore`, the new interpretation store class), no `append` attribute calls, no `sqlite3`, no `open(..., "w")`, no path literals (`models/`, `bindings/`, the new fixture root, `temporal.db`, `/home/`, `/mnt/`) — mirror `tests/model_state/test_isolation.py` with a count-guard so the sweep is never vacuous. PLUS the behavioral half: a full demonstration run leaves every injected store byte-identical (ES2). | New `test_isolation.py` for the facade package. | A write path or hidden repository in "read-only" composition. |
| AI2 | NO REVERSE IMPORTS INTO ACCEPTED LOWER LAYERS: `backend/temporal_state`, `backend/identity_binding`, `backend/model_kernel`, `backend/model_state`, `backend/observation_compatibility`, `backend/data_sources`, `backend/system_identity` import neither the new facade nor the new interpretation ledger package (AST sweep over every lower-layer file, mirror `TestReverseBoundaries::test_lower_layers_never_import_the_facade`). **[EXTENDS-ACCEPTED]**: add the two new package names to the FORBIDDEN lists in the accepted isolation tests of model_state and observation_compatibility (additive needle — strengthens, never weakens). | Extend existing sweeps. | Accepted layers growing a dependency on ES-001. |
| AI3 | NO SOURCE/VENDOR VOCABULARY IN UNIVERSAL KERNEL PRIMITIVES beyond identity tokens: the meaning record's contract source contains none of `moonraker, klipper, printer, extruder, hotend, source_id, adapter_id, json_pointer, extraction_route, item_key, declared_unit`; quantity-kind/role vocabularies are open token grammars (project-local identifiers), never Literal enums of device concepts. Kernel package sweep (extend the model_state needle-import pattern: the structural-evidence suite IMPORTS `LEDGER_VOCABULARY_NEEDLES`; ES-001 tests import, never copy, the needle constants). | AST/text sweep over `backend/model_kernel` additions. | Device semantics hard-coded into the kernel. |
| AI4 | The interpretation ledger package imports at most `system_identity` (if it targets anchors — per IL1 it must not), `temporal_state.contracts` (for the six-dimension locators), `identity_binding.contracts` (for AppliesScope/AuthorityRef reuse, if the design reuses rather than redefines — either way ONE definition of AppliesScope must govern; a second divergent copy is refused by an equality/import test), and pydantic/stdlib. Never `data_sources`, never `model_state`, never the facade. | Import sweep + "AppliesScope is the identity_binding class or a tested-equal contract" assertion. | Contract forking (two subtly different AppliesScope semantics). |
| AI5 | NO SECRETS OR ABSOLUTE PATHS in any new committed fixture: the standard needle sweep (`/home/`, `/mnt/`, `C:\\`, `password`, `secret`, `Bearer`, `api_key`) over the new fixture root and every new record file, count-guarded. | Mirror `test_no_secrets_or_absolute_paths_committed`. | Leakage via fixtures — CLAUDE.md hard rule. |

## K. Demonstration (demo-printer hotend + Moonraker chain) — DM rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| DM1 | THE COMPLETE ES-001 CHAIN over committed fixtures: committed model (meaning: quantity `temperature`, role `measured_actual` for `var_b7e2d3…`) + committed binding set + committed interpretation ledger (six-dimension pair for `SUBJECT`+`PROP_TEMP` interpreted as `temperature` in `project_local/ohk-units-1/degree_celsius`, applicability covering the accepted 20:00–21:00 receipt hour) + frozen three-occurrence timeline (60.1/60.1/60.4) → at `as_of` 20:30: attached candidate `value_json == "60.4"` with unchanged provenance (occurrence `cd2579c5…`, raw record `698aa72a…`, checksum `sha256:6771710d…`), quantity dimension MATCH, role dimension MATCH, unit-identity MATCH between authority-interpreted and model-required tokens, while `source_unit_evidence` stays `absent` and `declared_unit` stays `None` (SV7 live). **[PINS-BYTES]** on the provenance constants (already pinned in the VS-001 demo — import them). | Extend the `committed(tmp_path)` builder from `tests/observation_compatibility/test_demo_compatibility.py` with the new facade. | A demonstration that "works" only on synthetic fixtures. |
| DM2 | MEASURED vs TARGET adjacent synthetic counterexample: leave the committed demonstration and its interpretation ledger unchanged at exactly three `spi_` records, all for `PROP_TEMP`. In an offline temporary ledger/binding setup only, interpret `PROP_TEMP` as `temperature` / `measured_actual` / `degree_celsius` and `PROP_TARGET` as the identical quantity and unit but role `commanded_target`. The measured variable reports quantity and unit matches while the target candidate reports a role mismatch and withholds `declared_semantics_compatible`, proving identical quantity and unit do not collapse measured and commanded roles. | `PROP_TARGET` from helpers with temporary interpretations and binding; no committed `PROP_TARGET` record or ledger mutation. | The exact conflation the milestone exists to prevent without fabricating committed evidence. |
| DM3 | OUTSIDE THE DECLARED HOUR: the same query at a receipt-time past the interpretation's applicability end reports the interpretation `outside_applicability` for that occurrence with semantic dimensions honestly not-evaluated — while the identity binding and observation evidence remain exactly as VM-001/VS-001 report them (mirror `test_outside_declared_hour_is_outside_applicability`). | Second timeline receipt outside the hour, or replayed scope. | Applicability theater — scopes declared but never demonstrated to gate. |
| DM4 | OFFLINE: the demonstration runs from frozen fixtures only — the scripted transport (`happy_script`/`fixture_response`) and committed ledgers; no network, no live Moonraker; assert no socket use by construction (the accepted transport-script pattern already guarantees it — the row requires the demo to use `full_timeline_stack`, not a live connector). | `full_timeline_stack(tmp_path)`. | A demo that silently depends on a reachable printer. |
| DM5 | PRE-ES-001 REPLAY THROUGH THE DEMO: the demonstration re-run with the model replayed at `mrv_702c840f…` (no meaning) and/or an empty interpretation ledger answers with the honest absences (EM2/RS1) over the SAME frozen evidence, and every VS-001 demo assertion still holds verbatim. **[PINS-REVISION]** | `committed(tmp_path, model=replayed)`. | The new layer breaking accepted answers when its inputs are absent. |

## L. Verification matrix — VM rows

| ID | Behavior at the public boundary | Setup sketch | Failure killed |
|----|----|----|----|
| VM1 | FOCUSED: the new suites (`tests/<new_kernel_area>`, `tests/<interpretation_ledger>`, `tests/<semantic_facade>`) pass under `.venv/bin/python -m pytest -o addopts=""`; every new failure-path test is demonstrated RED first (red-baseline evidence in the report, per the repo's red-baseline plan convention). | Documented commands + captured red output. | Tests born green proving nothing. |
| VM2 | FULL SUITE: `.venv/bin/python -m pytest -o addopts="" tests/` passes with ZERO modifications to accepted tests except the explicitly-listed **[EXTENDS-ACCEPTED]** rows (IL8, AI2, RP5, RP7, and the per-record authority-map additions); the acceptance report enumerates every touched accepted test file with its diff rationale. Deleting, skipping, or loosening any accepted assertion is a rejection. | Full run + diff audit. | Green-by-weakening. |
| VM3 | BASE-ONLY CLEAN CHECKOUT: fresh venv from `requirements.txt` + `requirements-dev.txt` only, clean `git clone`-equivalent worktree → the ES-001 suites and the full non-extras suite pass; ES-001 must not import cad/pdf extras anywhere. | Clean-checkout column per the VS-001 plan convention (`docs/superpowers/plans/2026-08-09-vs001-…` §Verification). | Hidden dependency on an extras package. |
| VM4 | ALL-EXTRAS CLEAN CHECKOUT: + `requirements-cad.txt` + `requirements-pdf.txt` → full suite passes identically; ES-001 results are byte-identical across the two columns (semantics never depend on which extractors are installed). | Both columns, result-JSON comparison for one demo query. | Environment-dependent semantics. |
| VM5 | Per-record AUTHORITY REGRESSION (the mandatory IB/SN pattern): every NEW committed record (model meaning, interpretation ledger, any binding append) has `authority.kind == "test_fixture"` and an `es001_*` agent, asserted via an EXHAUSTIVE per-record expected-agent map in which an unlisted record FAILS (the AU1/AU2 form — never a blanket "all are test_fixture" assertion, which extension would weaken); the existing maps' entries are extended, never rewritten. **[EXTENDS-ACCEPTED]** | Extend `EXPECTED_AGENT_BY_RECORD` / the demo-model expected map. | Fixture records masquerading as human-owner decisions; regression maps degrading to blankets. |

---

## Extend vs. would-weaken register (explicit)

MUST EXTEND (additive, strengthens):
1. `tests/model_kernel/test_demo_model.py` — freeze maps gain the 3
   currently-unpinned SN-001 model digests and the ES-001 record digests;
   authority map gains `es001_*` entries; membership counts and the NEW
   current-revision constant added; old constants stay for replay (RP1,
   RP5, RP7, VM5).
2. `tests/model_state/test_isolation.py::TestLedgerVocabulary` — count
   guard updated to the new model-record total; needles untouched (IL8).
3. `tests/model_state/test_isolation.py` + `tests/observation_compatibility/
   test_isolation.py` FORBIDDEN lists — add the new package names (AI2).
4. `tests/identity_binding/test_demo_binding_set.py` — ONLY IF the design
   appends binding records: extend `EXPECTED_AGENT_BY_RECORD` and the
   record-count; also pin the 3 currently-unpinned binding digests (RP5).

EXTENSION WOULD WEAKEN (build NEW tests instead; touching these is a
red flag in review):
1. `backend/observation_compatibility/contracts.py` validators and the
   VS-001 verdict/reason tests — adding semantic fields to the accepted
   `VariableValueCompatibilityResult` changes accepted behavior; ES-001
   composes VS-001's result verbatim in a NEW contract (EM10, FC1).
2. `test_celsius_is_never_manufactured` — do not edit its token list
   in place to "account for" ES-001; write the ES-001 sweep as a new
   test with the UNION of tokens, keeping the accepted test byte-stable
   (ES1).
3. The blanket-to-map direction: any change replacing a per-record
   expected-authority map with a blanket assertion, an explicit
   membership list with a prefix filter, or a whole-object equality with
   a field-subset comparison is a weakening regardless of intent (VM5,
   RP1, FC1).
4. `tests/model_state/helpers.py` builders — extend by ADDING builders;
   changing `SUBJECT`/`PROP_TEMP`/`full_timeline_stack` semantics would
   silently re-base every accepted VM/VS test.

## Known attack surfaces beyond the owner floor (why extra rows exist)

- SI4 (case/whitespace identity), SV6 (unit-triple member sensitivity),
  SV8 (three-way unit provenance), ES3/ES4 (path-scoped leak sweeps —
  flat token sweeps cannot see a token that is legitimate in one subtree
  and illegitimate in another), RS3 (half-open boundary instants), HD4
  whole-object permutation equality, RP5's closure of the existing
  freeze-map gaps (3 model + 4 binding records currently unpinned), and
  AI4's AppliesScope-forking guard.
