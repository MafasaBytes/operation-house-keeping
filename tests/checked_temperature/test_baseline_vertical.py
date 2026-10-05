"""Baseline vertical path: FX1 selection, then CO1 reassessment (UN1), in process.

Uses the explicitly labelled TestDoubleBuild; this is unit-test evidence, not
executable-build qualification.
"""
import json
import pytest
from applications.bounded_decision_workflow.checked_contracts import T1, T2, canonical_bytes, sha
from tests.checked_temperature.fixtures import (co1, fx1, load, run_reassessment, run_replay, run_selection,
                                                run_verify, r)


@pytest.fixture(scope='module')
def selected():
    case = fx1()
    return case, run_selection(case)


@pytest.fixture(scope='module')
def reassessed(selected):
    base, prior = selected
    case = co1(prior, base)
    return case, prior, run_reassessment(case, prior)


def test_fx1_bundle_files_and_manifest(selected):
    case, files = selected
    assert sorted(files) == sorted(['invocation.json', 'closure.json', 'derivation.json', 'applicability.json',
                                    'result.json', 'trace.json', 'build.json', 'policy.json', 'manifest.json'])
    manifest = load(files, 'manifest.json')
    assert manifest['bundle_kind'] == 'selection'
    for entry in manifest['files']:
        assert sha(files[entry['name']]) == entry['sha256'] and len(files[entry['name']]) == entry['bytes']
    for name in files:   # every file is exactly canonical bytes of its record
        assert canonical_bytes(json.loads(files[name])) == files[name]


def test_fx1_derivation_ideal_sets(selected):
    case, files = selected
    d = load(files, 'derivation.json')
    h1, h2 = case.world.refof('H1'), case.world.refof('H2')
    pred = {(p['hypothesis']['sha256'], p['procedure_edition']): p for p in d['predictions']}
    assert pred[(h1['sha256'], T1)]['interval'] == {'lo': r(601, 10), 'hi': r(601, 10)}
    assert pred[(h2['sha256'], T1)]['interval'] == {'lo': r(451, 10), 'hi': r(551, 10)}
    assert pred[(h1['sha256'], T2)]['code'] == pred[(h2['sha256'], T2)]['code'] == 'heater_off'
    assert {b['eligibility'] for b in d['baseline']} == {'baseline_eligible'}


def test_fx1_selection_scores_sc1(selected):
    case, files = selected
    s = load(files, 'result.json')
    h1, h2 = case.world.refof('H1'), case.world.refof('H2')
    assert s['disposition'] == 'ranked' and s['withheld_reasons'] == []
    t1 = [x for x in s['scores'] if x['procedure_edition'] == T1][0]
    t2 = [x for x in s['scores'] if x['procedure_edition'] == T2][0]
    assert {b['outcome']: b['survivors'] for b in t1['branches']} == {'low': [h2], 'gap': [], 'high': [h1]}
    assert t1['worst_survivors'] == 1 and t1['reduction'] == 1
    assert {b['outcome']: len(b['survivors']) for b in t2['branches']} == {'heater_off': 2, 'heater_on': 0}
    assert t2['worst_survivors'] == 2 and s['best'] == [T1]
    assert s['score_domain'] == 'ideal_measurand_decoder_branches'
    assert s['post_measurement_elimination_guaranteed'] is False
    row = s['observation_uncertainty_not_in_score'][0]
    assert row['plan'] == case.world.refof('P0') and row['half_width'] == r(1, 2) and row['plan_state'] == 'captured'
    assert row['plan_claim'] is not None


def test_fx1_applicability_all_supported(selected):
    case, files = selected
    a = load(files, 'applicability.json')
    assert a['use_disposition'] == 'use_permitted'
    assert len(a['claims']) == 6
    assert {c['governing_state'] for c in a['claims']} == {'supported'}
    assert {c['declaration_state'] for c in a['claims']} == {'true'}
    assert a['unbound'] == {'claims': [], 'declarations': [], 'evidence_items': [], 'reviews': []}


