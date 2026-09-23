# Slice 5 clone/retention clarification — reduced approval alternative

Recommend the reduced alternative below, **not the frozen candidate unchanged**.
Candidate SHA-256 verified:
`6a1b7ad7cd1e52f75ae4eb4e2572cc805587e24532729cbaeb0e3ef3f02d846d`.
[Candidate](2026-09-24-reassessment-slice5-retention-correction-candidate.md) remains
byte-identical. This note changes only the proposed checkout construction/allocation;
all other category caps, preservation rules and qualifications carry forward. No
clone, test, operational-cap change, production edit or commit was performed.

## What the three roots establish

The precise test is `tests/applications/bounded_decision_workflow/test_s7_release.py`.
Its helper (lines26–30) currently clones locally with `--no-hardlinks`, then checks
out the requested commit. At lines54–98, source-0 and source-1 alternately verify
and replay the other's twelve constructed bundles and compare actual source/build
identity. Both roots must exist simultaneously for those cross-root checks, and the
test expressly requires independent Git databases. That requirement is preserved.
At lines112–136 the historical test separately verifies/replays the accepted S6
bundle. It does **not** require three databases to participate simultaneously.

| Root | Revision and purpose | Current full-tree/object payload projection | Why it coexists |
|---|---|---:|---|
| source-0 | Exact frozen final candidate F; first independent evaluate/verify/replay root | 274,469,605 +172,897,771 =447,367,376 | Needed with source-1 during the cross-root test |
| source-1 | Same F; second independent database and verifier/replayer | 447,367,376 | Same reciprocal test; not a repair contingency |
| accepted-source | `c37c24ee50667121d6b2dc4739aa3b7d12825c96`; actual matching historical build | Settled 73,827,366 +172,897,771 =246,725,137; old helper first materializes current tree | Separate sequential test; retaining earlier operational roots under the current no-cleanup rule produces coexistence, not an inherent three-way semantic requirement |

F is not invented here: execution must freeze it after repairs. Measurements use
administrative HEAD `1647c3931582b8183d00aedaaae2d959dd908fc8`; remeasure after approval.
All projections exclude other Git metadata and possible growth unless explicitly
reserved. The old transient third current tree is incidental construction, not
acceptance evidence. Nor does acceptance require three materialized copies of all
historical reports forever. No deletion of existing evidence is proposed.

Breakdown of measured working trees:

| Committed files | Current tree | Historical tree |
|---|---:|---:|
| applications/backend, including tracked data | 2,334,056 | 2,016,579 |
| reports/evidence under docs/superpowers/reports | 265,212,274 | 65,295,263 |
| other tracked files | 6,923,275 | 6,515,524 |
| total | 274,469,605 | 73,827,366 |

Each full local clone also copies the measured172,897,771-byte Git object store,
including historical representations; this is distinct from working-tree archives.
No .venv, unrelated untracked artifacts or ext4 runtime corpora enter Git cloning.
Environments remain external, explicitly provisioned prerequisites, with no copied
interpreter/dependency tree. Generated bundles, logs and faults are outside clone
source paths and retain their own category charges. Original archives remain in
place. A tracked archive copied into a working tree counts again; an object-store
representation also counts—neither is treated as free because content overlaps.

## Minimum safe construction proposed from this inspection

Shared-object worktrees or Git alternates could reduce operational storage, but
would weaken the independent-database test if used for source-0/source-1. Do not
use them. A historical worktree might satisfy its narrower clean-build requirement,
but would introduce an explicit backing-repository dependency. This proposal avoids
that additional recovery relationship and keeps all three databases self-contained.

Instead, propose a test-helper-only construction adjustment after approval:
local `git clone --no-checkout --no-hardlinks`, establish an explicit **non-cone
sparse working-tree allowlist before any checkout**, then detach at the exact
requested revision. No network, shared alternates, shallow history, object filtering
or missing-object fetch. All Git objects are still copied independently. Only
materialization of unnecessary working-tree files changes. No production build
validation or result expectation changes. Do not fall back to a full working-tree
checkout if configuration fails; stop before those writes.

