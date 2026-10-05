# Checked-temperature contract preparation package

Date: 2026-10-04. Status: **preparation for owner evaluation**. It authorizes no
implementation and no execution.

| Member | Purpose |
|---|---|
| [CONTRACT.md](CONTRACT.md) | Readable specification of the six design §10 prerequisites |
| [schemas.json](schemas.json) | Proposed record schemas (16 kinds) |
| [policy.json](policy.json) | Proposed editions, catalogue, roles, limits, refusal codes, allowlist default and synthetic example |
| [WITNESSES.md](WITNESSES.md) / [witnesses.json](witnesses.json) | 52 hand-derived expected outcomes (not executed) |
| [RESOURCES.md](RESOURCES.md) | Measured sizes, analytical bounds and engineering allowances |
| [PLAN.md](PLAN.md) | Implementation and bounded verification plan, with stop rules |
| MANIFEST.json | Binds every other member by SHA-256 and byte count |

## Prerequisites completed (as proposals)

1. H1/H2 meanings, parameter bounds, baseline eligibility, reference bias, units
   and endpoints (CONTRACT §1).
2. Decoders, editions, the T2 rule, containment and numeric admission (§2).
3. The finite condition catalogue, identities, phases and contradictory
   declarations (§3).
4. Pins, interfaces, local roles and the unresolved policy (§4).
5. Source/build capture and historical replay (§5).
6. Schemas, limits and plan (§6, plus `RESOURCES.md` and `PLAN.md`).

No prerequisite required a new semantic decision beyond what the corrected
design leaves explicitly to preparation. The fixed design rules are not
reopened.

## Owner decisions required (each a concrete proposal; alternatives in CONTRACT)

| ID | Decision | Proposal |
|---|---|---|
| D1 | H1 offset | exactly `[0,0]` |
| D2 | H2 offset domain | `0 < lo ≤ hi ≤ 50` °C |
| D3 | Reference bias bound | `[−10, 10]` °C; required, no default |
| D4 | Numeric admission | at most 6 fractional digits; 32 digits per rational part; scalar domain `[−200, 1000]` °C |
| D5 | T1 decoder edition | literal low `(−∞,56]` / gap `(56,59]` / high `(59,∞)`; cut points not caller-supplied |
| D6 | Hard-interval plan | `0 < w ≤ 5` °C; `w = 0` refused; no default plan |
| D7 | Condition catalogue and exclusion predicate | 4 conditions; conclusive exclusion only by a non-overlapping declared validity interval or an exact anchor mismatch |
| D8 | Roles and unresolved policy | 6 unauthenticated local roles; default allowlist empty; synthetic example permits unresolved calibration, mapping and hold only, if selected |
| D9 | Build re-baseline | Adding checked modules changes current build identities; legacy NM/NR bundles from `2f0afbd` then replay only in a reconstructed `2f0afbd` environment |
| D10 | Limits and next step | The `policy.json` limits; one bounded witness launch of 128 MiB / 4,000 files / 800 dirs |

**Disclosed discrepancy.** The three-region decoder of D5 comes from the
2026-10-01 experiment model, not the committed P case, whose decoder is two
regions split at 50. See CONTRACT §0.

## Static checks performed

- Both frozen commitments were verified before work: design v2 `68da70f2…` and
  confirmation v2 `f0259702…`.
- JSON parsing of every JSON member.
- Code-coverage check: every refusal code used in the witnesses is defined in
  `policy.json`.
- Relative-link check.
- A trailing-whitespace scan of every package file found none. `git diff --check` was
  attempted but does not apply to untracked files, and the `--no-index` form failed on
  its path argument, so no `git diff --check` result is claimed.
- Manifest digests recomputed.
- Witness arithmetic was cross-checked with a standalone exact-rational
  calculation that imported no repository code.
- Existing material was measured with `stat` and closure decoding only.

No application or backend code was executed. No runtime bundle was built.

## Preservation record

| Item | Start | End |
|---|---|---|
| HEAD | `2f0afbd368105b99f0b8548ffece107918386e3d` | unchanged |
| `.git/index` SHA-256 | `09ae83d4c39ead36e682600c851b5d355246c84708f8791080cc97b3183ff476` | unchanged |
| Tracked modifications | `.gitignore` (`/_to_delete/` added), `tests/reassessment_profile/bounded_pytest_runner.py` | unchanged; file SHA-256 `010b1010…` and `97999fad…` |
| Untracked entries (collapsed) | not counted at start | 268 at end, including this package directory; none restored, deleted or reinterpreted |

Nothing was staged, committed, cleaned, published or written to runtime or a
ledger.

END OF PACKAGE README
