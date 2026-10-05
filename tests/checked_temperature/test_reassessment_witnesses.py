"""Reassessment witnesses through the in-process evaluate entry point (CO1)."""
import json
import pytest
from applications.bounded_decision_workflow.checked_contracts import T1, T2, CheckedRefusal, canonical_bytes, sha
from tests.checked_temperature.fixtures import (claim, claim_params, co1, fx1, load, r, run_reassessment,
                                                run_selection, support_graph)


@pytest.fixture(scope='module')
def prior():
    base = fx1()
    return base, run_selection(base)


def refusal(fn, *a, **k):
    with pytest.raises(CheckedRefusal) as e:
        fn(*a, **k)
    return e.value


def outcome(case, files):
    res = load(files, 'result.json')
    names = {case.world.refof('H1')['sha256']: 'H1', case.world.refof('H2')['sha256']: 'H2'}
    return res, {names[h['hypothesis']['sha256']]: h for h in res['hypotheses']}


def test_un3_scalar_55_6_reaches_low_and_gap(prior):
    base, files = prior
    case = co1(files, base, scalar='55.6')
    res, hyp = outcome(case, run_reassessment(case, files))
    assert res['interval'] == {'lo': r(551, 10), 'hi': r(561, 10)}
    assert [b['outcome'] for b in res['branches']] == ['low', 'gap']
    assert hyp['H1']['status'] == 'conditionally_incompatible'
    assert (hyp['H2']['status'], hyp['H2']['reasons']) == ('unresolved', ['mixed_permit_exclude'])
    assert res['disposition'] == 'incomplete_assessment'


def test_un4_gap_is_open_at_56(prior):
    base, files = prior
    case = co1(files, base, scalar='55.5')
    res, hyp = outcome(case, run_reassessment(case, files))
    assert [b['outcome'] for b in res['branches']] == ['low']
    assert res['branches'][0]['intersection'] == {'lo': r(55), 'lo_closed': True, 'hi': r(56), 'hi_closed': True}
    assert hyp['H2']['status'] == 'compatible_under_declared_model' and res['disposition'] == 'one_compatible'


def test_ps2_newly_scoped_changed_plan_successor(prior):
    base, files = prior
    case = co1(files, base, selection_basis='historical_reference_with_plan_change', new_plan_w=(5, 2),
               scalar='57.6')
    res, hyp = outcome(case, run_reassessment(case, files))
    w = case.world
    assert (res['plan_changed'], res['original_plan_executed']) == (True, False)
    assert res['former_plan'] == w.refof('P0') and res['executed_plan'] == w.refof('P1')
    assert res['prior_selection'] == case.request['prior_selection']['selection']
    assert res['interval'] == {'lo': r(551, 10), 'hi': r(601, 10)}
    assert [b['outcome'] for b in res['branches']] == ['low', 'gap', 'high']
    assert hyp['H1']['status'] == hyp['H2']['status'] == 'unresolved'
    assert res['disposition'] == 'incomplete_assessment'
    assert (res['ranking'], res['adoption']) == ('not_reassessed', 'derived_not_adopted')
    app = load(run_reassessment(case, files), 'applicability.json')
    bound = [c for c in app['claims'] if c['condition'] == 'observation_error_bound'][0]
    assert json.loads(w.objects[bound['claim']['sha256']])['binding']['parameters']['plan'] == w.refof('P1')


