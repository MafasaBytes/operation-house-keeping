# Bounded model-derived prediction experiment: corrected final design

## Current status — complete and owner accepted, 2026-09-14

The bounded model-derived prediction experiment is complete and owner accepted.
Explicit equations and parameter assumptions produced conditional predictions with
the tested synthetic uncertainty, applicability and numerical semantics. Acceptance
establishes bounded mathematical/implementation consistency, not empirical accuracy,
real fault identification or causal truth. No production capability was added;
the disposable implementation is retained only as experimental evidence.
Empirical evaluation remains open. IN-001 remains open, available and untested,
with no successor authorized, allocated or implemented.

The [owner acceptance](../reports/2026-09-14-model-derived-prediction-owner-acceptance.md)
records the decision and immutable execution-report commitment. The original design
below remains historical authority; this addendum changes no premise, criterion or
resource limit and is not a new execution authorization. Its frozen original bytes,
historical input paths not committed separately, reviews, package and oracle are
recoverable from the execution report's canonical archive; the acceptance explains
their logical-path mapping. Original design SHA-256:
`1f057cece2dcea583a464889161875e951764c68d54f2fc93cf02cbd82b6ff65`.

2026-09-14 · synthesis only · proposed design for owner approval

## 1. Decision, verified baseline and frozen sources

Recommend preparing, under separate authorization, one exposed synthetic
application experiment: a fixed additive two-channel predictor and an independently
implemented raw-feasibility checker. Preparation and execution are separate gates.
This document authorizes neither. No generic solver, public API, influence control,
T2 implementation or finite ranker belongs to the immediate experiment.

Actual branch is `brc-exp001`; HEAD is
`a8b5327bcdeaf4a996f1e4c1240014ddff627420`, exactly the expected checkpoint.
There is no intervening advancement. Tracked and staged diffs are empty. Initial
inventories cover 772 tracked and 48 ordinary untracked files. Every existing
file, including all three inputs, is preserved; this design is the only addition
and remains untracked. Actual input paths match the links below; none was renamed.

All three inputs were read completely, through their ending markers, and their
whole-file SHA-256 commitments match:

| Frozen input | Verified SHA-256 | Provenance |
| --- | --- | --- |
| [Lead investigation](../proposals/2026-09-14-model-derived-prediction-codex-lead-investigation.md) | `8eead66545db04d9ca2f2a1837461619802bfa31a7a94b7405320a54a1103348` | Codex lead; same authoring conversation as the following challenger |
| [Lead-conversation challenger audit](../reports/2026-09-14-model-derived-prediction-codex-lead-investigation-challenger-audit.md) | `30c12d1825b5df399a7b3fe93d449a90c92a1d54d403ff0333497b27f3e1266b` | Fresh adversarial source/arithmetic review in the lead's conversation; not separately staffed or blind |
| [Independent focused review](../reports/2026-09-14-model-derived-prediction-independent-review.md) | `1be11cf816a4718c485135e3fc40c488d86cd27e5b17871fe92a9ffdf75b326d` | Fermat, separately staffed, fresh reviewer context, no authorship of the two frozen inputs; reported agent identity `01a0a0f8-4de8-7f13-b11c-04fad5adddc6` |

The independent review reports no additional unique model/build identity. Distinct
staffing is a review-role distinction, not empirical independence, blind selection
or immunity to correlated reasoning errors. This synthesizer has seen all inputs
and all specified observations. None is an unseen holdout.

Additional whole-file commitments were freshly verified:

| Accepted source | SHA-256 |
| --- | --- |
| [BRC final owner acceptance](../reports/2026-09-12-brc-exp001-final-owner-acceptance.md) | `74f833a1dd2f119d417c97a8b4b78590d9fd4c71fc3d04b7a35c3fd08c10ba78` |
| [Conditional-prediction comparative-proof acceptance](../reports/2026-09-13-conditional-prediction-comparative-proof-owner-acceptance.md) | `3922b52bb986ee0fba5540e0c8271bc4f4ab1346b35b12995b182c9741bb2922` |
| [Comparative-proof completion](../reports/2026-09-13-conditional-prediction-comparative-proof-completion-report.md) | `b97c7a3336d2d6cae684ba86b1f51acd6836d928c07fcf3c6bf8abf43d7fb91e` |
| [C7 equivalence correction](../reports/2026-09-13-conditional-prediction-c7-equivalence-correction-report.md) | `0adf183abed57fc06a26f3f27506dfe46bd355776d5737479dabec900786a79a` |

Historical execution results below are attributed to these accepted records, not
freshly replayed or archive-recovered results. Their bytes remain frozen. No tests,
experiment, package preparation, production evaluator, ledger write, allocation,
commit or history operation occurred during synthesis.

## 2. Findings reconciliation and exact claim

Both reviews give `approve_with_corrections`: three required corrections, four
non-blocking observations and no basic-recommendation blocker. The independent
review sustains MD-1–MD-3 and all observations, with the NBO-4 staffing distinction.
This design adopts the corrections without editing historical inputs.

| Finding and precise source | Resolution and acceptance evidence |
| --- | --- |
| MD-1 — challenger §6; independent review §4: raw versus decoder discrimination | §§3–5 require newly computed raw ranges and cells at baseline 40 and offset 5. Raw sets remain disjoint; only the supplied coarse vocabulary loses discrimination. Nominal separation is constructed by the supplied offsets/bounds, not discovered |
| MD-2 — challenger §§4.2/6; independent review §§3/4: unsupported raw elimination, full latent intersection | §§3–6 specify complete-domain admission, raw unknown for missing support, ±10 both-fit at 50, restored narrow neither-fit, inclusive endpoints and lower/upper latent clipping. No nominal fallback, forced winner or residual-only checker |
| MD-3 — challenger §§6/8; independent review §§4/7: exposed completion versus prospective custody | §7 makes exposed software completion the sole immediate track. Empirical custody and an optional unseen synthetic extension are separate; neither blocks the exposed experiment |
| NBO-1 — challenger §10; independent review §5: parameters/applicability | §§3/7/10 retain all constants as synthetic assumptions, no fitting or calibration claim, and disclose reference/hold/gain confounding |
| NBO-2 — same sections: optional T2/ranker | §8 omits both from execution and separately assesses any future BRC handoff; no test-selection or equivalence result is claimed here |
| NBO-3 — same sections: architecture limit | §9 keeps IN-001 open, available and unallocated; necessity is untested, not disproved by application feasibility |
| NBO-4 — same sections: reviewer independence | §1 distinguishes the same-conversation challenger from Fermat's separate staffing, without upgrading either to empirical or blind evidence |

Accepted BRC population made observed behavior evaluation available but did not
derive conditional predictions. The comparative proof carried supplied predictions
under equal-strength validation and showed no backend necessity from packaging.
The new bounded question is: given these equations, offset assignments, baseline
and complete domains, what raw reference readings and decoder outcomes are feasible,
how do parameter changes alter them, and can a raw observation challenge both
nominated models? This is conditional computation, not discovery of a physical law.

