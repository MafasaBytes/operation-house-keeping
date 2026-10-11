"""Independent receipt oracle; comparands originate in the pinned J closure.

Deliberately does not import the generation arithmetic or diagnostic producer.
The owning backend reconstruction is a disclosed common dependency.
"""
from fractions import Fraction
from .t1_contracts import canonical_bytes, refuse, sha


def _q(value):
    return Fraction(int(value['numerator']), int(value['denominator']))


def _rat(value):
    return {'numerator': str(value.numerator), 'denominator': str(value.denominator)}


def _decimal(value):
    power = 0
    while 10 ** power % value.denominator:
        power += 1
        if power > 32:
            raise ValueError('non-finite decimal')
    integer = value.numerator * (10 ** power // value.denominator)
    digits = str(abs(integer)).rjust(power + 1, '0')
    result = digits if not power else (digits[:-power] + '.' + digits[-power:]).rstrip('0').rstrip('.')
    return ('-' if integer < 0 else '') + result


def receipt_values(target, execution_authority, get):
    """`get` resolves typed references with full identity checks before this call."""
    world, context = get(target['world']), get(target['context'])
    policy = get(target['captured_policy'])
    execution = get(execution_authority['target'])
    model, plan = get(execution['model']), get(execution['interpretation_plan'])
    theta, beta, epsilon, baseline_theta = (Fraction(world[k]) for k in
                                           ('theta', 'beta', 'epsilon', 'baseline_theta'))
    baseline = _q(model['baseline'])
    width = _q(plan['half_width'])
    lo, hi = (_q(model['b_ref'][k]) for k in ('lo', 'hi'))
    subject = world['actual_measurand']['subject_entity_anchor_id'] == context['intended_subject_entity_anchor_id']
    variable = world['actual_measurand']['variable_anchor_id'] == context['intended_variable_anchor_id']
    same = subject and variable
    rows = []
    for hypothesis in model['hypotheses']:
        lower = baseline - _q(hypothesis['b_suspect']['hi'])
        upper = baseline - _q(hypothesis['b_suspect']['lo'])
        rows.append({'explanation': hypothesis['explanation'], 'interval': {'lo': _rat(lower), 'hi': _rat(upper)},
                     'same_referent': same, 'theta_in_interval': lower <= theta <= upper if same else None})
    hold = theta == baseline_theta
    delta = _decimal(theta - baseline_theta)
    return {'operands': {k: world[k] for k in ('theta', 'beta', 'epsilon', 'baseline_theta')},
            'r': _decimal(theta + beta + epsilon), 'd': min(6, policy['limits']['fractional_digits']),
            'diagnostics': {
                'reference_calibration': {'b_ref': model['b_ref'], 'beta_in_b_ref': lo <= beta <= hi},
                'observation_error_bound': {'w': plan['half_width'], 'abs_epsilon_le_w': abs(epsilon) <= width},
                'reference_mapping': {'subject_mapping_matches': subject, 'variable_mapping_matches': variable},
                'state_hold': {'model_baseline': model['baseline'], 'theta_equals_baseline_theta': hold,
                               'delta': delta, 'per_hypothesis': rows,
                               'intended_variable_hold': {
                                   'basis': 'same_declared_measurand' if same else 'not_declared_for_intended_variable',
                                   'theta_equals_baseline_theta': hold if same else None,
                                   'delta': delta if same else None}}},
            'intended': {'subject': context['intended_subject_entity_anchor_id'],
                         'variable': context['intended_variable_anchor_id'], 'unit': world['unit']},
            'actual_measurand': world['actual_measurand'], 'reading_locator': context['reading_locator']}


def _first_difference(actual, expected, path):
    if type(actual) is not type(expected):
        return path
    if isinstance(expected, dict):
        if actual.keys() != expected.keys():
            return path
        if set(expected) == {'numerator', 'denominator'}:
            try:
                return None if _q(actual) == _q(expected) else path
            except (ValueError, TypeError, ZeroDivisionError):
                return path
        if set(expected) == {'lo', 'hi'}:
            try:
                return None if all(_q(actual[k]) == _q(expected[k]) for k in ('lo', 'hi')) else path
            except (ValueError, TypeError, ZeroDivisionError):
                return path
        for key in sorted(expected):
            found = _first_difference(actual[key], expected[key], path + '/' + key)
            if found:
                return found
    elif isinstance(expected, list):
        if len(actual) != len(expected):
            return path
        for i, item in enumerate(expected):
            found = _first_difference(actual[i], item, path + '/' + str(i))
            if found:
                return found
    elif actual != expected:
        return path
    return None


def check_receipt(receipt, target, execution_authority, get, retained_values):
    expected = receipt_values(target, execution_authority, get)
    for key in ('operands', 'r', 'd', 'diagnostics', 'intended', 'actual_measurand', 'reading_locator'):
        # Operands use contract order rather than sorted JSON order.
        if key == 'operands':
            for operand in ('theta', 'beta', 'epsilon', 'baseline_theta'):
                if receipt[key][operand] != expected[key][operand]:
                    refuse('SIM_DERIVATION_MISMATCH', 7, '/receipt/operands/' + operand)
        else:
            difference = _first_difference(receipt[key], expected[key], '/receipt/' + key)
            if difference:
                refuse('SIM_DERIVATION_MISMATCH', 7, difference)
    for key in ('raw_response_digests', 'transcripts', 'evidence'):
        difference = _first_difference(receipt[key], retained_values[key], '/receipt/' + key)
        if difference:
            refuse('SIM_DERIVATION_MISMATCH', 7, difference)


def check_wrapper(evidence, baseline, target, target_digest):
    required = [('id', 'E-t1-' + target_digest[:59]), ('question/as_of', target['window']['to']),
                ('binding', baseline['binding']), ('token_roles', baseline['token_roles']),
                ('snapshot/as_of', target['window']['to'])]
    for pointer, expected in required:
        value = evidence
        for key in pointer.split('/'):
            value = value[key]
        if value != expected:
            refuse('SIM_DERIVATION_MISMATCH', 7, '/O/' + pointer)


def evidence_identity_check(records, *, order=1, receipt_digest=None):
    """No global registry; equal short ID/different full identity never merge."""
    seen = {}
    for target, wire in records:
        import json
        value = json.loads(wire)
        if value.get('schema') != 'nm.evidence.v1':
            continue
        digest = sha(wire)
        if value['id'] in seen and seen[value['id']][0] != digest:
            earlier_digest, _earlier_target = seen[value['id']]
            joined = receipt_digest in (digest, earlier_digest)
            refuse('SIM_REFERENCE_INVALID', order, '/O/id' if joined or target == '/O' else target)
        seen[value['id']] = (digest, target)
