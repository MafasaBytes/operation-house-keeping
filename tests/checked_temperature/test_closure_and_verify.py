"""Closure roots, prior-material carriage and verify/replay witnesses.

Bundle mutations are harness-style: records are edited, digests recomputed
and the manifest rehashed, while the external pins stay those of the original
request and evaluation authority.
"""
import base64
import json
import pytest
from applications.bounded_decision_workflow.checked_contracts import CheckedRefusal, canonical_bytes, sha
from tests.checked_temperature.fixtures import (TestDoubleBuild, co1, fx1, load, member, prov, PROFILE, WIDE,
                                                rehash_bundle, run_reassessment, run_replay, run_selection,
                                                run_verify)


@pytest.fixture(scope='module')
def bundles():
    base = fx1()
    sel = run_selection(base)
    case = co1(sel, base)
    return base, sel, case, run_reassessment(case, sel)


def refusal(fn, *a, **k):
    with pytest.raises(CheckedRefusal) as e:
        fn(*a, **k)
    return e.value


def edit_closure(files, fn):
    closure = json.loads(files['closure.json'])
    members = {m['sha256']: m for m in closure['members']}
    fn(closure, members)
    closure['members'] = sorted(members.values(), key=lambda m: (m['kind'], m['sha256']))
    out = dict(files)
    out['closure.json'] = canonical_bytes(closure)
    return rehash_bundle(out)


def decode(m):
    return json.loads(base64.b64decode(m['data']))


def replace_descriptor(closure, members, edit):
    old = closure['roots']['retained_selection']['sha256']
    d = decode(members.pop(old))
    edit(d)
    data = canonical_bytes(d)
    members[sha(data)] = member('ct.retained-selection.v1', data)
    closure['roots']['retained_selection'] = {'kind': 'ct.retained-selection.v1', 'sha256': sha(data)}


def stray_review(case):
    v = {'schema': 'ct.evidence-review.v1', 'profile': PROFILE, 'id': 'stray', 'revision': 1, 'predecessor': None,
         'provenance': prov('local_evidence_reviewer'), 'item': case.request['evidence_items'][0],
         'claim': case.request['claims'][0], 'completion': 'completed', 'relevance': 'relevant',
         'relation': 'opposition', 'rationale': 'stray', 'covers': WIDE}
    return canonical_bytes(v)


def test_cl3_unrelated_object_laundered_through_the_descriptor(bundles):
    base, sel, case, rea = bundles
    data = stray_review(case)

    def fn(closure, members):
        members[sha(data)] = member('ct.evidence-review.v1', data)
        replace_descriptor(closure, members, lambda d: d['prior_closure']['members'].__setitem__(
            slice(None), sorted(d['prior_closure']['members'] + [{'kind': 'ct.evidence-review.v1',
                                                                 'sha256': sha(data)}],
                                key=lambda x: (x['kind'], x['sha256']))))
    e = refusal(run_verify, case, edit_closure(rea, fn))
    assert (e.code, e.target) == ('PRIOR_BUNDLE_MISMATCH', '/retained_selection/prior_closure/rebuild')


def test_cl4_missing_evaluation_authority_root(bundles):
    base, sel, case, rea = bundles
    e = refusal(run_verify, case, edit_closure(rea, lambda c, m: m.pop(case.authority_pin)))
    assert e.code == 'REFERENCE_MISSING' and case.authority_pin in e.target


def _substitute_trace(closure, members):
    d = decode(members[closure['roots']['retained_selection']['sha256']])
    trace = decode(members.pop(d['trace']['sha256']))
    trace['entries'][-1]['outcome'] = 'substituted'
    data = canonical_bytes(trace)
    members[sha(data)] = member('ct.trace.v1', data)
    replace_descriptor(closure, members, lambda d: d.update(trace={'kind': 'ct.trace.v1', 'sha256': sha(data)}))
    return data


def test_cl5_substituted_prior_trace(bundles):
    base, sel, case, rea = bundles
    e = refusal(run_verify, case, edit_closure(rea, lambda c, m: _substitute_trace(c, m)))
    assert (e.code, e.target) == ('PRIOR_BUNDLE_MISMATCH', '/retained_selection/trace.json')


