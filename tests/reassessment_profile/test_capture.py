"""Slice 1 structural capture only; frozen outputs are never computation inputs."""
import base64
import json
from pathlib import Path
import zipfile

import pytest

from applications.bounded_decision_workflow.measurement_wire import Work, sha, ref, key
from applications.bounded_decision_workflow.measurement_contracts import canonical_json_bytes as wire
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError
from applications.bounded_decision_workflow.reassessment_capture import Captured, capture

PACKAGE = Path('docs/superpowers/reports/2026-09-23-reassessment-preparation/package.zip')


def case(name='P8-before'):
    with zipfile.ZipFile(PACKAGE) as z:
        c = json.loads(z.read('cases/'+name+'/input.json'))
        objects = {key(r): z.read('objects/'+r['sha256']+'.'+r['kind']) for r in c['members']}
    return c, objects


def bound_internal(name='P8-before'):
    c, objects = case(name)
    # Internal graph test: no executable claim. Public capture always binds build.
    iv=json.loads(objects.pop(key(c['invocation'])))
    build=json.loads(objects.pop(key(iv['build'])))
    build.pop('status',None)
    build.pop('binding',None)
    build['schema']='nr.build.v2'
    body={k:v for k,v in build.items() if k not in ('schema','profile','id','revision','predecessor')}
    build['id']=sha(wire(body))
    raw=wire(build);iv['build']=ref('nr.build.v2',sha(raw));objects[key(iv['build'])]=raw
    raw=wire(iv);c['invocation']=ref('nr.invocation.v2',sha(raw));objects[key(c['invocation'])]=raw
    return c, objects


def graph(c,objects,limits=None):
    return Captured(objects[key(c['invocation'])], objects.__getitem__, c['authority_pin'], Work(limits))


def structural(name='P8-before'):
    return graph(*bound_internal(name))


def test_exact_historical_recovery_and_sharing():
    g = structural()
    assert len(g.prior_bundles) == 1
    files = next(iter(g.prior_bundles.values()))
    assert sum(map(len, files.values())) == 232849
    assert sha(files['closure.json']) == '5d8df562890d51a2bfdba10ddc460fcc822c1f31adc247651c825305eda405cd'
    assert g.work.logical['reference_occurrences'] > len(g.objects)
    assert 'branch_intersections' not in g.work.logical


@pytest.mark.parametrize('name,dimension', [('P10-fifth','request_chain'), ('P10-context9','request_contexts'), ('P10-objects129','unique_objects')])
def test_frozen_structural_boundaries(name, dimension):
    with pytest.raises(MeasurementContractError) as e:
        structural(name)
    assert e.value.code == 'RESOURCE_LIMIT_EXCEEDED'
    assert e.value.details['dimension'] == dimension


@pytest.mark.parametrize('name', ['P10-shared_four', 'P10-context8', 'P10-objects128'])
def test_nearest_valid_boundaries(name):
    assert structural(name).objects


def replace(c,objects,target,value):
    """Test fixture rehashing only. Retained nm.basis bytes never get rewritten."""
    cache={}
    def obj(k):
        if k in cache:return cache[k]
        if k[0]=='nm.basis':cache[k]=k;return k
        v=value if k==target else json.loads(objects[k])
        def descend(x):
            if type(x) is dict:
                if set(x)=={'kind','sha256'}:
                    child=key(x)
                    if k==target and child==target:return x
                    return ref(*obj(child)) if child in objects else x
                return {f:descend(y) for f,y in x.items()}
            if type(x) is list:return [descend(y) for y in x]
            return x
        v=descend(v);b=wire(v);r=(k[0],sha(b));objects[r]=b;cache[k]=r;return r
    c['invocation']=ref(*obj(key(c['invocation'])))
    c['authority_pin']=json.loads(objects[key(c['invocation'])])['authority']['sha256']


@pytest.mark.parametrize('field,expected', [('extra','SCHEMA_INVALID'),('revision','REVISION_INVALID'),('profile','PROFILE_MISMATCH')])
def test_rehashed_closed_shape_attacks(field,expected):
    c,p=bound_internal('P1-point60');k=key(c['invocation']);v=json.loads(p[k])
    v[field]={'extra':True,'revision':True,'profile':'bdw.measurement.supplied.v1'}[field]
    replace(c,p,k,v)
    with pytest.raises(MeasurementContractError,match=expected):graph(c,p)


