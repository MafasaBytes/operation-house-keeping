"""Real Slice 4 commands, byte capture, independent replay and adverse twins."""
import base64
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from test_capture import actual_case,key,wire,sha,ref
from delivery_budget import ROOT,directory,put,reserve,record,inventory
from applications.bounded_decision_workflow import reassessment_runtime as runtime
from applications.bounded_decision_workflow.measurement_contracts import MeasurementContractError
from applications.bounded_decision_workflow.errors import WorkflowInputError
from applications.bounded_decision_workflow.measurement_wire import Work,BUNDLE_STATE

TAG=os.environ.get('NR_ATTEMPT','unassigned')
OUTPUTS=os.environ.get('NR_OUTPUT_CATEGORY','outputs')


def cli(*args):
    command=[sys.executable,'-m','applications.bounded_decision_workflow',*map(str,args)]
    record(dict(event='subprocess',argv=command))
    result=subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,
        cwd=ROOT/'recovery',env=dict(os.environ,PYTHONPATH=str(Path.cwd()),PYTHONDONTWRITEBYTECODE='1'))
    assert len(result.stdout)+len(result.stderr)<=4096
    record(dict(event='streams',argv=command,status=result.returncode,stdout=result.stdout.decode(),stderr=result.stderr.decode()))
    return result


def inputs(name,label):
    root=directory('inputs',TAG+'-'+label);c,p=actual_case(name);objects=root/'objects';objects.mkdir()
    for (kind,digest),raw in p.items():put(objects/(digest+'.'+kind),raw)
    iv=root/'invocation.json';put(iv,p[key(c['invocation'])])
    return root,iv,objects,c['authority_pin']