For both current roots, the exact allowlist is:
- Entire `applications/` and `backend/`, including every tracked data file and lock.
- `docs/superpowers/reports/2026-09-23-reassessment-preparation/package.zip`
  (33,618,258 bytes), providing committed standalone fixture/authority recovery.
- The following six governed runtime contract files (159,325 bytes total):
  `docs/superpowers/specs/2026-09-16-maintained-admissibility-enforcement-shared-reference-corrected-design.md`;
  `docs/superpowers/reports/2026-09-16-maintained-admissibility-amendment/AMENDMENT.md`;
  that directory's `policy.json` and `schemas.json`;
  `docs/superpowers/reports/2026-09-16-maintained-admissibility-consolidation/CONTRACT-AND-PLAN.md`;
  that directory's `build.schema.json`.

Historical root allowlist: complete `applications/` and `backend/` only, at the
historical revision. Its recovered seven-file S6 input bundle remains separately
retained test input, exactly as in the current test. Allow for sparse initialization
materializing the current applications/backend briefly before detaching:2,334,056
rather than2,016,579 bytes. No whole current tree need ever be materialized.

Why this preserves the inspected tests: `build.identity()` hashes every tracked
application file and its named public backend files; all remain present.
`measurement_build.identity()` reads maintained Python files under both trees, lock,
Git HEAD and external environment identity; these remain present and unchanged.
Governed build/closure/policy readers have the six exact files above. Test requests
and snapshots come from application examples. The S7 test driver itself runs in
the full repository; only its CLI subprocesses run from these roots. Current
reassessment clean-delivery fixtures recover from the committed package inside the
root, never unrelated untracked preparation. Sparse roots are not advertised as
complete materializations of all documentation, or as independent fresh dependency
installations. Unmaterialized tracked history remains recoverable from **each root's
own** complete Git database, not a cache or the original checkout.

Required future construction checks: exact HEAD; clean Git status; no alternates,
shared object backing or fetch requirement; enumerate the allowlist and compare
its bytes against committed blobs; compare actual build witnesses with F's witness;
run the existing reciprocal test without weakened assertions, including its missing-
witness adverse/valid twin. Exercise standalone reassessment delivery/replay using
only the root, captured bundle and declared external environment. No runtime success
is claimed from this static inspection. An additional required file must be explicitly
identified and accounted before hydration; no hidden fallback reads. If the allowlist
cannot satisfy the existing gate within its bound, stop rather than weaken the gate.

Operational roots are not themselves the whole proof: preserve command/input/build
commitments, actual outputs, failures and complete retained bundles independently.
Raw corpus evidence and selected exact exports remain recoverable. Do not serialize
three extra copies of each operational clone into evidence exports. Retain the
operational roots in place under the same no-cleanup rule; do not reuse their bytes
as allowance for later attempts. Historical root is not used to assert F equivalence.

## Peak arithmetic and precise reduction

The frozen full-checkout proposal budgeted:
3×447,367,376 =1,342,102,128 payload bytes at the incidental three-current-tree peak.
That alone exceeds the old1,120,927,744 allocation. Its three432-MiB slots total
1,358,954,496; other category caps total653,262,848; sum2,012,217,344.
Adding128MiB file-tail +32MiB directory/metadata reserve gives2,179,989,504.
That arithmetic was conservative, but was **not proof the copying was necessary**.

The proposed smaller construction has these measured components and hard envelopes:

| Root | Working files | Own Git objects | Payload projection | Proposed slot |
|---|---:|---:|---:|---:|
| source-0 | 36,111,639 | 172,897,771 | 209,009,410 | 218,103,808 (208MiB) |
| source-1 | 36,111,639 | 172,897,771 | 209,009,410 | 218,103,808 (208MiB) |
| historical, initialization peak | 2,334,056 | 172,897,771 | 175,231,827 | 184,549,376 (176MiB) |

Measured simultaneous payload projection593,250,647; proposed checkout slots total
**620,756,992 (592MiB)**. Headroom9,094,398 per current root and9,317,549 historical
covers bounded source/object growth, sparse index/config and other Git metadata;
remeasure/reserve before writing. These are hard scheduling ceilings, not guaranteed
future requirements. No packed-transfer/compression saving is assumed. No fourth
clone. Reuse source-0/source-1 for clean delivery.

