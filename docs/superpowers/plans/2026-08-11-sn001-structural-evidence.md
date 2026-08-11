# SN-001 implementation plan

Spec: `docs/superpowers/specs/2026-08-11-sn001-structural-evidence-design.md`.
ADR: `docs/adr/0010-structural-evidence-normalization-and-cross-source-binding.md`.
Branch `sn001` from `1d6216f`. Strict red-first TDD; every commit green in
both columns for the tests that exist at that commit. Push nothing.

## Test registry

Every planned test, one line each: ID · behaviour · first honest commit.
IDs from earlier design rounds that were merged or renamed are retired
explicitly: M27 → merged into the redaction sweep SW1; M28 → merged into
I4; A6 → renamed FX6; A10 → renamed J5; A5e/A5f/A5g → CP5 / A5f / A5g
below. Kernel-regression tests are KR* (formerly K*, renamed to avoid
colliding with owner-ruling numbering).

| ID | Behaviour (public boundary) | Commit |
|---|---|---|
| L1 | locator construction/rejection incl. K3 `min_length=1` on parent path | 2 |
| L2 | `canonical_locator_value` injectivity per scheme; `None` parent → empty `;pp=` tail; `-` path is NOT a sentinel; no bare 32-hex | 2 |
| L3 | path fields `max_length=1024` early guard AND `canonical_locator_value` > 510 chars ⇒ typed `SN_LOCATOR_TOO_LONG` (including a legal-length path whose quoted value overruns) | 2 |
| C0 | claim/field/context contract construction; `EngineeringContext` has no default (M19 construction half); three-arm pairwise inequality (M20 construction half) | 3 |
| R1 | golden rule fingerprints (hand-authored hex literals) | 4 |
| R2 | body change ⇒ new fingerprint ⇒ new namespace | 4 |
| R3 | statement/stability change ⇒ unchanged fingerprint | 4 |
| R4 | AST: `apply_rule` reads exactly the body's `model_fields` | 4 |
| R5 | hand-authored behaviour vectors incl. case-differing headers (K5 prose) | 4 |
| R6 | two bodies differing only in `column_name_as_extracted` ⇒ different namespaces | 4 |
| R7 | two configs differing only in `header_row_index` through the real `csv_extractor_identity` ⇒ different namespaces | 4 |
| R8 | adversarial values `a:b`, `a/b`, `..`, `%3A`, `-`, forged 8-part string | 4 |
| R9 | 9-way perturbation (8 namespace components + `source_id`) ⇒ distinct subjects | 4 |
| R10 | namespace parse round-trip; 7/9-part strings raise `SN_NAMESPACE_INVALID` | 4 |
| R11 | length cap; max case 254 ≤ 256 | 4 |
| R12 | encoder-drift literals: exact `quote(v, safe="")` output pinned for the adversarial set incl. `-` | 4 |
| CL1 | CSV claims replayable from the persisted `ExtractionResult` after source `unlink()` (M3) | 5 |
| CL2 | missing extraction ⇒ typed error at the claims boundary (M4 finding-form lands at 13) | 5 |
| CL3 | identical source names never one subject (M6) | 5 |
| CL4 | quantity lexeme verbatim; no `int()`; no instance count derivable (M14) | 5 |
| CL5 | full traceability to row/column/raw-record (A9, DS-001 criterion preserved) | 5 |
| CL6 | claim-set canonical ordering under reversed/adversarial enumeration (claim-level M1 precursor) | 5 |
| CL7 | filename parametrization: no view inferred from `as_built_assembly.step`-style names (M19 inference half) | 5 |
| CL8 | `bom_parent_column` within-source lookup: unique ⇒ claim; zero/multiple ⇒ `UnresolvedParentReference`, no claim | 5 |
| I1a | AST sweep `backend/structural_evidence/**`: no anchor/canonical-id minting, no `assembly_definition_contains` literal (asserted ABSENT here; exactly-once over `models/demo-printer/records/**` is I1c at 16) | 6 |
| I2 | no write path (`ModelStore`, `BindingStore`, `FilesystemRawStore`, `build_record`, `.append(`, write-mode `open(`) | 6 |
| I3 | import allow-list pinned exactly, both directions (curated `model_kernel` type surface IS allowed) | 6 |
| I4 | byte-sweep `models/`, `bindings/`, `var/` (+ `showcases/` from 8) across derivation incl. failure paths; corpus-size guard | 6 |
| I5 | no `LifecycleView` MEMBER literal in SN-001 source (the imported type and the `declared_lifecycle_view` discriminator are expected) | 6 |
| I6 | no module-level `Literal` alias re-expressing `ResolutionStatus`; comparisons against carried `.status` expected | 6 |
| A5b | module docstring verbatim | 6 |
| A5c | runtime-storage wording verbatim | 6 |
| A5h | K1 contract wording verbatim | 6 |
| A5i-a | SN-001a README limitations subset {1, 6, 7, 10, 12, 14, 15, 16} verbatim | 6 |
| SW1 | no absolute paths/secrets in any SN-001 output or committed showcase file; anti-vacuity guard (absorbs M27) | 6, extended 9 |
| SC1 | STEP definition/usage claims: per-kind counts, never totals (M11 Tier-2 frozen twin; Tier-1 `cad` half) | 9 |
| SC2 | corrupted STEP ⇒ quarantine, zero claims (M5, `cad`) | 9 |
| SC3 | repeated sub-assembly ⇒ `ambiguity="multiple_parent_uses"`, `steps=()` (M13; golden path count from `SOURCES.md`) | 9 |
| SC4 | upstream-id cross-check verified on read; mismatch is loud | 9 |
| SC5 | parenthood only from `parent_definition_ref`; root-only `None` | 9 |
| M2a | claim-set determinism: byte-identical claim sets across two `PYTHONHASHSEED` subprocesses | 9 |
| FX1–FX5, FX7, FX8 | fixture integrity, base-only (spec §demonstration) | 8 |
| FX6 | live STEP extractor == frozen `ExtractionResult`, full-object incl. literal upstream ids (`cad`; formerly A6) | 9 |
| A11 | golden literal upstream ids for the frozen showcase | 9 |
| A5a | showcase honesty label verbatim | 8 |
| KR1 | committed ledger loads under 6-arm union; all 11 ids verify; `mrv_25afc0eb…` pinned (migrates to RP1 at 16) | 11 |
| KR2 | five pre-existing evidence arms byte-identical to hand-authored literals | 11 |
| KR3 | `set(model_kernel.__all__)` == 54-name literal; every name resolves; `test_public_surface_is_53_names` renamed `test_public_surface_name_count`, 53 → 54 | 11 |
| KR4 | restated arm patterns added to `test_cross_layer_seam.py::test_restated_constants_equal_upstream` | 11 |
| X5 | real `rel_` carrying the arm appended in `tmp_path`; `ModelQueries` discloses `declared_reference` | 11 |
| X1/X1b | locator ↔ evidence round-trips both ways incl. `None` parent, adversarial paths | 12 |
| X2 | source fields carried verbatim | 12 |
| X3 | `dropped == ("extractor_toolchain", "source_id")` sorted literal | 12 |
| X4 | scheme/field vocabulary vs the accepted needle lists (imported, not copied); anti-vacuity anchor lands at 16 | 12, re-anchored 16 |
| X6 | quoted locator value > 510 chars ⇒ typed `SN_LOCATOR_TOO_LONG` from `to_kernel_evidence`, never a raw `ValidationError` at the kernel boundary | 12 |
| M1 | reversed source enumeration ⇒ full-object equality + equal `inputs_digest` | 13 |
| M2 | `inputs_digest` vs hand-authored hex literal; 2 `PYTHONHASHSEED` subprocesses | 13 |
| M4 | missing extraction ⇒ `evidence_unavailable` PRESENT | 13 |
| M7 | duplicate label reported AND two distinct subjects | 13 |
| M8 | competing anchors ⇒ `mapping_ambiguous`, sorted candidates, correct basis | 13 |
| M15 | quantity-vs-model check, parametrized over the lexeme against the joined registered count (always 1): `"4"`, `"8"`, `"1.0"`, `"01"` ⇒ `quantity_not_reconcilable_with_registered_instances`; `"1"` ⇒ no quantity finding; `None`/`""` on a declared quantity field ⇒ `evidence_incomplete`; the showcase quantity-vs-STEP-usages case pins `claims_not_comparable` | 13 |
| M16 | bom-only/step-only distinct literals per anchor | 13 |
| M17 | absence ⇒ `absence_is_not_evidence_of_absence`; `RelationshipWithdrawal` asserted by name | 13 |
| M18 | contradiction carries both claims verbatim + the comparison | 13 |
| M20 | declared/view-independent/unknown results pairwise unequal (reconciliation form) | 13 |
| M21 | wrong view ⇒ `context_incompatible`, with positive twin | 13 |
| M23 | retracted/superseded/conflicted pairwise unequal in one test | 13 |
| M24 | `outcome="partial"` ⇒ `evidence_incomplete` even when corroboration is otherwise possible | 13 |
| M29 | no network/wall clock: AST + two injected `resolution_at` values ⇒ predictable distinct digests | 13 |
| CS1 | no anchor in two committed sets (re-run over enlarged sets at 15 as CS1′) | 13 |
| CS2 | forward vs reversed resolvers ⇒ equal result + digest (no `position` field exists) | 13 |
| CS3 | same subject bound in 2 sets to same anchor ⇒ `subject_bound_in_multiple_sets_consistently`, both disclosed | 13 |
| CS4 | different anchors across sets ⇒ `mapping_conflicted_across_sets`, no join | 13 |
| CS5 | duplicate anchor declarations across supplied sets ⇒ reported | 13 |
| CS6 | missing required set ⇒ finding + `not_proposable`, never partial success | 13 |
| CS7 | empty/duplicate resolver inputs ⇒ typed errors | 13 |
| CS8 | digest sensitivity: 7 flips (claim lexeme, rule fp, each set revision, model revision, `resolution_at`, toolchain fp) ⇒ distinct digests | 13 |
| CS9 | naive `resolution_at` ⇒ `SN_NAIVE_RESOLUTION_AT` | 13 |
| J1 | AST: `_join_index` is the only claim-keyed mapping builder | 13 |
| J2 | rename invariant (K8/3): joins, resolutions, and proposal targets unchanged; digest CHANGES because verbatim evidence changed; no name is a join key | 13 |
| J3 | all 8 non-`bound` statuses ⇒ no join, correct mapping finding | 13 |
| J4 | published join sentence verbatim (A5d) | 13 |
| J5 | renaming anchors' display names changes nothing anywhere (formerly A10) | 13 |
| CP1 | `("2","2.0")` ⇒ contradictory (no numeric normalization) | 13 |
| CP2 | absent operand ⇒ `not_comparable`, validator-enforced via `model_construct` | 13 |
| CP3 | C2 compares parent anchors, never parent names | 13 |
| CP4 | same anchor, no comparator row ⇒ `claims_not_comparable` | 13 |
| CP5 | `"sources_disagree"` literal absent from source and docs | 13 |
| CP6 | forged `ClaimComparison` re-validation rejected | 13 |
| S1–S3 | per-basis empty support rejected | 13 |
| S4 | fabricated-but-valid supporting claim rejected by `_support_is_disclosed` | 13 |
| S5 | `ModelDisclosure` citing a record absent from the revision rejected | 13 |
| S6 | fabricated resolution rejected | 13 |
| A1 | changed payload checksum ⇒ `cited_payload_checksum_differs`, both disclosed | 13 |
| A2 | jointly incoherent mappings ⇒ `mappings_jointly_incoherent` | 13 |
| A3 | finding multiset vs golden `Counter` + full subject coverage under reordering | 13 |
| A4 | per-literal basis table asserted independently of `BASIS_BY_FINDING` | 13 |
| A5f | `resolution_at` semantics wording verbatim | 13 |
| A5g | no re-expressed `ResolutionStatus` wording verbatim | 13 |
| A7 | digest changes when any input changes (with CS8) | 13 |
| A12′ | negative corpus: multiset exactly `{source_subject_unmapped: N}`; four literals asserted absent; `not_proposable` | 13 |
| P1/P2 | proposal negative/positive twins (M9+M10) | 14 |
| P3 | usage alone never proposes `physical_instance`; interpretation load-bearing (M12) | 14 |
| P4 | unregistered anchor blocks acceptance; every revision unchanged; positive twin (M22) | 14 |
| P5 | `SN_REVISION_MISMATCH` on stale `propose` (M25) | 14 |
| P6 | append failure ⇒ counts/revision asserted, not the exception (M26) | 14 |
| P7 | proposal inertness: no record attr, no kernel-id attr, exact `caller_must_supply` tuples per frozen table (A8) | 14 |
| P8 | unknown context ⇒ nothing proposable (M19 materialization half) | 14 |
| AU1 | exhaustive per-record authority maps, both binding sets (`ib001_demo_fixture` ×4, `sn001_showcase_fixture` for `iba_S1`/`iba_S2`; `mk001_demo_fixture` ×3, `sn001_showcase_fixture` for `anc_S3`/`iba_S4`); unlisted record fails | 15 |
| RP4 | `load_revision(ORIGINAL_FOUR)` == `rev_8605f52c…`; Moonraker subject still `bound` | 15 |
| RP5 | `load_revision(ORIGINAL_THREE)` == `rev_b4878a69…` | 15 |
| CS1′ | seam duplicate-anchor check over the enlarged sets | 15 |
| AU2 | exhaustive per-record authority map, model set (`mk001_demo_fixture` ×11, `sn001_showcase_fixture` ×3); replaces `test_demo_model.py:43`'s blanket agent assert | 16 |
| RP1 | `replay(ELEVEN_IDS)` == `mrv_25afc0eb…` (GOLDEN_REVISION re-pinned: `load()` now asserts the new 14-record `CURRENT_REVISION` literal) | 16 |
| RP2 | `replay(TEN_IDS)` == `PRE_SPECIFICATION_REVISION`; converts BOTH `vsp_`-prefix filters (`test_demo_model.py:232` and `test_demo_compatibility.py:122`) | 16 |
| RP3 | `replay(NINE_IDS)` == `PRE_VARIABLE_REVISION` (existing; not regressed) | 16 |
| RP6 | 18-file byte-freeze extended map | 16 |
| HD1 | the silent-pass prefix filter `tests/model_state/test_demo_join.py:162-164` → explicit `NINE_IDS` + revision-id assert | 16 |
| I1c | `assembly_definition_contains` appears exactly once in `models/demo-printer/records/**` | 16 |
| D6-1 | replayed pre-SN-001 `contains` projection vs current: semantic nodes/edges/conflicts/lineage equal (embedded revision excluded) | 16 |
| D6-2 | `assembly_definition_contains` projection non-empty and anchor-disjoint from `contains` | 16 |
| D6-3 | type anchor has empty `contains` parents (assert EMPTY, no disjunction) | 16 |
| D6-4/5 | endpoint-kind rejection in both directions (`MODEL_ENDPOINT_KIND_INVALID`) | 16 |
| D6-6 | wording sweep: never "the hierarchy" | 16 |
| SV1 | semantic refinement of the two accepted vocabulary sweeps (registrations/specifications clean; `rel_S7`'s citation enumerated; no query treats it as discovery) | 16 |
| DM1 | the one coherent demonstration chain, every arrow's disclosure kind asserted | 17 |
| DM2 | negative corpus beside the showcase; Moonraker leg byte-identical to VS-001's result | 17 |
| A5d… | (J4 covers the join sentence at 13) | — |
| A5i | full 16-limitation README verbatim | 18 |

## SN-001a — CSV structural claims. No model-truth contact.

No store construction, no ledger read/write, no anchor minting, no
resolvers, no STEP derivation, no reconciliation. The curated
`model_kernel` **type** surface (e.g. `LifecycleView`) is imported and I3
pins that allow-list exactly.

Gate to prove: **a CSV structural claim is source-native evidence, not a
canonical identity or model claim, and this module has no mechanism capable
of making it one.**

1. `docs: SN-001 specification, ADR-0010, plan, and status alignment`
   — this spec/ADR/plan; `CLAUDE.md` status; `models/README.md` corrected
   to the current 11 (the 14-count lands at commit 16); root `README.md`
   overview. Behaviour-free.
2. `feat: structural evidence errors and payload-pinned locators`
   — `errors.py`, `locators.py` (all four locator kinds as contracts,
   `canonical_locator_value` with K7 scheme grammars, K3 `min_length=1`,
   `max_length=1024` + `SN_LOCATOR_TOO_LONG`). Tests: L1, L2, L3.
3. `feat: claim, field, and engineering-context contracts`
   — `contracts.py`: `StructuralClaimKind`, `SourceNativeField`,
   `SourceStructuralClaim`, `SourceContainmentClaim`, `DerivedUsagePath`,
   `QuantityFieldRef`, `UnresolvedParentReference`, `EngineeringContext`
   (three arms, no default), `SourceStructuralClaimSet`. Tests: C0.
4. `feat: subject identity rules, fingerprints, and the sx1 namespace`
   — `rules.py`: bodies, `SubjectIdentityRule`, `rule_fingerprint`,
   `apply_rule` (CSV bodies; the claim contracts it consumes exist since
   commit 3), 8-component namespace builder/parser,
   `to_source_subject_ref`. Tests: R1–R12.
5. `feat: CSV source-native claims`
   — `claims.py`: CSV derivation from a persisted `ExtractionResult`,
   including the `bom_parent_column` within-source lookup. Tests: CL1–CL8.
6. `test: SN-001a isolation gate and published wording`
   — I1a, I2, I3, I4, I5, I6, A5b, A5c, A5h, A5i-a, SW1; the SN-001a
   README (limitations 1, 6, 7, 10, 12, 14, 15, 16). Every sweep carries a
   corpus-size guard and is demonstrated red once by a deliberate mutation
   in a scratch copy (recorded in the commit message).

## SN-001b — frozen showcase first, then STEP claims.

7. `feat: showcase generator and committed frozen sources`
   — `showcases/demo-printer/{README.md,SOURCES.md,sources/*,
   MANIFEST.json,tools/generate.py}` (generator `cad`-marked, run once,
   frozen, never imported by a test).
8. `feat: frozen showcase extraction artifacts + fixture-integrity gate`
   — `extractions/<raw_record_id>.json` for BOM and STEP; manifest
   completed (checksums, extractor identity, config + toolchain
   fingerprints, pinned ids, regeneration command, honesty sentence).
   Tests: FX1–FX5, FX7, FX8 (base-only), A5a; I4's sweep corpus extended
   over `showcases/`. **This is the gate: all green base-only before any
   STEP-dependent test exists.**
9. `feat: STEP structural claims and derived usage paths`
   — `claims.py` STEP derivation; `apply_rule` for `StepPathRuleBody`.
   Tests: SC1–SC5, M2a, FX6 (`cad`), A11; SW1 extended over the showcase.

## SN-001c — kernel arm, reconciliation, proposals, ledger appends, demonstration.

10. `chore: red baseline evidence for the ledger appends`
    — author the seven append records (content-derived ids computed via
    the accepted builders) ahead of commits 15–16; apply them in place in
    a **full copy of the worktree**; run `pytest` from that copy's root;
    commit the observed failure list into `docs/superpowers/plans/` as
    evidence. Expected at this stage: **11 named failures**
    (`test_demo_binding_set.py:77/:88/:122` ·
    `test_cross_layer_seam.py:38` · `test_demo_model.py:31-37/:43/:236-237` ·
    `model_kernel/test_isolation.py:150/:156` ·
    `model_state/test_isolation.py:101` ·
    `observation_compatibility/test_demo_compatibility.py:151` ·
    `observation_compatibility/test_isolation.py:130`), with
    `tests/model_state/test_demo_join.py:162-164` and
    `test_demo_compatibility.py:122` **passing silently** while selecting
    12 and 13 records — the honesty defect RP2/HD1 kill. The 12th failure
    (`test_variable_registration.py:478`, `__all__` 53→54) fires at
    commit 11 and is recorded as that commit's expectation. No production
    change in this commit.
11. `feat: kernel structural evidence arm (D3)`
    — `StructuralSourceLocatorEvidence` + union member + `__all__`.
    Tests: KR1–KR4, X5; `test_variable_registration.py` renamed count
    test updated 53 → 54.
12. `feat: StructuralAddress <-> kernel evidence conversion`
    — Tests: X1, X1b, X2, X3, X4, X6.
13. `feat: resolved subjects, join index, comparators, findings, result,
    digest, multi-resolver reconciler`
    — `reconcile.py` in full (constructor takes `rules:`). All
    reconciliation tests author their binding sets in `tmp_path`; **only
    A12′ uses the committed resolvers**. Tests: M1, M2, M4, M7, M8,
    M15–M18, M20, M21, M23, M24, M29, CS1–CS9, J1–J5, CP1–CP6, S1–S6,
    A1–A4, A5f, A5g, A7, A12′.
14. `feat: inert proposals`
    — `proposals.py`. Tests: P1–P8.
15. `feat: structural binding assertions appended to the committed sets`
    — `iba_S1` + `iba_S2` → `bindings/demo-printer/` (4→6); `anc_S3` +
    `iba_S4` → `bindings/demo-printer-model/` (3→5). Same commit migrates:
    `test_demo_binding_set.py:77/:122` 4→6; `:85-90` → AU1;
    `model_kernel/test_isolation.py:156` 3→5 with prefix set
    `("anc","iba")`. Tests: AU1 (replacing the blanket agent assert at
    `test_demo_binding_set.py:85-88`), RP4, RP5, CS1′.
16. `feat: assembly_definition_contains type, registration, and assertion`
    — `rtd_S5`, `reg_S6`, `rel_S7` → `models/demo-printer/` (11→14);
    `rel_S7` = `anc_S3` → `ent_2b3c4d5e…` (the extruder-unit type — the
    only committed pair that type-checks), citing the new arm + both
    `iba_` records + `SourceRawRecordEvidence`. Same commit migrates: `test_demo_model.py`
    (GOLDEN_REVISION → `replay(ELEVEN_IDS)` via RP1, new
    `CURRENT_REVISION` under `load()`, counts 14/4/5/3/1/1, `:43` → AU2,
    `:232` → RP2); X4's anti-vacuity anchor (`rel_S7` carries the arm;
    `reg_S6` and the `vsp_` record stay clean);
    `model_kernel/test_isolation.py:150` 11→14;
    `test_cross_layer_seam.py:38` 4→5; `model_state/test_isolation.py:101`
    and `oc/test_isolation.py:130` 11→14 (and the stale "must see all 10"
    docstring fixed); `test_demo_compatibility.py:122` → RP2, `:151`
    11→14; `test_demo_join.py:162-164` → HD1; `models/README.md` and
    `bindings/README.md` counts finalized. Tests: AU2, RP1, RP2, RP3, RP6,
    HD1, I1c, D6-1…D6-6, SV1.
17. `test: SN-001 completion demonstration` — DM1, DM2.
18. `docs: structural_evidence README (full 16 limitations), showcase
    provenance` — A5i.

Post-implementation: adversarial review of the whole commit series (owner
workflow step 10), then architect validation (step 11), then stop for owner
validation. Push nothing.

## Must not change

`backend/data_sources/**`, `backend/temporal_state/**`,
`backend/system_identity/**`, `backend/identity_binding/**` (code),
`backend/model_state/**`, `backend/observation_compatibility/**`; every
existing committed record byte; the accepted fixtures; `var/` stays
untracked. The only accepted-module source edits are the two D3 files
(`model_kernel/contracts.py`, `model_kernel/__init__.py`).

## Verification commands

```
.venv/bin/python -m pytest                       # full, both columns
.venv/bin/python -m pytest tests/structural_evidence
.venv/bin/python -m pytest tests/model_kernel tests/identity_binding
# clean checkouts: fresh clone of branch sn001, fresh venv
#   base-only : requirements.txt + requirements-dev.txt
#   all-extras: + requirements-cad.txt + requirements-pdf.txt
```
