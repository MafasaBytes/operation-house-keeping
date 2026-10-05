"""Selection-phase witnesses through the in-process evaluate entry point.

Every case is a complete hash-consistent graph; build is the labelled test double.
"""
import json
import pytest
from applications.bounded_decision_workflow.checked_contracts import (EDITION_LIMITS, T1, T2, CheckedRefusal,
                                                                      canonical_bytes, sha)
from tests.checked_temperature.fixtures import (A1_ALLOWLIST, Case, authority, claim, claim_params, fx1, load, r,
                                                run_selection, selection_request, support_graph)


def refusal(fn, *a, **k):
    with pytest.raises(CheckedRefusal) as e:
        fn(*a, **k)
    return e.value


def select(case):
    files = run_selection(case)
    return files, load(files, 'result.json'), load(files, 'derivation.json'), load(files, 'applicability.json')


def branches(result, procedure, case):
    names = {case.world.refof('H1')['sha256']: 'H1', case.world.refof('H2')['sha256']: 'H2'}
    score = [s for s in result['scores'] if s['procedure_edition'] == procedure][0]
    return {b['outcome']: sorted(names[x['sha256']] for x in b['survivors']) for b in score['branches']}, score


def test_lb1_h2_offset_3_to_15_permits_low_and_gap():
    case = fx1(h2=(3, 15))
    files, res, der, app = select(case)
    got, score = branches(res, T1, case)
    assert got == {'low': ['H2'], 'gap': ['H2'], 'high': ['H1']} and score['worst_survivors'] == 1
    assert res['disposition'] == 'ranked'


def test_pm1_missing_t1_plan_withholds_without_default():
    case = fx1(plan_w=None)
    files, res, der, app = select(case)
    assert res['disposition'] == 'withheld'
    assert res['withheld_reasons'] == ['observation_interpretation_plan_missing']
    assert res['scores'] == [] and res['best'] is None
    assert len(der['cells']) == 10   # derivation cells retained
    row = res['observation_uncertainty_not_in_score'][0]
    assert row['plan'] is None and row['plan_state'] == 'missing' and row['plan_claim'] is None
    assert {c['condition'] for c in app['claims']} == {'reference_calibration', 'reference_mapping', 'state_hold',
                                                       'indicator_fidelity'}


@pytest.mark.parametrize('w,code', [((0, 1), 'INTERPRETATION_POINT_UNSUPPORTED'),
                                    ((5000001, 1000000), 'INTERPRETATION_HALF_WIDTH_OUT_OF_RANGE')])
def test_hw0_hw5p_plan_half_width_refusals(w, code):
    e = refusal(run_selection, fx1(plan_w=w))
    assert (e.code, e.stage) == (code, 4)


def test_hw5_half_width_5_is_admitted_and_ranked_as_sc1():
    case = fx1(plan_w=(5, 1))
    files, res, der, app = select(case)
    assert res['disposition'] == 'ranked' and res['best'] == [T1]
    assert res['observation_uncertainty_not_in_score'][0]['half_width'] == r(5)


def test_ob4_b_ref_applied_once_in_the_ideal_set_only():
    case = fx1(b_ref=((-1, 2), (1, 2)))
    files, res, der, app = select(case)
    h1, h2 = case.world.refof('H1')['sha256'], case.world.refof('H2')['sha256']
    pred = {(p['hypothesis']['sha256'], p['procedure_edition']): p['interval'] for p in der['predictions']}
    assert pred[(h1, T1)] == {'lo': r(596, 10), 'hi': r(606, 10)}
    assert pred[(h2, T1)] == {'lo': r(446, 10), 'hi': r(556, 10)}
    got, score = branches(res, T1, case)
    assert score['worst_survivors'] == 1 and got == {'low': ['H2'], 'gap': [], 'high': ['H1']}


@pytest.mark.parametrize('target,code', [((601, 10), 'heater_off'), ((602, 10), 'heater_on')])
def test_t2a_t2b_indicator_rule_equality_is_off(target, code):
    case = fx1(t2_target=target)
    files, res, der, app = select(case)
    got, score = branches(res, T2, case)
    assert got[code] == ['H1', 'H2'] and score['worst_survivors'] == 2 and res['best'] == [T1]


