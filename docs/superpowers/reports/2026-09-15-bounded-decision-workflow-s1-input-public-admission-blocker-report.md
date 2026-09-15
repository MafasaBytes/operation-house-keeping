# Bounded decision-workflow S1 input/public-admission blocker report

Date: 2026-09-15

Status: S1 authorized but not started; one frozen acceptance expectation contradicts the authoritative public reconstruction boundary

## 1. Verified authority and implementation state

The requested checkpoint was verified as branch `brc-exp001` at `ec027add0cb2dae5434c42f67454752eb93f7228`. The owner authorization was then recorded in commit `44600982e6ec0e2e2dd4759d0d24510f8c81da37` (`docs: authorize bounded decision workflow slice 1`). That commit is the starting and tested administrative HEAD. No application source or test was created, so there is no later implementation HEAD.

The following frozen inputs were read completely and their supplied commitments matched:

- [corrected design](../specs/2026-09-15-bounded-decision-workflow-corrected-delivery-design.md): `54b8b9dcd34d7bd31056f24d4fe82a9eab7e0cc5a5e1e383401dd3498de426ab`;
- [implementation plan](../plans/2026-09-15-bounded-decision-workflow-implementation-plan.md): `6686c8add03d2b8e9aae10b51d12553a9af81d7c56f83866d37fbb5ec26e18d5`;
- [candidate package](2026-09-15-bounded-decision-workflow-candidate-package.json): `0d3b3a6f53c465dc45a3fc44b79523bc7d51131c42b342e9f4afa62795d29365`;
- [candidate manifest](2026-09-15-bounded-decision-workflow-candidate-manifest.json): `6ac24d274ac5f898876a0ab28f7c250ae1413b909260e1a48eb6d3f00aa55959`;
- [readiness report](2026-09-15-bounded-decision-workflow-implementation-readiness-report.md): `3792d9ade000b83c9226d50217b4b35154e8abfc780c39d6d9c3ce797f568d93`; and
- [persistent-environment report](2026-09-15-bounded-decision-workflow-persistent-environment-report.md): `4e83517a4ee3ec360ed681c336c71cd94dbf58b76bc98bddc541f5f70c3935e2`.

Repository inspection found no applicable `AGENTS.md`. The existing public contracts remain authoritative. S1 is exactly strict wire/JSON preflight, request contracts, public snapshot reconstruction, observed-`T0` admission and complete canonical S1 examples. S2–S7 remain unauthorized.

## 2. Blocking contradiction

The frozen `OBS-3-decimal` variant changes only this serialized field:

```text
/snapshot/constraint_evaluations/0/semantic_compatibility/value_compatibility/candidates/0/state_candidate/bound/observed/occurrence/value_json: "40" -> "41"
```

It leaves the carried public `CandidateConstraintEvaluation.observed_decimal` at `"40"`, leaves the other carried lower results unchanged, and leaves `REQUEST.json.snapshot_commitment` at the baseline snapshot commitment `782332fd8dd350d6852f57d0497c2c152a031caf08ee2dfc2cb040cdde8f326f`. The package expects application diagnostic `OBSERVATION_DECIMAL_MISMATCH` targeting `observed_candidate`.

That expected stage cannot be reached through the frozen workflow:

1. The corrected design §5.2 requires the application to reconstruct the entire snapshot with public `StateClassificationResult.model_validate` before application admission checks.
2. Public `ConstraintEvaluationResult` derives each candidate by calling public `derive_candidate_evaluation`; that derivation calls `parse_observed_decimal` on the occurrence lexeme and requires the carried candidate to equal the derivation ([constraint evaluation contract](../../../backend/constraint_evaluation/contracts.py)).
3. The enclosing public value/semantic/state contracts additionally require carried candidates to remain verbatim and authoritative.
4. Consequently, the exact package mutation is rejected by public reconstruction at `semantic_compatibility.value_compatibility` with `candidates must be carried verbatim and in the VM-001 order`. Application admission never receives a reconstructed snapshot from which it could emit `OBSERVATION_DECIMAL_MISMATCH`.
5. Independently, the mutated canonical snapshot SHA-256 is `c593759c3813919d159eae767eb7bd0c9871fbed6c6b844fed71a76adabe33fa`, not the request's frozen snapshot commitment. Even if a public-consistent mutation were devised, this unchanged request would fail the snapshot commitment before an admitted-value discrepancy could be accepted as the expected case.

