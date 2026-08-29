# BH-001 Slice A — postimplementation architecture and import-isolation review

Date: 2026-08-29
Branch: `bh001`
Accepted base: `46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`
Initial implementation reviewed: `20bd22411a07c9fc2820b5cc15a1ce63df80fd7d`
Repair commit reviewed: `1fb1009` (`fix: repair BH-001 adversarial findings`)
Authority: corrected, owner-accepted BH-001 specification at accepted SHA-256
`2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978`

Review scope: BH-001 Slice A architecture, dependency direction, exact public
surface, record/store boundaries, lifecycle indexes, deterministic material,
historical replay, ledger/revision preservation, and absence of Slice B-D
implementation.

## 1. Verdict

GREEN after bounded repair and re-review.

The initial implementation was correctly limited to the stable behavior
identity and model-kernel record foundation, but independent review reproduced
one deterministic-index defect and confirmed two missing accepted foundation
gates. Repair commit `1fb1009` closes all three without changing the public
record contracts or broadening Slice A:

1. every BH `LoadedModel` mapping now has input-order-independent iteration;
2. the private, non-persisted five-field effective-engineering-body canonical
   projection now exists and is pinned;
3. BH collection validation now runs only after every pre-BH validation path,
   with a mixed-invalid precedence regression.

No remaining architecture or import-isolation blocker was found. This verdict
does not authorize Slice B queries, Slice C evaluation, or Slice D fixtures.

## 2. Authoritative architecture comparison

The repaired implementation conforms to the corrected design rather than any
superseded proposal:

- one opaque `BehaviorAnchor` identity in `backend.system_identity`;
- one permanent, context-free, evidence-bearing `BehaviorRegistration`;
- one exact-context, correctable `BehaviorRuleDeclaration` family;
- one minimal, evidence-free `BehaviorRuleWithdrawal` event;
- the existing model ledger, model store, and `mrv_` revision;
- exactly two distinct, unordered, role-free registered variables;
- exactly one v1 rule family, `exact_numeric_equality`;
- no port, VPA, input/output, direction, flow, influence, causality, control,
  compatibility, safety, diagnosis, or recommendation meaning;
- no evaluator, numeric parser use, source selection, temporal cohort logic,
  or committed demonstration in Slice A.

The implementation does not introduce a behavior-specific ledger, store,
repository, revision, projection, cache, database, or runtime.

## 3. Identity boundary

`backend.system_identity` adds exactly:

```text
BEHAVIOR_ANCHOR_ID_PATTERN = ^bhv_[0-9a-f]{32}$
BehaviorAnchor
mint_behavior_anchor
```

`BehaviorAnchor` carries exactly:

```text
anchor_id
namespace
display_name
role_name
```

It is frozen, extra-forbidden, and configured with
`revalidate_instances="always"`. It contains no owner, participant, rule,
context, evidence, lifecycle, state, port, direction, or causal field.

`mint_behavior_anchor()` produces `bhv_` plus `uuid4().hex` and delegates
human-field validation to the anchor. It performs no I/O or storage access.

The complete `system_identity.__all__` has 13 names: its accepted ten-name
pre-BH surface plus exactly the three names above.

AST inspection found imports only from the standard library, Pydantic, and
`backend.system_identity` itself. No private foreign object is accessed.

## 4. Model-record and canonical boundary

The supported `backend.model_kernel` surface adds exactly five Slice A names:

```text
BehaviorRegistration
BehaviorRuleDeclaration
BehaviorRuleWithdrawal
BehaviorVariableSemanticLock
ExactNumericEqualityRule
```

`backend.model_kernel.__all__` contains 131 names. No BH query result, status,
evaluator, selector, or implementation alias is exported.

The canonical ripple is additive:

```text
bhv_  BehaviorAnchor
brg_  BehaviorRegistration
bhd_  BehaviorRuleDeclaration
bhw_  BehaviorRuleWithdrawal
```

`brg_`, `bhd_`, and `bhw_` are admitted by the model-record and filename
grammars and the `ModelRecord` union. The kind-prefix mapping uses the exact
three prefixes. `brg_` and `bhd_` are citable `ModelRecordEvidence`; `bhw_`
remains uncitable.

The existing public `build_record()` path constructs all three content-derived
record IDs. No BH-specific builder or alternative serialization path exists.
No existing kind-to-prefix mapping or canonical algorithm was changed.

The private `_behavior_effective_body_bytes()` helper serializes exactly:

