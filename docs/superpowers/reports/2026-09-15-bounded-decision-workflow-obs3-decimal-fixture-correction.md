# Bounded decision-workflow OBS-3 decimal fixture correction

Date: 2026-09-15

Status: owner-resolved fixture contradiction corrected; S1 may resume

## Authority and preserved history

The correction starts from branch `brc-exp001` at
`a9473d5d4ffaa4276b29374466f6d1079cd0397f`. The S1 authorization remains
`44600982e6ec0e2e2dd4759d0d24510f8c81da37`; S2-S7 remain unauthorized. The
[blocker report](2026-09-15-bounded-decision-workflow-s1-input-public-admission-blocker-report.md)
was preserved byte-for-byte at SHA-256
`d7255969245010f4f41b922558e4a741993169bd13687110c52e67c559b0652c`.

The original package and manifest are retained verbatim as
[historical package](2026-09-15-bounded-decision-workflow-candidate-package-pre-obs3-decimal-correction.json)
(`0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365`)
and [historical manifest](2026-09-15-bounded-decision-workflow-candidate-manifest-pre-obs3-decimal-correction.json)
(`6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959`).
Those files preserve the contradicted oracle as historical evidence; they are not
the corrected S1 oracle.

## Exact correction

The untouched valid twin remains request
`24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125`
and snapshot
`782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f`.
It reconstructs publicly and admits canonical decimal `40`.

The former `OBS-3-decimal` now has two cases:

1. `OBS-3-decimal-reconstruction` changes only
   `/constraint_evaluations/0/semantic_compatibility/value_compatibility/candidates/0/state_candidate/bound/observed/occurrence/value_json`
   from `"40"` to `"41"`. Its canonical hostile snapshot is
   `c593759c3813919d159eae767eb7bd0c9871fbed6c6b844fed71a76adabe33fa`.
   A mechanically updated request names that digest and commits as
   `adc8e2650bcac78f498ca64c4b783640086fe52c1c6e10693abe8e0c28d9238d`.
   The enclosing digest is now coherent, but the nested carried result is still
   forged. The expected diagnostic is `PUBLIC_RECONSTRUCTION_REFUSED`, stage
   `commitment_public_reconstruction`, target `snapshot`.
2. `OBS-3-decimal-stale-commitment` pairs the original request with the hostile
   snapshot. The expected diagnostic is `SNAPSHOT_COMMITMENT_MISMATCH`, at the
   same stage but target `snapshot_commitment`. Authoritative public
   reconstruction is not reached.

The fixture sweep found the same latent stale-commitment bookkeeping issue in the
snapshot mutations for `OBS-3-wrong-revision` and `OBS-3-forged-result`. Their
intended public-reconstruction refusals were preserved by materializing the
mutants and mechanically updating only the enclosing request commitment:

| Case | Corrected request | Hostile snapshot | Expected first diagnostic |
| --- | --- | --- | --- |
| wrong revision | `2f959613c2b3b4caf1cfa9fe622b62f2903ddfdee99c1443979a505dfe318837` | `df573e95a13631b49c9438148abd9d78d8465e624235356edc73730fd93e4413` | `PUBLIC_RECONSTRUCTION_REFUSED` |
| forged result | `0631122202206e733bdbc716b1bbc6446406dd6be75635c340f5e1655859a31b` | `a7101695f8650322b68bddf7b8bf0d3d35d0417c2143073f38e1eb8d21d489ae` | `PUBLIC_RECONSTRUCTION_REFUSED` |

No observed value, backend contract, valid snapshot, numerical rule, application
admission predicate or diagnostic precedence changed. The package now has 69
variants and 38 recoverable objects. Its corrected commitments are:

- candidate package:
  `199d82590048b610f9aa9e96de1620f9015884e727459e88d156d6052ed20ad4`;
- candidate manifest:
  `5305aef821a19c01c74223ce9a1d483518b41d8c946ead4dd8aeea064b9b3b4a`;
- mechanically amended implementation plan:
  `ad18829d4d4f11c277ae1dd511cffd75be1e0777e71a694be1f2bd7550d66937`.

The plan amendment also corrects the nonsemantic count typo from ten to the
explicitly enumerated eleven request fields and describes the nine OBS-3 variants.
The approved design and frozen review were not changed.

## Admission precedence and reproduced results

The accepted order is: parse and validate the request sufficiently to obtain its
commitment; compute and compare the canonical snapshot commitment; reconstruct the
matching snapshot through public `StateClassificationResult.model_validate`; then
perform application binding/admission checks; finally reparse the admitted source
lexeme through public `parse_observed_decimal` as defense in depth.

A disposable independent harness recovered and hash-checked all 38 object-store
entries, then applied that order. Results were:

- request-only retarget, context, cutoff, unit and index mutants: commitment and
  public reconstruction succeeded, so application binding is the first relevant
  stage;
- wrong-revision, forged-result and hostile-decimal mutants with corrected
  enclosing commitments: public reconstruction refused;
- the preserved stale decimal pair: snapshot commitment refused before public
  reconstruction; and
- both the admitted baseline and coherent-unavailable public snapshots:
  reconstruction succeeded.

Thus a valid serialized public `StateClassificationResult` cannot reach the
decimal-mismatch branch: the public candidate derivation and carried-result
equality invariants reject such a mismatch first. The application retains its
post-reconstruction reparse/equality assertion as defense in depth. Its direct
unit test is scoped to an already reconstructed internal admission seam and is not
described as a valid serialized fixture.

## Remaining S1 fixture sweep

Every S1 object reference resolves to content with its declared SHA-256 and byte
count. Request-only mutations keep the valid snapshot commitment. All public-result
mutations intended to reach reconstruction now have matching enclosing
commitments. The stale pair contains exactly its intended earlier fault. OBS-2
producer recipes each name one unavailable cause, require the public facade chain
and retain the accepted baseline as nearest valid twin; they do not carry stale
serialized commitments. The `OBS-2-nonnumeric` recipe now explicitly supersedes
the baseline non-nullable value specification with a nullable numeric
specification: without that single producer premise, null correctly stops earlier
at `value_shape_not_satisfied` instead of the intended `numeric_value_absent`.
The OBS-4 conversion mutant remains a known unsupported
profile field with the frozen `PROFILE_UNSUPPORTED` result; the interpreted-unit
twin remains a public reconstruction/admission success. No additional semantic
contradiction was found.

The checks used CPython 3.13.11 from the approved isolated environment on the
verified ext4 workspace. They operated only on disposable copies and repository
documentation. No production application behavior, backend, ledger, authoritative
fixture, runtime result or dependency installation was changed.

END OF BOUNDED DECISION WORKFLOW OBS-3 DECIMAL FIXTURE CORRECTION
