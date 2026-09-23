"""Slice 2: real public reconstruction on synthetic retained evidence.

Internal graph fixtures do not assert executable binding; dedicated production
tests use capture and the real factory. Frozen expected outputs are never loaded.
"""
import pytest
import json

from applications.bounded_decision_workflow.reassessment_admission import admit
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError
from test_capture import structural, bound_internal, graph, replace, key, wire


def no_downstream(g):
    for name in ('interval_intersections', 'qualified_cells', 'source_contributions',
                 'mapped_cells', 'ranking_branches'):
        assert g.work.logical.get(name, 0) == 0


def test_public_point_admission_without_interpretation():
    g = structural('P1-point60')
    a = admit(g)
    assert a.disposition == 'ready_for_interpretation'
    assert a.observation['scalar'] == {'numerator': '60', 'denominator': '1'}
    assert a.envelope['lo'] == a.envelope['hi'] == a.observation['scalar']
    assert a.envelope['basis_kind'] == 'declared_point_assumption'
    assert [h['baseline'] for h in a.hypotheses] == ['baseline_eligible'] * 2
    assert g.work.logical['public_reconstructions'] == 2
    no_downstream(g)


@pytest.mark.parametrize('name', ['P2-below', 'P2-above', 'P2-reversed'])
def test_containment_refuses_before_later_work(name):
    g = structural(name)
    with pytest.raises(MeasurementContractError) as e:
        admit(g)
    assert (e.value.code, e.value.stage, e.value.target) == (
        'OBSERVATION_UNCERTAINTY_INCONSISTENT', 'phase_4', '/interpretation')
    assert g.work.logical.get('baseline_checks', 0) == 0
    no_downstream(g)


@pytest.mark.parametrize('name,expected', [
    ('P2-valid', 'ready_for_interpretation'),
    ('P10-denied', 'evaluation_denied'),
    ('P10-unknown_permission', 'evaluation_permission_unknown'),
    ('P10-no-baseline', 'baseline_unavailable'),
    ('P10-no-observation', 'observation_unavailable'),
    ('P10-acquisition-unknown', 'withheld_due_to_unknown_execution'),
    ('P10-hold', 'withheld_due_to_unknown_execution'),
    ('P10-hold-false', 'withheld_due_to_inapplicable_execution'),
    ('P10-original-inapplicable', 'withheld_due_to_inapplicable_execution'),
    ('P10-confidence', 'withheld_due_to_unknown_uncertainty'),
    ('P10-unknown_uncertainty', 'withheld_due_to_unknown_uncertainty'),
    ('P7-none', 'no_baseline_eligible_hypotheses'),
])
def test_gates_keep_exact_dispositions(name, expected):
    g = structural(name)
    a = admit(g)
    assert a.disposition == expected
    assert len(a.hypotheses) == 2
    if name in ('P10-denied', 'P10-unknown_permission'):
        assert all(h['baseline'] == 'not_assessed' for h in a.hypotheses)
        assert g.work.logical.get('baseline_checks', 0) == 0
    no_downstream(g)


@pytest.mark.parametrize('name', ['P7-wouldpermit', 'P7-wouldexclude'])
def test_baseline_cannot_be_eliminated_or_resurrected_by_observation(name):
    g = structural(name)
    a = admit(g)
    assert [h['baseline'] for h in a.hypotheses] == ['baseline_eligible', 'baseline_ineligible']
    assert a.disposition == 'ready_for_interpretation'
    no_downstream(g)


@pytest.mark.parametrize('name,chronology', [
    ('P8-before', 'declared_pre_exposure_unverified'),
    ('P8-after', 'declared_retrospective'), ('P8-unknown', 'exposure_unknown'),
    ('P8-null-times', 'declared_pre_exposure_unverified'),
    ('P8-absent', 'declared_pre_exposure_unverified'),
])
def test_content_is_not_chronology(name, chronology):
    g = structural(name)
    a = admit(g)
    assert a.exposure['chronology'] == chronology
    assert a.exposure['content_relationship'] == (
        'original_closure_verified' if name == 'P8-absent'
        else 'prior_bundle_integrity_and_reference_verified')
    assert 'unverified' in a.exposure['limitation']
    no_downstream(g)