def test_be1_baseline_mismatch_withholds_and_retains_both():
    case = fx1(model_edit=lambda m, w: m.update(baseline=r(602, 10)))
    files, res, der, app = select(case)
    assert {b['eligibility'] for b in der['baseline']} == {'baseline_ineligible'}
    assert len(der['baseline']) == 2
    assert der['baseline'][0]['value_check'] == {'expected': r(602, 10), 'observed': r(601, 10), 'result': 'false'}
    assert res['disposition'] == 'withheld' and res['withheld_reasons'] == ['baseline_ineligible']
    assert {c['relation'] for c in der['cells']} == {'not_assessed_baseline'}


def _cb_case(*, new_declaration, fresh_review):
    """CB1-CB3: model revision 2 changes b_ref; revision-1 calibration graph is retained."""
    case = fx1()
    w = case.world
    w.objects.pop(case.request_pin)
    w.objects.pop(case.authority_pin)
    model1_ref, model1 = w.refof('model'), w.value('model')
    model2 = dict(model1, revision=2, predecessor=model1_ref, b_ref={'lo': r(-1, 2), 'hi': r(1, 2)})
    w.put(model2, 'model2')
    old_claim_ref = [c for c in case.request['claims']
                     if json.loads(w.objects[c['sha256']])['binding']['condition'] == 'reference_calibration'][0]
    graph = {'claims': [], 'declarations': [], 'evidence_items': [], 'reviews': []}
    # Re-derive every non-calibration claim for revision 2 with support; keep the old calibration graph.
    w.h['model'] = w.h['model2']
    for p, conds in ((T1, ('reference_calibration', 'reference_mapping', 'state_hold', 'observation_error_bound')),
                     (T2, ('state_hold', 'indicator_fidelity'))):
        for c in conds:
            cr = w.put(claim(model_ref=w.refof('model2'), procedure=p, phase='selection', condition=c,
                             params=claim_params(c, model=model2, plan_ref=w.refof('P0'), plan=w.value('P0'))))
            graph['claims'].append(cr)
            if c == 'reference_calibration':
                new_claim = cr
                if not new_declaration:
                    continue
                g = support_graph(w, cr, 'r2-cal', review=fresh_review)
                if not fresh_review:   # declaration only: drop the item and its content entirely
                    item = json.loads(w.objects.pop(g['evidence_items'][0]['sha256']))
                    w.objects.pop(item['content']['sha256'])
                    g['evidence_items'] = []
            else:
                g = support_graph(w, cr, 'r2-%s-%s' % (p[-5:-3], c))
            for k in ('declarations', 'evidence_items', 'reviews'):
                graph[k] += g[k]
    old = [x for x in ('declarations', 'evidence_items', 'reviews')]
    for k in old:
        for x in case.request[k]:
            v = json.loads(w.objects[x['sha256']])
            bound = v.get('claim') == old_claim_ref or old_claim_ref in v.get('claims', [])
            if bound:
                graph[k].append(x)
    graph['claims'].append(old_claim_ref)
    # Drop revision-1 objects that the new request no longer references (other than via the old graph).
    keep = set()
    for k in graph:
        keep.update(x['sha256'] for x in graph[k])
    for x in case.request['claims'] + case.request['declarations'] + case.request['evidence_items'] + \
            case.request['reviews']:
        if x['sha256'] not in keep:
            v = json.loads(w.objects.pop(x['sha256']))
            if v['schema'] == 'ct.evidence-item.v1':
                w.objects.pop(v['content']['sha256'], None)
    request = selection_request(w, graph)
    rref = w.put(request)
    twin = Case(w, request, authority(purpose='evaluation', target=rref, phase='selection', procedures=[T1, T2]))
    return twin, old_claim_ref, new_claim


def test_cb1_changed_b_ref_without_new_declaration():
    case, old, new = _cb_case(new_declaration=False, fresh_review=False)
    files, res, der, app = select(case)
    row = [c for c in app['claims'] if c['claim'] == new][0]
    assert row['declaration_state'] == 'missing' and 'declaration_missing' in row['block_reasons']
    assert old in app['unbound']['claims'] and app['unbound']['reviews']
    assert res['disposition'] == 'withheld' and res['withheld_reasons'] == ['applicability_blocked']