```text
behavior_anchor_id
context
participant_semantics
rule
evaluation_basis
```

through the existing canonical JSON rules. It excludes record/schema/ID,
evidence, parents, authority, time, note, filename, and append order. It is not
re-exported, persisted, or used to create another identity. Public body groups,
agreement findings, conclusions, and queries remain reserved for Slice B.

## 5. Registration and declaration admission

The repaired store admits a BRG only when:

- its behavior anchor is registered at most once;
- both distinct canonical variable IDs have exact VariableRegistration
  members;
- both owner entity registrations close through the accepted variable
  registration validation;
- its evidence includes citations to both exact VRG record IDs;
- at least one `OwnerDeclarationEvidence` supplies the claim basis;
- every additional model-record citation closes in the selected membership.

Same-owner and cross-owner pairs are both supported only through an explicit
BRG. Ownership never creates behavior.

A BHD is admitted only when:

- its exact behavior registration is present;
- its two variable-keyed locks equal the permanent BRG pair;
- quantity-kind identities match exactly;
- unit identities match exactly;
- observation-role identities may be equal or different;
- evidence cites the exact BRG and contains an owner declaration;
- every additional model-record citation closes;
- every parent has the same behavior anchor and exact `AssertionContext`.

The kernel performs no VSP, VSM, source-interpretation, unit-conversion,
observation, or numeric comparison during admission. These remain independent
future evaluation gates.

Nested behavior anchors, contexts, locks, semantic signatures and tokens,
rules, evidence, and authority objects are serialized and reconstructed before
trust. The focused hostile tests cover both `model_construct` and `model_copy`
substitution and stale content-derived IDs.

## 6. Lifecycle and immutable indexes

The lineage key is exactly:

```text
(behavior_anchor_id, exact AssertionContext)
```

The store retains independent parentless roots, same-root chains and forks,
same-root multi-parent convergence, full ancestry, successors, current tips,
and withdrawals. It rejects cycles, cross-anchor parents, cross-context
parents, and cross-root convergence. It never selects a winner by time,
authority, record ID, filename, or append order.

Multiple active same-root tips remain visible as a conflict foundation even
when their effective engineering bodies are identical. Independent roots
remain distinct so Slice B can group identical active healthy bodies as
corroboration and distinguish different bodies as conflict.

BHW targets only one current, unsuperseded, unwithdrawn BHD tip. Duplicate or
unknown targets fail; a membership cannot both supersede and withdraw the same
target. Selective fork-tip withdrawal is admitted, and replay without a later
successor or withdrawal revives the earlier tip membership-relatively.

The exact twelve BH mappings are present as defensive read-only copies:

```text
behavior_registrations
behavior_registrations_by_anchor
behavior_anchor_ids_by_variable
behavior_rule_declarations
behavior_rule_ids_by_key
behavior_rule_root_by_id
behavior_rule_ancestry_by_id
behavior_rule_superseded_by
current_behavior_rule_tips_by_root
behavior_rule_withdrawals
behavior_rule_withdrawn_by
behavior_rule_withdrawals_by_target
```

A direct forward-versus-reversed collection reproduction confirms identical
ordered mapping items for all twelve mappings. The four initially defective
maps are now explicitly rebuilt by sorted record ID before freezing.

## 7. Validation ordering repair

The initial implementation placed BH validation after entity/variable closure
but before several pre-BH families. That contradicted the accepted stable
collection-validation sequence and could change mixed-invalid failure
precedence.

Repair commit `1fb1009` moves the complete BRG/BHD/DAG/BHW block after all
pre-BH validation and index derivation and before final model-revision
construction. A mixed-invalid regression supplies both:

- a pre-BH value specification referencing an unregistered variable; and
- a BH registration missing its owner-declaration claim basis.

The collection fails at the pre-BH reference gate. Valid memberships retain
the same model revision and record content.

## 8. Import direction and Slice A isolation

AST inspection of every direct import found:

```text
backend.system_identity
  -> standard library + Pydantic + its own package only

backend.model_kernel
  -> standard library + Pydantic + backend.system_identity
     + its own package only
```

No import was found from model kernel to:

```text
backend.behavior_evaluation
backend.model_state
backend.temporal_state
backend.identity_binding
backend.observation_compatibility
backend.semantic_compatibility
backend.constraint_evaluation
backend.source_interpretation
backend.data_sources
backend.structural_evidence
```

No private foreign attribute import was found.

