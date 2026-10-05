"""v4 successor obligations (CONTRACT §12): amended-contract evidence.

Every case here is new or amended relative to the v3 matrix; original-matrix
evidence lives in the other modules. Build is the labelled TestDoubleBuild.
"""
import json
import pytest
from applications.bounded_decision_workflow.checked_contracts import (EDITION_LIMITS, T1, T2, CheckedRefusal,
                                                                      canonical_bytes, sha)
from tests.checked_temperature.fixtures import (IND_INST, PROFILE, WIDE, co1, code_evidence, fx1, load, prov, r,
                                                rehash_bundle, run_reassessment, run_replay, run_selection,
                                                run_verify, support_graph)


@pytest.fixture(scope='module')
def prior():
    base = fx1()
    return base, run_selection(base)


def refusal(fn, *a, **k):
    with pytest.raises(CheckedRefusal) as e:
        fn(*a, **k)
    return e.value


# ---- §12.1 policy identity
def test_policy_identity_v4_label_only():
    e = refusal(run_selection, fx1(policy_edit=lambda p: p.update(edition='ct.policy-edition.v3')))
    assert e.code == 'POLICY_EDITION_MISMATCH'
    e = refusal(run_selection, fx1(policy_edit=lambda p: p.update(edition='ct.policy-edition.v2')))
    assert e.code == 'POLICY_EDITION_MISMATCH'   # Gate 1 label workaround removed


# ---- §12.3 result evidence (W20)
def test_re1_value_distinct_result_evidence(prior):
    base, files = prior
    case = co1(files, base)
    out = run_reassessment(case, files)
    ev = case.request['result']['acquisition']['public_evidence']
    assert ev != case.world.refof('evidence')   # not the baseline evidence
    assert load(out, 'result.json')['disposition'] == 'one_compatible'
    assert run_verify(case, out)['prior_material_checked'] is True
    assert run_replay(case, out)['result.json'] == out['result.json']


