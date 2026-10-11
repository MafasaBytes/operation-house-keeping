"""Independent analytical comparands; synthetic test premises, no authorities.

These checks make no workflow or physical truth claim. Literal expected values
were derived by rational arithmetic independently of the production generator.
"""
import copy
from fractions import Fraction

import pytest

from applications.bounded_decision_workflow.checked_derivation import region_hits
from applications.bounded_decision_workflow.t1_carrier import fixed
from applications.bounded_decision_workflow.t1_contracts import SCHEMAS, SimRefusal
from applications.bounded_decision_workflow.t1_oracle import check_receipt, receipt_values
from applications.bounded_decision_workflow.t1_schemas import Found, _check
from .fixtures import diagnostic_inputs


def test_exact_positive_bias_and_negative_error_do_not_cancel_by_sign_error():
    j, e, get = diagnostic_inputs(theta='60', beta='1.25', epsilon='-0.125')
    actual = receipt_values(j, e, get)
    assert actual['r'] == '61.125'
    assert actual['diagnostics']['reference_calibration']['beta_in_b_ref'] is False
    assert actual['diagnostics']['observation_error_bound']['abs_epsilon_le_w'] is True


def test_half_width_endpoint_is_inclusive_on_both_sides():
    for epsilon in ('-0.5', '0.5'):
        j, e, get = diagnostic_inputs(epsilon=epsilon)
        actual = receipt_values(j, e, get)
        assert actual['diagnostics']['observation_error_bound']['abs_epsilon_le_w'] is True
    j, e, get = diagnostic_inputs(epsilon='0.5001')
    actual = receipt_values(j, e, get)
    assert actual['diagnostics']['observation_error_bound']['abs_epsilon_le_w'] is False


def test_hypothesis_interval_endpoints_use_baseline_minus_suspect_bias():
    for theta in ('45.1', '55.1'):
        j, e, get = diagnostic_inputs(theta=theta)
        row = receipt_values(j, e, get)['diagnostics']['state_hold']['per_hypothesis'][1]
        assert row['interval'] == {'lo': {'numerator': '451', 'denominator': '10'},
                                   'hi': {'numerator': '551', 'denominator': '10'}}
        assert row['theta_in_interval'] is True
    j, e, get = diagnostic_inputs(theta='55.1001')
    row = receipt_values(j, e, get)['diagnostics']['state_hold']['per_hypothesis'][1]
    assert row['theta_in_interval'] is False


def test_decoder_boundary_singletons_have_exact_asymmetric_ownership():
    assert [name for name, _cut in region_hits(Fraction(56), Fraction(56))] == ['low']
    assert [name for name, _cut in region_hits(Fraction(59), Fraction(59))] == ['gap']
    assert [name for name, _cut in region_hits(Fraction(590001, 10000), Fraction(590001, 10000))] == ['high']
    assert [name for name, _cut in region_hits(Fraction(56), Fraction(59))] == ['low', 'gap']


def test_fixed_decimal_sign_zero_and_denominator_are_exact():
    assert fixed(Fraction(-1, 8)) == '-0.125'
    assert fixed(Fraction(0, 1000000)) == '0'
    assert fixed(Fraction(1, 1000000)) == '0.000001'
    with pytest.raises(ValueError):
        fixed(Fraction(1, 3))


def test_receipt_r_diagnostic_first_difference_is_not_self_authority():
    j, e, get = diagnostic_inputs(theta='60', beta='1.25', epsilon='-0.125')
    receipt = copy.deepcopy(receipt_values(j, e, get))
    receipt['r'] = '58.625'  # reversed instrument-bias convention
    receipt['diagnostics']['state_hold']['delta'] = '1'
    with pytest.raises(SimRefusal) as error:
        check_receipt(receipt, j, e, get, {})
    assert (error.value.code, error.value.target) == ('SIM_DERIVATION_MISMATCH', '/receipt/r')


def test_diagnostic_interval_mismatch_targets_the_atomic_interval():
    j, e, get = diagnostic_inputs()
    receipt = copy.deepcopy(receipt_values(j, e, get))
    receipt['diagnostics']['state_hold']['per_hypothesis'][1]['interval']['lo']['numerator'] = '452'
    with pytest.raises(SimRefusal) as error:
        check_receipt(receipt, j, e, get, {})
    assert error.value.target == '/receipt/diagnostics/state_hold/per_hypothesis/1/interval'


def test_companion_rational_schema_refuses_nonreduced_value():
    # Direct semantic admission witness, not a claim of a complete package twin.
    with pytest.raises(SimRefusal) as error:
        _check({'numerator': '1202', 'denominator': '20'}, SCHEMAS['definitions']['rational'],
               '/receipt/diagnostics/state_hold/model_baseline', Found())
    assert (error.value.code, error.value.order, error.value.target) == (
        'SIM_SCHEMA_INVALID', '0', '/receipt/diagnostics/state_hold/model_baseline')


def test_companion_rational_schema_refuses_noncanonical_zero():
    with pytest.raises(SimRefusal) as error:
        _check({'numerator': '0', 'denominator': '2'}, SCHEMAS['definitions']['rational'],
               '/receipt/diagnostics/reference_calibration/b_ref/lo', Found())
    assert error.value.code == 'SIM_SCHEMA_INVALID'


def test_companion_rational_schema_refuses_nondecimal_denominator():
    with pytest.raises(SimRefusal) as error:
        _check({'numerator': '1', 'denominator': '3'}, SCHEMAS['definitions']['rational'],
               '/receipt/diagnostics/state_hold/model_baseline', Found())
    assert error.value.code == 'SIM_SCHEMA_INVALID'