The one-scalar case reuses the accepted, exposed baseline/reference story and
threshold. Its small affine laws make inversion, error propagation, clipping and
information loss inspectable. It is not selected as evidence favoring a backend:
every alternative would need the same laws, meanings and uncertainty. H1/H2 share
the latent domain, rather than hiding high/low answers in hypothesis-specific
latent restrictions. Their offset separation nevertheless deliberately constructs
the positive separation case. Controls test input dependence and honest rejection.

## 3. Mathematical and measurement semantics

### 3.1 Roles, parameters and provenance

| Role | Fixed proposed specification | Epistemic status |
| --- | --- | --- |
| Equations Qb/Qr | `b = x + beta + e_b`; `r = x + e_r` | Supplied behavioral laws; no graph-derived law or entered prediction matrix |
| Scale and sign | x, b, r are absolute readings on the same Celsius scale, `degC`; beta and errors are Celsius differences; gains are dimensionless 1 | Explicit unit algebra. Positive beta raises b at fixed x; conditioning on b subtracts beta |
| Reference convention | Reference gain 1, reference bias 0 | Fixed synthetic assumption, not independently calibrated fidelity |
| Latent domain A-x | x in closed `[0,100]` | Common applicability-domain assumption, not an instrument display range |
| Hypotheses A-H | H1: beta=0; H2: beta=20 | Exact nominated offset accounts, not general faithful/faulty classes; P2 deliberately substitutes beta2=5 |
| Error domains A-eb/A-er | Closed `[-a_b,a_b]`, `[-a_r,a_r]`; nominal a_b=a_r=0.5 | Complete assumed hard support, including readout/rounding error. Not estimates, standard deviations, confidence intervals or proven empirical maxima |
| Joint support A-joint | Full Cartesian product of latent and error domains, without further cross-channel constraints | Set-valued completeness/attainability assumption, not statistical independence or a probability distribution |
| Measurement A-procedure | Baseline B and passive reference R have distinct readout identities, same subject, scalar scale, episode and law edition; x held fixed across acquisition; no saturation or perturbation | Frozen synthetic procedure meaning. Reference measurement is not an intervention on x or beta |
| Decoder A-decoder | low iff r≤50; high iff r>50 | Supplied partition, separate from prediction and from governing-criterion ownership |
| Parameter estimation | None | All numbers above are assumptions. Conditioning on b estimates no gain, bias, offset or error parameter |
| Observations for fitting | None | Exposed accepted material informed case selection, not an identifiable calibration fit |
| Observations for immediate evaluation | Every visible reading in §§5–6 | Synthetic controls, including mismatches; no reserved or acquired empirical observations |

Each A-* declaration in the future package must carry `synthetic_assumption`, its
own identifier, this design's externally computed commitment and its exact value
or rule. A citation/authority identifies an assumption; neither proves predictive
accuracy. Missing empirical calibration does not make an explicitly complete
synthetic assumption unavailable. P4 instead removes a required declaration/basis.

Applicability requires correct identities/unit/edition, successful finite readouts,
held scalar, passive reference, unit gains and absence of saturation. Unknown
required conditions prevent rejection. A documented broken hold, saturation or
reference perturbation is out of scope. Wrong identity/unit, failed acquisition
or unavailable metadata is unassessable. An offset other than the two nominated
values is not itself out of scope: it can produce an in-scope model mismatch.
Residual magnitude cannot supply an applicability-failure record.

Unknown reference bias gamma would give `b-r=beta-gamma+e_b-e_r`; unconstrained
gamma can erase offset identifiability. Hold change delta has the same confounding
role; unknown gain adds level dependence. A single baseline identifies neither x
nor beta. Distinct independently known levels are needed even for affine gain/bias
identification; calibration uncertainty and shared sources must then be propagated.
These limits do not block calculation with the proposed fixed assumptions.

### 3.2 Exact projection, endpoints and clipping

For each admitted H, independently of any reference observation:

`I_bh = [b-beta_h-a_b, b-beta_h+a_b]`

`X_h = [0,100] ∩ I_bh`.

If X_h=[L,U] is nonempty, `R_h=[L-a_r,U+a_r]`. Cartesian support makes this
an exact projection, not just a sampled envelope. Endpoint witnesses use the
opposite baseline/reference error extremes; all endpoints are closed. If X_h
is empty, H is baseline-incompatible; R_h and future cells are unavailable, not
an ordinary all-excluded future row. Missing required domains/bases are unknown,
not known empty sets. Known unsupported joint families are refused, not projected
using a rectangle while claiming exactness.

Clipping here means intersection of the inferred x interval with the assumed
latent domain before reference projection. It is neither physical instrument
saturation nor decoder clipping. Never clamp b or r to `[0,100]`, never clamp
R_h to that interval, and never clamp a raw reading to 50. Finite readings below
0 or above 100 are admitted mathematical readouts and receive decoder labels.

The local experiment uses exact scaled-integer rational arithmetic on decimal
inputs (scale 10^6 suffices), with no binary floats, epsilon comparison or display
rounding. Latent/error domains are real intervals; decimal wire encoding does not
introduce a quantization constraint on their feasible values. Canonical numeric
strings have optional minus, ordinary digits and at
most six fractional digits; no exponent, leading plus/zeros, trailing fractional
zeros or negative zero. Input integer parts have at most six digits. This modest
local wire bound exceeds every specified value, admits out-of-latent readouts and
makes numeric work statically bounded; it is not a physical range. Intermediate
results use exact integers without input-width truncation; output strings permit
the additional carry digit. Syntactic/capacity violations refuse without scientific
elimination. Later measured byte/node/time limits remain a separate gate (§11).

Interval forms are `{lower,upper,lower_closed,upper_closed}`. Finite endpoints
are canonical strings; null denotes an unbounded endpoint only in decoder regions,
with its closed flag false. A separate null interval plus its disposition denotes
empty/unavailable, never zero width. Closed `[v,v]` is a nonempty singleton;
open singleton intersections are empty. Interval intersection explicitly propagates
endpoint inclusion, not just maximum/minimum numbers.

### 3.3 Decoder and evaluation vocabulary

The complete successful mathematical decoder domain is every finite decimal
reference reading on the declared scale:

| Region | Endpoint rule |
| --- | --- |
| low: `(-∞,50]` | 50 belongs to low |
| high: `(50,∞)` | Any admitted finite value strictly above 50 belongs to high |

These regions are disjoint and exhaustive, including negative and above-100
readings. Infinity/NaN, absent values, failed acquisition and wrong-unit literals
are not successful decoder outcomes; no successful “other” category is invented.
Values outside local numeric serialization capacity refuse at the wire boundary,
not because the mathematical decoder lacks coverage.

