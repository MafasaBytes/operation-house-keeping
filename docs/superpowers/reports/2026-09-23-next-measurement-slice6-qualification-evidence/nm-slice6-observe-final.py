import json,sys,time,resource
from pathlib import Path
from applications.bounded_decision_workflow import measurement_runtime as runtime
root=Path('/tmp/nm-slice6-observed-final-20260923');root.mkdir(exist_ok=False)
source=Path('/tmp/nm-slice6-matrix-final-20260923');rows=[]
def observe(frame,event,arg):
 if event=='return' and frame.f_code is runtime.evaluate.__code__ and 'work' in frame.f_locals:
  w=frame.f_locals['work'];rows.append(dict(logical=dict(w.logical),physical=dict(w.physical)))
for case in ['p','cl-q4-envelope','g-denied','cl-q5-refused']:
 path=source/case;iv=json.loads((path/'invocation.json').read_bytes());before=resource.getrusage(resource.RUSAGE_SELF);start=time.monotonic_ns();sys.setprofile(observe)
 try:answer=runtime.evaluate(path/'invocation.json',path/'objects',iv['selection']['sha256'],root/case);error=None
 except Exception as e:answer=None;error=dict(type=type(e).__name__,code=getattr(e,'code',None),details=getattr(e,'details',None))
 finally:sys.setprofile(None)
 after=resource.getrusage(resource.RUSAGE_SELF);rows[-1].update(case=case,receipt=answer,error=error,wall_ns=time.monotonic_ns()-start,cpu_user_s=after.ru_utime-before.ru_utime,cpu_system_s=after.ru_stime-before.ru_stime,peak_rss_bytes=after.ru_maxrss*1024)
 (root/'observations.json').write_text(json.dumps(dict(method='read-only profiler; no input or function replacement; same-author observations; overhead present',rows=rows),sort_keys=True,indent=2)+'\n')
print(root)
