"""Checked selection over ideal modelled decoder branches (design §4, FIXED).

Score = maximum survivor cardinality across a procedure's decoder branches.
The observation-error plan is captured and reported, never scored. Any
withholding reason withholds the whole nominated set; nothing is pruned.
"""
from .checked_contracts import PROFILE, T1, T2, T2_CODES

PRESENTATION = ('Preferred for worst-case separation of ideal modelled decoder branches among these supplied '
                'hypotheses. Measurement uncertainty can leave multiple hypotheses unresolved; this score does '
                'not guarantee elimination, a settled reassessment or the actual cause.')
OUTCOMES = {T1: ('low', 'gap', 'high'), T2: T2_CODES}


def uncertainty_rows(model, plan_ref, plan, plan_claim_ref):
    if not any(p['edition'] == T1 for p in model['procedures']):
        return []
    return [{'procedure_edition': T1, 'plan': plan_ref,
             'half_width': None if plan is None else plan['half_width'], 'unit': 'degree_celsius',
             'plan_claim': plan_claim_ref, 'plan_state': 'missing' if plan_ref is None else 'captured'}]


def select(*, request_ref, derivation_ref, applicability_ref, build_ref, model, derivation, applicability,
           plan_ref, plan, plan_claim_ref):
    withheld = []
    if plan_ref is None and any(p['edition'] == T1 for p in model['procedures']):
        withheld.append('observation_interpretation_plan_missing')
    eligibility = {row['eligibility'] for row in derivation['baseline']}
    if 'baseline_ineligible' in eligibility:
        withheld.append('baseline_ineligible')
    if 'baseline_unknown' in eligibility:
        withheld.append('baseline_unknown')
    if any(p['status'] != 'derived' and p['unavailable_reason'] != 'baseline_not_eligible'
           for p in derivation['predictions']):
        withheld.append('derivation_unavailable')
    if applicability['use_disposition'] == 'blocked':
        withheld.append('applicability_blocked')
    scores, best = [], None
    if not withheld:
        hyps = [h['explanation'] for h in model['hypotheses']]
        permits = {(c['hypothesis']['sha256'], c['procedure_edition'], c['outcome'])
                   for c in derivation['cells'] if c['relation'] == 'permit'}
        for p in model['procedures']:
            edition = p['edition']
            branches = [{'outcome': o, 'survivors': sorted(
                [h for h in hyps if (h['sha256'], edition, o) in permits], key=lambda r: r['sha256'])}
                for o in OUTCOMES[edition]]
            worst = max(len(b['survivors']) for b in branches)
            scores.append({'procedure_edition': edition, 'worst_survivors': worst,
                           'reduction': len(hyps) - worst, 'branches': branches})
        low = min(s['worst_survivors'] for s in scores)
        best = sorted(s['procedure_edition'] for s in scores if s['worst_survivors'] == low)
    return {'schema': 'ct.selection.v1', 'profile': PROFILE, 'request': request_ref,
            'derivation': derivation_ref, 'applicability': applicability_ref, 'build': build_ref,
            'score_domain': 'ideal_measurand_decoder_branches',
            'post_measurement_elimination_guaranteed': False,
            'disposition': 'withheld' if withheld else 'ranked', 'withheld_reasons': withheld,
            'scores': scores, 'best': best,
            'observation_uncertainty_not_in_score': uncertainty_rows(model, plan_ref, plan, plan_claim_ref),
            'use_disposition': applicability['use_disposition'], 'presentation': PRESENTATION}