A future cell **permits** iff the complete R_h intersects its region. It **excludes**
iff complete admitted support proves the intersection empty. For R_h=[p,q], low
permits iff p≤50 and high permits iff q>50. If required support/applicability is
unknown, both cells are unknown. Baseline-incompatible H has null future cells.

Raw **compatible** means the following full set is nonempty, including endpoints:

`J_h(b,r) = [0,100] ∩ I_bh ∩ [r-a_r,r+a_r]`.

Raw **excluded** means this set is proven empty under the complete admitted
model/support and applicable procedure. An already empty X_h has reason
`baseline_incompatible`, distinguished from `reference_outside_prediction`.
Raw **unknown** means no supported fit/elimination determination is available;
it does not mean compatible or excluded. **Model mismatch** is the admitted,
complete-model disposition when no nominated H fits. It challenges the combined
assumed laws/bounds/hypotheses, not beta alone, and is not evidence of a true cause.
Return both, one or neither compatible H, never an obligatory winner.

The residual inequality `abs((b-r)-beta_h)≤a_b+a_r` is insufficient near latent
clipping. The checker must use J_h. At nominal b=60.1, r=50, both J sets are
empty even though decoding low is compatible with H2's coarse row. Raw membership
and decoded-cell compatibility must remain separately visible.

## 4. Independent expected-outcome specification

The tables below are analytic expected results, not executed fixtures. During
separately authorized preparation, an oracle author must specify complete expected
objects from these equations and tables without calling/importing the predictor
or copying its output. Record that person's/process's actual provenance and prior
exposure; do not relabel this already exposed design as a blind oracle.

The predictor implements inversion then projection. The independent checker uses
direct three-interval intersection for raw fit and independently calculated
min/max endpoint formulas for projections and decoder intersections. Compatible
cases include a witness: choose the lower included endpoint of J_h, then calculate
`e_b=b-x-beta_h`, `e_r=r-x` and check all three domains. Exclusions carry empty-set
antecedents, not a witness guessed outside support. Oracle and predictor share the
supplied mathematical assumptions; they may share canonical serialization, but
must not share projection/evaluation code. The future source/import review records
this boundary. Two agreeing implementations still do not validate the laws.

The predictor's runtime inputs exclude case names, expected ranges/cells/scores,
oracle objects and evaluation r. A manifest outside the predictor maps visible
role names to inputs and expected outputs. Prediction is frozen before the
checker receives r, even in this exposed experiment, to demonstrate direction of
computation; this ordering does not create a holdout.

## 5. Compact complete numeric case matrix

P/E below mean permits/excludes in `(low,high)` order. Every range is closed.
Unless changed, use beta=(0,20), a_b=a_r=0.5 and complete synthetic support.
Each listed reading is a separately accounted evaluation input/output. Unlisted
arithmetic examples in this document are explanations, not extra executed roles.

| Role / changed input | X1; X2 | R1; R2 | Cells H1; H2 | Evaluation readings → raw compatible set | Distinct obligation |
| --- | --- | --- | --- | --- | --- |
| P0 nominal b=60.1 | [59.6,60.6]; [39.6,40.6] | [59.1,61.1]; [39.1,41.1] | (E,P); (P,E) | 39→{}; 39.1→{H2}; 41.1→{H2}; 41.2→{}; 50→{}; 59→{}; 59.1→{H1}; 61.1→{H1}; 61.2→{} | Nominal derivation, four closed raw endpoints, adjacent exclusions, neither reading and coarse/raw divergence |
| P1 b=40 | [39.5,40.5]; [19.5,20.5] | [39,41]; [19,21] | (P,E); (P,E) | 40→{H1}; 20→{H2} | Changed baseline defeats hard-coded original ranges; raw discrimination retained despite decoder loss |
| P2 beta2=5, b=60.1 | [59.6,60.6]; [54.6,55.6] | [59.1,61.1]; [54.1,56.1] | (E,P); (E,P) | 55→{H2}; 60.1→{H1} | Offset parameter mutation, correct subtraction and coarse-high information loss |
| P3 both half-widths=10, b=60.1 | [50.1,70.1]; [30.1,50.1] | [40.1,80.1]; [20.1,60.1] | (P,P); (P,P) | 50→{H1,H2} | Widening changes raw fit as well as cells; no unsupported unique elimination |
| P4 nominal values, A-eb basis absent | unavailable; unavailable | unavailable; unavailable | (unknown,unknown); (unknown,unknown) | 50→unknown for both; no compatible/excluded set asserted | Required uncertainty support missing; no nominal fallback |
| P4-R exact restoration | Identical to P0 | Identical to P0 | Identical to P0 | 50→{} | Restoration is a separately frozen twin, not post-reveal refitting |
| P5 b=51 | [50.5,51.5]; [30.5,31.5] | [50,52]; [30,32] | (P,P); (P,E) | 50→{H1}; 52→{H1}; 52.1→{} | low singleton at 50 retained; high open boundary; inclusive raw endpoint |
| P6 b=49 | [48.5,49.5]; [28.5,29.5] | [48,50]; [28,30] | (P,E); (P,E) | 48→{H1}; 50→{H1}; 50.1→{} | Upper endpoint 50 does not permit high; immediately higher raw reading excluded |
| P7 b=0.4 | [0,0.9]; empty | [-0.5,1.4]; unavailable | (P,E); null | -0.6→{}; -0.5→{H1}; 1.4→{H1}; 1.5→{} | Lower latent clipping; residual-only false fit; negative raw endpoint admitted; H2 baseline incompatibility |
| P8 b=99.6 | [99.1,100]; [79.1,80.1] | [98.6,100.5]; [78.6,80.6] | (E,P); (E,P) | 98.6→{H1}; 100.5→{H1}; 100.6→{} | Upper clipping, above-100 endpoint admitted; residual-only false fit at 100.6 |
| P9 b=121 | empty; empty | unavailable; unavailable | null; null | 50→{}, both reason baseline_incompatible | Both fail baseline; never manufacture all-excluded future rows |

This is 11 prediction roles, including the restoration twin, and 30 numeric
evaluation roles. P4 has semantic unknown output; it is not a successful ranked
matrix. Exact P4-R/P0 duplicates remain disclosed roles, not independent worlds.

At baseline 40, raw `[39,41]` and `[19,21]` are disjoint. A fitting scalar
reading still distinguishes the nominated accounts. Both ranges lie wholly in
low, so the coarse decoder erases that distinction; it has not made raw prediction
sets overlap or destroyed raw discrimination. The same distinction applies to P2.
P3 ranges overlap, not coincide. In an unclipped interior case, closed ranges with
offset separation d overlap when `d≤2(a_b+a_r)`; equality already shares a reading.

