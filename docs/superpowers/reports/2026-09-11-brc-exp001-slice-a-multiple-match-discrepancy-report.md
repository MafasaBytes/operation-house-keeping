# BRC-EXP-001 Slice A final preexecution closure: not ready

## 1. Checkpoint and verdict

Branch: `brc-exp001`. Starting and ending HEAD:
`af16e925a2df80f84d5cdf5c1c6e97cf3172fea0`.
Tracked worktree is unchanged. The ten existing ordinary untracked owner-gate
artifacts were treated as read-only. This report is the only new artifact.

Verdict: **not ready**. The requested honest EA ambiguity/multiple-match parent
cannot be supplied through the inspected existing public producer chain. Its
multiple-match branch is defensively representable, but the public discovery
and observation producers prevent the duplicate matching locator rows needed
to reach it. Structural acceptance of manually duplicated rows is not evidence
that an honest disposable world produced them.

This is a preexecution discrepancy record, not a Slice A completion report.
No minimax procedure, ranking driver, preference result, or Mode B derivation
was run or produced. No accepted bytes were changed. Preparation stops at the
owner-dependent distinction described below; it does not silently replace the
requested parent with a different kind of ambiguity.

## 2. Frozen-input verification

All following SHA-256 values were recomputed from local bytes and matched.
JSON artifacts additionally matched compact sorted-key UTF-8 serialization,
with no trailing newline. Paths in this table are relative to this report.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| [Operational cohort](2026-09-11-brc-exp001-slice-a-operational-cohort.json) | 669382 | `2db52219a67285f67169413e12d9d016bff067c18da2e835f6ded65ba0567866` |
| [Cohort manifest](2026-09-11-brc-exp001-slice-a-operational-cohort-manifest.json) | 1399105 | `e1be77be0bb5c9229d5a073e8adafd6b1448487f590b04ffedebbf8ff4cb4f8a` |
| [Resource guards](2026-09-11-brc-exp001-slice-a-resource-guards.json) | 368740 | `f55198cb8a57378d51765f7eb5932b9137666bcefe9f5da9caa2b12c5134ea15` |
| [Guard manifest](2026-09-11-brc-exp001-slice-a-resource-guards-manifest.json) | 93619 | `c401e5aa04c79dd49c980b4c4508794deaad55a94f167f86db955cd00c294f1c` |
| [Approved rehearsal](2026-09-11-brc-exp001-slice-a-redesigned-preexecution-rehearsal-report.md) | 28764 | `7cec799a730584d315242db964c669629b1914826dcba36f88746267da02ad45` |
| [Primary assumptions](2026-09-11-brc-exp001-slice-a-candidate-assumptions.json) | 29153 | `4c5e48452ee81a5c65cef2a51dcae8de56262684e7056be429dd6166788241dc` |
| [Primary manifest](2026-09-11-brc-exp001-slice-a-candidate-assumptions-manifest.json) | 23490 | `296f0c8d78e6a248b7b647867f5a69a0de69190a5ee02198349c1c1269769c4d` |

The seven embedded complete requests were independently extracted and
canonically serialized for digest verification, without evaluating them:

| Request | Canonical bytes | SHA-256 |
| --- | ---: | --- |
| all_other | 97688 | `0ea4ae9192b59d0cf314edda4214597b2541632cd038ca999f99d70e9cd486c2` |
| one_viable | 94942 | `afb88121193b1ffc1b529ed20041fabde4d89280a79c14e1b08bcb0cb5e5ef07` |
| primary | 94819 | `67fe5d164251fdc6d8ba577e90660b0c486ea626af0a1faccac5362481f188c1` |
| surprise | 97269 | `6a913968dedbafcb1570d8ddc9fa5ca45faf93fe1f1b958ec68794c64f8bb3f0` |
| tied | 94705 | `36a896c8e8b87c679839d8f7fc8729d0f42312045e00539444485c3da2557c53` |
| unknown_single | 94623 | `3172aac61634d69fdfd12fe39906d5ef52a4e1a25d171f170555801c06505562` |
| zero_viable | 94936 | `e6a3568270bcb6331e673b4a5df9c6f51513ac3019d668008bf69ad01eeff330` |

Additional unchanged tracked commitments:

- Corrected synthesis: `18c44500c64757f71d46097c43d82978fac03e1729b73e9ea7cdf1f8b6f3eeaf`.
- Slice A plan: `197dd55d143999339b076a46e56a169d76aa74322d570a895c34aceafe9c0edc`.
- Immutable incomplete execution report: `7ac7a4aed2a930ea4fa225ecd73b082fb71d714720fca9f323209f4896beec80`.

## 3. Gate 3 reachability evidence

This conclusion concerns honest output of the existing producer composition,
not every value that the public Pydantic contracts can represent.

1. In [EA contracts](../../../backend/evidence_assurance/contracts.py),
   `OperationalEvidenceSelectionStatus` has exactly
   `complete_within_declared_horizon`, `incomplete_within_declared_horizon`,
   and `refused`. EA selection has no ambiguity status. A multiple-match
   reason belongs instead to evidence alignment.
2. [Binding discovery](../../../backend/identity_binding/resolver.py),
   `BindingResolver.declared_property_locators`, groups assertions by
   `(source_id, adapter_id, subject_identifier, extraction_route, item_key,
   json_pointer)` and emits one locator entry per key. Additional assertions,
   histories, or targets do not create duplicate entries for that key.
3. [Model-state production](../../../backend/model_state/facade.py),
   `ModelStateQueries.variable_state`, creates one observation candidate per
   discovered locator. An explicit selector creates exactly one specification.
4. [Value-compatibility production](../../../backend/observation_compatibility/facade.py),
   `ObservationCompatibilityQueries.variable_value_compatibility`, assesses
   each state candidate once; it does not multiply candidates.
5. [Alignment derivation](../../../backend/evidence_alignment/derivation.py)
   filters compatibility candidates by equality of those same six locator
   fields, then compares their complete observed occurrence with the selected
   occurrence. `multiple_matching_candidates` requires more than one exact
   match after this filter. The producer chain supplies at most one candidate
   for that locator, and therefore at most one exact match.

The existing [cardinality test](../../../tests/evidence_alignment/test_derivation.py)
reaches `not_aligned / multiple_matching_candidates / multiple_matches`
through [duplicate_consumer](../../../tests/evidence_alignment/helpers.py).
That helper copies the same state and compatibility candidate into two rows,
sets `declared_locator_count` to two and `selection` to `multiple`, and then
calls `VariableValueCompatibilityResult.model_validate`.

The helper demonstrates a genuine defensive contract branch. It does not
demonstrate two distinct query-produced candidates matching one locator.
The current owning validator accepts this reconstructed structural shape;
this report does not falsely claim it rejects duplicate locator rows.
Using that helper's duplicated payload as an honestly produced lower world
would misstate its provenance, even if all nested objects round-trip.

Alternatives considered without changing data:

- Multiple distinct discovered locators: possible, but only one can equal
  the alignment scope's exact six-field locator.
- Multiple bindings for the same locator: discovery still emits one entry.
  Binding-resolution ambiguity is a different assertion, not evidence of
  `multiple_matching_candidates`.
- Explicit source selector: produces one candidate, not multiple matches.
- Manual duplicate consumer rows: representable defensive input, not the
  requested honest producer-generated ambiguity parent.
- Changing production discovery or weakening the coherence requirement:
  outside authorization and not performed.

No public lower result was forged, no private helper was invoked, and no
existing test was repurposed as provenance for an honest world. Source and
test inspection here was read-only.

## 4. Outstanding gates, coverage, and commitments

| Gate | This closure attempt |
| --- | --- |
| Satisfied governing baseline parent | Not prepared; remains open. An H expecting satisfaction is not a satisfied governing public evaluation. |
| EA refusal parent | Not prepared; remains open. No claim that an honest refusal parent is impossible. |
| Honest EA ambiguity/multiple-match parent | Blocked by the producer/defensive-input distinction in section 3. |
| Independent expected-result oracle | Not created; neither seven-request nor 40-control oracle closure is claimed. |
| Trace/output-contract proof | Not performed; schema representability and adversarial reconstruction remain open. |
| Final resource maximum | Not established because the complete admitted-parent population is not frozen. |

The approved manifest contains exactly 23 Slice A obligation entries:
E01 through E17, E26, E27, E28, E30, E31, E32. This is preserved registered
coverage, not proof that every acceptance obligation has now passed. Its
pending-parent entries explicitly identify E16 and E17. Neither entry is
silently removed by this report.