Only checkout cap changes from the frozen candidate, down704MiB =738,197,504:
- **New retained/high-water cap:1,274,019,840 bytes.**
- **Combined H+Q+new:1,350,579,940 bytes.**
- **New physical reservation:1,441,792,000 bytes**, retaining160MiB padding/metadata.
- Increase over the previously approved1,120,927,744 is153,092,096 (146MiB),
  not the frozen candidate's891,289,600 increase.

All category ceilings can coexist: checkout620,756,992 +other653,262,848 =1,274,019,840.
All working-tree material, own Git databases, scratch, logs, faults, raw evidence,
archive copies, recovery extractions and planning documents count concurrently.
Existing H/Q are outside the *new* physical reservation, not granted extra writes.
32,768-file/4,096-directory ceilings and allocated-block monitoring remain. At most
4,100 files and400 directories per clone give additional per-clone allocation
reserve20,070,400; three clones plus that padding =680,968,192, within the overall
logical-plus160MiB envelope. Reserve producer-specific demand before writes; neither
sparse materialization nor process file-size limits replace aggregate enforcement.
No statement here proves unknown full-suite scratch fits the unchanged128MiB
regression category. Unknown/excessive demand must stop; no automatic cap extension.

The82MiB reallocation is unchanged and explicitly covers the enumerated bounded plan:
- Inputs:18,762,363 existing +48×1MiB control/calibration sources =69,094,011,
  below71,303,168 by2,209,157. Final-core changed inputs go to the dedicated slots.
- Outputs:19,646,652 existing +78×1MiB replay/delivery/resource/internal outputs
  =101,435,580, below103,809,024 by2,373,444. Core refresh outputs use their slots.
- Exports:65,423,591 existing +64MiB future selected evidence =132,532,455,
  below134,217,728 by1,685,273, before charging25,743-byte frozen candidate and this
  note. Sources and exports both count. Complete published bundles retain closure;
  raw R remains retained in place. No requirement to export every operational clone.
- Four1MiB additional complete recovery copies remain separately reserved. A fifth
  copy or evidence needing more space is a stop, not permission to omit content.

These arithmetic reservations cover the specified counts at their bounded sizes;
they do not establish that every future adverse fixture or export will meet those
sizes. That is an execution preflight/enforcement obligation. The108 pending matrix
commands,72 planned refreshes, separate controls/dossiers, regression and clean-
delivery duties remain as enumerated in the frozen candidate, with no removal.

## Slot semantics and owner gate

**72 refresh slots are planned final-candidate qualification**, not discretionary
repair retries. They permit one designated core case each at one frozen candidate.
**16 additional contingency slots** separately cover bounded calibration/repair or
focused reruns. Each slot: at most1MiB changed input/scratch +1MiB output/scratch;
32KiB stream and16KiB metadata charged to their separate categories. Two-MiB slot
bounds remain subject to unchanged production input/output/work limits. Planned
refreshes cannot be relabeled to expand repair authority; failed refreshes consume
their designated slot, and a retry consumes a contingency. No automatic second sweep.

All16 historical attempts remain consumed and preserved, including failed assertions,
plus their3,309,000 payload bytes and separately charged logs/indexes/export copies.
Total accounting:16 historical +72 planned +at most16 contingency =104 slots.
Repairs category180MiB =4MiB historical envelope +144MiB planned +32MiB contingency.
Stop before slot exhaustion, any category/aggregate/physical/file-count overflow,
unknown write demand, or any need to weaken a test/build/recovery requirement.

**Recommended single approval:** adopt this precisely reduced alternative together
with the frozen candidate's unchanged remaining rules; authorize only the described
test-helper checkout construction/verification and already-scoped Slice5 resumption.
This is not approval yet, not a production semantic amendment, and not final acceptance.
The frozen candidate is retained as historical proposal; its three-full-tree size
assumption is superseded only if the owner approves this note. No corpus or cap
changed during this static clarification.

END OF CLONE RETENTION CLARIFICATION — OWNER APPROVAL REQUIRED.
