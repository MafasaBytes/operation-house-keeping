# BH-001 Slice A backend implementation review

Date: 2026-08-29
Branch: `bh001`
Reviewed implementation commit: `20bd224` (`feat: add BH-001 identity and record foundation`)
Authority: corrected final BH-001 specification and the owner-accepted Slice A plan
Review scope: record contracts, hostile reconstruction, canonical identity,
store admission, evidence closure, lifecycle, withdrawal, indexes,
determinism, import boundaries, and Slice A exclusions

## 1. Outcome

The core Slice A implementation is structurally sound, and the existing
focused BH tests pass. The review nevertheless found three specification
defects that must be repaired before Slice A can be called complete:

1. four public `LoadedModel` BH mappings expose caller insertion order;
2. the required private effective-engineering-body canonical projection is
   absent;
3. BH validation runs before several pre-BH validation paths, contrary to the
   accepted stable collection-validation order.

The first defect has a direct executable reproduction. The second and third
are direct mismatches between the accepted normative plan/specification and
the committed source. None requires broadening Slice A.

## 2. Review basis and repository boundary

The implementation was compared with:

- `docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`, especially Sections 5, 6, 9, 10, 20, 21, 22, 23, and 26.1;
- `docs/superpowers/plans/2026-08-29-bh001-slice-a-implementation-plan.md`, especially Gates 3 through 8;
- `docs/superpowers/plans/2026-08-29-bh001-adversarial-acceptance-matrix.md`, especially rows C, D, E, F, G, and H;
- ADR-0015;
- the existing VP/PT/CN implementation conventions used by
  `backend/model_kernel/contracts.py`, `canonical.py`, and `store.py`.

No production code, tests, fixtures, ledgers, or existing documentation was
modified by this review. Only this report was added.

## 3. Finding BHR-A-01 — BH mapping iteration is input-order dependent

Severity: high for the accepted deterministic public material contract.

The authoritative specification requires every BH mapping to be a defensive
immutable copy and requires mapping-key iteration to be deterministic. The
Slice A plan repeats that the exact `LoadedModel` mappings are deterministic.

The committed implementation returns these mappings without canonicalizing
their key insertion order:

- `behavior_registrations`;
- `behavior_rule_withdrawals`;
- `behavior_rule_superseded_by`;
- `behavior_rule_withdrawn_by`.

`behavior_registrations` and `behavior_rule_withdrawals` inherit bucket order
from the caller-supplied record mapping. `_pt_dag_indexes()` initializes the
successor mapping by iterating its input mapping, so
`behavior_rule_superseded_by` inherits the same order.
`behavior_rule_withdrawn_by` is then constructed by iterating the unsorted
declaration bucket. `MappingProxyType(dict(mapping))` makes each mapping
immutable, but it preserves this noncanonical insertion order.

### 3.1 Reproduction

Using two registrations and two withdrawals, validating the same membership
in forward and reverse insertion order produced:

```text
behavior_registrations       ... False
behavior_rule_withdrawals    ... False
```

Using one fork and two withdrawals produced:

```text
behavior_rule_superseded_by  ... False
behavior_rule_withdrawn_by   ... False
```

The exact bounded reproduction used public test builders and
`validate_record_collection()` twice, once over the original tuple and once
over `reversed(items)`, then compared `tuple(mapping)` for every required BH
index.

The existing determinism test does not catch the defect because its fixture
has only one BRG and one BHW and its serialized projection omits
`behavior_rule_superseded_by` and `behavior_rule_withdrawn_by`.

### 3.2 Required repair

Add a red regression containing at least two registrations, multiple
declarations, and multiple withdrawals. Assert identical key iteration and
values for every required BH mapping under forward/reverse input and multiple
hash seeds. Canonicalize each affected mapping by the accepted record-ID/key
ordering before freezing it. Do not change tuple meaning, record identity, or
any pre-BH mapping contract.

## 4. Finding BHR-A-02 — effective-body projection helper is absent

Severity: high for the owner-accepted Slice A/B contract boundary.

The accepted Slice A plan, Gate 5 Section 7.2, explicitly requires one private
canonical effective-body projection helper and a pinning test. It must include
exactly:

```text
behavior_anchor_id
context
participant_semantics
rule
evaluation_basis
```

It must exclude record kind, schema, record ID, evidence, parents, authority,
recorded time, note, filename, and append order. It must serialize through the
accepted canonical JSON rules. It is private, unpersisted, and not exported;
Slice B will use it to derive effective-body groups without inventing another
identity rule.