Mapping this public validation failure to `OBSERVATION_DECIMAL_MISMATCH` by inspecting untrusted raw nested fields or parsing backend error text would bypass or duplicate the authoritative boundary. Relaxing the backend validator would be an unauthorized backend change and would weaken accepted carried-result integrity. Constructing an invalid `StateClassificationResult` in memory would not exercise the serialized public reconstruction path that S1 is required to implement.

## 3. Consolidated audit of related S1 expectations

The same disposable check used the frozen baseline object and the exact three snapshot mutations in `OBS-3`:

| Variant | Actual public reconstruction | Frozen expected class | Finding |
|---|---|---|---|
| baseline | accepted | success | agrees |
| `OBS-3-wrong-revision` | rejected at `constraint.revision`: revision ID does not match membership | `PUBLIC_RECONSTRUCTION_REFUSED` | agrees |
| `OBS-3-forged-result` | rejected at the state-classification root: disclosure is forged | `PUBLIC_RECONSTRUCTION_REFUSED` | agrees |
| `OBS-3-decimal` | rejected at `semantic_compatibility.value_compatibility`: candidates not carried verbatim | `OBSERVATION_DECIMAL_MISMATCH` | blocking disagreement |

No other S1 package expectation was found to have this public-reconstruction ordering conflict. Request-only retarget/context/cutoff/unit/index substitutions can reach application binding checks after a valid public reconstruction. A conversion field can be classified by the application profile/schema policy. Coherent unavailable results remain valid public results and can reach the application's typed `unavailable` outcome.

One non-blocking documentation count typo was also found: the design and plan say the request has “exactly ten” top-level fields, while their explicit field list, frozen package field set, and canonical baseline request consistently contain eleven. The enumerated eleven-field contract is unambiguous and does not require a semantic choice.

## 4. Exact correction gate

The smallest contract-preserving correction is to amend only `OBS-3-decimal` so the serialized mutation expects `PUBLIC_RECONSTRUCTION_REFUSED` at target `snapshot`, like the other forged public-result cases. The application should still call public `parse_observed_decimal` after successful reconstruction and compare it with the carried canonical decimal as a defense-in-depth assertion, but no serialized input should be claimed able to evade the public equality invariant and reach a distinct mismatch diagnostic.

If a separately observable `OBSERVATION_DECIMAL_MISMATCH` is considered essential, the owner must instead approve a changed test boundary and explain how a publicly reconstructed result can carry that mismatch without weakening or bypassing the public contract. No such input exists under the inspected contracts. A backend change is neither necessary nor recommended.

After that one frozen expectation is corrected and recommitted, S1 can proceed unchanged. No resource limit, premise, dependency, environment, admission join, or backend API needs amendment. The approved persistent environment was used for these checks: CPython 3.13.11, environment identity `693e458fefc4866bf83ce52c3b163995e0e6eb3cfe6389b73b748321bae0d27a`, on the verified ext4 workspace. Its retained wheel set and existing input/result directories were not changed.

## 5. Verification, preservation and pending capability

The check was a read-only, disposable public-contract reconstruction using the retained baseline bytes and exact package mutations. It was not an application test and did not execute `evaluate`, `verify`, `replay`, projection, policy, retention, or command behavior. No red/fixed implementation evidence exists because implementation correctly stopped before creating code against a contradictory oracle.

Tracked source remained unchanged apart from the authorization and this blocker record. Frozen design/review/package/report bytes, authoritative ledgers and fixtures, the persistent environment, and pre-existing untracked evidence were preserved. Whitespace, links, digest commitments and staged scope are checked before committing this record.

Owner action required: approve the one-case oracle/diagnostic correction above (or supply a different contract-consistent serialized case). That is the sole gate to resume S1. Later slices and production acceptance remain unauthorized.

END OF BOUNDED DECISION WORKFLOW S1 INPUT/PUBLIC-ADMISSION BLOCKER REPORT