@pytest.mark.parametrize('name,code,phase', [
    ('P8-contradiction', 'EXPOSURE_DECLARATION_INCONSISTENT', 'phase_4'),
    ('P10-acquisition-inconsistent', 'ACQUISITION_DECLARATION_INCONSISTENT', 'phase_4'),
    ('P10b-original', 'ORIGINAL_SELECTION_PIN_MISMATCH', 'phase_3'),
    ('P10b-result-pin', 'ORIGINAL_SELECTION_PIN_MISMATCH', 'phase_3'),
    ('P2-unit', 'OBSERVATION_JOIN_MISMATCH', 'phase_3'),
    ('P4-literal', 'RESULT_DOMAIN_UNSUPPORTED', 'phase_3'),
    ('P10-rational129', 'RESOURCE_LIMIT_EXCEEDED', 'phase_3'),
])
def test_frozen_adverse_twins(name, code, phase):
    g = structural(name)
    with pytest.raises(MeasurementContractError) as e:
        admit(g)
    assert (e.value.code, e.value.stage) == (code, phase)
    no_downstream(g)


def test_owning_reconstruction_hash_work_is_not_free(monkeypatch):
    import hashlib
    import inspect
    g=structural('P1-point60'); before=g.work.logical.get('hash_bytes',0)
    observed=0; backend=0; original=hashlib.sha256
    def measured(data=b'',*args,**kwargs):
        nonlocal observed,backend
        observed+=len(data)
        if '/backend/' in inspect.currentframe().f_back.f_code.co_filename:
            backend+=len(data)
        return original(data,*args,**kwargs)
    monkeypatch.setattr(hashlib,'sha256',measured)
    admit(g)
    assert observed>0
    # Backend canonical validators expose no application Work hook. Their real
    # hashing is measured here separately, without patching backend production.
    assert backend>0
    assert g.work.logical['hash_bytes']-before==observed-backend


@pytest.mark.parametrize('name',['P9-coherent','P9-context-twin','P9-decoder-twin',
    'P9-procedure-twin','P9-retrospective','P7-newbaseline','P10-shared_four',
    'P10-context8','P10-rational128','P3-lower','P3-upper'])
def test_valid_semantic_and_history_twins(name):
    g=structural(name);a=admit(g)
    assert a.disposition=='ready_for_interpretation'
    assert g.work.logical['baseline_checks']==sum(len(h['baseline_checks']) for h in a.hypotheses)
    no_downstream(g)


@pytest.mark.parametrize('kind,field,value,path',[
    ('nr.observation.v2','procedure','other_procedure','/observation/procedure'),
    ('nr.observation.v2','decoder','other_decoder','/observation/decoder'),
    ('nr.execution.v2','result_context','foreign_subject','/execution/result_context'),
])
def test_rehashed_observation_join_substitutions(kind,field,value,path):
    c,p=bound_internal('P1-point60');k=next(k for k in p if k[0]==kind);v=json.loads(p[k])
    if value in ('other_procedure','other_decoder'):
        target_kind='nm.procedure.v1' if value=='other_procedure' else 'nm.decoder.v1'
        other=next(k for k in p if k[0]==target_kind and json.loads(p[k])['id'].endswith('2'))
        v[field]={'kind':other[0],'sha256':other[1]}
    else:v[field]['subject_entity_anchor_id']='ent_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    replace(c,p,k,v);g=graph(c,p)
    with pytest.raises(MeasurementContractError) as e:admit(g)
    assert (e.value.code,e.value.target)==('OBSERVATION_JOIN_MISMATCH',path)
    no_downstream(g)


def test_public_unavailable_reason_and_execution_bases_survive():
    a=admit(structural('P10-no-observation'))
    assert a.observation['scalar'] is None and a.observation['reasons']
    assert all(r in a.reasons for r in a.observation['reasons'])
    g=structural('P10-hold');a=admit(g)
    assert [c for c in a.conditions if c['state']=='unknown'][0]['id']=='hold'
    assert any(r['code']=='condition_unknown' for r in a.reasons)


def test_same_phase_ordering_and_no_later_work():
    c,p=bound_internal('P2-below');k=next(k for k in p if k[0]=='nr.execution.v2');v=json.loads(p[k])
    v['acquisition']['end']='2026-08-08T00:00:00Z';replace(c,p,k,v);g=graph(c,p)
    with pytest.raises(MeasurementContractError) as e:admit(g)
    assert e.value.code=='ACQUISITION_DECLARATION_INCONSISTENT'
    assert g.work.logical.get('baseline_checks',0)==0
    no_downstream(g)


