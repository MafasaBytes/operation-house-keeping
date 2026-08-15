"""IB-001 identity binding: append-only ledger of explicit identity
decisions, deterministic resolver, and read-only bound temporal facade.

Reads `temporal_state` read-only and imports anchor contracts from
`system_identity`; never touches `data_sources`. See
docs/superpowers/specs/2026-08-07-ib001-identity-binding-design.md.
"""

from backend.identity_binding.resolver import membership

__all__ = ["membership"]
