"""Hierarchy projection for one (containment type lineage × lifecycle view)
within one revision.

Pure graph mechanics over assertion IDs: active edges parent→child,
same-edge corroboration preserved, distinct-parent/same-child conflicts and
cycle membership computed deterministically at build (iterative strongly-
connected components — never lazily mid-traversal, never by loop counters).
Result objects are built by ``queries``; this module carries no summaries.
"""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping

from backend.model_kernel.store import LoadedModel


@dataclass(frozen=True)
class HierarchyProjection:
    type_name: str
    view: str | None
    # (source, target) -> sorted assertion ids (corroboration preserved)
    edges: Mapping[tuple[str, str], tuple[str, ...]]
    children_of: Mapping[str, tuple[str, ...]]   # parent -> sorted children
    parents_of: Mapping[str, tuple[str, ...]]    # child  -> sorted parents
    cycle_members: frozenset[str]
    cycles: tuple[tuple[str, ...], ...]          # sorted members per SCC
    stale_assertion_ids: tuple[str, ...]


def _context_matches(assertion, requirement: str, view: str | None) -> bool:
    if requirement == "lifecycle_view":
        return (assertion.context.kind == "lifecycle_view"
                and assertion.context.view == view)
    return assertion.context.kind == "view_independent"


def _strongly_connected(nodes, children_of) -> list[list[str]]:
    """Iterative Tarjan; deterministic over sorted inputs."""
    index: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    on_stack: set[str] = set()
    stack: list[str] = []
    components: list[list[str]] = []
    counter = 0

    for root in sorted(nodes):
        if root in index:
            continue
        work = [(root, iter(children_of.get(root, ())))]
        index[root] = lowlink[root] = counter
        counter += 1
        stack.append(root)
        on_stack.add(root)
        while work:
            node, children = work[-1]
            advanced = False
            for child in children:
                if child not in index:
                    index[child] = lowlink[child] = counter
                    counter += 1
                    stack.append(child)
                    on_stack.add(child)
                    work.append((child, iter(children_of.get(child, ()))))
                    advanced = True
                    break
                if child in on_stack:
                    lowlink[node] = min(lowlink[node], index[child])
            if advanced:
                continue
            work.pop()
            if work:
                parent = work[-1][0]
                lowlink[parent] = min(lowlink[parent], lowlink[node])
            if lowlink[node] == index[node]:
                component = []
                while True:
                    member = stack.pop()
                    on_stack.discard(member)
                    component.append(member)
                    if member == node:
                        break
                components.append(component)
    return components


def build_projection(loaded: LoadedModel, type_name: str,
                     view: str | None) -> HierarchyProjection:
    lineage_ids = {record_id for record_id, name
                   in loaded.type_name_by_id.items() if name == type_name}
    current_id = loaded.current_type_by_name.get(type_name)
    requirement = loaded.types[current_id].context_requirement

    edges: dict[tuple[str, str], list[str]] = {}
    stale: list[str] = []
    for record_id in sorted(loaded.assertions):
        claim = loaded.assertions[record_id]
        if claim.type_id not in lineage_ids:
            continue
        active = (not loaded.superseded_by[record_id]
                  and not loaded.withdrawn_by[record_id])
        if not active:
            continue
        if not _context_matches(claim, requirement, view):
            continue
        edges.setdefault(
            (claim.source_anchor_id, claim.target_anchor_id), []).append(
            record_id)
        if claim.type_id != current_id:
            stale.append(record_id)

    children_of: dict[str, list[str]] = {}
    parents_of: dict[str, list[str]] = {}
    for source, target in sorted(edges):
        children_of.setdefault(source, [])
        if target not in children_of[source]:
            children_of[source].append(target)
        parents_of.setdefault(target, [])
        if source not in parents_of[target]:
            parents_of[target].append(source)

    nodes = set(children_of) | set(parents_of)
    components = _strongly_connected(nodes, {
        node: tuple(sorted(children)) for node, children
        in children_of.items()})
    cycles = tuple(tuple(sorted(component)) for component in
                   sorted((c for c in components if len(c) > 1),
                          key=lambda c: sorted(c)[0]))
    cycle_members = frozenset(member for cycle in cycles for member in cycle)

    return HierarchyProjection(
        type_name=type_name, view=view,
        edges=MappingProxyType({pair: tuple(sorted(ids))
                                for pair, ids in edges.items()}),
        children_of=MappingProxyType({node: tuple(sorted(children))
                                      for node, children
                                      in children_of.items()}),
        parents_of=MappingProxyType({node: tuple(sorted(parents))
                                     for node, parents
                                     in parents_of.items()}),
        cycle_members=cycle_members, cycles=cycles,
        stale_assertion_ids=tuple(sorted(stale)))
