# Slice 1 cycle-coverage closure

This bounded continuation closes the previously recorded cycle-coverage limitation. It does not accept Slice 1, start a later slice, or reopen the resolved replay attribution.

## Chronology and preservation

At the start of this continuation, the current HEAD was `c1b38de3cd7fa2398cbac2781f123937df5cb8ae`. The original Slice 1 code is `db1e927441a9d84a5398d59f7c83a3b0f2a51d8f`; the earlier administrative checkpoint is `e51fbbe86051a5d253b007af0c56d82c833873f8`. The prior verification report remains byte-for-byte preserved with SHA-256 `3cabd947bd1f10ef8e13bcc6278d746e367c81314d5c1ee7fd219d46f43795f2`. The approved package, manifest, recovery receipt, completion report, and runtime results were not changed.

## Validation order and public boundary

`resolve_required_closure` checks the active path before locating a child, but it verifies each located payload's SHA-256 before parsing it and before traversing its typed edges. A public self-reference therefore requires a payload whose bytes contain the reference digest of those same bytes. The supplied public fixture cannot satisfy that relation with ordinary fixed SHA-256 content; this investigation establishes only that the fixture construction is not available under the approved reference encoding, not a claim of cryptographic impossibility. The public adversarial twin remains valuable: its altered request reference reaches `REQUIRED_REFERENCE_MISSING`, and when a payload is deliberately placed under that altered key it reaches `REFERENCE_DIGEST_MISMATCH`. Neither result is relabeled as observed cycle detection.

## Internal traversal seam

The added test uses a test-only synthetic digest function, scoped by `monkeypatch`, to make a finite in-memory graph representable. It does not alter production code, public admission, digest checks, application commands, or expose a harness switch. Direct S1-to-S1 and indirect S1-to-S2-to-S1 graphs reach `REFERENCE_CYCLE`. A valid diamond with S1 and S2 sharing H1 and P1 completes successfully; edge traversal records both branches while complete-object memoization retains one canonical copy of each shared object. These are internal algorithm tests, not evidence that hash-consistent cyclic public material is admissible.

## Acceptance reconciliation

The frozen obligation must be read in two layers: public-input tests establish digest verification precedence and the first reachable diagnostic; the internal seam establishes active-path cycle handling and legitimate sharing. If the obligation is phrased as requiring a public, SHA-256-consistent cyclic fixture, the smallest correction is to say “public digest-precedence twin plus test-only traversal seam,” preserving the existing contract and diagnostics. No production bypass or weakened validation is permitted.

## Verification

At the closure commit, the focused measurement-contract suite passes 11 tests, including the public missing/mismatch twins, direct and indirect internal cycles, and diamond sharing. The clean replay regression `tests/applications/bounded_decision_workflow/test_s6_cli.py::test_baseline_command_and_exact_replay` passes. The dirty-build refusal attribution remains unchanged: dirty executable state refuses; clean baseline, Slice 1, and final checkouts pass.

No implementation, dependency, backend, resource-policy, package, oracle, runtime-result, ledger, push, merge, or history-rewrite operation was performed. Existing unrelated untracked artifacts remain preserved. Slice 1 acceptance, later slices, and the full proof remain separately gated.
