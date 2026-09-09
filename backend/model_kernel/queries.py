"""MK-001 query surface: total functions over one explicit immutable
revision.

No ambient model, no implicit clock; every result embeds the full
ModelRevision. Misuse raises typed ModelQueryError; absence and
disagreement are statuses. Strict context equality — no union across
context arms ever. Collections are in canonical order (ascending
anchor_id, ties by record_id); traversal is depth-first preorder with
children visited in canonical order.
"""

import re
import typing

from pydantic import BaseModel, TypeAdapter, ValidationError

from backend.model_kernel.contracts import (
    AssertionContext,
    ChildEntry,
    ChildrenResult,
    ConstraintDeclarationResult,
    CycleReport,
    EntityResult,
    EntityVariablesResult,
    EvidenceDisclosure,
    HierarchyHealth,
    LifecycleView,
    LineageConflict,
    ModelQueryError,
    ParentConflictReport,
    ParentResult,
    RegistrationSummary,
    RelationshipsResult,
    RelationshipSummary,
    TraversalAnnotation,
    TraversalBlock,
    TraversalResult,
    TraversalStep,
    VariableRegistrationSummary,
    VariableConstraintCollectionResult,
    VariableResult,
    VariableSpecificationResult,
    SemanticDimensionResult,
    VariableSemanticsResult,
)
from backend.model_kernel.hierarchy import HierarchyProjection, build_projection
from backend.model_kernel.behavior_results import (
    BehaviorAssertionDisclosureResult, BehaviorLookupResult,
    BehaviorRuleResult, VariableBehaviorsResult,
    _behavior_assertion_payload, _behavior_lookup_payload,
    _behavior_rule_payload, _variable_behaviors_payload,
)
from backend.model_kernel.state_results import (
    EntityStatesResult, StateAssertionDisclosureResult,
    StateDeclarationResult, StateLookupResult,
    _entity_states_payload, _state_assertion_payload,
    _state_declaration_payload, _state_lookup_payload,
)
from backend.model_kernel.transition_results import (
    EntityTransitionsResult, TransitionAssertionDisclosureResult,
    TransitionDeclarationResult, TransitionLookupResult,
    _entity_transitions_payload, _transition_assertion_payload,
    _transition_declaration_payload, _transition_lookup_payload,
)
from backend.model_kernel.flow_results import (
    FlowAssertionDisclosureResult, FlowDeclarationResult, FlowLookupResult,
    PortFlowsResult, _flow_assertion_payload, _flow_declaration_payload,
    _flow_lookup_payload, _port_flows_payload,
)
from backend.model_kernel.flow_measurement_results import (
    FlowMeasurementAssociationResult,
    FlowMeasurementAssociationsAtPortResult,
    FlowMeasurementAssociationsForFlowResult,
    FlowMeasurementAssociationsForVariableResult,
    FlowMeasurementAssertionResult,
    _assertion_payload as _flow_measurement_assertion_payload,
    _exact_payload as _flow_measurement_exact_payload,
    _reject_scalar_subclasses as _reject_flow_measurement_scalar_subclasses,
    _reverse_payload as _flow_measurement_reverse_payload,
)
from backend.model_kernel.flow_operating_criterion_results import (
    FlowOperatingCriterionResult, FlowOperatingCriterionAssertionResult,
    FlowOperatingCriterionSubjectResult, FlowOperatingCriterionLineageRow,
    FlowOperatingCriterionBodyRow, FlowOperatingCriterionSupportRow,
)
from backend.model_kernel.port_results import (
    ConnectionRootResult, ConnectionSubjectResult, SharedConnectionsResult,
    EndpointInterfaceResult,
    EntityPortsResult,
    ExactConnectionSetResult, PortConnectionsResult,
    InterfaceCompatibilityResult, InterfaceDimensionResult, ModelQueryMaterial,
    PortAssertionDisclosureResult, PortInterfaceResult, PortLookupResult,
    PortVariablesResult, VariablePortAssociationEntry,
    VariablePortAssociationResult, VariablePortAssociationRootResult,
    VariablePortAssertionDisclosureResult, VariablePortsResult,
    _connection_parts_payload, _port_assertion_payload,
    _port_interface_payload,
)
from backend.model_kernel.store import LoadedModel
from backend.system_identity import (
    BEHAVIOR_ANCHOR_ID_PATTERN,
    CONSTRAINT_ANCHOR_ID_PATTERN,
    ENTITY_ANCHOR_ID_PATTERN,
    FLOW_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN,
    STATE_ANCHOR_ID_PATTERN,
    TRANSITION_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
)

_ANCHOR_ID = re.compile(ENTITY_ANCHOR_ID_PATTERN)
_VARIABLE_ANCHOR_ID = re.compile(VARIABLE_ANCHOR_ID_PATTERN)
_CONSTRAINT_ANCHOR_ID = re.compile(CONSTRAINT_ANCHOR_ID_PATTERN)
_PORT_ANCHOR_ID = re.compile(PORT_ANCHOR_ID_PATTERN)
_BEHAVIOR_ANCHOR_ID = re.compile(BEHAVIOR_ANCHOR_ID_PATTERN)
_STATE_ANCHOR_ID = re.compile(STATE_ANCHOR_ID_PATTERN)
_TRANSITION_ANCHOR_ID = re.compile(TRANSITION_ANCHOR_ID_PATTERN)
_FLOW_ANCHOR_ID = re.compile(FLOW_ANCHOR_ID_PATTERN)
_PORT_RECORD_ID = re.compile(r"^(?:prg|pif|pcn|pcm|ptw)_[0-9a-f]{64}$")
_VARIABLE_PORT_RECORD_ID = re.compile(r"^(?:vpa|vpw)_[0-9a-f]{64}$")
_BEHAVIOR_RECORD_ID = re.compile(r"^(?:brg|bhd|bhw)_[0-9a-f]{64}$")
_STATE_RECORD_ID = re.compile(r"^(?:srg|std|stw)_[0-9a-f]{64}$")
_TRANSITION_RECORD_ID = re.compile(r"^(?:trg|trd|trw)_[0-9a-f]{64}$")
_FLOW_RECORD_ID = re.compile(r"^(?:frg|fld|flw)_[0-9a-f]{64}$")
_FLOW_MEASUREMENT_RECORD_ID = re.compile(r"^(?:fma|fmw)_[0-9a-f]{64}$")
_FLOW_MEASUREMENT_ORIENTATIONS = (
    "aligned", "opposite", "unsigned_magnitude", "not_applicable")
_CONTEXT_ADAPTER: TypeAdapter = TypeAdapter(AssertionContext)
_LIFECYCLE_VIEWS = frozenset(typing.get_args(LifecycleView))