def test_ps1_inherited_basis_with_substituted_plan(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'R':
            w.put({**w.value('P0'), 'id': 'plan-P1', 'half_width': r(5, 2)}, 'P1')
            value['result']['interpretation_plan'] = w.refof('P1')
    e = refusal(run_reassessment, co1(files, base, mutate=mutate), files)
    assert e.code == 'INTERPRETATION_PLAN_MISMATCH'


def _ps(mutate_name, edit):
    def mutate(name, value, w):
        if name == mutate_name:
            edit(value, w)
    return mutate


@pytest.mark.parametrize('name,edit,code', [
    ('A', lambda v, w: v.update(plan_change=None), 'AUTHORITY_SCOPE_MISMATCH'),                       # PS3
    ('R', lambda v, w: v['plan_change'].update(new_plan=w.refof('P0')), 'PLAN_CHANGE_INVALID'),         # PS4
    ('R', lambda v, w: v['result'].update(interpretation_plan=w.refof('P0')), 'PLAN_CHANGE_INVALID'),  # PS5
    ('E', lambda v, w: v.update(plan_change=None), 'AUTHORITY_SCOPE_MISMATCH'),                       # EO12
    ('X', lambda v, w: v.update(selection_basis='inherited', plan_change=None,
                                interpretation_plan=w.refof('P0')), 'EXECUTION_TARGET_MISMATCH'),       # EO11
], ids=['PS3', 'PS4', 'PS5', 'EO12', 'EO11'])
def test_changed_plan_refusals(prior, name, edit, code):
    base, files = prior
    case = co1(files, base, selection_basis='historical_reference_with_plan_change', new_plan_w=(5, 2),
               scalar='57.6', mutate=_ps(name, edit))
    assert refusal(run_reassessment, case, files).code == code


def test_pb1_old_error_bound_review_does_not_support_the_new_plan_claim(prior):
    base, files = prior

    def old_graph(w):
        old = w.put(claim(model_ref=w.refof('model'), procedure=T1, phase='reassessment',
                          condition='observation_error_bound',
                          params=claim_params('observation_error_bound', model=w.value('model'),
                                              plan_ref=w.refof('P0'), plan=w.value('P0'))))
        g = support_graph(w, old, 'old-P0-bound')
        g['claims'] = [old]
        return g
    case = co1(files, base, selection_basis='historical_reference_with_plan_change', new_plan_w=(5, 2),
               scalar='57.6', phase_kw={'no_item': ('observation_error_bound',)}, extra_graph=old_graph)
    out = run_reassessment(case, files)
    res, hyp = outcome(case, out)
    app = load(out, 'applicability.json')
    row = [c for c in app['claims'] if c['condition'] == 'observation_error_bound'][0]
    assert (row['reviewed_relation'], row['review_completeness'], row['governing_state']) == \
        ('none', 'complete', 'unresolved')
    assert row['block_reasons'] == ['unresolved_not_permitted']
    assert len(app['unbound']['reviews']) == 1 and len(app['unbound']['claims']) == 1
    assert res['disposition'] == 'applicability_blocked'
    assert {h['status'] for h in hyp.values()} == {'not_assessed'}


def test_ob2_opposed_error_bound_blocks_interpretation(prior):
    base, files = prior
    case = co1(files, base, phase_kw={'relation': {'observation_error_bound': 'opposition'}})
    res, hyp = outcome(case, run_reassessment(case, files))
    assert res['disposition'] == 'applicability_blocked'
    assert {h['status'] for h in hyp.values()} == {'not_assessed'}
    assert all(h['reasons'] == ['applicability_blocked'] for h in hyp.values())


def test_ob3_unreviewed_error_bound_is_not_allowlisted_by_a1(prior):
    base, files = prior
    case = co1(files, base, phase_kw={'no_review': ('observation_error_bound',)})
    out = run_reassessment(case, files)
    app = load(out, 'applicability.json')
    row = [c for c in app['claims'] if c['condition'] == 'observation_error_bound'][0]
    assert row['governing_state'] == 'unresolved' and row['block_reasons'] == ['unresolved_not_permitted']
    assert load(out, 'result.json')['disposition'] == 'applicability_blocked'


def test_ob4_reassessment_applies_w_once_and_not_b_ref():
    base = fx1(b_ref=((-1, 2), (1, 2)))
    files = run_selection(base)
    case = co1(files, base, scalar='60.0')
    res, hyp = outcome(case, run_reassessment(case, files))
    assert res['interval'] == {'lo': r(119, 2), 'hi': r(121, 2)}
    assert hyp['H1']['status'] == 'compatible_under_declared_model'
    assert hyp['H2']['status'] == 'conditionally_incompatible'


def test_eo5_evaluation_authority_targets_another_request(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'A':
            r2 = json.loads(json.dumps(w.value('R')))
            r2['id'] = 'request-R2'
            r2['result']['observation']['scalar'] = '60.2'
            value['target'] = w.put(r2, 'R2')
    e = refusal(run_reassessment, co1(files, base, mutate=mutate), files)
    assert (e.code, e.target) == ('AUTHORITY_TARGET_MISMATCH', '/evaluation_authority/target')


@pytest.mark.parametrize('edit,code', [
    (lambda v, w: v['result']['acquisition'].update(instrument_id='inst_' + 'c' * 32), 'EXECUTION_TARGET_MISMATCH'),
    (lambda v, w: v['result'].update(procedure_edition=T2, observation={'kind': 'code', 'code': 'heater_off'},
                                     interpretation_plan=None), 'EXECUTION_TARGET_MISMATCH'),
    (lambda v, w: v['result']['acquisition'].update(ended='2026-10-05T19:00:00Z'), 'AUTHORITY_SCOPE_MISMATCH'),
], ids=['EO6-instrument', 'EO8-procedure', 'EO10-time'])
def test_execution_target_and_scope_substitutions(prior, edit, code):
    base, files = prior
    assert refusal(run_reassessment, co1(files, base, mutate=_ps('R', edit)), files).code == code


def test_eo7_model_substitution(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'R':
            m2 = dict(w.value('model'), revision=2, predecessor=w.refof('model'))
            value['model'] = w.put(m2, 'model2')
    assert refusal(run_reassessment, co1(files, base, mutate=mutate), files).code == 'EXECUTION_TARGET_MISMATCH'


def test_eo9_execution_scope_excludes_procedure(prior):
    base, files = prior
    e = refusal(run_reassessment, co1(files, base, mutate=_ps('E', lambda v, w: v['scope'].update(
        procedure_editions=[T2]))), files)
    assert (e.code, e.target) == ('AUTHORITY_SCOPE_MISMATCH', '/execution_authority/scope')


def test_eo13_widened_execution_authority_under_original_pins(prior):
    base, files = prior
    original = co1(files, base)
    widened = co1(files, base, mutate=_ps('E', lambda v, w: v['valid'].update(to='2026-10-06T18:00:00Z')))
    assert widened.request_pin != original.request_pin
    e = refusal(run_reassessment, widened, files, request_pin=original.request_pin,
                authority_pin=original.authority_pin)
    assert (e.code, e.stage) == ('REQUEST_PIN_MISMATCH', 5)


def test_in9_evaluation_authority_with_selection_phase(prior):
    base, files = prior
    e = refusal(run_reassessment, co1(files, base, mutate=_ps('A', lambda v, w: v['scope'].update(
        phase='selection'))), files)
    assert (e.code, e.target) == ('AUTHORITY_SCOPE_MISMATCH', '/evaluation_authority/scope')


def test_in10_prior_bundle_differs_from_pinned_manifest(prior):
    base, files = prior
    from tests.checked_temperature.fixtures import run_replay
    other = run_replay(base, files)   # a different manifest (replay invocation)
    case = co1(files, base)
    e = refusal(run_reassessment, case, other)
    assert e.code == 'PRIOR_BUNDLE_MISMATCH'


@pytest.mark.parametrize('scalar,code', [('1000', None), ('1000.000001', 'SCALAR_OUT_OF_ADMISSION_DOMAIN')])
def test_f4_scalar_admission_domain(prior, scalar, code):
    base, files = prior
    case = co1(files, base, scalar=scalar)
    if code is None:
        res, hyp = outcome(case, run_reassessment(case, files))
        assert [b['outcome'] for b in res['branches']] == ['high']
    else:
        assert refusal(run_reassessment, case, files).code == code


def test_t2_code_reassessment(prior):
    base, files = prior
    case = co1(files, base, procedure=T2, code='heater_off')
    res, hyp = outcome(case, run_reassessment(case, files))
    assert res['interval'] is None and res['contained'] is None
    assert res['branches'] == [{'outcome': 'heater_off', 'intersection': None}]
    assert {h['status'] for h in hyp.values()} == {'compatible_under_declared_model'}
    assert res['disposition'] == 'multiple_compatible' and res['executed_plan'] is None
