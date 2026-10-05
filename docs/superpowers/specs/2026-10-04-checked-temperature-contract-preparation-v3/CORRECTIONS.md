# Correction map: successor v2 to successor v3

v2 (`MANIFEST.json` `e7dbccec4c7fc65947cd1847f36b6306daed10597399bec8106a82660c2b0811`)
and its nine members are preserved unchanged. The v2 map from the original
package remains at `../2026-10-04-checked-temperature-contract-preparation-v2/CORRECTIONS.md`.

Scoring, applicability precedence and manual adoption are not reopened. No
check was weakened.

## Correction A: acyclic authority binding (v2 CONTRACT §6.2)

| v2 | v3 |
|---|---|
| `ct.authority.v1.target_request_sha256` = request digest, while the reassessment request referenced the execution authority (`result.execution_authority`). This is a mutual digest dependency that cannot be constructed. | `target_request_sha256` removed. `ct.authority.v1` is a closed `oneOf` by purpose: **evaluation** → `target` ref `ct.request.v1` (completed request; externally pinned); **execution** → `target` ref `ct.execution-target.v1` (`scope.phase` const `reassessment`). |
| No pre-result target record | New authored kind `ct.execution-target.v1` (role `local_model_proposer`): prior selection refs, selection basis, plan change, model, procedure, instrument, plan. It references no authority, request or result. There are now 24 reference kinds and 22 record schemas. |
| Reassessment request: `prior_selection.manifest_sha256` (raw) | `prior_selection.manifest` is a typed ref to `ct.bundle-manifest.v1`. New `execution_target` ref. Request fields must equal X's (`EXECUTION_TARGET_MISMATCH`). |
| Instrument, model, procedure, plan-change and scope enforcement stated loosely | Explicit table (CONTRACT §6.2). E's `valid` must contain the acquisition interval (c2). E and X are fixed transitively by the request pin (EO13). |
| Stage-5 order unspecified | Fixed order (§6.5): request pin → authority pin → targets → prior material → plan admission → target agreement → scope. PS1 keeps its code. |
| `P0` = "plan captured by the prior selection" | `P0` is defined per procedure (T1 plan; T2 null) (c3). |
| Either issuer role allowed for either purpose | Role bound per purpose (c1, a tightening). |
| — | Construction order and worked example with computed digests (§6.4, `construction-example.json`). |

## Correction B: closure roots, edges and prior carriage (v2 CONTRACT §7.3)

| v2 | v3 |
|---|---|
| `ct.closure.v1.root` = request only; the invocation-referenced evaluation authority and the retained-selection descriptor were unreachable. Under v2's own rules, a well-formed bundle either lacked them (unresolvable reference) or carried them as `UNREFERENCED_MEMBER` | `roots {request, evaluation_authority, retained_selection}`. Each must equal its external pin (or is null for selection). Nothing else is a root. |
| Edges implicit | Every `x-target` field is an edge. Trace entry targets and raw-digest fields are not. Member set = reachable set exactly (`REFERENCE_MISSING` / `UNREFERENCED_MEMBER`). |
| Member kinds: all 23 | Selection: 12 input kinds. Reassessment: plus 9 carriage kinds. Closure, reassessment and adoption records are never members (c5). |
| Descriptor: `prior_manifest_sha256`, `files[9]`, refs to selection, derivation, applicability, build, policy, request. Prior closure merged without a member list; trace, invocation and manifest not carried. | Descriptor: `prior_manifest` ref, `prior_closure {sha256, bytes, roots, members[≤192]}`, refs to invocation, selection, derivation, applicability, trace, build and policy. The prior manifest, invocation and trace are now carried. The prior `closure.json` is rebuilt, not carried. |
| Standalone verify could not check prior material | Verify and replay recheck, with no prior bundle: the manifest pin through R, every manifest entry, and the rebuilt prior closure digest and length (`prior_material_checked`). |
| Bundle file bytes unspecified | Every file is exactly the canonical bytes of its record (c4). |
| Prior-bundle intake timing unspecified | Evaluate intake runs before new-closure assembly and always reports `PRIOR_BUNDLE_MISMATCH`. |

## Affected members

| Member | Change |
|---|---|
| `schemas.json` | `$id` `schemas-v3`. Changed records: authority, request (reassessment), closure, retained-selection, trace, invocation, bundle-manifest, plus the new execution-target. New limit key `retained_selection_bytes`. |
| `policy.json` | Edition `ct.policy-edition.v3`. New limit `retained_selection_bytes` = 32,768 (39 limits). Re-derived `reassessment_unique_objects` (395; fixes v2's stated 389 for a sum of 388) and `reassessment_closure_decoded_bytes` (= 2,621,440). Both values are unchanged. New codes `AUTHORITY_TARGET_MISMATCH` and `EXECUTION_TARGET_MISMATCH` (34 codes). |
| `witnesses.json` / `WITNESSES.md` | New: W18 (EO1–EO13) and W19 (CL1–CL9). Updated: PS1, PS2, PS3, IN9, IN10 inputs. Construction CO1 is common. Totals go from 17/82/154 to 19/104/179 (witnesses/cases/invocations), and harness copies from 3 to 10. |
| `RESOURCES.md` | §3 rows re-derived; reassessment estimate 480 → 615 KB. §4 recomputed: cap bound 273,154,048 → 319,553,536 B. The v2 L1 allowance is insufficient; re-proposed at 352/384 MiB (pending G2). |
| `PLAN.md` | Counts, ten harness mutations, re-proposed L1 figures. Gate structure and Gate 1 are unchanged. |
| `CONTRACT.md` | §0, §1.1–1.3, §5 edition, §6 rewritten (6.1–6.5), §7.2 canonical files, §7.3 rewritten, §7.4 verify flag, §9, §11. |
| `construction-example.json` | New. |

## Substitution and refusal twins

| Positive | Twins |
|---|---|
| EO1 (CO1 completes) | EO2 and EO3 (wrong target kind); EO4 and EO5 (wrong target); EO6 instrument; EO7 model; EO8 procedure; EO9 scope; EO10 time; EO11 and EO12 plan change; EO13 rehashed authority under the unchanged pin |
| CL1 (standalone verify/replay) | CL2 (unrelated member); CL3 (laundered through the descriptor); CL4 (missing root); CL5 (substituted prior record); CL6 (substituted prior manifest); CL7 (forged root); CL8 (unpinned authority); CL9 (invalid prior closure) |

END OF CORRECTION MAP V3
