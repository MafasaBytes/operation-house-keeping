"""Slice 3 mathematical oracle checks; no delivery or full command proof.

Frozen same-author hand expectations are assertions only, never runtime inputs.
Internal shaped-build graphs are labelled; production capture twins are separate.
"""
import json
import zipfile
from fractions import Fraction

import pytest

from applications.bounded_decision_workflow.reassessment_compute import compute, intersect
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError
from applications.bounded_decision_workflow.measurement_wire import Work
from test_capture import PACKAGE, structural, bound_internal, graph, key, wire

with zipfile.ZipFile(PACKAGE) as z:
    CASES = [c for c in json.loads(z.read('cases.json'))
             if c['id'].split('-')[0] in ('P1','P2','P3','P3b','P4','P5','P6','P7','P8','P9')]


@pytest.mark.parametrize('case',CASES,ids=lambda c:c['id'])
def test_frozen_mathematical_and_epistemic_expectations(case):
    expected=case['expected']
    if expected['exit']:
        with pytest.raises(MeasurementContractError) as error:
            compute(structural(case['id']))
        assert error.value.code==expected['diagnostic']['code']
        assert error.value.stage=='phase_'+str(expected['diagnostic']['phase'])
        return
    g=structural(case['id']);before=dict(g.objects);result,trace=compute(g)
    assert result['summary']['disposition']==expected['summary']
    names={'compatible':'compatible_under_declared_model','incompatible':'conditionally_incompatible'}
    assert [h['status'] for h in result['hypotheses']]==[names.get(s,s) for s in expected['states']]
    branches=result['interpretation']['branches']
    assert (None if branches is None else [b['outcome'] for b in branches])==expected['branches']
    assert result['adoption']=='derived_not_adopted'
    assert result['original']['ranking']=='not_reassessed'
    assert [h['reference'] for h in result['hypotheses']]==result['original']['hypotheses']
    assert g.objects==before
    assert trace['required_closure']==[{'kind':k[0],'sha256':k[1]} for k in sorted(g.objects)]
    assert g.work.logical.get('ranking_branches',0)==0


@pytest.mark.parametrize('denominator,nonempty',[(3,False),(2,True)])
def test_exact_endpoint_domain(denominator,nonempty):
    point={'numerator':'1','denominator':str(denominator)}
    region=dict(kind='interval',lower=point,upper=point,lower_closed=True,upper_closed=True)
    answer=intersect(region,Fraction(0),Fraction(1),Work())
    assert (answer is not None)==nonempty


@pytest.mark.parametrize('name',['P10-denied','P10-unknown_permission','P10-no-baseline',
    'P10-no-observation','P10-hold','P10-confidence'])
def test_withholding_has_no_qualification_or_intersection(name,monkeypatch):
    from applications.bounded_decision_workflow import reassessment_compute as module
    def forbidden(*args,**kwargs):pytest.fail('work past gate')
    monkeypatch.setattr(module,'qualify_supplied_support',forbidden)
    monkeypatch.setattr(module,'intersect',forbidden)
    g=structural(name);r,t=compute(g)
    assert r['interpretation']['branches'] is None
    assert all(h['cells'] is None for h in r['hypotheses'])
    assert g.work.logical.get('qualified_cells',0)==g.work.logical.get('interval_intersections',0)==0


def test_all_outcomes_qualified_but_only_envelope_concludes():
    g=structural('P5-unrelated');r,t=compute(g)
    assert r['summary']['disposition']=='one_compatible'
    assert g.work.logical['qualified_cells']==6
    assert g.work.logical['interval_intersections']==3
    assert all(len(h['cells'])==1 for h in r['hypotheses'])


def test_revision_discloses_before_and_after_without_changing_history():
    old,_=compute(structural('P5-mismatch'))
    g=structural('P9-retrospective');before=dict(g.objects);r,t=compute(g)
    assert old['summary']['disposition']=='model_prediction_mismatch'
    assert r['summary']['disposition']=='multiple_compatible'
    assert r['exposure']['chronology']=='declared_retrospective'
    assert r['exposure']['changed_references']
    assert any(x['path'].startswith('/original/support/') for x in r['exposure']['changed_references'])
    assert g.objects==before


def test_construction_order_and_no_ranking(monkeypatch):
    from applications.bounded_decision_workflow import measurement_compute,measurement_ranking
    def forbidden(*args,**kwargs):pytest.fail('ranking not authorized')
    monkeypatch.setattr(measurement_ranking,'rank_measurements',forbidden)
    monkeypatch.setattr(measurement_compute,'compute',forbidden)
    c,p=bound_internal('P6-multiple')
    a=compute(graph(c,p));b=compute(graph(c,dict(reversed(list(p.items())))))
    assert a==b


