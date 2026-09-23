# Slice 5 repair progress and evidence

The original Slice 5 completion claim remains superseded and unaccepted. Historical completion and delivery-review reports are unchanged at SHA-256 `2d0e90a4592c4845d107fbfad22a0f155e60b3cd72d7871c28662614acab84ae` and `24eef24c8c704a60006e18308a1c1372fbddc0b6a7846add35fa2ac7496f2996`.

## Scope-to-test map

| Approved obligation | Repair status | Evidence |
| --- | --- | --- |
| Complete typed closure and authority pin | Partial repair implemented | Real profile envelopes now require a closure object map and `resolve_required_closure` with the invocation selection pin; no real end-to-end fixture is yet executed. |
| Executable build/policy binding | Partial repair implemented | Profile envelopes require `nm.build.v1` with executable status and the approved policy digest; prepared witnesses are rejected. |
| Safe path/file admission and publication | Partial repair implemented | Bundle verification rejects symlink roots and nonregular payload files; full maintained root-containment/ext4 policy is not yet wired. |
| Logical/physical accounting | Unmet | Existing 835-byte fixture measurement remains storage-only; no semantic closure/work accounting is emitted. |
| Independent semantic replay | Unmet | `replay_measurement_bundle` still compares caller-supplied result/trace bytes; it does not reconstruct, re-admit, requalify, or recompute minimax. |
| Exact production command integration | Unmet | The separate verification module remains outside the existing application CLI and accepts caller-supplied replay inputs. |

## Implemented checkpoint

The repair is committed at `7d38e4d59a0622872dff821de7889e5efcbadc52`. The existing storage tests pass (3 tests); previously recorded Slice 1–4 and legacy replay evidence was not rerun. No historical report, package/oracle bytes, dependency, backend, ledger, limit, or unrelated artifact was changed.

The 835-byte seven-file fixture remains synthetic storage material: it contains no real Slice 1–4 result, complete closure, executable build witness, or physical work. It is not evidence of supported measurement delivery.

## Remaining boundary

The approved Slice 5 contract still requires genuine standalone semantic replay and exact command integration. Slice 6 remains limited to runtime budgets, filesystem qualification, fault paths, and the approved proof matrix; it cannot absorb these missing Slice 5 semantics. Slice 5 acceptance therefore remains withheld.
