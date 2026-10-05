"""Kind and issuer-role enforcement are semantic (stage 3), not schema annotations."""
import pytest
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal, canonical_bytes, validate
from tests.checked_temperature.fixtures import co1, fx1, run_reassessment, run_selection


@pytest.fixture(scope='module')
def prior():
    base = fx1()
    return base, run_selection(base)


def refusal(fn, *a, **k):
    with pytest.raises(CheckedRefusal) as e:
        fn(*a, **k)
    return e.value


def _target(kind_name):
    def mutate(name, value, w):
        if name == kind_name[0]:
            value['target'] = kind_name[1](w)
    return mutate


def test_annotations_alone_do_not_enforce_kind_or_role(prior):
    base, files = prior
    case = co1(files, base)
    bad = dict(case.spec['E'], target=case.request['model'])   # model ref where an execution target is required
    bad_role = dict(case.spec['E'], provenance=dict(case.spec['E']['provenance'], role='local_evaluation_issuer'))
    for record in (bad, bad_role):
        found = validate(record, 'ct.authority.v1')   # schema-valid: x-target / x-allowed-roles are annotations
        assert found.refs and found.roles


def test_eo2_execution_authority_targeting_a_request_kind(prior):
    base, files = prior
    case = co1(files, base, mutate=_target(('E', lambda w: w.refof('S'))))
    e = refusal(run_reassessment, case, files)
    assert (e.code, e.stage) == ('REFERENCE_KIND_MISMATCH', 3) and e.target.endswith('/target')


def test_eo3_evaluation_authority_targeting_an_execution_target(prior):
    base, files = prior
    case = co1(files, base, mutate=_target(('A', lambda w: w.refof('X'))))
    e = refusal(run_reassessment, case, files)
    assert (e.code, e.stage) == ('REFERENCE_KIND_MISMATCH', 3) and e.target.endswith('/target')


def test_execution_authority_issued_by_the_evaluation_role(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'E':
            value['provenance'] = dict(value['provenance'], role='local_evaluation_issuer')
    e = refusal(run_reassessment, co1(files, base, mutate=mutate), files)
    assert (e.code, e.stage) == ('ROLE_MISMATCH', 3) and e.target.endswith('/provenance/role')


def test_evaluation_authority_issued_by_the_execution_role(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'A':
            value['provenance'] = dict(value['provenance'], role='local_execution_issuer')
    e = refusal(run_reassessment, co1(files, base, mutate=mutate), files)
    assert e.code == 'ROLE_MISMATCH'


def test_declaration_issued_by_the_reviewer_role():
    case = fx1()
    w = case.world
    # Re-issue one declaration under a non-declarer role, rebuild the request and authority.
    from tests.checked_temperature.fixtures import Case, authority, selection_request
    import json
    decl_ref = case.request['declarations'][0]
    decl = json.loads(w.objects.pop(decl_ref['sha256']))
    decl['provenance']['role'] = 'local_evidence_reviewer'
    new_ref = w.put(decl)
    graph = {k: [new_ref if x == decl_ref else x for x in case.request[k]]
             for k in ('claims', 'declarations', 'evidence_items', 'reviews')}
    w.objects.pop(case.request_pin, None)
    w.objects.pop(case.authority_pin, None)
    request = selection_request(w, graph)
    rref = w.put(request)
    twin = Case(w, request, authority(purpose='evaluation', target=rref, phase='selection',
                                      procedures=['ct.procedure.T1.v1', 'ct.procedure.T2.v1']))
    e = refusal(run_selection, twin)
    assert e.code == 'ROLE_MISMATCH'