@pytest.mark.parametrize('case',[c for c in CASES if c['expected']['exit']==0],ids=lambda c:c['id'])
def test_complete_frozen_semantic_result_excluding_runtime_accounting(case):
    g=structural(case['id']);result,trace=compute(g)
    with zipfile.ZipFile(PACKAGE) as z:expected=json.loads(z.read('cases/'+case['id']+'/result.json'))
    # Only the prepared-build-dependent I reference is mechanically rebound.
    old=expected['invocation']
    def bind(value):
        if value==old:return g.root
        if isinstance(value,dict):return {k:bind(v) for k,v in value.items()}
        if isinstance(value,list):return [bind(v) for v in value]
        return value
    expected=bind(expected)
    expected.pop('accounting');result.pop('accounting')
    assert result==expected


def test_separate_frozen_arithmetic_checker_agrees():
    # Test-only use of the independently written same-author static checker.
    # No future production calculation loads this code or its assertions.
    with zipfile.ZipFile(PACKAGE) as z:
        namespace={'__name__':'frozen_static_oracle'}
        exec(compile(z.read('check_static.py'),'frozen/check_static.py','exec'),namespace)
    for case in CASES:
        if case['expected']['branches'] is None:continue
        g=structural(case['id']);r,t=compute(g);q=g.get(g.invocation['request'])
        envelope=r['interpretation']['envelope'];rat=namespace['rat']
        independent=[o['id'] for o in g.get(q['decoder'])['outcomes']
                     if namespace['intersects'](o['region'],rat(envelope['lo']),rat(envelope['hi']))]
        assert independent==case['expected']['branches']==[b['outcome'] for b in r['interpretation']['branches']]


def test_missing_complement_and_justified_twin():
    partial,_=compute(structural('P5-positive'));complete,_=compute(structural('P1-point60'))
    assert partial['hypotheses'][1]['status']=='unresolved'
    assert partial['hypotheses'][1]['cells'][0]['relation']=='unknown'
    assert complete['hypotheses'][1]['status']=='conditionally_incompatible'


def test_empty_nondecimal_branch_is_retained_not_interpreted():
    g=structural('P3b-third');q=g.get(g.invocation['request']);before=wire(g.get(q['decoder']))
    r,t=compute(g)
    assert len(g.get(q['decoder'])['outcomes'])==3
    assert len(r['interpretation']['branches'])==1
    assert g.work.logical['qualified_cells']==6
    assert wire(g.get(q['decoder']))==before


def test_defensive_envelope_coverage_rejects_gap_and_overlap():
    from applications.bounded_decision_workflow.reassessment_compute import _cover
    from applications.bounded_decision_workflow.measurement_compute import ratio
    g=structural('P1-point60');q=g.get(g.invocation['request'])
    def branch(lo,hi,lc=True,uc=True):return dict(outcome='test',intersection=dict(lo=ratio(Fraction(lo)),hi=ratio(Fraction(hi)),lower_closed=lc,upper_closed=uc))
    for branches in ([],[branch(0,1)],[branch(0,1),branch(1,2)], [branch(0,1,True,False),branch('1.1',2)]):
        with pytest.raises(MeasurementContractError,match='DECODER_INVALID'):
            _cover(branches,Fraction(0),Fraction(2),Work(),g.invocation['request'],q['decoder'])
    _cover([branch(0,1),branch(1,2,False,True)],Fraction(0),Fraction(2),Work(),g.invocation['request'],q['decoder'])


def test_baseline_ineligible_source_cannot_force_row_refusal(monkeypatch):
    from applications.bounded_decision_workflow import reassessment_compute as module
    g=structural('P7-wouldpermit');original=module.qualify_supplied_support;seen=[]
    def measured(*args,**kwargs):seen.append(g.get(kwargs['hypothesis'])['id']);return original(*args,**kwargs)
    monkeypatch.setattr(module,'qualify_supplied_support',measured)
    r,t=compute(g)
    assert seen==['H1']
    assert r['hypotheses'][1]['cells'] is None
    assert r['hypotheses'][1]['outcome_state']=='not_assessed_baseline_ineligible'


@pytest.mark.parametrize('name',['P1-point60','P5-missing','P5-mismatch','P6-multiple','P10-denied'])
def test_real_captured_semantic_path(tmp_path,name):
    from test_capture import actual_case,files_for,capture
    c,p=actual_case(name);g=capture(*files_for(tmp_path,c,p));r,t=compute(g)
    assert r['invocation']==g.root and r['adoption']=='derived_not_adopted'
    assert g.work.physical['bytes_written']==0
    assert len(wire(r))<=g.work.limits['result_bytes']
    assert len(wire(t))<=g.work.limits['trace_bytes']
    (tmp_path/'measurements.json').write_bytes(wire(dict(result=r,trace=t,logical=g.work.logical,physical=g.work.physical)))


