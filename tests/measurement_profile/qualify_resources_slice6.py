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
    baseline_result=read(a.output/'profiled/result.json')
    baseline_closure=read(a.output/'profiled/closure.json')
    for dimension,maximum in sorted(attempted.items()):
        # The caller override is itself retained. Solve the exact deterministic
        # carriage demand; this is byte accounting, not a semantic-result oracle.
        if dimension in ('closure_bytes','bundle_bytes'):
            value=maximum
            for unused in range(8):
                closure=dict(baseline_closure,limits_override={dimension:value})
                closure_size=len(wire(closure));delta=closure_size-len(wire(baseline_closure))
                result=read(a.output/'profiled/result.json')
                result['accounting']['logical_required']['closure_bytes']=closure_size
                demand=maximum+delta
                if dimension=='bundle_bytes':demand+=len(wire(result))-len(wire(baseline_result))
                if demand==value:break
                value=demand
            maximum=value
        for name,limit in [('exact',maximum),('below',maximum-1)]:
            if limit<1:continue
            filename=a.output/(dimension+'-'+name+'.json');save(filename,{dimension:limit});output=a.output/(dimension+'-'+name)
            start=time.monotonic_ns();before=resource.getrusage(resource.RUSAGE_CHILDREN)
            run=subprocess.run([sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(iv),'--objects-dir',str(objects),'--authority-pin',pin,'--output-dir',str(output),'--limits',str(filename)],capture_output=True,timeout=30,preexec_fn=ceiling)
            after=resource.getrusage(resource.RUSAGE_CHILDREN)
            (a.output/(dimension+'-'+name+'.stdout')).write_bytes(run.stdout);(a.output/(dimension+'-'+name+'.stderr')).write_bytes(run.stderr)
            expected_exit=0 if name=='exact' else 4
            events.append(dict(expected_exit=expected_exit,matched=run.returncode==expected_exit,dimension=dimension,limit=limit,relation_to_baseline=name,exit=run.returncode,stdout_sha256=digest(run.stdout),stderr_sha256=digest(run.stderr),diagnostic=json.loads(run.stderr) if run.stderr else None,manifest_present=(output/'manifest.json').exists(),wall_ns=time.monotonic_ns()-start,cpu_user_s=after.ru_utime-before.ru_utime,cpu_system_s=after.ru_stime-before.ru_stime))
            save(a.output/'boundary-observations.json',events);print(dimension,name,limit,run.returncode,flush=True)
    # Manifest counters are freshly observed; RSS/time digit widths can change
    # its demand between runs. Keep nominal mismatches, then measure a true
    # neighboring refusal without rewriting an earlier expectation.
    repairs=[]
    for event in events:
        if event['dimension']=='manifest_bytes' and event['relation_to_baseline']=='below' and event['exit']==0:
            successful=a.output/'manifest_bytes-below'/'manifest.json'
            demand=len(successful.read_bytes())
            assert demand<=event['limit']
            for attempt in range(8):
                limit=demand-1;label='manifest-calibration-'+str(attempt)
                filename=a.output/(label+'.json');save(filename,{'manifest_bytes':limit});output=a.output/label
                run=subprocess.run([sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(iv),'--objects-dir',str(objects),'--authority-pin',pin,'--output-dir',str(output),'--limits',str(filename)],capture_output=True,timeout=30,preexec_fn=ceiling)
                (a.output/(label+'.stdout')).write_bytes(run.stdout);(a.output/(label+'.stderr')).write_bytes(run.stderr)
                row=dict(limit=limit,exit=run.returncode,prior_measured_demand=demand,diagnostic=json.loads(run.stderr) if run.stderr else None)
                repairs.append(row);save(a.output/'manifest-calibration.json',repairs)
                if run.returncode==4:
                    assert row['diagnostic']['resource']['dimension']=='manifest_bytes'
                    assert not (output/'manifest.json').exists()
                    break
                assert run.returncode==0,run.stderr
                demand=len((output/'manifest.json').read_bytes());assert demand<=limit
            else:raise AssertionError('manifest physical demand did not stabilize within bounded calibration')
    save(a.output/'summary.json',dict(twins=len(events),matched=sum(e['matched'] for e in events),nominal_mismatches=[e for e in events if not e['matched']],manifest_calibration=repairs,unreached=sorted(set(Work().limits)-set(attempted))))
    print('Guard dimensions not reached:',sorted(set(Work().limits)-set(attempted)),flush=True)

if __name__=='__main__':main()