@pytest.mark.parametrize('attack,expected',[
    ('recipe','SCHEMA_INVALID'),('duplicate','SCHEMA_INVALID'),('extra','SCHEMA_INVALID'),
    ('missing','SCHEMA_INVALID'),('role','REFERENCE_ROLE_MISMATCH'),('manifest','MANIFEST_COMMITMENT_MISMATCH'),
])
def test_rehashed_descriptor_attacks(attack,expected):
    c,p=bound_internal();k=next(k for k in p if k[0]=='nr.retained-bundle.v2');d=json.loads(p[k])
    if attack=='recipe':next(r for r in d['files'] if r['name']=='closure.json')['source']['recipe']='caller_patch'
    if attack=='duplicate':d['closure']['members'].append(d['closure']['members'][0])
    if attack=='extra':d['closure']['extra']=True
    if attack=='missing':d['closure']['members'].pop()
    if attack=='role':
        row=next(r for r in d['files'] if r['name']=='result.json')
        build=next(k for k in p if k[0]=='nm.build.v1');b=p[build];r=('nm.basis',sha(b));p[r]=b
        row['source']['reference']=ref(*r)
    if attack=='manifest':
        row=next(r for r in d['files'] if r['name']=='manifest.json');v=json.loads(p[key(row['source']['reference'])])
        v['files'][0]['bytes']+=1;b=wire(v);r=('nm.basis',sha(b));p[r]=b;row['source']['reference']=ref(*r)
    replace(c,p,k,d)
    with pytest.raises(MeasurementContractError,match=expected):graph(c,p)


@pytest.mark.parametrize('missing', [False,True])
def test_public_bytes_hash_precedes_cycle_claim(missing):
    c,p=bound_internal('P10-shared_four')
    k=next(k for k in p if k[0]=='nr.request.v2' and json.loads(p[k])['revision']==1)
    if missing:del p[k]
    else:
        v=json.loads(p[k]);v['predecessor']=ref(*k);p[k]=wire(v) # deliberately stale digest
    with pytest.raises(MeasurementContractError,match='REQUIRED_REFERENCE_MISSING' if missing else 'REFERENCE_DIGEST_MISMATCH'):
        graph(c,p)


@pytest.mark.parametrize('adj,cycle', [({'a':['a']},True),({'a':['b'],'b':['a']},True),({'a':['b','c'],'b':['d'],'c':['d'],'d':[]},False)])
def test_internal_actual_traversal_cycles_and_diamond(adj,cycle):
    from applications.bounded_decision_workflow.reassessment_capture import _walk
    seen=[];work=Work()
    def run():return _walk('a',lambda k,p,path:seen.append(k),lambda k:[('/'+str(i),x) for i,x in enumerate(adj[k])],work)
    if cycle:
        with pytest.raises(MeasurementContractError,match='REFERENCE_CYCLE'):run()
    else:
        assert run()==set(adj)
        assert seen.count('d')==2 and work.logical['reference_occurrences']==4


@pytest.mark.parametrize('dimension', ['active_depth','capture_bytes','context_scan_bytes','edge_visits','invocation_bytes','json_nodes','object_bytes','reference_occurrences','scoped_expansions','unique_objects','request_contexts','request_chain'])
def test_real_graph_measured_demand_and_one_below(dimension):
    c,p=bound_internal('P10-shared_four' if dimension=='request_chain' else 'P8-before');g=graph(c,p);d=g.work.logical[dimension]
    assert graph(c,p,{dimension:d}).objects
    with pytest.raises(MeasurementContractError) as e:graph(c,p,{dimension:d-1})
    assert e.value.code=='RESOURCE_LIMIT_EXCEEDED' and e.value.details['dimension']==dimension


@pytest.mark.parametrize('dimension', ['active_depth','build_bytes','bundle_bytes','capture_bytes','closure_bytes','context_scan_bytes','edge_visits','integer_digits','invocation_bytes','json_depth','json_nodes','manifest_bytes','object_bytes','reference_occurrences','request_chain','request_contexts','result_bytes','scoped_expansions','string_bytes','trace_bytes','unique_objects'])
def test_internal_unchanged_guard_at_ceiling_and_plus_one(dimension):
    w=Work();n=w.limits[dimension];w.guard(dimension,n)
    with pytest.raises(MeasurementContractError) as e:w.guard(dimension,n+1)
    assert e.value.details=={'dimension':dimension,'attempted':n+1,'limit':n}


