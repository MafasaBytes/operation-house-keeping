"""Legally formed adverse twins that reach their intended semantic checks.

Each twin is schema-valid, every affected digest and pin is recomputed, and
the expected refusal is the specific semantic code (not SCHEMA_INVALID).
"""
import pytest
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal, canonical_bytes, sha
from tests.checked_temperature.fixtures import (closure_with, co1, fx1, member, prov, PROFILE, WIDE, run_reassessment,
                                                run_selection, run_verify)


@pytest.fixture(scope='module')
def prior():
    base = fx1()
    return base, run_selection(base)


def refusal(fn, *a, **k):
    with pytest.raises(CheckedRefusal) as e:
        fn(*a, **k)
    return e.value


def test_eo4_execution_authority_targets_a_different_execution_target(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'E':   # E authorizes X2 (same as X except instrument), R keeps X
            x2 = dict(w.value('X'), id='xt-2', instrument_id='inst_' + 'c' * 32)
            value['target'] = w.put(x2, 'X2')
    case = co1(files, base, mutate=mutate)
    assert case.spec['E']['target'] != case.spec['R']['execution_target']
    e = refusal(run_reassessment, case, files)
    assert (e.code, e.stage) == ('AUTHORITY_TARGET_MISMATCH', 5)
    assert e.target == '/execution_authority/target'


def test_eo1_twin_control_completes(prior):
    base, files = prior
    out = run_reassessment(co1(files, base), files)
    assert sha(out['manifest.json'])


def test_cl8_unpinned_second_evaluation_authority_is_an_unrelated_object(prior):
    base, files = prior
    case = co1(files, base)
    a2 = dict(case.spec['A'], id='auth-eval-R-second')
    objects = dict(case.objects)
    objects[sha(canonical_bytes(a2))] = canonical_bytes(a2)
    e = refusal(run_reassessment, case, files, objects=objects)
    assert e.code == 'UNREFERENCED_MEMBER' and sha(canonical_bytes(a2)) in e.target


def test_in11_selection_unrelated_valid_object(prior):
    base, _ = prior
    stray = {'schema': 'ct.condition-declaration.v1', 'profile': PROFILE, 'id': 'stray', 'revision': 1,
             'predecessor': None, 'provenance': prov('local_condition_declarer'),
             'claim': {'kind': 'ct.claim.v1', 'sha256': '0' * 64}, 'state': 'true', 'rationale': '', 'covers': WIDE}
    objects = dict(base.objects)
    objects[sha(canonical_bytes(stray))] = canonical_bytes(stray)
    e = refusal(run_selection, base, objects=objects)
    assert e.code == 'UNREFERENCED_MEMBER'


def test_cl2_unrelated_member_added_to_retained_bundle_is_refused_by_verify(prior):
    base, files = prior
    case = co1(files, base)
    bundle = run_reassessment(case, files)
    stray = {'schema': 'ct.evidence-review.v1', 'profile': PROFILE, 'id': 'stray-review', 'revision': 1,
             'predecessor': None, 'provenance': prov('local_evidence_reviewer'),
             'item': case.request['evidence_items'][0], 'claim': case.request['claims'][0],
             'completion': 'completed', 'relevance': 'relevant', 'relation': 'opposition', 'rationale': 'stray',
             'covers': WIDE}
    mutated = closure_with(bundle, lambda c: c['members'].append(member('ct.evidence-review.v1',
                                                                        canonical_bytes(stray))))
    assert mutated['manifest.json'] != bundle['manifest.json']   # manifest rehashed; pins unchanged
    e = refusal(run_verify, case, mutated)
    assert e.code == 'UNREFERENCED_MEMBER'
    assert run_verify(case, bundle)['prior_material_checked'] is True   # untouched twin verifies
