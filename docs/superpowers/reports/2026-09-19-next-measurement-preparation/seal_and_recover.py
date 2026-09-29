"""Seal this data package and independently recover exact ZIP bytes in memory.
No extraction over existing artifacts and no application/proof execution.
"""
from pathlib import Path,PurePosixPath
import json,hashlib,subprocess,os,zipfile,io,time,resource
P=Path(__file__).resolve().parent;ROOT=P.parents[3]
C=lambda x:json.dumps(x,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
H=lambda b:hashlib.sha256(b).hexdigest()
env=dict(os.environ,GIT_OPTIONAL_LOCKS='0')
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT,env=env)
initial=json.loads((P/'starting-inventory.json').read_bytes())
assert len(initial['rows'])==initial['count']==1207
assert H(json.dumps(initial['rows'],separators=(',',':')).encode())==initial['sha256']
relative=str(P.relative_to(ROOT))+'/'
paths=sorted(set(git('ls-files','--cached','--others','--exclude-standard','-z').decode().split('\0'))-{''})
rows=[]
for name in paths:
 if name.startswith(relative):continue
 f=ROOT/name
 if f.is_file():rows.append([name,H(f.read_bytes())])
assert rows==initial['rows'],'Existing file inventory changed'
assert git('rev-parse','HEAD').decode().strip()=='6351750b3cacad288cb99d9d11a8b61b6fe85b71'
assert git('diff','--name-only')==b'' and git('diff','--cached','--name-only')==b''
preservation=dict(status='passed',starting_nonignored_files=1207,ending_original_nonignored_files=len(rows),starting_inventory_sha256=initial['sha256'],ending_original_inventory_sha256=H(json.dumps(rows,separators=(',',':')).encode()),tracked_and_index_changes=[],new_artifact_root=relative,ignored_runtime_cache='not inventoried; not targeted for writes',remote_operations=False)
(P/'preservation.json').write_bytes(C(preservation))
excludes={'MANIFEST.json','package.zip','recovery.json'}
files=[f for f in sorted(P.rglob('*')) if f.is_file() and str(f.relative_to(P)) not in excludes]
payload={str(f.relative_to(P)):f.read_bytes() for f in files}
assert all(not f.is_symlink() for f in files)
manifest=dict(schema='nm.preparation-package.v1',status='prepared_for_owner_package_policy_approval_not_executed',checkpoint=git('rev-parse','HEAD').decode().strip(),files=[dict(path=n,bytes=len(b),sha256=H(b)) for n,b in sorted(payload.items())],payload_bytes=sum(map(len,payload.values())),payload_file_count=len(payload),semantic_candidate_sha256='8726f35dac9997ee82c0764c95f749cb462e796c6d04794758a90775d0671305',confirmation_sha256='70a8c4ba7909bc35ae1479c43cf70fcbbf703463cb9f1d4096358af3312a27ee',owner_gate='exact package and resource policy, separately scoped implementation')
wire=C(manifest);(P/'MANIFEST.json').write_bytes(wire);payload['MANIFEST.json']=wire
start=time.perf_counter()
with zipfile.ZipFile(P/'package.zip','w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
 for n,b in sorted(payload.items()):
  zi=zipfile.ZipInfo(n,date_time=(2026,9,19,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;zi.external_attr=0o100644<<16;zi.create_system=3;z.writestr(zi,b)
archive=(P/'package.zip').read_bytes();recovered={}
with zipfile.ZipFile(io.BytesIO(archive),'r') as z:
 assert len(z.namelist())==len(set(z.namelist()))
 for info in z.infolist():
  n=PurePosixPath(info.filename);assert not n.is_absolute() and '..' not in n.parts and not info.is_dir()
  recovered[str(n)]=z.read(info)
assert recovered==payload
decoded_manifest=json.loads(recovered['MANIFEST.json'])
for f in decoded_manifest['files']:
 b=recovered[f['path']];assert len(b)==f['bytes'] and H(b)==f['sha256']
# Independently recover each case's inline closure from the archive, keeping
# deliberate omitted/tampered inputs intact rather than drawing from the union.
casecounts=[]
for c in json.loads(recovered['cases.json']):
 capture=json.loads(recovered[c['input']+'/capture.json']);members={}
 for row in capture['members']:
  import base64
  key=(row['reference']['kind'],row['reference']['sha256']);assert key not in members
  b=base64.b64decode(row['bytes'],validate=True);members[key]=b
  assert H(b)==key[1] or c['id']=='J-stale-hash'
 casecounts.append(dict(case=c['id'],members=len(members),decoded_bytes=sum(map(len,members.values()))))
receipt=dict(status='archive_recovery_verified',archive='package.zip',archive_sha256=H(archive),archive_bytes=len(archive),manifest_sha256=H(wire),payload_file_count=manifest['payload_file_count'],archive_member_count=len(recovered),payload_bytes=manifest['payload_bytes'],archive_recovered_bytes=sum(map(len,recovered.values())),case_recovery=casecounts,actual_preparation_work=dict(payload_file_read_calls=len(files),payload_bytes_read=manifest['payload_bytes'],zip_member_writes=len(payload),zip_member_reads=len(recovered),elapsed_archive_and_recovery_seconds=time.perf_counter()-start,peak_rss_KiB=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,filesystem_cache_and_device_IO='not measured'),application_proof_executed=False,executable_environment_recovery='future exact build unavailable; all prepared input bytes recoverable',preservation_sha256=H((P/'preservation.json').read_bytes()))
(P/'recovery.json').write_bytes(C(receipt))
print(json.dumps({k:v for k,v in receipt.items() if k not in ('case_recovery','actual_preparation_work')}))
