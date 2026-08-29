# BH-001 Slice C — adversarial acceptance matrix

Status: owner-resolved red-first controls for the authorized evidence-gated
evaluator. The preimplementation discrepancy and every blocker row below are
owner resolved. Documentation assertions passed before production began.
BH-001 Slices A and B are owner accepted. Slice C is implemented and
adversarially reviewed; awaiting owner acceptance. Slice D has not started.

## 1. Public contract

| ID | Assertion or attack | Required result |
|---|---|---|
| C01 | Public package boundary | `backend.behavior_evaluation` exists and is read-only; private module layout is not public contract |
| C02 | Query facade method | Only `behavior_evaluation` with exact signature |
| C03 | Literal aliases and order | Exact status aliases plus ordered 22-reason `BehaviorEvaluationRefusalReason` |
| C04 | Result class fields and order | Exact accepted fields, no extras |
| C05 | Exact `__all__` | No aliases, private helpers, or future APIs |
| C06 | Frozen/extra-forbid/revalidate | Every public model reconstructs |
| C07 | Index booleans/coercion | Typed rejection |
| C08 | Implication-bearing fields | Rejected as extras |
| C08a | Public evaluator errors and exact ordered `__all__` | Exact three-class inheritance/codes, exact CN error class object, exact 21 names; no parser export |

## 2. Input and selector boundary

| ID | Assertion or attack | Required result |
|---|---|---|
| C09 | Wrong constructor dependency | Typed configuration error |
| C10 | Malformed behavior ID/context/cutoff | Typed input error before evidence access |
| C11 | Naive cutoff | Typed input error |
| C12 | Fewer/more than two selectors | Typed input error |
| C13 | Duplicate selector variable | Typed input error |
| C14 | Reversed valid selectors | Canonical identical result |
| C15 | Missing/forged nested SourceSelector | Typed input error |
| C16 | Registered behavior participant substitution | Typed before lower evidence access |
| C17 | Absent behavior with two valid variables | Both evidence branches preserved |
| C18 | Implicit source/discovery/cross-product | Absent by contract and AST |

## 3. Declaration lifecycle and evidence preservation

| ID | Assertion or attack | Required result |
|---|---|---|
| C19 | Behavior not registered | Exact refusal; both lower results carried |
| C20 | Registered, exact context not declared | Exact refusal; both lower results carried |
| C21 | All roots inactive | Exact refusal; both lower results carried |
| C22 | Same-root fork | Exact conflict refusal |
| C23 | Cross-root body disagreement | Exact conflict refusal |
| C24 | One healthy root | Declaration gate admitted |
| C25 | Corroborating identical roots | Declaration gate admitted; no winner |
| C26 | Different context only | Exact-context not declared |
| C27 | Lower typed failure on either branch | Both branches attempted once; first canonical unwrapped public failure type/code/message propagates; no result |
| C28 | Lifecycle failure with observations | Observation evidence unchanged |

## 4. Participant gates and refusals

| ID | Assertion or attack | Required result |
|---|---|---|
| C29 | Variable unregistered | `participant_model_not_registered` |
| C30 | No occurrence before cutoff | `observation_absent` |
| C31 | Resolution nonpositive | attachment refusal plus `binding_not_positive` |
| C32 | Resolution mismatch/divergent anchor | `observation_not_attached` |
| C33 | Malformed or inconsistent evidence | `evidence_not_assessable`; no parser call |
| C34 | Consistent boolean/string/object/array evidence against numeric VSP | `numeric_value_shape_mismatch`; numeric not evaluated; no parser call |
| C34a | Explicit null against nullable or nonnullable numeric VSP | `numeric_value_absent` only; numeric not evaluated; no parser call; lower finding preserved |
| C35 | VSP conflict | `numeric_specification_conflicted` |
| C36 | Quantity kind absent/conflicted | `model_quantity_kind_not_available` |
| C37 | Observation role absent/conflicted | `model_observation_role_not_available` |
| C38 | Source interpretation absent/conflicted/mismatch | `source_semantics_not_admitted` |
| C39 | Source unit mismatch | unit mismatch independent; no conversion |
| C40 | Quantity lock mismatch | Exact lock refusal |
| C41 | Observation-role lock mismatch | Exact lock refusal; roles may differ across pair |
| C42 | Unit lock mismatch | Exact lock refusal; no conversion |
| C43 | Multiple local failures | All exact reasons in gate order |
| C44 | Participant admission forgery | Recomputed and rejected |
| C44a | Missing/inactive or unique current nonnumeric VSP | `numeric_specification_not_available`; numeric not evaluated; no parser call |
| C44b | Numeric VSP with unit `not_declared` | `model_unit_not_available`; unit and numeric not evaluated; no parser call |

## 5. Cohort and time