No effective-body function exists in `backend/model_kernel`, and no test pins
the exact projection or proves that evidence/audit differences preserve its
bytes while an engineering-field difference changes them. The current tests
only prove that independent roots remain separate and that whole-record IDs
change when audit fields change. Whole-record identity is deliberately not the
effective-body comparison contract.

### 4.1 Required repair

Add the private helper using the existing canonical JSON implementation, and
add exact positive and negative vectors:

- evidence, authority, time, note, ID, parent, and caller order differences
  preserve effective-body bytes;
- context, participant-keyed lock, rule, or evaluation-basis differences
  change them;
- reordered valid participant locks normalize to identical bytes;
- the helper is neither persisted nor exported.

This remains Slice A foundation work. It must not add public query results,
body groups, conclusions, or an evaluator.

## 5. Finding BHR-A-03 — BH validation precedes pre-BH validation paths

Severity: medium for deterministic failure precedence and preservation.

The authoritative specification defines this stable collection-validation
order:

1. validate and reconstruct the collection;
2. bucket records;
3. validate every pre-BH record kind through its unchanged path;
4. then validate BRG, BHD, DAG, BHW, tips, and BH indexes.

The committed BH block begins immediately after entity and variable
registration validation and before value-specification, semantic,
constraint, PT, VP, and relationship validation. Therefore a mixed hostile
membership can surface a BH error before a pre-BH error that the accepted
ordering requires to be evaluated first. The individual pre-BH algorithms may
be textually unchanged, but their collection-level failure precedence is not.

### 5.1 Required repair

Move or orchestrate BH validation after all pre-BH validation paths while
retaining its dependency on the already-derived entity and variable
registration indexes. Add a mixed-invalid regression that proves the accepted
stable order. The repair must not change validation outcomes for valid
memberships, existing record hashes, or historical revisions.

## 6. Green findings

The review found the following implementation areas consistent with the
accepted Slice A design:

- `BehaviorAnchor` is frozen, extra-forbidden, always revalidated, role-free,
  and minted as an opaque UUID4-backed `bhv_` identity.
- BRG fixes exactly two distinct canonical unordered variable IDs and the
  sole `exact_numeric_equality` family without context or lifecycle.
- BHD carries exact context, two variable-keyed semantic locks, the minimal
  rule body, `same_acquisition_cohort`, canonical evidence, and canonical
  BHD-only parents.
- Quantity-kind and unit identities must match exactly, while observation
  roles may differ.
- BHW is a minimal uncitable event targeting only a BHD identity.
- BRG admission requires both registered variables, owner-entity closure,
  both exact VRG citations, an owner declaration, and closure for additional
  model-record citations. Explicit cross-owner registration remains allowed.
- BHD admission requires the exact BRG, exact participant-lock pair, exact BRG
  citation, owner declaration, evidence closure, and same-anchor/context
  lineage.
- Nested anchor, context, semantic signature, rule, evidence, and authority
  material is serialized and reconstructed at public trust boundaries.
- Same-root forks are retained, convergence is restricted to one root,
  cross-root convergence and cycles fail, and no winner is selected.
- Withdrawals reject unknown, superseded, and already-withdrawn targets;
  selective fork-tip withdrawal and membership-relative replay revival work.
- Canonical prefixes, filename grammar, discriminated record union, builder
  path, and evidence citation arms are additive; BHW remains uncitable.
- No Slice B query, Slice C evaluator, Slice D fixture, port/VPA semantic,
  observation selection, or numeric comparison was introduced.
- Kernel imports remain downward-only.

## 7. Focused verification evidence

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
107 passed in 19.38s
```

This green result confirms the implemented paths but does not negate the
reproduced determinism gap or the two missing normative gates.

## 8. Repair and rereview gate

Before backend review can be green:

1. add red tests for all four order-dependent mappings;
2. canonicalize every BH mapping's public iteration order;
3. implement and pin the private five-field effective-body bytes helper;
4. restore the accepted pre-BH-before-BH collection-validation ordering;
5. rerun focused BH tests plus model-kernel and historical preservation tests;
6. rerun this independent backend review against the repaired commit.

No finding authorizes Slice B queries, Slice C evaluation, Slice D fixtures,
or any ledger mutation.

END OF BH-001 SLICE A BACKEND REVIEW
