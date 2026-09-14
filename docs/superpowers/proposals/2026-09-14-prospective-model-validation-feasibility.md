# Prospective model-validation feasibility

## 1. Decision and verified baseline

**Outcome: equipment/data confirmation required.** No inspected record establishes
available physical equipment or a suitable independent empirical dataset. Passive
cooling is a provisional candidate, not an acquisition recommendation. Request
metadata confirmation first; preparation and acquisition require separate authority.
This investigation accessed repository files only, not services, devices or credentials.

Verified on 2026-09-14: branch `brc-exp001`, HEAD
`09f0db2f7ea472cd850ff5226c7fa196eb13a330`, matching the checkpoint.

| Accepted authority | SHA-256 |
| --- | --- |
| [Owner acceptance](../reports/2026-09-14-model-derived-prediction-owner-acceptance.md) | `1e6d1501e931382c255c43c911174f8e61dbfd6d1cc35ee95e7eec577f482717` |
| [Execution report](../reports/2026-09-14-model-derived-prediction-final-execution-report.md) | `14f7149e89d9242459c6f1cc379c0ea7de6346dec220aa03328f6f6f86767d81` |
| [Current design, including acceptance addendum](../specs/2026-09-14-model-derived-prediction-bounded-experiment-design.md) | `23905c499923b138d9e6d2b2baf528d86dfc0c35952d538a3334f565ef81d5ea` |

The original approved design is preserved inside the execution archive at
`frozen/design.md`, digest
`1f057cece2dcea583a464889161875e951764c68d54f2fc93cf02cbd82b6ff65`.
Its §7.2 custody requirements govern this proposal; its synthetic offset equations
and held-scalar procedure do not. Acceptance covers 76 synthetic cases, 18 resource
probes, independent mathematical checking and reproducibility, not physical accuracy,
causal truth or production promotion. Same-author oracle provenance remains disclosed.

## 2. Availability and evidence inventory

Inspection covered source contracts/catalog/adapters, acquisition documentation,
fixtures/showcase/model provenance, relevant accepted records and the BOM notebook.
Absence below means not established within this scope, not proof that an owner has
no equipment. No unrelated personal files were searched.

| Candidate resource/source | Classification and provenance | Empirical limitation |
| --- | --- | --- |
| CSV ingestion, immutable raw-file storage and fixed read-only Moonraker producer | **Documented available: software only.** [Source documentation](../../../backend/data_sources/README.md) and [catalog profile](../../../backend/data_sources/catalog/profile_v2.py) describe capabilities. | A configured/validated connector does not establish current physical-device access or acquisition authority. |
| `printer-1` / `voron-1`, loopback API configuration | **Synthetic or unsuitable.** [Runner test](../../../tests/data_sources/test_ingestion_runner_api.py) uses scripted transport and a fake clock, not a deployed source inventory. | No possession, current endpoint, physical instrument or operator is established. |
| Demo printer, BOM/CAD/PDF and temperature payloads | **Synthetic or unsuitable; known prior exposure.** [Showcase sources](../../../showcases/demo-printer/SOURCES.md), [model provenance](../../../models/demo-printer/README.md) and [fixture provenance](../../../backend/data_sources/testing/fixtures/FIXTURES.md) explicitly disclaim physical evidence. | Hand-authored 60.1/60.4 temperature values informed exposed synthetic cases; they are not calibration/fitting observations or an empirical holdout. A declared `measured_actual` role does not change their origin. |
| DS-004 historical Moonraker captures | **Existing data with known prior exposure; unsuitable for physical validation.** [Design validation record](../specs/2026-08-07-ds004-operational-api-design.md), “Virtual-Moonraker validation evidence,” records real Moonraker software on virtual Klipper, loopback only, no device passthrough; teardown followed validation. | Software-integration provenance is documented, but no physical thermometer, operating environment, calibration or independent physical measurement is established. This is not currently accessible equipment. |
| BOM notebook | **Synthetic or unsuitable.** [Notebook](../../../notebooks/bill_of_material_data_source.ipynb) has an empty, unexecuted code cell and no outputs. | No acquired dataset. |
| Real printer, passive-cooling specimen/logger, or RC apparatus; owner-held raw exports | **Availability requires owner confirmation.** These are candidate requirements, not documented possessions. | Instrument identity, calibration, sample times, conditions, retention and prior fitting/exposure are unknown. |
| Independently collected physical data with documented provenance | **None identified.** | No dataset can presently be certified as prospective evaluation evidence. |

