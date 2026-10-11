import copy
import pytest
from applications.bounded_decision_workflow.t1_contracts import SimRefusal
from applications.bounded_decision_workflow.t1_oracle import receipt_values, check_receipt
from .fixtures import diagnostic_inputs


def test_p1_uses_captured_baseline_not_latent_baseline():
    j, e, get = diagnostic_inputs()
    v = receipt_values(j, e, get)
    assert v['r'] == '60'
    state = v['diagnostics']['state_hold']
    assert state['model_baseline'] == {'numerator': '601', 'denominator': '10'}
    assert state['theta_equals_baseline_theta'] is True
    assert [h['theta_in_interval'] for h in state['per_hypothesis']] == [False, False]


def test_wrong_mapping_keeps_actual_hold_but_nulls_intended_hold():
    j, e, get = diagnostic_inputs(wrong_mapping=True)
    state = receipt_values(j, e, get)['diagnostics']['state_hold']
    assert state['theta_equals_baseline_theta'] is True
    assert state['intended_variable_hold'] == {'basis': 'not_declared_for_intended_variable',
                                             'theta_equals_baseline_theta': None, 'delta': None}
    assert [h['theta_in_interval'] for h in state['per_hypothesis']] == [None, None]


def test_w6_positive_exact_hold_delta():
    j, e, get = diagnostic_inputs(theta='60.0001')
    v = receipt_values(j, e, get)
    assert v['r'] == '60.0001' and v['d'] == 4
    assert v['diagnostics']['state_hold']['delta'] == '0.0001'


def test_altered_model_baseline_compared_with_pinned_model_at_atomic_target():
    j, e, get = diagnostic_inputs()
    receipt = copy.deepcopy(receipt_values(j, e, get))
    receipt['diagnostics']['state_hold']['model_baseline'] = {'numerator': '301', 'denominator': '5'}
    with pytest.raises(SimRefusal) as exc:
        check_receipt(receipt, j, e, get, {})
    assert exc.value.target == '/receipt/diagnostics/state_hold/model_baseline'
