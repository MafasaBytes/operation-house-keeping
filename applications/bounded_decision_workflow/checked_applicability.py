"""Checked applicability: required claims, coverage, declarations, aggregation, gates.

Item-level order, the two condition axes and the governing-state precedence
follow the corrected design §5 exactly. Pending evidence never weakens
`contradicted` or `conflicting`; the allowlist can never permit them.
"""
from .checked_contracts import (CATALOGUE, PROCEDURE_CONDITIONS, PROFILE, T1, T2,
                                canonical_bytes, ref, refuse, sha, window)


def claim_core(*, model_ref, model, procedure, phase, condition, plan_ref=None, plan=None):
    ctx = model['context']
    if condition == 'reference_calibration':
        params = {'instrument_id': model['reference_instrument_id'], 'b_ref': model['b_ref']}
    elif condition == 'reference_mapping':
        params = {'instrument_id': model['reference_instrument_id'],
                  'structural_model_revision': ctx['structural_model_revision'],
                  'subject_entity_anchor_id': ctx['subject_entity_anchor_id'],
                  'variable_anchor_id': ctx['variable_anchor_id']}
    elif condition == 'state_hold':
        params = {'baseline_as_of': ctx['as_of'],
                  'b_suspect': [{'explanation': h['explanation'], 'interval': h['b_suspect']}
                                for h in model['hypotheses']]}
    elif condition == 'indicator_fidelity':
        t2 = next(p for p in model['procedures'] if p['edition'] == T2)
        params = {'instrument_id': t2['indicator_instrument_id'], 'target': t2['target']}
    else:  # observation_error_bound
        params = {'instrument_id': plan['instrument_id'], 'plan': plan_ref, 'half_width': plan['half_width']}
    return {'schema': 'ct.claim.v1', 'profile': PROFILE, 'catalogue': CATALOGUE,
            'procedure_edition': procedure, 'phase': phase, 'model': model_ref,
            'subject_entity_anchor_id': ctx['subject_entity_anchor_id'],
            'variable_anchor_id': ctx['variable_anchor_id'],
            'binding': {'condition': condition, 'parameters': params}}


def required_claims(*, model_ref, model, phase, procedures, plans):
    """One claim per nominated procedure x governing condition for this phase.

    `plans` maps procedure edition to (plan_ref, plan) or None. A T1 procedure
    with no plan has no observation-error claim (selection withholds instead).
    """
    out = []
    for procedure in procedures:
        for condition in PROCEDURE_CONDITIONS[procedure]:
            if condition == 'observation_error_bound':
                pp = plans.get(procedure)
                if pp is None:
                    continue
                core = claim_core(model_ref=model_ref, model=model, procedure=procedure, phase=phase,
                                  condition=condition, plan_ref=pp[0], plan=pp[1])
            else:
                core = claim_core(model_ref=model_ref, model=model, procedure=procedure, phase=phase,
                                  condition=condition)
            out.append(core)
    return out


def _cover(w, scope):
    a, b = window(w)
    if a <= scope[0] and b >= scope[1]:
        return 'full'
    if b < scope[0] or a > scope[1]:
        return 'disjoint'
    return 'partial'


def _sorted(refs):
    return sorted(refs, key=lambda r: (r['kind'], r['sha256']))


def _claim_parameter(claim, name):
    return claim['binding']['parameters'].get(name)


