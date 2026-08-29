# VP-001 Slice C — implementation plan

Status: VP-001 Slices A, B, and C are owner accepted. Slice D is implemented
and adversarially reviewed; awaiting final owner acceptance.
The accepted Slice B base is
`81179700513bb671cf9955c6a5d7163e3bcc7e1b`.

## Decision being validated

Slice C adds one read-only composition to the existing `backend.model_state`
facade. It presents an exact-context, model-revision-relative
`VariablePortAssociationResult` beside the independently computed
`VariableStateResult` for the same variable and an explicit UTC cutoff.

The composition does not say that an observation occurred at, was produced by,
was consumed by, or travelled through the port. Association status is derived
only from the model association result. Variable state remains attached only to
the variable through the accepted binding and temporal pipeline.
Displaying variable state beside a port is not a claim that an observation
occurred at the port.

## Frozen boundary

Permitted production changes are limited to:

- `backend/model_state/contracts.py`;
- `backend/model_state/facade.py`;
- `backend/model_state/__init__.py`.

No model-kernel contract, query, canonical rule, store, index, system identity,
binding, temporal projection, source layer, ledger, fixture, or artifact may
change. No new runtime module, store, ledger, cache, database, or revision type
is introduced.

## Gate 0 — accepted base and preservation freeze

1. Verify `vp001` at the accepted Slice B HEAD with a clean worktree.
2. Record Slice B owner acceptance in its own administrative commit.
3. Pin the committed demo at 28 records, zero `vpa_`, zero `vpw_`, revision
   `mrv_c6244b6dc41de599de9894b55f4064e41ba5260e7d00f50bffc1e1e63da560a2`,
   and PT artifact SHA-256
   `53dd32846956d10331dfca8fc370ef7d7019325904a062db5f037605aa4cf3d8`.
4. Preserve every explicit historical model membership and revision.

## Gate 1 — red-first public contract

Add focused tests that require exactly:

```python
AssociatedPortVariableStateStatus = Literal[
    "endpoint_not_admitted",
    "association_not_declared",
    "association_conflicted",
    "association_inactive",
    "associated",
]
```

and one frozen, extra-forbidden result with exactly these fields:

```text
variable_anchor_id
port_anchor_id
context
as_of
status
association
variable_state
```

Pin the single accepted `ModelStateQueries.associated_port_variable_state`
signature, exact return annotation, exact package exports, and absence of
alternate names or implication-bearing fields.

## Gate 2 — red-first composition semantics

Use disposable public stores only. Build one same-owner variable with separate
ports whose exact-context association histories produce:

- endpoint not admitted;
- registered same-owner but not declared;
- inactive roots only;
- one forked conflicted root;
- one or more healthy active roots;
- a healthy root plus a conflicted root.

Use the same resolver, temporal projection, variable, cutoff, requested entity,
and source selector across statuses. Require the nested serialized
`VariableStateResult` to equal a direct `variable_state()` result and to remain
unchanged when only the association subject changes.

Add separate tests for all four endpoint-admission states and registered
different-owner admission. Add explicit historical-model replay, context-only
changes, cutoff-only changes, selector passthrough, requested-entity
passthrough, evidence-in-limbo for an unregistered variable, and propagation of
typed temporal failures.

## Gate 3 — red-first authoritative revalidation

Attack every outer field and both nested results through plain payload mutation,
`model_copy`, and `model_construct`. Cover:

- status, variable, port, context, and cutoff substitution;
- mixed model revisions and mismatched request echoes;
- forged association endpoint, owner, conclusion, summary, roots, tips,
  withdrawals, material order, membership, and stale content IDs;
- forged variable-state membership, registrations, owner, requested entity,
  binding revision, candidate declaration, resolution, attachment, and cutoff;
- naive cutoff, boolean/coercion payloads, and forbidden extra fields.

The outer contract must reconstruct both nested results from serialized content,
require one exact model revision, require exact echoes and UTC cutoff, recompute
the outer status exclusively from the association, and access no store or
filesystem.

## Gate 4 — smallest production implementation

1. Add the exact alias and result contract to `model_state/contracts.py` using
   full-instance reconstruction and existing pattern/context/time contracts.
2. Add local typed port/context input guards to `ModelStateQueries`.
3. Add exactly one facade method. Normalize inputs, call the public
   `ModelQueries.variable_port_association()`, always call the existing
   `variable_state()`, derive the outer status, and construct the result.
4. Export only the alias and result from `backend.model_state`.
5. Preserve upstream typed errors; create no lower-layer surrogate status.

## Gate 5 — architecture and non-inference

Extend AST tests to prove:

- no store construction, writes, path literals, `sqlite3`, dynamic imports, or
  private access to foreign objects;
- imports remain within system identity, model kernel, identity binding,
  temporal state, model state, Pydantic, and the standard library;
- model kernel has no upward import;
- no data-source, interpretation, compatibility, constraint, CAD, or PDF
  dependency;
- no traversal or hidden model selection by cutoff;
- no field or alias suggesting observation at a port, value at a port, signal,
  direction, flow, causality, influence, control, compatibility, health, safety,
  behavior, or current operation.

## Gate 6 — independent adversarial review

The software architect reviews dependency direction and provenance separation.
The backend engineer reviews public composition and validation. The test
engineer attacks state independence and every status before first green. After
first green, the code reviewer independently reproduces nested-instance,
revision-mixing, cutoff/context, store-isolation, and preservation attacks.
Every genuine defect retains red-before/fixed-after evidence.

## Gate 7 — verification

Run, in order:

1. focused Slice C tests;
2. all `tests/model_state/`;
3. complete VP Slice A+B regressions;
4. complete model-kernel tests;
5. identity-binding and temporal-state suites;
6. architecture/import-isolation suites;
7. complete repository suite with the sandbox-denied loopback case reported and
   run separately with permission;
8. fresh base-only clean checkout;
9. fresh all-extras clean checkout;
10. focused OCP/STEP and PDF suites;
11. backend compilation and `git diff --check`.

At the Slice C gate, both clean checkouts reproduced the then-unchanged demo
revision and PT artifact hash.

## Reviewable commits

1. `docs: record VP-001 Slice B acceptance`
2. `docs: add VP-001 Slice C implementation plan`
3. `test: add VP-001 Slice C composition reds`
4. `feat: compose associated port variable state`
5. bounded test or validation repair commits for genuine review findings
6. `docs: record VP-001 Slice C review status`

## Historical Slice C stop condition — satisfied

Slice C stopped after it was implemented, independently adversarially reviewed,
dual-clean-checkout verified, committed, and accepted by the owner. The Slice D
VPA was not appended until the later owner authorization. No behavior, flow,
control, causality, compatibility, safety, or state-at-port work began.
