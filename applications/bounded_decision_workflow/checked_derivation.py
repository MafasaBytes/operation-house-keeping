"""Checked derivation: exact ideal predicted sets, decoder cells, baseline checks.

`b_ref` enters the ideal T1 predicted set once; the observation-error bound `w`
never enters here (CONTRACT §3). Missing numbers give derivation unavailable,
never guesses; baseline-ineligible hypotheses are retained, not pruned.
"""
from fractions import Fraction
from .checked_contracts import (CALCULATOR, PROFILE, T1, T1_REGIONS, T2, T2_CODES,
                                as_rational, frac, interval)


def _intersect(lo, hi, region, ops=None):
    """Closed [lo, hi] with an open/closed decoder region; None if empty (4 operations)."""
    if ops is not None:
        ops.add(4)
    _, rlo, rlo_closed, rhi, rhi_closed = region
    a, a_closed = lo, True
    if rlo is not None and (rlo > a or (rlo == a and not rlo_closed)):
        a, a_closed = rlo, rlo_closed
    b, b_closed = hi, True
    if rhi is not None and (rhi < b or (rhi == b and not rhi_closed)):
        b, b_closed = rhi, rhi_closed
    if a > b or (a == b and not (a_closed and b_closed)):
        return None
    return {'lo': as_rational(a), 'lo_closed': a_closed, 'hi': as_rational(b), 'hi_closed': b_closed}


def region_hits(lo, hi, ops=None):
    """Decoder T1 regions reached by closed [lo, hi], with their intersections."""
    out = []
    for region in T1_REGIONS:
        cut = _intersect(lo, hi, region, ops)
        if cut is not None:
            out.append((region[0], cut))
    return out


def baseline_checks(model, observed_scalar, observed_verdict):
    """Rational equality of admitted baseline and model baseline, plus verdict.

    `observed_*` is None when the public evidence could not supply a value
    (unknown); a value that differs is false.
    """
    expected = frac(model['baseline'], '/model/baseline')

    def check(exp, obs, exp_wire, obs_wire):
        result = 'unknown' if obs is None else ('true' if obs == exp else 'false')
        return {'expected': exp_wire, 'observed': obs_wire, 'result': result}
    value = check(expected, observed_scalar, model['baseline'],
                  None if observed_scalar is None else as_rational(observed_scalar))
    verdict = check(model['baseline_verdict'], observed_verdict, model['baseline_verdict'], observed_verdict)
    results = {value['result'], verdict['result']}
    eligibility = ('baseline_ineligible' if 'false' in results else
                   'baseline_unknown' if 'unknown' in results else 'baseline_eligible')
    return value, verdict, eligibility


def derive(*, request_ref, model_ref, build_ref, model, observed_scalar, observed_verdict, ops=None):
    """Return the ct.derivation.v1 record for the model's nominated procedures."""
    baseline = frac(model['baseline'], '/model/baseline')
    b_ref_lo, b_ref_hi = interval(model['b_ref'], '/model/b_ref')
    value, verdict, eligibility = baseline_checks(model, observed_scalar, observed_verdict)
    rows, predictions, cells = [], [], []
    for h in model['hypotheses']:
        hyp = h['explanation']
        rows.append({'hypothesis': hyp, 'value_check': value, 'verdict_check': verdict,
                     'eligibility': eligibility})
        s_lo, s_hi = interval(h['b_suspect'], '/model/hypotheses/b_suspect')
        for p in model['procedures']:
            edition = p['edition']
            outcomes = ('low', 'gap', 'high') if edition == T1 else T2_CODES
            if eligibility != 'baseline_eligible':
                predictions.append({'hypothesis': hyp, 'procedure_edition': edition,
                                    'status': 'derivation_unavailable', 'interval': None, 'code': None,
                                    'unavailable_reason': 'baseline_not_eligible'})
                cells.extend({'hypothesis': hyp, 'procedure_edition': edition, 'outcome': o,
                              'relation': 'not_assessed_baseline', 'intersection': None,
                              'exclusion_basis': None} for o in outcomes)
                continue
            if edition == T1:
                lo = baseline - s_hi + b_ref_lo
                hi = baseline - s_lo + b_ref_hi
                if ops is not None:
                    ops.add(4)
                predictions.append({'hypothesis': hyp, 'procedure_edition': edition, 'status': 'derived',
                                    'interval': {'lo': as_rational(lo), 'hi': as_rational(hi)},
                                    'code': None, 'unavailable_reason': None})
                for region in T1_REGIONS:
                    cut = _intersect(lo, hi, region, ops)
                    cells.append({'hypothesis': hyp, 'procedure_edition': edition, 'outcome': region[0],
                                  'relation': 'permit' if cut else 'exclude', 'intersection': cut,
                                  'exclusion_basis': None if cut else 'empty_intersection_complete_ideal_set'})
            else:
                target = frac(p['target'], '/model/procedures/target')
                # T2: heater_on iff the held suspect baseline < target; equality is off.
                code = 'heater_on' if baseline < target else 'heater_off'
                if ops is not None:
                    ops.add(1)
                predictions.append({'hypothesis': hyp, 'procedure_edition': edition, 'status': 'derived',
                                    'interval': None, 'code': code, 'unavailable_reason': None})
                cells.extend({'hypothesis': hyp, 'procedure_edition': edition, 'outcome': o,
                              'relation': 'permit' if o == code else 'exclude', 'intersection': None,
                              'exclusion_basis': None if o == code else 'code_differs'} for o in T2_CODES)
    return {'schema': 'ct.derivation.v1', 'profile': PROFILE, 'request': request_ref, 'model': model_ref,
            'build': build_ref, 'calculator_edition': CALCULATOR, 'baseline': rows,
            'predictions': predictions, 'cells': cells}


def cell_map(derivation):
    return {(c['hypothesis']['sha256'], c['procedure_edition'], c['outcome']): c for c in derivation['cells']}


def ideal_interval(prediction):
    i = prediction['interval']
    return Fraction(int(i['lo']['numerator']), int(i['lo']['denominator'])), \
        Fraction(int(i['hi']['numerator']), int(i['hi']['denominator']))