@pytest.fixture(scope='module')
def delivered():
    root,iv,objects,pin=inputs('P8-before','admitted');out=ROOT/OUTPUTS/(TAG+'-admitted')
    with reserve(OUTPUTS,1048576,'real evaluate'):r=cli('reassessment-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out)
    assert r.returncode==0,(r.stdout,r.stderr)
    assert r.stderr==b'' and r.stdout.endswith(b'\n')
    answer=json.loads(r.stdout);assert answer['disposition']=='one_compatible'
    # Preserve bytes but remove the original path before standalone replay.
    retired=root.with_name(root.name+'-retained');root.rename(retired)
    record(dict(event='new_input_path_retired',old=str(root),retained=str(retired)))
    assert not root.exists()
    return out,answer,retired,pin


def clone(bundle,label,mutate=None):
    files={p.name:p.read_bytes() for p in bundle.iterdir()}
    if mutate:mutate(files)
    manifest=json.loads(files['manifest.json'])
    for row in manifest['files']:
        b=files[row['name']];row.update(bytes=len(b),sha256=sha(b))
    files['manifest.json']=wire(manifest)
    out=directory(OUTPUTS,TAG+'-'+label)
    for n,b in files.items():put(out/n,b)
    return out


def test_standalone_command_replay(delivered):
    out,answer,retired,pin=delivered
    v=cli('reassessment-verify','--bundle',out)
    assert v.returncode==0 and v.stderr==b''
    replay=ROOT/OUTPUTS/(TAG+'-replay')
    with reserve(OUTPUTS,1048576,'standalone replay'):r=cli('reassessment-replay','--bundle',out,'--output-dir',replay)
    assert r.returncode==0,(r.stdout,r.stderr)
    assert json.loads(r.stdout)['result_sha256']==answer['result_sha256']
    for n in ['invocation.json','closure.json','result.json','trace.json','build.json','policy.json']:
        assert (out/n).read_bytes()==(replay/n).read_bytes()
    m=json.loads((replay/'manifest.json').read_bytes())
    assert m['physical']['bytes_read']>sum(p.stat().st_size for p in out.iterdir())
    assert m['physical']['bytes_written']==sum((replay/n).stat().st_size for n in runtime.FILES[:-1])
    assert m['physical']['status']=='observed_before_manifest_write'
    assert sum(p.stat().st_size for p in replay.iterdir())<=1048576


def test_rehashed_forgery_is_not_recomputation(delivered):
    out,*_=delivered
    def forge(files):
        r=json.loads(files['result.json']);r['summary']['disposition']='model_prediction_mismatch';files['result.json']=wire(r)
    bad=clone(out,'forged',forge)
    # Verification intentionally establishes integrity, not a recomputed claim.
    assert runtime.verify(bad)['disposition']=='model_prediction_mismatch'
    target=ROOT/OUTPUTS/(TAG+'-forgery-must-not-publish')
    with pytest.raises(MeasurementContractError,match='REPLAY_SEMANTIC_MISMATCH'):runtime.replay(bad,target)
    assert not target.exists()


def test_real_withholding_command():
    root,iv,objects,pin=inputs('P10-denied','withheld');out=ROOT/OUTPUTS/(TAG+'-withheld')
    with reserve(OUTPUTS,1048576,'withheld evaluate'):r=cli('reassessment-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',pin,'--output-dir',out)
    assert r.returncode==0 and r.stderr==b''
    result=json.loads((out/'result.json').read_bytes())
    assert result['summary']['disposition']=='evaluation_denied'
    assert len(result['hypotheses'])==2 and all(h['cells'] is None for h in result['hypotheses'])
    assert result['accounting']['logical']['qualified_cells']==0
    assert result['adoption']=='derived_not_adopted'


@pytest.mark.parametrize('attack,code',[
    ('authority','AUTHORITY_PIN_REQUIRED'),('missing','REQUIRED_REFERENCE_MISSING'),
    ('build','BUILD_IDENTITY_MISMATCH'),('policy','RESOURCE_POLICY_IDENTITY_MISMATCH'),
    ('profile','PROFILE_MISMATCH')])
def test_rehashed_retained_substitutions(delivered,attack,code):
    out,*_=delivered
    def change(files):
        c=json.loads(files['closure.json']);pool={key(m['reference']):base64.b64decode(m['bytes']) for m in c['members']}
        iv=json.loads(files['invocation.json']);old=key(c['invocation'])
        if attack=='authority':c['authority_pin']='0'*64
        elif attack=='missing':
            r=next(k for k in pool if k[0]=='nr.observation.v2');del pool[r]
        elif attack in ('build','policy'):
            field='build' if attack=='build' else 'resource_policy';k=key(iv[field]);v=json.loads(pool.pop(k))
            v['checkpoint']='0'*40 if attack=='build' else v.get('checkpoint','substituted')
            b=wire(v);new=(k[0],sha(b));pool[new]=b;iv[field]=ref(*new)
            files['build.json' if attack=='build' else 'policy.json']=b
            pool.pop(old);files['invocation.json']=wire(iv);newiv=ref('nr.invocation.v2',sha(files['invocation.json']));pool[key(newiv)]=files['invocation.json'];c['invocation']=newiv
            for n in ['result.json','trace.json']:
                value=json.loads(files[n]);value['invocation']=newiv;files[n]=wire(value)
        else:c['profile']='bdw.measurement.supplied.v1'
        c['members']=[dict(reference=ref(*k),encoding='base64',bytes=base64.b64encode(b).decode()) for k,b in sorted(pool.items())]
        files['closure.json']=wire(c)
    bad=clone(out,attack,change)
    with pytest.raises(MeasurementContractError,match=code):runtime.verify(bad)


def test_unsafe_paths_and_collision(delivered):
    out,_,retired,pin=delivered
    before={p.name:p.read_bytes() for p in out.iterdir()}
    r=cli('reassessment-replay','--bundle',out,'--output-dir',out)
    assert r.returncode==5 and json.loads(r.stderr)['code']=='OUTPUT_COLLISION' and r.stdout==b''
    assert before=={p.name:p.read_bytes() for p in out.iterdir()}
    link=ROOT/'inputs'/(TAG+'-symlink')
    with reserve('inputs',len(str(retired/'invocation.json')),'symlink control'):link.symlink_to(retired/'invocation.json')
    r=cli('reassessment-evaluate','--invocation',link,'--objects-dir',retired/'objects','--authority-pin',pin,'--output-dir',ROOT/OUTPUTS/(TAG+'-unsafe'))
    assert r.returncode==5 and r.stdout==b''
    assert json.loads(r.stderr)['code'] in ('PATH_FINAL_SYMLINK','PATH_COMPONENT_UNSAFE')
    r=cli('reassessment-verify','--bundle',str(out)+'/../'+out.name)
    assert r.returncode==5


@pytest.mark.parametrize('fault',['write','file_fsync','directory_fsync'])
def test_interrupted_publication(delivered,monkeypatch,fault):
    out,*_=delivered
    # Real semantic bytes already produced by the actual executable; the fault
    # seam is monkeypatch-only and not exposed through the production CLI.
    payloads={n:(out/n).read_bytes() for n in runtime.FILES[:-1]}
    target=ROOT/OUTPUTS/(TAG+'-fault-'+fault);w=Work();BUNDLE_STATE.set('absent')
    import time,stat
    original=runtime.retention._write_file;fsync=os.fsync
    if fault=='write':
        def write(fd,name,*a,**kw):
            if name=='result.json':raise runtime.retention._error('RETENTION_WRITE_FAILED')
            return original(fd,name,*a,**kw)
        monkeypatch.setattr(runtime.retention,'_write_file',write)
    else:
        def fail(fd):
            mode=os.fstat(fd).st_mode
            if (fault=='file_fsync' and stat.S_ISREG(mode)) or (fault=='directory_fsync' and stat.S_ISDIR(mode)):raise OSError('injected fsync')
            return fsync(fd)
        monkeypatch.setattr(os,'fsync',fail)
    with reserve(OUTPUTS,1048576,'fault '+fault):
        with pytest.raises(WorkflowInputError):runtime.publish(target,payloads,w,time.monotonic_ns())
    if fault=='directory_fsync':
        assert (target/'manifest.json').exists() and BUNDLE_STATE.get()=='complete_visible_durability_unknown'
    else:
        assert not (target/'manifest.json').exists() and BUNDLE_STATE.get()=='incomplete'
        with pytest.raises(MeasurementContractError,match='BUNDLE_INCOMPLETE'):runtime.verify(target)


def test_no_runtime_callback_or_build_option():
    for flag in ('--computed-result','--build','--skip-validation','--inv'):
        r=cli('reassessment-verify','--bundle',ROOT,flag,'x')
        assert r.returncode==2 and r.stdout==b''
    r=cli('reassessment-verify','--bundle',ROOT,'--bundle',ROOT)
    assert r.returncode==2


def test_recovery_accounting_and_tight_limits(delivered):
    out,*_=delivered;payloads,g,total=runtime._retained(out)
    assert total.logical['decoded_bytes']>0
    assert total.logical['reference_occurrences']>g.work.logical['reference_occurrences']
    assert total.physical['bytes_written']==0
    limits=ROOT/'inputs'/(TAG+'-limits.json');put(limits,wire(dict(closure_bytes=100)))
    with pytest.raises(MeasurementContractError,match='RESOURCE_LIMIT_EXCEEDED'):
        runtime.replay(out,ROOT/OUTPUTS/(TAG+'-resource-refusal'),limits)
    record(dict(event='actual_work',logical=total.logical,physical=total.physical,
        files={n:len(b) for n,b in payloads.items()},corpus=inventory()))


def test_malformed_retained_shape_is_input_refusal():
    with pytest.raises(MeasurementContractError,match='SCHEMA_INVALID'):
        runtime._output([], 'nr.result.v2')


def test_current_directory_descriptor_is_valid():
    runtime._stable('.',os.stat('.'))


def test_largest_required_closure_and_actual_work():
    from applications.bounded_decision_workflow.reassessment_capture import capture
    root,iv,objects,pin=inputs('P7-newbaseline','largest')
    g=capture(iv,objects,pin);payloads=runtime._payloads(g)
    reserve_bytes=sum(map(len,payloads.values()))+g.work.limits['manifest_bytes']
    assert len(payloads['closure.json'])<=524288 and reserve_bytes<=1048576
    assert g.work.physical['bytes_written']==0
    record(dict(event='largest_actual_case',files={n:len(b) for n,b in payloads.items()},logical=g.work.logical,
        physical=g.work.physical,complete_reservation=reserve_bytes,build_sha256=sha(payloads['build.json'])))


def test_prepared_build_remains_nonexecutable():
    from test_capture import case
    root=directory('inputs',TAG+'-prepared');c,p=case();objects=root/'objects';objects.mkdir()
    for (kind,digest),raw in p.items():put(objects/(digest+'.'+kind),raw)
    iv=root/'invocation.json';put(iv,p[key(c['invocation'])])
    r=cli('reassessment-evaluate','--invocation',iv,'--objects-dir',objects,'--authority-pin',c['authority_pin'],'--output-dir',ROOT/OUTPUTS/(TAG+'-prepared-refused'))
    assert r.returncode==3 and json.loads(r.stderr)['code']=='NONEXECUTABLE_BUILD_WITNESS'


def test_legacy_dispatch_usage_is_unchanged():
    for operation in ['evaluate','governed-evaluate','measurement-evaluate']:
        r=cli(operation)
        assert r.returncode==2 and r.stdout==b'' and json.loads(r.stderr)['code']=='USAGE_ERROR'
