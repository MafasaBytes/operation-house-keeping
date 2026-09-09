# FC-001 Slice A adversarial acceptance matrix

## 1. Authority and boundary

The frozen [synthesis](../specs/2026-09-09-fc001-explicit-flow-operating-criterion-design.md)
and [owner approval](../reports/2026-09-09-fc001-final-design-owner-approval.md)
govern. This matrix translates only Slice A obligations. Valid retained
historical support remains loadable; stale content IDs and structural closure
attacks reject. Currentness/applicability statuses are excluded.

## 2. Executable obligations

| ID | Attack or positive counterpart | Required Slice A evidence |
| --- | --- | --- |
| A01 | Two exact records, defaults, field order, unknown/null fields | 11/7 exact fields; no alias or extra record kind |
| A02 | Canonical IDs and stored filenames | Independent literal fcd/fcw goldens; UTC and UTF-8 parity |
| A03 | Evidence/parent permutations and duplicates | Evidence canonical dedup; duplicate parents reject before sorting |
| A04 | Six evidence arms, positive citation, withdrawal citation | FCD citable; FCW evidence-free and uncitable |
| A05 | Missing/wrong-kind/forged FMA, CRG, VCN | Typed rejection; no staged write |
| A06 | Missing/substituted six FM and transitive FL pins | Full existing lower closure rerun, no trusted flags |
| A07 | Wrong variable, participant, flow, context, role or constraint anchor | Exact coherence; VSM context-independent |
| A08 | All four orientations | Separate S values; no sign evaluation |
| A09 | Different same-body witnesses and provenance | Different record IDs, equal canonical FC body; exact witness retained |
| A10 | Withdraw or correct nominated witness, retain equal-body assertion | Valid history loads; no substitution or applicability claim |
| A11 | Omit nominated witness while equal replacement remains | Closure rejects; equality cannot repair missing provenance |
| A12 | Same/different authority withdrawals in FM and FC | Exact target only; no implicit cross-family revocation |
| A13 | Same-root equal-body and differing-body forks | Multiple tip IDs persist; no automatic convergence |
| A14 | Full/partial same-root convergence | Exact parent/successor/root/ancestry/tips; omitted branch survives |
| A15 | Cross-root and cross-S convergence, duplicate/self/cyclic parents | Typed lineage rejection; iterative traversal |
| A16 | Independent equal/different bodies; inactive disagreeing roots | Separate immutable roots/body groups and live tips; no winner |
| A17 | Selective fork-tip withdrawal, all inactive roots | Exact eligible targets; inactive history retained |
| A18 | Wrong-kind/missing/superseded/already withdrawn target | Typed withdrawal rejection |
| A19 | Successor plus withdrawal in either input order | Entire membership rejects |
| A20 | Historical replay omits withdrawal versus required parent/evidence | Revival only for dependency-closed membership |
| A21 | Identical-looking VCN correction and explicit FC renewal | Old exact pin/body retained; renewed FC has new edition/body |
| A22 | Retained non-current FLD/VPA/VSM/PCN/PIF | Load/replay succeeds; no automatic latest replacement |
| A23 | Historical evidence citation versus typed support | Both structural closures preserved; no evidence activity gate |
| A24 | Registered constraint without VCN versus retained valid VCN DAG | Missing pin rejects; no fabricated zero-tip VCN world |
| A25 | Independent differing global FL root beside valid selected FLD | Structural model still loads; no global consensus admission gate |
| A26 | Hostile model_construct/model_copy, wrong unions, hidden state | Strict reconstruction before callbacks and hashing |
| A27 | Scalar/container/model subclasses, custom mapping/generator/tzinfo | Reject before user callbacks; value-free outer errors |
| A28 | Mutated content with stale ID; coherently rehashed wrong support | Hash rejection versus structural rejection distinguished |
| A29 | Deep/cyclic/shared-DAG input, duplicate JSON keys | Bounded expanded accounting and pre-parse checks |
| A30 | Every record limit at/over, combined budgets, integer/string edges | Inclusive limits and exact typed resource failures |
| A31 | Constructor/validate/JSON/strings/builder/store entry points | No alternate validation bypass; old families unchanged |
| A32 | Filename kind mismatch, extra suffix, symlink, oversized file | New-prefix bounded read and existing integrity/storage rules |
| A33 | Failed append and corrupt sibling on idempotent append | No bytes/revision changes or validation staging |
| A34 | Twelve index mappings and nested tuple ordering | Copied immutable maps; exact ID-valued current-tip tuples |
| A35 | Five hash seeds, input/evidence/parent permutations | Identical canonical/index witnesses without priority |
| A36 | Export prefix and forbidden Slice B surface | Exactly 227; exact 225-prefix digest; only two appended names |
| A37 | Authoritative 36-record/zero-FMA model and old memberships | Exact revision, empty FC indexes, unchanged historical bytes |
| A38 | Protected ledger/settings/artifact inventories | Exact digests; no fixture/artifact-logic mutation |
| A39 | Imports and no evaluation/observation fields | Kernel-only ownership; no upper calls or FC result/status API |
| A40 | Full/affected/base/extras/CAD/PDF/dependency/compile gates | Executed evidence, honest restrictions, exact tested commit |

## 3. Review obligations, not invented test counts

Architecture, backend, test and adversarial reviewers inspect the first green
implementation against the contract and all seven original objectives.
Specifically reject contract theatre: the durable governing relation must
distinguish nominated A from another same-variable constraint without relying
on sample admission, authority rank, timestamps or a status wrapper.

Slice A directly adds declared model meaning and provenance (questions 1/7),
and inspectable dependencies relevant to question 5, not impact propagation.
Question 2's bounded sample answer requires later FC/CN/evidence composition.
No progress is claimed on causal explanation, next-best-test optimization or
planning (questions 3/4/6). Multiple legitimate criteria for one S remain
unsupported, not false. Currentness eligibility, A-violated/B-satisfied consumer
proof and FA cancellation demonstration are Slice B obligations, not missing
Slice A runtime features.

Adversarial review explicitly verifies (1) forged/invalid closure rejects,
(2) retained historical support loads/replays, (3) no Slice B conclusion leaks.
Report real failures and repairs separately from these review judgments.

END OF FC-001 SLICE A ADVERSARIAL ACCEPTANCE MATRIX
