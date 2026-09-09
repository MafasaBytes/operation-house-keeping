# FC-001 Slice B final verification report

Date: 2026-09-09. Branch: `fc001`.

## 1. Scope, starting checkpoint and stopping boundary

This report closes the requested post-reconciliation verification from clean
starting HEAD `077aff2b22f7e638f7d9dc88fce3bce3d7bd9d89`. The starting tested
candidate was `9737e9f137b80d526565e62e714f0603791dc3e6`; the exact implementation
tested by the complete final matrix is
`9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`.

The existing interim completion report was not rewritten. Its SHA-256 remains
`501d217a0ffea7faad08fc85133b89c1351f469e9be3a2f86a807c5d2c97a642`.
No successor milestone, authoritative append, fixture mutation, push or merge
was performed.

## 2. Final-verification commit topology

The bounded repair commits after the immutable interim checkpoint are:

1. `5e717f5649b7091eb63f6f6ffafe07df3aaaa9f1` — enforce authoritative FC
   applicability results.
2. `9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082` — bound and harden FC query
   reconstruction.

The forthcoming commit containing only this report is administrative and is
not part of the tested implementation.

## 3. Reproduced defects, red evidence and bounded repairs

The post-interim review reproduced nine defective outcomes and repaired all
nine without changing the accepted contract.

At the original candidate, four probes showed that outer results could trust
forged derived fields, FC-to-FM equality compared the wrong bytes, support
disclosure stopped after CRG/VCN instead of carrying the complete selected
closure, and currentness/conflict applicability was incomplete. The first
repair added authoritative outer recomputation, exact retained-witness FM-body
comparison, the full ordered support closure and lower currentness reasons.

The independent adversarial pass then reported four important findings: a
single-root different-body fork incorrectly added cross-root disagreement;
hostile result subclasses could execute serializer callbacks; inherited JSON
admission accepted duplicate keys and over-4-MiB input; and public validation
errors exposed values without the fixed FC codes. The red-first regression run
was `4 failed, 7 passed`. A fifth focused hostile-object probe showed an
unnecessary `isinstance` check could still invoke `__class__`; it was removed
and covered by a zero-callback regression.

The final repair provides callback-free exact-class reconstruction, expanded
edge accounting, duplicate-rejecting bounded JSON parsing, fixed value-free
`FC_RESULT_INVALID` / `FC_RESULT_LIMIT_EXCEEDED` errors, operational query
error translation, exact root/body-pair disagreement, and preflight of the
accepted material/positive/root/group/pin/row ceilings before output
expansion. The repaired Slice B file has 13 passing tests; the complete FC
Slice A+B suite has 178. Red/fixed outcome count: **9/9**.

## 4. Final public contract and semantic boundary

The public responsibilities remain exactly
`ModelQueries.flow_operating_criterion(...)` and
`ModelQueries.flow_operating_criterion_assertion(...)`. No facade, reverse
discovery API, evaluator, store or additional public model was introduced.

FC reports designation presence, lineage health, agreement, exact selected
support currentness/alignment and present applicability. It does not evaluate
a variable constraint or choose an observation. Valid historical support
continues to load and replay; currentness changes only the Slice B
applicability disclosure. FC does not establish physical flow, measurement at
the participant, activity, occurrence, continuity, conservation, causality,
correctness, safety, diagnosis, recommendation or operating health.

## 5. Independent architecture and adversarial verdict

The bounded independent implementation review first rejected
`5e717f5649b7091eb63f6f6ffafe07df3aaaa9f1` with zero critical, four important
and zero minor findings, then identified the remaining callback edge as one
important finding. After both repairs and the derived-output preflight, its
final verdict was **approve**, with **0 critical, 0 important and 0 minor**
open findings.

The final review confirmed exact FM-body comparison, complete support and
currentness disclosure, root/body-pair conflict semantics, callback-free
outer validation, bounded duplicate-rejecting JSON admission, fixed
value-free failures, no upper imports or I/O, and no evaluation or physical
claim. The A/B consumer result below makes the contract decision-useful rather
than contract theatre.

## 6. Verification environments and dependency state

All final runs used commit `9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`.
The working tree used `.venv`. New detached checkouts were created at:

- base: `/tmp/fc001-slice-b-final3-base-SUMPAF/checkout`;
- all-extras: `/tmp/fc001-slice-b-final3-extras-PWCiqO/checkout`.