def assess_item(*, item_ref, item, claim, claim_ref, reviews, scope, required_reviews):
    """Item-level precedence (design §5 steps 1-4) for one claim-bound item.

    `reviews` are (ref, record) pairs of reviews of this item bound to this claim.
    Returns (row, inapplicable_reviews).
    """
    row = {'item': item_ref, 'status': None, 'exclusion_basis': None,
           'reviews': _sorted([r for r, _ in reviews]), 'contributions': [], 'pending_reasons': []}
    inapplicable = []
    # 1. Conclusive typed exclusion.
    basis = None
    if item['validity'] is not None and _cover(item['validity'], scope) == 'disjoint':
        basis = 'validity_non_overlapping'
    elif (item['subject_entity_anchor_id'] not in (None, claim['subject_entity_anchor_id']) or
          item['variable_anchor_id'] not in (None, claim['variable_anchor_id'])):
        basis = 'anchor_mismatch'
    elif (item['instrument_id'] is not None and _claim_parameter(claim, 'instrument_id') is not None and
          item['instrument_id'] != _claim_parameter(claim, 'instrument_id')):
        basis = 'instrument_mismatch'
    if basis is not None:
        row.update(status='excluded_conclusive', exclusion_basis=basis)
        return row, inapplicable
    # 2. Collect every potentially applicable review.
    pending, contributions, irrelevant, relevant, unresolved, completed = set(), set(), 0, 0, 0, 0
    if item['validity'] is not None and _cover(item['validity'], scope) == 'partial':
        pending.add('partial_or_unknown_scope')   # CONTRACT §4.3: partial item validity stays pending
    applicable = 0
    for r_ref, r in reviews:
        coverage = _cover(r['covers'], scope)
        if coverage == 'disjoint':
            inapplicable.append({'record': r_ref, 'reason': 'covers_disjoint'})
            continue
        if coverage == 'partial':
            pending.add('partial_or_unknown_scope')
            continue
        applicable += 1
        if r['completion'] == 'incomplete':
            pending.add('incomplete_review')
            unresolved += 1
            continue
        completed += 1
        if r['relevance'] == 'irrelevant':
            irrelevant += 1
        elif r['relevance'] == 'unresolved':
            pending.add('unresolved_relevance')
            unresolved += 1
        else:
            relevant += 1
            if r['relation'] in ('support', 'opposition'):
                contributions.add(r['relation'])
            else:
                pending.add('unresolved_relation')
                unresolved += 1
    if applicable == 0 and not pending:
        pending.add('unreviewed')
    # 3. Competing relevance judgments.
    if irrelevant and unresolved:
        pending.add('irrelevant_with_unresolved')
    if irrelevant and relevant:
        pending.add('disputed_relevance')
    if applicable and completed < required_reviews:
        pending.add('missing_required_review')
    # 4. Reviewed exclusion only after those checks.
    if irrelevant and not pending and irrelevant == applicable:
        row.update(status='excluded_reviewed', exclusion_basis='reviewed_irrelevant_unanimous')
        return row, inapplicable
    row['contributions'] = sorted(contributions)
    row['pending_reasons'] = sorted(pending)
    row['status'] = 'pending' if pending else 'contributing'
    return row, inapplicable


def governing_state(relation, completeness):
    if relation == 'support_and_opposition':
        return 'conflicting'
    if relation == 'opposition_only':
        return 'contradicted'
    if relation == 'support_only' and completeness == 'complete':
        return 'supported'
    return 'unresolved'


