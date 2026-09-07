# FM-001 Final Contract Correction Report

Date: 2026-09-07

## 1. Accepted inputs and digest transition

The frozen lead proposal remains 578 lines, 30,026 bytes, SHA-256
`2e8e69b465defe2e9610bb1a34e85b80cc20cdd2a668dc0d01eb119818bf36f2`.
The frozen challenger audit remains 625 lines, 37,054 bytes, SHA-256
`84079ebe361de207819b4d964435cf163dddfdfd97109eb6a40928fb1f6d0bd3`.
The accepted pre-correction synthesis was SHA-256
`33b25f771662e0df5d621af782aae1d45f884c868c6e4c0ac635d4a97270d0ad`.

The corrected synthesis is
`docs/superpowers/specs/2026-09-07-fm001-explicit-flow-to-measurement-association-design.md`,
745 lines, 38,533 UTF-8 bytes, SHA-256
`4179a46a9413ad7a666171572db058a7b71f8d8734af39ae3650e6bf100238e2`, ending
`END OF FM-001 CORRECTED FINAL SYNTHESIS`.

The correction preserves refined Alternative A: existing model-kernel ledger,
no association anchor, direct-measurement relevance only, participant-port
locus, exact same-revision support, uncitable withdrawal, five future queries,
and two owner-gated slices.

## 2. C1 — generic builder surface

The synthesis no longer proposes FM-specific builders. Positive and withdrawal
records use only the existing public
`backend.model_kernel.build_record(record_cls, **fields)` convention. No alias,
private-looking public builder, or alternative construction API is permitted.

Slice A exports only the two record classes and their exact record contracts;
future Slice B exports are enumerated separately and remain unauthorized.

## 3. C2 — exact future result boundary

The synthesis now freezes every Slice B alias, literal order, nested row,
outer-result field order, strict-index rule, carry-once placement,
deterministic ordering/grouping rule, and exact future export list. It names
private helpers as private and keeps query methods out of Slice A.

Each result carries one `ModelQueryMaterial` first and exactly once. Support
rows, root rows, entry rows, and all five outer result classes have complete
field/type/default order. No future implementation may invent a result shape.

## 4. C3 — orthogonal support and activity

The old aggregate `support_activity` vocabulary was removed. The corrected
boundary separates pinned assertion activity, containing lineage health,
support presence, support alignment, semantic support, derived participant
role, declaration conclusion, and orientation.

FRG, VRG, and PRG are permanent registrations and therefore use only
`not_applicable` lineage health. An admitted FMA has all six support pins in
the selected membership; support rows have `present` presence and exact or
unaligned alignment. No-declaration results carry no fabricated support rows.
The unsupported `measured_actual_absent` literal was removed. Healthy
corroborating roots, same-root conflicts, inactive roots, and cross-root body
disagreement remain separately disclosed.

## 5. C4 — independent roots

The contradictory phrase about duplicate subject records was replaced. The
invariant is that record IDs/files and invalid ancestry are unique/invalid;
independent parentless roots for one immutable subject are allowed and may
corroborate or disagree. Subject uniqueness is not introduced.

## 6. C5 — Slice boundary

Slice A no longer promises structured absence from public FM queries. Slice A
prepares immutable indexes and preserves the 36-record revision. The five
public query methods, result classes, and structured no-declaration absence
belong exclusively to Slice B.

## 7. C6 — implicit relationship dimension

`direct_measurement_relevance` is explicitly an immutable implicit subject
dimension fixed by the record kind and measured-actual VSM support. It is not a
caller-supplied query parameter, redundant mutable field, or alternate value.
The exact lookup still selects the complete v1 subject.

## 8. Verification and disposition

The corrected synthesis was checked for contiguous numbered sections, ending
marker, UTF-8 readability, and whitespace. The six corrections tighten the
accepted architecture and do not introduce a new layer, identity, truth
claim, or ledger. There are zero unresolved owner questions.

The owner therefore accepts the corrected FM-001 design for ADR-0021 and
Slice A implementation only. Slice B, fixtures, append/demo, and FA-001
remain unauthorized.

END OF FM-001 FINAL CONTRACT CORRECTION REPORT