def test_no_support_or_ranking_calls_even_when_ready(monkeypatch):
    from applications.bounded_decision_workflow import measurement_compute, support_qualification, measurement_ranking
    def forbidden(*a,**kw):pytest.fail('later-slice work')
    monkeypatch.setattr(measurement_compute,'compute',forbidden)
    monkeypatch.setattr(measurement_compute,'qualify_supplied_support',forbidden)
    monkeypatch.setattr(support_qualification,'qualify_supplied_support',forbidden)
    monkeypatch.setattr(measurement_ranking,'rank_measurements',forbidden)
    for name in ('P1-point60','P5-missing','P5-conflict','P5-positive','P6-mixed'):
        g=structural(name);assert admit(g).disposition=='ready_for_interpretation';no_downstream(g)


@pytest.mark.parametrize('decimal,numerator,denominator',[
    ('0e999999','0','1'),('0.5','1','2'),('-0.002','-1','500'),
    ('2e-128','1',str(5*10**127)),('1'+'0'*127,'1'+'0'*127,'1'),
])
def test_exact_decimal_boundary_without_binary_float(decimal,numerator,denominator):
    from applications.bounded_decision_workflow.reassessment_admission import _decimal
    from applications.bounded_decision_workflow.measurement_wire import Work
    f=_decimal(decimal,Work())
    assert (str(f.numerator),str(f.denominator))==(numerator,denominator)


@pytest.mark.parametrize('decimal',['1e128','1e-128','1e999999','1e-999999'])
def test_expanded_decimal_refuses_without_large_power(decimal):
    from applications.bounded_decision_workflow.reassessment_admission import _decimal
    from applications.bounded_decision_workflow.measurement_wire import Work
    w=Work()
    with pytest.raises(MeasurementContractError,match='RESOURCE_LIMIT_EXCEEDED'):_decimal(decimal,w)
    assert w.logical.get('rational_operations',0)<1000


def test_public_reconstruction_refuses_rehashed_snapshot_corruption():
    c,p=bound_internal('P1-point60')
    g=graph(c,p);q=g.get(g.invocation['request']);e=g.get(q['observation'])['evidence']
    v=json.loads(p[key(e)]);v['snapshot']['state_anchor_id']='sta_bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    replace(c,p,key(e),v);g=graph(c,p)
    with pytest.raises(MeasurementContractError) as exc:admit(g)
    assert exc.value.code in ('PUBLIC_RECONSTRUCTION_INVALID','EVIDENCE_JOIN_MISMATCH')
    assert exc.value.stage=='phase_3'
    assert g.work.logical.get('baseline_checks',0)==0
    no_downstream(g)


def test_exact_reconstruction_demand_and_one_below():
    c,p=bound_internal('P1-point60');g=graph(c,p);admit(g)
    n=g.work.logical['public_reconstruction_nodes']
    g=graph(c,p,{'public_reconstruction_nodes':n});assert admit(g).disposition=='ready_for_interpretation'
    g=graph(c,p,{'public_reconstruction_nodes':n-1})
    with pytest.raises(MeasurementContractError) as exc:admit(g)
    assert exc.value.details['dimension']=='public_reconstruction_nodes'
    assert g.work.logical.get('baseline_checks',0)==0
    no_downstream(g)


def test_permutation_preserves_admission_and_original_bytes():
    from dataclasses import asdict
    c,p=bound_internal('P8-before');original=dict(p)
    a=admit(graph(c,p));b=admit(graph(c,dict(reversed(list(p.items())))))
    assert asdict(a)==asdict(b)
    assert p==original


def test_permission_does_not_bypass_containment():
    c,p=bound_internal('P2-above');k=next(k for k in p if k[0]=='nr.authority.v2');v=json.loads(p[k]);v['permission']='false'
    replace(c,p,k,v);g=graph(c,p)
    with pytest.raises(MeasurementContractError,match='OBSERVATION_UNCERTAINTY_INCONSISTENT'):admit(g)
    assert g.work.logical.get('baseline_checks',0)==0


def test_historical_containment_is_checked_without_historical_baseline():
    c,p=bound_internal('P10-shared_four')
    k=next(k for k in p if k[0]=='nr.request.v2' and json.loads(p[k])['revision']==1);q=json.loads(p[k])
    q['interpretation'].update(kind='hard_interval',lo={'numerator':'0','denominator':'1'},hi={'numerator':'1','denominator':'1'})
    replace(c,p,k,q);g=graph(c,p)
    with pytest.raises(MeasurementContractError) as exc:admit(g)
    assert exc.value.code=='OBSERVATION_UNCERTAINTY_INCONSISTENT'
    assert g.get(exc.value.details['request'])['revision']==1
    assert g.work.logical.get('baseline_checks',0)==0