class ModelQueries:
    def __init__(self, loaded: LoadedModel) -> None:
        if not isinstance(loaded, LoadedModel):
            raise ModelQueryError(
                "MODEL_LOADED_MODEL_INVALID",
                "queries require a LoadedModel from ModelStore.load() or "
                "ModelStore.replay()")
        self.loaded = loaded

    # -- boundary checks ---------------------------------------------------

    def _require_anchor_id(self, anchor_id: str) -> str:
        if not isinstance(anchor_id, str) or not _ANCHOR_ID.fullmatch(anchor_id):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical entity anchor id")
        return anchor_id

    def _require_variable_anchor_id(self, anchor_id: str) -> str:
        if not isinstance(anchor_id, str) or not _VARIABLE_ANCHOR_ID.fullmatch(
                anchor_id):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical variable anchor id")
        return anchor_id

    def _require_constraint_anchor_id(self, anchor_id: str) -> str:
        if (not isinstance(anchor_id, str)
                or not _CONSTRAINT_ANCHOR_ID.fullmatch(anchor_id)):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical constraint anchor id")
        return anchor_id

    def _require_port_anchor_id(self, anchor_id: str) -> str:
        if (not isinstance(anchor_id, str)
                or not _PORT_ANCHOR_ID.fullmatch(anchor_id)):
            raise ModelQueryError("MODEL_ANCHOR_ID_INVALID",
                                  f"{anchor_id!r} is not a canonical port anchor id")
        return anchor_id

    def _require_behavior_anchor_id(self, anchor_id: str) -> str:
        if (not isinstance(anchor_id, str)
                or not _BEHAVIOR_ANCHOR_ID.fullmatch(anchor_id)):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical behavior anchor id")
        return anchor_id

    def _require_state_anchor_id(self, anchor_id: str) -> str:
        if (not isinstance(anchor_id, str)
                or not _STATE_ANCHOR_ID.fullmatch(anchor_id)):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical state anchor id")
        return anchor_id

    def _require_transition_anchor_id(self, anchor_id: str) -> str:
        if (not isinstance(anchor_id, str)
                or not _TRANSITION_ANCHOR_ID.fullmatch(anchor_id)):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical transition anchor id")
        return anchor_id

    def _require_flow_anchor_id(self, anchor_id: str) -> str:
        if (not isinstance(anchor_id, str)
                or not _FLOW_ANCHOR_ID.fullmatch(anchor_id)):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical flow anchor id")
        return anchor_id

    def _require_port_record_id(self, record_id: str) -> str:
        if (not isinstance(record_id, str)
                or not _PORT_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError("MODEL_RECORD_ID_INVALID",
                                  f"{record_id!r} is not a PT record id")
        return record_id

    def _require_variable_port_record_id(self, record_id: str) -> str:
        if (not isinstance(record_id, str)
                or not _VARIABLE_PORT_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError(
                "MODEL_RECORD_ID_INVALID",
                f"{record_id!r} is not a VP record id")
        return record_id

    def _require_behavior_record_id(self, record_id: str) -> str:
        if (not isinstance(record_id, str)
                or not _BEHAVIOR_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError(
                "MODEL_RECORD_ID_INVALID",
                f"{record_id!r} is not a BH record id")
        return record_id

    def _require_state_record_id(self, record_id: str) -> str:
        if (not isinstance(record_id, str)
                or not _STATE_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError(
                "MODEL_RECORD_ID_INVALID",
                f"{record_id!r} is not an ST record id")
        return record_id

    def _require_transition_record_id(self, record_id: str) -> str:
        if (not isinstance(record_id, str)
                or not _TRANSITION_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError(
                "MODEL_RECORD_ID_INVALID",
                f"{record_id!r} is not an ST-002 transition record id")
        return record_id

    def _require_flow_record_id(self, record_id: str) -> str:
        if (not isinstance(record_id, str)
                or not _FLOW_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError(
                "MODEL_RECORD_ID_INVALID",
                f"{record_id!r} is not an FL-001 flow record id")
        return record_id

    def _require_flow_measurement_record_id(self, record_id: str) -> str:
        if (type(record_id) is not str
                or not _FLOW_MEASUREMENT_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError(
                "MODEL_RECORD_ID_INVALID",
                "record id is not a canonical FM-001 record id")
        return record_id

    def _require_flow_measurement_orientation(self, orientation: str) -> str:
        if (type(orientation) is not str
                or orientation not in _FLOW_MEASUREMENT_ORIENTATIONS):
            raise ModelQueryError(
                "MODEL_ORIENTATION_INVALID",
                "orientation is not an FM-001 orientation")
        return orientation

    def _require_flow_measurement_context(self, context) -> AssertionContext:
        try:
            _reject_flow_measurement_scalar_subclasses(context)
        except (ValueError, TypeError, AttributeError) as error:
            raise ModelQueryError(
                "MODEL_CONTEXT_INVALID",
                "FM context contains a non-built-in scalar") from error
        return self._require_context(context)

    def _material(self) -> ModelQueryMaterial:
        return ModelQueryMaterial(
            revision=self.loaded.revision,
            records=tuple(self.loaded.records[record_id]
                          for record_id in self.loaded.revision.record_ids))

    def _record_index(self) -> dict[str, int]:
        return {record_id: index for index, record_id
                in enumerate(self.loaded.revision.record_ids)}

    def _require_view(self, view):
        """Validate the lifecycle view BEFORE evaluation — never at result
        construction, which would leak a raw ValidationError."""
        if view is None:
            return None
        if not isinstance(view, str) or view not in _LIFECYCLE_VIEWS:
            raise ModelQueryError(
                "MODEL_VIEW_INVALID",
                f"{view!r} is not a lifecycle view "
                f"({', '.join(sorted(_LIFECYCLE_VIEWS))})")
        return view

    def _require_context(self, context) -> AssertionContext:
        """Normalize a valid context mapping into the discriminated model so
        matching never compares against raw input; malformed context is a
        typed error, never a silently empty answer."""
        try:
            if isinstance(context, BaseModel):
                fields = type(context).model_fields
                stored = vars(context)
                extras = getattr(context, "__pydantic_extra__", None)
                if set(stored).difference(fields):
                    raise ValueError(
                        "assertion context instance contains extra fields")
                if (extras is not None
                        and (type(extras) is not dict or len(extras) != 0)):
                    raise ValueError(
                        "assertion context instance contains extra fields")
                private = getattr(context, "__pydantic_private__", None)
                if private is not None and (
                        type(private) is not dict or len(private) != 0):
                    raise ValueError(
                        "assertion context instance contains private state")
                payload = context.model_dump(mode="python")
            else:
                payload = context
            return _CONTEXT_ADAPTER.validate_python(payload)
        except (ValidationError, ValueError, TypeError, AttributeError) as error:
            raise ModelQueryError(
                "MODEL_CONTEXT_INVALID",
                "context must be a lifecycle_view or view_independent "
                "assertion context") from error

    def _require_type(self, type_name: str):
        # guard the type BEFORE the mapping lookup: an unhashable value
        # would otherwise leak a raw TypeError past the error contract
        if not isinstance(type_name, str):
            raise ModelQueryError(
                "MODEL_UNKNOWN_TYPE",
                f"{type_name!r} is not a relationship type name")
        current_id = self.loaded.current_type_by_name.get(type_name)
        if current_id is None:
            raise ModelQueryError(
                "MODEL_UNKNOWN_TYPE",
                f"no relationship type named {type_name!r} in this revision")
        return self.loaded.types[current_id]

    def _require_hierarchy_type(self, type_name: str, view):
        view = self._require_view(view)
        definition = self._require_type(type_name)
        if definition.hierarchy_semantics != "containment":
            raise ModelQueryError(
                "MODEL_NOT_A_HIERARCHY",
                f"type {type_name!r} has no hierarchy semantics")
        if definition.context_requirement == "lifecycle_view":
            if view is None:
                raise ModelQueryError(
                    "MODEL_VIEW_REQUIRED",
                    f"type {type_name!r} is lifecycle-scoped; an explicit "
                    "view is required")
        elif view is not None:
            raise ModelQueryError(
                "MODEL_VIEW_FORBIDDEN",
                f"type {type_name!r} is view-independent; no view applies")
        return definition

    # -- summaries ---------------------------------------------------------

    def _summary(self, record_id: str) -> RelationshipSummary:
        claim = self.loaded.assertions[record_id]
        definition = self.loaded.types[claim.type_id]
        current_id = self.loaded.current_type_by_name[definition.type_name]
        superseded_by = self.loaded.superseded_by[record_id]
        withdrawn_by = self.loaded.withdrawn_by[record_id]
        return RelationshipSummary(
            record_id=record_id, type_id=claim.type_id,
            type_name=definition.type_name,
            forward_label=definition.forward_label,
            inverse_label=definition.inverse_label,
            cited_type_current=claim.type_id == current_id,
            source_anchor_id=claim.source_anchor_id,
            target_anchor_id=claim.target_anchor_id,
            context=claim.context, authority=claim.authority,
            evidence=tuple(
                EvidenceDisclosure(
                    ref=reference,
                    verification=("verified_in_revision"
                                  if reference.kind == "model_record"
                                  else "declared_reference"))
                for reference in claim.evidence),
            supersedes=claim.supersedes, superseded_by=superseded_by,
            withdrawn_by=withdrawn_by,
            active=not superseded_by and not withdrawn_by,
            recorded_at=claim.recorded_at)

    def _is_active(self, record_id: str) -> bool:
        return (not self.loaded.superseded_by[record_id]
                and not self.loaded.withdrawn_by[record_id])

    # -- entity ------------------------------------------------------------

    def entity(self, anchor_id: str) -> EntityResult:
        anchor_id = self._require_anchor_id(anchor_id)
        registration = self.loaded.registrations_by_anchor.get(anchor_id)
        if registration is None:
            return EntityResult(status="not_registered", anchor_id=anchor_id,
                                registration=None,
                                revision=self.loaded.revision)
        return EntityResult(
            status="registered", anchor_id=anchor_id,
            registration=RegistrationSummary(
                record_id=registration.record_id, anchor=registration.anchor,
                authority=registration.authority,
                recorded_at=registration.recorded_at),
            revision=self.loaded.revision)

    # -- variables (membership only; never hierarchy, never state) --------

    def _variable_summary(self, registration) -> VariableRegistrationSummary:
        return VariableRegistrationSummary(
            record_id=registration.record_id, anchor=registration.anchor,
            authority=registration.authority,
            recorded_at=registration.recorded_at)

    def variable(self, anchor_id: str) -> VariableResult:
        anchor_id = self._require_variable_anchor_id(anchor_id)
        registration = self.loaded.variable_registrations_by_anchor.get(
            anchor_id)
        if registration is None:
            return VariableResult(status="not_registered",
                                  anchor_id=anchor_id, registration=None,
                                  revision=self.loaded.revision)
        return VariableResult(
            status="registered", anchor_id=anchor_id,
            registration=self._variable_summary(registration),
            revision=self.loaded.revision)

    # -- constraints ------------------------------------------------------

    def constraint_declaration(
            self, constraint_anchor_id: str) -> ConstraintDeclarationResult:
        constraint_anchor_id = self._require_constraint_anchor_id(
            constraint_anchor_id)
        revision = self.loaded.revision
        registration = self.loaded.constraint_registrations_by_anchor.get(
            constraint_anchor_id)
        if registration is None:
            return ConstraintDeclarationResult(
                constraint_anchor_id=constraint_anchor_id,
                status="not_registered", revision=revision)
        tips = self.loaded.current_constraint_tips_by_anchor.get(
            constraint_anchor_id, ())
        members = tuple(
            item for item in self.loaded.constraint_declarations.values()
            if item.constraint_anchor_id == constraint_anchor_id)
        superseded = tuple(sorted(
            item.record_id for item in members
            if self.loaded.constraint_superseded_by.get(item.record_id, ())))
        if not tips:
            return ConstraintDeclarationResult(
                constraint_anchor_id=constraint_anchor_id,
                status="not_declared", registration=registration,
                revision=revision)
        if len(tips) == 1:
            return ConstraintDeclarationResult(
                constraint_anchor_id=constraint_anchor_id,
                status="declared", registration=registration,
                declaration=tips[0],
                superseded_declaration_ids=superseded,
                revision=revision)
        return ConstraintDeclarationResult(
            constraint_anchor_id=constraint_anchor_id,
            status="conflicted", registration=registration,
            conflicting_declarations=tuple(sorted(
                tips, key=lambda item: item.record_id)),
            superseded_declaration_ids=superseded,
            revision=revision)

    def constraints_of_variable(
            self, variable_anchor_id: str
    ) -> VariableConstraintCollectionResult:
        variable_anchor_id = self._require_variable_anchor_id(variable_anchor_id)
        revision = self.loaded.revision
        if variable_anchor_id not in self.loaded.variable_registrations_by_anchor:
            return VariableConstraintCollectionResult(
                variable_anchor_id=variable_anchor_id,
                status="not_registered", revision=revision)
        anchors = self.loaded.constraint_anchor_ids_by_variable.get(
            variable_anchor_id, ())
        entries = tuple(self.constraint_declaration(anchor_id)
                        for anchor_id in anchors)
        return VariableConstraintCollectionResult(
            variable_anchor_id=variable_anchor_id, status="registered",
            constraints=entries, revision=revision)

    def variables_of(self, entity_anchor_id: str) -> EntityVariablesResult:
        entity_anchor_id = self._require_anchor_id(entity_anchor_id)
        if entity_anchor_id not in self.loaded.registrations_by_anchor:
            return EntityVariablesResult(
                status="not_registered", entity_anchor_id=entity_anchor_id,
                entries=(), revision=self.loaded.revision)
        entries = tuple(
            self._variable_summary(registration)
            for anchor_id, registration in sorted(
                self.loaded.variable_registrations_by_anchor.items())
            if registration.anchor.entity_anchor_id == entity_anchor_id)
        return EntityVariablesResult(
            status="registered", entity_anchor_id=entity_anchor_id,
            entries=entries, revision=self.loaded.revision)

    def variable_value_specification(
            self, anchor_id: str) -> VariableSpecificationResult:
        """What the model requires this variable's value to be. Competing
        current tips are reported as `conflicted` with every tip carried
        verbatim — never resolved by recency, authority, record id, file
        order, or append order."""
        anchor_id = self._require_variable_anchor_id(anchor_id)
        revision = self.loaded.revision
        if anchor_id not in self.loaded.variable_registrations_by_anchor:
            return VariableSpecificationResult(
                status="not_registered", anchor_id=anchor_id,
                revision=revision)
        tips = self.loaded.current_specification_tips_by_variable.get(
            anchor_id, ())
        superseded = tuple(sorted(
            record_id for record_id, successors
            in self.loaded.specification_superseded_by.items()
            if successors and self.loaded.specifications[
                record_id].variable_anchor_id == anchor_id))
        if not tips:
            return VariableSpecificationResult(
                status="not_specified", anchor_id=anchor_id,
                superseded_specification_ids=superseded, revision=revision)
        if len(tips) > 1:
            return VariableSpecificationResult(
                status="conflicted", anchor_id=anchor_id,
                conflicting_specifications=tips,
                superseded_specification_ids=superseded, revision=revision)
        return VariableSpecificationResult(
            status="specified", anchor_id=anchor_id, specification=tips[0],
            superseded_specification_ids=superseded, revision=revision)

    def variable_semantics(self, anchor_id: str) -> VariableSemanticsResult:
        anchor_id = self._require_variable_anchor_id(anchor_id)
        revision = self.loaded.revision
        if anchor_id not in self.loaded.variable_registrations_by_anchor:
            absent = lambda dimension: SemanticDimensionResult(
                dimension=dimension, status="not_registered")
            return VariableSemanticsResult(
                anchor_id=anchor_id, quantity_kind=absent("quantity_kind"),
                observation_role=absent("observation_role"), revision=revision)

        def dimension_result(dimension: str) -> SemanticDimensionResult:
            tips = self.loaded.current_semantic_tips_by_variable_dimension.get(
                (anchor_id, dimension), ())
            superseded = tuple(sorted(
                record_id for record_id, successors
                in self.loaded.semantic_superseded_by.items()
                if successors
                and self.loaded.semantic_declarations[record_id].variable_anchor_id == anchor_id
                and self.loaded.semantic_declarations[record_id].declaration.dimension == dimension))
            if not tips:
                return SemanticDimensionResult(
                    dimension=dimension, status="not_declared",
                    superseded_declaration_ids=superseded)
            if len(tips) > 1:
                return SemanticDimensionResult(
                    dimension=dimension, status="conflicted",
                    conflicting_declarations=tips,
                    superseded_declaration_ids=superseded)
            return SemanticDimensionResult(
                dimension=dimension, status="declared", declaration=tips[0],
                superseded_declaration_ids=superseded)

        return VariableSemanticsResult(
            anchor_id=anchor_id,
            quantity_kind=dimension_result("quantity_kind"),
            observation_role=dimension_result("observation_role"),
            revision=revision)

    # -- relationships (strict context equality) ---------------------------

    def relationships(self, anchor_id: str, *, direction: str,
                      type_name: str | None = None,
                      context: AssertionContext) -> RelationshipsResult:
        anchor_id = self._require_anchor_id(anchor_id)
        if direction not in ("incoming", "outgoing", "both"):
            raise ModelQueryError("MODEL_DIRECTION_INVALID",
                                  f"{direction!r} is not a query direction")
        context = self._require_context(context)
        if type_name is not None:
            definition = self._require_type(type_name)
            if definition.context_requirement != context.kind:
                raise ModelQueryError(
                    "MODEL_CONTEXT_MISMATCH",
                    f"type {type_name!r} requires "
                    f"{definition.context_requirement} context; a "
                    f"{context.kind} query cannot match it")

        if anchor_id not in self.loaded.registrations_by_anchor:
            # absence is structured: unknown to this revision is not the
            # same answer as "registered, no declared edge"
            return RelationshipsResult(
                status="not_registered", anchor_id=anchor_id,
                direction=direction, type_name=type_name, context=context,
                active=(), inactive=(), lineage_conflicts=(),
                revision=self.loaded.revision)

        matched: list[str] = []
        for record_id in sorted(self.loaded.assertions):
            claim = self.loaded.assertions[record_id]
            involves = ((direction in ("outgoing", "both")
                         and claim.source_anchor_id == anchor_id)
                        or (direction in ("incoming", "both")
                            and claim.target_anchor_id == anchor_id))
            if not involves:
                continue
            claim_type_name = self.loaded.type_name_by_id[claim.type_id]
            if type_name is not None and claim_type_name != type_name:
                continue
            if claim.context != context:
                continue
            matched.append(record_id)

        summaries = [self._summary(record_id) for record_id in matched]
        active = tuple(s for s in summaries if s.active)
        inactive = tuple(s for s in summaries if not s.active)
        by_predecessor: dict[str, list[str]] = {}
        for summary in active:
            if summary.supersedes is not None:
                by_predecessor.setdefault(summary.supersedes, []).append(
                    summary.record_id)
        conflicts = tuple(
            LineageConflict(predecessor_id=predecessor,
                            competing_successor_ids=tuple(sorted(successors)))
            for predecessor, successors in sorted(by_predecessor.items())
            if len(successors) >= 2)
        return RelationshipsResult(
            status="registered", anchor_id=anchor_id, direction=direction,
            type_name=type_name, context=context, active=active,
            inactive=inactive, lineage_conflicts=conflicts,
            revision=self.loaded.revision)

    # -- hierarchy ---------------------------------------------------------

    def _projection(self, type_name: str, view) -> HierarchyProjection:
        return build_projection(self.loaded, type_name, view)

    def _edge_summaries(self, projection, source, target):
        return tuple(self._summary(record_id)
                     for record_id in projection.edges[(source, target)])

    def _cycle_report(self, projection, member) -> tuple[str, ...]:
        for cycle in projection.cycles:
            if member in cycle:
                return cycle
        return ()

    def parents(self, anchor_id: str, type_name: str,
                view: LifecycleView | None = None) -> ParentResult:
        anchor_id = self._require_anchor_id(anchor_id)
        self._require_hierarchy_type(type_name, view)
        common = dict(child_anchor_id=anchor_id, type_name=type_name,
                      view=view, revision=self.loaded.revision)
        if anchor_id not in self.loaded.registrations_by_anchor:
            return ParentResult(status="not_registered", **common)
        projection = self._projection(type_name, view)
        if anchor_id in projection.cycle_members:
            return ParentResult(
                status="cyclic",
                cycle_members=self._cycle_report(projection, anchor_id),
                **common)
        parent_ids = projection.parents_of.get(anchor_id, ())
        if len(parent_ids) >= 2:
            supporting = tuple(
                summary
                for parent in parent_ids
                for summary in self._edge_summaries(projection, parent,
                                                    anchor_id))
            return ParentResult(
                status="conflicted",
                candidate_parents=tuple(
                    self.loaded.registrations_by_anchor[parent].anchor
                    for parent in parent_ids),
                supporting=supporting, **common)
        if len(parent_ids) == 1:
            parent = parent_ids[0]
            return ParentResult(
                status="resolved",
                parent=self.loaded.registrations_by_anchor[parent].anchor,
                supporting=self._edge_summaries(projection, parent,
                                                anchor_id),
                **common)
        return ParentResult(status="no_declared_parent", **common)

    def children(self, anchor_id: str, type_name: str,
                 view: LifecycleView | None = None) -> ChildrenResult:
        anchor_id = self._require_anchor_id(anchor_id)
        self._require_hierarchy_type(type_name, view)
        common = dict(parent_anchor_id=anchor_id, type_name=type_name,
                      view=view, revision=self.loaded.revision)
        if anchor_id not in self.loaded.registrations_by_anchor:
            return ChildrenResult(status="not_registered", **common)
        projection = self._projection(type_name, view)
        if anchor_id in projection.cycle_members:
            return ChildrenResult(
                status="cyclic",
                cycle_members=self._cycle_report(projection, anchor_id),
                **common)
        entries = tuple(
            ChildEntry(
                anchor=self.loaded.registrations_by_anchor[child].anchor,
                supporting=self._edge_summaries(projection, anchor_id, child),
                annotations=self._annotations(projection, child))
            for child in projection.children_of.get(anchor_id, ()))
        return ChildrenResult(status="listed", entries=entries, **common)

    def _annotations(self, projection, child) -> tuple[TraversalAnnotation, ...]:
        parent_ids = projection.parents_of.get(child, ())
        if len(parent_ids) < 2:
            return ()
        via = tuple(sorted(
            record_id
            for parent in parent_ids
            for record_id in projection.edges[(parent, child)]))
        return (TraversalAnnotation(kind="multiple_parents",
                                    candidate_parent_anchor_ids=parent_ids,
                                    via_assertion_ids=via),)

    def ancestors(self, anchor_id: str, type_name: str,
                  view: LifecycleView | None = None) -> TraversalResult:
        anchor_id = self._require_anchor_id(anchor_id)
        self._require_hierarchy_type(type_name, view)
        common = dict(origin_anchor_id=anchor_id, type_name=type_name,
                      view=view, revision=self.loaded.revision)
        if anchor_id not in self.loaded.registrations_by_anchor:
            return TraversalResult(status="not_registered", **common)
        projection = self._projection(type_name, view)
        steps: list[TraversalStep] = []
        current = anchor_id
        while True:
            if current in projection.cycle_members:
                return TraversalResult(
                    status="partial", steps=tuple(steps),
                    blocked=(TraversalBlock(anchor_id=current,
                                            reason="cyclic"),), **common)
            parent_ids = projection.parents_of.get(current, ())
            if len(parent_ids) >= 2:
                return TraversalResult(
                    status="partial", steps=tuple(steps),
                    blocked=(TraversalBlock(anchor_id=current,
                                            reason="conflicted"),), **common)
            if not parent_ids:
                return TraversalResult(status="complete", steps=tuple(steps),
                                       **common)
            parent = parent_ids[0]
            steps.append(TraversalStep(
                anchor=self.loaded.registrations_by_anchor[parent].anchor,
                supporting=self._edge_summaries(projection, parent, current),
                annotations=()))
            current = parent

    def descendants(self, anchor_id: str, type_name: str,
                    view: LifecycleView | None = None) -> TraversalResult:
        anchor_id = self._require_anchor_id(anchor_id)
        self._require_hierarchy_type(type_name, view)
        common = dict(origin_anchor_id=anchor_id, type_name=type_name,
                      view=view, revision=self.loaded.revision)
        if anchor_id not in self.loaded.registrations_by_anchor:
            return TraversalResult(status="not_registered", **common)
        projection = self._projection(type_name, view)
        if anchor_id in projection.cycle_members:
            return TraversalResult(
                status="partial", steps=(),
                blocked=(TraversalBlock(anchor_id=anchor_id,
                                        reason="cyclic"),), **common)
        steps: list[TraversalStep] = []
        blocked: dict[str, TraversalBlock] = {}
        visited: set[str] = set()
        stack = [(anchor_id, child)
                 for child in reversed(
                     projection.children_of.get(anchor_id, ()))]
        while stack:
            parent, child = stack.pop()
            if child in projection.cycle_members:
                blocked.setdefault(child, TraversalBlock(
                    anchor_id=child, reason="cyclic"))
                continue
            if child in visited:
                continue
            visited.add(child)
            steps.append(TraversalStep(
                anchor=self.loaded.registrations_by_anchor[child].anchor,
                supporting=self._edge_summaries(projection, parent, child),
                annotations=self._annotations(projection, child)))
            stack.extend(
                (child, grandchild)
                for grandchild in reversed(
                    projection.children_of.get(child, ())))
        blocks = tuple(blocked[key] for key in sorted(blocked))
        return TraversalResult(
            status="partial" if blocks else "complete",
            steps=tuple(steps), blocked=blocks, **common)

    # -- PT-001 ports and topology -----------------------------------------

    def port(self, port_anchor_id: str) -> PortLookupResult:
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        registration = self.loaded.port_registrations_by_anchor.get(port_anchor_id)
        indices = self._record_index()
        return PortLookupResult(
            material=self._material(), port_anchor_id=port_anchor_id,
            status="registered" if registration is not None else "not_registered",
            registration_index=(None if registration is None
                                else indices[registration.record_id]),
            owner_registration_index=(None if registration is None else
                indices[self.loaded.registrations_by_anchor[
                    registration.owner_entity_anchor_id].record_id]))

    def ports_of_entity(self, entity_anchor_id: str) -> EntityPortsResult:
        entity_anchor_id = self._require_anchor_id(entity_anchor_id)
        registered = entity_anchor_id in self.loaded.registrations_by_anchor
        indices = self._record_index()
        anchors = self.loaded.port_anchor_ids_by_owner.get(entity_anchor_id, ())
        return EntityPortsResult(
            material=self._material(), entity_anchor_id=entity_anchor_id,
            status="registered" if registered else "owner_not_registered",
            entity_registration_index=(
                indices[self.loaded.registrations_by_anchor[
                    entity_anchor_id].record_id] if registered else None),
            port_registration_indices=tuple(
                indices[self.loaded.port_registrations_by_anchor[a].record_id]
                for a in anchors) if registered else ())

    def port_interface(self, port_anchor_id: str, *, context) -> PortInterfaceResult:
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        context = self._require_context(context)
        material = self._material()
        payload = _port_interface_payload(
            material, self.loaded, port_anchor_id, context,
            record_indices=self._record_index())
        return PortInterfaceResult(material=material, **payload)

    def port_assertion(self, record_id: str) -> PortAssertionDisclosureResult:
        record_id = self._require_port_record_id(record_id)
        material = self._material()
        payload = _port_assertion_payload(
            material, self.loaded, record_id,
            record_indices=self._record_index())
        return PortAssertionDisclosureResult(material=material, **payload)

    def _require_endpoint_set(self, endpoint_ids, *, minimum: int = 2):
        if not isinstance(endpoint_ids, (tuple, list)):
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "port endpoints must be a bounded collection")
        if not minimum <= len(endpoint_ids) <= 64:
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "port endpoints must be unique and bounded")
        try:
            values = tuple(self._require_port_anchor_id(value)
                           for value in endpoint_ids)
        except ModelQueryError as error:
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "port endpoints are invalid") from error
        if len(set(values)) != len(values):
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "port endpoints must be unique and bounded")
        return tuple(sorted(values))

    def _connection_result_parts(self, roots, requested):
        selected = tuple(
            record_id for record_id, root_id
            in self.loaded.port_connection_root_by_id.items()
            if root_id in roots)
        material = self._material()
        payload = _connection_parts_payload(
            material, self.loaded, selected, requested,
            record_indices=self._record_index())
        entries = tuple(ConnectionRootResult(**row)
                        for row in payload["roots"])
        subjects = tuple(ConnectionSubjectResult(**row)
                         for row in payload["subjects"])
        return payload["conclusion"], entries, subjects

    def connections_exact(
            self, endpoint_port_anchor_ids, *, context
    ) -> ExactConnectionSetResult:
        requested = self._require_endpoint_set(endpoint_port_anchor_ids)
        context = self._require_context(context)
        ids = self.loaded.port_connection_ids_by_subject.get((requested, context), ())
        roots = {self.loaded.port_connection_root_by_id[i] for i in ids}
        conclusion, entries, subjects = self._connection_result_parts(
            roots, requested)
        missing = tuple(
            port_id for port_id in requested
            if port_id not in self.loaded.port_registrations_by_anchor)
        return ExactConnectionSetResult(
            material=self._material(), context=context,
            admission_status=("endpoint_not_registered" if missing else
                              "admitted"),
            conclusion=conclusion, roots=entries, subjects=subjects,
            requested_port_anchor_ids=requested,
            unregistered_port_anchor_ids=missing)

    def connections_of_port(
            self, port_anchor_id: str, *, context
    ) -> PortConnectionsResult:
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        context = self._require_context(context)
        ids = tuple(i for i in self.loaded.port_connection_ids_by_port.get(port_anchor_id, ())
                    if self.loaded.port_connections[i].context == context)
        roots = {self.loaded.port_connection_root_by_id[i] for i in ids}
        conclusion, entries, subjects = self._connection_result_parts(
            roots, (port_anchor_id,))
        return PortConnectionsResult(
            material=self._material(), context=context,
            status=("registered" if port_anchor_id
                    in self.loaded.port_registrations_by_anchor else
                    "port_not_registered"),
            conclusion=conclusion,
            roots=entries, subjects=subjects, port_anchor_id=port_anchor_id,
        )

    def connections_containing(
            self, requested_port_anchor_ids, *, context
    ) -> SharedConnectionsResult:
        requested = self._require_endpoint_set(requested_port_anchor_ids)
        context = self._require_context(context)
        wanted = set(requested)
        roots = {self.loaded.port_connection_root_by_id[record_id]
                 for record_id, record in self.loaded.port_connections.items()
                 if record.context == context
                 and wanted.issubset(record.endpoint_port_anchor_ids)}
        conclusion, entries, subjects = self._connection_result_parts(
            roots, requested)
        missing = tuple(
            port_id for port_id in requested
            if port_id not in self.loaded.port_registrations_by_anchor)
        return SharedConnectionsResult(
            material=self._material(), context=context,
            admission_status=("endpoint_not_registered" if missing else
                              "admitted"),
            conclusion=conclusion,
            roots=entries, subjects=subjects,
            requested_port_anchor_ids=requested,
            unregistered_port_anchor_ids=missing)

    def interface_compatibility(self, left_port_anchor_id: str,
                                right_port_anchor_id: str, *, context
                                ) -> InterfaceCompatibilityResult:
        left_port_anchor_id = self._require_port_anchor_id(left_port_anchor_id)
        right_port_anchor_id = self._require_port_anchor_id(right_port_anchor_id)
        if left_port_anchor_id == right_port_anchor_id:
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "compatibility requires distinct endpoints")
        context = self._require_context(context)
        pair = tuple(sorted((left_port_anchor_id, right_port_anchor_id)))
        material = self._material()
        indices = self._record_index()
        left_full = self.port_interface(left_port_anchor_id, context=context)
        right_full = self.port_interface(right_port_anchor_id, context=context)
        left = EndpointInterfaceResult(
            port_anchor_id=left_port_anchor_id, status=left_full.status,
            port_registration_index=left_full.material.revision.record_ids.index(
                self.loaded.port_registrations_by_anchor[
                    left_port_anchor_id].record_id)
                if left_full.status == "registered" else None,
            owner_registration_index=(indices[
                self.loaded.registrations_by_anchor[
                    self.loaded.port_registrations_by_anchor[
                        left_port_anchor_id].owner_entity_anchor_id].record_id]
                if left_full.status == "registered" else None),
            dimensions=tuple(InterfaceDimensionResult.model_validate(
                row.model_dump()) for row in left_full.dimensions))
        right = EndpointInterfaceResult(
            port_anchor_id=right_port_anchor_id, status=right_full.status,
            port_registration_index=right_full.material.revision.record_ids.index(
                self.loaded.port_registrations_by_anchor[
                    right_port_anchor_id].record_id)
                if right_full.status == "registered" else None,
            owner_registration_index=(indices[
                self.loaded.registrations_by_anchor[
                    self.loaded.port_registrations_by_anchor[
                        right_port_anchor_id].owner_entity_anchor_id].record_id]
                if right_full.status == "registered" else None),
            dimensions=tuple(InterfaceDimensionResult.model_validate(
                row.model_dump()) for row in right_full.dimensions))

        def token_relation(position):
            lrow, rrow = left.dimensions[position], right.dimensions[position]
            statuses = {lrow.status, rrow.status}
            if "port_not_registered" in statuses:
                return "not_declared"
            if "conflicted" in statuses:
                return "conflicted"
            if "inactive" in statuses:
                return "inactive"
            if statuses != {"declared"}:
                return "not_declared"
            lvalue = self.loaded.records[
                material.revision.record_ids[lrow.declaration_index]].declaration.value
            rvalue = self.loaded.records[
                material.revision.record_ids[rrow.declaration_index]].declaration.value
            return "token_identical" if lvalue == rvalue else "token_different"

        domain_relation = token_relation(0)
        interface_type_relation = token_relation(2)
        ldir, rdir = left.dimensions[1], right.dimensions[1]
        if ldir.status != "declared" or rdir.status != "declared":
            direction = "indeterminate"
        else:
            lv = material.records[ldir.declaration_index].declaration.value
            rv = material.records[rdir.declaration_index].declaration.value
            if lv == rv == "non_directional":
                direction = "not_applicable"
            elif "non_directional" in (lv, rv):
                direction = "indeterminate"
            elif lv == rv and lv in ("input", "output"):
                direction = "inadmissible"
            else:
                direction = "admissible"

        key = (pair, context)
        pcm_ids = self.loaded.port_compatibility_ids_by_key.get(key, ())
        tips = self.loaded.current_port_compatibility_tips_by_key.get(key, ())
        stale_ids = []
        for tip in tips:
            for citation_id in self.loaded.port_compatibility_citations[
                    tip.record_id]:
                citation = self.loaded.port_interface_declarations[citation_id]
                current = self.loaded.current_port_interface_tips_by_key.get((
                    citation.port_anchor_id, context,
                    citation.declaration.dimension), ())
                if (len(current) != 1
                        or current[0].record_id != citation_id):
                    stale_ids.append(citation_id)
        stale_ids = tuple(sorted(set(stale_ids)))
        explicit_index = None
        conflicting = ()
        if not pcm_ids:
            explicit = "not_declared"
        elif not tips:
            explicit = "inactive"
        elif len(tips) > 1:
            explicit = "conflicted"
            conflicting = tuple(indices[item.record_id] for item in tips)
        else:
            explicit_index = indices[tips[0].record_id]
            explicit = "stale" if stale_ids else tips[0].outcome
        if explicit in ("declared_compatible", "declared_incompatible") and direction in (
                "admissible", "inadmissible"):
            compatible = explicit == "declared_compatible"
            admissible = direction == "admissible"
            consistency = "consistent" if compatible == admissible else "inconsistent"
        else:
            consistency = "indeterminate"
        return InterfaceCompatibilityResult(
            material=material,
            requested_left_port_anchor_id=left_port_anchor_id,
            requested_right_port_anchor_id=right_port_anchor_id,
            endpoint_port_anchor_ids=pair, context=context,
            endpoint_registration_status=(
                "both_registered"
                if left.status == right.status == "registered" else
                "left_not_registered"
                if left.status != "registered" and right.status == "registered" else
                "right_not_registered"
                if left.status == "registered" and right.status != "registered" else
                "both_not_registered"),
            left_interface=left, right_interface=right,
            domain_relation=domain_relation,
            interface_type_relation=interface_type_relation,
            direction_relation=direction, explicit_status=explicit,
            explicit_declaration_index=explicit_index,
            conflicting_explicit_declaration_indices=conflicting,
            pcm_lineage_record_indices=tuple(indices[i] for i in pcm_ids),
            current_pcm_tip_indices=tuple(indices[i.record_id] for i in tips),
            stale_citation_indices=tuple(indices[i] for i in stale_ids),
            consistency=consistency)

    # -- BH-001 explicit behavior declarations ----------------------------

    def behavior(self, behavior_anchor_id) -> BehaviorLookupResult:
        behavior_anchor_id = self._require_behavior_anchor_id(
            behavior_anchor_id)
        material = self._material()
        return BehaviorLookupResult(
            material=material,
            **_behavior_lookup_payload(
                material, self.loaded, behavior_anchor_id))

    def behavior_declaration(
            self, behavior_anchor_id, *, context
    ) -> BehaviorRuleResult:
        behavior_anchor_id = self._require_behavior_anchor_id(
            behavior_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return BehaviorRuleResult(
            material=material,
            **_behavior_rule_payload(
                material, self.loaded, behavior_anchor_id, context))

    def behaviors_involving_variable(
            self, variable_anchor_id, *, context
    ) -> VariableBehaviorsResult:
        variable_anchor_id = self._require_variable_anchor_id(
            variable_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return VariableBehaviorsResult(
            material=material,
            **_variable_behaviors_payload(
                material, self.loaded, variable_anchor_id, context))

    def behavior_assertion(
            self, record_id
    ) -> BehaviorAssertionDisclosureResult:
        record_id = self._require_behavior_record_id(record_id)
        material = self._material()
        return BehaviorAssertionDisclosureResult(
            material=material,
            **_behavior_assertion_payload(
                material, self.loaded, record_id))

    # -- ST-001 explicit state declarations -------------------------------

    def state(self, state_anchor_id) -> StateLookupResult:
        state_anchor_id = self._require_state_anchor_id(state_anchor_id)
        material = self._material()
        return StateLookupResult(
            material=material,
            **_state_lookup_payload(material, self.loaded, state_anchor_id))

    def state_declaration(
            self, state_anchor_id, *, context
    ) -> StateDeclarationResult:
        state_anchor_id = self._require_state_anchor_id(state_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return StateDeclarationResult(
            material=material,
            **_state_declaration_payload(
                material, self.loaded, state_anchor_id, context))

    def states_of_entity(
            self, entity_anchor_id, *, context
    ) -> EntityStatesResult:
        entity_anchor_id = self._require_anchor_id(entity_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return EntityStatesResult(
            material=material,
            **_entity_states_payload(
                material, self.loaded, entity_anchor_id, context))

    def state_assertion(
            self, record_id
    ) -> StateAssertionDisclosureResult:
        record_id = self._require_state_record_id(record_id)
        material = self._material()
        return StateAssertionDisclosureResult(
            material=material,
            **_state_assertion_payload(material, self.loaded, record_id))

    # -- ST-002 explicit transition declarations --------------------------

    def transition(
            self, transition_anchor_id
    ) -> TransitionLookupResult:
        transition_anchor_id = self._require_transition_anchor_id(
            transition_anchor_id)
        material = self._material()
        return TransitionLookupResult(
            material=material,
            **_transition_lookup_payload(
                material, self.loaded, transition_anchor_id))

    def transition_declaration(
            self, transition_anchor_id, *, context
    ) -> TransitionDeclarationResult:
        transition_anchor_id = self._require_transition_anchor_id(
            transition_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return TransitionDeclarationResult(
            material=material,
            **_transition_declaration_payload(
                material, self.loaded, transition_anchor_id, context))

    def transitions_of_entity(
            self, entity_anchor_id, *, context
    ) -> EntityTransitionsResult:
        entity_anchor_id = self._require_anchor_id(entity_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return EntityTransitionsResult(
            material=material,
            **_entity_transitions_payload(
                material, self.loaded, entity_anchor_id, context))

    def transition_assertion(
            self, record_id
    ) -> TransitionAssertionDisclosureResult:
        record_id = self._require_transition_record_id(record_id)
        material = self._material()
        return TransitionAssertionDisclosureResult(
            material=material,
            **_transition_assertion_payload(
                material, self.loaded, record_id))

    # -- FL-001 explicit logical-flow declarations -----------------------

    def flow(self, flow_anchor_id) -> FlowLookupResult:
        flow_anchor_id = self._require_flow_anchor_id(flow_anchor_id)
        material = self._material()
        return FlowLookupResult(
            material=material,
            **_flow_lookup_payload(material, self.loaded, flow_anchor_id))

    def flow_declaration(
            self, flow_anchor_id, *, context
    ) -> FlowDeclarationResult:
        flow_anchor_id = self._require_flow_anchor_id(flow_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return FlowDeclarationResult(
            material=material,
            **_flow_declaration_payload(
                material, self.loaded, flow_anchor_id, context))

    def flows_involving_port(
            self, port_anchor_id, *, context
    ) -> PortFlowsResult:
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        context = self._require_context(context)
        material = self._material()
        return PortFlowsResult(
            material=material,
            **_port_flows_payload(
                material, self.loaded, port_anchor_id, context))

    def flow_assertion(
            self, record_id
    ) -> FlowAssertionDisclosureResult:
        record_id = self._require_flow_record_id(record_id)
        material = self._material()
        return FlowAssertionDisclosureResult(
            material=material,
            **_flow_assertion_payload(material, self.loaded, record_id))

    # -- FM-001 explicit flow-to-measurement associations ---------------

    def flow_measurement_association(
            self, flow_anchor_id, variable_anchor_id,
            participant_port_anchor_id, context, orientation
    ) -> FlowMeasurementAssociationResult:
        if type(flow_anchor_id) is not str:
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                "flow anchor id is not canonical")
        if type(variable_anchor_id) is not str:
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                "variable anchor id is not canonical")
        if type(participant_port_anchor_id) is not str:
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                "participant port anchor id is not canonical")
        flow_anchor_id = self._require_flow_anchor_id(flow_anchor_id)
        variable_anchor_id = self._require_variable_anchor_id(variable_anchor_id)
        participant_port_anchor_id = self._require_port_anchor_id(
            participant_port_anchor_id)
        context = self._require_flow_measurement_context(context)
        orientation = self._require_flow_measurement_orientation(orientation)
        material = self._material()
        return FlowMeasurementAssociationResult(
            material=material,
            **_flow_measurement_exact_payload(
                material, self.loaded, flow_anchor_id, variable_anchor_id,
                participant_port_anchor_id, context, orientation))

    def flow_measurement_associations_for_flow(
            self, flow_anchor_id, *, context
    ) -> FlowMeasurementAssociationsForFlowResult:
        if type(flow_anchor_id) is not str:
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                "flow anchor id is not canonical")
        flow_anchor_id = self._require_flow_anchor_id(flow_anchor_id)
        context = self._require_flow_measurement_context(context)
        material = self._material()
        return FlowMeasurementAssociationsForFlowResult(
            material=material,
            **_flow_measurement_reverse_payload(
                material, self.loaded, flow_anchor_id, context, axis="flow"))

    def flow_measurement_associations_for_variable(
            self, variable_anchor_id, *, context
    ) -> FlowMeasurementAssociationsForVariableResult:
        if type(variable_anchor_id) is not str:
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                "variable anchor id is not canonical")
        variable_anchor_id = self._require_variable_anchor_id(variable_anchor_id)
        context = self._require_flow_measurement_context(context)
        material = self._material()
        return FlowMeasurementAssociationsForVariableResult(
            material=material,
            **_flow_measurement_reverse_payload(
                material, self.loaded, variable_anchor_id, context,
                axis="variable"))

    def flow_measurement_associations_at_port(
            self, participant_port_anchor_id, *, context
    ) -> FlowMeasurementAssociationsAtPortResult:
        if type(participant_port_anchor_id) is not str:
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                "participant port anchor id is not canonical")
        participant_port_anchor_id = self._require_port_anchor_id(
            participant_port_anchor_id)
        context = self._require_flow_measurement_context(context)
        material = self._material()
        return FlowMeasurementAssociationsAtPortResult(
            material=material,
            **_flow_measurement_reverse_payload(
                material, self.loaded, participant_port_anchor_id, context,
                axis="port"))

    def flow_measurement_assertion(
            self, record_id
    ) -> FlowMeasurementAssertionResult:
        record_id = self._require_flow_measurement_record_id(record_id)
        material = self._material()
        return FlowMeasurementAssertionResult(
            material=material,
            **_flow_measurement_assertion_payload(
                material, self.loaded, record_id))

    # -- FC-001 explicit governing criterion ------------------------------
    def _flow_operating_criterion_subject(self, flow_anchor_id, variable_anchor_id,
                                          participant_port_anchor_id, context, orientation):
        material = self._material()
        indices = self._record_index()
        subject = (flow_anchor_id, variable_anchor_id, participant_port_anchor_id,
                   context, "direct_measurement_relevance", orientation)
        def lineage_rows(root_map, tips_map, withdrawn_map, subject_ids):
            roots = sorted({root_map[x] for x in subject_ids})
            out=[]
            for ri, root in enumerate(roots):
                ids=tuple(sorted(x for x in subject_ids if root_map[x]==root))
                tips=tuple(sorted(x for x in tips_map.get(root, ()) if x in ids))
                ws=tuple(sorted(w for x in ids for w in withdrawn_map.get(x, ())))
                out.append(FlowOperatingCriterionLineageRow(
                    root_index=ri, root_record_index=indices[root],
                    lineage_record_indices=tuple(indices[x] for x in ids),
                    current_tip_indices=tuple(indices[x] for x in tips),
                    withdrawal_indices=tuple(indices[x] for x in ws),
                    lineage_health=("inactive" if not tips else "conflicted" if len(tips)>1 else "healthy")))
            return tuple(out)
        fc_ids=tuple(sorted(x for x,s in self.loaded.flow_operating_criterion_subject_by_id.items() if s==subject))
        fm_ids=tuple(self.loaded.flow_measurement_ids_by_subject.get(subject, ()))
        fc_roots=lineage_rows(self.loaded.flow_operating_criterion_root_by_id,
                              self.loaded.flow_operating_criterion_current_tips_by_root,
                              self.loaded.flow_operating_criterion_withdrawn_by, fc_ids)
        fm_roots=lineage_rows(self.loaded.flow_measurement_root_by_id,
                              self.loaded.current_flow_measurement_tips_by_root,
                              self.loaded.flow_measurement_withdrawn_by, fm_ids)
        bodies={}
        for rid in fc_ids:
            body=self.loaded.flow_operating_criterion_effective_body_by_id[rid]
            bodies.setdefault(body,[]).append(rid)
        groups=[]
        for gi, body in enumerate(sorted(bodies)):
            ids=tuple(sorted(bodies[body])); current=tuple(x for x in ids if not self.loaded.flow_operating_criterion_successor_ids[x] and not self.loaded.flow_operating_criterion_withdrawn_by[x])
            witnesses=tuple(sorted({self.loaded.flow_operating_criterion_declarations[x].flow_measurement_association_record_id for x in ids}))
            matching=tuple(indices[x] for x in fm_ids if self.loaded.flow_measurement_effective_body_by_id[x] == body and not self.loaded.flow_measurement_successor_ids[x] and not self.loaded.flow_measurement_withdrawn_by[x])
            support=[]
            if ids:
                d=self.loaded.flow_operating_criterion_declarations[ids[0]]
                for kind, rid in (("crg", d.constraint_registration_record_id),("vcn", d.constraint_declaration_record_id)):
                    if rid in indices: support.append(FlowOperatingCriterionSupportRow(support_kind=kind,record_index=indices[rid],activity="current",lineage_health="healthy",alignment="exact"))
            groups.append(FlowOperatingCriterionBodyRow(group_index=gi,declaration_indices=tuple(indices[x] for x in ids),current_declaration_indices=tuple(indices[x] for x in current),witness_record_indices=tuple(indices[x] for x in witnesses),matching_fm_current_indices=matching,support_rows=tuple(support),reasons=()))
        active=[i for i,g in enumerate(groups) if g.current_declaration_indices]
        if not fc_ids: conclusion="not_declared"; reasons=("fc_not_declared",); gi=None
        elif not active: conclusion="inactive"; reasons=("fc_inactive",); gi=None
        elif any(row.lineage_health == "conflicted" for row in fc_roots): conclusion="conflicted"; reasons=("fc_same_root_conflict",); gi=None
        elif len(active)>1: conclusion="disagreed"; reasons=("fc_cross_root_disagreement",); gi=None
        else: conclusion="applicable"; reasons=(); gi=active[0]
        result=FlowOperatingCriterionSubjectResult(flow_anchor_id=flow_anchor_id,variable_anchor_id=variable_anchor_id,participant_port_anchor_id=participant_port_anchor_id,context=context,orientation=orientation,conclusion=conclusion,reasons=reasons,roots=fc_roots,fm_roots=fm_roots,body_groups=tuple(groups),governing_body_group_index=gi)
        return material,result

    def flow_operating_criterion(self, flow_anchor_id: str, variable_anchor_id: str,
                                 participant_port_anchor_id: str, context, orientation) -> FlowOperatingCriterionResult:
        flow_anchor_id=self._require_flow_anchor_id(flow_anchor_id)
        variable_anchor_id=self._require_variable_anchor_id(variable_anchor_id)
        participant_port_anchor_id=self._require_port_anchor_id(participant_port_anchor_id)
        context=self._require_flow_measurement_context(context)
        orientation=self._require_flow_measurement_orientation(orientation)
        material, subject=self._flow_operating_criterion_subject(flow_anchor_id,variable_anchor_id,participant_port_anchor_id,context,orientation)
        return FlowOperatingCriterionResult(material=material,subject=subject)

    def flow_operating_criterion_assertion(self, record_id: str) -> FlowOperatingCriterionAssertionResult:
        if type(record_id) is not str or not re.fullmatch(r"^(?:fcd|fcw)_[0-9a-f]{64}$", record_id):
            raise ModelQueryError("MODEL_FLOW_CRITERION_QUERY_INVALID", "record id is not a canonical FC id")
        material=self._material(); indices=self._record_index()
        record=self.loaded.records.get(record_id)
        if record is None or record.record_kind not in {"flow_operating_criterion_declaration","flow_operating_criterion_withdrawal"}:
            return FlowOperatingCriterionAssertionResult(material=material,record_id=record_id,lookup_status="not_found",record_index=None,positive_record_index=None,positive_activity=None,body_group_index=None,subject=None)
        target=record_id if record.record_kind=="flow_operating_criterion_declaration" else record.withdraws
        d=self.loaded.flow_operating_criterion_declarations[target]; s=self.loaded.flow_operating_criterion_subject_by_id[target]
        material2, subject=self._flow_operating_criterion_subject(s[0], s[1], s[2], s[3], s[5])
        activity="current" if not self.loaded.flow_operating_criterion_successor_ids[target] and not self.loaded.flow_operating_criterion_withdrawn_by[target] else "withdrawn" if self.loaded.flow_operating_criterion_withdrawn_by[target] else "superseded"
        body=self.loaded.flow_operating_criterion_effective_body_by_id[target]
        gi=next((i for i,g in enumerate(subject.body_groups) if indices[target] in g.declaration_indices),None)
        return FlowOperatingCriterionAssertionResult(material=material2,record_id=record_id,lookup_status="found",record_index=indices[record_id],positive_record_index=indices[target],positive_activity=activity,body_group_index=gi,subject=subject)

    # -- VP-001 explicit variable-to-port associations --------------------

    def _variable_port_root_results(self, root_ids):
        indices = self._record_index()
        rows = []
        for root_id in sorted(set(root_ids)):
            lineage_ids = tuple(sorted(
                record_id for record_id, candidate_root
                in self.loaded.variable_port_association_root_by_id.items()
                if candidate_root == root_id))
            tips = tuple(sorted(
                self.loaded.current_variable_port_association_tips_by_root[
                    root_id], key=lambda record: record.record_id))
            withdrawals = tuple(sorted(
                withdrawal_id
                for record_id in lineage_ids
                for withdrawal_id in
                self.loaded.variable_port_association_withdrawn_by[record_id]))
            rows.append(VariablePortAssociationRootResult(
                root_record_index=indices[root_id],
                lineage_record_indices=tuple(indices[record_id]
                                             for record_id in lineage_ids),
                current_tip_indices=tuple(indices[record.record_id]
                                         for record in tips),
                withdrawal_indices=tuple(indices[record_id]
                                         for record_id in withdrawals),
                lineage_health=(
                    "inactive" if not tips else
                    "conflicted" if len(tips) > 1 else
                    "healthy"),
            ))
        return tuple(rows)

    @staticmethod
    def _variable_port_aggregate(roots):
        if not roots:
            return "not_declared", "not_applicable"
        active = tuple(root for root in roots if root.current_tip_indices)
        if not active:
            return "inactive", "inactive"
        return (
            "asserted",
            "conflicted" if any(root.lineage_health == "conflicted"
                                for root in active) else "healthy",
        )

    def variable_port_association(
            self, variable_anchor_id, port_anchor_id, *, context
    ) -> VariablePortAssociationResult:
        variable_anchor_id = self._require_variable_anchor_id(
            variable_anchor_id)
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        context = self._require_context(context)
        material = self._material()
        indices = self._record_index()
        variable = self.loaded.variable_registrations_by_anchor.get(
            variable_anchor_id)
        port = self.loaded.port_registrations_by_anchor.get(port_anchor_id)
        endpoint_status = (
            "both_registered" if variable is not None and port is not None else
            "variable_not_registered" if variable is None and port is not None else
            "port_not_registered" if variable is not None and port is None else
            "both_not_registered")
        variable_owner_id = (None if variable is None else
                             variable.anchor.entity_anchor_id)
        port_owner_id = (None if port is None else
                         port.owner_entity_anchor_id)
        variable_index = (None if variable is None else
                          indices[variable.record_id])
        variable_owner_index = (None if variable_owner_id is None else
            indices[self.loaded.registrations_by_anchor[
                variable_owner_id].record_id])
        port_index = None if port is None else indices[port.record_id]
        port_owner_index = (None if port_owner_id is None else
            indices[self.loaded.registrations_by_anchor[
                port_owner_id].record_id])
        if variable is None or port is None:
            owner_alignment = "not_evaluated"
            conclusion, lineage_summary = "not_evaluated", "not_applicable"
            roots = ()
        elif variable_owner_id != port_owner_id:
            owner_alignment = "different_owners"
            conclusion, lineage_summary = "not_evaluated", "not_applicable"
            roots = ()
        else:
            owner_alignment = "same_owner"
            association_ids = (
                self.loaded.variable_port_association_ids_by_subject.get(
                    (variable_anchor_id, port_anchor_id, context), ()))
            roots = self._variable_port_root_results(
                self.loaded.variable_port_association_root_by_id[record_id]
                for record_id in association_ids)
            conclusion, lineage_summary = self._variable_port_aggregate(roots)
        return VariablePortAssociationResult(
            material=material,
            variable_anchor_id=variable_anchor_id,
            port_anchor_id=port_anchor_id,
            context=context,
            endpoint_status=endpoint_status,
            owner_alignment=owner_alignment,
            variable_registration_index=variable_index,
            variable_owner_registration_index=variable_owner_index,
            port_registration_index=port_index,
            port_owner_registration_index=port_owner_index,
            conclusion=conclusion,
            lineage_summary=lineage_summary,
            roots=roots,
        )

    def _variable_port_entries(self, association_ids, *, order_by):
        indices = self._record_index()
        roots_by_subject = {}
        for record_id in association_ids:
            record = self.loaded.variable_port_associations[record_id]
            subject = (record.variable_anchor_id, record.port_anchor_id,
                       record.context)
            roots_by_subject.setdefault(subject, set()).add(
                self.loaded.variable_port_association_root_by_id[record_id])
        pending = []
        for (variable_anchor_id, port_anchor_id, _), root_ids \
                in roots_by_subject.items():
            variable = self.loaded.variable_registrations_by_anchor[
                variable_anchor_id]
            port = self.loaded.port_registrations_by_anchor[port_anchor_id]
            roots = self._variable_port_root_results(root_ids)
            conclusion, summary = self._variable_port_aggregate(roots)
            first_root_id = min(root_ids)
            sort_anchor = (port_anchor_id if order_by == "port" else
                           variable_anchor_id)
            pending.append(((sort_anchor, first_root_id), {
                "variable_anchor_id": variable_anchor_id,
                "port_anchor_id": port_anchor_id,
                "variable_registration_index": indices[variable.record_id],
                "variable_owner_registration_index": indices[
                    self.loaded.registrations_by_anchor[
                        variable.anchor.entity_anchor_id].record_id],
                "port_registration_index": indices[port.record_id],
                "port_owner_registration_index": indices[
                    self.loaded.registrations_by_anchor[
                        port.owner_entity_anchor_id].record_id],
                "conclusion": conclusion,
                "lineage_summary": summary,
                "roots": roots,
            }))
        return tuple(VariablePortAssociationEntry(
            entry_index=entry_index, **payload)
            for entry_index, (_, payload) in enumerate(sorted(pending)))

    def ports_associated_with_variable(
            self, variable_anchor_id, *, context
    ) -> VariablePortsResult:
        variable_anchor_id = self._require_variable_anchor_id(
            variable_anchor_id)
        context = self._require_context(context)
        material = self._material()
        indices = self._record_index()
        variable = self.loaded.variable_registrations_by_anchor.get(
            variable_anchor_id)
        if variable is None:
            return VariablePortsResult(
                material=material, variable_anchor_id=variable_anchor_id,
                context=context, status="variable_not_registered")
        association_ids = (
            self.loaded.variable_port_association_ids_by_variable_context.get(
                (variable_anchor_id, context), ()))
        return VariablePortsResult(
            material=material, variable_anchor_id=variable_anchor_id,
            context=context, status="registered",
            variable_registration_index=indices[variable.record_id],
            owner_registration_index=indices[
                self.loaded.registrations_by_anchor[
                    variable.anchor.entity_anchor_id].record_id],
            entries=self._variable_port_entries(
                association_ids, order_by="port"),
        )

    def variables_associated_with_port(
            self, port_anchor_id, *, context
    ) -> PortVariablesResult:
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        context = self._require_context(context)
        material = self._material()
        indices = self._record_index()
        port = self.loaded.port_registrations_by_anchor.get(port_anchor_id)
        if port is None:
            return PortVariablesResult(
                material=material, port_anchor_id=port_anchor_id,
                context=context, status="port_not_registered")
        association_ids = (
            self.loaded.variable_port_association_ids_by_port_context.get(
                (port_anchor_id, context), ()))
        return PortVariablesResult(
            material=material, port_anchor_id=port_anchor_id,
            context=context, status="registered",
            port_registration_index=indices[port.record_id],
            owner_registration_index=indices[
                self.loaded.registrations_by_anchor[
                    port.owner_entity_anchor_id].record_id],
            entries=self._variable_port_entries(
                association_ids, order_by="variable"),
        )

    def variable_port_assertion(
            self, record_id
    ) -> VariablePortAssertionDisclosureResult:
        record_id = self._require_variable_port_record_id(record_id)
        material = self._material()
        indices = self._record_index()
        record = self.loaded.records.get(record_id)
        if record is None or record.record_kind not in {
                "variable_port_association",
                "variable_port_association_withdrawal"}:
            return VariablePortAssertionDisclosureResult(
                material=material, record_id=record_id,
                lookup_status="not_found")
        if record.record_kind == "variable_port_association_withdrawal":
            return VariablePortAssertionDisclosureResult(
                material=material, record_id=record_id,
                lookup_status="found", record_index=indices[record_id])
        root_id = self.loaded.variable_port_association_root_by_id[record_id]
        tips = self.loaded.current_variable_port_association_tips_by_root[
            root_id]
        successors = self.loaded.variable_port_association_superseded_by[
            record_id]
        withdrawals = self.loaded.variable_port_association_withdrawn_by[
            record_id]
        return VariablePortAssertionDisclosureResult(
            material=material, record_id=record_id, lookup_status="found",
            record_index=indices[record_id],
            activity=("superseded" if successors else
                      "withdrawn" if withdrawals else "current"),
            containing_lineage_health=(
                "inactive" if not tips else
                "conflicted" if len(tips) > 1 else "healthy"),
            root_record_index=indices[root_id],
            successor_indices=tuple(indices[item]
                                    for item in sorted(successors)),
            withdrawal_indices=tuple(indices[item]
                                     for item in sorted(withdrawals)),
        )

    # -- health ------------------------------------------------------------

    def hierarchy_health(self, type_name: str,
                         view: LifecycleView | None = None) -> HierarchyHealth:
        self._require_hierarchy_type(type_name, view)
        projection = self._projection(type_name, view)
        cycles = tuple(
            CycleReport(
                members=cycle,
                via_assertion_ids=tuple(sorted(
                    record_id
                    for (source, target), ids in projection.edges.items()
                    if source in cycle and target in cycle
                    for record_id in ids)))
            for cycle in projection.cycles)
        conflicts = tuple(
            ParentConflictReport(
                child_anchor_id=child,
                candidate_parent_anchor_ids=parent_ids,
                via_assertion_ids=tuple(sorted(
                    record_id
                    for parent in parent_ids
                    for record_id in projection.edges[(parent, child)])))
            for child, parent_ids in sorted(projection.parents_of.items())
            if len(parent_ids) >= 2)
        return HierarchyHealth(
            type_name=type_name, view=view, cycles=cycles,
            parent_conflicts=conflicts,
            stale_type_assertions=projection.stale_assertion_ids,
            revision=self.loaded.revision)
