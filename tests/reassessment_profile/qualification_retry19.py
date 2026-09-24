"""Explicit owner-named retries plus still-unused planned core slots, not a retry pool."""
import json,os,sys,subprocess,zipfile
from pathlib import Path
import qualification as q
from test_capture import case,key,ref
from applications.bounded_decision_workflow.reassessment_build import identity
from applications.bounded_decision_workflow import retention
SCHEDULE=q.REPO/'docs/superpowers/reports/2026-09-24-reassessment-slice5-retry19-schedule.json'

def records():
    return [json.loads(p.read_bytes()) for p in sorted((q.ROOT/'indexes').glob('[0-9][0-9][0-9][0-9]-*.json'))]

def material(row,build,z):
    name=row['case'];c,p=case(name);oldroot=c['invocation'];iv=json.loads(p.pop(key(oldroot)))
    oldbuild=iv['build'];p.pop(key(oldbuild));newbuild=ref('nr.build.v2',q.sha(build));p[key(newbuild)]=build
    iv['build']=newbuild;raw=q.wire(iv);newroot=ref('nr.invocation.v2',q.sha(raw));p[key(newroot)]=raw
    def bind(x):
        if x==oldroot:return newroot
        if x==oldbuild:return newbuild
        if isinstance(x,dict):return {k:bind(v) for k,v in x.items()}
        if isinstance(x,list):return [bind(v) for v in x]
        return x
    expected={}
    if row['expected']['exit']==0:
        value=bind(json.loads(z.read('cases/'+name+'/result.json')));value.pop('accounting')
        trace=bind(json.loads(z.read('cases/'+name+'/trace.json')));trace['required_closure'].sort(key=lambda r:(r['kind'],r['sha256']))
        expected={'result_without_accounting':q.wire(value),'trace':q.wire(trace)}
    else:expected={'stderr':q.wire(bind(json.loads(q.expected_member(z,'cases/'+name+'/stderr.expected'))))+b'\n'}
    return c,p,raw,expected

def schedule():
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();build=identity();rs=records()
    assert not subprocess.check_output(['git','diff','af86f93929b7fcb161fc4a8466a02e6f02372a80',head,'--','applications','backend'])
    channel=[r for r in rs if r.get('event')=='internal_control_fixed' and r.get('head')=='af86f93929b7fcb161fc4a8466a02e6f02372a80']
    assert len(channel)==1 and all(channel[0]['checks'].values())
    entries=[]
    with zipfile.ZipFile(q.PACKAGE) as z:
        rows=[r for r in json.loads(z.read('command-matrix.json'))['commands'] if r['id'].startswith('E-')];assert len(rows)==72
        for n,row in enumerate(rows,1):
            c,p,raw,expected=material(row,build,z)
            old=[r for r in rs if r.get('event')=='planned_refresh' and r.get('slot')==n]
            if n<=19:
                assert len(old)==1 and old[0]['case']==row['case']
                comparisons=[r for r in rs if r.get('event')=='final_core_comparison' and r.get('case')==row['case']]
                assert (len(comparisons)==1 and all(comparisons[0]['checks'].values())) if n<=18 else not comparisons
            else:assert not old
            entries.append(dict(id=row['id'],case=row['case'],slot=n,allocation='named_retry19' if n<=19 else 'unused_planned_refresh',tag=('T19-' if n<=19 else 'F-')+row['id'],target_head=head,original_attempt=('F-'+row['id']) if n<=19 else None,original_outcome=('passed_comparison_at_f6445e6789c306a5d085c1dd1655ad236a3db603' if n<=18 else 'operational_slot_consumed_prelaunch_no_application_evidence') if n<=19 else 'unused',reason='fresh coverage after receipt-channel executable repair' if n<=19 else 'remaining original planned qualification',expected=row['expected'],expected_commits={k:dict(bytes=len(b),sha256=q.sha(b)) for k,b in expected.items()},bound_invocation_sha256=q.sha(raw),input_bytes=sum(map(len,p.values()))+len(raw),allowance=dict(input_scratch=1048576,output_scratch=1048576,logs=32768,indexes=16384)))
    value=dict(schema='reassessment.retry19.schedule/v1',target_head=head,package_sha256=q.sha(q.PACKAGE.read_bytes()),build_sha256=q.sha(build),build_bytes=len(build),channel_evidence_head=channel[0]['head'],channel_checks=channel[0]['checks'],entries=entries,named_retry_count=19,unused_planned_count=53,repair_contingencies_remaining=0,expected_commitment_scope='result excludes observed accounting; trace exact; refusal stderr exact. Success receipt binds actual physical manifest, not preparation nulls. No expected output enters production.')
    q.publish_export(SCHEDULE,q.wire(value));print(head,q.sha(q.wire(value)),flush=True)