def test_cb2_new_declaration_but_only_the_old_review():
    case, old, new = _cb_case(new_declaration=True, fresh_review=False)
    files, res, der, app = select(case)
    row = [c for c in app['claims'] if c['claim'] == new][0]
    assert (row['reviewed_relation'], row['review_completeness'], row['governing_state']) == \
        ('none', 'complete', 'unresolved')
    assert row['block_reasons'] == ['unresolved_not_permitted']
    assert len(app['unbound']['reviews']) == 1   # the old review does not support the changed claim


def test_cb3_fresh_supporting_review_of_revision_2_claim():
    case, old, new = _cb_case(new_declaration=True, fresh_review=True)
    files, res, der, app = select(case)
    row = [c for c in app['claims'] if c['claim'] == new][0]
    assert row['governing_state'] == 'supported' and res['disposition'] == 'ranked'
    assert len(app['unbound']['reviews']) == 1


def test_po1_absent_policy_refuses_without_default():
    case = fx1()
    objects = {d: b for d, b in case.objects.items() if d != case.world.refof('policy')['sha256']}
    e = refusal(run_selection, case, objects=objects)
    assert e.code == 'REFERENCE_MISSING' and case.world.refof('policy')['sha256'] in e.target


def test_po2_explicit_empty_allowlist_is_honoured():
    case = fx1(allowlist=[], phase_kw={'no_review': ('reference_calibration',)})
    files, res, der, app = select(case)
    row = [c for c in app['claims'] if c['condition'] == 'reference_calibration' and
           c['procedure_edition'] == T1][0]
    assert row['governing_state'] == 'unresolved' and row['block_reasons'] == ['unresolved_not_permitted']
    assert res['withheld_reasons'] == ['applicability_blocked']


def test_a1_example_allowlist_covers_calibration_and_omits_error_bound_and_fidelity():
    case = fx1(allowlist=A1_ALLOWLIST,
               phase_kw={'no_review': ('reference_calibration', 'observation_error_bound', 'indicator_fidelity')})
    files, res, der, app = select(case)
    effect = {c['condition']: c['use_effect'] for c in app['claims']}
    assert effect['reference_calibration'] == 'conditional_unresolved'
    assert effect['observation_error_bound'] == 'blocked' and effect['indicator_fidelity'] == 'blocked'
    assert app['use_disposition'] == 'blocked'


def test_po3_empty_permitted_builds_is_schema_invalid():
    e = refusal(run_selection, fx1(policy_edit=lambda p: p.update(permitted_builds=[])))
    assert (e.code, e.stage) == ('SCHEMA_INVALID', 2)


def test_po4_loosened_limit_refuses():
    e = refusal(run_selection, fx1(policy_edit=lambda p: p['limits'].update(reviews=65)))
    assert e.code == 'POLICY_LIMIT_INVALID'


def test_po5_wrong_policy_edition_label_refuses():
    e = refusal(run_selection, fx1(policy_edit=lambda p: p.update(edition='ct.policy-edition.v1')))
    assert e.code == 'POLICY_EDITION_MISMATCH'


def test_build_outside_permitted_builds_refuses():
    from tests.checked_temperature.fixtures import TestDoubleBuild
    case = fx1()
    e = refusal(run_selection, case, build=TestDoubleBuild(marker='1'))
    assert e.code == 'BUILD_NOT_PERMITTED'


def test_f1b_three_hypotheses_schema_invalid():
    def edit(m, w):
        m['hypotheses'].append(dict(m['hypotheses'][1]))
    e = refusal(run_selection, fx1(model_edit=edit))
    assert e.code == 'SCHEMA_INVALID'


def test_f2b_t1_twice_refuses():
    def edit(m, w):
        m['procedures'][1] = dict(m['procedures'][0])
    e = refusal(run_selection, fx1(model_edit=edit, phase_kw={}))
    assert e.code == 'SCHEMA_INVALID'


