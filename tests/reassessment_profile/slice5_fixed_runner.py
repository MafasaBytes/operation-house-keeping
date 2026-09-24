"""Run the one allocated targeted repaired-code qualification group."""
import json,os,resource,selectors,subprocess,sys,time
from pathlib import Path

REPO=Path('/mnt/d/operation-house-keeping');sys.path.insert(0,str(REPO/'docs/superpowers/reports'))
import importlib.util
spec=importlib.util.spec_from_file_location('budget',REPO/'docs/superpowers/reports/2026-09-24-reassessment-slice5-amended-budget-v2.py');q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
PY=Path('/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python')

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else 'fixed'
    if mode=='fixed':
        tag='T-fixed';root=q.ROOT/'repairs'/'v2-targeted-fixed';charges={'repairs':8*1048576,'logs':262144}
        paths=['tests/applications/bounded_decision_workflow/test_governed_build.py',
               'tests/applications/bounded_decision_workflow/test_governed_persistence.py',
               'tests/reassessment_profile/test_bounded_pytest_runner.py']
        report_mem=6*1048576
    elif mode=='legacy':
        tag='T-legacy';root=q.ROOT/'repairs'/'v2-affected-legacy';charges={'repairs':24*1048576,'logs':262144}
        paths=['tests/applications/bounded_decision_workflow']
        report_mem=20*1048576
    else:raise SystemExit('one approved mode: fixed or legacy')
    assert not root.exists();q.reserve(charges,files=8,dirs=2)
    with q.transaction(tag,charges,files=8,dirs=2):
        q.mkdir(root)
        q.mkdir(root/'tmp')
        collection=root/'collection.jsonl';results=root/'phase-results.jsonl'
        argv=[str(PY),str(REPO/'tests/reassessment_profile/bounded_pytest_runner.py'),'--collection',str(collection),'--results',str(results),'--','-o','addopts=','-p','no:cacheprovider',
              *paths,'-q','--basetemp',str(root/'tmp')]
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()
        q.record(dict(event='slice5_approved_launch',slot=tag,candidate=head,argv=argv,
                      reservation={'repairs':charges['repairs'],'logs':charges['logs'],'report_memory':report_mem,'retries':0}))
        def bounds():
            resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912));resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
        out=q.ROOT/'logs'/(tag+'.stdout');err=q.ROOT/'logs'/(tag+'.stderr');data={'stdout':bytearray(),'stderr':bytearray()};started=time.monotonic()
        env=dict(os.environ,PYTHONPATH=str(REPO),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1',BDW_REPORT_BYTES=str(report_mem))
        reason=None;timeout=180 if mode=='fixed' else 600
        with out.open('xb') as so,err.open('xb') as se:
            child=subprocess.Popen(argv,cwd=REPO,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=bounds)
            sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ,('stdout',so));sel.register(child.stderr,selectors.EVENT_READ,('stderr',se))
            while sel.get_map():
                if time.monotonic()-started>timeout and reason is None:reason='timeout';child.kill()
                for key,_ in sel.select(.1):
                    b=os.read(key.fileobj.fileno(),8192)
                    if not b:sel.unregister(key.fileobj);continue
                    name,stream=key.data;stream.write(b);data[name].extend(b)
                    if sum(map(len,data.values()))>262144 and reason is None:reason='stream_limit';child.kill()
            code=child.wait();sel.close()
        result={'exit':code,'termination':reason,'elapsed_seconds':time.monotonic()-started,'stdout_bytes':len(data['stdout']),'stderr_bytes':len(data['stderr']),
                'stdout_sha256':q.sha(data['stdout']),'stderr_sha256':q.sha(data['stderr']),
                'collection_bytes':collection.stat().st_size if collection.exists() else None,
                'phase_record_bytes':results.stat().st_size if results.exists() else None}
        q.record(dict(event='slice5_launch_result',slot=tag,**result,inventory=q.census()))
        print(json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__':main()
