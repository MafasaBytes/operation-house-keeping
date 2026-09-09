# FM-001 Final Owner Acceptance

Date: 2026-09-09

Status: FM-001 complete and owner accepted

## 1. Final owner decision

The owner accepts FM-001 Slice B and completes FM-001 at the exact tested
implementation:

`4d8219d88d3f5f531c1a1cf250b36cb25e001c2f`.

The accepted Slice B completion report is:

`docs/superpowers/reports/2026-09-09-fm001-slice-b-completion-report.md`.

It remains byte-identical at 213 lines and 10,565 UTF-8 bytes, with SHA-256
`f7ce3280a6d1af1682b6ef1139fc8d8d2166c26e56525c703029f03586d8c290`,
ending with `END OF FM-001 SLICE B COMPLETION REPORT`. It was committed
unchanged in the documentation-only checkpoint
`80b1752ca9f639e07b249523e5c48b76d1334dfb`.

The owner accepts the exact 225-name `backend.model_kernel.__all__` surface
and these five read-only `ModelQueries` responsibilities:

1. `flow_measurement_association(flow_anchor_id, variable_anchor_id, participant_port_anchor_id, context, orientation)`;
2. `flow_measurement_associations_for_flow(flow_anchor_id, *, context)`;
3. `flow_measurement_associations_for_variable(variable_anchor_id, *, context)`;
4. `flow_measurement_associations_at_port(participant_port_anchor_id, *, context)`; and
5. `flow_measurement_assertion(record_id)`.

The Slice B addition remains exactly 11 aliases, four nested public rows, and
five outer public results: 20 ordered additions after the accepted 205-name
Slice A prefix. There is no free-function query alias, FM-specific builder,
store, ledger, facade, cache, identity, fixture, or second consumer.

## 2. Accepted implementation lineage

The corrected FM design and repaired Slice A remain owner accepted at exact
tested implementation
`6210d3c250b96f54b764a365cb0a3a988d9bf9f6`. The corrected Slice B public
contract remains owner accepted at
`7bb7db8ec27af74bdd887d763222757c1f1fc821`. The exact final tested runtime
implementation is the commit in Section 1.

The contract authorities at that tested implementation had these accepted
SHA-256 digests:

| Authority | SHA-256 |
| --- | --- |
| Corrected FM synthesis | `6c1061fe63bf77d0975a4854fb0ba9a462cf03bef6af125d91b3ed43433592f7` |
| Slice B implementation plan | `1bf6c8835d799186795478c337e12df9446e0b16d494d412604d07d6717922f2` |
| Slice B adversarial matrix | `6f4d6927b41bb97089c4b4277c064b9cc6371ffa68375b36af36954d617c8200` |

This administrative closeout updates their current-path status wording after
acceptance. Their accepted tested-implementation blobs and digests remain
preserved in Git history and in the unchanged completion report.

## 3. Accepted result semantics

The exact query selects the complete immutable v1 subject: flow, variable,
participant port, exact context, implicit direct-measurement relevance, and
orientation. The three reverse queries use their dedicated flow/context,
variable/context, and port/context indexes and emit one complete entry per
subject. Assertion lookup distinguishes not-found, positive, and withdrawal
shapes.

Each outer result carries one complete, authoritatively reconstructed
`ModelQueryMaterial` exactly once. Nested rows carry strict indices and
derived disclosures. Roots, effective-body groups, current assertions,
agreement findings, support lifecycle, lineage health, and current alignment
remain explicit and deterministic. No conflicted or inactive root is hidden,
and no record ID, root, body, authority, or timestamp selects a winner.

Every positive effective-body group and found positive assertion carries
exactly six support rows in FRG/VRG/PRG/FLD/VPA/VSM order. Registration,
declaration presence, conclusion, support activity, support health, and
current alignment remain separate axes.

## 4. Accepted verification

The owner accepts the verification recorded against the exact tested
implementation:

- Slice B contract and adversarial gate: 43 passed in 27.58 seconds;
- uninterrupted working repository: 3,896 passed in 2,084.21 seconds;
- fresh base-only checkout: 3,860 passed, 35 expected optional skips, and one
  sandbox-denied loopback setup, with the exact loopback rerun passing and
  reconciling 3,861 runnable passes;
- fresh all-extras checkout: 3,895 passed and one sandbox-denied loopback
  setup, with the exact loopback rerun passing and reconciling all 3,896
  runnable tests;
- explicit CAD/STEP/PDF gate: 120 passed in 48.36 seconds;
- dependency checks and backend compilation passed in working, base-only,
  and all-extras environments; and
- whitespace and clean-checkout state checks passed.

The deterministic FM witness remained identical under forward and reverse
construction and five hash seeds: 245,676 bytes at SHA-256
`b65567aae97c7dc3c6913a12ab52c78e329a99fedcb40bfa1b9bc36f69a40839`.

Accepted lower material remained 24,766 bytes at SHA-256
`ba9e924ab556b4b5671e35e6c0fb000bcfcfe864e328d3c7327a9c93b7fd9da7`.
The accepted TA canonical result remained 195,429 bytes at SHA-256
`1583864df00ce91f20f22104266111efc65f41f6045d16bacd9d5228d95d0e97`.

## 5. Preserved authoritative state

The authoritative model remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
Its ledger inventory aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
Family counts remain FRG/FLD/FLW `1/1/0`, TRG/TRD/TRW `0/0/0`, and FMA/FMW
`0/0`.

The frozen FL disclosure remains 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
The ignored owner-local `.claude/settings.local.json` remains unchanged and
uncommitted at SHA-256
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

This acceptance changes no runtime code, test, dependency, fixture, identity,
record, ledger membership, canonical byte, index, historical revision,
accepted artifact, or artifact-generation logic.

## 6. Intentional truth boundary

FM-001 records and discloses an authority's model declaration that one
registered variable has direct-measurement relevance to one registered
logical flow at one registered participant port, under exact context and
orientation and with exact same-revision support.

It does not establish that an observation occurred at the port, that a sensor
is physically located there, that a variable currently has a value, or that a
logical or physical flow is active, observed, measured, continuous,
conserved, balanced, causal, correct, safe, or occurred. It performs no
evidence selection, observation read, temporal query, value evaluation, sign
normalization, unit conversion, aggregation, conservation calculation, flow
assessment, diagnosis, or recommendation.

## 7. Closeout boundary

FM-001 has no Slice C and no demonstration. FA-001 remains separate and
unauthorized. This acceptance opens no successor milestone and authorizes no
record append, fixture, demonstration, assessment, occurrence/history work,
push, merge, or history rewrite.

END OF FM-001 FINAL OWNER ACCEPTANCE
