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

from pydantic import TypeAdapter, ValidationError

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
from backend.model_kernel.port_results import (
    ConnectionRootResult, ContainingConnectionsResult, EndpointInterfaceResult,
    EntityPortsResult,
    ExactConnectionsResult, IncidentConnectionsResult,
    InterfaceCompatibilityResult, InterfaceDimensionResult, ModelQueryMaterial, PortAssertionResult,
    PortInterfaceResult, PortResult,
)
from backend.model_kernel.store import LoadedModel
from backend.system_identity import (
    CONSTRAINT_ANCHOR_ID_PATTERN,
    ENTITY_ANCHOR_ID_PATTERN,
    PORT_ANCHOR_ID_PATTERN,
    VARIABLE_ANCHOR_ID_PATTERN,
)

_ANCHOR_ID = re.compile(ENTITY_ANCHOR_ID_PATTERN)
_VARIABLE_ANCHOR_ID = re.compile(VARIABLE_ANCHOR_ID_PATTERN)
_CONSTRAINT_ANCHOR_ID = re.compile(CONSTRAINT_ANCHOR_ID_PATTERN)
_PORT_ANCHOR_ID = re.compile(PORT_ANCHOR_ID_PATTERN)
_PORT_RECORD_ID = re.compile(r"^(?:prg|pif|pcn|pcm|ptw)_[0-9a-f]{64}$")
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

    def _require_port_record_id(self, record_id: str) -> str:
        if (not isinstance(record_id, str)
                or not _PORT_RECORD_ID.fullmatch(record_id)):
            raise ModelQueryError("MODEL_RECORD_ID_INVALID",
                                  f"{record_id!r} is not a PT record id")
        return record_id

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
            return _CONTEXT_ADAPTER.validate_python(context)
        except ValidationError as error:
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

    def port(self, port_anchor_id: str) -> PortResult:
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        registration = self.loaded.port_registrations_by_anchor.get(port_anchor_id)
        indices = self._record_index()
        return PortResult(
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
            status="registered" if registered else "not_registered",
            entity_registration_index=(
                indices[self.loaded.registrations_by_anchor[
                    entity_anchor_id].record_id] if registered else None),
            port_registration_indices=tuple(
                indices[self.loaded.port_registrations_by_anchor[a].record_id]
                for a in anchors) if registered else ())

    def port_interface(self, port_anchor_id: str, *, context) -> PortInterfaceResult:
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        context = self._require_context(context)
        registered = port_anchor_id in self.loaded.port_registrations_by_anchor
        material = self._material()
        indices = self._record_index()
        rows = []
        for dimension in ("interface_domain", "direction_role", "interface_type"):
            key = (port_anchor_id, context, dimension)
            ids = self.loaded.port_interface_ids_by_key.get(key, ()) if registered else ()
            tips = self.loaded.current_port_interface_tips_by_key.get(key, ()) if ids else ()
            withdrawals = tuple(sorted(
                withdrawal_id for record_id in ids
                for withdrawal_id in self.loaded.port_interface_withdrawn_by[record_id]))
            if not registered:
                status = "port_not_registered"
            elif not ids:
                status = "not_declared"
            elif len(tips) == 1:
                status = "declared"
            elif len(tips) > 1:
                status = "conflicted"
            else:
                status = "inactive"
            rows.append(InterfaceDimensionResult(
                dimension=dimension, status=status,
                lineage_health=(
                    "healthy" if status == "declared" else
                    "conflicted" if status == "conflicted" else
                    "inactive" if status == "inactive" else
                    "not_applicable"),
                lineage_record_indices=tuple(indices[i] for i in ids),
                current_tip_indices=tuple(indices[r.record_id] for r in tips),
                withdrawal_indices=tuple(indices[i] for i in withdrawals),
                declaration_index=(indices[tips[0].record_id]
                                   if status == "declared" else None),
                conflicting_declaration_indices=(
                    tuple(indices[r.record_id] for r in tips)
                    if status == "conflicted" else ()),
                superseded_declaration_indices=(
                    tuple(indices[i] for i in ids
                          if self.loaded.port_interface_superseded_by[i])
                    if registered else ()),
                inactive_declaration_indices=(
                    tuple(indices[i] for i in ids)
                    if status == "inactive" else ())))
        return PortInterfaceResult(
            material=material, port_anchor_id=port_anchor_id,
            status="registered" if registered else "not_registered",
            context=context, dimensions=tuple(rows))

    def port_assertion(self, record_id: str) -> PortAssertionResult:
        record_id = self._require_port_record_id(record_id)
        material = self._material()
        indices = self._record_index()
        record = self.loaded.records.get(record_id)
        if record is None or record.record_kind not in {
                "port_registration", "port_interface_declaration",
                "port_connection_assertion", "port_compatibility_declaration",
                "port_claim_withdrawal"}:
            return PortAssertionResult(material=material, record_id=record_id,
                                       status="not_found")
        if record.record_kind in {"port_registration", "port_claim_withdrawal"}:
            return PortAssertionResult(material=material, record_id=record_id,
                                       status="found", record_index=indices[record_id])
        if record.record_kind == "port_interface_declaration":
            roots = self.loaded.port_interface_root_by_id
            successors = self.loaded.port_interface_superseded_by
            withdrawn = self.loaded.port_interface_withdrawn_by
            current_by_root = {
                root: tuple(item for item in self.loaded.port_interface_declarations.values()
                            if roots[item.record_id] == root
                            and not successors[item.record_id]
                            and not withdrawn[item.record_id])
                for root in set(roots.values())}
        elif record.record_kind == "port_connection_assertion":
            roots = self.loaded.port_connection_root_by_id
            successors = self.loaded.port_connection_superseded_by
            withdrawn = self.loaded.port_connection_withdrawn_by
            current_by_root = self.loaded.current_port_connection_tips_by_root
        else:
            roots = self.loaded.port_compatibility_root_by_id
            successors = self.loaded.port_compatibility_superseded_by
            withdrawn = self.loaded.port_compatibility_withdrawn_by
            current_by_root = {
                root: tuple(item for item in self.loaded.port_compatibility_declarations.values()
                            if roots[item.record_id] == root
                            and not successors[item.record_id]
                            and not withdrawn[item.record_id])
                for root in set(roots.values())}
        root = roots[record_id]
        tips = current_by_root[root]
        health = "inactive" if not tips else ("conflicted" if len(tips) > 1 else "healthy")
        activity = ("superseded" if successors[record_id] else
                    "withdrawn" if withdrawn[record_id] else "current")
        return PortAssertionResult(
            material=material, record_id=record_id, status="found",
            record_index=indices[record_id], activity=activity,
            lineage_health=health, root_record_index=indices[root],
            successor_indices=tuple(indices[i] for i in successors[record_id]),
            withdrawal_indices=tuple(indices[i] for i in withdrawn[record_id]))

    def _require_endpoint_set(self, endpoint_ids, *, minimum: int = 2):
        if not isinstance(endpoint_ids, (tuple, list)):
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "port endpoints must be a bounded collection")
        try:
            values = tuple(self._require_port_anchor_id(value)
                           for value in endpoint_ids)
        except ModelQueryError as error:
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "port endpoints are invalid") from error
        if not minimum <= len(values) <= 64 or len(set(values)) != len(values):
            raise ModelQueryError("MODEL_PORT_ENDPOINTS_INVALID",
                                  "port endpoints must be unique and bounded")
        return tuple(sorted(values))

    def _connection_result_parts(self, roots, requested):
        indices = self._record_index()
        entries = []
        for position, root_id in enumerate(sorted(roots)):
            lineage_ids = tuple(sorted(
                record_id for record_id, candidate_root
                in self.loaded.port_connection_root_by_id.items()
                if candidate_root == root_id))
            tips = self.loaded.current_port_connection_tips_by_root[root_id]
            withdrawals = tuple(sorted(
                withdrawal_id for record_id in lineage_ids
                for withdrawal_id in self.loaded.port_connection_withdrawn_by[record_id]))
            health = "inactive" if not tips else ("conflicted" if len(tips) > 1 else "healthy")
            entries.append(ConnectionRootResult(
                root_index=position, root_record_index=indices[root_id],
                lineage_record_indices=tuple(indices[i] for i in lineage_ids),
                current_tip_indices=tuple(indices[r.record_id] for r in tips),
                withdrawal_indices=tuple(indices[i] for i in withdrawals),
                lineage_health=health,
                exact_endpoint_set=(self.loaded.port_connections[root_id].endpoint_port_anchor_ids
                                    == requested)))
        status = ("unknown" if not entries else
                  "asserted" if any(entry.current_tip_indices for entry in entries)
                  else "inactive")
        return status, tuple(entries)

    def connections_exact(self, endpoint_port_anchor_ids, *, context):
        requested = self._require_endpoint_set(endpoint_port_anchor_ids)
        context = self._require_context(context)
        ids = self.loaded.port_connection_ids_by_subject.get((requested, context), ())
        roots = {self.loaded.port_connection_root_by_id[i] for i in ids}
        status, entries = self._connection_result_parts(roots, requested)
        return ExactConnectionsResult(material=self._material(), context=context,
                                      status=status, roots=entries,
                                      requested_port_anchor_ids=requested)

    def connections_of_port(self, port_anchor_id: str, *, context):
        port_anchor_id = self._require_port_anchor_id(port_anchor_id)
        context = self._require_context(context)
        ids = tuple(i for i in self.loaded.port_connection_ids_by_port.get(port_anchor_id, ())
                    if self.loaded.port_connections[i].context == context)
        roots = {self.loaded.port_connection_root_by_id[i] for i in ids}
        status, entries = self._connection_result_parts(roots, (port_anchor_id,))
        return IncidentConnectionsResult(
            material=self._material(), context=context, status=status,
            roots=entries, port_anchor_id=port_anchor_id,
            port_status=("registered" if port_anchor_id in self.loaded.port_registrations_by_anchor
                         else "not_registered"))

    def connections_containing(self, requested_port_anchor_ids, *, context):
        requested = self._require_endpoint_set(requested_port_anchor_ids)
        context = self._require_context(context)
        wanted = set(requested)
        roots = {self.loaded.port_connection_root_by_id[record_id]
                 for record_id, record in self.loaded.port_connections.items()
                 if record.context == context
                 and wanted.issubset(record.endpoint_port_anchor_ids)}
        status, entries = self._connection_result_parts(roots, requested)
        return ContainingConnectionsResult(
            material=self._material(), context=context, status=status,
            roots=entries, requested_port_anchor_ids=requested,
            unregistered_port_anchor_ids=tuple(
                p for p in requested
                if p not in self.loaded.port_registrations_by_anchor))

    def interface_compatibility(self, left_port_anchor_id: str,
                                right_port_anchor_id: str, *, context):
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
        stale_ids = tuple(sorted({citation_id
            for tip in tips
            for citation_id in self.loaded.port_compatibility_citations[tip.record_id]
            if citation_id not in {
                item.record_id for dimension in (
                    self.loaded.port_interface_declarations[citation_id].declaration.dimension,)
                for item in self.loaded.current_port_interface_tips_by_key.get((
                    self.loaded.port_interface_declarations[citation_id].port_anchor_id,
                    context, dimension), ())}}))
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
            endpoint_registration_status=(left.status, right.status),
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