`ModelQueries` has none of the four reserved BH methods. Neither
`backend/behavior_evaluation` nor `tests/behavior_evaluation` exists. There is
no behavior evaluator inside `model_kernel`.

The production diff from accepted base is confined to:

```text
backend/system_identity/anchors.py
backend/system_identity/minting.py
backend/system_identity/__init__.py
backend/system_identity/README.md
backend/model_kernel/contracts.py
backend/model_kernel/canonical.py
backend/model_kernel/store.py
backend/model_kernel/__init__.py
backend/model_kernel/README.md
```

The README changes are documentation. `queries.py`, query-result modules,
model-state, temporal, binding, interpretation, semantic, constraint,
observation, source, structural, and fixture production paths are unchanged.

## 9. Ledger, revision, and artifact preservation

The committed demo remains exactly:

```text
record count: 29
BH records: 0 brg_, 0 bhd_, 0 bhw_
model revision:
mrv_18da4ce963ab5c4b1121cdcc009eaaef4cd1c5c11034f4678c6437361ffd7652
```

All twelve BH indexes are empty and immutable for the current demo and every
explicit pre-BH 9/10/11/14/16/18/28/29-record membership. Historical replay
uses the explicit repository constants; no BH migration or directory-derived
membership exists.

No `models/`, `bindings/`, `interpretations/`, source, temporal, or structural
file differs from the accepted base. The accepted VPA file remains at SHA-256:

```text
95f9390f784600b2f7a17e74a540d6874722039be5d093614c15a716ff08034e
```

The bounded artifact regressions recomputed and verified the accepted VP and
PT artifact byte counts and hashes, including:

```text
VP: a150e10317982ccc6330fa17a921128d3cf31ee9d6b710ef0ad8ea23f63e4ea3
PT: 53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8
```

## 10. Bounded verification evidence

### 10.1 Focused BH Slice A

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_revalidation.py -q
```

Result:

```text
110 passed in 14.91s
```

### 10.2 Complete model-kernel suite

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/model_kernel -q
```

Result:

```text
1052 passed in 79.56s
```

### 10.3 Identity-binding suite

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider tests/identity_binding -q
```

Result:

```text
249 passed in 4.97s
```

### 10.4 Historical, PT, VP, and artifact column

Command:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest -o addopts='' \
  -p no:cacheprovider \
  tests/model_kernel/test_isolation.py \
  tests/model_kernel/test_demo_model.py \
  tests/model_kernel/test_demo_pt001.py \
  tests/model_kernel/test_demo_vp001.py \
  tests/model_state/test_demo_vp001.py -q
```

Result:

```text
40 passed in 36.90s
```

The initial form of this column found one PT status-test boundary problem after
BH status text was appended to `CLAUDE.md`: `1 failed, 39 passed`. The repair
adds the already accepted final VP status marker as the PT section boundary.
The rerun is the 40-pass result above and does not alter PT implementation or
artifact content.

### 10.5 Direct architecture probes

Read-only probes confirmed:

- all twelve BH mapping ordered item sequences match under forward/reversed
  input;
- `model_kernel.__all__` length 131 with exactly five new BH names;
- `system_identity.__all__` length 13 with exactly three new BH names;
- no reserved BH method on `ModelQueries`;
- no evaluator package or BH demo record;
- demo load at exact 29-record revision;
- direct-import graph contains no forbidden upward edge;
- `git diff --check` passes.

These are bounded specialist checks. The lead agent remains responsible for
the complete repository and dual-clean-checkout verification required by the
Slice A plan.

## 11. Findings and disposition

| Finding | Initial result | Repair | Re-review |
|---|---|---|---|
| BH mapping iteration inherited caller order | Reproduced in four mappings | Sort affected maps before freezing; comprehensive twelve-map reverse-input test | Closed |
| Private five-field effective-body projection absent | Source/spec mismatch | Add private canonical helper and exact projection test | Closed |
| BH validation preceded pre-BH paths | Source/spec mismatch | Move BH block after pre-BH validation; add mixed-invalid precedence test | Closed |
| PT final-status test scanned into new BH text | One bounded regression failure | Stop PT status slice at accepted final VP marker | Closed |

No unresolved architecture question remains for Slice A. Slice B remains the
first owner-gated location for public behavior queries, effective-body groups,
corroboration/conflict results, and hostile query-result reconstruction. Slice
C remains the first location for source selection, temporal cohort admission,
CN parser reuse, and exact comparison. Slice D remains the first location for
any committed BH demonstration record.

END OF BH-001 SLICE A ARCHITECTURE REVIEW
