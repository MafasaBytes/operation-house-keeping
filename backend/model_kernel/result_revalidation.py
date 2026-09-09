"""Shared bounded reconstruction primitives for carry-once query results."""

from collections.abc import Mapping

from pydantic import BaseModel, TypeAdapter

from backend.model_kernel.contracts import AssertionContext
from backend.model_kernel.port_results import ModelQueryMaterial


_MAX_RESULT_GRAPH_DEPTH = 128
_MAX_RESULT_GRAPH_NODES = 100_000
_CONTEXT_ADAPTER = TypeAdapter(AssertionContext)


def inspect_supplied_graph(value) -> None:
    """Reject hidden state, cycles, excessive depth, and coercive counts."""

    def field(container, name, missing):
        if isinstance(container, BaseModel):
            stored = vars(container)
            if type(stored) is not dict:
                raise ValueError(
                    "pydantic result storage must be an exact dictionary")
            return dict.get(stored, name, missing)
        if type(container) is dict:
            return dict.get(container, name, missing)
        if isinstance(container, Mapping):
            raise ValueError("result mappings must be exact dictionaries")
        return missing

    def children(item, outer_material):
        if isinstance(item, BaseModel):
            fields = type(item).model_fields
            stored = vars(item)
            if type(stored) is not dict:
                raise ValueError(
                    "pydantic result storage must be an exact dictionary")
            extras = getattr(item, "__pydantic_extra__", None)
            if set(dict.keys(stored)).difference(fields):
                raise ValueError(
                    "pydantic result instance contains extra fields")
            if (extras is not None
                    and (type(extras) is not dict or len(extras) != 0)):
                raise ValueError(
                    "pydantic result instance contains extra fields")
            private = getattr(item, "__pydantic_private__", None)
            if private is None:
                private = {}
            elif type(private) is not dict:
                raise ValueError(
                    "pydantic result instance contains private cache")
            permitted_private = (
                {"_material"}
                if "_material" in getattr(
                    type(item), "__private_attributes__", {})
                else set())
            if set(private).difference(permitted_private):
                raise ValueError(
                    "pydantic result instance contains private cache")
            if "_material" in private:
                bound_material = private["_material"]
                if (not isinstance(outer_material, ModelQueryMaterial)
                        or bound_material is not outer_material):
                    raise ValueError(
                        "nested result is bound to another material snapshot")
            return tuple(dict.__getitem__(stored, name)
                         for name in fields if name in stored)
        if type(item) is dict:
            return tuple(dict.keys(item)) + tuple(dict.values(item))
        if isinstance(item, Mapping):
            raise ValueError("result mappings must be exact dictionaries")
        if isinstance(item, (tuple, list, set, frozenset)):
            return tuple(item)
        return None

    missing = object()
    material = field(value, "material", missing)
    revision = field(material, "revision", missing)
    record_count = field(revision, "record_count", missing)
    if record_count is not missing and type(record_count) is not int:
        raise ValueError("material revision record_count must be strict int")

    stack = [(False, value, 0)]
    active: set[int] = set()
    complete: set[int] = set()
    visited = 0
    while stack:
        exiting, item, depth = stack.pop()
        if not (isinstance(item, (BaseModel, Mapping))
                or isinstance(item, (tuple, list, set, frozenset))):
            continue
        identity = id(item)
        if exiting:
            active.remove(identity)
            complete.add(identity)
            continue
        if identity in active:
            raise ValueError("result object graph contains a cycle")
        if identity in complete:
            continue
        if depth > _MAX_RESULT_GRAPH_DEPTH:
            raise ValueError("result object graph exceeds maximum depth")
        visited += 1
        if visited > _MAX_RESULT_GRAPH_NODES:
            raise ValueError("result object graph exceeds maximum size")
        nested = children(item, material)
        if nested is None:  # pragma: no cover - guarded above
            continue
        active.add(identity)
        stack.append((True, item, depth))
        stack.extend((False, child, depth + 1)
                     for child in reversed(nested))


def _dump_nested(value):
    return (value.model_dump(mode="python")
            if isinstance(value, BaseModel) else value)


def rebuild_material(value) -> ModelQueryMaterial:
    return ModelQueryMaterial.model_validate(_dump_nested(value))


def rebuild_context(value) -> AssertionContext:
    return _CONTEXT_ADAPTER.validate_python(_dump_nested(value))


def rebuild_rows(value, contract, label: str):
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{label} must be a tuple of result rows")
    return tuple(contract.model_validate(_dump_nested(row)) for row in value)


def rebuild_row(value, contract):
    return contract.model_validate(_dump_nested(value))


def material_indices(material: ModelQueryMaterial) -> dict[str, int]:
    return {record_id: index for index, record_id
            in enumerate(material.revision.record_ids)}
