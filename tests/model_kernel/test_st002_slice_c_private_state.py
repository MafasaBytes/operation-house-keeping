"""ST-002 Slice C red-first private-state laundering attacks."""

import pytest
from pydantic import ValidationError

import backend.model_kernel as kernel
from tests.model_kernel.builders import ENT_A
from tests.model_kernel.st002_slice_a_helpers import (
    AS_OPERATED,
    TRANSITION_A,
    transition_declaration,
    transition_registration,
    transition_withdrawal,
    world,
)
from tests.model_kernel.test_transition_query_revalidation import complex_result


class FalseyPrivate(dict):
    """Hostile mapping whose truth value conceals carried private state."""

    def __bool__(self):
        return False


def inject_private(value, private_type=dict, **private):
    object.__setattr__(
        value, "__pydantic_private__", private_type(private))
    return value


@pytest.mark.parametrize("record_name,field,private", (
    ("registration", "anchor", {"_mechanism": "forged"}),
    ("registration", "authority", {"_winner_cache": True}),
    ("registration", "evidence", {"_assessment": "forged"}),
    ("declaration", "context", {"_cutoff": "forged"}),
    ("declaration", "from_endpoint", {"_occurred": True}),
    ("declaration", "to_endpoint", {"_occurred": True}),
    ("declaration", "authority", {"_winner_cache": True}),
    ("declaration", "evidence", {"_assessment": "forged"}),
    ("withdrawal", "authority", {"_winner_cache": True}),
))
@pytest.mark.parametrize("private_type", (dict, FalseyPrivate))
def test_every_nested_private_slot_rejects_at_constructor_and_builder(
        record_name, field, private, private_type):
    registration = transition_registration()
    declaration = transition_declaration(registration)
    records = {
        "registration": registration,
        "declaration": declaration,
        "withdrawal": transition_withdrawal(declaration),
    }
    record = records[record_name]
    payload = record.model_dump(
        mode="python", exclude={"record_id"})
    if field == "evidence":
        hostile = inject_private(record.evidence[0], private_type, **private)
        payload[field] = (hostile, *record.evidence[1:])
    else:
        payload[field] = inject_private(
            getattr(record, field), private_type, **private)

    with pytest.raises(ValidationError):
        type(record)(record_id=record.record_id, **payload)
    with pytest.raises(kernel.ModelIntegrityError) as error:
        kernel.build_record(type(record), **payload)
    assert error.value.error_code == "MODEL_RECORD_INVALID"


def tree_snapshot(store):
    root = store.records_dir.parent
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*")) if path.is_file()
    }


@pytest.mark.parametrize("record_name", (
    "registration", "declaration", "withdrawal"))
@pytest.mark.parametrize("private_type", (dict, FalseyPrivate))
def test_top_level_private_state_rejects_at_store_without_any_byte_change(
        tmp_path, private_type, record_name):
    store, registration, from_registration, to_registration, \
        from_declaration, to_declaration = world(tmp_path)
    declaration = transition_declaration(
        registration, from_registration=from_registration,
        to_registration=to_registration, from_declaration=from_declaration,
        to_declaration=to_declaration)
    withdrawal = transition_withdrawal(declaration)
    if record_name == "withdrawal":
        store.append(declaration)
    record = {
        "registration": registration,
        "declaration": declaration,
        "withdrawal": withdrawal,
    }[record_name]
    hostile = inject_private(record, private_type, _winner_cache=True)
    before = tree_snapshot(store)
    revision = store.load().revision
    with pytest.raises(kernel.ModelIntegrityError) as error:
        store.append(hostile)
    assert error.value.error_code == "MODEL_RECORD_INVALID"
    assert tree_snapshot(store) == before
    assert store.load().revision == revision


@pytest.mark.parametrize("private_type", (dict, FalseyPrivate))
def test_private_context_rejects_before_both_context_queries_access_material(
        tmp_path, private_type):
    store, *_ = world(tmp_path)
    context = inject_private(
        AS_OPERATED.model_copy(), private_type, _cutoff="forged")
    loaded = store.load()

    class ExplodingRecords(dict):
        def __iter__(self):
            raise AssertionError("material accessed before context rejection")

        def __getitem__(self, key):
            raise AssertionError("material accessed before context rejection")

        def values(self):
            raise AssertionError("material accessed before context rejection")

    object.__setattr__(loaded, "records", ExplodingRecords())
    queries = kernel.ModelQueries(loaded)
    for call in (
        lambda: queries.transition_declaration(
            TRANSITION_A, context=context),
        lambda: queries.transitions_of_entity(ENT_A, context=context),
    ):
        with pytest.raises(kernel.ModelQueryError) as error:
            call()
        assert error.value.error_code == "MODEL_CONTEXT_INVALID"


def test_falsey_private_mapping_rejects_in_outer_nested_and_material_results(
        tmp_path):
    result, _, _, _, _ = complex_result(tmp_path)
    outer = type(result).model_validate(result.model_dump(mode="python"))
    inject_private(outer, FalseyPrivate, _occurred=True)

    nested = type(result).model_validate(result.model_dump(mode="python"))
    endpoint = nested.effective_body_groups[0].from_endpoint
    object.__setattr__(endpoint, "__pydantic_private__", FalseyPrivate({
        **endpoint.__pydantic_private__, "_winner": "forged"}))

    material = type(result).model_validate(result.model_dump(mode="python"))
    inject_private(material.material, FalseyPrivate, _assessment="forged")

    for hostile in (outer, nested, material):
        with pytest.raises(ValidationError, match="private"):
            type(hostile).model_validate(hostile)
