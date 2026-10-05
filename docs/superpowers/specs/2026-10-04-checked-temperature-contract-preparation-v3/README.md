# Checked-temperature contract preparation package v3 (successor)

**Date:** 2026-10-04.

**Status:** documentation-only preparation for owner evaluation. This package
authorizes no implementation, test, qualification or execution. It is **not**
evidence of executable readiness: no application code has exercised its
schemas, witnesses, example or limits.

**Predecessors** (each preserved byte-for-byte):

- v2: `../2026-10-04-checked-temperature-contract-preparation-v2/`, `MANIFEST.json`
  `e7dbccec4c7fc65947cd1847f36b6306daed10597399bec8106a82660c2b0811`;
- original: `../2026-10-04-checked-temperature-contract-preparation/`,
  `MANIFEST.json`
  `c3de4cb9d5868454e8d666267d9dd9cf58f33d69500065c1f648005bf3da48c2`.

**Governing commitments (unchanged):**

- corrected design v2 `68da70f2…`;
- focused confirmation v2 `f0259702…`.

## Scope of v3

Only the two owner-specified defects are corrected, together with everything
they affect:

- **A:** the mutual digest dependency between the reassessment request and its
  execution authority (v2 CONTRACT §6.2);
- **B:** the incomplete closure root set, reference edges and prior-material
  carriage (v2 CONTRACT §7.3).

Scoring, applicability precedence and manual adoption are not reopened.
[CORRECTIONS.md](CORRECTIONS.md) is the exact change map.

## Members

| Member | Purpose |
|---|---|
| [CONTRACT.md](CONTRACT.md) | Specification. v3 rewrites §6 (execution target, split authority, admission, construction order, stage-5 order) and §7.3 (roots, edges, carriage) |
| [schemas.json](schemas.json) | 22 closed record schemas, 24 typed-reference kinds, 39 limit keys |
| [policy.json](policy.json) | Edition `ct.policy-edition.v3`: 39 limits, 34 refusal codes, catalogue `ct.conditions.v2`, 7 local roles |
| [WITNESSES.md](WITNESSES.md) / [witnesses.json](witnesses.json) | 19 witnesses, 104 cases (33 positive, 71 adverse), 179 invocations; hand-derived, not executed |
| [construction-example.json](construction-example.json) | Worked construction order (X → E → O → R → A → D) with computed digests |
| [RESOURCES.md](RESOURCES.md) | Re-derived reassessment limits and Gate 2 storage for the larger matrix |
| [PLAN.md](PLAN.md) | Gates 0–2 (structure unchanged), updated counts |
| [CORRECTIONS.md](CORRECTIONS.md) | v2 → v3 change map |
| MANIFEST.json | Binds every other member by SHA-256 and bytes |

## Conflicts with the governing design

None. CONTRACT §11 lists five specification completions (c1–c5) so the owner can
see them. Each is a tightening or a clarification inside design "exact
target, scope/time/basis" and §6 "complete typed closure":

- **c1:** per-purpose issuer roles;
- **c2:** the execution authority's validity window must contain the
  acquisition;
- **c3:** `P0` is defined per procedure;
- **c4:** bundle files are exactly canonical bytes;
- **c5:** closure, reassessment and adoption records are never closure members.

## Pending owner choices (none recorded as approved)

| ID | Choice | State |
|---|---|---|
| D1–D10 | As listed in the v2 README (D7, D8 and D10 revised in v2) | pending |
| O3 | Does `observation_error_bound` gate selection as well as reassessment? | pending (v2 recommendation: both phases) |
| O5 | Does a claim bind the whole model revision or only the governing parameters? | pending (v2 recommendation: whole revision) |
| A1 | Synthetic allowlist content | pending (v2 recommendation: without `observation_error_bound`) |
| G1 | Gate 1 TDD allowance | pending (unchanged proposal: 40 launches, 512 MiB) |
| G2 | Gate 2 allowance | pending. **Re-proposed:** the v2 L1 figure (288 MiB) no longer covers the cap-based bound of 319,553,536 B, so L1 is now 352/384 MiB. L2 is unchanged. |

## Static checks actually performed

These used standalone Python scripts and the pre-installed third-party
`jsonschema` 4.26.0 library. No repository or application code was imported or
executed, and no dependency was installed. All 26 checks pass:

- JSON parse of the four JSON members.
- Schema consistency:
  - no dangling `$ref`;
  - every `x-target` is a known kind;
  - no required field missing from `properties`;
  - no open object;
  - 22 records and 24 kinds; only `ct.evidence-content` and `nm.evidence.v1` lack
    a record schema.
- Closure member kinds (21) exclude closure, reassessment and adoption records.
  Descriptor member targets equal the 12 selection kinds.
- Every refusal code used in the witnesses (25) and in CONTRACT is defined in
  `policy.json` (34).
- Witness totals:
  - recounted as 19 / 104 (33 positive, 71 adverse) / 179;
  - case IDs are unique;
  - `WITNESSES.md` lists every case;
  - only PS1, PS2, PS3, IN9 and IN10 differ from v2 among the old rows.
- Limits:
  - the 39 keys match between schema and policy;
  - the key ceilings are cited in CONTRACT or RESOURCES;
  - the non-policy embedded maxima are structural constants only.
- Arithmetic:
  - 395 ≤ 400 objects;
  - 2,621,440 decoded bytes;
  - file and bundle caps;
  - Gate 2 bound of 319,553,536 logical and 343,617,536 physical bytes against
    the re-proposed allowance;
  - the counting rule reproduces v2's 69/17/29/39 on the v2 matrix.
- Construction example:
  - all five records validate against `schemas.json`;
  - digests recompute;
  - none of X, E, R or A references itself or a later record;
  - the target joins are correct.
- Negative structural twins rejected by the schema:
  - the v2 authority (`target_request_sha256`);
  - an execution authority with phase `selection`;
  - the v2 `prior_selection.manifest_sha256`;
  - a request without `execution_target`;
  - an execution target carrying an authority field;
  - a descriptor with a nested retained selection;
  - the v2 descriptor `files`;
  - the v2 single-`root` closure;
  - an adoption closure member.

  A v3 closure skeleton is accepted.
- Kind restrictions (`x-target`) and roles (`x-allowed-roles`) are custom
  keywords. JSON Schema validation does not enforce them; they are stage-3
  semantics (`REFERENCE_KIND_MISMATCH`, `ROLE_MISMATCH`). The checks confirm they
  are declared. The EO2/EO3 refusals therefore depend on the future
  implementation.
- Relative links resolve. There is no trailing whitespace or tabs, and every
  Markdown member ends with its marker. `git diff --check` does not apply to
  untracked files, so no result is claimed.
- Manifest digests recomputed. The v2 and original manifests and all their
  members were re-verified unchanged.

## Preservation record

| Item | Value |
|---|---|
| HEAD | `2f0afbd368105b99f0b8548ffece107918386e3d` (unchanged) |
| `.git/index` SHA-256 | `09ae83d4c39ead36e682600c851b5d355246c84708f8791080cc97b3183ff476` (unchanged) |
| Tracked modifications | `.gitignore`, `tests/reassessment_profile/bounded_pytest_runner.py` (unchanged; file SHA-256 `010b1010…`, `97999fad…`) |

Nothing was staged, committed, cleaned, published, or written to runtime or a
ledger. No dependency was added.

IN-001 and CI-001 remain open and unselected.

END OF PACKAGE README V3
