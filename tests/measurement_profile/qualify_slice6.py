"""Frozen Slice 6 command executor/checker; never imported by production.

Same-author oracle binding, not independent reviewer evidence. Expected semantic
fields are read from the frozen package, never computed by the future selector.
Only executable/I references, consequent byte/node demand, trace observation
provenance and physical manifest commitments are rebound per CONTRACTS.md.
"""
import argparse
import base64
import collections
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/'docs/superpowers/reports/2026-09-19-next-measurement-preparation'
def wire(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()
def digest(b):return hashlib.sha256(b).hexdigest()
def read(p):return json.loads(p.read_bytes())
def save(p,v):p.write_bytes(wire(v))
def k(r):return r['kind'],r['sha256']
def ref(kind,b):return dict(kind=kind,sha256=digest(b))
def nodes(v):return 1+sum(nodes(x) for x in (v.values() if isinstance(v,dict) else v if isinstance(v,list) else []))
def difference(a,b,path=''):
    if type(a)!=type(b):return [dict(path=path,expected=a,actual=b)]
    if isinstance(a,dict):
        out=[]
        for key in sorted(set(a)|set(b)):
            if key not in a or key not in b:out.append(dict(path=path+'/'+key,expected=a.get(key),actual=b.get(key)))
            else:out+=difference(a[key],b[key],path+'/'+key)
        return out
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(path=path,expected=a,actual=b)]
        return sum((difference(x,y,path+'/'+str(i)) for i,(x,y) in enumerate(zip(a,b))),[])
    return [] if a==b else [dict(path=path,expected=a,actual=b)]

def verify_package():
    for name,sha in [('package.zip','a6e48ea447444e4f7c12993d9567905978c2a0c8972414e0ac421df47cd2217f'),('MANIFEST.json','18ed716ab327944f700b8e00b30235512a9ea6d5b41f49e87ab88b343680e2ea'),('recovery.json','ecfe3f62d796a21edc5509419206aebb68d46d8d3f10736d6708c412110a8dac')]:
        assert digest((PACKAGE/name).read_bytes())==sha,name
    for entry in read(PACKAGE/'MANIFEST.json')['files']:
        b=(PACKAGE/entry['path']).read_bytes()
        assert len(b)==entry['bytes'] and digest(b)==entry['sha256'],entry['path']
    matrix=read(PACKAGE/'command-matrix.json');compat=read(PACKAGE/'compatibility-commands.json')
    assert len(matrix)==140 and len(compat)==2
    assert collections.Counter(x['operation'] for x in matrix)=={'measurement-evaluate':68,'measurement-verify':36,'measurement-replay':36}
    return matrix,compat

def bind(case,build,root):
    cap=read(PACKAGE/'inputs'/case/'capture.json');old=cap['invocation']
    original={k(m['reference']):base64.b64decode(m['bytes'],validate=True) for m in cap['members']}
    ib=json.loads(original[k(old)]);oldbuild=next(r for r in original if r[0]=='nm.prepared-build.v1')
    newbuild=ref('nm.build.v1',build);ib['build_identity']=newbuild['sha256'];inv=wire(ib);new=ref('nm.invocation.v1',inv)
    replacements={k(old):new,oldbuild:newbuild}
    def replace(v):
        if isinstance(v,dict):
            if set(v)=={'kind','sha256'} and k(v) in replacements:return replacements[k(v)]
            return {key:replace(x) for key,x in v.items()}
        if isinstance(v,list):return [replace(x) for x in v]
        if isinstance(v,str) and v.startswith('/closure/'+old['sha256']+'/'):
            return '/closure/'+new['sha256']+v[len('/closure/'+old['sha256']):]
        return v
    captured={k(replacements.get(r,dict(kind=r[0],sha256=r[1]))):b for r,b in original.items() if r not in replacements}
    captured[k(new)]=inv;captured[k(newbuild)]=build
    root.mkdir();obj=root/'objects';obj.mkdir()
    for (kind,sha),b in captured.items():
        if kind!='nm.invocation.v1':(obj/(sha+'.'+kind)).write_bytes(b)
    (root/'invocation.json').write_bytes(inv)
    if cap['limits_override'] is not None:save(root/'limits.json',cap['limits_override'])
    cap=replace(cap);cap['members']=[dict(reference=dict(kind=r[0],sha256=r[1]),encoding='base64',bytes=base64.b64encode(b).decode()) for r,b in sorted(captured.items())]
    save(root/'bound-capture.json',cap)
    expected=PACKAGE/'expected'/case
    if not (expected/'result.json').exists():
        save(root/'bound-expected-diagnostic.json',replace(read(expected/'stderr.jsonl')))
        return None
    result=replace(read(expected/'result.json'));trace=replace(read(expected/'trace.json'))
    trace['required_closure'].sort(key=k);trace['origin']='observed_execution';trace['physical_observed']=True
    for phase in trace['phases']:
        if phase['state']=='expected_reached':phase['state']='assessed'
    logical=result['accounting']['logical_required']
    logical['unique_bytes']=logical['capture_bytes']=sum(map(len,captured.values()))
    logical['closure_bytes']=len(wire(cap));logical['invocation_bytes']=len(inv);logical['object_bytes']=max(map(len,captured.values()))
    logical['json_nodes']=sum(nodes(json.loads(b)) for r,b in captured.items() if r[0]!='nm.basis')
    logical['context_scan_bytes']=sum(len(captured[k(e['source'])])+len(captured[k(e['target'])])+66 for e in trace['reference_occurrences'])
    save(root/'bound-expected-result.json',result);save(root/'bound-expected-trace.json',trace)
    return result,trace