Every ready evaluation also outputs the literal decoder label and cell comparison
for each baseline-feasible H, independent of raw compatible sets. Thus P0/50
outputs low, coarse H1 excluded/H2 permits, and raw neither. P3/50 outputs low,
both coarse permits and both raw compatible. P1/40 and P1/20 both output low and
both coarse permits, but different singleton raw compatible sets. For P7, all
listed readings decode low; H2's future comparison stays unavailable. For P8,
above-100 readings decode high rather than being clipped or refused.

P0/50 can be specified by a different visible synthetic mechanism: x=50,
beta=10.1, errors zero, same unit gains and passive reference gives b=60.1,r=50.
It is in measurement scope but outside both nominated offsets. Its rejection
tests whether the evaluator can detect a bad nominated family, not merely confirm
same-model generated data. It supplies no empirical robustness or causal evidence.

## 6. Supplemental cases, refusals and exact diagnostics

Supplemental/refusal roles use P0's model, b=60.1 and evaluation r=50 unless
stated. They are mandatory, not
optional work discovered after the oracle freeze. Each mutation is a separate role;
independent condition records determine applicability before numerical evaluation.
Parameter controls carry matching changed assumption declarations; documented
false conditions carry matching false condition records. This is part of each
frozen control input, not a runtime repair. Unknown condition controls set both
the truth value and its basis to null. Deliberate missing/malformed/conflicting
basis controls are the exceptions and must remain defective as specified.

| Role | Mutation / stage | Exact disposition, diagnostic and target |
| --- | --- | --- |
| S1 | Prediction A-eb half-width=null, basis present | unknown both; `support_missing` at `/model/errors/baseline/half_width`; no X/R or elimination |
| S2 | Prediction joint-support basis=null | unknown both; `support_missing` at `/model/joint/basis`; no rectangular fallback |
| S3 | Evaluation held-scalar condition=null, r=50 | unknown both; `applicability_unknown` at `/conditions/held`; compatible/excluded sets null |
| S4 | Evaluation held=false, documented condition record, r=50 | out_of_scope; raw fits unknown, no elimination; `out_of_scope` at `/conditions/held` |
| S5 | Evaluation passive=false, documented reference perturbation | out_of_scope; no elimination; `out_of_scope` at `/conditions/passive` |
| S6 | Evaluation unsaturated=false, documented saturation | out_of_scope; no elimination; `out_of_scope` at `/conditions/unsaturated` |
| S7 | Evaluation reference unit=`K`, r=50 | unassessable; no decoding/elimination; `unit_mismatch` at `/observation/unit` |
| S8 | Evaluation reference subject differs | unassessable; `identity_mismatch` at `/observation/subject` |
| S9 | Evaluation reference episode differs | unassessable; `identity_mismatch` at `/observation/episode` |
| S10 | Evaluation reference law edition differs | unassessable; `identity_mismatch` at `/observation/edition` |
| S11 | Evaluation acquisition=failed, value=null | unassessable; `acquisition_unavailable` at `/observation/acquisition` |
| S12 | Prediction baseline acquisition=failed, value=null | unassessable, result=null; `acquisition_unavailable` at `/baseline/acquisition` |
| S13 | Prediction held=null | unknown prediction; `applicability_unknown` at `/episode/conditions/held` |
| S14 | Prediction held=false, documented condition record | out_of_scope prediction, result=null; `out_of_scope` at `/episode/conditions/held` |
| F1 | Prediction input includes forbidden expected_ranges field | refused; `schema_invalid` at `/expected_ranges` |
| F2 | Prediction beta2 supplied as `NaN` string | refused; `numeric_invalid` at `/model/hypotheses/1/beta` |
| F3 | Evaluation acquired reading is JSON null | refused; `schema_invalid` at `/observation/value`; not a successful “other” |
| F4 | Prediction baseline half-width=-0.5 | refused; `domain_invalid` at `/model/errors/baseline/half_width` |
| F5 | Prediction latent lower=1, upper=0 | refused; `domain_invalid` at `/model/latent` |
| F6 | Prediction baseline gain=2 | refused; `model_unsupported` at `/model/gains/baseline` |
| F7 | Prediction reference bias=1 | refused; `model_unsupported` at `/model/reference_bias` |
| F8 | Prediction joint kind=`diagonal_complete` | refused; `model_unsupported` at `/model/joint/kind` |
| F9 | Evaluation P0 result R1 lower changed to 59, original carried and independent pins retained | refused; `commitment_mismatch` at `/prediction/result` |
| F10 | Evaluation F11 hostile material with carried expected_sha256 changed to its new hash, independent pin still P0 | refused; same code/target as F9; coherent replacement is not accepted |
| F11 | Evaluation intact pinned prediction whose numerical content fails independent recomputation (hostile artifact with its own pin) | refused; `prediction_invalid` at `/prediction/result`; hashing alone is not mathematical validation |
| F12 | Prediction baseline basis is an object missing kind | refused; `schema_invalid` at `/model/errors/baseline/basis/kind` |
| F13 | Prediction baseline basis names `A-missing`, no matching declaration | refused; `basis_invalid` at `/model/errors/baseline/basis` |

P4's exact diagnostic is `support_missing` at
`/model/errors/baseline/basis`. P4-R and all ready P roles have no diagnostics.
Ready mismatch is a result disposition, not a refusal diagnostic. S1/S2 show
missing domain versus missing admission basis; no empirical citation is required
to restore a declared synthetic assumption. F6–F8 reject unsupported laws rather
than pretending the fixed local implementation is a general solver.

F11's hostile artifact must be independently specified during preparation, not
produced by running the predictor. It contains P0's canonical result shape with
R1 lower endpoint wrongly set to 59 and all dependent interval/cell traces made
internally consistent with that erroneous bound. Its independently pinned bytes
pass commitment checking but fail recomputation of Qb/Qr. Expected rejection is
atomic, without success payload. This distinct obligation separates pin integrity
from mathematical integrity.

These tables contain 14 supplemental semantic roles and 13 refusal roles, in
addition to §5. P0 prediction is the shared valid twin for S12/F12/F13; those
three links add no execution roles or independent scenarios.

| Wire role, nominal prediction mutated | Exact expectation |
| --- | --- |
| W1 duplicate stage key, both values predict | refused; `wire_invalid` at `/` |
| W2 extra field unexpected=true | refused; `schema_invalid` at `/unexpected` |
| W3 hypotheses field changed from array to object | refused; `schema_invalid` at `/model/hypotheses` |
| W4 baseline numeric string `60.10` | refused; `numeric_invalid` at `/baseline/value` |
| W5 baseline `999999` (integer-width boundary) | ready, both X empty, null R/future cells, baseline-incompatible traces |
| W6 baseline `1000000` (integer-width plus-one) | refused; `numeric_invalid` at `/baseline/value` |
| W7 baseline `60.123456` (fraction-width boundary) | ready; X1=[59.623456,60.623456], X2=[39.623456,40.623456]; R1=[59.123456,61.123456], R2=[39.123456,41.123456]; nominal cells and exact traces |
| W8 baseline `60.1234567` (fraction-width plus-one) | refused; `numeric_invalid` at `/baseline/value` |