The base checkout used the base/dev-only environment prepared from
`requirements.txt` and `requirements-dev.txt`. The extras checkout used that
base plus the accepted `--require-hashes` CAD/PDF inputs. Requirement digests
were respectively
`783e219f8fd03bd79eb7d0a21d96fc6bd31b4778d8c1509c684adcc5e4f7e9b7`,
`e8df7d69da1b48125985fb4cb0b8c015103baa89db1f5f86796da1753522a3f1`,
`30c4842f0824ee05149d5db2303a6bfd79dd009173d69b657f34cb4024dcd1d6`
and `bbe625db9d3748b3f475c3fb5d27505b5c8cf230029bf758a55577e10a246e43`.
`pip check` and `python -m compileall -q backend` passed in all three
environments. Both detached worktrees remained clean.

## 7. Complete command and result matrix

Every pytest command used `PYTHONDONTWRITEBYTECODE=1`, `-o addopts=''` and
`-p no:cacheprovider`.

The exact working-tree selections were:

```text
pytest tests/model_kernel/test_flow_operating_criterion_records.py tests/model_kernel/test_flow_operating_criterion_store.py tests/model_kernel/test_flow_operating_criterion_determinism.py tests/model_kernel/test_flow_operating_criterion_slice_b.py -q
pytest tests/model_kernel/test_isolation.py tests/model_kernel/test_flow_architecture.py tests/model_kernel/test_flow_query_contracts.py tests/model_kernel/test_flow_query_parity.py tests/model_kernel/test_flow_query_revalidation.py tests/model_kernel/test_transition_architecture.py tests/model_kernel/test_transition_query_contracts.py tests/model_kernel/test_transition_query_parity.py tests/model_kernel/test_transition_query_revalidation.py tests/model_kernel/test_flow_measurement_integrity_repair.py tests/model_kernel/test_flow_measurement_slice_a.py tests/model_kernel/test_flow_measurement_slice_b.py tests/model_kernel/test_flow_measurement_slice_b_adversarial.py tests/model_kernel/test_flow_operating_criterion_records.py tests/model_kernel/test_flow_operating_criterion_store.py tests/model_kernel/test_flow_operating_criterion_determinism.py tests/model_kernel/test_flow_operating_criterion_slice_b.py -q
pytest tests/model_kernel -q
pytest tests/model_kernel/test_flow_*.py tests/model_kernel/test_variable_port_*.py tests/model_kernel/test_variable_semantics.py tests/model_kernel/test_variable_value_specification.py tests/model_kernel/test_state_*.py tests/model_kernel/test_behavior_*.py tests/model_kernel/test_transition_*.py tests/constraint_evaluation tests/evidence_assurance tests/evidence_alignment tests/model_state tests/observation_compatibility tests/semantic_compatibility tests/state_classification tests/behavior_evaluation tests/transition_assessment tests/temporal_state tests/identity_binding tests/source_interpretation tests/structural_evidence -q
pytest tests/ -q
```

The two clean checkouts ran the same final `pytest tests/ -q` selection with
their own interpreter. The optional extras command selected the STEP
extractor/runner, PDF extractor/detection/coordinates/contracts/runner and
structural STEP-claim files explicitly.

| Column | Exact selection | Final result |
| --- | --- | --- |
| FC Slice A+B | the four `test_flow_operating_criterion_{records,store,determinism,slice_b}.py` files | 178 passed in 30.11s |
| architecture/import/no-I/O/reconstruction/adversarial | `test_isolation.py`; all FL query architecture/parity/revalidation files; transition architecture/query files; all FM repair/Slice A/Slice B files; all four FC files | 400 passed in 135.74s |
| complete model kernel | `pytest tests/model_kernel -q` | 1,928 passed in 929.78s |
| complete affected matrix | all flow, VP, VS, state, behavior and transition kernel files plus complete CN, EA, alignment, model-state, compatibility, classification, assessment, temporal, binding, interpretation and structural-evidence directories | 2,813 passed in 1,290.20s |
| working repository | `pytest tests/ -q` | 4,073 passed; sole loopback setup error; 2,497.44s |
| fresh base-only repository | `pytest tests/ -q` | 4,038 passed, 35 skipped; sole loopback setup error; 1,833.66s |
| fresh all-extras repository | `pytest tests/ -q` | 4,073 passed; sole loopback setup error; 1,893.53s |
| CAD/STEP/PDF gate, fresh extras | STEP extractor/runner, PDF extractor/detection/coordinates/contracts/runner and structural STEP claims | 120 passed in 40.05s |
| dependency consistency | `python -m pip check` in all three environments | passed in all three |
| backend compilation | `python -m compileall -q backend` in all three environments | passed in all three |

