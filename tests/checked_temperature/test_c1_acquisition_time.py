"""Amendment C1: T1 acquisition-time binding over a coherent later evidence chain.

Declared-time consistency only; the later chain is synthetic (tests/checked_temperature/
later_chain.py). Build is the labelled TestDoubleBuild.
"""
import json
import re
from datetime import datetime
import pytest
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal
from tests.checked_temperature.fixtures import co1, fx1, load, run_reassessment, run_replay, run_selection, run_verify
from tests.checked_temperature.later_chain import later_evidence_bytes, occurrence_finished_at
from tests.checked_temperature.result_evidence import result_evidence_bytes

WINDOW = '/result/acquisition/public_evidence/acquisition_window'


@pytest.fixture(scope='module')
def prior():
    base = fx1()
    return base, run_selection(base)


def refusal(fn, *a, **k):
    with pytest.raises(CheckedRefusal) as e:
        fn(*a, **k)
    return e.value


def test_later_chain_is_coherent_and_later():
    e = json.loads(later_evidence_bytes('60'))
    finished = occurrence_finished_at(later_evidence_bytes('60'))
    assert finished.startswith('2026-10-05T09:01:') and e['question']['as_of'] == '2026-10-05T09:05:00Z'
    baseline = json.loads(result_evidence_bytes('60'))
    ids = lambda v: set(re.findall(r'"record_id": ?"([a-z]{3}_[0-9a-f]{64})"', json.dumps(v)))
    old_assertions, new_assertions = ids(baseline), ids(e)
    assert new_assertions - old_assertions   # rebuilt binding/interpretation records, new hashes
    assert e['snapshot']['state']['material']['revision'] == baseline['snapshot']['state']['material']['revision']


def test_tc1_later_result_completes_and_verifies_standalone(prior):
    base, files = prior
    case = co1(files, base)
    out = run_reassessment(case, files)
    assert load(out, 'result.json')['disposition'] == 'one_compatible'
    assert run_verify(case, out)['prior_material_checked'] is True
    assert run_replay(case, out)['result.json'] == out['result.json']


@pytest.mark.parametrize('edge', ['started', 'ended'], ids=['TC2a-start', 'TC2b-end'])
def test_tc2_closed_window_boundaries(prior, edge):
    base, files = prior
    finished = occurrence_finished_at(later_evidence_bytes('60'))

    def mutate(name, value, w):
        if name == 'R':
            value['result']['acquisition'][edge] = finished
    assert run_reassessment(co1(files, base, mutate=mutate), files)


def test_tc2_one_second_outside_refuses(prior):
    base, files = prior
    finished = datetime.fromisoformat(occurrence_finished_at(later_evidence_bytes('60')))

    def mutate(name, value, w):
        if name == 'R':
            value['result']['acquisition']['ended'] = (finished.replace(second=finished.second - 1)
                                                       ).strftime('%Y-%m-%dT%H:%M:%SZ')
    e = refusal(run_reassessment, co1(files, base, mutate=mutate), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', WINDOW)


def test_tc3_retained_instant_evidence_outside_the_window(prior):
    base, files = prior
    ev = lambda w: w.put(json.loads(result_evidence_bytes('60')))
    e = refusal(run_reassessment, co1(files, base, evidence=ev), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', WINDOW)


def test_tc4_acquisition_before_model_baseline(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'R':
            value['result']['acquisition']['started'] = '2026-08-07T20:29:59Z'
    e = refusal(run_reassessment, co1(files, base, mutate=mutate), files)
    assert (e.code, e.stage, e.target) == ('SCHEMA_INVALID', 4, '/result/acquisition/started_before_baseline')


def _shift_all(evidence, delta):
    def shift(x):
        if isinstance(x, dict):
            return {k: shift(v) for k, v in x.items()}
        if isinstance(x, list):
            return [shift(v) for v in x]
        if isinstance(x, str) and re.fullmatch(r'\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z', x):
            return (datetime.fromisoformat(x) + delta).strftime('%Y-%m-%dT%H:%M:%SZ')
        return x
    return shift(evidence)


def test_tc5a_naive_shift_of_every_timestamp_refuses(prior):
    base, files = prior
    e0 = json.loads(result_evidence_bytes('60'))
    delta = datetime.fromisoformat('2026-10-05T09:01:06Z') - datetime.fromisoformat(
        occurrence_finished_at(result_evidence_bytes('60')))
    shifted = dict(_shift_all(e0, delta), id='E-naive-shift')
    e = refusal(run_reassessment, co1(files, base, evidence=lambda w: w.put(shifted)), files)
    assert e.code in ('SCHEMA_INVALID', 'RESULT_EVIDENCE_MISMATCH')
    assert (e.code, e.target) == ('SCHEMA_INVALID', '/nm.evidence.v1')   # the owning validator rejects it


def test_tc5b_substituting_only_finished_at_refuses(prior):
    """Amendment C2: now an explicit refusal. Historical outcome retained: under C1 alone this
    forged chain was ACCEPTED (strict xfail in launches 13-15; witnesses-c1.json `observed`).
    received_at stays outside the window, so C2.1 refuses it."""
    base, files = prior
    e0 = json.loads(result_evidence_bytes('60'))
    old = occurrence_finished_at(result_evidence_bytes('60'))
    forged = json.loads(json.dumps(e0).replace('"finished_at":"%s"' % old, '"finished_at":"2026-10-05T09:01:06Z"')
                        .replace('"finished_at": "%s"' % old, '"finished_at": "2026-10-05T09:01:06Z"'))
    forged['id'] = 'E-finished-substituted'
    assert occurrence_finished_at(json.dumps(forged)) == '2026-10-05T09:01:06Z'
    e = refusal(run_reassessment, co1(files, base, evidence=lambda w: w.put(forged)), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', WINDOW)   # C2.1: received_at outside


def test_tc6_baseline_evidence_and_occurrence_reuse_remain_refused(prior):
    base, files = prior
    e = refusal(run_reassessment, co1(files, base, evidence='baseline'), files)
    assert e.target.endswith('/baseline_reuse')
    reused = lambda w: w.put(json.loads(result_evidence_bytes('60.1', reuse_occurrence=True)))
    e = refusal(run_reassessment, co1(files, base, scalar='60.1', evidence=reused), files)
    assert e.target.endswith('/occurrence')


def _substitute(evidence_bytes, fields, new):
    e = json.loads(evidence_bytes)
    occ = json.loads(evidence_bytes)
    text = json.dumps(e)
    for field in fields:
        b = e['binding']
        old = e['snapshot']['constraint_evaluations'][b['constraint_evaluation_index']]['semantic_compatibility'][
            'candidates'][b['semantic_candidate_index']]['value_candidate']['state_candidate']['bound']['observed'][
            'occurrence'][field]
        text = text.replace('"%s": "%s"' % (field, old), '"%s": "%s"' % (field, new))
    return json.loads(text)


def test_tc5c_probe_received_and_finished_substitution(prior):
    """Probe for the owner choice: substituting received_at (the governed effective wall time)
    together with finished_at; the owning validator is expected to reject the inconsistency."""
    base, files = prior
    forged = _substitute(result_evidence_bytes('60'), ('received_at', 'finished_at'), '2026-10-05T09:01:06Z')
    forged['id'] = 'E-received-finished-substituted'
    e = refusal(run_reassessment, co1(files, base, evidence=lambda w: w.put(forged)), files)
    assert (e.code, e.target) == ('SCHEMA_INVALID', '/nm.evidence.v1')
