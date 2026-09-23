from pathlib import Path
import json,os,subprocess,time,hashlib
source=Path('/tmp/nm-release-delivery-clean');root=Path('/tmp/nm-release-delivery-runtime');python='/tmp/nm-release-fresh-env/bin/python'
assert not (source/'docs/superpowers/reports/2026-09-19-next-measurement-preparation').exists()
assert subprocess.check_output(['git','status','--porcelain'],cwd=source)==b''
pin=(root/'input/authority-pin.txt').read_text().strip();records=[]
def run(name,args):
 start=time.monotonic_ns();r=subprocess.run([python,'-m','applications.bounded_decision_workflow',*map(str,args)],cwd=source,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','PYTHONPATH':''},capture_output=True,timeout=30)
 (root/(name+'.stdout')).write_bytes(r.stdout);(root/(name+'.stderr')).write_bytes(r.stderr)
 records.append(dict(name=name,argv=args,exit=r.returncode,wall_ns=time.monotonic_ns()-start));(root/'commands.json').write_text(json.dumps(records,default=str,sort_keys=True))
 assert r.returncode==0 and r.stderr==b'',r.stderr
 return json.loads(r.stdout)
a=run('evaluate',['measurement-evaluate','--invocation',root/'input/invocation.json','--objects-dir',root/'input/objects','--authority-pin',pin,'--output-dir',root/'result'])
r=json.loads((root/'result/result.json').read_bytes());assert [s['worst'] for s in r['ranking']['scores']]==[1,2]
assert r['ranking']['disposition']=='preferred_within_supplied_set'
run('verify',['measurement-verify','--bundle',root/'result'])
(root/'input').rename(root/'preserved-original-not-at-input-path')
run('replay',['measurement-replay','--bundle',root/'result','--output-dir',root/'replay'])
for name in ['result.json','trace.json']:
 assert (root/'result'/name).read_bytes()==(root/'replay'/name).read_bytes()
assert subprocess.check_output(['git','status','--porcelain'],cwd=source)==b''
(root/'summary.json').write_text(json.dumps(dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=source).decode().strip(),commands=3,all_exits=0,original_path_absent=not (root/'input').exists(),untracked_preparation_absent=True,clean_git=True,bundle_bytes=sum(p.stat().st_size for p in (root/'result').iterdir()),replay_bytes=sum(p.stat().st_size for p in (root/'replay').iterdir()),result_sha256=hashlib.sha256((root/'result/result.json').read_bytes()).hexdigest()),sort_keys=True))
print((root/'summary.json').read_text())