The affected command deliberately repeats lower families already covered by
the complete kernel column so each named FM, FL, CN, EA, evidence-alignment,
VP, VS, ES, ST, BH and TA impact boundary has direct final-candidate evidence.

## 8. Managed-sandbox loopback reconciliation

In each complete-repository run, the only error was setup of exactly:

`tests/data_sources/test_http_api_connector.py::TestRealLoopbackTransport::test_get_redirect_refusal_and_proxy_isolation`

Each traceback ended at `socket.socket.__init__` with `PermissionError: [Errno
1] Operation not permitted`. The exact test was rerun separately under the
established permitted boundary, without changing code or test selection:

- working tree: 1 passed in 1.72s;
- fresh base: 1 passed in 0.70s;
- fresh extras: 1 passed in 0.70s.

The final accounting is therefore split evidence, not an uninterrupted-suite
claim: working/all-extras each cover 4,074 passing tests; base covers 4,039
passing and 35 correctly skipped optional tests.

## 9. Named-consumer A/B substitution proof

A labelled disposable 19-record model was built only in temporary storage
through public APIs. The exact FC subject was:

- flow `flo_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`;
- participant port `prt_11111111111111111111111111111111`;
- measured-actual variable `var_11111111111111111111111111111111`;
- context `lifecycle_view/as_designed` and orientation `aligned`;
- retained FMA witness
  `fma_cd234041b6e1a98b65a33c61b7b742c463a348fcb92f1de912e88de2555cb2cb`.

FC returned `applicable` and pinned governing criterion A exactly to
`vcn_70b5e146d682db6ca696a9165d0d4521c36ba4324b3d52f96c8a13bae13912cd`.
The ungoverned same-variable criterion B was
`vcn_3caad214041adad24a48bac3f13767078022329de34e2f46161a745c11c0273e`.
At explicit receipt cutoff `2026-08-07T21:00:00+00:00`, the nominated
measured-actual observation was `dbe466795f83b2fbab8d8d79fa62cc59`, value
`60.1`, occurrence `79bcec2f4de12d6e67f657f2e1153637`, received at
`2026-08-07T20:00:06+00:00`.

Evidence assurance returned `complete_within_declared_horizon`; evidence
alignment returned `aligned_with_complete_evidence` with candidate attachment
`attached`. Its reconstructed snapshot fingerprint was
`sha256:36e4c7f6065fbb531bf441d8891410f93851294093c7ad14b40593c62dd0e5ab`.
Existing CN evaluated the nominated candidate against exact A as `violated`
with observed decimal `60.1` and an inclusive upper boundary `50`. CN
independently returned `satisfied` for ungoverned B, whose upper boundary was
`80`. The consumer followed the FC-pinned VCN and therefore reported A's
`violated` result; B could not substitute.

In the valid twin, changing only the nominated observed value to `40` changed
CN's A result to `satisfied`; the FC result was byte-for-field unchanged. FC
performed applicability, EA/alignment supplied bounded evidence disposition,
and CN performed predicate evaluation. The join introduced no physical-flow,
occurrence, causality, safety, correctness or operating-health conclusion.

## 10. Deterministic witness reproduction

The complete six-result consumer payload was serialized in the normative
public-model order `(FC, EA selection, evidence alignment, CN A, CN B, CN A
twin)`. Working, base and extras produced identical **174,490-byte** payloads
with SHA-256
`1aa2f3ffd092743691d705ae070fd1b27ab92dd87ab8be12080d4a2a2912285e`.

The corrected FC-only public result, in the fixed disposable model `x`, has 11
ordered support rows and was reproduced identically in all three environments:
**14,677 bytes**, SHA-256
`a54daa9f263f1b5c2cb7bbf6b841ea3a28de2a6e1556dd18ca934d0d736039ca`.

The earlier proposed value, 13,665 bytes at
`1760ac23221e4a947df7bf81c75c6a378799df006ea57689aa2b2a378111846d`,
does **not** remain accepted: it serialized the defective two-row CRG/VCN-only
support disclosure and is superseded by the complete 11-row witness above.

## 11. Exact public export preservation