def test_fx1_closure_roots_and_members(selected):
    case, files = selected
    c = load(files, 'closure.json')
    assert c['roots'] == {'request': {'kind': 'ct.request.v1', 'sha256': case.request_pin},
                          'evaluation_authority': {'kind': 'ct.authority.v1', 'sha256': case.authority_pin},
                          'retained_selection': None}
    digests = {m['sha256'] for m in c['members']}
    assert {case.request_pin, case.authority_pin} <= digests
    assert digests == set(case.objects) | {case.request_pin}


def test_fx1_verify_and_replay(selected):
    case, files = selected
    report = run_verify(case, files)
    assert report == {'operation': 'checked-selection-verify', 'bundle_commitment': sha(files['manifest.json']),
                      'derivation_checked': True, 'applicability_policy_checked': True,
                      'downstream_result_not_replayed': True}
    again = run_replay(case, files)
    for name in ('closure.json', 'derivation.json', 'applicability.json', 'result.json', 'trace.json'):
        assert again[name] == files[name]
    inv = load(again, 'invocation.json')
    assert inv['operation'] == 'checked-selection-replay'
    assert inv['replay_of'] == {'manifest_sha256': sha(files['manifest.json'])}


def test_un1_reassessment(reassessed):
    case, prior, files = reassessed
    res = load(files, 'result.json')
    h1, h2 = case.world.refof('H1'), case.world.refof('H2')
    assert res['interval'] == {'lo': r(119, 2), 'hi': r(121, 2)} and res['contained'] is True
    assert [b['outcome'] for b in res['branches']] == ['high']
    status = {h['hypothesis']['sha256']: h['status'] for h in res['hypotheses']}
    assert status == {h1['sha256']: 'compatible_under_declared_model', h2['sha256']: 'conditionally_incompatible'}
    assert res['disposition'] == 'one_compatible'
    assert res['ranking'] == 'not_reassessed' and res['adoption'] == 'derived_not_adopted'
    assert res['selection_basis'] == 'inherited' and res['plan_changed'] is False
    assert res['original_plan_executed'] is True and res['former_plan'] is None
    assert res['executed_plan'] == case.world.refof('P0')
    assert res['prior_selection'] == case.request['prior_selection']['selection']


def test_un1_closure_roots_and_prior_carriage(reassessed):
    case, prior, files = reassessed
    c = load(files, 'closure.json')
    roots = c['roots']
    assert roots['request']['sha256'] == case.request_pin
    assert roots['evaluation_authority']['sha256'] == case.authority_pin
    digests = {m['sha256']: m['kind'] for m in c['members']}
    d = json.loads(__import__('base64').b64decode(
        [m for m in c['members'] if m['sha256'] == roots['retained_selection']['sha256']][0]['data']))
    assert d['prior_manifest']['sha256'] == sha(prior['manifest.json'])
    assert d['prior_closure']['sha256'] == sha(prior['closure.json'])
    prior_members = {m['sha256'] for m in json.loads(prior['closure.json'])['members']}
    assert {m['sha256'] for m in d['prior_closure']['members']} == prior_members
    assert prior_members <= set(digests)
    for name in ('manifest.json', 'invocation.json', 'result.json', 'derivation.json', 'applicability.json',
                 'trace.json', 'build.json', 'policy.json'):
        assert sha(prior[name]) in digests          # carried prior records
    assert sha(prior['closure.json']) not in digests  # rebuilt, not carried
    assert 'ct.adoption.v1' not in digests.values() and 'ct.closure.v1' not in digests.values()


def test_un1_verify_standalone_and_replay(reassessed):
    case, prior, files = reassessed
    report = run_verify(case, files)
    assert report['operation'] == 'checked-reassessment-verify' and report['prior_material_checked'] is True
    again = run_replay(case, files)
    assert again['result.json'] == files['result.json']
    assert load(again, 'invocation.json')['operation'] == 'checked-reassessment-replay'