def run():
    s=json.loads(SCHEDULE.read_bytes());head=s['target_head'];build=identity();assert q.sha(build)==s['build_sha256']
    assert q.sha(q.PACKAGE.read_bytes())==s['package_sha256']
    rs=records();assert not any(r.get('event')=='retry19_core_claim' for r in rs)
    with zipfile.ZipFile(q.PACKAGE) as z:
        for row in s['entries']:
            assert subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==head
            assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--','applications','backend'])
            c,p,raw,expected=material(row,build,z)
            assert q.sha(raw)==row['bound_invocation_sha256']
            assert {k:dict(bytes=len(b),sha256=q.sha(b)) for k,b in expected.items()}==row['expected_commits']
            root=q.ROOT/'repairs'/row['tag'].lower();out=root/'bundle';size=sum(map(len,p.values()))+len(raw);assert size<=1048576
            with q.transaction(row['tag'],{'repairs':2097152,'logs':32768},files=len(p)+20,dirs=3):
                q.record(dict(event='retry19_core_claim',id=row['id'],slot=row['slot'],allocation=row['allocation'],head=head,schedule_sha256=q.sha(SCHEDULE.read_bytes())))
                # Exact bounded batch reservation precedes every exclusive file in it.
                q.reserve({'repairs':size},files=len(p)+1,dirs=2)
                root.mkdir();(root/'objects').mkdir()
                for (kind,digest),b in p.items():
                    with (root/'objects'/(digest+'.'+kind)).open('xb') as f:f.write(b);f.flush();os.fsync(f.fileno())
                with (root/'invocation.json').open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
                assert root.resolve()==root and not out.exists()
                absolute,parts=retention._parts(root)
                with retention._directory(absolute,parts) as fd:assert retention._filesystem(fd)=='ext4'
                assert identity()==build
                q.record(dict(event='retry19_launch_ready',id=row['id'],head=head,build_sha256=q.sha(build),input_bytes=size,channels='exclusive stdout/stderr capture; retained passing channel twin reused',accounting=q.census()))
                a,so,se=q.command(row['tag'],['reassessment-evaluate','--invocation',root/'invocation.json','--objects-dir',root/'objects','--authority-pin',c['authority_pin'],'--output-dir',out],out)
                checks=dict(exit=a['exit']==row['expected']['exit'],no_timeout=a['termination'] is None);measures={}
                if row['expected']['exit']==0 and a['exit']==0:
                    result=json.loads((out/'result.json').read_bytes());accounting=result.pop('accounting')
                    checks.update(result=q.wire(result)==expected['result_without_accounting'],trace=(out/'trace.json').read_bytes()==expected['trace'])
                    receipt=json.loads(so);checks.update(streams=se==b'' and so==q.wire(receipt)+b'\n',receipt_result=receipt['result_sha256']==q.sha((out/'result.json').read_bytes()),receipt_manifest=receipt['bundle_sha256']==q.sha((out/'manifest.json').read_bytes()))
                    expected_receipt=json.loads(z.read('cases/'+row['case']+'/stdout.expected'))
                    expected_receipt.update(result_sha256=q.sha((out/'result.json').read_bytes()),bundle_sha256=q.sha((out/'manifest.json').read_bytes()))
                    checks['exact_receipt']=so==q.wire(expected_receipt)+b'\n'
                    measures=dict(files={p.name:p.stat().st_size for p in out.iterdir()},accounting=accounting,manifest=json.loads((out/'manifest.json').read_bytes()))
                    checks['retained_bound']=sum(measures['files'].values())<=1048576
                elif row['expected']['exit']:
                    checks.update(exact_diagnostic=se==expected['stderr'],empty_stdout=so==b'',no_bundle=not out.exists())
                else:checks['unexpected_refusal']=False
                q.record(dict(event='retry19_core_comparison',id=row['id'],allocation=row['allocation'],head=head,checks=checks,measurements=measures))
                print(row['slot'],row['id'],all(checks.values()),flush=True)
            if not all(checks.values()):raise RuntimeError(('stop and classify',row['id'],checks))

if __name__=='__main__':
    if sys.argv[1:]==['--schedule']:schedule()
    elif sys.argv[1:]==['--run']:run()
    else:raise SystemExit('only --schedule or --run')
