# State classification

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