@pytest.mark.parametrize('h2,ok', [((5, 50), True), ((5, (50000001, 1000000)), False), ((0, 15), False)])
def test_f8_h2_offset_domain(h2, ok):
    lo, hi = h2
    def edit(m, w):
        m['hypotheses'][1]['b_suspect'] = {'lo': r(lo), 'hi': r(*hi) if isinstance(hi, tuple) else r(hi)}
    case = fx1(model_edit=edit)
    if ok:
        assert run_selection(case)
    else:
        assert refusal(run_selection, case).code == 'ACCOUNT_KIND_CONSTRAINT_VIOLATED'


@pytest.mark.parametrize('hi,ok', [((10, 1), True), ((10000001, 1000000), False)])
def test_f9_b_ref_bound(hi, ok):
    case = fx1(b_ref=((0, 1), hi))
    if ok:
        assert run_selection(case)
    else:
        assert refusal(run_selection, case).code == 'ACCOUNT_KIND_CONSTRAINT_VIOLATED'


def test_f5b_seven_fractional_digits_is_rational_invalid():
    e = refusal(run_selection, fx1(b_ref=((0, 1), (1, 10000000))))
    assert e.code == 'RATIONAL_INVALID'


@pytest.mark.parametrize('digits,code', [(32, None), (33, 'RESOURCE_LIMIT_EXCEEDED')])
def test_f6_integer_digits(digits, code):
    n = 10 ** (digits - 1) + 1
    case = fx1(model_edit=lambda m, w: m.update(baseline={'numerator': str(n), 'denominator': '1000000'}))
    if code is None:
        files, res, der, app = select(case)   # admitted; baseline then ineligible, withheld
        assert res['withheld_reasons'] == ['baseline_ineligible']
    else:
        assert refusal(run_selection, case).code == code


def _extra_items(count, *, reviews_on_first=0):
    def extra(w):
        cal = [k for k in w.h if k.startswith('claim-selection-T1-reference_calibration')][0]
        claim_ref = w.refof(cal)
        out = {'evidence_items': [], 'reviews': []}
        for i in range(count):
            g = support_graph(w, claim_ref, 'extra-%d' % i, review=i < reviews_on_first)
            out['evidence_items'] += g['evidence_items']
            out['reviews'] += g['reviews']
            w.objects.pop(g['declarations'][0]['sha256'])
        return out
    return extra


@pytest.mark.parametrize('extra,ok', [(7, True), (8, False)])
def test_f10_evidence_items_per_claim(extra, ok):
    case = fx1(extra_graph=_extra_items(extra))
    if ok:
        assert run_selection(case)
    else:
        assert refusal(run_selection, case).code == 'RESOURCE_LIMIT_EXCEEDED'


@pytest.mark.parametrize('count,ok', [(4, True), (5, False)])
def test_f11_reviews_per_item(count, ok):
    def extra(w):
        cal = [k for k in w.h if k.startswith('item-selection-T1-reference_calibration')][0]
        item_ref = w.refof(cal)
        claim_ref = w.refof([k for k in w.h if k.startswith('claim-selection-T1-reference_calibration')][0])
        reviews = []
        for i in range(count - 1):
            reviews.append(w.put({**w.value('review-selection-T1-reference_calibration'), 'id': 'extra-review-%d' % i,
                                  'item': item_ref, 'claim': claim_ref}))
        return {'reviews': reviews}
    case = fx1(extra_graph=extra)
    if ok:
        assert run_selection(case)
    else:
        assert refusal(run_selection, case).code == 'RESOURCE_LIMIT_EXCEEDED'


def test_f12b_65_reviews_refused_at_stage_2_finding_f7():
    """AMENDED (v4 §12.2): original F12b expected RESOURCE_LIMIT_EXCEEDED; the schema's
    request.reviews maxItems 64 precedes the stage-4 count, so SCHEMA_INVALID."""
    def extra(w):
        base = w.value('review-selection-T1-reference_calibration')
        return {'reviews': [w.put({**base, 'id': 'bulk-%d' % i}) for i in range(59)]}
    e = refusal(run_selection, fx1(extra_graph=extra))
    assert (e.code, e.stage) == ('SCHEMA_INVALID', 2)


