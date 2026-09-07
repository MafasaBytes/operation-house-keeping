# TA-001 Slice A Contract Correction and Owner Resolution

Date: 2026-09-07

Status: both preimplementation discrepancies owner resolved; corrected Slice A
authorized; Slice B unauthorized

## 1. Accepted discrepancy checkpoint

The owner accepts the TA-001 Slice A preimplementation discrepancy stop on
branch `ta001` at exact HEAD
`47a747ad9df020d631318b09f24a0d2a2c39fc6a`.

The historical discrepancy report remains unchanged at:

`docs/superpowers/reports/2026-09-07-ta001-slice-a-preimplementation-discrepancy-report.md`

Its verified SHA-256 remains
`857ceb224b9fd15799276ccaa94d88042fc3876b1ce740e01f6a407916877f64`.
The report is preserved as the accurate record of why implementation stopped;
it has not been rewritten to anticipate this later resolution.

## 2. Corrected authority and digests

The pre-correction synthesis remains historical evidence at SHA-256
`99db3b31f5fa94eb119b32529784a64aff08c604f71ee9eb7530225963816062`.
The bounded owner correction changes only the normative synthesis and the
Slice A implementation plan:

| Document | Corrected SHA-256 |
|---|---|
| `docs/superpowers/specs/2026-09-07-ta001-evidence-gated-declared-transition-assessment-design.md` | `3468a2a5ca48540e3656b1224e6af34364ea94671379253f1755df51e99092bd` |
| `docs/superpowers/plans/2026-09-07-ta001-slice-a-implementation-plan.md` | `da9e426d52348203bed716bcc7d11d4deb2dde7d8d303c7a4e98392b1ec9d0a8` |

The corrected synthesis digest supersedes the old digest only for TA-001
implementation after this gate. The proposal, challenger audit, final-design
approval, ADR reconciliation report, ADR-0019, ADR-0020, administrative
authorization, historical discrepancy report, and all accepted lower designs
retain their original bytes and authority.

ADR-0020 contains no direct claim that finite carried floats are forbidden and
no T43 outcome, so it required no change.

## 3. Owner resolution R1 — finite lower-contract floats

TA structural preflight admits an exact built-in Python `float` only when
`type(value) is float` and `math.isfinite(value)` is true. Float subclasses,
booleans masquerading as numbers, NaN, positive infinity, and negative
infinity are malformed and map to the sole public input error
`TRANSITION_ASSESSMENT_INPUT_INVALID`.

This schema-independent structural admission does not widen any public field.
After preflight, full nominal lower reconstruction remains authoritative for
whether a position legally accepts a float. A float substituted into a
non-float field rejects. TA adds no float-valued field of its own.

The ordinary reconstructed request/result graph remains unchanged. TA neither
stringifies nor integer-coerces, decimalizes, tags, rounds, omits, or otherwise
rewrites an accepted lower float.

Private canonical test bytes encode an admitted finite float as a JSON number
using built-in `float.__repr__(value)`, after checking the JSON-number grammar.
They preserve `-0.0` and the `.0` of integral-valued floats, lowercase an
exponent marker if necessary, and perform no other rewrite of the shortest
round-trip token. The streaming byte counter counts that same token before the
bounded encoder retains a complete result.

Tests must cover `0.0`, `-0.0`, `1794.0`, a fractional finite value, small and
large exponent notation, clean-checkout reproduction on the supported Python,
float-subclass rejection, all three non-finite values, and a finite float in a
non-float field. This is only inherited scalar disclosure, not an engineering
comparison or a general TA numeric policy.

## 4. Owner resolution R2 — corrected T43

The normative T43 is corrected to:

| ID | Base | Mutation | Expected result |
|---|---|---|---|
| T43 | T01 | forge or substitute an evidence-alignment candidate index other than the exact governing candidate, including candidate index one | nominal lower reconstruction fails and TA raises `TransitionAssessmentInputError` with `TRANSITION_ASSESSMENT_INPUT_INVALID` before derivation; no structured assessment result is emitted |

The valid twin carries the exact candidate-zero alignment and remains
accepted. T42 remains the reachable structured non-execution case for a valid
lower `not_aligned` result. T63 remains the broader hostile divergence between
semantic and value index domains. The correction creates no multi-candidate
state-classification behavior and weakens no lower validator.

## 5. Executable reproduction and corrected expectations

The R1 reproduction constructed a disposable state classification through the
accepted public orchestration. It remained a valid executed result and its
ordinary Python graph contained six exact built-in floats:

```text
R1 executed 6 [1794.0, 1794.0, 1794.0, 1794.0, 1794.0, 1794.0] float
```

The corrected expectation admits those finite scalars structurally, retains
them unchanged through nominal lower reconstruction, and encodes each
`1794.0` token exactly. It still rejects them if a lower schema does not
declare that position as a float.

The R2 reproduction constructed one real complete evidence alignment with a
matched independently supplied expected fingerprint. The exact valid and
forged observations were:

```text
R2_TWIN aligned_with_complete_evidence 0
R2_FORGED nominal_lower_reconstruction_rejected
```

This confirms candidate zero is the valid public twin and candidate one is a
malformed lower result, not a structured TA gate outcome.

## 6. Scope and compatibility consequences

The correction changes no public TA name, field, type, literal, exception,
signature, limit, join, issue order, status table, fingerprint rule, carry-once
rule, or conclusion. It changes no lower model or serialization. In
particular, `LatestObservedState.staleness_seconds` remains the accepted lower
`float` disclosure.

TA remains a pure read-only leaf over carried public model-kernel,
state-classification, and evidence-alignment results. It owns no facade, store,
cache, database, persistent receipt, identity, ledger, connector, clock,
environment discovery, write path, occurrence model, demonstration, fixture,
or authoritative artifact. It makes no transition occurrence or
non-occurrence, cohort, continuity, causality, flow, correctness, diagnosis,
recommendation, control, or truth claim.

## 7. Pre-commit verification and preservation

The six-module documentation/status gate passed `26 passed in 2.12s`. The two
immutable model/artifact preservation twins passed `2 passed in 3.84s`.
Working-tree `git diff --check` passed with no output before staging.

The corrected synthesis ends with its exact existing marker. This resolution
report ends with the required marker. Changed-document local links and both
markers are checked again after the report is written and before commit.

The authoritative model remains exactly 36 records at revision
`mrv_b8f03e1c03c23efc5c4454d00e43e6b89b8254ab87ce724d7418b8a94288c7ee`.
FRG/FLD/FLW remains `1/1/0`; TRG/TRD/TRW remains `0/0/0`. The record-file
aggregate remains
`bbb09d9be9b6096381394fd4f491e3ecfed3ebe071c78bd9276a03c8ddd5cd8a`.
The flow disclosure remains 660,516 bytes at SHA-256
`096bb4d00600b861d5e127afe5a41a158f43bbb926017f62592307d0db43723b`.
The owner-local settings digest remains
`abbdd3f4e359b1e88fb93a4801b6e314bf701726df76a13e344c8b7e89f18357`.

## 8. Renewed authorization and next gate

The owner authorizes resumption of TA-001 Slice A only from the corrected
synthesis and plan. The work is confined to the exact 28-name pure public
surface, bounded preflight, pure derivation, authoritative reconstruction,
focused red-first tests, README/status documentation, and required
verification.

Slice B remains unauthorized. The implementation must stop again if another
genuine public-contract contradiction appears. No push, merge, rebase, reset,
amend, cherry-pick, or history rewrite is authorized.

END OF TA-001 SLICE A CONTRACT CORRECTION AND OWNER RESOLUTION
