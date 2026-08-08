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

from backend.model_kernel.contracts import (
    AssertionContext,
    ChildEntry,
    ChildrenResult,
    CycleReport,
    EntityResult,
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
)
from backend.model_kernel.hierarchy import HierarchyProjection, build_projection
from backend.model_kernel.store import LoadedModel
from backend.system_identity import ENTITY_ANCHOR_ID_PATTERN

_ANCHOR_ID = re.compile(ENTITY_ANCHOR_ID_PATTERN)


class ModelQueries:
    def __init__(self, loaded: LoadedModel) -> None:
        self.loaded = loaded

    # -- boundary checks ---------------------------------------------------

    def _require_anchor_id(self, anchor_id: str) -> str:
        if not isinstance(anchor_id, str) or not _ANCHOR_ID.fullmatch(anchor_id):
            raise ModelQueryError(
                "MODEL_ANCHOR_ID_INVALID",
                f"{anchor_id!r} is not a canonical entity anchor id")
        return anchor_id

    def _require_type(self, type_name: str):
        current_id = self.loaded.current_type_by_name.get(type_name)
        if current_id is None:
            raise ModelQueryError(
                "MODEL_UNKNOWN_TYPE",
                f"no relationship type named {type_name!r} in this revision")
        return self.loaded.types[current_id]

    def _require_hierarchy_type(self, type_name: str, view):
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

    # -- relationships (strict context equality) ---------------------------

    def relationships(self, anchor_id: str, *, direction: str,
                      type_name: str | None = None,
                      context: AssertionContext) -> RelationshipsResult:
        anchor_id = self._require_anchor_id(anchor_id)
        if direction not in ("incoming", "outgoing", "both"):
            raise ModelQueryError("MODEL_DIRECTION_INVALID",
                                  f"{direction!r} is not a query direction")
        if type_name is not None:
            definition = self._require_type(type_name)
            if definition.context_requirement != context.kind:
                raise ModelQueryError(
                    "MODEL_CONTEXT_MISMATCH",
                    f"type {type_name!r} requires "
                    f"{definition.context_requirement} context; a "
                    f"{context.kind} query cannot match it")

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
            anchor_id=anchor_id, direction=direction, type_name=type_name,
            context=context, active=active, inactive=inactive,
            lineage_conflicts=conflicts, revision=self.loaded.revision)

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