The [Moonraker adapter](../../../backend/data_sources/adapters/moonraker.py) exposes
bed/extruder temperature and target, among other fields, but not ambient temperature,
heater power or fan status. Its observation unit is source-undeclared. Event time is
host-monotonic, not fabricated UTC. CSV file modification time is not sample time.
Synthetic timestamps, targets and fixture hashes cannot supply missing physical
conditions, calibration certificates or custody.

## 3. At most three practical cases

All cases are conditional on owner confirmation. Prefer a suitable existing raw
export with known provenance and exposure over new acquisition; prefer existing
equipment/export paths over purchases or a new connector.

| Case / procedure | Nominated hypotheses and needed parameters | Discrimination, confounding and challenge | Effort, evidence path and relationships |
| --- | --- | --- | --- |
| A. One passive body cooling in stable ambient; time-stamped body and ambient thermometry | Linear relaxation versus linear-plus-quadratic relaxation, specified below. Ordinary model-structure alternatives, not fault labels. Fit rate parameters on development episodes; separately characterize measurement chains. | Two initial temperature excesses and a cooling trajectory may distinguish rate dependence. Small temperature span, uncertain ambient, sensor lag or quadratic coefficient near zero can erase separation. Warming or systematic departures outside both frozen bands can challenge laws/bounds. | Provisionally simplest if a suitable CSV archive or owner-owned logger/specimen exists. New heating/preconditioning, operator effort and safe range need authority. Body–ambient relationship is explicit in equations, not an inferred connectivity effect. |
| B. Physical printer bed passive cooldown, with independently recorded power/fan conditions and ambient/reference measurements | The same two relaxation alternatives, now for bed temperature; controller/probe calibration and thermal gradients are additional nuisance factors. Not the synthetic offset hypotheses. | Active heating, changing fans, gradients and controller bias can imitate changed cooling rates. `target=0` alone does not establish unpowered cooling. Both laws may fail under documented steady conditions. | Higher burden: owner must confirm a real printer and read-only access; device operation needs separate authority. Existing API retains readouts but lacks necessary condition channels; an operator record/reference export is needed, not a new endpoint here. Heater/bed/fan interaction alone establishes no backend necessity. |
| C. Low-voltage RC discharge, time-stamped voltage measurements | Nominal discharge versus additional parallel leakage: `C dv/dt=-(1/R+G_m+G_L)v`, with `G_L=0` versus a development-specified nonnegative leakage domain. `R` in ohms, `C` in farads, conductances in siemens; meter loading `G_m` must be characterized. Possible parameter/fault alternatives only if nominal limits justify that interpretation. | Voltage decay rate alone confounds leakage with `R`, `C` and meter loading. Independent component/loading estimates are essential; an admitted leakage domain containing zero overlaps nominal. Nonexponential or reversed decay may challenge both, subject to procedure validity. | Only if apparatus, isolated safe procedure and logger/export already exist. CSV retention suffices; no serial connector proposed. Circuit relationships contribute through the stated current balance, not dependency direction alone. |

**Provisional preference: A.** It avoids assuming a physical demo printer and needs
no ingestion development. It is informative because it predicts trajectories at
two initial levels, where nuisance uncertainty and nested hypotheses can genuinely
defeat discrimination. No case is recommended unconditionally. If only B or C has
adequately documented resources, choose again using this comparison before freezing.

## 4. Provisional mathematical and uncertainty specification for A

Let `t` be elapsed seconds from a prescribed initial reading, `T` body temperature
in degrees Celsius, `A` constant ambient temperature, and `x=T-A>0` a temperature
difference. Difference units are equivalent to kelvins; no absolute-temperature
conversion is implicit. The proposed phenomenological laws are:

- `H_L: dx/dt=-k x`, giving `x(t)=x0 exp(-k t)`.
- `H_Q: dx/dt=-k x-q x²`, giving
  `x(t)=k x0 exp(-k t)/(k+q x0(1-exp(-k t)))`.

Here `k>0` has units `s^-1`, and `q>=0` has units inverse temperature-difference per
second. The closed `q=0` boundary reproduces `H_L`: do not exclude it merely to
manufacture separation. Hypothesis domains and point estimates are development
outputs to freeze, not numerical values invented in this plan. If development
cannot identify them sufficiently, prediction may remain wide or comparison
unavailable. RC voltage predictions would instead follow the exponential solution
of case C's current balance, with independently constrained component parameters.

For A, keep separate: the laws; fitted `k,q`; nominated model alternatives; body and
ambient measurement procedures; applicability assumptions; joint parameter/error
domains; and development versus evaluation records. Applicability requires the same
specimen/configuration, no ongoing heat input, bounded ambient variation and a
documented probe response compatible with the frozen horizons. These are untested
scientific assumptions until evidence addresses them, not architectural facts.

Use a declared measurement law such as `y=g T+a+e`: gain `g` is dimensionless,
offset `a` and residual `e` are in degrees Celsius. A separate ambient chain has its
own parameters. Resolution, rounding, drift, saturation, clock uncertainty and probe
lag require measured characterization or explicit working assumptions. Initial and
later readings from one probe share gain/offset; ambient/reference errors may also
be correlated. Carry joint domains with those shared parameters, rather than
silently treating every error as independently resampled. Bound provenance must
distinguish specifications, calibration estimates and assumed discrepancy allowances.

Project each frozen joint feasible set through its trajectory and measurement laws
to obtain raw readout sets at scheduled times, including elapsed-time uncertainty
and a bounded numerical error. Do not enter a prediction matrix manually. Specify
endpoint inclusion, rounding and any saturation law during preparation; an unknown
instrument limit is not permission to clamp a reading. Retain point forecasts
separately from uncertainty sets. Missing support prevents a complete exclusion
claim, even if an exploratory nominal curve can be computed. Finite calibration
does not establish universal hard bounds; authority or citation alone does not
establish predictive accuracy.

## 5. Prospective protocol, custody and evaluation

1. **Eligibility and calibration.** Obtain metadata first, without evaluation values
   or credentials. A named custodian records acquisition origin and exposure by
   person/process, including previous construction/tuning use. Previously exposed
   data may support development, not an unseen evaluation claim. Existing archived
   data are eligible only if raw provenance/conditions are adequate and the model
   team has not seen evaluation values before freeze. Separate known-level sensor
   calibration from physical-model development and evaluation episodes.
2. **Development and schedule.** Propose four development episodes, two at each of
   two owner-approved safe initial excess levels, followed by six evaluation episodes,
   three at each level. This checks level dependence and repeatability; it is not
   a statistically powered population study. Choose three early/middle/late forecast
   horizons from development, within characterized probe response and observation
   duration, then freeze exact times and permissible timing error. Six episodes
   yield 18 scheduled forecasts, not 18 independent trials. Preserve full available
   raw trajectories rather than selecting favorable points. Actual feasibility and
   operator effort must be confirmed before these counts become acquisition policy.
3. **Freeze before reveal.** Commit hypotheses, equations, parameter domains and
   point estimates, joint uncertainty/discrepancy rules, instrument/condition scope,
   numerical rules, decoder, baseline, usefulness thresholds, schedule and all
   inclusion/deviation/failure criteria before evaluation trajectories are revealed.
   Only prescribed initial body/ambient readings may condition each episode; commit
   its future predictions before subsequent readings are disclosed. Later ambient
   records check scope, not retrospectively tune the forecast. No fit to evaluation
   residuals, enlarged bounds or revised scope may preserve the original holdout claim.
