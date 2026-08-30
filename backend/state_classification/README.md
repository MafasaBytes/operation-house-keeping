# State classification

Status: Slices A and B are owner accepted. Slice C is implemented and
adversarially reviewed; awaiting owner acceptance. Slice D remains unstarted
and unauthorized.

`backend.state_classification` is the read-only ST-001 composition layer. It
combines an exact-context model state declaration with explicitly selected,
public CN-001 constraint-evaluation results. It owns no store and persists no
classification.

`matches` means only that every admitted pinned constraint was satisfied by
its independently selected latest evidence at or before one cutoff.
`does_not_match` means only that at least one admitted conjunct was violated.
Neither result establishes a current physical state, exclusivity,
completeness, transition, causality, control, safety, health, correctness, or
recommended action. Observation times are preserved independently;
simultaneity and synchronization are not asserted.

The facade accepts one public `ConstraintEvaluationQueries` instance and uses
the public chain `constraints.semantic.compatibility.state.model` to construct
public `ModelQueries` over that exact loaded membership. It accesses no private
foreign field, owns no store, and creates no filesystem, network, cache,
projection, ledger, or persistence capability. Every permanent condition is
evaluated exactly once with the same normalized cutoff and the registration's
permanent subject entity.

Public result validation proves the internal coherence of carried model and
lower public results. It does not independently authenticate uncaptured raw payload bytes.
A coherent lower-evidence content mutation accepted by the
lower public contracts remains outside this store-independent boundary; an
ST-specific disposable regression test documents that limit.

The `not_registered` and `not_declared` condition-alignment/refusal branches
are defensive-unreachable through a valid public SRG/STD membership because
store reference closure requires every permanent constraint and every pinned
declaration. They remain implemented fail-closed for hostile reconstruction;
tests prove the closure instead of manufacturing invalid private models.

ST-002 alone may define transition identity, direction, triggers, guards,
actions, events, history, or execution. Slice C contains none of those
meanings.
