# EA-001 Slice B Adversarial Acceptance Matrix

Date: 2026-09-04

Status: mapped; Slice B execution blocked at the preimplementation contract gate

## 1. Matrix

| Row | Planned executable Slice B acceptance | Current disposition |
|---|---|---|
| A01 | Exact valid DS-004 route, selection, closure, and result. | Planned after gate. |
| A02 | Payload mutation maps to `checksum_mismatch`. | Planned after gate. |
| A03 | Payload plus carried-checksum replacement fails named store validation. | Blocked by named-artifact lower capability. |
| A04 | Metadata mutation changes a source fence or causes digest refusal. | Planned in-horizon; blocked for a selected pre-horizon seed. |
| A05 | Raw ID/reference/locator/request/attempt/run substitutions map to provenance closure failure. | Planned after gate. |
| A06 | Extraction wrapper/manifest/raw/adapter/item/extractor disagreement fails closed. | Planned after gate. |
| A07 | Missing extraction and quarantine maps to `extraction_incomplete`. | Planned after gate. |
| A08 | Same byte read supplies metadata hash and parse; second-access twin cannot pass. | Accepted lower fact; Slice B mapping planned. |
| A09 | RFC 6901 escape ordering and malformed escape behavior remain exact. | Accepted lower fact; Slice B mapping planned. |
| A10 | Pointer/value/type/coercion mismatches map to observation-content mismatch. | Planned after gate. |
| A11 | Ambiguous/malformed/oversized JSON cannot produce a content match. | Accepted lower fact; Slice B mapping planned. |
| A12 | Observed/omitted/empty/failed/quarantined routes remain distinct and ordered. | Planned after gate. |
| A13 | Missing temporal attempt maps to `temporal_occurrence_absent`. | Planned after gate. |
| A14 | Every governed temporal occurrence substitution maps to inconsistency. | Planned after gate. |
| A15 | Unequal independently valid source/temporal attempt or occurrence sets map to parity failure. | Planned after gate. |
| A16 | Inclusive cutoff and one-microsecond exclusion. | Planned after gate. |
| A17 | Full `AttemptOrderKey` tie-break is enumeration independent. | Planned after gate. |
| A18 | Receipt membership and effective-time coverage remain separate. | Planned after gate. |
| A19 | No-response failure uses `finished_at_no_response`. | Planned after gate. |
| A20 | Source time and clock segments are disclosure-only. | Planned after gate. |
| A21 | Cross-clock comparison misuse raises `EA_TIME_COMPARISON_UNSUPPORTED` before I/O. | Exact trigger field/API is not present in the pinned request. Owner pin required. |
| A22 | Byte-identical attempts/occurrences remain distinct; shared source objects index once. | Planned after gate. |
| A23 | One selected pre-horizon seed is carried and labelled. | Planned; its required source fence is blocked. |
| A24 | Seed is excluded from coverage and creates no pre-horizon completeness claim. | Planned; its required source fence is blocked. |
| A25 | Exact no-observation outcome remains distinct from failed coverage. | Planned after gate. |
| A26 | Lifetime history over 4,096 succeeds when horizon membership is bounded. | Planned after gate. |
| A27 | In-horizon excess refuses without sampling/truncation. | Planned after gate. |
| A28 | Count/byte limits precede retention and reject boolean/coercible values. | Public fixed-limit model fields are not pinned. |
| A29 | Path/traversal/symlink/device/socket rejection and diagnostic redaction. | Accepted lower fact; Slice B mapping planned. |
| A30 | Mutation before the initial source token may be captured without a false concurrent-change issue. | Planned after gate. |
| A31 | Source mutation after the initial source token and before source material refuses. | Reproduction fails for a selected pre-horizon seed. |
| A32 | Source mutation during named reads refuses or fails same-read checks. | In-horizon path planned; selected seed is not fenced by either token. |
| A33 | Source mutation after reads and before the final source token refuses. | Reproduction fails for a selected pre-horizon seed. |
| A34 | Temporal mutation before/during the transaction is coherent in memberships or refuses. | Planned after gate. |
| A35 | Temporal mutation after transaction and before final temporal token refuses. | Planned after gate. |
| A36 | Crossed source/temporal mutations cannot yield false equal parity. | Cannot prove while seed source dependencies are outside source fences. |
| A37 | Post-final-fence mutation is explicitly not detected and makes no current/global claim. | Planned after gate. |
| A38 | Non-DS-004 file families return `unsupported_operational_evidence`. | Planned after gate. |
| A39 | Exact AST/import isolation in both directions. | Planned after gate. |
| A40 | Exact public fields exclude semantic/model/freshness/physical claims. | Missing result field sets and exports block exact equality. |
| A41 | Exact age is disclosed without threshold or status effect. | Planned after gate. |
| A42 | Empty/omitted/failed/quarantined coverage yields the exact incomplete issue only as an operational disclosure. | Planned after gate. |
| A43 | Source unavailable, temporal unavailable, no observation, and incomplete coverage remain distinct. | Planned after gate. |
| A44 | Every mixed scope/horizon/cutoff/policy dimension rejects. | Planned after gate. |
| A45 | Forgery, cycles, extras, union/index/order/derived/result substitutions reject at every public boundary. | Missing result field sets block exhaustive boundary assertions. |
| A46 | Coherent snapshot-plus-fingerprint replacement may validate structurally without a mutation claim. | Planned after gate. |
| A47 | Independent expected fingerprint reports exact match/mismatch. | Planned after gate. |
| A48 | Offline validation performs zero dependency calls and reports both store axes `not_rechecked`. | Missing validation-result fields block exact assertion. |
| A49 | Enumeration reversal and hash seeds 1/7/12345 yield exact canonical bytes/fingerprint. | Planned after gate. |
| A50 | No network, connector, extraction, write, ambient clock, environment, or model mutation. | Planned after gate. |

## 2. Boundary injection plan

Controllable public reader/query doubles would inject mutations at all eight
intervals around initial tokens, material reads, parity, final tokens, and the
post-final non-detection point. Each double would record call order and reject
unexpected I/O. Separate cases would cover source-only, temporal-only,
crossed, material/token disagreement, and immediate post-fence mutations.

This matrix does not weaken or mark passing any blocked row. No Slice B test or
runtime surface has been created while the lower-seam discrepancy remains.

END OF EA-001 SLICE B ADVERSARIAL ACCEPTANCE MATRIX
