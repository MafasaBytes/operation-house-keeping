"""This ledger records how an identified authority interprets an exact
source-native property. An interpretation is a claim ABOUT a source
property, never evidence FROM the source: it is never inserted into,
copied into, or presented as a source-supplied field, and a source that
supplied no unit still supplied no unit. It declares no canonical
identity, mints no anchor, and never maps a source property to a model
variable — that decision lives exclusively in identity_binding.
"""

from backend.source_interpretation.canonical import (
    build_record,
    canonical_bytes,
    canonical_payload,
    canonical_sort_key,
    compute_record_id,
    compute_revision_id,
    verify_record_id,
)
from backend.source_interpretation.contracts import (
    INTERPRETATION_RECORD_ID_PATTERN,
    INTERPRETATION_SET_ID_PATTERN,
    DimensionInterpretationResolution,
    InterpretationAssertionSummary,
    InterpretationBody,
    InterpretationClosure,
    InterpretationRecord,
    InterpretationRejection,
    InterpretationRetraction,
    InterpretationRevision,
    ObservationRoleInterpretation,
    PropertyInterpretationResult,
    QuantityKindInterpretation,
    SourcePropertyInterpretation,
    UnitInterpretation,
)
from backend.source_interpretation.errors import (
    InterpretationConfigurationError,
    InterpretationIntegrityError,
    InterpretationResolutionError,
    SourceInterpretationError,
)
from backend.source_interpretation.store import (
    InterpretationStore,
    LoadedInterpretationSet,
    validate_record_collection,
)
from backend.source_interpretation.resolver import InterpretationResolver

__all__ = [
    "INTERPRETATION_RECORD_ID_PATTERN", "INTERPRETATION_SET_ID_PATTERN",
    "DimensionInterpretationResolution", "InterpretationAssertionSummary",
    "InterpretationBody", "InterpretationClosure",
    "InterpretationConfigurationError", "InterpretationIntegrityError",
    "InterpretationRecord", "InterpretationRejection",
    "InterpretationResolutionError", "InterpretationRetraction",
    "InterpretationResolver", "InterpretationRevision",
    "ObservationRoleInterpretation", "PropertyInterpretationResult",
    "QuantityKindInterpretation", "SourceInterpretationError",
    "InterpretationStore", "LoadedInterpretationSet",
    "SourcePropertyInterpretation", "UnitInterpretation", "build_record",
    "canonical_bytes", "canonical_payload", "canonical_sort_key",
    "compute_record_id", "compute_revision_id", "validate_record_collection",
    "verify_record_id",
]
