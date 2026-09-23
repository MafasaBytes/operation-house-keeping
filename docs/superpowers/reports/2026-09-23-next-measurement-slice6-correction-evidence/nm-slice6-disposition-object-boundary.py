import sys,json,hashlib,shutil,subprocess,os
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tests.measurement_profile.qualify_slice6 import wire,save,read,digest,ceiling
root=Path('/tmp/nm-slice6-disposition-object-boundary');root.mkdir()
source=Path('/tmp/nm-slice6-disposition-matrix/p');events=[]
for count in [128,129]:
 case=root/str(count);case.mkdir();objects=case/'objects';shutil.copytree(source/'objects',objects)
 i=read(source/'invocation.json')
 def get(r):return read(objects/(r['sha256']+'.'+r['kind']))
 def put(v,kind=None):
  b=v if isinstance(v,bytes) else wire(v);kind=kind or v['schema'];r=dict(kind=kind,sha256=digest(b));p=objects/(r['sha256']+'.'+kind)
  if p.exists():assert p.read_bytes()==b
  else:p.write_bytes(b)
  return r
 q=get(i['request']);p=get(q['measurements'][0]);old=q['measurements'][0]
 # P's original closure has 19 unique objects; all rebound old objects become
 # unreachable. Only these extra basis objects increase the required count.
 extra=[put(('bounded-object-witness-'+str(n)).encode(),'nm.basis') for n in range(count-19)]
 p['conditions'][0]['basis']=sorted(p['conditions'][0]['basis']+extra,key=lambda r:(r['kind'],r['sha256']))
 q['measurements'][0]=put(p)
 for n,r in enumerate(q['support']):
  s=get(r)
  if s['procedure']==old:s['procedure']=q['measurements'][0];q['support'][n]=put(s)
 a=get(i['selection']);d=get(a['declaration']);i['request']=put(q);d['requests']=[i['request']];a['declaration']=put(d);a['request']=i['request'];i['selection']=put(a)
 save(case/'invocation.json',i)
 cmd=[sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(case/'invocation.json'),'--objects-dir',str(objects),'--authority-pin',i['selection']['sha256'],'--output-dir',str(case/'result')]
 run=subprocess.run(cmd,capture_output=True,timeout=30,preexec_fn=ceiling)
 (case/'stdout').write_bytes(run.stdout);(case/'stderr').write_bytes(run.stderr)
 event=dict(unique_objects=count,exit=run.returncode,argv=cmd)
 if count==128:
  assert run.returncode==0,run.stderr
  result=read(case/'result/result.json');assert result['accounting']['logical_required']['unique_objects']==128
  assert [s['worst'] for s in result['ranking']['scores']]==[1,2]
  event['logical_required']=result['accounting']['logical_required'];event['bundle_bytes']=sum(p.stat().st_size for p in (case/'result').iterdir())
 else:
  assert run.returncode==4,run.stderr
  diagnostic=json.loads(run.stderr);assert diagnostic['resource']==dict(dimension='unique_objects',attempted=129,limit=128)
  assert not (case/'result').exists();event['diagnostic']=diagnostic
 events.append(event)
save(root/'observations.json',events);print(json.dumps(events))
