# T1 rebind tool: implementation receipt

Date 2026-10-23. Implementation grant: tool and tests only. **Nothing was executed**: no tool run, application
command, test, collection, import, compilation, syntax check, linter, probe, fixture generation, K, Git
command, checkout, commit or merge. Verification was static reading only.

- **Governing specification:** `docs/superpowers/reports/2026-10-22-t1-rebind-implementation-specification.md`,
  SHA-256 `42d92411d35a3d7764930ac8867329e643e3442d95dba07f2789316b03a4ff61`. Verified before and after; unchanged.
- **Dispositions applied:** D-RB1 to D-RB7 as granted. No attestation text was chosen, no approval record was
  written, and no runtime authority was issued. Test attestations are labelled TEST-ONLY.

## 1. Files

| Path | Status | SHA-256 | Logical B | Allocated B | Lines |
|---|---|---|---|---|---|
| `tools/fixtures/t1_rebind.py` | new | `caf238d2debdbb99d73e7df49f0aa654607c73e02ab97658d8c4b54e1cba0095` | 67,935 | 69,632 | 1,327 |
| `tests/tools/test_t1_rebind.py` | new | `941f70cd6a48ae47980fd3959763796a7ee35aeb85084ba186636bafb9cbc14b` | 65,370 | 65,536 | 1,182 |
| `tests/t1_simulation/request_fixtures.py` | new | `d17270ca20a508bba46cd2a1ed7be576eb3a76efb75781a1f4ee6c226bc92625` | 2,202 | 4,096 | 49 |
| `tests/t1_simulation/test_maintained_increment.py` | edited | before `1a3bcb55…dd68027` (14,616 B), after `a52277423c31427af5a979784a304fe2e8a28b2cb2d31a3425ce7ac48c395889` | 13,074 | 16,384 (unchanged) | 228 |

- **New directories:** `tools/fixtures`, `tests/tools` (2 of 3 allowed). No `tests/tools/__init__.py`: several
  sibling test directories have none and `pyproject.toml` sets `pythonpath = ["."]`. Collection is unverified.
- **The helper edit:** `request_for` and `request_inputs_for` moved verbatim into `request_fixtures.py`.
  `test_maintained_increment.py` imports and re-exports them, so `test_command_integration.py` (unchanged,
  `a2d0543d…`) keeps working without edits.

## 2. Implementation summary

- **Interface:** `python3 -I -B tools/fixtures/t1_rebind.py stage1|stage2|stage3 --flag value ...`, using the
  flags of §6.1. Refusals are one canonical JSON line with exits 2/3/4/5/7, no traceback and no absolute path.
- **Stages:**
  - stage 1 renders policy′, P′ and A0′;
  - stage 2 checks B0′ (§6.3), then renders S′, X′, E′, J′ and G′;
  - stage 3 checks M′ membership (§7.4, including the 59-character `id` rule), then renders R′ and copies
    evidence′ byte for byte.
- **Safeguards:**
  - the rule table with old-value and kind preconditions, and a post-render leaf-diff invariant;
  - source pins with the `prior_bundle` map, plus inventory, hash names, canonical form, topology and the
    completeness check;
  - the output scan, and limits matching `t1_records.parse` (finite floats accepted; floats refused only in the
    nine rendered kinds);
  - O_NOFOLLOW capped reads, exclusive writes under `PARTIAL` with readback, and earlier-stage review pins;
  - lineage checks (source pins, stage-1 review inside stage 2);
  - packets carrying the exact candidate bytes, and `not_approved` / `NOT AUTHORIZED BY THIS PACKET`.

## 3. Tests written (not run)

They cover T01–T16, plus: the parser, usage, the internal-error path, the isolated `-I -B` entry point, the
stdlib-only import check, the Appendix A pilot pins (37/14/30, 69 distinct), the byte caps and the early
output-count refusal.
- **The source fixture is generated in tmp:** a build-1 acquisition, then R built from its actual evidence.
- **The chain runs in process:** stage 1 → selection on `TestDoubleBuild('2')` → stage 2 → acquisition →
  stage 3, and T06 runs the maintained `t1-reassessment-prepare`.
- **Expected cost is heavy:** about four acquisitions in total.

## 4. Focused review

One read-only `code-reviewer` pass over the final files found no Blocker and no Major. It judged B1, M1 and M2
correct on reading and traced every expected refusal code.
- **Fixed, with a focused readback that confirmed them:**
  - Minor 1: per-kind byte caps on rendered records (G 4,096; J and policy 16,384);
  - Minor 4: early refusal when the pins imply more output files than the fixed caps allow;
  - the test gaps and the tautological assertion.
- **Open, because the specification text contradicts itself (reported, not resolved):**
  - Minor 2: a historical digest inside a rendered source record's own provenance text is refused, per §4.2,
    although §3.5 says it is not;
  - Minor 3: the output scan runs before `mkdir` (no `PARTIAL`), and failures after `mkdir` in readback exit 7
    rather than 5.
- **Low, recorded:**
  - extra entries refuse with exit 4;
  - earlier-stage renders are labelled `copied_generated` with a `source` field;
  - the packet is listed in a `packet` field and the review gains a `rendered` map (both additive);
  - an M′ with `PARTIAL` refuses `REBIND_DEPENDENCY_MISMATCH`, per §7.4.1;
  - `StageInput` trusts more than it strictly needs to;
  - unresolved references are not required to resolve;
  - zero B refuses `REBIND_USAGE`, and the historical B refuses `REBIND_INPUT_INVALID`.
- **Not verified:** runtime behaviour, collection, success of the maintained commands, test duration, and
  byte identity against HEAD.

## 5. Accounting

- **This grant:** new logical bytes 135,507 plus this receipt; positive growth of the edited file is 0. New
  allocated bytes 139,264 plus this receipt. Directories report 0 allocated blocks on this filesystem.
- **Not borrowed:** no held capacity or spent execution reservation.
- **Final charges and balance:** reported in chat, so this file holds no self-hash.

## 6. Preservation

- Unchanged and re-hashed: the specification, the reconciliation `7d8bff11…`, L2 `74a39d87…` and `6bca403b…`,
  and the pilot producer manifest `fe2d646e…`.
- Untouched: everything under `applications/` and `backend/`, sealed evidence and runtime workspaces.
- R1's 141 results, the three deferred cases, scoped L1 and synthetic end-to-end acceptance keep their
  attribution. D-P remains open.
- The earlier scratch-file incident stays disclosed in its own record.

END RECEIPT