def test_all_reached_execution_reasons_and_basis_are_retained():
    c,p=bound_internal('P1-point60');k=next(k for k in p if k[0]=='nr.execution.v2');v=json.loads(p[k])
    v['conditions'][0]['state']='false';v['conditions'][4]['state']='unknown'
    replace(c,p,k,v);a=admit(graph(c,p))
    assert a.disposition=='withheld_due_to_inapplicable_execution'
    assert [r['path'] for r in a.reasons]==['/conditions/applicability','/conditions/hold']
    assert [c for c in a.conditions if c['state']!='true']==[
        dict(reference=a.conditions[5]['reference'],id=r['id'],state=r['state'],basis=r['basis'],observed=None,threshold=None)
        for r in (v['conditions'][0],v['conditions'][4])]


@pytest.mark.parametrize('name',['P1-point60','P8-before','P7-newbaseline','P10-no-observation'])
def test_production_capture_then_admit(tmp_path,name):
    from dataclasses import asdict
    from test_capture import actual_case,files_for,capture
    c,p=actual_case(name);g=capture(*files_for(tmp_path,c,p));a=admit(g)
    assert a.disposition==('observation_unavailable' if name=='P10-no-observation' else 'ready_for_interpretation')
    assert g.work.physical['bytes_read']==sum(map(len,g.objects.values()))
    assert g.work.physical['bytes_written']==0
    no_downstream(g)
    (tmp_path/'slice2-measurement.json').write_bytes(wire(dict(case=name,admission=asdict(a),logical=g.work.logical,
        physical=g.work.physical,closure_bytes=len(g.closure_bytes),build_bytes=len(g.objects[key(g.invocation['build'])]))))


def test_public_lower_string_guard_is_not_waived():
    from applications.bounded_decision_workflow.errors import WorkflowInputError
    c,p=bound_internal('P1-point60');g=graph(c,p);q=g.get(g.invocation['request'])
    e=g.get(q['observation'])['evidence'];v=json.loads(p[key(e)])
    v['snapshot']['state_anchor_id']='x'*257
    replace(c,p,key(e),v);g=graph(c,p)
    with pytest.raises(WorkflowInputError) as exc:admit(g)
    assert exc.value.diagnostic.code=='INPUT_RESOURCE_LIMIT_EXCEEDED'
    assert exc.value.diagnostic.target=='input_max_string_bytes'
    no_downstream(g)


def test_json_decode_work_matches_actual_public_parse(monkeypatch):
    g=structural('P1-point60');original=json.loads;seen=0
    def measured(data,*args,**kwargs):
        nonlocal seen
        seen+=len(data.encode() if isinstance(data,str) else data)
        return original(data,*args,**kwargs)
    monkeypatch.setattr(json,'loads',measured)
    before=g.work.logical['json_decode_bytes'];admit(g)
    assert g.work.logical['json_decode_bytes']-before==seen


def test_new_permission_is_independent_of_original_permission():
    c,p=bound_internal('P1-point60');k=next(k for k in p if k[0]=='nm.declaration.v1');v=json.loads(p[k]);v['scope_state']='false'
    replace(c,p,k,v)
    # Mechanical rehash changes original selection; update its explicit pin in
    # this new test request. No frozen input or stored result is rewritten.
    g=graph(c,p);qk=key(g.invocation['request']);q=g.get(g.invocation['request'])
    q['original_selection_pin']=g.get(q['original_invocation'])['selection']['sha256']
    replace(c,p,qk,q);g=graph(c,p)
    assert admit(g).disposition=='ready_for_interpretation'


def test_unknown_chronology_with_times_does_not_become_pre_exposure():
    g=structural('P8-unknown-times');a=admit(g)
    assert a.exposure['chronology']=='exposure_unknown'
    assert a.exposure['declared_prediction_commitment_at'] is not None


@pytest.mark.parametrize('field',['start','end'])
def test_unknown_acquisition_cannot_retain_times(field):
    c,p=bound_internal('P10-acquisition-unknown');k=next(k for k in p if k[0]=='nr.execution.v2');v=json.loads(p[k])
    v['acquisition'][field]='2026-08-07T20:00:05Z';replace(c,p,k,v);g=graph(c,p)
    with pytest.raises(MeasurementContractError,match='ACQUISITION_DECLARATION_INCONSISTENT'):admit(g)
    no_downstream(g)
