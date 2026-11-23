# T1 carried-acquisition companion calibration gate, edition 2

This successor incorporates [edition 1](../2026-11-19-c05-companion-gate-v1/CONTRACT.md), SHA-256 `ee27af369d900b318fa81f73e0592fd3725c2131243deb16c477e2972332c226`, with the following resource and edition bindings.

| Binding | Edition 2 |
|---|---|
| Rule on every finding, outcome and check | `ct.t1-calibration-primary-gate.v2` |
| Schema pack | `applications/bounded_decision_workflow/t1_calibration_schemas_v2.json`, 45,030 bytes |
| Pack SHA-256 on every record | `81126f8f63cd6ef5ff4bd3046e814d0a1a1d51680828522ace8ad3910aa25a39` |
| Inclusive canonical UTF-8 byte limits | Finding 23,770, outcome 32,768, check 65,536 |

The parser checks input bytes before decoding. Validation checks canonical bytes including all keys, delimiters, escaped text and operands. Embedded findings meet the same finding limit. Excess size refuses with `SIM_RESOURCE_LIMIT` at `/calibration/record`, class 4. The separate 65,536-byte stdout limit includes its terminating newline.

The finding budget is a conservative bound for the admitted builder described in the [size comparison](../../reports/2026-11-20-c05-finding-size-CORRECTION-COMPARISON.md). Larger schema-shaped records can refuse. A change to upstream cardinalities, widths or emitted fields requires reviewing the bound.

Evaluate, verify and replay use the compiled rule and pack together, including the inline finding. Historical edition 1 commitments require their original pinned verifier. The three v1 record kind names, operand encoding and `producer-checked-primary-calibration-gated-v1` guarantee apply as defined in the predecessor. Only the complete companion package with its bound inputs carries this guarantee. Correction release is disabled.
