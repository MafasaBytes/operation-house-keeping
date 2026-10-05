# Checked-temperature contract preparation package v4 (successor)

**Date:** 2026-10-04.

**Status:** successor contract for the owner-authorized consolidated correction.
It records amendments; it is not acceptance. Gate 1 acceptance and the
commit/build-binding step remain owner-gated.

**Predecessors** (each preserved byte-for-byte):

- v3 `1a9eccbd…5572` (approved Gate 1 baseline);
- v2 `e7dbccec…0811`;
- original `c3de4cb9…`.

**Governing commitments (unchanged):**

- corrected design v2 `68da70f2…`;
- focused confirmation v2 `f0259702…`.

## Members

| Member | Purpose |
|---|---|
| [CONTRACT.md](CONTRACT.md) | v3 text verbatim plus §12 amendments, which supersede the cited clauses |
| [AMENDMENTS.md](AMENDMENTS.md) | Explicit old-to-new contract, schema, policy and witness map |
| [schemas.json](schemas.json) | v4 schemas (vendored byte-identically by the implementation) |
| [policy.json](policy.json) | `ct.policy-edition.v4` |
| [witnesses.json](witnesses.json) | 135 cases: 103 original, 1 amended, 31 new |
| MANIFEST.json | Binds every other member |

Not carried forward, because Gate 2 is deferred:

- `RESOURCES.md` and `PLAN.md` (the v3 copies govern G1; G2 needs resizing);
- `WITNESSES.md` (the readable table; `witnesses.json` is authoritative).

## Pending owner choice

**C1, T1 acquisition-time binding (§12.3).**

The question: which evidence instant must fall within
`[acquisition.started, acquisition.ended]`? The candidates are the snapshot
`as_of`, the question `as_of` and the occurrence `finished_at`. Must that instant
follow `model.context.as_of`?

Why it is open: no committed or reproducibly derivable T1 public evidence has a
later instant. Every instance carries `2026-08-07T20:30:00Z`. A positive witness
would need new synthetic upstream evidence generation (the source-interpretation
and assertion chain), which is not authorized here.

Smallest exact proposal: occurrence `finished_at` within the acquisition window,
with `acquisition.started` ≥ `model.context.as_of`. It is not implemented.

END OF PACKAGE README V4
