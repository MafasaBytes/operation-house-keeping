"""Read-only Work profiling plus real CLI tighter-limit twins (test harness).

No counter, hash, admission or computation is replaced. Profiling overhead is
reported separately. Boundary thresholds are observed guard demands, not policy
increases or static corpus capacity claims. Failures remain raw evidence.
"""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

from tests.measurement_profile.qualify_slice6 import wire,save,read,ceiling,digest
from applications.bounded_decision_workflow import measurement_runtime as rt
from applications.bounded_decision_workflow.measurement_wire import Work


def main():
    p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(exist_ok=False)
    root=a.input;iv=root/'invocation.json';objects=root/'objects';pin=read(iv)['selection']['sha256']
    attempted={};events=[];observed={}
    def profile(frame,event,arg):
        if event=='call' and frame.f_code is Work.guard.__code__:
            key=frame.f_locals['k'];n=frame.f_locals['n'];attempted[key]=max(attempted.get(key,0),n)
        if event=='return' and frame.f_code is rt.evaluate.__code__ and 'work' in frame.f_locals:
            w=frame.f_locals['work'];observed.update(logical=dict(w.logical),physical=dict(w.physical))
    sys.setprofile(profile)
    try:rt.evaluate(iv,objects,pin,a.output/'profiled')
    finally:sys.setprofile(None)
    save(a.output/'observed-work.json',dict(method='read-only profiler; overhead present',maximum_guard_demands=attempted,observed=observed))
    for dimension,maximum in sorted(attempted.items()):
        # limits_override changes closure bytes, hence result size and aggregate
        # reserve. Record these interactions, never normalize a failed twin.
        for name,limit in [('exact',maximum),('below',maximum-1)]:
            if limit<1:continue
            filename=a.output/(dimension+'-'+name+'.json');save(filename,{dimension:limit});output=a.output/(dimension+'-'+name)
            start=time.monotonic_ns();before=resource.getrusage(resource.RUSAGE_CHILDREN)
            run=subprocess.run([sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(iv),'--objects-dir',str(objects),'--authority-pin',pin,'--output-dir',str(output),'--limits',str(filename)],capture_output=True,timeout=30,preexec_fn=ceiling)
            after=resource.getrusage(resource.RUSAGE_CHILDREN)
            (a.output/(dimension+'-'+name+'.stdout')).write_bytes(run.stdout);(a.output/(dimension+'-'+name+'.stderr')).write_bytes(run.stderr)
            events.append(dict(dimension=dimension,limit=limit,relation_to_baseline=name,exit=run.returncode,stdout_sha256=digest(run.stdout),stderr_sha256=digest(run.stderr),diagnostic=json.loads(run.stderr) if run.stderr else None,manifest_present=(output/'manifest.json').exists(),wall_ns=time.monotonic_ns()-start,cpu_user_s=after.ru_utime-before.ru_utime,cpu_system_s=after.ru_stime-before.ru_stime))
            save(a.output/'boundary-observations.json',events);print(dimension,name,limit,run.returncode,flush=True)
    print('Guard dimensions not reached:',sorted(set(Work().limits)-set(attempted)),flush=True)

if __name__=='__main__':main()
