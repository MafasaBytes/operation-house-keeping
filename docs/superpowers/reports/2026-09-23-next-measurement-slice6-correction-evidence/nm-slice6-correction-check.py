import sys,os,json,hashlib,subprocess
from pathlib import Path
sys.path.insert(0,str(Path.cwd()))
from tests.measurement_profile.qualify_slice6 import bind,save,digest,verify_package
from applications.bounded_decision_workflow.measurement_build import identity
from applications.bounded_decision_workflow.input import parse_request_wire
root=Path('/tmp/nm-slice6-correction-20260923');root.mkdir()
pkg=Path('docs/superpowers/reports/2026-09-19-next-measurement-preparation');prop=Path('docs/superpowers/reports/2026-09-23-next-measurement-slice6-qualification-evidence/proposed-cross-profile-correction')
verify_package()
old=(pkg/'public/legacy-request.json').read_bytes();new=(prop/'legacy-request.json').read_bytes()
assert digest((prop/'proposal.json').read_bytes())=='edccbb50a2b50c2b8400652ea44148fcf6b275872ecf5d4d051478c35f350c61'
assert len(old)==16460 and len(new)==16382
assert digest(old)=='24635e493d371a5e05f9b61e729457fde7397ddfb0f31bc3dbb7f14ebe19c125'
assert digest(new)=='170d3ced7bfec018ddc63b03687edcb3716661b7f9f824c8715a6eaa954456c9'
a=json.loads(old);b=json.loads(new)
for obj in (a,b):
 obj['request_id']='x';obj['actor_assertion']['actor_label']='x';obj['actor_assertion']['purpose']='x'
assert a==b
parse_request_wire(new)
(root/'empty').mkdir();events=[]
for label,wire in [('corrected',new),('oversized-original',old)]:
 path=root/(label+'.json');path.write_bytes(wire)
 cmd=[sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(path),'--objects-dir',str(root/'empty'),'--authority-pin','7e94de3a64c6dbcf303406d39d4c63be415aaa82599ce268478c5831cda9ff80','--output-dir',str(root/(label+'-result'))]
 p=subprocess.run(cmd,capture_output=True);(root/(label+'.stdout')).write_bytes(p.stdout);(root/(label+'.stderr')).write_bytes(p.stderr)
 events.append(dict(label=label,argv=cmd,exit=p.returncode,diagnostic=json.loads(p.stderr),input_sha256=digest(wire),bytes=len(wire),output_exists=(root/(label+'-result')).exists()))
 assert p.returncode==(3 if label=='corrected' else 4)
 if label=='corrected':assert p.stderr==(pkg/'compatibility/J-existing-at-measurement/stderr.jsonl').read_bytes()
bind('P',identity(),root/'valid-profile')
iv=root/'valid-profile/invocation.json';pin=json.loads(iv.read_bytes())['selection']['sha256']
cmd=[sys.executable,'-m','applications.bounded_decision_workflow','measurement-evaluate','--invocation',str(iv),'--objects-dir',str(iv.parent/'objects'),'--authority-pin',pin,'--output-dir',str(root/'valid-result')]
p=subprocess.run(cmd,capture_output=True);(root/'valid.stdout').write_bytes(p.stdout);(root/'valid.stderr').write_bytes(p.stderr)
assert p.returncode==0,p.stderr
assert (root/'valid-result/result.json').read_bytes()==(iv.parent/'bound-expected-result.json').read_bytes()
events.append(dict(label='valid-measurement-P',exit=p.returncode,argv=cmd))
save(root/'checks.json',events);print(json.dumps(events))
