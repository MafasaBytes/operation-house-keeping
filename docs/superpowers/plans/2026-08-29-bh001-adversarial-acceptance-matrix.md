# BH-001 — Adversarial Acceptance Matrix

Status: BH-001 Slices A, B, and C are owner accepted; Slice C is accepted at
`8002e6ae7ca85ab1c7e7ccf25a5ea504ff971521`. The owner-resolved Slice D
public-variable-minter repair and disposable pre-append contract are complete.
The exact candidate identities, canonical records, 32-record revision, and
122406-byte artifact are owner approved; the bounded authoritative append and
final verification are authorized.

Authoritative specification:
`docs/superpowers/specs/2026-08-29-bh001-explicit-behavior-and-evidence-gated-evaluation-design.md`
at SHA-256
`2efdf75850d0e003e8524ac9603f5c3f2eedb769069f558e39029c952b2db978`.

Accepted base: `main` at
`46c04ed6f6f09b254b2f52f07611e2efbdd1d4f6`.

## 1. Scope and evidence protocol

Slice A implements only stable behavior identity, BRG/BHD/BHW record
contracts, canonical identity, model-store admission, lifecycle indexes,
withdrawal, replay, builders, exports, tests, and documentation.

Slice A adds no query method or result, evaluator, observation selection,
numeric comparison, state composition, fixture record, artifact, ledger,
store, cache, projection, or revision axis.

Every attack below must fail at the public or authoritative collection
boundary with a typed error. Failed append must be atomic. Valid counterexamples
must remain valid and deterministic. A passing result is evidence only for the
named row; it must not be generalized into behavior, causality, or real-machine
truth.

## 2. Red-before evidence

The first public-contract reproduction against the unmodified Slice A
production baseline was:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_canonical.py -q

66 failed in 8.10s
```

The complete initial Slice A adversarial reproduction was:

```text
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest \
  -o addopts='' -p no:cacheprovider \
  tests/identity_binding/test_behavior_anchor.py \
  tests/model_kernel/test_behavior_records.py \
  tests/model_kernel/test_behavior_canonical.py \
  tests/model_kernel/test_behavior_store.py \
  tests/model_kernel/test_behavior_revalidation.py -q