def ceiling():resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    out=args.output.resolve();out.mkdir(exist_ok=False)
    matrix,compat=verify_package()
    from applications.bounded_decision_workflow.measurement_build import identity
    build=identity();(out/'build.json').write_bytes(build)
    metadata=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),package_sha256=digest((PACKAGE/'package.zip').read_bytes()),harness_sha256=digest(Path(__file__).read_bytes()),python=sys.executable,oracle='frozen hand tables; same-author independent byte-demand binding; no runtime oracle',commands=142,safety=dict(wall_seconds=30,address_space_bytes=536870912,retained_corpus_bytes=67108864))
    save(out/'metadata.json',metadata)
    expected={}
    for case in dict.fromkeys(x['case'] for x in matrix):expected[case]=bind(case,build,out/case.lower())
    empty=out/'empty';empty.mkdir();legacy=out/'legacy-request.json';legacy.write_bytes((PACKAGE/'public/legacy-request.json').read_bytes())
    records=[]
    for index,entry in enumerate(matrix+compat):
        case=entry.get('case',entry.get('id'));directory=out/case.lower();directory.mkdir(exist_ok=True)
        argv=[]
        for arg in entry['argv'][1:]:
            if arg.startswith('inputs/'):
                bits=arg.split('/');arg=str(out/bits[1].lower()/bits[2])
            elif arg=='public/legacy-request.json':arg=str(legacy)
            elif arg.startswith('<isolated-recovery/'):arg=str(directory/'objects')
            elif arg.startswith('<new-output/'):arg=str(directory/'result')
            elif arg.startswith('<successful-runtime-output/'):arg=str(directory/'result')
            elif arg.startswith('<new-replay/'):arg=str(directory/'replay')
            elif arg=='<qualified-empty-objects-directory>':arg=str(empty)
            elif arg=='<new-qualified-output>':arg=str(directory/'result')
            argv.append(arg)
        operation=entry.get('operation',argv[2]);prefix=directory/(str(index).zfill(3)+'-'+operation)
        before=resource.getrusage(resource.RUSAGE_CHILDREN);start=time.monotonic_ns()
        with prefix.with_suffix('.stdout').open('wb') as stdout,prefix.with_suffix('.stderr').open('wb') as stderr:
            child=subprocess.Popen([sys.executable,*argv],cwd=ROOT,stdout=stdout,stderr=stderr,preexec_fn=ceiling,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            timeout=False
            try:status=child.wait(timeout=30)
            except subprocess.TimeoutExpired:child.kill();status=child.wait();timeout=True
        elapsed=time.monotonic_ns()-start;after=resource.getrusage(resource.RUSAGE_CHILDREN)
        record=dict(index=index,case=case,operation=operation,argv=[sys.executable,*argv],expected_exit=entry['expected_exit'],actual_exit=status,timeout=timeout,wall_ns=elapsed,cpu_user_s=after.ru_utime-before.ru_utime,cpu_system_s=after.ru_stime-before.ru_stime,children_peak_rss_bytes=after.ru_maxrss*1024,block_in=after.ru_inblock-before.ru_inblock,block_out=after.ru_oublock-before.ru_oublock,differences=[])
        stdout=prefix.with_suffix('.stdout').read_bytes();stderr=prefix.with_suffix('.stderr').read_bytes()
        if status!=entry['expected_exit']:record['differences'].append(dict(path='/exit',expected=entry['expected_exit'],actual=status))
        if entry['expected_exit']==0 and status==0:
            bundle=directory/('replay' if operation=='measurement-replay' else 'result')
            result,trace=expected[case]
            for filename,value in [('result.json',result),('trace.json',trace)]:record['differences']+=difference(value,read(bundle/filename),'/'+filename)
            receipt=read(PACKAGE/entry['stdout']);receipt['result_sha256']=digest(wire(result));receipt['bundle_sha256']=digest((bundle/'manifest.json').read_bytes())
            record['differences']+=difference(receipt,json.loads(stdout),'/stdout')
            if stderr:record['differences'].append(dict(path='/stderr',expected='',actual=stderr.decode(errors='replace')))
            record['bundle_bytes']=sum(p.stat().st_size for p in bundle.iterdir());record['physical']=read(bundle/'manifest.json')['physical']
        elif entry['expected_exit']!=0:
            bound=directory/'bound-expected-diagnostic.json'
            exp=bound.read_bytes() if bound.exists() else (PACKAGE/entry.get('stderr',entry.get('expected_stderr'))).read_bytes()
            try:record['differences']+=difference(json.loads(exp),json.loads(stderr),'/stderr')
            except ValueError:record['differences'].append(dict(path='/stderr',expected=exp.decode(errors='replace'),actual=stderr.decode(errors='replace')))
            if stdout:record['differences'].append(dict(path='/stdout',expected='',actual=stdout.decode(errors='replace')))
        record['stdout_sha256']=digest(stdout);record['stderr_sha256']=digest(stderr)
        records.append(record);save(out/'commands.json',records)
        used=sum(p.stat().st_size for p in out.rglob('*') if p.is_file())
        print(index,case,operation,status,'diffs',len(record['differences']),'retained',used,flush=True)
        if used>67108864:raise RuntimeError('retained corpus safety ceiling exceeded')
    summary=dict(metadata=metadata,executed=len(records),exit_matches=sum(r['actual_exit']==r['expected_exit'] for r in records),exact_matches=sum(not r['differences'] for r in records),differences=sum(len(r['differences']) for r in records),retained_bytes=used)
    save(out/'summary.json',summary);print(json.dumps(summary),flush=True)
    return int(any(r['differences'] for r in records))

if __name__=='__main__':raise SystemExit(main())