def test_serialization_reserves_before_base64(monkeypatch):
    from applications.bounded_decision_workflow import reassessment_capture as module
    c,p=bound_internal('P1-point60');g=graph(c,p);raw=g.closure(c['authority_pin']);n=len(raw)
    g.work.limits['closure_bytes']=n
    assert g.closure(c['authority_pin'])==raw
    g.work.limits['closure_bytes']=n-1
    def forbidden(*args):raise AssertionError('allocation before guard')
    monkeypatch.setattr(module.base64,'b64encode',forbidden)
    with pytest.raises(MeasurementContractError,match='RESOURCE_LIMIT_EXCEEDED'):g.closure(c['authority_pin'])


@pytest.mark.parametrize('name', ['P1-point60','P2-below'])
def test_no_observation_or_support_work_in_slice_one(name):
    # Containment is deliberately Slice 2; positive capture is not admission.
    g=structural(name)
    assert not any(k in g.work.logical for k in ('branch_intersections','public_reconstruction_nodes','support_cells','ranking_cells'))


@pytest.mark.parametrize('kind',['nr.request.v2','nr.observation.v2','nr.execution.v2','nr.exposure.v2','nr.authority.v2','nr.policy.v2'])
def test_ancestor_identity_mismatch_and_coherent_twin(kind):
    for adverse in (False,True):
        c,p=bound_internal('P1-point60');k=next(k for k in p if k[0]==kind);old=json.loads(p[k])
        v=dict(old,revision=2,predecessor=ref(*k))
        if adverse:v['id']='different-identity'
        replace(c,p,k,v)
        if adverse:
            with pytest.raises(MeasurementContractError,match='PREDECESSOR_VERSION_MISMATCH'):graph(c,p)
        else:assert graph(c,p).objects


@pytest.mark.parametrize('name,code',[('P4-gap','DECODER_INVALID'),('P4-overlap','DECODER_INVALID'),('P4-remote_gap','DECODER_INVALID')])
def test_original_decoder_and_rational_guards(name,code):
    with pytest.raises(MeasurementContractError,match=code):structural(name)


@pytest.mark.parametrize('name',['P4-partition','P10-rational128','P7-newbaseline'])
def test_recovery_valid_large_and_numerical_twins(name):
    assert structural(name).objects


def test_interval_endpoint_digit_boundary_without_observation_admission():
    for digits in (128,129):
        c,p=bound_internal('P1-point60');k=next(k for k in p if k[0]=='nr.request.v2');q=json.loads(p[k])
        q['interpretation'].update(kind='hard_interval',lo={'numerator':'0','denominator':'1'},hi={'numerator':'9'*digits,'denominator':'1'})
        replace(c,p,k,q)
        if digits==128:assert graph(c,p).objects
        else:
            with pytest.raises(MeasurementContractError,match='RESOURCE_LIMIT_EXCEEDED'):graph(c,p)
    # This frozen case's huge value is inside E1, not an nr endpoint. Public
    # numerical reconstruction and its integer conversion belong to Slice 2.
    assert structural('P10-rational129').objects


def test_canonical_and_token_preallocation_guards():
    from applications.bounded_decision_workflow.measurement_wire import decode
    with pytest.raises(MeasurementContractError,match='CANONICAL_FORM_REQUIRED'):decode(b'{"x": 1}',Work())
    with pytest.raises(MeasurementContractError):decode(b'{"x":1,"x":2}',Work())
    for valid,invalid,limits in [
        (b'{"x":"abcd"}',b'{"x":"abcde"}',{'string_bytes':4}),
        (b'{"x":[]}',b'{"x":[[]]}',{'json_depth':2}),
        (b'{"x":[1]}',b'{"x":[1,2]}',{'json_nodes':3}),
    ]:
        decode(valid,Work(limits))
        with pytest.raises(MeasurementContractError,match='RESOURCE_LIMIT_EXCEEDED'):decode(invalid,Work(limits))


@pytest.mark.parametrize('attack,expected',[('exact','DUPLICATE_NOMINATION_REFERENCE'),('revision','DUPLICATE_NOMINATION_ID'),('collision','IDENTITY_VERSION_COLLISION')])
def test_owning_nomination_integrity(attack,expected):
    c,p=bound_internal('P1-point60');qk=next(k for k in p if k[0]=='nm.request.v1');q=json.loads(p[qk])
    if attack=='exact':q['hypotheses'][1]=q['hypotheses'][0];replace(c,p,qk,q)
    elif attack=='revision':
        hk=key(q['hypotheses'][1]);h=json.loads(p[hk]);h['id']=json.loads(p[key(q['hypotheses'][0])])['id'];h['revision']=2
        replace(c,p,hk,h)
    else:
        h=json.loads(p[key(q['hypotheses'][0])]);h['account_kind']='low_underlying_positive_offset'
        b=wire(h);r=(h['schema'],sha(b));p[r]=b;q['hypotheses'][1]=ref(*r);replace(c,p,qk,q)
    with pytest.raises(MeasurementContractError,match=expected):graph(c,p)