def assess(*, request_ref, policy_ref, build_ref, phase, scope, required, supplied, policy, limits):
    """Return the ct.applicability.v1 record.

    `required` is a list of claim cores; `supplied` maps 'claims', 'declarations',
    'evidence_items', 'reviews' to lists of (ref, record) pairs from the request.
    """
    req_refs = {sha(canonical_bytes(c)): c for c in required}
    allow = {(e['condition'], e['phase']) for e in policy['unresolved_allowlist']}
    rows, pending_items, assumed = [], set(), []
    used_decl, used_items, used_reviews = set(), set(), set()
    for digest, claim in req_refs.items():
        claim_ref = ref('ct.claim.v1', digest)
        condition = claim['binding']['condition']
        inapplicable = []
        decls = [(r, d) for r, d in supplied['declarations'] if d['claim']['sha256'] == digest]
        if len(decls) > limits['declarations_per_claim']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 4, '/declarations_per_claim')
        applicable_decls = []
        for r, d in decls:
            used_decl.add(r['sha256'])
            c = _cover(d['covers'], scope)
            if c == 'full':
                applicable_decls.append((r, d))
            else:
                inapplicable.append({'record': r, 'reason': 'covers_disjoint' if c == 'disjoint'
                                     else 'declaration_covers_partial'})
        states = {d['state'] for _, d in applicable_decls}
        declaration_state = ('missing' if not states else 'conflicting' if len(states) > 1 else states.pop())
        items = [(r, i) for r, i in supplied['evidence_items'] if any(c['sha256'] == digest for c in i['claims'])]
        if len(items) > limits['evidence_items_per_claim']:
            refuse('RESOURCE_LIMIT_EXCEEDED', 4, '/evidence_items_per_claim')
        item_rows = []
        for i_ref, item in items:
            used_items.add(i_ref['sha256'])
            reviews = [(r, v) for r, v in supplied['reviews']
                       if v['item']['sha256'] == i_ref['sha256'] and v['claim']['sha256'] == digest]
            if len(reviews) > limits['reviews_per_item']:
                refuse('RESOURCE_LIMIT_EXCEEDED', 4, '/reviews_per_item')
            used_reviews.update(r['sha256'] for r, _ in reviews)
            row, inap = assess_item(item_ref=i_ref, item=item, claim=claim, claim_ref=claim_ref,
                                    reviews=reviews, scope=scope,
                                    required_reviews=policy['required_reviews_per_item'])
            inapplicable.extend(inap)
            item_rows.append(row)
        live = [r for r in item_rows if r['status'] in ('contributing', 'pending')]
        sides = {c for r in live for c in r['contributions']}
        relation = ('support_and_opposition' if sides == {'support', 'opposition'} else
                    'support_only' if sides == {'support'} else
                    'opposition_only' if sides == {'opposition'} else 'none')
        completeness = 'pending' if any(r['status'] == 'pending' for r in item_rows) else 'complete'
        state = governing_state(relation, completeness)
        permits = (condition, phase) in allow
        reasons = []
        reasons += {'missing': ['declaration_missing'], 'conflicting': ['conflicting_declarations'],
                    'false': ['declaration_false'], 'unknown': ['declaration_unknown'], 'true': []}[declaration_state]
        if state == 'contradicted':
            reasons.append('governing_state_contradicted')
        if state == 'conflicting':
            reasons.append('governing_state_conflicting')
        if state == 'unresolved' and not permits:
            reasons.append('unresolved_not_permitted')
        effect = 'blocked' if reasons else 'conditional_unresolved' if state == 'unresolved' else 'permitted'
        if effect == 'conditional_unresolved':
            assumed.append(claim_ref)
        pending_items.update(r['item']['sha256'] for r in item_rows if r['status'] == 'pending')
        rows.append({'claim': claim_ref, 'condition': condition, 'procedure_edition': claim['procedure_edition'],
                     'phase': phase, 'declarations': _sorted([r for r, _ in decls]),
                     'declaration_state': declaration_state,
                     'items': sorted(item_rows, key=lambda r: r['item']['sha256']),
                     'reviewed_relation': relation, 'review_completeness': completeness,
                     'governing_state': state, 'policy_permits_unresolved': permits,
                     'use_effect': effect, 'block_reasons': reasons,
                     'time_scope': {'from': scope[0].strftime('%Y-%m-%dT%H:%M:%SZ'),
                                    'to': scope[1].strftime('%Y-%m-%dT%H:%M:%SZ')},
                     'inapplicable': sorted(inapplicable, key=lambda x: (x['record']['sha256'], x['reason']))})
    rows.sort(key=lambda r: (r['procedure_edition'], r['condition'], r['claim']['sha256']))
    effects = {r['use_effect'] for r in rows}
    disposition = ('blocked' if 'blocked' in effects else
                   'conditional_use_with_unresolved_conditions' if 'conditional_unresolved' in effects
                   else 'use_permitted')
    unbound = {
        'claims': _sorted([r for r, _ in supplied['claims'] if r['sha256'] not in req_refs]),
        'declarations': _sorted([r for r, _ in supplied['declarations'] if r['sha256'] not in used_decl]),
        'evidence_items': _sorted([r for r, _ in supplied['evidence_items'] if r['sha256'] not in used_items]),
        'reviews': _sorted([r for r, _ in supplied['reviews'] if r['sha256'] not in used_reviews]),
    }
    return {'schema': 'ct.applicability.v1', 'profile': PROFILE, 'request': request_ref, 'policy': policy_ref,
            'build': build_ref, 'phase': phase, 'claims': rows, 'unbound': unbound,
            'use_disposition': disposition, 'assumed_conditions': _sorted(assumed),
            'pending_items': _sorted([ref('ct.evidence-item.v1', d) for d in pending_items])}