Thus 76 fixed stage roles precede the resource probes: 41 from §5, 27 S/F
and eight W. Each measured byte/node/depth/
reference/count limit adds its separately frozen at/plus-one probes (§11); their
payloads depend on measured limits and cannot be instantiated honestly today.
Preparation must record final exact counts and full expected outputs for all
probes. There are no uncounted supplemental cases or silent oracle exceptions.

## 7. Two evidence tracks and freeze boundaries

### 7.1 Immediate: exposed synthetic mathematical/software consistency

Every baseline, reading, mutation and expected answer is exposed synthetic
material. Before execution, freeze design, complete role inventory, model/input
objects, independent oracle, predictor/checker sources, canonicalization, diagnostics,
resource policy and acceptance criteria. For each role lock prediction bytes before
feeding evaluation r. Cases P3 and P4-R are independent predeclared parameter
inputs, not adaptations to a surprising observation. Record actual accesses and
source-sharing. No custodian or unseen batch is required to finish this track.

A passing result supports tested implementation consistency, parameterized
projection, proper raw/category separation and rejection/unknown behavior on the
listed synthetic controls. Independent arithmetic checking and independent code
structure are distinct evidence. Same-model pairs provide procedural consistency
only; the alternative-offset and scope controls test particular mismatch boundaries,
not general physical robustness. No empirical accuracy, calibration or causal
identification follows. Survival among two hypotheses is not proof of the cause.

An optional later unseen synthetic challenge is not part of this execution.
It would additionally require a real named custodian, access separation, actual
pre-reveal prediction commitments and per-person exposure disclosure. Hashes or
an independently authored harness alone do not establish withholding. Any exposed
case or breach downgrades that case to development evidence.

### 7.2 Prospective: empirical prediction evaluation

No suitable independently acquired paired empirical dataset has been identified
in the accepted inputs; no new acquisition or external dataset search occurred.
The accepted baseline and showcase evidence are exposed/synthetic. This design
creates no empirical holdout and invents no measurements. This track is outside
immediate execution and does not block the exposed software experiment.

Before any empirical reveal, an independently controlled lab/data custodian must
retain paired raw records and episode-condition records. Independently calibrated
readout chains must observe the same held scalar with documented scale, gain,
bias, resolution/rounding, drift, saturation, pairing and nonperturbation bounds.
Separate known-level calibration/fitting records must identify the needed parameters
and justified joint uncertainty before evaluation. Shared calibration errors must
be assessed; another channel name is not independence. A commanded offset requires
independent verification of its effective value and noninterference.

Freeze equations, hypotheses, all estimated/fixed parameters and uncertainties,
decoder, procedure/applicability rules, allowed per-episode baseline conditioning,
raw criteria, sample schedule/inclusion and failure dispositions before withholding
reference observations is lifted. The custodian reveals all scheduled records,
including failures/out-of-scope cases; disclose prior exposure per person/process.
Do not fit parameters, enlarge bounds or alter scope from those observations and
claim the old holdout stayed unseen. Revised models require new evaluation records.

One verified in-scope pair can challenge a complete claimed hard-bounded model;
it cannot identify which law/bound failed or establish population accuracy. Finite
calibration samples cannot establish universal hard limits. If uncertainty is
statistical, the owner must instead approve coverage, sample-size justification
and rejection policy prospectively; a tail observation is not logical impossibility.
Prediction accuracy remains separate from causal identification. Synthetic
completion satisfies none of these acquisition/custody/calibration prerequisites.

## 8. BRC handoff is separate, not an implicit contract change

Immediate outputs are raw ranges, T1 cells and raw-fit dispositions, not BRC
requests, finite-test scores or recommendations. T2's nuisance law and the accepted
ranker are unnecessary for that claim. Omission is minimality, not evidence against
their utility. No accepted premise, decoder admission or ranking rule is changed.

A future authorized handoff would need a complete admitted finite matrix and
all accepted hypothesis/procedure/decoder/epistemic forms under the
[BRC synthesis](2026-09-11-brc-exp001-baseline-reasoning-closure-spike-design.md)
and [comparative design](2026-09-13-conditional-prediction-comparative-proof-design.md).
Unknown support must stop complete ranking; baseline failure is not a fabricated
all-excluded row. Raw rejection at 50 cannot be smuggled into the existing low/high
matrix: the observed low category still has H2 as its coarse survivor. Raw study
evaluation stays separate unless a different consumer contract is explicitly approved.

At baseline 40, an optional T2/ranker extension would have T1 survivor branches
`[{H1,H2},{}]` and T2 `[{H1,H2},{H1,H2}]`. Equal worst counts of 2 do not make
these equivalent: accepted C7 retains empty branches and multiset multiplicity.
No extension, handoff execution or revised finite-ranking policy is proposed here.

## 9. Architecture comparison and IN-001 disposition

| Approach | What it can contribute to this case | What remains necessary |
| --- | --- | --- |
| Application-owned additive model | Explicit bindings, model declarations, exact interval projection and raw evaluation over public/admitted input material | Supplied law/procedure/domain meanings and local freeze/integrity checks; empirical validity remains separate |
| Existing behavior/evaluation contracts | Observed equality/difference and existing observation/constraint admission | BH's native exact unordered numeric equality has no offset/error law or hypothetical projection; population cannot supply the missing rule semantics |
| Explicit influence/dependency representation | If explicitly specified: source/dependent variable bindings, applicability, law edition and dependency review; intervention invariance only if separately declared | The numerical equations, parameter/error support, conditioning/projection rule, units/procedure and decoder still have to be supplied |
| Narrow combination | Existing public input ownership plus application equations | No added influence representation is required for the bounded conditional computation; no broad backend design follows |

The inspected [BH contracts](../../../backend/model_kernel/contracts.py),
`ExactNumericEqualityRule`/`BehaviorRuleDeclaration`, and
[ADR-0015](../../adr/0015-explicit-behavior-declarations-and-evidence-gated-evaluation.md)
expressly delimit the native rule. [BH evaluation](../../../backend/behavior_evaluation/facade.py)
admits observed paths, not fabricated future observations. CN observed predicates
([ADR-0012](../../adr/0012-explicit-variable-constraints-and-evidence-gated-evaluation.md))
and FC governing designation
([ADR-0022](../../adr/0022-explicit-flow-operating-criterion.md)) do not supply
these affine laws. [Evidence alignment](../../../backend/evidence_alignment/contracts.py)
and content commitments
([ADR-0019](../../adr/0019-content-bound-operational-evidence-selection-and-assurance.md))
bind carried content, not calibration or physical truth. Public owners remain
authoritative for their own facts; computed references cannot impersonate evidence.