def test_case_sensitive_identity_and_construction_permutation():
    c,p=bound_internal('P1-point60');hk=next(k for k in p if k[0]=='nm.hypothesis.v1' and json.loads(p[k])['id']=='H2')
    h=json.loads(p[hk]);h['id']='h1';replace(c,p,hk,h)
    a=graph(c,p);b=graph(c,dict(reversed(list(p.items()))))
    assert a.objects==b.objects and a.work.logical==b.work.logical
    assert a.closure(c['authority_pin'])==b.closure(c['authority_pin'])


def test_typed_reference_rejects_rehashed_cross_profile():
    c,p=bound_internal('P1-point60');k=key(c['invocation']);v=json.loads(p[k])
    v['request']['kind']='thermal.request.v1';replace(c,p,k,v)
    with pytest.raises(MeasurementContractError,match='REFERENCE_ROLE_MISMATCH'):graph(c,p)


def test_original_recorded_work_limit_is_not_erased_by_sharing():
    c,p=bound_internal();k=next(k for k in p if k[0]=='nr.retained-bundle.v2');d=json.loads(p[k])
    d['closure']['limits_override']={'edge_visits':1}
    old=dict(d['closure'],members=[dict(reference=r,encoding='base64',bytes=base64.b64encode(p[key(r)]).decode()) for r in d['closure']['members']])
    row=next(r for r in d['files'] if r['name']=='manifest.json');m=json.loads(p[key(row['source']['reference'])])
    entry=next(r for r in m['files'] if r['name']=='closure.json');entry.update(bytes=len(wire(old)),sha256=sha(wire(old)))
    b=wire(m);r=('nm.basis',sha(b));p[r]=b;row['source']['reference']=ref(*r)
    replace(c,p,k,d)
    with pytest.raises(MeasurementContractError) as e:graph(c,p)
    assert e.value.code=='RESOURCE_LIMIT_EXCEEDED' and e.value.details['dimension']=='edge_visits'


def test_phase_two_prior_integrity_precedes_nomination_diagnostics():
    c,p=bound_internal();qk=next(k for k in p if k[0]=='nm.request.v1');q=json.loads(p[qk])
    q['hypotheses'][1]=q['hypotheses'][0];replace(c,p,qk,q)
    with pytest.raises(MeasurementContractError) as e:graph(c,p)
    assert e.value.stage=='phase_2'
    # Rehashing changed the selection, while the recipe's scalar pin remained
    # frozen. That phase-2 join precedes both manifest and nomination checks.
    assert e.value.code=='AUTHORITY_REFERENCE_MISMATCH'


def files_for(tmp_path,c,p):
    directory=tmp_path/'objects';directory.mkdir()
    for (kind,digest),raw in p.items():(directory/(digest+'.'+kind)).write_bytes(raw)
    invocation=tmp_path/'invocation.json';invocation.write_bytes(p[key(c['invocation'])])
    return invocation,directory,c['authority_pin']


def actual_case(name='P8-before'):
    from applications.bounded_decision_workflow.reassessment_build import identity
    c,p=case(name);iv=json.loads(p.pop(key(c['invocation'])))
    p.pop(key(iv['build']));raw=identity();iv['build']=ref('nr.build.v2',sha(raw));p[key(iv['build'])]=raw
    raw=wire(iv);c['invocation']=ref('nr.invocation.v2',sha(raw));p[key(c['invocation'])]=raw
    return c,p


def test_production_capture_actual_build_exact_prior_and_measurements(tmp_path):
    c,p=actual_case();g=capture(*files_for(tmp_path,c,p))
    assert g.work.physical['bytes_read']>0 and g.work.physical['build_bytes_read']>0
    assert g.objects=={k:p[k] for k in g.objects}
    assert sum(map(len,next(iter(g.prior_bundles.values())).values()))==232849
    assert g.work.physical['bytes_written']==0
    record=dict(logical=g.work.logical,physical=g.work.physical,closure_bytes=len(g.closure_bytes),build_bytes=len(g.objects[key(g.invocation['build'])]))
    (tmp_path/'measurement.json').write_bytes(wire(record))


