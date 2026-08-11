"""SN-001 structural evidence.

This module records what a structural source reported and how that report
is addressed. It accepts nothing into any model, declares no canonical
identity, mints no anchor, writes no ledger, and nothing here is
engineering truth. The runtime module owns no authoritative store or
ledger. Identity decisions live in identity_binding; model truth lives in
model_kernel.
"""

from backend.structural_evidence.contracts import (
    DeclaredEngineeringContext,
    DerivedUsagePath,
    EngineeringContext,
    QuantityFieldRef,
    SourceContainmentClaim,
    SourceNativeField,
    SourceStructuralClaim,
    SourceStructuralClaimSet,
    StructuralClaimKind,
    UnknownEngineeringContext,
    UnresolvedParentReference,
    ViewIndependentEngineeringContext,
)
from backend.structural_evidence.errors import (
    StructuralEvidenceConfigurationError,
    StructuralEvidenceError,
)
from backend.structural_evidence.locators import (
    CsvCellLocator,
    CsvRowLocator,
    StepDefinitionLocator,
    StepUsageLocator,
    StructuralAddress,
    StructuralLocator,
    StructuralSourceRef,
    canonical_locator_value,
)

__all__ = [
    "StructuralEvidenceError",
    "StructuralEvidenceConfigurationError",
    "StructuralClaimKind",
    "SourceNativeField",
    "SourceStructuralClaim",
    "SourceContainmentClaim",
    "DerivedUsagePath",
    "QuantityFieldRef",
    "UnresolvedParentReference",
    "DeclaredEngineeringContext",
    "ViewIndependentEngineeringContext",
    "UnknownEngineeringContext",
    "EngineeringContext",
    "SourceStructuralClaimSet",
    "StructuralSourceRef",
    "CsvRowLocator",
    "CsvCellLocator",
    "StepDefinitionLocator",
    "StepUsageLocator",
    "StructuralLocator",
    "StructuralAddress",
    "canonical_locator_value",
]
