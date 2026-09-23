"""Approved measurement delivery facade.

The superseded storage API accepted unbound caller result/trace/matrix bytes.
It is deliberately not a supported compatibility surface. Production delivery
now accepts only the frozen file/closure command contract.
"""
from .measurement_runtime import (
    FILES,
    evaluate as evaluate_semantic_bundle,
    replay as replay_semantic_bundle,
    verify as verify_measurement_bundle,
)

__all__ = ['FILES','evaluate_semantic_bundle','replay_semantic_bundle','verify_measurement_bundle']