@pytest.mark.parametrize('attack,expected', [('prepared','NONEXECUTABLE_BUILD_WITNESS'),('build','BUILD_IDENTITY_MISMATCH'),('policy','RESOURCE_POLICY_IDENTITY_MISMATCH'),('pin','AUTHORITY_PIN_REQUIRED')])
def test_production_build_policy_and_external_pin(tmp_path,attack,expected):
    c,p=case() if attack=='prepared' else actual_case()
    if attack=='build':
        k=next(k for k in p if k[0]=='nr.build.v2');v=json.loads(p[k]);v['checkpoint']='0'*40
        body={k:v[k] for k in ('checkpoint','source_manifest','environment_manifest','entrypoint','contract_sha256','resource_policy_sha256','supported_nm_contract_sha256')}
        v['id']=sha(wire(body));replace(c,p,k,v)
    if attack=='policy':
        k=key(c['invocation']);v=json.loads(p[k]);v['resource_policy']['sha256']='0'*64;replace(c,p,k,v)
    if attack=='pin':c['authority_pin']='0'*64
    with pytest.raises(MeasurementContractError,match=expected):capture(*files_for(tmp_path,c,p))


@pytest.mark.parametrize('attack',['symlink','fifo','parent'])
def test_production_file_admission(tmp_path,attack):
    import os
    from applications.bounded_decision_workflow.errors import WorkflowInputError
    c,p=case();iv,objects,pin=files_for(tmp_path,c,p)
    if attack=='symlink':iv.rename(tmp_path/'saved.json');iv.symlink_to(tmp_path/'saved.json')
    elif attack=='fifo':iv.rename(tmp_path/'saved.json');os.mkfifo(iv)
    else:iv=iv.parent/'..'/iv.parent.name/iv.name
    with pytest.raises(WorkflowInputError):capture(iv,objects,pin)


def test_production_detects_invocation_replacement(tmp_path,monkeypatch):
    from applications.bounded_decision_workflow import retention
    c,p=case();iv,objects,pin=files_for(tmp_path,c,p);original=retention._read_at
    def replace_after_read(fd,name,*args,**kwargs):
        item=original(fd,name,*args,**kwargs)
        iv.rename(tmp_path/'saved.json');iv.write_bytes(item.data)
        return item
    monkeypatch.setattr(retention,'_read_at',replace_after_read)
    with pytest.raises(MeasurementContractError,match='INPUT_CHANGED_DURING_READ'):capture(iv,objects,pin)


def test_production_detects_directory_replacement(tmp_path,monkeypatch):
    from applications.bounded_decision_workflow import reassessment_capture as module
    c,p=actual_case();iv,objects,pin=files_for(tmp_path,c,p);original=module._read;done=False
    def replace_after_read(fd,name,*args,**kwargs):
        nonlocal done
        item=original(fd,name,*args,**kwargs)
        if name.endswith('.nr.build.v2') and not done:
            objects.rename(tmp_path/'saved-objects');objects.mkdir();done=True
        return item
    monkeypatch.setattr(module,'_read',replace_after_read)
    with pytest.raises(MeasurementContractError,match='INPUT_CHANGED_DURING_READ'):capture(iv,objects,pin)


@pytest.mark.parametrize('case_name',['P7-newbaseline','P10-context8','P10-objects128','P10-shared_four'])
def test_production_complete_required_material_fits(tmp_path,case_name):
    c,p=actual_case(case_name);g=capture(*files_for(tmp_path,c,p))
    assert len(g.closure_bytes)<=Work().limits['closure_bytes']
    assert g.work.logical['unique_objects']==len(g.objects)
    assert g.work.physical['bytes_read']==sum(map(len,g.objects.values()))
    (tmp_path/'measurement.json').write_bytes(wire(dict(case=case_name,logical=g.work.logical,physical=g.work.physical,closure_bytes=len(g.closure_bytes))))


def test_production_unreferenced_files_never_supply_or_expand_nomination(tmp_path):
    c,p=actual_case('P1-point60');iv,objects,pin=files_for(tmp_path,c,p)
    (objects/'unreferenced').symlink_to('/not/a/real/file')
    g=capture(iv,objects,pin)
    assert len(g.objects)==len(p)