def test_cl6_substituted_prior_manifest(bundles):
    base, sel, case, rea = bundles

    def fn(closure, members):
        trace = _substitute_trace(closure, members)
        d = decode(members[closure['roots']['retained_selection']['sha256']])
        manifest = decode(members[d['prior_manifest']['sha256']])
        for f in manifest['files']:
            if f['name'] == 'trace.json':
                f['sha256'], f['bytes'] = sha(trace), len(trace)
        data = canonical_bytes(manifest)
        members[sha(data)] = member('ct.bundle-manifest.v1', data)   # original manifest kept
        replace_descriptor(closure, members, lambda d: d.update(
            prior_manifest={'kind': 'ct.bundle-manifest.v1', 'sha256': sha(data)}))
    e = refusal(run_verify, case, edit_closure(rea, fn))
    assert (e.code, e.target) == ('PRIOR_BUNDLE_MISMATCH', '/retained_selection/prior_manifest')


def test_cl7_forged_evaluation_root_fails_the_external_pin(bundles):
    base, sel, case, rea = bundles
    a2 = canonical_bytes(dict(case.auth, id='auth-eval-R-forged'))
    a2ref = {'kind': 'ct.authority.v1', 'sha256': sha(a2)}

    def fn(closure, members):
        members.pop(case.authority_pin)
        members[sha(a2)] = member('ct.authority.v1', a2)
        closure['roots']['evaluation_authority'] = a2ref
    mutated = edit_closure(rea, fn)
    inv = json.loads(mutated['invocation.json'])
    inv['authority'] = a2ref
    mutated = rehash_bundle(dict(mutated, **{'invocation.json': canonical_bytes(inv)}))
    e = refusal(run_verify, case, mutated)
    assert (e.code, e.stage) == ('AUTHORITY_PIN_MISMATCH', 5)


def test_cl9_prior_closure_with_unreachable_member(bundles):
    base, sel, case, rea = bundles
    data = stray_review(case)
    bad_prior = edit_closure(sel, lambda c, m: m.__setitem__(sha(data), member('ct.evidence-review.v1', data)))
    twin = co1(bad_prior, base)
    e = refusal(run_reassessment, twin, bad_prior)
    assert e.code == 'PRIOR_BUNDLE_MISMATCH' and e.target.endswith(sha(data))   # unreachable stray named


def test_in2_altered_derivation_fails_fresh_comparison(bundles):
    base, sel, case, rea = bundles
    d = json.loads(sel['derivation.json'])
    d['predictions'][1]['interval'] = {'lo': {'numerator': '451', 'denominator': '10'},
                                       'hi': {'numerator': '561', 'denominator': '10'}}
    e = refusal(run_verify, base, rehash_bundle(dict(sel, **{'derivation.json': canonical_bytes(d)})))
    assert e.code == 'DERIVATION_MISMATCH'


def _altered_score(sel):
    s = json.loads(sel['result.json'])
    s['scores'][0]['worst_survivors'] = 2
    return rehash_bundle(dict(sel, **{'result.json': canonical_bytes(s)}))


def test_in3_verify_does_not_replay_downstream(bundles):
    base, sel, case, rea = bundles
    report = run_verify(base, _altered_score(sel))
    assert report['downstream_result_not_replayed'] is True and report['derivation_checked'] is True


def test_in4_replay_detects_altered_downstream_score(bundles):
    base, sel, case, rea = bundles
    assert refusal(run_replay, base, _altered_score(sel)).code == 'DOWNSTREAM_REPLAY_MISMATCH'


def test_in5_misleading_score_metadata_refuses_verify(bundles):
    base, sel, case, rea = bundles
    s = json.loads(sel['result.json'])
    s['post_measurement_elimination_guaranteed'] = True
    e = refusal(run_verify, base, rehash_bundle(dict(sel, **{'result.json': canonical_bytes(s)})))
    assert e.code == 'SCORE_METADATA_INVALID'


def test_unrehashed_file_edit_is_a_digest_mismatch(bundles):
    base, sel, case, rea = bundles
    e = refusal(run_verify, base, dict(sel, **{'trace.json': sel['trace.json'] + b' '}))
    assert e.code == 'REFERENCE_DIGEST_MISMATCH'


def test_verify_with_wrong_external_request_pin(bundles):
    base, sel, case, rea = bundles
    e = refusal(run_verify, case, rea, request_pin='0' * 64)
    assert e.code == 'REQUEST_PIN_MISMATCH'