def test_f12a_64_reviews_admitted():
    """64 reviews within every per-item (4) and per-claim (8) cap: 6 base items x 4
    reviews plus 10 extra reviewed items x 4 reviews."""
    def extra(w):
        claims = sorted(k for k in w.h if k.startswith('claim-selection-'))
        out = {'evidence_items': [], 'reviews': []}
        for k in sorted(w.h):
            if k.startswith('review-selection-'):
                v = w.value(k)
                out['reviews'] += [w.put({**v, 'id': '%s-x%d' % (v['id'], i)}) for i in range(3)]
        for i in range(10):
            g = support_graph(w, w.refof(claims[i % len(claims)]), 'bulk-%d' % i)
            w.objects.pop(g['declarations'][0]['sha256'])
            out['evidence_items'] += g['evidence_items']
            v = w.value('review-bulk-%d' % i)
            out['reviews'] += g['reviews'] + [w.put({**v, 'id': 'review-bulk-%d-x%d' % (i, j)}) for j in range(3)]
        return out
    case = fx1(extra_graph=extra)
    assert len(case.request['reviews']) == 64 and len(case.request['evidence_items']) == 16
    files, res, der, app = select(case)
    assert res['disposition'] == 'ranked'


def test_in6_request_references_absent_model_revision():
    case = fx1()
    model = case.world.value('model')
    model2 = dict(model, revision=2, predecessor=case.world.refof('model'))
    objects = {d: b for d, b in case.objects.items() if d != case.world.refof('model')['sha256']}
    objects[sha(canonical_bytes(model2))] = canonical_bytes(model2)
    e = refusal(run_selection, case, objects=objects)
    assert e.code == 'REFERENCE_MISSING' and case.world.refof('model')['sha256'] in e.target


def test_in7_changed_authority_under_unchanged_pin():
    case = fx1()
    changed = dict(case.auth, valid={'from': '2026-10-01T00:00:00Z', 'to': '2026-11-30T00:00:00Z'})
    objects = {d: b for d, b in case.objects.items() if d != case.authority_pin}
    objects[sha(canonical_bytes(changed))] = canonical_bytes(changed)
    e = refusal(run_selection, case, objects=objects)
    assert (e.code, e.stage) == ('AUTHORITY_PIN_MISMATCH', 5)


def test_in8_fresh_request_and_authority_with_fresh_pins_complete():
    case = fx1(as_of='2026-10-04T13:00:00Z')
    files, res, der, app = select(case)
    assert res['disposition'] == 'ranked'
    assert load(files, 'invocation.json')['expected_request_pin'] == case.request_pin


def test_selection_authority_scope_and_target():
    case = fx1()
    for edit, code in ((lambda a: a['scope'].update(phase='reassessment'), 'AUTHORITY_SCOPE_MISMATCH'),
                       (lambda a: a['scope'].update(procedure_editions=[T1]), 'AUTHORITY_SCOPE_MISMATCH'),
                       (lambda a: a.update(target={'kind': 'ct.request.v1', 'sha256': '0' * 64}), None)):
        changed = json.loads(json.dumps(case.auth))
        edit(changed)
        wire = canonical_bytes(changed)
        objects = {d: b for d, b in case.objects.items() if d != case.authority_pin}
        objects[sha(wire)] = wire
        from tests.checked_temperature.fixtures import run_selection as rs
        from applications.bounded_decision_workflow import checked_runtime as rt
        with pytest.raises(CheckedRefusal) as e:
            rt.evaluate_selection(request_wire=case.request_wire, objects=objects, request_pin=case.request_pin,
                                  authority_pin=sha(wire), build=case.world.build)
        # A target outside the closure is unresolvable before it can be compared.
        assert e.value.code == (code or 'REFERENCE_MISSING')