103 failed, 4 passed in 25.07s
```

There were zero collection errors. An earlier complete pass before the final
withdrawal-target, all-tips-withdrawn, and crafted-load evidence-closure
attacks recorded `97 failed, 4 passed in 18.47s`; the final frozen red suite is
the 103-failure result above. The failures arose from the deliberately
absent BH anchor, contracts, prefixes, evidence arms, indexes, and store
lifecycle support. The four passing tests were pre-existing preservation and
Slice A isolation gates.

## 3. Identity and public surface

| ID | Attack or assertion | Required result |
|---|---|---|
| A01 | Malformed `bhv_`: separator, case, hex, prefix, short, or long | Pydantic rejection |
| A02 | `BehaviorAnchor` carries owner, participant, context, rule, port, direction, or evidence | Extra-forbid rejection |
| A03 | Frozen anchor mutation | Rejected |
| A04 | `model_construct` or `model_copy` forged anchor | Full-instance revalidation rejects |
| A05 | Public minter called repeatedly | Unique RFC-4122 UUID4 `bhv_` values |
| A06 | Rename/display-role change | Same supplied opaque identity; no matching inference |
| A07 | `system_identity.__all__` | Exact Slice A surface only |
| A08 | `model_kernel.__all__` | Exact five BH record/value names added; no query/evaluator names |
| A09 | Alternate aliases or deprecated BH names | Absent |

## 4. Record contracts and exclusions

| ID | Attack or assertion | Required result |
|---|---|---|
| B01 | BRG field set/discriminator/version | Exact permanent registration contract |
| B02 | BHD field set/discriminator/version | Exact contextual declaration contract |
| B03 | BHW field set/discriminator/version | Exact minimal withdrawal event |
| B04 | Lock and rule field sets | Variable-keyed signature lock; kind-only rule |
| B05 | BRG pair empty, singleton, duplicate, triple, or wrong anchor kind | Typed rejection |
| B06 | BRG pair reversed | Same canonical tuple, bytes, and ID |
| B07 | BHD locks missing, duplicate, wrong participant, or reversed | Exact pair required; reversed valid input canonicalizes |
| B08 | Pair quantity-kind identity differs | Rejected |
| B09 | Pair unit identity differs | Rejected |
| B10 | Pair observation roles differ | Accepted and remain variable-keyed |
| B11 | Rule family or rule kind other than `exact_numeric_equality` | Rejected |
| B12 | Evaluation basis other than `same_acquisition_cohort` | Rejected |
| B13 | Coefficient, offset, tolerance, expression, operator, direction, role, result, or verdict field | Rejected |
| B14 | Port, VPA, input, output, flow, cause, control, influence, safety, or state field | Rejected |
| B15 | BRG context, parent, withdrawal, owner, or lifecycle field | Rejected |
| B16 | BHW evidence, context, parent, outcome, replacement, reason, or negative claim | Rejected |

## 5. Canonical identity and nested trust

| ID | Attack or assertion | Required result |
|---|---|---|
| C01 | Exact BRG golden vector | `brg_ecd5a9b669f91dca639fde20202ce4f3c4ff17006d7f0ffd23f09ed44f1f9e3e` |
| C02 | Exact BHD golden vector | `bhd_9e3af9219521d1b3c5dfd5d41ae359dc8d3fb4c5db4b002586998e52f0a823eb` |
| C03 | Exact BHW golden vector | `bhw_4c2456b2a6473f6a37c47b9aadedc10b1a8610c80e6650ba70cdbd7b2dd938f6` |
| C04 | Malformed `brg_`/`bhd_`/`bhw_` ID or filename | Typed rejection |
| C05 | Record kind/prefix substitution | Union rejection |
| C06 | Mutated content under stale record ID | Hash rejection |
| C07 | Filename/content identity mismatch | Typed load failure |
| C08 | Evidence, lock, or parent input reversed | Identical canonical bytes and ID |
| C09 | Duplicate parent | Rejected, never silently deduplicated |
| C10 | Self-parent or wrong-kind parent | Rejected |
| C11 | Forged nested context, lock, signature, rule, evidence, or authority | Serialized reconstruction rejects |
| C12 | BRG and BHD as `ModelRecordEvidence` | Structurally citable; membership closure enforced |
| C13 | BHW as evidence | Structurally uncitable |
| C14 | Existing record kind canonical bytes or hash changes | Preservation failure |

The initial handwritten C01-C03 placeholders used variable-registration
citations that were not produced by the matrix's own frozen synthetic
builders. The red-first reproduction exposed that contradiction before the
golden column could pass. The vectors above are the measured public-builder
identities over the fully pinned canonical inputs in
`tests/model_kernel/bh001_slice_a_helpers.py`; the tests pin the complete
canonical bytes as well as these IDs. No existing record vector changed.

## 6. Registration and declaration admission

| ID | Attack or assertion | Required result |
|---|---|---|
| D01 | Either participant VRG absent | Atomic reference failure |
| D02 | Either variable owner registration absent | Reference failure on append/load/replay |
| D03 | Same-owner pair with explicit valid BRG | Accepted |
| D04 | Cross-owner pair with explicit valid BRG | Accepted; ownership never inferred as behavior |
| D05 | Second BRG for one `bhv_` | Permanent-identity duplicate failure |
| D06 | Missing exact citation to either VRG | Registration admission failure |
| D07 | No `OwnerDeclarationEvidence` in BRG | Registration admission failure |
| D08 | Additional missing model-record evidence | Uniform evidence-closure failure |
| D09 | Additional foreign evidence arm | Preserved as citation; no foreign inference |
| D10 | BHD without exact BRG | Reference failure |
| D11 | BHD locks differ from registered variable pair | Declaration admission failure |
| D12 | BHD lacks exact BRG citation | Declaration admission failure |
| D13 | BHD lacks claim-bearing owner declaration | Declaration admission failure |
| D14 | BHD current VSP/VSM absent | Store admission remains valid; evaluation is later |
| D15 | Same anchor in different exact contexts | Separate valid lineage keys |

## 7. Correction DAG, independent roots, and effective bodies

| ID | Attack or assertion | Required result |
|---|---|---|
| E01 | Missing or wrong-kind parent | Reference failure |
| E02 | Parent changes behavior anchor | Lineage failure |
| E03 | Parent changes exact context | Lineage failure |
| E04 | Crafted cycle with hash checking disabled | Iterative lineage rejection |
| E05 | One correction chain | Root/ancestry/successor indexes exact |
| E06 | Same-root fork with identical engineering bodies | Both current tips retained; conflict is not hidden |
| E07 | Same-root fork with differing bodies | Both current tips retained |
| E08 | Partial convergence | Uncovered sibling remains current |
| E09 | Full same-root convergence | One current merged tip |
| E10 | Parents derived from different roots | Cross-root convergence rejected |
| E11 | Independent roots with identical projected body but different evidence/audit fields | Separate roots admitted for later corroboration disclosure |
| E12 | Independent roots with different projected bodies | Separate roots admitted for later conflict disclosure |
| E13 | Evidence, authority, timestamp, note, filename, ID, or append order differs | Does not alter effective engineering body |
| E14 | Engineering context, keyed lock, rule, or basis differs | Effective body differs |
| E15 | Timestamp, authority, ID, or order used as winner | Test failure |

Store indexes do not persist an effective-body digest or winner. Slice B must
derive canonical body groups from the validated Slice A roots and tips.

## 8. Withdrawal and historical revival

| ID | Attack or assertion | Required result |
|---|---|---|
| F01 | Unknown or non-BHD target | Typed failure |
| F02 | Superseded/non-tip target | Withdrawal failure |
| F03 | Already-withdrawn target or duplicate BHW | Withdrawal failure |
| F04 | Target has both successor and withdrawal | Membership rejected |
| F05 | Correction cites a withdrawn target | Membership rejected |
| F06 | Selective withdrawal of one fork tip | Valid; sibling remains current |
| F07 | Every root tip withdrawn | Root remains indexed with empty current tips |
| F08 | Replay omits later BHW | Target revives membership-relatively |
| F09 | Replay omits later successor | Parent revives membership-relatively |
| F10 | Earlier event timestamp | Does not alter structural withdrawal truth |
| F11 | BHW interpreted as false/impossible/stopped behavior | Prohibited meaning |

## 9. Immutable indexes, determinism, and persistence

| ID | Attack or assertion | Required result |
|---|---|---|
| G01 | Any required BRG/BHD/BHW index member absent | Exact index test fails |
| G02 | Mapping mutation | `TypeError`; defensive immutable copy |
| G03 | Input mapping reversed | Same indexes and revision |
| G04 | Python hash seed varied | Byte-identical deterministic projection |
| G05 | Record iteration or file enumeration order varied | Canonical record-ID ordering |
| G06 | Hostile nested record written directly to disk | Typed all-or-nothing load failure |
| G07 | Failed prospective append | No new file and prior revision unchanged |
| G08 | Replay omits evidence or parent dependency | Reference failure |
| G09 | Root, ancestry, successors, or tips forged by ordering | Recomputed result differs; attack fails |
| G10 | New behavior-specific ledger, store, cache, or revision | Architecture failure |

Required Slice A indexes are exactly those specified in Section 20 of the
authoritative design. Effective-body groups are deliberately not persisted.

## 10. Historical, byte, and architecture preservation

| ID | Attack or assertion | Required result |
|---|---|---|
| H01 | Replay explicit 9/10/11/14/16/18/28/29 memberships | Exact accepted revisions and counts |
| H02 | Any pre-BH replay has a nonempty BH index | Failure |
| H03 | Current committed model count or revision changes | Failure; remains 29 at accepted revision |
| H04 | Any committed `brg_`, `bhd_`, or `bhw_` appears | Slice A failure |
| H05 | Any of 29 accepted model record bytes changes | SHA-256 freeze failure |
| H06 | PT artifact changes | Exact byte/size/hash failure |
| H07 | VP artifact changes | Exact byte/size/hash failure |
| H08 | Kernel imports state, temporal, binding, ES, CN, interpretation, source, structural, or BH evaluator | AST isolation failure |
| H09 | `backend/behavior_evaluation` exists | Slice C boundary failure |
| H10 | Any BH `ModelQueries` method or result exists | Slice B boundary failure |
| H11 | Observation selection or numeric comparison exists | Slice C boundary failure |
| H12 | Demo fixture or binding ledger changes | Slice D boundary failure |
| H13 | `.claude/settings.local.json` changes | Scope failure |

## 11. Non-inference and vocabulary gates

No BH record may be created from matching names, ownership, hierarchy, CAD,
geometry, PIF direction, PCN topology, PCM compatibility, VPA association,
semantic compatibility, constraint results, observation availability, temporal
correlation, or value equality.

Slice A public fields contain no `input`, `output`, `port`, `VPA`, `signal`,
`flow`, `direction`, `cause`, `control`, `influence`, `compatible`, `safe`,
`state`, `result`, `equal`, or `different` outcome. `exact_numeric_equality` is
the declared rule family, not an evaluated result.

## 12. Verification columns required for Slice A completion

The completion report must record exact counts for:

1. focused BH Slice A tests;
2. complete identity-binding and system-identity affected tests;
3. complete model-kernel tests;
4. VP, PT, CN, ES, VS, and VM regressions;
5. architecture/import-isolation tests;
6. historical replay and hostile-revalidation tests;
7. the complete repository suite;
8. a fresh base-only checkout;
9. a fresh all-extras checkout;
10. focused OCP/STEP tests;
11. focused PDF tests;
12. backend compilation;
13. `git diff --check`;
14. branch topology, remote status, and clean worktree.

Any genuine defect discovered after first green retains its minimal red
reproduction, repair, and fixed-after result. Sandbox-denied loopback tests are
reported separately and rerun with the required permission.

## 13. Slice stop gate

Slice A is complete only when every A-H row applicable to identity and kernel
records is green, every preservation hash is unchanged, specialist findings
are reconciled, the completion report is persisted, and the work stops for
owner acceptance.

Owner resolution: add the narrowly scoped public `mint_variable_anchor()` API, commit it green before candidate allocation, then resume only the disposable pre-append rehearsal. Its exact red-first and preservation gates continue in
`docs/superpowers/plans/2026-08-30-bh001-slice-d-preappend-acceptance-matrix.md`.
No candidate may be minted before the minter commit is green. Thereafter mint
each candidate with one invocation of its public minter, freeze it, never invoke
either minter again, and reuse it in both independent disposable ledger roots.
Each ledger has one behavior lineage root. Historically, this matrix did not
authorize the Slice D fixture append. Owner approval now authorizes only the
exact contract committed at `0905de0`: approved report SHA-256
`0a559255359440f54f370eaf11645122089d4c0744e537c9446e20c12ffd4778`,
unchanged manifest SHA-256
`8524e9219ee7e1e452d7390f00df99c790bc8d91068e04fc4ec4f7463f75ea07`,
revision
`mrv_d7d9b3918eb3f04157fb862164fe1d5fb17b4ef18d627fb89ff9bc429a94506b`,
and 122406-byte artifact SHA-256
`4c29928156ceb2e1947473039bc20d07af4f3ff9e25a1b664b17c3e96ac415b3`.
A push, merge, rebase, reset, cherry-pick, amend, or history rewrite remains
prohibited. Final BH-001 owner acceptance remains a separate gate.

END OF BH-001 SLICE A ADVERSARIAL ACCEPTANCE MATRIX
