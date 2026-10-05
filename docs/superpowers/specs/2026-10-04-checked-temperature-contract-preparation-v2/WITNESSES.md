# Witness matrix v2 (hand-derived expected outcomes; not executed)

Source of truth: `witnesses.json`. Hierarchy: **witness** (contract property) → **case** (one positive or adverse input) → **invocations** (CLI commands). Process launches are counted in `PLAN.md`, not here.

Common inputs: FX1 = selection of the common baseline (plan w=1/2, every required claim declared true and supported by one completed applicable review); baseline 60.1; H1 [0,0]; H2 [5,15]; b_ref [0,0]; T1 decoder low(-inf,56] gap(56,59] high(59,inf); T2 target 60.

Totals: 17 witnesses, 82 cases (31 positive, 51 adverse), 154 application invocations: checked-reassessment-evaluate 16, checked-reassessment-replay 8, checked-reassessment-verify 8, checked-selection-evaluate 62, checked-selection-replay 29, checked-selection-verify 31. IN2, IN3/IN4 (one shared mutated copy), IN5: 3 bundle copies mutated by the harness; not application invocations.

| Witness | Case | Pol. | Inputs | Expected | Invocations | Prior | Was |
|---|---|---|---|---|---|---|---|
| W01 | FX1 | p | FX1 = selection of the common baseline (plan w=1/2, every required claim declared true and supported by one completed applicable review) | ranked; produces the shared prior selection bundle | SE |  |  |
| W02 | SC1 | p | FX1 inputs | ranked; T1 branches low{H2} gap{} high{H1} worst 1; T2 heater_off{H1,H2} heater_on{} worst 2; best [T1]; score_domain ideal_measurand_decoder_branches; post_measurement_elimination_guaranteed false; observation_uncertainty_not_in_score [T1 plan w=1/2, plan_state captured] | SV SR | FX1 | A1 |
| W03 | UN1 | p | reassessment of FX1, inherited plan, T1 scalar 60.0 | interval [59.5,60.5]; branches high; H1 compatible_under_declared_model; H2 conditionally_incompatible; one_compatible; ranking not_reassessed; adoption derived_not_adopted; no adoption record produced | RE RV RR | FX1 | A2 |
| W03 | UN3 | p | reassessment of FX1, scalar 55.6 | [55.1,56.1] low+gap; H1 incompatible; H2 unresolved (mixed_permit_exclude); incomplete_assessment | RE RV RR | FX1 | A4 |
| W03 | UN4 | p | reassessment of FX1, scalar 55.5 | [55,56] low only (gap open at 56); H2 compatible; H1 incompatible; one_compatible | RE RV RR | FX1 | A4b |
| W04 | LB1 | p | FX1 with H2 b_suspect [3,15] | H2 T1 set [45.1,57.1] permits low and gap; T1 branches low{H2} gap{H2} high{H1}; worst 1; ranked | SE SV SR |  | A5 |
| W05 | PM1 | a | FX1 with T1 interpretation_plan null | withheld (observation_interpretation_plan_missing); scores []; best null; derivation cells retained; no default plan | SE SV SR |  | B1 |
| W06 | PS1 | a | reassessment of FX1, selection_basis inherited, plan_change null, result interpretation_plan = w=5/2 | refuse INTERPRETATION_PLAN_MISMATCH exit 3 before interpretation | RE | FX1 | B2 |
| W07 | PS2 | p | selection_basis historical_reference_with_plan_change; plan_change {former w=1/2 (FX1 captured plan), new w=5/2, reason}; result plan w=5/2; evaluation authority plan_change {former, new} digests equal; fresh observation_error_bound claim for w=5/2 declared and supported; scalar 57.6 | completes: plan_changed true; original_plan_executed false; former_plan w=1/2; executed_plan w=5/2; prior_selection FX1 (historical); [55.1,60.1] low+gap+high; H1 and H2 unresolved; incomplete_assessment; ranking not_reassessed; no rerank; adoption derived_not_adopted | RE RV RR | FX1 | A3, B2b |
| W07 | PS3 | a | PS2 but authority.plan_change null | refuse AUTHORITY_SCOPE_MISMATCH | RE | FX1 |  |
| W07 | PS4 | a | PS2 but plan_change.new_plan equals former_plan | refuse PLAN_CHANGE_INVALID | RE | FX1 |  |
| W07 | PS5 | a | PS2 but result interpretation_plan differs from plan_change.new_plan | refuse PLAN_CHANGE_INVALID | RE | FX1 |  |
| W07 | PB1 | a | PS2 but the only observation_error_bound review is the old one bound to w=1/2 | old review listed in applicability.unbound; new plan claim none/complete/unresolved; blocked (unresolved_not_permitted); disposition applicability_blocked; hypotheses not_assessed | RE RV RR | FX1 |  |
| W08 | HW0 | a | plan w=0 | refuse INTERPRETATION_POINT_UNSUPPORTED | SE |  | B3 |
| W08 | HW5 | p | plan w=5 | admitted; ranked as SC1 | SE SV SR |  | F7 |
| W08 | HW5p | a | plan w=5.000001 | refuse INTERPRETATION_HALF_WIDTH_OUT_OF_RANGE | SE |  | F7 |
| W09 | OB2 | a | reassessment of FX1, scalar 60.0; completed applicable review opposing the observation_error_bound claim (w=1/2) | governing_state contradicted; applicability_blocked; hypotheses not_assessed; interval not applied | RE RV RR | FX1 |  |
| W09 | OB3 | a | as OB2 but only an unreviewed bound attachment; allowlist omits observation_error_bound | unresolved; blocked (unresolved_not_permitted) | RE RV RR | FX1 |  |
| W09 | OB4 | p | model b_ref [-1/2,1/2], plan w=1/2, all claims supported; then reassessment scalar 60.0 | derivation: H1 T1 [59.6,60.6], H2 [44.6,55.6] (b_ref applied once, w absent); selection ranked worst 1; reassessment interval [59.5,60.5] (w applied once, b_ref absent); H1 compatible; H2 incompatible | SE SV SR RE RV RR |  |  |
| W10 | CB1 | a | model revision 2 changes b_ref [0,0]->[-1/2,1/2]; old calibration declaration and review bound to the revision-1 claim are retained; no new declaration | old declaration/review in applicability.unbound; new calibration claim declaration_missing; selection withheld (applicability_blocked) | SE SV SR |  |  |
| W10 | CB2 | a | CB1 plus a new declaration true for the revision-2 claim; still only the old review | new claim none/complete/unresolved; blocked (unresolved_not_permitted); the old review does not support the changed claim | SE SV SR |  |  |
| W10 | CB3 | p | CB2 plus a completed applicable supporting review of the revision-2 claim | supported; ranked; old review remains listed unbound | SE SV SR |  |  |
| W11 | AG1 | p | one applicable completed supporting review | support_only/complete/supported; permitted | SE SV SR |  | C1 |
| W11 | AG2 | a | AG1 + unreviewed bound attachment | support_only/pending/unresolved; blocked | SE SV SR |  | C2 |
| W11 | AG3 | p | AG2 + synthetic allowlist permitting reference_calibration/selection | support_only/pending/unresolved; conditional_use_with_unresolved_conditions; assumed and pending listed | SE SV SR |  | C3 |
| W11 | AG4 | a | opposition + unreviewed attachment | opposition_only/pending/contradicted; blocked regardless of allowlist | SE SV SR |  | C4 |
| W11 | AG5 | a | support + opposition + unreviewed attachment | support_and_opposition/pending/conflicting; blocked regardless of allowlist | SE SV SR |  | C5 |
| W11 | AG6 | a | support on A; B completed irrelevant + completed unresolved-relevance | support_only/pending/unresolved; blocked; B pending_reasons irrelevant_with_unresolved | SE SV SR |  | C6 |
| W11 | AG7 | a | same item relevant support + irrelevant | support_only/pending/unresolved; disputed_relevance; blocked | SE SV SR |  | C7 |
| W11 | AG8 | a | same item relevant opposition + irrelevant | opposition_only/pending/contradicted; blocked | SE SV SR |  | C8 |
| W11 | AG9 | p | support on A; B only unopposed completed irrelevant | support_only/complete/supported; B excluded_reviewed | SE SV SR |  | C9 |
| W11 | AG10 | p | support on A; B validity entirely outside time scope | support_only/complete/supported; B excluded_conclusive validity_non_overlapping | SE SV SR |  | C10 |
| W11 | AG11 | a | AG10 but B validity partially overlaps | support_only/pending/unresolved; partial_or_unknown_scope; blocked | SE SV SR |  | C11 |
| W11 | AG12 | a | only expired support, conclusively non-overlapping | none/complete/unresolved; blocked | SE SV SR |  | C12 |
| W11 | AG13 | a | sole completed unresolved relation | none/pending/unresolved; blocked | SE SV SR |  | C13 |
| W11 | AG14 | a | same item support + opposition + irrelevant | support_and_opposition/pending/conflicting; blocked | SE SV SR |  | C14 |
| W12 | DC1 | a | calibration claim declared true and false | conflicting_declarations; blocked; both retained | SE SV SR |  | E1 |
| W12 | DC2 | a | state_hold claim undeclared | declaration_missing; blocked | SE SV SR |  | E2 |
| W12 | DC3 | a | calibration declared true + completed applicable opposing review | contradicted; blocked | SE SV SR |  | E3 |
| W13 | PO1 | a | request.policy referenced but absent from closure | refuse REFERENCE_MISSING; no default policy applied | SE |  |  |
| W13 | PO2 | p | captured policy with explicit empty allowlist; AG2 graph | completes; blocked (unresolved_not_permitted); empty allowlist honoured as a recorded choice | SE SV SR |  |  |
| W13 | PO3 | a | captured policy permitted_builds [] | refuse SCHEMA_INVALID | SE |  |  |
| W13 | PO4 | a | captured policy loosens a limit above the edition value | refuse POLICY_LIMIT_INVALID | SE |  |  |
| W13 | PO5 | a | captured policy edition ct.policy-edition.v1 | refuse POLICY_EDITION_MISMATCH | SE |  |  |
| W14 | IN1 | a | evaluate with submitted cached derivation, H2 set altered to [45.1,56.1], rehashed | refuse CACHED_DERIVATION_MISMATCH | SE |  | D1 |
| W14 | IN2 | a | copy of FX1 bundle with altered derivation.json, all digests rehashed | verify refuses DERIVATION_MISMATCH | SV | FX1 | D2 |
| W14 | IN3 | p | copy of FX1 bundle with altered T1 worst_survivors 2 in result.json, rehashed | verify completes reporting derivation_checked, applicability_policy_checked, downstream_result_not_replayed | SV | FX1 | D3 |
| W14 | IN4 | a | same mutated copy as IN3 | replay refuses DOWNSTREAM_REPLAY_MISMATCH | SR | FX1 | D4 |
| W14 | IN5 | a | copy of FX1 with post_measurement_elimination_guaranteed true, rehashed | verify refuses SCORE_METADATA_INVALID | SV | FX1 | D5 |
| W14 | IN6 | a | request references model revision 1 digest; closure supplies revision 2 only | refuse REFERENCE_MISSING | SE |  | D6 |
| W14 | IN7 | a | authority changed and rehashed; external expected authority pin unchanged | refuse AUTHORITY_PIN_MISMATCH before computation | SE |  | D7 |
| W14 | IN8 | p | fresh request + fresh authority with matching fresh external pins | completes as a new declared assessment; unauthenticated | SE SV SR |  | D7b |
| W14 | IN9 | a | evaluation authority scope phase selection used for reassessment | refuse AUTHORITY_SCOPE_MISMATCH | RE | FX1 | D8 |
| W14 | IN10 | a | reassessment prior_selection.manifest_sha256 differs from the supplied prior bundle manifest | refuse PRIOR_BUNDLE_MISMATCH | RE | FX1 |  |
| W14 | IN11 | a | closure carries an unreferenced extra member | refuse UNREFERENCED_MEMBER | SE |  |  |
| W15 | BE1 | a | baseline evidence scalar 60.2, model baseline 60.1 | both baseline_ineligible, retained; withheld (baseline_ineligible); not pruned | SE SV SR |  | G1 |
| W16 | F1a | p | 2 hypotheses | admitted (evaluate completes; content checked as in SC1) | SE |  | F1 |
| W16 | F1b | a | 3 hypotheses | refuse SCHEMA_INVALID | SE |  | F1 |
| W16 | F2a | p | T1 and T2 once each | admitted (evaluate completes; content checked as in SC1) | SE |  | F2 |
| W16 | F2b | a | T1 twice | refuse SCHEMA_INVALID | SE |  | F2 |
| W16 | F3a | p | decoder content equal to edition | admitted (evaluate completes; content checked as in SC1) | SE |  | F3 |
| W16 | F3b | a | 4 regions or cut 56.5 under same edition | refuse EDITION_CONTENT_MISMATCH | SE |  | F3 |
| W16 | F4a | p | scalar 1000 | admitted (evaluate completes; content checked as in SC1) | RE | FX1 | F4 |
| W16 | F4b | a | scalar 1000.000001 | refuse SCALAR_OUT_OF_ADMISSION_DOMAIN | RE | FX1 | F4 |
| W16 | F5a | p | 6 fractional digits | admitted (evaluate completes; content checked as in SC1) | SE |  | F5 |
| W16 | F5b | a | 7 fractional digits | refuse RATIONAL_INVALID | SE |  | F5 |
| W16 | F6a | p | 32-digit numerator (in bounds after reduction checks) | admitted (evaluate completes; content checked as in SC1) | SE |  | F6 |
| W16 | F6b | a | 33-digit numerator | refuse RESOURCE_LIMIT_EXCEEDED | SE |  | F6 |
| W16 | F8a | p | H2 hi 50 | admitted (evaluate completes; content checked as in SC1) | SE |  | F8 |
| W16 | F8b | a | H2 hi 50.000001 or lo 0 | refuse ACCOUNT_KIND_CONSTRAINT_VIOLATED | SE |  | F8 |
| W16 | F9a | p | b_ref hi 10 | admitted (evaluate completes; content checked as in SC1) | SE |  | F9 |
| W16 | F9b | a | b_ref hi 10.000001 | refuse ACCOUNT_KIND_CONSTRAINT_VIOLATED | SE |  | F9 |
| W16 | F10a | p | 8 evidence items on one claim | admitted (evaluate completes; content checked as in SC1) | SE |  | F10 |
| W16 | F10b | a | 9 | refuse RESOURCE_LIMIT_EXCEEDED | SE |  | F10 |
| W16 | F11a | p | 4 reviews on one item | admitted (evaluate completes; content checked as in SC1) | SE |  | F11 |
| W16 | F11b | a | 5 | refuse RESOURCE_LIMIT_EXCEEDED | SE |  | F11 |
| W16 | F12a | p | 64 reviews | admitted (evaluate completes; content checked as in SC1) | SE |  | F12 |
| W16 | F12b | a | 65 | refuse RESOURCE_LIMIT_EXCEEDED | SE |  | F12 |
| W16 | F13a | p | decoded selection closure 1,048,576 B | admitted (evaluate completes; content checked as in SC1) | SE |  | F13 |
| W16 | F13b | a | 1,048,577 B | refuse RESOURCE_LIMIT_EXCEEDED | SE |  | F13 |
| W17 | T2a | p | target 60.1 equal to baseline | heater_off for both; T2 worst 2 | SE |  | T2a |
| W17 | T2b | p | target 60.2 | heater_on for both; T2 worst 2; best [T1] | SE |  | T2b |

Abbreviations: SE/SV/SR = checked-selection evaluate/verify/replay; RE/RV/RR = checked-reassessment evaluate/verify/replay. 'Was' maps to predecessor-package witness IDs.

END OF WITNESS MATRIX V2