IN-001 remains open, available, unallocated and unimplemented. Its necessity is
untested here. The historical inactive influence alternative is untested, not
disproved. Application success would show local sufficiency for supplied laws,
not settle future backend ownership. Connectivity, dependency direction and
association alone imply neither causality nor conditional predictions.

Future comparative evidence could establish value for a named consumer needing
an authoritative mechanism binding/context/law-edition fact or correction,
withdrawal/replay integrity boundary that equally validated application/public
carriage cannot satisfy. Hold equations, parameters, evidence, procedure and
validation constant; isolate the one missing fact/relation and identify the rule
or obligation it enables. If only the influence side receives equations, the
comparison confounds law expressivity with influence. Reuse/packaging convenience,
an application bug or BH's narrow rule alone is insufficient. Do not add an influence
control merely to expand this small software experiment's architectural claim.

## 10. Complete local runtime forms and trace contract

These are closed, experiment-local wire forms, not a public API proposal.
Preparation must materialize every field and expected object; abbreviated tables
are not permission to omit carried inputs, refusals or output traces.

| Form | Complete required fields and rules |
| --- | --- |
| Prediction request | `version=1`; `stage=predict`; `design_sha256`; `model`; `episode`; `baseline`. No other fields |
| Model | `kind=additive_two_channel_v1`; `edition`; `equations` containing exactly Qb/Qr identifiers and the exact bodies in §3.1; `scale=degC`; `gains={baseline:1,reference:1}`; `reference_bias=0`; `latent={lower:0,upper:100,basis:A-x}`; `hypotheses=[{id:H1,beta,basis:A-H1},{id:H2,beta,basis:A-H2}]`; `errors={baseline:{half_width,basis},reference:{half_width,basis}}`; `joint={kind:cartesian_complete,basis:A-joint}`; `procedure_basis=A-procedure`; `decoder={threshold:50,low_upper_closed:true,high_lower_closed:false,basis:A-decoder}`; `declarations` mapping declaration IDs to complete `{id,kind,design_sha256,role,value}` records. Numeric values use strings. Unknown support fields/bases may be null; known invalid/unsupported fields refuse |
| Basis | `{id,kind:synthetic_assumption,design_sha256}`; id identifies the exact frozen declaration in the package's carried declaration map. Full declaration map is part of each request's model under `declarations`, not an external trusted lookup; duplicate/missing/conflicting known declarations fail admission. Null required basis produces semantic unknown |
| Episode | `{subject,scalar,episode,edition,conditions}`; conditions exactly `{held,passive,unsaturated,declarations}`, each truth field `{value:true/false/null,basis}` with a carried synthetic condition declaration or null. The declarations map uses the complete declaration-record form above. Required known values have a matching declaration |
| Baseline | `{channel:B,subject,scalar,episode,edition,unit:degC,acquisition:acquired/failed,value}`; all identities must match episode. Value is canonical numeric string when acquired, null when failed |
| Evaluation request | `version=1`; `stage=evaluate`; `design_sha256`; `prediction={request,result,expected_sha256}` containing the complete frozen prediction request/result, with expected pin independently retained; `conditions`; `observation`. No oracle or expected fit fields. Evaluation conditions are independently recorded held/passive/unsaturated forms, not changed model parameters |
| Observation | Same fields as baseline, with `channel=R`. Finite acquired readings require canonical value; failed acquisition requires null. Wrong unit/identity is a syntactically admitted unassessable control, not mathematical coercion |
| Prediction response | `version,stage,input_sha256,status,diagnostics,result`. Status is ready/unknown/out_of_scope/unassessable/refused. Ready result has H1/H2 ordered records: `id,baseline_status,X,R,cells,trace`. Baseline status feasible/baseline_incompatible. Cells are low/high records with `disposition,intersection,antecedents`; null for baseline-incompatible H. Unknown result has both H unknown, null X/R, unknown cells and admission-only trace |
| Evaluation response | Same envelope. Ready result has `decoded`, H1/H2 ordered records `{id,fit,reason,J,witness,coarse,trace}`, `compatible_hypotheses`, `excluded_hypotheses`, `unknown_hypotheses`, `model_mismatch`. Fit compatible/excluded; coarse comparisons low/high cell or unavailable for baseline-incompatible H. Compatible/excluded arrays may be empty. Unknown evaluation has both fit unknown, compatible/excluded arrays null, unknown list both, model_mismatch null |
| Failure responses | Out_of_scope/unassessable prediction has result null. Out_of_scope/unassessable evaluation uses the unknown evaluation form, decoded=null, plus diagnostic. Refused always has result=null and exactly one diagnostic, no H/range/cell/fit/success fields. Unknown prediction/evaluation has exactly one missing-support/applicability diagnostic; ready has none |