@pytest.mark.parametrize('kw,where', [
    (dict(scalar='60.2', evidence_value='60'), '/value'),                     # RE2
    (dict(evidence='baseline'), '/baseline_reuse'),                           # RE3
    (dict(evidence=lambda w: code_evidence(w, instrument=IND_INST)), '/kind'),  # RE5
], ids=['RE2-value', 'RE3-baseline-reuse', 'RE5-code-evidence-for-T1'])
def test_t1_result_evidence_twins(prior, kw, where):
    base, files = prior
    e = refusal(run_reassessment, co1(files, base, **kw), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', '/result/acquisition/public_evidence' + where)


def test_re4_consistent_instrument_substitution():
    other = 'inst_' + 'd' * 32
    base = fx1(plan_instrument=other)
    files = run_selection(base)
    e = refusal(run_reassessment, co1(files, base), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', '/result/acquisition/public_evidence/instrument')


def test_re6_t2_code_evidence_positive(prior):
    base, files = prior
    case = co1(files, base, procedure=T2, code='heater_off')
    out = run_reassessment(case, files)
    assert load(out, 'result.json')['disposition'] == 'multiple_compatible'
    assert run_verify(case, out)['prior_material_checked'] is True
    assert run_replay(case, out)['result.json'] == out['result.json']


@pytest.mark.parametrize('ev,where', [
    (lambda w: code_evidence(w, code='heater_on'), '/value'),                              # RE7
    (lambda w: code_evidence(w, instrument='inst_' + 'e' * 32), '/instrument'),            # RE8
    (lambda w: code_evidence(w, observed_at='2026-10-05T10:00:00Z'), '/acquisition'),      # RE9
    (lambda w: w.refof('evidence'), '/kind'),                                              # RE10
], ids=['RE7-code', 'RE8-instrument', 'RE9-window', 'RE10-temperature-for-T2'])
def test_t2_result_evidence_twins(prior, ev, where):
    base, files = prior
    e = refusal(run_reassessment, co1(files, base, procedure=T2, code='heater_off', evidence=ev), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', '/result/acquisition/public_evidence' + where)


# ---- §12.4 applicability scope (W21)
def test_ap1_reassessment_qualifies_only_the_executed_procedure(prior):
    base, files = prior
    case = co1(files, base)
    app = load(run_reassessment(case, files), 'applicability.json')
    assert {c['procedure_edition'] for c in app['claims']} == {T1} and len(app['claims']) == 4
    sel = load(files, 'applicability.json')   # selection still requires the whole nominated set
    assert {c['procedure_edition'] for c in sel['claims']} == {T1, T2} and len(sel['claims']) == 6


# ---- §12.5 encoded carriage (W22)
def test_ec1_authored_strings_stay_limited_while_base64_payloads_are_designated():
    tight = lambda p: p['limits'].update(string_bytes=1500)

    def long_rationale(m, w):
        h1 = dict(w.value('H1'), rationale='r' * 2000)   # schema maxLength 2048
        m['hypotheses'][0]['explanation'] = w.replace('H1', h1)
    e = refusal(run_selection, fx1(policy_edit=tight, model_edit=long_rationale))
    assert e.code == 'RESOURCE_LIMIT_EXCEEDED' and e.target.startswith('/captured_limits/')
    base = fx1(policy_edit=tight)   # same captured limit: base64 data (> 100 KB strings) still carried
    files = run_selection(base)
    assert max(len(m['data']) for m in load(files, 'closure.json')['members']) > 1500
    assert run_verify(base, files)['derivation_checked'] is True


def test_ec2_non_data_string_in_closure_is_limited(prior):
    base, files = prior
    closure = json.loads(files['closure.json'])
    assert max(len(m['data']) for m in closure['members']) > EDITION_LIMITS['string_bytes']   # designated field
    closure['members'][0]['kind'] = 'k' * (EDITION_LIMITS['string_bytes'] + 1)
    mutated = rehash_bundle(dict(files, **{'closure.json': canonical_bytes(closure)}))
    e = refusal(run_verify, base, mutated)
    assert (e.code, e.target) == ('RESOURCE_LIMIT_EXCEEDED', '/bundle/closure.json')


# ---- §12.6 withheld selections (W23)
@pytest.fixture(scope='module')
def withheld():
    base = fx1(phase_kw={'omit': ('reference_calibration',)})
    return base, run_selection(base)


def test_wd1_withheld_selection_is_self_contained(withheld):
    base, files = withheld
    res, app = load(files, 'result.json'), load(files, 'applicability.json')
    assert res['withheld_reasons'] == ['applicability_blocked']
    unsupplied = [c['claim'] for c in app['claims'] if c['declaration_state'] == 'missing']
    assert unsupplied and unsupplied[0]['sha256'] not in base.objects   # derived core, not a closure member
    assert run_verify(base, files)['derivation_checked'] is True
    assert run_replay(base, files)['result.json'] == files['result.json']


def test_wd2_reassessment_over_withheld_prior(withheld):
    base, files = withheld
    case = co1(files, base)
    out = run_reassessment(case, files)
    assert run_verify(case, out)['prior_material_checked'] is True


# ---- §12.7 evaluation authority validity (W24)
def test_av1_selection_authority_window_excludes_as_of():
    e = refusal(run_selection, fx1(auth_valid={'from': '2026-10-01T00:00:00Z', 'to': '2026-10-03T00:00:00Z'}))
    assert (e.code, e.target) == ('AUTHORITY_SCOPE_MISMATCH', '/evaluation_authority/valid')


def test_av3_closed_window_boundary_is_admitted():
    assert run_selection(fx1(auth_valid={'from': '2026-10-04T12:00:00Z', 'to': '2026-10-04T12:00:00Z'}))


def test_av2_reassessment_authority_window_excludes_acquisition_end(prior):
    base, files = prior

    def mutate(name, value, w):
        if name == 'A':
            value['valid'] = {'from': '2026-10-01T00:00:00Z', 'to': '2026-10-05T09:04:59Z'}
    e = refusal(run_reassessment, co1(files, base, mutate=mutate), files)
    assert (e.code, e.target) == ('AUTHORITY_SCOPE_MISMATCH', '/evaluation_authority/valid')


# ---- §12.8 cached derivation (W25; IN1)
def test_cd1_cd2_cd3_cached_derivation(prior):
    from applications.bounded_decision_workflow import checked_runtime as rt
    base, files = prior

    def run(cache):
        return rt.evaluate_selection(request_wire=base.request_wire, objects=base.objects,
                                     request_pin=base.request_pin, authority_pin=base.authority_pin,
                                     build=base.world.build, cached_derivation=cache)
    assert run(files['derivation.json'])['derivation.json'] == files['derivation.json']   # CD1
    d = json.loads(files['derivation.json'])
    d['predictions'][2]['interval']['hi'] = r(561, 10)
    e = refusal(run, canonical_bytes(d))                                                   # CD2 / IN1
    assert (e.code, e.stage) == ('CACHED_DERIVATION_MISMATCH', 7)
    e = refusal(run, files['derivation.json'] + b' ')                                     # CD3
    assert e.code == 'SCHEMA_INVALID'


def test_cached_derivation_on_reassessment(prior):
    base, files = prior
    case = co1(files, base)
    out = run_reassessment(case, files)
    from applications.bounded_decision_workflow import checked_runtime as rt
    d = json.loads(out['derivation.json'])
    d['cells'][0]['relation'] = 'exclude' if d['cells'][0]['relation'] == 'permit' else 'permit'
    with pytest.raises(CheckedRefusal) as e:
        rt.evaluate_reassessment(request_wire=case.request_wire, objects=case.objects, prior_files=files,
                                 request_pin=case.request_pin, authority_pin=case.authority_pin,
                                 build=case.world.build, cached_derivation=canonical_bytes(d))
    assert e.value.code == 'CACHED_DERIVATION_MISMATCH'


# ---- §12.9 captured limits (W26)
@pytest.mark.parametrize('limit,value,target', [
    ('object_bytes', 80000, '/captured_limits/object_bytes/'),          # LM1 (evidence is 86,310 B)
    ('string_bytes', 40, '/captured_limits/'),                         # LM2
    ('json_depth', 10, '/captured_limits/'),                           # LM3 (evidence depth 16)
    ('json_nodes', 1000, '/captured_limits/'),                         # LM4 (evidence 2,727 nodes)
    ('integer_digits', 2, '/captured_limits/'),                        # LM5 (baseline 601/10)
    ('trace_entries', 7, '/trace_entries'),                            # LM6 (trace has 8)
    ('rational_operations', 33, '/rational_operations'),               # LM7 (FX1 counts exactly 34)
], ids=['LM1', 'LM2', 'LM3', 'LM4', 'LM5', 'LM6', 'LM7'])
def test_captured_limits_are_enforced(limit, value, target):
    e = refusal(run_selection, fx1(policy_edit=lambda p: p['limits'].update({limit: value})))
    assert e.code == 'RESOURCE_LIMIT_EXCEEDED' and e.target.startswith(target)


def test_lm6_lm7_exact_accounting_boundaries():
    files = run_selection(fx1(policy_edit=lambda p: p['limits'].update(trace_entries=8, rational_operations=34)))
    assert len(load(files, 'trace.json')['entries']) == 8


def test_f12c_captured_review_count_is_a_resource_refusal():
    def extra(w):
        out = []
        for k in sorted(k for k in w.h if k.startswith('review-selection-'))[:5]:
            v = w.value(k)
            out.append(w.put({**v, 'id': v['id'] + '-dup'}))
        return {'reviews': out}
    e = refusal(run_selection, fx1(extra_graph=extra, policy_edit=lambda p: p['limits'].update(reviews=10)))
    assert (e.code, e.stage, e.target) == ('RESOURCE_LIMIT_EXCEEDED', 4, '/request/reviews')


# ---- v4 review fixes
@pytest.mark.parametrize('limit,value', [('hypotheses', 1), ('procedures', 1), ('outcomes_per_procedure', 2),
                                         ('fractional_digits', 1)])
def test_captured_count_and_format_limits(limit, value):
    # b_ref hi 1/100 is edition-valid (6 digits) but exceeds a captured 1 fractional digit.
    e = refusal(run_selection, fx1(b_ref=((0, 1), (1, 100)),
                                   policy_edit=lambda p: p['limits'].update({limit: value})))
    assert (e.code, e.stage) == ('RESOURCE_LIMIT_EXCEEDED', 4) and e.target.startswith('/captured_limits/' + limit)


def test_captured_derivation_cells_limit():
    e = refusal(run_selection, fx1(policy_edit=lambda p: p['limits'].update(derivation_cells=9)))
    assert (e.code, e.target) == ('RESOURCE_LIMIT_EXCEEDED', '/derivation_cells')


def test_captured_successor_chain_limit():
    def extra(w):
        k = [k for k in w.h if k.startswith('decl-selection-T1-reference_calibration')][0]
        rev2 = dict(w.value(k), revision=2, predecessor=w.refof(k))
        return {'declarations': [w.put(rev2)]}
    assert run_selection(fx1(extra_graph=extra))
    e = refusal(run_selection, fx1(extra_graph=extra, policy_edit=lambda p: p['limits'].update(successor_chain=1)))
    assert e.code == 'RESOURCE_LIMIT_EXCEEDED' and e.target.startswith('/captured_limits/successor_chain')


def test_captured_retained_selection_bytes_limit(prior):
    base, files = prior
    case = co1(files, base)
    policy = case.world.value('policy')
    # The reassessment request names the same captured policy; a tighter copy is not allowed
    # for the same request, so the descriptor limit is exercised through a fresh world.
    tight = fx1(policy_edit=lambda p: p['limits'].update(retained_selection_bytes=1000))
    tfiles = run_selection(tight)
    e = refusal(run_reassessment, co1(tfiles, tight), tfiles)
    assert e.code == 'RESOURCE_LIMIT_EXCEEDED' and e.target.startswith('/captured_limits/retained_selection_bytes')


def test_cached_derivation_must_be_an_object(prior):
    from applications.bounded_decision_workflow import checked_runtime as rt
    base, files = prior
    with pytest.raises(CheckedRefusal) as e:
        rt.evaluate_selection(request_wire=base.request_wire, objects=base.objects, request_pin=base.request_pin,
                              authority_pin=base.authority_pin, build=base.world.build, cached_derivation=b'[]')
    assert e.value.code == 'SCHEMA_INVALID'


def test_result_evidence_reusing_the_baseline_occurrence(prior):
    from tests.checked_temperature.result_evidence import result_evidence_bytes
    base, files = prior
    ev = lambda w: w.put(json.loads(result_evidence_bytes('60.1', reuse_occurrence=True)))
    case = co1(files, base, scalar='60.1', evidence=ev)
    assert case.request['result']['acquisition']['public_evidence'] != case.world.refof('evidence')
    e = refusal(run_reassessment, case, files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', '/result/acquisition/public_evidence/occurrence')


def test_result_evidence_with_other_anchors(prior):
    from tests.checked_temperature.result_evidence import result_evidence_bytes
    base, files = prior

    def ev(w):
        e = json.loads(result_evidence_bytes('60'))
        e['binding']['subject_entity_anchor_id'] = 'ent_' + '8' * 32
        return w.put(e)
    e = refusal(run_reassessment, co1(files, base, evidence=ev), files)
    assert (e.code, e.target) == ('RESULT_EVIDENCE_MISMATCH', '/result/acquisition/public_evidence/anchors')


def test_result_evidence_assertion_context_is_the_models(prior):
    from tests.checked_temperature.result_evidence import result_evidence_bytes
    base, files = prior

    def ev(w):
        e = json.loads(result_evidence_bytes('60'))
        e['question']['assertion_context'] = {'kind': 'lifecycle_view', 'view': 'as_designed'}
        return w.put(e)
    e = refusal(run_reassessment, co1(files, base, evidence=ev), files)
    assert e.code == 'SCHEMA_INVALID' and e.target == '/nm.evidence.v1'   # legacy join refuses the context