def _padded(target_total):
    """F13: pad six distinct unreviewed calibration contents so the decoded closure is exact."""
    def build(sizes):
        def extra(w):
            claim_ref = w.refof([k for k in w.h if k.startswith('claim-selection-T1-reference_calibration')][0])
            out = {'evidence_items': [], 'reviews': []}
            for i, n in enumerate(sizes):
                g = support_graph(w, claim_ref, 'pad-%d' % i, review=False)
                item = json.loads(w.objects.pop(g['evidence_items'][0]['sha256']))
                w.objects.pop(item['content']['sha256'])
                w.objects.pop(g['declarations'][0]['sha256'])
                item['content'] = w.put(bytes([65 + i]) * n)   # distinct bytes: no deduplication
                out['evidence_items'].append(w.put(item))
            return out
        case = fx1(extra_graph=extra)
        return case, sum(len(b) for b in case.objects.values()) + len(case.request_wire)
    sizes = [1000] * 6
    case, total = build(sizes)
    need = target_total - (total - sum(sizes))
    q, rem = divmod(need, 6)
    sizes = [q + (1 if i < rem else 0) for i in range(6)]
    assert max(sizes) <= EDITION_LIMITS['object_bytes']
    case, total = build(sizes)
    assert total == target_total
    return case


@pytest.mark.parametrize('total,ok', [(1048576, True), (1048577, False)])
def test_f13_decoded_selection_closure_boundary(total, ok):
    case = _padded(total)
    if ok:
        files, res, der, app = select(case)
        assert sum(m['decoded_bytes'] for m in load(files, 'closure.json')['members']) == total
    else:
        e = refusal(run_selection, case)
        assert (e.code, e.target) == ('RESOURCE_LIMIT_EXCEEDED', '/closure/decoded_bytes')


def test_captured_policy_may_tighten_the_unique_object_cap():
    e = refusal(run_selection, fx1(policy_edit=lambda p: p['limits'].update(selection_unique_objects=10)))
    assert (e.code, e.target) == ('RESOURCE_LIMIT_EXCEEDED', '/closure/unique_objects')


def _c1_case(*, supplied_item):
    """Review C1 twin: an opposing review bound to the required calibration claim whose
    item is reachable only through the review (or whose claim is not among the item's claims)."""
    def extra(w):
        cal = w.refof([k for k in w.h if k.startswith('claim-selection-T1-reference_calibration')][0])
        g = support_graph(w, cal, 'hidden', relation='opposition')
        w.objects.pop(g['declarations'][0]['sha256'])
        if supplied_item:   # variant: supplied item, review claim not among the item's claims
            mapping = w.refof([k for k in w.h if k.startswith('claim-selection-T1-reference_mapping')][0])
            item = json.loads(w.objects.pop(g['evidence_items'][0]['sha256']))
            w.objects.pop(g['reviews'][0]['sha256'])
            item['claims'] = [mapping]
            item_ref = w.put(item)
            review = w.put({**w.value('review-hidden'), 'item': item_ref})
            return {'evidence_items': [item_ref], 'reviews': [review]}
        return {'reviews': g['reviews']}   # item deliberately not listed in evidence_items
    return fx1(extra_graph=extra)


@pytest.mark.parametrize('supplied_item', [False, True], ids=['item-unsupplied', 'claim-not-in-item'])
def test_c1_review_cannot_drop_out_of_aggregation(supplied_item):
    e = refusal(run_selection, _c1_case(supplied_item=supplied_item))
    assert (e.code, e.stage) == ('SCHEMA_INVALID', 4) and e.target.endswith('/item_claim_binding')


def test_i3_malformed_legacy_evidence_is_a_structural_refusal():
    def edit(m, w):
        w.objects.pop(m['baseline_evidence']['sha256'])
        m['baseline_evidence'] = w.put({'schema': 'nm.evidence.v1'})
    e = refusal(run_selection, fx1(model_edit=edit))
    assert (e.code, e.target) == ('SCHEMA_INVALID', '/nm.evidence.v1')


def test_i4_deep_nesting_is_a_resource_refusal():
    from applications.bounded_decision_workflow import checked_runtime as rt
    case = fx1()
    wire = b'[' * 90000 + b']' * 90000
    with pytest.raises(CheckedRefusal) as e:
        rt.evaluate_selection(request_wire=wire, objects=case.objects, request_pin=sha(wire),
                              authority_pin=case.authority_pin, build=case.world.build)
    assert e.value.code == 'RESOURCE_LIMIT_EXCEEDED'