All 40 ordered negative-control recipe entries remain unchanged in the
approved manifest. Every entry has the same disposition in this attempt:
approved recipe retained; no new independent oracle judgment, execution,
or output-contract proof performed. Registration does not count as a passed
control. Ordered array positions and exact recipe bytes remain bound by the
manifest digest; control display labels are not substituted for byte identity.

No pending-parent JSON, parent manifest, expected-oracle JSON, or oracle
manifest was created. Consequently no parent, valid-nearest-twin, or oracle
SHA-256 exists for this attempt. This absence is explicit, not a digest-only
reference or a promise that missing material is reconstructable elsewhere.

## 5. Resource and determinism status

The accounting contract remains:

`charged_validation_node_count = wire_node_count + resolution_charge_node_count`.

The operational limit remains 12,000 and the safety ceiling remains 16,384.
From the unchanged approved manifest, `M_A_support = 7,680`, cohort aggregate
charge is 50,738 and maximum cohort request bytes is 97,688.
`M_A_complete` remains **not established**, not 7,680 or 11,567 by substitution.

The approved natural-boundary evidence remains unchanged: 11,567 charged
nodes admitted through input inspection/public reconstruction; 12,355 refused
in charged-node preflight with zero owning calls. Those are retained prior
rehearsal results, not a new guard execution in this attempt.

No new counter comparison or six seed/root replay was performed after the
reachability blocker. Canonical artifact and seven-request digests were
reverified, which is narrower than new counter/determinism closure. Existing
independent-counter and seed/root evidence is preserved in the approved
rehearsal; it cannot prove counts for nonexistent pending parents. No owning
calls for new preflight-refusal cases occurred because no such cases ran.

## 6. Assumption inventory and spill analysis

No assumption, prediction, identity, provenance classification, cost policy,
or semantic input changed. Owner approval of the primary, six non-primary
variants, supplemental guard premises, T2-only BH variants and 40 recipes
is respected; no additional semantic premise was minted under that approval.

Supplied hypotheses remain level 3 / assumed; supplied conditional predictions
remain level 4 / assumed. Neither a consumer duplication nor a binding
ambiguity may be presented as an observed physical condition. A public model's
structural acceptance is not proof that an observation producer emitted it.
No calculated score, bounded preference, or inference was generated here.
Unknown completeness remains unknown. No physical cause, real fault,
prediction accuracy, global completeness, global optimum, influence,
planning, control, or successor-milestone claim is supported by this report.

## 7. Preservation and focused checks

Read-only public `ModelStore.load` confirmed 36 authoritative records and
accepted revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
The public model-kernel export list remains 236 entries, all unique.
FMA/FMW/FCD/FCW record counts remain 0/0/0/0.

Protected path-to-file-SHA-256 inventories, serialized as compact sorted
JSON with one final LF, match the retained preservation evidence:

| Root | Files | Inventory SHA-256 |
| --- | ---: | --- |
| models/demo-printer | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| bindings/demo-printer | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| bindings/demo-printer-model | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| interpretations/demo-printer | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| showcases/demo-printer | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| var/raw_store | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

ADR-0001 through ADR-0022 remain contiguous and unique. ADR-0023 remains
absent, unallocated, and unreserved; the existing README assertion is unchanged.
No production, production-test, fixture, ledger, identity, or accepted report
was edited. No temporary program, execution root or generated scratch dataset
was created, so there is no disposable material to delete.

Focused documentation tests: 26 passed using the existing documentation tests
for behavior evaluation, semantic compatibility, state classification, state
Slice B, behavior Slice C resolution and behavior Slice D rehearsal. Tests ran
with bytecode and pytest cache writing disabled. No full repository or
clean-checkout suite ran. Working-tree and checkpoint-range `git diff --check`
passed. This new report is separately checked for structure, local links,
ending marker, whitespace and digest before handoff.

## 8. Required owner decision

Authorize treating EA `multiple_matching_candidates` as an explicitly
adversarial carried-input control, rather than requiring an honest
producer-generated multiple-match world, and authorize the corresponding
preexecution gate correction. This is the recommended single next decision;
it does not authorize minimax execution or waive EA refusal, valid nearest
twins, output proof, independent oracle, or final resource measurement.

Until that decision, no approved artifact is amended and Slice A remains
incomplete. Binding ambiguity is not silently substituted. After any gate
correction, complete exact parent/oracle commitments and resource closure
would still require preparation and final owner approval before execution.

END OF BRC-EXP-001 SLICE A FINAL PREEXECUTION CLOSURE REPORT