def test_replay_requires_the_exact_recorded_build():
    other = TestDoubleBuild(marker='1')
    base = fx1(policy_edit=lambda p: p.update(permitted_builds=sorted([TestDoubleBuild().digest, other.digest])))
    sel = run_selection(base)
    assert run_verify(base, sel, build=other)['derivation_checked'] is True   # permitted current build
    assert refusal(run_replay, base, sel, build=other).code == 'HISTORICAL_BUILD_UNAVAILABLE'


def test_altered_applicability_fails_fresh_comparison(bundles):
    base, sel, case, rea = bundles
    a = json.loads(sel['applicability.json'])
    a['claims'][0]['use_effect'] = 'conditional_unresolved'
    e = refusal(run_verify, base, rehash_bundle(dict(sel, **{'applicability.json': canonical_bytes(a)})))
    assert e.code == 'APPLICABILITY_MISMATCH'


def test_trace_target_outside_bundle_is_unresolvable(bundles):
    base, sel, case, rea = bundles
    t = json.loads(sel['trace.json'])
    t['entries'][0]['target'] = {'kind': 'ct.request.v1', 'sha256': '0' * 64}
    e = refusal(run_verify, base, rehash_bundle(dict(sel, **{'trace.json': canonical_bytes(t)})))
    assert (e.code, e.target) == ('REFERENCE_MISSING', '/bundle/trace.json/target')


def test_reassessment_only_kind_in_a_selection_closure_is_refused(bundles):
    base, sel, case, rea = bundles
    data = canonical_bytes(json.loads(rea['trace.json']))
    e = refusal(run_verify, base, edit_closure(sel, lambda c, m: m.__setitem__(sha(data), member('ct.trace.v1', data))))
    assert (e.code, e.target) == ('REFERENCE_KIND_MISMATCH', '/closure/' + sha(data))


def test_invocation_operation_must_match_bundle_kind(bundles):
    base, sel, case, rea = bundles
    inv = json.loads(sel['invocation.json'])
    inv['operation'] = 'checked-reassessment-evaluate'
    e = refusal(run_verify, base, rehash_bundle(dict(sel, **{'invocation.json': canonical_bytes(inv)})))
    assert (e.code, e.target) == ('SCHEMA_INVALID', '/invocation/operation')


def test_i1_mislabelled_closure_member_is_refused(bundles):
    base, sel, case, rea = bundles
    model = base.world.refof('model')['sha256']
    e = refusal(run_verify, base, edit_closure(sel, lambda c, m: m[model].update(kind='ct.policy.v1')))
    assert (e.code, e.target) == ('REFERENCE_KIND_MISMATCH', '/closure.json/members')


def test_i2_missing_descriptor_member(bundles):
    base, sel, case, rea = bundles
    e = refusal(run_verify, case, edit_closure(rea, lambda c, m: m.pop(c['roots']['retained_selection']['sha256'])))
    assert e.code == 'REFERENCE_MISSING'


def test_i5_carried_prior_selection_is_recomputed(bundles):
    base, sel, case, rea = bundles
    s = json.loads(sel['result.json'])
    s['scores'][0]['worst_survivors'] = 2
    forged = rehash_bundle(dict(sel, **{'result.json': canonical_bytes(s)}))
    twin = co1(forged, base)
    e = refusal(run_reassessment, twin, forged)
    assert (e.code, e.target) == ('PRIOR_BUNDLE_MISMATCH', '/retained_selection/selection_recomputed')


def test_i6_reassessment_plan_disclosure_is_mandatory_metadata(bundles):
    base, sel, case, rea = bundles
    res = json.loads(rea['result.json'])
    res['original_plan_executed'] = False
    e = refusal(run_verify, case, rehash_bundle(dict(rea, **{'result.json': canonical_bytes(res)})))
    assert (e.code, e.target) == ('SCORE_METADATA_INVALID', '/result/original_plan_executed')


def test_i6_selection_conditional_use_disclosure_is_mandatory_metadata(bundles):
    base, sel, case, rea = bundles
    s = json.loads(sel['result.json'])
    s['use_disposition'] = 'conditional_use_with_unresolved_conditions'
    e = refusal(run_verify, base, rehash_bundle(dict(sel, **{'result.json': canonical_bytes(s)})))
    assert (e.code, e.target) == ('SCORE_METADATA_INVALID', '/result/use_disposition')
