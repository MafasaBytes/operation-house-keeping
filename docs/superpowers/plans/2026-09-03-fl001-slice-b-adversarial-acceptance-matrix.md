# FL-001 Slice B Adversarial Acceptance Matrix

Date: 2026-09-03

Status: executable Slice B matrix; evidence is completed by pinned tests

| ID | Boundary | Required executable result |
|---|---|---|
| B01 | Public surface | Exactly four signatures, exact exports, field order, and literal order pass by equality. |
| B02 | Registration | Absent FRG is `not_registered`; present FRG is `registered` with exact FRG/PRG indices regardless of FLD/support. |
| B03 | Conclusions | All five declaration conclusions and four lineage summaries are reachable exactly where specified. |
| B04 | Findings | Findings emit only in normative order and never select a winner. |
| B05 | Correction roots | One root, fork, convergence, corroborating roots, disagreement, inactivity, withdrawal, and replay derive exactly. |
| B06 | RC1 PCN | Every reachable PCN activity/health pair derives its accepted alignment; `inactive/current` rejects. |
| B07 | RC1 PIF | Every reachable PIF activity/health pair derives its accepted alignment; `inactive/current` rejects. |
| B08 | Support | Exact topology, all source/sink direction relations, and conflict/inactive/stale/aligned precedence remain orthogonal to FLD conclusion. |
| B09 | RC2 selection | Other-context roots affect no port entry field or membership; `view_independent` is exact, never wildcard. |
| B10 | Registered-empty | Registered port with no exact-context FLD root returns `registered` with empty entries. |
| B11 | Direct parity | Every included port entry equals the direct exact-context declaration payload modulo wrapper fields. |
| B12 | Hyperedge | Participant-index discovery reports one role only and creates no pairwise adjacency or flow claim. |
| B13 | Assertion | FRG/FLD/FLW lookup is typed; only FLD has activity/root health/flow conclusion. |
| B14 | Indices | Missing, duplicate, extra, reordered, substituted, wrong-kind, boolean, negative, and out-of-range indices reject. |
| B15 | Material | Missing/extra/reordered/mixed-revision/stale-ID records and revision substitution reject. |
| B16 | Derived forgery | Context, root, group, finding, support, activity, alignment, status, conclusion, and precedence substitutions reject. |
| B17 | Object forgery | `model_construct`, `model_copy`, hidden extras/private caches, cycles, depth, and graph-size attacks reject. |
| B18 | Store independence | Public result reconstruction performs no store/filesystem/database/network/environment/clock/cache/write access. |
| B19 | Determinism | Reversed source order, reversed predecessor copy order, and multiple hash seeds produce byte-identical result JSON. |
| B20 | Pre-FL absence | All four query families return exact structured absence over the untouched 34-record authoritative ledger. |
| B21 | Historical replay | Explicit historical memberships replay unchanged and return structured flow absence. |
| B22 | Preservation | Authoritative records, revision, Slice A golden bytes/IDs, and accepted PT/VP/BH/ST artifacts remain byte-identical. |
| B23 | Import direction | Kernel flow disclosure imports no upper layer, source, temporal, assessment, occurrence, or fixture module. |
| B24 | Semantic restraint | No result/API asserts physical occurrence, transfer, activity, compatibility, behavior, causality, safety, correctness, diagnosis, or recommendation. |

