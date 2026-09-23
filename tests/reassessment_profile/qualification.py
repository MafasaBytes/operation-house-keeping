"""Owner-authorized Slice 5 evidence driver; never imported by production.

Frozen expectations are comparison inputs only. Each application uses its public
CLI and captures its own inputs. All writes are exclusively created and reserved.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import selectors
import stat
import subprocess
import sys
import time
import zipfile

ROOT = Path('/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/test-workspaces/nr-slice5-qualification-r1')
REPO = Path(__file__).resolve().parents[2]
PACKAGE = REPO/'docs/superpowers/reports/2026-09-23-reassessment-preparation/package.zip'
CAPS = dict(outputs=135266304,inputs=125829120,repairs=33554432,regressions=134217728,
            checkouts=536870912,recovery=4194304,logs=8388608,indexes=8388608,exports=134217728)

def wire(x):
    return json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()

def sha(b):
    return hashlib.sha256(b).hexdigest()

def census():
    counts=dict.fromkeys(CAPS,0);physical=0;files=0;dirs=0
    for here,ds,fs in os.walk(ROOT,followlinks=False):
        physical+=os.lstat(here).st_blocks*512;dirs+=1
        for n in fs+[n for n in ds if (Path(here)/n).is_symlink()]:
            p=Path(here)/n;s=p.lstat();files+=1;physical+=s.st_blocks*512
            counts[p.relative_to(ROOT).parts[0]]+=s.st_size
    external={}
    for p in (ROOT/'indexes').glob('*record.json'):
        row=json.loads(p.read_bytes())
        if row.get('event')=='external_export':external[row['path']]=row
    for name,row in external.items():
        p=Path(name);b=p.read_bytes()
        assert len(b)==row['bytes'] and sha(b)==row['sha256']
        counts['exports']+=len(b);physical+=p.stat().st_blocks*512;files+=1
    assert all(counts[k]<=CAPS[k] for k in counts)
    assert sum(counts.values())<=1120927744 and physical<=1204813824
    assert files<=16384 and dirs<=2048
    return dict(categories=counts,total=sum(counts.values()),combined=76560100+sum(counts.values()),physical=physical,files=files,directories=dirs)

def reserve(charges,files=1,dirs=0):
    now=census();growth=sum(charges.values())
    assert all(now['categories'][k]+v<=CAPS[k] for k,v in charges.items())
    assert now['total']+growth<=1120927744
    assert now['files']+files<=16384 and now['directories']+dirs<=2048
    assert now['physical']+growth+files*4096+dirs*8192<=1204813824
    s=os.statvfs(ROOT);assert s.f_bavail*s.f_frsize>=1204813824-now['physical']

def put(p,b):
    reserve({p.relative_to(ROOT).parts[0]:len(b)})
    with p.open('xb') as f:f.write(b)

def record(x):
    names=sorted((ROOT/'indexes').glob('*.json'));last=names[-1]
    b=wire(dict(previous=sha(last.read_bytes()),**x))
    put(ROOT/'indexes'/f'{len(names):04d}-record.json',b)

def mkdir(p):
    reserve({},files=0,dirs=1);p.mkdir()

def command(tag,args,output=None):
    charges={'logs':32768,'indexes':16384}
    if output:charges[output.relative_to(ROOT).parts[0]]=1048576
    reserve(charges,files=12,dirs=1 if output else 0)
    argv=[sys.executable,'-m','applications.bounded_decision_workflow',*map(str,args)]
    record(dict(event='command',tag=tag,head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),argv=argv,reservation=charges))
    def limits():
        resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
        resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
    started=time.monotonic();sel=selectors.DefaultSelector();streams={'stdout':bytearray(),'stderr':bytearray()};reason=None
    with (ROOT/'logs'/(tag+'.stdout')).open('xb') as so, (ROOT/'logs'/(tag+'.stderr')).open('xb') as se:
        child=subprocess.Popen(argv,cwd=ROOT/'recovery',env=dict(os.environ,PYTHONPATH=str(REPO),PYTHONDONTWRITEBYTECODE='1'),stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=limits)
        sel.register(child.stdout,selectors.EVENT_READ,('stdout',so));sel.register(child.stderr,selectors.EVENT_READ,('stderr',se))
        while sel.get_map():
            if time.monotonic()-started>30 and reason is None:reason='timeout';child.kill()
            for key,_ in sel.select(.1):
                b=os.read(key.fileobj.fileno(),4096)
                if not b:sel.unregister(key.fileobj);continue
                left=32768-sum(map(len,streams.values()))
                if len(b)>left:
                    if reason is None:reason='stream_limit';child.kill()
                    b=b[:left]
                name,f=key.data;f.write(b);streams[name].extend(b)
        status=child.wait()
    sel.close()
    result=dict(tag=tag,exit=status,termination=reason,elapsed_seconds=time.monotonic()-started,
                stdout_sha256=sha(streams['stdout']),stderr_sha256=sha(streams['stderr']))
    record(dict(event='command_result',**result,inventory=census()))
    return result,bytes(streams['stdout']),bytes(streams['stderr'])

def core():
    sys.path.insert(0,str(REPO));sys.path.insert(0,str(Path(__file__).parent))
    from test_capture import case,key,ref
    from applications.bounded_decision_workflow.reassessment_build import identity
    from applications.bounded_decision_workflow.measurement_wire import Work
    w=Work();build=identity(w);put(ROOT/'inputs'/'actual-build.json',build)
    record(dict(event='actual_build',sha256=sha(build),bytes=len(build),logical=w.logical,physical=w.physical))
    results=[]
    with zipfile.ZipFile(PACKAGE) as z:
        matrix=json.loads(z.read('command-matrix.json'))
        for row in matrix['commands']:
            if not row['id'].startswith('E-'):continue
            name=row['case'];c,p=case(name);oldroot=c['invocation'];iv=json.loads(p.pop(key(oldroot)))
            oldbuild=iv['build'];p.pop(key(oldbuild));newbuild=ref('nr.build.v2',sha(build));p[key(newbuild)]=build
            iv['build']=newbuild;raw=wire(iv);newroot=ref('nr.invocation.v2',sha(raw));p[key(newroot)]=raw
            d=ROOT/'inputs'/name;reserve({'inputs':sum(map(len,p.values()))+len(raw)},files=len(p)+1,dirs=2);mkdir(d);mkdir(d/'objects')
            for (kind,digest),b in sorted(p.items()):put(d/'objects'/(digest+'.'+kind),b)
            put(d/'invocation.json',raw)
            out=ROOT/'outputs'/row['id'].lower()
            answer,stdout,stderr=command(row['id'],['reassessment-evaluate','--invocation',d/'invocation.json','--objects-dir',d/'objects','--authority-pin',c['authority_pin'],'--output-dir',out],out)
            def bind(x):
                if x==oldroot:return newroot
                if x==oldbuild:return newbuild
                if isinstance(x,dict):return {k:bind(v) for k,v in x.items()}
                if isinstance(x,list):return [bind(v) for v in x]
                return x
            checks={'exit':answer['exit']==row['expected']['exit'],'no_timeout':answer['termination'] is None}
            if row['expected']['exit']==0 and answer['exit']==0:
                r=json.loads((out/'result.json').read_bytes());expected=bind(json.loads(z.read('cases/'+name+'/result.json')))
                r.pop('accounting');expected.pop('accounting');checks['semantic_result']=r==expected
                expected_trace=bind(json.loads(z.read('cases/'+name+'/trace.json')))
                expected_trace['required_closure']=sorted(expected_trace['required_closure'],key=lambda x:(x['kind'],x['sha256']))
                checks['trace']=json.loads((out/'trace.json').read_bytes())==expected_trace
                receipt=json.loads(stdout);checks['streams']=stderr==b'' and stdout==wire(receipt)+b'\n'
                checks['receipt_result']=receipt['result_sha256']==sha((out/'result.json').read_bytes())
                checks['receipt_manifest']=receipt['bundle_sha256']==sha((out/'manifest.json').read_bytes())
            elif row['expected']['exit']:
                expected=wire(bind(json.loads(z.read('cases/'+name+'/stderr.expected'))))+b'\n'
                checks['exact_diagnostic']=stderr==expected;checks['empty_stdout']=stdout==b'';checks['no_bundle']=not out.exists()
            else:checks['unexpected_refusal']=False
            record(dict(event='comparison',case=name,checks=checks));results.append(dict(case=name,checks=checks))
            print(name,all(checks.values()),flush=True)
    put(ROOT/'indexes'/'core-comparison.json',wire(results))
    print(json.dumps(census()),flush=True)

if __name__=='__main__':core()
