"""MK-001 model kernel: typed entity/relationship ledger and hierarchy view
over canonical system_identity anchors.

Runtime code imports only system_identity, the standard library, and
pydantic. See docs/superpowers/specs/2026-08-08-mk001-model-kernel-design.md
and ADR-0007.

This module is the supported import surface: the ledger record contracts,
the assertion/query context contracts, the typed error tree, the result
contracts, and the three operations a caller needs (``build_record``,
``ModelStore``/``LoadedModel``, ``ModelQueries``). Canonicalization
internals (``canonical_bytes``, ``compute_record_id``, …), collection
validation, and the hierarchy projection are implementation details: they
live in their submodules and are deliberately NOT re-exported, so their
shape can change without breaking callers.
"""

from backend.model_kernel.canonical import build_record
from backend.model_kernel.contracts import (
    AssertionContext,
    AuthorityRef,
    CanonicalDecimal,
    ChildEntry,
    ChildrenResult,
    ConstraintPredicate,
    CycleReport,
    DeclaredUnit,
    EntityRegistration,
    EntityResult,
    EntityVariablesResult,
    EvidenceDisclosure,
    EvidenceRef,
    HierarchyHealth,
    IdentityBindingRecordEvidence,
    LifecycleView,
    LifecycleViewContext,
    LineageConflict,
    ModelConfigurationError,
    ModelIntegrityError,
    ModelKernelError,
    ModelQueryError,
    ModelRecord,
    ModelRecordEvidence,
    ModelRevision,
    OwnerDeclarationEvidence,
    ParentConflictReport,
    ParentResult,
    ParentStatus,
    ReferentKind,
    RegistrationSummary,
    RelationshipAssertion,
    RelationshipsResult,
    RelationshipSummary,
    RelationshipTypeDefinition,
    RelationshipWithdrawal,
    ScalarComparisonOperator,
    ScalarComparisonPredicate,
    UnitDeclaration,
    UnitNotDeclared,
    UnitReference,
    SourceRawRecordEvidence,
    StructuralSourceLocatorEvidence,
    TemporalOccurrenceEvidence,
    TraversalAnnotation,
    TraversalBlock,
    TraversalResult,
    TraversalStep,
    VariableRegistration,
    VariableRegistrationSummary,
    VariableResult,
    VariableSpecificationResult,
    VariableValueSpecification,
    VariableSemanticDeclaration,
    QuantityKindReference, ObservationRoleReference,
    QuantityKindDeclaration, ObservationRoleDeclaration,
    SemanticDimensionDeclaration, SemanticDimensionResult,
    VariableSemanticsResult,
    ViewIndependentContext,
)
from backend.model_kernel.queries import ModelQueries
from backend.model_kernel.store import LoadedModel, ModelStore

__all__ = [
    # ledger record contracts
    "EntityRegistration", "VariableRegistration",
    "VariableValueSpecification",
    "VariableSemanticDeclaration",
    "RelationshipTypeDefinition",
    "RelationshipAssertion",
    "RelationshipWithdrawal",
    "ModelRecord",
    # assertion / query context contracts
    "AssertionContext",
    "LifecycleViewContext",
    "ViewIndependentContext",
    "LifecycleView",
    "ReferentKind",
    # authority and evidence contracts
    "AuthorityRef",
    "EvidenceRef",
    "OwnerDeclarationEvidence",
    "ModelRecordEvidence",
    "IdentityBindingRecordEvidence",
    "SourceRawRecordEvidence",
    "StructuralSourceLocatorEvidence",
    "UnitReference", "DeclaredUnit", "UnitNotDeclared",
    "UnitDeclaration",
    "CanonicalDecimal",
    "ScalarComparisonOperator", "ScalarComparisonPredicate",
    "ConstraintPredicate",
    "QuantityKindReference", "ObservationRoleReference",
    "QuantityKindDeclaration", "ObservationRoleDeclaration",
    "SemanticDimensionDeclaration",
    "TemporalOccurrenceEvidence",
    # typed errors
    "ModelKernelError",
    "ModelConfigurationError",
    "ModelIntegrityError",
    "ModelQueryError",
    # result contracts
    "ModelRevision",
    "EvidenceDisclosure",
    "RelationshipSummary",
    "LineageConflict",
    "RelationshipsResult",
    "RegistrationSummary", "VariableRegistrationSummary", "VariableResult",
    "VariableSpecificationResult",
    "SemanticDimensionResult", "VariableSemanticsResult",
    "EntityResult", "EntityVariablesResult",
    "ParentResult",
    "ParentStatus",
    "TraversalAnnotation",
    "ChildEntry",
    "ChildrenResult",
    "TraversalStep",
    "TraversalBlock",
    "TraversalResult",
    "CycleReport",
    "ParentConflictReport",
    "HierarchyHealth",
    # operations
    "build_record",
    "ModelStore",
    "LoadedModel",
    "ModelQueries",
]
