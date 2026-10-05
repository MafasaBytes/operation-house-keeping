# Witness matrix (hand-derived expected outcomes; not executed)

Source of truth: `witnesses.json`. Each row is an expected contract outcome to be
frozen before execution; none is passing evidence. Common baseline: baseline 60.1; H1 b_suspect [0,0]; H2 [5,15]; b_ref [0,0]; T1 decoder low(-inf,56] gap(56,59] high(59,inf); T2 target 60.

| ID | Group | Inputs | Expected | Twin |
|---|---|---|---|---|
| A1 | score_vs_uncertainty | baseline 60.1; H1 b_suspect [0,0]; H2 [5,15]; b_ref [0,0]; T1 decoder low(-inf,56] gap(56,59] high(59,inf); T2 target 60; plan T1 w=1/2; all conditions declared true and supported | selection ranked: T1 ideal sets H1 {60.1}->high, H2 [45.1,55.1]->low; T1 survivor sets {H2},{},{H1} score 1; T2 heater_off {H1,H2}, heater_on {} score 2; best [T1]; score_domain ideal_measurand_decoder_branches; post_measurement_elimination_guaranteed false; observation_uncertainty_not_in_score lists w=1/2 |  |
| A2 | score_vs_uncertainty | A1 selection; T1 result 60.0, plan w=1/2 | interval [59.5,60.5] reaches high only; H1 compatible_under_declared_model; H2 conditionally_incompatible; disposition one_compatible; adoption derived_not_adopted | A3 |
| A3 | score_vs_uncertainty | A1 inputs but plan w=5/2 (successor request); result 57.6 | selection unchanged ideal score 1 (plan not scored); interval [55.1,60.1] reaches low,gap,high; H1 unresolved (mixed), H2 unresolved (mixed); disposition incomplete_assessment; no hypothesis described as eliminated | A2 |
| A4 | score_vs_uncertainty | A1; result 55.6, w=1/2 | interval [55.1,56.1] reaches low,gap; H1 conditionally_incompatible; H2 unresolved; disposition incomplete_assessment | A4b |
| A4b | score_vs_uncertainty | A1; result 55.5, w=1/2 | interval [55,56] reaches low only (gap open at 56); H2 compatible; H1 incompatible; one_compatible | A4 |
| A5 | score_vs_uncertainty | A1 but H2 b_suspect [3,15] | H2 T1 set [45.1,57.1] permits low and gap; T1 survivor sets {H2},{H2},{H1} score 1; ranking unchanged |  |
| B1 | interpretation_plan | A1 but T1 interpretation_plan null | selection withheld for the whole nominated set: observation_interpretation_plan_missing; derivation cells remain inspectable; no default plan supplied | A1 |
| B2 | interpretation_plan | A1 selection (w=1/2); reassessment request result references plan w=5/2 without successor | refuse INTERPRETATION_PLAN_MISMATCH exit 3; no compatibility computed | B2b |
| B2b | interpretation_plan | immutable successor request with plan w=5/2 and newly scoped authority/pin, prior selection referenced historically | accepted as a new declared assessment; reports plan_changed with former selection reference; does not claim execution of the original plan; no automatic rerank or adoption | B2 |
| B3 | interpretation_plan | plan w=0 | refuse INTERPRETATION_POINT_UNSUPPORTED |  |
| C1 | aggregation | one applicable completed supporting review | axes support_only / complete / supported; use permitted subject to other gates |  |
| C2 | aggregation | C1 + unreviewed bound attachment | axes support_only / pending / unresolved; blocked: unresolved_not_permitted (selection withheld whole set) |  |
| C3 | aggregation | C2 with synthetic allowlist permitting reference_calibration/selection | axes support_only / pending / unresolved; conditional_use_with_unresolved_conditions listing pending attachment |  |
| C4 | aggregation | opposition + unreviewed attachment | axes opposition_only / pending / contradicted; blocked regardless of allowlist |  |
| C5 | aggregation | support + opposition + unreviewed attachment | axes support_and_opposition / pending / conflicting; blocked regardless of allowlist |  |
| C6 | aggregation | support on A; B has completed irrelevant + completed unresolved-relevance reviews | axes support_only / pending / unresolved; blocked; irrelevant cannot suppress unresolved |  |
| C7 | aggregation | same item: completed relevant support + completed irrelevant | axes support_only / pending / unresolved; blocked; support retained in relation axis |  |
| C8 | aggregation | same item: completed relevant opposition + completed irrelevant | axes opposition_only / pending / contradicted; blocked |  |
| C9 | aggregation | support on A; B only unopposed completed irrelevant review | axes support_only / complete / supported; use permitted; B retained with exclusion reason |  |
| C10 | aggregation | support on A; B validity interval entirely outside assessment window (conclusive), unresolved review retained | axes support_only / complete / supported; use permitted; B conclusive-exclusion basis explicit |  |
| C11 | aggregation | C10 but B validity interval partially overlaps the window | axes support_only / pending / unresolved; blocked; partial overlap is not exclusion |  |
| C12 | aggregation | only expired support (conclusively non-overlapping) | axes none / complete / unresolved; blocked; historical support readable |  |
| C13 | aggregation | sole completed unresolved relation on applicable item | axes none / pending / unresolved; blocked; no support invented |  |
| C14 | aggregation | same item: support + opposition + irrelevant review | axes support_and_opposition / pending / conflicting; blocked |  |
| E1 | declarations | reference_calibration selection declared true and false (two declarations) | conflicting_declarations; blocked; both retained |  |
| E2 | declarations | state_hold selection declaration absent | declaration_missing; blocked |  |
| E3 | declarations | calibration declared true + completed applicable opposition review | governing_state contradicted; blocked; declaration cannot erase opposition |  |
| D1 | integrity | evaluate with submitted cached derivation whose H2 set altered to [45.1,56.1], correctly rehashed | refuse CACHED_DERIVATION_MISMATCH exit 3 |  |
| D2 | integrity | retained bundle with altered derivation, all digests and manifest rehashed | verify refuses DERIVATION_MISMATCH (fresh recomputation) |  |
| D3 | integrity | retained bundle with altered downstream score (T1 worst 2), rehashed | verify completes reporting downstream_result_not_replayed (does not claim ranking checked) | D4 |
| D4 | integrity | same bundle as D3 | replay refuses DOWNSTREAM_REPLAY_MISMATCH | D3 |
| D5 | integrity | retained selection with post_measurement_elimination_guaranteed true, rehashed | verify refuses SCORE_METADATA_INVALID |  |
| D6 | integrity | request references model revision 1 digest; closure supplies revision 2 | refuse REFERENCE_DIGEST_MISMATCH |  |
| D7 | integrity | authority record changed and rehashed; external --expected-authority-pin unchanged | refuse AUTHORITY_PIN_MISMATCH before computation | D7b |
| D7b | integrity | fresh request and fresh authority with matching fresh external pins | accepted as a new declared assessment; not authenticated; prior history untouched | D7 |
| D8 | integrity | authority scope phase selection used for reassessment | refuse AUTHORITY_SCOPE_MISMATCH |  |
| G1 | baseline | baseline evidence scalar 60.2 while model baseline 60.1 | both hypotheses baseline_ineligible; retained; selection withheld whole set (baseline_ineligible); not pruned |  |
| F1 | boundary | 2 hypotheses (one per kind) / plus-one: 3 hypotheses | boundary: admitted; plus-one: refuse RESOURCE_LIMIT_EXCEEDED/ hypotheses |  |
| F2 | boundary | T1 and T2 once each / plus-one: T1 twice | boundary: admitted; plus-one: refuse SCHEMA_INVALID (edition at most once) |  |
| F3 | boundary | decoder content equal to ct.decoder.T1.v1 / plus-one: 4 regions or cut point 56.5 under same edition | boundary: admitted; plus-one: refuse EDITION_CONTENT_MISMATCH |  |
| F4 | boundary | scalar 1000 / plus-one: 1000.000001 | boundary: admitted; plus-one: refuse SCALAR_OUT_OF_ADMISSION_DOMAIN |  |
| F5 | boundary | 6 fractional digits / plus-one: 7 fractional digits | boundary: admitted; plus-one: refuse RATIONAL_INVALID |  |
| F6 | boundary | 32-digit numerator / plus-one: 33-digit numerator | boundary: admitted (then bounds checked); plus-one: refuse RESOURCE_LIMIT_EXCEEDED/ integer_digits |  |
| F7 | boundary | w=5 / plus-one: w=5.000001 | boundary: admitted; plus-one: refuse INTERPRETATION_HALF_WIDTH_OUT_OF_RANGE |  |
| F8 | boundary | H2 b_suspect hi 50 / plus-one: hi 50.000001 or lo 0 | boundary: admitted; plus-one: refuse ACCOUNT_KIND_CONSTRAINT_VIOLATED |  |
| F9 | boundary | b_ref [-10,10] / plus-one: b_ref hi 10.000001 | boundary: admitted; plus-one: refuse ACCOUNT_KIND_CONSTRAINT_VIOLATED |  |
| F10 | boundary | 8 evidence items on one condition key / plus-one: 9 | boundary: admitted; plus-one: refuse RESOURCE_LIMIT_EXCEEDED/ evidence_items_per_condition_key |  |
| F11 | boundary | 4 reviews on one item / plus-one: 5 | boundary: admitted; plus-one: refuse RESOURCE_LIMIT_EXCEEDED/ reviews_per_item |  |
| F12 | boundary | 64 reviews total / plus-one: 65 | boundary: admitted; plus-one: refuse RESOURCE_LIMIT_EXCEEDED/ reviews |  |
| F13 | boundary | decoded closure 1,048,576 B / plus-one: 1,048,577 B | boundary: admitted; plus-one: refuse RESOURCE_LIMIT_EXCEEDED/ closure_bytes before aggregation |  |
| T2a | t2_rule | target 60.1 equal to baseline 60.1 | heater_off for both (equality off); T2 survivor sets {H1,H2},{} score 2 |  |
| T2b | t2_rule | target 60.2 | heater_on for both; survivor sets {},{H1,H2}; score 2; T2 never preferred over T1 in A1 |  |

Groups: score_vs_uncertainty (ideal discrimination vs uncertainty-driven unresolved),
interpretation_plan (missing/changed plans), aggregation (design §5 twins), declarations,
integrity (rehashed alterations, stale references, authority substitution), baseline,
boundary (boundary-sized inputs and plus-one refusals), t2_rule.

END OF WITNESS MATRIX