Identifiers are nonempty ASCII strings of at most 64 characters, sorted where
maps are used; pins are lowercase 64-hex SHA-256 strings. All records forbid extra
fields and duplicate keys. Condition basis declarations accompany the condition
object in a required `declarations` map in each conditions form; this map is part
of request accounting. Edition disagreements yield unassessable identity mismatch.
Declaration IDs are local to the complete frozen input, not authoritative anchors.
Declaration roles are latent, hypothesis_offset, baseline_error, reference_error,
joint_support, procedure, decoder, condition_held, condition_passive and
condition_unsaturated. Their values are respectively the closed latent interval;
`{hypothesis,beta}`; baseline/reference half-width strings; the joint-family string;
the exact unit-gain/zero-bias/held/passive/unsaturated procedure in §3; the decoder
threshold/endpoint flags; or the corresponding condition boolean. The latent value
uses §3.2's interval form; procedure value contains `scale,gains,reference_bias,
held,passive,unsaturated`; decoder value contains `threshold,low_upper_closed,
high_lower_closed`. For known values these declarations must match the model or
condition fields they support. Null required values stay unknown and must not be
filled from spare declarations. Extra declarations cannot silently modify the
fixed law family.
Known malformed basis/declaration shapes use `schema_invalid` at their pointer;
unresolved/conflicting known basis IDs use `basis_invalid` at the basis pointer.
F12/F13 and their disclosed valid twins cover these distinct obligations.

Canonical JSON is UTF-8, sorted object keys, compact separators, ASCII identifiers,
no duplicate keys, no floating JSON numbers and no nonfinite values. Version is the
integer 1; endpoint flags and condition truth are JSON booleans, not numerics.
Arrays are in fixed H1/H2 and low/high order. Hashes of responses, byte/node
measurements and object-map references are external receipts, avoiding self-hash
or self-size circularity. Pins and declaration commitments are checked against
independently retained manifest expectations, not just attacker-supplied self-hashes.

Exact diagnostics are `{code,target}`. Admission precedence is: bounded wire
preflight; structural/numeric/domain validation; commitment verification;
supported-law/basis validation; acquisition/identity/unit; known scope failure;
unknown support/applicability; numerical derivation. Within a phase choose the
lexicographically first failing JSON pointer. Supplemental cases isolate one failure.
For aggregate faults this precedence is frozen; no arbitrary latest-owner rule.
Evaluation first validates the carried prediction commitment and independently
recomputes its ready content before using its ranges. Non-ready frozen predictions
propagate their unavailable disposition without inventing fit. Failed baseline
acquisition is unassessable (S12, valid twin P0); prediction unknown/false conditions
use S13/S14's exact code/target and prediction output forms.

Every per-H trace has exactly `design_sha256,model_sha256,request_sha256,basis_ids,
admission,baseline,projection,decoder,evaluation,stop_reason`. Basis IDs are sorted
and identify carried declarations. Admission is `{identity,unit,held,passive,
unsaturated,complete_support}`, each boolean or null when unknown; it makes no
physical verification claim. Baseline is `{I_b,X}` or null; projection is `{R}`
or null; decoder is `{low_intersection,high_intersection}` or null; evaluation
is `{reference_inverse,J}` or null. Intervals follow §3.2. Stop reason is null
or the missing-support/applicability/scope/acquisition/identity/unit code, or
`baseline_incompatible`. Prediction evaluation is always null. Unknown paths
have all numeric components null; baseline-empty paths have baseline material
but projection/decoder null. Response/H witnesses are `{x,e_b,e_r}` or null;
cell antecedents are sorted required declaration IDs. Unknown evaluation H records
retain the same fields as ready records, with J/witness=null, coarse unknown (or
unavailable for a known baseline failure), and reason equal to the unavailable
diagnostic code. Unknown prediction H records use baseline_status=unknown,
null X/R and both unknown cells with null intersections. Out-of-scope/unassessable
evaluation follows that unknown form. Refusals carry no trace or result.

Ready prediction traces carry: design/model/input/declaration commitments;
Qb equation/beta/error/domain antecedents; untrimmed I_bh; clipped X_h; Qr
projection to R_h; both exact decoder intersections and completeness basis.
Ready evaluation traces carry: frozen prediction pin; procedure/identity admission;
inverse reference interval; all three J_h intersection operands/result; witness
or empty-set reason; raw fit and separate coarse comparison. Empty X_h trace
stops before future projection. Unknown traces stop at missing admission basis;
scope/acquisition unavailable dispositions include no numerical claims. No cell, authority, case
label or expected matrix is allowed as an equation antecedent.

No public facade call or backend mutation is needed by this immediate local
arithmetic experiment. Accepted public-input findings are reused with attribution,
not represented as fresh integration verification. Future production/public-owner
integration requires its own authorized scope.

These forms resolve routine serialization, exact arithmetic, diagnostic ordering,
local layout and checker strategy with the rationale of auditability and bounded
work. They do not assert production integrity, physical authentication or general
solver correctness. Preparation must translate these definitions into an exact
closed schema and independent complete oracle; any ambiguity found then is a
reported design discrepancy, not an unreviewed semantic change.

## 11. Preparation, resource measurement and execution gates

### 11.1 Separately authorized preparation requirements

Preparation may later create only the explicitly authorized disposable package
and its retention documents, not production source/tests/fixtures. It must freeze
complete runtime forms, declarations, every P/S/F role and valid twin, all supplemental
wire/basis/acquisition/condition/resource probes, canonical input/output objects,
exact diagnostics/targets, source-to-output traces, and independent expected objects.
A role manifest must disclose duplicates, stages, aliases and exact counts; §5's
counts do not include §6/§10 additions. Unknown and refusal roles have complete
expected output objects too, not placeholders or status-only comparisons.

Review predictor/checker source independence and provenance, including shared
canonicalization; freeze all source bytes and record assumptions/prior exposure.
Independent oracle construction must precede any access to actual predictor output.
Static schema, arithmetic witness and full-output accounting checks are preparation
work; execution of the predictor/checker against experimental observations is not.
No outcome rehearsal, mutant experiment or claimed passing run is authorized by
this design or by package preparation alone.

### 11.2 Separate input/output accounting and measurement plan

After preparation authorization, measure the canonical prepared inputs and
independently specified complete expected outputs, not estimates from an earlier
experiment. Report separate per-role and maximum byte sizes, JSON charged-node
counts, depth, scalar/identifier lengths, declaration/ref occurrences, trace/event
counts and batch object-map totals. A charged node is each JSON container and
each primitive value per occurrence; keys affect bytes but are not nodes. References
are charged as wire values, not recursively expanded; fully carried prediction
request/result in evaluation is charged again in full. Declaration resolution
counts are separate telemetry, not silently exempt work or an imported BRC charge.

Use an independent static counter to cross-check these measurements and derive
upper bounds from the closed schema and numeric widths. Include ready, unknown,
baseline-empty, out-of-scope, unassessable, every refusal template and the largest
complete evaluation trace. Measure complete outputs, not only raw ranges or final
cells. Separate source/package/archive storage from runtime IO accounting.

Before execution approval, propose new input-byte/node/depth, output-byte/node/depth,
reference/declaration/cardinality and batch limits from those measurements, with
explicit measured headroom and a reason for each margin. No inherited BRC or
comparative-proof numerical cap is justified here. No measured maximum is claimed
today. The numeric format bound in §3.2 is a design capacity, not a measured runtime
maximum. The preexecution receipt must contain actual measured values and adopted
limits; absent that receipt, execution approval is blocked.

Measure clock/timer and allocation instrumentation with schema-only traversal,
serialization and counter calibration, not prediction/evaluation experiments.
Propose an environment-specific wall-time, memory and evidence-storage safety
budget from measured envelope work plus an explicit allowance for unmeasured
arithmetic. If such calibration requires prediction execution, request a separate
resource-only authorization; do not smuggle it into preparation. Actual predictor
time/memory maxima and stopping behavior remain unmeasured until execution. Hard
supervisor ceilings are safety limits, not invented certified maxima.

Freeze both valid domain specimens and primitive at/plus-one guard probes for
each capacity. Synthetic padding probes do not establish that equally large valid
domain outputs exist. The bounded preflight must reject oversized requests before
model reconstruction; incremental output construction must stop before materializing
an over-budget result. Resource refusal uses `resource_limit` targeted to the
first exceeded dimension (`/limits/input_bytes`, `/limits/input_nodes`,
`/limits/input_depth`, `/limits/output_bytes`, `/limits/output_nodes`,
`/limits/output_depth`, `/limits/references`, `/limits/declarations`,
`/limits/roles`), in that listed order when simultaneous. The small fixed refusal
envelope must itself be measured and reserved outside successful-output space;
it leaks no partial ranges/cells/fit. Numeric-width limits use §6's numeric diagnostic.

### 11.3 Execution remains separately gated

Execution approval requires the frozen package/oracle/source/schema/role commitments,
closed discrepancy register, complete measured accounting and justified limits,
retention/recovery plan and owner adoption of §13. Dynamic checks are explicitly
deferred to that authorized execution: exact actual-versus-oracle comparisons,
parameter mutation/hard-code controls, missing-support non-elimination, raw/coarse
separation, independent checker rejection of hostile predictions, source/import
and oracle-access isolation, guard ordering/zero derivation on early refusal,
incremental output-stop/no partial success, and deterministic replay under permissible
input order and independently chosen temporary roots. Compare canonical semantic
outputs, diagnostics, traces and deterministic byte/node/event counters exactly.
Clock and memory samples are retained per run with environmental context, not
asserted byte-identical; every run must satisfy its adopted safety limits.
Preserve all diagnostics, traces, telemetry and failures; no pass claim is made
at preparation.

Recoverable canonical evidence must retain the exact design/source/oracle/schema/
manifest, every complete input and actual output, expected outputs, comparisons,
pins, resource measurements, dynamic-check receipts and source-sharing/exposure
records. Retain canonical object bytes with lengths and digests in a self-contained
path-safe archive and independently held manifest; verify bounded decoding,
duplicate-path/key rejection, reserialization and every entry's digest before
disposing of temporary work. Hashes alone without recoverable bytes are insufficient.
Preserve historical failures and all original artifacts; no overwrite or relabelling.

## 12. Acceptance criteria and contribution to original objectives

A passing immediate result requires every frozen role to match its complete
independently specified expected object, including numerical endpoints, inclusion
flags, decoder intersections, antecedent bases, witness/empty-set traces, diagnostic
codes/targets and unknown/refusal no-success invariants. Every supplemental/refusal/
capacity role must be accounted for. Changed b and beta must change raw ranges as
specified; missing required support must not eliminate; widened support must fit
both at 50; narrow support must fit neither there; clipping must defeat residual-only
fit. No unapproved oracle correction, omitted surprise or post-freeze parameter
adaptation is a passing result. Resource overrun, premature evaluation-input access
by the predictor, unavailable canonical evidence or failed replay blocks acceptance.

A pass adds tested equation/domain-to-range derivation and honest raw evaluation
upstream of the earlier supplied-matrix experiments. It does not repeat their
ranking/packaging results as new empirical evidence. These are potential bounded
contributions to the [original objectives](../../../CLAUDE.md), not closures:

| Objective | Added result if passing; unresolved requirement |
| --- | --- |
| 1. Existence/connectivity | Explicit model participant identities only; no new topology or physical connectivity evidence |
| 2. Current particular-system state | Conditional latent feasible set at an exposed synthetic baseline; no new measured state or production state delivery |
| 3. Why behavior? | Consequences of two nominated offset accounts and a way to challenge their combined assumptions. Explaining the calculation/comparing nominated H is not explaining actual behavior. Real diagnosis still needs validated models/procedures, independent evidence, adequate hypothesis scope and causal identification where claimed |
| 4. Next best measurement/test? | Raw sets and T1 cells can supply future justified premises. Immediate experiment selects no best test. Accepted BRC already selects within a supplied finite set; neither result generates that set, establishes global optimality, operational utility, costs or safety. Decoder information loss remains explicit |
| 5. Change impact | Parameter sensitivity and dependency review only. Physical changes require justified interventions, mechanism invariance, configuration/regime applicability and validated effect propagation. Objective 5 remains open |
| 6. Smallest valid changes/planning | No plan. Still requires goals, permitted actions, validated effects, interactions/constraints, reachability, uncertainty and an approved cost/cardinality optimum. Objective 6 remains open |
| 7. Epistemic distinctions | Inspectable assumed law/domain → calculated projection/cells → conditional raw compatibility/exclusion, separate unknown/scope/mismatch and exposed evidence labels. No source authentication, calibrated accuracy or causal truth is supplied by citation or calculation |

## 13. Consolidated owner decisions, blockers and recommendation

| Decision / scope | Already available | Still needed; smallest resolution | Owner boundary |
| --- | --- | --- | --- |
| Bounded synthetic H/procedure/applicability/uncertainty meaning | Complete proposed exact offsets, common latent domain, passive held procedure and Cartesian hard assumed support | Adopt §§3–6 as one bounded conditional claim; P1/P2/P3/P4 discriminate implementation behavior | Owner design approval; no separate meeting for each decimal/layout choice |
| Raw evaluation/exclusion policy | J_h, unknown/no forced winner, mismatch distinct from independent scope records; complete decoder | Approve these dispositions and immediate exposed-only completion; P0/50, P3/50 and P4/50 distinguish policies | Consequential evaluation-policy adoption, not ordinary implementation discretion |
| Preparation completeness and resources | Runtime forms, role obligations and measurement plan | Separate preparation authorization, full oracle/accounting/limits receipt and closure of any discovered ambiguity | Blocks execution, not today's synthesis; ordinary arithmetic/serialization choices are resolved here |
| Empirical accuracy/parameter identification | No suitable independent paired data identified; explicit confounding/acquisition requirement | Data/operator authority, calibration/hold/joint-error evidence, independent custody and frozen criterion; first new verified pair can challenge a hard claim | Blocks empirical evaluation only; deterministic versus statistical policy and study size require owner approval |
| Optional unseen synthetic extension | All current controls exposed | Explicit stronger claim, named custodian/access separation and new withheld inputs | Not immediate scope and not a synthetic completion blocker |
| Production/backend ownership | Public contracts plus application law can in principle carry this case; IN-001 necessity untested | Named consumer and demonstrated missing semantic fact or lifecycle/integrity boundary; equally validated fixed-law comparison | Production/future architecture only, no allocation now |
| Future generality, physical impact and planning | Scalar model and limited dependency sensitivity | Resolve richer hypotheses/dynamics/joint support/test generation/actions only for a named later question | Future work; objectives 5/6 stay open |

Minimum owner choices for the next gate are adoption of the exact bounded
synthetic meanings and raw evaluation policy, acceptance of exposed-only evidence,
and separate preparation authorization. No empirical custodian, production owner,
general causal ontology or IN-001 decision is required first. Routine exact-number
representation, fixed local schema, diagnostic priority, checker method and omitted
T2/ranker are resolved with the rationale above. No proposed measurement policy
has been silently promoted to physical truth.

Recommend approving this corrected design for a later, separately authorized
preparation step. Execute only after the complete measured preexecution receipt
and separate execution approval. If the desired result is empirical accuracy rather
than computational consistency, prioritize the independent acquisition/calibration
prerequisite instead; this experiment cannot deliver that result. Keep IN-001 open
and available, with no successor, milestone or ADR selected. Stop for design approval.

Verification covers complete frozen-input reads/digests, accepted-evidence pins,
checkpoint, source links, sections/tables/traceability, ending marker, whitespace,
empty tracked/staged diffs and byte-for-byte preservation inventories. Only this
untracked design is created; no preparation or experiment has been performed.

END OF MODEL-DERIVED PREDICTION BOUNDED EXPERIMENT DESIGN
