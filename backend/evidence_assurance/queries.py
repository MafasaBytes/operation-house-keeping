"""EA-001 read-only composition facade and store-independent validator."""

from __future__ import annotations

from backend.evidence_assurance.contracts import (
    EvidenceAssuranceConfigurationError,
)


class EvidenceAssuranceQueries:
    def __init__(self, *, source, temporal) -> None:
        source_methods = ("inventory_token", "read_material", "reread_named_material")
        temporal_methods = ("selection_inventory_token", "selection_material")
        if not all(callable(getattr(source, name, None)) for name in source_methods):
            raise EvidenceAssuranceConfigurationError(
                "EA_DEPENDENCY_INVALID", "source dependency is invalid")
        if not all(callable(getattr(temporal, name, None)) for name in temporal_methods):
            raise EvidenceAssuranceConfigurationError(
                "EA_DEPENDENCY_INVALID", "temporal dependency is invalid")
        self._source = source
        self._temporal = temporal

    def select_operational_evidence(self, request):
        raise NotImplementedError

    def revalidate_operational_evidence(self, snapshot, *, membership_mode):
        raise NotImplementedError


def validate_operational_evidence_snapshot(snapshot, *, expected_fingerprint=None):
    raise NotImplementedError
