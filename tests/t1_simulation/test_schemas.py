import pytest
from applications.bounded_decision_workflow.t1_contracts import SimRefusal, canonical_bytes
from applications.bounded_decision_workflow.t1_records import parse
from applications.bounded_decision_workflow.t1_schemas import validate
from .fixtures import world_record


def test_positive_world_closed_schema():
    validate(world_record(), 'ct.t1-world.v1', '/W')


def test_decimal_newline_is_refused():
    w = world_record()
    w['theta'] = '60\n'
    with pytest.raises(SimRefusal) as exc:
        validate(w, w['schema'], '/W')
    assert exc.value.target == '/W/theta'


def test_extra_alias_cannot_replace_anchor():
    w = world_record()
    w['intended_variable'] = w['intended_variable_anchor_id']
    with pytest.raises(SimRefusal) as exc:
        validate(w, w['schema'], '/W')
    assert exc.value.code == 'SIM_SCHEMA_INVALID'


def test_false_applicability_premises_do_not_invalidate_world_shape():
    w = world_record()
    w.update(beta='10', epsilon='5', theta='50', baseline_theta='60')
    w['actual_measurand']['variable_anchor_id'] = 'var_' + '2' * 32
    parse(canonical_bytes(w), w['schema'], '/W')


def test_duplicate_keys_refused_before_canonical_comparison():
    with pytest.raises(SimRefusal) as exc:
        parse(b'{"schema":"ct.t1-world.v1","schema":"ct.t1-world.v1"}', 'ct.t1-world.v1', '/W')
    assert (exc.value.order, exc.value.target) == ('0', '/W')
