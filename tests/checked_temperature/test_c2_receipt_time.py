"""Amendment C2: received_at and finished_at of the admitted occurrence both in the window.

Declared-time consistency only. Build is the labelled TestDoubleBuild. RC3b/RC4 use
validator-accepted evidence whose finished_at alone was moved (labelled; not a
coherently rebuilt chain) to obtain distinct receipt and completion instants.
"""
import json
import pytest
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal
from tests.checked_temperature.fixtures import co1, fx1, load, run_reassessment, run_selection
from tests.checked_temperature.later_chain import (later_evidence_bytes, occurrence_finished_at,
                                                   occurrence_received_at, with_finished_at)
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


def window(started=None, ended=None):
    def mutate(name, value, w):
        if name == 'R':
            if started:
                value['result']['acquisition']['started'] = started
            if ended:
                value['result']['acquisition']['ended'] = ended
    return mutate


def test_genuine_chain_receipt_equals_completion():
    e = later_evidence_bytes('60')
    assert occurrence_received_at(e) == occurrence_finished_at(e) == '2026-10-05T09:01:06Z'


def test_rc1_received_outside_finished_inside(prior):
    base, files = prior
    forged = with_finished_at(result_evidence_bytes('60'), '2026-10-05T09:01:06Z', 'rc1')
    assert occurrence_received_at(json.dumps(forged)).startswith('2026-08-07')
    e = refusal(run_reassessment, co1(files, base, evidence=lambda w: w.put(forged)), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', WINDOW)


def test_rc2_finished_outside_received_inside(prior):
    base, files = prior
    forged = with_finished_at(later_evidence_bytes('60'), '2026-10-05T09:06:00Z', 'rc2')   # ended is 09:05:00
    assert occurrence_received_at(json.dumps(forged)) == '2026-10-05T09:01:06Z'
    e = refusal(run_reassessment, co1(files, base, evidence=lambda w: w.put(forged)), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', WINDOW)


def test_rc3a_genuine_receipt_at_start_and_completion_at_end(prior):
    base, files = prior
    e = later_evidence_bytes('60')
    case = co1(files, base, mutate=window(occurrence_received_at(e), occurrence_finished_at(e)))
    assert load(run_reassessment(case, files), 'result.json')['disposition'] == 'one_compatible'


@pytest.fixture(scope='module')
def moved():
    return with_finished_at(later_evidence_bytes('60'), '2026-10-05T09:01:26Z', 'rc3')


def test_rc3b_distinct_receipt_at_start_completion_at_end(prior, moved):
    base, files = prior
    received, finished = occurrence_received_at(json.dumps(moved)), occurrence_finished_at(json.dumps(moved))
    assert received < finished
    case = co1(files, base, evidence=lambda w: w.put(moved), mutate=window(received, finished))
    assert load(run_reassessment(case, files), 'result.json')['disposition'] == 'one_compatible'


def test_rc4_start_at_completion_refuses_when_receipt_precedes_it(prior, moved):
    """Replaces the C1 TC2a expectation for evidence whose receipt precedes completion."""
    base, files = prior
    case = co1(files, base, evidence=lambda w: w.put(moved),
               mutate=window(started=occurrence_finished_at(json.dumps(moved))))
    e = refusal(run_reassessment, case, files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', WINDOW)
