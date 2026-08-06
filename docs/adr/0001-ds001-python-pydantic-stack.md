# ADR-0001: Python 3.13 + Pydantic v2 + filesystem raw store for DS-001

Date: 2026-08-06
Status: Accepted (project owner, 2026-08-06)

## Context

The repository had no established backend stack. DS-001 needs typed
contracts, CSV extraction, checksummed immutable persistence, and a test
suite — nothing distributed. The owner already works in Python (project
venvs, exploration notebook).

## Options considered

1. **Python + stdlib dataclasses** — zero dependencies, most boring;
   weaker runtime validation, hand-rolled (de)serialization.
2. **Python + Pydantic v2** — declarative validation and JSON
   round-tripping for the contract models; one well-maintained dependency.
3. **Go or TypeScript** — stronger static typing, but abandons the owner's
   working environment and slows the first slice for no DS-001 benefit.

## Decision

Option 2. Contracts are Pydantic v2 models (frozen where they represent
records); extraction and persistence mechanics use the standard library
(`csv`, `hashlib`, `json`, `pathlib`); the raw store is a write-once
filesystem layout (content-addressed payloads + JSON envelopes); tests use
pytest. pandas is a notebook/dev convenience only and must not appear in
`backend/` imports, because it interprets tabular data (type coercion,
header inference) in ways the extraction boundary forbids.

## Consequences

- One runtime dependency (`pydantic`) recorded in `requirements.txt`.
- Contract models double as JSON schema documentation.
- The store is human-inspectable and trivially replayable; if later slices
  need querying, a SQLite index can be added *beside* the immutable files
  without changing the contract boundary.
- Portability note: the contract boundary is JSON, so a future language or
  service split does not invalidate persisted evidence.
