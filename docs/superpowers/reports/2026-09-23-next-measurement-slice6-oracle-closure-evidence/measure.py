from pathlib import Path
import json,hashlib,collections
root=Path('/tmp/nm-slice6-oracle-matrix-final');out=Path('/mnt/d/operation-house-keeping/docs/superpowers/reports/2026-09-23-next-measurement-slice6-oracle-closure-evidence')
def sha(b):return hashlib.sha256(b).hexdigest()
def save(name,v):(out/name).write_text(json.dumps(v,sort_keys=True,separators=(',',':')))
summary=json.loads((root/'summary.json').read_bytes());commands=json.loads((root/'commands.json').read_bytes())
assert summary['executed']==summary['exit_matches']==summary['exact_matches']==142
assert summary['differences']==0
bundles=sorted(root.glob('*/result/manifest.json'))+sorted(root.glob('*/replay/manifest.json'))
logical={};physical={};sizes={};bmax=0
for p in bundles:
 manifest=json.loads(p.read_bytes());result=json.loads((p.parent/'result.json').read_bytes())
 for k,v in result['accounting']['logical_required'].items():logical[k]=max(logical.get(k,0),v)
 for k,v in manifest['physical'].items():
  if isinstance(v,int):physical[k]=max(physical.get(k,0),v)
 total=0
 for f in p.parent.iterdir():
  n=f.stat().st_size;total+=n;sizes[f.name]=max(sizes.get(f.name,0),n)
 bmax=max(bmax,total)
measure=dict(head=summary['metadata']['head'],matrix_commands=len(commands),exact_matches=sum(not c['differences'] for c in commands),exit_counts=dict(collections.Counter(c['actual_exit'] for c in commands)),operation_counts=dict(collections.Counter(c['operation'] for c in commands)),timeouts=sum(c['timeout'] for c in commands),max_bundle_bytes=bmax,max_file_bytes=sizes,logical_required_maxima=logical,physical_manifest_maxima=physical,bundles=len(bundles),bundle_files=len(bundles)*7,wall_seconds_max=max(c['wall_ns'] for c in commands)/1e9,children_rss_highwater=max(c['children_peak_rss_bytes'] for c in commands),cpu_user_seconds=sum(c['cpu_user_s'] for c in commands),cpu_system_seconds=sum(c['cpu_system_s'] for c in commands),retained_regular_bytes=sum(p.stat().st_size for p in root.rglob('*') if p.is_file()))
save('measurements.json',measure)
old=Path('/mnt/d/operation-house-keeping/docs/superpowers/reports/2026-09-23-next-measurement-slice6-correction-evidence')
delta=dict(base_package_sha256='a6e48ea447444e4f7c12993d9567905978c2a0c8972414e0ac421df47cd2217f',base_manifest_sha256='18ed716ab327944f700b8e00b30235512a9ea6d5b41f49e87ab88b343680e2ea',base_recovery_sha256='ecfe3f62d796a21edc5509419206aebb68d46d8d3f10736d6708c412110a8dac',amendment_sha256=sha((old/'historical-diagnostic-amendment.json').read_bytes()),pointer='/target/field',path='expected/CL-historical-invalid/stderr.jsonl',old_sha256=sha((old/'historical-diagnostic-original.jsonl').read_bytes()),new_sha256=sha((out/'corrected-stderr.jsonl').read_bytes()),old_bytes=507,new_bytes=495,old_harness_sha256='bdab77e52e1a51de10224862c65cfdd50a6ebd0258b4d49a05e119ffa8c2f968',new_harness_sha256=summary['metadata']['harness_sha256'],commands_sha256=sha((root/'commands.json').read_bytes()),summary_sha256=sha((root/'summary.json').read_bytes()),bound_expected_diagnostic_sha256=sha((root/'cl-historical-invalid/bound-expected-diagnostic.json').read_bytes()),note='Immutable base package plus two explicit approved overlays (previous cross-profile fixture; this single diagnostic field). No base manifest rewrite. Runtime binding changes build/I and dependent commitments only, per CONTRACTS. Bound JSON expectation has no LF; stream expectation includes one LF.')
save('ORACLE-DELTA.json',delta)
print(json.dumps(measure,indent=2));print(json.dumps(delta,indent=2))
