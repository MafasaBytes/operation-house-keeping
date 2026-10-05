# Amendment map: v3 to v4

v3 (`MANIFEST.json` `1a9eccbd8b0191eac08b4677a087f7503ee934845425985b05686c179e1e5572`),
v2 and the original package are preserved byte-for-byte. v4 keeps the v3
contract text verbatim (CONTRACT §0–§11) and adds §12, which supersedes only the
clauses it cites.

## Contract map

| # | Obligation | v3 (old) | v4 (new) |
|---|---|---|---|
| 1 | Policy identity | §5: edition must be `ct.policy-edition.v3`; schema const `ct.policy-edition.v2` (Gate 1 F1 workaround accepted the v2 label) | §12.1: schema const and contract both `ct.policy-edition.v4`. The label is checked before structure (`POLICY_EDITION_MISMATCH`). The workaround is removed. |
| 2 | Diagnostics and precedence | §7.1: exit classes only; no build-unavailable or usage codes. F12b expected `RESOURCE_LIMIT_EXCEEDED` | §12.2: `ct.diagnostic.v1`; `CLI_USAGE` (2), `BUILD_IDENTITY_UNAVAILABLE` (3, distinct from `BUILD_NOT_PERMITTED`), `INTERNAL_ERROR` (7). Schema bounds precede stage-4 counts: **F12b amended** to `SCHEMA_INVALID` (original retained); new F12c covers the captured-count refusal. |
| 3 | Result evidence | §6.1: acquisition carries `public_evidence`; no value join (Gate 1 F3) | §12.3: T1 value, instrument, anchor and distinct-occurrence bindings; T2 application-owned `ct.code-evidence.v1` (value, instrument, acquisition window); kind per procedure; `RESULT_EVIDENCE_MISMATCH`. **T1 acquisition-time binding pending (choice C1).** |
| 4 | Applicability scope | §4.2 "nominated procedure × condition for the request's phase" (Gate 1 F4) | §12.4: selection covers the whole nominated set; reassessment covers the executed procedure only |
| 5 | Encoded carriage | Gate 1 F5 exempted all `closure.json` strings | §12.5: only `ct.closure.v1.members[*].data`, bounded by `decoded_bytes` ≤ `object_bytes` |
| 6 | Withheld priors | §7.3: every `x-target` is an edge; a blocked prior with unsupplied claim cores refused (Gate 1 F6) | §12.6: claim references inside computed records are derived, non-edge references verified by recomputation (`x-edge: false` in the schema) |
| 7 | Evaluation authority validity | No rule (Gate 1 F8) | §12.7: `A.valid` contains the assessment-scope end (`request.as_of`, or `acquisition.ended`) |
| 8 | Cached derivation | IN1 had no interface | §12.8: `--cached-derivation` / `cached_derivation`; independent recomputation; `CACHED_DERIVATION_MISMATCH` |
| 9 | Captured limits | Captured limits retained; only counts, unique-objects and closure caps applied | §12.9: object, string, depth, node and integer-digit limits rechecked under the captured policy; `trace_entries` and `rational_operations` defined and enforced |

## Schema and policy deltas (`schemas.json` `43c2af0b…`, `policy.json` `46df039b…`)

**`schemas.json`:**

- `$id` `schemas-v4`;
- `ct.policy.v1.edition` const v4;
- new `ct.code-evidence.v1` and `ct.diagnostic.v1` (24 records, 25 reference kinds);
- `acquisition.public_evidence` and `reassessment.observation.public_evidence`
  targets now `[nm.evidence.v1, ct.code-evidence.v1]`;
- closure member kinds gain `ct.code-evidence.v1` after the 12 selection kinds;
- `x-edge: false` on the three derived claim references.

**`policy.json`:**

- edition `ct.policy-edition.v4`;
- 4 new refusal codes (38 in total);
- `exit_classes` table;
- `rational_operations` and `trace_entries` derivations rewritten as exact
  accounting definitions.

## Witness map (`witnesses.json`, `ct.witness-matrix.v4`)

| Status | Count | Cases |
|---|---:|---|
| original (v3 expectation unchanged) | 103 | all v3 cases except F12b |
| amended (original expectation kept in `original_expected`) | 1 | F12b |
| new | 31 | RE1–RE10 (W20), AP1 (W21), EC1–EC2 (W22), WD1–WD2 (W23), AV1–AV3 (W24), CD1–CD3 (W25), LM1–LM7 and F12c (W26), DG1–DG2 (W27) |

IN1 keeps its v3 expectation and is now implementable through §12.8.

Gate 2 sizing (`RESOURCES.md` and `PLAN.md`) is **not** updated: G2 is deferred.
The v4 matrix has 217 invocations versus 179 in v3, so the v3 Gate 2 storage
derivation no longer applies.

END OF AMENDMENT MAP V4