Working, base and extras each produced exactly **236 unique ordered**
`backend.model_kernel.__all__` names. The accepted 227-name prefix is
unchanged; its compact JSON-list SHA-256 is
`756698e83e44948ed24646d2808b9cfeb1f0d8c6f7d7650b2d61c455851afefd`.
The complete 236-name export digest is exactly
`77d0fc94f21132270c3653d290cf625c322748c7249cff55749af83881a90252`.
No new public definition was introduced by the bounded repair.

## 12. Authoritative ledger, revision and artifact preservation

The read-only preservation witness passed in the working tree and both clean
checkouts. The authoritative model remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remains `1/1/0`; TRG/TRD/TRW remains `0/0/0`;
FMA/FMW/FCD/FCW remains `0/0/0/0`. The record-inventory digest remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.

Protected tree counts and SHA-256 inventory digests remain:

| Tree | Files | Digest |
| --- | ---: | --- |
| `models/demo-printer` | 37 | `ea13596e56d00c1bc39866d8ddc7a0ae551af3fa2d1e3b5f500c0edec0b1ca37` |
| `bindings/demo-printer` | 6 | `11ccbed0d42505fa33925ef9ef3d56da12484f9f167106f28f3b6772c39e15b0` |
| `bindings/demo-printer-model` | 5 | `1c861155fbd04676f2ac2f86edc60f0d07899a8b1832772af9d20fb8259771dd` |
| `interpretations/demo-printer` | 3 | `819a21911a227c1175d6a5552ba924806e1ee0d13ae75009c4b789db979c83fd` |
| `showcases/demo-printer` | 9 | `dd7d8c986d769dcec519b7422cad417d6c3cdd39252dcd686c8c2a4a225d45ce` |
| `var/raw_store` | 5 | `16ff9454f9e13cbbcb5be687d0fcbc029d80c556bd51728c6ef025f78e71d91a` |

The frozen synthesis remains
`7aa5007058c1733720fc624839c19efd98258c800c67461d1afc5ade674a3453`.
The frozen lead proposal and challenger audit remain respectively
`8a65e3a4721fc0ba3dc28b0772e920f2dcc3008a9e1411ce07c9a8d1b204749e`
and `35d8537e2b1dc17775e2e96b0c021c4387ee1b6cd02265d861d17974b6e3d94f`.
The accepted Slice A completion report remains
`0f2c41555791ba60fb5bfc24450b273312bf9f55b2d50d6d59ce515d22c2ea67`.
Ignored `.claude/settings.local.json` remains unchanged and uncommitted at
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 13. Whitespace, revision-range and repository checks

`git diff --check` passed for the clean tested working tree. It also passed for
the final-verification range
`077aff2b22f7e638f7d9dc88fce3bce3d7bd9d89..9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`
and the full FC milestone range
`c0e1c8fe930e10243fec16a4950a3d34d4c85df4..9a993bdc7a9a4f2e2fa665ea2282ebefd59a6082`.
Before this report was added, `git status --short` was empty in the working
tree and both detached checkouts.

## 14. Product contribution, FA disposition and limitations

The direct public-result join now answers the approved commissioning/operations
question: at one explicit receipt cutoff, the consumer can identify the exact
authority-designated VCN for an exact flow-measurement subject, retain its
declaration/support provenance, attach one bounded evidence candidate and
report CN's exact evaluation without substituting another same-variable
constraint. This advances the accepted objective gaps for explicit model
meaning, trustworthy evidence, current comparison and provenance disclosure.

FA-001 remains cancelled because explicit checks over the FC, EA/alignment and
CN public results prevent the demonstrated criterion/candidate/revision
substitution attacks. A combined validator, aggregate status, smaller object,
deduplicated carriage or named package would add convenience only. FA can be
reconsidered only through a future owner-approved proposal that reproduces a
specific integrity attack these explicit public-result checks cannot prevent.

The authoritative model intentionally has no FMA or FC records, so this report
makes no authoritative commissioning claim. FC still cannot answer physical
flow, continuity, conservation, causality, impact propagation, next-best
measurement, planning, control, correctness or safety questions.

## 15. Final owner gate

The complete post-repair matrix passes with the loopback restriction separately
and exactly reconciled. FC-001 Slice B is ready for final owner validation. No
Slice C exists, and no later milestone is authorized by this report.

END OF FC-001 SLICE B FINAL VERIFICATION REPORT
