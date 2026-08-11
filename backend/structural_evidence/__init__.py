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
    LabelFieldRef,
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
from backend.structural_evidence.claims import (
    CsvStructuralReading,
    csv_structural_claims,
    step_structural_claims,
)
from backend.structural_evidence.proposals import (
    REQUIRED_BY_PROPOSAL_KIND,
    EntityRegistrationProposal,
    ModelProposalResult,
    RelationshipAssertionProposal,
)
from backend.structural_evidence.reconcile import (
    BASIS_BY_FINDING,
    BindingSetParticipation,
    BindingSetResolution,
    ClaimComparison,
    ClaimSetDisclosure,
    ComparisonOperand,
    Finding,
    FindingBasis,
    ModelDisclosure,
    PayloadVerification,
    ReconciliationFinding,
    ResolvedSubject,
    StructuralReconciler,
    StructuralReconciliationResult,
    compute_inputs_digest,
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
    StructuralEvidenceProjection,
    StructuralSourceRef,
    canonical_locator_value,
    from_kernel_evidence,
    to_kernel_evidence,
    toolchain_fingerprint,
)

__all__ = [
    "StructuralEvidenceError",
    "StructuralEvidenceConfigurationError",
    "CsvStructuralReading",
    "csv_structural_claims",
    "step_structural_claims",
    "StructuralClaimKind",
    "SourceNativeField",
    "SourceStructuralClaim",
    "SourceContainmentClaim",
    "DerivedUsagePath",
    "QuantityFieldRef",
    "LabelFieldRef",
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
    "StructuralEvidenceProjection",
    "to_kernel_evidence",
    "from_kernel_evidence",
    "toolchain_fingerprint",
    "BASIS_BY_FINDING",
    "Finding",
    "FindingBasis",
    "BindingSetResolution",
    "ResolvedSubject",
    "ClaimSetDisclosure",
    "ModelDisclosure",
    "ComparisonOperand",
    "ClaimComparison",
    "ReconciliationFinding",
    "PayloadVerification",
    "BindingSetParticipation",
    "StructuralReconciliationResult",
    "StructuralReconciler",
    "compute_inputs_digest",
    "REQUIRED_BY_PROPOSAL_KIND",
    "EntityRegistrationProposal",
    "RelationshipAssertionProposal",
    "ModelProposalResult",
]
