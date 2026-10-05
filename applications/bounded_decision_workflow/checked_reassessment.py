"""Checked reassessment of one supplied result (design §4, FIXED).

`w` is applied once to the admitted scalar ([r - w, r + w]); `b_ref` is not
applied here. A hypothesis is compatible only if every reached branch permits
it. Ranking is never reassessed and nothing is adopted.
"""
from .checked_contracts import PROFILE, T1, as_rational, frac
from .checked_derivation import region_hits

PRESENTATION = ('Supplied hypotheses are assessed for compatibility under this model, these conditions and this '
                'observation interpretation; actual cause is not established.')


def reassess(*, request_ref, request, derivation_ref, applicability_ref, build_ref, model, derivation,
             applicability, plan, scalar, prior_selection_ref, former_plan, executed_plan, ops=None):
    result = request['result']
    edition = result['procedure_edition']
    obs = result['observation']
    blocked = applicability['use_disposition'] == 'blocked'
    if edition == T1:
        w = frac(plan['half_width'], '/plan/half_width')
        lo, hi = scalar - w, scalar + w
        if ops is not None:
            ops.add(2)
        hits = region_hits(lo, hi, ops)
        interval = {'lo': as_rational(lo), 'hi': as_rational(hi)}
        contained = lo <= scalar <= hi
        branches = [{'outcome': o, 'intersection': cut} for o, cut in hits]
        observation = {'procedure_edition': edition, 'kind': 'scalar', 'scalar': obs['scalar'], 'code': None,
                       'unit': 'degree_celsius', 'public_evidence': result['acquisition']['public_evidence']}
    else:
        interval, contained = None, None
        branches = [{'outcome': obs['code'], 'intersection': None}]
        observation = {'procedure_edition': edition, 'kind': 'code', 'scalar': None, 'code': obs['code'],
                       'unit': None, 'public_evidence': result['acquisition']['public_evidence']}
    reached = [b['outcome'] for b in branches]
    cells = {(c['hypothesis']['sha256'], c['procedure_edition'], c['outcome']): c for c in derivation['cells']}
    eligibility = {row['hypothesis']['sha256']: row['eligibility'] for row in derivation['baseline']}
    rows = []
    for h in model['hypotheses']:
        hyp = h['explanation']
        base = eligibility[hyp['sha256']]
        hc = [{'outcome': o, 'relation': (lambda r: 'unavailable' if r not in ('permit', 'exclude') else r)(
            cells[(hyp['sha256'], edition, o)]['relation'])} for o in reached]
        reasons = []
        if base == 'baseline_ineligible':
            status = 'baseline_ineligible'
        elif blocked:
            status, reasons = 'not_assessed', ['applicability_blocked']
        elif base == 'baseline_unknown':
            status, reasons = 'unresolved', ['baseline_unknown']
        else:
            rel = {c['relation'] for c in hc}
            if rel == {'permit'}:
                status = 'compatible_under_declared_model'
            elif rel == {'exclude'}:
                status = 'conditionally_incompatible'
            else:
                status = 'unresolved'
                reasons = ['cell_unavailable'] if 'unavailable' in rel or not rel else ['mixed_permit_exclude']
        rows.append({'hypothesis': hyp, 'baseline': base, 'status': status, 'cells': hc, 'reasons': reasons})
    statuses = [r['status'] for r in rows]
    if blocked:
        disposition = 'applicability_blocked'
    elif 'unresolved' in statuses:
        disposition = 'incomplete_assessment'
    elif statuses.count('compatible_under_declared_model') >= 2:
        disposition = 'multiple_compatible'
    elif statuses.count('compatible_under_declared_model') == 1:
        disposition = 'one_compatible'
    else:
        disposition = 'model_prediction_mismatch'
    changed = request['selection_basis'] == 'historical_reference_with_plan_change'
    return {'schema': 'ct.reassessment.v1', 'profile': PROFILE, 'request': request_ref,
            'selection_basis': request['selection_basis'], 'prior_selection': prior_selection_ref,
            'former_plan': former_plan, 'executed_plan': executed_plan,
            'original_plan_executed': not changed, 'plan_changed': changed,
            'derivation': derivation_ref, 'applicability': applicability_ref, 'build': build_ref,
            'observation': observation, 'interval': interval, 'contained': contained,
            'branches': branches, 'hypotheses': rows, 'disposition': disposition,
            'ranking': 'not_reassessed', 'adoption': 'derived_not_adopted', 'presentation': PRESENTATION}
