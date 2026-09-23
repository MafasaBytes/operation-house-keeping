import sys,json,subprocess,os
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tests.measurement_profile.qualify_slice6 import save,read,wire,digest,ceiling
root=Path('/tmp/nm-slice6-disposition-extra');root.mkdir();p=Path('/tmp/nm-slice6-disposition-matrix/p');pin=read(p/'invocation.json')['selection']['sha256'];events=[]
for label,limits,status,code in [('stdout-full',None,7,'INTERNAL_ERROR'),('stdout-full-tight',{'diagnostic_bytes':1},4,'DIAGNOSTIC_LIMIT_EXCEEDED')]:
 out=root/label;args=[sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(p/'invocation.json'),'--objects-dir',str(p/'objects'),'--authority-pin',pin,'--output-dir',str(out)]
 if limits is not None:
  f=root/(label+'.json');save(f,limits);args+=['--limits',str(f)]
 with open('/dev/full','wb',buffering=0) as sink:run=subprocess.run(args,stdout=sink,stderr=subprocess.PIPE,timeout=30,preexec_fn=ceiling)
 (root/(label+'.stderr')).write_bytes(run.stderr);d=json.loads(run.stderr)
 assert run.returncode==status and d['code']==code and (out/'manifest.json').exists(),run.stderr
 assert d['bundle_state']=='complete_visible_durability_unknown'
 events.append(dict(label=label,exit=run.returncode,argv=args,diagnostic=d,manifest_present=True))
 args=[sys.executable,'-m','applications.bounded_decision_workflow','measurement-verify','--bundle',str(out)]
 checked=subprocess.run(args,capture_output=True,timeout=30,preexec_fn=ceiling)
 assert checked.returncode==0,checked.stderr
 (root/(label+'-verify.stdout')).write_bytes(checked.stdout);(root/(label+'-verify.stderr')).write_bytes(checked.stderr)
 events.append(dict(label=label+'-verify',exit=checked.returncode,argv=args))
original=Path('docs/superpowers/reports/2026-09-19-next-measurement-preparation/public/legacy-request.json').read_bytes();(root/'oversized-original.json').write_bytes(original);(root/'empty').mkdir()
args=[sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(root/'oversized-original.json'),'--objects-dir',str(root/'empty'),'--authority-pin',pin,'--output-dir',str(root/'oversized-refused')]
run=subprocess.run(args,capture_output=True,timeout=30,preexec_fn=ceiling);d=json.loads(run.stderr)
assert run.returncode==4 and not run.stdout and not (root/'oversized-refused').exists()
assert d['resource']==dict(dimension='invocation_bytes',attempted=16385,limit=16384)
(root/'oversized.stdout').write_bytes(run.stdout);(root/'oversized.stderr').write_bytes(run.stderr)
events.append(dict(label='historical-oversized-resource-control-not-profile-proof',exit=4,input_bytes=len(original),input_sha256=digest(original),argv=args,diagnostic=d))
save(root/'observations.json',events);print(json.dumps(events))
