"""Independent declared-world counterexamples, not operational authorities.

These analytical inputs exercise the receipt oracle only. They do not establish
an admitted context, actual applicability or a completed acquisition route.
"""
import pytest

from applications.bounded_decision_workflow.t1_contracts import canonical_bytes, ref
from applications.bounded_decision_workflow.t1_oracle import receipt_values
from .fixtures import diagnostic_inputs


@pytest.mark.parametrize('wrong_subject,wrong_variable', [(True, False), (False, True), (True, True)])
def test_either_mapping_difference_withholds_intended_hold(wrong_subject, wrong_variable):
    target, authority, get = diagnostic_inputs(theta='70', baseline_theta='60')
    world = get(target['world'])
    if wrong_subject:
        world['actual_measurand']['subject_entity_anchor_id'] = 'ent_' + '8' * 32
    if wrong_variable:
        world['actual_measurand']['variable_anchor_id'] = 'var_' + '2' * 32
    updated_world = ref('ct.t1-world.v1', canonical_bytes(world))
    target['world'] = updated_world
    values = receipt_values(target, authority,
                            lambda rr: world if rr == updated_world else get(rr))
    assert values['diagnostics']['reference_mapping'] == {
        'subject_mapping_matches': not wrong_subject,
        'variable_mapping_matches': not wrong_variable}
    state = values['diagnostics']['state_hold']
    assert state['theta_equals_baseline_theta'] is False and state['delta'] == '10'
    assert state['intended_variable_hold'] == {
        'basis': 'not_declared_for_intended_variable',
        'theta_equals_baseline_theta': None, 'delta': None}
    assert all(row['same_referent'] is False and row['theta_in_interval'] is None
               for row in state['per_hypothesis'])


@pytest.mark.parametrize('operands,diagnostic', [
    ({'beta': '1'}, 'reference_calibration'),
    ({'epsilon': '1'}, 'observation_error_bound'),
    ({'theta': '61'}, 'state_hold'),
])
def test_false_declared_applicability_is_diagnostic_not_an_oracle_refusal(operands, diagnostic):
    target, authority, get = diagnostic_inputs(**operands)
    values = receipt_values(target, authority, get)
    key = {'reference_calibration': 'beta_in_b_ref',
           'observation_error_bound': 'abs_epsilon_le_w',
           'state_hold': 'theta_equals_baseline_theta'}[diagnostic]
    assert values['diagnostics'][diagnostic][key] is False
    assert values['r'] == '61'


def test_same_reading_cannot_identify_bias_hold_or_latent_temperature():
    held = diagnostic_inputs(theta='60', baseline_theta='60', beta='0')
    moved = diagnostic_inputs(theta='59', baseline_theta='60', beta='1')
    left, right = [receipt_values(*args) for args in (held, moved)]
    assert left['r'] == right['r'] == '60'
    assert left['diagnostics']['state_hold']['theta_equals_baseline_theta'] is True
    assert right['diagnostics']['state_hold']['theta_equals_baseline_theta'] is False
    assert left['diagnostics']['reference_calibration']['beta_in_b_ref'] is True
    assert right['diagnostics']['reference_calibration']['beta_in_b_ref'] is False
    # Equal sensor scalars do not imply equal full packages: their world pins differ.
    assert held[0]['world']['sha256'] != moved[0]['world']['sha256']


def test_actual_hold_does_not_identify_model_baseline_or_hypothesis_truth():
    target, authority, get = diagnostic_inputs(theta='60', baseline_theta='60')
    state = receipt_values(target, authority, get)['diagnostics']['state_hold']
    assert state['theta_equals_baseline_theta'] is True and state['delta'] == '0'
    assert state['model_baseline'] == {'numerator': '601', 'denominator': '10'}
    assert [row['theta_in_interval'] for row in state['per_hypothesis']] == [False, False]
    assert state['intended_variable_hold']['basis'] == 'same_declared_measurand'
