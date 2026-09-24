"""Charge and run the two specifically approved retained-failure reproductions."""
import json,os,resource,selectors,subprocess,sys,time
from pathlib import Path

REPO=Path('/mnt/d/operation-house-keeping')
sys.path.insert(0,str(REPO/'docs/superpowers/reports'))
import importlib.util
spec=importlib.util.spec_from_file_location('budget',REPO/'docs/superpowers/reports/2026-09-24-reassessment-slice5-amended-budget-v2.py')
q=importlib.util.module_from_spec(spec);spec.loader.exec_module(q)
SOURCE=q.ROOT/'checkouts/source-0'
PY=Path('/home/mafasa/operation-house-keeping-runtime/bounded-decision-workflow/environments/cp313-bdw001/bin/python')

def invoke(slot,argv,*,timeout=120):
    stdout=q.ROOT/'logs'/(slot+'.stdout');stderr=q.ROOT/'logs'/(slot+'.stderr')
    assert not stdout.exists() and not stderr.exists()
    charges={'repairs':8*1048576,'logs':262144}
    with q.transaction(slot,charges,files=4,dirs=0):
        q.record(dict(event='slice5_approved_launch',slot=slot,base_candidate='40fbb7b0a5ea5251179a9661c782a41cf7356ed6',administrative_checkpoint='358d2867db478494ca8b6e6475b83fdd53a9750c',argv=list(map(str,argv)),write_bound=dict(repairs=charges['repairs'],logs=charges['logs'],max_stream_bytes=131072),retries=0))
        def bounds():
            resource.setrlimit(resource.RLIMIT_AS,(536870912,536870912))
            resource.setrlimit(resource.RLIMIT_FSIZE,(1048576,1048576))
        data={'stdout':bytearray(),'stderr':bytearray()};reason=None;started=time.monotonic()
        with stdout.open('xb') as so,stderr.open('xb') as se:
            child=subprocess.Popen(list(map(str,argv)),cwd=SOURCE,env=dict(os.environ,PYTHONPATH=str(SOURCE),PYTHONDONTWRITEBYTECODE='1',PYTHONNOUSERSITE='1'),stdout=subprocess.PIPE,stderr=subprocess.PIPE,preexec_fn=bounds)
            sel=selectors.DefaultSelector();sel.register(child.stdout,selectors.EVENT_READ,('stdout',so));sel.register(child.stderr,selectors.EVENT_READ,('stderr',se))
            while sel.get_map():
                if time.monotonic()-started>timeout and reason is None:reason='timeout';child.kill()
                for key,_ in sel.select(.1):
                    chunk=os.read(key.fileobj.fileno(),8192)
                    if not chunk:sel.unregister(key.fileobj);continue
                    left=131072-sum(map(len,data.values()))
                    if len(chunk)>left:
                        reason='stream_limit';child.kill();chunk=chunk[:left]
                    name,stream=key.data;stream.write(chunk);data[name].extend(chunk)
            status=child.wait();sel.close()
        result={'slot':slot,'exit':status,'termination':reason,'elapsed_seconds':time.monotonic()-started,
                'stdout_sha256':q.sha(data['stdout']),'stderr_sha256':q.sha(data['stderr']),
                'stdout_bytes':len(data['stdout']),'stderr_bytes':len(data['stderr'])}
        q.record(dict(event='slice5_launch_result',**result))
        print(json.dumps(result,sort_keys=True),flush=True)

def main():
    assert subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip()=='40fbb7b0a5ea5251179a9661c782a41cf7356ed6'
    assert not subprocess.check_output(['git','-C',str(SOURCE),'status','--porcelain','--untracked-files=all'],text=True)
    p1=[str(PY),'-m','pytest','-o','addopts=','-p','no:cacheprovider','tests/applications/bounded_decision_workflow/test_governed_build.py::test_actual_identity_or_explicit_dirty_refusal','-q']
    invoke('T-red-product',p1)
    collision=q.ROOT/'repairs'/'reporting-hook-collision-red.jsonl'
    assert not collision.exists()
    p2=[str(PY),str(REPO/'tests/reassessment_profile/legacy_report_collision_probe.py'),str(SOURCE),str(collision)]
    invoke('T-red-hook',p2)
    print(json.dumps(q.census(),sort_keys=True),flush=True)

if __name__=='__main__':main()