def check_shape(value,schema):
    """Test-only closed-shape checker for the packaged output schema vocabulary."""
    import re
    if 'anyOf' in schema:
        for option in schema['anyOf']:
            try:check_shape(value,option);return
            except AssertionError:pass
        raise AssertionError('no schema alternative: '+repr(value)[:150])
    types={'object':dict,'array':list,'string':str,'integer':int,'boolean':bool,'null':type(None)}
    if 'type' in schema:assert type(value) is types[schema['type']]
    if 'enum' in schema:assert value in schema['enum']
    if 'pattern' in schema:assert re.search(schema['pattern'],value)
    if 'minimum' in schema:assert value>=schema['minimum']
    if 'maximum' in schema:assert value<=schema['maximum']
    if type(value) is dict:
        assert set(schema.get('required',[]))<=set(value)
        if schema.get('additionalProperties') is False:assert set(value)<=set(schema['properties'])
        for k,v in value.items():check_shape(v,schema.get('properties',{}).get(k,{}))
    if type(value) is list:
        for v in value:check_shape(v,schema.get('items',{}))


@pytest.mark.parametrize('name',['P8-before','P5-missing','P10-no-baseline','P10-denied','P10-no-observation','P9-retrospective'])
def test_closed_output_shapes_and_actual_high_water(name):
    with zipfile.ZipFile(PACKAGE) as z:schemas=json.loads(z.read('wire-catalog.json'))['$defs']
    g=structural(name);r,t=compute(g)
    check_shape(r,schemas['nr.result.v2']);check_shape(t,schemas['nr.trace.v2'])
    assert r['accounting']['logical']['json_depth']>0
    assert r['accounting']['logical']['string_bytes']>0
    assert r['accounting']['logical']['prior_bundle_bytes']==sum(len(b) for fs in g.prior_bundles.values() for b in fs.values())


@pytest.mark.parametrize('dimension,index',[('result_bytes',0),('trace_bytes',1)])
def test_output_demand_and_one_below(dimension,index):
    c,p=bound_internal('P6-multiple');g=graph(c,p);outputs=compute(g);n=len(wire(outputs[index]))
    # Setting this after capture isolates the output guard, not prior-file caps.
    exact=graph(c,p);exact.work.limits[dimension]=n;compute(exact)
    short=graph(c,p);short.work.limits[dimension]=n-1
    with pytest.raises(MeasurementContractError) as e:compute(short)
    assert e.value.code=='RESOURCE_LIMIT_EXCEEDED'
    assert e.value.details['dimension']==dimension
    assert short.work.physical['bytes_written']==0


def test_legacy_work_does_not_gain_new_reporting_fields():
    legacy=Work();legacy.guard('json_depth',5);legacy.guard('string_bytes',9)
    assert legacy.logical=={}
    g=structural('P1-point60');assert g.work.logical['json_depth']>0


def test_dependency_and_reason_references_are_captured_and_not_discovery():
    for name in ('P5-conflict','P9-retrospective','P7-newbaseline'):
        g=structural(name);r,t=compute(g)
        def references(v):
            if isinstance(v,dict):
                if set(v)=={'kind','sha256'}:yield v
                else:
                    for x in v.values():yield from references(x)
            elif isinstance(v,list):
                for x in v:yield from references(x)
        assert all(key(ref) in g.objects for ref in references((list((r,t)))))
        assert [d['result_path'] for d in t['dependencies']]==sorted(d['result_path'] for d in t['dependencies'])
        assert r['exposure']['changed_references']==sorted(r['exposure']['changed_references'],key=lambda x:x['path'])


@pytest.mark.parametrize('name',['P10-denied','P10-unknown_permission','P10-no-baseline','P10-no-observation',
    'P10-hold','P10-hold-false','P10-unknown_uncertainty','P10-original-inapplicable','P10-acquisition-unknown'])
def test_complete_withholding_result_matches_frozen_template(name):
    g=structural(name);r,t=compute(g)
    with zipfile.ZipFile(PACKAGE) as z:expected=json.loads(z.read('cases/'+name+'/result.json'))
    old=expected['invocation']
    def bind(v):
        if v==old:return g.root
        if isinstance(v,dict):return {k:bind(x) for k,x in v.items()}
        if isinstance(v,list):return [bind(x) for x in v]
        return v
    expected=bind(expected);r.pop('accounting');expected.pop('accounting')
    assert r==expected


@pytest.mark.parametrize('name',['P1-point60','P5-conflict','P9-retrospective','P10-denied'])
def test_complete_trace_matches_bound_frozen_template(name):
    g=structural(name);r,t=compute(g)
    with zipfile.ZipFile(PACKAGE) as z:
        expected=json.loads(z.read('cases/'+name+'/trace.json'))
        iv=json.loads(z.read('cases/'+name+'/invocation.json'))
    mapping={key(expected['invocation']):g.root,key(iv['build']):g.invocation['build']}
    def bind(v):
        if isinstance(v,dict):
            if set(v)=={'kind','sha256'}:return mapping.get(key(v),v)
            return {k:bind(x) for k,x in v.items()}
        if isinstance(v,list):return [bind(x) for x in v]
        return v
    assert t==bind(expected)
