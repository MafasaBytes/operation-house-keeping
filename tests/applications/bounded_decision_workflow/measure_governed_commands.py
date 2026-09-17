"""Isolated real-subprocess Slice 3 acceptance; expectations are authored, not learned.

No dependency installation/environment repair. New paths only. Returns recoverable
records; callers retain them separately from the seven-file operational bundles.
"""
import base64
import gzip
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

from applications.bounded_decision_workflow import governed_build
from .governed_fixtures import fixture,C,H

ROOT=Path(__file__).resolve().parents[3]
PY=sys.executable
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')

def measure(root):
    root=Path(root);root.mkdir(mode=0o700,exist_ok=False)
    commands=[];cases={};startup=[];bw,bid=governed_build.identity(observer=startup.append)
    journal=root/'command-evidence';journal.mkdir()
    def retain(row):
        commands.append(row)
        with (journal/(str(len(commands)).zfill(3)+'.json')).open('xb') as f:f.write(C(row))
    def run(argv,expected=0,code=None):
        start=time.monotonic();p=subprocess.run(argv,cwd=ROOT,env=ENV,capture_output=True,timeout=120)
        row={'argv':list(map(str,argv)),'returncode':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode(),'seconds':time.monotonic()-start}
        retain(row)
        assert p.returncode==expected,row
        assert len(p.stdout)<=512 and len(p.stderr)<=512,row
        if expected:
            assert not p.stdout and json.loads(p.stderr)['code']==code,row
            return json.loads(p.stderr)
        assert not p.stderr,row
        return json.loads(p.stdout)
    def cmd(*args):return [PY,'-m','applications.bounded_decision_workflow',*map(str,args)]
    def prepare(name,source,prior=None):
        folder=root/(name+'-input');folder.mkdir();objects=folder/'objects';objects.mkdir()
        old,entries,pin=fixture(source);v=json.loads(old);v['build_identity']=bid
        v['comparison']=None if prior is None else {'kind':'prior-bundle-manifest','sha256':H((root/prior/'manifest.json').read_bytes())}
        wire=C(v);(folder/'invocation.json').write_bytes(wire)
        for kind,b in entries:(objects/(H(b)+'.'+kind)).write_bytes(b)
        argv=cmd('governed-evaluate','--invocation',folder/'invocation.json','--objects-dir',objects,'--authority-pin',pin,'--output-dir',root/name)
        if prior:argv+=['--compare-to',str(root/prior)]
        return argv,{'source':source,'old_invocation':H(old),'new_invocation':H(wire),'pin':pin}
    schedule=[('w0','W0',None,True,['aH']),('d1-x','X-denied','w0',False,None),
              ('d2-x','D2-X','d1-x',True,[]),('j1','J1',None,True,['aH']),
              ('unavailable','amended-unavailable','w0',True,[]),
              *[(f'four-{i}',f'amended-four-{i}',None,True,None) for i in range(4)],
              ('working','working-adopted',None,True,['aH']),('j1-review','J1','w0',True,['aH']),
              ('unknown','applicability-unknown',None,False,None)]
    for name,source,prior,permission,selected in schedule:
        argv,meta=prepare(name,source,prior);receipt=run(argv)
        assert receipt['evaluation_permitted'] is permission
        r=json.loads((root/name/'result.json').read_bytes());rows=r['decision_review']['rows']
        assert len(rows)==23 and sum(x['performed'] for x in rows)==(23 if permission else 2)
        if selected is not None:assert r['selection']['selected_action_ids']==selected
        if name=='d2-x':
            assert r['selection']['disposition']=='no_feasible_action_in_supplied_set'
            assert r['resource_accounting']['lower_charges']==11847 and r['resource_accounting']['corner_evaluations']==16
        run(cmd('governed-verify','--bundle',root/name))
        replay=run(cmd('governed-replay','--bundle',root/name,'--output-dir',root/(name+'-replay')))
        assert replay['evaluation_permitted'] is permission
        for n in ['request.json','result.json','trace.json','resolved-input.json','build.json']:
            assert (root/name/n).read_bytes()==(root/(name+'-replay')/n).read_bytes()
        cases[name]=dict(meta,permission=permission,rows=23,performed=sum(x['performed'] for x in rows),
            required=sum(x['reevaluation']=='required' for x in rows),blocked=sum(not x['performed'] for x in rows),
            typed_changes=sum(x['value_changed'] is True for x in rows),numeric_comparable=sum(x['numeric_comparable'] for x in rows),
            logical=r['resource_accounting'],physical=json.loads((root/name/'manifest.json').read_bytes())['run_metadata']['operation_work'],
            replay_physical=json.loads((root/(name+'-replay')/'manifest.json').read_bytes())['run_metadata']['operation_work'],
            bytes={p.name:p.stat().st_size for p in (root/name).iterdir()})
    # Refusal nearest twins, without altering any accepted output.
    argv,_=prepare('wrong-pin','W0');argv[argv.index('--authority-pin')+1]='0'*64
    run(argv,3,'AUTHORITY_REFERENCE_MISMATCH');assert not (root/'wrong-pin').exists()
    argv,_=prepare('missing-authority','missing-authority')
    run(argv,3,'AUTHORITY_UNAVAILABLE')
    argv,_=prepare('oversized-wire','W0')
    supplied=root/'oversized-wire-input/objects'
    snapshot=next(supplied.glob('*.public-snapshot'))
    snapshot.write_bytes(b' '*(131072+1)) # Raw counter refusal, not a valid boundary snapshot.
    run(argv,4,'INPUT_WIRE_LIMIT_EXCEEDED')
    run(cmd('governed-evaluate'),2,'CLI_USAGE')
    run(cmd('governed-replay','--bundle',root/'w0','--output-dir',root/'w0'),5,'OUTPUT_COLLISION')
    # Legacy command semantics remain 22-row and cannot consume governed I.
    i,o,pin=fixture();v=json.loads(i);db={H(b):(k,b) for k,b in o};s=json.loads(db[v['scenario']['sha256']][1])
    legacy=root/'legacy-input';legacy.mkdir()
    (legacy/'request.json').write_bytes(db[s['request']['sha256']][1]);(legacy/'snapshot.json').write_bytes(db[s['snapshot']['sha256']][1])
    run(cmd('evaluate','--request',legacy/'request.json','--snapshot',legacy/'snapshot.json','--output-dir',root/'legacy'))
    assert len(json.loads((root/'legacy/result.json').read_bytes())['reevaluation']['decision_rows'])==22
    run(cmd('verify','--bundle',root/'legacy'))
    run(cmd('replay','--bundle',root/'legacy','--output-dir',root/'legacy-replay'))
    historical=root/'historical-build-source';historical.mkdir()
    for path in (root.parent/'commands-b/w0').iterdir():(historical/path.name).write_bytes(path.read_bytes())
    run(cmd('governed-verify','--bundle',historical))
    run(cmd('governed-replay','--bundle',historical,'--output-dir',root/'unavailable-historical-build'),3,'REPLAY_BUILD_UNAVAILABLE')
    for name in ('w0','d1-x'):
        receipt=run(cmd('governed-replay','--bundle',root/name,'--output-dir',root/(name+'-after-d2')))
        assert receipt['evaluation_permitted'] is (name=='w0')
        assert (root/name/'result.json').read_bytes()==(root/(name+'-after-d2')/'result.json').read_bytes()
    # Fresh hostile copy: all hashes agree, but the selected action is false.
    tampered=root/'rehashed-false-result';tampered.mkdir()
    for path in (root/'w0').iterdir():(tampered/path.name).write_bytes(path.read_bytes())
    r=json.loads((tampered/'result.json').read_bytes());r['selection']['selected_action_ids']=['aF'];b=C(r)
    (tampered/'result.json').write_bytes(b);m=json.loads((tampered/'manifest.json').read_bytes())
    m['files']['result.json']={'bytes':len(b),'sha256':H(b)};m['semantic_commitments']['result.json']=H(b)
    (tampered/'manifest.json').write_bytes(C(m))
    run(cmd('governed-verify','--bundle',tampered))
    diagnostic=run(cmd('governed-replay','--bundle',tampered,'--output-dir',root/'false-replay'),3,'REPLAY_SEMANTIC_MISMATCH')
    assert diagnostic['retry_class']=='investigate_integrity' and diagnostic['bundle_state']=='absent'
    # Exact subprocess observer seam, not a CLI flag or bypass. Same real build.
    argv,_=prepare('observed-d2','D2-X','d1-x')
    bootstrap="""import json,sys
from pathlib import Path
from applications.bounded_decision_workflow.cli import main
events=[]
def observe(e):
 if len(events)>=4096 or len(json.dumps(e,separators=(',',':')).encode())>512:raise RuntimeError('observer bound')
 events.append(e)
def fault(stage,name):observe({'phase':'filesystem','stage':stage,'name':name})
code=main(sys.argv[2:],observer=observe,fault=fault)
with Path(sys.argv[1]).open('x') as f:json.dump(events,f,separators=(',',':'))
raise SystemExit(code)
"""
    eventfile=root/'instrumentation.json';run([PY,'-c',bootstrap,str(eventfile),*argv[3:]])
    events=json.loads(eventfile.read_bytes())
    assert sum(e.get('scope')=='policy_assessment' and e.get('outcome')=='started' for e in events)==2
    assert any(e.get('stage')=='parent_fsync' for e in events)
    assert (root/'observed-d2/result.json').read_bytes()==(root/'d2-x/result.json').read_bytes()
    for name,source,bad in [('observed-denied','X-denied',False),('observed-refused','W0',True)]:
        args,_=prepare(name,source)
        if bad:args[args.index('--authority-pin')+1]='0'*64
        target=root/(name+'-events.json')
        run([PY,'-c',bootstrap,str(target),*args[3:]],3 if bad else 0,'AUTHORITY_REFERENCE_MISMATCH' if bad else None)
        es=json.loads(target.read_bytes())
        assert not any(e.get('scope') in ('policy_assessment','projection_plan') for e in es)
    # Two real competing processes: exactly one exclusively publishes.
    argv,_=prepare('concurrent','W0');children=[subprocess.Popen(argv,cwd=ROOT,env=ENV,stdout=subprocess.PIPE,stderr=subprocess.PIPE) for _ in range(2)]
    codes=[]
    for child in children:
        out,err=child.communicate(timeout=120);codes.append(child.returncode)
        retain({'argv':argv,'returncode':child.returncode,'stdout':out.decode(),'stderr':err.decode(),'concurrent':True})
        if child.returncode:assert child.returncode==5 and json.loads(err)['code']=='OUTPUT_COLLISION' and not out
    assert sorted(codes)==[0,5]
    run(cmd('governed-verify','--bundle',root/'concurrent'))
    # Trusted fault seam abruptly exits before manifest publication; no cleanup.
    argv,_=prepare('interrupted','W0')
    crash="""import os,sys
from applications.bounded_decision_workflow.cli import main
def fault(stage,name):
 if stage=='manifest_before_rename':os._exit(91)
raise SystemExit(main(sys.argv[1:],fault=fault))
"""
    p=subprocess.run([PY,'-c',crash,*argv[3:]],cwd=ROOT,env=ENV,capture_output=True,timeout=120)
    retain({'argv':[PY,'-c',crash,*argv[3:]],'returncode':p.returncode,'stdout':p.stdout.decode(),'stderr':p.stderr.decode()})
    assert p.returncode==91 and not p.stdout
    run(cmd('governed-verify','--bundle',root/'interrupted'),3,'BUNDLE_INCOMPLETE')
    run(argv,5,'OUTPUT_COLLISION')
    objects={};files={}
    for path in sorted(root.rglob('*')):
        if path.is_file():
            b=path.read_bytes();h=H(b);objects[h]=base64.b64encode(b).decode();files[str(path.relative_to(root))]=h
    usage=resource.getrusage(resource.RUSAGE_CHILDREN)
    evidence={'schema':'slice3-command-evidence.v1','root':str(root),'build_sha256':bid,'build_bytes':len(bw),'startup':startup,
            'commands':commands,'cases':cases,'events':events,'files':files,'objects':objects,
            'children_usage':{'user_seconds':usage.ru_utime,'system_seconds':usage.ru_stime,'max_rss_kib':usage.ru_maxrss,
                              'scope':'cumulative children of harness, not isolated per-command peaks'},
            'oracle':'same-author frozen law/expectations; exact executable and manifest bindings renewed, not historical bytes changed'}
    with (root/'execution-evidence.json').open('xb') as f:f.write(C(evidence))
    with (root/'execution-evidence.json.gz').open('xb') as f:f.write(gzip.compress(C(evidence),mtime=0))
    return evidence