4. **Custody and retention.** The named custodian controls the unrevealed raw bundle
   and access log; identify operator and any overlap with the modeling team. Preserve
   original measurements, units, instrument IDs, calibration records, locations,
   configuration, ambient/power/fan conditions as relevant, acquisition/sample times,
   clock basis and deviations. Separate capture time from measurement time. Retain
   immutable originals, digest manifest and a second recoverable copy, linked to
   model/version/results. Hashes detect changes, not truthful acquisition, blindness
   or physical accuracy. Disclose any access breach; downgrade exposed records to
   development evidence. Independent software checking is not independent acquisition.
5. **Raw evaluation first.** Compare original readouts with raw prediction sets.
   Compatible means a joint feasible assignment explains the evaluated observations;
   do not refit `k,q` independently at each time or episode. Incompatible means no
   assignment under the frozen model and complete supplied bounds, conditional on
   their assumptions. Unavailable means missing support/data/metadata or a predefined
   applicability failure prevents assessment, not evidence against a hypothesis.
   Both compatible means unresolved alternatives. Neither compatible means explicit
   model mismatch: equations, bounds, calibration or procedure may be inadequate;
   it does not identify which failed. Preserve per-time and joint episode/batch
   assessments, maintaining parameters declared shared across episodes.
6. **Uncertainty policy and decoder.** The proposed pilot reports compatibility
   against declared engineering working bands, not universal impossibility or
   confidence coverage. If the owner wants statistical rejection/coverage claims,
   design justified sampling and multiplicity policy separately before acquisition.
   A reporting-only decoder may categorize temperature drop as below an owner-set
   useful threshold `d_use`, or at/above it, with equality in the latter category.
   Its domain is finite, applicable numeric drops; missing/invalid/out-of-scope inputs
   are unavailable, not forced categories. Freeze threshold and numerical rules.
   Categories must never override raw discrimination or require a winner.
7. **Usefulness comparator.** Use persistence, `T_hat_B(t)=T0`, with the same allowed
   initial information. Score each development-fixed hypothesis point forecast
   separately against raw measurements: mean absolute error with equal episode
   weighting over the fixed horizons, improvement over persistence, and prediction
   band width/compatibility. Do not score the retrospectively best feasible point or
   choose a winning model on evaluation data and call it prospectively selected.
   Owner must freeze acceptable error, minimum worthwhile improvement and maximum
   useful band width. Report denominators and unavailable cases alongside all scores;
   a model may be unhelpful even if its bands contain every reading. No confidence
   statement follows from six episodes.
8. **Failures and revisions.** Record missing samples and deviations without
   automatic replacement. Independently recorded condition failures invoke frozen
   scope rules; a surprising residual alone is not an out-of-scope excuse. Retain
   failed predictions and unsuccessful acquisitions. Any later tuning creates a new
   model version and requires fresh evaluation data. Prediction assessment compares
   nominated laws; it does not establish the true cause, physical fault or effects
   of an intervention.

## 6. Application boundaries and architectural implications

[Raw acquisition contracts](../../../backend/data_sources/README.md) can retain CSV
exports or authorized API payloads with checksums and provenance. A CSV's sample
times and instrument/condition metadata must be retained explicitly: ingestion
does not automatically create calibrated operational observations or a trajectory
evaluation. [Source interpretation](../../adr/0011-engineering-semantics-and-source-property-interpretation.md)
can declare units with authority; it cannot make undeclared units or calibration
true. [Evidence assurance](../../adr/0019-content-bound-operational-evidence-selection-and-assurance.md)
checks selected evidence integrity, not empirical independence, and does not embed
raw bytes: retain the raw store separately. [Model state](../../../backend/model_state/README.md)
provides selected latest values, not a time-series prediction engine.

The [behavior contract](../../../backend/behavior_evaluation/README.md) and
[ADR-0015](../../adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md) support gated
exact numeric equality, not these relaxation laws, coefficient fitting or interval
projection. A small application can own the frozen mathematics, forecast evaluation
and custody manifest using existing raw retention paths. Preparation must specify
that composition honestly; no new backend capability is proposed here. Accepted
BRC finite candidate admission/ranking and decoder rules remain unchanged; any
future handoff is a separate justified exercise.

