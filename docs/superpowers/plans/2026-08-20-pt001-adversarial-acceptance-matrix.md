# PT-001 Slice A adversarial acceptance matrix

Status: PT-001 Slice A implemented and adversarially reviewed; awaiting owner acceptance.

| Area | Required attack | Required result |
|---|---|---|
| Anchor | malformed/case/length/extra fields and nested construct/copy forgery | structural or public typed rejection |
| Anchor | domain/type/state/owner fields | extra-field rejection |
| Registration | absent owner, duplicate port registration, empty/forged evidence | collection invalid; atomic no-write |
| Tokens | missing/wrong `token_kind`, cross-kind dict/instance/construct/copy | full reconstruction rejects |
| Tokens | bounded qualified `system_id`: `project_local`, `iec`, `iso`, `opc-ua`, `vendor.example` | both token kinds accept and preserve the exact value |
| Tokens | empty, uppercase, whitespace, path, Unicode, over-length, newline/partial-match `system_id` | `LocalIdentifier` rejection |
| Tokens | otherwise identical domain/type token | different canonical bytes and PIF IDs |
| PIF | cross-dimension body, wrong-context/key parent, cycle | collection invalid |
| PIF | fork, partial/full convergence, withdrawal, replay revival | exact membership-relative tips/conflict |
| PIF | second parentless root for one port/context/dimension | collection invalid |
| PCN | `(A,B)` vs `(B,A)` | identical canonical bytes and ID |
| PCN | `(A,B,A)`, `(A,A)`, 1 or 65 endpoints | typed rejection; never deduplicate |
| PCN | 2 and 64 unique endpoints | accepted without cardinality change |
| PCN | independent roots | permitted corroboration |
| PCN | same-root fork/convergence; cross-root or endpoint-changing parent | fork represented; invalid changes rejected |
| PCN | parents deriving from different roots | cross-root convergence rejected |
| PCM | permuted dimensions/citations | normative identical bytes and ID |
| PCM | detached citation collection or reordered ownership | ordered dimension entries own exactly two endpoint citations |
| PCM | missing, duplicate, wrong endpoint/dimension/context/member citation | collection invalid |
| PCM | structurally valid noncurrent citation | load/replay succeeds; Slice A index retains it |
| PCM | second parentless root for one pair/context | collection invalid |
| Replay | earlier membership current, later membership stale structurally | both revisions load; no chronology used |
| Replay | timestamps/file/directory/hash-seed order changes | same validation and canonical result |
| PTW | target registration, withdrawal, non-PT, unknown, superseded, withdrawn | collection invalid |
| PTW | renamed or alternate target field | only `withdraws` is accepted |
| PTW | successor plus withdrawal or resurrection | collection invalid |
| PTW | target is not an unsuperseded tip; duplicate target withdrawal | collection invalid |
| PTW | replay omits withdrawal | target activity revives membership-relatively |
| Evidence | `prg/pif/pcn/pcm` citation closure; cited `ptw_` | closure enforced; `ptw_` uncitable |
| Forgery | stale content IDs, wrong union arm, nested model substitution | append/load/replay reject |
| Store | corrupted current sibling or invalid prospective record | all-or-nothing failure |
| History | every explicit pre-PT membership | same bytes, record IDs, revision; no PT records |
| Isolation | upward imports, PT store/module/query/traversal | architecture guard fails |
| Scope | any committed `prt/prg/pif/pcn/pcm/ptw` fixture | Slice A gate fails |

Exact public symbol, field, discriminator, prefix, and vocabulary tests compare
equality, never subsets. Every genuine adversarial defect is reproduced red
before repair. The complete repository, two clean-checkout columns, OCP/STEP,
PDF, and permitted loopback rerun are required before owner handoff.