| ID | Assertion or attack | Required result |
|---|---|---|
| C45 | Same exact five-field envelope | Cohort admitted |
| C46 | Source ID differs only | Cohort mismatch |
| C47 | Adapter ID differs only | Cohort mismatch |
| C48 | Attempt ID differs only | Cohort mismatch |
| C49 | Raw-record ID differs only | Cohort mismatch |
| C50 | Payload checksum differs only | Cohort mismatch |
| C51 | Source/receipt time differs only | Cohort remains same |
| C52 | Clock/run/sweep/occurrence/value/unit/quality differs | None redefine cohort |
| C53 | Staleness differs | Disclosed below; no age veto |
| C54 | Cohort mismatch | Parser not called; never `different` |
| C55 | `as_of` mutation | Temporal evidence may change, model membership may not |
| C55a | Peer local refusal with both occurrences present | Cohort still computed from exact five-field key |
| C55b | Either selected occurrence absent | Cohort `not_evaluated` |

## 6. Numeric parser and execution

| ID | Assertion or attack | Required result |
|---|---|---|
| C56 | Public parser identity/AST import | No copied/private numeric regex or parser, private import, float, or Decimal arithmetic |
| C57 | Input bytes boundary twin | 512 admitted / 513 refused |
| C58 | Coefficient digits boundary twin | 256 admitted / 257 refused |
| C59 | Fraction digits boundary twin | 128 admitted / 129 refused |
| C60 | Exponent representation twin | 4 admitted / 5 refused |
| C61 | Absolute exponent twin | 1024 zero admitted / 1025 refused |
| C62 | Expanded digits twin | 384 admitted / 385 refused |
| C63 | Expanded fraction twin | 384 admitted / 385 refused |
| C64 | Canonical byte twin | 386 admitted / 387 refused |
| C65 | Boolean/string/object/array/null/malformed | Never compared as numbers |
| C66 | Expansion-hostile input | Bounded refusal before allocation |
| C67 | Public parser typed parity failure | Exact re-exported CN class propagates unchanged; not `different` |
| C68 | First parser ordinary refusal, second parity failure | Failure not hidden |
| C68a | Numeric-eligible participant with peer earlier local refusal | After cohort admission, parser still called; typed parity failure not hidden |
| C68b | Model-unit identity unavailable | Participant is parser-ineligible even after cohort admission |
| C69 | Ambient Decimal precision/rounding | Output byte-identical |
| C70 | Equivalent lexemes/negative zero | Canonical exact `equal` |
| C71 | Different admitted canonicals | Exact `different` only |
| C72 | Any incomplete gate | `not_executed`, relation `None` |

## 7. Authoritative result reconstruction

| ID | Assertion or attack | Required result |
|---|---|---|
| C73 | Outer/nested `model_construct` | Rejected |
| C74 | Outer/nested `model_copy` | Rejected |
| C75 | Stale model-record ID | Rejected by reconstructed kernel material |
| C76 | Mixed model revisions | Rejected |
| C77 | Mixed binding revisions | Rejected |
| C78 | Mixed interpretation revisions | Rejected |
| C79 | Mixed cutoffs/contexts | Rejected |
| C80 | Swapped/duplicate sources or semantic results | Rejected |
| C81 | Selector/variable/entity/source retarget | Rejected |
| C82 | Candidate/occurrence substitution detectable from carried material | Rejected |
| C82a | Coherent value substitution preserving non-content-bound temporal IDs | Executable limitation: internally coherent lower result revalidates; BH rederives from it and does not claim raw authenticity |
| C83 | Forged lock/cohort/decimal/status/refusal/relation | Rejected |
| C84 | Missing/extra/reordered participant rows | Rejected |
| C85 | Wrong union-arm/index/count/order | Rejected |
| C86 | Deterministic serialization under map/order/hash seed | Byte-identical |

## 8. Architecture, preservation, and stop gate

| ID | Assertion or attack | Required result |
|---|---|---|
| C87 | Store/ledger/database/path/socket/cache construction | Absent |
| C88 | Writes, append, persistence, projection | Absent |
| C89 | Kernel or lower-layer upward import | Absent |
| C90 | CN dependency | Public parser contracts only |
| C91 | Port/VPA/flow/control/safety/diagnosis vocabulary | Absent |
| C92 | Committed model records | 29; zero BRG/BHD/BHW |
| C93 | Model revision | Exact accepted 29-record revision |
| C94 | VPA file and PT/VP artifacts | Exact accepted hashes |
| C95 | Binding/interpretation/temporal/source/structural bytes | Unchanged |
| C96 | Explicit historical memberships | 9/10/11/14/16/18/28/29 unchanged |
| C97 | Equal/different worlds | Disposable tests only |
| C98 | Slice D identities/artifact/fixture | Not started |
| C99 | Full and dual-clean-checkout suites | Green; loopback separately disclosed |
| C100 | Specialist findings and final report | Reconciled and committed before stop |

Every numbered row, including letter-suffixed resolution rows, must be green
before Slice C completion. The documentation assertions must pass before red
production tests begin. Stop for owner acceptance without beginning Slice D.

END OF BH-001 SLICE C ADVERSARIAL ACCEPTANCE MATRIX