**IN-001 remains open, available and necessity untested.** In A the explicit
body–ambient dependence enters `x=T-A` and its evolution law. An influence declaration
could identify participating variables, governing context and dependency authority,
but would still need equations, parameters, units, uncertainty and temporal/
intervention meaning to derive a forecast. This case demonstrates no result
unavailable to the application approach. Physical interaction is not a backend
integrity gap; neither feasibility nor a successful empirical fit settles ownership.
Future comparative evidence would need a named consumer and a concrete missing
authoritative relationship/lifecycle fact or integrity boundary, tested against
application and existing-contract approaches under the same empirical task.

Separate open classes: empirical questions are forecast error, usefulness versus
persistence, and failures of nominated laws/bands; scientific assumptions include
lumped temperature, stable ambient and measurement response; application requirements
are timing, joint uncertainty, freezing and recoverable evaluation; possible
architectural gaps need a future concrete consumer, not speculative API design.

## 7. Original-objective contribution

Against the [seven original objectives](../../../CLAUDE.md), this plan adds no new
physical evidence. A future valid evaluation could contribute as follows:

| Objective | Bounded contribution and remaining requirement |
| --- | --- |
| 1. What exists/how connected | Documents specimen and measurement chain if confirmed; no general connectivity discovery. |
| 2. Particular-system state | Time-stamped local observations, not complete system-state knowledge. |
| 3. Why behavior | Challenges nominated response laws/bounds; plausible survivors do not identify a real fault or true cause. Diagnosis needs adequate alternatives and discriminating evidence/interventions. |
| 4. Next measurement/test | Assesses whether forecasts are empirically useful. BRC ranks within a supplied finite test set; this plan neither generates that set nor proves optimal measurement selection. Future selection needs supported prediction differences, uncertainty, costs and candidate procedures. |
| 5. Change impact | Remains open. Dependency review is not physical change impact; intervention laws and validated scope are still needed. |
| 6. Smallest valid changes | Remains open. Planning additionally needs goals, permitted actions, costs, constraints and validated change outcomes. |
| 7. Epistemic status | Separates acquired readings, assumed/fitted domains, calculated sets, unavailable assessments and custody exposure. Empirical accuracy and causal identification remain distinct. |

## 8. Consolidated owner decisions and authorization gates

| Information/decision needed | Gate and smallest next resolution |
| --- | --- |
| Which existing dataset or physical asset is actually available? | **Case selection.** Provide metadata-only description, physical versus virtual origin, current access and export capability. No credentials or evaluation values. |
| Instrument/model/ID, calibration/specification, resolution/response, sample clocks, ambient/configuration records and raw retention | **Feasibility.** Provide a metadata/schema description and calibration provenance; establish whether two initial levels and forecast horizons are observable without changing hardware. |
| Prior exposure and construction/tuning history for any existing data | **Evaluation eligibility.** Identify who/process saw which partitions, when and for what purpose; exposed records cannot be relabeled unseen. |
| Named custodian/operator and permissions | **Prospective independence/acquisition.** Specify access separation, retention responsibility and authority for reading/export and any physical preconditioning. Configuration is not permission. |
| Safe range, schedule and repeat effort | **Final procedure.** Confirm the proposed four-development/six-evaluation pilot is practical, or revise the schedule prospectively with its narrower claim. No statistical power is asserted. |
| Prediction purpose and policy | **Evaluation freeze.** Approve horizons, acceptable error, useful improvement/band width, decoder threshold and engineering-band versus statistical purpose. Statistical claims require a separately justified design. |

Minimum immediate action: owner confirms candidate availability and metadata
adequacy, without revealing evaluation values. Then finalize one procedure and its
custody/evaluation policy for separate preparation and acquisition approval.
General influence architecture, production deployment and causal identification do
not block this bounded feasibility decision. No successor is authorized.

END OF PROSPECTIVE MODEL VALIDATION FEASIBILITY
